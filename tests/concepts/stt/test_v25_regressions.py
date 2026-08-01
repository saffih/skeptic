from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from concepts.stt.canonical import atomic_write, canonical_json_bytes, sha256_bytes
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
