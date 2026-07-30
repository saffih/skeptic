"""Deterministic command execution for a Target Task step.

`capabilities.execution_envelope.execution_envelope.run_command` already is
the deterministic command contract this repository needs: one explicit
argument vector (never a shell string), a Git mutation preflight
(root/worktree/branch/HEAD/clean-state), and complete stdout/stderr capture
to a file before any structured result is returned. This module only fixes
the Target Task log-path convention (`commands/<command_id>.log`, written
under the task's external workspace, never inside the repository being
operated on) and offers a small helper to build a correct preflight dict.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Mapping

from capabilities.execution_envelope.execution_envelope import run_command as _run_command


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ).stdout.strip()


def build_mutation_preflight(repository_root: Path, worktree: Path, *, mutation_authorized: bool = True) -> dict[str, Any]:
    """Observe the actual current Git state and bind a preflight to it,
    rather than letting a caller assert stale values."""
    return {
        "expected_repository_root": str(Path(repository_root).resolve()),
        "expected_worktree": str(Path(worktree).resolve()),
        "expected_branch": _git(worktree, "branch", "--show-current"),
        "expected_head": _git(worktree, "rev-parse", "HEAD"),
        "required_clean": _git(worktree, "status", "--porcelain", "--untracked-files=all") == "",
        "mutation_authorized": mutation_authorized,
    }


def run_task_command(
    workspace_root: Path,
    command_id: str,
    description: str,
    command: list[str],
    *,
    worktree: Path,
    mutating: bool = False,
    preflight: Mapping[str, Any] | None = None,
    relevant_counts: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    """Run one command; the log lives under the external task workspace at
    commands/<command_id>.log (never inside the repository being operated
    on), hashed and size-bound like every other immutable artifact.
    `worktree` is the real repository the command runs in and the preflight
    checks against. Mutating commands require a preflight, built fresh with
    `build_mutation_preflight` immediately before the call."""
    return _run_command(
        command_id,
        description,
        command,
        repository_root=workspace_root,
        cwd=worktree,
        log_path=f"commands/{command_id}.log",
        mutating=mutating,
        preflight=preflight,
        relevant_counts=relevant_counts,
    )
