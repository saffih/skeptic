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

The Lead owns the Task Prompt and the terminal outcome. An Agent Prompt is a bounded child instruction. A Dispatch Ticket is the compact delegated form of an Agent Prompt. An Agent Receipt is a compact claim-and-evidence index returned by one role. A Task Closure Receipt reports whether the whole Task Prompt reached verified terminal conditions.

## Relationship to other repository contracts

- `agents/task-prompt.md` is authoritative for Task Prompt construction, execution control, and closure.
- `agents/lead-agent-prompt.md` is authoritative for the Lead role, prompt architecture, and prompt gating.
- `skeptic.md` is authoritative for RunSkeptic review behavior and output categories.
- Repository and runtime governance remain authoritative within their scopes.

Do not copy this entire file into `agents/lead-agent-prompt.md`, `skeptic.md`, or every Dispatch Ticket. Reference it and include only the local contract needed by the current role.

## Stateless library and runtime-owned state

This repository is a reusable, normally read-only prompt and review library. It defines portable execution contracts; it does not own runtime state, workflow storage, or task workspaces. State handling belongs to the invoking runtime and the actual task environment, not to this checkout.

Persistence is conditional, not automatic:

- A task that can reliably finish in one session, with no handoff, interruption, independent review, delegation, repeated execution, or cross-session consumer, may remain entirely session-only. It does not require a controller, checkpoint file, gap-ledger file, state directory, or durable artifact store.
- Persistence is required when evidence or state must survive handoff, interruption, context clearing, independent review, delegation, repeated execution, or cross-session continuation.
- This Task Prompt defines the required state and evidence properties for the survival need that actually exists -- identity, scope, freshness, and acceptance -- not a particular mechanism or path.
- When persistence is materially required, the environment selects an authorized location: the current runtime, the target repository or workspace, authorized temporary storage, runtime-managed storage, or another user-selected store.
- The Skeptic checkout is not the default task workspace. Writing to it is valid only when Skeptic itself is the explicit target and mutation is authorized.

Any field in this contract or its copyable template that names a durable location, checkpoint, or state destination may be marked `NOT_APPLICABLE` with a stated reason when the task is valid session-only work.

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

Before each phase and immediately after each acceptance, the Task Prompt requires the Lead to record capacity as `SUFFICIENT` (next phase plus verification and closure can still finish), `CONSTRAINED` (optional work is forbidden; continue only with required work), or `UNSAFE` (checkpoint and hand off before further substantive work). Every unplanned action must be classified as `acceptance-required`, `blocker-required`, or `optional`; optional work is forbidden immediately after any acceptance and whenever capacity is `CONSTRAINED` or `UNSAFE`. A valid acceptance requires persistence and immediate advancement, not another semantic review, spot-check, or rereading of the accepted candidate for reassurance.

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
Deterministic promotion checks:
Accepting owner:
What acceptance authorizes:
What acceptance forbids:
Checkpoint / resume state:
Deterministic invalidation conditions:
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

The Task Closure Receipt is the required terminal summary for the whole Task Prompt. It must enumerate each DONE condition, its yes/no result, evidence, delivered refs or artifact identifiers, tests and reviews, protected-state result, unresolved blockers, and residual risk.

For resumed or `CLOSURE_ONLY` execution, it must also include the checkpoint-first resume record, the Lead-context file ledger, and any backward-transition authorization. Fill absent procedural fields from deterministic current facts without reopening completed phases.

`Overall DONE: yes` is allowed only when every required terminal condition is verified. Agent Receipts, confidence, and a successful push command are inputs to closure, not substitutes for it, and `Overall DONE: yes` must not contradict deterministic facts or accepted checkpoint state.

### 15. Receipt, evidence, checkpoint, and closure authority

Resolve a material conflict claim-by-claim. Before relying on an artifact, Checker/controller result, or checkpoint, verify that it is bound to the relevant claim through identity, scope, inputs, freshness, and acceptance state. A receipt never outranks the evidence it summarizes. An accepted checkpoint governs resume until verified contradictory evidence deterministically invalidates it. When source binding or authority remains unresolved, verify narrowly and block consequential promotion.

A Task Closure Receipt is derived from verified terminal conditions; it is not independent evidence that those conditions are true. On a mismatch between a receipt and higher-authority evidence, verify the specific conflicting claim, repair or reject the receipt, and reopen only the smallest phase that deterministic invalidation actually supports. Missing or inaccurate receipt prose alone does not replay completed work.

A small, non-delegated, reversible task may use a compact inline evidence summary in place of formal Agent Receipt ceremony. This does not waive the Task Closure Receipt for a serious Task Prompt or the RunSkeptic Receipt when RunSkeptic is invoked.

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
Confidence and evidence level (optional; not an independent promotion input):
```

The Lead or a Checker must verify material receipt claims before promoting them into readiness, mutation, integration, publication, or safety decisions. See [Receipt, evidence, checkpoint, and closure authority](#15-receipt-evidence-checkpoint-and-closure-authority) for the full precedence order.

## Recursive execution hierarchy (A/B/C)

This hierarchy controls three things at once -- ownership, information flow, and promotion authority. Hierarchy alone is insufficient unless all three are explicit. Delegation that only moves work down, while all detailed outputs and lifecycle responsibilities still converge on the top Lead, is not this hierarchy.

It is a set of roles and boundaries, not a requirement for genuine nested agents. A runtime with real subagents may place each role in a separate protected context; a single agent realizes the same contract as phase-scoped context boundaries with receipt discipline. The contract must hold with or without nested agents. If a runtime cannot represent the boundary at all, return `CONFLICT` rather than pretending the layer exists.

Role mapping to this document's existing vocabulary:

- A -- Executive Lead is the Lead / Orchestrator defined in "Lead ownership" and `agents/lead-agent-prompt.md`.
- C -- Worker, Checker, or Reviewer is the bounded execution role; Reviewer is the independent-evaluation role this document also calls Judge.
- B -- Phase Supervisor is a new bounded layer between A and C, owning one phase.

### A -- Executive Lead

A owns the task objective, authority, global phase state, material conflicts, integration, and closure. A retains only:

- objective and exact DONE;
- authority and source-of-truth order;
- phase dependency state;
- accepted artifact identities;
- compact material findings and dissent;
- blockers and remaining feasibility;
- integration and closure state.

A must not normally receive:

- full Task Prompt copies from children;
- raw worker reasoning;
- full logs or diffs;
- repeated receipts;
- entire evidence packages.

A opens lower-level evidence only for a named dispute or deterministic invalidation. When a B Supervisor exists, A does not directly manage that phase's C agents; it manages B and consumes B's one upward receipt.

### B -- Phase Supervisor

B owns exactly one bounded phase and:

- creates bounded C tickets;
- receives C evidence;
- verifies material receipt claims;
- handles local bounded repair and retry;
- preserves dissent and contradictions;
- produces one compact upward phase receipt to A.

B cannot:

- expand the task objective;
- claim task-level DONE;
- accept its own unverified implementation;
- forward all C output to A;
- continue optional work after phase acceptance.

Context protection applies recursively. B must use references and bounded receipts rather than accumulating unlimited C history. The context-allocation, compression, and closure disciplines that bind A bind B within its phase. Moving overload from A to B is a failed design, not a solution.

### C -- Worker / Checker / Reviewer

C receives one bounded Dispatch Ticket with role, objective, source of truth, scope, allowed and forbidden actions, output limit, evidence destination, and acceptance and stop rules. C:

- cannot promote its own output across a trust boundary;
- cannot silently expand scope;
- reports adjacent findings without acting on them;
- returns evidence to its B Supervisor, not directly to A.

C reports only to the B Supervisor that dispatched it. It does not claim phase or task completion.

### No self-promotion across a trust boundary

No producer may accept or promote its own output across a trust boundary. An agent that produced or implemented a phase result cannot be the sole acceptor of that same result: acceptance requires an independent Reviewer or a deterministic Checker. This applies at every level -- C cannot self-accept to B, and B cannot self-accept its own implementation as the phase result to A.

### Upward phase receipt (B -> A)

B returns exactly one compact upward phase receipt to A containing only:

- phase ID and status;
- accepted artifact identity;
- evidence location and hash;
- acceptance owner and validation result;
- material findings;
- unresolved dissent, contradiction, unknown, or blocker;
- budget / capacity result;
- next authorized state.

The receipt carries references and material conclusions, not full evidence. It is a claim until A or a deterministic Checker verifies its material fields. A receipt whose accepted artifact identity, evidence location, or hash is missing cannot be promoted.

Size is bounded by field, not by an arbitrary count: the receipt is exactly the enumerated fields above, and every field that would otherwise embed a log, diff, or full artifact must instead carry a reference (path, ref, hash, line range) and the material conclusion. This is the same compact-receipt convention already used for the [Agent Receipt](#agent-receipt) and [Context allocation and evidence custody](#9-context-allocation-and-evidence-custody); it introduces no new numeric limit.

Minority dissent, contradictions, blockers, and unknowns cannot be silently removed during upward compression. Compression that drops a material dissent, contradiction, unknown, failed case, or minority finding is a defective receipt, not a smaller one.

### Safe hierarchy collapse

The hierarchy is proportional; a missing level must collapse safely rather than be faked. Permit:

- A-only execution for tiny, reversible, non-delegated work;
- A -> C for one small bounded delegation when creating a B Supervisor would cost more than the work.

Require A -> B -> C when the work materially includes:

- multiple C agents;
- broad or verbose evidence;
- implementation plus checking;
- independent review;
- repeated evaluation;
- meaningful context-exhaustion risk.

Collapsed execution does not waive receipt verification, authority boundaries, or exact DONE. A missing layer must not be invented: do not describe a single-context task as if a separate B or C reviewed it, and do not claim independence a collapsed structure did not have. The closure-ready restriction in "Checkpoint-first resume and closure-only execution" still binds a collapsed A: no optional advisor or extra review after any phase is accepted.

### Logical hierarchy versus physical launch

The hierarchy is logical -- it governs ownership, information flow, and promotion, not which runtime process spawns which. It must not assume that a B Supervisor can technically spawn its own C agents. When the runtime supports only flat spawning -- A or the runtime can launch a C agent, but B cannot nest a child -- the logical hierarchy is preserved by routing, not by nesting:

- A or the runtime physically launches C from B's frozen Dispatch Ticket;
- C's result is routed to B's evidence boundary, not to A;
- B remains the accepting and summarizing owner for the phase;
- A receives only B's one bounded upward receipt unless a named dispute authorizes narrow evidence access.

Flat physical spawning therefore does not collapse the logical layer: B still owns acceptance and compression for its phase even when B did not issue the launch call. Physical launch topology never overrides logical ownership and routing.

### Dispatch-fit gate and measurable context guards

Before every child launch, run a dispatch-fit gate. It measures whether the bounded Dispatch Ticket plus the context the child must inherit fits within the child's declared budget. When exact token counters are unavailable, use the measurable substitutes already required by the completion-feasibility preflight -- maximum child count per phase, maximum embedded excerpts or lines, maximum receipt fields, references and hashes instead of embedded logs or diffs, and maximum retry and review counts.

If the ticket plus required inherited context does not fit, do not launch. In order:

1. reduce embedded material;
2. replace embedded material with references and hashes;
3. split the phase into smaller bounded tickets;
4. otherwise stop with `CONTEXT_HANDOFF_REQUIRED`.

Oversized dispatch stops before launch, not after a failed launch. `CONTEXT_HANDOFF_REQUIRED` is an operational stop or transition reason, not a Skeptic verdict and not DONE: it means the current context cannot safely carry the next launch and must hand off compact authoritative state first. Each serious Task Prompt declares its own runtime-appropriate measurable bound or substitute during the completion-feasibility preflight; this contract does not fix one universal byte or token threshold.

### A failed launch is not a result

A child launch that fails, times out, is rejected, or returns incomplete output is an operational failure, not evidence. It does not count as a completed check, a completed review, or a RunSkeptic PASS, and it does not advance any phase or verification counter. Re-launch only within the declared retry bound; the same launch failure twice without materially new information triggers redesign or a truthful blocked result, not a counted pass.

### Terminal-state lock

After a phase is accepted, only that phase's declared next authorized state is available. After the third consecutive RunSkeptic PASS, integration readiness, or closure readiness, the terminal state is locked: no optional advisor, no reassurance review, no broad reread, no regenerated inventory or evidence chain, and no fourth RunSkeptic pass. This restates at the hierarchy level the closure-ready restriction in "Checkpoint-first resume and closure-only execution" and the three-PASS stop in `AGENTS.md` ("Skeptic verification"); it adds no new rule. Only deterministic completion, a named blocker, or proven invalidation may reopen work, and only the smallest affected phase, under the backward-transition rule.

## Compact execution state

Some tasks materially require handoff, interruption recovery, delegation, repeated verification, or cross-session continuation. For those, define a portable minimum execution-state record sufficient to replace or resume the Lead without replaying history. This is a set of required properties, not a mandatory file format, path, storage mechanism, controller, or database. Per "Stateless library and runtime-owned state", the invoking runtime or task environment selects an authorized location; a task that can reliably finish in one session with no such need may mark the record `NOT_APPLICABLE` with a reason.

The record consolidates, rather than duplicates, the resume-checkpoint record in "Checkpoint-first resume and closure-only execution" and the gap ledger in "Context allocation and evidence custody". Reusing those fields, it must identify, where applicable:

- task or objective identity;
- authoritative base identity and current candidate identity (for example the base ref and the candidate commit and tree);
- current phase and highest accepted phase;
- accepted artifact and receipt identities, locations, hashes, freshness, and acceptance owner;
- unresolved dissent, contradiction, unknown, blocker, or deterministic invalidation;
- fix-cycle, PASS-streak, retry, and gate counters when the workflow uses them;
- capacity state (`SUFFICIENT`, `CONSTRAINED`, or `UNSAFE`);
- first incomplete dependency-ready phase;
- next authorized state;
- closure-ready status.

A replacement Lead reads this record and resumes at the first incomplete dependency-ready phase without reconstructing full history. The record carries identities, hashes, and material conclusions -- not embedded logs, diffs, or full evidence -- so it stays compact and never becomes a workflow controller or a repository-owned state store. A candidate change updates the candidate identity and resets any PASS-streak counter it records.

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

### Relationship to canonical Skeptic verification

This readiness gate is an ordinary, bounded gate: one initial pass plus at most two materially revised reruns (see "Checkpoints, failure, retry, and redesign"). It is not `Skeptic verification` as defined in `AGENTS.md`, and passing it must not be reported as satisfying the three-consecutive-PASS Skeptic verification criterion.

When a Task Prompt's terminal DONE explicitly requires pure or fix Skeptic verification, use the canonical definitions and bounds in `AGENTS.md` ("Verification vocabulary") rather than this readiness gate. State the RunSkeptic mode (pure or fix), the artifact identity/hash under review, the required consecutive-PASS count, the maximum fix cycles, the maximum total passes, and the remaining-budget early-stop rule in the Task Prompt's "System verification" section and copyable template.

## Copyable Task Prompt template

```text
# Task Prompt: <outcome>

Note: fields below that name a durable location, checkpoint, or state destination may read `NOT_APPLICABLE` with a stated reason for valid session-only work. See "Stateless library and runtime-owned state" above.

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

## Compact execution-state record (when handoff/resume/delegation/repeated-verification/cross-session is material; else NOT_APPLICABLE)
Consolidates the resume/checkpoint block above and the gap ledger; adds only:
Task/objective identity:
Authoritative base and current candidate identity (ref / commit / tree):
Accepted artifact+receipt identities, hashes, freshness, acceptance owner:
Fix-cycle / PASS-streak / retry / gate counters (if used):
Capacity state:
Next authorized state:

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
Deterministic promotion checks:
Accepting owner:
What acceptance authorizes:
What acceptance forbids:
Checkpoint / resume state:
Deterministic invalidation conditions:
Backward-transition authorization and evidence:
Failure / retry / rollback:
Next-state rule:

## Agent Prompts / Dispatch Tickets
<for each delegated phase, include or reference the bounded ticket>
Dispatch-fit gate (ticket + inherited context fits; else CONTEXT_HANDOFF_REQUIRED):
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
RunSkeptic mode (ordinary readiness gate / pure Skeptic verification / fix Skeptic verification):
Artifact identity/hash under review:
Required consecutive PASS count:
Maximum fix cycles:
Maximum total RunSkeptic passes:
Remaining-budget early-stop rule:

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
