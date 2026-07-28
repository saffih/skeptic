# Model Routing

Use the least expensive route reasonably expected to complete the bounded role reliably.

For substantive Task Prompt execution, begin with a concise
`EXECUTION_ROUTING_NOTICE` that states the exact requested starting model or
model class and effort, the work expected to remain on that route, known
potential premium stages, and that execution stops before any unapproved
premium stage. Tell the owner that they may stop at that checkpoint without
losing completed work. Do not require a response while economical work can
safely begin, and do not claim that a named runtime or model exists unless it
is observable.

## Default order

1. Deterministic tool or script.
2. Small model with low reasoning.
3. Medium model with proportionate reasoning.
4. Strongest model only when justified.

The cheapest individual call is not always the lowest-cost completion path. Include likely retries, correction, review, context transfer, and integration burden.

## Deterministic work

Prefer deterministic tools for exact mechanical work, including tests, linting, type checks, builds, repository-state checks, hashing, schema validation, exact comparison, receipt structure checks, fixed-envelope parsing, and report generation from verified structured data.

## Model classes

### Small

Use for bounded, low-ambiguity work such as narrow extraction, formatting, classification, or a small mechanical repair.

### Medium

Use for ordinary implementation, multi-file edits, focused semantic review, and planning that requires judgment but not exceptional synthesis.

### Strongest

Use only for materially consequential architecture, high-risk ambiguity, conflicting evidence, difficult synthesis, or a demonstrated lower-class failure.

"Best model", "Lead model", or "important task" is not sufficient justification.

## Reasoning effort

Use the lowest effort likely to be reliable:

- low for mechanical bounded work;
- medium for ordinary implementation and review;
- high only for difficult ambiguity, architecture, or high-impact synthesis.

## Delegation

Delegate only when isolation, specialization, parallelism, protected context, or independent review provides clear value.

A delegated model role must state:

- unique dispatch ID;
- bounded objective and scope;
- authority and prohibitions;
- expected output;
- requested model class and reasoning effort;
- acceptance checks;
- escalation condition;
- required Agent Completion Envelope.

Delegated agents do not inherit the Lead model or effort automatically.

## Boundary routing

Use `agents/boundary-agent.md` conditionally when context processing has material
expected value. A compact direct delegation needs no Boundary Agent.

Route boundary work in this order:

1. deterministic tool or script;
2. free or local agent when available, exposed, and reliable;
3. smallest low-effort model reasonably expected to perform the transformation;
4. a stronger route only after observed insufficiency or when semantic omission
   risk materially requires it.

The boundary route does not inherit the substantive worker's model or effort.
Do not claim that a free/local route exists unless the runtime exposes it.

Routing and context discipline are transitive when a delegated orchestrator
delegates further, proportionate to its subtree; this does not transfer global
Lead ownership or task-level completion.

## Escalation

Escalate only when observed evidence shows that the assigned route is insufficient. Record the failed route, the observed defect or uncertainty, why an unchanged retry is unlikely to help, and the expected benefit of escalation.

Before HIGH, XHIGH, MAX, a strongest-model route, an additional premium
reviewer, or a retry of a failed premium attempt, preserve completed work and
emit a `MODEL_ESCALATION_CHECKPOINT` containing:

- completed durable work and checks passed;
- the preserved artifact or commit location;
- the exact remaining bounded stage and recommended model or class and effort;
- why the current route is insufficient and the maximum calls or attempts;
- the context-isolation requirement and minimum inputs;
- work that must not be repeated;
- the safe stopping result and exact resume instruction.

Include this meaning: “You may stop here to avoid additional usage. All
completed work has been preserved.”

Premium execution may proceed automatically only when the Task Prompt already
authorizes the exact role, model or class, effort, bounded purpose, maximum
calls or attempts, and necessary permission and data disclosure. Otherwise
stop for explicit owner authorization; silence is not authorization.

Allow one premium attempt by default and zero automatic premium retries. After
a failed, timed-out, or malformed attempt, report the outcome, diagnose with
deterministic tools, narrow the task, and obtain explicit authorization before
another attempt unless the exact retries were pre-authorized. A timeout or
malformed receipt alone does not justify a stronger or repeated call.

Give a premium worker only the exact bounded question, relevant frozen
artifacts or excerpts, identities or hashes, compact evidence summary, rubric,
output schema, and authority and prohibitions. Do not repeat repository
exploration, implementation, completed tests, planning, or resolved findings
at the premium route.

After bounded premium judgment, return integration, deterministic checks,
documentation, manifests, commits, publication, and final packaging to LOW or
the least expensive reliable route.

Do not change controlled model or generation settings in a frozen benchmark merely to reduce cost.

## Requested and actual routing

Record requested model class and effort. Record actual runtime, model, version, effort, and exposed settings only when observable.

When actual routing is hidden, report `ACTUAL_ROUTING_UNKNOWN`. Do not claim verified routing.

Substantive RunSkeptic is a bounded Brain-level role. Deterministic receipt
lint is not RunSkeptic reasoning. Use MEDIUM only for narrow low-risk semantic
review; use HIGH by default for repository-wide architecture or promotion
review. XHIGH requires unresolved architectural conflict, materially conflicting
evidence, or inadequate HIGH confidence, and is never automatic. The Brain
retrieves primary evidence independently. An underpowered, incomplete,
non-independent, or context-degraded review cannot qualify as a promotion pass.
Record `RUNSKEPTIC_MODEL_PER_RUN`, `RUNSKEPTIC_REASONING_LEVEL_PER_RUN`,
`RUNSKEPTIC_CONTEXT_STATUS_PER_RUN`, `RUNSKEPTIC_INDEPENDENCE_PER_RUN`,
`RUNSKEPTIC_REPAIR_RUNS`, `RUNSKEPTIC_QUALIFYING_PASSES`, and
`RUNSKEPTIC_FINAL_CATEGORY`.
