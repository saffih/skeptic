"""The deterministic firewall between the durable Lead ("Luna") and
substantive Target Task work.

Boundary owns two things, kept in one module while a single owner is clear
(AGENTS.md's own convention: split only when evidence proves a separate
contract is necessary):

1. Transition legality — a thin call into `flow.next_phase`; Boundary
   decides whether a Lead-requested action is legal, never substantive
   correctness.
2. The no-body-leak guarantee — `capabilities.body_state.validate_state_bytes`
   already provides this mechanically: its exact-field-set and short-string
   checks make it structurally impossible for a body_state object to carry a
   mission, plan, patch, or log. `build_luna_receipt` is the one place a
   Luna-bound object is assembled and validated.

The Plan's RunSkeptic Fix Loop reuses `capabilities.runskeptic_receipt`
verbatim (already source-bound, already implements the three-consecutive-
qualifying-pass state machine). Its FIX_LOOP-typed loop-state functions are
not reusable as-is for the final read-only Find Loop, whose convergence rule
is different in kind, not just in name: a Find Loop can stabilize on a
*stable set of open findings* (skeptic.md: "Find Loop convergence means
detection stabilized; it does not mean the artifact passed"), where a Fix
Loop only qualifies on all-PASS. Re-using `advance_fix_loop`'s PASS-only
rule for the Find Loop would silently change its meaning. No modification to
`capabilities/runskeptic_receipt` is proposed or needed; a small local
counterpart is added here instead, matching that capability's own
plain-dict external-state convention.
"""

from __future__ import annotations

from typing import Any, Mapping

from capabilities.body_state.body_state import BodyStateError, validate_state_bytes, validate_state_structure_bytes
from capabilities.focused_retrieval.focused_retrieval import RetrievalError, retrieve
from capabilities.runskeptic_receipt.runskeptic_receipt import (
    ValidationResult,
    advance_fix_loop,
    fix_loop_complete,
    validate_loop_state,
    validate_receipt,
)
from concepts.target_task.contracts import LunaAction, Phase
from concepts.target_task.flow import TransitionResult, next_phase

__all__ = [
    "BoundaryError",
    "admit_transition",
    "build_luna_receipt",
    "retrieve_evidence",
    "validate_receipt",
    "validate_loop_state",
    "advance_fix_loop",
    "fix_loop_complete",
    "validate_find_loop_state",
    "advance_find_loop",
    "find_loop_complete",
]


class BoundaryError(ValueError):
    pass


def admit_transition(current_phase: Phase, action: LunaAction, *, resume_phase: Phase | None = None) -> TransitionResult:
    """The only function that may move a task's phase. Raises
    IllegalTransitionError, never silently substitutes a different phase."""
    return next_phase(current_phase, action, resume_phase=resume_phase)


def build_luna_receipt(state: Mapping[str, Any], *, repository_root, structural_only: bool = False) -> bytes:
    """Validate and canonically serialize the exact object Luna may hold.
    Raises BoundaryError (never returns a partially-valid receipt) if the
    candidate carries anything outside the fixed body_state field set, an
    oversized field, or an unverifiable artifact reference.

    `repository_root` is the real repository: every `ARTIFACT_REFERENCES`
    entry, including `SEALED_PLAN_REFERENCE`, must resolve as a file under
    it (`body_state.py`'s own requirement). Workspace-only bookkeeping
    (ledger, checkpoints, step results) is never placed in this object's
    `ARTIFACT_REFERENCES` — see `target_task_contract.md`, "Two roots"."""
    import json

    raw = (json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    try:
        if structural_only:
            validate_state_structure_bytes(raw, expected_task_id=state.get("TASK_ID"))
        else:
            validate_state_bytes(raw, repository_root=repository_root, expected_task_id=state.get("TASK_ID"))
    except BodyStateError as exc:
        raise BoundaryError(f"receipt rejected: {exc.code} at {exc.path}") from exc
    return raw


def retrieve_evidence(request: Mapping[str, Any], *, repository_root) -> dict[str, Any]:
    """Boundary's 'select only required evidence' behavior: a bounded,
    size-limited, single-range read of one artifact a current Luna receipt
    already references, verified against that receipt's own hash. Thin
    delegation to `capabilities.focused_retrieval`; Boundary adds no
    retrieval logic of its own."""
    try:
        return retrieve(dict(request), repository_root=repository_root)
    except RetrievalError as exc:
        raise BoundaryError(f"evidence retrieval rejected: {exc.code}") from exc


# --- Find Loop: same binding discipline as the Fix Loop, different
# qualifying rule (stable findings, not all-PASS). See module docstring.

FIND_LOOP_BINDING_FIELDS = (
    "TARGET_TASK_SHA256",
    "REVIEWED_ARTIFACT_SHA256",
    "SKEPTIC_SOURCE_BLOB_SHA",
    "APPLICABLE_COMPANION_SET_SHA256",
    "MATERIAL_FINDINGS_SHA256",
    "INVOCATION_KIND",
    "PERMISSION_MODE",
)


def validate_find_loop_state(state: Mapping[str, Any]) -> ValidationResult:
    errors: list[str] = []
    for name in FIND_LOOP_BINDING_FIELDS:
        if name not in state:
            errors.append(f"missing loop field: {name}")
    if errors:
        return ValidationResult(False, tuple(errors))
    if state["INVOCATION_KIND"] != "FIND_LOOP":
        errors.append("loop state must be FIND_LOOP")
    if state["PERMISSION_MODE"] != "read-only":
        errors.append("Find Loop must be read-only")
    passes = state.get("CONSECUTIVE_STABLE_PASSES")
    if not isinstance(passes, int) or isinstance(passes, bool) or passes < 0:
        errors.append("invalid consecutive-stable-pass count")
    required = state.get("PASSES_REQUIRED", 3)
    if required != 3:
        errors.append("default Find Loop convergence requires three passes")
    return ValidationResult(not errors, tuple(errors))


def advance_find_loop(state: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Next external Find Loop state. A modification is never legal here
    (read-only); callers must reject a receipt whose PERMISSION_MODE is not
    read-only before calling this."""
    result = validate_find_loop_state(state)
    if not result.ok:
        raise BoundaryError("invalid Find Loop state: " + "; ".join(result.errors))
    if receipt.get("PERMISSION_MODE") != "read-only":
        raise BoundaryError("Find Loop receipt must be read-only")
    stable = all(state[field] == receipt.get(field) for field in FIND_LOOP_BINDING_FIELDS)
    next_state = dict(state)
    next_state["CONSECUTIVE_STABLE_PASSES"] = state["CONSECUTIVE_STABLE_PASSES"] + 1 if stable else 0
    if not stable:
        for field in FIND_LOOP_BINDING_FIELDS:
            next_state[field] = receipt.get(field)
    return next_state


def find_loop_complete(state: Mapping[str, Any]) -> bool:
    result = validate_find_loop_state(state)
    return result.ok and state["CONSECUTIVE_STABLE_PASSES"] >= state.get("PASSES_REQUIRED", 3)
