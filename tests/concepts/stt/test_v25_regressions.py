from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from concepts.stt.artifacts import ArtifactRef
from concepts.stt.canonical import atomic_write, canonical_json_bytes, sha256_bytes
from concepts.stt.runner import BLOCKED_UNKNOWN, TERMINAL, Runner


class V25RegressionTests(unittest.TestCase):
    def _repo(self, root: Path) -> Path:
        repo = root / "repo"; repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
        (repo / "skeptic.md").write_text("# Skeptic\n")
        subprocess.run(["git", "-C", str(repo), "add", "skeptic.md"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
        return repo

    def test_invalid_planner_result_is_rejected_without_consuming_operation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo = self._repo(root)
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"inspect branches\n", included_ignored=[])
            runner = Runner(Path(started["task_root"]))
            request, request_ref = runner._pending_operation()
            result_path = runner.task_root / request["result_ref"]
            evidence_path = runner.task_root / request["_provider_evidence_ref"]
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(evidence_path, canonical_json_bytes({"provider_id": "generic-recorded-host", "invocation_id": "planner-1", "status": "COMPLETE", "timed_out": False, "exit_code": 0}))
            atomic_write(result_path, canonical_json_bytes({"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": "0" * 64, "kind": "PLAN_CANDIDATE"}))
            rejected = runner.run()
            self.assertEqual(rejected["next_action"], "RETRY_OPERATION")
            self.assertIsNotNone(runner._pending_operation())
            self.assertEqual(runner.status()["next_action"], "RETRY_OPERATION")
            self.assertEqual(runner.run()["next_action"], "RETRY_OPERATION")
            self.assertFalse(any(e["event"]["event_type"] == "OPERATION_ACCEPTED" for e in runner._events()))

    def test_artifact_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); repo = self._repo(root)
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"inspect\n", included_ignored=[])
            runner = Runner(Path(started["task_root"]))
            target = runner.task_root / "x"; target.write_bytes(b"x")
            link = runner.task_root / "link"; link.symlink_to(target)
            from concepts.stt.artifacts import ArtifactRef
            with self.assertRaises(Exception):
                runner.store.verify(ArtifactRef("link", sha256_bytes(b"x"), 1))

    def _worker_request(self, runner: Runner) -> tuple[dict, ArtifactRef, ArtifactRef]:
        capsule = runner.task_root / "capsule"; capsule.mkdir()
        request_ref = runner._create_semantic_request(role="worker", purpose="execute_step", body={
            "step": {"id": "change", "write_scope": [{"path": "value.txt", "kind": "file"}], "validation_commands": [{"tool_id": "test"}]},
            "capsule_path": str(capsule),
        })
        request, _ = runner._pending_operation()
        worker_result = runner.store.publish_json("test/worker-result.json", {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": "x", "kind": "WORKER_RESULT", "step_id": "change", "summary": "changed", "declared_outputs": []})
        evidence = runner.store.publish_json("test/provider-evidence.json", {"provider_id": "generic-recorded-host", "invocation_id": "worker-test", "status": "COMPLETE", "timed_out": False, "exit_code": 0})
        return request, worker_result, evidence

    def _assert_terminal_last(self, runner: Runner, event_type: str, operation_id: str) -> None:
        events = runner._events()
        self.assertEqual(events[-1]["event"]["event_type"], event_type)
        self.assertEqual(events[-1]["payload"]["operation_id"], operation_id)
        self.assertFalse(any(item["event"]["event_type"] == "OPERATION_ACCEPTED" for item in events[-1:]))
        self.assertIsNone(runner._pending_operation())

    def test_worker_validation_failure_preserves_applied_delta_and_consumes_operation(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td)); (repo / "value.txt").write_text("before\n")
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"change\n", included_ignored=[])
            runner = Runner(Path(started["task_root"])); request, worker_result, evidence = self._worker_request(runner)
            delta = [{"path": "value.txt", "kind": "modify"}]
            def apply(*_: object) -> None: (repo / "value.txt").write_text("after\n")
            with patch("concepts.stt.runner.derive_delta", return_value=delta), patch("concepts.stt.runner.apply_delta", side_effect=apply), patch("concepts.stt.runner.run_command", return_value={"result_status": "FAILED", "reason": "VALIDATION_FAILED"}):
                self.assertEqual(runner._process_worker_result(request, {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": "x", "kind": "WORKER_RESULT", "step_id": "change", "summary": "changed", "declared_outputs": []}, worker_result, evidence), TERMINAL)
            self.assertEqual((repo / "value.txt").read_text(), "after\n")
            terminal = runner._last_event_payload("TERMINAL_RECEIPT_RECORDED")
            receipt = runner.store.verify(ArtifactRef(**terminal["receipt"]))
            failure = json.loads(receipt.read_text())["evidence"][0]
            self.assertEqual(json.loads(runner.store.verify(ArtifactRef(**failure)).read_text())["application_state"], "applied")
            self._assert_terminal_last(runner, "TERMINAL_RECEIPT_RECORDED", request["operation_id"])

    def test_worker_termination_unknown_is_last_and_consumed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td)); (repo / "value.txt").write_text("before\n")
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"change\n", included_ignored=[])
            runner = Runner(Path(started["task_root"])); request, worker_result, evidence = self._worker_request(runner)
            with patch("concepts.stt.runner.derive_delta", return_value=[]), patch("concepts.stt.runner.apply_delta"), patch("concepts.stt.runner.run_command", return_value={"result_status": "TERMINATION_UNKNOWN", "reason": "UNKNOWN"}):
                self.assertEqual(runner._process_worker_result(request, {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": "x", "kind": "WORKER_RESULT", "step_id": "change", "summary": "changed", "declared_outputs": []}, worker_result, evidence), BLOCKED_UNKNOWN)
            self._assert_terminal_last(runner, "TASK_BLOCKED_UNKNOWN", request["operation_id"])
            self.assertEqual(runner.run()["status"], "BLOCKED_UNKNOWN")
            self.assertEqual(runner.reconcile()["status"], "BLOCKED_UNKNOWN")

    def test_worker_apply_exception_preserves_intended_delta_as_partial_or_unknown(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td)); (repo / "value.txt").write_text("before\n")
            started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"change\n", included_ignored=[])
            runner = Runner(Path(started["task_root"])); request, worker_result, evidence = self._worker_request(runner)
            delta = [{"path": "value.txt", "kind": "modify"}]
            def partial(*_: object) -> None:
                (repo / "value.txt").write_text("possibly-applied\n")
                raise RuntimeError("interrupted")
            with patch("concepts.stt.runner.derive_delta", return_value=delta), patch("concepts.stt.runner.apply_delta", side_effect=partial):
                self.assertEqual(runner._process_worker_result(request, {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": "x", "kind": "WORKER_RESULT", "step_id": "change", "summary": "changed", "declared_outputs": []}, worker_result, evidence), TERMINAL)
            receipt = runner.store.verify(ArtifactRef(**runner._last_event_payload("TERMINAL_RECEIPT_RECORDED")["receipt"]))
            failure = json.loads(runner.store.verify(ArtifactRef(**json.loads(receipt.read_text())["evidence"][0])).read_text())
            self.assertEqual((failure["application_state"], failure["delta"]), ("partial_or_unknown", delta))
            self._assert_terminal_last(runner, "TERMINAL_RECEIPT_RECORDED", request["operation_id"])

    def test_terminal_disposition_stops_runner_before_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td)); started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"review\n", included_ignored=[])
            runner = Runner(Path(started["task_root"])); request, _ = runner._pending_operation()
            result_path = runner.task_root / request["result_ref"]; evidence_path = runner.task_root / request["_provider_evidence_ref"]
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(evidence_path, canonical_json_bytes({"provider_id": "generic-recorded-host", "invocation_id": "planner-test", "status": "COMPLETE", "timed_out": False, "exit_code": 0}))
            atomic_write(result_path, canonical_json_bytes({"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request and sha256_bytes((runner.task_root / f"semantic/requests/{request['operation_id']}.json").read_bytes()), "kind": "NEEDS_EVIDENCE", "selectors": []}))
            with patch.object(runner, "_process_planner_result", side_effect=lambda req, *_: (runner._terminal("FAILED", "TEST", [], operation_id=req["operation_id"]), TERMINAL)[1]):
                runner.run()
            self._assert_terminal_last(runner, "TERMINAL_RECEIPT_RECORDED", request["operation_id"])

    def test_ledger_refuses_any_event_after_terminal_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td)); started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"stop\n", included_ignored=[])
            runner = Runner(Path(started["task_root"])); runner._terminal("FAILED", "TEST", [])
            marker = runner.store.publish_json("test/later.json", {"schema_version": 1})
            with self.assertRaisesRegex(Exception, "no ledger event may follow a terminal receipt"):
                runner.ledger.append("OPERATION_ACCEPTED", marker.ref, marker.sha256)
