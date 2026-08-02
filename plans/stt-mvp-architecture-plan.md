# STT MVP Architecture Plan

**Status:** Corrected, implementation-ready architecture source of truth  
**Repository:** `saffih/skeptic`  
**Historical base:** `31451c8f45d5e9f2fe63434b37a2b7b02626a403`  
**Original accepted-plan commit:** `ec9e8771e4bf9a4ecd03d3d9cd5ff0b1486d9887`  
**Supersedes:** the previous contents of this file at `ec9e8771e4bf9a4ecd03d3d9cd5ff0b1486d9887`  
**Companion implementation plan:** `plans/stt-mvp-implementation-plan.md`

---

## 1. Purpose

Safe Target Task, abbreviated STT, is a small durable execution system for work that must be:

- planned before execution;
- executed sequentially;
- validated after execution;
- resumable from persisted files;
- bounded in model context;
- safe when modifying a live workspace;
- recursively decomposable without a separate subtask mechanism;
- able to modify its own source while continuing from a frozen runtime.

The architecture is intentionally smaller than the later Target Task systems.

The preserved history under:

```text
archive/target-task-overbuilt-20260802
```

is not an architecture source of truth. It may be consulted only for narrowly reusable deterministic primitives or lessons. No lifecycle, state machine, compatibility layer, recovery framework, review ceremony, or orchestration protocol is inherited from that archive.

---

## 2. Fundamental invariant

STT has one recursive construct:

```text
Task
```

Every Task always performs:

```text
Mission
→ Planner
→ ordered Plan steps
→ Validator
→ terminal result
```

This applies without exception to:

- the root Task;
- every child Task;
- every nested descendant;
- research Tasks;
- implementation Tasks;
- diagnostic Tasks;
- inspection Tasks.

A Task may not:

- skip its Planner;
- receive an executable Plan from its parent;
- let the Lead invent or change Plan steps;
- continue past a failed or blocked step;
- skip its Validator;
- become terminal without a Validator-produced result accepted through Boundary.

A parent Planner may include a Task step. That step contains a child mission and delegated authority. The child then performs the complete ordinary Task lifecycle.

There is no special subtask workflow.

---

## 3. Architecture in one paragraph

Bootstrap recognizes an STT invocation, finalizes the root mission, freezes the runnable STT control plane, creates persistent run data, and starts a mechanical Lead. The Lead advances exactly one deepest active Task at a time. Every substantive operation passes through Boundary. Each Task receives a mission, calls a strong Planner, executes an immutable ordered Plan, calls a strong independent Validator, and persists a terminal result. A Plan step is one of `worker`, `command`, `mutation`, or `task`. Child Tasks live at deterministic paths under their parent steps and return named verified outputs through the same result schema as any other step. All intended workspace changes are staged by Workers and installed by deterministic mutation code. If mutation completion is uncertain, it is never replayed. Every ancestor still runs its Validator before failure or uncertainty reaches the root.

---

## 4. Explicit non-goals

The MVP does not provide:

- concurrency;
- parallel Tasks;
- distributed scheduling;
- a general workflow language;
- automatic rollback;
- workspace snapshots;
- transactional cutover;
- recovery packs;
- restoration into another workspace;
- candidate commit freezing;
- automatic commits, staging, pushing, merging, rebasing, or publication;
- remote integration verification;
- Fix Loop or Find Loop ceremonies;
- repeated three-pass convergence;
- explicit ADVANCE protocols;
- automatic semantic replanning after validation failure;
- compatibility with archived Target Task systems;
- hostile-code containment;
- arbitrary filesystem-object support;
- automatic escalation to unbound models;
- writable command steps.

These features are not partially implemented in the MVP.

---

## 5. Terms

### Run

One root Task tree sharing:

- one run ID;
- one persistent run directory;
- one frozen runtime generation;
- one immutable set of provider and role bindings.

### Task

The only recursive execution construct.

### Bootstrap

Pre-Task logic that creates or resumes a Run. Bootstrap is not a Task.

### Lead

The mechanical depth-first driver.

### Boundary

The mandatory deterministic context, identity, authority, persistence, and integrity firewall.

### Planner

A strong semantic role that converts one Task mission into one executable ordered Plan.

### Worker

A bounded semantic role that produces staged artifacts. A Worker never edits the live workspace.

### Command

A deterministic non-mutating process invocation.

### Mutation

A deterministic installation of an exact replacement manifest into the live workspace.

### Validator

A strong independent semantic role that judges Task completion after execution stops.

### Receipt

A compact structured return to the Lead. A receipt contains references and state transitions, not substantive bodies.

---

## 6. Bootstrap

Bootstrap happens before the root Task.

Bootstrap responsibilities:

1. recognize the exact conversational prefix:

   ```text
   STT:
   ```

2. distinguish a new run from an explicit resume;
3. use the intelligence of the invoking agent to refine the proposed root mission;
4. define the root authority;
5. bind the host provider adapter;
6. bind the Planner, Validator, and allowed Worker routes;
7. create a unique run ID;
8. prepare the unique persistent run directory;
9. freeze or reconstruct the STT runtime and re-execute from frozen control without reading Task lifecycle state;
10. acquire the Run's exclusive writer lock in the frozen process before publishing or reading lifecycle state;
11. persist the root Task's explicit initial evidence references and a bounded deterministic workspace index over its read authority;
12. create the root Task;
13. launch or resume the mechanical Lead.

Bootstrap may think about:

- mission wording;
- scope;
- authority;
- model bindings;
- run-location selection;
- restoration failures.

After root `TASK_CREATED`, Bootstrap may not change:

- the mission;
- Task authority;
- runtime identity;
- role bindings.

A materially changed mission creates a new Run.

Bootstrap does not plan or execute the root mission. The root Task still calls its own Planner.

Root initial evidence comes from explicit host or CLI references plus one bounded deterministic workspace index containing canonical paths and file metadata within the root read authority. Each Task owns `workspace-index.json`, bound from `task.json`; Boundary creates a child index from the child's narrowed read authority using the same path-admission rules, so `.git`, `.stt`, symlinks, special files, and containment escapes are excluded. If enumeration exceeds the configured index limit, the index contains deterministic directory summaries and explicit overflow markers rather than silently truncating. The index is context for planning, not permission to read outside authority. When no explicit evidence is supplied, the Planner may still create bounded inspection Worker or child Task steps from the index.

---

## 7. Control and data separation

Active executable control:

```text
${TMPDIR:-/tmp}/stt/<run-id>/control/
```

Persistent run data:

```text
<workspace>/.stt/runs/<run-id>/
```

Invariant:

```text
Control executes.
Data persists.
Control never imports executable code from run data.
Run data never controls imports.
```

The active control directory is disposable.

The persistent runtime bundle is authoritative for reconstruction.

Every mutating `stt start` or `stt run` invocation reconstructs or freezes and re-executes from the Run's control generation, then holds one OS-backed exclusive writer lock on `<run-root>/run.lock` before reading or writing lifecycle state. A second writer fails visibly and performs no lifecycle action. `status` and strictly read-only `diagnose` acquire a shared nonblocking lock; when a writer is active they report `RUN_BUSY` without reading changing lifecycle state. The MVP supports hosts where this lock primitive is available and fails closed otherwise; it does not implement leases, stale-lock recovery, distributed locking, or concurrent Task execution.

STT's own control code is authorized to write persistent run data under the selected `.stt/runs/<run-id>/` directory. Plan steps, Workers, commands, and workspace mutation manifests are never authorized to target `.stt`. Internal run-data persistence and target-workspace mutation are separate authorities.

---

## 8. Frozen runtime

Every root Run freezes one runtime generation before root planning begins.

All Tasks in the Run use the same generation.

Children do not freeze new runtimes.

### 8.1 Runtime contents

The bundle is generated from an explicit allowlist, not a directory-wide copy.

Expected contents are a literal manifest generated from a maintained runtime allowlist:

```text
scripts/stt.py
each exact required `concepts/stt/` Python module named in the manifest
concepts/stt/contracts/planner.md
concepts/stt/contracts/worker.md
concepts/stt/contracts/validator.md
exact selected provider-adapter files
exact required package initializers
runtime-manifest.json
```

No wildcard is evaluated during reconstruction. The freeze operation resolves the maintained allowlist to exact paths and records those paths in the manifest.

The bundle excludes:

```text
.git/
.stt/
tests/
caches/
plans/
archive/
unrelated project source
```

`skeptic.md` and `skeptic-questions.md` are excluded unless an actual STT-private role contract explicitly requires them. The MVP lifecycle does not require RunSkeptic.

### 8.2 Persistent runtime bundle

Recommended path:

```text
<run-root>/runtime/bundle/
<run-root>/runtime/manifest.json
```

The manifest records for every bundled file:

- canonical relative path;
- byte size;
- SHA-256;
- executable mode where relevant.

It also records, when observable:

- Python interpreter realpath and version;
- selected provider-adapter identity and exposed version;
- required external dependency identities needed to invoke the provider.

STT freezes its own control source and role contracts. It does not freeze the operating system, interpreter installation, provider service, or complete host environment. Resume fails visibly when a required recorded external dependency is missing or incompatible.

The persistent bundle is create-only for the Run. “Immutable” means identity-bound and never intentionally overwritten; the MVP does not depend on filesystem immutable flags.

### 8.3 Active runtime

Bootstrap reconstructs the active control directory from the persistent bundle, verifies the manifest, makes files read-only where supported, and re-executes from that control path.

After re-execution:

- Python imports resolve from frozen control;
- executable modules are not loaded from run data;
- executable modules are not loaded from the target workspace’s possibly modified STT source.

If the temporary control directory disappears, it is reconstructed only from the persistent bundle.

---

## 9. Persistent run layout

```text
<workspace>/.stt/runs/<run-id>/
├── run.lock
├── run.json
├── runtime/
│   ├── manifest.json
│   └── bundle/
└── root/
    ├── task.json
    ├── mission.md
    ├── workspace-index.json
    ├── plan.json
    ├── ledger.jsonl
    ├── result.json
    ├── planning/
    │   └── attempt-001/
    ├── validation/
    │   └── attempt-001/
    └── steps/
        ├── 000-<step-id>/
        ├── 001-<step-id>/
        └── ...
```

There is no separate `tasks/` directory.

A child Task for a Task step always lives at:

```text
steps/<index>-<step-id>/task/
```

That child uses the exact same Task layout.

---

## 10. Task identity and authority

`task.json` is immutable after `TASK_CREATED`.

Required fields:

```json
{
  "schema": "stt.task.v1",
  "run_id": "run-...",
  "task_id": "root.000.002",
  "task_path": "root/steps/000-research/task",
  "parent_task_path": "root",
  "parent_plan_sha256": "...",
  "parent_step_id": "research",
  "mission_sha256": "...",
  "runtime_manifest_sha256": "...",
  "workspace_index_sha256": "...",
  "initial_inputs": [],
  "required_outputs": [],
  "authority": {
    "workspace_root": "/absolute/path",
    "read_paths": ["src", "tests"],
    "write_paths": ["src/report.py", "tests/test_report.py"]
  },
  "role_bindings": {
    "planner": "strong-planner",
    "validator": "strong-validator",
    "workers_allowed": ["economical-worker", "strong-worker"]
  }
}
```

For the root Task, parent fields are `null`.

A child Task must bind:

- parent Task identity;
- parent accepted Plan identity;
- parent step identity;
- child mission identity;
- common runtime identity;
- the exact child initial-input references declared by the parent Task step;
- the child required-output names and artifact types declared by that step.

Child authority must be a subset of parent authority.

Authority expansion is invalid.

---

## 11. Mission

Each Task owns:

```text
mission.md
```

A child mission is copied from the accepted parent Task step exactly.

The parent does not supply a child Plan.

Mission content should define:

- objective;
- scope;
- constraints;
- required outputs;
- success criteria;
- prohibited actions.

The mission is immutable after `TASK_CREATED`.

---

## 12. Planner

Every Task calls its Planner exactly once successfully before execution.

Provider attempts are bounded by a finite `maximum_attempts`. Planner, Worker,
and Validator never automatically retry a completed provider return: malformed,
schema-invalid, identity-mismatched, rejected, explicitly failed, or
semantically unsuccessful returns are persisted as evidence and stop the
current invocation. Automatic retry is permitted only for a `transport timeout`
whose termination state is exactly `TIMED_OUT_CONFIRMED_TERMINATED` while
`attempt_count < maximum_attempts`. Otherwise persist `TERMINATION_UNKNOWN`
when termination is not positively established and fail closed. No semantic
corrective planning, replanning, or generalized retry framework exists.

If no acceptable Planner result is available, the Task remains nonterminal in `NEEDS_PLAN`. The current `stt run` invocation stops with a compact operational blocker and may be resumed. Infrastructure failure does not create a fake Task terminal result. Every attempt directory contains a canonical persisted disposition binding `dispatch_id`, `role`, `attempt_number`, `request_identity`, `completion_kind`, `termination_state`, `retry_permitted`, `blocker_code`, and `raw_return_reference`. Its closed vocabulary is `ACCEPTED`, `COMPLETED_NONRETRIABLE`, `TIMED_OUT_CONFIRMED_TERMINATED`, and `TERMINATION_UNKNOWN`.

Before invoking Planner, Worker, or Validator, Boundary reads the latest disposition. `ACCEPTED` continues the lifecycle; `COMPLETED_NONRETRIABLE` returns its persisted blocker without reinvocation; `TIMED_OUT_CONFIRMED_TERMINATED` permits a new attempt only while `attempt_count < maximum_attempts`; and `TERMINATION_UNKNOWN` fails closed without reinvocation. An exhausted budget returns the persisted blocker. This applies after process restart and on repeated `stt run` commands. Planner remains `NEEDS_PLAN`, an unaccepted Worker step remains unfinished, and Validator remains `NEEDS_VALIDATION`, while each returns the same blocker without reinvocation. A new external operator decision requires a new Run; MVP resume never silently clears the blocker.

The first output that passes:

- provider-return identity checks;
- Plan schema validation;
- Task authority validation;
- binding validation;

is accepted and immutable.

The MVP does not perform a separate semantic Plan review or Planner repair loop.

A poor but structurally valid Plan may later lead to `FAILED`. This is an honest limitation of the small architecture.

### 12.1 Planner inputs

The Planner receives only:

- `mission.md`;
- Task authority;
- role-binding choices available to the Task;
- the Task's persisted `initial_inputs`;
- the Task's required-output contract;
- the deterministic workspace index over its read authority;
- fixed STT Planner instructions;
- exact output schema.

Bootstrap owns root initial-input selection. A parent Task step owns child initial-input selection. Boundary resolves and validates those references mechanically; neither Lead nor Boundary chooses semantic evidence.

The Planner does not receive:

- the full Task ledger;
- broad workspace context;
- prior conversations;
- archived Target Task history;
- unrelated files.

### 12.2 Planner output

The Planner returns one complete ordered Plan.

The Planner does not:

- execute;
- mutate the workspace;
- write Task state;
- approve its own work;
- select authority beyond the Task;
- invent writable artifact paths;
- recursively call another Planner.

---

## 13. Plan schema

`plan.json` is canonical JSON and immutable after `PLAN_ACCEPTED`.

Required top-level fields:

```json
{
  "schema": "stt.plan.v1",
  "task_id": "root",
  "mission_sha256": "...",
  "runtime_manifest_sha256": "...",
  "steps": []
}
```

A Plan step has:

```json
{
  "id": "stable-lowercase-id",
  "kind": "worker|command|mutation|task",
  "description": "bounded purpose",
  "inputs": [],
  "outputs": [],
  "success": {}
}
```

Rules:

- step IDs are unique within the Task;
- IDs use lowercase ASCII letters, digits, and hyphens;
- order is array order;
- a step may reference only workspace inputs or outputs from earlier steps;
- a step may not reference future steps;
- paths must be canonical Task-authorized relative paths;
- output names are unique within a step;
- every semantically required artifact is a named output;
- Boundary assigns exact persisted request and result paths.

There are exactly four step kinds.

---

## 14. Worker step

A Worker step performs bounded semantic work and writes staged artifacts only.

Example:

```json
{
  "id": "prepare-report-change",
  "kind": "worker",
  "description": "Prepare replacements for report JSON mode and focused tests.",
  "worker_binding": "economical-worker",
  "instructions": "Implement only the declared behavior.",
  "inputs": [
    {"workspace_path": "scripts/report.py"},
    {"from_step": "research-contract", "output": "contract"}
  ],
  "write_scope": [
    "scripts/report.py",
    "tests/test_report.py"
  ],
  "outputs": [
    {"name": "replacement-manifest", "artifact_type": "replacement-manifest"}
  ],
  "success": {
    "required_outputs": ["replacement-manifest"]
  }
}
```

Worker properties:

- receives one step;
- receives only resolved exact inputs;
- receives exact write scope;
- receives Boundary-assigned output paths;
- may use an economical or strong Worker binding explicitly allowed by the Task;
- writes replacements under the step directory;
- does not edit the live workspace;
- does not run commands;
- does not modify the Plan;
- does not write the ledger;
- does not validate Task completion.

Strong Planner plus strong Validator reduce quality loss from economical Workers, but do not prevent all bad mutations. The architecture limits blast radius through narrow scope, staged output, deterministic checks, and final independent validation.

Planner should select a strong Worker when the step is:

- highly coupled across files;
- semantically ambiguous;
- architecture-sensitive;
- high-impact if wrong.

There is no dynamic execution-time model escalation ceremony. Bootstrap freezes allowed bindings.

---

## 15. Command step

A command step invokes one exact deterministic process.

Example:

```json
{
  "id": "run-focused-tests",
  "kind": "command",
  "description": "Run the focused report tests.",
  "argv": ["python", "-m", "unittest", "tests.test_report"],
  "cwd": ".",
  "environment": {},
  "timeout_seconds": 300,
  "expected_exit_codes": [0],
  "workspace_mutation": false,
  "replay_safe": true,
  "inputs": [],
  "outputs": [
    {"name": "command-result", "artifact_type": "command-result"}
  ],
  "success": {
    "exit_code_in": [0]
  }
}
```

Rules:

- no shell interpretation by default;
- command arguments are an explicit array;
- `argv[0]` is resolved before execution to an absolute executable path and its observable identity is persisted;
- working directory is canonical and inside the workspace;
- the environment is built from an explicit sanitized baseline plus the declared `environment`; ambient variables are not inherited wholesale;
- complete stdout and stderr are persisted;
- exit code and timing are persisted;
- command steps are non-mutating in the MVP;
- temporary directories and language/tool caches are redirected outside the target workspace where supported;
- Python commands default to `PYTHONDONTWRITEBYTECODE=1`;
- qualification commands disable repository-local test caches.

Boundary records a deterministic identity before and after the command over the complete workspace tree, including `.git` and `.stt`, while excluding only the exact Boundary-owned stdout, stderr, and temporary files that are expected to change during that command. The identity covers canonical path, object type, regular-file bytes, symlink target, and relevant file and directory mode bits where observable and meaningful. Permission-only changes such as `chmod` produce `BLOCKED_UNKNOWN`. ACL, ownership, extended-attribute, and other platform metadata are not claimed universally; unsupported required observations fail closed or are outside the supported MVP host contract. This is reliable for cooperative non-hostile commands; hostile evasion is outside the MVP.

`replay_safe` is mandatory. Command replay requires `replay_safe: true`, prior
state `TIMED_OUT_CONFIRMED_TERMINATED`, unchanged complete workspace identity,
and `attempt_count < maximum_attempts`. `TERMINATION_UNKNOWN`, false safety,
changed identity, or an exhausted budget blocks replay with `BLOCKED_UNKNOWN`.
The declaration concerns repeatability, not mutation permission.

If the command changes the live workspace unexpectedly, the step is:

```text
BLOCKED_UNKNOWN
```

Intentional formatters, generators, or commands that rewrite source are unsupported as command steps. Their desired output must be produced as staged Worker artifacts and installed by a mutation step.

This detects accidental mutation. It is not hostile-process containment.

---

## 16. Mutation step

A mutation step installs one exact replacement manifest previously produced as a named output of an earlier Worker step.

Example:

```json
{
  "id": "install-report-change",
  "kind": "mutation",
  "description": "Install the prepared report and test replacements.",
  "inputs": [
    {"from_step": "prepare-report-change", "output": "replacement-manifest"}
  ],
  "replacement_input": {
    "from_step": "prepare-report-change",
    "output": "replacement-manifest"
  },
  "outputs": [
    {"name": "mutation-result", "artifact_type": "mutation-result"}
  ],
  "success": {
    "installed_manifest_matches": true
  }
}
```

Only deterministic STT code mutates the live workspace.

Supported operations:

- create regular file;
- replace regular file;
- delete regular file;
- create required real directories.

Before mutation:

1. validate the replacement manifest;
2. validate canonical relative paths;
3. reject absolute paths;
4. reject `..`;
5. reject `.git` path components;
6. reject `.stt` path components;
7. reject symlink parents;
8. reject special files;
9. verify exact Task write authority;
10. verify current live identities match admitted before-state;
11. persist exact before-images and absence markers;
12. persist exact replacement bytes and manifest;
13. append durable `MUTATION_INTENT`.

Then:

14. install regular-file changes atomically per file where possible;
15. verify exact installed identities;
16. append `STEP_FINISHED`.

The MVP makes no multi-file transaction claim.

---

## 17. Task step

A Task step contains a child mission and delegated authority.

Example:

```json
{
  "id": "research-output-contract",
  "kind": "task",
  "description": "Determine the existing report output contract.",
  "mission": "Determine and verify the report output compatibility contract.",
  "inputs": [
    {"workspace_path": "scripts/report.py"},
    {"workspace_path": "tests"}
  ],
  "authority": {
    "read_paths": ["scripts/report.py", "tests"],
    "write_paths": []
  },
  "outputs": [
    {"name": "contract", "artifact_type": "contract"}
  ],
  "success": {
    "child_status": "COMPLETE",
    "required_outputs": ["contract"]
  }
}
```

When the Lead reaches this step:

1. Boundary validates the child mission and delegated authority;
2. Boundary creates the deterministic child Task if absent, binding the declared inputs and required-output contract;
3. Lead descends into that child;
4. child performs its complete lifecycle;
5. Boundary validates the child terminal result, output names, artifact types, identities, and provenance;
6. Boundary records the child result as the parent step result;
7. Lead returns to the parent after every terminal child result; later parent steps run only when the child result is `COMPLETE`.

A child failure does not bypass the parent Validator.

---

## 18. Step inputs and named outputs

All step results use one structural shape:

```json
{
  "schema": "stt.step-result.v1",
  "task_id": "root",
  "step_id": "research-output-contract",
  "status": "COMPLETE",
  "summary": "Verified output contract.",
  "outputs": {
    "contract": {
      "path": "steps/000-research-output-contract/task/artifacts/contract.json",
      "sha256": "...",
      "byte_size": 1240,
      "artifact_type": "contract"
    }
  },
  "evidence": []
}
```

Allowed status values:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
```

Later steps reference outputs structurally:

```json
{
  "from_step": "research-output-contract",
  "output": "contract"
}
```

Boundary resolves that reference without semantic discovery.

A Task terminal output may reference only an accepted output of one of its own completed steps or a Boundary-assigned Validator artifact. Boundary verifies provenance, output name, artifact type, path, hash, and size before promoting it into `result.json` or a parent Task step. Validator prose alone cannot invent an unbound artifact reference.

Substantive bodies are never copied into the Plan, ledger, Lead receipt, or parent context.

---

## 19. Boundary

Every substantive call passes through Boundary:

```text
Lead
→ Boundary
→ Planner / Worker / command / mutation / Validator / Task operation
→ Boundary
→ persisted complete result
→ ledger event
→ compact receipt
→ Lead
```

Boundary is one mandatory façade over small deterministic helpers.

### 19.1 Boundary responsibilities

Boundary uses one canonical workspace-path admission primitive for every model-visible workspace read and every workspace write. It rejects absolute paths, traversal, symlink components or leaves, special files, and containment escapes. Semantic roles cannot request `.git` or `.stt` as workspace paths; optional deterministic Git observation is isolated from model context. Separately, Boundary may load exact identity-bound Task artifacts under `.stt` only when an accepted Plan or Task binding declares them as inputs. Those artifact references are validated by path, hash, size, type, producer, and authority and do not grant arbitrary `.stt` access. Containment is checked when the object is opened, not only by string normalization.

Boundary:

- validates run identity;
- validates runtime identity;
- validates Task identity;
- validates accepted Plan identity;
- validates step identity and current eligibility;
- validates authority;
- resolves declared inputs;
- constructs bounded operation requests;
- invokes providers or deterministic operations;
- validates returned schemas and identities;
- validates paths, hashes, sizes, and containment;
- persists requests, raw returns, accepted results, logs, and artifacts;
- appends accepted lifecycle facts to the Task ledger;
- creates child Tasks;
- validates child return binding;
- returns compact receipts.

### 19.2 Boundary non-responsibilities

Boundary does not decide:

- whether a mission is wise;
- whether a Plan is semantically good;
- whether an implementation is elegant;
- whether a Task mission is satisfied;
- how to repair failed semantic work.

Planner and Validator think.

Boundary remains deterministic.

Before any semantic invocation, Boundary applies this persisted attempt-disposition resume gate. It adds no ledger event and no retry state machine.

### 19.3 Provider unavailability

A confirmed terminated timeout within the finite attempt budget may be retried.
Every other completed provider return is persisted and is not retried.
Unavailable executable/provider, unsupported route, unresolved binding, malformed,
schema-invalid, identity-mismatched, rejected, explicit failure, or unknown
termination fails closed without inventing a semantic result.

- Planner unavailability leaves the Task in `NEEDS_PLAN`.
- Worker unavailability leaves the current step started but unfinished; only a
  confirmed terminated timeout may be retried under the bounded policy.
- Validator unavailability leaves the Task in `NEEDS_VALIDATION`.

Provider attempts use monotonically numbered create-only directories. Resume never overwrites an earlier request or raw return.

The current run invocation stops with a compact operational blocker. Resume reconstructs the same logical request from persisted files. No new lifecycle event is required.

### 19.4 Internal implementation

Boundary may call internal modules for:

- Plan validation;
- Task path construction;
- ledger validation and append;
- provider invocation;
- workspace safety;
- command execution;
- mutation installation;
- receipt construction.

This is decomposition inside one Boundary behavior, not multiple workflow gateways.

---

## 20. Lead

The Lead is deliberately mechanical.

It carries only:

- run ID;
- current Task path;
- current step identity;
- ledger head;
- runtime identity;
- compact receipts;
- next action.

It does not carry:

- full Plans;
- source files;
- logs;
- patches;
- child histories;
- complete validation reports;
- prior conversations;
- broad workspace context.

Correctness must not depend on Lead session memory.

### 20.1 Lead algorithm

Conceptually:

```text
advance(task):

    validate task identity and ledger

    if task has no accepted Plan:
        Boundary.plan(task)
        return

    step = first unfinished Plan step

    if no step:
        Boundary.validate_and_finish(task)
        return

    if any earlier step finished non-COMPLETE:
        Boundary.validate_and_finish(task)
        return

    if step.kind == task:
        child = canonical child path

        if child does not exist:
            Boundary.create_child(task, step)

        if child is not terminal:
            advance(child)
            return

        Boundary.finish_parent_step_from_child(task, step, child)

        if child status is not COMPLETE:
            Boundary.validate_and_finish(task)

        return

    Boundary.execute_step(task, step)

    if step result is not COMPLETE:
        Boundary.validate_and_finish(task)
```

The executable outer loop repeatedly calls `advance(root)` until the root is terminal.

It does not scan the whole run tree for arbitrary unfinished Tasks.

---

## 21. Durable depth-first call stack

Task-local directories form the durable DFS call stack.

Required rules:

1. child path is deterministic:

   ```text
   steps/<index>-<step-id>/task/
   ```

2. child Task identity is deterministically derived from parent Task and step;
3. child `task.json` binds the parent Task, Plan, step, and runtime;
4. the parent step remains unfinished until a validated child terminal result is recorded;
5. a terminal child with no parent `STEP_FINISHED` is validated and resumed on the canonical child path;
6. a parent `STEP_STARTED` with no child directory may recreate the child deterministically;
7. conflicting child contents fail closed;
8. only the canonical child is considered.

No global stack file, waiting protocol, scheduler, or child registry is required.

---

## 22. Failure and validation propagation

Every Task always runs its Validator.

There is no direct propagation operation that skips ancestor validation.

For any ordinary step that finishes `FAILED` or `BLOCKED_UNKNOWN`:

```text
stop later steps
→ call current Task Validator
→ produce current Task terminal result
```

For a child failure:

```text
child Validator
→ child terminal result
→ parent Task step finishes non-COMPLETE
→ parent Validator
→ parent terminal result
→ repeat upward
```

This preserves the fundamental invariant at every level.

---

## 23. Validator

Every Task ends with one accepted Validator result.

The Validator receives a bounded final index referring to:

- `mission.md`;
- accepted `plan.json`;
- every step result;
- verified child results;
- mutation evidence;
- command evidence;
- final workspace identities;
- explicitly selected substantive artifacts.

The Validator does not receive entire child ledgers or prior conversations.

The Validator returns:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
```

with:

- concise reason;
- named result outputs;
- validation-report reference;
- material findings.

### 23.1 Mechanical terminal floors

Boundary enforces:

```text
any BLOCKED_UNKNOWN step
→ Task finishes BLOCKED_UNKNOWN

otherwise any FAILED step
→ Task finishes FAILED

all steps COMPLETE but a required Task output is missing, mismatched, or lacks accepted provenance
→ Task finishes FAILED

all steps COMPLETE and every required Task output is valid
→ Validator may return COMPLETE, FAILED, or BLOCKED_UNKNOWN
```

The Validator still supplies the report and reasoning, but it cannot contradict mechanical facts.

A final Validator failure ends the Task. The MVP does not automatically replan or repair.

---

## 24. Ledger

Each Task owns one append-only hash-chained JSONL ledger.

The ledger is the lifecycle authority.

Substantive bodies live in files. Ledger events commit facts about those files. All lifecycle reads and appends occur while the Run writer lock is held.

Minimal event vocabulary:

```text
TASK_CREATED
PLAN_ACCEPTED
STEP_STARTED
MUTATION_INTENT
STEP_FINISHED
TASK_FINISHED
```

### 24.1 Event meaning

#### `TASK_CREATED`

Commits:

- Task identity;
- mission identity;
- authority identity;
- runtime identity;
- parent binding.

#### `PLAN_ACCEPTED`

Commits:

- accepted Plan path;
- SHA-256;
- byte size.

#### `STEP_STARTED`

Commits:

- Plan identity;
- step ID;
- request identity.

#### `MUTATION_INTENT`

Commits:

- mutation step;
- before-image manifest;
- replacement manifest;
- exact intended destinations.

#### `STEP_FINISHED`

Commits:

- step ID;
- status;
- result reference;
- output index;
- evidence references.

#### `TASK_FINISHED`

Commits:

- terminal status;
- Validator report;
- `result.json`;
- terminal output index.

`STEP_FINISHED` is used for successful, failed, and blocked steps.

There is no recursive event family.

---

## 25. Cursor derivation

Current Task state and next action are derived from:

- validated ledger events;
- immutable accepted Plan;
- persisted requests and results;
- validated child result;
- terminal report.

The cursor is not separately mutable state.

Files not committed by an accepted ledger event are incomplete attempts and do not change lifecycle state.

### 25.1 Durable publication and narrow adoption

Control-bearing files are written to a same-directory temporary sibling, flushed and file-synced where supported, atomically published, followed by directory sync where supported, then reread and verified. Each bounded canonical ledger event is appended in one write, flushed, and synced before the operation reports success. `MUTATION_INTENT` is durable before any live mutation begins.

A single incomplete trailing ledger fragment is treated as an uncommitted torn append. Under the writer lock, STT preserves the fragment for diagnosis, validates the complete prefix, and truncates only that trailing fragment. Any other malformed line, hash mismatch, gap, or interior corruption fails closed.

Task creation is different: construct the complete initial Task under a
same-parent temporary directory containing `task.json`, `mission.md`, initial
input bindings, required-output contract, `workspace-index.json`, required
directories, and a valid `TASK_CREATED` ledger event. Validate, flush, fsync,
reread, verify, and atomically rename it only after confirming the deterministic
final path does not exist; fsync the parent where supported, reread and verify,
then return the compact reference. If same-parent atomic directory rename is
unavailable or unsafe, fail before publishing. A visible final Task directory
always contains `TASK_CREATED`. Temporary residue is non-authoritative and is
never adopted. No generalized orphan recovery is used.

---

## 26. Interruption semantics

### 26.1 Before `STEP_STARTED`

Nothing began. Retry is safe.

### 26.2 After `STEP_STARTED`, before accepted result

For Worker provider attempts:

- preserve attempt files;
- retry only for `transport timeout` with
  `TIMED_OUT_CONFIRMED_TERMINATED` and an unexhausted finite
  `maximum_attempts`;
- do not append `STEP_FINISHED` without an accepted result;
- resume the same immutable step and reconstruct the request.

Planner and Validator attempts occur outside step events:

- Planner remains `NEEDS_PLAN` until `PLAN_ACCEPTED`;
- Validator remains `NEEDS_VALIDATION` until `TASK_FINISHED`.

For a command started without a durable result, current process state cannot be
reconstructed. Persist `TERMINATION_UNKNOWN` unless positive termination is
established. Replay only when the state is
`TIMED_OUT_CONFIRMED_TERMINATED`, `replay_safe: true`, the complete workspace
identity is unchanged, and `attempt_count < maximum_attempts`; otherwise finish
the step `BLOCKED_UNKNOWN`.

### 26.3 After child terminal result, before parent step finish

Resume validates the child and records the parent step result.

### 26.4 After `MUTATION_INTENT`, before `STEP_FINISHED`

This is the one non-replayable uncertainty window.

After restart:

1. do not replay the mutation;
2. preserve before-images;
3. preserve intended replacements;
4. inspect current live identities deterministically;
5. create uncertainty evidence;
6. finish the mutation step as `BLOCKED_UNKNOWN`;
7. run the current Task Validator;
8. validate every ancestor normally.

The Task becomes `BLOCKED_UNKNOWN`.

No automatic rollback is attempted.

---

## 27. Naming conventions

Fixed Task files:

```text
task.json
mission.md
workspace-index.json
plan.json
ledger.jsonl
result.json
```

Planning attempts:

```text
planning/
├── attempt-001/
│   ├── request.json
│   └── raw-return.txt
└── attempt-002/
    ├── request.json
    └── raw-return.txt
```

`plan.json` is the only canonical accepted Plan copy. Attempt directories preserve transport evidence only.

Validation:

```text
validation/
├── attempt-001/
│   ├── request.json
│   └── raw-return.txt
└── report.json
```

Worker provider attempts use the same monotonic `attempt-NNN` pattern under the step directory; the accepted `result.json` remains outside attempt directories.

Steps:

```text
steps/
├── 000-research-contract/
├── 001-prepare-change/
├── 002-install-change/
└── 003-run-tests/
```

Step contents as applicable:

```text
request.json
raw-return.txt
result.json
receipt.json
artifacts/
stdout.log
stderr.log
before/
replacement/
task/
```

Boundary supplies all writable paths.

Agents never invent output locations.

---

## 28. Context discipline

Every model invocation must be reconstructible from persisted files and fixed instructions.

Data flow:

```text
operation request persisted
→ exact referenced inputs loaded
→ provider invoked
→ complete return persisted
→ accepted output validated
→ ledger records reference and identity
→ Lead receives compact receipt
```

The Lead never carries substantive bodies.

Planner receives only mission, authority, role choices, persisted initial inputs, the required-output contract, the deterministic workspace index, fixed instructions, and schema.

Worker receives only one step, exact inputs, exact scope, and output paths.

Validator receives a compact final index and only the exact files required for judgment.

A child result is referenced, not copied into parent context.

All model-visible workspace references pass the common read-path admission rules. `.git`, `.stt`, symlinks, special files, and containment escapes are never accepted as semantic workspace paths. Exact identity-bound Task artifacts stored under `.stt` may be loaded only through declared artifact references.

---

## 29. Model routing

Bootstrap freezes bindings for the Run.

The immutable `run.json` binding persists `provider`, `requested_model`,
`requested_effort`, finite positive `maximum_attempts`, executable selection or
resolution policy, and `live_provider_authorized`. Omitted model or effort is
stored as `UNSPECIFIED`, never fabricated. `stt run --run-root <path>` cannot
add or remove authorization or change any binding; any such change requires a
new Run. Actual observed provider/model/effort belong to attempt records and
may be `UNKNOWN`.

Recommended default:

```text
strong Planner
→ bounded economical Workers by default
→ strong Worker only when the Planner explicitly selects it
→ strong independent Validator
```

Lead, Boundary, hashing, storage, command execution, and mutation use deterministic code.

Validator independence in the MVP means a separate Validator invocation with Validator-specific fixed instructions, no Planner or Worker conversation, and only the persisted final index plus explicitly referenced evidence. Bootstrap may bind a separate model or provider route, but STT reports runtime or context isolation as unknown unless the host exposes it. Independence never means an unverified claim of fresh context or a different model.

### 29.1 Economical Worker quality loss

Expected losses include:

- weaker ambiguity handling;
- poorer cross-file consistency;
- less architectural awareness;
- more literal execution;
- inability to repair underspecified instructions.

Mitigations:

```text
strong Planner
→ executable narrow step
→ exact context
→ staged output
→ deterministic checks
→ strong independent Validator
```

This is sufficient to limit scope and detect many defects. It does not guarantee prevention before mutation. Therefore:

- Worker scope must remain narrow;
- high-impact semantic work may use an allowed strong Worker;
- validation failure is reported honestly;
- no automatic rollback is claimed.

---

## 30. Plain-directory support

STT must work in a plain directory without Git.

Workspace identity uses deterministic file observations, not Git.

Git, when present, may add:

- repository root;
- HEAD;
- branch;
- status;
- final diff.

Git is not used for:

- Task state;
- runtime identity;
- before-images;
- rollback;
- mutation authority;
- correctness;
- writer locking.

The Run writer lock is an OS-backed filesystem lock owned by STT, not Git.

STT does not commit, stage, push, merge, rebase, or publish.

---

## 31. Public CLI

MVP commands:

```text
stt start --workspace <path> --mission-file <path> --provider <fake|claude-code|codex> [--model <value>] [--effort <value>] [--maximum-attempts <positive-integer>] [--allow-live-provider] [--evidence <relative-path>]...
stt run --run-root <path>
stt status --run-root <path>
stt diagnose --run-root <path>
```

### `start`

- validates workspace;
- finalizes explicit CLI mission input;
- accepts zero or more explicit authorized evidence references;
- binds providers;
- persists an immutable Run binding containing `provider`, `requested_model`,
  `requested_effort`, finite positive `maximum_attempts`, executable selection
  or resolution policy, and `live_provider_authorized`; omitted model/effort
  are explicitly `UNSPECIFIED`;
- creates the unique Run;
- freezes the runtime and re-executes from frozen control;
- acquires the writer lock before lifecycle publication;
- builds and persists the root workspace index;
- creates root Task;
- begins execution unless a no-run option is deliberately added later.

### `run`

- verifies the persistent runtime without reading Task lifecycle state;
- reconstructs and re-executes from active frozen control;
- acquires the Run writer lock in the frozen process or fails without advancing state;
- resumes the mechanical Lead.
- never changes provider, model, effort, attempt limit, or live-provider
  authorization; changing any requires a new Run.

`fake` never requires live authorization. `claude-code` and `codex` fail before
launch without `--allow-live-provider`; unsupported provider/model/effort
combinations fail closed. The immutable Run binding is referenced by each
provider request, which supplies `dispatch_id`, `role`, `provider`,
`requested_model`, `requested_effort`, `maximum_attempts`, `attempt_number`,
`live_provider_authorized`, `instruction_paths`, `input_references`,
`output_schema`, and `timeout_seconds`. Actual observed routing is recorded per
attempt and is `UNKNOWN` when unobservable; authorization is never inferred.

### `status`

- reconstructs and re-executes from the Run's frozen control without reading Task lifecycle state;
- acquires a shared nonblocking Run lock;
- reports `RUN_BUSY` without reading changing lifecycle state when a writer is active;
- otherwise validates run and Task ledgers and reports compact current state and next action;
- does not mutate.

### `diagnose`

- reconstructs and re-executes from the Run's frozen control without reading Task lifecycle state;
- acquires a shared nonblocking Run lock;
- reports `RUN_BUSY` when a writer is active;
- otherwise reports invalid state, blocked uncertainty, missing runtime data, or failed identities;
- is strictly read-only and does not repair automatically.

The conversational `STT:` prefix is a host adapter over Bootstrap.

---

## 32. STT-private role contracts

STT owns private contracts:

```text
concepts/stt/contracts/planner.md
concepts/stt/contracts/worker.md
concepts/stt/contracts/validator.md
```

The current general repository contracts under:

```text
agents/
workflows/
```

do not govern STT runtime behavior.

In particular, STT does not inherit:

- the old Target Task Planner gate;
- RunSkeptic review and repair;
- Lead semantic acceptance;
- optional Boundary behavior;
- direct Lead execution;
- execution-exactly-once ceremony.

Existing general contracts may remain unchanged unless documentation routing needs a small explicit STT pointer.

---

## 33. Implementation shape

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
├── mutation.py
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

CLI entry:

The recorded launcher is `concepts/stt/launcher.py`. It resolves the exact
executable, invokes an explicit argv array without shell interpolation,
classifies timeout and termination, persists bounded request/raw-return data,
exit status, executable identity, dispatch ID, and truthful requested/actual
provider-model-effort metadata, and performs no semantic interpretation.
Thin mandatory adapters are `concepts/stt/providers/claude_code.py` and
`concepts/stt/providers/codex.py`, alongside `fake.py` and `__init__.py`.
Claude Code and Codex fail closed before launch unless the explicit
`--allow-live-provider` opt-in is present. Actual routing is recorded only when
observable; otherwise it is `UNKNOWN`. Deterministic controlled-executable
tests cover both adapters without a paid invocation.

Slice 3 owns these deterministic adapter and launcher tests:

```text
tests/concepts/stt/test_launcher.py
tests/concepts/stt/test_provider_claude_code.py
tests/concepts/stt/test_provider_codex.py
```

Slice 3 is accepted only when all three tests pass.

```text
scripts/stt.py
```

Tests:

```text
tests/concepts/stt/
```

Module count may be reduced when two modules are genuinely clearer together. Do not create abstraction layers solely to match this list.

Design target:

- one Task construct;
- one Lead loop;
- one Boundary façade;
- one Task-local ledger;
- one frozen runtime per Run;
- ordinary standard-library Python where practical;
- no orchestration monolith.

Line count is a warning signal, not an acceptance gate. Every module and mechanism must justify itself by an invariant or qualification scenario.

---

## 34. Qualification scenarios

The MVP is accepted only after proving:

### Lifecycle

1. root Task always calls Planner;
2. root Task executes ordered steps;
3. root Task always calls Validator;
4. child Task calls its own Planner;
5. child executes its own Plan;
6. child calls its own Validator;
7. failed child still causes parent Validator to run;
8. failed parent still causes root Validator to run;
9. nested execution is depth-first;
10. later parent steps do not run after a failed or blocked step.

### Durable DFS

11. child path is deterministic;
12. parent resumes after every terminal child result and continues later steps only after child `COMPLETE`;
13. crash after child finish but before parent step finish resumes safely;
14. conflicting child identity fails closed;
15. child inputs and required-output contract are bound and enforced;
16. child terminal output provenance is verified before parent promotion;
17. no scheduler or stack file is required.

### Plan and Boundary

18. Plan accepts only four step kinds;
19. future-step references fail;
20. authority expansion fails;
21. root and child Planner initial evidence has explicit ownership;
22. every operation passes through Boundary;
23. one path-admission primitive protects every model-visible read and workspace write;
24. Lead receipts contain no substantive bodies;
25. Planner, Worker, and Validator calls reconstruct from files.

### Workspace safety

26. plain-directory create succeeds;
27. plain-directory replace succeeds;
28. plain-directory delete succeeds;
29. Git-repository change succeeds without Git as authority;
30. out-of-scope write fails;
31. `.git` and `.stt` semantic reads and writes fail;
32. traversal and containment escape fail;
33. symlink-component and symlink-leaf reads and writes fail;
34. special-file reads and writes fail;
35. before-images are persisted;
36. mutation intent is durable before live mutation;
37. uncertain mutation is never replayed;
38. no rollback occurs automatically.

### Commands

39. command logs are file-backed;
40. explicit argument vectors and resolved executable identity are used;
41. sanitized explicit environment is used;
42. complete workspace observation detects unexpected mutation;
43. command failure becomes step failure;
44. command timeout is recorded;
45. interrupted replay-safe command retries only under the confirmed-timeout policy; interrupted non-replay-safe command becomes `BLOCKED_UNKNOWN`;
46. unexpected command mutation becomes `BLOCKED_UNKNOWN`.

Additional retry and identity qualification scenarios prove malformed Planner
output is not retried; completed provider failure is not retried; confirmed
terminated timeout retries only within finite `maximum_attempts`; unknown
termination blocks; `replay_safe: false`, changed workspace identity, and an
exhausted attempt budget each block command replay; and a mode-only mutation is
detected as `BLOCKED_UNKNOWN`.

Provider qualification proves the recorded launcher and both mandatory live
adapters: exact argv, request/raw-return persistence, opt-in enforcement,
requested and observable actual routing, truthful `UNKNOWN`, dispatch mismatch,
timeout classification, bounded output, and unavailable executable failure.
No live paid provider call is required or claimed.

Task-publication qualification proves interruption before temporary construction
completes, after temporary files exist, immediately after rename, root and
child creation, pre-existing final-path failure, normal resume of a complete
published Task, non-authoritative temporary residue, the invariant that no
visible final Task lacks `TASK_CREATED`, and honest parent-directory fsync
limitations.

The architecture contains 101 numbered qualification scenarios: baseline
scenarios 1–74 and added scenarios 75–101 below.

### Added qualification scenarios

#### Retry and persisted blocker behavior

75. malformed Planner return is not retried in the same process;
76. malformed Planner return remains blocked after restart;
77. completed Worker provider failure remains blocked after restart;
78. completed Validator failure remains blocked after restart;
79. confirmed terminated timeout retries within budget;
80. exhausted timeout budget remains blocked after restart;
81. unknown termination remains blocked after restart.

#### Recorded launcher and provider adapters

82. launcher persists the canonical attempt disposition;
83. request identity binds every attempt disposition;
84. Claude Code adapter translates the common request contract;
85. Codex adapter translates the common request contract;
86. both live adapters fail before launch without authorization;
87. omitted model and effort remain explicitly unspecified;
88. unsupported provider combinations fail closed.

#### Permission-only mutation detection

89. regular-file mode-only mutation is detected;
90. directory mode-only mutation is detected;
91. complete identity includes canonical path and object type;
92. complete identity includes bytes and symlink target;
93. unsupported ACL and ownership observations are reported honestly.

#### Atomic Task publication

94. root publication contains `TASK_CREATED` before rename;
95. child publication contains `TASK_CREATED` before rename;
96. interruption before temporary construction leaves no authoritative final Task;
97. interruption after temporary files leaves residue non-authoritative;
98. interruption after rename verifies the complete final directory;
99. pre-existing final path fails closed;
100. complete published Tasks resume normally;
101. no visible final Task lacks `TASK_CREATED`.

### Runtime

47. all Tasks share one runtime identity;
48. runtime manifest contains literal exact paths, not reconstruction globs;
49. interpreter and observable provider dependencies are recorded;
50. active Run survives modification of workspace STT source;
51. active Run survives deletion of workspace STT source;
52. missing temporary control reconstructs from persistent bundle;
53. reconstruction never reads executable control from modified workspace source;
54. generation A can modify STT and generation B can later freeze the new source.

### Validation and model context

55. Planner provider outage leaves Task nonterminal and resumable;
56. Worker provider outage leaves step unfinished and resumable;
57. Validator provider outage leaves Task nonterminal and resumable;
58. provider attempts are monotonic and never overwritten;
59. mechanical status and required-output floors prevent false `COMPLETE`;
60. child result is referenced, not copied;
61. Validator receives a compact final index in a separate role invocation with no Planner or Worker conversation;
62. hidden context isolation is reported as unknown;
63. economical Worker context is bounded;
64. strong Worker binding is selectable only when frozen at Bootstrap;
65. no dynamic escalation protocol appears.

### Durability and exclusions

66. a second writer is rejected before lifecycle action;
67. one torn trailing ledger append is safely diagnosed and removed under the writer lock; interior corruption fails closed;
68. incomplete or temporary artifacts are non-authoritative and conflicting publication state fails closed;
69. archived Target Task modules are not imported by active STT;
70. no Fix Loop or Find Loop lifecycle appears;
71. no three-pass convergence gate appears;
72. no concurrent Task execution path appears;
73. no automatic rollback path appears;
74. no Git commit or publication path appears.

---

## 35. Remaining open implementation parameters

These are not architecture blockers:

1. exact provider adapter APIs exposed by the target host;
2. numeric byte and collection limits;
3. exact timeout defaults;
4. performance optimization for complete command workspace observation on very large plain directories without narrowing correctness scope;
5. supported durability and writer-lock claims on network filesystems;
6. conversational host integration for `STT:`.

Implementation must choose conservative defaults, document them, and test them.

---

## 36. Authoritative architecture statement

```text
Bootstrap recognizes STT:, finalizes the root mission, persists explicit initial
evidence plus a deterministic workspace index, freezes the exact listed STT
control source, creates persistent run data, binds roles, acquires one Run writer
lock, creates the root Task, and launches the mechanical Lead.

STT has one recursive construct: Task.

Every Task receives a mission, always calls its own Planner, executes one
immutable ordered Plan, always calls its own Validator, and produces a terminal
result.

A Plan contains exactly four step kinds: worker, command, mutation, and task.

A Task step creates one child Task at a deterministic path. The Lead descends
into that child. The child performs the same complete lifecycle. A verified
child result becomes the parent step result. Execution is ordinary sequential
depth-first execution.

Failure never bypasses a Validator. A failed or blocked child ends the parent
step, then the parent Validator runs, and the resulting terminal status returns
upward one Task at a time.

Every substantive operation passes through Boundary. Boundary validates
identity, authority, references, paths, schemas, and results; persists complete
bodies; appends accepted facts to the Task ledger; and returns compact receipts.

Workers stage artifacts. Commands are non-mutating. Only deterministic mutation
code changes the live workspace.

Every Task owns one append-only ledger and predictable files. Current state is
derived from the ledger and immutable artifacts, not model-session memory.

All Tasks in one Run use one frozen runtime. A missing temporary control copy is
reconstructed only from the persistent runtime bundle.

After MUTATION_INTENT without STEP_FINISHED, the mutation is never replayed.
The Task becomes BLOCKED_UNKNOWN and every ancestor still runs its Validator.

Git is optional. Concurrency, rollback, generalized recovery, old Target Task
compatibility, and review ceremonies are outside the MVP.
```
