"""The universal Target Task lifecycle: legal phases and transitions only.

flow.py owns exactly one thing: which `LunaAction` is legal from which
`Phase`, and what phase results. It holds no task-specific instructions (no
mission text, no plan content, no step bodies) and is not a general workflow
engine — the transition table below is fixed and closed, not user-extensible.

The table is also where the sealed-plan invariant is mechanically enforced:
there is no transition out of PLAN_SEALED back to PLAN_DRAFTED or PLAN_REVIEW,
so a sealed plan cannot be replanned inside the same run merely by calling
this function differently.
"""

from __future__ import annotations

from dataclasses import dataclass

from concepts.target_task.contracts import LunaAction, Phase

# Normal forward/lateral transitions. STOP (-> BLOCKED) and BLOCKED's RECOVER
# (-> an explicit resume_phase) are handled outside this table because they
# are not phase-local: STOP is always legal except once CLOSED, and RECOVER
# requires deterministic proof of which phase is safe to resume, which this
# fixed table cannot express as a mapping. next_phase() still enforces the
# one bound expressible without that proof: a recovery may never target
# CLOSED (reachable only via INTEGRATED + ADVANCE) or BLOCKED itself.
# Proving a *specific* resume_phase is actually safe (matching the ledger's
# last valid phase before the STOP event) is Boundary's job, not flow.py's.
LEGAL_TRANSITIONS: dict[Phase, dict[LunaAction, Phase]] = {
    Phase.MISSION_PERSISTED: {LunaAction.CONTINUE: Phase.PLAN_DRAFTED},
    Phase.PLAN_DRAFTED: {LunaAction.CONTINUE: Phase.PLAN_REVIEW},
    Phase.PLAN_REVIEW: {
        LunaAction.CONTINUE: Phase.PLAN_REVIEW,  # another Fix Loop pass ran; streak not yet 3
        LunaAction.RETRY: Phase.PLAN_DRAFTED,  # material change: new Planner repair dispatch
        LunaAction.ADVANCE: Phase.PLAN_SEALED,  # three consecutive qualifying passes
    },
    Phase.PLAN_SEALED: {LunaAction.ADVANCE: Phase.STEP_EXECUTING},
    Phase.STEP_EXECUTING: {
        LunaAction.CONTINUE: Phase.STEP_EXECUTING,
        LunaAction.RETRY: Phase.STEP_EXECUTING,
        LunaAction.RECOVER: Phase.STEP_EXECUTING,
        LunaAction.ADVANCE: Phase.STEP_VALIDATED,
    },
    Phase.STEP_VALIDATED: {LunaAction.ADVANCE: Phase.CANDIDATE_FROZEN},
    Phase.CANDIDATE_FROZEN: {LunaAction.ADVANCE: Phase.FINAL_REVIEW},
    Phase.FINAL_REVIEW: {
        LunaAction.CONTINUE: Phase.FINAL_REVIEW,  # another Find Loop pass ran
        LunaAction.ADVANCE: Phase.INTEGRATED,  # Find Loop clean and integration possible
    },
    Phase.INTEGRATED: {LunaAction.ADVANCE: Phase.CLOSED},
    Phase.CLOSED: {},
}


class IllegalTransitionError(ValueError):
    def __init__(self, current: Phase, action: LunaAction) -> None:
        self.current, self.action = current, action
        super().__init__(f"{action.value} is not legal from {current.value}")


@dataclass(frozen=True)
class TransitionResult:
    phase: Phase
    allowed_actions: tuple[LunaAction, ...]


def allowed_actions(phase: Phase) -> tuple[LunaAction, ...]:
    """The set of legally requestable actions from a phase, for building a
    compact receipt's ALLOWED_ACTIONS-equivalent hint."""
    if phase is Phase.BLOCKED:
        return (LunaAction.RECOVER, LunaAction.STOP)
    table = LEGAL_TRANSITIONS.get(phase, {})
    actions = tuple(table.keys())
    if phase is not Phase.CLOSED:
        actions = actions + (LunaAction.STOP,)
    return actions


def next_phase(current: Phase, action: LunaAction, *, resume_phase: Phase | None = None) -> TransitionResult:
    """Advance one legal step. Boundary calls this to decide whether a
    Lead-requested transition may be admitted; it never decides substantive
    correctness itself."""
    if current is Phase.CLOSED:
        raise IllegalTransitionError(current, action)
    if action is LunaAction.STOP:
        next_ = Phase.BLOCKED
        return TransitionResult(next_, allowed_actions(next_))
    if current is Phase.BLOCKED:
        if action is not LunaAction.RECOVER:
            raise IllegalTransitionError(current, action)
        # CLOSED is reachable only via INTEGRATED + ADVANCE; admitting it
        # here would let RECOVER bypass every downstream gate (deterministic
        # validation, the frozen-candidate Find Loop, integration) in one
        # step. BLOCKED itself is excluded for the same reason a phase
        # cannot legally recover into itself without evidence of what
        # actually became safe again.
        if resume_phase is None or resume_phase not in LEGAL_TRANSITIONS or resume_phase in (Phase.CLOSED, Phase.BLOCKED):
            raise IllegalTransitionError(current, action)
        return TransitionResult(resume_phase, allowed_actions(resume_phase))
    table = LEGAL_TRANSITIONS.get(current, {})
    if action not in table:
        raise IllegalTransitionError(current, action)
    next_ = table[action]
    return TransitionResult(next_, allowed_actions(next_))
