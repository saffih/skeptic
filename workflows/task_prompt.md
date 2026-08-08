# Task Prompt

## Invocation

`TP: <task>` is the Task Prompt invocation syntax: the text after `TP:` is the governing user task input; it activates this workflow; execution is orchestrated by the Lead contract (`agents/lead_agent.md`).

Include only what is needed to execute reliably:

- objective;
- scope;
- constraints;
- success criteria;
- permitted actions;
- prohibited actions, when relevant.

This is the Task Prompt's own schema. It is distinct from a bounded child's dispatch fields, which `agents/lead_agent.md`'s "Dispatch" section owns.

## Substantive pipeline

For substantive work, the first task-specific action is an unconditional bounded Planner dispatch, before any Lead-side discovery, source selection, or planning, because `docs/context-stewardship.md`'s domain-blind control plane forbids the Lead from deciding what happens next based on domain meaning. One pipeline governs every substantive Task Prompt, whether or not it designates a Target Task (skeptic.md's externally bound review target):

```text
bounded Planner dispatch (first task-specific action, unconditional)
-> Agent Completion Envelope validation (agents/agent_return_contract.md)
-> complete Planner-produced plan (agents/planner.md)
-> RunSkeptic review and receipt validation (skeptic.md)
-> Planner repair after every material plan change (agents/planner.md)
-> bounded qualifier acceptance of the final unchanged plan (agents/agent_return_contract.md)
-> execution exactly once
```

Supplied drafts are Planner input only. Lead-authored, same-runtime, supplied, previously approved, planning-not-required, or role-name-only planning cannot satisfy the gate. If a mandatory route or receipt is unavailable, stop with `CONFLICT`.

Repeat RunSkeptic only after a material plan change, unexpected serious risk, or insufficient validation; repair a harmless receipt-format defect without rerunning the review. This governs the ordinary single review only — when a Task Prompt explicitly invokes a RunSkeptic Find Loop or Fix Loop, `skeptic.md` alone governs that loop's invocation repetition, convergence, reset, stopping, and receipt rules, because a workflow contract must not override the framework's own loop authority.

For trivial read-only work or one specified deterministic command, a bounded child still performs the action outside the Lead context; no trivial-work exception skips bounded-child dispatch itself. Such a child may use the smallest control packet and omit unnecessary planning ceremony — that narrows the packet, not the Planner-first requirement.

Routing — model class, reasoning effort, `EXECUTION_ROUTING_NOTICE`, premium pre-authorization, `MODEL_ESCALATION_CHECKPOINT` — is `agents/model_routing_policy.md` and `agents/lead_agent.md` default behavior, applied automatically to every substantive Task Prompt; this workflow does not restate it.

## Post-execution

Envelope validation, qualifier acceptance, deterministic validation, and reporting follow `agents/lead_agent.md`'s "Returns and continuation," "Candidate safety and validation," and "Reporting" sections without addition.
