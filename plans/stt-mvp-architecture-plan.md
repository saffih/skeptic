# STT MVP Architecture Plan

**Status:** Corrected architecture source of truth; implementation may begin only after the companion implementation plan and private role contracts pass review
**Repository:** `saffih/skeptic`
**Companion:** `plans/stt-mvp-implementation-plan.md`
**Private role contracts:** `concepts/stt/contracts/{planner,worker,validator}.md`
**Supersedes:** every earlier STT MVP architecture draft and correction layer

---

## 1. Purpose

Safe Target Task (STT) is a small durable runner for work that must be planned, executed sequentially, independently validated, resumable from files, recursively decomposable, and safe enough to modify a live workspace without relying on model-session memory.

The design target is:

```text
one recursive Task
one mechanical Lead
one deterministic Boundary
one Task-local append-only ledger
one frozen runtime per Run
one call per semantic or command operation
four Plan step kinds
```

STT is not the archived Target Task lifecycle. Existing code may supply reviewed leaf primitives, but it supplies no active orchestration, schema, compatibility, or lifecycle contract.

---

## 2. Core lifecycle

`Task` is the only recursive construct.

A normal Task performs:

```text
Mission
→ one Planner call
→ accepted ordered Plan
→ sequential Plan steps
→ one Validator call
→ terminal Task result
```

Failure shortens the same lifecycle:

```text
Planner or step failure / uncertainty
→ persist available evidence
→ mark later Plan steps SKIPPED when a Plan exists
→ one Validator call
→ terminal Task result
```

Every child Task performs the same lifecycle. A parent gives a child only an explicit mission reference or bounded mission text, authority no broader than the parent, exact declared inputs, required outputs, and frozen role bindings. The child Planner creates the child Plan.

A Task may not:

- receive an executable Plan from its parent;
- let Lead or Boundary invent or edit semantic Plan steps;
- execute a later step after an earlier step is non-`COMPLETE`;
- bypass Validator because planning or execution failed;
- call Planner, Worker, Command, or Validator more than once for the same Task or step;
- treat uncommitted call files as accepted lifecycle state;
- automatically replan, repair, or start a replacement Run.

### 2.1 Validator unavailable

A valid negative or uncertain Validator judgment is a successful Validator operation.

If the single Validator call produces no usable result, Boundary mechanically finishes the Task as:

```text
BLOCKED_UNKNOWN / VALIDATOR_UNAVAILABLE
```

The failed Validator call and its available evidence remain visible. There is no Validator retry.

### 2.2 New Runs after failure

A later Run is an ordinary new Run, not an automatic continuation protocol. Its explicitly supplied initial evidence may include:

- the original or revised mission;
- a previous terminal Task result;
- a previous Validator report;
- selected artifacts or observations from earlier Runs.

The new Planner decides what that evidence means and whether inspection, revalidation, repair, or a different plan is warranted. Prior reports are evidence, not instructions or executable Plans.

---

## 3. Status vocabulary

Step result statuses:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
SKIPPED
```

`SKIPPED` is permitted only for a later Plan step after a causal `FAILED` or `BLOCKED_UNKNOWN` planning or step outcome. It records the cause and contains no invented outputs.

Task result statuses:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
```

Mechanical floors:

```text
any BLOCKED_UNKNOWN planning or step outcome
→ Task floor is BLOCKED_UNKNOWN

otherwise any FAILED planning or step outcome
→ Task floor is FAILED

known missing, mismatched, unauthorized, or unproven required output
→ Task floor is FAILED

required-output identity or provenance cannot be established
→ Task floor is BLOCKED_UNKNOWN
```

Boundary may make the Validator judgment more severe to satisfy a mechanical floor. It never makes the Validator judgment less severe.

---

## 4. Roles and ownership

### Bootstrap

Creates a new Run from an immutable start specification, materializes the exact starting evidence once, freezes the runtime, and creates the root Task. Bootstrap does not plan the mission.

### Lead

A mechanical depth-first driver. It derives the next action from persisted state and compact Boundary receipts.

### Boundary

The mandatory deterministic firewall for identity, authority, context construction, invocation, persistence, validation, and compact returns.

Boundary performs integrity validation. It does not decide whether evidence is current enough or whether the mission is wise.

### Planner

A strong semantic role that creates one complete ordered Plan or returns a planning failure. It decides whether current evidence is sufficient for execution composition or whether evidence refinement is the rational next step, and expresses that decision as ordinary Plan steps or child Tasks.

### Worker

A bounded semantic role that performs one declared step against exact materialized inputs and produces staged artifacts. It cannot invoke commands or edit the target workspace.

### Command

A deterministic explicit process invocation executed once inside a fresh disposable command workspace populated from declared inputs. It never receives target-workspace write access.

### Mutation

Deterministic STT code that installs one exact previously accepted replacement manifest into the target workspace.

### Validator

A strong independent semantic role that analyzes the mission, Plan or planning failure, all step evidence, failures, skipped steps, child results, required outputs, and final workspace evidence. It returns one terminal judgment and one report useful to a future Run.

The private role contracts are part of the frozen runtime and define the exact semantic instructions.

---

## 5. Start specification and one-time evidence materialization

A new Run begins from one canonical `start-spec.json` containing:

- absolute target workspace root;
- one mission source with expected SHA-256 and byte size;
- exact read and write authority;
- named initial evidence sources with expected identity;
- named required outputs and artifact types;
- frozen Planner, Validator, and allowed Worker routes;
- an exact allowlist of Command routes, each binding executable identity, a fixed argv template, typed parameter slots, maximum timeout, and allowed environment keys;
- whether live providers are authorized.

Mission and initial evidence sources may be:

- an authorized regular file inside the workspace; or
- an explicitly supplied absolute regular host file.

Bootstrap opens each source once using no-follow regular-file validation, verifies its expected hash and size, and copies its exact bytes create-only into Run-owned bootstrap evidence. The persisted start specification binds those materialized copies.

After publication, STT never rereads the original mission or initial-evidence source path. The root Task consumes only the persisted copies. This preserves the exact starting evidence without a second post-freeze source read.

This one-time identity check is mechanical integrity, not semantic revalidation. Whether a fact, assumption, dependency, test result, or workspace condition must be checked again is a Planner decision expressed in the Plan.

Bootstrap sequence:

1. validate the proposed start specification without publishing Task lifecycle state;
2. create a unique Run root;
3. materialize and identity-bind mission and initial evidence exactly once;
4. persist the canonical start specification create-only, referring to those Run-owned copies;
5. freeze the exact STT runtime, private contracts, and selected provider adapters;
6. reconstruct and re-execute from frozen control;
7. acquire the Run writer lock;
8. reverify the persisted start specification and every Run-owned mission and initial-evidence copy by identity;
9. verify the selected provider routes and Command allowlist identities;
10. publish `run.json` binding the start specification, runtime manifest, route identities, and Command allowlist;
11. build the bounded root workspace index;
12. atomically create the root Task with `TASK_CREATED`;
13. start Lead.

A failure before `TASK_CREATED` leaves a diagnosable non-lifecycle Run root. A new start creates a new Run.

After `TASK_CREATED`, mission, authority, required outputs, runtime identity, routes, and live-provider authorization cannot change.

---

## 6. Control, persistence, and locking

Active executable control:

```text
${TMPDIR:-/tmp}/stt/<run-id>/control/
```

Persistent Run data:

```text
<workspace>/.stt/runs/<run-id>/
```

Invariant:

```text
Control executes.
Data persists.
Control never imports executable code from Run data.
Run data never controls imports.
```

Every mutating `start` or `run` invocation executes from verified frozen control and holds one OS-backed exclusive Run writer lock for lifecycle reads and writes.

A second writer fails before lifecycle action. `status` and `diagnose` are read-only and return `RUN_BUSY` when a writer prevents a trustworthy read.

No leases, stale-lock recovery, distributed locking, or concurrent Task execution exist.

Every Run owns one frozen runtime generation. Its external manifest records the exact allowlisted runtime files, private contracts, provider adapters, interpreter identity, hashes, sizes, and relevant modes. The manifest does not hash itself.

---

## 7. Task identity, authority, and workspace evidence

`task.json` is immutable after `TASK_CREATED`. It binds:

- Run and Task identities and canonical Task path;
- parent Task, parent Plan, and parent step when applicable;
- exact mission and initial-evidence references;
- runtime manifest and workspace-index identities;
- required output names and artifact types;
- exact read and write authority;
- Planner, Validator, allowed Worker routes, and allowed Command identities.

A child authority must be a subset of its parent authority.

Each Task owns a bounded deterministic `workspace-index.json` over its read authority. It describes available live workspace objects but grants no authority. Overflow is explicit; it is never silently truncated.

Boundary applies one object-open-time path-admission primitive. It rejects:

- absolute semantic workspace paths;
- traversal or containment escape;
- `.git` and `.stt` components;
- symlink components or leaves;
- special files;
- unauthorized paths.

When a Plan step consumes a live workspace path, Boundary opens it through this primitive and records the exact identity materialized for that step. Planner may require additional semantic checks, but Boundary never substitutes unverified bytes.

---

## 8. Plan

A Plan candidate exists only in the Planner call output directory. `PLAN_ACCEPTED` selects its exact path, hash, and byte size. There is no second canonical Plan copy.

There are exactly four step kinds:

```text
worker
command
mutation
task
```

Every step has:

- a stable unique lowercase ID;
- a clear description and success contract;
- exact named inputs;
- exact named outputs and artifact types;
- exact read or write authority needed by the step;
- only backward references to accepted earlier outputs or fixed system evidence from earlier Task steps.

A Command step selects one frozen allowed Command route and supplies only schema-valid named parameter values. Boundary renders the explicit argument vector from the route's fixed argv template; shell command strings and model-authored free-form argv are forbidden. Path parameters resolve only inside the disposable command workspace, and scalar parameters are bounded by the route schema.

A Task step carries one of:

- bounded child-mission text inside the accepted Plan;
- an exact backward reference to an earlier accepted mission artifact; or
- an exact reference to the current Task mission.

Its required-output contract is either explicitly declared for a narrower child mission or exactly references the current Task required-output contract for a same-mission child. Child authority and role or Command bindings may be equal to or narrower than the parent, never broader.

A Plan may not contain conditions, loops, arbitrary plugins, future references, implicit authority expansion, retries, or model-chosen live output paths.

Planner may use:

- a Worker step for bounded reasoning or artifact generation;
- a Command step for deterministic inspection or verification in a disposable copy;
- a Mutation step for an exact accepted replacement manifest;
- one or more Task steps when stable sub-missions warrant their own Planners and Validators;
- a same-mission Task step when materially expanded evidence should be reconsidered by a fresh Planner.

### 8.1 Planning forms

There are two semantic uses of the same `task` step.

**Execution composition** applies when current evidence is sufficient to identify stable sub-missions and how their validated outputs contribute to the parent mission. The parent Plan may contain several narrower child Tasks and may continue after each child returns. Each child has its own meaningful mission, required outputs, authority no broader than the parent, Planner, and Validator.

**Evidence refinement** applies when current evidence is insufficient to determine the correct work, but the Planner can identify useful authorized evidence-gathering steps. The Plan gathers that evidence and may then create a child Task that references the exact same mission and normally the same required-output contract, adds the accepted evidence, and invokes a fresh Planner. The earlier Planner does not predict the findings or preselect unsupported future work.

A Plan may combine both forms: it may execute known narrow child Tasks, gather additional evidence, and then use a same-mission child for the unresolved whole. A same-mission child is naturally the final substantive step because it owns the whole mission; when meaningful parent execution remains afterward, the child should normally have a narrower mission instead. This is Planner guidance, not a Boundary rule.

Creating a child is an ordinary next Plan step; it does not invoke the parent Validator. The child Validator runs when the child reaches its own end, and the parent Validator runs only after the parent Plan finishes or stops.

The Planner owns whether another child Task is rational. STT imposes no semantic progress threshold, child-count limit, Task-depth budget, or automatic termination policy. Each individual Task still has one sealed finite Plan, one Planner call, sequential execution, and one Validator call. A same-mission child is not a retry, loop inside the current Plan, or mutation of that Plan; it is a new immutable Task with its own fresh lifecycle.

If no acceptable Plan is produced, `PLANNING_FAILED` selects the exact planning-failure evidence and the Task proceeds to Validator:

```text
FAILED
→ a material contradiction, prohibition, impossibility, or authority mismatch
  is established from available evidence

BLOCKED_UNKNOWN
→ a material fact, decision, capability, evidence item, or authority is missing,
  cannot be resolved through authorized work in this Task, and prevents a
  trustworthy Plan
```

---

## 9. One-call operation environments

Each Planner, Worker, Command, and Validator operation owns exactly one create-only call directory. There are no attempt numbers or attempt budgets.

Semantic call layout:

```text
call/
├── request.json
├── disposition.json
├── in/                 # exact materialized inputs, read-only
├── out/                # only accepted semantic output location
├── stdout.log
├── stderr.log
└── raw-return.bin
```

Before invocation, Boundary:

1. constructs and persists the exact request from immutable accepted references;
2. creates empty input, output, and log locations;
3. appends the matching durable start event, consuming that operation even if later preparation fails;
4. materializes and verifies declared inputs;
5. verifies the selected adapter or Command identity and required isolation or argument policy;
6. invokes the operation once when preparation succeeds.

A preparation or materialization failure after the start event is persisted as `FAILED` or `BLOCKED_UNKNOWN` and does not permit another call.

After invocation, Boundary records process facts and available output, confirms termination when possible, validates schemas and identities, seals accepted regular files, and appends the matching lifecycle outcome. On interruption or resume, Boundary may mechanically terminate the exact owned local process group when its identity can be re-established; it never signals an uncertain or reused process identity and never relaunches the operation.

Operation dispositions are:

```text
ACCEPTED
FAILED
BLOCKED_UNKNOWN
```

Examples:

- valid declared output: `ACCEPTED`;
- explicit provider failure or structurally invalid output: `FAILED`;
- identity, confinement, termination, or integrity uncertainty: `BLOCKED_UNKNOWN`.

No disposition permits another STT dispatch in the same Run. Adapters must disable client-side retry behavior where supported and report the setting. STT does not claim that an opaque provider transport or remote service never retries internally; when that fact is unobservable, the report states `UNKNOWN`.

Uncommitted call output is forensic evidence only. It is never promoted after restart.

---

## 10. Step semantics

### 10.1 Worker

Worker receives one immutable step, exact inputs, exact output contract, and its fresh call directory.

It may analyze and produce staged artifacts. It may not invoke commands, edit the target workspace, write the ledger, alter the Plan, or decide Task completion.

### 10.2 Command

Command selects one frozen allowed Command route and supplies schema-valid named parameters, expected exit codes, and declared outputs. Boundary renders an explicit argument vector from the route's fixed template, uses a canonical disposable working directory and sanitized allowed environment, and enforces the route's maximum timeout. Shell command strings and model-authored free-form argv are forbidden.

Boundary creates a fresh command workspace and materializes the exact declared workspace and artifact inputs into it. STT passes only disposable paths and no target-workspace or authoritative Task path. The command is required to be a cooperative local operation with no intended external side effects. STT does not claim containment against a hostile executable that independently discovers other filesystem paths, network services, or external resources.

A Command call is never replayed. Timeout, crash, uncertain termination, invalid output, or Boundary interruption finishes the step `FAILED` or `BLOCKED_UNKNOWN` and proceeds toward Validator.

Intentional target-workspace changes require Mutation.

### 10.3 Mutation

Mutation installs one exact replacement manifest produced by an earlier accepted Worker output.

Before live change, Boundary:

1. persists the immutable mutation request and appends `STEP_STARTED`;
2. verifies exact write authority, destination paths, before-state identities, replacement bytes, and manifest;
3. persists exact before-images or absence markers;
4. appends durable `MUTATION_INTENT`.

Then deterministic code creates, replaces, or deletes regular files, verifies final identities, and emits exact accepted references for any declared Mutation outputs.

Before `MUTATION_INTENT`, deterministic preparation may resume without a second semantic or command call. After `MUTATION_INTENT` without `STEP_FINISHED`, mutation is never replayed: Boundary records current evidence, finishes the step `BLOCKED_UNKNOWN`, skips later steps, and invokes Validator. No automatic rollback occurs.

The MVP makes no multi-file atomicity claim.

### 10.4 Task

A Task step declares a child mission reference or bounded mission text, authority no broader than the parent, exact inputs, required outputs, and frozen role bindings.

A narrower child owns a stable sub-mission. A same-mission child references the exact parent mission and normally the exact parent required-output contract while adding accepted evidence inputs. In both cases the child receives a fresh Planner; it does not inherit the parent Planner's conversation, provisional reasoning, or uncommitted state.

After the parent `STEP_STARTED`, Boundary may create or resume the one canonical child path. Resuming an already-created child is continuation of persisted deterministic state, not a second call. Lead executes the child depth-first until terminal, then Boundary verifies the child result, terminal-output identities, provenance, and either the accepted child validation-report reference or exact `VALIDATOR_UNAVAILABLE` evidence before finishing the parent step.

Every Task-step result has fixed system evidence fields for the child terminal result and, when available, the accepted child validation report; otherwise it records the exact validator-unavailable evidence. These fields are distinct from the child's declared mission outputs. Later parent steps may consume fixed evidence from an earlier `COMPLETE` Task step only through explicit backward references, and the parent Validator always receives the available child evidence.

A non-`COMPLETE` child result establishes the same parent step floor, skips later parent steps, and still reaches the parent Validator.

---

## 11. Crash and resume rules

The ledger is the lifecycle commitment boundary.

On resume:

```text
PLANNER_STARTED without PLAN_ACCEPTED or PLANNING_FAILED
→ record PLANNING_FAILED / BLOCKED_UNKNOWN
→ invoke Validator once

STEP_STARTED for Worker or Command without STEP_FINISHED
→ record STEP_FINISHED / BLOCKED_UNKNOWN
→ skip later steps
→ invoke Validator once

STEP_STARTED for Task without STEP_FINISHED
→ create or resume the exact canonical child when mechanically valid
→ otherwise finish BLOCKED_UNKNOWN

STEP_STARTED for Mutation without MUTATION_INTENT
→ resume deterministic preparation

MUTATION_INTENT without STEP_FINISHED
→ never replay mutation
→ finish BLOCKED_UNKNOWN

VALIDATOR_STARTED without TASK_FINISHED
→ mechanically finish BLOCKED_UNKNOWN / VALIDATOR_UNAVAILABLE
```

A structurally corrupt Task ledger or immutable binding that prevents trustworthy state reconstruction is `INVALID_RUN`. STT reports it through `diagnose` and does not make another semantic call using untrustworthy state. This is not an ordinary planning or execution failure.

---

## 12. Boundary and Lead

Every substantive operation passes through one Boundary façade:

```text
Lead
→ Boundary
→ Planner / Worker / Command / Mutation / child Task / Validator
→ Boundary
→ persisted evidence
→ ledger commitment
→ compact receipt
→ Lead
```

Boundary validates identity, authority, paths, schemas, references, route bindings, call eligibility, child bindings, and output provenance. It does not judge mission wisdom, Plan quality, or semantic completion.

Conceptual Lead algorithm:

```text
advance(task):
    validate task, runtime, ledger, and immutable bindings

    if no committed planning outcome:
        if PLANNER_STARTED exists:
            Boundary.finish_abandoned_planning_unknown(task)
        else:
            Boundary.plan_once(task)
        return

    if planning outcome is non-COMPLETE:
        Boundary.validate_once_and_finish(task)
        return

    step = first Plan step without STEP_FINISHED

    if no step:
        Boundary.validate_once_and_finish(task)
        return

    if an earlier step is non-COMPLETE:
        Boundary.finish_later_steps_skipped(task, cause)
        Boundary.validate_once_and_finish(task)
        return

    Boundary.advance_step_once_or_resume_deterministic_state(task, step)

    if step becomes non-COMPLETE:
        Boundary.finish_later_steps_skipped(task, step)
        Boundary.validate_once_and_finish(task)
```

Lead carries references and compact receipts, not full Plans, source files, logs, patches, child histories, or model conversations.

---

## 13. Validator and terminal result

Before the Validator call, Boundary captures exact final identities for every Mutation destination, every required workspace output, and every additional live workspace path explicitly requested by the accepted Plan for final validation.

Validator receives a bounded final index referring to:

- mission, authority, and required-output contract;
- accepted Plan or planning-failure evidence;
- every finished and skipped step result;
- verified child results and child validation reports;
- selected command, mutation, and final workspace evidence;
- accepted substantive artifacts.

Validator receives no Planner or Worker conversation and no full child ledger.

Validator returns:

- `COMPLETE`, `FAILED`, or `BLOCKED_UNKNOWN`;
- a concise reason;
- one validation-report artifact;
- material findings and unresolved unknowns;
- references to terminal outputs selected only from accepted step outputs;
- optional non-executable guidance for a possible future Run.

Boundary verifies the report and every selected output, including any final workspace artifact reference emitted by an accepted Mutation result, applies mechanical floors, and appends `TASK_FINISHED`. Every later artifact read revalidates its recorded identity.

The validation report is durable evidence. It does not modify the current Plan, trigger another call, or create a replacement Run.

---

## 14. Ledger

Each Task owns one append-only hash-chained JSONL ledger. It is the lifecycle authority.

Event vocabulary:

```text
TASK_CREATED
PLANNER_STARTED
PLAN_ACCEPTED
PLANNING_FAILED
STEP_STARTED
MUTATION_INTENT
STEP_FINISHED
VALIDATOR_STARTED
TASK_FINISHED
```

`PLANNER_STARTED`, `STEP_STARTED`, and `VALIDATOR_STARTED` bind the exact immutable request before the corresponding fallible operation begins.

`STEP_FINISHED` records `COMPLETE`, `FAILED`, `BLOCKED_UNKNOWN`, or `SKIPPED`. A skipped step has no `STEP_STARTED`.

Every external artifact reference binds canonical path, SHA-256, byte size, artifact type, producer, and authority.

Current state is derived from the validated ledger and immutable referenced files. There is no mutable cursor.

A single torn trailing ledger fragment may be preserved and removed under the writer lock after validating the complete prefix. Interior corruption, hash mismatch, sequence gaps, or conflicting canonical files fail closed as `INVALID_RUN`.

---

## 15. Provider contract

The deterministic fake provider is required for qualification.

A live provider route is supported only when its frozen adapter can verify before `TASK_CREATED` that it provides:

- noninteractive invocation;
- bounded structured input and output;
- observable process termination where the host supports it;
- no semantic command, connector, or independent network-action tools;
- Boundary-enforced filesystem isolation limiting semantic writes to the call output directory;
- truthful requested-versus-observed provider/model reporting;
- client-side retries disabled where the provider exposes that control, with unobservable transport or service retries reported as `UNKNOWN`.

Prompt instructions or provider permission flags alone are not proof of isolation. If the configured host cannot enforce the contract, that live route is unsupported and start fails before `TASK_CREATED`.

Exact provider-specific flags and host isolation mechanisms are implementation details documented and tested by the adapter. STT does not build a generalized plugin framework.

---

## 16. Existing implementation policy

The active old STT lifecycle is replaced, not evolved or wrapped.

Implementation may inspect existing STT or archived Target Task code and reuse only small deterministic leaf primitives whose contracts are understood and independently tested, such as:

- canonical JSON encoding;
- SHA-256 and artifact-reference helpers;
- create-only atomic publication;
- append-only ledger mechanics;
- filesystem locking;
- no-follow path admission;
- subprocess termination helpers.

Reuse means copying or adapting the primitive into the new STT-owned implementation. Active STT must not import the old Runner, lifecycle reducer, capsule/delta workflow, Git workflow, review loops, old event schemas, or compatibility behavior.

The implementation Task Planner owns the concrete keep/copy/reject decisions after inspecting the actual branch state; this architecture predetermines only the boundary above. Before implementation, produce a short evidence table for every reused primitive:

```text
source
protected property
copy/adapt/reject decision
new owning module
focused test
```

Everything else remains available in Git history; no additional archive or compatibility layer is required.

---

## 17. Explicit non-goals

The MVP does not provide:

- retries inside a Run;
- automatic replanning, repair, or continuation Runs;
- concurrency or distributed scheduling;
- conditional or looping Plan syntax;
- generalized workflow plugins;
- automatic rollback;
- multi-file transactional mutation;
- orphan output adoption;
- Git staging, commits, pushes, merges, rebases, or publication;
- archived Target Task compatibility;
- hostile-command containment or external-side-effect containment;
- arbitrary filesystem-object mutation;
- execution-time escalation to an unbound provider or model;
- RunSkeptic, Fix Loop, Find Loop, or review ceremonies inside STT runtime.

---

## 18. Qualification obligations

Promotion requires focused deterministic proof of these behaviors:

1. root success performs one Planner call and one Validator call;
2. child and grandchild Tasks execute depth-first and each performs its own Planner and Validator calls;
3. one parent Plan may compose several narrower child Tasks and continue from their verified results;
4. evidence-gathering steps may feed a same-mission child that receives the exact parent mission, normally the exact parent required-output contract, accepted added evidence, and a fresh Planner without recalling the parent Planner;
5. a hybrid Plan may combine narrower child Tasks and a final same-mission evidence-refinement child;
6. child terminal results and accepted validation reports, or exact validator-unavailable evidence, are identity-bound fixed Task-step evidence available to explicitly referencing later parent steps and to every ancestor Validator;
7. planning failure distinguishes established `FAILED` from unresolved `BLOCKED_UNKNOWN` and reaches Validator without an invented Plan;
8. Worker failure or uncertainty skips later steps and reaches Validator;
9. child failure reaches every ancestor Validator;
10. Planner, Worker, Command, and Validator are never dispatched twice by STT for the same Task or step, including after restart, and interrupted owned process handling never relaunches them;
11. Validator unavailable becomes terminal `BLOCKED_UNKNOWN / VALIDATOR_UNAVAILABLE`;
12. a later Run may receive a previous terminal result and Validator report as explicit evidence without a continuation protocol;
13. changed, unauthorized, or identity-mismatched inputs are rejected when materialized or consumed;
14. Planner receives the frozen allowed Command route catalog, and Command selects only an allowed route; Boundary renders argv from a fixed typed template without a shell, and the process receives only disposable materialized paths;
15. Mutation intent is durable and uncertain mutation is never replayed;
16. atomic Task publication never exposes an authoritative Task without `TASK_CREATED`;
17. ledger torn-tail handling is narrow and interior corruption becomes `INVALID_RUN`;
18. frozen runtime remains authoritative after target-workspace STT source changes;
19. active STT has no runtime reachability to the old lifecycle.

The focused STT suite, frozen-runtime test, and full repository suite must pass. Fake-only execution proves mechanics but is not a releasable STT: Claude Code and Codex adapters must satisfy their frozen adapter contracts, and at least one configured live route must pass an authorized end-to-end smoke test on a supported host. Unsupported routes fail closed before `TASK_CREATED`.

---

## 19. Authoritative statement

```text
STT has one recursive construct: Task.

Bootstrap materializes the exact mission and explicit initial evidence once,
freezes one runtime, verifies the selected routes, creates the root Task, and
starts one mechanical Lead.

Every Task calls Planner at most once. An accepted Plan executes sequentially.
The first non-COMPLETE outcome is persisted, later steps are recorded SKIPPED,
and Validator is called at most once. Planning failure follows the same path.
No semantic or command operation is retried inside the Run.

Planner may compose several stable narrower child Tasks when the work is
sufficiently known, or gather evidence and create a same-mission child with a
fresh Planner when the correct work is not yet knowable. Both use the same Task
step and may be combined in one sealed Plan. Rationality is owned by Planner,
not by counters, retry policy, or Boundary.

Every substantive operation crosses deterministic Boundary. Workers operate only on materialized inputs outside the live target workspace.
Commands receive only allowed routes, Boundary-rendered argv templates, and
disposable materialized paths; hostile-command or external-side-effect containment
is not claimed. Only deterministic Mutation may change the target workspace, and durable
MUTATION_INTENT is the non-replay boundary.

A valid negative or uncertain Validator judgment is accepted. If Validator
produces no usable result, Boundary terminates the Task as visible
VALIDATOR_UNAVAILABLE / BLOCKED_UNKNOWN evidence.

A future Run may explicitly receive the prior mission, terminal result,
Validator report, and selected artifacts as evidence. Its new Planner decides
what to inspect, revalidate, repair, or redesign. No automatic continuation or
replanning protocol exists.

The Task ledger and immutable referenced artifacts, not model memory, determine
state. Active STT replaces the old lifecycle and may reuse only reviewed,
independently tested deterministic leaf primitives.
```
