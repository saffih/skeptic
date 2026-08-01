"""One reusable, fail-closed verifier for terminal Task results."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import ArtifactRef
from .canonical import loads_strict, sha256_file
from .errors import require


def verify_task_terminal(
    task_root: Path,
    expected_parent_binding: dict[str, Any] | None = None,
    expected_delivery_kind: str | None = None,
    expected_success_outcome: str | None = None,
) -> dict[str, Any]:
    """Verify a terminal Task exactly as an external parent would."""
    from .runner import Runner

    runner = Runner(task_root, read_only=True)
    task = runner.task
    binding = task.get("parent_binding")
    if expected_parent_binding is None:
        require(binding is None, "TASK_BINDING_MISMATCH", "root Task unexpectedly has a parent binding")
    else:
        require(binding == expected_parent_binding, "TASK_BINDING_MISMATCH", "Task parent binding mismatch")
        require(task.get("task_id") == expected_parent_binding.get("child_task_id"), "TASK_ID_MISMATCH", "terminal Task identity does not match its parent binding")
    if expected_delivery_kind is not None:
        observed_delivery = task.get("delivery_kind")
        if observed_delivery is None:
            current = runner._current_plan()
            observed_delivery = current[0].get("delivery_kind") if current else None
        require(observed_delivery == expected_delivery_kind, "TASK_DELIVERY_MISMATCH", "Task delivery kind mismatch")
    terminal_events = [record for record in runner._events() if record["event"]["event_type"] == "TERMINAL_RECEIPT_RECORDED"]
    require(len(terminal_events) == 1, "TERMINAL_RECEIPT_INVALID", "terminal receipt must be unique")
    terminal = terminal_events[0]["payload"]
    require(isinstance(terminal, dict), "TERMINAL_RECEIPT_INVALID", "terminal event payload unavailable")
    receipt = terminal.get("receipt")
    require(isinstance(receipt, dict) and set(receipt) == {"ref", "sha256", "size"}, "TERMINAL_RECEIPT_INVALID", "terminal receipt reference malformed")
    ref = ArtifactRef(**receipt)
    receipt_path = runner.store.verify(ref)
    require(receipt_path.stat().st_size <= 64 * 1024 and sha256_file(receipt_path) == ref.sha256, "TERMINAL_RECEIPT_INVALID", "terminal receipt hash or size invalid")
    value = loads_strict(receipt_path.read_bytes())
    require(isinstance(value, dict) and value.get("outcome") == terminal.get("outcome"), "TERMINAL_RECEIPT_INVALID", "terminal outcome binding invalid")
    if expected_success_outcome is not None:
        require(value.get("outcome") == expected_success_outcome, "TASK_OUTCOME_MISMATCH", "unexpected successful Task outcome")
    require(runner._last_event_payload("PLAN_SEALED") is not None, "TASK_PLAN_INVALID", "terminal Task has no sealed Plan")
    plan, plan_ref = runner._current_plan() or (None, None)
    require(plan is not None and plan_ref is not None, "TASK_PLAN_INVALID", "sealed Plan artifact unavailable")
    require(len(runner._consecutive_plan_passes(plan_ref.sha256)) >= 3, "TASK_PLAN_REVIEWS_INVALID", "terminal Task lacks three unchanged Plan reviews")
    frozen = runner._last_event_payload("FINAL_SUBJECT_FROZEN")
    require(frozen is not None, "TASK_FINAL_INVALID", "terminal Task has no frozen final subject")
    require(len(runner._consecutive_final_passes(frozen["subject_sha256"])) >= 3, "TASK_FINAL_REVIEWS_INVALID", "terminal Task lacks three unchanged final reviews")
    for evidence in value.get("evidence", []):
        require(isinstance(evidence, dict) and set(evidence) == {"ref", "sha256", "size"}, "TASK_RESULT_INVALID", "terminal evidence reference malformed")
        runner.store.verify(ArtifactRef(**evidence))
    return {"task": task, "outcome": value["outcome"], "terminal_receipt": value, "terminal_ref": ref, "plan": plan, "frozen": frozen}
