#!/usr/bin/env python3
"""Mechanically decide whether one disposable real-host Target Task smoke passed."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from capabilities.runskeptic_receipt.runskeptic_receipt import validate_receipt  # noqa: E402
from concepts.target_task.contracts import CursorStatus, Phase  # noqa: E402
from concepts.target_task.runtime import RuntimeAdapterError, validate_host_role_receipt  # noqa: E402
from concepts.target_task.store import load_plan_artifact, read_ledger  # noqa: E402
from concepts.target_task.trigger import rediscover_task  # noqa: E402


class SmokeError(ValueError):
    pass


def canonical_json_file(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SmokeError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise SmokeError(f"JSON object required: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeError(message)


def collect_review_receipts(task_root: Path) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    review_root = task_root / "reviews"
    if not review_root.is_dir():
        return receipts
    for path in sorted(review_root.rglob("*.json")):
        value = canonical_json_file(path)
        if "INVOCATION_KIND" in value:
            result = validate_receipt(value, root=ROOT, artifact_root=task_root)
            require(result.ok, f"invalid RunSkeptic receipt {path}: {'; '.join(result.errors)}")
            receipts.append(value)
    return receipts


def stable_count(receipts: list[dict[str, Any]], kind: str) -> int:
    selected = [r for r in receipts if r.get("INVOCATION_KIND") == kind]
    if not selected:
        return 0
    fields = (
        "TARGET_TASK_SHA256", "REVIEWED_ARTIFACT_SHA256", "SKEPTIC_SOURCE_BLOB_SHA",
        "APPLICABLE_COMPANION_SET_SHA256", "MATERIAL_FINDINGS_SHA256", "INVOCATION_KIND", "PERMISSION_MODE",
    )
    count = 0
    previous = None
    for receipt in selected:
        binding = tuple(receipt.get(field) for field in fields)
        if kind == "FIX_LOOP":
            qualifying = (
                receipt.get("FINDING_CATEGORIES") == ["PASS"]
                and receipt.get("FINAL_OUTPUT_CATEGORY") == "HANDLED"
                and not receipt.get("OPEN_ITEMS")
                and not receipt.get("REPAIR_RUN")
                and receipt.get("REVIEW_SCOPE") != "DELTA"
            )
        else:
            qualifying = receipt.get("PERMISSION_MODE") == "read-only"
        count = count + 1 if qualifying and binding == previous else (1 if qualifying else 0)
        previous = binding
    return count


def validate_host_receipts(task_root: Path) -> set[str]:
    receipt_root = task_root / "receipts"
    require(receipt_root.is_dir(), "receipts directory missing")
    roles: set[str] = set()
    validated_count = 0
    for path in sorted(receipt_root.glob("*.json")):
        receipt = canonical_json_file(path)
        if set(receipt) != {
            "schema_version", "task_id", "operation_id", "attempt", "role", "step_id", "status",
            "summary", "request_ref", "result_ref", "dispatch_evidence_ref", "synthetic",
        }:
            continue
        evidence_ref = receipt["dispatch_evidence_ref"]
        require(isinstance(evidence_ref, dict), f"production dispatch evidence missing: {path}")
        evidence_path = task_root / evidence_ref["repository_relative_path"]
        evidence = canonical_json_file(evidence_path)
        try:
            validate_host_role_receipt(
                receipt,
                workspace_root=task_root,
                source_root=ROOT,
                expected_task_id=evidence["task_id"],
                expected_operation_id=evidence["operation_id"],
                expected_attempt=evidence["attempt"],
                expected_role=evidence["role"],
                expected_step_id=evidence["step_id"],
                expected_request_ref=evidence["request_ref"],
            )
        except RuntimeAdapterError as exc:
            raise SmokeError(f"invalid host receipt {path}: {exc}") from exc
        roles.add(receipt["role"])
        validated_count += 1
    require(validated_count >= 3, "fewer than three real host receipts")
    require("planner" in roles, "real Planner receipt missing")
    require(bool(roles & {"skeptic", "reviewer"}), "real Reviewer/Skeptic receipt missing")
    require("worker" in roles, "real Worker receipt missing")
    return roles


def run_negative_probe(task_root: Path) -> None:
    paths = sorted((task_root / "receipts").glob("*.json"))
    source = next((canonical_json_file(path) for path in paths if "request_ref" in canonical_json_file(path)), None)
    require(source is not None, "no receipt available for negative probe")
    evidence_ref = source["dispatch_evidence_ref"]
    evidence = canonical_json_file(task_root / evidence_ref["repository_relative_path"])
    ledger_path = task_root / "ledger.jsonl"
    before = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    bad = dict(source)
    bad["body"] = "forbidden substantive body"
    try:
        validate_host_role_receipt(
            bad,
            workspace_root=task_root,
            source_root=ROOT,
            expected_task_id=evidence["task_id"],
            expected_operation_id=evidence["operation_id"],
            expected_attempt=evidence["attempt"],
            expected_role=evidence["role"],
            expected_step_id=evidence["step_id"],
            expected_request_ref=evidence["request_ref"],
        )
    except RuntimeAdapterError:
        pass
    else:
        raise SmokeError("body-bearing receipt was accepted")
    after = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    require(before == after, "negative probe changed durable state")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-root", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--expected-mission-file", required=True)
    parser.add_argument("--claude-result", required=True)
    args = parser.parse_args()

    tasks_root = Path(args.tasks_root).resolve()
    task_id = args.task_id
    task_root = tasks_root / task_id
    expected_mission = Path(args.expected_mission_file).read_bytes()
    result_path = Path(args.claude_result)
    require(result_path.is_file() and result_path.stat().st_size > 0, "Claude result missing")

    found = rediscover_task(tasks_root, task_id)
    actual_mission = (task_root / found.mission_relative_path).read_bytes()
    require(actual_mission == expected_mission, "exact mission bytes differ")
    require(found.accepted_plan_ref is not None, "sealed Plan reference missing")
    plan = load_plan_artifact(task_root, found.accepted_plan_ref)
    require(plan["task_id"] == task_id and plan["mission_sha256"] == found.mission_sha256, "Plan binding mismatch")
    require(found.cursor is not None, "durable cursor missing")
    require(found.cursor.status is CursorStatus.EXECUTION_COMPLETE, "cursor not complete")
    require(len(found.cursor.completed_step_ids) >= 2, "fewer than two accepted steps")

    events = read_ledger(task_root / "ledger.jsonl")
    phases = {event["phase"] for event in events}
    for phase in (
        Phase.MISSION_PERSISTED.value,
        Phase.PLAN_REVIEW.value,
        Phase.PLAN_SEALED.value,
        Phase.STEP_EXECUTING.value,
        Phase.STEP_VALIDATED.value,
        Phase.CANDIDATE_FROZEN.value,
        Phase.FINAL_REVIEW.value,
    ):
        require(phase in phases, f"lifecycle phase missing: {phase}")
    accepted = [event for event in events if event["status"] == "STEP_ACCEPTED"]
    require(len(accepted) >= 2, "two explicit STEP_ACCEPTED ledger events missing")

    roles = validate_host_receipts(task_root)
    reviews = collect_review_receipts(task_root)
    require(stable_count(reviews, "FIX_LOOP") >= 3, "Plan Fix Loop did not reach three stable qualifying receipts")
    require(stable_count(reviews, "FIND_LOOP") >= 3, "Find Loop did not reach three stable receipts")
    final_reviews = [r for r in reviews if r.get("INVOCATION_KIND") == "FIND_LOOP"]
    require(final_reviews[-1].get("FINDING_CATEGORIES") == ["PASS"] and not final_reviews[-1].get("OPEN_ITEMS"), "final Find Loop is stable but not clean")
    run_negative_probe(task_root)

    terminal = task_root / "terminal/receipt.json"
    require(terminal.is_file() and terminal.stat().st_size <= 4096, "compact terminal receipt missing")
    terminal_value = canonical_json_file(terminal)
    require(terminal_value.get("task_id") == task_id, "terminal task ID mismatch")
    require("body" not in terminal_value and "mission" not in terminal_value, "terminal receipt carries a body")

    print(json.dumps({
        "status": "PASS",
        "task_id": task_id,
        "completed_steps": list(found.cursor.completed_step_ids),
        "roles": sorted(roles),
        "ledger_events": len(events),
        "fix_loop_stable_passes": stable_count(reviews, "FIX_LOOP"),
        "find_loop_stable_passes": stable_count(reviews, "FIND_LOOP"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeError as exc:
        print(f"TARGET_TASK_SMOKE_INVALID: {exc}", file=sys.stderr)
        raise SystemExit(2)
