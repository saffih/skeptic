# Task Prompt

Include only what is needed to execute reliably:

- objective;
- scope;
- constraints;
- success criteria;
- permitted actions;
- prohibited actions, when relevant.

For substantive work:

### Common substantive preflight

1. specify the starting model or model class and reasoning effort, work expected
   to remain there, and any likely premium roles;
2. require the `EXECUTION_ROUTING_NOTICE` from `agents/model_routing_policy.md`;
3. select deterministic work, direct work, delegation, model class, and reasoning effort proportionately.

### Planning and execution path (mutually exclusive)

Choose exactly one path. Ordinary non-Target work follows the ordinary path
below. A Target Task replaces the entire ordinary plan/review/repair/execution
path as a whole, not only its planning step, with the mandatory Planner
lifecycle in "## Target Tasks" below, ending in execution exactly once.

#### Ordinary non-Target path

4. make a concise plan;
5. RunSkeptic on the plan once;
6. validate the RunSkeptic receipt;
7. resolve material findings;
8. execute.

### Common post-execution closeout

9. validate delegated Agent Completion Envelopes and then independently accept or reject their work;
10. run the smallest sufficient deterministic checks;
11. report the result, routing, validation, and blockers.

## Target Tasks

A Target Task is triggered by the exact prefix `TT:`; the text after it is the
immutable mission. Read `workflows/target_task.md` before designating or
executing one — it owns the complete lifecycle, the Luna compact-Lead
contract, the sealed-Plan invariant, the append-only ledger discipline, and
the live Claude Code MVP route loaded through root `CLAUDE.md` and `AGENTS.md`.
`concepts/target_task/` holds the deterministic contracts used by that live
workflow; `.claude/agents/target-task-*.md` registers its bounded host roles.

When a prompt designates or executes a Target Task, replace the entire
ordinary plan/review/repair/execution path as a whole — not only its
planning step — with this mandatory sequence before execution:

```text
mission persisted immutably, never inlined into durable Lead context
-> distinct bounded Planner dispatch
-> Agent Completion Envelope validation
-> complete Planner-produced plan
-> RunSkeptic Fix Loop on the plan (three consecutive qualifying passes)
-> Plan sealed: path, SHA-256, byte size, schema version recorded and frozen
-> execution of the sealed plan exactly once, never replanned inside the run
-> deterministic validation
-> candidate frozen
-> read-only RunSkeptic Find Loop over the frozen candidate
-> integration only when clean and mechanically possible
-> close with a compact receipt
```

Supplied drafts are Planner input only. Lead-authored, same-runtime, supplied,
previously approved, planning-not-required, or role-name-only planning cannot
satisfy the gate. Every executable plan version must be Planner-produced, and a
material plan change requires a new Planner repair dispatch and fresh
RunSkeptic Fix Loop before the plan may be sealed. Once sealed, the plan is
frozen for that run: it may not be edited, replaced, extended, reordered,
repaired, or reinterpreted. If the sealed plan cannot be completed safely,
stop and report the blocker rather than replanning inside the same run. The
bounded Planner does not recurse or authorize execution. If a mandatory
route or receipt is unavailable, stop with `CONFLICT`. Ordinary non-Target work
remains proportional and does not inherit this section merely because it is
substantive.

Do not use the Target Task lifecycle to construct or modify the Target Task
lifecycle itself. Changes to this section, `workflows/target_task.md`, or
`concepts/target_task/` are ordinary Task Prompt work.

If premium work may be needed, state whether it is pre-authorized. Pre-authorization
must identify the exact role, model or class, effort, bounded purpose, maximum
calls or attempts, and necessary permission and data-disclosure authority.
Otherwise require the Lead to preserve completed work, emit the
`MODEL_ESCALATION_CHECKPOINT`, and stop for explicit owner authorization before
premium execution or retry. Require minimum-context escalation, no repetition
of completed economical work, and return to LOW or the least expensive reliable
route after the bounded premium judgment.

For Target Task, run complete Fix Loop reviews until three consecutive qualifying passes exist on the exact unchanged Plan. A material Plan change resets the count and requires a replacement Planner Plan; a harmless receipt-format repair does not substitute for or add a review pass. The final Find Loop is independent and read-only.

For ordinary non-Target trivial read-only work or one specified deterministic command, skip the formal plan and RunSkeptic unless risk or ambiguity justifies them. This exception never applies to an explicit Target Task.
Do not add routing notices or escalation machinery to those trivial tasks.

For ordinary non-Target work, delegation is optional and Boundary processing is conditional. Target Task is the explicit exception: its distinct Planner/reviewer/worker dispatches and deterministic Boundary gates are mandatory exactly where `workflows/target_task.md` requires them.

When delegating to a model agent, specify a unique dispatch ID; bounded objective, scope, authority, and prohibitions; requested model class and reasoning effort; expected output and acceptance checks; escalation condition; and the Agent Completion Envelope required by `agents/agent_return_contract.md`.

A valid envelope confirms the return protocol, not the work. Apply role-specific acceptance before integration.

When recursive delegation is authorized, state that orchestration obligations are
transitive and proportionate to each subtree: deterministic-first routing,
smallest-reliable model and effort, bounded dispatch, conditional Boundary Agent
selection, artifact-first handling, Agent Completion Envelope validation,
independent work acceptance, compact upward reporting, and evidence-based
escalation. A child orchestrator does not become the global Lead.

Use artifact references for substantial or reusable context when the recipient can
reliably access them; keep small decision-critical content inline. Do not require
artifacts or persistence for trivial one-session work. Do not assume fresh context:
use `FRESH_CONTEXT_CONFIRMED`, `PARENT_CONTEXT_INHERITED`, or
`CONTEXT_ISOLATION_UNKNOWN` when observable, and minimize explicit context when
inheritance is present or unknown.

Any Task Prompt that invokes RunSkeptic must include receipt validation before relying on its result.
