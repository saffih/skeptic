"""Narrow adapter between a Target Task step and a bounded specialist.

No live agent runtime is wired into this repository (see AGENTS.md — this
repository is a portable prompt/review library, not a running orchestrator).
This module is therefore reference-only: it defines the shape a real runtime
adapter must have and proves the one property that actually matters —
a specialist's raw output is captured directly into an immutable artifact
and never returned to the caller. Only a validated, bounded `role_return`
(from `capabilities.execution_envelope`) referencing that artifact crosses
back. An injected `executor` callable stands in for the real dispatch.
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
