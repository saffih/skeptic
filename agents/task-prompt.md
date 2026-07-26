# Task Prompt

Include only what is needed to execute reliably:

- objective;
- scope;
- constraints;
- success criteria;
- permitted actions;
- prohibited actions, when relevant.

For substantive work:

1. specify the starting model or model class and reasoning effort, work expected
   to remain there, and any likely premium roles;
2. require the `EXECUTION_ROUTING_NOTICE` from `agents/model-routing.md`;
3. make a concise plan;
4. select deterministic work, direct work, delegation, model class, and reasoning effort proportionately;
5. RunSkeptic on the plan once;
6. validate the RunSkeptic receipt;
7. resolve material findings;
8. execute;
9. validate delegated Agent Completion Envelopes and then independently accept or reject their work;
10. run the smallest sufficient deterministic checks;
11. report the result, routing, validation, and blockers.

If premium work may be needed, state whether it is pre-authorized. Pre-authorization
must identify the exact role, model or class, effort, bounded purpose, maximum
calls or attempts, and necessary permission and data-disclosure authority.
Otherwise require the Lead to preserve completed work, emit the
`MODEL_ESCALATION_CHECKPOINT`, and stop for explicit owner authorization before
premium execution or retry. Require minimum-context escalation, no repetition
of completed economical work, and return to LOW or the least expensive reliable
route after the bounded premium judgment.

Repeat RunSkeptic only after a material plan change, unexpected serious risk, or insufficient validation. Repair a harmless receipt-format defect without rerunning the review.

For trivial read-only work or one specified deterministic command, skip the formal plan and RunSkeptic unless risk or ambiguity justifies them.
Do not add routing notices or escalation machinery to those trivial tasks.

Delegation is optional. Use it only when it clearly improves isolation, specialization, parallelism, protected context, or review.

Boundary processing is also optional. Use `agents/boundary-agent.md` only when its
expected context, exposure, integration, or error-risk reduction exceeds its own
cost. Direct compact delegation remains valid.

When delegating to a model agent, specify a unique dispatch ID; bounded objective, scope, authority, and prohibitions; requested model class and reasoning effort; expected output and acceptance checks; escalation condition; and the Agent Completion Envelope required by `agents/agent-return.md`.

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
