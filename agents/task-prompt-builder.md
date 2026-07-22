# Task-Prompt Builder

## Purpose

The Task-Prompt Builder is the single authoritative operation that turns a user objective, or an already-verified plan, into one verified, execution-ready Task Prompt.

It does not replace `agents/lead-agent-prompt.md`, `agents/task-prompt.md`, or `skeptic.md`. It applies them in one bounded sequence so the user does not have to separately request planning, RunSkeptic, Lead-Agent application, Task-Prompt construction, context protection, or prompt verification.

The builder never executes the Task Prompt it produces. It returns it unexecuted.

## Invocation aliases

These forms are equivalent. The text after the alias is the objective:

- `TP: <objective>`
- `Create task prompt for: <objective>`
- `Create a task prompt for: <objective>`
- `Task prompt for: <objective>`

See `AGENTS.md` for routing precedence between this operation and the generic prompt-construction route.

## Required current reads

On invocation, read and apply the actual current:

- `AGENTS.md`
- this file, `agents/task-prompt-builder.md`
- `agents/lead-agent-prompt.md`
- `agents/task-prompt.md`
- `skeptic.md`
- only additional current evidence materially required by the objective

Do not substitute memory, conversation summaries, or copied excerpts for any of these.

Record the identities (path and content hash, when material) of the governing contracts actually used. If material current-contract drift affects an already-verified plan's assumptions, requirements, authority boundary, or feasibility, return to plan production and repeat Plan Skeptic verification rather than building on the stale plan. Non-material drift is recorded and revalidated without silently changing the plan.

## Input classification

### Objective-only input

1. Create a compact objective record.
2. Determine whether the objective warrants a Task Prompt under the current `agents/task-prompt.md` ("When a Task Prompt is required").
3. If the task is trivial, reversible, and does not require task-level orchestration, return `TASK_PROMPT_NOT_REQUIRED` with a compact reason.
4. If material meaning or authority is unresolved, return a truthful conflict rather than guessing.
5. Otherwise, proceed to plan production.

### Verified-plan input

Accept a supplied plan as already-verified only when all of the following are present:

- exact plan bytes, or an authorized immutable artifact reference;
- the plan's SHA-256;
- the objective identity;
- three consecutive same-hash Plan Skeptic PASS receipts.

An unsupported "verified plan" label alone is insufficient. Validate the package (hash matches the supplied bytes, receipts name that same hash, objective identity is coherent) before using it. When valid, skip directly to Task-Prompt construction. When invalid or incomplete, treat the input as objective-only evidence and produce a new plan.

## Plan production and full Plan Skeptic verification

A Plan Author receives the objective, the current required contracts, and only narrowly relevant evidence — no unnecessary drafting history or raw repository dump.

The plan proportionately defines: objective and observable terminal DONE; starting-state verification; authority and source-of-truth order; scope, exclusions, and protected state; task/risk classification and the smallest credible alternative; roles, ownership, and model/effort routing; Lead and worker context protection; dependency-ready phases; evidence and cross-context persistence; deterministic and behavioral verification; repair, retry, futility, integration, and closure; assumptions and residual risk.

**Plan Skeptic verification** is this Builder's specialization of the canonical **Fix Skeptic verification** defined in `AGENTS.md` ("Verification vocabulary"): the artifact identity is fixed to the exact plan bytes and their SHA-256, so a plan-byte change is the fix event that resets the consecutive-PASS count to zero. Do not restate the canonical fix procedure here; apply it as written in `AGENTS.md`, run on the exact plan bytes via the actual current RunSkeptic procedure (`skeptic.md`).

Builder-specific bounds and receipts:

- at most two plan-changing repair cycles;
- at most seven RunSkeptic reviews total;
- stop early when the remaining review allowance cannot still produce three consecutive passes;
- preserve every required RunSkeptic receipt and the plan SHA-256 at each attempt.

Failure returns `PLAN_VERIFICATION_BLOCKED` with the latest plan bytes, hash, receipts, findings, and blocker.

Fresh bounded reviewer contexts are preferred when the runtime provides genuine isolation. When it does not, sequential reviews may satisfy this project's definition of Plan Skeptic verification but must not be described as independent.

After three consecutive `PASS` verdicts on one unchanged hash, freeze: the verified plan, its SHA-256, the three PASS receipts, the objective identity, and any unresolved assumptions.

## Task-Prompt construction

Task-Prompt construction is the bounded objective of a fresh Boundary Agent dispatched by the Lead, per the current `agents/lead-agent-prompt.md`.

Before drafting, this Boundary Agent reads and applies the current `AGENTS.md`, `agents/lead-agent-prompt.md`, `agents/task-prompt.md`, the verified plan, and only additional evidence needed to operationalize it. It receives the verified plan and compact evidence — not the full Plan Author or reviewer history.

It produces:

1. One complete, minimum-sufficient Task Prompt following the `agents/task-prompt.md` contract and template. The Task Prompt must explicitly appoint its execution Lead, require it to read and apply the current repository contracts, bind task-specific authority/scope/exact-DONE, define starting-state checks and source-of-truth order, define dependency-ready phases, define bounded child tickets and compact receipts, protect Lead context and closure capacity, define evidence identity and persistence where context boundaries require it, define tests/behavioral checks/repair/retry/futility/integration/closure, define truthful blocked states, remain no larger than the verified plan requires, and not execute itself.
2. A compact **semantic traceability map**: every material plan requirement mapped to the Task-Prompt section that preserves it, or marked `NOT_APPLICABLE` with a reason. Semantic consolidation is allowed; silent omission, weakening, or unauthorized expansion is not. Assumptions are kept separate from verified facts.

## Unified Prompt-Build Verification

Use one bounded, read-only Prompt-Build Checker against the exact candidate Task Prompt, its SHA-256, the verified plan, and the traceability map. For serious tasks, use a fresh context that did not draft the candidate; if the runtime cannot provide that independence and independence is materially required, return `BLOCKED`, otherwise disclose that the review was same-context.

Run the complete checklist in one pass:

**A. Plan fidelity and provenance** — verified-plan SHA-256 recorded; every material plan requirement preserved or justified `NOT_APPLICABLE`; no unauthorized omission, weakening, expansion, or added objective; assumptions separated from verified facts.

**B. Task-Prompt completeness** — observable terminal DONE; starting state, authority, source-of-truth order, scope, exclusions, protected state explicit; every material phase has owner, dependencies, inputs, allowed actions, output, acceptance, failure route, and next state; required testing, repair, integration, external verification, and closure present; no intermediate state mistaken for DONE; truthful blocked states.

**C. Dependency integrity** — valid entry phase and complete path to DONE; inputs available before consumption; phase graph acyclic (including semantic cycles such as an artifact requiring approval from its own output); verification follows artifact freeze; integration follows required verification; optional work cannot block mandatory completion; deterministic topological-order check when phases are structurally represented.

**D. Lead-Agent application** — execution agent explicitly appointed Lead; required to read and apply current contracts; Lead retains task-level ownership; child roles bounded; no worker can promote its output to task-level DONE; model/effort choices proportionate and feasible.

**E. Lead-context protection** — Lead receives compact authoritative inputs, not full histories; child roles receive bounded Dispatch Tickets; worker receipts are compact and checkable; raw logs/discussions/large outputs stay outside Lead context absent a named dispute; closure capacity protected by a measurable reserve or substitute; pre-exhaustion stop defined; a replacement Lead could resume from a verified compact handoff if handoff is materially required; the first incomplete phase is identifiable without reconstructing the whole task.

**F. Execution feasibility** — the whole workflow, including verification and closure, can fit; expensive phases and prerequisites identified; retries/reviews bounded; optional work cannot consume the completion reserve; unavailable tools/permissions/credentials/isolation are checked before expensive work; truthful failure/blocked outcome; process cost proportionate to task value and risk.

**G. Internal consistency and authority** — paths, refs, hashes, models, role names, permissions, and pass counts agree; the stated review budget can mathematically satisfy its gate; Reviewer permissions are read-only where independence is claimed; no instruction both requires and forbids the same action; fallback routes preserve acceptance criteria; no lower-authority role receives a higher-authority decision.

**H. End-to-end Lead dry run** — without mutating the target, walk through: the Lead's first action; the evidence completing preflight; the first dependency-ready phase; the receipt/evidence returned to the Lead; the continue/repair/retry/handoff/stop rule; the evidence permitting integration; the evidence permitting terminal DONE. If the walkthrough cannot reach DONE without guessing, the verdict cannot be `READY`.

**I. Proportionality** — permanent doctrine referenced rather than copied; no unnecessary roles, reviews, tests, persistence, or phases; recursive self-application bounded; no materially smaller prompt preserves the verified plan, evidence, context protection, authority, reversibility, and closure.

Every receipt names the exact Task-Prompt SHA-256, marks each of the nine categories `PASS` or `FAIL` with compact evidence pointers, states the final verdict, and names the required next state.

Verdicts and routing:

- `READY` — freeze the exact final Task-Prompt SHA-256 and traceability map.
- `REPAIR_REQUIRED` — a fresh Boundary Agent dispatched by the Lead repairs the Task Prompt; rerun the complete checklist against the new candidate.
- `PLAN_DEFECT` — return to plan production; count the change against the plan-repair budget; repeat full Plan Skeptic verification; then rebuild the Task Prompt.
- `BLOCKED` — preserve the exact candidate identity and name the unavailable requirement.

Any Task-Prompt byte change invalidates the previous verdict; `READY` applies only to the exact final Task-Prompt SHA-256.

Bounds:

- at most two Task-Prompt repair cycles;
- at most three complete Prompt-Build Verification runs.

## Builder output

Return:

- the verified plan (or authorized immutable reference), its SHA-256, and the governing-contract identities used;
- the three same-hash Plan Skeptic PASS receipts;
- the final Task Prompt and its SHA-256;
- the compact semantic traceability map;
- the Prompt-Build Verification verdict and its checklist receipt;
- execution-time assumptions and any blocked-capability notes;
- explicit confirmation that the Task Prompt was not executed.

## Non-execution boundary

The builder's terminal output is a verified, unexecuted Task Prompt. Executing that Task Prompt is a separate, later authorization and a separate task.

## Proportionality

`TASK_PROMPT_NOT_REQUIRED`, `PLAN_VERIFICATION_BLOCKED`, and the Prompt-Build Verification verdicts are operational outcomes of this builder, not new Skeptic categories; they do not change `PASS`, `ACTION`, `DECOMPOSE`, or `CONFLICT` as defined in `skeptic.md`.

This file does not add a script, controller, permanent state or receipt directory, or separate checklist files. Bounded evidence and receipts for a given run belong to the invoking runtime's authorized storage, not to this repository.
