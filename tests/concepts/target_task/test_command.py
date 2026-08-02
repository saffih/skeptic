import sys
import tempfile
import unittest
from pathlib import Path
import subprocess

from concepts.target_task.command import CommandError, build_mutation_preflight, run_task_command


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.tasks = root / "task"
        self.repo.mkdir(); self.tasks.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test")
        (self.repo / "README.md").write_text("hello\n")
        git(self.repo, "add", "README.md"); git(self.repo, "commit", "-q", "-m", "initial")

    def tearDown(self):
        self.tmp.cleanup()

    def test_dirty_worktree_cannot_produce_mutation_preflight(self):
        (self.repo / "dirty").write_text("x")
        with self.assertRaises(CommandError):
            build_mutation_preflight(self.repo, self.repo)

    def test_mutation_requires_fresh_clean_preflight(self):
        receipt = run_task_command(self.tasks, "blocked", "blocked", ["touch", "x"], worktree=self.repo, mutating=True)
        self.assertEqual(receipt["status"], "BLOCKED")
        preflight = build_mutation_preflight(self.repo, self.repo)
        receipt = run_task_command(self.tasks, "allowed", "allowed", ["touch", "x"], worktree=self.repo, mutating=True, preflight=preflight)
        self.assertEqual(receipt["status"], "SUCCEEDED")

    def test_timeout_is_preserved_and_duplicate_log_is_rejected(self):
        receipt = run_task_command(
            self.tasks, "slow", "slow", [sys.executable, "-c", "import time; time.sleep(5)"],
            worktree=self.repo, timeout_seconds=1,
        )
        self.assertEqual(receipt["exit_code"], 124)
        with self.assertRaises(CommandError):
            run_task_command(self.tasks, "slow", "again", ["true"], worktree=self.repo)

    def test_log_is_private(self):
        receipt = run_task_command(self.tasks, "ok", "ok", ["printf", "ok"], worktree=self.repo)
        self.assertEqual((self.tasks / receipt["log_path"]).stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
