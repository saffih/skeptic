from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Callable
from unittest.mock import patch

from concepts.stt.artifacts import ArtifactRef
from concepts.stt.canonical import canonical_json_bytes, loads_strict, sha256_file
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
        return [{"id": "inventory", "kind": "deterministic_predicate", "predicate_id": "inventory_scope_completed", "subject_ref": "inspect_report"}, {"id": "bound", "kind": "reviewer_claim", "claim_id": "report_bound_to_baseline", "subject_ref": "inspect_report"}, *common]
    return [{"id": "commands", "kind": "deterministic_predicate", "predicate_id": "all_declared_final_commands_succeeded", "subject_ref": "final_evidence"}, {"id": "paths", "kind": "deterministic_predicate", "predicate_id": "changed_paths_bound_to_workspace", "subject_ref": "final_evidence"}, *common]


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

    def complete(
        self,
        runner: Runner,
        planner_steps: dict[str, tuple[str, list[dict]]],
        worker_writes: dict[str, str | dict[str, str | None]] | None = None,
        tamper_root_after_final_reviews: Callable[[Runner], None] | None = None,
    ) -> None:
        plan_reviews = 0
        final_reviews: dict[str, int] = {}
        for _ in range(160):
            active = runner
            while active._active_task_binding():
                candidate = Runner(Path(active._active_task_binding()["child_task_root"]))
                if candidate.status()["status"] in {"COMPLETE", "FAILED", "BLOCKED_UNKNOWN", "STOPPED"}:
                    break
                active = candidate
            status = runner.status()["status"]
            if status in {"COMPLETE", "FAILED", "BLOCKED_UNKNOWN"}:
                return
            pending = active._pending_operation()
            if pending is None:
                active.run(); continue
            request, request_ref = pending
            root = active.task_root; out = root / request["result_ref"].rsplit("/", 1)[0]
            is_final_review = False
            if request["role"] == "planner":
                delivery, steps = planner_steps[request["mission"]["sha256"]]
                plan_path, map_path, _ = self.plan({**request, "_task_root": str(root)}, delivery, steps)
                write_json(root / request["_provider_evidence_ref"], {"provider_id": "generic-recorded-host", "invocation_id": f"planner-{request['operation_id']}", "status": "COMPLETE", "timed_out": False, "exit_code": 0})
                write_json(root / request["result_ref"], {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request_ref.sha256, "kind": "PLAN_CANDIDATE", "plan_ref": plan_path.relative_to(root).as_posix(), "plan_sha256": sha256_file(plan_path), "finding_map_ref": map_path.relative_to(root).as_posix()})
            elif request["role"] == "reviewer":
                final = request["purpose"] == "final_review"
                is_final_review = final
                if final: final_reviews[active.task_id] = final_reviews.get(active.task_id, 0) + 1
                else: plan_reviews += 1
                receipt = out / "review.json"; findings = out / "findings.json"
                write_json(receipt, {"verdict": "PASS"}); write_json(findings, {"findings": []})
                invocation = f"review-{request['operation_id']}"
                write_json(root / request["_provider_evidence_ref"], {"provider_id": "generic-recorded-host", "invocation_id": invocation, "status": "COMPLETE", "timed_out": False, "exit_code": 0})
                write_json(root / request["result_ref"], {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request_ref.sha256, "protocol_outcome": "COMPLETE", "review_disposition": "PASS", "runskeptic_final_outcome": "PASS", "receipt_ref": receipt.relative_to(root).as_posix(), "findings_ref": findings.relative_to(root).as_posix(), "subject_sha256": request["subject"]["sha256"], "session_id": invocation, "claims": request["required_claims"] if final else []})
            elif request["role"] == "worker":
                write = (worker_writes or {}).get(request["step"]["id"], "child\n")
                if isinstance(write, dict):
                    for rel, body in write.items():
                        target = Path(request["capsule_path"], rel)
                        if body is None:
                            if target.is_dir(): target.rmdir()
                            elif target.exists() or target.is_symlink(): target.unlink()
                        else:
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_text(body)
                else:
                    Path(request["capsule_path"], "value.txt").write_text(write)
                write_json(root / request["_provider_evidence_ref"], {"provider_id": "generic-recorded-host", "invocation_id": f"worker-{request['operation_id']}", "status": "COMPLETE", "timed_out": False, "exit_code": 0})
                write_json(root / request["result_ref"], {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request_ref.sha256, "kind": "WORKER_RESULT", "step_id": request["step"]["id"], "summary": "updated", "declared_outputs": []})
            if is_final_review and active.task_id == runner.task_id and final_reviews[active.task_id] == 3 and tamper_root_after_final_reviews is not None:
                result, result_ref, provider_report, evidence_ref = active._adopt_result(request)
                active._process_reviewer_result(request, result, result_ref, provider_report, evidence_ref)
                effect = active._effect_records(request["operation_id"])
                self.assertEqual(len(effect), 1)
                active._accept_effect(request, request_ref, effect[0])
                tamper_root_after_final_reviews(active)
            active.run()
        active = runner._active_task_binding()
        child_state = Runner(Path(active["child_task_root"])).status() if active else None
        self.fail(f"recursive smoke exceeded cycle bound: status={runner.status()} child={child_state} events={[r['event']['event_type'] for r in runner._events()[-12:]]} pending={runner._pending_operation()}")

    def change_step(self, step_id: str = "change") -> dict:
        return {"id": step_id, "kind": "change", "route_profile": "standard", "objective": "update value", "read_scope": [{"path": "value.txt", "kind": "file"}], "write_scope": [{"path": "value.txt", "kind": "file"}], "validation_commands": []}

    def tree_change_step(self, step_id: str = "change", path: str = "generated") -> dict:
        return {"id": step_id, "kind": "change", "route_profile": "standard", "objective": "update tree", "read_scope": [{"path": path, "kind": "tree"}], "write_scope": [{"path": path, "kind": "tree"}], "validation_commands": []}

    def frozen_evidence(self, runner: Runner) -> dict:
        frozen = runner._last_event_payload("FINAL_SUBJECT_FROZEN")
        self.assertIsNotNone(frozen)
        return loads_strict(runner.store.verify(ArtifactRef(**frozen["evidence"])).read_bytes())

    def inspect_step(self) -> dict:
        return {"id": "inspect", "kind": "inspect", "scope": ".", "operation": "repository_inventory"}

    def task_step(self, mission: str, delivery: str | None = None, step_id: str = "child") -> dict:
        return {"id": step_id, "kind": "task", "mission": mission}

    def test_task_schema_is_exact_and_planner_cannot_control_runtime(self):
        base = {"schema_version": 2, "mission_sha256": "m" * 64, "baseline_id": "base", "objective": "x", "done": done("workspace_change"), "steps": [], "delivery_kind": "workspace_change"}
        valid = dict(base); valid["steps"] = [self.task_step("inspect repository")]
        validate_plan(valid, mission_sha256="m" * 64, baseline_id="base", catalog_ids=set(), source_paths=[], limits=DEFAULT_LIMITS)
        for extra in ({"delivery_kind": "inspect"}, {"authority": {}}, {"child_task_id": "x"}, {"required_outcome": "COMPLETE"}, {"child_root": "x"}, {"parent_binding": {}}):
            plan = dict(base); plan["steps"] = [{**self.task_step("inspect"), **extra}]
            with self.assertRaises(STTError):
                validate_plan(plan, mission_sha256="m" * 64, baseline_id="base", catalog_ids=set(), source_paths=[], limits=DEFAULT_LIMITS)
        for bad in ("", "   "):
            plan = dict(base); plan["steps"] = [self.task_step(bad)]
            with self.assertRaises(STTError):
                validate_plan(plan, mission_sha256="m" * 64, baseline_id="base", catalog_ids=set(), source_paths=[], limits=DEFAULT_LIMITS)

    def test_root_child_workspace_and_deterministic_binding(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo = self.repo(root)
            root_started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"root\n", included_ignored=[])
            root_runner = Runner(Path(root_started["task_root"]))
            child_mission = "child\n"; child_sha = __import__("hashlib").sha256(child_mission.encode()).hexdigest()
            root_sha = root_runner.task["mission"]["sha256"]
            self.complete(root_runner, {root_sha: ("workspace_change", [self.task_step(child_mission, "workspace_change")]), child_sha: ("workspace_change", [self.change_step()])}, {"change": "grandchild\n", "child": "ignored\n"})
            self.assertEqual(root_runner.status()["status"], "COMPLETE")
            child_root = root_runner.task_root.parent / root_runner._last_event_payload("TASK_BOUND")["child_task_id"]
            self.assertFalse((root_runner.task_root / "checkpoints").exists())
            bound = root_runner._last_event_payload("TASK_BOUND")
            self.assertIsNotNone(bound)
            self.assertNotIn("delivery_kind", bound)
            self.assertNotIn("required_success_outcome", bound)
            self.assertEqual(set(bound["parent_binding"]), {"parent_task_id", "parent_plan_sha256", "parent_step_id", "parent_workspace_sha256", "depth", "child_task_id", "mission_sha256", "read_only_authority"})
            self.assertEqual(bound["child_task_id"], str(__import__("uuid").uuid5(__import__("uuid").NAMESPACE_URL, "skeptic-task\0" + "\0".join([root_runner.task_id, bound["parent_plan_sha256"], "child", bound["parent_workspace_sha256"]]))))
            self.assertEqual((repo / "value.txt").read_text(), "grandchild\n")
            self.assertEqual(len([r for r in root_runner._events() if r["event"]["event_type"] == "TASK_RESULT_ACCEPTED"]), 1)
            verified = verify_task_terminal(root_runner.task_root, expected_parent_binding=None, expected_success_outcome="COMPLETE")
            self.assertEqual(verified["terminal_receipt"]["result"], verified["result_ref"].as_dict())
            evidence = self.frozen_evidence(root_runner)
            self.assertEqual([entry["path"] for entry in evidence["declared_changed_paths"]], ["value.txt"])
            self.assertEqual(evidence["declared_changed_paths"][0]["state"], "file")
            accepted = root_runner._last_event_payload("TASK_RESULT_ACCEPTED")
            self.assertEqual(accepted["frozen_evidence"], verify_task_terminal(child_root, expected_parent_binding=bound["parent_binding"], expected_success_outcome="COMPLETE")["evidence_ref"].as_dict())

    def test_task_whose_plan_performs_inspection_is_closed_without_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo = self.repo(root)
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"root\n", included_ignored=[])
            runner = Runner(Path(started["task_root"]))
            child_mission = "inspect child\n"; child_sha = __import__("hashlib").sha256(child_mission.encode()).hexdigest()
            root_sha = runner.task["mission"]["sha256"]
            with patch("concepts.stt.runner.run_command", side_effect=AssertionError("inspect called generic command")):
                self.complete(runner, {root_sha: ("workspace_change", [self.task_step(child_mission, "inspect")]), child_sha: ("inspect", [self.inspect_step()])})
            self.assertEqual(runner.status()["status"], "COMPLETE")
            self.assertFalse((runner.task_root / "checkpoints").exists())
            self.assertTrue((runner.task_root / "tasks/results").is_dir())
            child_id = runner._last_event_payload("TASK_BOUND")["child_task_id"]
            child = Runner(runner.task_root.parent / child_id, read_only=True)
            self.assertEqual(child.status()["status"], "COMPLETE")
            child_verified = verify_task_terminal(child.task_root, expected_parent_binding=child.task["parent_binding"], expected_success_outcome="COMPLETE")
            self.assertNotIn("checkpoint", child_verified["result"])
            accepted = runner._last_event_payload("TASK_RESULT_ACCEPTED")
            self.assertEqual(accepted["result_ref"], child_verified["result_ref"].as_dict())

    def test_root_child_grandchild_executes_depth_first(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self.repo(Path(td))
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"root\n", included_ignored=[])
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
            self.assertEqual([entry["path"] for entry in self.frozen_evidence(child)["declared_changed_paths"]], ["value.txt"])
            self.assertEqual([entry["path"] for entry in self.frozen_evidence(runner)["declared_changed_paths"]], ["value.txt"])

    def test_ignored_tree_delta_records_each_changed_path_without_git_status(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self.repo(Path(td))
            (repo / ".gitignore").write_text("generated/\n")
            subprocess.run(["git", "-C", str(repo), "add", ".gitignore"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "ignore generated"], check=True)
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"root tree change\n", included_ignored=[])
            runner = Runner(Path(started["task_root"]))
            root_sha = runner.task["mission"]["sha256"]
            self.complete(
                runner,
                {root_sha: ("workspace_change", [self.tree_change_step()])},
                {"change": {"generated/one.txt": "one\n", "generated/nested/two.txt": "two\n"}},
            )

            self.assertEqual(runner.status()["status"], "COMPLETE")
            evidence = self.frozen_evidence(runner)
            entries = {entry["path"]: entry for entry in evidence["declared_changed_paths"]}
            self.assertEqual(
                set(entries),
                {"generated", "generated/nested", "generated/nested/two.txt", "generated/one.txt"},
            )
            self.assertEqual(entries["generated"]["state"], "directory")
            self.assertEqual(entries["generated/one.txt"]["state"], "file")
            self.assertEqual(entries["generated/nested/two.txt"]["state"], "file")
            self.assertNotIn("generated", subprocess.run(["git", "-C", str(repo), "status", "--short"], check=True, capture_output=True, text=True).stdout)
            runner._verify_frozen_workspace(evidence)
            with patch("concepts.stt.runner.run_git", side_effect=AssertionError("git status must not discover changed paths")):
                self.assertEqual(runner._workspace_evidence()["declared_changed_paths"], evidence["declared_changed_paths"])

    def test_descendant_tamper_after_final_reviews_fails_root(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self.repo(Path(td))
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"root\n", included_ignored=[])
            runner = Runner(Path(started["task_root"]))
            child_mission = "child\n"
            root_sha = runner.task["mission"]["sha256"]
            child_sha = __import__("hashlib").sha256(child_mission.encode()).hexdigest()
            self.complete(
                runner,
                {
                    root_sha: ("workspace_change", [self.task_step(child_mission, "workspace_change")]),
                    child_sha: ("workspace_change", [self.change_step()]),
                },
                {"change": "descendant\n"},
                tamper_root_after_final_reviews=lambda _: (repo / "value.txt").write_text("tampered\n"),
            )

            self.assertEqual(runner.status()["status"], "FAILED")
            verified = verify_task_terminal(runner.task_root, expected_parent_binding=None)
            self.assertEqual(verified["terminal_receipt"]["reason"], "FINAL_WORKSPACE_CHANGED")
            self.assertEqual((repo / "value.txt").read_text(), "tampered\n")

    def test_terminal_verifier_rejects_wrong_parent_and_task_has_no_stack(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self.repo(Path(td)); started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"inspect\n", included_ignored=[])
            runner = Runner(Path(started["task_root"]))
            self.assertFalse((runner.task_root / "stack.json").exists())
            with self.assertRaises(STTError):
                verify_task_terminal(runner.task_root, expected_parent_binding={"parent_task_id": "wrong"})
