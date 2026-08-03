# STT MVP Architecture Plan

**Status:** Architecture source of truth; ready for implementation after bundle installation
**Repository:** `saffih/skeptic`
**Documentation base:** `c3be467ec71924f63ea5bafa8f97908b594e8d15`
**Historical base:** `31451c8f45d5e9f2fe63434b37a2b7b02626a403`
**Companion implementation plan:** `plans/stt-mvp-implementation-plan.md`

---

## 1. Purpose

Safe Target Task, abbreviated STT, is a small durable system for executing one target mission through a planned, sequential, evidence-backed lifecycle.

STT protects:

- the separation between planning, execution, and validation;
- immutable accepted planning decisions;
- append-only orchestration evidence;
- sequential depth-first Task execution;
- bounded model context through file-backed evidence;
- honest reporting when execution or validation cannot be established;
- its active runtime when the Skeptic source repository is itself the target.

STT does **not** promise to prevent or reverse every filesystem, process, network, credential, remote, or external side effect produced by a Worker or command.

The preserved Target Task history under `archive/` is not an architecture source of truth. Active STT does not import or inherit that lifecycle.

---

## 2. Core lifecycle

STT has one recursive construct:

```text
Task
```

Every Task whose orchestration state remains valid enough for semantic processing follows:

```text
Mission
→ planning phase
→ immutable planning outcome
→ ordered Plan steps, when any
→ Validator
→ terminal result
```

This applies to:

- the root Task;
- every child Task;
- every nested descendant;
- research, implementation, inspection, and diagnostic work.

A Task may not:

- skip its planning phase;
- inherit an executable Plan from its parent;
- let the Lead invent or change steps;
- continue to later steps after a non-complete step;
- skip its Validator before semantic terminal completion;
- accept a semantic terminal result without Boundary validation.

Corrupt or conflicting orchestration state may stop as an invalid Run before a semantic Validator result can be accepted. Deterministic code must not fabricate a semantic audit from invalid control records.

---

## 3. Architecture in one paragraph

Bootstrap creates a unique temporary Run directory, copies the runnable Skeptic/STT source into it, verifies the copy, and re-executes from that frozen runtime. The target workspace remains a separate path. A mechanical Lead advances one deepest active Task at a time. Every outer STT operation passes through Boundary. Each Task performs a planning phase, persists one immutable planning outcome, executes an ordered Plan containing only `worker`, `command`, or `task` steps, invokes an independent Validator, and persists a terminal result. Workers and commands may change the live target. STT records their returns and best-effort observations rather than classifying their effects. When an operation is abandoned or uncertain, later steps stop and the Validator audits the facts that remain. A child Task may receive the same mission with richer evidence and plan it again without changing its parent Plan.

---

## 4. Explicit non-goals

The MVP does not provide:

- concurrency or parallel Tasks;
- distributed scheduling;
- a general workflow language;
- conditions, loops, or dynamic Plan editing;
- automatic rollback or workspace restoration;
- filesystem or process sandboxing;
- hostile-code containment;
- prevention of remote or external side effects;
- automatic Git commits, staging, pushes, merges, rebases, or publication;
- automatic semantic repair after validation failure;
- automatic replay of abandoned work;
- semantic recursion or progress detection;
- a maximum Task depth;
- a conversational `STT:` integration contract;
- compatibility with archived Target Task systems;
- RunSkeptic, Find Loop, or Fix Loop as part of the runtime lifecycle.

These exclusions are not partially implemented.

---

## 5. Physical locations

STT uses three distinct locations.

### 5.1 STT source repository

The original Skeptic repository containing the STT source used to create a Run.

Example:

```text
/home/user/code/skeptic
```

The source is consulted only while preparing the Run runtime.

### 5.2 Target workspace

The directory or repository the mission concerns.

Example:

```text
/home/user/code/project
```

The target may be:

- a plain directory;
- a Git repository;
- the Skeptic source repository itself.

### 5.3 Run directory

A unique temporary directory, normally:

```text
${TMPDIR:-/tmp}/stt/<run-id>/
```

It contains both the frozen runtime and all authoritative orchestration state:

```text
<run-root>/
├── runtime/
├── runtime-manifest.json
├── run.json
├── run.lock
└── root/
```

Authoritative STT state never lives under `<target>/.stt/`.

The Run directory should be created with owner-only permissions where supported. It must be disjoint from the target workspace.

A Run is resumable only while its Run directory still exists. Temporary-directory cleanup may make a Run non-resumable. STT reports that limitation honestly.

---

## 6. Frozen runtime

Before root Task creation, Bootstrap:

1. resolves the STT source repository;
2. resolves and validates the target workspace;
3. creates the unique Run directory outside the target;
4. copies the runnable Skeptic/STT checkout into `runtime/`;
5. excludes `.git`, caches, prior Run state, and generated temporary files;
6. records the exact copied-file manifest;
7. verifies every copied file by path, size, and SHA-256;
8. verifies that the copied source files did not change during copying;
9. records the interpreter and provider-launcher observations available to the host;
10. re-executes exclusively from the copied runtime;
11. creates all Run and Task state beside that runtime.

After re-execution:

- active STT imports resolve only from `<run-root>/runtime/`;
- active entry points execute only from `<run-root>/runtime/`;
- the target cannot replace the active runtime through ordinary relative-path edits;
- all Tasks in the Run share the same runtime identity.

When Skeptic is the target:

```text
source:         /home/user/code/skeptic
active runtime: /tmp/stt/<run-id>/runtime
 target:        /home/user/code/skeptic
```

The active Run may continue while target Skeptic files are edited, replaced, reorganized, or deleted.

This separation protects ordinary self-modification. It is not a security sandbox against a process running with the same operating-system authority.

---

## 7. Terms and roles

### Run

One root Task tree sharing:

- one Run identity;
- one temporary Run directory;
- one frozen runtime identity;
- one target workspace identity;
- one immutable set of role and provider bindings;
- one exclusive writer lock.

### Bootstrap

Pre-Task deterministic logic that creates a new Run or locates an existing Run. Bootstrap is not a Task and does not plan or execute the mission.

### Lead

The deterministic depth-first driver. It derives the next action and calls Boundary. It does not think about mission correctness.

### Boundary

The mandatory deterministic façade for outer operations, identity checks, persistence, lifecycle transitions, and compact receipts.

### Planner

A strong semantic role that decides whether and how one Task should proceed from its current mission and evidence.

### Worker

A semantic executor that performs one assigned step against the target and returns a bounded report.

### Command

An exact Planner-selected process invocation executed as one Plan step.

### Task step

A recursive child Task with its own mission, planning phase, steps, Validator, ledger, and result.

### Validator

An independent semantic investigator and judge that determines what the available facts establish after Task execution stops.

### Receipt

A compact structured reference returned to the Lead. Substantive bodies stay in files.

---

## 8. Bootstrap and Run identity

A new Run binds immutable values in `run.json`, including:

```json
{
  "schema": "stt.run.v1",
  "run_id": "run-...",
  "source_root": "/absolute/source/path",
  "target_root": "/absolute/target/path",
  "target_root_identity": {},
  "runtime_manifest_sha256": "...",
  "submission_sha256": "...",
  "provider_bindings": {},
  "role_bindings": {},
  "prior_run": null
}
```

The target-root identity must distinguish the admitted directory from a later delete-and-replace at the same path where the host exposes a stable observation. If the target can no longer be established as the admitted target, the Run stops visibly.

A materially changed submission, target, provider binding, role binding, or runtime requires a new Run.

The MVP entry point is CLI-only. A future conversational adapter may invoke the same Bootstrap contract without changing core behavior.

---

## 9. Task identity

Each Task owns an immutable `task.json` and `mission.md`.

A Task identity binds:

- Run identity;
- Task identity and deterministic Task path;
- mission identity;
- runtime identity;
- target identity;
- parent Task, parent planning outcome, and parent step when applicable;
- exact initial evidence references;
- required terminal outputs;
- same or narrower authority than its parent;
- allowed Worker bindings;
- Planner and Validator bindings.

A child Task lives at:

```text
steps/<index>-<step-id>/task/
```

A child mission is copied exactly from the accepted parent Task step. It may be byte-identical to the parent mission.

The parent supplies a child mission and evidence bindings, never a child Plan.

---

## 10. Planning phase

Each Task enters its planning phase once.

The Planner receives only bounded, persisted inputs:

- `mission.md`;
- Task authority and target root;
- required terminal outputs;
- allowed role choices;
- explicit initial evidence;
- outputs of earlier parent steps bound into the child;
- a deterministic bounded workspace index;
- fixed STT Planner instructions;
- the output schema.

The Planner does not:

- execute commands;
- edit the target;
- write Task state;
- change its authority;
- approve Task completion;
- call another Planner directly.

The planning phase produces one immutable `planning-result.json` with one disposition:

```text
PLAN
DECLINE
GAVE_UP
```

### 10.1 PLAN

`PLAN` contains one ordered immutable Plan. A zero-step Plan is valid and proceeds directly to validation.

### 10.2 DECLINE

`DECLINE` is a successful semantic Planner return. It means the Planner concludes that no feasible execution path exists under current authority, evidence, capabilities, dependencies, or constraints.

It must provide:

- concise reason;
- blocking facts;
- missing requirements;
- why further investigation or delegation is not useful.

No execution steps run. The Task proceeds to its Validator.

### 10.3 GAVE_UP

`GAVE_UP` is an operational planning outcome recorded by Boundary when the Planner invocation was launched or attempted but no accepted `PLAN` or `DECLINE` was obtained and the adapter abandoned the attempt.

It records:

- launch observation;
- settlement observation;
- available provider logs and return evidence;
- blocker reason.

No execution steps run. The Task proceeds to its Validator so the failed planning attempt is audited rather than silently stranded.

A malformed semantic return is evidence for `GAVE_UP`; it is not silently converted into a Plan or Decline.

`planning-result.json` is immutable once committed by `PLANNING_FINISHED`.

---

## 11. Planner trust and recursive same-mission delegation

STT trusts the Planner to decide decomposition.

STT imposes:

- no maximum Task depth;
- no same-mission delegation cap;
- no semantic non-progress detector.

A Planner may use this pattern:

```text
same mission
→ Worker or command gathers evidence
→ child Task receives the same mission plus richer evidence
→ child Planner decides the next Plan
```

This is ordinary recursive planning. It does not alter or replace the parent planning result.

The Planner must not delegate merely to postpone a decision. When no credible evidence-gathering or execution path remains, it should return `DECLINE`.

A defective Planner may recurse indefinitely or consume resources until an operator or host resource limit stops the Run. STT does not mechanically guarantee semantic termination. This is an explicit MVP trust decision.

---

## 12. Plan schema

A `PLAN` disposition contains canonical ordered steps.

Common fields:

```json
{
  "id": "stable-lowercase-id",
  "kind": "worker|command|task",
  "description": "bounded purpose",
  "inputs": [],
  "outputs": [],
  "success": {}
}
```

Rules:

- step IDs are unique within the Task;
- order is array order;
- later steps may reference only target inputs or accepted outputs from earlier steps;
- future-step references are invalid;
- child authority is equal to or narrower than parent authority;
- named output declarations are unique within a step;
- required semantic outputs are named;
- Boundary owns persisted request, return, report, and receipt paths;
- Plan acceptance checks structure, references, bindings, and authority, not semantic wisdom.

There are exactly three step kinds.

---

## 13. Worker step

A Worker performs one bounded semantic assignment against the live target workspace.

A Worker may:

- inspect target files;
- create, edit, move, and delete target files;
- use authorized tools;
- invoke commands;
- run tests;
- gather evidence;
- create named target outputs;
- report what it did.

A Worker does not:

- change the immutable planning result;
- write the ledger;
- change Run or Task identity;
- publish Boundary receipts;
- publish the Task terminal result;
- decide that the complete Task succeeded.

A Worker receives:

- one step;
- exact declared inputs and references;
- the target path;
- its responsibility and expected scope;
- allowed Worker binding;
- required report schema.

A Worker returns a bounded structured report containing:

```text
status
summary
named target outputs
best-effort created paths
best-effort changed paths
best-effort deleted paths
verification performed
warnings
unknowns
```

The changed-path report is evidence, not proof that every effect was observed.

Boundary verifies named target outputs by target containment, path, current size, SHA-256, and declared artifact type where applicable.

---

## 14. Command step

A command step executes the exact process invocation selected by the Planner.

Command fields include only what execution and later judgment require:

```text
argv
cwd
environment declaration
give-up policy
expected result conditions
inputs
named outputs
```

Rules:

- no shell interpretation by default;
- `argv` is an explicit array;
- the executable is resolved and observed where supported;
- `cwd` is explicit;
- environment construction is bounded and persisted;
- complete stdout and stderr are file-backed;
- exit status is persisted when available;
- launch, timing, return, settlement, and give-up observations are persisted;
- best-effort target before-and-after evidence may be recorded;
- a changed target is not an automatic failure;
- STT does not classify commands by their effects;
- STT does not automatically replay a command after it may have launched.

A command may affect the target, other local state, processes, services, networks, or remote systems. STT records only what it can observe and makes no completeness claim about hidden or external effects.

---

## 15. Task step

A Task step contains:

- a child mission;
- same or narrower child authority;
- exact initial inputs and evidence references;
- required child output names and types;
- allowed child role bindings.

When the Lead reaches a Task step:

1. Boundary validates the parent and step;
2. Boundary creates or verifies the deterministic child Task;
3. the Lead descends into the child;
4. the child performs the complete Task lifecycle;
5. Boundary validates the child result and named outputs;
6. Boundary records the child result as the parent step result;
7. the Lead returns to the parent;
8. later parent steps run only when the child step is complete.

A non-complete child stops later parent steps but does not bypass the parent Validator.

---

## 16. Boundary contract

Every outer STT operation passes through Boundary:

```text
Lead
→ Boundary
→ Planner / Worker / explicit command / child Task operation / Validator
→ Boundary
→ persisted evidence and accepted result
→ ledger event
→ compact receipt
→ Lead
```

Boundary owns:

- Run, runtime, target, and Task identity validation;
- planning-result identity and immutability;
- current-step eligibility;
- declared-input resolution;
- request construction;
- provider and command invocation through adapters;
- raw-return and log persistence;
- schema validation;
- named-output verification;
- child creation and child-result binding;
- lifecycle ledger appends;
- atomic/create-only control-file publication;
- compact receipts.

Boundary does not decide:

- whether the mission is wise;
- whether the Plan is semantically good;
- whether target changes are elegant;
- whether the Task mission is satisfied.

Workers and Validators may internally use tools or commands as part of their semantic invocation. Those internal actions are not separate STT Plan steps and do not each create another Boundary cycle.

---

## 17. Scope and safety boundary

Task and step scopes define:

- responsibility;
- context supplied;
- expected work area;
- named outputs;
- validation expectations.

They are cooperative contracts, not operating-system containment.

STT does not guarantee that an arbitrary Worker or command cannot:

- use absolute paths;
- alter unrelated files;
- access credentials;
- use the network;
- alter remote state;
- start background processes;
- discover the Run directory;
- temporarily change and restore state before observation;
- conceal effects.

STT avoids passing the Run-directory path as ordinary work context. That reduces accidental interference but is not a security boundary.

The precise safety claim is:

> STT protects its orchestration evidence, immutable planning outcome, sequential lifecycle, and uncertainty reporting. It does not prevent or roll back every target or external side effect.

---

## 18. Operation outcomes and giving up

STT does not impose one universal retry state machine.

Each adapter owns its practical mechanism for:

- launch;
- waiting;
- progress observation;
- timeout;
- cancellation;
- termination;
- deciding when further waiting is not useful.

Every outer operation persists common observations:

```text
launch_state: NOT_LAUNCHED | LAUNCHED | UNKNOWN
completion_state: RETURNED | GAVE_UP
settlement_state: SETTLED | UNSETTLED | UNKNOWN
logs and evidence references
```

Adapter-internal bounded attempts are permitted before the adapter returns its final outer outcome.

Once an outer Worker or command outcome is `GAVE_UP`:

1. preserve every available fact;
2. do not automatically invoke it again;
3. stop later Plan steps;
4. invoke the current Task Validator.

When settlement is `UNSETTLED` or `UNKNOWN`, target observations are provisional and the Task cannot conclude `COMPLETE`.

A returned operation may still report semantic failure. That also stops later steps and invokes the Validator.

A planning `GAVE_UP` proceeds directly to the Validator.

If the Validator invocation itself gives up without an accepted result:

- no semantic terminal result is fabricated;
- the Task remains operationally blocked in `NEEDS_VALIDATION`;
- later `stt run` does not silently clear the blocker;
- an operator may start a new Run using the available evidence.

---

## 19. Step results

A completed outer step has one immutable result with status:

```text
COMPLETE
FAILED
GAVE_UP
```

It includes:

- concise summary;
- named outputs;
- evidence references;
- launch, completion, and settlement observations where applicable;
- warnings and unknowns.

`COMPLETE` means the step’s declared local success conditions were met. It does not mean the Task mission is complete.

`FAILED` means the operation returned and its declared local success conditions were conclusively unmet.

`GAVE_UP` means the adapter abandoned the operation without an accepted conclusive return.

Later Plan steps run only after `COMPLETE`.

---

## 20. Validator

Every semantically processable Task ends through an independent Validator.

The Validator receives bounded references to:

- mission;
- planning result;
- every completed or abandoned step result;
- Worker reports;
- command logs and observations;
- verified child results and reports;
- current observable target state;
- explicitly selected prior evidence;
- required terminal outputs.

The Validator may investigate and verify. It may use read-oriented tools and verification commands within its invocation, but it must not intentionally repair the target, continue Plan execution, invent new steps, or replace the planning result.

The Validator returns:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
```

with:

- concise reason;
- validation report;
- material findings;
- unresolved unknowns;
- named terminal outputs.

The Validator judges the resulting facts, not merely intermediate step statuses.

It may return `COMPLETE` when it independently proves the mission is satisfied despite:

- a missing Worker return;
- an interrupted command;
- a locally failed or abandoned intermediate step.

It returns `FAILED` when the facts conclusively establish non-completion.

It returns `BLOCKED_UNKNOWN` when the evidence cannot establish either conclusion.

Boundary enforces only mechanical facts the Validator cannot override:

```text
invalid orchestration state
possibly active outer operation
missing or unverifiable required terminal output
```

If an outer operation may still be active, the terminal status cannot be `COMPLETE`.

Boundary may accept Validator-bound target outputs only after verifying current path, containment, size, SHA-256, and declared type.

The Validator report is reusable evidence for ancestor Validators and new Runs.

---

## 21. Failure propagation

For any non-complete ordinary step:

```text
stop later steps
→ invoke current Validator
→ persist current Task result
```

For a non-complete child:

```text
child Validator
→ child terminal result
→ parent child-step result
→ stop later parent steps
→ parent Validator
→ repeat upward
```

No direct failure-propagation operation writes ancestor terminal results. Every valid ancestor performs its own semantic audit.

---

## 22. Same-Run resume

Same-Run resume:

- uses the immutable planning result already committed;
- never replans;
- never changes the mission or bindings;
- never automatically repeats a Worker or command that may have launched;
- never silently clears a give-up or uncertainty;
- derives the exact next action from the ledger and immutable files;
- validates deterministic child paths and returned child results;
- uses only the copied Run runtime.

A file that exists without its committing ledger event is not accepted lifecycle state.

Conflicting canonical state makes the Run invalid. Same-Run resume does not adopt, overwrite, delete, or reinterpret conflicting control files semantically.

---

## 23. New Run and prior evidence

A new Run may receive:

- the original submission;
- the current target workspace;
- an optional prior Run directory.

Boundary exposes only verified prior references selected for the new Planner, such as:

- prior submission;
- prior planning result;
- prior terminal result;
- Validator report;
- selected Worker reports;
- selected command logs;
- named outputs.

Lifecycle state is never merged across Runs.

The new Planner may verify, continue, repair, replace, or decline previous work.

Uncommitted files from a prior Run may be presented as diagnostic evidence, but never as accepted lifecycle facts.

---

## 24. Ledger and durable publication

Each Task owns one append-only hash-chained JSONL ledger.

Minimal event vocabulary:

```text
TASK_CREATED
PLANNING_FINISHED
STEP_STARTED
STEP_FINISHED
TASK_FINISHED
```

Event bodies contain bounded references and identities, not substantive content.

Current state is derived from:

- validated ledger events;
- immutable Task identity;
- immutable planning result;
- persisted step results;
- verified child results;
- Validator result.

There is no mutable cursor file.

Control-bearing files are create-only or atomically published, flushed, reread, and identity-verified where the host supports those operations.

Task creation constructs the complete initial Task in a same-parent temporary directory, including `TASK_CREATED`, before atomic publication.

A single incomplete trailing ledger fragment may be preserved for diagnosis and removed under the exclusive writer lock after validating the complete prefix. Interior corruption, hash mismatch, sequence gaps, or conflicting publication fail visibly.

---

## 25. Task and Run layout

```text
<run-root>/
├── runtime/
├── runtime-manifest.json
├── run.json
├── run.lock
└── root/
    ├── task.json
    ├── mission.md
    ├── workspace-index.json
    ├── planning-result.json
    ├── ledger.jsonl
    ├── result.json
    ├── planning/
    ├── validation/
    └── steps/
        ├── 000-<step-id>/
        ├── 001-<step-id>/
        └── ...
```

A child Task is stored under its parent step:

```text
steps/<index>-<step-id>/task/
```

Step directories contain applicable files such as:

```text
request.json
raw-return.txt
result.json
receipt.json
stdout.log
stderr.log
observations.json
artifacts/
task/
```

Boundary supplies all orchestration paths. Semantic roles do not invent control-state locations.

---

## 26. Context discipline

Every outer model invocation must be reconstructible from persisted files and fixed role instructions.

Substantive bodies remain file-backed.

The Lead receives only compact receipts and identifiers.

The Planner receives mission, authority, initial evidence, required outputs, role choices, and workspace index.

A Worker receives one step and exact declared inputs.

The Validator receives a bounded final evidence index and selected referenced bodies.

Child history is referenced, not copied wholesale into parent context.

Actual hidden provider context and model isolation are reported as `UNKNOWN` unless the host exposes proof.

---

## 27. Model routing

Bootstrap freezes requested provider, model, and effort bindings for the Run.

Recommended default:

```text
strong Planner
→ economical Worker by default
→ stronger Worker only when Planner selects an allowed binding
→ strong independent Validator
```

Actual observed routing is recorded when available and otherwise reported as `UNKNOWN`.

No dynamic escalation ceremony is required. A changed binding creates a new Run.

---

## 28. Git and plain directories

STT works without Git.

When Git exists, observations may include:

- repository root;
- HEAD;
- branch;
- status;
- diff;
- selected object identities.

Git is not the authority for:

- Run or Task state;
- runtime identity;
- rollback;
- correctness;
- writer locking;
- terminal success.

STT does not automatically commit, stage, push, merge, rebase, or publish.

---

## 29. Public CLI

MVP commands:

```text
stt start \
  --workspace <target-path> \
  --submission <submission-file> \
  --provider <provider> \
  [--model <model>] \
  [--effort <effort>] \
  [--prior-run <run-directory>]

stt run --run-root <run-directory>
stt status --run-root <run-directory>
stt diagnose --run-root <run-directory>
```

### `start`

- validates source and target;
- reads and freezes the submission;
- validates optional prior-Run evidence;
- binds roles and providers;
- creates and verifies the temporary Run directory and copied runtime;
- re-executes from the copied runtime;
- acquires the exclusive writer lock;
- creates the root Task;
- begins the mechanical Lead;
- prints the Run directory and exact resume command.

### `run`

- invokes the entry point inside the copied runtime;
- acquires the writer lock before lifecycle action;
- validates Run, target, runtime, Task, and ledger identities;
- resumes the mechanical Lead without replanning.

### `status`

- uses the copied runtime;
- is read-only;
- uses a shared nonblocking lock where supported;
- reports `RUN_BUSY` without reading changing lifecycle state when a writer is active;
- reports compact current state, next action, blocker, and result reference.

### `diagnose`

- uses the copied runtime;
- is read-only;
- reports missing Run directory, identity mismatch, ledger corruption, conflicting publication, abandoned operation, unsettled process, or provider failure;
- never repairs automatically.

The MVP does not claim current `AGENTS.md` routing for conversational invocation.

---

## 30. STT-private contracts and implementation shape

STT owns private contracts:

```text
concepts/stt/contracts/planner.md
concepts/stt/contracts/worker.md
concepts/stt/contracts/validator.md
```

Current general contracts under `agents/` and `workflows/` do not govern STT runtime behavior.

Recommended package:

```text
concepts/stt/
├── __init__.py
├── bootstrap.py
├── runtime.py
├── run_lock.py
├── lead.py
├── task.py
├── ledger.py
├── plan.py
├── boundary.py
├── launcher.py
├── workspace.py
├── command.py
├── receipt.py
├── cli.py
├── contracts/
│   ├── planner.md
│   ├── worker.md
│   └── validator.md
└── providers/
    ├── __init__.py
    ├── fake.py
    ├── claude_code.py
    └── codex.py
```

Modules may be consolidated when that is simpler. Do not add abstractions solely to match the list.

---

## 31. Qualification scenarios

The MVP is accepted only after proving at least:

1. root Worker success;
2. root command success that changes the target;
3. Worker edits the target and returns verified named outputs;
4. target changes are evidence, not automatic command failure;
5. evidence gathering followed by a byte-identical child mission;
6. child and grandchild execution is sequential and depth-first;
7. Planner returns a structured Decline and Validator runs;
8. planning give-up proceeds to Validator;
9. child failure still invokes every valid ancestor Validator;
10. Worker give-up stops later steps;
11. command give-up with unsettled execution cannot yield Task Complete;
12. interrupted work changes the target and Validator independently proves completion;
13. Validator cannot conclude and returns Blocked Unknown;
14. same-Run resume preserves the planning result and never replans;
15. a new Run consumes a prior Validator report without merging state;
16. Skeptic target source can be changed or deleted while generation A continues from copied runtime;
17. source changes during runtime copying are detected;
18. deleted temporary Run directory is honestly non-resumable;
19. a competing writer fails before lifecycle action;
20. one torn ledger tail is handled narrowly and interior corruption fails;
21. conflicting control publication never produces a fabricated semantic result;
22. plain-directory execution succeeds;
23. Git-repository execution succeeds without Git as lifecycle authority;
24. active STT imports no archived Target Task modules;
25. deterministic provider-adapter tests pass without a paid provider invocation;
26. the full repository suite passes.

---

## 32. Remaining implementation parameters

These are not architecture blockers:

- exact provider CLI contracts available on the host;
- conservative request, return, log, and reference byte limits;
- default per-adapter wait and give-up settings;
- exact target-root identity observations available on each platform;
- durability and locking guarantees on non-local filesystems;
- pruning policy for old temporary Run directories;
- future conversational adapter behavior.

Implementation must choose conservative defaults, document them, and test them.

---

## 33. Authoritative statement

```text
STT has one recursive construct: Task.

Bootstrap copies the runnable Skeptic/STT source into a unique temporary Run
folder, verifies it, and re-executes from that frozen copy. The target workspace
is a separate path. All authoritative Run state lives beside the copied runtime.

Every semantically processable Task performs a planning phase, persists one
immutable planning outcome, executes an ordered Plan when present, invokes an
independent Validator, and persists a terminal result.

Planning may produce PLAN, DECLINE, or operational GAVE_UP. A Planner may gather
evidence and delegate the same mission to a child Task without any mechanical
depth cap. The Planner is trusted to decline when no credible path remains.

A Plan contains exactly three step kinds: worker, command, and task.

Workers and commands may change the live target. STT does not classify their
effects. It persists reports, logs, named outputs, and best-effort observations.

The Lead is mechanical. Every outer operation passes through Boundary. Boundary
owns identity, persistence, lifecycle transitions, output verification, and
compact receipts. It does not judge mission completion.

When work fails or is abandoned, later steps stop and the Validator investigates
the resulting facts. Intermediate failure does not mechanically determine the
Task result. A possibly active operation prevents COMPLETE.

Same-Run resume never replans or automatically repeats possibly launched work.
A new Run may use verified prior evidence without merging lifecycle state.

STT protects orchestration evidence and honest uncertainty reporting. It is not
a sandbox and does not prevent or roll back every target or external side effect.
```
