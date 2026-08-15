# Task Prompt (TP)

This file is the canonical and complete authority for a normal Task Prompt.
It is deliberately host-neutral. A host may provide transport and map the
abstract routes below to available models, but may not add semantic TP rules.

## Invocation and mission

An agent receiving `TP: <mission>` activates this workflow. The mission is the
text received after `TP:`. The agent is responsible for understanding it; TP
does not require a pre-model capture of chat bytes, a user-managed intent file,
or a mandatory hash ceremony.

The controller persists the mission immediately in its host-owned external run
root at `mission.md`, creates that run directory, writes `events.jsonl` and
equivalent run-control bookkeeping,
and then starts a fresh Brain on the normal capable route. Only the controller
may write that bookkeeping. Brain and Blocks may write only their authorized
result and artifact files; Brain may propose control decisions in `TP_RESULT`
but may not mutate controller-owned state. A host may keep an internal digest
for identity or diagnostics, but it is not a semantic admission gate.

## Roles and authority

The controller/Lead is domain-blind. It may create run state, dispatch fresh
agents, follow valid Brain-authored control, perform already-authorized
mechanical actions, and record outcomes. It must not interpret repository
meaning, choose relevant sources, judge acceptance, or infer continuation from
substantive output.

Brain is the semantic authority. It understands the mission, retrieves and
selects sources, decomposes work, chooses the next dispatch capability, judges
completion, handles unexpected conditions, and authorizes the next control
step. `route` names that capability; `next` names its dispatch kind. Brain
normally starts at `MEDIUM` and may request a fresh `STRONG` Brain when the
current capability is insufficient. The controller follows those selections
mechanically and never decides semantic escalation itself. Provider/model
mapping remains outside this authority, in the host or its routing policy.

Before accepting each materially new semantic judgment, including initial
mission design where applicable, Brain performs Capability Admission under
`agents/model_routing_policy.md`, because the current role must establish that
it can safely own the next judgment.

Brain distinguishes insufficient current capability from authorized retrieval,
safe decomposition, a missing-authority or feasibility blocker, or stronger
downstream work, because those paths do not have the same remedy. Brain
escalates itself only when the judgment Brain itself must own exceeds its
current capability; stronger downstream work does not itself require stronger
Brain capability.

A Block is one bounded semantic assignment. Its worker performs that assignment
and returns the bounded result. A worker never chooses continuation, spawns
TP, or grants itself authority.

## Durable run state

The minimal durable layout is relative to that external run root (it is not a
directory in the target repository):

    mission.md
    events.jsonl
    artifacts/

Events should record at least run creation, dispatch admission, valid return,
and terminal outcome. References in packets and results must be resolvable by
the receiving agent. A dispatch is admitted before launch and marked returned
only after a valid result is observed.

If admission is recorded but no terminal result is known, do not blindly replay
the dispatch. Return to Brain with the unresolved effect so it can decide a
safe recovery. Malformed, missing, or otherwise unexpected state is likewise
fail-closed to Brain (or `CONFLICT` when Brain cannot safely be reached).

## Brain return

Brain returns a compact control result containing:

    TP_RESULT
    role: BRAIN
    status: CONTINUE | COMPLETE | BLOCKED | CONFLICT
    route: LOW | MEDIUM | STRONG | NONE
    next: SEQUENCE | BRAIN | NONE
    blocks: <finite non-empty ordered block references> | NONE
    result_ref: <receiver-resolvable report/result reference> | NONE
    reason: <short control explanation, at most 240 characters>

For `CONTINUE`, `next: SEQUENCE` requires a `LOW`, `MEDIUM`, or `STRONG`
`route`, a finite non-empty ordered sequence of authorized durable
Block-assignment artifact references, and `result_ref: NONE`. `next: BRAIN`
requires `route: STRONG`, `blocks: NONE`, and a resolvable handoff `result_ref`.
Before dispatch the controller verifies each reference resolves below the
external run root's `artifacts/` directory, without reading it. For `COMPLETE`,
`BLOCKED`, or `CONFLICT`, `route` and `next` are `NONE`, `blocks` is `NONE`, and
`result_ref` is a resolvable terminal
report/result artifact when Brain has substantive terminal material to
preserve, otherwise `NONE`. These are terminal outcomes for the current Brain
result. `SEQUENCE` dispatches its assignments in order; `BRAIN` dispatches one
fresh `STRONG` Brain with the durable run, mission, and handoff-result
references. Neither action requires the controller to interpret the mission or
an artifact, and workers never choose successors. `COMPLETE` is allowed only
when Brain has judged the mission and its acceptance obligation satisfied. If
the mission requires publication, that judgment must include the required
publication evidence, including commit, push, and any required remote
verification; local implementation or test success alone is not completion.
A missing publication step is remaining authorized work unless the required
external action has been attempted and is a genuine external blocker.
`BLOCKED` is a terminal semantic decision, not a progress report. Brain may
use it only when remaining authorized work cannot safely proceed now because
required meaning or authority is unavailable or irreconcilably conflicting, a
required capability is unavailable with no authorized substitute, or an
authorized external action has failed after the required attempt. An expected
starting defect, incomplete implementation, unrun in-scope check, or sequence
exhaustion is not by itself a blocker; Brain returns `CONTINUE` with the next
bounded work, or escalates to a fresh Brain when it cannot safely decide. The
terminal artifact preserves the evidence supporting why continuation is
unavailable. `BLOCKED` or `CONFLICT` keeps `reason` to a compact control
summary sufficient for a subsequent dispatch (at most 240 characters).

Before returning `BLOCKED` or `CONFLICT`, Brain performs bounded terminal
validation proportional to the proposed stopping reason. Brain identifies the
exact stopping proposition, records primary evidence sufficient to support it,
and checks durable evidence already returned in the run for a material
contradiction. A Block's unsupported conclusion, or failure to locate a rule,
is not by itself evidence that the rule or capability does not exist. For an
absence claim, when the authoritative owner is available and the check is
bounded, Brain retrieves or dispatches the smallest reasonable owner-coverage
or falsification check that could disprove the claim. Brain must reconcile a
contradiction through bounded evidence retrieval, decomposition, or the
existing Brain capability/escalation path; it must not select one claim by
preference. If evidence is insufficient but a safe evidence-gathering path
exists, Brain returns `CONTINUE` with that bounded retrieval, contradiction
resolution, decomposition, or escalation. Only an evidenced genuine blocker
or irreconcilable conflict permits terminal `BLOCKED`/`CONFLICT`. This is a
semantic Brain obligation, not a controller check, a new role or status, and
does not require a full RunSkeptic invocation for every terminal decision.

## Block return

Each Block receives its own reference, the mission/run references needed for
context, and its bounded acceptance obligation. It returns:

    TP_RESULT
    role: BLOCK
    status: DONE | BLOCKED | CONFLICT
    block_ref: <its assigned reference>
    result_ref: <receiver-resolvable result/artifact reference>
    reason: <short control explanation, at most 240 characters>

`DONE` means this Block satisfied the acceptance and validation obligation Brain
assigned to it. It does not mean the whole mission is complete. A Block writes
its report or work product under `artifacts/` and returns that reference; it
does not create a second receipt about that work. `BLOCKED` and `CONFLICT` also
return a report artifact so their substantive explanation and evidence survive
the invocation. A Block cannot authorize another Block. Before recording a
Block return as valid, the controller mechanically verifies that `result_ref`
resolves to an existing authorized run artifact, then durably records only the
assigned `block_ref`, status, and `result_ref`; it never reads the artifact.

## Bounded continuation

Brain authorizes a finite non-empty ordered sequence of one or more Blocks.
The controller dispatches the next reference only after the current Block
returns a valid `DONE`; it does not call Brain between successful Blocks.
The controller alone records every admission and return in its bookkeeping.

When a mission calls for repeated semantic passes over the same material,
each pass runs in its own fresh Block and writes a distinct report artifact;
only compact control and durable references carry forward, not the accumulating
context of prior passes. Scout and RunSkeptic are ordinary Blocks under this
same rule: their research or review work product is the result artifact, and
their `TP_RESULT` carries status, reference, and compact control reason only.

Return to Brain on `BLOCKED`, `CONFLICT`, a malformed or missing result, an
unexpected condition, or sequence exhaustion. Sequence exhaustion is not
completion: Brain decides whether the mission is complete, needs another
sequence, or is blocked. The controller never infers that decision.

Brain may request the `BRAIN` continuation when the current Brain cannot safely
decide. Escalation is a fresh invocation with the durable run and handoff-result
references; the host maps `STRONG` as it can. A worker cannot request or
perform semantic escalation on its own.

## Context, process, and return safety

Before Brain authorizes a Block, it must establish that the Block's semantic
obligation and expected working set are genuinely bounded, including known
subsequent source loading. If fit is not established, Brain decomposes before
dispatch into smaller semantic obligations carried by durable references.
Decomposition must not weaken required freshness, completeness, or
independence. If a required complete semantic obligation cannot fit, Brain
returns an explicit context blocker rather than narrowing the obligation.

A worker must not leave transient processes it started running after return.
Persistent or external processes require explicit mission authorization and
must not be killed merely because TP observes them.

For research, Brain authorizes a Scout Block with the question, source authority,
and bounded return contract; Scout gathers and condenses only the requested
evidence with resolvable references, and Brain decides from the result.

## Completion and publication

Only Brain may declare mission completion, after reviewing the returned evidence
against the mission and acceptance obligation. Publication, commit, push, or
other external effects require explicit authorization in the mission and the
repository's governing rules. The controller remains domain-blind: it may
validate mechanically supplied publication facts and references, but it does
not decide semantic completion or whether a failure is mission-related. TP
records the terminal result and stops. If completion cannot be established
safely, the terminal result is `BLOCKED` or `CONFLICT`, not a guess.
