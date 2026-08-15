# Task Prompt (TP)

This is the complete and only authority for `TP: <mission>`. TP is a simple,
host-neutral Brain/Execution ping-pong. The controller is mechanical and
domain-blind; it never performs semantic work or chooses semantic
continuation.

## Roles and first action

There are exactly two semantic roles: `BRAIN` and `EXECUTION`. The controller
creates host-owned run storage containing `mission.md`, `tp-authority.md`,
`events.jsonl`, and `artifacts/`, persists the verbatim mission, binds and
snapshots the exact TP authority for the run as described below, and only then
launches one fresh native Brain. These mechanical startup actions occur before
any task-specific discovery, reading, testing, or planning.

The initial Brain uses the normal authorized starting route. Brain selects the
route for each bounded Execution under `agents/model_routing_policy.md` and
may request a stronger fresh Brain when its own capability is insufficient.
The controller applies Brain-authored routing mechanically; it never chooses
semantic escalation. Actual provider, model, authentication, session,
networking, and process details are supplied by the host and remain `UNKNOWN`
unless directly observable.

## Authority binding before semantic work

The host selects the exact TP authority bytes before launching the first Brain
and snapshots those bytes as `tp-authority.md` in the run root. It records the
source identity when observable and the SHA-256 of the exact snapshot bytes in
`events.jsonl`; every fresh Brain and Execution receives a resolvable
`tp_authority_ref` to that same snapshot. Fresh semantic invocations use the
snapshot and do not substitute a mutable repository copy.

When the caller, transport, or repository policy supplies an immutable authority
identity, such as a repository commit plus the expected `workflows/task_prompt.md`
blob or content hash, the host validates that identity mechanically before
creating any semantic dispatch. A mismatch, unavailable identity, or inability
to materialize the exact authority bytes stops before Brain launch and is
reported as host authority unavailability; it is never converted into semantic
`BLOCKED` or `CONFLICT`.

Authority needed to start TP is host input, not meaning that may be discovered
from inside the mission after Brain launch. A mission may further constrain the
target repository, but it cannot retroactively choose the TP authority that
already governed its first Brain. A clean checkout is not proof that the
checkout is the intended or current authority. An already-obsolete TP file
cannot prove its own freshness; when freshness matters, the expected immutable
authority identity must arrive from outside the semantic mission.

Resume uses the same snapshotted authority bytes and recorded hash. If that
snapshot is missing, altered, or no longer resolvable, the host fails closed
before another semantic invocation rather than rereading a mutable checkout.

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

## Native invocation ownership and safety

Every native Brain or Execution invocation launched for TP is host-owned by one
run and has a recorded invocation identity plus a finite host-enforced lease or
wall-clock deadline. The ownership record remains mechanically discoverable
across controller restart until that invocation is observed exited or reaped. A
run never has more than one live TP semantic invocation. The host never relies
on the semantic worker to enforce its own deadline. If the host cannot retain
mechanically discoverable ownership or enforce a finite deadline, it does not
launch the TP semantic invocation and reports host safety unavailability.

Before launching a TP invocation, the host reconciles TP-owned invocations it
can identify. A still-live invocation belonging to the same active run prevents
a duplicate launch. A TP-owned invocation whose controller is gone, whose run
is terminal or abandoned, or whose deadline has expired is terminated and
reaped before the host starts replacement work. An active invocation belonging
to another live run may continue. The host never terminates a process whose TP
ownership it cannot establish.

When an Execution reaches its deadline or its return cannot be established, the
host terminates and reaps that invocation and returns `UNKNOWN` evidence to a
fresh Brain. When a Brain invocation reaches its deadline, the host terminates
and reaps it and reports Brain/host execution unavailability without fabricating
a semantic status. On observed TP cancellation, terminalization, controller failure, or orderly
host shutdown, the host terminates and reaps every still-live semantic child it
owns for that run and verifies that none remains. Abrupt controller loss is
bounded by the independent lease/deadline and by owned-child reconciliation on
the next host start. Processes separately launched by an Execution are governed
by the mission and are not killed merely because TP observes them.

## Host observability

`events.jsonl` is the primary durable mechanical lifecycle evidence. For every
native Brain or Execution invocation, it records the role and invocation ID;
requested route and host-supplied requested model/reasoning effort; actual
runtime/model/effort only when directly observable (otherwise `UNKNOWN`);
admission, start, finish, and return timing; finite deadline/lease; owned
semantic-child and, when present, watchdog stable process identities; exit,
deadline, cancellation, termination, returned TP status, references, and
cleanup/reap state. At terminalization it also makes total elapsed time,
semantic invocation count, role/route sequence, terminal result, and verified
remaining TP-owned semantic-child/watchdog counts derivable.

This telemetry is mechanical evidence only: it never controls continuation or
terminal status, contains no secrets, auth material, environment dumps, or
substantive mission/result bodies, and never guesses hidden provider facts.
Hosts may materialize `diagnostics.jsonl` as a compact derived, non-authoritative
debugging projection of `events.jsonl`; it is never controller input. A
diagnostics-generation failure is reported separately and cannot rewrite an
already established semantic result.

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
contradiction, and performs the smallest bounded owner/falsification check that
could disprove an absence claim. “I did not find it” is not “it does not
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

The controller may bind and snapshot exact TP authority, persist exact input,
create run storage, mechanically validate identity/reference shape, record
dispatch/return events, launch and clean up fresh native invocations, and
report. It may not read substantive artifacts to choose continuation, discover
task requirements, judge acceptance, infer absence, choose a route, or declare
a terminal status.

The lifecycle is:

    bind authority -> fresh Brain -> one Execution -> fresh Brain -> ... -> terminal Brain -> reap owned semantic children

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
