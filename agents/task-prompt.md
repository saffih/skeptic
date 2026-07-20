# Task Prompt

## Purpose

A Task Prompt is the complete Lead-owned execution contract for accomplishing a defined outcome from verified starting state through terminal DONE.

It is a control plane for the task. It may coordinate phases, agents, tools, decisions, retries, evidence checkpoints, tests, reviews, commits, merges, pushes, and remote verification. It must not become a transcript, evidence dump, or copy of every child prompt.

Canonical hierarchy:

```text
User objective
-> Task Prompt
   -> Lead Agent Prompt
      -> Agent Prompts / Dispatch Tickets
         -> Agent Receipts and evidence
   -> verification and integration
-> Task Closure Receipt
```

The Lead owns the Task Prompt and the terminal outcome. An Agent Prompt is a bounded child instruction. A Dispatch Ticket is the compact delegated form of an Agent Prompt. An Agent Receipt is evidence returned by one role. A Task Closure Receipt proves whether the whole Task Prompt reached the requested terminal state.

## Relationship to other repository contracts

- `agents/task-prompt.md` is authoritative for Task Prompt construction, execution control, and closure.
- `agents/lead-agent-prompt.md` is authoritative for the Lead role, prompt architecture, and prompt gating.
- `skeptic.md` is authoritative for RunSkeptic review behavior and output categories.
- Repository and runtime governance remain authoritative within their scopes.

Do not copy this entire file into `agents/lead-agent-prompt.md`, `skeptic.md`, or every Dispatch Ticket. Reference it and include only the local contract needed by the current role.

## When a Task Prompt is required

Use a Task Prompt when the user asks for terminal execution of serious work, especially when the task materially involves one or more of:

- multiple dependent phases or roles;
- repository mutation, integration, publication, or external side effects;
- a requested terminal state beyond analysis, a patch, or a branch;
- significant context, token, time, credit, or tool constraints;
- decision-critical evidence that must survive handoffs or context compression;
- clean-room or independent evaluation;
- retries, redesign, recovery, or cross-session continuation.

A small, reversible task may use a compact Task Prompt containing only the fields that materially apply. Proportionality may reduce ceremony; it must not remove exact DONE, authority, material scope limits, verification, or stop conditions.

## Lead ownership

The Lead retains ownership of:

- the user objective and exact terminal DONE;
- authority and source-of-truth resolution;
- feasibility, useful-slice, and protocol-cost decisions;
- phase architecture and dependency order;
- model, effort, agent, context, and completion-budget routing;
- evidence custody and promotion decisions;
- failure classification, retry, redesign, and escalation;
- verification, integration, publication, remote confirmation, and closure.

Delegation transfers bounded work, not terminal ownership. A worker may report success within its ticket while the Task Prompt remains incomplete.

## Task Prompt state machine

```text
New execution:
INTAKE
-> PREFLIGHT
-> DESIGN
-> TASK-LEVEL SKEPTIC GATE

Resumed execution:
RESUME ENTRY
-> VERIFY AUTHORITATIVE CHECKPOINT
-> first incomplete dependency-ready phase
   or CLOSURE_ONLY when substantive work is complete
   or smallest evidenced backward transition after deterministic invalidation
   or CHECKPOINT_CONFLICT when state cannot be reconciled

Execution loop (entered from the new-execution gate or a verified resume route):
-> EXECUTE READY PHASE
-> VERIFY AND PERSIST CHECKPOINT
-> REASSESS FEASIBILITY AND BUDGET
-> next ready phase or REDESIGN / DECOMPOSE / CONFLICT
-> SYSTEM VERIFICATION
-> INTEGRATION / PUBLICATION when required by DONE
-> REMOTE OR EXTERNAL VERIFICATION when required by DONE
-> TASK CLOSURE RECEIPT
```

No phase may consume an unmet dependency. No dependent phase may use an output that has not passed its acceptance check and been durably persisted. No intermediate state may be promoted to DONE.

A lifecycle written from phase zero does not authorize replay of verified work.

## Checkpoint-first resume and closure-only execution

Before broad artifact review, resumed execution must verify the authoritative checkpoint and record:

- authoritative checkpoint path or ref and hash;
- highest completed phase;
- first incomplete phase;
- blockers;
- closure-ready status;
- remaining work;
- Lead-context files opened and reason;
- backward-transition authorization and evidence.

Resume at the first incomplete dependency-ready phase. Completed phases and their accepted outputs are immutable evidence.

Reopen a completed phase only when a deterministic Checker proves invalidation through a hash mismatch, corrupt or missing accepted artifact, failed acceptance, changed immutable input, or contradictory authoritative state.

A backward transition must name the invalid checkpoint, deterministic evidence, smallest phase reopened, preserved unaffected evidence, and renewed feasibility. Otherwise return `CHECKPOINT_CONFLICT`.

Missing prose, summaries, governance receipts, formatting preferences, extra-confidence requests, optional advice, or unfavorable accepted results do not invalidate substantive work.

When substantive work is complete, enter `CLOSURE_ONLY`. By default, read only:

1. the authoritative checkpoint;
2. the authoritative final result;
3. the gap or missing-field ledger;
4. the draft or final Task Closure Receipt.

Then verify required hashes, counts, state, external status, and terminal conditions; fill only missing receipt fields; preserve accepted results; issue the Task Closure Receipt; and stop. Any additional artifact requires a named blocker and an explanation of why the default four are insufficient.

For an accepted deterministic result, verify identity, input and result hashes, acceptance, and required counts. Do not recreate inventories, scores, ledgers, or conclusions, and do not read all raw outputs. Raw evidence may be opened only for one named unresolved dispute.

After closure-ready, do not add an advisor, Judge, optional review, new inventory, broad analysis, or "one more check" unless it was explicitly frozen into the terminal contract before execution.

Missing procedural evidence does not reopen completed phases. Reconstruct only the absent receipt or summary field from current hashes and deterministic facts.

`prompt too long`, session exhaustion, forced compression, or unplanned handoff after substantive completion is a failed Task Prompt execution path even when artifacts survive.

`PACKAGE_INCOMPLETE` and `CHECKPOINT_CONFLICT` are operational stop reasons, not Skeptic verdicts. They do not change `PASS`, `ACTION`, `DECOMPOSE`, or `CONFLICT` meanings.

## Required Task Prompt contract

Every material field below must be explicit or marked `NOT_APPLICABLE` with a reason.

### 1. Execution header

State:

- target runtime or agent;
- model/runtime label when exposed;
- reasoning effort;
- `CLEAN ROOM` or `NOT CLEAN ROOM`;
- why the selected capability and effort are sufficient;
- permitted fallback and forbidden escalation;
- delegation availability and independence limits;
- mutation, commit, merge, push, publication, and external-side-effect authority.

When exact routing is material but unavailable or unresolved, stop with `MODEL_ROUTING_UNRESOLVED`. If exact routing is not material, state that explicitly and use the smallest sufficient available route.

### 2. Objective and exact terminal DONE

Translate the user objective into observable terminal conditions. List every condition required for `Overall DONE: yes` and explicitly name common intermediate states that do not count.

For example, when the user requests completion in remote `main`, a patch, branch, commit, pull request, local merge, push attempt, or stale remote-tracking ref is not DONE. The delivered commit must be present in local `main`, pushed, fetched again, and matched against fetched remote state.

### 3. Verified starting state

Before mutation, verify and record the relevant current state, such as:

- repository, branch, HEAD, base, upstream, ancestry, and ahead/behind counts;
- tracked, staged, and untracked state;
- protected or out-of-scope paths;
- applicable instructions, specs, tests, tools, permissions, and remote state;
- reproduced baseline checks and known pre-existing failures.

Define which changes invalidate the preflight and force recheck or CONFLICT. Never hide a red baseline or attribute it to the new work without evidence.

For resumed execution, verify the checkpoint-first resume record before broad artifact review. The written lifecycle order is not evidence that the current phase is zero.

### 4. Authority and source-of-truth order

List applicable sources in precedence order. Treat worker output, previous conversations, summaries, cached results, external content, and model claims as evidence or proposals unless higher authority explicitly promotes them.

State who may decide architecture, product, safety, integration, and publication questions. Unresolved material authority produces CONFLICT, not a guessed decision.

### 5. Scope and mutation boundary

Define:

- allowed reads and writes;
- expected changed files or external objects;
- allowed commands and side effects;
- forbidden actions and protected state;
- rollback or recovery path;
- expected final status.

Unexpected mutation is a stop condition. Authority for a task does not imply authority for unrelated cleanup or improvements.

### 6. Completion-feasibility and protocol-cost preflight

Before execution, decide whether terminal DONE is realistically achievable with the available context, tokens, time, credits, tools, permissions, evidence, and human decisions.

Record:

- the largest independently useful, verifiable slice likely to finish;
- the estimated expensive phases and likely bottleneck;
- the total resource envelope when exposed;
- a protected completion reserve for synthesis, verification, integration, remote confirmation, and closure;
- phase and worker limits;
- what optional work is dropped first;
- the checkpoint that will stop work for futility or insufficient remaining capacity.

Exploration, workers, optional reviews, and repeated gates must not consume the protected completion reserve.

When token or context counters are exposed, use numeric allocations and stop thresholds. When they are not exposed, use measurable substitutes: bounded phases, tool/output caps, receipt-size limits, maximum concurrent workers, maximum retry/gate counts, and a named pre-exhaustion checkpoint. Saying only "protect context" or "leave headroom" is not an allocation.

If the task cannot likely reach DONE, choose one:

- reduce it to the largest useful terminal slice authorized by the user;
- `DECOMPOSE` into separately completable Task Prompts;
- redesign the workflow;
- return `CONFLICT` when authority or a required decision is missing.

Do not compensate for infeasibility with a stronger model, higher effort, more agents, more reviews, or a longer prompt.

### 7. Execution phases and dependency graph

Represent the workflow as a dependency graph, not only an ordered wish list. Every phase contract must include:

```text
Phase ID and objective:
Dependencies:
Owner / role:
Model and effort, if material:
Inputs and source of truth:
Allowed actions and mutation boundary:
Budget / context / output limit:
Required output and durable evidence location:
Acceptance and disconfirming checks:
Checkpoint / resume state:
Backward-transition authorization and evidence:
Failure, retry, and rollback path:
Next-state rule:
```

Prefer the fewest phases that keep ownership, evidence, and recovery clear. Do not over-fragment a small task, and do not keep a large all-or-nothing phase whose failure discards useful verified work.

### 8. Role, model, and effort routing

Route by the actual work:

- deterministic commands or scripts for hashes, counts, status, diffs, builds, and repeatable checks;
- bounded workers for broad searches, inventories, or isolated implementation;
- Checkers for deterministic promotion evidence;
- independent Judges only when independence materially affects the decision;
- the Lead for ambiguity, architecture, authority, tradeoffs, readiness, integration, and closure.

For every material route, state the role, required capability, selected runtime/model and effort, reason, fallback, and stop condition. Runtime availability must be verified when selection matters. A stronger model must not substitute for a repaired ticket, smaller scope, better evidence flow, or correct decomposition.

### 9. Context allocation and evidence custody

The Task Prompt must say what remains in Lead context, what stays with workers or deterministic tools, and what is durably persisted.

Keep with the Lead:

- objective, authority, dependencies, material findings and dissent;
- phase/checkpoint status, gap ledger, decisions, and terminal verification.

Keep outside Lead context when proportionate:

- broad raw searches, repetitive inventories, large logs, and full worker reasoning.

Return paths, hashes, short excerpts, concise findings, and compact receipts. Do not paste the parent Task Prompt into each ticket.

Every expensive or decision-critical phase must persist an authoritative artifact before dependent work begins. Temporary chat, worker memory, transient context, and unverified summaries are not durable evidence. Compression must preserve dissent, contradictions, failed cases, unknowns, and minority evidence that could change a decision.

On resume, Lead context begins with the authoritative checkpoint record. In `CLOSURE_ONLY`, use the default four artifacts defined above and record every Lead-context file opened and its reason; broader reading requires a named blocker.

Maintain a compact gap ledger for long or delegated tasks:

```text
Requested outcome:
Completed and verified phases:
Unresolved gaps:
Blocking conflicts:
Deferred out-of-scope work:
Evidence locations:
Remaining budget / feasibility:
```

### 10. Clean-room and independence requirements

Define what prior material may be seen and what evidence is prohibited. Do not claim clean-room or independent review unless protected contexts were genuinely separate. When isolation is unavailable, label the result same-context and stop if genuine independence is required for authorization.

### 11. Checkpoints, failure, retry, and redesign

At each checkpoint:

1. verify the phase output and disconfirming case;
2. persist the evidence;
3. update the gap ledger;
4. re-estimate remaining work against the protected completion reserve;
5. authorize only dependency-ready next phases.

Completed accepted checkpoints are monotonic. Reopen only the smallest phase supported by deterministic invalidation under the checkpoint-first resume contract, preserve unaffected evidence, and reassess feasibility. Missing procedural fields are not a failure class and do not authorize replay.

On failure, preserve evidence, identify the exact point and failure class, find the smallest verified cause, and retry only when the next attempt is materially safer or better informed.

The Task Prompt must declare retry and Skeptic-gate limits before execution. Unless a stricter task-specific rule is justified, the same failure class repeating twice without materially new evidence triggers redesign rather than another retry. A bounded gate may use one initial pass plus at most two materially revised reruns; lack of improvement returns DECOMPOSE or CONFLICT.

Define a pre-exhaustion handoff that records verified state, evidence paths, failures, remaining work, exact next action, and terminal state still missing. Handoff is not DONE.

### 12. Verification and acceptance

Define checks that can prove each phase and the whole system wrong. Include, when relevant:

- targeted and regression tests;
- known-bad, edge, and silent-pass cases;
- manifests, status, diff, hash, or equivalence checks;
- end-to-end trace from requested input to terminal output;
- independent review where materially necessary;
- RunSkeptic using the current authoritative `skeptic.md`.

Marker presence and polished prose prove structure only. Behavioral or scenario claims require evidence that exercises the claimed decision path.

### 13. Integration, publication, and remote verification

When integration or publication is part of DONE, make it an explicit dependency-gated phase. Require clean intended state, current upstream verification, exact commit/ref checks, non-force publication, post-publication refresh, and comparison against freshly observed external state.

If authority, credentials, network, CI, review, mergeability, or remote state blocks completion, preserve the verified work and return CONFLICT. Do not relabel a local intermediate state as DONE.

### 14. Task Closure Receipt

The Task Closure Receipt is the only terminal proof for the whole Task Prompt. It must enumerate each DONE condition, its yes/no result, evidence, delivered refs or artifact identifiers, tests and reviews, protected-state result, unresolved blockers, and residual risk.

For resumed or `CLOSURE_ONLY` execution, it must also include the checkpoint-first resume record, the Lead-context file ledger, and any backward-transition authorization. Fill absent procedural fields from deterministic current facts without reopening completed phases.

`Overall DONE: yes` is allowed only when every required terminal condition is verified. Agent Receipts, confidence, and a successful push command are inputs to closure, not substitutes for it.

## Agent Prompt and Dispatch Ticket

An Agent Prompt is a bounded instruction for one participating role. It does not own overall completion unless the Task Prompt explicitly appoints that agent as Lead.

Use this compact Dispatch Ticket for delegated work:

```text
Role:
Objective:
Source of truth:
Scope:
Allowed actions:
Forbidden actions:
Budget / context / output limit:
Required evidence and durable destination:
Acceptance and disconfirming checks:
Stop conditions:
Return receipt:
```

## Agent Receipt

```text
Role and task:
Scope completed:
Files or objects read:
Commands or tools used:
Evidence and durable locations:
Changes made:
Verification and disconfirming checks:
Failures, unknowns, and blockers:
Budget / context result:
Recommended next action:
Confidence and evidence level:
```

The Lead or a Checker must verify material receipt claims before promoting them into readiness, mutation, integration, publication, or safety decisions.

## Task-level Skeptic readiness gate

Before execution and before terminal promotion, apply the current `skeptic.md` at both applicable levels:

1. Agent Prompt level: each child instruction is bounded, authorized, testable, and able to return useful evidence.
2. Task Prompt level: the aggregate system can realistically traverse its dependency graph and reach exact terminal DONE within the available resources and authority.

Task-level verdicts:

- `PASS`: executable as written; no blocking task- or child-level finding remains.
- `ACTION`: repairable prompt defect remains; fix and rerun within the declared gate budget.
- `DECOMPOSE`: the objective is clear but the Task Prompt is too large or coupled to finish safely as one contract.
- `CONFLICT`: authority, source of truth, design choice, safety, or required completion path cannot be resolved within prompt scope.

A Task Prompt must not receive PASS merely because every Agent Prompt passes locally. Do not execute a Task Prompt with unresolved ACTION, DECOMPOSE, CONFLICT, review-required status, or blocking unknown.

## Copyable Task Prompt template

```text
# Task Prompt: <outcome>

## Execution header
Target runtime/agent:
Model/runtime label and effort:
Clean-room status:
Routing reason, fallback, and forbidden escalation:
Delegation and independence availability:
Mutation/integration/publication authority:

## Objective
<useful outcome>

## Exact terminal DONE
1. <observable condition>
Intermediate states that are not DONE:

## Verified starting state
Repository/environment/ref/state:
Protected or out-of-scope state:
Baseline checks and pre-existing failures:
Invalidation/recheck conditions:

## Resume / checkpoint state
Authoritative checkpoint path/ref and hash:
Highest completed phase:
First incomplete phase:
Blockers:
Closure-ready status:
Remaining work:
Lead-context files opened and reason:
Backward-transition authorization and evidence:

## Authority and source-of-truth order
1. <highest applicable authority>
Decision owners:

## Scope and mutation boundary
Allowed reads/writes/actions:
Forbidden actions:
Expected final state:
Rollback/recovery:

## Completion-feasibility and budget
Largest useful terminal slice:
Resource envelope or measurable substitutes:
Protected completion reserve:
Phase/worker/output/gate limits:
Futility and pre-exhaustion stop:
Protocol-cost assessment:

## Execution graph
### <Phase ID - objective>
Dependencies:
Owner / role:
Model and effort, if material:
Inputs / source of truth:
Allowed actions:
Budget / context / output limit:
Output and durable evidence location:
Acceptance and disconfirming checks:
Checkpoint / resume state:
Backward-transition authorization and evidence:
Failure / retry / rollback:
Next-state rule:

## Agent Prompts / Dispatch Tickets
<for each delegated phase, include or reference the bounded ticket>
Level 1 Skeptic gate result:
Receipt destination and verifying owner:

## Context and evidence custody
Lead context:
Worker/tool context:
Authoritative artifacts:
Gap ledger location:
Lead-context files opened and reason:
Compression/handoff rule:

## Clean-room / independence
Allowed prior material:
Prohibited evidence:
Isolation proof or same-context limitation:

## Failure, retry, redesign, and handoff
Failure classes:
Maximum retries/gate passes:
Redesign trigger:
Checkpoint conflict / backward-transition rule:
Pre-exhaustion handoff contents/location:

## System verification
Targeted checks:
Regression and disconfirming checks:
RunSkeptic loop and maximum passes:

## Integration / publication / remote verification
Preconditions:
Integration steps:
Fresh external verification:
Failure stop:

## Task Closure Receipt
Execution mode / `CLOSURE_ONLY` status:
Authoritative checkpoint path/ref and hash:
Highest completed phase:
First incomplete phase:
Remaining work:
Lead-context files opened and reason:
Backward-transition authorization and evidence:
Task Prompt created and gated: yes/no + evidence
Implementation complete: yes/no + evidence
Required verification passed: yes/no + evidence
RunSkeptic passed/HANDLED: yes/no + evidence
Integration/publication complete: yes/no/not applicable + evidence
Fresh external or remote state verified: yes/no/not applicable + evidence
Protected and out-of-scope state preserved: yes/no + evidence
Delivered artifact/ref identifiers:
Unresolved blockers:
Residual risk:
Overall DONE: yes/no

# PONYTAIL / KISS — NON-NEGOTIABLE EXECUTION CHECKSUM

<short task-specific non-negotiable rules>

# END OF PROMPT
```

## Final invariant

Building a Task Prompt means engineering the whole task to finish or fail early with preserved evidence. It does not mean making one enormous prompt.

No Task Prompt may claim completion while terminal integration, publication, fresh external verification, or another user-requested DONE condition remains unverified.
