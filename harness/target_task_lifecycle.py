"""Deterministic Target Task lifecycle and trust-boundary reference mechanics.

This module deliberately does not claim a model runtime, fresh invocation, or
context isolation.  It validates the control state that a provider-neutral
Body is allowed to accept.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

OBSERVED_CONTEXT_STATUSES = {"FRESH_CONTEXT_CONFIRMED", "PARENT_CONTEXT_INHERITED", "CONTEXT_ISOLATION_UNKNOWN"}
ISOLATION_REQUIREMENTS = {"ISOLATION_OPTIONAL", "ISOLATION_REQUIRED"}
EXECUTION_MODES = {"ISOLATED_ORCHESTRATION", "SHARED_CONTEXT_DEGRADED", "ISOLATION_REQUIRED_BLOCKED"}
CLAIM_PROVENANCE = {"WORKER_REPORTED", "DIRECTLY_OBSERVED", "DETERMINISTICALLY_VALIDATED", "INDEPENDENTLY_REVIEWED", "INFERRED", "UNRESOLVED"}
ACCEPTABLE_PROVENANCE = {"DIRECTLY_OBSERVED", "DETERMINISTICALLY_VALIDATED"}
CHECKPOINT_VERSION = 1
BODY_ROTATION_FIELDS = ("TARGET_TASK_ID", "TASK_REFERENCE", "AUTHORITY_REFERENCE", "PLAN_REFERENCE", "PLAN_HASH", "CHECKPOINT_VERSION", "EXECUTION_MODE", "OBSERVED_CONTEXT_STATUS", "CURRENT_STEP", "COMPLETED_STEPS_AND_EVIDENCE", "ACCEPTED_VALIDATED_CLAIMS", "OPEN_FINDINGS", "OPEN_BLOCKERS", "MATERIAL_DEVIATIONS", "ARTIFACT_REFERENCES", "NEXT_AUTHORIZED_ACTION", "LAST_VALIDATION_STATE", "PRESSURE_STATUS", "ROTATION_STATE")

PLAN_FIELDS = ("TASK_ID", "OBJECTIVE", "DONE", "SCOPE", "PROHIBITIONS", "SOURCE_OF_TRUTH_ORDER", "ASSUMPTIONS", "UNKNOWNS", "STEPS", "VALIDATION", "HANDOFF", "STOP_CONDITIONS", "RETRIEVAL_CONDITIONS", "ESCALATION_CONDITIONS", "REVIEW_MODE", "SUCCESS_CRITERIA")
STEP_FIELDS = ("STEP_ID", "OBJECTIVE", "DIRECT_INPUTS", "REFERENCED_INPUTS", "DEPENDENCIES", "AUTHORITY", "PROHIBITIONS", "ACTIONS", "OUTPUTS", "VALIDATION", "HANDOFF_REQUIREMENTS", "RETRIEVAL_CONDITIONS", "ESCALATION_CONDITIONS", "STOP_CONDITIONS")
CHECKPOINT_FIELDS = ("TARGET_TASK_ID", "TASK_REFERENCE", "AUTHORITY_REFERENCE", "PLAN_REFERENCE", "PLAN_HASH", "CHECKPOINT_VERSION", "EXECUTION_MODE", "OBSERVED_CONTEXT_STATUS", "CURRENT_STEP", "COMPLETED_STEPS_AND_EVIDENCE", "ACCEPTED_VALIDATED_CLAIMS", "OPEN_FINDINGS", "OPEN_BLOCKERS", "MATERIAL_DEVIATIONS", "ARTIFACT_REFERENCES", "NEXT_AUTHORIZED_ACTION", "LAST_VALIDATION_STATE")
HANDOFF_FIELDS = ("STATUS", "WORK_PERFORMED", "VALIDATED_FACTS", "DECISION_RELEVANT_FINDINGS", "LIMITATIONS", "UNRESOLVED", "ARTIFACT_REFERENCES", "RETRIEVAL_GUIDANCE", "READ_CONDITIONS", "NEXT_AUTHORIZED_ACTION")
RECEIPT_FIELDS = ("TASK_RESULT", "PLAN_INTEGRITY", "DETERMINISTIC_VALIDATION", "REVIEW_RESULT", "EXECUTION_MODE", "OBSERVED_CONTEXT_STATUS", "BOUNDARY_PROCESSING_STATUS", "CHECKPOINT_AND_RESUME_STATUS", "CONTEXT_CONTAINMENT_EVIDENCE", "ACTUAL_RUNTIME_ISOLATION", "ACTUAL_CONTEXT_REDUCTION", "BLOCKERS", "DETERMINISTIC_LIFECYCLE_SIMULATION", "DETERMINISTIC_BOUNDARY_SIMULATION", "REAL_INTERRUPTION_RESUME_EXERCISE", "REAL_AGENT_BOUNDARY_EXERCISE", "RUNSKEPTIC_MODEL_PER_RUN", "RUNSKEPTIC_REASONING_LEVEL_PER_RUN", "RUNSKEPTIC_CONTEXT_STATUS_PER_RUN", "RUNSKEPTIC_INDEPENDENCE_PER_RUN", "RUNSKEPTIC_REPAIR_RUNS", "RUNSKEPTIC_QUALIFYING_PASSES", "RUNSKEPTIC_FINAL_CATEGORY")

class TargetTaskIntegrityError(ValueError):
    """A plan/checkpoint cannot authorize continuation."""

def stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def select_execution_mode(observed_context_status: str, isolation_requirement: str) -> str:
    if observed_context_status not in OBSERVED_CONTEXT_STATUSES or isolation_requirement not in ISOLATION_REQUIREMENTS:
        raise ValueError("invalid context or isolation status")
    if isolation_requirement == "ISOLATION_REQUIRED" and observed_context_status != "FRESH_CONTEXT_CONFIRMED":
        return "ISOLATION_REQUIRED_BLOCKED"
    return "ISOLATED_ORCHESTRATION" if observed_context_status == "FRESH_CONTEXT_CONFIRMED" else "SHARED_CONTEXT_DEGRADED"

def _canonical(value: Mapping[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    aliases = {field: field.lower() for field in fields}
    if "STEP_ID" in fields:
        aliases["STEP_ID"] = "id"
    out = {}
    for field in fields:
        if field in value:
            out[field] = value[field]
        elif aliases[field] in value:
            out[field] = value[aliases[field]]
    return out

def _nonempty(value: Any) -> bool:
    if isinstance(value, str): return bool(value.strip())
    if isinstance(value, (list, tuple, set)): return all(_nonempty(item) for item in value)
    return bool(value)

def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def _text_list(value: Any, *, allow_empty: bool = False) -> bool:
    return isinstance(value, list) and (allow_empty or bool(value)) and all(_text(item) for item in value)

def validate_plan(plan: Mapping[str, Any], task_id: str | None = None) -> dict[str, Any]:
    p = _canonical(plan, PLAN_FIELDS)
    missing = [f for f in PLAN_FIELDS if f not in p]
    if missing or not isinstance(p["STEPS"], list) or not p["STEPS"]:
        raise ValueError("plan rejected: missing fields " + ", ".join(missing))
    if not isinstance(p["TASK_ID"], str) or not p["TASK_ID"].strip() or p["TASK_ID"] != p["TASK_ID"].strip() or p["TASK_ID"] != (task_id or p["TASK_ID"]):
        raise ValueError("plan task identity mismatch")
    if p["REVIEW_MODE"] not in {"DETERMINISTIC_ONLY", "SELF_REVIEW", "RUNSKEPTIC_REVIEW"}:
        raise ValueError("plan rejected: invalid review mode")
    steps = []
    ids = set()
    top_lists = ("SCOPE", "PROHIBITIONS", "SOURCE_OF_TRUTH_ORDER", "ASSUMPTIONS", "UNKNOWNS", "VALIDATION", "HANDOFF", "STOP_CONDITIONS", "RETRIEVAL_CONDITIONS", "ESCALATION_CONDITIONS", "SUCCESS_CRITERIA")
    for field in top_lists:
        if not isinstance(p[field], list): raise ValueError("plan rejected: field must be a list " + field)
    for raw in p["STEPS"]:
        step = _canonical(raw, STEP_FIELDS)
        missing_step = [f for f in STEP_FIELDS if f not in step]
        if missing_step:
            raise ValueError("step rejected: missing fields " + ", ".join(missing_step))
        if not isinstance(step["STEP_ID"], str) or not step["STEP_ID"].strip() or step["STEP_ID"] != step["STEP_ID"].strip() or step["STEP_ID"] in ids:
            raise ValueError("step rejected: duplicate or invalid STEP_ID")
        for field in ("OBJECTIVE", "AUTHORITY", "ACTIONS", "OUTPUTS", "VALIDATION", "HANDOFF_REQUIREMENTS", "STOP_CONDITIONS"):
            if not _nonempty(step[field]) or (field == "AUTHORITY" and not isinstance(step[field], str)):
                raise ValueError("step rejected: empty bounded field " + field)
        for field in ("DIRECT_INPUTS", "REFERENCED_INPUTS", "DEPENDENCIES", "PROHIBITIONS", "ACTIONS", "OUTPUTS", "VALIDATION", "HANDOFF_REQUIREMENTS", "RETRIEVAL_CONDITIONS", "ESCALATION_CONDITIONS", "STOP_CONDITIONS"):
            if not isinstance(step[field], list): raise ValueError("step rejected: field must be a list " + field)
            if any(not _nonempty(item) for item in step[field]): raise ValueError("step rejected: blank member in " + field)
        ids.add(step["STEP_ID"]); steps.append(step)
    for step in steps:
        if any(dep not in ids for dep in step["DEPENDENCIES"]):
            raise ValueError("step rejected: missing dependency")
    # Kahn's algorithm rejects cycles and makes the first executable step explicit.
    remaining = {s["STEP_ID"]: set(s["DEPENDENCIES"]) for s in steps}
    order = []
    while remaining:
        ready = [s["STEP_ID"] for s in steps if s["STEP_ID"] in remaining and not remaining[s["STEP_ID"]]]
        if not ready:
            raise ValueError("plan rejected: dependency cycle")
        order.extend(ready)
        for key in ready: remaining.pop(key)
        for deps in remaining.values(): deps.difference_update(ready)
    if not p["VALIDATION"] or not p["SUCCESS_CRITERIA"] or not p["HANDOFF"]:
        raise ValueError("plan rejected: final validation, handoff, and success criteria are required")
    if not _text(p["OBJECTIVE"]) or not _text(p["DONE"]): raise ValueError("plan rejected: objective/done must be text")
    for field in ("SCOPE", "PROHIBITIONS", "SOURCE_OF_TRUTH_ORDER", "STOP_CONDITIONS"):
        if not _text_list(p[field]): raise ValueError("plan rejected: field must be non-empty text list " + field)
    for field in ("VALIDATION", "HANDOFF", "SUCCESS_CRITERIA"):
        if not isinstance(p[field], list) or not p[field]: raise ValueError("plan rejected: empty field " + field)
    for field in ("SCOPE", "PROHIBITIONS", "SOURCE_OF_TRUTH_ORDER", "ASSUMPTIONS", "UNKNOWNS", "VALIDATION", "STOP_CONDITIONS", "RETRIEVAL_CONDITIONS", "ESCALATION_CONDITIONS", "SUCCESS_CRITERIA"):
        if not _text_list(p[field], allow_empty=field in {"ASSUMPTIONS", "UNKNOWNS", "RETRIEVAL_CONDITIONS", "ESCALATION_CONDITIONS"}): raise ValueError("plan rejected: field must be a text list " + field)
    if not isinstance(p["HANDOFF"], list) or any(not isinstance(item, str) and not isinstance(item, Mapping) for item in p["HANDOFF"]): raise ValueError("plan rejected: invalid handoff")
    p["STEPS"] = steps
    retry_policy = plan.get("retry_policy", plan.get("RETRY_POLICY", {}))
    if not isinstance(retry_policy, Mapping) or any(step_id not in ids or not isinstance(limit, int) or limit < 1 for step_id, limit in retry_policy.items()): raise ValueError("plan rejected: invalid retry policy")
    p["RETRY_POLICY"] = dict(retry_policy)
    p["FIRST_EXECUTABLE_STEP"] = order[0]
    return p

def accept_and_seal_plan(plan: Mapping[str, Any], task_id: str) -> dict[str, Any]:
    frozen = json.loads(json.dumps(validate_plan(plan, task_id), sort_keys=True))
    return {"PLAN_REFERENCE": "sealed://" + task_id, "PLAN_HASH": stable_hash(frozen), "PLAN": frozen}

def _step_map(sealed_plan: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    plan = sealed_plan.get("PLAN", sealed_plan)
    return {s["STEP_ID"]: s for s in plan["STEPS"]}

def _accepted_evidence(evidence: Any) -> bool:
    return isinstance(evidence, Mapping) and evidence.get("status") == "ACCEPTED" and bool(evidence.get("artifact"))

def make_checkpoint(*, task_id: str, task_reference: str, authority_reference: str, plan_reference: str, plan_hash: str, execution_mode: str, observed_context_status: str, current_step: str, completed_steps_and_evidence: Mapping[str, Any], accepted_validated_claims: tuple[Mapping[str, Any], ...] = (), open_findings: tuple[str, ...] = (), open_blockers: tuple[str, ...] = (), material_deviations: tuple[str, ...] = (), artifact_references: tuple[Mapping[str, Any], ...] = (), next_authorized_action: str = "NONE", last_validation_state: str = "NOT_RUN") -> dict[str, Any]:
    if execution_mode not in EXECUTION_MODES or observed_context_status not in OBSERVED_CONTEXT_STATUSES:
        raise ValueError("invalid checkpoint mode")
    return {"TARGET_TASK_ID": task_id, "TASK_REFERENCE": task_reference, "AUTHORITY_REFERENCE": authority_reference, "PLAN_REFERENCE": plan_reference, "PLAN_HASH": plan_hash, "CHECKPOINT_VERSION": CHECKPOINT_VERSION, "EXECUTION_MODE": execution_mode, "OBSERVED_CONTEXT_STATUS": observed_context_status, "CURRENT_STEP": current_step, "COMPLETED_STEPS_AND_EVIDENCE": dict(completed_steps_and_evidence), "ACCEPTED_VALIDATED_CLAIMS": list(accepted_validated_claims), "OPEN_FINDINGS": list(open_findings), "OPEN_BLOCKERS": list(open_blockers), "MATERIAL_DEVIATIONS": list(material_deviations), "ARTIFACT_REFERENCES": list(artifact_references), "NEXT_AUTHORIZED_ACTION": next_authorized_action, "LAST_VALIDATION_STATE": last_validation_state}

def make_rotation_checkpoint(**values: Any) -> dict[str, Any]:
    values = dict(values); values.setdefault("CHECKPOINT_VERSION", CHECKPOINT_VERSION)
    values.setdefault("PRESSURE_STATUS", "BODY_ROTATION_REQUIRED"); values.setdefault("ROTATION_STATE", "STOPPED_BEFORE_RESUME")
    missing = [field for field in BODY_ROTATION_FIELDS if field not in values]
    if missing: raise TargetTaskIntegrityError("rotation checkpoint missing: " + ", ".join(missing))
    return values

def validate_rotation_checkpoint(checkpoint: Mapping[str, Any], *, task_id: str, plan_reference: str, plan_hash: str) -> None:
    missing = [field for field in BODY_ROTATION_FIELDS if field not in checkpoint]
    if missing: raise TargetTaskIntegrityError("rotation checkpoint missing: " + ", ".join(missing))
    if any((checkpoint[field] != expected) for field, expected in (("TARGET_TASK_ID", task_id), ("PLAN_REFERENCE", plan_reference), ("PLAN_HASH", plan_hash), ("CHECKPOINT_VERSION", CHECKPOINT_VERSION), ("PRESSURE_STATUS", "BODY_ROTATION_REQUIRED"), ("ROTATION_STATE", "STOPPED_BEFORE_RESUME"))):
        raise TargetTaskIntegrityError("rotation checkpoint identity or state mismatch")
    if checkpoint["NEXT_AUTHORIZED_ACTION"] != "RUN-" + checkpoint["CURRENT_STEP"]: raise TargetTaskIntegrityError("rotation next action mismatch")
    if checkpoint["OPEN_BLOCKERS"]: raise TargetTaskIntegrityError("rotation checkpoint has blockers")

def validate_checkpoint(checkpoint: Mapping[str, Any], sealed_plan: Mapping[str, Any] | None = None, evidence_ledger: Mapping[str, Any] | None = None) -> None:
    missing = [f for f in CHECKPOINT_FIELDS if f not in checkpoint]
    if missing: raise TargetTaskIntegrityError("checkpoint missing: " + ", ".join(missing))
    if checkpoint["CHECKPOINT_VERSION"] != CHECKPOINT_VERSION: raise TargetTaskIntegrityError("unsupported checkpoint version")
    if checkpoint["EXECUTION_MODE"] not in EXECUTION_MODES or checkpoint["OBSERVED_CONTEXT_STATUS"] not in OBSERVED_CONTEXT_STATUSES: raise TargetTaskIntegrityError("invalid checkpoint mode")
    completed = checkpoint["COMPLETED_STEPS_AND_EVIDENCE"]
    if not isinstance(completed, Mapping) or any(not _accepted_evidence(e) for e in completed.values()): raise TargetTaskIntegrityError("completed-step evidence is missing or invalid")
    if sealed_plan:
        plan = sealed_plan["PLAN"]
        if stable_hash(plan) != sealed_plan["PLAN_HASH"] or checkpoint["PLAN_HASH"] != sealed_plan["PLAN_HASH"]: raise TargetTaskIntegrityError("plan content hash mismatch")
        if checkpoint["TARGET_TASK_ID"] != plan["TASK_ID"] or checkpoint["PLAN_REFERENCE"] != sealed_plan["PLAN_REFERENCE"]: raise TargetTaskIntegrityError("checkpoint identity mismatch")
        if checkpoint["ACCEPTED_VALIDATED_CLAIMS"] and tuple(accept_claims(checkpoint["ACCEPTED_VALIDATED_CLAIMS"], evidence_ledger)) != tuple(checkpoint["ACCEPTED_VALIDATED_CLAIMS"]): raise TargetTaskIntegrityError("unvalidated claim in checkpoint ledger")
        steps = _step_map(sealed_plan)
        if checkpoint["CURRENT_STEP"] not in steps: raise TargetTaskIntegrityError("unknown current step")
        if any(step not in steps for step in completed): raise TargetTaskIntegrityError("completed step is not in plan")
        if checkpoint["CURRENT_STEP"] in completed: raise TargetTaskIntegrityError("current step already completed")
        for step_id in completed:
            if any(dep not in completed for dep in steps[step_id]["DEPENDENCIES"]): raise TargetTaskIntegrityError("completed dependency state is incoherent")
        expected = "RUN-" + checkpoint["CURRENT_STEP"]
        if checkpoint["NEXT_AUTHORIZED_ACTION"] != expected: raise TargetTaskIntegrityError("unauthorized next action")
    if checkpoint["OPEN_BLOCKERS"]: raise TargetTaskIntegrityError("resume blocked by open blockers")

def write_checkpoint(path: Path, checkpoint: Mapping[str, Any]) -> None:
    validate_checkpoint(checkpoint); path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle: json.dump(checkpoint, handle, sort_keys=True, indent=2); handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try: os.unlink(temporary)
        except FileNotFoundError: pass
        raise

def resume_checkpoint(path: Path, *, task_id: str, task_reference: str, authority_reference: str, plan_hash: str, plan_reference: str, sealed_plan: Mapping[str, Any], evidence_ledger: Mapping[str, Any] | None = None) -> dict[str, Any]:
    checkpoint = json.loads(path.read_text(encoding="utf-8"))
    validate_checkpoint(checkpoint, sealed_plan, evidence_ledger)
    expected = (("TARGET_TASK_ID", task_id), ("PLAN_HASH", plan_hash), ("PLAN_REFERENCE", plan_reference))
    expected += (("TASK_REFERENCE", task_reference), ("AUTHORITY_REFERENCE", authority_reference))
    mismatches = [field for field, value in expected if checkpoint[field] != value]
    if mismatches: raise TargetTaskIntegrityError("resume mismatch: " + ", ".join(mismatches))
    return checkpoint

def validate_handoff(handoff: Mapping[str, Any]) -> dict[str, Any]:
    missing = [f for f in HANDOFF_FIELDS if f not in handoff]
    if missing: raise ValueError("handoff missing: " + ", ".join(missing))
    if set(handoff) != set(HANDOFF_FIELDS) or not isinstance(handoff["STATUS"], str) or not handoff["STATUS"].strip() or not isinstance(handoff["NEXT_AUTHORIZED_ACTION"], str) or not handoff["NEXT_AUTHORIZED_ACTION"].strip(): raise ValueError("handoff has invalid fields")
    for field in ("WORK_PERFORMED", "RETRIEVAL_GUIDANCE", "READ_CONDITIONS"):
        if not isinstance(handoff[field], str) or not handoff[field].strip(): raise ValueError("handoff field must be text: " + field)
    for field in ("VALIDATED_FACTS", "DECISION_RELEVANT_FINDINGS", "LIMITATIONS", "UNRESOLVED", "ARTIFACT_REFERENCES"):
        if not isinstance(handoff[field], (list, tuple)): raise ValueError("handoff field must be a sequence: " + field)
    for claim in handoff.get("VALIDATED_FACTS", ()):
        if not isinstance(claim, Mapping) or claim.get("provenance") not in CLAIM_PROVENANCE: raise ValueError("validated fact lacks known provenance")
    return dict(handoff)

def accept_claims(claims: Any, evidence_ledger: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], ...]:
    accepted = []
    for claim in claims:
        if not isinstance(claim, Mapping) or claim.get("provenance") not in ACCEPTABLE_PROVENANCE: continue
        evidence = claim.get("evidence_reference")
        if not isinstance(evidence, Mapping) or not evidence.get("reference") or not evidence.get("validator") or evidence_ledger is None or evidence["reference"] not in evidence_ledger: continue
        entry = evidence_ledger[evidence["reference"]]
        if not isinstance(entry, Mapping) or entry.get("provenance") != claim["provenance"] or entry.get("result") != "PASS" or entry.get("validator") != evidence["validator"]: continue
        accepted.append(dict(claim))
    for claim in claims:
        if isinstance(claim, Mapping) and claim.get("provenance") == "INDEPENDENTLY_REVIEWED" and all(claim.get(k) for k in ("reviewer_identity", "evidence_reference", "acceptance_basis")) and evidence_ledger is not None and isinstance(claim["evidence_reference"], Mapping) and claim["evidence_reference"].get("reference") in evidence_ledger and evidence_ledger[claim["evidence_reference"]["reference"]].get("provenance") == "INDEPENDENTLY_REVIEWED" and evidence_ledger[claim["evidence_reference"]["reference"]].get("result") == "PASS" and evidence_ledger[claim["evidence_reference"]["reference"]].get("reviewer_identity") == claim["reviewer_identity"] and evidence_ledger[claim["evidence_reference"]["reference"]].get("acceptance_basis") == claim["acceptance_basis"]:
            accepted.append(dict(claim))
    return tuple(accepted)

def authorize_step(checkpoint: Mapping[str, Any], sealed_plan: Mapping[str, Any], requested_step: str, *, retry: Mapping[str, Any] | None = None, evidence_ledger: Mapping[str, Any] | None = None) -> str:
    validate_checkpoint(checkpoint, sealed_plan, evidence_ledger); steps = _step_map(sealed_plan)
    if requested_step not in steps: raise TargetTaskIntegrityError("unknown requested step")
    if requested_step in checkpoint["COMPLETED_STEPS_AND_EVIDENCE"]:
        prior = checkpoint["COMPLETED_STEPS_AND_EVIDENCE"][requested_step]
        policy_max = sealed_plan["PLAN"].get("RETRY_POLICY", {}).get(requested_step, prior.get("max_attempts", 1))
        history = set(prior.get("prior_artifacts", ())) | {prior.get("artifact")}
        if not retry or not all(isinstance(retry.get(k), str) and retry.get(k).strip() for k in ("RETRY_REASON", "PRIOR_RESULT_STATUS", "AUTHORITY", "EXPECTED_NEW_EVIDENCE")) or retry.get("AUTHORITY") != checkpoint["AUTHORITY_REFERENCE"] or retry.get("PRIOR_RESULT_STATUS") != prior.get("status") or retry.get("EXPECTED_NEW_EVIDENCE") in history or retry.get("MAX_ATTEMPTS") != policy_max or retry["MAX_ATTEMPTS"] <= prior.get("attempts", 1): raise TargetTaskIntegrityError("completed step repetition requires sealed retry authority and new evidence")
    elif requested_step != checkpoint["CURRENT_STEP"]: raise TargetTaskIntegrityError("requested step is not current")
    if any(dep not in checkpoint["COMPLETED_STEPS_AND_EVIDENCE"] for dep in steps[requested_step]["DEPENDENCIES"]): raise TargetTaskIntegrityError("step dependencies incomplete")
    return requested_step

def accept_step_result(checkpoint: Mapping[str, Any], sealed_plan: Mapping[str, Any], step_result: Mapping[str, Any]) -> dict[str, Any]:
    step = step_result.get("STEP_ID")
    authorize_step(checkpoint, sealed_plan, step, retry=step_result.get("RETRY"), evidence_ledger=step_result.get("EVIDENCE_LEDGER"))
    if not _accepted_evidence(step_result.get("EVIDENCE")): raise TargetTaskIntegrityError("step result lacks required evidence")
    retry = step_result.get("RETRY")
    if retry and retry.get("EXPECTED_NEW_EVIDENCE") != step_result["EVIDENCE"].get("artifact"): raise TargetTaskIntegrityError("retry evidence does not match authorization")
    if step_result.get("VALIDATION") != "PASS": raise TargetTaskIntegrityError("blocking validation failure")
    if retry:
        checkpoint["COMPLETED_STEPS_AND_EVIDENCE"][step]["attempts"] = checkpoint["COMPLETED_STEPS_AND_EVIDENCE"][step].get("attempts", 1) + 1
        record = checkpoint["COMPLETED_STEPS_AND_EVIDENCE"][step]
        record.setdefault("prior_artifacts", []).append(record["artifact"])
        record["artifact"] = step_result["EVIDENCE"]["artifact"]
    return dict(step_result)

def terminal_receipt(**values: Any) -> dict[str, Any]:
    receipt = {field: values.get(field, "UNKNOWN") for field in RECEIPT_FIELDS}
    if receipt["TASK_RESULT"] not in {"ACCEPTED", "REJECTED", "BLOCKED"}: raise ValueError("invalid task result")
    if receipt["ACTUAL_RUNTIME_ISOLATION"] not in {"CONFIRMED", "NOT_REQUIRED", "UNKNOWN"}: raise ValueError("invalid runtime isolation")
    if receipt["ACTUAL_CONTEXT_REDUCTION"] not in {"CONFIRMED", "NOT_CLAIMED", "UNKNOWN"}: raise ValueError("invalid context reduction")
    if receipt["TASK_RESULT"] == "ACCEPTED" and (receipt["PLAN_INTEGRITY"] != "PASS" or receipt["DETERMINISTIC_VALIDATION"] != "PASS" or receipt["BLOCKERS"] not in ((), [], "NONE") or receipt["EXECUTION_MODE"] not in {"ISOLATED_ORCHESTRATION", "SHARED_CONTEXT_DEGRADED"} or receipt["OBSERVED_CONTEXT_STATUS"] not in OBSERVED_CONTEXT_STATUSES or receipt["BOUNDARY_PROCESSING_STATUS"] != "PASS" or receipt["CHECKPOINT_AND_RESUME_STATUS"] != "PASS" or receipt["REVIEW_RESULT"] != "PASS" or receipt["DETERMINISTIC_LIFECYCLE_SIMULATION"] != "PASS" or receipt["DETERMINISTIC_BOUNDARY_SIMULATION"] != "PASS" or receipt["REAL_INTERRUPTION_RESUME_EXERCISE"] != "PASS" or receipt["REAL_AGENT_BOUNDARY_EXERCISE"] != "PASS" or receipt["RUNSKEPTIC_QUALIFYING_PASSES"] != 3 or receipt["RUNSKEPTIC_FINAL_CATEGORY"] != "PASS"): raise ValueError("accepted receipt has unresolved lifecycle or promotion controls")
    return receipt
