"""Immutable artifacts and the append-only, hash-chained task ledger.

All Target Task run state lives under one caller-supplied authoritative task
root (`TASKS_ROOT/TASK_ID`): mission, Plan versions, sealed Plan, steps,
requests, results, reviews, findings, receipts, command logs, checkpoints, and
ledger. The source repository is a separate work target, not another task-state
root. This module owns create-only artifact writes and the event ledger.
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from capabilities.body_state.body_state import BodyStateError, _hash_file, _path
from concepts.target_task.contracts import ContractError, LedgerEvent, canonical_bytes


class StoreError(ValueError):
    def __init__(self, code: str, path: str = "$") -> None:
        self.code, self.path = code, path
        super().__init__(f"{code} at {path}")


def _fsync_dir(directory: Path) -> None:
    """Durably persist a directory-entry change (create, rename, replace)
    against a crash immediately after the syscall returns, matching the
    pattern `capabilities.immutable_checkpoint`/`capabilities.restart_admission`
    already use for their own atomic publish steps. Some filesystems do not
    support fsync on a directory; that is not an error here."""
    try:
        dir_fd = os.open(str(directory), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError as exc:
        if exc.errno not in {errno.ENOTSUP, errno.EOPNOTSUPP, errno.EINVAL, errno.ENOSYS}:
            raise


def _safe_target(workspace_root: Path, relative_path: str) -> Path:
    try:
        rel = _path(relative_path, "$.relative_path")
    except BodyStateError as exc:
        raise StoreError(exc.code, exc.path) from exc
    root = workspace_root.resolve()
    target = (root / rel).resolve()
    if os.path.commonpath((str(root), str(target))) != str(root):
        raise StoreError("UNSAFE_PATH", "$.relative_path")
    if target.is_symlink():
        raise StoreError("SYMLINK_ESCAPE", "$.relative_path")
    return target


def write_immutable_artifact(
    workspace_root: Path,
    relative_path: str,
    content: bytes,
    *,
    reference_id: str,
    artifact_type: str,
    description: str,
    read_condition: str,
) -> dict[str, Any]:
    """Create-only write of one immutable artifact under the external task
    workspace; returns a `body_state.ARTIFACT_FIELDS`-shaped reference.
    Never overwrites. This reference is workspace-relative and must not be
    placed in a `body_state` object's `ARTIFACT_REFERENCES` list (which
    resolves against `repository_root`, not `workspace_root` — see
    `target_task_contract.md`, "Two roots"); it is for workspace-internal
    bookkeeping (ledger events, step results, command logs) only."""
    target = _safe_target(workspace_root, relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise StoreError("ALREADY_EXISTS", "$.relative_path") from exc
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    _fsync_dir(target.parent)
    digest, size = _hash_file(target)
    return {
        "reference_id": reference_id,
        "repository_relative_path": relative_path,
        "sha256": digest,
        "byte_size": size,
        "artifact_type": artifact_type,
        "description": description,
        "read_condition": read_condition,
    }


def _event_hash(event: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(event)).hexdigest()


@dataclass(frozen=True)
class LedgerAppendResult:
    event: LedgerEvent
    head_hash: str


class AppendOnlyLedger:
    """Single-writer, append-only, hash-chained ledger.jsonl."""

    def __init__(self, ledger_path: Path) -> None:
        self._path = ledger_path

    def _existing_lines(self) -> list[bytes]:
        if not self._path.exists():
            return []
        raw = self._path.read_bytes()
        if not raw:
            return []
        return raw.split(b"\n")[:-1] if raw.endswith(b"\n") else raw.split(b"\n")

    def head(self) -> tuple[int, str | None]:
        """Return (next_sequence, previous_event_hash) for the current tail."""
        lines = self._existing_lines()
        if not lines:
            return 0, None
        try:
            tail = json.loads(lines[-1].decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise StoreError("TORN_TAIL") from exc
        return tail["sequence"] + 1, _event_hash(tail)

    def append(self, event: LedgerEvent) -> LedgerAppendResult:
        next_sequence, previous_hash = self.head()
        if event.sequence != next_sequence:
            raise StoreError("SEQUENCE_MISMATCH")
        if event.previous_event_hash != previous_hash:
            raise StoreError("HEAD_MISMATCH")
        line = canonical_bytes(event.to_dict()) + b"\n"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self._path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            with os.fdopen(fd, "ab") as stream:
                stream.write(line)
                stream.flush()
                os.fsync(stream.fileno())
        finally:
            pass
        written = self._existing_lines()[-1]
        if written + b"\n" != line:
            raise StoreError("APPEND_VERIFY_FAILED")
        return LedgerAppendResult(event=event, head_hash=_event_hash(event.to_dict()))


def read_ledger(ledger_path: Path) -> list[dict[str, Any]]:
    if not ledger_path.exists():
        return []
    raw = ledger_path.read_bytes()
    lines = raw.split(b"\n")[:-1] if raw.endswith(b"\n") else raw.split(b"\n")
    events: list[dict[str, Any]] = []
    for i, line in enumerate(lines):
        try:
            events.append(json.loads(line.decode("utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise StoreError("TORN_TAIL", f"$[{i}]") from exc
    return events


def verify_chain(events: list[Mapping[str, Any]]) -> bool:
    previous_hash: str | None = None
    for i, event in enumerate(events):
        try:
            LedgerEvent.from_dict(event)
        except ContractError:
            return False
        if event["sequence"] != i or event["previous_event_hash"] != previous_hash:
            return False
        previous_hash = _event_hash(event)
    return True


@dataclass(frozen=True)
class RecoveryResult:
    recovered: bool
    valid_event_count: int


def recover_torn_tail(ledger_path: Path) -> RecoveryResult:
    """Remove an incomplete final JSONL line only when every prior line
    parses and the resulting chain validates. Never touches a complete,
    valid ledger."""
    if not ledger_path.exists():
        return RecoveryResult(recovered=False, valid_event_count=0)
    raw = ledger_path.read_bytes()
    if raw.endswith(b"\n") or not raw:
        events = read_ledger(ledger_path)
        return RecoveryResult(recovered=False, valid_event_count=len(events))
    lines = raw.split(b"\n")
    prefix_lines = lines[:-1]
    try:
        prior_events = [json.loads(line.decode("utf-8")) for line in prefix_lines]
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise StoreError("UNRECOVERABLE_PRIOR_STATE") from exc
    if not verify_chain(prior_events):
        raise StoreError("UNRECOVERABLE_PRIOR_STATE")
    tmp_path = ledger_path.with_suffix(ledger_path.suffix + ".recover.tmp")
    payload = b"".join(line + b"\n" for line in prefix_lines) if prefix_lines else b""
    fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp_path, ledger_path)
    _fsync_dir(ledger_path.parent)
    return RecoveryResult(recovered=True, valid_event_count=len(prior_events))
