# Task Prompt

Include only what is needed to execute reliably:

- objective;
- scope;
- constraints;
- success criteria;
- permitted actions;
- prohibited actions, when relevant.

For substantive work:

1. make a concise plan;
2. select deterministic work, direct work, delegation, model class, and reasoning effort proportionately;
3. RunSkeptic on the plan once;
4. validate the RunSkeptic receipt;
5. resolve material findings;
6. execute;
7. validate delegated Agent Completion Envelopes and then independently accept or reject their work;
8. run the smallest sufficient deterministic checks;
9. report the result, routing, validation, and blockers.

Repeat RunSkeptic only after a material plan change, unexpected serious risk, or insufficient validation. Repair a harmless receipt-format defect without rerunning the review.

For trivial read-only work or one specified deterministic command, skip the formal plan and RunSkeptic unless risk or ambiguity justifies them.

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
