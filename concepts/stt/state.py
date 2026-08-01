from __future__ import annotations

from collections import Counter
from typing import Any

from .errors import STTError


TERMINAL = {"COMPLETE", "FAILED", "CONTROL_STATE_FAILED"}


def derive(events: list[dict[str, Any]]) -> dict[str, Any]:
    types = [str(event["event_type"]) for event in events]
    counts = Counter(types)
    if counts["TERMINAL_RECEIPT_RECORDED"]:
        return {"status": "TERMINAL", "next_action": None}
    admitted = [event for event in events if event["event_type"] == "OPERATION_ADMITTED"]
    results = [event for event in events if event["event_type"] == "OPERATION_RESULT"]
    if len(admitted) > len(results):
        return {"status": "BLOCKED_UNKNOWN", "next_action": "RECONCILE_OPERATION"}
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
