#!/usr/bin/env python3
"""Fail-closed validator for the disposable Target Task host qualification."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from capabilities.runskeptic_receipt.runskeptic_receipt import validate_receipt  # noqa: E402
from concepts.target_task.contracts import (  # noqa: E402
    CursorStatus,
    Phase,
    parse_candidate_manifest_bytes,
    parse_remote_verification_manifest_bytes,
)
from concepts.target_task.runtime import RuntimeAdapterError, validate_host_role_receipt  # noqa: E402
from concepts.target_task.store import load_plan_artifact, read_ledger  # noqa: E402
from concepts.target_task.trigger import rediscover_task  # noqa: E402


class SmokeError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeError(message)


def json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SmokeError(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise SmokeError(f"JSON object required: {path}")
    return value


def walk(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def parse_agent_transcript(path: Path) -> dict[str, Any]:
    calls: list[dict[str, Any]] = []
    results: dict[str, dict[str, Any]] = {}
    for number, raw in enumerate(path.read_bytes().splitlines(), 1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SmokeError(f"non-JSON stream line {number}") from exc
        for item in walk(event):
            if item.get("name") == "Agent" or (item.get("type") == "tool_use" and item.get("name") == "Agent"):
                input_value = item.get("input")
                require(isinstance(input_value, dict), f"Agent call {number} has no input object")
                role = input_value.get("subagent_type")
                require(isinstance(role, str) and role, f"Agent call {number} has no subagent_type")
                calls.append({"id": item.get("id"), "role": role, "event": item})
            if item.get("type") == "tool_result" and item.get("tool_use_id"):
                results[str(item["tool_use_id"])] = item
    allowed = {"target-task-planner", "target-task-reviewer", "target-task-worker"}
    require(calls, "verbose stream contains no Agent tool calls")
    require({call["role"] for call in calls} == allowed, "Agent roles are missing or include an unapproved role")
    for call in calls:
        tool_id = call["id"]
        require(tool_id is not None and str(tool_id) in results, f"Agent result missing for {call['role']}")
        result = results[str(tool_id)]
        encoded = json.dumps(result.get("content"), ensure_ascii=False, separators=(",", ":"))
        require(len(encoded.encode("utf-8")) <= 4096, f"oversized Agent result for {call['role']}")
        for item in walk(result.get("content")):
            forbidden = {"body", "plan", "review", "patch"} & set(item)
            require(not forbidden, f"body-bearing Agent result for {call['role']}")
    return {"agent_calls": len(calls), "roles": sorted(allowed), "tool_results": len(results)}


def all_task_json(task_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    result = []
    for path in task_root.rglob("*.json"):
        try:
            result.append((path, json_object(path)))
        except SmokeError:
            continue
    return result


def validate_host_receipts(task_root: Path, events: list[dict[str, Any]]) -> tuple[set[str], list[dict[str, Any]], dict[str, Any]]:
    receipt_root = task_root / "receipts"
    require(receipt_root.is_dir(), "receipts directory missing")
    receipts: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in receipt_root.glob("*.json"):
        value = json_object(path)
        if set(value) == {
            "schema_version", "task_id", "operation_id", "attempt", "role", "step_id", "status",
            "summary", "request_ref", "result_ref", "dispatch_evidence_ref", "synthetic",
        }:
            receipts[str(path.relative_to(task_root))] = (path, value)
    roles: set[str] = set()
    seen_operations: set[str] = set()
    ordered_reviews: list[dict[str, Any]] = []
    first_receipt: dict[str, Any] | None = None
    for event in events:
        receipt_ref = event.get("receipt_ref")
        if not receipt_ref:
            continue
        pair = receipts.get(receipt_ref)
        require(pair is not None, f"ledger receipt reference is not a real receipt: {receipt_ref}")
        path, receipt = pair
        require(not receipt["synthetic"], f"synthetic production receipt: {path}")
        evidence_ref = receipt["dispatch_evidence_ref"]
        require(isinstance(evidence_ref, dict), f"dispatch evidence missing: {path}")
        evidence_path = task_root / evidence_ref["repository_relative_path"]
        evidence = json_object(evidence_path)
        try:
            validated = validate_host_role_receipt(
                receipt, workspace_root=task_root, source_root=ROOT,
                expected_task_id=evidence["task_id"], expected_operation_id=evidence["operation_id"],
                expected_attempt=evidence["attempt"], expected_role=evidence["role"],
                expected_step_id=evidence["step_id"], expected_request_ref=evidence["request_ref"],
            )
        except RuntimeAdapterError as exc:
            raise SmokeError(f"invalid host receipt {path}: {exc}") from exc
        require(receipt["operation_id"] not in seen_operations, "receipt operation counted more than once")
        seen_operations.add(receipt["operation_id"])
        roles.add(receipt["role"])
        first_receipt = first_receipt or {"receipt": receipt, "evidence": evidence}
        if event["phase"] in {Phase.PLAN_REVIEW.value, Phase.FINAL_REVIEW.value}:
            for output in validated["output_references"]:
                if output["artifact_type"] != "runskeptic_receipt":
                    continue
                review = json_object(task_root / output["repository_relative_path"])
                result = validate_receipt(review, root=ROOT, artifact_root=task_root)
                require(result.ok, f"invalid RunSkeptic receipt in ledger order: {'; '.join(result.errors)}")
                ordered_reviews.append(review)
    require({"planner", "reviewer", "worker"} <= roles, "planner, reviewer, and worker receipts are required")
    require(len(ordered_reviews) >= 6, "review receipts are not all referenced in durable ledger order")
    require(first_receipt is not None, "no durable host receipt")
    return roles, ordered_reviews, first_receipt


def negative_probes(task_root: Path, first: dict[str, Any]) -> None:
    receipt = first["receipt"]
    evidence = first["evidence"]
    ledger = task_root / "ledger.jsonl"
    before = hashlib.sha256(ledger.read_bytes()).digest()
    probes = (
        {**receipt, "body": "forbidden"},
        {**receipt, "summary": "x" * 513},
        {**receipt, "operation_id": "mismatched-operation"},
        {**receipt, "synthetic": True, "dispatch_evidence_ref": None},
    )
    for bad in probes:
        try:
            validate_host_role_receipt(
                bad, workspace_root=task_root, source_root=ROOT,
                expected_task_id=evidence["task_id"], expected_operation_id=evidence["operation_id"],
                expected_attempt=evidence["attempt"], expected_role=evidence["role"],
                expected_step_id=evidence["step_id"], expected_request_ref=receipt["request_ref"],
            )
        except RuntimeAdapterError:
            continue
        raise SmokeError("negative host receipt probe was accepted")
    require(hashlib.sha256(ledger.read_bytes()).digest() == before, "negative probe advanced durable ledger")


def loop_passes(receipts: list[dict[str, Any]], kind: str) -> int:
    selected = [r for r in receipts if r.get("INVOCATION_KIND") == kind]
    count = 0
    previous: tuple[Any, ...] | None = None
    fields = ("TARGET_TASK_SHA256", "REVIEWED_ARTIFACT_SHA256", "SKEPTIC_SOURCE_BLOB_SHA", "MATERIAL_FINDINGS_SHA256")
    for receipt in selected:
        binding = tuple(receipt.get(field) for field in fields)
        if kind == "FIX_LOOP":
            qualifying = receipt.get("FINDING_CATEGORIES") == ["PASS"] and receipt.get("FINAL_OUTPUT_CATEGORY") == "HANDLED" and not receipt.get("OPEN_ITEMS") and not receipt.get("REPAIR_RUN") and receipt.get("REVIEW_SCOPE") != "DELTA"
        else:
            qualifying = receipt.get("PERMISSION_MODE") == "read-only" and receipt.get("REVIEW_SCOPE") != "DELTA" and not receipt.get("REPAIR_RUN")
        count = count + 1 if qualifying and binding == previous else (1 if qualifying else 0)
        previous = binding
    return count


def validate_git_proof(task_root: Path, task_id: str, found: Any, source_repo: Path, remote: Path) -> dict[str, str]:
    hello = source_repo / "hello.txt"
    require(hello.is_file() and not hello.is_symlink() and hello.read_bytes() == b"hello", "hello.txt bytes are not exactly hello")
    candidate = None
    remote_manifest = None
    for path, value in all_task_json(task_root):
        try:
            candidate = parse_candidate_manifest_bytes(path.read_bytes())
        except Exception:
            try:
                remote_manifest = parse_remote_verification_manifest_bytes(path.read_bytes())
            except Exception:
                pass
    require(candidate is not None and candidate["task_id"] == task_id, "canonical candidate manifest missing or mismatched")
    require(remote_manifest is not None and remote_manifest["task_id"] == task_id, "canonical remote verification manifest missing or mismatched")
    plan_bytes = (task_root / found.accepted_plan_ref).read_bytes()
    cursor_ref = next(event["cursor_ref"] for event in reversed(read_ledger(task_root / "ledger.jsonl")) if event.get("cursor_ref"))
    cursor_bytes = (task_root / cursor_ref).read_bytes()
    require(hashlib.sha256(plan_bytes).hexdigest() == candidate["sealed_plan_sha256"], "candidate is not bound to sealed Plan bytes")
    require(hashlib.sha256(cursor_bytes).hexdigest() == candidate["completed_cursor_sha256"], "candidate is not bound to completed cursor bytes")
    require(remote_manifest["expected_commit"] == candidate["candidate_commit"] and remote_manifest["expected_tree"] == candidate["candidate_tree"], "remote manifest is not bound to candidate")
    commit = subprocess.check_output(["git", "--git-dir", str(remote), "rev-parse", "refs/heads/main"], text=True).strip()
    tree = subprocess.check_output(["git", "--git-dir", str(remote), "show", "-s", "--format=%T", commit], text=True).strip()
    require(commit == candidate["candidate_commit"] and tree == candidate["candidate_tree"], "local remote commit/tree differs from candidate")
    return {"candidate_commit": commit, "candidate_tree": tree}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-root", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--expected-mission-file", required=True)
    parser.add_argument("--claude-result", required=True)
    parser.add_argument("--claude-metadata", required=True)
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--local-remote", required=True)
    args = parser.parse_args()
    tasks_root = Path(args.tasks_root).resolve()
    task_root = tasks_root / args.task_id
    result_path = Path(args.claude_result)
    require(result_path.is_file() and result_path.stat().st_size > 0, "Claude stream missing")
    metadata = json_object(Path(args.claude_metadata))
    require(isinstance(metadata.get("exit_status"), int) and metadata["exit_status"] == 0, "host exit status was not zero")
    require(metadata.get("timed_out") is False, "host timed out")
    stream = parse_agent_transcript(result_path)
    expected_mission = Path(args.expected_mission_file).read_bytes()
    found = rediscover_task(tasks_root, args.task_id)
    require((task_root / found.mission_relative_path).read_bytes() == expected_mission, "exact mission bytes differ")
    require(found.accepted_plan_ref is not None and found.cursor is not None, "sealed Plan or cursor missing")
    plan = load_plan_artifact(task_root, found.accepted_plan_ref)
    require(plan["task_id"] == args.task_id and plan["mission_sha256"] == found.mission_sha256, "Plan binding mismatch")
    require(found.phase == Phase.CLOSED.value and found.cursor.status is CursorStatus.EXECUTION_COMPLETE, "lifecycle did not reach CLOSED")
    require(len(found.cursor.completed_step_ids) >= 2, "fewer than two completed steps")
    events = read_ledger(task_root / "ledger.jsonl")
    require(events[-1]["phase"] == Phase.CLOSED.value and events[-1]["status"] == "CLOSED", "terminal CLOSED ledger event missing")
    for phase in (Phase.MISSION_PERSISTED.value, Phase.PLAN_REVIEW.value, Phase.PLAN_SEALED.value, Phase.STEP_EXECUTING.value, Phase.STEP_VALIDATED.value, Phase.CANDIDATE_FROZEN.value, Phase.FINAL_REVIEW.value, Phase.INTEGRATED.value, Phase.CLOSED.value):
        require(any(event["phase"] == phase for event in events), f"lifecycle phase missing: {phase}")
    roles, reviews, first_receipt = validate_host_receipts(task_root, events)
    negative_probes(task_root, first_receipt)
    fix = loop_passes(reviews, "FIX_LOOP")
    find = loop_passes(reviews, "FIND_LOOP")
    require(fix >= 3 and find >= 3, "review loops lack three qualifying passes")
    final = [r for r in reviews if r.get("INVOCATION_KIND") == "FIND_LOOP"][-1]
    require(final.get("FINDING_CATEGORIES") == ["PASS"] and not final.get("OPEN_ITEMS"), "final Find Loop is not clean")
    git_proof = validate_git_proof(task_root, args.task_id, found, Path(args.source_repo).resolve(), Path(args.local_remote).resolve())
    terminal = task_root / "terminal/receipt.json"
    require(terminal.is_file() and terminal.stat().st_size <= 4096, "compact terminal receipt missing")
    terminal_value = json_object(terminal)
    require(terminal_value.get("task_id") == args.task_id and "body" not in terminal_value and "mission" not in terminal_value, "terminal receipt is not compact")
    require(terminal_value.get("INITIAL_MISSION_CONTEXT_ISOLATION") == "UNAVAILABLE_FOR_DIRECT_TT", "terminal isolation claim is not honest")
    require(terminal_value.get("HIDDEN_HOST_CONTEXT_ISOLATION") == "UNKNOWN", "terminal hidden-context claim is not honest")
    print(json.dumps({"status": "PASS", "task_id": args.task_id, "stream": stream, "roles": sorted(roles), "ledger_events": len(events), "fix_loop_qualifying_passes": fix, "find_loop_qualifying_passes": find, **git_proof}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeError as exc:
        print(f"TARGET_TASK_SMOKE_INVALID: {exc}", file=sys.stderr)
        raise SystemExit(2)
