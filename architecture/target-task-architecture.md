# Target Task architecture

Status: approved repository architecture; canonical design for Target Task.

This document is the source of truth for the intended Target Task design. The
protocol files implement or summarize it and must not silently contradict it.
`TT:` is canonical; `OTP:` is a compatibility alias only.

## 1. Goal

Target Task completes substantial, multi-stage work while keeping the
persistent Lead Agent, the **Body**, small, correct, stable, and able to
continue. Large reasoning and evidence live in bounded agents and durable
artifacts. The Body retains only compact, validated control state and the
references needed to choose and authorize the next action. The Body is the
continuity and control layer, not the main intelligence of the system.

## 2. Primary values

### Correct context

Correct context is the first priority. The Body preserves every fact,
constraint, uncertainty, contradiction, dependency, authorization boundary,
and validation obligation that could materially affect the next action,
continuation, retrieval, acceptance, or risk judgment.

Information may be omitted from active context only when its omission cannot
reasonably change the recipient's next authorized action, validation
obligation, stop decision, or material risk judgment.

### A slim Body

The Body normally retains only:

```text
TARGET_TASK_ID
TASK_REFERENCE
AUTHORITY_AND_GLOBAL_CONSTRAINTS
SEALED_PLAN_REFERENCE
SEALED_PLAN_HASH
EXECUTION_MODE
OBSERVED_CONTEXT_STATUS
CURRENT_STEP
COMPLETED_STEP_IDENTITIES
ACCEPTED_VALIDATED_CLAIMS
OPEN_FINDINGS
OPEN_BLOCKERS
MATERIAL_DEVIATIONS
ARTIFACT_REFERENCES
NEXT_AUTHORIZED_ACTION
VALIDATION_STATUS
REVIEW_STATUS
```

It does not normally retain full source files, broad diffs, raw logs, full
worker outputs or reasoning, repeated task/plan text, all prior handoffs,
unfiltered research, or broad tool output. A small decision-critical excerpt
may remain inline only when repeated retrieval would cost more or create more
correctness risk. This is a narrow exception, not cumulative storage.

In contract notation, the normally prohibited payloads are
`FULL_SOURCE_FILES`, `BROAD_DIFFS`, `RAW_LOGS`, `FULL_WORKER_OUTPUTS`,
`WORKER_REASONING_TRANSCRIPTS`, `FULL_BRAIN_REASONING`, `REPEATED_TASK_TEXT`,
`REPEATED_PLAN_TEXT`, `ALL_PRIOR_HANDOFFS`, `UNFILTERED_RESEARCH`, and
`BROAD_TOOL_OUTPUT`.

### Context-growth invariant

Small justified additions of new decision-critical state are permitted.
Completed detail must be externalized or replaced by validated compact state;
raw output must not accumulate; and repeated stages must not cause roughly
linear Body growth. Unexpected cumulative growth triggers a boundary and
state-management diagnosis. The protocol makes no exact token-size claim
unless the runtime exposes reliable measurements.

### No reasoning reconstruction

The Body is never required to reconstruct prior reasoning. Reasoning no longer
active is retrieved from a referenced artifact or assigned to a bounded
reasoning role. A compressed summary may guide retrieval but cannot replace
the missing analysis.

## 3. Roles

### Body

The Body owns task identity and authority, compact lifecycle state, runtime
mode selection, plan acceptance/rejection/sealing, integrity verification,
bounded dispatch, structural return validation, explicitly specified
deterministic operations, accepted-claims updates, checkpoint persistence and
resume, next-action authorization, and terminal acceptance.

It may check repository state, resolve known paths/commits, hash a plan, invoke
named tests, check envelopes, compare expected and observed values, and apply
specified mechanical changes. It must not perform substantial planning,
open-ended diagnosis, architecture design, broad research/exploration,
multi-source synthesis, raw-output interpretation, semantic plan repair, or
unbounded final review; it dispatches those roles instead.

### Brain

The Brain owns substantive planning. It receives the task/reference, authority
and global constraints, necessary source references, validated facts, unknowns,
and context-status limitations. It produces one Acceptance Plan containing
identity, objective/DONE, scope/prohibitions, source-of-truth order,
assumptions/unknowns, ordered steps, inputs, worker authority, outputs,
validation, handoffs, dependencies, stop conditions, retrieval/escalation,
review mode, and success criteria. It is not the execution owner.

### Worker

A Worker owns one bounded step or explicitly bounded reasoning role. It
receives the step identity, hash-bound plan view, constraints, validated facts,
input references, expected outputs, validation, handoff schema, and stop
conditions. Substantial output is written to authorized artifacts, not copied
wholesale into the Body.

### Boundary processing

Boundary processing protects the receiver from unnecessary, unvalidated, or
excessively large material. It is required when a return is not already a
valid compact Sufficient Handoff, but is not always a separate model call.
Deterministic processing is used for mechanical extraction, hashing, limiting,
schema validation, metadata, or fixed ranges. A reasoning Boundary Agent is
used when judgment is needed to preserve contradictions, classify claims, or
compress meaning without changing it. It never silently promotes a worker
report to fact.

Every material claim is classified as `WORKER_REPORTED`, `DIRECTLY_OBSERVED`,
`DETERMINISTICALLY_VALIDATED`, `INFERRED`, or `UNRESOLVED`. Only accepted,
appropriately validated claims enter the Body ledger.

## 4. Information flow

```text
User authority and Target Task -> Body compact state -> Brain plan
-> Body accepts/seals -> bounded step -> Worker references/artifacts
-> Boundary processing -> compact Sufficient Handoff
-> Body validates/updates -> next bounded step
```

Large information moves into temporary contexts and artifacts, not unfiltered
back into the Body.

## 5. References before copied material

The default transfer is a path, repository/commit, hash, test, symbol,
heading, line/byte range, source classification, compact validated claim,
limitation, and retrieval condition. A reference establishes existence, not
truth; the recipient distinguishes worker claims, observation, deterministic
validation, inference, and unresolved status.

## 6. Sufficient Handoff

Every material boundary crossing contains:

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

A handoff is sufficient only when the receiver can safely continue, validate,
retrieve, stop, reject, replan, or escalate. Otherwise it records
`HANDOFF_SUFFICIENT: NO`, the specific missing information, focused retrieval,
and why the next decision depends on it. Retrieval order is compact handoff,
metadata/index, focused extraction, narrow surrounding context, then complete
artifact only when necessary.

## 7. Source of truth

Unless a task specifies a stricter valid order, continuation uses:

1. explicit user authority and constraints;
2. sealed Acceptance Plan;
3. verified durable checkpoint;
4. accepted validated-claims ledger;
5. valid Sufficient Handoffs;
6. referenced authoritative artifacts;
7. unvalidated worker reports and inferences.

A lower-authority source cannot silently override a higher one. Contradictions
are preserved and resolved by validation, retrieval, rejection, or replanning.

## 8. Plan acceptance and sealing

The Body checks identity, authority, objective/DONE, scope/prohibitions,
source-of-truth order, executability, dependencies, outputs, validation,
handoffs, stop conditions, review mode, and success criteria. It may reject a
material defect but must not semantically repair it. An accepted plan is stored
at a stable reference with a content hash and is immutable; bounded views remain
traceable. An integrity mismatch blocks continuation.

## 9. Runtime context and execution mode

Observed context status is exactly one of `FRESH_CONTEXT_CONFIRMED`,
`PARENT_CONTEXT_INHERITED`, or `CONTEXT_ISOLATION_UNKNOWN`; it is never
inferred from a small handoff. Isolation requirement is independently
`ISOLATION_OPTIONAL` or `ISOLATION_REQUIRED`.

Use `ISOLATED_ORCHESTRATION` when fresh context is confirmed. Use
`SHARED_CONTEXT_DEGRADED` when context is inherited or unknown and isolation is
optional: acknowledge that the transcript cannot be removed, compact early,
minimize inline content, externalize material, and make no isolation claim.
Use `ISOLATION_REQUIRED_BLOCKED` when required isolation cannot be confirmed.
Task completion, isolation, and containment evidence are reported separately.

## 10. Durable checkpoint and resume

A checkpoint is required across interruption, delegation, context loss,
cross-session continuation, independent review, or a material execution
boundary. It contains task/reference/authority, plan reference and hash,
execution/context status, current step, completed steps and evidence, accepted
claims, findings, blockers, deviations, artifact references, next action, last
validation, and checkpoint version.

After plan acceptance and every accepted material step, the Body persists a
checkpoint. Resume verifies task identity, plan hash, checkpoint structure and
version, completed-step evidence, authorization of the next action, and absence
of blocking integrity failures. Mismatch stops precisely; accepted steps are
not silently rerun.

## 11. Acceptance semantics

The terminal receipt reports separately:

```text
TASK_RESULT
PLAN_INTEGRITY
DETERMINISTIC_VALIDATION
REVIEW_RESULT
EXECUTION_MODE
OBSERVED_CONTEXT_STATUS
BOUNDARY_PROCESSING_STATUS
CHECKPOINT_AND_RESUME_STATUS
CONTEXT_CONTAINMENT_EVIDENCE
ACTUAL_RUNTIME_ISOLATION
ACTUAL_CONTEXT_REDUCTION
BLOCKERS
```

For example, a completed task may truthfully report
`TASK_RESULT: ACCEPTED`, `EXECUTION_MODE: SHARED_CONTEXT_DEGRADED`,
`ACTUAL_RUNTIME_ISOLATION: UNKNOWN`, and
`ACTUAL_CONTEXT_REDUCTION: NOT_CLAIMED`.

## 12. Testable DONE

The architecture repair is complete when canonical `TT:`/compatibility `OTP:`
routing, stable architecture ownership, explicit Body boundaries, provenance,
degraded/blocked context modes, durable checkpoint/resume, integrity mismatch
stops, non-repetition, externalized output, focused retrieval, bounded-state
growth, truthful receipts, preserved existing contracts, focused/full tests,
an interruption/resume exercise, and an actual boundary exercise are all
evidenced. No unresolved action, conflict, decomposition path, review-required
status, or blocking unknown remains before promotion.

## 13. Repair sequence

Implement in reversible slices: persist and align ownership; add context modes;
add checkpoint/resume; add boundary transport and provenance; add behavioral
validation; then consider splitting `agents/target-task.md` only if measured
loading-surface evidence shows a clear benefit and ownership remains explicit.

## 14. Ultimate success criterion

The Brain may think deeply, workers may read extensively, artifacts may grow,
and reviewers may analyze broadly. The Body retains only the owned task,
immutable plan identity, current position, accepted validated facts, open risks
and blockers, evidence references, and next authorized action. No additional
material enters the Body unless the next decision genuinely requires it.
