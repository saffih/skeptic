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
3. dispatch every substantive action to a bounded child and select its route, model class, and reasoning effort proportionately.

### Planning and execution path (mutually exclusive)

Choose exactly one path. Ordinary non-Target work follows the ordinary path
below. A Target Task replaces the entire ordinary plan/review/repair/execution
path as a whole, not only its planning step, with the mandatory Planner
lifecycle in "## Target Tasks" below, ending in execution exactly once.

#### Ordinary non-Target path

4. dispatch a bounded Planner child to make a concise plan;
5. dispatch a bounded Skeptic child to run RunSkeptic on the plan once;
6. validate the returned receipt envelope;
7. dispatch bounded children to resolve material findings;
8. dispatch a bounded executor child.

### Common post-execution closeout

9. validate Agent Completion Envelopes and dispatch bounded qualifiers for semantic acceptance;
10. dispatch bounded deterministic children for the smallest sufficient checks;
11. report the result, routing, validation, and blockers.

## Target Tasks

When a prompt designates or executes a Target Task, replace the entire
ordinary plan/review/repair/execution path as a whole — not only its
planning step — with this mandatory sequence before execution:

```text
distinct bounded Planner dispatch
-> Agent Completion Envelope validation
-> complete Planner-produced plan
-> RunSkeptic review and receipt validation
-> Planner repair after every material plan change
-> bounded qualifier acceptance of the final unchanged plan
-> execution exactly once
```

Supplied drafts are Planner input only. Lead-authored, same-runtime, supplied,
previously approved, planning-not-required, or role-name-only planning cannot
satisfy the gate. Every executable plan version must be Planner-produced, and a
material plan change requires a new Planner repair dispatch and fresh review.
The bounded Planner does not recurse or authorize execution. If a mandatory
route or receipt is unavailable, stop with `CONFLICT`. Every substantive
ordinary or Target action uses a bounded child, because no trivial-work
exception is safe for cumulative session context.

If premium work may be needed, state whether it is pre-authorized. Pre-authorization
must identify the exact role, model or class, effort, bounded purpose, maximum
calls or attempts, and necessary permission and data-disclosure authority.
Otherwise require the Lead to preserve completed work, emit the
`MODEL_ESCALATION_CHECKPOINT`, and stop for explicit owner authorization before
premium execution or retry. Require minimum-context escalation, no repetition
of completed economical work, and return to LOW or the least expensive reliable
route after the bounded premium judgment.

Repeat RunSkeptic only after a material plan change, unexpected serious risk, or insufficient validation. Repair a harmless receipt-format defect without rerunning the review.

For trivial read-only work or one specified deterministic command, a bounded
child may use the smallest control packet and omit unnecessary planning
ceremony, but it still performs the substantive action outside the Lead context.

Delegation is mandatory for every substantive action, because bounded child
context is the architecture invariant rather than an optimization selected by
expected value.

Boundary processing is optional. Use `agents/boundary_agent.md` only when its
expected context, exposure, integration, or error-risk reduction exceeds its own
cost, because Boundary transformation is distinct from the mandatory bounded child.

When delegating to a model agent, specify a unique dispatch ID; bounded objective, scope, authority, and prohibitions; requested model class and reasoning effort; expected output and acceptance checks; escalation condition; and the Agent Completion Envelope required by `agents/agent_return_contract.md`.

A valid envelope confirms the return protocol, not the work. Dispatch a bounded
role-specific qualifier before integration, because the Lead must not read the
substantive return to accept or reject it.

When recursive delegation is authorized, state that orchestration obligations are
transitive and proportionate to each subtree: deterministic-first routing,
smallest-reliable model and effort, bounded dispatch, conditional Boundary Agent
selection, artifact-first handling, Agent Completion Envelope validation,
bounded downstream work acceptance, compact upward reporting, and evidence-based
escalation. A child orchestrator does not become the global Lead.

Use exact file references for every substantive inter-agent input and output in the
run-scoped orchestration workspace; keep only control metadata inline. Do not
assume fresh context:
use `FRESH_CONTEXT_CONFIRMED`, `PARENT_CONTEXT_INHERITED`, or
`CONTEXT_ISOLATION_UNKNOWN` when observable, and minimize explicit context when
inheritance is present or unknown.

Any Task Prompt that invokes RunSkeptic must include receipt validation before relying on its result.
