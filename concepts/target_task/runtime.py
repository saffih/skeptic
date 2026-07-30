"""Narrow adapters for Target Task child-role execution.

Claude Code is the live MVP host through `CLAUDE.md` -> `AGENTS.md` ->
`workflows/target_task.md`. `dispatch_specialist` retains the injected executor
used by deterministic unit tests. Production child returns cross Boundary only
through `validate_host_role_receipt`, which validates compact references and
rejects body-bearing, oversized, mismatched, or synthetic production returns.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from capabilities.execution_envelope.execution_envelope import (
    ExecutionEnvelopeError,
    validate_role_return,
    validate_task_envelope,
)
from concepts.target_task.store import StoreError, write_immutable_artifact


class RuntimeAdapterError(ValueError):
    pass


@dataclass(frozen=True)
class SpecialistOutcome:
    """What a bounded specialist call actually produces. `body` is the raw
    substantive result text; everything else is already compact."""

    body: str
    status: str
    summary: str
    findings: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    next_authorized_action: str = "NONE"


SpecialistExecutor = Callable[[Mapping[str, Any]], SpecialistOutcome]


def dispatch_specialist(
    task_envelope: Mapping[str, Any],
    executor: SpecialistExecutor,
    *,
    role: str,
    workspace_root: Path,
    output_relative_path: str,
    output_reference_id: str,
    repository_root: Path | str = ".",
) -> dict[str, Any]:
    """Validate the dispatch, run the injected executor, capture its body
    directly to an immutable artifact, and return only the validated
    role_return. The raw body is never part of this function's return
    value, so a caller that only inspects the return value structurally
    cannot leak it further.

    `repository_root` is the real repository the task envelope's
    `input_artifact_references`/`contract_references` resolve against (a
    specialist typically needs to read real repo files: a sealed plan,
    source, a companion contract). `workspace_root` is the external,
    non-repo location the specialist's raw output is captured to and the
    produced reference is validated against — a specialist's own output is
    workspace bookkeeping, not repository content, until something later
    explicitly commits it."""
    try:
        validated_task = validate_task_envelope(task_envelope, repository_root=repository_root)
    except ExecutionEnvelopeError as exc:
        raise RuntimeAdapterError(f"invalid task envelope: {exc.code} at {exc.path}") from exc

    outcome = executor(validated_task)
    if not isinstance(outcome, SpecialistOutcome):
        raise RuntimeAdapterError("executor must return a SpecialistOutcome")

    try:
        produced_ref = write_immutable_artifact(
            Path(workspace_root),
            output_relative_path,
            outcome.body.encode("utf-8"),
            reference_id=output_reference_id,
            artifact_type="specialist_result",
            description=f"{role} result for {validated_task['task_id']}",
            read_condition="read when validating this dispatch's outcome",
        )
    except StoreError as exc:
        raise RuntimeAdapterError(f"could not capture specialist output: {exc.code} at {exc.path}") from exc

    role_return = {
        "role": role,
        "status": outcome.status,
        "summary": outcome.summary,
        "produced_artifact_references": [produced_ref],
        "findings": list(outcome.findings),
        "blockers": list(outcome.blockers),
        "next_authorized_action": outcome.next_authorized_action,
    }
    try:
        return validate_role_return(role_return, repository_root=workspace_root)
    except ExecutionEnvelopeError as exc:
        raise RuntimeAdapterError(f"invalid role return: {exc.code} at {exc.path}") from exc


# --- Production Claude Code host receipt ----------------------------------

import hashlib as _hashlib
import json as _json
import os as _os

HOST_RECEIPT_FIELDS = {
    "schema_version",
    "task_id",
    "operation_id",
    "attempt",
    "role",
    "status",
    "summary",
    "result_ref",
    "dispatch_evidence_ref",
    "synthetic",
}
HOST_ARTIFACT_REFERENCE_FIELDS = {
    "reference_id",
    "repository_relative_path",
    "sha256",
    "byte_size",
    "artifact_type",
    "description",
    "read_condition",
}
MAX_HOST_RECEIPT_BYTES = 4096
MAX_HOST_SUMMARY_BYTES = 512


def _validate_host_artifact_reference(reference, workspace_root: Path, path: str) -> None:
    if not isinstance(reference, Mapping) or set(reference) != HOST_ARTIFACT_REFERENCE_FIELDS:
        raise RuntimeAdapterError(f"invalid artifact reference fields at {path}")
    relative = reference["repository_relative_path"]
    if not isinstance(relative, str) or not relative or relative.startswith("/") or ".." in Path(relative).parts:
        raise RuntimeAdapterError(f"unsafe artifact path at {path}")
    root = Path(workspace_root).resolve()
    target = (root / relative).resolve()
    if _os.path.commonpath((str(root), str(target))) != str(root) or target.is_symlink() or not target.is_file():
        raise RuntimeAdapterError(f"unresolvable artifact at {path}")
    data = target.read_bytes()
    if _hashlib.sha256(data).hexdigest() != reference["sha256"] or len(data) != reference["byte_size"]:
        raise RuntimeAdapterError(f"artifact identity mismatch at {path}")


def validate_host_role_receipt(
    receipt: Mapping[str, Any],
    *,
    workspace_root: Path,
    allow_test_synthetic: bool = False,
) -> dict[str, Any]:
    """Validate one compact Claude Code child-role return.

    Production callers leave `allow_test_synthetic=False`. Synthetic receipts
    exist only for explicit deterministic test injection.
    """
    if not isinstance(receipt, Mapping) or set(receipt) != HOST_RECEIPT_FIELDS:
        raise RuntimeAdapterError("host receipt fields mismatch")
    raw = _json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_HOST_RECEIPT_BYTES:
        raise RuntimeAdapterError("host receipt too large")
    for field in ("schema_version", "task_id", "operation_id", "role", "status", "summary"):
        value = receipt[field]
        if not isinstance(value, str) or not value:
            raise RuntimeAdapterError(f"invalid {field}")
    if len(receipt["summary"].encode("utf-8")) > MAX_HOST_SUMMARY_BYTES:
        raise RuntimeAdapterError("summary too large")
    if not isinstance(receipt["attempt"], int) or isinstance(receipt["attempt"], bool) or receipt["attempt"] < 1:
        raise RuntimeAdapterError("invalid attempt")
    if not isinstance(receipt["synthetic"], bool):
        raise RuntimeAdapterError("synthetic must be boolean")
    if receipt["synthetic"] and not allow_test_synthetic:
        raise RuntimeAdapterError("synthetic receipt rejected in production")
    if not receipt["synthetic"] and receipt["dispatch_evidence_ref"] is None:
        raise RuntimeAdapterError("production receipt requires dispatch evidence")
    _validate_host_artifact_reference(receipt["result_ref"], workspace_root, "$.result_ref")
    evidence = receipt["dispatch_evidence_ref"]
    if evidence is not None:
        _validate_host_artifact_reference(evidence, workspace_root, "$.dispatch_evidence_ref")
    return dict(receipt)
