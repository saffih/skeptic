"""Provider-neutral host adapter contract for Target Task.

The Boundary consumes only canonical role names, durable references, and the
normalized receipt.  Provider event formats stay behind an adapter.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from concepts.target_task.runtime import (
    HOST_RECEIPT_FIELDS,
    RuntimeAdapterError,
    validate_host_role_receipt,
)
from concepts.target_task.store import write_content_addressed_artifact


CANONICAL_ROLES = frozenset({"planner", "reviewer", "worker", "command"})
INVOCATION_EVIDENCE_FIELDS = frozenset({
    "schema_version", "provider_id", "invocation_id", "task_id", "operation_id",
    "canonical_role", "provider_role", "attempt", "request_ref",
    "raw_provider_evidence_ref", "normalized_receipt_ref", "completion_status",
    "timeout", "exit_status", "cost_metadata",
})
EVIDENCE_STATUSES = frozenset({"COMPLETE", "FAILED", "UNKNOWN"})


class HostAdapterError(ValueError):
    pass


@dataclass(frozen=True)
class ProviderCapabilities:
    provider_id: str
    available: bool
    roles: tuple[str, ...]
    supports_execution: bool
    evidence_mode: str


@dataclass(frozen=True)
class DispatchRequest:
    task_id: str
    operation_id: str
    attempt: int
    canonical_role: str
    provider_role: str
    request_ref: Mapping[str, Any]


@dataclass(frozen=True)
class InvocationReport:
    provider_id: str
    invocation_id: str
    completion_status: str
    timeout: bool
    exit_status: int | None
    cost_metadata: Mapping[str, Any] | str


def _id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 256:
        raise HostAdapterError(f"invalid {label}")
    return value


def canonical_invocation_evidence(value: Mapping[str, Any]) -> bytes:
    if not isinstance(value, Mapping) or set(value) != INVOCATION_EVIDENCE_FIELDS:
        raise HostAdapterError("invocation evidence fields")
    if value["schema_version"] != "1":
        raise HostAdapterError("invocation evidence schema")
    for field in ("provider_id", "invocation_id", "task_id", "operation_id", "canonical_role", "provider_role"):
        _id(value[field], field)
    if value["canonical_role"] not in CANONICAL_ROLES:
        raise HostAdapterError("unknown canonical role")
    if not isinstance(value["attempt"], int) or isinstance(value["attempt"], bool) or value["attempt"] < 1:
        raise HostAdapterError("invalid attempt")
    if value["completion_status"] not in EVIDENCE_STATUSES:
        raise HostAdapterError("invalid completion status")
    if not isinstance(value["timeout"], bool):
        raise HostAdapterError("timeout must be boolean")
    if value["exit_status"] is not None and (not isinstance(value["exit_status"], int) or isinstance(value["exit_status"], bool)):
        raise HostAdapterError("invalid exit status")
    if not isinstance(value["request_ref"], Mapping):
        raise HostAdapterError("request reference required")
    for field in ("raw_provider_evidence_ref", "normalized_receipt_ref"):
        if not isinstance(value[field], Mapping):
            raise HostAdapterError(f"{field} required")
    if not (value["timeout"] or value["completion_status"] == "UNKNOWN") and value["exit_status"] is None:
        raise HostAdapterError("non-unknown invocation requires exit status")
    try:
        raw = (json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    except (TypeError, ValueError) as exc:
        raise HostAdapterError("invocation evidence JSON") from exc
    if len(raw) > 8192:
        raise HostAdapterError("invocation evidence too large")
    return raw


def persist_raw_provider_evidence(task_root: Path, provider_id: str, raw: bytes) -> dict[str, Any]:
    """Persist immutable provider bytes under a content-derived name."""
    if not isinstance(raw, bytes) or not raw:
        raise HostAdapterError("raw provider evidence must be nonempty bytes")
    _id(provider_id, "provider_id")
    return write_content_addressed_artifact(
        Path(task_root), f"evidence/providers/{provider_id}", ".bin", raw,
        reference_id=f"provider-evidence-{hashlib.sha256(raw).hexdigest()[:16]}",
        artifact_type="raw_provider_evidence",
        description=f"immutable raw evidence from {provider_id}",
        read_condition="read only by the matching provider adapter",
    )


def validate_invocation_evidence(value: Mapping[str, Any], *, expected: Mapping[str, Any] | None = None) -> dict[str, Any]:
    canonical_invocation_evidence(value)
    if expected:
        for key, wanted in expected.items():
            if value.get(key) != wanted:
                raise HostAdapterError(f"invocation evidence {key} mismatch")
    return dict(value)


class TargetTaskHostAdapter(ABC):
    """Minimal replaceable provider boundary; no provider schema is canonical."""

    provider_id: str

    @abstractmethod
    def discover_capabilities(self) -> ProviderCapabilities: ...

    @abstractmethod
    def provider_role(self, canonical_role: str) -> str: ...

    def build_dispatch_request(self, request: Mapping[str, Any]) -> DispatchRequest:
        role = request.get("role")
        if role not in CANONICAL_ROLES:
            raise HostAdapterError("request uses a non-canonical role")
        return DispatchRequest(
            task_id=_id(request.get("task_id"), "task_id"),
            operation_id=_id(request.get("operation_id"), "operation_id"),
            attempt=request.get("attempt"),
            canonical_role=role,
            provider_role=self.provider_role(role),
            request_ref=request,
        )

    @abstractmethod
    def validate_provider_evidence(self, raw: bytes) -> InvocationReport: ...

    def ingest_invocation_evidence(self, raw: bytes, *, task_root: Path) -> tuple[dict[str, Any], InvocationReport]:
        """Persist raw bytes first, then admit only this provider's evidence."""
        reference = persist_raw_provider_evidence(task_root, self.provider_id, raw)
        return reference, self.validate_provider_evidence(raw)

    def normalize_receipt(
        self, receipt: Mapping[str, Any], *, workspace_root: Path, source_root: Path,
        expected: Mapping[str, Any], expected_request_ref: Mapping[str, Any],
    ) -> dict[str, Any]:
        if set(receipt) != HOST_RECEIPT_FIELDS:
            raise HostAdapterError("provider return is not a compact canonical receipt")
        try:
            return validate_host_role_receipt(
                receipt, workspace_root=workspace_root, source_root=source_root,
                expected_task_id=expected["task_id"], expected_operation_id=expected["operation_id"],
                expected_attempt=expected["attempt"], expected_role=expected["role"],
                expected_step_id=expected["step_id"], expected_request_ref=expected_request_ref,
            )
        except RuntimeAdapterError as exc:
            raise HostAdapterError(str(exc)) from exc

    def report_outcome(self, report: InvocationReport) -> str:
        if report.timeout:
            return "UNKNOWN"
        return report.completion_status


__all__ = [
    "CANONICAL_ROLES", "DispatchRequest", "EVIDENCE_STATUSES", "HostAdapterError",
    "INVOCATION_EVIDENCE_FIELDS", "InvocationReport", "ProviderCapabilities",
    "TargetTaskHostAdapter", "canonical_invocation_evidence", "persist_raw_provider_evidence",
    "validate_invocation_evidence",
]
