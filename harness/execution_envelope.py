"""Fail-closed, file-backed execution envelopes for the metadata-only Body."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from .body_state import ARTIFACT_FIELDS, BodyStateError, _hash_file, _path, _short

TASK_ENVELOPE_LIMIT = 8192
ROLE_RETURN_LIMIT = 4096
COMMAND_RECEIPT_LIMIT = 4096
SHORT_STRING_LIMIT = 256
TASK_FIELDS = {"task_id", "objective", "scope", "authority", "prohibitions", "success_criteria", "contract_references", "input_artifact_references", "required_output_references"}
ROLE_FIELDS = {"role", "status", "summary", "produced_artifact_references", "findings", "blockers", "next_authorized_action"}
RECEIPT_FIELDS = {"command_id", "description", "status", "exit_code", "log_path", "log_sha256", "log_byte_size", "summary", "relevant_counts"}
PREFLIGHT_FIELDS = {"expected_repository_root", "expected_worktree", "expected_branch", "expected_head", "required_clean", "mutation_authorized"}
SHA256_RE = __import__("re").compile(r"^[0-9a-f]{64}$")


class ExecutionEnvelopeError(ValueError):
    def __init__(self, code: str, path: str = "$") -> None:
        self.code, self.path = code, path
        super().__init__(f"{code} at {path}")


def _canonical(value: Mapping[str, Any], limit: int) -> bytes:
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(raw) > limit:
        raise ExecutionEnvelopeError("TOO_LARGE")
    return raw


def _strings(value: Any, path: str, *, max_items: int = 32) -> None:
    if not isinstance(value, list) or len(value) > max_items:
        raise ExecutionEnvelopeError("LIST", path)
    for i, item in enumerate(value):
        _short(item, f"{path}/{i}", SHORT_STRING_LIMIT)


def _references(value: Any, path: str, repository_root: Path) -> None:
    if not isinstance(value, list) or len(value) > 32:
        raise ExecutionEnvelopeError("ARTIFACTS", path)
    seen: set[str] = set()
    for i, item in enumerate(value):
        p = f"{path}/{i}"
        if not isinstance(item, dict) or set(item) != ARTIFACT_FIELDS:
            raise ExecutionEnvelopeError("FIELDS", p)
        try:
            rid = _short(item["reference_id"], f"{p}/reference_id", 64)
            rel = _path(item["repository_relative_path"], f"{p}/repository_relative_path")
        except BodyStateError as exc:
            raise ExecutionEnvelopeError(exc.code, exc.path) from exc
        if rid in seen:
            raise ExecutionEnvelopeError("DUPLICATE_REFERENCE", f"{p}/reference_id")
        seen.add(rid)
        if not isinstance(item["sha256"], str) or not SHA256_RE.fullmatch(item["sha256"]):
            raise ExecutionEnvelopeError("SHA256", f"{p}/sha256")
        if not isinstance(item["byte_size"], int) or isinstance(item["byte_size"], bool) or item["byte_size"] < 0:
            raise ExecutionEnvelopeError("BYTE_SIZE", f"{p}/byte_size")
        for key in ("artifact_type", "description", "read_condition"):
            try:
                _short(item[key], f"{p}/{key}")
            except BodyStateError as exc:
                raise ExecutionEnvelopeError(exc.code, exc.path) from exc
        root = repository_root.resolve()
        target = (root / rel).resolve()
        if os.path.commonpath((str(root), str(target))) != str(root) or not target.is_file():
            raise ExecutionEnvelopeError("ARTIFACT_MISSING", f"{p}/repository_relative_path")
        digest, size = _hash_file(target)
        if digest != item["sha256"] or size != item["byte_size"]:
            raise ExecutionEnvelopeError("ARTIFACT_MISMATCH", p)


def validate_task_envelope(value: Mapping[str, Any], *, repository_root: Path | str = ".") -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != TASK_FIELDS:
        raise ExecutionEnvelopeError("FIELDS")
    root = Path(repository_root)
    for key in ("task_id", "objective", "scope", "authority"):
        try:
            _short(value[key], f"$.{key}")
        except BodyStateError as exc:
            raise ExecutionEnvelopeError(exc.code, exc.path) from exc
    for key in ("prohibitions", "success_criteria"):
        _strings(value[key], f"$.{key}")
    for key in ("contract_references", "input_artifact_references", "required_output_references"):
        _references(value[key], f"$.{key}", root)
    _canonical(value, TASK_ENVELOPE_LIMIT)
    return dict(value)


def serialize_task_envelope(value: Mapping[str, Any], *, repository_root: Path | str = ".") -> bytes:
    validate_task_envelope(value, repository_root=repository_root)
    return _canonical(value, TASK_ENVELOPE_LIMIT)


def validate_role_return(value: Mapping[str, Any], *, repository_root: Path | str = ".") -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != ROLE_FIELDS:
        raise ExecutionEnvelopeError("FIELDS")
    for key in ("role", "status", "summary", "next_authorized_action"):
        try:
            _short(value[key], f"$.{key}")
        except BodyStateError as exc:
            raise ExecutionEnvelopeError(exc.code, exc.path) from exc
    _references(value["produced_artifact_references"], "$.produced_artifact_references", Path(repository_root))
    for key in ("findings", "blockers"):
        _strings(value[key], f"$.{key}")
    _canonical(value, ROLE_RETURN_LIMIT)
    return dict(value)


def serialize_role_return(value: Mapping[str, Any], *, repository_root: Path | str = ".") -> bytes:
    validate_role_return(value, repository_root=repository_root)
    return _canonical(value, ROLE_RETURN_LIMIT)


def _safe_log_path(log_path: str | Path, root: Path) -> tuple[str, Path]:
    try:
        rel = _path(str(log_path), "$.log_path")
    except BodyStateError as exc:
        raise ExecutionEnvelopeError(exc.code, exc.path) from exc
    target = (root.resolve() / rel).resolve()
    if os.path.commonpath((str(root.resolve()), str(target))) != str(root.resolve()):
        raise ExecutionEnvelopeError("UNSAFE_PATH", "$.log_path")
    return rel, target


def _receipt(value: Mapping[str, Any], *, root: Path) -> dict[str, Any]:
    if set(value) != RECEIPT_FIELDS:
        raise ExecutionEnvelopeError("FIELDS")
    for key in ("command_id", "description", "status", "summary"):
        try:
            _short(value[key], f"$.{key}")
        except BodyStateError as exc:
            raise ExecutionEnvelopeError(exc.code, exc.path) from exc
    if not isinstance(value["exit_code"], int) or isinstance(value["exit_code"], bool):
        raise ExecutionEnvelopeError("EXIT_CODE", "$.exit_code")
    if not isinstance(value["log_sha256"], str) or not SHA256_RE.fullmatch(value["log_sha256"]):
        raise ExecutionEnvelopeError("SHA256", "$.log_sha256")
    if not isinstance(value["log_byte_size"], int) or isinstance(value["log_byte_size"], bool) or value["log_byte_size"] < 0:
        raise ExecutionEnvelopeError("BYTE_SIZE", "$.log_byte_size")
    if not isinstance(value["relevant_counts"], dict) or len(value["relevant_counts"]) > 16:
        raise ExecutionEnvelopeError("COUNTS", "$.relevant_counts")
    for key, count in value["relevant_counts"].items():
        try:
            _short(key, "$.relevant_counts.key", 64)
        except BodyStateError as exc:
            raise ExecutionEnvelopeError(exc.code, exc.path) from exc
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ExecutionEnvelopeError("COUNTS", "$.relevant_counts")
    rel, target = _safe_log_path(value["log_path"], root)
    if not target.is_file():
        raise ExecutionEnvelopeError("LOG_MISSING", "$.log_path")
    digest, size = _hash_file(target)
    if digest != value["log_sha256"] or size != value["log_byte_size"]:
        raise ExecutionEnvelopeError("LOG_MISMATCH", "$.log_path")
    _canonical(value, COMMAND_RECEIPT_LIMIT)
    return dict(value)


def validate_command_receipt(value: Mapping[str, Any], *, repository_root: Path | str = ".") -> dict[str, Any]:
    return _receipt(value, root=Path(repository_root))


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()


def _preflight(cwd: Path, expected: Mapping[str, Any]) -> str | None:
    if set(expected) != PREFLIGHT_FIELDS:
        return "PREFLIGHT_FIELDS"
    actual_root = _git(cwd, "rev-parse", "--show-toplevel")
    actual_worktree = str(cwd.resolve())
    actual_branch = _git(cwd, "branch", "--show-current")
    actual_head = _git(cwd, "rev-parse", "HEAD")
    actual_clean = _git(cwd, "status", "--porcelain", "--untracked-files=all") == ""
    checks = (("REPOSITORY_ROOT", str(Path(expected["expected_repository_root"]).resolve()), actual_root), ("WORKTREE", str(Path(expected["expected_worktree"]).resolve()), actual_worktree), ("BRANCH", expected["expected_branch"], actual_branch), ("HEAD", expected["expected_head"], actual_head), ("CLEAN", bool(expected["required_clean"]), actual_clean))
    for name, want, got in checks:
        if want != got:
            return f"PREFLIGHT_{name}_MISMATCH"
    if expected["mutation_authorized"] is not True:
        return "MUTATION_NOT_AUTHORIZED"
    return None


def run_command(command_id: str, description: str, command: Sequence[str], *, repository_root: Path | str = ".", cwd: Path | str | None = None, log_path: Path | str, mutating: bool = False, preflight: Mapping[str, Any] | None = None, relevant_counts: Mapping[str, int] | None = None) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    workdir = Path(cwd or root).resolve()
    rel_log, target = _safe_log_path(log_path, root)
    target.parent.mkdir(parents=True, exist_ok=True)
    blocked = _preflight(workdir, preflight) if mutating and preflight is not None else ("MUTATION_PREFLIGHT_REQUIRED" if mutating else None)
    if blocked:
        target.write_bytes((f"PREVENTED: {blocked}\n").encode())
        status, code, summary = "BLOCKED", 2, blocked
    else:
        try:
            proc = subprocess.run(list(command), cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            target.write_bytes(b"STDOUT\n" + proc.stdout + b"\nSTDERR\n" + proc.stderr)
            status, code = ("SUCCEEDED", 0) if proc.returncode == 0 else ("FAILED", proc.returncode)
            summary = "command completed" if proc.returncode == 0 else "command failed; complete output preserved"
        except OSError as exc:
            target.write_bytes(f"COMMAND_START_ERROR\n{type(exc).__name__}: {exc}\n".encode())
            status, code, summary = "FAILED", 127, "command could not start; failure preserved"
    digest, size = _hash_file(target)
    receipt = {"command_id": command_id, "description": description, "status": status, "exit_code": code, "log_path": rel_log, "log_sha256": digest, "log_byte_size": size, "summary": summary, "relevant_counts": dict(relevant_counts or {})}
    return validate_command_receipt(receipt, repository_root=root)


def serialize_command_receipt(value: Mapping[str, Any], *, repository_root: Path | str = ".") -> bytes:
    validate_command_receipt(value, repository_root=repository_root)
    return _canonical(value, COMMAND_RECEIPT_LIMIT)
