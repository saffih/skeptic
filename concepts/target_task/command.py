"""Bounded deterministic commands with immutable task-root evidence."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from capabilities.execution_envelope.execution_envelope import validate_command_receipt
from concepts.target_task.store import StoreError, write_immutable_artifact


class CommandError(ValueError):
    pass


COMMAND_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    ).stdout.strip()


def build_mutation_preflight(
    repository_root: Path,
    worktree: Path,
    *,
    mutation_authorized: bool = True,
) -> dict[str, Any]:
    """Bind authorization to the current clean Git state; dirty state is never admissible."""
    repository_root = Path(repository_root).resolve()
    worktree = Path(worktree).resolve()
    if _git(worktree, "status", "--porcelain", "--untracked-files=all") != "":
        raise CommandError("WORKTREE_DIRTY")
    return {
        "expected_repository_root": str(repository_root),
        "expected_worktree": str(worktree),
        "expected_branch": _git(worktree, "branch", "--show-current"),
        "expected_head": _git(worktree, "rev-parse", "HEAD"),
        "required_clean": True,
        "mutation_authorized": mutation_authorized,
    }


def _preflight_error(worktree: Path, expected: Mapping[str, Any] | None) -> str | None:
    required = {
        "expected_repository_root",
        "expected_worktree",
        "expected_branch",
        "expected_head",
        "required_clean",
        "mutation_authorized",
    }
    if not isinstance(expected, Mapping) or set(expected) != required:
        return "MUTATION_PREFLIGHT_REQUIRED"
    if expected["mutation_authorized"] is not True or expected["required_clean"] is not True:
        return "MUTATION_NOT_AUTHORIZED"
    try:
        actual = {
            "expected_repository_root": _git(worktree, "rev-parse", "--show-toplevel"),
            "expected_worktree": str(worktree.resolve()),
            "expected_branch": _git(worktree, "branch", "--show-current"),
            "expected_head": _git(worktree, "rev-parse", "HEAD"),
            "required_clean": _git(worktree, "status", "--porcelain", "--untracked-files=all") == "",
        }
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "PREFLIGHT_OBSERVATION_FAILED"
    for key, value in actual.items():
        wanted = str(Path(expected[key]).resolve()) if key in {"expected_repository_root", "expected_worktree"} else expected[key]
        if wanted != value:
            return f"PREFLIGHT_{key.upper()}_MISMATCH"
    return None


def run_task_command(
    workspace_root: Path,
    command_id: str,
    description: str,
    command: Sequence[str],
    *,
    worktree: Path,
    mutating: bool = False,
    preflight: Mapping[str, Any] | None = None,
    relevant_counts: Mapping[str, int] | None = None,
    timeout_seconds: int = 300,
) -> dict[str, Any]:
    """Run explicit argv with timeout and create exactly one immutable private log."""
    if not isinstance(command_id, str) or not COMMAND_ID_RE.fullmatch(command_id):
        raise CommandError("COMMAND_ID")
    if not isinstance(description, str) or not description:
        raise CommandError("DESCRIPTION")
    if not isinstance(command, (list, tuple)) or not command or any(not isinstance(arg, str) or "\x00" in arg for arg in command):
        raise CommandError("COMMAND_ARGV")
    if not isinstance(timeout_seconds, int) or isinstance(timeout_seconds, bool) or timeout_seconds < 1:
        raise CommandError("TIMEOUT")
    worktree = Path(worktree).resolve()
    blocked = _preflight_error(worktree, preflight) if mutating else None
    if blocked:
        output = f"PREVENTED: {blocked}\n".encode("utf-8")
        status, exit_code, summary = "BLOCKED", 2, blocked
    else:
        try:
            process = subprocess.run(
                list(command),
                cwd=worktree,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=timeout_seconds,
            )
            output = b"STDOUT\n" + process.stdout + b"\nSTDERR\n" + process.stderr
            status = "SUCCEEDED" if process.returncode == 0 else "FAILED"
            exit_code = process.returncode
            summary = "command completed" if process.returncode == 0 else "command failed; complete output preserved"
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or b""
            stderr = exc.stderr or b""
            output = b"TIMEOUT\nSTDOUT\n" + stdout + b"\nSTDERR\n" + stderr
            status, exit_code, summary = "FAILED", 124, "command timed out; partial output preserved"
        except OSError as exc:
            output = f"COMMAND_START_ERROR\n{type(exc).__name__}: {exc}\n".encode("utf-8")
            status, exit_code, summary = "FAILED", 127, "command could not start; failure preserved"
    try:
        log_ref = write_immutable_artifact(
            Path(workspace_root),
            f"commands/{command_id}.log",
            output,
            reference_id=f"command-{command_id}",
            artifact_type="command_log",
            description=description,
            read_condition="read when validating this command receipt",
        )
    except StoreError as exc:
        raise CommandError(f"COMMAND_LOG:{exc.code}") from exc
    receipt = {
        "command_id": command_id,
        "description": description,
        "status": status,
        "exit_code": exit_code,
        "log_path": log_ref["repository_relative_path"],
        "log_sha256": log_ref["sha256"],
        "log_byte_size": log_ref["byte_size"],
        "summary": summary,
        "relevant_counts": dict(relevant_counts or {}),
    }
    return validate_command_receipt(receipt, repository_root=workspace_root)
