from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from concepts.stt.errors import STTError
from concepts.stt.runner import Runner


class RunnerTests(unittest.TestCase):
    def _repo(self, base: Path) -> Path:
        repo = base / "repo"; repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
        (repo / "skeptic.md").write_text("# Skeptic\n")
        subprocess.run(["git", "-C", str(repo), "add", "skeptic.md"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
        return repo

    def test_bootstrap_status_restore(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td); repo = self._repo(base); state = repo.with_name(f"{repo.name}.stt") / "tasks"; restore = base / "restore"
            (repo / "file.txt").write_text("dirty")
            result = Runner.bootstrap(repo=repo, state_root=state, mission=b"repair\n", included_ignored=[])
            self.assertEqual(result["next_action"], "DISPATCH_PLANNER")
            runner = Runner(Path(result["task_root"]))
            self.assertEqual(runner.status()["next_action"], "DISPATCH_PLANNER")
            restored = runner.restore(restore)
            self.assertEqual(restored["status"], "RESTORED")
            self.assertEqual((restore / "file.txt").read_text(), "dirty")

    def test_status_read_only_does_not_repair_partial_ledger(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td); repo = self._repo(base); state = repo.with_name(f"{repo.name}.stt") / "tasks"
            result = Runner.bootstrap(repo=repo, state_root=state, mission=b"repair\n", included_ignored=[])
            ledger = Path(result["task_root"]) / "ledger.jsonl"
            with ledger.open("ab") as handle:
                handle.write(b'{"partial"')
            before = ledger.read_bytes()
            with self.assertRaises(STTError):
                Runner(Path(result["task_root"]), read_only=True)
            self.assertEqual(ledger.read_bytes(), before)

    def test_role_request_does_not_disclose_provider_evidence_path(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td); repo = self._repo(base); state = repo.with_name(f"{repo.name}.stt") / "tasks"
            result = Runner.bootstrap(repo=repo, state_root=state, mission=b"repair\n", included_ignored=[])
            runner = Runner(Path(result["task_root"]))
            request, request_ref = runner._pending_operation()
            public = json.loads((runner.task_root / request_ref.ref).read_text())
            self.assertNotIn("provider_evidence_ref", public)
            self.assertNotIn("provider_id", public)
            self.assertIn("_provider_evidence_ref", request)


    def test_locks_are_local_to_state_root(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td); repo = self._repo(base); state = repo.with_name(f"{repo.name}.stt") / "tasks"
            result = Runner.bootstrap(repo=repo, state_root=state, mission=b"repair\n", included_ignored=[])
            Runner(Path(result["task_root"])).status()
            locks = state.resolve() / ".locks"
            self.assertTrue(locks.is_dir())
            self.assertEqual(locks.stat().st_mode & 0o777, 0o700)
            self.assertTrue(any(locks.iterdir()))

    def test_nested_repository_is_preserved_but_execution_excluded(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td); repo = self._repo(base); state = repo.with_name(f"{repo.name}.stt") / "tasks"; restore = base / "restore"
            nested = repo / "vendor"; nested.mkdir()
            subprocess.run(["git", "init", "-q", str(nested)], check=True)
            (nested / "private.txt").write_text("private")
            result = Runner.bootstrap(repo=repo, state_root=state, mission=b"repair\n", included_ignored=[])
            task_root = Path(result["task_root"])
            snapshot = json.loads((task_root / "preservation/initial-receipt.json").read_text())
            self.assertEqual(snapshot["nested_repository_roots"], ["vendor"])
            self.assertFalse((task_root / "checkpoints/000/workspace/vendor").exists())
            Runner(task_root).restore(restore)
            self.assertEqual((restore / "vendor/private.txt").read_text(), "private")
