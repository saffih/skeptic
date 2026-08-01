from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from concepts.stt.cli import local_state_root


class CliTests(unittest.TestCase):
    def test_default_state_root_is_adjacent_to_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
        self.assertEqual(local_state_root(repo), repo.resolve() / ".stt" / "tasks")


if __name__ == "__main__":
    unittest.main()
