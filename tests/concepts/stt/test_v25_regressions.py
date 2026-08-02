from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from adapters.generic_host import GenericHostAdapter
from concepts.stt.artifacts import ArtifactRef
from concepts.stt.canonical import atomic_write, canonical_json_bytes, sha256_bytes
from concepts.stt.errors import STTError
from concepts.stt.runner import Runner


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

    def _runner(self, root: Path) -> Runner:
        repo = self._repo(root)
        started = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"inspect branches\n", included_ignored=[])
        return Runner(Path(started["task_root"]))

    def _reject_initial_result(self, runner: Runner) -> tuple[str, ArtifactRef]:
        request, request_ref = runner._pending_operation()
        evidence = runner.task_root / request["_provider_evidence_ref"]
        result = runner.task_root / request["result_ref"]
        evidence.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(evidence, canonical_json_bytes({"provider_id": "generic-recorded-host", "invocation_id": "planner-1", "status": "COMPLETE", "timed_out": False, "exit_code": 0}))
        atomic_write(result, canonical_json_bytes({"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": "0" * 64, "kind": "PLAN_CANDIDATE"}))
        rejected = runner.run()
        self.assertEqual(rejected["next_action"], "RETRY_OPERATION")
        return request["operation_id"], request_ref

    def test_invalid_result_is_rejected_without_consuming_operation(self):
        with tempfile.TemporaryDirectory() as td:
            runner = self._runner(Path(td)); operation_id, _ = self._reject_initial_result(runner)
            self.assertEqual(runner._pending_operation()[0]["operation_id"], operation_id)
            self.assertEqual(runner.retry()["next_action"], "DISPATCH_PLANNER")
            self.assertEqual(runner._pending_operation()[0]["operation_id"], operation_id)
            self.assertFalse(any(event["event"]["event_type"] == "OPERATION_ACCEPTED" for event in runner._events()))

    def test_replan_supersedes_exact_rejected_operation_before_replacement(self):
        with tempfile.TemporaryDirectory() as td:
            runner = self._runner(Path(td)); old_id, _ = self._reject_initial_result(runner)
            runner.replan(); reconstructed = Runner(runner.task_root)
            pending = reconstructed._pending_operation()
            self.assertIsNotNone(pending); self.assertNotEqual(pending[0]["operation_id"], old_id)
            superseded = [event for event in reconstructed._events() if event["event"]["event_type"] == "OPERATION_SUPERSEDED"]
            self.assertEqual([event["payload"]["operation_id"] for event in superseded], [old_id])

    def test_artifact_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            runner = self._runner(Path(td)); target = runner.task_root / "x"; target.write_bytes(b"x"); (runner.task_root / "link").symlink_to(target)
            with self.assertRaises(STTError):
                runner.store.verify(ArtifactRef("link", sha256_bytes(b"x"), 1))

    def test_stop_and_resume_survive_reconstruction_without_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            runner = self._runner(Path(td)); pending_id = runner._pending_operation()[0]["operation_id"]
            runner.stop(); stopped = Runner(runner.task_root)
            before = len(stopped._events()); self.assertEqual(stopped.run()["status"], "STOPPED"); self.assertEqual(len(stopped._events()), before)
            resumed = stopped.resume(); self.assertEqual(resumed["next_action"], "RUN")
            reconstructed = Runner(runner.task_root)
            self.assertEqual(reconstructed._pending_operation()[0]["operation_id"], pending_id)
            self.assertEqual(reconstructed.status()["next_action"], "DISPATCH_PLANNER")

    def test_blocked_unknown_is_nonresumable_and_diagnose_only(self):
        with tempfile.TemporaryDirectory() as td:
            runner = self._runner(Path(td)); operation_id = runner._pending_operation()[0]["operation_id"]
            evidence = runner.store.publish_json("test/failure.json", {"schema_version": 1, "kind": "partial_or_unknown"})
            runner._record_blocked_unknown("WORKER_DELTA_PARTIAL_OR_UNKNOWN", [evidence], operation_id=operation_id)
            state = Runner(runner.task_root).status()
            self.assertEqual((state["status"], state["next_action"], state["resumable"]), ("BLOCKED_UNKNOWN", "DIAGNOSE", False))
            with self.assertRaises(STTError):
                Runner(runner.task_root).resume()
            later = runner.store.publish_json("test/later.json", {"schema_version": 1})
            with self.assertRaises(STTError):
                runner.ledger.append("TASK_STOPPED", later.ref, later.sha256)

    def test_malformed_provider_types_are_bounded_adapter_errors(self):
        adapter = GenericHostAdapter()
        malformed = [
            {"provider_id": "generic-recorded-host", "invocation_id": [], "status": "COMPLETE", "timed_out": False, "exit_code": 0},
            {"provider_id": "generic-recorded-host", "invocation_id": "x", "status": "COMPLETE", "timed_out": "false", "exit_code": 0},
            {"provider_id": "generic-recorded-host", "invocation_id": "x", "status": "COMPLETE", "timed_out": False, "exit_code": "0"},
            {"provider_id": "generic-recorded-host", "invocation_id": "x", "status": "COMPLETE", "timed_out": True, "exit_code": 0},
            {"provider_id": "generic-recorded-host", "invocation_id": "x", "status": [], "timed_out": False, "exit_code": 0},
        ]
        for value in malformed:
            with self.subTest(value=value), self.assertRaises(STTError) as caught:
                adapter.validate_provider_evidence(canonical_json_bytes(value))
            self.assertEqual(caught.exception.code, "HOST_ADAPTER_ERROR")

    def test_ledger_refuses_any_event_after_terminal_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            runner = self._runner(Path(td)); runner._terminal("FAILED", "TEST", [])
            marker = runner.store.publish_json("test/later.json", {"schema_version": 1})
            with self.assertRaises(STTError) as caught:
                runner.ledger.append("OPERATION_ACCEPTED", marker.ref, marker.sha256)
            self.assertEqual(caught.exception.code, "CONTROL_STATE_TERMINAL")


if __name__ == "__main__":
    unittest.main()
