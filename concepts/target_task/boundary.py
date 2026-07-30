"""Deterministic firewall for Target Task control, receipts, and cursor state."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from capabilities.body_state.body_state import BodyStateError, validate_state_bytes, validate_state_structure_bytes
from capabilities.focused_retrieval.focused_retrieval import RetrievalError, retrieve
from capabilities.runskeptic_receipt.runskeptic_receipt import (
    ValidationResult,
    advance_fix_loop as _advance_fix_loop,
    fix_loop_complete,
    validate_loop_state,
    validate_receipt as _validate_receipt,
)
from concepts.target_task.contracts import (
    ContractError,
    CursorStatus,
    LedgerEvent,
    LunaAction,
    Phase,
    StepCursor,
    plan_step_ids,
    validate_task_id,
    validate_candidate_manifest_dict,
    validate_remote_verification_manifest_dict,
)
from concepts.target_task.flow import TransitionResult, allowed_actions, next_phase
from concepts.target_task.store import (
    AppendOnlyLedger,
    StoreError,
    load_finding_set_artifact,
    load_plan_artifact,
    persist_cursor_snapshot,
    persist_loop_state_artifact,
    read_content_addressed_artifact,
    read_ledger,
)

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


class BoundaryError(ValueError):
    pass


def _mission_task_id(task_root: Path) -> str:
    events = read_ledger(Path(task_root) / "ledger.jsonl")
    if not events:
        raise BoundaryError("mission event missing")
    return events[0]["task_id"]


def _canonical_object(raw: bytes, label: str, maximum: int = 32768) -> dict[str, Any]:
    if len(raw) > maximum:
        raise BoundaryError(f"{label} too large")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BoundaryError(f"{label} is not UTF-8") from exc
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise BoundaryError(f"{label} encoding")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise BoundaryError(f"{label} duplicate key")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs)
    except BoundaryError:
        raise
    except json.JSONDecodeError as exc:
        raise BoundaryError(f"{label} JSON") from exc
    if not isinstance(value, dict):
        raise BoundaryError(f"{label} object required")
    canonical = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if canonical != raw:
        raise BoundaryError(f"{label} noncanonical")
    return value


def _validated_task_reference(
    reference: Any,
    task_root: Path,
    label: str,
    *,
    artifact_type: str | None = None,
) -> dict[str, Any]:
    from concepts.target_task.runtime import validate_task_artifact_reference

    try:
        validated = validate_task_artifact_reference(reference, Path(task_root), f"$.{label}")
    except Exception as exc:
        raise BoundaryError(f"{label} artifact invalid") from exc
    if artifact_type is not None and validated["artifact_type"] != artifact_type:
        raise BoundaryError(f"{label} artifact type mismatch")
    if artifact_type in {"candidate_manifest", "remote_verification_manifest"}:
        raw = (Path(task_root) / validated["repository_relative_path"]).read_bytes()
        value = _canonical_object(raw, label)
        try:
            if artifact_type == "candidate_manifest":
                candidate = validate_candidate_manifest_dict(value)
                if candidate["task_id"] != _mission_task_id(task_root):
                    raise BoundaryError(f"{label} task binding mismatch")
            else:
                remote = validate_remote_verification_manifest_dict(value)
                if remote["expected_commit"] != remote["observed_commit"] or remote["expected_tree"] != remote["observed_tree"]:
                    raise BoundaryError(f"{label} remote mismatch")
        except ContractError as exc:
            raise BoundaryError(f"{label} manifest invalid") from exc
    return validated


def _mission_sha256(task_root: Path, task_id: str) -> str:
    try:
        events = read_ledger(Path(task_root) / "ledger.jsonl")
        if not events or events[0]["task_id"] != task_id or events[0]["phase"] != Phase.MISSION_PERSISTED.value:
            raise BoundaryError("mission event missing")
        mission_ref = events[0]["result_ref"]
        if mission_ref is None:
            raise BoundaryError("mission reference missing")
        mission = read_content_addressed_artifact(Path(task_root), mission_ref)
    except BoundaryError:
        raise
    except Exception as exc:
        raise BoundaryError("mission identity unavailable") from exc
    return hashlib.sha256(mission).hexdigest()


def _pass_receipt(
    value: Any,
    name: str,
    task_root: Path | None,
    task_id: str | None,
    subject_reference: Mapping[str, Any] | None,
    *,
    subject_artifact_type: str | None = None,
) -> Mapping[str, Any]:
    if task_root is None or task_id is None or subject_reference is None:
        raise BoundaryError(f"{name} evidence is incomplete")
    try:
        validate_task_id(task_id)
    except Exception as exc:
        raise BoundaryError("invalid task ID") from exc
    if not isinstance(value, Mapping) or set(value) != {"status", "reference"} or value.get("status") != "PASS":
        raise BoundaryError(f"{name} PASS receipt required")
    subject = _validated_task_reference(
        subject_reference, Path(task_root), f"{name}.subject", artifact_type=subject_artifact_type
    )
    receipt = _validated_task_reference(
        value["reference"], Path(task_root), f"{name}.reference", artifact_type="validation_receipt"
    )
    raw = (Path(task_root) / receipt["repository_relative_path"]).read_bytes()
    payload = _canonical_object(raw, f"{name} receipt", maximum=4096)
    expected_fields = {"schema_version", "task_id", "gate", "status", "subject_sha256"}
    if set(payload) != expected_fields:
        raise BoundaryError(f"{name} receipt fields")
    if (
        payload["schema_version"] != "1"
        or payload["task_id"] != task_id
        or payload["gate"] != name
        or payload["status"] != "PASS"
        or payload["subject_sha256"] != subject["sha256"]
    ):
        raise BoundaryError(f"{name} receipt binding mismatch")
    return value


def _material_findings(
    reference: Mapping[str, Any] | None,
    *,
    task_root: Path,
    task_id: str,
    expected_sha256: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if reference is None:
        raise BoundaryError("material finding-set reference required")
    validated = _validated_task_reference(reference, task_root, "material_findings", artifact_type="material_findings")
    if validated["sha256"] != expected_sha256:
        raise BoundaryError("material finding-set hash mismatch")
    try:
        finding_set = load_finding_set_artifact(task_root, validated["repository_relative_path"])
    except (StoreError, ContractError) as exc:
        raise BoundaryError("material finding-set artifact invalid") from exc
    if finding_set["task_id"] != task_id:
        raise BoundaryError("material finding-set task mismatch")
    open_findings = [item for item in finding_set["findings"] if item["status"] == "OPEN"]
    return validated, open_findings


def _validated_plan(
    task_root: Path,
    task_id: str,
    plan_reference: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if plan_reference is None:
        raise BoundaryError("accepted Plan reference required")
    validated = _validated_task_reference(plan_reference, task_root, "accepted_plan", artifact_type="sealed_plan")
    try:
        plan = load_plan_artifact(Path(task_root), validated["repository_relative_path"])
    except Exception as exc:
        raise BoundaryError("accepted Plan artifact invalid") from exc
    if plan["task_id"] != task_id or plan["mission_sha256"] != _mission_sha256(task_root, task_id):
        raise BoundaryError("accepted Plan mission/task binding mismatch")
    return validated, plan


def _validated_cursor(
    task_root: Path,
    task_id: str,
    cursor: StepCursor | None,
    cursor_reference: Mapping[str, Any] | None,
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    if cursor is None or cursor_reference is None:
        raise BoundaryError("durable cursor reference required")
    validated = _validated_task_reference(cursor_reference, task_root, "cursor", artifact_type="step_cursor")
    from concepts.target_task.store import load_cursor_snapshot

    try:
        persisted = load_cursor_snapshot(task_root, validated["repository_relative_path"])
    except Exception as exc:
        raise BoundaryError("cursor artifact invalid") from exc
    if persisted != cursor or cursor.step_ids != plan_step_ids(plan):
        raise BoundaryError("cursor does not match persisted sealed Plan state")
    try:
        events = read_ledger(Path(task_root) / "ledger.jsonl")
    except Exception as exc:
        raise BoundaryError("ledger unavailable for cursor binding") from exc
    last_cursor_ref = next((event["cursor_ref"] for event in reversed(events) if event["cursor_ref"]), None)
    if last_cursor_ref != validated["repository_relative_path"] or events[-1]["task_id"] != task_id:
        raise BoundaryError("cursor is not the latest durable ledger state")
    return validated


def _blocked_resume_phase(task_root: Path, task_id: str) -> tuple[Phase, str]:
    try:
        events = read_ledger(Path(task_root) / "ledger.jsonl")
    except Exception as exc:
        raise BoundaryError("blocked ledger unavailable") from exc
    if not events or events[-1]["task_id"] != task_id or events[-1]["phase"] != Phase.BLOCKED.value:
        raise BoundaryError("task is not durably BLOCKED")
    previous = next((event for event in reversed(events[:-1]) if event["phase"] != Phase.BLOCKED.value), None)
    if previous is None:
        raise BoundaryError("blocked origin phase unavailable")
    return Phase(previous["phase"]), hashlib.sha256(
        json.dumps(events[-1], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _recovery_evidence(
    reference: Mapping[str, Any] | None,
    *,
    task_root: Path,
    task_id: str,
    resume_phase: Phase,
    blocked_head_sha256: str,
) -> dict[str, Any]:
    if reference is None:
        raise BoundaryError("recovery evidence reference required")
    validated = _validated_task_reference(reference, task_root, "recovery", artifact_type="recovery_evidence")
    raw = (Path(task_root) / validated["repository_relative_path"]).read_bytes()
    value = _canonical_object(raw, "recovery evidence", maximum=4096)
    fields = {"schema_version", "task_id", "blocked_ledger_head_sha256", "resume_phase", "status"}
    if set(value) != fields or value != {
        "schema_version": "1",
        "task_id": task_id,
        "blocked_ledger_head_sha256": blocked_head_sha256,
        "resume_phase": resume_phase.value,
        "status": "PASS",
    }:
        raise BoundaryError("recovery evidence binding mismatch")
    return validated


def admit_transition(
    current_phase: Phase,
    action: LunaAction,
    *,
    resume_phase: Phase | None = None,
    task_root: Path | None = None,
    task_id: str | None = None,
    recovery_evidence_reference: Mapping[str, Any] | None = None,
    recovery_receipt: Mapping[str, Any] | None = None,
    fix_loop_state: Mapping[str, Any] | None = None,
    material_findings_reference: Mapping[str, Any] | None = None,
    accepted_plan_reference: Mapping[str, Any] | None = None,
    plan_qualification_receipt: Mapping[str, Any] | None = None,
    cursor: StepCursor | None = None,
    cursor_reference: Mapping[str, Any] | None = None,
    candidate_reference: Mapping[str, Any] | None = None,
    deterministic_validation_receipt: Mapping[str, Any] | None = None,
    find_loop_state: Mapping[str, Any] | None = None,
    integration_receipt: Mapping[str, Any] | None = None,
    remote_state_reference: Mapping[str, Any] | None = None,
    remote_verification_receipt: Mapping[str, Any] | None = None,
) -> TransitionResult:
    """Admit a phase transition only when its exact durable evidence is bound."""
    if action is LunaAction.STOP:
        return next_phase(current_phase, action, resume_phase=resume_phase)

    if current_phase is Phase.BLOCKED and action is LunaAction.RECOVER:
        if task_root is None or task_id is None or resume_phase is None:
            raise BoundaryError("RECOVER requires task identity and resume phase")
        durable_phase, blocked_head = _blocked_resume_phase(task_root, task_id)
        if resume_phase is not durable_phase:
            raise BoundaryError("resume phase does not match durable blocked origin")
        recovery_subject = _recovery_evidence(
            recovery_evidence_reference,
            task_root=task_root,
            task_id=task_id,
            resume_phase=resume_phase,
            blocked_head_sha256=blocked_head,
        )
        _pass_receipt(
            recovery_receipt,
            "recovery",
            task_root,
            task_id,
            recovery_subject,
            subject_artifact_type="recovery_evidence",
        )
        return next_phase(current_phase, action, resume_phase=resume_phase)

    if current_phase is Phase.PLAN_REVIEW and action is LunaAction.ADVANCE:
        if task_root is None or task_id is None or fix_loop_state is None:
            raise BoundaryError("PLAN_SEALED requires task identity and complete Fix Loop")
        plan_ref, plan = _validated_plan(task_root, task_id, accepted_plan_reference)
        if not fix_loop_complete(fix_loop_state):
            raise BoundaryError("PLAN_SEALED requires a complete Fix Loop")
        mission_sha = _mission_sha256(task_root, task_id)
        if (
            fix_loop_state.get("TARGET_TASK_SHA256") != mission_sha
            or fix_loop_state.get("REVIEWED_ARTIFACT_SHA256") != plan_ref["sha256"]
        ):
            raise BoundaryError("Fix Loop is not bound to the mission and accepted Plan")
        _, open_findings = _material_findings(
            material_findings_reference,
            task_root=task_root,
            task_id=task_id,
            expected_sha256=fix_loop_state["MATERIAL_FINDINGS_SHA256"],
        )
        if open_findings:
            raise BoundaryError("accepted Plan still has open material findings")
        _pass_receipt(
            plan_qualification_receipt,
            "plan_qualification",
            task_root,
            task_id,
            plan_ref,
            subject_artifact_type="sealed_plan",
        )

    if current_phase is Phase.PLAN_SEALED and action is LunaAction.ADVANCE:
        if task_root is None or task_id is None:
            raise BoundaryError("STEP_EXECUTING requires task identity")
        _, plan = _validated_plan(task_root, task_id, accepted_plan_reference)
        _validated_cursor(task_root, task_id, cursor, cursor_reference, plan)
        if cursor is None or cursor.status is not CursorStatus.STEP_READY or cursor.current_index != 0:
            raise BoundaryError("STEP_EXECUTING requires the initial persisted STEP_READY cursor")

    if current_phase is Phase.STEP_EXECUTING and action is LunaAction.ADVANCE:
        if task_root is None or task_id is None:
            raise BoundaryError("STEP_VALIDATED requires task identity")
        _, plan = _validated_plan(task_root, task_id, accepted_plan_reference)
        _validated_cursor(task_root, task_id, cursor, cursor_reference, plan)
        if cursor is None or cursor.status is not CursorStatus.EXECUTION_COMPLETE:
            raise BoundaryError("STEP_VALIDATED requires complete sealed-Plan cursor")

    if current_phase is Phase.STEP_VALIDATED and action is LunaAction.ADVANCE:
        candidate = _validated_task_reference(
            candidate_reference, Path(task_root) if task_root is not None else Path("."),
            "candidate", artifact_type="candidate_manifest"
        ) if task_root is not None else None
        _pass_receipt(
            deterministic_validation_receipt,
            "deterministic_validation",
            task_root,
            task_id,
            candidate,
            subject_artifact_type="candidate_manifest",
        )

    if current_phase is Phase.CANDIDATE_FROZEN and action is LunaAction.ADVANCE:
        if task_root is None:
            raise BoundaryError("FINAL_REVIEW requires candidate evidence")
        _validated_task_reference(candidate_reference, task_root, "candidate", artifact_type="candidate_manifest")

    if current_phase is Phase.FINAL_REVIEW and action is LunaAction.ADVANCE:
        if task_root is None or task_id is None or find_loop_state is None:
            raise BoundaryError("integration requires task identity and complete Find Loop")
        candidate = _validated_task_reference(candidate_reference, task_root, "candidate", artifact_type="candidate_manifest")
        if not find_loop_complete(find_loop_state):
            raise BoundaryError("integration requires a complete Find Loop")
        mission_sha = _mission_sha256(task_root, task_id)
        if (
            find_loop_state.get("TARGET_TASK_SHA256") != mission_sha
            or find_loop_state.get("REVIEWED_ARTIFACT_SHA256") != candidate["sha256"]
        ):
            raise BoundaryError("Find Loop is not bound to the frozen candidate")
        _, open_findings = _material_findings(
            material_findings_reference,
            task_root=task_root,
            task_id=task_id,
            expected_sha256=find_loop_state["MATERIAL_FINDINGS_SHA256"],
        )
        if open_findings:
            raise BoundaryError("integration requires no open material findings")
        _pass_receipt(
            integration_receipt,
            "integration",
            task_root,
            task_id,
            candidate,
            subject_artifact_type="candidate_manifest",
        )

    if current_phase is Phase.INTEGRATED and action is LunaAction.ADVANCE:
        if task_root is None or task_id is None or candidate_reference is None:
            raise BoundaryError("remote verification requires the frozen candidate")
        candidate = _validated_task_reference(candidate_reference, task_root, "candidate", artifact_type="candidate_manifest")
        candidate_value = validate_candidate_manifest_dict(_canonical_object((Path(task_root) / candidate["repository_relative_path"]).read_bytes(), "candidate"))
        remote_state = _validated_task_reference(
            remote_state_reference,
            Path(task_root) if task_root is not None else Path("."),
            "remote_state",
            artifact_type="remote_verification_manifest",
        ) if task_root is not None else None
        remote_value = validate_remote_verification_manifest_dict(_canonical_object((Path(task_root) / remote_state["repository_relative_path"]).read_bytes(), "remote_state"))
        if (remote_value["expected_commit"] != candidate_value["candidate_commit"]
                or remote_value["expected_tree"] != candidate_value["candidate_tree"]):
            raise BoundaryError("remote verification is not bound to the candidate")
        _pass_receipt(
            remote_verification_receipt,
            "remote_verification",
            task_root,
            task_id,
            remote_state,
            subject_artifact_type="remote_verification_manifest",
        )

    return next_phase(current_phase, action, resume_phase=resume_phase)


def _latest_non_null(events: list[Mapping[str, Any]], field: str) -> Any:
    return next((event[field] for event in reversed(events) if event.get(field) is not None), None)


def admit_and_persist_transition(
    current_phase: Phase,
    action: LunaAction,
    *,
    task_root: Path,
    task_id: str,
    event_id: str,
    blocker: str | None = None,
    **gate_evidence: Any,
) -> dict[str, Any]:
    """Apply one high-level gate and append the resulting durable phase fact."""
    events = read_ledger(Path(task_root) / "ledger.jsonl")
    if not events or events[-1]["task_id"] != task_id or events[-1]["phase"] != current_phase.value:
        raise BoundaryError("current phase does not match durable ledger tail")
    result = admit_transition(
        current_phase,
        action,
        task_root=task_root,
        task_id=task_id,
        **gate_evidence,
    )
    if result.phase is current_phase and current_phase in {Phase.PLAN_REVIEW, Phase.STEP_EXECUTING, Phase.FINAL_REVIEW}:
        raise BoundaryError("same-phase progress must use its dedicated durable transition helper")

    accepted_plan_path = _latest_non_null(events, "accepted_plan_ref")
    cursor_path = _latest_non_null(events, "cursor_ref")
    request_path = None
    result_path = None
    receipt_path = None
    status = "READY"
    validation = "NOT_RUN"

    def path_of(name: str, artifact_type: str | None = None) -> str | None:
        value = gate_evidence.get(name)
        if value is None:
            return None
        if name.endswith("_receipt") and isinstance(value, Mapping) and set(value) == {"status", "reference"}:
            value = value["reference"]
        return _validated_task_reference(value, task_root, name, artifact_type=artifact_type)["repository_relative_path"]

    if result.phase is Phase.BLOCKED:
        request_path = _latest_non_null(events, "request_ref")
        result_path = _latest_non_null(events, "result_ref")
        receipt_path = _latest_non_null(events, "receipt_ref")
        status, validation = "BLOCKED", "UNKNOWN"
        blocker = blocker or "STOP_REQUESTED"
    elif result.phase is Phase.PLAN_DRAFTED:
        status = "READY"
    elif result.phase is Phase.PLAN_REVIEW:
        status = "READY"
    elif result.phase is Phase.PLAN_SEALED:
        accepted_plan_path = path_of("accepted_plan_reference", "sealed_plan")
        result_path = accepted_plan_path
        receipt_path = path_of("plan_qualification_receipt", "validation_receipt")
        status, validation = "COMPLETE", "PASS"
    elif result.phase is Phase.STEP_EXECUTING:
        cursor_path = path_of("cursor_reference", "step_cursor") or cursor_path
        status, validation = "READY", "PASS"
    elif result.phase is Phase.STEP_VALIDATED:
        status, validation = "EXECUTION_COMPLETE", "PASS"
    elif result.phase is Phase.CANDIDATE_FROZEN:
        result_path = path_of("candidate_reference", "candidate_manifest")
        receipt_path = path_of("deterministic_validation_receipt", "validation_receipt")
        status, validation = "COMPLETE", "PASS"
    elif result.phase is Phase.FINAL_REVIEW:
        result_path = path_of("candidate_reference", "candidate_manifest")
        status = "READY"
    elif result.phase is Phase.INTEGRATED:
        result_path = path_of("candidate_reference", "candidate_manifest")
        receipt_path = path_of("integration_receipt", "validation_receipt")
        status, validation = "INTEGRATED", "PASS"
    elif result.phase is Phase.CLOSED:
        result_path = path_of("remote_state_reference", "remote_verification_manifest")
        receipt_path = path_of("remote_verification_receipt", "validation_receipt")
        status, validation = "CLOSED", "PASS"
    if current_phase is Phase.BLOCKED and action is LunaAction.RECOVER:
        result_path = path_of("recovery_evidence_reference", "recovery_evidence")
        receipt_path = path_of("recovery_receipt", "validation_receipt")
        status, validation, blocker = "READY", "PASS", None

    latest_cursor = None
    if cursor_path is not None:
        from concepts.target_task.store import load_cursor_snapshot
        latest_cursor = load_cursor_snapshot(task_root, cursor_path)
    actions = allowed_actions(result.phase)
    if current_phase is Phase.BLOCKED and action is LunaAction.RECOVER and result.phase is Phase.STEP_EXECUTING and latest_cursor is not None:
        actions = _cursor_actions(latest_cursor, Phase.STEP_EXECUTING)
        status = {
            CursorStatus.STEP_READY: "READY",
            CursorStatus.OPERATION_ADMITTED: "ADMITTED",
            CursorStatus.OPERATION_FAILED: "FAILED",
            CursorStatus.EXECUTION_OUTCOME_UNKNOWN: "UNKNOWN",
            CursorStatus.STEP_AWAITING_ADVANCE: "AWAITING_ADVANCE",
            CursorStatus.EXECUTION_COMPLETE: "EXECUTION_COMPLETE",
        }[latest_cursor.status]
        validation = "FAIL" if status == "FAILED" else ("UNKNOWN" if status == "UNKNOWN" else "PASS")
    next_action = actions[0].value if actions else None
    ledger = AppendOnlyLedger(Path(task_root) / "ledger.jsonl")
    sequence, previous_hash = ledger.head()
    event = LedgerEvent(
        schema_version="1", sequence=sequence, event_id=event_id, task_id=task_id,
        phase=result.phase.value, accepted_plan_ref=accepted_plan_path,
        current_step=latest_cursor.current_step if latest_cursor else None,
        operation_id=latest_cursor.operation_id if latest_cursor else None,
        attempt=latest_cursor.attempt if latest_cursor else 0,
        request_ref=request_path, result_ref=result_path, cursor_ref=cursor_path,
        status=status, validation=validation, blocker=blocker,
        allowed_actions=tuple(item.value for item in actions), next_action=next_action,
        previous_event_hash=previous_hash, receipt_ref=receipt_path,
    )
    ledger.append(event)
    return {"transition": result, "event": event}


def build_luna_receipt(state: Mapping[str, Any], *, task_root: Path, structural_only: bool = False) -> bytes:
    """Build the only durable Lead object; all references resolve under task root."""
    import json

    raw = (json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    try:
        if structural_only:
            validate_state_structure_bytes(raw, expected_task_id=state.get("TASK_ID"))
        else:
            validate_state_bytes(raw, repository_root=task_root, expected_task_id=state.get("TASK_ID"))
    except BodyStateError as exc:
        raise BoundaryError(f"receipt rejected: {exc.code} at {exc.path}") from exc
    return raw


def retrieve_evidence(request: Mapping[str, Any], *, task_root: Path) -> dict[str, Any]:
    try:
        return retrieve(dict(request), repository_root=task_root)
    except RetrievalError as exc:
        raise BoundaryError(f"evidence retrieval rejected: {exc.code}") from exc


def validate_receipt(
    receipt: Mapping[str, Any], *, source_root: Path, artifact_root: Path
) -> ValidationResult:
    return _validate_receipt(receipt, root=source_root, artifact_root=artifact_root)


def advance_fix_loop(
    state: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    source_root: Path,
    artifact_root: Path,
    task_id: str,
    material_findings_reference: Mapping[str, Any],
) -> dict[str, Any]:
    state_result = validate_loop_state(state)
    if not state_result.ok:
        raise BoundaryError("invalid Fix Loop state: " + "; ".join(state_result.errors))
    validated = validate_receipt(receipt, source_root=source_root, artifact_root=artifact_root)
    if not validated.ok:
        raise BoundaryError("invalid RunSkeptic receipt: " + "; ".join(validated.errors))
    if receipt.get("INVOCATION_KIND") != "FIX_LOOP":
        raise BoundaryError("Fix Loop receipt kind mismatch")
    if receipt.get("TARGET_TASK_SHA256") != state.get("TARGET_TASK_SHA256"):
        raise BoundaryError("Target Task identity changed during Fix Loop")
    if receipt.get("SKEPTIC_SOURCE_BLOB_SHA") != state.get("SKEPTIC_SOURCE_BLOB_SHA"):
        raise BoundaryError("Skeptic source changed during Fix Loop")
    if receipt.get("APPLICABLE_COMPANION_SET_SHA256") != state.get("APPLICABLE_COMPANION_SET_SHA256"):
        raise BoundaryError("companion set changed during Fix Loop")
    finding_ref, _ = _material_findings(
        material_findings_reference,
        task_root=artifact_root,
        task_id=task_id,
        expected_sha256=receipt["MATERIAL_FINDINGS_SHA256"],
    )
    next_state = _advance_fix_loop(state, receipt)
    next_state["MATERIAL_FINDINGS_REFERENCE"] = finding_ref
    return next_state


FIND_LOOP_BINDING_FIELDS = (
    "TARGET_TASK_SHA256",
    "REVIEWED_ARTIFACT_SHA256",
    "SKEPTIC_SOURCE_BLOB_SHA",
    "APPLICABLE_COMPANION_SET_SHA256",
    "MATERIAL_FINDINGS_SHA256",
    "INVOCATION_KIND",
    "PERMISSION_MODE",
    "OPEN_ITEMS",
)


def validate_find_loop_state(state: Mapping[str, Any]) -> ValidationResult:
    errors: list[str] = []
    for name in FIND_LOOP_BINDING_FIELDS + ("MATERIAL_FINDINGS_REFERENCE",):
        if name not in state:
            errors.append(f"missing loop field: {name}")
    if errors:
        return ValidationResult(False, tuple(errors))
    for name in (
        "TARGET_TASK_SHA256",
        "REVIEWED_ARTIFACT_SHA256",
        "APPLICABLE_COMPANION_SET_SHA256",
        "MATERIAL_FINDINGS_SHA256",
    ):
        if not isinstance(state[name], str) or not HEX64.fullmatch(state[name]):
            errors.append(f"{name} must be SHA-256")
    if not isinstance(state["SKEPTIC_SOURCE_BLOB_SHA"], str) or not HEX40.fullmatch(state["SKEPTIC_SOURCE_BLOB_SHA"]):
        errors.append("SKEPTIC_SOURCE_BLOB_SHA must be a Git blob SHA")
    if state["INVOCATION_KIND"] != "FIND_LOOP":
        errors.append("loop state must be FIND_LOOP")
    if state["PERMISSION_MODE"] != "read-only":
        errors.append("Find Loop must be read-only")
    if not isinstance(state["OPEN_ITEMS"], list) or any(not isinstance(item, str) or not item for item in state["OPEN_ITEMS"]):
        errors.append("OPEN_ITEMS must be a list of bounded strings")
    passes = state.get("CONSECUTIVE_STABLE_PASSES")
    if not isinstance(passes, int) or isinstance(passes, bool) or passes < 0:
        errors.append("invalid consecutive-stable-pass count")
    if state.get("PASSES_REQUIRED", 3) != 3:
        errors.append("default Find Loop convergence requires three passes")
    return ValidationResult(not errors, tuple(errors))


def advance_find_loop(
    state: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    source_root: Path,
    artifact_root: Path,
    task_id: str,
    material_findings_reference: Mapping[str, Any],
) -> dict[str, Any]:
    state_result = validate_find_loop_state(state)
    if not state_result.ok:
        raise BoundaryError("invalid Find Loop state: " + "; ".join(state_result.errors))
    validated = validate_receipt(receipt, source_root=source_root, artifact_root=artifact_root)
    if not validated.ok:
        raise BoundaryError("invalid RunSkeptic receipt: " + "; ".join(validated.errors))
    if (
        receipt.get("INVOCATION_KIND") != "FIND_LOOP"
        or receipt.get("PERMISSION_MODE") != "read-only"
        or receipt.get("REVIEW_SCOPE") == "DELTA"
        or receipt.get("REPAIR_RUN")
    ):
        raise BoundaryError("Find Loop receipt must be a complete read-only review")
    if not isinstance(receipt.get("OPEN_ITEMS"), list):
        raise BoundaryError("Find Loop receipt must persist OPEN_ITEMS")
    for field in (
        "TARGET_TASK_SHA256", "REVIEWED_ARTIFACT_SHA256",
        "SKEPTIC_SOURCE_BLOB_SHA", "APPLICABLE_COMPANION_SET_SHA256",
    ):
        if receipt.get(field) != state.get(field):
            raise BoundaryError(f"frozen Find Loop binding changed: {field}")
    finding_ref, _ = _material_findings(
        material_findings_reference,
        task_root=artifact_root,
        task_id=task_id,
        expected_sha256=receipt["MATERIAL_FINDINGS_SHA256"],
    )
    stable = all(state[field] == receipt.get(field) for field in FIND_LOOP_BINDING_FIELDS)
    next_state = dict(state)
    next_state["CONSECUTIVE_STABLE_PASSES"] = state["CONSECUTIVE_STABLE_PASSES"] + 1 if stable else 0
    if not stable:
        next_state["MATERIAL_FINDINGS_SHA256"] = receipt.get("MATERIAL_FINDINGS_SHA256")
    next_state["MATERIAL_FINDINGS_REFERENCE"] = finding_ref
    return next_state


def find_loop_complete(state: Mapping[str, Any]) -> bool:
    result = validate_find_loop_state(state)
    return result.ok and state["CONSECUTIVE_STABLE_PASSES"] >= state.get("PASSES_REQUIRED", 3)


def persist_review_loop_transition(
    task_root: Path,
    task_id: str,
    phase: Phase,
    state: Mapping[str, Any],
    *,
    event_id: str,
    material_findings_reference: Mapping[str, Any],
    review_receipt_reference: Mapping[str, Any],
    review_request_reference: Mapping[str, Any] | None = None,
    accepted_plan_reference: Mapping[str, Any] | None = None,
    next_action: LunaAction = LunaAction.CONTINUE,
) -> dict[str, Any]:
    """Persist a complete review-loop state before the Lead relies on it."""
    validate_task_id(task_id)
    if phase is Phase.PLAN_REVIEW:
        result = validate_loop_state(state)
        kind = "fix"
    elif phase is Phase.FINAL_REVIEW:
        result = validate_find_loop_state(state)
        kind = "find"
    else:
        raise BoundaryError("review-loop state is legal only in PLAN_REVIEW or FINAL_REVIEW")
    if not result.ok:
        raise BoundaryError("invalid review-loop state: " + "; ".join(result.errors))
    finding_ref, _ = _material_findings(
        material_findings_reference, task_root=task_root, task_id=task_id,
        expected_sha256=state["MATERIAL_FINDINGS_SHA256"],
    )
    if state.get("MATERIAL_FINDINGS_REFERENCE") != finding_ref:
        raise BoundaryError("review-loop state does not carry the validated finding-set reference")
    receipt_ref = _validated_task_reference(
        review_receipt_reference, task_root, "review_receipt", artifact_type="runskeptic_receipt"
    )
    request_ref = None
    if review_request_reference is not None:
        request_ref = _validated_task_reference(
            review_request_reference, task_root, "review_request", artifact_type="role_request"
        )
    plan_path = None
    if accepted_plan_reference is not None:
        plan_path = _validated_plan(task_root, task_id, accepted_plan_reference)[0]["repository_relative_path"]
    if phase is Phase.FINAL_REVIEW and plan_path is None:
        raise BoundaryError("FINAL_REVIEW state requires the sealed Plan reference")
    state_ref = persist_loop_state_artifact(task_root, kind, state)
    ledger = AppendOnlyLedger(Path(task_root) / "ledger.jsonl")
    sequence, previous_hash = ledger.head()
    actions = tuple(action.value for action in allowed_actions(phase))
    if next_action.value not in actions:
        raise BoundaryError("next action is not legal for review phase")
    event = LedgerEvent(
        schema_version="1", sequence=sequence, event_id=event_id, task_id=task_id,
        phase=phase.value, accepted_plan_ref=plan_path, current_step=None,
        operation_id=None, attempt=0,
        request_ref=request_ref["repository_relative_path"] if request_ref else None,
        result_ref=state_ref["repository_relative_path"], cursor_ref=None,
        status="COMPLETE", validation="PASS", blocker=None,
        allowed_actions=actions, next_action=next_action.value,
        previous_event_hash=previous_hash, receipt_ref=receipt_ref["repository_relative_path"],
    )
    ledger.append(event)
    return {"event": event, "loop_state_reference": state_ref}


# --- Explicit linear sealed-Plan cursor ------------------------------------


def new_step_cursor(step_ids, *, max_attempts: int = 3) -> StepCursor:
    return StepCursor(step_ids=tuple(step_ids), max_attempts=max_attempts)


def new_step_cursor_from_plan(plan: Mapping[str, Any], *, max_attempts: int = 3) -> StepCursor:
    return new_step_cursor(plan_step_ids(plan), max_attempts=max_attempts)


def admit_operation(cursor: StepCursor, operation_id: str) -> StepCursor:
    if cursor.status is not CursorStatus.STEP_READY:
        raise BoundaryError("operation admission requires STEP_READY")
    from concepts.target_task.contracts import SAFE_ID_RE
    if not isinstance(operation_id, str) or not SAFE_ID_RE.fullmatch(operation_id):
        raise BoundaryError("operation_id must use the safe ID rules")
    if cursor.attempt >= cursor.max_attempts:
        raise BoundaryError("attempt policy exhausted")
    return replace(
        cursor,
        status=CursorStatus.OPERATION_ADMITTED,
        operation_id=operation_id,
        attempt=cursor.attempt + 1,
        successful_operation_id=None,
    )


def record_operation_outcome(cursor: StepCursor, operation_id: str, outcome: str) -> StepCursor:
    if cursor.status is not CursorStatus.OPERATION_ADMITTED:
        raise BoundaryError("operation outcome requires OPERATION_ADMITTED")
    if cursor.operation_id != operation_id:
        raise BoundaryError("operation identity mismatch")
    if outcome == "COMPLETE":
        return replace(cursor, status=CursorStatus.STEP_AWAITING_ADVANCE, successful_operation_id=operation_id)
    if outcome == "FAILED":
        return replace(cursor, status=CursorStatus.OPERATION_FAILED)
    if outcome == "UNKNOWN":
        return replace(cursor, status=CursorStatus.EXECUTION_OUTCOME_UNKNOWN)
    raise BoundaryError("outcome must be COMPLETE, FAILED, or UNKNOWN")


def record_validated_host_outcome(
    cursor: StepCursor,
    receipt: Mapping[str, Any],
    *,
    workspace_root: Path,
    source_root: Path,
    expected_task_id: str,
    expected_role: str,
    expected_step_id: str,
    expected_request_ref: Mapping[str, Any],
) -> StepCursor:
    from concepts.target_task.runtime import validate_host_role_receipt

    if cursor.status is not CursorStatus.OPERATION_ADMITTED or cursor.operation_id is None:
        raise BoundaryError("no admitted operation")
    if cursor.current_step != expected_step_id:
        raise BoundaryError("expected step does not match cursor")
    validated = validate_host_role_receipt(
        receipt,
        workspace_root=workspace_root,
        source_root=source_root,
        expected_task_id=expected_task_id,
        expected_operation_id=cursor.operation_id,
        expected_attempt=cursor.attempt,
        expected_role=expected_role,
        expected_step_id=expected_step_id,
        expected_request_ref=expected_request_ref,
        allow_test_synthetic=False,
    )
    return record_operation_outcome(cursor, cursor.operation_id, validated["status"])


def retry_operation(cursor: StepCursor) -> StepCursor:
    if cursor.status is not CursorStatus.OPERATION_FAILED:
        raise BoundaryError("retry requires OPERATION_FAILED")
    if cursor.attempt >= cursor.max_attempts:
        raise BoundaryError("attempt policy exhausted")
    return replace(cursor, status=CursorStatus.STEP_READY, operation_id=None, successful_operation_id=None)


def recover_operation(cursor: StepCursor, recovered_outcome: str) -> StepCursor:
    raise BoundaryError("operation UNKNOWN is STOP-only; evidence-bound task recovery is required")


def advance_step(cursor: StepCursor, operation_id: str) -> StepCursor:
    if cursor.status is not CursorStatus.STEP_AWAITING_ADVANCE:
        raise BoundaryError("ADVANCE requires STEP_AWAITING_ADVANCE")
    if cursor.successful_operation_id != operation_id or cursor.operation_id != operation_id:
        raise BoundaryError("ADVANCE operation identity mismatch")
    next_index = cursor.current_index + 1
    completed = cursor.step_ids[:next_index]
    if next_index == len(cursor.step_ids):
        return replace(
            cursor,
            current_index=next_index,
            completed_step_ids=completed,
            status=CursorStatus.EXECUTION_COMPLETE,
            operation_id=None,
            successful_operation_id=None,
        )
    return replace(
        cursor,
        current_index=next_index,
        completed_step_ids=completed,
        status=CursorStatus.STEP_READY,
        operation_id=None,
        attempt=0,
        successful_operation_id=None,
    )


def _cursor_actions(cursor: StepCursor, phase: Phase) -> tuple[LunaAction, ...]:
    if phase is Phase.PLAN_SEALED:
        return (LunaAction.ADVANCE, LunaAction.STOP)
    table = {
        CursorStatus.STEP_READY: (LunaAction.CONTINUE, LunaAction.STOP),
        CursorStatus.OPERATION_ADMITTED: (LunaAction.CONTINUE, LunaAction.STOP),
        CursorStatus.OPERATION_FAILED: (LunaAction.RETRY, LunaAction.STOP),
        CursorStatus.EXECUTION_OUTCOME_UNKNOWN: (LunaAction.STOP,),
        CursorStatus.STEP_AWAITING_ADVANCE: (LunaAction.ADVANCE, LunaAction.STOP),
        CursorStatus.EXECUTION_COMPLETE: (LunaAction.ADVANCE, LunaAction.STOP),
    }
    return table[cursor.status]


def _latest_cursor_path(task_root: Path) -> str | None:
    events = read_ledger(Path(task_root) / "ledger.jsonl")
    return next((event["cursor_ref"] for event in reversed(events) if event["cursor_ref"]), None)


def _ensure_new_event_id(task_root: Path, event_id: str) -> None:
    from concepts.target_task.contracts import SAFE_ID_RE
    if not isinstance(event_id, str) or not SAFE_ID_RE.fullmatch(event_id):
        raise BoundaryError("invalid event_id")
    if any(event["event_id"] == event_id for event in read_ledger(Path(task_root) / "ledger.jsonl")):
        raise BoundaryError("duplicate event_id")


def _artifact_ref_from_path(task_root: Path, relative_path: str, artifact_type: str) -> dict[str, Any]:
    target = Path(task_root) / relative_path
    if not target.is_file() or target.is_symlink():
        raise BoundaryError("durable artifact missing")
    raw = target.read_bytes()
    return {
        "reference_id": target.stem,
        "repository_relative_path": relative_path,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
        "artifact_type": artifact_type,
        "description": "durable Target Task evidence",
        "read_condition": "read by the deterministic Boundary",
    }


def _latest_operation_event(task_root: Path, task_id: str, status: str) -> Mapping[str, Any]:
    events = read_ledger(Path(task_root) / "ledger.jsonl")
    if not events or events[-1]["task_id"] != task_id or events[-1]["status"] != status:
        raise BoundaryError(f"latest durable event must be {status}")
    return events[-1]


def admit_and_persist_operation(
    task_root: Path,
    task_id: str,
    accepted_plan_reference: Mapping[str, Any],
    request: Mapping[str, Any],
    *,
    source_root: Path,
    operation_id: str,
    event_id: str,
) -> dict[str, Any]:
    """Admit one operation from the latest durable cursor and persist its evidence."""
    _ensure_new_event_id(task_root, event_id)
    plan_ref, plan = _validated_plan(task_root, task_id, accepted_plan_reference)
    events = read_ledger(Path(task_root) / "ledger.jsonl")
    if not events or events[-1]["task_id"] != task_id or events[-1]["phase"] != Phase.STEP_EXECUTING.value:
        raise BoundaryError("operation admission requires the durable execution phase")
    if any(event.get("operation_id") == operation_id for event in events):
        raise BoundaryError("operation_id already exists in task ledger")
    cursor_path = _latest_cursor_path(task_root)
    if cursor_path is None:
        raise BoundaryError("durable cursor required")
    from concepts.target_task.store import load_cursor_snapshot
    cursor = load_cursor_snapshot(task_root, cursor_path)
    if cursor.status is not CursorStatus.STEP_READY or cursor.attempt >= cursor.max_attempts:
        raise BoundaryError("operation admission requires an unexhausted STEP_READY cursor")
    step = next(step for step in plan["steps"] if step["step_id"] == cursor.current_step)
    if request.get("role") != step["role"]:
        raise BoundaryError("request role does not match sealed Plan step")
    from concepts.target_task.runtime import prepare_host_role_dispatch
    prepared = prepare_host_role_dispatch(
        {**dict(request), "task_id": task_id, "operation_id": operation_id,
         "attempt": cursor.attempt + 1, "step_id": cursor.current_step},
        task_root=task_root, source_root=source_root,
    )
    admitted = admit_operation(cursor, operation_id)
    return _persist_cursor_transition(
        task_root, task_id, Phase.STEP_EXECUTING, admitted,
        event_id=event_id, accepted_plan_reference=plan_ref,
        prior_cursor=cursor, prior_cursor_reference=_artifact_ref_from_path(task_root, cursor_path, "step_cursor"),
        request_reference=prepared["request_ref"],
        control_evidence_reference=prepared["dispatch_evidence_ref"],
    )


def accept_and_persist_operation_outcome(
    task_root: Path,
    task_id: str,
    accepted_plan_reference: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    source_root: Path,
    event_id: str,
) -> dict[str, Any]:
    """Accept only the latest admitted operation's durable, bound host outcome."""
    _ensure_new_event_id(task_root, event_id)
    plan_ref, plan = _validated_plan(task_root, task_id, accepted_plan_reference)
    event = _latest_operation_event(task_root, task_id, "ADMITTED")
    cursor_path = event["cursor_ref"]
    from concepts.target_task.store import load_cursor_snapshot
    cursor = load_cursor_snapshot(task_root, cursor_path)
    if cursor.status is not CursorStatus.OPERATION_ADMITTED or event["operation_id"] != cursor.operation_id:
        raise BoundaryError("durable admitted cursor mismatch")
    request_ref = _artifact_ref_from_path(task_root, event["request_ref"], "role_request")
    step = next(step for step in plan["steps"] if step["step_id"] == cursor.current_step)
    from concepts.target_task.runtime import validate_host_role_receipt, persist_validated_host_receipt
    validated = validate_host_role_receipt(
        receipt, workspace_root=task_root, source_root=source_root,
        expected_task_id=task_id, expected_operation_id=cursor.operation_id,
        expected_attempt=cursor.attempt, expected_role=step["role"],
        expected_step_id=cursor.current_step, expected_request_ref=request_ref,
    )
    receipt_ref = persist_validated_host_receipt(
        receipt, workspace_root=task_root, source_root=source_root,
        expected_task_id=task_id, expected_operation_id=cursor.operation_id,
        expected_attempt=cursor.attempt, expected_role=step["role"],
        expected_step_id=cursor.current_step, expected_request_ref=request_ref,
    )
    result_ref = validated["result_ref"]
    outcome = record_operation_outcome(cursor, cursor.operation_id, validated["status"])
    return _persist_cursor_transition(
        task_root, task_id, Phase.STEP_EXECUTING, outcome,
        event_id=event_id, accepted_plan_reference=plan_ref,
        prior_cursor=cursor, prior_cursor_reference=_artifact_ref_from_path(task_root, cursor_path, "step_cursor"),
        request_reference=request_ref, result_reference=result_ref,
        control_evidence_reference=receipt_ref,
    )


def _validate_cursor_progression(prior: StepCursor | None, current: StepCursor) -> None:
    if prior is None:
        if not (
            current.status is CursorStatus.STEP_READY
            and current.current_index == 0
            and current.attempt == 0
            and not current.completed_step_ids
        ):
            raise BoundaryError("initial cursor must be STEP_READY at step zero")
        return
    if current.step_ids != prior.step_ids or current.max_attempts != prior.max_attempts:
        raise BoundaryError("cursor Plan identity changed")
    legal = False
    if prior.status is CursorStatus.STEP_READY:
        legal = (
            current.status is CursorStatus.OPERATION_ADMITTED
            and current.current_index == prior.current_index
            and current.attempt == prior.attempt + 1
            and current.operation_id is not None
        )
    elif prior.status is CursorStatus.OPERATION_ADMITTED:
        legal = (
            current.current_index == prior.current_index
            and current.operation_id == prior.operation_id
            and current.attempt == prior.attempt
            and current.status in {
                CursorStatus.STEP_AWAITING_ADVANCE,
                CursorStatus.OPERATION_FAILED,
                CursorStatus.EXECUTION_OUTCOME_UNKNOWN,
            }
        )
    elif prior.status is CursorStatus.OPERATION_FAILED:
        legal = (
            current.status is CursorStatus.STEP_READY
            and current.current_index == prior.current_index
            and current.attempt == prior.attempt
            and current.operation_id is None
        )
    elif prior.status is CursorStatus.EXECUTION_OUTCOME_UNKNOWN:
        legal = (
            current.current_index == prior.current_index
            and current.operation_id == prior.operation_id
            and current.attempt == prior.attempt
            and current.status in {CursorStatus.STEP_AWAITING_ADVANCE, CursorStatus.OPERATION_FAILED}
        )
    if not legal:
        raise BoundaryError("illegal durable cursor progression")


def _optional_reference_path(
    reference: Mapping[str, Any] | None,
    *,
    task_root: Path,
    label: str,
    artifact_type: str,
) -> str | None:
    if reference is None:
        return None
    return _validated_task_reference(reference, task_root, label, artifact_type=artifact_type)["repository_relative_path"]


def _persist_cursor_transition(
    task_root: Path,
    task_id: str,
    phase: Phase,
    cursor: StepCursor,
    *,
    event_id: str,
    accepted_plan_reference: Mapping[str, Any],
    prior_cursor: StepCursor | None = None,
    prior_cursor_reference: Mapping[str, Any] | None = None,
    request_reference: Mapping[str, Any] | None = None,
    result_reference: Mapping[str, Any] | None = None,
    control_evidence_reference: Mapping[str, Any] | None = None,
    blocker: str | None = None,
) -> dict[str, Any]:
    """Publish a legal cursor snapshot, then append the bound ledger fact."""
    validate_task_id(task_id)
    if phase not in {Phase.PLAN_SEALED, Phase.STEP_EXECUTING}:
        raise BoundaryError("cursor transitions are legal only while sealed or executing")
    plan_ref, plan = _validated_plan(Path(task_root), task_id, accepted_plan_reference)
    if cursor.step_ids != plan_step_ids(plan):
        raise BoundaryError("cursor does not match sealed Plan")
    latest = _latest_cursor_path(task_root)
    if prior_cursor is None:
        if prior_cursor_reference is not None or latest is not None:
            raise BoundaryError("initial cursor cannot replace existing durable cursor state")
    else:
        if prior_cursor_reference is None:
            raise BoundaryError("prior cursor reference required")
        prior_ref = _validated_task_reference(
            prior_cursor_reference, task_root, "prior_cursor", artifact_type="step_cursor"
        )
        from concepts.target_task.store import load_cursor_snapshot
        if load_cursor_snapshot(task_root, prior_ref["repository_relative_path"]) != prior_cursor:
            raise BoundaryError("prior cursor reference mismatch")
        if latest != prior_ref["repository_relative_path"]:
            raise BoundaryError("stale cursor transition")
    _validate_cursor_progression(prior_cursor, cursor)

    status_by_cursor = {
        CursorStatus.STEP_READY: "READY",
        CursorStatus.OPERATION_ADMITTED: "ADMITTED",
        CursorStatus.OPERATION_FAILED: "FAILED",
        CursorStatus.EXECUTION_OUTCOME_UNKNOWN: "UNKNOWN",
        CursorStatus.STEP_AWAITING_ADVANCE: "AWAITING_ADVANCE",
    }
    if cursor.status is CursorStatus.EXECUTION_COMPLETE:
        raise BoundaryError("execution completion must be persisted by advance_and_persist_step")
    status = status_by_cursor[cursor.status]
    validation = {
        "FAILED": "FAIL",
        "UNKNOWN": "UNKNOWN",
    }.get(status, "PASS")

    request_path = _optional_reference_path(
        request_reference, task_root=task_root, label="request", artifact_type="role_request"
    )
    result_path = _optional_reference_path(
        result_reference, task_root=task_root, label="result", artifact_type="role_result_manifest"
    )
    evidence_type = "dispatch_evidence" if cursor.status is CursorStatus.OPERATION_ADMITTED else "host_receipt"
    evidence_path = _optional_reference_path(
        control_evidence_reference, task_root=task_root, label="control_evidence", artifact_type=evidence_type
    )
    if cursor.status is CursorStatus.OPERATION_ADMITTED and (request_path is None or evidence_path is None or result_path is not None):
        raise BoundaryError("admission requires request and dispatch evidence only")
    if cursor.status in {
        CursorStatus.OPERATION_FAILED,
        CursorStatus.EXECUTION_OUTCOME_UNKNOWN,
        CursorStatus.STEP_AWAITING_ADVANCE,
    } and (request_path is None or result_path is None or evidence_path is None):
        raise BoundaryError("operation outcome requires request, result manifest, and host receipt")
    if cursor.status is CursorStatus.STEP_READY and any(
        value is not None for value in (request_path, result_path, evidence_path)
    ):
        raise BoundaryError("STEP_READY cursor cannot retain an operation artifact")

    cursor_ref = persist_cursor_snapshot(Path(task_root), cursor)
    ledger = AppendOnlyLedger(Path(task_root) / "ledger.jsonl")
    sequence, previous_hash = ledger.head()
    actions = _cursor_actions(cursor, phase)
    next_action = actions[0]
    event = LedgerEvent(
        schema_version="1", sequence=sequence, event_id=event_id, task_id=task_id,
        phase=phase.value, accepted_plan_ref=plan_ref["repository_relative_path"],
        current_step=cursor.current_step, operation_id=cursor.operation_id,
        attempt=cursor.attempt, request_ref=request_path, result_ref=result_path,
        cursor_ref=cursor_ref["repository_relative_path"], status=status,
        validation=validation, blocker=blocker,
        allowed_actions=tuple(action.value for action in actions), next_action=next_action.value,
        previous_event_hash=previous_hash, receipt_ref=evidence_path,
    )
    ledger.append(event)
    return {"cursor": cursor, "cursor_reference": cursor_ref, "event": event}


def persist_cursor_transition(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Internal-compatible entry point restricted to initial cursor serialization."""
    cursor = kwargs.get("cursor")
    if cursor is None and len(args) >= 4:
        cursor = args[3]
    if not isinstance(cursor, StepCursor) or cursor.status is not CursorStatus.STEP_READY or cursor.attempt != 0:
        raise BoundaryError("generic cursor persistence cannot publish operation outcomes")
    if kwargs.get("prior_cursor") is not None or kwargs.get("prior_cursor_reference") is not None:
        raise BoundaryError("generic cursor persistence is restricted to initial cursor serialization")
    return _persist_cursor_transition(*args, **kwargs)


def advance_and_persist_step(
    task_root: Path,
    task_id: str,
    phase: Phase = Phase.STEP_EXECUTING,
    cursor: StepCursor | None = None,
    *,
    operation_id: str | None = None,
    event_id: str,
    accepted_plan_reference: Mapping[str, Any] | None = None,
    cursor_reference: Mapping[str, Any] | None = None,
    request_reference: Mapping[str, Any] | None = None,
    result_reference: Mapping[str, Any] | None = None,
    host_receipt_reference: Mapping[str, Any] | None = None,
    source_root: Path | None = None,
) -> dict[str, Any]:
    """Consume exactly the latest durable AWAITING_ADVANCE operation once."""
    _ensure_new_event_id(task_root, event_id)
    if phase is not Phase.STEP_EXECUTING:
        raise BoundaryError("step acceptance is legal only during execution")
    latest_event = _latest_operation_event(task_root, task_id, "AWAITING_ADVANCE")
    if accepted_plan_reference is None:
        accepted_plan_reference = _artifact_ref_from_path(task_root, latest_event["accepted_plan_ref"], "sealed_plan")
    if cursor is None:
        from concepts.target_task.store import load_cursor_snapshot
        cursor = load_cursor_snapshot(task_root, latest_event["cursor_ref"])
    if operation_id is None:
        operation_id = latest_event["operation_id"]
    if cursor_reference is None:
        cursor_reference = _artifact_ref_from_path(task_root, latest_event["cursor_ref"], "step_cursor")
    if request_reference is None:
        request_reference = _artifact_ref_from_path(task_root, latest_event["request_ref"], "role_request")
    if result_reference is None:
        result_reference = _artifact_ref_from_path(task_root, latest_event["result_ref"], "role_result_manifest")
    if host_receipt_reference is None:
        host_receipt_reference = _artifact_ref_from_path(task_root, latest_event["receipt_ref"], "host_receipt")
    plan_ref, plan = _validated_plan(task_root, task_id, accepted_plan_reference)
    _validated_cursor(task_root, task_id, cursor, cursor_reference, plan)
    if cursor.status is not CursorStatus.STEP_AWAITING_ADVANCE:
        raise BoundaryError("step acceptance requires STEP_AWAITING_ADVANCE")
    if cursor.operation_id != operation_id or cursor.successful_operation_id != operation_id:
        raise BoundaryError("accepted operation identity mismatch")
    if source_root is not None:
        receipt_raw = read_content_addressed_artifact(task_root, host_receipt_reference["repository_relative_path"])
        receipt = _canonical_object(receipt_raw, "host receipt", maximum=4096)
        step = next(step for step in plan["steps"] if step["step_id"] == cursor.current_step)
        from concepts.target_task.runtime import validate_host_role_receipt
        validate_host_role_receipt(
            receipt, workspace_root=task_root, source_root=source_root,
            expected_task_id=task_id, expected_operation_id=operation_id,
            expected_attempt=cursor.attempt, expected_role=step["role"],
            expected_step_id=cursor.current_step, expected_request_ref=request_reference,
        )
    request_path = _optional_reference_path(
        request_reference, task_root=task_root, label="request", artifact_type="role_request"
    )
    result_path = _optional_reference_path(
        result_reference, task_root=task_root, label="result", artifact_type="role_result_manifest"
    )
    receipt_path = _optional_reference_path(
        host_receipt_reference, task_root=task_root, label="host_receipt", artifact_type="host_receipt"
    )
    after = advance_step(cursor, operation_id)
    after_ref = persist_cursor_snapshot(task_root, after)
    ledger = AppendOnlyLedger(Path(task_root) / "ledger.jsonl")
    sequence, previous_hash = ledger.head()
    actions = _cursor_actions(after, phase)
    event = LedgerEvent(
        schema_version="1", sequence=sequence, event_id=event_id, task_id=task_id,
        phase=phase.value, accepted_plan_ref=plan_ref["repository_relative_path"],
        current_step=after.current_step, operation_id=operation_id, attempt=cursor.attempt,
        request_ref=request_path, result_ref=result_path,
        cursor_ref=after_ref["repository_relative_path"], status="STEP_ACCEPTED",
        validation="PASS", blocker=None,
        allowed_actions=tuple(action.value for action in actions), next_action=actions[0].value,
        previous_event_hash=previous_hash, receipt_ref=receipt_path,
    )
    ledger.append(event)
    return {"cursor": after, "cursor_reference": after_ref, "event": event}


__all__ = [
    "BoundaryError",
    "admit_transition",
    "admit_and_persist_transition",
    "build_luna_receipt",
    "retrieve_evidence",
    "validate_receipt",
    "validate_loop_state",
    "advance_fix_loop",
    "fix_loop_complete",
    "validate_find_loop_state",
    "advance_find_loop",
    "find_loop_complete",
    "persist_review_loop_transition",
    "new_step_cursor",
    "new_step_cursor_from_plan",
    "admit_operation",
    "admit_and_persist_operation",
    "accept_and_persist_operation_outcome",
    "record_operation_outcome",
    "record_validated_host_outcome",
    "retry_operation",
    "recover_operation",
    "advance_step",
    "persist_cursor_transition",
    "advance_and_persist_step",
]
