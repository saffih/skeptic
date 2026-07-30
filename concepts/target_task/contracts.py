"""Shared deterministic schemas for the Claude Code Target Task MVP.

Field shapes owned elsewhere are imported, not redefined: a compact Luna
receipt is a `capabilities.body_state` object; a specialist dispatch/return
is a `capabilities.execution_envelope` task envelope/role return. This module
owns only what nothing else in the repository owns: the append-only ledger
event shape and the small phase/action vocabulary that `flow.py` sequences.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MAX_LEDGER_EVENT_BYTES = 4096

LEDGER_EVENT_FIELDS = {
    "schema_version", "sequence", "event_id", "task_id", "phase",
    "accepted_plan_ref", "current_step", "operation_id", "attempt",
    "request_ref", "result_ref", "status", "validation", "blocker",
    "allowed_actions", "next_action", "previous_event_hash", "receipt_ref",
}


class ContractError(ValueError):
    def __init__(self, code: str, path: str = "$") -> None:
        self.code, self.path = code, path
        super().__init__(f"{code} at {path}")


class Phase(str, Enum):
    """Legal lifecycle phases. Owned and sequenced by flow.py, not here."""

    MISSION_PERSISTED = "MISSION_PERSISTED"
    PLAN_DRAFTED = "PLAN_DRAFTED"
    PLAN_REVIEW = "PLAN_REVIEW"
    PLAN_SEALED = "PLAN_SEALED"
    STEP_EXECUTING = "STEP_EXECUTING"
    STEP_VALIDATED = "STEP_VALIDATED"
    CANDIDATE_FROZEN = "CANDIDATE_FROZEN"
    FINAL_REVIEW = "FINAL_REVIEW"
    INTEGRATED = "INTEGRATED"
    CLOSED = "CLOSED"
    BLOCKED = "BLOCKED"


class LunaAction(str, Enum):
    """The only actions the compact durable Lead may request."""

    CONTINUE = "CONTINUE"
    ADVANCE = "ADVANCE"
    RETRY = "RETRY"
    RECOVER = "RECOVER"
    STOP = "STOP"


@dataclass(frozen=True)
class LedgerEvent:
    """One append-only, durable lifecycle fact. Never carries a body."""

    schema_version: str
    sequence: int
    event_id: str
    task_id: str
    phase: str
    accepted_plan_ref: Optional[str]
    current_step: Optional[str]
    operation_id: Optional[str]
    attempt: int
    request_ref: Optional[str]
    result_ref: Optional[str]
    status: str
    validation: str
    blocker: Optional[str]
    allowed_actions: tuple[str, ...]
    next_action: Optional[str]
    previous_event_hash: Optional[str]
    receipt_ref: Optional[str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_actions"] = list(self.allowed_actions)
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LedgerEvent":
        _validate_event_dict(data)
        kwargs = dict(data)
        kwargs["allowed_actions"] = tuple(data["allowed_actions"])
        return cls(**kwargs)


def _validate_event_dict(data: Mapping[str, Any]) -> None:
    if not isinstance(data, Mapping) or set(data) != LEDGER_EVENT_FIELDS:
        raise ContractError("FIELDS")
    if not isinstance(data["sequence"], int) or isinstance(data["sequence"], bool) or data["sequence"] < 0:
        raise ContractError("SEQUENCE", "$.sequence")
    if not isinstance(data["attempt"], int) or isinstance(data["attempt"], bool) or data["attempt"] < 1:
        raise ContractError("ATTEMPT", "$.attempt")
    if data["phase"] not in {p.value for p in Phase}:
        raise ContractError("PHASE", "$.phase")
    if not isinstance(data["allowed_actions"], (list, tuple)) or not data["allowed_actions"]:
        raise ContractError("ALLOWED_ACTIONS", "$.allowed_actions")
    for action in data["allowed_actions"]:
        if action not in {a.value for a in LunaAction}:
            raise ContractError("ALLOWED_ACTIONS", "$.allowed_actions")
    if data["next_action"] is not None and data["next_action"] not in {a.value for a in LunaAction}:
        raise ContractError("NEXT_ACTION", "$.next_action")
    for key in ("previous_event_hash", "receipt_ref"):
        value = data[key]
        if key == "previous_event_hash" and value is not None and not SHA256_RE.fullmatch(value):
            raise ContractError("SHA256", f"$.{key}")
    for key in ("event_id", "task_id", "status", "validation"):
        if not isinstance(data[key], str) or not data[key]:
            raise ContractError("SHORT_STRING", f"$.{key}")
    for key in ("accepted_plan_ref", "current_step", "operation_id", "request_ref", "result_ref", "blocker", "receipt_ref"):
        value = data[key]
        if value is not None and (not isinstance(value, str) or not value or len(value.encode("utf-8")) > 256):
            raise ContractError("OPTIONAL_SHORT_STRING", f"$.{key}")


def canonical_bytes(event: Mapping[str, Any]) -> bytes:
    """Canonical UTF-8 JSONL encoding of one ledger event (no trailing LF;
    the ledger appender owns line termination)."""
    _validate_event_dict(event)
    raw = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_LEDGER_EVENT_BYTES:
        raise ContractError("TOO_LARGE")
    return raw


class CursorStatus(str, Enum):
    """Observable state of the one sequential sealed-Plan cursor."""

    STEP_READY = "STEP_READY"
    OPERATION_ADMITTED = "OPERATION_ADMITTED"
    OPERATION_FAILED = "OPERATION_FAILED"
    EXECUTION_OUTCOME_UNKNOWN = "EXECUTION_OUTCOME_UNKNOWN"
    STEP_AWAITING_ADVANCE = "STEP_AWAITING_ADVANCE"
    EXECUTION_COMPLETE = "EXECUTION_COMPLETE"


@dataclass(frozen=True)
class StepCursor:
    """Immutable cursor for one linear Plan.

    `attempt` counts admitted attempts for the current step.
    `successful_operation_id` binds ADVANCE to exactly one validated success.
    """

    step_ids: tuple[str, ...]
    current_index: int = 0
    status: CursorStatus = CursorStatus.STEP_READY
    operation_id: Optional[str] = None
    attempt: int = 0
    completed_step_ids: tuple[str, ...] = ()
    successful_operation_id: Optional[str] = None
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if not self.step_ids or any(not isinstance(step, str) or not step for step in self.step_ids):
            raise ContractError("STEP_IDS", "$.step_ids")
        if len(set(self.step_ids)) != len(self.step_ids):
            raise ContractError("DUPLICATE_STEP_ID", "$.step_ids")
        if not isinstance(self.current_index, int) or isinstance(self.current_index, bool):
            raise ContractError("CURRENT_INDEX", "$.current_index")
        if not 0 <= self.current_index <= len(self.step_ids):
            raise ContractError("CURRENT_INDEX", "$.current_index")
        if not isinstance(self.attempt, int) or isinstance(self.attempt, bool) or self.attempt < 0:
            raise ContractError("ATTEMPT", "$.attempt")
        if not isinstance(self.max_attempts, int) or isinstance(self.max_attempts, bool) or self.max_attempts < 1:
            raise ContractError("MAX_ATTEMPTS", "$.max_attempts")
        if self.completed_step_ids != self.step_ids[: self.current_index]:
            raise ContractError("COMPLETED_STEP_IDS", "$.completed_step_ids")
        if self.current_index == len(self.step_ids):
            if self.status is not CursorStatus.EXECUTION_COMPLETE:
                raise ContractError("TERMINAL_STATUS", "$.status")
            if self.operation_id is not None or self.successful_operation_id is not None:
                raise ContractError("TERMINAL_OPERATION", "$.operation_id")
        elif self.status is CursorStatus.EXECUTION_COMPLETE:
            raise ContractError("EARLY_EXECUTION_COMPLETE", "$.status")

    @property
    def current_step(self) -> Optional[str]:
        if self.current_index >= len(self.step_ids):
            return None
        return self.step_ids[self.current_index]
