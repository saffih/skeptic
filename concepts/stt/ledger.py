from __future__ import annotations

import os
import stat
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .canonical import atomic_write, canonical_json_bytes, ensure_no_symlink_components, loads_strict, safe_relpath, sha256_bytes
from .contracts import EVENT_TYPES
from .errors import STTError, require


ZERO_HASH = "0" * 64


@dataclass(frozen=True, slots=True)
class LedgerEvent:
    value: dict[str, Any]
    canonical: bytes

    @property
    def event_sha256(self) -> str:
        return str(self.value["event_sha256"])


class Ledger:
    def __init__(self, task_root: Path, task_id: str) -> None:
        # macOS exposes /var and /tmp through system symlinks.  Normalize the
        # trusted root once; paths below it must still have no symlink
        # components.
        self.task_root = Path(os.path.realpath(os.fspath(task_root)))
        self.task_id = task_id
        self.path = self.task_root / "ledger.jsonl"
        self.pending = self.task_root / "ledger.pending.json"

    def _validate_control_file(self, path: Path, label: str) -> os.stat_result:
        try:
            value = os.lstat(path)
        except FileNotFoundError as exc:
            raise STTError("CONTROL_STATE_FAILED", f"{label} is missing") from exc
        require(stat.S_ISREG(value.st_mode) and value.st_uid == os.geteuid() and value.st_nlink == 1, "CONTROL_STATE_FAILED", f"{label} is not an owned unique regular file")
        require(value.st_mode & 0o7000 == 0 and value.st_mode & 0o022 == 0, "CONTROL_STATE_FAILED", f"{label} is not owner-controlled")
        return value

    def initialize(self) -> None:
        if not self.path.exists() and not self.path.is_symlink():
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.fsync(fd)
            os.close(fd)
            fd_dir = os.open(self.task_root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(fd_dir)
            finally:
                os.close(fd_dir)
        self._validate_control_file(self.path, "ledger.jsonl")
        self.read(recover_partial=True)
        self.recover_pending()

    def _validate_payload(self, payload_ref: str, payload_sha256: str, payload_size: int | None = None) -> int:
        rel = safe_relpath(payload_ref)
        require(isinstance(payload_sha256, str) and len(payload_sha256) == 64 and all(character in "0123456789abcdef" for character in payload_sha256), "LEDGER_PAYLOAD_HASH", "ledger payload SHA-256 is malformed")
        payload_path = self.task_root / rel
        resolved_parent = payload_path.parent.resolve(strict=False)
        root = self.task_root.resolve(strict=False)
        require(resolved_parent == root or root in resolved_parent.parents, "LEDGER_PAYLOAD_ESCAPE", "ledger payload escapes Task root")
        ensure_no_symlink_components(payload_path, include_leaf=False)
        try:
            st = os.lstat(payload_path)
        except FileNotFoundError as exc:
            raise STTError("LEDGER_PAYLOAD_MISSING", f"ledger payload missing: {rel}") from exc
        require(stat.S_ISREG(st.st_mode), "LEDGER_PAYLOAD_UNSAFE", "ledger payload is not a regular file")
        require(st.st_uid == os.geteuid(), "LEDGER_PAYLOAD_OWNER", "ledger payload owner mismatch")
        require(st.st_nlink == 1, "LEDGER_PAYLOAD_UNSAFE", "ledger payload is not uniquely linked")
        require(st.st_mode & 0o7000 == 0 and st.st_mode & 0o022 == 0, "LEDGER_PAYLOAD_MODE", "ledger payload is not owner-controlled")
        if payload_size is not None:
            require(type(payload_size) is int and st.st_size == payload_size, "LEDGER_PAYLOAD_SIZE", "ledger payload size mismatch")
        try:
            fd = os.open(payload_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        except OSError as exc:
            raise STTError("LEDGER_PAYLOAD_UNSAFE", f"ledger payload cannot be opened safely: {rel}") from exc
        try:
            opened = os.fstat(fd)
            require((opened.st_dev, opened.st_ino, opened.st_size) == (st.st_dev, st.st_ino, st.st_size), "LEDGER_PAYLOAD_UNSAFE", "ledger payload changed before read")
            chunks: list[bytes] = []
            remaining = opened.st_size
            while remaining:
                chunk = os.read(fd, min(1024 * 1024, remaining))
                require(bool(chunk), "LEDGER_PAYLOAD_UNSAFE", "ledger payload truncated during read")
                chunks.append(chunk)
                remaining -= len(chunk)
            require(os.read(fd, 1) == b"", "LEDGER_PAYLOAD_UNSAFE", "ledger payload grew during read")
            after = os.fstat(fd)
            require((opened.st_dev, opened.st_ino, opened.st_size) == (after.st_dev, after.st_ino, after.st_size), "LEDGER_PAYLOAD_UNSAFE", "ledger payload changed during read")
            data = b"".join(chunks)
        finally:
            os.close(fd)
        require(sha256_bytes(data) == payload_sha256, "LEDGER_PAYLOAD_HASH", "ledger payload hash mismatch")
        value = loads_strict(data)
        require(isinstance(value, dict), "LEDGER_PAYLOAD_SCHEMA", "lifecycle payload must be a JSON object")
        return st.st_size

    def _event_with_hash(self, *, sequence: int, event_type: str, payload_ref: str, payload_sha256: str, previous: str) -> dict[str, Any]:
        require(event_type in EVENT_TYPES, "LEDGER_EVENT_TYPE", f"unknown lifecycle event type: {event_type}")
        payload_size = self._validate_payload(payload_ref, payload_sha256)
        base = {
            "schema_version": 1,
            "task_id": self.task_id,
            "sequence": sequence,
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "payload_ref": payload_ref,
            "payload_sha256": payload_sha256,
            "payload_size": payload_size,
            "previous_event_sha256": previous,
        }
        event_hash = sha256_bytes(canonical_json_bytes(base))
        return {**base, "event_sha256": event_hash}

    def read(self, *, recover_partial: bool = False) -> list[LedgerEvent]:
        if not self.path.exists() and not self.path.is_symlink():
            return []
        self._validate_control_file(self.path, "ledger.jsonl")
        data = self.path.read_bytes()
        if data and not data.endswith(b"\n"):
            if not recover_partial:
                raise STTError("LEDGER_PARTIAL_SUFFIX", "ledger has non-newline partial suffix")
            cut = data.rfind(b"\n") + 1
            with self.path.open("r+b") as handle:
                handle.truncate(cut)
                handle.flush()
                os.fsync(handle.fileno())
            data = data[:cut]
        events: list[LedgerEvent] = []
        previous = ZERO_HASH
        ids: set[str] = set()
        closed = False
        for index, line in enumerate(data.splitlines(), start=1):
            require(not closed, "CONTROL_STATE_TERMINAL", "no ledger event may follow terminal or nonresumable block")
            require(line.strip() != b"", "LEDGER_BLANK_LINE", "blank committed ledger line")
            value = loads_strict(line)
            require(isinstance(value, dict), "LEDGER_SCHEMA", "ledger event must be an object")
            required = {"schema_version", "task_id", "sequence", "event_id", "event_type", "timestamp_utc", "payload_ref", "payload_sha256", "payload_size", "previous_event_sha256", "event_sha256"}
            require(set(value) == required, "LEDGER_SCHEMA", "ledger event fields mismatch")
            require(value["schema_version"] == 1 and value["task_id"] == self.task_id, "LEDGER_IDENTITY", "ledger task identity mismatch")
            require(value["sequence"] == index, "LEDGER_SEQUENCE", "invalid ledger sequence")
            require(value["event_type"] in EVENT_TYPES, "LEDGER_EVENT_TYPE", "unknown committed lifecycle event type")
            require(isinstance(value["event_id"], str) and value["event_id"], "LEDGER_SCHEMA", "ledger event ID invalid")
            require(isinstance(value["timestamp_utc"], str) and value["timestamp_utc"], "LEDGER_SCHEMA", "ledger timestamp invalid")
            require(value["event_id"] not in ids, "LEDGER_DUPLICATE_EVENT", "duplicate ledger event id")
            ids.add(value["event_id"])
            require(value["previous_event_sha256"] == previous, "LEDGER_HASH_CHAIN", "previous-event hash mismatch")
            unhashed = dict(value)
            claimed = str(unhashed.pop("event_sha256"))
            computed = sha256_bytes(canonical_json_bytes(unhashed))
            require(claimed == computed, "LEDGER_EVENT_HASH", "event hash mismatch")
            self._validate_payload(str(value["payload_ref"]), str(value["payload_sha256"]), value["payload_size"])
            canonical = canonical_json_bytes(value)
            events.append(LedgerEvent(value, canonical))
            previous = claimed
            closed = value["event_type"] in {"TERMINAL_RECEIPT_RECORDED", "TASK_BLOCKED_UNKNOWN"}
        return events

    def recover_pending(self) -> None:
        if not self.pending.exists() and not self.pending.is_symlink():
            return
        self._validate_control_file(self.pending, "ledger.pending.json")
        pending_value = loads_strict(self.pending.read_bytes())
        require(isinstance(pending_value, dict), "CONTROL_STATE_FAILED", "pending ledger event malformed")
        events = self.read(recover_partial=True)
        canonical = canonical_json_bytes(pending_value)
        if events and events[-1].canonical == canonical:
            self.pending.unlink()
            return
        expected_sequence = len(events) + 1
        require(pending_value.get("sequence") == expected_sequence, "CONTROL_STATE_FAILED", "pending ledger event conflicts with head")
        previous = events[-1].event_sha256 if events else ZERO_HASH
        require(pending_value.get("previous_event_sha256") == previous, "CONTROL_STATE_FAILED", "pending ledger chain mismatch")
        require(pending_value.get("event_type") in EVENT_TYPES, "LEDGER_EVENT_TYPE", "pending lifecycle event type invalid")
        require(not any(event.value["event_type"] in {"TERMINAL_RECEIPT_RECORDED", "TASK_BLOCKED_UNKNOWN"} for event in events), "CONTROL_STATE_TERMINAL", "no ledger event may follow terminal or nonresumable block")
        self._validate_payload(str(pending_value.get("payload_ref")), str(pending_value.get("payload_sha256")), pending_value.get("payload_size"))
        with self.path.open("ab", buffering=0) as handle:
            handle.write(canonical)
            os.fsync(handle.fileno())
        self.pending.unlink()

    def append(self, event_type: str, payload_ref: str, payload_sha256: str) -> LedgerEvent:
        self.recover_pending()
        events = self.read(recover_partial=True)
        require(event_type in EVENT_TYPES, "LEDGER_EVENT_TYPE", f"unknown lifecycle event type: {event_type}")
        require(not any(event.value["event_type"] in {"TERMINAL_RECEIPT_RECORDED", "TASK_BLOCKED_UNKNOWN"} for event in events), "CONTROL_STATE_TERMINAL", "no ledger event may follow terminal or nonresumable block")
        previous = events[-1].event_sha256 if events else ZERO_HASH
        value = self._event_with_hash(sequence=len(events) + 1, event_type=event_type, payload_ref=payload_ref, payload_sha256=payload_sha256, previous=previous)
        pending_bytes = canonical_json_bytes(value)
        atomic_write(self.pending, pending_bytes, mode=0o600, create_only=True)
        with self.path.open("ab", buffering=0) as handle:
            handle.write(pending_bytes)
            os.fsync(handle.fileno())
        self.pending.unlink()
        return LedgerEvent(value, pending_bytes)

    def types(self) -> Iterable[str]:
        return (str(event.value["event_type"]) for event in self.read(recover_partial=True))
