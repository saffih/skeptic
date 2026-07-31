"""Exact `TT:` recognition, atomic task bootstrap, and fresh-session rediscovery."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from capabilities.restart_admission.restart_admission import admit_restart
from concepts.target_task.contracts import ContractError, CursorStatus, LedgerEvent, LunaAction, Phase, StepCursor, canonical_bytes, validate_task_id
from concepts.target_task.store import (
    AppendOnlyLedger,
    StoreError,
    _fsync_dir,
    load_cursor_snapshot,
    load_finding_set_artifact,
    load_loop_state_artifact,
    load_plan_artifact,
    read_content_addressed_artifact,
    read_ledger,
    verify_chain,
    write_content_addressed_artifact,
)

TRIGGER_PREFIX = "TT:"


class TriggerError(ValueError):
    pass


def parse_trigger(message: str) -> str | None:
    if not isinstance(message, str):
        raise TriggerError("MESSAGE_TYPE")
    stripped = message.lstrip()
    if not stripped.startswith(TRIGGER_PREFIX):
        return None
    mission = stripped[len(TRIGGER_PREFIX) :]
    if not mission.strip():
        raise TriggerError("EMPTY_MISSION")
    return mission


def _task_root(tasks_root: Path, task_id: str, *, must_exist: bool) -> Path:
    try:
        validate_task_id(task_id)
    except Exception as exc:
        raise TriggerError("INVALID_TASK_ID") from exc
    supplied = Path(tasks_root).expanduser()
    if supplied.is_symlink():
        raise TriggerError("TASKS_ROOT_SYMLINK")
    if must_exist:
        try:
            root = supplied.resolve(strict=True)
        except OSError as exc:
            raise TriggerError("TASKS_ROOT_INVALID") from exc
        if not root.is_dir():
            raise TriggerError("TASKS_ROOT_INVALID")
    else:
        supplied.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(supplied, 0o700)
        root = supplied.resolve(strict=True)
    target = root / task_id
    if target.parent != root:
        raise TriggerError("INVALID_TASK_ID")
    return target


@dataclass(frozen=True)
class BootstrapResult:
    task_id: str
    workspace_root: Path
    mission_reference_id: str
    mission_relative_path: str
    mission_sha256: str
    mission_byte_size: int
    ledger_head_hash: str


def bootstrap_task(mission: str, task_id: str, tasks_root: Path) -> BootstrapResult:
    """Persist the exact host-provided mission before substantive orchestration."""
    if not isinstance(mission, str) or not mission.strip():
        raise TriggerError("EMPTY_MISSION")
    final_dir = _task_root(Path(tasks_root), task_id, must_exist=False)
    if final_dir.exists():
        raise TriggerError("TASK_ALREADY_EXISTS")
    root = final_dir.parent
    tmp_dir = root / f".{task_id}.bootstrap.tmp"
    if tmp_dir.exists():
        raise TriggerError("BOOTSTRAP_TMP_EXISTS")
    tmp_dir.mkdir(mode=0o700)
    os.chmod(tmp_dir, 0o700)
    published = False
    try:
        mission_ref = write_content_addressed_artifact(
            tmp_dir,
            "mission",
            ".txt",
            mission.encode("utf-8"),
            reference_id="mission",
            artifact_type="mission",
            description="immutable exact Target Task mission suffix",
            read_condition="read only by bounded Planner and mission validators",
        )
        ledger = AppendOnlyLedger(tmp_dir / "ledger.jsonl")
        first_event = LedgerEvent(
            schema_version="1",
            sequence=0,
            event_id=f"{task_id}:bootstrap",
            task_id=task_id,
            phase=Phase.MISSION_PERSISTED.value,
            accepted_plan_ref=None,
            current_step=None,
            operation_id=None,
            attempt=0,
            request_ref=None,
            result_ref=mission_ref["repository_relative_path"],
            cursor_ref=None,
            status="COMPLETE",
            validation="PASS",
            blocker=None,
            allowed_actions=(LunaAction.CONTINUE.value, LunaAction.STOP.value),
            next_action=LunaAction.CONTINUE.value,
            previous_event_hash=None,
            receipt_ref=None,
        )
        append_result = ledger.append(first_event)
        os.rename(tmp_dir, final_dir)
        published = True
        _fsync_dir(root)
    except BaseException:
        if not published:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    return BootstrapResult(
        task_id=task_id,
        workspace_root=final_dir,
        mission_reference_id=mission_ref["reference_id"],
        mission_relative_path=mission_ref["repository_relative_path"],
        mission_sha256=mission_ref["sha256"],
        mission_byte_size=mission_ref["byte_size"],
        ledger_head_hash=append_result.head_hash,
    )


def resume_task(checkpoint_request_raw: bytes, *, workspace_root: Path | str, repository_root: Path | str | None = None) -> dict[str, Any]:
    """Admit a checkpoint whose Body-state artifacts all resolve under the task root.

    `repository_root` remains accepted for call-site compatibility but is not an
    authority for task-run artifacts.
    """
    return admit_restart(
        checkpoint_request_raw,
        repository_root=workspace_root,
        workspace_root=workspace_root,
    )


@dataclass(frozen=True)
class RediscoveredTask:
    task_id: str
    workspace_root: Path
    mission_relative_path: str
    mission_sha256: str
    mission_byte_size: int
    phase: str
    accepted_plan_ref: str | None
    plan_step_ids: tuple[str, ...]
    cursor: StepCursor | None
    current_step: str | None
    current_step_index: int | None
    operation_id: str | None
    attempt: int
    completed_step_ids: tuple[str, ...]
    successful_operation_id: str | None
    review_loop_state: dict[str, Any] | None
    review_loop_state_relative_path: str | None
    request_relative_path: str | None
    result_relative_path: str | None
    receipt_relative_path: str | None
    blocked_from_phase: str | None
    status: str
    next_action: str | None
    ledger_head_hash: str


def rediscover_task(
    tasks_root: Path,
    task_id: str,
    *,
    expected_mission_sha256: str | None = None,
    expected_ledger_head_hash: str | None = None,
) -> RediscoveredTask:
    """Reconstruct all decision-critical state from `TASKS_ROOT + TASK_ID`."""
    root = _task_root(Path(tasks_root), task_id, must_exist=True)
    if not root.is_dir() or root.is_symlink():
        raise TriggerError("TASK_NOT_FOUND")
    try:
        events = read_ledger(root / "ledger.jsonl")
    except StoreError as exc:
        raise TriggerError(f"INVALID_LEDGER:{exc.code}") from exc
    if not events or not verify_chain(events, expected_task_id=task_id):
        raise TriggerError("INVALID_LEDGER")
    first = events[0]
    if first["phase"] != Phase.MISSION_PERSISTED.value or first["result_ref"] is None:
        raise TriggerError("MISSION_EVENT_MISSING")
    try:
        mission_raw = read_content_addressed_artifact(root, first["result_ref"])
    except StoreError as exc:
        raise TriggerError(f"MISSION_INVALID:{exc.code}") from exc
    import hashlib

    mission_sha = hashlib.sha256(mission_raw).hexdigest()
    if expected_mission_sha256 is not None and mission_sha != expected_mission_sha256:
        raise TriggerError("MISSION_IDENTITY_MISMATCH")
    tail = events[-1]
    blocked_from_phase: str | None = None
    effective_phase = tail["phase"]
    if effective_phase == Phase.BLOCKED.value:
        prior = next((event for event in reversed(events[:-1]) if event["phase"] != Phase.BLOCKED.value), None)
        if prior is None:
            raise TriggerError("BLOCKED_ORIGIN_MISSING")
        blocked_from_phase = prior["phase"]
        effective_phase = blocked_from_phase

    accepted_plan_ref = next((event["accepted_plan_ref"] for event in reversed(events) if event["accepted_plan_ref"] is not None), None)
    phases_requiring_plan = {
        Phase.PLAN_SEALED.value, Phase.STEP_EXECUTING.value, Phase.STEP_VALIDATED.value,
        Phase.CANDIDATE_FROZEN.value, Phase.FINAL_REVIEW.value, Phase.INTEGRATED.value, Phase.CLOSED.value,
    }
    if effective_phase in phases_requiring_plan and accepted_plan_ref is None:
        raise TriggerError("SEALED_PLAN_REQUIRED")
    plan_steps: tuple[str, ...] = ()
    if accepted_plan_ref is not None:
        try:
            plan = load_plan_artifact(root, accepted_plan_ref)
        except (StoreError, ContractError, OSError) as exc:
            raise TriggerError("SEALED_PLAN_INVALID") from exc
        if plan["task_id"] != task_id or plan["mission_sha256"] != mission_sha:
            raise TriggerError("SEALED_PLAN_BINDING")
        plan_steps = tuple(step["step_id"] for step in plan["steps"])

    cursor: StepCursor | None = None
    cursor_ref = next((event["cursor_ref"] for event in reversed(events) if event["cursor_ref"] is not None), None)
    phases_requiring_cursor = {
        Phase.STEP_EXECUTING.value, Phase.STEP_VALIDATED.value, Phase.CANDIDATE_FROZEN.value,
        Phase.FINAL_REVIEW.value, Phase.INTEGRATED.value, Phase.CLOSED.value,
    }
    if effective_phase in phases_requiring_cursor and cursor_ref is None:
        raise TriggerError("CURSOR_REQUIRED")
    if cursor_ref is not None:
        try:
            cursor = load_cursor_snapshot(root, cursor_ref)
        except (StoreError, ContractError, OSError) as exc:
            raise TriggerError("CURSOR_INVALID") from exc
        if not plan_steps or cursor.step_ids != plan_steps:
            raise TriggerError("CURSOR_PLAN_MISMATCH")
        state_event = tail if tail["phase"] != Phase.BLOCKED.value else next(
            event for event in reversed(events[:-1]) if event["phase"] != Phase.BLOCKED.value
        )
        if effective_phase == Phase.STEP_EXECUTING.value:
            if state_event["current_step"] != cursor.current_step:
                raise TriggerError("CURSOR_STEP_MISMATCH")
            if state_event["status"] != "STEP_ACCEPTED" and (
                state_event["operation_id"] != cursor.operation_id or state_event["attempt"] != cursor.attempt
            ):
                raise TriggerError("CURSOR_OPERATION_MISMATCH")
            if state_event["status"] == "STEP_ACCEPTED" and cursor.status not in {
                CursorStatus.STEP_READY, CursorStatus.EXECUTION_COMPLETE
            }:
                raise TriggerError("CURSOR_ACCEPTANCE_MISMATCH")
        elif effective_phase in {
            Phase.STEP_VALIDATED.value, Phase.CANDIDATE_FROZEN.value, Phase.FINAL_REVIEW.value,
            Phase.INTEGRATED.value, Phase.CLOSED.value,
        } and cursor.status.value != "EXECUTION_COMPLETE":
            raise TriggerError("INCOMPLETE_CURSOR_AFTER_EXECUTION")

    review_loop_state: dict[str, Any] | None = None
    review_loop_state_ref: str | None = None
    if effective_phase in {Phase.PLAN_REVIEW.value, Phase.FINAL_REVIEW.value}:
        expected_prefix = "state/fix-loop/" if effective_phase == Phase.PLAN_REVIEW.value else "state/find-loop/"
        phase_events = [
            event for event in events
            if event["phase"] == effective_phase
            and isinstance(event["result_ref"], str)
            and event["result_ref"].startswith(expected_prefix)
        ]
        if phase_events:
            review_loop_state_ref = phase_events[-1]["result_ref"]
            try:
                review_loop_state = load_loop_state_artifact(root, review_loop_state_ref)
                if effective_phase == Phase.PLAN_REVIEW.value:
                    from capabilities.runskeptic_receipt.runskeptic_receipt import validate_loop_state
                    validation = validate_loop_state(review_loop_state)
                else:
                    from concepts.target_task.boundary import validate_find_loop_state
                    validation = validate_find_loop_state(review_loop_state)
                if not validation.ok:
                    raise TriggerError("REVIEW_LOOP_STATE_INVALID")
                finding_ref = review_loop_state.get("MATERIAL_FINDINGS_REFERENCE")
                if not isinstance(finding_ref, dict) or finding_ref.get("sha256") != review_loop_state.get("MATERIAL_FINDINGS_SHA256"):
                    raise TriggerError("REVIEW_FINDING_SET_BINDING")
                from concepts.target_task.runtime import validate_task_artifact_reference
                validated_finding_ref = validate_task_artifact_reference(finding_ref, root, "$.MATERIAL_FINDINGS_REFERENCE")
                if validated_finding_ref["artifact_type"] != "material_findings":
                    raise TriggerError("REVIEW_FINDING_SET_TYPE")
                finding_set = load_finding_set_artifact(root, validated_finding_ref["repository_relative_path"])
                if finding_set["task_id"] != task_id:
                    raise TriggerError("REVIEW_FINDING_SET_TASK")
            except TriggerError:
                raise
            except Exception as exc:
                raise TriggerError("REVIEW_LOOP_STATE_INVALID") from exc

    ledger_head_hash = hashlib.sha256(canonical_bytes(tail)).hexdigest()
    if expected_ledger_head_hash is not None and ledger_head_hash != expected_ledger_head_hash:
        raise TriggerError("LEDGER_HEAD_MISMATCH")

    return RediscoveredTask(
        task_id=task_id,
        workspace_root=root,
        mission_relative_path=first["result_ref"],
        mission_sha256=mission_sha,
        mission_byte_size=len(mission_raw),
        phase=tail["phase"],
        accepted_plan_ref=accepted_plan_ref,
        plan_step_ids=plan_steps,
        cursor=cursor,
        current_step=cursor.current_step if cursor else tail["current_step"],
        current_step_index=cursor.current_index if cursor else None,
        operation_id=cursor.operation_id if cursor else tail["operation_id"],
        attempt=cursor.attempt if cursor else tail["attempt"],
        completed_step_ids=cursor.completed_step_ids if cursor else (),
        successful_operation_id=cursor.successful_operation_id if cursor else None,
        review_loop_state=review_loop_state,
        review_loop_state_relative_path=review_loop_state_ref,
        request_relative_path=tail["request_ref"],
        result_relative_path=tail["result_ref"],
        receipt_relative_path=tail["receipt_ref"],
        blocked_from_phase=blocked_from_phase,
        status=tail["status"],
        next_action=tail["next_action"],
        ledger_head_hash=ledger_head_hash,
    )
