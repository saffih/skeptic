from __future__ import annotations

from collections import Counter
from typing import Any

from .errors import STTError


TERMINAL = {"COMPLETE", "INSPECT_COMPLETE", "FAILED", "BLOCKED_UNKNOWN", "STOPPED", "CONTROL_STATE_FAILED"}


def derive(events: list[dict[str, Any]], *, pending_operation: dict[str, Any] | None = None) -> dict[str, Any]:
    """The only ledger-to-control-state reducer used by all control commands."""
    types = [str(event.get("event", event)["event_type"]) for event in events]
    counts = Counter(types)
    if counts["TERMINAL_RECEIPT_RECORDED"]:
        return {"status": "TERMINAL", "next_action": None}
    if pending_operation is not None:
        rejected = any(event.get("event", event)["event_type"] == "OPERATION_RESULT_REJECTED" and isinstance(event.get("payload"), dict) and event["payload"].get("operation_id") == pending_operation.get("operation_id") for event in events)
        role = pending_operation.get("role")
        action = {"planner": "DISPATCH_PLANNER", "reviewer": "DISPATCH_REVIEWER", "worker": "DISPATCH_WORKER"}.get(role, "CONTROL_STATE_FAILED")
        return {"status": "RETRYABLE" if rejected else "RUNNING", "next_action": "RETRY_OPERATION" if rejected else action, "pending_operation": pending_operation.get("operation_id")}
    if "PLAN_SEALED" not in types:
        if "PLAN_CANDIDATE_RECORDED" not in types:
            return {"status": "RUNNING", "next_action": "DISPATCH_PLANNER"}
        clean = counts["PLAN_REVIEW_RECORDED"]
        return {"status": "RUNNING", "next_action": "SEAL_PLAN" if clean >= 3 else "DISPATCH_PLAN_REVIEW"}
    if "FINAL_SUBJECT_FROZEN" not in types:
        return {"status": "RUNNING", "next_action": "EXECUTE_OR_VALIDATE_NEXT_STEP"}
    if counts["FINAL_REVIEW_RECORDED"] < 3:
        return {"status": "RUNNING", "next_action": "DISPATCH_FINAL_REVIEW"}
    if "CUTOVER_APPLIED" not in types:
        return {"status": "RUNNING", "next_action": "APPLY_CUTOVER"}
    return {"status": "RUNNING", "next_action": "WRITE_TERMINAL_RECEIPT"}
