# Model Routing

Use the least expensive route reasonably expected to complete the bounded role reliably.

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

## Escalation

Escalate only when observed evidence shows that the assigned route is insufficient. Record the failed route, the observed defect or uncertainty, why an unchanged retry is unlikely to help, and the expected benefit of escalation.

Do not change controlled model or generation settings in a frozen benchmark merely to reduce cost.

## Requested and actual routing

Record requested model class and effort. Record actual runtime, model, version, effort, and exposed settings only when observable.

When actual routing is hidden, report `ACTUAL_ROUTING_UNKNOWN`. Do not claim verified routing.
