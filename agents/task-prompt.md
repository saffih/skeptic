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

When delegating to a model agent, specify a unique dispatch ID; bounded objective, scope, authority, and prohibitions; requested model class and reasoning effort; expected output and acceptance checks; escalation condition; and the Agent Completion Envelope required by `agents/agent-return.md`.

A valid envelope confirms the return protocol, not the work. Apply role-specific acceptance before integration.

Any Task Prompt that invokes RunSkeptic must include receipt validation before relying on its result.
