import subprocess
import tempfile
import unittest
from pathlib import Path

from concepts.target_task.command import build_mutation_preflight, run_task_command


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


class CommandTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.worktree = root / "repo"
        self.workspace = root / "workspace"
        self.worktree.mkdir()
        self.workspace.mkdir()
        _git(self.worktree, "init", "-q", "-b", "main")
        _git(self.worktree, "config", "user.email", "test@example.com")
        _git(self.worktree, "config", "user.name", "Test")
        (self.worktree / "README.md").write_text("hello\n")
        _git(self.worktree, "add", "README.md")
        _git(self.worktree, "commit", "-q", "-m", "initial")

    def tearDown(self) -> None:
        self.tmp.cleanup()


class RunTaskCommandTests(CommandTestCase):
    def test_non_mutating_command_succeeds_and_logs_under_workspace(self) -> None:
        receipt = run_task_command(
            self.workspace, "list-files", "list repo files", ["ls", "README.md"],
            worktree=self.worktree,
        )
        self.assertEqual(receipt["status"], "SUCCEEDED")
        self.assertEqual(receipt["exit_code"], 0)
        self.assertTrue((self.workspace / receipt["log_path"]).is_file())

    def test_failing_command_is_reported_failed_with_preserved_log(self) -> None:
        receipt = run_task_command(
            self.workspace, "fail", "deliberately fail", ["ls", "does-not-exist"],
            worktree=self.worktree,
        )
        self.assertEqual(receipt["status"], "FAILED")
        self.assertNotEqual(receipt["exit_code"], 0)

    def test_mutating_command_without_preflight_is_blocked(self) -> None:
        receipt = run_task_command(
            self.workspace, "touch", "touch a file", ["touch", "new.txt"],
            worktree=self.worktree, mutating=True,
        )
        self.assertEqual(receipt["status"], "BLOCKED")
        self.assertFalse((self.worktree / "new.txt").exists())

    def test_mutating_command_with_correct_preflight_succeeds(self) -> None:
        preflight = build_mutation_preflight(self.worktree, self.worktree)
        receipt = run_task_command(
            self.workspace, "touch-ok", "touch a file", ["touch", "new.txt"],
            worktree=self.worktree, mutating=True, preflight=preflight,
        )
        self.assertEqual(receipt["status"], "SUCCEEDED")
        self.assertTrue((self.worktree / "new.txt").exists())

    def test_stale_preflight_head_blocks_command(self) -> None:
        preflight = build_mutation_preflight(self.worktree, self.worktree)
        (self.worktree / "second.txt").write_text("x\n")
        _git(self.worktree, "add", "second.txt")
        _git(self.worktree, "commit", "-q", "-m", "second")
        receipt = run_task_command(
            self.workspace, "touch-stale", "touch a file", ["touch", "new.txt"],
            worktree=self.worktree, mutating=True, preflight=preflight,
        )
        self.assertEqual(receipt["status"], "BLOCKED")


class BuildMutationPreflightTests(CommandTestCase):
    def test_reflects_actual_branch_and_head(self) -> None:
        preflight = build_mutation_preflight(self.worktree, self.worktree)
        self.assertEqual(preflight["expected_branch"], "main")
        self.assertTrue(preflight["required_clean"])
        self.assertTrue(preflight["mutation_authorized"])

    def test_dirty_worktree_is_reflected_as_not_clean(self) -> None:
        (self.worktree / "untracked.txt").write_text("x\n")
        preflight = build_mutation_preflight(self.worktree, self.worktree)
        self.assertFalse(preflight["required_clean"])


if __name__ == "__main__":
    unittest.main()
