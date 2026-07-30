"""Deterministic provider-neutral schemas for the Target Task lifecycle.

This module owns the closed lifecycle vocabulary, immutable ledger-event shape,
minimal sealed-Plan schema, and the complete serializable linear-step cursor.
Task bodies never belong in these structures.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping, Optional

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
MAX_LEDGER_EVENT_BYTES = 4096
MAX_PLAN_BYTES = 131072
MAX_CURSOR_BYTES = 16384
MAX_SHORT_BYTES = 512


class ContractError(ValueError):
    def __init__(self, code: str, path: str = "$") -> None:
        self.code, self.path = code, path
        super().__init__(f"{code} at {path}")


def validate_task_id(value: Any, path: str = "$.task_id") -> str:
    if not isinstance(value, str) or not TASK_ID_RE.fullmatch(value):
        raise ContractError("TASK_ID", path)
    return value


def _safe_id(value: Any, path: str) -> str:
    if not isinstance(value, str) or not SAFE_ID_RE.fullmatch(value):
        raise ContractError("ID", path)
    return value


def _short(value: Any, path: str, *, maximum: int = MAX_SHORT_BYTES) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > maximum:
        raise ContractError("SHORT_STRING", path)
    return value


def _safe_relative(value: Any, path: str) -> str:
    value = _short(value, path, maximum=512)
    if value.startswith("/") or "\\" in value:
        raise ContractError("UNSAFE_PATH", path)
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ContractError("UNSAFE_PATH", path)
    return value


class Phase(str, Enum):
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
    CONTINUE = "CONTINUE"
    ADVANCE = "ADVANCE"
    RETRY = "RETRY"
    RECOVER = "RECOVER"
    STOP = "STOP"


LEDGER_STATUSES = {
    "READY",
    "ADMITTED",
    "COMPLETE",
    "FAILED",
    "UNKNOWN",
    "AWAITING_ADVANCE",
    "STEP_ACCEPTED",
    "EXECUTION_COMPLETE",
    "BLOCKED",
    "INTEGRATED",
    "CLOSED",
}
LEDGER_VALIDATIONS = {"PASS", "FAIL", "NOT_RUN", "UNKNOWN"}

LEDGER_EVENT_FIELDS = {
    "schema_version",
    "sequence",
    "event_id",
    "task_id",
    "phase",
    "accepted_plan_ref",
    "current_step",
    "operation_id",
    "attempt",
    "request_ref",
    "result_ref",
    "cursor_ref",
    "status",
    "validation",
    "blocker",
    "allowed_actions",
    "next_action",
    "previous_event_hash",
    "receipt_ref",
}


@dataclass(frozen=True)
class LedgerEvent:
    """One append-only lifecycle fact. No field may contain a substantive body."""

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
    cursor_ref: Optional[str]
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
    if data["schema_version"] != "1":
        raise ContractError("SCHEMA_VERSION", "$.schema_version")
    if not isinstance(data["sequence"], int) or isinstance(data["sequence"], bool) or data["sequence"] < 0:
        raise ContractError("SEQUENCE", "$.sequence")
    if not isinstance(data["attempt"], int) or isinstance(data["attempt"], bool) or data["attempt"] < 0:
        raise ContractError("ATTEMPT", "$.attempt")
    _safe_id(data["event_id"], "$.event_id")
    validate_task_id(data["task_id"])
    if data["phase"] not in {p.value for p in Phase}:
        raise ContractError("PHASE", "$.phase")
    if data["status"] not in LEDGER_STATUSES:
        raise ContractError("STATUS", "$.status")
    if data["validation"] not in LEDGER_VALIDATIONS:
        raise ContractError("VALIDATION", "$.validation")

    actions = data["allowed_actions"]
    if not isinstance(actions, (list, tuple)) or len(set(actions)) != len(actions):
        raise ContractError("ALLOWED_ACTIONS", "$.allowed_actions")
    for action in actions:
        if action not in {a.value for a in LunaAction}:
            raise ContractError("ALLOWED_ACTIONS", "$.allowed_actions")
    if data["phase"] == Phase.CLOSED.value:
        if actions or data["next_action"] is not None or data["status"] != "CLOSED":
            raise ContractError("CLOSED_EVENT", "$.allowed_actions")
    elif not actions:
        raise ContractError("ALLOWED_ACTIONS", "$.allowed_actions")
    if data["next_action"] is not None and data["next_action"] not in actions:
        raise ContractError("NEXT_ACTION", "$.next_action")

    previous = data["previous_event_hash"]
    if previous is not None and (not isinstance(previous, str) or not SHA256_RE.fullmatch(previous)):
        raise ContractError("SHA256", "$.previous_event_hash")

    for key in (
        "accepted_plan_ref",
        "request_ref",
        "result_ref",
        "cursor_ref",
        "receipt_ref",
    ):
        value = data[key]
        if value is not None:
            _safe_relative(value, f"$.{key}")
    for key in ("current_step", "operation_id"):
        value = data[key]
        if value is not None:
            _safe_id(value, f"$.{key}")
    status = data["status"]
    if status in {"ADMITTED", "FAILED", "UNKNOWN", "AWAITING_ADVANCE"}:
        if data["operation_id"] is None or data["attempt"] < 1:
            raise ContractError("OPERATION_IDENTITY", "$.operation_id")
    if status == "READY" and any(data[key] is not None for key in ("operation_id", "request_ref", "result_ref", "receipt_ref")):
        raise ContractError("READY_IDENTITY", "$.status")
    if status == "ADMITTED" and (data["request_ref"] is None or data["receipt_ref"] is None or data["result_ref"] is not None):
        raise ContractError("ADMISSION_IDENTITY", "$.status")
    if status in {"FAILED", "UNKNOWN", "AWAITING_ADVANCE", "STEP_ACCEPTED"}:
        if any(data[key] is None for key in ("request_ref", "result_ref", "receipt_ref")):
            raise ContractError("OUTCOME_IDENTITY", "$.status")
    blocker = data["blocker"]
    if blocker is not None:
        _short(blocker, "$.blocker", maximum=256)


def canonical_bytes(event: Mapping[str, Any]) -> bytes:
    _validate_event_dict(event)
    raw = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_LEDGER_EVENT_BYTES:
        raise ContractError("TOO_LARGE")
    return raw


# --- Minimal sealed Plan ----------------------------------------------------

PLAN_FIELDS = {"schema_version", "plan_id", "task_id", "mission_sha256", "steps"}
PLAN_STEP_FIELDS = {"step_id", "objective", "role", "success_criteria"}
PLAN_ROLES = {"worker", "command"}


def validate_plan_dict(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != PLAN_FIELDS:
        raise ContractError("PLAN_FIELDS")
    if value["schema_version"] != "1":
        raise ContractError("PLAN_SCHEMA_VERSION", "$.schema_version")
    _safe_id(value["plan_id"], "$.plan_id")
    validate_task_id(value["task_id"])
    if not isinstance(value["mission_sha256"], str) or not SHA256_RE.fullmatch(value["mission_sha256"]):
        raise ContractError("SHA256", "$.mission_sha256")
    steps = value["steps"]
    if not isinstance(steps, list) or not steps or len(steps) > 128:
        raise ContractError("PLAN_STEPS", "$.steps")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        path = f"$.steps/{index}"
        if not isinstance(step, Mapping) or set(step) != PLAN_STEP_FIELDS:
            raise ContractError("PLAN_STEP_FIELDS", path)
        step_id = _safe_id(step["step_id"], f"{path}/step_id")
        if step_id in seen:
            raise ContractError("DUPLICATE_STEP_ID", f"{path}/step_id")
        seen.add(step_id)
        objective = _short(step["objective"], f"{path}/objective", maximum=2048)
        if step["role"] not in PLAN_ROLES:
            raise ContractError("PLAN_ROLE", f"{path}/role")
        criteria = step["success_criteria"]
        if not isinstance(criteria, list) or not criteria or len(criteria) > 32:
            raise ContractError("SUCCESS_CRITERIA", f"{path}/success_criteria")
        normalized_criteria = [
            _short(item, f"{path}/success_criteria/{i}", maximum=1024)
            for i, item in enumerate(criteria)
        ]
        normalized.append(
            {
                "step_id": step_id,
                "objective": objective,
                "role": step["role"],
                "success_criteria": normalized_criteria,
            }
        )
    return {
        "schema_version": "1",
        "plan_id": value["plan_id"],
        "task_id": value["task_id"],
        "mission_sha256": value["mission_sha256"],
        "steps": normalized,
    }


def canonical_plan_bytes(value: Mapping[str, Any]) -> bytes:
    normalized = validate_plan_dict(value)
    raw = (json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(raw) > MAX_PLAN_BYTES:
        raise ContractError("PLAN_TOO_LARGE")
    return raw


def parse_plan_bytes(raw: bytes) -> dict[str, Any]:
    if len(raw) > MAX_PLAN_BYTES:
        raise ContractError("PLAN_TOO_LARGE")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError("PLAN_UTF8") from exc
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ContractError("PLAN_ENCODING")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContractError("PLAN_DUPLICATE_KEY")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs)
    except ContractError:
        raise
    except json.JSONDecodeError as exc:
        raise ContractError("PLAN_JSON") from exc
    normalized = validate_plan_dict(value)
    if canonical_plan_bytes(normalized) != raw:
        raise ContractError("PLAN_NONCANONICAL")
    return normalized


def plan_step_ids(plan: Mapping[str, Any]) -> tuple[str, ...]:
    normalized = validate_plan_dict(plan)
    return tuple(step["step_id"] for step in normalized["steps"])


# --- Complete immutable linear cursor --------------------------------------


class CursorStatus(str, Enum):
    STEP_READY = "STEP_READY"
    OPERATION_ADMITTED = "OPERATION_ADMITTED"
    OPERATION_FAILED = "OPERATION_FAILED"
    EXECUTION_OUTCOME_UNKNOWN = "EXECUTION_OUTCOME_UNKNOWN"
    STEP_AWAITING_ADVANCE = "STEP_AWAITING_ADVANCE"
    EXECUTION_COMPLETE = "EXECUTION_COMPLETE"


CURSOR_FIELDS = {
    "schema_version",
    "step_ids",
    "current_index",
    "status",
    "operation_id",
    "attempt",
    "completed_step_ids",
    "successful_operation_id",
    "max_attempts",
}


@dataclass(frozen=True)
class StepCursor:
    step_ids: tuple[str, ...]
    current_index: int = 0
    status: CursorStatus = CursorStatus.STEP_READY
    operation_id: Optional[str] = None
    attempt: int = 0
    completed_step_ids: tuple[str, ...] = ()
    successful_operation_id: Optional[str] = None
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if not self.step_ids or len(self.step_ids) > 128:
            raise ContractError("STEP_IDS", "$.step_ids")
        for index, step in enumerate(self.step_ids):
            _safe_id(step, f"$.step_ids/{index}")
        if len(set(self.step_ids)) != len(self.step_ids):
            raise ContractError("DUPLICATE_STEP_ID", "$.step_ids")
        if not isinstance(self.current_index, int) or isinstance(self.current_index, bool):
            raise ContractError("CURRENT_INDEX", "$.current_index")
        if not 0 <= self.current_index <= len(self.step_ids):
            raise ContractError("CURRENT_INDEX", "$.current_index")
        if not isinstance(self.attempt, int) or isinstance(self.attempt, bool) or self.attempt < 0:
            raise ContractError("ATTEMPT", "$.attempt")
        if not isinstance(self.max_attempts, int) or isinstance(self.max_attempts, bool) or not 1 <= self.max_attempts <= 100:
            raise ContractError("MAX_ATTEMPTS", "$.max_attempts")
        if self.attempt > self.max_attempts:
            raise ContractError("ATTEMPT_POLICY", "$.attempt")
        if self.completed_step_ids != self.step_ids[: self.current_index]:
            raise ContractError("COMPLETED_STEP_IDS", "$.completed_step_ids")

        active = self.current_index < len(self.step_ids)
        if not active:
            if self.status is not CursorStatus.EXECUTION_COMPLETE:
                raise ContractError("TERMINAL_STATUS", "$.status")
            if self.operation_id is not None or self.successful_operation_id is not None:
                raise ContractError("TERMINAL_OPERATION", "$.operation_id")
            return
        if self.status is CursorStatus.EXECUTION_COMPLETE:
            raise ContractError("EARLY_EXECUTION_COMPLETE", "$.status")
        if self.status is CursorStatus.STEP_READY:
            if self.attempt >= self.max_attempts:
                raise ContractError("READY_ATTEMPT_EXHAUSTED", "$.attempt")
            if self.operation_id is not None or self.successful_operation_id is not None:
                raise ContractError("READY_OPERATION", "$.operation_id")
        elif self.status is CursorStatus.STEP_AWAITING_ADVANCE:
            if not self.operation_id or self.operation_id != self.successful_operation_id:
                raise ContractError("SUCCESSFUL_OPERATION", "$.successful_operation_id")
        else:
            if self.attempt < 1:
                raise ContractError("ACTIVE_ATTEMPT", "$.attempt")
            if not self.operation_id or self.successful_operation_id is not None:
                raise ContractError("ACTIVE_OPERATION", "$.operation_id")

    @property
    def current_step(self) -> Optional[str]:
        return None if self.current_index >= len(self.step_ids) else self.step_ids[self.current_index]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1",
            "step_ids": list(self.step_ids),
            "current_index": self.current_index,
            "status": self.status.value,
            "operation_id": self.operation_id,
            "attempt": self.attempt,
            "completed_step_ids": list(self.completed_step_ids),
            "successful_operation_id": self.successful_operation_id,
            "max_attempts": self.max_attempts,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "StepCursor":
        if not isinstance(value, Mapping) or set(value) != CURSOR_FIELDS:
            raise ContractError("CURSOR_FIELDS")
        if value["schema_version"] != "1":
            raise ContractError("CURSOR_SCHEMA_VERSION", "$.schema_version")
        try:
            status = CursorStatus(value["status"])
        except (TypeError, ValueError) as exc:
            raise ContractError("CURSOR_STATUS", "$.status") from exc
        if not isinstance(value["step_ids"], list) or not isinstance(value["completed_step_ids"], list):
            raise ContractError("CURSOR_LIST")
        return cls(
            step_ids=tuple(value["step_ids"]),
            current_index=value["current_index"],
            status=status,
            operation_id=value["operation_id"],
            attempt=value["attempt"],
            completed_step_ids=tuple(value["completed_step_ids"]),
            successful_operation_id=value["successful_operation_id"],
            max_attempts=value["max_attempts"],
        )


def canonical_cursor_bytes(cursor: StepCursor | Mapping[str, Any]) -> bytes:
    value = cursor.to_dict() if isinstance(cursor, StepCursor) else StepCursor.from_dict(cursor).to_dict()
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(raw) > MAX_CURSOR_BYTES:
        raise ContractError("CURSOR_TOO_LARGE")
    return raw


def parse_cursor_bytes(raw: bytes) -> StepCursor:
    if len(raw) > MAX_CURSOR_BYTES:
        raise ContractError("CURSOR_TOO_LARGE")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError("CURSOR_UTF8") from exc
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ContractError("CURSOR_ENCODING")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContractError("CURSOR_DUPLICATE_KEY")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs)
    except ContractError:
        raise
    except json.JSONDecodeError as exc:
        raise ContractError("CURSOR_JSON") from exc
    cursor = StepCursor.from_dict(value)
    if canonical_cursor_bytes(cursor) != raw:
        raise ContractError("CURSOR_NONCANONICAL")
    return cursor

# --- Compact material-finding set manifest ---------------------------------

FINDING_SET_FIELDS = {"schema_version", "task_id", "findings"}
FINDING_ENTRY_FIELDS = {"finding_id", "status", "finding_sha256"}
FINDING_STATUSES = {"OPEN", "RESOLVED"}
MAX_FINDING_SET_BYTES = 65536


def validate_finding_set_dict(value: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the compact finding identity set; finding bodies live elsewhere."""
    if not isinstance(value, Mapping) or set(value) != FINDING_SET_FIELDS:
        raise ContractError("FINDING_SET_FIELDS")
    if value["schema_version"] != "1":
        raise ContractError("FINDING_SET_SCHEMA", "$.schema_version")
    task_id = validate_task_id(value["task_id"])
    findings = value["findings"]
    if not isinstance(findings, list) or len(findings) > 256:
        raise ContractError("FINDINGS", "$.findings")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, finding in enumerate(findings):
        path = f"$.findings/{index}"
        if not isinstance(finding, Mapping) or set(finding) != FINDING_ENTRY_FIELDS:
            raise ContractError("FINDING_FIELDS", path)
        finding_id = _safe_id(finding["finding_id"], f"{path}/finding_id")
        if finding_id in seen:
            raise ContractError("DUPLICATE_FINDING", f"{path}/finding_id")
        seen.add(finding_id)
        status = finding["status"]
        if status not in FINDING_STATUSES:
            raise ContractError("FINDING_STATUS", f"{path}/status")
        digest = finding["finding_sha256"]
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise ContractError("SHA256", f"{path}/finding_sha256")
        normalized.append({"finding_id": finding_id, "status": status, "finding_sha256": digest})
    normalized.sort(key=lambda item: item["finding_id"])
    return {"schema_version": "1", "task_id": task_id, "findings": normalized}


def canonical_finding_set_bytes(value: Mapping[str, Any]) -> bytes:
    normalized = validate_finding_set_dict(value)
    raw = (json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(raw) > MAX_FINDING_SET_BYTES:
        raise ContractError("FINDING_SET_TOO_LARGE")
    return raw


def parse_finding_set_bytes(raw: bytes) -> dict[str, Any]:
    if len(raw) > MAX_FINDING_SET_BYTES:
        raise ContractError("FINDING_SET_TOO_LARGE")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError("FINDING_SET_UTF8") from exc
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ContractError("FINDING_SET_ENCODING")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContractError("FINDING_SET_DUPLICATE_KEY")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs)
    except ContractError:
        raise
    except json.JSONDecodeError as exc:
        raise ContractError("FINDING_SET_JSON") from exc
    normalized = validate_finding_set_dict(value)
    if canonical_finding_set_bytes(normalized) != raw:
        raise ContractError("FINDING_SET_NONCANONICAL")
    return normalized


# --- Candidate and remote verification manifests ---------------------------

GIT_OBJECT_ID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
CANDIDATE_MANIFEST_FIELDS = {
    "schema_version", "task_id", "base_commit", "candidate_commit", "candidate_tree",
    "sealed_plan_sha256", "completed_cursor_sha256",
}
REMOTE_VERIFICATION_MANIFEST_FIELDS = {
    "schema_version", "task_id", "remote_name", "remote_ref", "expected_commit",
    "expected_tree", "observed_commit", "observed_tree",
}


def _git_object(value: Any, path: str) -> str:
    if not isinstance(value, str) or not GIT_OBJECT_ID_RE.fullmatch(value):
        raise ContractError("GIT_OBJECT_ID", path)
    return value


def _safe_manifest_string(value: Any, path: str, maximum: int = 256) -> str:
    value = _short(value, path, maximum=maximum)
    if any(ord(char) < 0x20 for char in value) or "\\" in value or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ContractError("UNSAFE_STRING", path)
    return value


def validate_candidate_manifest_dict(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != CANDIDATE_MANIFEST_FIELDS:
        raise ContractError("CANDIDATE_MANIFEST_FIELDS")
    if value["schema_version"] != "1":
        raise ContractError("CANDIDATE_MANIFEST_SCHEMA", "$.schema_version")
    task_id = validate_task_id(value["task_id"])
    result = {
        "schema_version": "1", "task_id": task_id,
        "base_commit": _git_object(value["base_commit"], "$.base_commit"),
        "candidate_commit": _git_object(value["candidate_commit"], "$.candidate_commit"),
        "candidate_tree": _git_object(value["candidate_tree"], "$.candidate_tree"),
        "sealed_plan_sha256": _short(value["sealed_plan_sha256"], "$.sealed_plan_sha256", maximum=64),
        "completed_cursor_sha256": _short(value["completed_cursor_sha256"], "$.completed_cursor_sha256", maximum=64),
    }
    if not SHA256_RE.fullmatch(result["sealed_plan_sha256"]) or not SHA256_RE.fullmatch(result["completed_cursor_sha256"]):
        raise ContractError("SHA256", "$.sealed_plan_sha256")
    return result


def canonical_candidate_manifest_bytes(value: Mapping[str, Any]) -> bytes:
    normalized = validate_candidate_manifest_dict(value)
    if not SHA256_RE.fullmatch(normalized["sealed_plan_sha256"]) or not SHA256_RE.fullmatch(normalized["completed_cursor_sha256"]):
        raise ContractError("SHA256", "$.sealed_plan_sha256")
    return (json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def validate_remote_verification_manifest_dict(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != REMOTE_VERIFICATION_MANIFEST_FIELDS:
        raise ContractError("REMOTE_MANIFEST_FIELDS")
    if value["schema_version"] != "1":
        raise ContractError("REMOTE_MANIFEST_SCHEMA", "$.schema_version")
    task_id = validate_task_id(value["task_id"])
    remote_name = _safe_manifest_string(value["remote_name"], "$.remote_name", 64)
    remote_ref = _safe_manifest_string(value["remote_ref"], "$.remote_ref", 256)
    result = {
        "schema_version": "1", "task_id": task_id, "remote_name": remote_name,
        "remote_ref": remote_ref,
        "expected_commit": _git_object(value["expected_commit"], "$.expected_commit"),
        "expected_tree": _git_object(value["expected_tree"], "$.expected_tree"),
        "observed_commit": _git_object(value["observed_commit"], "$.observed_commit"),
        "observed_tree": _git_object(value["observed_tree"], "$.observed_tree"),
    }
    if result["expected_commit"] != result["observed_commit"] or result["expected_tree"] != result["observed_tree"]:
        raise ContractError("REMOTE_MISMATCH")
    return result


def canonical_remote_verification_manifest_bytes(value: Mapping[str, Any]) -> bytes:
    normalized = validate_remote_verification_manifest_dict(value)
    if normalized["expected_commit"] != normalized["observed_commit"] or normalized["expected_tree"] != normalized["observed_tree"]:
        raise ContractError("REMOTE_MISMATCH")
    return (json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _parse_manifest_bytes(raw: bytes, validator, canonicalizer, label: str) -> dict[str, Any]:
    if not isinstance(raw, bytes) or not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ContractError(f"{label}_ENCODING")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"{label}_JSON") from exc
    normalized = validator(value)
    if canonicalizer(normalized) != raw:
        raise ContractError(f"{label}_NONCANONICAL")
    return normalized


def parse_candidate_manifest_bytes(raw: bytes) -> dict[str, Any]:
    return _parse_manifest_bytes(raw, validate_candidate_manifest_dict, canonical_candidate_manifest_bytes, "CANDIDATE_MANIFEST")


def parse_remote_verification_manifest_bytes(raw: bytes) -> dict[str, Any]:
    return _parse_manifest_bytes(raw, validate_remote_verification_manifest_dict, canonical_remote_verification_manifest_bytes, "REMOTE_MANIFEST")
