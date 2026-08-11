# Model Routing Policy

This is the single canonical policy for route selection, model-class
selection, reasoning-effort selection, escalation, premium authorization,
route-related data disclosure, and requested-versus-actual routing
observability. A control plane such as `agents/lead_agent.md` applies a route
decision produced under this policy; it does not redefine routing meaning.

This policy does not define Lead orchestration-only behavior, mandatory
bounded-child delegation, run-workspace creation, Context Rules,
working-context decomposition, dispatch-field schema, Agent Return fields,
Boundary invocation criteria, workflow lifecycle, Task Prompt schema,
RunSkeptic, WELL, semantic acceptance, candidate isolation, or task
completion. Those belong to their own owning authorities.

## Objective

The routing objective is not "use the cheapest individual call." It is: use
the least expensive authorized route reasonably expected to complete the
bounded obligation reliably, accounting for expected retries, correction,
review, context-transfer and integration overhead, and failure risk.

Do not pay for stronger capability without a reason. Do not choose a weaker
route when the expected total completion cost or failure risk makes it a
false economy. The cheapest individual call is not always the lowest-cost
completion path.

## Route classes

### Default order

1. Deterministic tool or script.
2. Small model with low reasoning.
3. Medium model with proportionate reasoning.
4. Strongest model only when justified.

### Deterministic work

Prefer deterministic tools for exact mechanical work, including tests,
linting, type checks, builds, repository-state checks, hashing, schema
validation, exact comparison, receipt structure checks, fixed-envelope
parsing, and report generation from verified structured data. Deterministic
execution does not replace semantic judgment; use it only where the
obligation is genuinely mechanical and exact.

### Model classes

Define model classes by required capability, not provider names.

#### Small

Use for bounded, low-ambiguity work such as narrow extraction, formatting,
classification, or a small mechanical repair.

#### Medium

Use for ordinary implementation, multi-file edits, focused semantic review,
and planning that requires judgment across multiple interacting facts but not
exceptional synthesis.

#### Strongest

Use only for materially consequential architecture, high-risk or conflicting
evidence, difficult synthesis, or a demonstrated lower-class failure.

"Best model", "Lead model", or "important task" is not sufficient
justification.

## Reasoning effort

Reasoning effort is selected independently from model class. Use the lowest
effort reasonably expected to be reliable:

- low for mechanical, low-ambiguity work;
- medium for ordinary semantic implementation, review, and planning;
- high only for difficult ambiguity, architecture, conflicting evidence, or
  high-impact synthesis.

This policy does not define provider-specific effort levels beyond this
generic vocabulary.

## Selection

A route may be selected in one of three ways:

- explicitly fixed by governing authority;
- selected mechanically, when the selection criteria are deterministic;
- selected by a semantic routing role, when applying the criteria requires
  judgment.

A control plane consumes and applies that decision under its own contract; it
does not itself make a semantic route judgment. No routing decision may
silently widen permissions or data access beyond what was already authorized
for the obligation.

When a Boundary role is invoked, its own obligation is routed under this same
policy. The Boundary route does not automatically inherit the substantive
worker's model class or effort.

A role that is itself authorized to dispatch further bounded work applies
this routing policy independently to what it dispatches. It does not
automatically inherit its own parent's model class or effort, and it cannot
widen its parent's authorization. This does not transfer global Lead
ownership to that role.

## Escalation

Escalate to a stronger or more expensive route only on evidence:

- observed insufficiency of the current route;
- ambiguity or risk already evident before execution;
- conflicting evidence requiring higher capability;
- governing authority explicitly requires the stronger route.

A failed call by itself does not automatically justify a stronger model.
Avoid an unchanged retry when evidence says it is unlikely to help.

A context-capacity failure — a context-window rejection or equivalent
admission failure — is not evidence of insufficient semantic model
capability. Context-capacity handling belongs to Context Rules, not to
this policy; do not escalate model class or effort in response to it. A
timeout or malformed return likewise does not by itself establish that a
stronger semantic model is required.

### Retries

Allow one premium attempt by default and zero automatic premium retries.
After a failed, timed-out, or malformed attempt, report the outcome,
diagnose with deterministic tools, narrow the task, and obtain explicit
authorization before another attempt unless the exact retries were
pre-authorized. A timeout or malformed receipt alone does not justify a
stronger or repeated call.

Give a premium worker the exact bounded question, the required output
schema, and durable references to already-completed exploration, tests, and
resolved findings rather than retransmitting their bodies. Do not repeat
repository exploration, implementation, completed tests, or resolved
findings as retransmitted content where a reference is sufficient. This
controls cost; it is not an evidence boundary — the premium recipient
retains access to every source already authorized for its obligation under
Context Rules, and may independently retrieve additional authorized
source material when correctness, freshness, contradiction resolution,
completeness, or evidence sufficiency requires it.

Each follow-on bounded obligation — including return integration,
documentation, and other work that follows a premium stage — is routed
independently under this policy. It does not inherit the premium route
merely because an upstream stage used one, but neither is LOW forced when
the follow-on obligation genuinely requires greater capability or effort.
Among authorized options, the least expensive reliable route remains the
objective.

## Authorization and disclosure

### Execution routing notice

This policy owns the meaning and required contents of
`EXECUTION_ROUTING_NOTICE`; the governing workflow or control binding decides
when that notice is required. When activated, the notice states the
requested starting model or model class and effort, the work expected to
remain on that route, known potential premium stages, and that execution
stops before any unapproved premium stage. Tell the owner that they may stop
at that checkpoint without losing completed work. Do not require a response
while economical work can safely begin, and do not claim that a named
runtime or model exists unless it is observable.

### Premium and additional-usage authorization

"Premium" is not tied to a particular provider; it names any route or stage
that requires additional explicit authorization under the active task.

Premium execution may proceed automatically only when the Task Prompt already
authorizes the exact role, model or class, effort, bounded purpose, maximum
calls or attempts, and necessary permission and data disclosure. Otherwise
stop for explicit owner authorization; silence is not authorization.
Pre-authorized premium execution is allowed only within the exact granted
scope.

Before an unapproved premium or additional-usage stage — including a
strongest-model route, HIGH effort when it requires additional
authorization, any runtime-specific route or effort tier designated premium
by the governing authorization, or an additional premium reviewer, call, or
retry — preserve completed work and emit a `MODEL_ESCALATION_CHECKPOINT`
containing:

- completed durable work and checks passed;
- the preserved artifact or commit location;
- the exact remaining bounded stage and recommended model or class and
  effort;
- why the current route is insufficient and the maximum calls or attempts;
- the context-isolation requirement and minimum inputs;
- work that must not be repeated;
- the safe stopping result and exact resume instruction.

Include this meaning: "You may stop here to avoid additional usage. All
completed work has been preserved."

### Data disclosure and egress

Selecting a route does not authorize sending data to it. Before a route
receives protected, private, or restricted data, the governing authorization
must permit that disclosure. Supply only the material needed for the bounded
obligation.

If the needed route is available but the necessary disclosure is not
authorized, report or return an authorization or data-egress blocker. Do not
misclassify it as a context failure, a model failure, or a semantic failure.
Routing cannot widen source permissions granted elsewhere, and this policy
does not duplicate Context Rules' curation rules.

## Requested and actual routing

Record requested route, model class, and effort. Record actual runtime,
model, version, effort, and exposed settings only when observable.

When actual routing is hidden, report `ACTUAL_ROUTING_UNKNOWN`. Do not claim
verified routing, and do not claim that a free, local, or other route exists
unless the runtime exposes it.

If a required requested route is unavailable, expose `ROUTE_UNAVAILABLE`. Do
not silently substitute a materially different route when the governing
authorization requires the exact route or class. If a permitted equivalent
substitution is mechanically authorized, record it.

## Fixed routing constraints

Routing and cost optimization must not alter model, generation, benchmark, or
other settings fixed by governing authority merely to reduce cost.
