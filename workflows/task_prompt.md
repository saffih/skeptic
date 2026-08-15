# Task Prompt (TP)

This is the complete and only authority for `TP: <mission>`. TP is a simple,
host-neutral Brain/Execution ping-pong. The controller is mechanical and
domain-blind; it never performs semantic work or chooses semantic
continuation.

## Roles and first action

There are exactly two semantic roles: `BRAIN` and `EXECUTION`. The controller
persists the verbatim mission, creates host-owned run storage containing
`mission.md`, `events.jsonl`, and `artifacts/`, and launches one fresh native
Brain before any task-specific discovery, reading, testing, or planning.

The initial Brain uses the normal authorized starting route. Brain selects the
route for each bounded Execution under `agents/model_routing_policy.md` and
may request a stronger fresh Brain when its own capability is insufficient.
The controller applies Brain-authored routing mechanically; it never chooses
semantic escalation. Actual provider, model, authentication, session,
networking, and process details are supplied by the host and remain `UNKNOWN`
unless directly observable.

## Native transport and references

TP specifies only:

    launch fresh native semantic invocation(role, route, references)

The controller passes receiver-resolvable references, not mission, authority,
repository, or result bodies. TP does not own `codex exec`, `CODEX_HOME`,
`auth.json`, MCP initialization, WebSockets, `--add-dir`, provider supervision,
or provider networking. If the host cannot provide a fresh invocation, it
reports host execution unavailability; TP does not redesign itself or fabricate
a semantic terminal decision.

References identify authorized, resolvable artifacts. Equivalent relative and
absolute spellings are equivalent after resolution; unresolved, unauthorized,
escaping, or stale references are rejected mechanically.

## Brain result

Brain writes substantive understanding, evidence, and the next assignment to a
durable artifact, then returns compact control:

    TP_RESULT
    role: BRAIN
    status: CONTINUE | COMPLETE | BLOCKED | CONFLICT
    route: LOW | MEDIUM | STRONG | NONE
    next: EXECUTION | BRAIN | NONE
    execution_ref: <one durable assignment reference> | NONE
    result_ref: <durable result reference> | NONE
    reason: <compact control reason>

`CONTINUE + EXECUTION` names exactly one bounded assignment and a route;
`result_ref` is `NONE`. `CONTINUE + BRAIN` names one fresh Brain escalation at
`STRONG` with a resolvable handoff; `execution_ref` is `NONE`. Terminal Brain
results use `route: NONE`, `next: NONE`, and `execution_ref: NONE`.

There is no Planner role or Validator role. Planning and validation belong to
Brain, and the controller has no semantic plan or queue.

Before Brain returns `BLOCKED` or `CONFLICT`, it identifies the exact stopping
proposition, records primary supporting evidence, checks returned evidence for
contradiction, and performs the smallest bounded owner/falsification check
that could disprove an absence claim. “I did not find it” is not “it does not
exist.” If safe evidence gathering remains, Brain returns `CONTINUE` with that
work. Only a genuine evidenced blocker or irreconcilable conflict terminalizes.

If the mission requires commit, push, or remote verification, local
implementation/test success is not completion; Brain must obtain the required
publication evidence before `COMPLETE`.

## Execution result

The controller dispatches exactly one Brain-authored assignment:

    TP_RESULT
    role: EXECUTION
    status: DONE | NOT_DONE | UNKNOWN
    execution_ref: <assigned reference>
    result_ref: <durable evidence/result reference> | NONE
    reason: <compact observed outcome>

`DONE` means the bounded assignment was satisfied. `NOT_DONE` means its local
acceptance condition was not satisfied and evidence explains why. `UNKNOWN`
means the outcome or effect cannot safely be established. Execution never
decides mission-level `COMPLETE`, `BLOCKED`, or `CONFLICT`; after every return
Brain decides what happens next. Research and RunSkeptic are ordinary bounded
Executions whose evidence Brain interprets.

Malformed, missing, or mechanically unverifiable Execution returns become
uncertain evidence and go to a fresh Brain. They do not become semantic
blockers and are not silently treated as success.

## Durable interruption and resume

A dispatch admission is recorded before launch. A returned outcome is recorded
when observed. The record contains only mechanical identity, route, references,
admission state, and returned control; substantive content remains in artifacts.

On resume, a terminal Brain result remains terminal. A Brain-selected Execution
that was never admitted may be admitted once. A returned Execution goes to a
fresh Brain. An admitted Execution without a trustworthy return is not replayed:
fresh Brain receives `UNKNOWN`/uncertain evidence and decides. The controller
never reconstructs semantic state, guesses idempotence, or blindly replays
uncertain side effects.
An uncertain Execution is never replayed automatically.

## Controller boundary and lifecycle

The controller may persist exact input, create run storage, mechanically
validate identity/reference shape, record dispatch/return events, launch fresh
native invocations, and report. It may not read substantive artifacts to choose
continuation, discover task requirements, judge acceptance, infer absence,
choose a route, or declare a terminal status.

The lifecycle is:

    fresh Brain -> one Execution -> fresh Brain -> ... -> terminal Brain

After `NOT_DONE`, Brain may replan. After `UNKNOWN`, Brain may gather evidence,
choose a safe new Execution, or terminalize if evidence supports it. Brain may
escalate itself to a stronger fresh Brain. Context capacity is handled by
bounded decomposition or research, not automatically treated as model
incapability. A worker/local route failure is observable inability returned to
Brain. A Brain launch failure is host unavailability, not semantic `BLOCKED`.

Semantic material crossing every fresh boundary is durable and passed by
reference. Run artifacts use host scratch/run storage and do not contaminate
tracked product state. No second runtime product, adapter, compatibility mode,
legacy parser, protocol version, or provider workaround is part of TP.

TP remains separate from STT and does not define or modify STT authority.
