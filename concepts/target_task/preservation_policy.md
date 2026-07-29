# Preservation Policy (Outcome G)

This policy documents what must be preserved when implementing compact reference handoff and rotation.

## Mandatory Preservations

### 1. Lead Terminal Ownership
- Lead remains the decision-making authority for Target Tasks
- Lead issues mandatory acceptance gate per agents/lead_agent.md
- Lead approval required before any plan execution
- No Planner or child agent can approve, execute, or claim terminal completion
- Preserved in: agents/lead_agent.md (no modification required)

### 2. Distinct Mandatory Planner
- Planner is a separate bounded role for every Target Task
- Planner receives reference-based dispatch (not inline expansion)
- Planner produces exactly one complete replacement Plan per dispatch
- No Planner recursion; child agent cannot dispatch another Planner
- Planner may not approve, execute, or claim DONE
- Preserved in: agents/planner.md (input/output sections may be clarified only)

### 3. Planner-Only Planning for Target Tasks
- Every executable plan version must be Planner-produced
- Lead-authored plans, same-runtime plans, or supplied drafts cannot substitute
- Material plan changes require new unique Planner repair dispatch and fresh review
- Preserved in: agents/lead_agent.md Target Task gate

### 4. RunSkeptic Review and Receipt Validation
- RunSkeptic review mandatory after Planner delivers plan
- RunSkeptic receipt must be validated and preserved
- Planner repair required after every material plan change
- Three consecutive passing RunSkeptic runs required before DONE
- Preserved in: agents/lead_agent.md, workflows/task_prompt.md

### 5. Independent Lead Acceptance
- Lead independently accepts or rejects plan based on RunSkeptic receipt
- Lead acceptance is source-of-truth for execution decision
- Acceptance binds to final unchanged plan identity and valid receipt
- No partial acceptance or conditional execution
- Preserved in: agents/lead_agent.md mandatory gate

### 6. Execution Exactly Once
- Each authorized action executed exactly once
- Execution ID registry prevents replay across rotations
- Checkpoint tracks exactly-once state
- Fresh resume validates no duplicate execution before continuing
- Preserved in: rotation_checkpoint.py, resume_validator.py

### 7. Agent Completion Envelope Validation
- All delegated work returns with Agent Completion Envelope
- Envelope validated before work is accepted
- Role-specific acceptance gates applied
- Preserved in: agents/lead_agent.md, workflows/task_prompt.md

### 8. ACTUAL_ROUTING_UNKNOWN When Hidden
- If actual runtime routing is hidden, report ACTUAL_ROUTING_UNKNOWN
- Do not infer actual routing from request or claimed model
- Report observed routing when directly observable
- Preserved in: agents/planner.md (instruction to report accurately)

### 9. Conditional Boundary Agent Policy
- Boundary Agent used only when expected context/error-risk reduction exceeds cost
- Not a wrapper around every delegation
- Direct compact delegation remains valid
- Preserved in: agents/boundary_agent.md (no modification)

### 10. Deterministic-First, Smallest-Reliable Routing
- Use deterministic work first, direct work second
- Smallest model and reasoning effort for bounded role
- Premium escalation requires pre-authorization with exact bounds
- Preserved in: agents/model_routing_policy.md (no modification)

### 11. Body State Metadata-Only Semantics
- Body state remains metadata-only (max 32,768 bytes)
- Artifact references to external evidence
- No embedding of full transcripts, logs, source, or diffs
- Focused-retrieval discipline maintained
- Preserved in: capabilities/body_state/body_state.md (no modification)

### 12. Repository Safety and Protected State
- No force push to main or candidate branches
- No deletion of branches or worktrees used for work
- No stash, reset, or clean of uncommitted work
- Untracked evidence remains in shared workspace
- No cleanup actions in this task (separate future task)
- Preserved in: Branch protection, git workflow discipline

## What Changes (Authorized Roots)

### concepts/target_task/ (NEW)
- artifact_reference.py: ArtifactReference schema + validation
- reference_contract.md: Contract documentation
- dispatch_ticket.py: DispatchTicket schema + validator
- planner_ticket_builder.py: Ticket construction helper
- dispatch_state.py: State machine + failed ID registry
- transport_failure_handler.py: Failure detection + redispatch
- rotation_checkpoint.py: Checkpoint schema
- rotation_policy.py: Context-pressure policy
- resume_validator.py: Resume validation
- return_envelope.py: CompactReturn schema

### tests/concepts/target_task/ (NEW)
- test_reference_contract.py: Tests categories 1-3
- test_dispatch_ticket.py: Tests categories 4-6
- test_transport_failure.py: Tests categories 7-8
- test_checkpoint_resume.py: Tests categories 9-13
- test_execution_return.py: Tests categories 14-17
- test_context_pressure_harness.py: Tests category 18 + negative probes
- test_preservation.py: Frozen-file + out-of-scope validation

### agents/lead_agent.md (MINIMAL UPDATE IF NEEDED)
- Reference contract section: clarify Target Task dispatch gate for reference-based handoff
- No new stages; only clarification of existing gate
- Preservation: Lead terminal ownership, mandatory Planner, acceptance, exactly-once

### agents/planner.md (MINIMAL UPDATE IF NEEDED)
- Input section: clarify receiving ArtifactReference-based dispatch
- Output section: clarify producing DispatchTicket or CompactReturn
- Preservation: Planner role boundaries, no recursion, no approval/execution/DONE

### workflows/task_prompt.md (MINIMAL UPDATE IF NEEDED)
- Target Tasks section: clarify handoff uses ArtifactReference + DispatchTicket
- Preservation: orchestration gate, Agent Completion Envelope requirement

### workflows/task_prompt_builder.md (OPTIONAL)
- If updated: reference planner_ticket_builder helper
- Document: compact dispatch ticket construction (reference-based semantics)
- Example: construction with large Task + manifest as external references

## What Does NOT Change (Frozen Roots)

### skeptic.md
- Reference implementation; frozen by task
- No modification; hash validation only

### capabilities/immutable_checkpoint/
- Existing atomic checkpoint creation + publication
- No logic modification; use existing capability
- No modification of implementation

### capabilities/body_state/
- Existing metadata-only Body state + artifact references
- No logic modification; use existing structures
- No modification of implementation

### agents/model_routing_policy.md
- Model routing and escalation policy
- No broaden into routing changes
- No modification

### agents/boundary_agent.md
- Boundary Agent conditional policy
- No broaden into boundary changes
- No modification

### benchmarks/
- Benchmark framework and discovery
- No broaden into benchmark redesign
- No modification

## Validation Checklist

- [ ] skeptic.md: hash verification only, no changes
- [ ] immutable_checkpoint/: use only, no changes
- [ ] body_state/: use only, no changes
- [ ] model_routing_policy.md: not modified
- [ ] boundary_agent.md: not modified
- [ ] benchmarks/: not modified
- [ ] All changes in concepts/target_task/ owned by Target Task
- [ ] All changes in tests/concepts/target_task/ owned by Target Task
- [ ] agents/lead_agent.md: reference contract clarification only (or no change)
- [ ] agents/planner.md: input/output clarification only (or no change)
- [ ] workflows/task_prompt.md: Target Tasks section clarification only (or no change)
- [ ] workflows/task_prompt_builder.md: optional reference to ticket builder (or no change)
- [ ] No changes outside authorized roots
- [ ] Frozen files unchanged (hash validation passed)
- [ ] Lead ownership preserved
- [ ] Planner role preserved
- [ ] RunSkeptic review preserved
- [ ] Exactly-once semantics preserved
- [ ] Boundary Agent policy preserved
- [ ] Routing policy preserved
