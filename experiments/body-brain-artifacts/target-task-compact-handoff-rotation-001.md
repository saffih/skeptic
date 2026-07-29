# TT-COMPACT-REFERENCE-HANDOFF-ROTATION-001

## Purpose

Implement and integrate the missing provider-neutral mechanism that keeps Target Task delegation and continuation compact:

1. substantial task/evidence content crosses agent boundaries by validated references and hashes rather than by automatic inline expansion;
2. Planner and other agent dispatch tickets remain bounded and compact;
3. transport/context-size failures cause bounded reference-based redispatch, never a Lead-authored substitute plan;
4. the persistent Lead/Body checkpoints before usable context is exhausted and resumes in a fresh invocation from a compact validated continuation record;
5. the mechanism is exercised by deterministic tests and a context-pressure harness reproducing the failure class observed in the previous Claude run.

This task fixes the handoff/rotation architecture only. Repository cleanup, branch deletion, worktree removal, experiment disposal, and cleanup-report execution are explicitly out of scope and remain the next separate task.

## Required Implementation Outcomes

### A. COMPACT REFERENCE CONTRACT

Implement one concept-owned, provider-neutral contract for substantial cross-agent context.

A valid artifact reference must carry enough information to verify:
- identity
- accessibility
- integrity
- authority/source-of-truth class
- size
- media/schema type
- focused retrieval guidance
- read conditions
- whether complete reading is required

Required rules:
- small decision-critical instructions may remain inline
- substantial, reusable, already-persisted, or boundary-surviving material must be referenced
- a sender must not automatically expand a reference into the receiving prompt
- a receiver starts from the compact handoff or manifest and retrieves only the focused evidence required for its next authorized action
- a complete-artifact read requires a recorded reason
- reference presence alone does not prove access, integrity, sufficiency, or correctness

Do not impose one universal filesystem layout or provider-specific artifact API. The invoking runtime chooses an authorized shared location.

### B. COMPACT DISPATCH TICKET

Define and enforce a compact dispatch schema for Planner and other bounded model-agent roles. It must include identity, objective, authority, references, expected return, validation, and stop conditions without repeating source bodies.

Provide deterministic ticket construction and validation where the repository's current architecture supports executable helpers. Otherwise provide the smallest deterministic harness that proves the contract.

The validator must reject:
- ticket over budget
- missing dispatch ID
- missing Target Task or evidence-manifest identity
- unverified or inaccessible required reference
- embedded full artifacts where a reference is required
- duplicate dispatch ID
- missing return/acceptance contract
- instructions that let the child self-approve or claim task-level completion

### C. TRANSPORT/CONTEXT FAILURE RECOVERY

Implement the following state transition:
```
dispatch transport/context failure
-> preserve correlated error evidence
-> mark dispatch ID consumed and failed
-> verify referenced artifacts remain current and accessible
-> issue one compact redispatch with a new unique ID
-> validate the new envelope and Plan
```

Rules:
- do not generate a Lead-authored substitute Plan
- do not replay completed broad preflight when the manifest remains valid
- do not inline more content as the recovery strategy
- do not increase model effort merely because transport failed
- allow at most one repaired redispatch for the same failure instance
- a second same-class failure triggers pre-exhaustion checkpoint and fresh-session rotation when safe, otherwise `CONFLICT`
- partial, placeholder-bearing, truncated, or uncorrelated output is never a Plan

### D. PRE-EXHAUSTION LEAD/BODY CHECKPOINT

Implement a provider-neutral context-pressure policy.

Before starting another expansion-heavy phase or dispatch, the Lead/Body must evaluate whether enough reserve remains for final review/repair/validation/integration/checkpoint/reporting.

When the reserve is inadequate or context pressure becomes material:
1. stop new context expansion
2. persist and verify completed evidence
3. create a compact continuation checkpoint
4. return `ROTATION_REQUIRED`
5. continue only in a fresh Lead/Body invocation

The checkpoint must be no larger than 32,768 UTF-8 bytes and contain only:
- schema version
- Target Task ID and immutable task reference/hash
- repository/base/candidate identity
- accepted Plan reference/hash/version
- current step
- completed step IDs
- validated facts and their evidence references
- accepted delegated-work identities
- deviations
- unresolved blockers
- artifact references and retrieval guidance
- routing/context status
- validation and review status
- next authorized action
- exactly-once execution state
- checkpoint hash and creation time

It must exclude: raw transcripts, logs, diffs, source bundles, repeated task/plan text, secrets.

### E. FRESH-INVOCATION RESUME

A fresh Lead/Body resume must:
1. read only the compact checkpoint first
2. validate its schema, size, hash, task binding, Plan binding, artifact access
3. revalidate current repository/remote state required by the next action
4. reject stale base, missing evidence, changed accepted Plan, duplicate execution, or inaccessible mandatory artifacts
5. use focused retrieval for missing decision-relevant evidence
6. continue from `NEXT_AUTHORIZED_ACTION`
7. avoid recomputing completed accepted work

The old invocation must not continue execution after emitting `ROTATION_REQUIRED`.

### F. COMPACT RETURNS AND UPWARD REPORTING

Substantial Plans, reviews, logs, diffs, validation records remain artifacts. Conversation and parent-agent returns carry compact envelopes, hashes, status, material findings, blockers, and retrieval guidance.

A compact return must never conceal a material unresolved issue. Compression is not permission to omit information that could change validation duty or risk judgment.

### G. PRESERVATION

Preserve:
- the global Lead's terminal ownership
- the distinct mandatory Planner
- Planner-only plan authorship for Target Tasks
- source-bound RunSkeptic review and receipt validation
- Planner repair after every material Plan change
- independent Lead acceptance
- execution exactly once
- Agent Completion Envelope validation followed by work acceptance
- `ACTUAL_ROUTING_UNKNOWN` when actual routing is hidden
- current conditional Boundary Agent policy
- deterministic-first, smallest-reliable routing
- current Body state cap and focused-retrieval semantics
- repository safety, protected checkouts, worktrees, branches, untracked evidence, cleanup artifacts

Do not modify `skeptic.md`.

## Concept Ownership and Change Scope

Changes may touch only:
- current Lead/Planner/Task Prompt/Task-Prompt Builder contracts where necessary
- current concept-owned Target Task handoff, state, checkpoint, rotation, receipt, or repository-adapter components
- directly applicable deterministic helpers/harnesses
- directly applicable tests and fixtures
- minimal documentation owned by those concepts

Do not revive deprecated paths. Do not broaden into model routing, Skeptic redesign, or unrelated architecture.

## Deterministic Acceptance Tests

Add or strengthen tests that prove:
1. A large Target Task and large repository evidence produce a Planner ticket within byte budget
2. The ticket contains references/hashes, not full bodies
3. The Planner validates reference access and hashes before planning
4. Missing/inaccessible/stale/mismatched references fail closed
5. Placeholder-bearing or truncated apparent Plan is rejected
6. Failed dispatch ID is consumed and cannot be reused
7. Recovery uses a new unique ID and one compact redispatch
8. A second same-class transport/context failure triggers rotation or conflict
9. Lead-authored substitute planning remains forbidden
10. Continuation checkpoint respects 32,768-byte cap
11. Checkpoint excludes raw transcripts, logs, diffs, source bundles, repeated text
12. Fresh resume validates task/Plan/checkpoint/artifact/repository/exactly-once before continuing
13. Fresh resume continues from next action without replaying accepted work
14. Stale remote/base or changed accepted Plan blocks resume
15. Execution exactly once remains protected across rotation
16. Compact returns preserve material blockers and retrieval guidance
17. Current Target Task, routing, envelope, focused-retrieval, Body-state tests remain green
18. Static documentation is labeled as evidence, not hidden enforcement

## Validation Sequence

1. Focused new unit/contract tests
2. Current Target Task context/state/handoff/routing tests
3. Planner, Task Prompt, Task-Prompt Builder, Agent Completion Envelope, exactly-once tests
4. Deterministic context-pressure/rotation harness
5. Negative probes (stale refs, mismatch, duplicate, placeholder, oversize, second-failure)
6. `git diff --check`
7. Changed-path and concept-ownership audit
8. Full repository test suite
9. Final full diff review against frozen base
10. Final implementation/result-level RunSkeptic Fix Loop until three consecutive passing runs on unchanged commit/tree

## Terminal Conditions

Return `DONE` only when:
- base remains exact parent
- candidate is one commit ahead, zero behind
- changed paths match accepted Plan
- all deterministic validation passes
- final three unchanged RunSkeptic passes qualify
- remote branch SHA/tree match
- no blocker or unresolved material unknown remains
- remote `main` fast-forward successful

Otherwise return `CONFLICT` with exact blocker and durable continuation references.

## Terminal Receipt

Return compact receipt with: verdict, task/base/candidate IDs, routing, validation passes, Plan acceptance, implementation details, checkpoint status, rotation validation, test results, remote match, cleanup status, unresolved blockers.
