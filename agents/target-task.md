# Target Task

This is the canonical, provider-neutral execution and context-management
harness. `TT:` is the preferred trigger. `OTP:` is an explicit compatibility
alias that maps to this same protocol; Optimal Task Prompt is historical
migration terminology, and `TP:` remains the separate legacy Task Prompt
builder.

The approved architecture is persisted at
`architecture/target-task-architecture.md`. That document is the source of
truth for the design; this file is the executable protocol summary and must
remain aligned with it.

## Core invariant

Active context contains only the minimum sufficient, current,
decision-relevant information required for the present stage. Task history,
raw evidence, large artifacts, completed reasoning, and superseded state do
not accumulate automatically in the Body.

## Activation and lifecycle

Recognize a leading `TT:` after optional blank lines as canonical. Recognize a
leading `OTP:` only as compatibility. Plain text does not activate Target Task.
`OTP:` followed by a `TT:` line is redundant and activates exactly once,
using the `TT:` payload. Record the trigger form as `TT:`, `OTP:`, or
`OTP:+TT:` and never infer activation
from task content or intent.

The provider-neutral lifecycle is:

1. Body records task identity, authority, scope, prohibitions, outputs,
   validation, and success criteria.
2. Brain performs one planning cycle. At most one replan is allowed after a
   material Body rejection; a second rejected plan ends as
   `TARGET_TASK_BLOCKED`.
3. Body checks and seals the accepted immutable plan by stable hash. It does
   not rewrite or semantically improve a defective plan.
4. Body dispatches bounded steps, validates returns, and integrates only
   accepted work.
5. Deterministic validation runs before the sealed review mode. The plan
   selects exactly one of `DETERMINISTIC_ONLY`, `SELF_REVIEW`, or
   `RUNSKEPTIC_REVIEW`; execution cannot substitute another mode.
6. Body rechecks the sealed plan hash. A mismatch ends as
   `TARGET_TASK_INTEGRITY_FAILURE`; otherwise it performs final acceptance and
   returns a compact terminal receipt.

## Body

The Body is a slim Lead/orchestrator. It maintains compact lifecycle state,
requests and accepts planning, seals plans, dispatches bounded workers,
performs authorized deterministic execution, validates structurally and
substantively, decides handoff sufficiency, retrieves focused evidence only
when required, maintains an incremental acceptance ledger, and reports the
terminal receipt.

The Body must not redo Brain planning without plan rejection, ingest all
referenced artifacts by default, inherit full worker reasoning or raw output,
retain every prior receipt verbatim, become an unrestricted general worker, or
claim runtime isolation without observable evidence.

The compact current-state record contains only Target Task identity,
sealed-plan identity, current step, global invariants, completed-step status,
accepted validated claims, deviations, unresolved blockers, artifact
references, and validation/review status. Raw logs and prior handoffs remain
external. The acceptance ledger records incremental accepted claims so final
review does not reconstruct execution from raw artifacts.

The complete Body field contract is `TARGET_TASK_ID`, `TASK_REFERENCE`,
`AUTHORITY_AND_GLOBAL_CONSTRAINTS`, `SEALED_PLAN_REFERENCE`, `SEALED_PLAN_HASH`,
`EXECUTION_MODE`, `OBSERVED_CONTEXT_STATUS`, `CURRENT_STEP`,
`COMPLETED_STEP_IDENTITIES`, `ACCEPTED_VALIDATED_CLAIMS`, `OPEN_FINDINGS`,
`OPEN_BLOCKERS`, `MATERIAL_DEVIATIONS`, `ARTIFACT_REFERENCES`,
`NEXT_AUTHORIZED_ACTION`, `VALIDATION_STATUS`, and `REVIEW_STATUS`. Full
source, broad diffs, raw logs, full reasoning, repeated task/plan text, and
unfiltered research are prohibited from normal Body state.

The independent runtime fields are `OBSERVED_CONTEXT_STATUS` (what the
runtime exposes) and `ISOLATION_REQUIRED` (what the task requires). Their
combination selects `ISOLATED_ORCHESTRATION`, `SHARED_CONTEXT_DEGRADED`, or
`ISOLATION_REQUIRED_BLOCKED`; artifact discipline never proves runtime
isolation.

## Brain and Acceptance Plan

The Brain plans only unless the accepted plan assigns one other bounded
reasoning role. It receives the Target Task, compact invariants, current
validated state, decision-relevant summaries, focused evidence, and references
to larger artifacts—not all raw execution material.

For every meaningful step the Acceptance Plan specifies: objective; direct
inputs; referenced inputs; scope and prohibitions; actions; outputs;
validation; handoff requirements; dependencies; authority; and retrieval or
escalation conditions. The Body validates identity, authorization,
executability, budgets, plan integrity, and these handoff requirements before
sealing. A bounded plan view is hash-bound and cannot silently change the
accepted plan's semantics.

## Bounded worker view

A worker receives only its sealed-plan step or hash-bound view, required global
invariants, current validated facts, constraints, relevant references,
success criteria, expected output, and required handoff. Boundary mediation is
conditional: deterministic mediation is preferred when safe. A Boundary Agent is not required
at every transition. See `agents/boundary-agent.md` for
its owned selection and truthfulness rules.

## Sufficient Handoff

Every material boundary crossing supplies these semantics, compactly:

```text
STATUS
WORK_PERFORMED
VALIDATED_FACTS
DECISION_RELEVANT_FINDINGS
LIMITATIONS
UNRESOLVED
ARTIFACT_REFERENCES
RETRIEVAL_GUIDANCE
READ_CONDITIONS
NEXT_AUTHORIZED_ACTION
```

The governing rule is: information may be omitted from active context only
when its omission cannot reasonably change the recipient's next authorized
action, validation obligation, or material risk judgment.

Distinguish worker-reported facts, directly observed facts, deterministically
validated facts, inferences, and unresolved claims. A sufficient handoff lets
the recipient safely continue, stop, validate, retrieve, replan, escalate, or
reject.

Before reading a substantial referenced artifact, the recipient independently
records either:

```text
HANDOFF_SUFFICIENT: YES
```

or:

```text
HANDOFF_SUFFICIENT: NO
MISSING: <validated information>
RETRIEVE: <focused reference or extraction>
REASON: <why the next action or risk judgment depends on it>
```

`READ_CONDITIONS` guides retrieval but never replaces this recipient check.

## Progressive focused retrieval and evidence preservation

Retrieval order is: compact handoff; artifact metadata or index; focused
search/extraction; narrow surrounding context; complete artifact only when
necessary. Use heading or identifier search, exact test-name search, symbol or
JSON-key lookup, line ranges, path/commit filters, or diff hunks. A reference
never requires whole-artifact reading.

Keep raw logs, source bundles, inventories, diffs, research, large worker
outputs, detailed analysis, and validation records outside active context when
persistence or reuse materially helps. Pass stable paths, hashes or
identifiers, compact summaries, and retrieval guidance. Keep tiny,
decision-critical instructions inline when indirection costs more.

## Context truthfulness and bookkeeping

Use exactly one observable status where applicable:
`FRESH_CONTEXT_CONFIRMED`, `PARENT_CONTEXT_INHERITED`, or
`CONTEXT_ISOLATION_UNKNOWN`. Explicit boundary processing limits transmitted
information but does not prove runtime isolation. When inherited or unknown,
minimize parent state and dispatches and make no stronger leakage claim.

## Durable checkpoint and resume

Persist a checkpoint after plan acceptance and every accepted material step.
It contains task, authority, plan reference/hash, execution/context status,
current step, completed-step evidence, accepted claims, findings, blockers,
deviations, artifact references, next authorized action, last validation, and
checkpoint version. Resume verifies task identity, plan identity/hash,
checkpoint structure/version, evidence, authorization, and integrity. A
mismatch stops with `TARGET_TASK_INTEGRITY_FAILURE`; accepted completed steps
are not silently repeated. The deterministic reference implementation is in
`harness/target_task_lifecycle.py`.

Protocol scratch state is permitted only when necessary, minimal, disclosed
when materially relevant, cleaned up when required, and compliant with every
explicit security, privacy, data-location, workspace, no-write, and
filesystem constraint. It is not silently an authorized deliverable. User
constraints may apply to all writes, not only deliverables.

## Review, statuses, and receipt

The sealed plan selects the final review mode. Deterministic validation must
precede review, and RunSkeptic receipts are validated under `skeptic.md`.
For this harness-defining task, RunSkeptic Fix Loop requires three
consecutive valid passes with no new meaningful findings; unchanged ceremonial
passes do not count.

Canonical terminal statuses are `TARGET_TASK_ACCEPTED`,
`TARGET_TASK_REJECTED`, `TARGET_TASK_BLOCKED`, and
`TARGET_TASK_INTEGRITY_FAILURE`. Compatibility `OTP_*` mappings live only in
the stub.

The compact receipt includes trigger form, Target Task identity, requested and
observed routing, planning-cycle count, sealed-plan identity, bounded
execution summary, context/handoff and retrieval summary, artifact
references, deterministic validation, review mode and RunSkeptic convergence,
deviations, blockers, final status, and repository/workspace state. Unknown
runtime facts remain `UNKNOWN`; raw evidence is never reproduced in the
receipt.

See `agents/lead-agent-prompt.md`, `agents/boundary-agent.md`,
`agents/agent-return.md`, and `agents/model-routing.md` for their owned
orchestration, boundary, return-envelope, and routing contracts. This file
does not require a Boundary Agent model call at every transition.
