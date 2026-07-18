# Inbound Slice 3B Task Prompt — preserved as received (2026-07-18)

Classification: inbound task description, owner-supplied via chat,
uncorroborated by any repository artifact. This is the only surviving
reference to "Slice 3A", "Case 2", "R1", and the decision
"HANDLED — NO_PROMOTION". Preserved verbatim, including its original
truncation marker on the final line. The model-routing section was
superseded by an explicit owner instruction ("adapt to claude env") after
`MODEL_ROUTING_UNRESOLVED` was returned; the routing text below is the
original, unedited.

---

Task Prompt: Slice 3B — Recover Slice 3A Case 2 evidence and stabilize the next decision

Execute this Task Prompt exactly in a cloud-based Codex execution environment with access to the "saffih/skeptic" repository.

This is a Codex-only diagnostic workflow. Read the complete prompt before acting.

The frozen Slice 3A decision remains:

HANDLED — NO_PROMOTION

Do not reopen, rescore, weaken, or retroactively modify that decision.

This task does not implement an R1 candidate. It recovers the missing evidence, diagnoses the failure, and produces the bounded specification for whatever next action the evidence supports.

Execution header

Runtime and role routing

Lead / Architect

- Runtime: Codex cloud repository environment.
- Required model: "GPT-5.6 Sol".
- Required reasoning effort: "HIGH".
- Context status: "NOT CLEAN ROOM".
- Reason: the Lead must inspect repository history, prior evaluation evidence, contracts, candidate diffs, and conflicting causal explanations.
- Fallback: none.
- If the required Lead model or effort is unavailable, return:

MODEL_ROUTING_UNRESOLVED

Do not substitute Claude, another provider, a weaker reasoning mode, or an unspecified session default.

Evidence Inventory Worker

- Preferred model: "GPT-5.6 Terra".
- Effort: "MEDIUM".
- Context status: "NOT CLEAN ROOM".
- Purpose: bounded local-object and evidence-path inventory only.
- Permitted fallback: the smallest available Codex model at "MEDIUM" effort that can reliably inspect git objects and return the required receipt.
- Record the exact visible model, version, effort, and fallback actually used.
- Do not escalate to a stronger model merely because evidence is difficult to locate.

Independent Diagnostic Reviewer

- Required model: "GPT-5.6 Sol".
- Required effort: "HIGH".
- Context status: "CLEAN ROOM".
- Use a fresh protected context.
- The reviewer may see only the verified evidence packet, current runtime contracts, and the neutral review ticket.
- The reviewer must not see:
  - the Lead’s provisional diagnosis;
  - the prior proposed correction sentence;
  - earlier chat conclusions;
  - the preferred next action;
  - aggregate advocacy for baseline or candidate.
- Fallback: none.
- If genuine protected isolation is unavailable, record:

REVIEW_INDEPENDENCE_UNAVAILABLE

Continue the evidence and Lead diagnosis phases, but do not recommend a narrow R1 for execution. The permitted terminal recommendations then become:

- redesigned behavioral test;
- documentation/interface clarification requiring owner decision;
- or "CONFLICT".

Checker

Use deterministic commands and scripts for:

- git refs and object existence;
- commit, tree, and blob identities;
- file hashes;
- manifest completeness;
- diff scope;
- test execution;
- protected-file equivalence;
- final branch and worktree state.

A model statement is not a substitute for a Checker result.

Contract loading requirement

Before constructing or dispatching any child phase:

1. Read the current:
   - "AGENTS.md";
   - "skeptic.md";
   - "agents/lead-agent-prompt.md";
   - "agents/task-prompt.md".
2. Record their current commit/ref, Git blob, and SHA-256.
3. Apply the complete Dispatch Ticket and Agent Receipt contracts from "agents/task-prompt.md" for this Task Prompt.
4. Record that the companion files were loaded and applied.
5. If any required companion is unavailable, unreadable, materially incompatible, or cannot be identified as current, return "CONFLICT" before dispatch.

For this task, the full Task Prompt ticket and receipt schemas control delegated phases. A smaller compatible schema elsewhere may not remove required fields.

Mutation and publication authority

The pasted Task Prompt authorizes only:

- creation of one fresh isolated git worktree within the cloud environment;
- creation of one fresh local diagnostic branch;
- writes under:

plans/slice-3a-case2-diagnostic/

- local commits containing only the authorized diagnostic and evidence package.

It does not authorize:

- changes to production/runtime contracts;
- changes to tests or harness code;
- changes to prior evaluation artifacts;
- merge to "main";
- push;
- pull request creation;
- remote branch or tag creation;
- publication;
- PR comments;
- branch deletion;
- any other remote side effect.

No merge, push, PR, publication, or remote mutation is allowed.

Task mode

DIAGNOSTIC EVIDENCE RECOVERY AND DESIGN DECISION

This task is not:

- an R1 implementation;
- a new six-case A/B evaluation;
- a retroactive rescore;
- a production consolidation change;
- a rewrite of the frozen promotion rule;
- a general repository cleanup task.

Objective

Recover and verify the complete decision-critical Slice 3A Case 2 evidence from cloud-accessible git state, diagnose why the candidate failed to load and operationalize "agents/lead-agent-prompt.md", and decide the smallest properly evidenced next action.

The diagnosis must distinguish:

1. test-design weakness;
2. candidate-contract weakness;
3. Generator-following variance;
4. Judge interpretation or scoring-contract mismatch.

Do not assume the correction before examining the evidence.

Exact terminal DONE

"Overall DONE: yes" requires all of the following:

1. The current repository, remote base, worktree state, protected paths, and applicable contracts are verified and recorded.
2. The Slice 3A branch and commits are resolved from the cloud-accessible repository, or their absence is proved after the bounded recovery procedure.
3. Every required Case 2 artifact is recovered and identified by:
   - source commit;
   - source path;
   - Git blob where applicable;
   - byte size;
   - SHA-256;
   - evidence classification.
4. The raw evidence package contains, when present:
   - baseline Case 2 input and output;
   - candidate Case 2 input and output;
   - evaluation manifest;
   - frozen behavioral/scoring contract;
   - Judge packet;
   - Judge rationale and per-dimension scoring;
   - final RunSkeptic receipt;
   - terminal evidence or closure receipt;
   - relevant candidate diff and protected-file blobs.
5. Raw recovered evidence is copied byte-for-byte without silent editing.
6. Missing artifacts are explicitly listed with the exact searches performed and why recovery failed.
7. A two-part architecture map is produced:
   - runtime discovery and load order;
   - execution ownership and artifact/control flow.
8. A cross-file contract matrix identifies:
   - reader;
   - authority;
   - mandatory load condition;
   - delegation interface;
   - receipt interface;
   - fail-closed behavior;
   - duplicate or conflicting rules.
9. The causal diagnosis separates the four required cause classes and states:
   - evidence;
   - evidence level;
   - confidence;
   - disconfirming evidence;
   - unresolved unknowns.
10. The Lead chooses exactly one next disposition:
    - "NO_FURTHER_CHANGE";
    - "DOCUMENTATION_OR_INTERFACE_CORRECTION";
    - "NARROW_R1_CANDIDATE";
    - "REDESIGNED_BEHAVIORAL_TEST";
    - or "CONFLICT".
11. The selected disposition is supported by the evidence and does not depend on aggregate score alone.
12. A complete bounded specification is produced for the selected next disposition, but it is not executed.
13. The independent reviewer returns a protected receipt, or the lack of genuine independence is explicitly recorded and applied to the decision boundary.
14. RunSkeptic is completed against:
    - the diagnosis;
    - the selected disposition;
    - the next-action specification.
15. No unresolved "ACTION", "DECOMPOSE", "CONFLICT", review-required status, or blocking unknown is hidden behind a positive recommendation.
16. Protected production files remain byte-for-byte unchanged.
17. Only the authorized diagnostic directory is changed.
18. The evidence and diagnosis are committed locally on the fresh diagnostic branch within the cloud environment.
19. A complete Task Closure Receipt is persisted with concrete observed values, not forward references.

(remaining content unchanged)
