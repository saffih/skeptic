"""Thin reference-only controller for the Target Task lifecycle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from concepts.target_task.boundary import (
    BoundaryError,
    accept_and_persist_operation_outcome,
    admit_and_persist_operation,
    admit_and_persist_transition,
    advance_and_persist_step,
    retry_and_persist_operation,
    retrieve_evidence,
)
from concepts.target_task.contracts import CursorStatus, LunaAction, Phase
from concepts.target_task.executable_plan import (
    ExecutablePlanError,
    load_execution_manifest,
    validate_step_references,
)
from concepts.target_task.routing import ResolvedRoute, RoutingError, resolve_lead_route, resolve_route
from concepts.target_task.runtime import validate_task_artifact_reference
from concepts.target_task.store import (
    load_cursor_snapshot,
    load_plan_artifact,
    read_ledger,
    write_content_addressed_artifact,
)
from concepts.target_task.trigger import BootstrapResult, RediscoveredTask, bootstrap_task, parse_trigger, rediscover_task


class ControllerError(ValueError):
    pass


MAX_CONTROLLER_RECEIPT_BYTES = 4096
BODY_KEYS = {"body", "content", "text", "excerpt", "transcript", "patch", "log", "stdout", "stderr"}


def _reference_from_path(root: Path, relative_path: str, artifact_type: str) -> dict[str, Any]:
    target = Path(root) / relative_path
    if not target.is_file() or target.is_symlink():
        raise ControllerError("durable artifact missing")
    raw = target.read_bytes()
    return {
        "reference_id": target.stem[:64],
        "repository_relative_path": relative_path,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
        "artifact_type": artifact_type,
        "description": "durable Target Task artifact",
        "read_condition": "read only by the deterministic controller or Boundary",
    }


def _scan_compact(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ControllerError(f"non-string compact receipt key at {path}")
            if key.lower() in BODY_KEYS:
                raise ControllerError(f"substantive body field rejected at {path}.{key}")
            _scan_compact(item, f"{path}.{key}")
    elif isinstance(value, list):
        if len(value) > 128:
            raise ControllerError(f"oversized compact receipt list at {path}")
        for index, item in enumerate(value):
            _scan_compact(item, f"{path}/{index}")
    elif isinstance(value, str) and len(value.encode("utf-8")) > 1024:
        raise ControllerError(f"oversized compact receipt string at {path}")


def compact_receipt(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ControllerError("compact receipt object required")
    result = dict(value)
    _scan_compact(result)
    try:
        raw = (json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ControllerError("compact receipt JSON") from exc
    if len(raw) > MAX_CONTROLLER_RECEIPT_BYTES:
        raise ControllerError("compact receipt too large")
    return result


def _state(tasks_root: Path, task_id: str) -> RediscoveredTask:
    try:
        return rediscover_task(tasks_root, task_id)
    except Exception as exc:
        raise ControllerError(f"task rediscovery failed: {exc}") from exc


def _tail(task_root: Path) -> dict[str, Any]:
    events = read_ledger(Path(task_root) / "ledger.jsonl")
    if not events:
        raise ControllerError("task ledger is empty")
    return events[-1]


def status(tasks_root: Path, task_id: str) -> dict[str, Any]:
    task = _state(tasks_root, task_id)
    tail = _tail(task.workspace_root)
    return compact_receipt({
        "schema_version": "1",
        "operation": "status",
        "task_id": task.task_id,
        "phase": task.phase,
        "status": task.status,
        "sealed_plan_ref": task.accepted_plan_ref,
        "current_step_id": task.current_step,
        "current_step_index": task.current_step_index,
        "operation_id": task.operation_id,
        "attempt": task.attempt,
        "completed_step_count": len(task.completed_step_ids),
        "next_action": task.next_action,
        "blocker": tail.get("blocker"),
        "ledger_head_hash": task.ledger_head_hash,
    })


def bootstrap(
    message: str,
    task_id: str,
    tasks_root: Path,
    *,
    lead_profile: Mapping[str, Any],
    current_provider: str | None = None,
) -> dict[str, Any]:
    mission = parse_trigger(message)
    if mission is None:
        raise ControllerError("exact TT: trigger required")
    try:
        result: BootstrapResult = bootstrap_task(mission, task_id, tasks_root)
        lead_route = resolve_lead_route(lead_profile, current_provider=current_provider)
    except Exception as exc:
        raise ControllerError(str(exc)) from exc
    return compact_receipt({
        "schema_version": "1",
        "operation": "bootstrap",
        "task_id": result.task_id,
        "phase": Phase.MISSION_PERSISTED.value,
        "mission_ref": result.mission_relative_path,
        "mission_sha256": result.mission_sha256,
        "mission_byte_size": result.mission_byte_size,
        "ledger_head_hash": result.ledger_head_hash,
        "lead_route": lead_route.to_dict(),
        "next_action": LunaAction.CONTINUE.value,
    })


def _validated_plan_state(task: RediscoveredTask) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if task.accepted_plan_ref is None:
        raise ControllerError("sealed Plan is unavailable")
    plan_ref = _reference_from_path(task.workspace_root, task.accepted_plan_ref, "sealed_plan")
    plan = load_plan_artifact(task.workspace_root, task.accepted_plan_ref)
    try:
        execution_ref, execution = load_execution_manifest(task.workspace_root, plan_ref, plan)
    except ExecutablePlanError as exc:
        raise ControllerError(str(exc)) from exc
    return plan_ref, plan, {"reference": execution_ref, "manifest": execution}


def _focused_retrieval_reference(step: Mapping[str, Any], *, task_root: Path) -> dict[str, Any] | None:
    recipe_ref = step.get("retrieval_recipe_ref")
    if recipe_ref is None:
        return None
    validated = validate_task_artifact_reference(recipe_ref, task_root, "$.retrieval_recipe_ref")
    raw = (Path(task_root) / validated["repository_relative_path"]).read_bytes()
    try:
        request = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ControllerError("retrieval recipe JSON") from exc
    try:
        result = retrieve_evidence(request, task_root=task_root)
    except BoundaryError as exc:
        raise ControllerError(str(exc)) from exc
    # The EXCERPT is intentionally persisted outside the Lead return.
    result_raw = (json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return write_content_addressed_artifact(
        task_root,
        "retrieval/results",
        ".json",
        result_raw,
        reference_id=f"retrieval-{hashlib.sha256(result_raw).hexdigest()[:16]}",
        artifact_type="focused_retrieval_result",
        description="bounded focused retrieval result; substantive excerpt remains outside Lead",
        read_condition="read only by the dispatched child or reviewer",
    )


def prepare(
    tasks_root: Path,
    task_id: str,
    *,
    source_root: Path,
    current_provider: str | None = None,
) -> dict[str, Any]:
    task = _state(tasks_root, task_id)
    if task.phase != Phase.STEP_EXECUTING.value or task.cursor is None or task.cursor.status is not CursorStatus.STEP_READY:
        raise ControllerError("prepare requires durable STEP_EXECUTING / STEP_READY state")
    plan_ref, _plan, execution = _validated_plan_state(task)
    step = execution["manifest"]["steps"][task.cursor.current_index]
    if step["step_id"] != task.current_step:
        raise ControllerError("execution companion current-step mismatch")
    try:
        step = validate_step_references(step, task_root=task.workspace_root, source_root=source_root)
        route: ResolvedRoute = resolve_route(step["role"], step["routing_profile"], current_provider=current_provider)
    except (ExecutablePlanError, RoutingError) as exc:
        raise ControllerError(str(exc)) from exc
    retrieval_result_ref = _focused_retrieval_reference(step, task_root=task.workspace_root)
    task_refs = list(step["resolved_task_artifact_references"])
    if retrieval_result_ref is not None:
        task_refs.append(retrieval_result_ref)
    next_attempt = task.cursor.attempt + 1
    operation_id = f"op-{step['step_id']}-{next_attempt}"
    request = {
        "schema_version": "1",
        "role": step["role"],
        "objective": step["objective"],
        "scope": step["scope"],
        "authority": step["authority"],
        "prohibitions": step["prohibitions"],
        "success_criteria": step["success_criteria"],
        "task_artifact_references": task_refs,
        "source_artifact_references": step["resolved_source_artifact_references"],
        "result_relative_path": f"{step['result_manifest_directory']}/{operation_id}.json",
    }
    try:
        persisted = admit_and_persist_operation(
            task.workspace_root,
            task_id,
            plan_ref,
            request,
            source_root=source_root,
            operation_id=operation_id,
            event_id=f"prepare-{operation_id}",
        )
    except BoundaryError as exc:
        raise ControllerError(str(exc)) from exc
    event = persisted["event"]
    return compact_receipt({
        "schema_version": "1",
        "operation": "prepare",
        "task_id": task_id,
        "operation_id": operation_id,
        "step_id": step["step_id"],
        "route": route.to_dict(),
        "request_ref": event.request_ref,
        "dispatch_evidence_ref": event.receipt_ref,
        "execution_manifest_ref": execution["reference"]["repository_relative_path"],
        "focused_retrieval_result_ref": retrieval_result_ref["repository_relative_path"] if retrieval_result_ref else None,
        "expected_result_manifest_path": request["result_relative_path"],
        "timeout_seconds": route.timeout_seconds,
        "next_action": LunaAction.CONTINUE.value,
    })


def accept(
    tasks_root: Path,
    task_id: str,
    receipt: Mapping[str, Any],
    *,
    source_root: Path,
) -> dict[str, Any]:
    task = _state(tasks_root, task_id)
    if task.phase != Phase.STEP_EXECUTING.value or task.status != "ADMITTED" or task.operation_id is None:
        raise ControllerError("accept requires the latest durable ADMITTED operation")
    plan_ref, _plan, _execution = _validated_plan_state(task)
    try:
        persisted = accept_and_persist_operation_outcome(
            task.workspace_root,
            task_id,
            plan_ref,
            receipt,
            source_root=source_root,
            event_id=f"accept-{task.operation_id}",
        )
    except BoundaryError as exc:
        raise ControllerError(str(exc)) from exc
    event = persisted["event"]
    return compact_receipt({
        "schema_version": "1", "operation": "accept", "task_id": task_id,
        "operation_id": event.operation_id, "step_id": event.current_step,
        "status": event.status, "validation": event.validation,
        "result_ref": event.result_ref, "receipt_ref": event.receipt_ref,
        "next_action": event.next_action,
    })


def advance(tasks_root: Path, task_id: str, *, source_root: Path) -> dict[str, Any]:
    task = _state(tasks_root, task_id)
    if task.phase != Phase.STEP_EXECUTING.value or task.status != "AWAITING_ADVANCE" or task.operation_id is None:
        raise ControllerError("advance requires the latest durable AWAITING_ADVANCE operation")
    try:
        persisted = advance_and_persist_step(
            task.workspace_root,
            task_id,
            event_id=f"advance-{task.operation_id}",
            source_root=source_root,
        )
    except BoundaryError as exc:
        raise ControllerError(str(exc)) from exc
    event = persisted["event"]
    after = persisted["cursor"]
    return compact_receipt({
        "schema_version": "1", "operation": "advance", "task_id": task_id,
        "accepted_operation_id": event.operation_id,
        "cursor_status": after.status.value,
        "current_step_id": after.current_step,
        "completed_step_count": len(after.completed_step_ids),
        "cursor_ref": event.cursor_ref,
        "next_action": event.next_action,
    })


def retry(tasks_root: Path, task_id: str) -> dict[str, Any]:
    task = _state(tasks_root, task_id)
    if task.phase != Phase.STEP_EXECUTING.value or task.status != "FAILED" or task.operation_id is None:
        raise ControllerError("retry requires the latest durable FAILED operation")
    try:
        persisted = retry_and_persist_operation(
            task.workspace_root,
            task_id,
            event_id=f"retry-{task.operation_id}",
        )
    except BoundaryError as exc:
        raise ControllerError(str(exc)) from exc
    event = persisted["event"]
    return compact_receipt({
        "schema_version": "1", "operation": "retry", "task_id": task_id,
        "failed_operation_id": task.operation_id,
        "status": event.status, "current_step_id": event.current_step,
        "attempt": event.attempt, "cursor_ref": event.cursor_ref,
        "next_action": event.next_action,
    })


def stop(tasks_root: Path, task_id: str, *, blocker: str = "STOP_REQUESTED") -> dict[str, Any]:
    task = _state(tasks_root, task_id)
    phase = Phase(task.phase)
    try:
        persisted = admit_and_persist_transition(
            phase,
            LunaAction.STOP,
            task_root=task.workspace_root,
            task_id=task_id,
            event_id=f"stop-{len(read_ledger(task.workspace_root / 'ledger.jsonl'))}",
            blocker=blocker,
        )
    except BoundaryError as exc:
        raise ControllerError(str(exc)) from exc
    event = persisted["event"]
    return compact_receipt({
        "schema_version": "1", "operation": "stop", "task_id": task_id,
        "phase": event.phase, "status": event.status, "blocker": event.blocker,
        "next_action": event.next_action,
    })


def handoff(tasks_root: Path, task_id: str) -> dict[str, Any]:
    task = _state(tasks_root, task_id)
    return compact_receipt({
        "schema_version": "1", "operation": "handoff", "task_id": task_id,
        "mission_sha256": task.mission_sha256,
        "ledger_head_hash": task.ledger_head_hash,
        "phase": task.phase, "status": task.status,
        "next_action": task.next_action,
    })


def resume(tasks_root: Path, handoff_receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(handoff_receipt, Mapping) or handoff_receipt.get("operation") != "handoff":
        raise ControllerError("handoff receipt required")
    try:
        task = rediscover_task(
            tasks_root,
            handoff_receipt.get("task_id"),
            expected_mission_sha256=handoff_receipt.get("mission_sha256"),
            expected_ledger_head_hash=handoff_receipt.get("ledger_head_hash"),
        )
    except Exception as exc:
        raise ControllerError(f"resume rejected: {exc}") from exc
    return compact_receipt({
        "schema_version": "1", "operation": "resume", "task_id": task.task_id,
        "phase": task.phase, "status": task.status,
        "current_step_id": task.current_step, "operation_id": task.operation_id,
        "attempt": task.attempt, "completed_step_count": len(task.completed_step_ids),
        "ledger_head_hash": task.ledger_head_hash, "next_action": task.next_action,
    })


def validate_execution(tasks_root: Path, task_id: str) -> dict[str, Any]:
    task = _state(tasks_root, task_id)
    if task.phase == Phase.STEP_VALIDATED.value:
        return compact_receipt({
            "schema_version": "1", "operation": "validate", "task_id": task_id,
            "phase": task.phase, "status": "PASS", "next_action": task.next_action,
        })
    if task.phase != Phase.STEP_EXECUTING.value or task.cursor is None or task.cursor.status is not CursorStatus.EXECUTION_COMPLETE:
        raise ControllerError("execution validation requires EXECUTION_COMPLETE cursor")
    plan_ref, plan, _execution = _validated_plan_state(task)
    tail = _tail(task.workspace_root)
    cursor_ref = _reference_from_path(task.workspace_root, tail["cursor_ref"], "step_cursor")
    events = read_ledger(task.workspace_root / "ledger.jsonl")
    completed_outcomes = [event for event in events if event["status"] == "AWAITING_ADVANCE"]
    accepted = [event for event in events if event["status"] == "STEP_ACCEPTED"]
    expected_steps = [step["step_id"] for step in plan["steps"]]
    if [event["current_step"] for event in completed_outcomes] != expected_steps:
        raise ControllerError("successful operation order does not match sealed Plan")
    if [event["operation_id"] for event in accepted] != [event["operation_id"] for event in completed_outcomes]:
        raise ControllerError("accepted operations do not match successful outcomes")
    if len(accepted) != len(plan["steps"]) or len({event["operation_id"] for event in accepted}) != len(accepted):
        raise ControllerError("sealed Plan steps were not accepted exactly once")
    try:
        persisted = admit_and_persist_transition(
            Phase.STEP_EXECUTING,
            LunaAction.ADVANCE,
            task_root=task.workspace_root,
            task_id=task_id,
            event_id="execution-validated",
            accepted_plan_reference=plan_ref,
            cursor=task.cursor,
            cursor_reference=cursor_ref,
        )
    except BoundaryError as exc:
        raise ControllerError(str(exc)) from exc
    event = persisted["event"]
    return compact_receipt({
        "schema_version": "1", "operation": "validate", "task_id": task_id,
        "phase": event.phase, "status": "PASS",
        "sealed_plan_ref": event.accepted_plan_ref,
        "cursor_ref": event.cursor_ref,
        "accepted_step_count": len(accepted),
        "next_action": event.next_action,
    })


__all__ = [
    "ControllerError", "accept", "advance", "bootstrap", "compact_receipt",
    "handoff", "prepare", "resume", "retry", "status", "stop", "validate_execution",
]
