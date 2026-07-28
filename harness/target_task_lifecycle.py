"""Deterministic reference mechanics for the Target Task architecture.

This is a small provider-neutral harness, not a model runtime.  It makes the
architecture's integrity, checkpoint, handoff, mode, and receipt rules
testable without claiming model isolation or token reduction.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

OBSERVED_CONTEXT_STATUSES = {
    "FRESH_CONTEXT_CONFIRMED",
    "PARENT_CONTEXT_INHERITED",
    "CONTEXT_ISOLATION_UNKNOWN",
}
ISOLATION_REQUIREMENTS = {"ISOLATION_OPTIONAL", "ISOLATION_REQUIRED"}
EXECUTION_MODES = {
    "ISOLATED_ORCHESTRATION",
    "SHARED_CONTEXT_DEGRADED",
    "ISOLATION_REQUIRED_BLOCKED",
}
CLAIM_PROVENANCE = {
    "WORKER_REPORTED",
    "DIRECTLY_OBSERVED",
    "DETERMINISTICALLY_VALIDATED",
    "INFERRED",
    "UNRESOLVED",
}
CHECKPOINT_VERSION = 1
CHECKPOINT_FIELDS = (
    "TARGET_TASK_ID", "TASK_REFERENCE", "AUTHORITY_REFERENCE",
    "PLAN_REFERENCE", "PLAN_HASH", "EXECUTION_MODE",
    "OBSERVED_CONTEXT_STATUS", "CURRENT_STEP", "COMPLETED_STEPS_AND_EVIDENCE",
    "ACCEPTED_VALIDATED_CLAIMS", "OPEN_FINDINGS", "OPEN_BLOCKERS",
    "MATERIAL_DEVIATIONS", "ARTIFACT_REFERENCES", "NEXT_AUTHORIZED_ACTION",
    "LAST_VALIDATION_STATE", "CHECKPOINT_VERSION",
)
HANDOFF_FIELDS = (
    "STATUS", "WORK_PERFORMED", "VALIDATED_FACTS",
    "DECISION_RELEVANT_FINDINGS", "LIMITATIONS", "UNRESOLVED",
    "ARTIFACT_REFERENCES", "RETRIEVAL_GUIDANCE", "READ_CONDITIONS",
    "NEXT_AUTHORIZED_ACTION",
)
RECEIPT_FIELDS = (
    "TASK_RESULT", "PLAN_INTEGRITY", "DETERMINISTIC_VALIDATION",
    "REVIEW_RESULT", "EXECUTION_MODE", "OBSERVED_CONTEXT_STATUS",
    "BOUNDARY_PROCESSING_STATUS", "CHECKPOINT_AND_RESUME_STATUS",
    "CONTEXT_CONTAINMENT_EVIDENCE", "ACTUAL_RUNTIME_ISOLATION",
    "ACTUAL_CONTEXT_REDUCTION", "BLOCKERS",
)


class TargetTaskIntegrityError(ValueError):
    """A checkpoint or sealed plan cannot be trusted for continuation."""


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def select_execution_mode(observed_context_status: str,
                          isolation_requirement: str) -> str:
    if observed_context_status not in OBSERVED_CONTEXT_STATUSES:
        raise ValueError("invalid observed context status")
    if isolation_requirement not in ISOLATION_REQUIREMENTS:
        raise ValueError("invalid isolation requirement")
    if isolation_requirement == "ISOLATION_REQUIRED":
        if observed_context_status != "FRESH_CONTEXT_CONFIRMED":
            return "ISOLATION_REQUIRED_BLOCKED"
        return "ISOLATED_ORCHESTRATION"
    if observed_context_status == "FRESH_CONTEXT_CONFIRMED":
        return "ISOLATED_ORCHESTRATION"
    return "SHARED_CONTEXT_DEGRADED"


def accept_and_seal_plan(plan: Mapping[str, Any], task_id: str) -> dict[str, Any]:
    """Validate minimum acceptance-plan structure and return immutable identity."""
    required = {
        "task_id", "objective", "done", "scope", "prohibitions",
        "source_of_truth_order", "steps", "validation", "handoff",
        "stop_conditions", "review_mode", "success_criteria",
    }
    missing = sorted(required - set(plan))
    if missing or plan.get("task_id") != task_id or not plan.get("steps"):
        raise ValueError(f"plan rejected: missing or mismatched fields: {missing}")
    if plan["review_mode"] not in {"DETERMINISTIC_ONLY", "SELF_REVIEW",
                                    "RUNSKEPTIC_REVIEW"}:
        raise ValueError("plan rejected: invalid review mode")
    frozen = json.loads(json.dumps(plan, sort_keys=True))
    return {"PLAN_REFERENCE": "sealed://" + task_id,
            "PLAN_HASH": stable_hash(frozen), "PLAN": frozen}


def make_checkpoint(*, task_id: str, task_reference: str,
                    authority_reference: str, plan_reference: str,
                    plan_hash: str, execution_mode: str,
                    observed_context_status: str, current_step: str,
                    completed_steps_and_evidence: Mapping[str, Any],
                    accepted_validated_claims: tuple[Mapping[str, Any], ...] = (),
                    open_findings: tuple[str, ...] = (),
                    open_blockers: tuple[str, ...] = (),
                    material_deviations: tuple[str, ...] = (),
                    artifact_references: tuple[Mapping[str, Any], ...] = (),
                    next_authorized_action: str = "NONE",
                    last_validation_state: str = "NOT_RUN") -> dict[str, Any]:
    if execution_mode not in EXECUTION_MODES:
        raise ValueError("invalid execution mode")
    if observed_context_status not in OBSERVED_CONTEXT_STATUSES:
        raise ValueError("invalid observed context status")
    return {
        "TARGET_TASK_ID": task_id, "TASK_REFERENCE": task_reference,
        "AUTHORITY_REFERENCE": authority_reference,
        "PLAN_REFERENCE": plan_reference, "PLAN_HASH": plan_hash,
        "EXECUTION_MODE": execution_mode,
        "OBSERVED_CONTEXT_STATUS": observed_context_status,
        "CURRENT_STEP": current_step,
        "COMPLETED_STEPS_AND_EVIDENCE": dict(completed_steps_and_evidence),
        "ACCEPTED_VALIDATED_CLAIMS": list(accepted_validated_claims),
        "OPEN_FINDINGS": list(open_findings), "OPEN_BLOCKERS": list(open_blockers),
        "MATERIAL_DEVIATIONS": list(material_deviations),
        "ARTIFACT_REFERENCES": list(artifact_references),
        "NEXT_AUTHORIZED_ACTION": next_authorized_action,
        "LAST_VALIDATION_STATE": last_validation_state,
        "CHECKPOINT_VERSION": CHECKPOINT_VERSION,
    }


def write_checkpoint(path: Path, checkpoint: Mapping[str, Any]) -> None:
    validate_checkpoint(checkpoint)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(checkpoint, handle, sort_keys=True, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def validate_checkpoint(checkpoint: Mapping[str, Any]) -> None:
    missing = [field for field in CHECKPOINT_FIELDS if field not in checkpoint]
    if missing:
        raise TargetTaskIntegrityError("checkpoint missing: " + ", ".join(missing))
    if checkpoint["CHECKPOINT_VERSION"] != CHECKPOINT_VERSION:
        raise TargetTaskIntegrityError("unsupported checkpoint version")
    if checkpoint["EXECUTION_MODE"] not in EXECUTION_MODES:
        raise TargetTaskIntegrityError("invalid checkpoint execution mode")
    if checkpoint["OBSERVED_CONTEXT_STATUS"] not in OBSERVED_CONTEXT_STATUSES:
        raise TargetTaskIntegrityError("invalid checkpoint context status")


def resume_checkpoint(path: Path, *, task_id: str, plan_hash: str,
                      plan_reference: str) -> dict[str, Any]:
    checkpoint = json.loads(path.read_text(encoding="utf-8"))
    validate_checkpoint(checkpoint)
    checks = (("TARGET_TASK_ID", task_id), ("PLAN_HASH", plan_hash),
              ("PLAN_REFERENCE", plan_reference))
    mismatches = [field for field, expected in checks
                  if checkpoint[field] != expected]
    if mismatches:
        raise TargetTaskIntegrityError("resume mismatch: " + ", ".join(mismatches))
    if checkpoint["OPEN_BLOCKERS"]:
        raise TargetTaskIntegrityError("resume blocked by open blockers")
    return checkpoint


def validate_handoff(handoff: Mapping[str, Any]) -> dict[str, Any]:
    missing = [field for field in HANDOFF_FIELDS if field not in handoff]
    if missing:
        raise ValueError("handoff missing: " + ", ".join(missing))
    claims = handoff.get("VALIDATED_FACTS", ())
    for claim in claims:
        if not isinstance(claim, Mapping) or claim.get("provenance") not in CLAIM_PROVENANCE:
            raise ValueError("validated fact lacks claim provenance")
    return dict(handoff)


def terminal_receipt(**values: Any) -> dict[str, Any]:
    receipt = {field: values.get(field, "UNKNOWN") for field in RECEIPT_FIELDS}
    if receipt["TASK_RESULT"] not in {"ACCEPTED", "REJECTED", "BLOCKED"}:
        raise ValueError("invalid task result")
    if receipt["ACTUAL_RUNTIME_ISOLATION"] not in {"CONFIRMED", "NOT_REQUIRED", "UNKNOWN"}:
        raise ValueError("invalid runtime-isolation claim")
    if receipt["ACTUAL_CONTEXT_REDUCTION"] not in {"CONFIRMED", "NOT_CLAIMED", "UNKNOWN"}:
        raise ValueError("invalid context-reduction claim")
    return receipt
