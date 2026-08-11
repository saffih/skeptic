# Task Prompt (TP)

This file is the canonical and complete authority for a normal Task Prompt.
It is deliberately host-neutral. A host may provide transport and map the
abstract routes below to available models, but may not add semantic TP rules.

## Invocation and mission

An agent receiving `TP: <mission>` activates this workflow. The mission is the
text received after `TP:`. The agent is responsible for understanding it; TP
does not require a pre-model capture of chat bytes, a user-managed intent file,
or a mandatory hash ceremony.

The controller persists the mission immediately in `run/mission.md`, creates a
run directory, writes `events.jsonl` and equivalent run-control bookkeeping,
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
selects sources, decomposes work, chooses a route, judges completion, handles
unexpected conditions, and authorizes the next control step. `LOW`, `MEDIUM`,
and `STRONG` name the capability requested for the next semantic dispatch;
`NONE` means that no further semantic dispatch is requested. Brain normally
starts at `MEDIUM` and may request `STRONG` when the current capability is
insufficient. The controller applies Brain's selected route mechanically and
never decides semantic escalation itself. Provider/model mapping remains
outside this authority, in the host or its routing policy.

A Block is one bounded semantic assignment. Its worker performs that assignment
and returns the bounded result. A worker never chooses continuation, spawns
TP, or grants itself authority.

## Durable run state

The minimal durable layout is:

    run/
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
    next: SEQUENCE | NONE
    blocks: <finite non-empty ordered block references> | NONE
    reason: <short explanation>

For `CONTINUE`, `route` is `LOW`, `MEDIUM`, or `STRONG`, `next` is `SEQUENCE`,
and `blocks` is a finite non-empty ordered sequence authored by Brain. For
`COMPLETE`, `BLOCKED`, or `CONFLICT`, `route` is `NONE`, `next` is `NONE`, and
`blocks` is `NONE`; these are terminal outcomes for the current Brain result.
`SEQUENCE` means the controller may mechanically dispatch those blocks in
order; it does not mean the controller understood their content, and workers
never choose successors. If the current Brain is insufficient, it returns
`CONTINUE` with `route: STRONG`; the controller then makes the next Brain
dispatch at `STRONG` without interpreting the mission. `COMPLETE` is allowed
only when Brain has judged the mission and its acceptance obligation satisfied.
`BLOCKED` or `CONFLICT` must identify the
unresolved condition sufficiently for the next Brain to act.

## Block return

Each Block receives its own reference, the mission/run references needed for
context, and its bounded acceptance obligation. It returns:

    TP_RESULT
    role: BLOCK
    status: DONE | BLOCKED | CONFLICT
    block_ref: <its assigned reference>
    result_ref: <receiver-resolvable result/artifact reference, or NONE>
    reason: <short explanation>

`DONE` means this Block satisfied the acceptance and validation obligation Brain
assigned to it. It does not mean the whole mission is complete. A Block may
write artifacts under `run/artifacts/`, but it cannot authorize another Block.

## Bounded continuation

Brain authorizes a finite non-empty ordered sequence of one or more Blocks.
The controller dispatches the next reference only after the current Block
returns a valid `DONE`; it does not call Brain between successful Blocks.
The controller alone records every admission and return in its bookkeeping.

When a mission calls for repeated semantic passes over the same material,
each pass runs in its own fresh Block; only compact durable findings or
references carry forward between passes, not the accumulating context of
prior passes.

Return to Brain on `BLOCKED`, `CONFLICT`, a malformed or missing result, an
unexpected condition, or sequence exhaustion. Sequence exhaustion is not
completion: Brain decides whether the mission is complete, needs another
sequence, or is blocked. The controller never infers that decision.

Brain may request a stronger Brain when the current Brain cannot safely decide.
Escalation is a fresh invocation with the durable run and result references;
the host maps `STRONG` as it can. A worker cannot request or perform semantic
escalation on its own.

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

Brain need not spawn subagents. For substantial exploration it should create a
bounded discovery Block and regain semantic control through its result.

## Completion and publication

Only Brain may declare mission completion, after reviewing the returned evidence
against the mission and acceptance obligation. Publication, commit, push, or
other external effects require explicit authorization in the mission and the
repository's governing rules. TP records the terminal result and stops. If
completion cannot be established safely, the terminal result is `BLOCKED` or
`CONFLICT`, not a guess.
