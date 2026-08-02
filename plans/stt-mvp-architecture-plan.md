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

STT is a disciplined execution protocol for **simple, cooperative** semantic
agents — Planner, Worker, and Validator. These roles receive only the bounded
context Boundary gives them, follow short explicit instructions, and return
structured text. They never own lifecycle state, never append the ledger,
never directly mutate the live workspace, and never call Boundary machinery
themselves. STT is not a general hostile-agent sandbox, and it does not claim
to prevent every possible way an underlying model could ignore its
instructions in an arbitrary environment. That containment problem is out of
scope. What STT does guarantee is protocol discipline: every substantive
effect is proposed by a role, validated and performed by deterministic
Boundary code, and recorded on an append-only ledger, so a role that simply
does what it is asked cannot corrupt lifecycle state or bypass validation.

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

This applies without exception to the root Task and every descendant Task.

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

Bootstrap recognizes an STT invocation, finalizes the root mission, freezes the runnable STT control plane, creates persistent run data, and starts a mechanical Lead. The Lead advances exactly one deepest active Task at a time:

```text
Lead
  ↓ compact request
Boundary
  ↓ bounded role request
Planner / Worker / Validator
  ↓ structured return
Boundary
  ↓ validate, persist, perform authorized effect, append ledger
Lead
```

Every substantive operation passes through Boundary. Each Task receives a mission, calls a Planner, executes an immutable ordered Plan, calls an independent Validator, and persists a terminal result. A Plan step is one of `worker`, `command`, `mutation`, or `task`. Child Tasks live at deterministic paths under their parent steps and return named verified outputs through the same result schema as any other step. All intended workspace changes are staged by Workers and installed by deterministic mutation code. If mutation completion is uncertain, it is never replayed. Every ancestor still runs its Validator before failure or uncertainty reaches the root.

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
- containment of a deliberately adversarial or hostile provider;
- mandatory support for two simultaneous live semantic providers;
- arbitrary filesystem-object support;
- automatic escalation to unbound models;
- writable command steps;
- unbounded arbitrary command capability;
- speculative extension points for features not yet needed;
- distributed or concurrent execution mechanisms.

These features are not partially implemented in the MVP.

---

## 5. Terms

### Run

One root Task tree sharing one run ID, one persistent run directory, one frozen runtime generation, and one immutable set of provider and role bindings.

### Task

The only recursive execution construct.

### Bootstrap

Pre-Task logic that creates or resumes a Run. Bootstrap is not a Task.

### Lead

The mechanical depth-first driver. Lead never inspects substantive agent output.

### Boundary

The mandatory mediator that owns every protocol effect: creating role requests, invoking Planner/Worker/Validator, validating their structured returns, persisting results, performing authorized workspace effects, and appending the ledger.

### Planner

A cooperative semantic role that converts one Task mission into one executable ordered Plan.

### Worker

A cooperative semantic role that produces staged artifacts. A Worker never edits the live workspace directly.

### Command

A deterministic, explicitly authorized, non-mutating process invocation.

### Mutation

A deterministic installation of an exact replacement manifest into the live workspace.

### Validator

A cooperative, independently invoked semantic role that judges Task completion after execution stops.

### Receipt

A compact structured return to the Lead. A receipt contains references and state transitions, not substantive bodies.

---

## 6. Bootstrap

Bootstrap happens before the root Task.

Bootstrap responsibilities:

1. recognize the exact conversational prefix `STT:`;
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

After root `TASK_CREATED`, Bootstrap may not change the mission, Task authority, runtime identity, or role bindings. A materially changed mission creates a new Run.

Bootstrap does not plan or execute the root mission. The root Task still calls its own Planner.

Root initial evidence comes from explicit host or CLI references plus one bounded deterministic workspace index containing canonical paths and file metadata within the root read authority. Each Task owns `workspace-index.json`, bound from `task.json`; Boundary creates a child index from the child's narrowed read authority using the same path-admission rules, so `.git`, `.stt`, symlinks, special files, and containment escapes are excluded. If enumeration exceeds the configured index limit, the index contains deterministic directory summaries and explicit overflow markers rather than silently truncating. The index is context for planning, not permission to read outside authority.

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

Invariant: control executes, data persists, control never imports executable code from run data, and run data never controls imports. The active control directory is disposable; the persistent runtime bundle is authoritative for reconstruction.

Every mutating `stt start` or `stt run` invocation reconstructs or freezes and re-executes from the Run's control generation, then holds one OS-backed exclusive writer lock on `<run-root>/run.lock` before reading or writing lifecycle state. A second writer fails visibly and performs no lifecycle action. `status` and strictly read-only `diagnose` acquire a shared nonblocking lock; when a writer is active they report `RUN_BUSY` without reading changing lifecycle state. The MVP supports hosts where this lock primitive is available and fails closed otherwise; it does not implement leases, stale-lock recovery, or concurrent Task execution.

STT's own control code is authorized to write persistent run data under the selected `.stt/runs/<run-id>/` directory. Plan steps, Workers, commands, and workspace mutation manifests are never authorized to target `.stt`. Internal run-data persistence and target-workspace mutation are separate authorities.

---

## 8. Frozen runtime

Every root Run freezes one runtime generation before root planning begins. All Tasks in the Run use the same generation. Children do not freeze new runtimes.

### 8.1 Runtime contents

The bundle is generated from an explicit allowlist, not a directory-wide copy:

```text
scripts/stt.py
each exact required `concepts/stt/` Python module named in the manifest
concepts/stt/contracts/planner.md
concepts/stt/contracts/worker.md
concepts/stt/contracts/validator.md
the fake provider adapter, plus one real provider adapter
exact required package initializers
runtime-manifest.json
```

No wildcard is evaluated during reconstruction. The freeze operation resolves the maintained allowlist to exact paths and records those paths in the manifest.

The bundle excludes `.git/`, `.stt/`, `tests/`, `caches/`, `plans/`, `archive/`, and unrelated project source. `skeptic.md` and `skeptic-questions.md` are excluded unless an actual STT-private role contract explicitly requires them. The MVP lifecycle does not require RunSkeptic.

### 8.2 Persistent runtime bundle

Recommended path:

```text
<run-root>/runtime/bundle/
<run-root>/runtime/manifest.json
```

The manifest records for every bundled file its canonical relative path, byte size, SHA-256, and executable mode where relevant. It also records, when observable, the Python interpreter realpath and version, the selected provider-adapter identity and exposed version, and required external dependency identities needed to invoke the provider.

STT freezes its own control source and role contracts. It does not freeze the operating system, interpreter installation, provider service, or complete host environment. Resume fails visibly when a required recorded external dependency is missing or incompatible.

The persistent bundle is create-only for the Run. "Immutable" means identity-bound and never intentionally overwritten; the MVP does not depend on filesystem immutable flags.

### 8.3 Active runtime

Bootstrap reconstructs the active control directory from the persistent bundle, verifies the manifest, makes files read-only where supported, and re-executes from that control path. After re-execution, Python imports resolve from frozen control, and executable modules are not loaded from run data or from the target workspace's possibly modified STT source. If the temporary control directory disappears, it is reconstructed only from the persistent bundle.

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

There is no separate `tasks/` directory. A child Task for a Task step always lives at `steps/<index>-<step-id>/task/`, using the exact same Task layout.

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
    "planner": "planner",
    "validator": "validator",
    "workers_allowed": ["worker"]
  }
}
```

For the root Task, parent fields are `null`.

A child Task must bind the parent Task identity, the parent accepted Plan identity, the parent step identity, the child mission identity, the common runtime identity, the exact child initial-input references declared by the parent Task step, and the child required-output names and artifact types declared by that step.

Child authority must be a subset of parent authority. Authority expansion is invalid.

---

## 11. Mission

Each Task owns `mission.md`. A child mission is copied from the accepted parent Task step exactly. The parent does not supply a child Plan.

Mission content should define objective, scope, constraints, required outputs, success criteria, and prohibited actions.

The mission is immutable after `TASK_CREATED`.

---

## 12. Planner

Every Task calls its Planner exactly once successfully before execution.

Provider attempts are bounded by a finite `maximum_attempts`. Planner, Worker, and Validator never automatically retry a completed provider return: malformed, schema-invalid, identity-mismatched, rejected, explicitly failed, or semantically unsuccessful returns are persisted as evidence and stop the current invocation. Automatic retry is permitted only when repeating the operation is harmless — a `transport timeout` whose termination state is exactly `TIMED_OUT_CONFIRMED_TERMINATED`, while `attempt_count < maximum_attempts`. Otherwise persist `TERMINATION_UNKNOWN` when termination is not positively established and stop; do not retry. No semantic corrective planning, replanning, or generalized retry framework exists. This one rule — retry only when repeating the operation is harmless or explicitly retry-safe, otherwise stop and validate what happened — governs every retry in the system.

If no acceptable Planner result is available, the Task remains nonterminal in `NEEDS_PLAN`. The current `stt run` invocation stops with a compact operational blocker and may be resumed. Infrastructure failure does not create a fake Task terminal result. Every attempt directory contains a canonical persisted disposition binding `dispatch_id`, `role`, `attempt_number`, `request_identity`, `completion_kind`, `termination_state`, `retry_permitted`, `blocker_code`, and `raw_return_reference`. Its closed vocabulary is `ACCEPTED`, `COMPLETED_NONRETRIABLE`, `TIMED_OUT_CONFIRMED_TERMINATED`, and `TERMINATION_UNKNOWN`.

Before invoking Planner, Worker, or Validator, Boundary reads the latest disposition. `ACCEPTED` continues the lifecycle; `COMPLETED_NONRETRIABLE` returns its persisted blocker without reinvocation; `TIMED_OUT_CONFIRMED_TERMINATED` permits a new attempt only while `attempt_count < maximum_attempts`; and `TERMINATION_UNKNOWN` fails closed without reinvocation. An exhausted budget returns the persisted blocker. This applies after process restart and on repeated `stt run` commands. Planner remains `NEEDS_PLAN`, an unaccepted Worker step remains unfinished, and Validator remains `NEEDS_VALIDATION`, while each returns the same blocker without reinvocation. A new external operator decision requires a new Run; MVP resume never silently clears the blocker.

The first output that passes provider-return identity checks, Plan schema validation, Task authority validation, and binding validation is accepted and immutable.

The MVP does not perform a separate semantic Plan review or Planner repair loop. A poor but structurally valid Plan may later lead to `FAILED`. This is an honest limitation of the small architecture.

### 12.1 Planner inputs

The Planner receives only `mission.md`, Task authority, role-binding choices available to the Task, the Task's persisted `initial_inputs`, the Task's required-output contract, the deterministic workspace index over its read authority, fixed STT Planner instructions, and the exact output schema.

Bootstrap owns root initial-input selection. A parent Task step owns child initial-input selection. Boundary resolves and validates those references mechanically; neither Lead nor Boundary chooses semantic evidence.

The Planner does not receive the full Task ledger, broad workspace context, prior conversations, archived Target Task history, or unrelated files.

### 12.2 Planner output

The Planner returns one complete ordered Plan. The Planner does not execute, mutate the workspace, write Task state, approve its own work, select authority beyond the Task, invent writable artifact paths, or recursively call another Planner.

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

Rules: step IDs are unique within the Task; IDs use lowercase ASCII letters, digits, and hyphens; order is array order; a step may reference only workspace inputs or outputs from earlier steps; a step may not reference future steps; paths must be canonical Task-authorized relative paths; output names are unique within a step; every semantically required artifact is a named output; Boundary assigns exact persisted request and result paths.

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
  "worker_binding": "worker",
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

Worker properties: receives one step; receives only resolved exact inputs; receives exact write scope; receives Boundary-assigned output paths; writes replacements under the step directory; does not edit the live workspace; does not run commands; does not modify the Plan; does not write the ledger; does not validate Task completion.

A clear Planner instruction, narrow scope, staged output, deterministic checks, and a final independent Validator are sufficient to catch a cooperative Worker's mistakes. They are not a claim that no bad mutation can ever reach the workspace; the architecture limits blast radius rather than proving perfection.

---

## 15. Command step

A command step invokes one exact deterministic process that Boundary explicitly authorizes; a Plan may not invoke an arbitrary command outside the Task/Run specification's authorized set.

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

Rules: no shell interpretation by default; command arguments are an explicit array; `argv[0]` is resolved before execution to an absolute executable path and its observable identity is persisted; working directory is canonical and inside the workspace; the environment is built from an explicit sanitized baseline plus the declared `environment`; complete stdout and stderr are persisted; exit code and timing are persisted; command steps are non-mutating in the MVP.

Boundary records argv, working directory, start/finish evidence, exit status, and references to stdout/stderr for every authorized command, and records whether completion is known. A known success is `COMPLETE`; a known failure is `FAILED`; an interruption with uncertain effects is `BLOCKED_UNKNOWN`. Command steps are declared non-mutating by the Plan (`workspace_mutation: false`); the MVP does not observe the whole workspace before and after each command to detect unexpected side effects — that would be exhaustive filesystem comparison, which is explicitly out of MVP scope. A required Task output that a command was supposed to help produce is still caught downstream by the mechanical output-provenance floor in the Validator (§23.1); command-level side-effect detection beyond declared outputs is not claimed.

`replay_safe` is mandatory. Command replay requires `replay_safe: true`, prior state `TIMED_OUT_CONFIRMED_TERMINATED`, and `attempt_count < maximum_attempts`; it is retried only when explicitly declared idempotent/retry-safe by the Plan. `TERMINATION_UNKNOWN`, false safety, or an exhausted budget blocks replay with `BLOCKED_UNKNOWN`.

Intentional formatters, generators, or commands that rewrite source are unsupported as command steps. Their desired output must be produced as staged Worker artifacts and installed by a mutation step.

---

## 16. Mutation step

A mutation step installs one exact replacement manifest previously produced as a named output of an earlier Worker step. This is the special case that changes the live workspace, and its sequence is the smallest safe one that still gives an honest answer after an interruption.

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

Only deterministic STT code mutates the live workspace. Supported operations: create regular file; replace regular file; delete regular file; create required real directories.

Sequence:

1. validate the staged replacement manifest and canonical relative paths (reject absolute paths, `..`, `.git`/`.stt` components, symlink parents, special files);
2. verify exact Task write authority;
3. verify current live identities match the admitted before-state;
4. persist exact before-images and absence markers, plus the replacement bytes and manifest;
5. append the durable `MUTATION_INTENT` ledger event — this must be durable before any live change begins;
6. install regular-file changes atomically per file where possible;
7. verify exact installed identities;
8. append `STEP_FINISHED`.

If execution is interrupted after `MUTATION_INTENT` and completion cannot be proven, STT does not retry automatically: the step finishes `BLOCKED_UNKNOWN`, and the Validator reports the known evidence. Never automatically replay an uncertain mutation. The MVP makes no multi-file transaction claim and is not a generalized transaction engine.

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

When the Lead reaches this step: Boundary validates the child mission and delegated authority; Boundary creates the deterministic child Task if absent, binding the declared inputs and required-output contract; Lead descends into that child; the child performs its complete lifecycle; Boundary validates the child terminal result, output names, artifact types, identities, and provenance; Boundary records the child result as the parent step result; Lead returns to the parent after every terminal child result, and later parent steps run only when the child result is `COMPLETE`.

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

Allowed status values: `COMPLETE`, `FAILED`, `BLOCKED_UNKNOWN`.

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

Boundary is one mandatory façade over small deterministic helpers, and owns every protocol effect: creating requests, invoking role agents, validating structured returns, persisting requests/responses, materializing accepted artifact contents, reading and writing files, executing authorized commands, installing staged mutations, appending ledger events, and returning compact receipts.

### 19.1 Boundary responsibilities

Boundary uses one canonical workspace-path admission primitive for every model-visible workspace read and every workspace write. It rejects absolute paths, traversal, symlink components or leaves, special files, and containment escapes. Semantic roles cannot request `.git` or `.stt` as workspace paths; optional deterministic Git observation is isolated from model context. Separately, Boundary may load exact identity-bound Task artifacts under `.stt` only when an accepted Plan or Task binding declares them as inputs. Those artifact references are validated by path, hash, size, type, producer, and authority and do not grant arbitrary `.stt` access. Containment is checked when the object is opened, not only by string normalization.

Boundary's checks are practical, not exhaustive: correct Task, correct step, correct role, valid response schema, declared output names, allowed destination paths, bounded response size, and required hashes where applicable. Boundary is not a general-purpose security platform, and it does not attempt to prove that a role could never have been instructed to misbehave — it proves that a role's structured return either passes these checks and is accepted, or it does not and nothing happens.

Boundary validates run identity, runtime identity, Task identity, accepted Plan identity, step identity and current eligibility, and authority; resolves declared inputs; constructs bounded operation requests; invokes providers or deterministic operations; validates returned schemas and identities; validates paths, hashes, sizes, and containment; persists requests, raw returns, accepted results, logs, and artifacts; appends accepted lifecycle facts to the Task ledger; creates child Tasks; validates child return binding; and returns compact receipts.

### 19.2 Boundary non-responsibilities

Boundary does not decide whether a mission is wise, whether a Plan is semantically good, whether an implementation is elegant, whether a Task mission is satisfied, or how to repair failed semantic work. Planner and Validator think; Boundary remains deterministic.

Before any semantic invocation, Boundary applies the persisted attempt-disposition resume gate described in section 12. It adds no ledger event and no retry state machine.

### 19.3 Provider unavailability

A confirmed terminated timeout within the finite attempt budget may be retried. Every other completed provider return is persisted and is not retried. Unavailable executable/provider, unsupported route, unresolved binding, malformed, schema-invalid, identity-mismatched, rejected, explicit failure, or unknown termination fails closed without inventing a semantic result.

- Planner unavailability leaves the Task in `NEEDS_PLAN`. Retrying Planner costs nothing beyond attempts already spent, so leaving the Task nonterminal and resumable is safe indefinitely.
- Worker unavailability leaves the current step started but unfinished; only a confirmed terminated timeout may be retried under the bounded policy. As with Planner, the Task simply remains resumable.
- Validator unavailability is different, because the Validator is the only path to a terminal result: while `attempt_count < maximum_attempts` the Task remains in `NEEDS_VALIDATION` and is resumable. Once the Validator's `maximum_attempts` is exhausted without an accepted response, Boundary does not leave the Task nonterminal indefinitely. It mechanically records the Task as `BLOCKED_UNKNOWN`, states in the terminal report that validation was unavailable, and appends `TASK_FINISHED`. This is the one case where budget exhaustion itself produces a terminal result rather than a persisted blocker awaiting resume, because an STT Run must not be left permanently without a terminal outcome.

Provider attempts use monotonically numbered create-only directories. Resume never overwrites an earlier request or raw return.

The current run invocation stops with a compact operational blocker. Resume reconstructs the same logical request from persisted files. No new lifecycle event is required.

### 19.4 Internal implementation

Boundary may call internal modules for Plan validation, Task path construction, ledger validation and append, provider invocation, workspace safety, command execution, mutation installation, and receipt construction. This is decomposition inside one Boundary behavior, not multiple workflow gateways.

---

## 20. Lead

The Lead is deliberately mechanical. It carries only run ID, current Task path, current step identity, ledger head, runtime identity, compact receipts, and next action. It does not carry full Plans, source files, logs, patches, child histories, complete validation reports, prior conversations, or broad workspace context.

The Lead may ask Boundary for the next action, dispatch the requested operation, and receive a compact receipt. It must not inspect substantive agent output, interpret semantic results, modify files, run commands directly, append the ledger directly, or invent recovery decisions.

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

The executable outer loop repeatedly calls `advance(root)` until the root is terminal. It does not scan the whole run tree for arbitrary unfinished Tasks.

---

## 21. Durable depth-first call stack

Task-local directories form the durable DFS call stack.

Required rules: child path is deterministic (`steps/<index>-<step-id>/task/`); child Task identity is deterministically derived from parent Task and step; child `task.json` binds the parent Task, Plan, step, and runtime; the parent step remains unfinished until a validated child terminal result is recorded; a terminal child with no parent `STEP_FINISHED` is validated and resumed on the canonical child path; a parent `STEP_STARTED` with no child directory may recreate the child deterministically; conflicting child contents fail closed; only the canonical child is considered.

No global stack file, waiting protocol, scheduler, or child registry is required.

---

## 22. Failure and validation propagation

Every Task always runs its Validator. There is no direct propagation operation that skips ancestor validation.

For any ordinary step that finishes `FAILED` or `BLOCKED_UNKNOWN`: stop later steps, call the current Task Validator, produce the current Task terminal result.

For a child failure: child Validator runs, produces the child terminal result; the parent Task step finishes non-`COMPLETE`; the parent Validator runs; the parent terminal result is produced; this repeats upward.

This preserves the fundamental invariant at every level: a Task Validator is always reachable after any failure, at any depth.

---

## 23. Validator

Every Task ends with one accepted Validator result.

The Validator receives a bounded final index referring to: `mission.md`; accepted `plan.json`; every step result; verified child results; mutation evidence; command evidence; final workspace identities; explicitly selected substantive artifacts; and any missing or uncertain required outputs. The Validator does not receive entire child ledgers or prior conversations.

The Validator returns exactly one of `COMPLETE`, `FAILED`, or `BLOCKED_UNKNOWN`, with a concise reason, named result outputs, a validation-report reference, and material findings.

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

Each Task owns one append-only hash-chained JSONL ledger. The ledger is the sole lifecycle authority; one reducer derives state from it.

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

- `TASK_CREATED` commits Task identity, mission identity, authority identity, runtime identity, and parent binding.
- `PLAN_ACCEPTED` commits accepted Plan path, SHA-256, and byte size.
- `STEP_STARTED` commits Plan identity, step ID, and request identity.
- `MUTATION_INTENT` commits the mutation step, before-image manifest, replacement manifest, and exact intended destinations.
- `STEP_FINISHED` commits step ID, status, result reference, output index, and evidence references. It is used for successful, failed, and blocked steps.
- `TASK_FINISHED` commits terminal status, Validator report, `result.json`, and terminal output index.

There is no recursive event family.

---

## 25. Cursor derivation

Current Task state and next action are derived from validated ledger events, the immutable accepted Plan, persisted requests and results, validated child results, and the terminal report. The cursor is not separately mutable state.

Files not committed by an accepted ledger event are incomplete attempts and do not change lifecycle state.

### 25.1 Durable publication and narrow adoption

Control-bearing files are written to a same-directory temporary sibling, flushed and file-synced where supported, atomically published, followed by directory sync where supported, then reread and verified. Each bounded canonical ledger event is appended in one write, flushed, and synced before the operation reports success. `MUTATION_INTENT` is durable before any live mutation begins.

A single incomplete trailing ledger fragment is treated as an uncommitted torn append. Under the writer lock, STT preserves the fragment for diagnosis, validates the complete prefix, and truncates only that trailing fragment. Any other malformed line, hash mismatch, gap, or interior corruption fails closed.

Task creation is different: construct the complete initial Task under a same-parent temporary directory containing `task.json`, `mission.md`, initial input bindings, required-output contract, `workspace-index.json`, required directories, and a valid `TASK_CREATED` ledger event. Validate, flush, fsync, reread, verify, and atomically rename it only after confirming the deterministic final path does not exist; fsync the parent where supported, reread and verify, then return the compact reference. If same-parent atomic directory rename is unavailable or unsafe, fail before publishing. A visible final Task directory always contains `TASK_CREATED`. Temporary residue is non-authoritative and is never adopted. This is narrow idempotent reconciliation, not a broad recovery framework.

---

## 26. Crash reconciliation and interruption semantics

STT's crash handling is narrow idempotent reconciliation, not a broad recovery framework. The general rule: adopt an existing immutable prepared result only when its validity and identity can be proven without repeating the semantic operation.

### 26.1 Before `STEP_STARTED`

Nothing began. Retry is safe.

### 26.2 Plan or Worker result prepared but ledger commit missing

If a complete, valid, immutable Plan exists on disk but `PLAN_ACCEPTED` is missing, Boundary validates the existing Plan and appends the missing event; it does not invoke the Planner again. Symmetrically, if a complete, valid, immutable Worker result exists but `STEP_FINISHED` is missing, Boundary validates the existing result and appends the missing event; it does not invoke the Worker again.

For Worker provider attempts still in flight: preserve attempt files; retry only for `transport timeout` with `TIMED_OUT_CONFIRMED_TERMINATED` and an unexhausted finite `maximum_attempts`; do not append `STEP_FINISHED` without an accepted result; resume the same immutable step and reconstruct the request.

Planner and Validator attempts occur outside step events: Planner remains `NEEDS_PLAN` until `PLAN_ACCEPTED`; Validator remains `NEEDS_VALIDATION` until `TASK_FINISHED`.

For a command started without a durable result, current process state cannot be reconstructed. Persist `TERMINATION_UNKNOWN` unless positive termination is established. Replay only when the state is `TIMED_OUT_CONFIRMED_TERMINATED`, `replay_safe: true`, and `attempt_count < maximum_attempts`; otherwise finish the step `BLOCKED_UNKNOWN`.

### 26.3 Child terminal but parent step unfinished

Resume validates the child terminal result and records the parent step result. It does not re-invoke the child's Planner, Workers, or Validator.

### 26.4 After `MUTATION_INTENT`, before `STEP_FINISHED`

This is the one non-replayable uncertainty window. After restart: do not replay the mutation; preserve before-images; preserve intended replacements; inspect current live identities deterministically; create uncertainty evidence; finish the mutation step as `BLOCKED_UNKNOWN`; run the current Task Validator; validate every ancestor normally. The Task becomes `BLOCKED_UNKNOWN`. No automatic rollback is attempted.

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

Step contents as applicable: `request.json`, `raw-return.txt`, `result.json`, `receipt.json`, `artifacts/`, `stdout.log`, `stderr.log`, `before/`, `replacement/`, `task/`.

Boundary supplies all writable paths. Agents never invent output locations.

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

The Lead never carries substantive bodies. Planner receives only mission, authority, role choices, persisted initial inputs, the required-output contract, the deterministic workspace index, fixed instructions, and schema. Worker receives only one step, exact inputs, exact scope, and output paths. Validator receives a compact final index and only the exact files required for judgment. A child result is referenced, not copied into parent context.

All model-visible workspace references pass the common read-path admission rules. `.git`, `.stt`, symlinks, special files, and containment escapes are never accepted as semantic workspace paths. Exact identity-bound Task artifacts stored under `.stt` may be loaded only through declared artifact references.

---

## 29. Model routing

Bootstrap freezes bindings for the Run.

The immutable `run.json` binding persists `provider`, `requested_model`, `requested_effort`, finite positive `maximum_attempts`, executable selection or resolution policy, and `live_provider_authorized`. Omitted model or effort is stored as `UNSPECIFIED`, never fabricated. `stt run --run-root <path>` cannot add or remove authorization or change any binding; any such change requires a new Run. Actual observed provider/model/effort belong to attempt records and may be `UNKNOWN`.

The MVP requires the deterministic fake provider plus exactly one proven real provider adapter. Supporting two simultaneous live semantic providers before MVP completion is not required; a second adapter may be added later without changing this architecture.

Lead, Boundary, hashing, storage, command execution, and mutation use deterministic code.

Validator independence in the MVP means a separate Validator invocation with Validator-specific fixed instructions, no Planner or Worker conversation, and only the persisted final index plus explicitly referenced evidence. Bootstrap may bind a separate model or provider route, but STT reports runtime or context isolation as unknown unless the host exposes it. Independence never means an unverified claim of fresh context or a different model.

---

## 30. Plain-directory support

STT must work in a plain directory without Git. Workspace identity uses deterministic file observations, not Git.

Git, when present, may add repository root, HEAD, branch, status, and final diff for informational purposes. Git is not used for Task state, runtime identity, before-images, rollback, mutation authority, correctness, or writer locking. The Run writer lock is an OS-backed filesystem lock owned by STT, not Git.

STT does not commit, stage, push, merge, rebase, or publish.

---

## 31. Public CLI

MVP commands:

```text
stt start --workspace <path> --mission-file <path> --provider <fake|claude-code> [--model <value>] [--effort <value>] [--maximum-attempts <positive-integer>] [--allow-live-provider] [--evidence <relative-path>]...
stt run --run-root <path>
stt status --run-root <path>
stt diagnose --run-root <path>
```

### `start`

Validates workspace; finalizes explicit CLI mission input; accepts zero or more explicit authorized evidence references; binds providers; persists an immutable Run binding containing `provider`, `requested_model`, `requested_effort`, finite positive `maximum_attempts`, executable selection or resolution policy, and `live_provider_authorized` (omitted model/effort are explicitly `UNSPECIFIED`); creates the unique Run; freezes the runtime and re-executes from frozen control; acquires the writer lock before lifecycle publication; builds and persists the root workspace index; creates root Task; begins execution.

### `run`

Verifies the persistent runtime without reading Task lifecycle state; reconstructs and re-executes from active frozen control; acquires the Run writer lock in the frozen process or fails without advancing state; resumes the mechanical Lead. Never changes provider, model, effort, attempt limit, or live-provider authorization; changing any requires a new Run.

`fake` never requires live authorization. The one real provider fails before launch without `--allow-live-provider`; unsupported provider/model/effort combinations fail closed. The immutable Run binding is referenced by each provider request, which supplies `dispatch_id`, `role`, `provider`, `requested_model`, `requested_effort`, `maximum_attempts`, `attempt_number`, `live_provider_authorized`, `instruction_paths`, `input_references`, `output_schema`, and `timeout_seconds`. Actual observed routing is recorded per attempt and is `UNKNOWN` when unobservable; authorization is never inferred.

### `status`

Reconstructs and re-executes from the Run's frozen control without reading Task lifecycle state; acquires a shared nonblocking Run lock; reports `RUN_BUSY` without reading changing lifecycle state when a writer is active; otherwise validates run and Task ledgers and reports compact current state and next action; does not mutate.

### `diagnose`

Reconstructs and re-executes from the Run's frozen control without reading Task lifecycle state; acquires a shared nonblocking Run lock; reports `RUN_BUSY` when a writer is active; otherwise reports invalid state, blocked uncertainty, missing runtime data, or failed identities; is strictly read-only and does not repair automatically.

The conversational `STT:` prefix is a host adapter over Bootstrap.

---

## 32. STT-private role contracts

STT owns private contracts:

```text
concepts/stt/contracts/planner.md
concepts/stt/contracts/worker.md
concepts/stt/contracts/validator.md
```

The current general repository contracts under `agents/` and `workflows/` do not govern STT runtime behavior. In particular, STT does not inherit the old Target Task Planner gate, RunSkeptic review and repair, Lead semantic acceptance, optional Boundary behavior, direct Lead execution, or execution-exactly-once ceremony.

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
    └── claude_code.py
```

The recorded launcher is `concepts/stt/launcher.py`. It resolves the exact executable, invokes an explicit argv array without shell interpolation, classifies timeout and termination, persists bounded request/raw-return data, exit status, executable identity, dispatch ID, and truthful requested/actual provider-model-effort metadata, and performs no semantic interpretation. `concepts/stt/providers/claude_code.py` is the one mandatory live adapter, alongside `fake.py` and `__init__.py`. It fails closed before launch unless the explicit `--allow-live-provider` opt-in is present. Actual routing is recorded only when observable; otherwise it is `UNKNOWN`. Deterministic controlled-executable tests cover the adapter without a paid invocation. A second live adapter (for example Codex) may be added later using the same contract; it is not required for MVP completion.

```text
scripts/stt.py
```

Tests live under `tests/concepts/stt/`.

Module count may be reduced when two modules are genuinely clearer together. Do not create abstraction layers solely to match this list.

Design target: one Task construct; one Lead loop; one Boundary façade; one Task-local ledger; one frozen runtime per Run; ordinary standard-library Python where practical; no orchestration monolith.

Line count is a warning signal, not an acceptance gate. Every module and mechanism must justify itself by an invariant or one of the four vertical proofs in the implementation plan.

---

## 34. Qualification scenarios

The MVP is accepted only after proving the 15 end-to-end scenarios named in the implementation plan (§46 there), which together exercise every invariant in this document: the Task lifecycle (§2), Boundary mediation (§19), the retry rule (§20/§22), recursive depth-first execution (§21), workspace safety and mutation (§16, §26), authorized commands (§15), the frozen runtime (§8), and compact Lead receipts (§20).

This document does not maintain a separate numbered qualification catalogue. Adding invariants belongs here, in prose, under the relevant section; proving them belongs in the implementation plan's 15 scenarios and their supporting unit tests. Do not reintroduce a parallel list.

---

## 35. Remaining open implementation parameters

These are not architecture blockers:

1. exact provider adapter API exposed by the target host;
2. numeric byte and collection limits;
3. exact timeout defaults;
4. supported durability and writer-lock claims on network filesystems;
5. conversational host integration for `STT:`.

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

Workers stage artifacts. Commands are explicitly authorized and non-mutating.
Only deterministic mutation code changes the live workspace.

Every Task owns one append-only ledger and predictable files. Current state is
derived from the ledger and immutable artifacts, not model-session memory.

All Tasks in one Run use one frozen runtime. A missing temporary control copy is
reconstructed only from the persistent runtime bundle.

After MUTATION_INTENT without STEP_FINISHED, the mutation is never replayed.
The Task becomes BLOCKED_UNKNOWN and every ancestor still runs its Validator.

Planner, Worker, and Validator are simple cooperative roles: they receive only
bounded Boundary-supplied context, follow short explicit instructions, and
return structured text. They never own lifecycle state, never append the
ledger, and never mutate the workspace directly.

Git is optional. Concurrency, rollback, generalized recovery, old Target Task
compatibility, and review ceremonies are outside the MVP.
```
