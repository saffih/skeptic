# Receipt Authority Consolidation Plan

Repository: `saffih/skeptic`  
Planning base: current `main` observed at `e2fa2a985a683c6eb2a97ce13543461ba792ed49`  
Mode: `DESIGN_PACKAGE`  
Purpose: make receipts simpler and more trustworthy without adding a receipt system.

## 1. Problem

The repository has several useful receipt types, but their authority is not stated consistently enough.

Current strengths:

- Agent Receipt claims must be verified before promotion.
- decision-critical evidence must be durable;
- accepted checkpoints support resume and prevent replay;
- missing receipt fields do not invalidate completed substantive work;
- Task Closure Receipts enumerate terminal conditions.

Remaining ambiguity:

- a receipt can sound like proof even when it is only an agent claim;
- “Task Closure Receipt proves” may be read as the receipt itself being authoritative;
- receipts, checkpoints, primary evidence, and deterministic checker results are not given one explicit authority order;
- an agent can fill a polished receipt with unsupported `PASS`, test, mutation, or DONE claims;
- extra receipt ceremony can be imposed on trivial tasks even when direct evidence is sufficient.

## 2. Objective

Establish one cross-cutting rule:

> A receipt is a compact index of claims and evidence. It is not authoritative merely because it exists, and it is not an authorization artifact. Material receipt claims must be verified against primary artifacts, deterministic state, or Checker output before they affect execution, promotion, integration, publication, safety, or DONE.

Preserve the useful functions of receipts:

- compact worker-to-Lead handoff;
- RunSkeptic compliance record;
- checkpoint/resume support;
- terminal human-readable closure summary.

Do not create a new receipt infrastructure.

## 3. Authority model

Use this precedence model:

1. **Primary observed artifacts and external state**
   - actual files, command results, test exit codes, Git state, remote state, generated outputs, API responses.
2. **Deterministic Checker/controller results**
   - reproducible counts, hashes, validation, scoring, status, and acceptance results.
3. **Accepted authoritative checkpoint**
   - governs resume and phase status until deterministically invalidated by levels 1 or 2.
4. **Verified receipt**
   - compact index whose material claims have been checked against levels 1–3.
5. **Unverified receipt or model summary**
   - proposal or claim only; cannot authorize a consequential next state.
6. **Task Closure Receipt**
   - terminal human-readable summary derived from verified terminal facts; required when the Task Prompt contract calls for it, but not independent evidence that those facts are true.

Conflict rule:

- higher-authority evidence wins;
- a mismatch triggers narrow verification;
- reopen only the smallest phase supported by deterministic invalidation;
- missing or inaccurate receipt prose alone does not replay completed work.

## 4. Proportionality rule

Formal receipts remain required where they materially support control or recovery:

- delegated Agent work;
- RunSkeptic invocation;
- checkpoint/resume;
- serious Task Prompts;
- destructive or external actions;
- benchmarks and independent evaluation;
- publication or merge-to-main;
- cross-session or auditable work.

Do not require a new formal receipt for:

- ordinary questions;
- translations;
- trivial calculations;
- small non-delegated read-only checks;
- every command or micro-step;
- a small reversible task where direct inline evidence and immediate verification are sufficient.

This does not waive the compact RunSkeptic Receipt when `RunSkeptic` is invoked.

## 5. Scope

Modify exactly these existing runtime/governance files:

1. `skeptic.md`
2. `agents/task-prompt.md`
3. `agents/lead-agent-prompt.md`
4. `skeptic-tests.md`

Add one focused governance test:

5. `tests/test_receipt_authority.py`

Do not modify:

- verdict vocabulary;
- Thinker definitions;
- evidence-level vocabulary;
- checkpoint invalidation conditions;
- task execution modes;
- existing benchmark packages;
- unrelated tests or plans.

## 6. File-level changes

### 6.1 `skeptic.md`

Target: `RunSkeptic Receipt` section only, plus at most one cross-reference where needed.

Add:

- a receipt is an evidence index, not proof or authorization;
- material findings must point to evidence;
- a receipt/evidence mismatch blocks a RunSkeptic compliance claim until corrected or resolved;
- listing steps or Thinkers without material application/evidence is not sufficient compliance;
- retain the existing compact receipt fields in this slice.

Do not shorten or redesign the RunSkeptic flow in this change.

Line budget: no more than +14 net lines.

### 6.2 `agents/task-prompt.md`

Add a compact subsection near authority/evidence custody:

`Receipt, evidence, checkpoint, and closure authority`

Define:

- primary evidence;
- deterministic Checker/controller result;
- accepted checkpoint;
- Agent Receipt;
- Task Closure Receipt;
- their precedence and conflict behavior.

Correct ambiguous wording:

- change “An Agent Receipt is evidence returned by one role” to “an Agent Receipt is a compact claim-and-evidence index returned by one role”;
- change “A Task Closure Receipt proves” to wording that says it reports whether verified terminal conditions were reached;
- preserve the rule that the Task Closure Receipt is the required terminal summary for a serious Task Prompt;
- state that `Overall DONE: yes` must be derived from verified conditions and cannot contradict deterministic facts;
- preserve closure-only reconstruction without replay;
- make `Confidence and evidence level` optional or remove confidence as an independent promotion input;
- state that small non-delegated tasks may use a compact inline evidence summary instead of formal Agent Receipt ceremony.

Do not require a universal event ledger, JSON schema, controller, signature, or new status engine.

Line budget: no more than +42 net lines after replacing redundant wording.

### 6.3 `agents/lead-agent-prompt.md`

Add one compact operational rule:

- treat receipts as claims until material fields are verified;
- verify decision-critical claims only;
- do not repeat the worker’s entire investigation merely for confidence;
- accepted checkpoint and primary evidence outrank receipt prose;
- on mismatch, perform narrow verification and repair the receipt;
- reopen only the smallest deterministically invalidated phase;
- do not impose formal receipt ceremony on ordinary small work.

Preserve checkpoint-first and `CLOSURE_ONLY`.

Line budget: no more than +18 net lines.

### 6.4 `skeptic-tests.md`

Add a section:

`Receipt authority regression scenarios`

Document the scenarios in section 7 below.

Add reject conditions:

- unverified receipt authorizes a consequential transition;
- receipt prose overrides primary evidence or deterministic state;
- missing receipt prose causes completed phases to replay;
- receipt ceremony becomes mandatory for trivial non-delegated work;
- checklist-only RunSkeptic receipt is accepted without evidence;
- closure receipt independently invents DONE.

Line budget: no more than +40 net lines.

### 6.5 `tests/test_receipt_authority.py`

Create a focused executable governance reference.

It must:

- assert the cross-file authority markers exist;
- include a small data-driven decision table;
- distinguish `VERIFY_NARROWLY`, `REPAIR_RECEIPT`, `REOPEN_SMALLEST_PHASE`, `CLOSE`, and `REJECT_PROMOTION`;
- remain governance coverage, not a production receipt engine;
- avoid testing only marker presence by exercising the scenario decisions below.

Target: at most 170 lines.

## 7. Required scenarios

### Scenario 1 — false test claim

Given:

- Agent Receipt says tests passed;
- primary command record has non-zero exit code.

Expected:

- reject promotion;
- primary evidence wins;
- record the mismatch;
- do not claim DONE.

### Scenario 2 — claimed mutation without mutation

Given:

- Agent Receipt says a file changed;
- Git diff and file hash show no change.

Expected:

- reject the mutation claim;
- repair the receipt;
- do not reopen unrelated phases.

### Scenario 3 — missing closure field after completed work

Given:

- accepted checkpoint proves substantive phases complete;
- one closure receipt field is absent.

Expected:

- enter or remain in `CLOSURE_ONLY`;
- reconstruct the field from deterministic facts;
- close;
- do not replay execution.

### Scenario 4 — receipt conflicts with checkpoint

Given:

- unverified worker receipt says phase incomplete;
- accepted checkpoint and artifacts prove it complete;
- no deterministic invalidation exists.

Expected:

- checkpoint wins;
- repair or reject the receipt;
- continue from the first genuinely incomplete phase.

### Scenario 5 — deterministic checkpoint invalidation

Given:

- receipt and checkpoint say complete;
- accepted artifact hash no longer matches.

Expected:

- reopen only the smallest affected phase;
- preserve unaffected evidence;
- record backward-transition evidence.

### Scenario 6 — trivial non-delegated task

Given:

- one reversible local edit;
- immediate deterministic verification;
- no delegation, handoff, publication, or serious Task Prompt requirement.

Expected:

- compact inline evidence is sufficient;
- no separate formal Agent Receipt machinery.

### Scenario 7 — checklist theatre

Given:

- RunSkeptic receipt lists all major steps and Thinkers;
- no material evidence or actual application is shown.

Expected:

- do not claim RunSkeptic compliance;
- require evidence for material findings and skipped/unknown areas.

### Scenario 8 — controller result versus receipt prose

Given:

- deterministic controller reports failure or incomplete;
- closure receipt says `Overall DONE: yes`.

Expected:

- reject terminal promotion;
- controller/primary evidence wins;
- repair closure receipt;
- do not regenerate accepted expensive work unless its outputs are invalid.

### Scenario 9 — honest judgment remains with Lead

Given:

- deterministic facts are complete;
- terminal decision still requires an authorized product, architecture, or safety judgment.

Expected:

- do not pretend a checker can compute the human-owned decision;
- Lead or owner makes the judgment;
- record facts and decision separately.

## 8. Implementation phases

### P0 — verified start

- fetch current `origin/main`;
- require clean worktree;
- record current blobs for the four existing files;
- run full baseline tests;
- stop on unexplained baseline failure.

### P1 — doctrine patch

- patch `skeptic.md` first;
- keep the receipt field list stable;
- add only authority and evidence semantics.

Acceptance:

- no verdict or flow change;
- no receipt cryptography or new artifact system;
- section-level wording is unambiguous.

### P2 — Task Prompt and Lead alignment

- add the authority model to `agents/task-prompt.md`;
- add the compact operational rule to `agents/lead-agent-prompt.md`;
- check that both preserve checkpoint-first resume and closure-only behavior.

Acceptance:

- no cross-file contradiction;
- no requirement to reperform accepted work;
- no blanket rule that all judgments must be deterministically computed;
- trivial-task proportionality remains explicit.

### P3 — governance and executable coverage

- add scenarios to `skeptic-tests.md`;
- add `tests/test_receipt_authority.py`;
- run the new focused test;
- run existing Task Prompt and Lead contract tests.

Acceptance:

- all nine scenarios have an explicit expected decision;
- tests cover decision outcomes, not only strings;
- existing checkpoint/resume scenarios remain unchanged.

### P4 — full verification and integration

Run:

- `uv run python -m unittest tests.test_receipt_authority`
- `uv run python -m unittest tests.test_task_prompt_contract`
- `uv run python -m unittest tests.test_task_prompt_scenarios`
- `uv run python -m unittest tests.test_lead_execution_modes`
- `uv run python -m unittest discover -s tests`

Then verify:

- exactly five intended paths changed;
- line budgets respected or justified;
- no new runtime dependency;
- no new verdict/status vocabulary;
- current receipt/checkpoint behavior remains compatible;
- fresh remote state before non-force integration;
- fresh fetch after integration;
- local `main == origin/main`;
- clean worktree.

## 9. Change acceptance tests

The implementation passes only when:

1. unverified receipts cannot authorize consequential transitions;
2. deterministic evidence can disprove a receipt;
3. a receipt mismatch triggers narrow handling, not broad replay;
4. accepted checkpoints remain authoritative until deterministically invalidated;
5. Task Closure Receipt remains required for serious Task Prompts but is clearly derived from verified facts;
6. RunSkeptic still requires a compact receipt;
7. checklist theatre cannot establish compliance;
8. trivial non-delegated work does not gain unnecessary receipt ceremony;
9. human-owned judgments remain human-owned;
10. existing full suite passes.

## 10. Reject conditions

Reject or revise the implementation if it:

- adds signing keys, signatures, authorization tokens, or PKI;
- creates a generic receipt service;
- requires JSON ledgers for every task;
- adds new terminal verdicts;
- treats a self-hash as truth;
- makes every task produce a formal receipt;
- removes durable evidence or checkpoint requirements;
- lets receipts override primary evidence;
- turns every judgment into a fake deterministic computation;
- duplicates the full Task Prompt contract into `skeptic.md` or the Lead prompt;
- exceeds the patch’s expected value with new ceremony.

## 11. Risks and mitigations

### Risk: receipts become too weak

Mitigation:

- retain receipts for delegated, serious, resumable, and RunSkeptic work;
- weaken only their unsupported authority, not their reporting role.

### Risk: closure receipt loses terminal meaning

Mitigation:

- preserve it as the mandatory terminal summary for serious Task Prompts;
- clarify that its claims must be verified rather than self-proving.

### Risk: deterministic machinery is overgeneralized

Mitigation:

- require deterministic facts where practical and already available;
- keep authorized judgment with Lead/owner;
- do not add a universal status engine.

### Risk: cross-file duplication

Mitigation:

- detailed authority model lives in `agents/task-prompt.md`;
- `skeptic.md` gets only RunSkeptic-local semantics;
- Lead prompt gets only the operational rule.

### Risk: tests merely freeze wording

Mitigation:

- combine contract-marker checks with a compact executable scenario table;
- state clearly that governance tests do not prove arbitrary agent compliance.

## 12. Expected result

After this slice:

- receipts remain useful and compact;
- checkpoints remain the resume authority;
- primary evidence and deterministic checks outrank model prose;
- unsupported `PASS` or `DONE` claims are rejected;
- missing receipt fields do not destroy completed work;
- small work stays small;
- no cryptographic or receipt-service infrastructure is introduced.

## 13. Plan RunSkeptic record

Review method:

- actual current `skeptic.md` from repository `main`;
- `agents/task-prompt.md`, `agents/lead-agent-prompt.md`, `skeptic-tests.md`, and relevant tests as companions;
- same-context semantic review, not independent clean-room review;
- permission mode: fix-plan-only.

### Review cycle 1 — ACTION

Findings fixed:

1. Initial plan treated “deterministic status” too broadly and risked creating a universal status engine.
2. It did not clearly preserve authorized human judgment.
3. It proposed shortening the RunSkeptic receipt in the same slice, creating unnecessary compatibility risk.
4. It did not distinguish accepted checkpoint authority from stale/corrupt checkpoint invalidation.

Changes:

- limited deterministic computation to available primary/checker facts;
- separated facts from human-owned judgment;
- retained the current RunSkeptic receipt fields;
- added explicit authority and invalidation precedence.

### Review cycle 2 — ACTION

Findings fixed:

1. “No formal receipt for small work” could be misread as waiving the RunSkeptic receipt.
2. Closure receipt wording risked removing its required terminal role.
3. Structural marker tests alone would not exercise the claimed behavior.
4. The patch scope lacked explicit line and file budgets.

Changes:

- preserved the RunSkeptic receipt whenever invoked;
- kept Task Closure Receipt mandatory for serious Task Prompts;
- added nine executable governance scenarios;
- froze five paths and line budgets.

### Frozen review pass 1 — PASS / HANDLED

- Gate: PASS
- Fundamental scan: no unresolved architecture, authority, or source-of-truth conflict.
- All Thinkers considered.
- Evidence: current receipt, checkpoint, closure, proportionality, and governance contracts.
- Verification: scenarios, scope, non-goals, compatibility, and implementation acceptance criteria checked.
- Unknowns: exact final wording and line counts remain implementation-time facts.
- Final category: HANDLED.

### Frozen review pass 2 — PASS / HANDLED

- Same plan bytes.
- No new material finding.
- No unresolved ACTION, DECOMPOSE, CONFLICT, or blocking unknown.
- Final category: HANDLED.

### Frozen review pass 3 — PASS / HANDLED

- Same plan bytes.
- No new material finding.
- No unresolved ACTION, DECOMPOSE, CONFLICT, or blocking unknown.
- Final category: HANDLED.

The three frozen passes are same-context reviews. They are not independent protected-context reviews and must not be described as such.
