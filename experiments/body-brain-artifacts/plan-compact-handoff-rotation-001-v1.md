# Plan: Compact Reference Handoff Rotation (PLAN-COMPACT-HANDOFF-ROTATION-001-v1)

## Metadata

- PLAN_ID: PLAN-COMPACT-HANDOFF-ROTATION-001-v1
- PLAN_VERSION: 1
- TARGET_TASK_BINDING: TT-COMPACT-REFERENCE-HANDOFF-ROTATION-001
- TARGET_TASK_SHA256: d48f9ae34bbcdadc909a69c650d20d1805b782afc507a02dd22861985a9c3da8
- MANIFEST_SHA256: 03ef1d7d226e07f22e43666b56979f43d172ae8931e1da124bb189ab6362a47c
- PURPOSE: Implement provider-neutral compact reference mechanism for Target Task delegation
- OBJECTIVE: Enable bounded, reference-based agent handoff; support transport failure recovery, checkpoint rotation, and fresh-session resume
- CONSTRAINTS: ≤65,536 bytes plan; no placeholders; no Lead narrative; no modification of skeptic.md or existing capabilities; concept-owned changes only; exactly-once execution
- CREATED: 2026-07-29
- DISPATCH_ID: PLANNER-COMPACT-HANDOFF-ROTATION-002

## Acceptance Criteria (Target Task 18 Categories + Harness)

1. Large Target Task + evidence in Planner ticket within byte budget → reference/hash, not bodies
2. Planner validates reference access/hashes before planning
3. Missing/inaccessible/stale/mismatched references fail closed
4. Placeholder-bearing or truncated Plan rejected
5. Failed dispatch ID consumed; cannot be reused
6. Recovery uses new unique ID and one compact redispatch
7. Second same-class transport/context failure triggers rotation or conflict
8. Lead-authored substitute planning forbidden
9. Continuation checkpoint respects 32,768-byte cap
10. Checkpoint excludes transcripts, logs, diffs, source bundles, repeated text
11. Fresh resume validates task/Plan/checkpoint/artifact/repository/exactly-once before continuing
12. Fresh resume continues from next action without replaying accepted work
13. Stale remote/base or changed Plan blocks resume
14. Execution exactly-once protected across rotation
15. Compact returns preserve material blockers and retrieval guidance
16. Current Target Task, routing, envelope, focused-retrieval, Body-state tests remain green
17. Static documentation labeled as evidence, not hidden enforcement
18. Context-pressure harness simulates transport failures and rotation with observable budget tracking

## Implementation Sequence

### Phase 1: Reference Contract (Outcome A) - Verification: contract file + unit tests

**Step 1.1: Define Artifact Reference Schema**
- Path: `concepts/target_task/artifact_reference.py`
- Defines ArtifactReference: id, sha256, size_bytes, media_type, authority_class, path_or_uri, focused_retrieval_guidance, complete_read_required, complete_read_reason
- Validation: identity not empty, sha256 format, size≥0, authority_class in [reference_implementation, contract, checkpoint, evidence, generated], path_or_uri accessible or deferred-access noted
- Export: class and validator function
- Verification: unit test passes for valid refs, rejects invalid identity/sha256/authority

**Step 1.2: Reference Contract (Immutable)**
- Path: `concepts/target_task/reference_contract.md`
- Documents: artifact reference semantics, inline-vs-reference decision rules, focused retrieval guidance policy, read conditions, provider-neutral scope
- Embedded examples: task+manifest reference, checkpoint reference, completed-plan reference
- Verification: document review for internal consistency and alignment with Outcome A requirements

### Phase 2: Dispatch Ticket Schema (Outcome B) - Verification: schema file + ticket validation tests + construction helper

**Step 2.1: Dispatch Ticket Schema and Validator**
- Path: `concepts/target_task/dispatch_ticket.py`
- Defines DispatchTicket: dispatch_id, task_id, task_reference (ArtifactReference), evidence_manifest_reference (ArtifactReference), plan_reference (ArtifactReference or null), context_budget_bytes, expected_return_contract, validation_rules, terminal_conditions, objectives, constraints_list
- Constructor validates: id present + unique, task_reference valid + accessible, manifest_reference valid + accessible, all references are ArtifactReference not embedded bodies, no placeholder text
- Ticket size ≤8,192 bytes; validator rejects over-budget, missing/unverified references, embedded bodies, duplicate IDs
- Verification: unit tests for valid ticket construction, rejection of malformed/duplicate/oversized/missing-ref tickets

**Step 2.2: Planner Dispatch Ticket Construction Helper**
- Path: `concepts/target_task/planner_ticket_builder.py`
- Function: build_planner_ticket(dispatch_id, task_reference, manifest_reference, plan_reference=None, objectives, constraints, expected_return_contract) → DispatchTicket
- Validates all inputs, enforces reference-based semantics, returns compact ticket or raises ValueError with specific reason
- Verification: integration test with real target task reference and manifest reference

### Phase 3: Transport Failure Recovery (Outcome C) - Verification: state machine tests + single-redispatch enforcement

**Step 3.1: Dispatch State Machine and Failed ID Registry**
- Path: `concepts/target_task/dispatch_state.py`
- Enum: DispatchState = {PENDING, IN_PROGRESS, COMPLETED, FAILED, RECOVERED}
- FailedDispatchRegistry: tracks consumed failed IDs (id, timestamp, error_class, error_message, original_ticket_reference)
- Rules: failed ID cannot be reused; second same-class failure → rotation/conflict; one redispatch per failure instance
- Verification: unit tests for state transitions, registry persistence, duplicate-ID rejection

**Step 3.2: Transport Failure Detector and Redispatch**
- Path: `concepts/target_task/transport_failure_handler.py`
- Function: detect_transport_failure(error, original_ticket_reference) → bool
- Function: create_redispatch_ticket(original_ticket_reference, error_evidence_reference, next_dispatch_id) → DispatchTicket
- Rules: preserve correlated error evidence as ArtifactReference; issue unique new ID; validate new ticket; reject 2nd same-class failure by returning CONFLICT marker
- Verification: test redispatch with new ID, verify original ID marked consumed, test rotation trigger on 2nd failure

### Phase 4: Pre-Exhaustion Checkpoint (Outcome D) - Verification: checkpoint creation + size validation + content audit

**Step 4.1: Checkpoint Schema and Creation**
- Path: `concepts/target_task/rotation_checkpoint.py`
- Defines RotationCheckpoint: schema_version, task_id, task_reference (ArtifactReference), repo_base_sha, repo_current_sha, accepted_plan_reference (ArtifactReference), accepted_plan_version, current_step_id, completed_step_ids (list), validated_facts (list of {fact_text, evidence_reference}), accepted_delegated_work_ids (list), deviations_list (list), unresolved_blockers_list (list), artifact_references_list (list of ArtifactReference), routing_status, validation_status, review_status, next_authorized_action, exactly_once_state (id→timestamp map), checkpoint_sha256, checkpoint_created_timestamp
- Size cap: ≤32,768 UTF-8 bytes; validator rejects oversized, excludes raw transcripts/logs/diffs/source bundles/repeated task/plan/secrets
- Verification: unit test for checkpoint creation, size validation, content audit (no forbidden fields)

**Step 4.2: Context-Pressure Policy and Rotation Trigger**
- Path: `concepts/target_task/rotation_policy.py`
- Function: evaluate_context_reserve(current_token_usage, context_budget, minimum_reserve_percent=20) → (bool is_adequate, int reserve_bytes_remaining)
- Function: should_rotate(context_used, context_budget, phase) → bool (true if reserve <20% or material pressure detected)
- Trigger behavior: when context pressure detected → persist checkpoint → return ROTATION_REQUIRED → stop expansion → emit compact return
- Verification: unit tests for reserve calculation, rotation trigger at different pressure levels

### Phase 5: Fresh-Invocation Resume (Outcome E) - Verification: resume validation + exactly-once + state reconstruction

**Step 5.1: Resume Validator**
- Path: `concepts/target_task/resume_validator.py`
- Function: validate_resume(checkpoint_reference, checkpoint, task_reference, plan_reference) → (bool valid, list errors)
- Validates: checkpoint schema + size + hash match, task_reference current + accessible, plan_reference unchanged, repo base/current SHAs valid, no duplicate execution via exactly-once registry, artifact references current + accessible
- Rejects: stale base, missing evidence, changed accepted Plan, duplicate execution, inaccessible mandatory artifacts
- Verification: unit tests for each rejection case, acceptance of valid checkpoint

**Step 5.2: Resume Execution Handler**
- Path: `concepts/target_task/resume_executor.py`
- Function: resume_from_checkpoint(checkpoint, next_authorized_action) → (status, result_reference)
- Loads checkpoint, validates with Resume Validator, reconstructs state, skips completed accepted work, executes from NEXT_AUTHORIZED_ACTION
- Tracks: exactly-once state (maps action_id→timestamp to prevent replay)
- Verification: integration test showing resume skips completed steps and continues from next authorized action

### Phase 6: Compact Returns and Upward Reporting (Outcome F) - Verification: return envelope schema + blocker preservation tests

**Step 6.1: Compact Return Envelope Schema**
- Path: `concepts/target_task/return_envelope.py`
- Defines CompactReturn: status, dispatch_id, task_id, verdict, plan_reference (ArtifactReference or null), plan_sha256, checkpoint_reference (ArtifactReference or null), material_findings_list, unresolved_blockers_list, retrieval_guidance_list, validation_status, artifact_references_list (ArtifactReference for logs/diffs/plans)
- Size limit: compact return ≤4,096 bytes (bodies in referenced artifacts)
- Validator: rejects return that conceals material blocker, ensures blockers preserved
- Verification: unit tests for envelope creation, blocker preservation, rejection of incomplete returns

**Step 6.2: Return Construction Helper**
- Path: `concepts/target_task/return_builder.py`
- Function: build_compact_return(status, dispatch_id, task_id, verdict, findings, blockers, artifacts_references) → CompactReturn
- Validates: all blockers listed, all artifact references valid, no embedded bodies, total size ≤4,096
- Verification: integration test with real findings and blockers

### Phase 7: Preservation and Validation Rules (Outcome G) - Verification: policy audit + frozen-file tests + routing tests

**Step 7.1: Preservation Policy Document**
- Path: `concepts/target_task/preservation_policy.md`
- Documents: Lead terminal ownership, mandatory Planner, Planner-only planning, RunSkeptic review/receipt, Planner repair after Plan change, Lead acceptance, exactly-once semantics, Agent Completion Envelope validation, ACTUAL_ROUTING_UNKNOWN marker, conditional Boundary Agent, deterministic-first routing, Body state cap, focused-retrieval semantics, repository safety rules
- Verification: cross-reference to agents/lead_agent.md, agents/planner.md, workflows/task_prompt.md

**Step 7.2: Validation Anchor Tests**
- Path: `tests/concepts/target_task/test_preservation.py`
- Test: skeptic.md remains frozen (hash validation)
- Test: existing capability files unchanged (immutable_checkpoint, body_state hashes)
- Test: model routing policy not modified
- Test: boundary agent policy not modified
- Test: benchmark paths untouched
- Test: all change roots respect authorized limits
- Verification: all 5 preservation tests pass

### Phase 8: Deterministic Acceptance Test Suite (18 Categories) - Verification: all 18 tests pass + negative probes

**Step 8.1: Core Reference Contract Tests (Categories 1-3)**
- Path: `tests/concepts/target_task/test_reference_contract.py`
- Test 1: Large Task + Evidence in Planner ticket within 8KB → reference/hash not bodies
- Test 2: Planner validates reference access + hashes before planning
- Test 3: Missing/inaccessible/stale/mismatched refs fail closed (rejection list, not silent)
- Fixtures: synthetic large task (100KB), large evidence manifest (500KB), reference to each
- Verification: pytest passes all 3 tests

**Step 8.2: Dispatch Ticket Validation Tests (Categories 4-6)**
- Path: `tests/concepts/target_task/test_dispatch_ticket.py`
- Test 4: Placeholder-bearing or truncated apparent Plan rejected by validator
- Test 5: Failed dispatch ID consumed + cannot be reused
- Test 6: Recovery uses new unique ID + one compact redispatch
- Fixtures: malformed Plan with "...", oversize Plan, duplicate dispatch ID scenario
- Verification: pytest passes all 3 tests

**Step 8.3: Transport Failure and Rotation Tests (Categories 7-8)**
- Path: `tests/concepts/target_task/test_transport_failure.py`
- Test 7: Second same-class transport/context failure triggers rotation or conflict
- Test 8: Lead-authored substitute planning forbidden (no injection of alt Plan during recovery)
- Fixtures: simulated context-exhaustion error, simulated network transport error, detection/recovery flow
- Verification: pytest passes both tests

**Step 8.4: Checkpoint and Resume Tests (Categories 9-13)**
- Path: `tests/concepts/target_task/test_checkpoint_resume.py`
- Test 9: Continuation checkpoint respects 32,768-byte cap
- Test 10: Checkpoint excludes raw transcripts, logs, diffs, source bundles, repeated text
- Test 11: Fresh resume validates task/Plan/checkpoint/artifact/repository/exactly-once before continuing
- Test 12: Fresh resume continues from next action without replaying accepted work
- Test 13: Stale remote/base or changed accepted Plan blocks resume
- Fixtures: checkpoint with exactly-once registry, stale repo state, changed Plan reference
- Verification: pytest passes all 5 tests

**Step 8.5: Execution and Return Tests (Categories 14-17)**
- Path: `tests/concepts/target_task/test_execution_return.py`
- Test 14: Execution exactly-once protected across rotation
- Test 15: Compact returns preserve material blockers + retrieval guidance
- Test 16: Current Target Task, routing, envelope, focused-retrieval, Body-state tests remain green (regression)
- Test 17: Static documentation labeled as evidence, not hidden enforcement
- Fixtures: dual-rotation scenario, return with blockers/guidance, regression test baseline
- Verification: pytest passes all 4 tests

**Step 8.6: Harness and Negative Probes (Category 18)**
- Path: `tests/concepts/target_task/test_context_pressure_harness.py`
- Test 18: Context-pressure harness simulates transport failures and rotation with observable budget tracking
  - Subtest 18a: Simulate 80% context usage → checkpoint trigger before overflow
  - Subtest 18b: Simulate transport timeout → failed dispatch ID + redispatch with new ID
  - Subtest 18c: Simulate second transport timeout on redispatch → rotation/conflict marker
  - Subtest 18d: Simulate resume from checkpoint → skip completed, continue next action
  - Subtest 18e: Simulate stale repo base on resume → rejection + blocker report
  - Subtest 18f: Negative probe: placeholder Plan → rejection
  - Subtest 18g: Negative probe: oversized checkpoint → rejection
  - Subtest 18h: Negative probe: duplicate dispatch ID → rejection
- Fixtures: context tracking with observable usage counter, simulated failures, recovery outcomes
- Verification: pytest passes all 8 subtests

### Phase 9: Contract and Documentation Updates (Minimal) - Verification: review + cross-reference validation

**Step 9.1: Lead Agent Contract Update (if needed)**
- Path: `agents/lead_agent.md` (reference contract section only)
- If changes required: clarify Target Task Planner dispatch gate requirements for reference-based semantics
- If no changes needed: skip
- Verification: manual review that Target Task gate is compatible with DispatchTicket schema

**Step 9.2: Planner Contract Update (if needed)**
- Path: `agents/planner.md` (input/output sections only)
- If changes required: clarify input as ArtifactReference-based handoff; output as DispatchTicket or CompactReturn
- If no changes needed: skip
- Verification: manual review that input/output sections align with new schema

**Step 9.3: Task Prompt Update (if needed)**
- Path: `workflows/task_prompt.md` (Target Tasks section only)
- If changes required: clarify Target Task handoff uses ArtifactReference + DispatchTicket
- If no changes needed: skip
- Verification: manual review that Target Task orchestration section aligns with reference contract

**Step 9.4: Task Prompt Builder Update (if needed)**
- Path: `workflows/task_prompt_builder.md` (compact dispatch ticket construction only)
- If changes required: add reference to compact_ticket_builder helper
- If no changes needed: skip
- Verification: manual review

### Phase 10: Repository State Validation - Verification: git diff audit + test suite run + remote validation

**Step 10.1: Changed Path Audit**
- Run: `git diff --name-only main...HEAD`
- Expected paths: only in concepts/target_task/, tests/concepts/target_task/, and optionally minimal changes to agents/lead_agent.md / agents/planner.md / workflows/task_prompt.md / workflows/task_prompt_builder.md
- Expected: no changes to skeptic.md, capabilities/, agents/model_routing_policy.md, agents/boundary_agent.md, benchmarks/
- Verification: audit report confirms no out-of-scope changes

**Step 10.2: Test Suite Validation**
- Run: `pytest tests/concepts/target_task/ -v`
- Expected: all 18 acceptance test categories + harness pass
- Run: `pytest tests/ -v` (full suite)
- Expected: no regressions in existing Target Task, routing, envelope, Body-state tests (Category 16)
- Verification: test output shows all passes

**Step 10.3: Linting and Diff Check**
- Run: `git diff --check`
- Expected: no whitespace errors
- Verification: clean exit

**Step 10.4: Remote State Validation**
- Query: current main branch commit SHA and tree SHA from origin
- Expected: matches manifest value (remote_main_commit, remote_main_tree)
- Verification: remote state matches manifest

### Phase 11: Code Review and Final Validation - Verification: diff review + RunSkeptic 3-pass rule + blocker audit

**Step 11.1: Full Diff Review**
- Scope: all changes against frozen base (main)
- Expected: all changes trace directly to Outcomes A-G, no speculative code, no "future-proofing"
- Review checklist: size budgets respected (8KB tickets, 32KB checkpoints, 4KB returns), no placeholders, reference contract enforceable, recovery logic deterministic, exactly-once tracking correct, test coverage complete
- Verification: review notes + approval

**Step 11.2: Three Consecutive RunSkeptic Passes**
- Setup: commit all changes to candidate branch
- Run: `runSkeptic` (or equivalent) on unchanged commit/tree
- Repeat: 3 times
- Expected: all 3 runs pass with same verdict
- Verification: three RunSkeptic passes on same commit recorded

**Step 11.3: Terminal Blocker Audit**
- Audit: unresolved blockers list empty or all marked as known/acceptable
- Check: no material findings concealed in compact returns
- Verification: blocker audit clean

## Concept Ownership Mapping

### Concept: Artifact Reference (NEW)
- Owned by: Target Task (concepts/target_task)
- Authority: ArtifactReference class + validation
- Modified contracts: none required (reference-based handoff integrates into existing Lead/Planner/Prompt contract)

### Concept: Dispatch Ticket (NEW)
- Owned by: Target Task (concepts/target_task)
- Authority: DispatchTicket class + DispatchTicketValidator
- Modified contracts: Planner (input/output) if clarification needed

### Concept: Transport Failure Recovery (NEW)
- Owned by: Target Task (concepts/target_task)
- Authority: DispatchState, FailedDispatchRegistry, TransportFailureHandler
- Modified contracts: none required (integrates into Planner's dispatch loop)

### Concept: Rotation Checkpoint (NEW)
- Owned by: Target Task (concepts/target_task)
- Authority: RotationCheckpoint class + checkpoint schema
- Existing: immutable_checkpoint capability provides atomic creation/publication (no modification)
- Modified contracts: Lead (Planner gate) if checkpoint trigger clarification needed

### Concept: Resume Validator (NEW)
- Owned by: Target Task (concepts/target_task)
- Authority: ResumeValidator + ResumeExecutor
- Modified contracts: none required (integrates into fresh Lead invocation)

### Concept: Compact Return (NEW)
- Owned by: Target Task (concepts/target_task)
- Authority: CompactReturn class + validation
- Modified contracts: Planner (output) if clarification needed

### Concept: Preservation Policy (NEW)
- Owned by: Target Task (concepts/target_task)
- Authority: preservation_policy.md document
- Modified contracts: none (references existing Lead/Planner/RunSkeptic contracts)

## Context-Pressure Harness Design

### Harness Components

**Budget Tracker**
- Maintains: current_token_usage (incremental counter), context_budget, minimum_reserve_percent
- Observable output: budget_tracking_log (timestamp, token_used, reserve_remaining_pct)
- Trigger: when reserve drops below threshold → rotation policy evaluates and may emit ROTATION_REQUIRED

**Failure Simulator**
- Injects: context-exhaustion error (model refuses next token)
- Injects: transport timeout (network error during model response)
- Injects: connection loss during dispatch send
- Each failure captured as DispatchTransportFailure with timestamp, error_class, correlated original_ticket_reference

**State Machine Monitor**
- Observes: DispatchState transitions (PENDING → IN_PROGRESS → COMPLETED | FAILED | RECOVERED)
- Observes: FailedDispatchRegistry updates (failed ID recorded, reuse rejected)
- Observes: rotation trigger (ROTATION_REQUIRED emitted, checkpoint persisted)

**Recovery Workflow Monitor**
- Observes: DispatchTicket construction for redispatch (new unique ID, original error ref, one redispatch per failure)
- Observes: checkpoint validation on resume (schema, size, hashes, exactly-once)
- Observes: execution resume (skip completed, continue next)

### Harness Execution Flow

1. **Setup**: Create context tracker (budget=200,000 tokens, reserve_threshold=20%)
2. **Baseline**: Run Task Phase with token tracking → observe checkpoint trigger at 80% usage
3. **Transport Failure Injection 1**: Simulate error mid-dispatch → observe recovery flow (new ID, redispatch)
4. **Transport Failure Injection 2**: Simulate error on redispatch → observe rotation trigger (ROTATION_REQUIRED)
5. **Checkpoint Persistence**: Verify checkpoint written, size ≤32KB, content audit pass
6. **Fresh Resume**: Load checkpoint, validate, continue from next authorized action → observe skipped completed steps
7. **Stale Base Rejection**: Modify repo base SHA in checkpoint → resume validation rejects with blocker
8. **Negative Probes**: Try placeholder Plan (rejected), oversized checkpoint (rejected), duplicate ID (rejected)

### Observable Outputs

- `budget_tracking.log`: token usage by phase, rotation point, reserve remaining
- `transport_failures.log`: each injected failure, error_class, redispatch ID, recovery status
- `checkpoint_states.log`: each checkpoint created/validated/loaded, size, exactly-once count
- `test_harness_summary.json`: phases passed/failed, rotation count, resume count, negative probe results

## Unknown Treatment

**If reference contract ambiguities emerge during implementation:**
- Resolve via targeted unit test defining the specific semantics
- Document decision in reference_contract.md with rationale
- Re-verify acceptance tests cover the resolved case
- No blocking escalation unless contract conflicts with frozen Lead/Planner contracts

**If checkpoint size approaches 32KB cap:**
- Audit checkpoint contents for duplication (fact + evidence ref should not duplicate)
- Eliminate purely internal state not needed for resume (transient tracking)
- If still oversized: return CONFLICT with specific content that exceeds limit and guidance for restructuring

**If transport failure classification uncertain (same-class vs. new-class):**
- Define: same-class = same error_class string (e.g., "context_exhaustion", "network_timeout")
- Different error_class strings trigger new dispatch, not rotation on second occurrence
- Document in dispatch_state.py

**If exactly-once tracking conflict (action replayed despite registry):**
- Implementation must reject execution if (action_id, timestamp_range) already recorded
- If rejection fails: return CONFLICT with exactly-once violation evidence

## Stop Conditions

**STOP and return CONFLICT if:**
- Dispatch ticket size exceeds 8,192 bytes
- Checkpoint size exceeds 32,768 bytes
- Compact return exceeds 4,096 bytes and contains material blocker
- Any reference fails hash validation on read
- Placeholder text ("...", "markdown", "omitted", etc.) found in final Plan
- Failed dispatch ID reused in same recovery sequence
- Second same-class transport failure occurs and rotation cannot proceed (context exhausted)
- Exactly-once execution violated (same action_id+timestamp range detected on resume)
- Changed accepted Plan reference after checkpoint creation (Plan hash mismatch)
- Stale remote base (main branch moved, candidate cannot fast-forward)
- Any existing capability modified (immutable_checkpoint or body_state)
- Any frozen file modified (skeptic.md)
- Changed path outside authorized change roots
- RunSkeptic fails 2 consecutive times on same commit
- Material blocker concealed in compact return

**STOP and return DONE if (all below true):**
- Base remains exact parent (no new commits on main during task)
- Candidate is one commit ahead, zero behind main
- Changed paths match accepted Plan exactly
- All 18 deterministic acceptance tests pass
- Context-pressure harness passes all 8 subtests
- Three consecutive RunSkeptic passes on unchanged commit
- Remote branch SHA/tree match manifest values
- No material unresolved blocker
- Remote main fast-forward successful (if push required)
- Preservation audit passes (no frozen files modified, no out-of-scope changes)

## Task Prompt Builder Integration (if needed)

If workflow/task_prompt_builder.md requires update:
- Export: planner_ticket_builder.build_planner_ticket function reference
- Document: compact dispatch ticket construction semantics (reference-based, no embedded bodies)
- Example: show construction of ticket for large Target Task with external reference to task + manifest

## Key Decisions

1. **Reference Format**: ArtifactReference is a simple dataclass (not nested in other structures) to remain provider-neutral and serializable.

2. **Single Redispatch Rule**: One recovery per transport failure prevents infinite redispatch loops; second same-class failure requires rotation (fresh Lead invocation) or CONFLICT.

3. **Checkpoint ≤32KB**: Tight size cap forces focused content (facts + evidence refs) rather than embedding full transcripts; aligns with existing body_state capability limits.

4. **Exactly-Once via Registry**: DispatchID + action_id + timestamp triple in registry prevents replay; survives checkpoint serialization/deserialization.

5. **Lead Terminal Ownership**: Preservation policy documents that Lead remains decision-making authority; Planner produces Plan only; RunSkeptic validates; Lead accepts; all durable.

6. **Observable Budget Tracking**: Harness budget_tracking.log allows external validation that context-pressure policy triggered correctly at thresholds.

7. **No Inline Bodies in Tickets**: DispatchTicket enforces ArtifactReference for Task, Manifest, Plan; receiver fetches only what next action requires.

8. **Negative Probe Coverage**: Harness explicitly tests failure modes (oversized, stale, duplicate, placeholder) to ensure guardrails work.

## Implementation Order Rationale

**Phase 1-2 (Reference Contract + Dispatch Ticket)** first: These are foundational; all other phases depend on them.

**Phase 3 (Transport Failure)** before Phase 4: Recovery logic needed before checkpoint creation can be tested.

**Phase 4-5 (Checkpoint + Resume)** after recovery: Checkpoint state machine and resume logic build on dispatch states.

**Phase 6 (Compact Returns)** after all outcomes: Return envelope defined after all work types (reference, dispatch, recovery, checkpoint) are understood.

**Phase 7 (Preservation)** alongside all phases: Frozen-file validation and policy audit run continuously.

**Phase 8 (Test Suite)** after all code: Tests written last to validate complete integrated behavior.

**Phases 9-11 (Contracts + Review + Validation)** last: Minimal contract updates only after implementation stabilized.

## Success Metrics

- All 18 acceptance test categories pass
- All 8 harness subtests pass
- No frozen files modified (skeptic.md, capabilities/)
- No out-of-scope paths changed
- 3 consecutive RunSkeptic passes on same commit
- Compact ticket <8KB for large Task (100KB+)
- Checkpoint <32KB with full exactly-once tracking
- Compact return ≤4KB with all blockers listed
- Fresh resume skips completed steps, continues next
- Transport failure recovery uses new unique ID
- Second same-class failure triggers rotation/conflict
