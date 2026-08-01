from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .canonical import atomic_write, canonical_json_bytes, loads_strict, sha256_bytes
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
        self.task_root = task_root
        self.task_id = task_id
        self.path = task_root / "ledger.jsonl"
        self.pending = task_root / "ledger.pending.json"

    def initialize(self) -> None:
        if not self.path.exists():
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.fsync(fd)
            os.close(fd)
            fd_dir = os.open(self.task_root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(fd_dir)
            finally:
                os.close(fd_dir)
        self.read(recover_partial=True)
        self.recover_pending()

    def _event_with_hash(self, *, sequence: int, event_type: str, payload_ref: str, payload_sha256: str, previous: str) -> dict[str, Any]:
        payload_path = self.task_root / payload_ref
        payload_size = os.lstat(payload_path).st_size if payload_path.exists() else 0
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
        if not self.path.exists():
            return []
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
        for index, line in enumerate(data.splitlines(), start=1):
            require(line.strip() != b"", "LEDGER_BLANK_LINE", "blank committed ledger line")
            value = loads_strict(line)
            require(isinstance(value, dict), "LEDGER_SCHEMA", "ledger event must be an object")
            required = {"schema_version", "task_id", "sequence", "event_id", "event_type", "timestamp_utc", "payload_ref", "payload_sha256", "payload_size", "previous_event_sha256", "event_sha256"}
            require(set(value) == required, "LEDGER_SCHEMA", "ledger event fields mismatch")
            require(value["schema_version"] == 1 and value["task_id"] == self.task_id, "LEDGER_IDENTITY", "ledger task identity mismatch")
            require(value["sequence"] == index, "LEDGER_SEQUENCE", "invalid ledger sequence")
            require(value["event_id"] not in ids, "LEDGER_DUPLICATE_EVENT", "duplicate ledger event id")
            ids.add(value["event_id"])
            require(value["previous_event_sha256"] == previous, "LEDGER_HASH_CHAIN", "previous-event hash mismatch")
            unhashed = dict(value)
            claimed = str(unhashed.pop("event_sha256"))
            computed = sha256_bytes(canonical_json_bytes(unhashed))
            require(claimed == computed, "LEDGER_EVENT_HASH", "event hash mismatch")
            payload = self.task_root / str(value["payload_ref"])
            if payload.exists():
                st = os.lstat(payload)
                require(os.path.isfile(payload) and st.st_nlink == 1, "LEDGER_PAYLOAD_UNSAFE", "ledger payload is not a unique regular file")
                require(st.st_mode & 0o7000 == 0, "LEDGER_PAYLOAD_MODE", "ledger payload has unsafe special bits")
                require(st.st_size == int(value["payload_size"]), "LEDGER_PAYLOAD_SIZE", "ledger payload size mismatch")
                require(sha256_bytes(payload.read_bytes()) == value["payload_sha256"], "LEDGER_PAYLOAD_HASH", "ledger payload hash mismatch")
            canonical = canonical_json_bytes(value)
            events.append(LedgerEvent(value, canonical))
            previous = claimed
        return events

    def recover_pending(self) -> None:
        if not self.pending.exists():
            return
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
        with self.path.open("ab", buffering=0) as handle:
            handle.write(canonical)
            os.fsync(handle.fileno())
        self.pending.unlink()

    def append(self, event_type: str, payload_ref: str, payload_sha256: str) -> LedgerEvent:
        self.recover_pending()
        events = self.read(recover_partial=True)
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
