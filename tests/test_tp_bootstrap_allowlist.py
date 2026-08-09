"""Static contract tests for the TP pre-Brain bootstrap allowlist and the
first-Brain routing fixation (Cycle 2A.1 repair).

These tests prove only the written contract, not model behavior. Each
assertion body is factored into a module-level function of flattened text so
the same logic can be replayed against a pre-repair baseline copy of
`workflows/task_prompt.md` to demonstrate the assertions are load-bearing
(fail on the old text, pass on the current one).
"""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def raw(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def flat(path: str) -> str:
    return " ".join(raw(path).split())


def flat_text(text: str) -> str:
    return " ".join(text.split())


def assert_closed_positive_allowlist(text: str, case: unittest.TestCase) -> None:
    """Item 2: pre-Brain reads must be a closed positive allowlist naming
    exactly CLAUDE.md (conditional), AGENTS.md (conditional),
    MUST_READ_FIRST.md, and this file — not a negative list of exceptions."""
    case.assertIn(
        "the controller's behavior is a closed positive allowlist, not a "
        "general permission bounded by exceptions",
        text,
    )
    case.assertIn(
        "closed to the fixed orientation set: `CLAUDE.md` only if the host "
        "requires a manual bootstrap read, `AGENTS.md` only if not already "
        "supplied by the host, `MUST_READ_FIRST.md`, and this file",
        text,
    )
    case.assertIn("Nothing else is permitted before Brain.", text)


def assert_explicit_git_command_boundary(text: str, case: unittest.TestCase) -> None:
    """Item 3: the git-command boundary must be operational — the exact
    prohibited commands named, not left implicit under a generic ban."""
    case.assertIn(
        "any Git command other than resolving the absolute repository root",
        text,
    )
    case.assertIn(
        "`status`, `log`, `diff`, `show`, `fetch`, `pull`, `branch`, "
        "`remote`, HEAD, ancestry, and worktree-state inspection are all "
        "prohibited before Brain",
        text,
    )


def assert_no_ambiguous_repository_identity_concept(
    text: str, case: unittest.TestCase
) -> None:
    """Item 1: the removed bootstrap concept must not reappear anywhere."""
    case.assertNotIn("repository root and identity", text)
    case.assertNotIn("repository root/identity reference", text)


def assert_first_brain_route_is_unconditional(
    text: str, case: unittest.TestCase
) -> None:
    """Item 4: the first-Brain route must be fixed regardless of task-body
    content — no escape hatch letting task text pick a different route."""
    case.assertNotIn(
        "unless the task input explicitly fixes a different Brain route", text
    )
    case.assertIn(
        "The initial Brain route is always `MEDIUM`. Brain never starts at `LOW`.",
        text,
    )
    case.assertIn("MEDIUM = gpt-5.6-terra", text)


class TpBootstrapAllowlistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = flat("workflows/task_prompt.md")

    def test_pre_brain_allowlist_is_closed_and_positive(self) -> None:
        assert_closed_positive_allowlist(self.task, self)

    def test_pre_brain_git_command_boundary_is_explicit(self) -> None:
        assert_explicit_git_command_boundary(self.task, self)

    def test_ambiguous_repository_identity_concept_is_gone(self) -> None:
        assert_no_ambiguous_repository_identity_concept(self.task, self)

    def test_first_brain_route_is_fixed_without_task_body_override(self) -> None:
        assert_first_brain_route_is_unconditional(self.task, self)


if __name__ == "__main__":
    unittest.main()
