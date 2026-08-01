from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from concepts.stt.canonical import canonical_json_bytes, sha256_file
from concepts.stt.errors import STTError
from concepts.stt.plan import validate_plan
from concepts.stt.runner import Runner
from concepts.stt.verifier import verify_task_terminal
from concepts.stt.contracts import DEFAULT_LIMITS


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_bytes(canonical_json_bytes(value))


def done(delivery: str) -> list[dict]:
    common = [
        {"id": "objective", "kind": "reviewer_claim", "claim_id": "mission_objective_satisfied", "subject_ref": "frozen_final_candidate"},
        {"id": "clean", "kind": "reviewer_claim", "claim_id": "final_find_loop_clean", "subject_ref": "frozen_final_candidate"},
    ]
    if delivery == "inspect":
        return [{"id": "inventory", "kind": "deterministic_predicate", "predicate_id": "inventory_scope_completed", "subject_ref": "inspect_report"}, {"id": "bound", "kind": "reviewer_claim", "claim_id": "report_bound_to_baseline", "subject_ref": "inspect_report"}, {"id": "unchanged", "kind": "reviewer_claim", "claim_id": "source_workspace_unchanged", "subject_ref": "inspect_report"}, *common]
    return [{"id": "commands", "kind": "deterministic_predicate", "predicate_id": "all_declared_final_commands_succeeded", "subject_ref": "final_checkpoint"}, {"id": "tree", "kind": "deterministic_predicate", "predicate_id": "installed_tree_equals_frozen_candidate", "subject_ref": "installed_tree"}, {"id": "git", "kind": "deterministic_predicate", "predicate_id": "git_control_state_unchanged", "subject_ref": "installed_tree"}, *common]


class RecursiveTaskTests(unittest.TestCase):
    def repo(self, root: Path) -> Path:
        repo = root / "repo"; repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
        (repo / "skeptic.md").write_text("# Skeptic\n")
        (repo / "value.txt").write_text("before\n")
        subprocess.run(["git", "-C", str(repo), "add", "skeptic.md", "value.txt"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
        return repo

    def plan(self, request: dict, delivery: str, steps: list[dict]) -> tuple[Path, Path, dict]:
        root = Path(request["_task_root"]); out = root / request["result_ref"].rsplit("/", 1)[0]
        plan = {"schema_version": 2, "mission_sha256": request["mission"]["sha256"], "baseline_id": request["baseline_id"], "objective": "complete recursive task", "done": done(delivery), "steps": steps, "delivery_kind": delivery}
        plan_path = out / "plan.json"; map_path = out / "finding-map.json"
        write_json(plan_path, plan); write_json(map_path, {"findings": []})
        return plan_path, map_path, plan

    def complete(self, runner: Runner, planner_steps: dict[str, tuple[str, list[dict]]], worker_writes: dict[str, str] | None = None) -> None:
        plan_reviews = 0; final_reviews = 0
        for _ in range(160):
            active = runner
            while active._active_task_binding():
                candidate = Runner(Path(active._active_task_binding()["child_task_root"]))
                if candidate.status()["status"] in {"COMPLETE", "INSPECT_COMPLETE", "FAILED", "BLOCKED_UNKNOWN", "STOPPED"}:
                    break
                active = candidate
            status = runner.status()["status"]
            if status in {"COMPLETE", "INSPECT_COMPLETE", "FAILED", "BLOCKED_UNKNOWN"}:
                return
            pending = active._pending_operation()
            if pending is None:
                active.run(); continue
            request, request_ref = pending
            root = active.task_root; out = root / request["result_ref"].rsplit("/", 1)[0]
            if request["role"] == "planner":
                delivery, steps = planner_steps[request["mission"]["sha256"]]
                plan_path, map_path, _ = self.plan({**request, "_task_root": str(root)}, delivery, steps)
                write_json(root / request["_provider_evidence_ref"], {"provider_id": "generic-recorded-host", "invocation_id": f"planner-{request['operation_id']}", "status": "COMPLETE", "timed_out": False, "exit_code": 0})
                write_json(root / request["result_ref"], {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request_ref.sha256, "kind": "PLAN_CANDIDATE", "plan_ref": plan_path.relative_to(root).as_posix(), "plan_sha256": sha256_file(plan_path), "finding_map_ref": map_path.relative_to(root).as_posix()})
            elif request["role"] == "reviewer":
                final = request["purpose"] == "final_review"
                if final: final_reviews += 1
                else: plan_reviews += 1
                receipt = out / "review.json"; findings = out / "findings.json"
                write_json(receipt, {"verdict": "PASS"}); write_json(findings, {"findings": []})
                invocation = f"review-{request['operation_id']}"
                write_json(root / request["_provider_evidence_ref"], {"provider_id": "generic-recorded-host", "invocation_id": invocation, "status": "COMPLETE", "timed_out": False, "exit_code": 0})
                write_json(root / request["result_ref"], {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request_ref.sha256, "protocol_outcome": "COMPLETE", "review_disposition": "PASS", "runskeptic_final_outcome": "PASS", "receipt_ref": receipt.relative_to(root).as_posix(), "findings_ref": findings.relative_to(root).as_posix(), "subject_sha256": request["subject"]["sha256"], "session_id": invocation, "claims": ["mission_objective_satisfied", "final_find_loop_clean"] if final else []})
            elif request["role"] == "worker":
                write = (worker_writes or {}).get(request["step"]["id"], "child\n")
                Path(request["capsule_path"], "value.txt").write_text(write)
                write_json(root / request["_provider_evidence_ref"], {"provider_id": "generic-recorded-host", "invocation_id": f"worker-{request['operation_id']}", "status": "COMPLETE", "timed_out": False, "exit_code": 0})
                write_json(root / request["result_ref"], {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request_ref.sha256, "kind": "WORKER_RESULT", "step_id": request["step"]["id"], "summary": "updated", "declared_outputs": []})
            active.run()
        active = runner._active_task_binding()
        child_state = Runner(Path(active["child_task_root"])).status() if active else None
        self.fail(f"recursive smoke exceeded cycle bound: status={runner.status()} child={child_state} events={[r['event']['event_type'] for r in runner._events()[-12:]]} pending={runner._pending_operation()}")

    def change_step(self, step_id: str = "change") -> dict:
        return {"id": step_id, "kind": "change", "route_profile": "standard", "objective": "update value", "read_scope": [{"path": "value.txt", "kind": "file"}], "write_scope": [{"path": "value.txt", "kind": "file"}], "validation_commands": []}

    def inspect_step(self) -> dict:
        return {"id": "inspect", "kind": "inspect", "scope": ".", "operation": "repository_inventory"}

    def task_step(self, mission: str, delivery: str, step_id: str = "child") -> dict:
        return {"id": step_id, "kind": "task", "mission": mission, "delivery_kind": delivery}

    def test_task_schema_is_exact_and_planner_cannot_control_runtime(self):
        base = {"schema_version": 2, "mission_sha256": "m" * 64, "baseline_id": "base", "objective": "x", "done": done("workspace_change"), "steps": [], "delivery_kind": "workspace_change"}
        for extra in ({"authority": {}}, {"child_task_id": "x"}, {"required_outcome": "COMPLETE"}):
            plan = dict(base); plan["steps"] = [{**self.task_step("inspect", "inspect"), **extra}]
            with self.assertRaises(STTError):
                validate_plan(plan, mission_sha256="m" * 64, baseline_id="base", catalog_ids=set(), source_paths=[], limits=DEFAULT_LIMITS)
        for bad in ("", "   ", "unknown"):
            plan = dict(base); plan["steps"] = [self.task_step("mission", bad)]
            with self.assertRaises(STTError):
                validate_plan(plan, mission_sha256="m" * 64, baseline_id="base", catalog_ids=set(), source_paths=[], limits=DEFAULT_LIMITS)

    def test_root_child_workspace_and_deterministic_binding(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo = self.repo(root)
            root_started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"root\n", included_ignored=[], allow_unconfined=True)
            root_runner = Runner(Path(root_started["task_root"]))
            child_mission = "child\n"; child_sha = __import__("hashlib").sha256(child_mission.encode()).hexdigest()
            root_sha = root_runner.task["mission"]["sha256"]
            self.complete(root_runner, {root_sha: ("workspace_change", [self.task_step(child_mission, "workspace_change")]), child_sha: ("workspace_change", [self.change_step()])}, {"change": "grandchild\n", "child": "ignored\n"})
            self.assertEqual(root_runner.status()["status"], "COMPLETE")
            child_root = root_runner.task_root.parent / root_runner._last_event_payload("TASK_BOUND")["child_task_id"]
            self.assertEqual((Runner(child_root)._latest_checkpoint()[1] / "value.txt").read_text(), "grandchild\n")
            self.assertEqual((root_runner._latest_checkpoint()[1] / "value.txt").read_text(), "grandchild\n", root_runner._last_event_payload("TASK_RESULT_ACCEPTED"))
            bound = root_runner._last_event_payload("TASK_BOUND")
            self.assertIsNotNone(bound)
            self.assertEqual(bound["child_task_id"], str(__import__("uuid").uuid5(__import__("uuid").NAMESPACE_URL, "skeptic-task\0" + "\0".join([root_runner.task_id, bound["parent_plan_sha256"], "child", bound["parent_checkpoint_sha256"]]))))
            self.assertEqual((repo / "value.txt").read_text(), "grandchild\n")
            self.assertEqual(len([r for r in root_runner._events() if r["event"]["event_type"] == "TASK_RESULT_ACCEPTED"]), 1)
            verify_task_terminal(root_runner.task_root, expected_parent_binding=None, expected_delivery_kind="workspace_change", expected_success_outcome="COMPLETE")

    def test_inspect_child_is_closed_and_preserves_parent_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo = self.repo(root)
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"root\n", included_ignored=[], allow_unconfined=True)
            runner = Runner(Path(started["task_root"]))
            child_mission = "inspect child\n"; child_sha = __import__("hashlib").sha256(child_mission.encode()).hexdigest()
            root_sha = runner.task["mission"]["sha256"]
            before = runner._checkpoint_sha256(0)
            with patch("concepts.stt.runner.run_command", side_effect=AssertionError("inspect called generic command")):
                self.complete(runner, {root_sha: ("workspace_change", [self.task_step(child_mission, "inspect")]), child_sha: ("inspect", [self.inspect_step()])})
            self.assertEqual(runner.status()["status"], "COMPLETE")
            self.assertEqual(runner._checkpoint_sha256(runner._latest_checkpoint()[0]), before)
            self.assertTrue((runner.task_root / "task-results/child/inspect-report.json").is_file())
            child_id = runner._last_event_payload("TASK_BOUND")["child_task_id"]
            child = Runner(runner.task_root.parent / child_id, read_only=True)
            self.assertEqual(child.status()["status"], "INSPECT_COMPLETE")
            self.assertFalse(any(r["event"]["event_type"] == "TASK_RESULT_ACCEPTED" for r in child._events()))

    def test_root_child_grandchild_executes_depth_first(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self.repo(Path(td))
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"root\n", included_ignored=[], allow_unconfined=True)
            runner = Runner(Path(started["task_root"]))
            child_mission = "child\n"; grandchild_mission = "grandchild\n"
            root_sha = runner.task["mission"]["sha256"]
            child_sha = __import__("hashlib").sha256(child_mission.encode()).hexdigest()
            grandchild_sha = __import__("hashlib").sha256(grandchild_mission.encode()).hexdigest()
            self.complete(runner, {
                root_sha: ("workspace_change", [self.task_step(child_mission, "workspace_change")]),
                child_sha: ("workspace_change", [self.task_step(grandchild_mission, "workspace_change", "grandchild")]),
                grandchild_sha: ("workspace_change", [self.change_step()]),
            }, {"change": "depth-first\n"})
            self.assertEqual(runner.status()["status"], "COMPLETE")
            self.assertEqual((repo / "value.txt").read_text(), "depth-first\n")
            self.assertEqual(len([r for r in runner._events() if r["event"]["event_type"] == "TASK_BOUND"]), 1)
            child_id = runner._last_event_payload("TASK_BOUND")["child_task_id"]
            child = Runner(runner.task_root.parent / child_id, read_only=True)
            self.assertEqual(len([r for r in child._events() if r["event"]["event_type"] == "TASK_BOUND"]), 1)
            self.assertEqual(len([r for r in child._events() if r["event"]["event_type"] == "TASK_RESULT_ACCEPTED"]), 1)

    def test_terminal_verifier_rejects_wrong_parent_and_task_has_no_stack(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self.repo(Path(td)); started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"inspect\n", included_ignored=[])
            runner = Runner(Path(started["task_root"]))
            self.assertFalse((runner.task_root / "stack.json").exists())
            with self.assertRaises(STTError):
                verify_task_terminal(runner.task_root, expected_parent_binding={"parent_task_id": "wrong"})
