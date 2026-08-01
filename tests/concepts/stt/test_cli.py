from __future__ import annotations

import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from concepts.stt.cli import local_state_root, main


class CliTests(unittest.TestCase):
    def test_default_state_root_is_adjacent_to_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
        self.assertEqual(local_state_root(repo), repo.resolve() / ".stt" / "tasks")

    def test_unconfined_compatibility_flag_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            mission = root / "mission.txt"
            mission.write_text("inspect\n")
            state = root / "state" / "tasks"
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                status = main([
                    "start", "--repo", str(repo), "--state-root", str(state),
                    "--mission-file", str(mission), "--allow-unconfined-candidate-execution",
                ])
            self.assertNotEqual(status, 0)
            self.assertIn("UNCONFINED_SHARED_WORKSPACE_EXECUTION_UNSUPPORTED", stderr.getvalue())
            self.assertFalse(state.exists())


if __name__ == "__main__":
    unittest.main()
