"""Immutable task-root artifacts and a strict append-only hash-chained ledger.

`TASKS_ROOT/TASK_ID` is the sole authority for mission, Plans, cursor snapshots,
requests, results, reviews, receipts, and ledger state. The source repository is
only the work target.
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
from concepts.target_task.contracts import (
    ContractError,
    LedgerEvent,
    StepCursor,
    canonical_bytes,
    canonical_cursor_bytes,
    canonical_finding_set_bytes,
    canonical_plan_bytes,
    parse_cursor_bytes,
    parse_finding_set_bytes,
    parse_plan_bytes,
)


class StoreError(ValueError):
    def __init__(self, code: str, path: str = "$") -> None:
        self.code, self.path = code, path
        super().__init__(f"{code} at {path}")


def _fsync_dir(directory: Path) -> None:
    try:
        dir_fd = os.open(str(directory), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError as exc:
        if exc.errno not in {errno.ENOTSUP, errno.EOPNOTSUPP, errno.EINVAL, errno.ENOSYS}:
            raise


def _short_metadata(value: Any, path: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > maximum:
        raise StoreError("SHORT_STRING", path)
    return value


def _workspace_root(workspace_root: Path) -> Path:
    supplied = Path(workspace_root).expanduser()
    if supplied.is_symlink():
        raise StoreError("WORKSPACE_SYMLINK", "$.workspace_root")
    try:
        root = supplied.resolve(strict=True)
    except OSError as exc:
        raise StoreError("WORKSPACE_INVALID", "$.workspace_root") from exc
    if not root.is_dir():
        raise StoreError("WORKSPACE_INVALID", "$.workspace_root")
    return root


def _safe_target(workspace_root: Path, relative_path: str) -> Path:
    try:
        rel = _path(relative_path, "$.relative_path")
    except BodyStateError as exc:
        raise StoreError(exc.code, exc.path) from exc
    root = _workspace_root(workspace_root)
    current = root
    parts = rel.split("/")
    for part in parts[:-1]:
        current = current / part
        if current.exists() and current.is_symlink():
            raise StoreError("SYMLINK_ESCAPE", "$.relative_path")
    target = root.joinpath(*parts)
    if target.exists() and target.is_symlink():
        raise StoreError("SYMLINK_ESCAPE", "$.relative_path")
    return target


def _ensure_private_directory_chain(root: Path, directory: Path) -> None:
    """Create/chmod every task-root-relative directory; never traverse a symlink."""
    root = _workspace_root(root)
    try:
        relative = directory.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise StoreError("UNSAFE_PATH", "$.relative_path") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise StoreError("SYMLINK_ESCAPE", "$.relative_path")
        current.mkdir(exist_ok=True, mode=0o700)
        os.chmod(current, 0o700)


def _reference(
    relative_path: str,
    content: bytes,
    *,
    reference_id: str,
    artifact_type: str,
    description: str,
    read_condition: str,
) -> dict[str, Any]:
    return {
        "reference_id": reference_id,
        "repository_relative_path": relative_path,
        "sha256": hashlib.sha256(content).hexdigest(),
        "byte_size": len(content),
        "artifact_type": artifact_type,
        "description": description,
        "read_condition": read_condition,
    }


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
    """Create one private immutable task artifact and return its task-root-relative reference."""
    if not isinstance(content, bytes):
        raise StoreError("CONTENT_BYTES", "$.content")
    _short_metadata(reference_id, "$.reference_id", 64)
    _short_metadata(artifact_type, "$.artifact_type", 64)
    _short_metadata(description, "$.description")
    _short_metadata(read_condition, "$.read_condition")
    root = _workspace_root(Path(workspace_root))
    target = _safe_target(root, relative_path)
    _ensure_private_directory_chain(root, target.parent)
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
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
    if digest != hashlib.sha256(content).hexdigest() or size != len(content):
        target.unlink(missing_ok=True)
        raise StoreError("WRITE_VERIFY_FAILED", "$.relative_path")
    return _reference(
        relative_path,
        content,
        reference_id=reference_id,
        artifact_type=artifact_type,
        description=description,
        read_condition=read_condition,
    )


def write_content_addressed_artifact(
    workspace_root: Path,
    directory: str,
    suffix: str,
    content: bytes,
    *,
    reference_id: str,
    artifact_type: str,
    description: str,
    read_condition: str,
) -> dict[str, Any]:
    """Publish or reuse the immutable artifact named by its SHA-256 identity."""
    if not suffix.startswith(".") or "/" in suffix or "\\" in suffix:
        raise StoreError("SUFFIX", "$.suffix")
    digest = hashlib.sha256(content).hexdigest()
    relative_path = f"{directory}/{digest}{suffix}"
    target = _safe_target(Path(workspace_root), relative_path)
    if target.exists():
        if target.is_symlink() or target.read_bytes() != content:
            raise StoreError("CONTENT_ADDRESS_COLLISION", "$.relative_path")
        return _reference(
            relative_path,
            content,
            reference_id=reference_id,
            artifact_type=artifact_type,
            description=description,
            read_condition=read_condition,
        )
    return write_immutable_artifact(
        Path(workspace_root),
        relative_path,
        content,
        reference_id=reference_id,
        artifact_type=artifact_type,
        description=description,
        read_condition=read_condition,
    )


def read_content_addressed_artifact(workspace_root: Path, relative_path: str) -> bytes:
    target = _safe_target(Path(workspace_root), relative_path)
    if target.is_symlink() or not target.is_file():
        raise StoreError("ARTIFACT_MISSING", "$.relative_path")
    name = target.name
    digest = name.split(".", 1)[0]
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        raise StoreError("CONTENT_ADDRESS", "$.relative_path")
    content = target.read_bytes()
    if hashlib.sha256(content).hexdigest() != digest:
        raise StoreError("ARTIFACT_IDENTITY", "$.relative_path")
    return content


def persist_plan_artifact(workspace_root: Path, plan: Mapping[str, Any]) -> dict[str, Any]:
    return write_content_addressed_artifact(
        workspace_root,
        "plans",
        ".json",
        canonical_plan_bytes(plan),
        reference_id="sealed-plan",
        artifact_type="sealed_plan",
        description="accepted immutable Target Task Plan",
        read_condition="read for step dispatch and deterministic validation",
    )


def load_plan_artifact(workspace_root: Path, relative_path: str) -> dict[str, Any]:
    return parse_plan_bytes(read_content_addressed_artifact(workspace_root, relative_path))


def persist_cursor_snapshot(workspace_root: Path, cursor: StepCursor) -> dict[str, Any]:
    return write_content_addressed_artifact(
        workspace_root,
        "state/cursors",
        ".json",
        canonical_cursor_bytes(cursor),
        reference_id="cursor",
        artifact_type="step_cursor",
        description="complete immutable Target Task step cursor",
        read_condition="read on every transition admission or restart",
    )


def load_cursor_snapshot(workspace_root: Path, relative_path: str) -> StepCursor:
    return parse_cursor_bytes(read_content_addressed_artifact(workspace_root, relative_path))


def persist_finding_set_artifact(workspace_root: Path, finding_set: Mapping[str, Any]) -> dict[str, Any]:
    return write_content_addressed_artifact(
        workspace_root,
        "findings/sets",
        ".json",
        canonical_finding_set_bytes(finding_set),
        reference_id="material-findings",
        artifact_type="material_findings",
        description="compact material finding identity set",
        read_condition="read when advancing or closing a review loop",
    )


def load_finding_set_artifact(workspace_root: Path, relative_path: str) -> dict[str, Any]:
    return parse_finding_set_bytes(read_content_addressed_artifact(workspace_root, relative_path))


def persist_loop_state_artifact(workspace_root: Path, kind: str, state: Mapping[str, Any]) -> dict[str, Any]:
    if kind not in {"fix", "find"}:
        raise StoreError("LOOP_KIND", "$.kind")
    try:
        raw = (json.dumps(dict(state), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise StoreError("LOOP_STATE_JSON", "$.state") from exc
    if len(raw) > 32768:
        raise StoreError("LOOP_STATE_TOO_LARGE", "$.state")
    return write_content_addressed_artifact(
        workspace_root,
        f"state/{kind}-loop",
        ".json",
        raw,
        reference_id=f"{kind}-loop-state",
        artifact_type=f"{kind}_loop_state",
        description=f"complete durable {kind} loop state",
        read_condition="read on the next review pass or fresh-session restart",
    )


def load_loop_state_artifact(workspace_root: Path, relative_path: str) -> dict[str, Any]:
    raw = read_content_addressed_artifact(workspace_root, relative_path)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StoreError("LOOP_STATE_JSON", "$.relative_path") from exc
    if not isinstance(value, dict):
        raise StoreError("LOOP_STATE_OBJECT", "$.relative_path")
    canonical = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if canonical != raw:
        raise StoreError("LOOP_STATE_NONCANONICAL", "$.relative_path")
    return value


def _event_hash(event: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(event)).hexdigest()


def _json_object(raw: bytes, path: str) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise StoreError("LEDGER_UTF8", path) from exc

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise StoreError("DUPLICATE_KEY", path)
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs)
    except StoreError:
        raise
    except json.JSONDecodeError as exc:
        raise StoreError("TORN_TAIL", path) from exc
    if not isinstance(value, dict):
        raise StoreError("LEDGER_OBJECT", path)
    try:
        LedgerEvent.from_dict(value)
        canonical = canonical_bytes(value)
    except ContractError as exc:
        raise StoreError(exc.code, path) from exc
    if canonical != raw:
        raise StoreError("NONCANONICAL_LEDGER", path)
    return value


def read_ledger(ledger_path: Path) -> list[dict[str, Any]]:
    if not ledger_path.exists():
        return []
    raw = ledger_path.read_bytes()
    if not raw:
        return []
    if not raw.endswith(b"\n"):
        raise StoreError("TORN_TAIL")
    lines = raw.split(b"\n")[:-1]
    events = [_json_object(line, f"$[{index}]") for index, line in enumerate(lines)]
    if not verify_chain(events):
        raise StoreError("INVALID_CHAIN")
    return events


def verify_chain(events: list[Mapping[str, Any]], *, expected_task_id: str | None = None) -> bool:
    previous_hash: str | None = None
    observed_task_id = expected_task_id
    for index, event in enumerate(events):
        try:
            parsed = LedgerEvent.from_dict(event)
        except ContractError:
            return False
        if observed_task_id is None:
            observed_task_id = parsed.task_id
        if parsed.task_id != observed_task_id:
            return False
        if parsed.sequence != index or parsed.previous_event_hash != previous_hash:
            return False
        previous_hash = _event_hash(event)
    return True


@dataclass(frozen=True)
class LedgerAppendResult:
    event: LedgerEvent
    head_hash: str


class AppendOnlyLedger:
    """Single-writer, strict-canonical append-only `ledger.jsonl`."""

    def __init__(self, ledger_path: Path) -> None:
        self._path = Path(ledger_path)

    def head(self) -> tuple[int, str | None]:
        events = read_ledger(self._path)
        return (0, None) if not events else (len(events), _event_hash(events[-1]))

    def append(self, event: LedgerEvent) -> LedgerAppendResult:
        existing = read_ledger(self._path)
        next_sequence = len(existing)
        previous_hash = None if not existing else _event_hash(existing[-1])
        if event.sequence != next_sequence:
            raise StoreError("SEQUENCE_MISMATCH")
        if event.previous_event_hash != previous_hash:
            raise StoreError("HEAD_MISMATCH")
        if existing and event.task_id != existing[0]["task_id"]:
            raise StoreError("TASK_ID_MISMATCH")
        line = canonical_bytes(event.to_dict()) + b"\n"
        # The ledger parent is the already-created private task root.
        if self._path.parent.is_symlink():
            raise StoreError("SYMLINK_ESCAPE", "$.ledger_path")
        self._path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self._path.parent, 0o700)
        newly_created = not self._path.exists()
        flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
        fd = os.open(self._path, flags, 0o600)
        with os.fdopen(fd, "ab") as stream:
            stream.write(line)
            stream.flush()
            os.fsync(stream.fileno())
        if newly_created:
            _fsync_dir(self._path.parent)
        written = read_ledger(self._path)
        if len(written) != next_sequence + 1 or written[-1] != event.to_dict():
            raise StoreError("APPEND_VERIFY_FAILED")
        return LedgerAppendResult(event=event, head_hash=_event_hash(event.to_dict()))


@dataclass(frozen=True)
class RecoveryResult:
    recovered: bool
    valid_event_count: int


def recover_torn_tail(ledger_path: Path) -> RecoveryResult:
    """Remove only the non-newline-terminated final fragment after validating the prefix."""
    ledger_path = Path(ledger_path)
    if not ledger_path.exists():
        return RecoveryResult(recovered=False, valid_event_count=0)
    raw = ledger_path.read_bytes()
    if not raw or raw.endswith(b"\n"):
        events = read_ledger(ledger_path)
        return RecoveryResult(recovered=False, valid_event_count=len(events))
    parts = raw.split(b"\n")
    prefix_lines = parts[:-1]
    try:
        prior_events = [_json_object(line, f"$[{i}]") for i, line in enumerate(prefix_lines)]
    except StoreError as exc:
        raise StoreError("UNRECOVERABLE_PRIOR_STATE") from exc
    if not verify_chain(prior_events):
        raise StoreError("UNRECOVERABLE_PRIOR_STATE")
    payload = b"".join(line + b"\n" for line in prefix_lines)
    tmp_path = ledger_path.with_suffix(ledger_path.suffix + ".recover.tmp")
    try:
        fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp_path, ledger_path)
        _fsync_dir(ledger_path.parent)
    finally:
        tmp_path.unlink(missing_ok=True)
    return RecoveryResult(recovered=True, valid_event_count=len(prior_events))
