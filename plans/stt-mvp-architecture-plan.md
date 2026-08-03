# STT MVP Architecture Plan

**Status:** Corrected architecture source of truth; implementation may begin only after the companion implementation plan passes the same review  
**Repository:** `saffih/skeptic`  
**Companion:** `plans/stt-mvp-implementation-plan.md`  
**Supersedes:** every earlier STT MVP architecture draft

---

## 1. Purpose

Safe Target Task (STT) is a small durable system for work that must be planned, executed sequentially, validated, resumable from files, bounded in model context, recursively decomposable, and safe enough to modify a live workspace without relying on model-session memory.

The design target is:

```text
one recursive Task
one mechanical Lead
one deterministic Boundary
one Task-local ledger
one frozen runtime per Run
four Plan step kinds
```

STT is not the archived Target Task system. The archive may supply lessons or small deterministic primitives, but it supplies no active lifecycle or compatibility contract.

---

## 2. Core lifecycle

`Task` is the only recursive construct.

A normal Task performs:

```text
Mission
→ Planner
→ accepted ordered Plan
→ sequential Plan steps
→ Validator
→ terminal Task result
```

Failure does not create a second lifecycle. It shortens the same lifecycle:

```text
Planner or step failure
→ persist the failure
→ mark all remaining Plan steps SKIPPED when a Plan exists
→ Validator
→ terminal Task result
```

Every child Task performs the same lifecycle. A parent gives a child only a mission, narrowed authority, declared inputs, required outputs, and frozen role bindings. The child creates its own Plan.

A Task may not:

- receive an executable Plan from its parent;
- let Lead or Boundary invent or edit semantic Plan steps;
- execute a later step after an earlier step is non-`COMPLETE`;
- bypass its Validator because execution failed;
- propagate a child result directly into an ancestor terminal result;
- treat uncommitted attempt files as lifecycle state.

### 2.1 Validator-unavailable exception

STT always attempts the Validator. A valid negative or uncertain Validator judgment is a successful Validator operation.

If no usable Validator result is produced:

1. Boundary records the failed attempt;
2. Boundary makes one fresh independent retry;
3. if the retry also produces no usable result, Boundary mechanically finishes the Task as `BLOCKED_UNKNOWN` with `VALIDATOR_UNAVAILABLE` evidence.

This mechanical fallback is the only Task terminal result not produced by a Validator. It makes the failure visible and allows it to propagate to the parent Validator. The root returns the same bounded operational result.

---

## 3. Status vocabulary

Step result statuses:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
SKIPPED
```

`SKIPPED` is permitted only for a later Plan step whose causal predecessor is `FAILED` or `BLOCKED_UNKNOWN`. Its result records the causal step and contains no invented outputs.

Task result statuses, ordered from least to most uncertain/severe for mechanical floors:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
```

Mechanical floors:

```text
any BLOCKED_UNKNOWN step or planning outcome
→ Task cannot be COMPLETE or FAILED; floor is BLOCKED_UNKNOWN

otherwise any FAILED step or planning outcome
→ Task cannot be COMPLETE; floor is FAILED

any required output is known missing, mismatched, unauthorized, or lacks accepted provenance
→ floor is FAILED

required-output identity or provenance cannot be established
→ floor is BLOCKED_UNKNOWN

all semantic work COMPLETE
→ Validator may return COMPLETE, FAILED, or BLOCKED_UNKNOWN
```

A `SKIPPED` step inherits the floor established by its causal predecessor.

---

## 4. Explicit non-goals

The MVP does not provide:

- concurrency or parallel Tasks;
- distributed scheduling;
- conditional or looping Plan syntax;
- automatic semantic replanning or repair;
- automatic rollback;
- multi-file transactional mutation;
- generalized orphan adoption or recovery packs;
- Git staging, commits, pushes, merges, rebases, or publication;
- compatibility with archived Target Task lifecycles;
- hostile-code containment beyond the explicit provider-attempt confinement contract;
- hostile-command containment;
- writable command steps;
- arbitrary filesystem-object mutation;
- automatic escalation to an unbound provider or model;
- RunSkeptic, Fix Loop, Find Loop, or three-pass ceremonies inside STT runtime.

---

## 5. Roles

### Bootstrap

Creates or resumes a Run from an immutable start specification. Bootstrap is not a Task and does not plan the mission.

### Lead

A mechanical depth-first driver. It derives the next action from files and compact receipts.

### Boundary

The mandatory deterministic firewall for identity, authority, context, invocation, persistence, integrity, and compact returns.

### Planner

A strong semantic role that attempts to create one complete ordered Plan for one Task.

### Worker

A bounded semantic role that produces staged artifacts inside a fresh attempt environment. It never edits the target workspace.

### Command

A deterministic process invocation authorized as non-mutating. STT detects covered workspace changes after execution; it does not claim hostile-process prevention.

### Mutation

Deterministic STT code that installs an exact previously staged replacement manifest.

### Validator

A strong independent semantic role that analyzes the mission, planning outcome, execution results, failures, skipped steps, evidence, and final workspace state.

---

## 6. Bootstrap and immutable start specification

A new Run begins from one canonical `start-spec.json`.

Required root fields:

```json
{
  "schema": "stt.start-spec.v1",
  "workspace_root": "/absolute/path",
  "mission": {
    "path": "/absolute/or-host-materialized/path",
    "sha256": "...",
    "byte_size": 123
  },
  "authority": {
    "read_paths": ["relative/path"],
    "write_paths": ["relative/path"]
  },
  "initial_inputs": [
    {
      "name": "evidence-name",
      "artifact_type": "evidence",
      "source": {
        "kind": "workspace|host-file",
        "path": "relative/path-or-absolute-host-path",
        "sha256": "...",
        "byte_size": 123
      }
    }
  ],
  "required_outputs": [
    {
      "name": "output-name",
      "artifact_type": "artifact-type"
    }
  ],
  "routes": {
    "planner": {
      "name": "strong-planner",
      "provider": "fake|claude-code|codex",
      "model": "UNSPECIFIED",
      "effort": "UNSPECIFIED",
      "executable": null
    },
    "validator": {
      "name": "strong-validator",
      "provider": "fake|claude-code|codex",
      "model": "UNSPECIFIED",
      "effort": "UNSPECIFIED",
      "executable": null
    },
    "workers_allowed": [
      {
        "name": "economical-worker",
        "provider": "fake|claude-code|codex",
        "model": "UNSPECIFIED",
        "effort": "UNSPECIFIED",
        "executable": null
      }
    ]
  },
  "attempt_policy": {
    "operation_maximum_attempts": 2
  },
  "live_provider_authorized": false
}
```

The invoking host may intelligently construct this object from an `STT:` request, but the persisted object is the Run contract. Authority paths are canonical workspace-relative paths. Initial-input names and required-output names are unique. A `workspace` input uses the ordinary path-admission rules; a `host-file` input must be an explicitly supplied absolute regular file with no symlink component and is materialized into Task evidence, never treated as workspace authority. Route names are unique and become the immutable names referenced by Task bindings and Worker steps. `UNSPECIFIED` is explicit; observed routing is recorded separately.

`mission` follows the same explicit host-file admission rule: absolute regular file, no symlink component, exact hash, and exact size. `mission` and every `initial_inputs` entry are identity-bound before Bootstrap persists the Run contract. Bootstrap may reread those source paths after frozen re-execution only through no-follow object-open validation and exact hash-and-size verification; a mismatch fails before `TASK_CREATED`.

Bootstrap:

1. validates the start specification without publishing lifecycle state;
2. creates a unique Run ID and Run root;
3. canonicalizes and persists the start specification create-only;
4. freezes the exact STT runtime, including the selected adapter code;
5. re-executes from frozen control;
6. acquires the Run writer lock;
7. probes every selected route through the frozen adapters and persists one immutable probe record;
8. reopens the mission and every `host-file` input with no-follow validation and re-verifies their exact hashes and sizes;
9. publishes `run.json` binding the start specification, runtime manifest, and probe-record identities;
10. builds the bounded root workspace index;
11. creates the root Task atomically from the re-verified mission and inputs;
12. starts the mechanical Lead.

A failure before `TASK_CREATED` leaves a diagnosable non-lifecycle Run root. It has no Task state and `stt run` does not pretend it is resumable; a new start creates a new Run.

`operation_maximum_attempts` is the finite budget for Planner, Worker, and replay-safe Command attempts. The Validator attempt limit is fixed by this architecture at two attempts: one initial attempt plus one fresh retry when no usable result exists. Mutation is never retried after `MUTATION_INTENT`.

After frozen re-execution, the provider probe uses only the frozen adapter code and records, where observable:

- executable realpath;
- executable hash;
- version;
- required noninteractive and structured-output capabilities;
- model and effort support;
- the Boundary-controlled confinement mechanism required for semantic attempts, including a controlled non-model write-escape canary;
- proof that the semantic role receives no command, connector, network-action, or other side-effecting tool authority beyond provider transport and its confined `in/`/`out/` contract.

An unsupported or unverifiable required capability fails before `TASK_CREATED`. Provider transport may contact the selected model service; the semantic role itself is not authorized to perform independent external actions.

After `TASK_CREATED`, mission, authority, required outputs, runtime identity, routes, attempt limits, and live-provider authorization cannot change. A material change creates a new Run.

`provider-probes.json` is one immutable canonical record containing the per-route probe results and identities. `run.json` is published create-only after frozen probing succeeds:

```json
{
  "schema": "stt.run.v1",
  "run_id": "run-...",
  "start_spec": {"path": "start-spec.json", "sha256": "...", "byte_size": 123},
  "runtime_manifest": {"path": "runtime/manifest.json", "sha256": "...", "byte_size": 123},
  "provider_probes": {"path": "provider-probes.json", "sha256": "...", "byte_size": 123},
  "root_task_path": "root"
}
```

`root_task_path` is deterministic location metadata, not a claim that `TASK_CREATED` already exists. Run and Task lifecycle authority begins only when the atomic root Task publication contains its first ledger event.

---

## 7. Control, data, and locking

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

Every mutating `start` or `run` invocation reconstructs or freezes and re-executes from the Run's frozen control generation before reading lifecycle state. The frozen process holds one OS-backed exclusive writer lock for all lifecycle reads and writes.

A second writer fails before lifecycle action. Read-only `status` and `diagnose` use a shared nonblocking lock and return `RUN_BUSY` while a writer is active.

No leases, stale-lock recovery, distributed locking, or concurrent Task execution are implemented.

---

## 8. Frozen runtime

Every Run owns one runtime generation shared by all Tasks.

Persistent layout:

```text
<run-root>/runtime/
├── manifest.json
└── bundle/
```

The bundle is created from one maintained literal allowlist containing exact active Python modules, exact STT-private role contracts, exact selected provider adapters, and required package initializers.

`runtime/manifest.json` is outside the bundle and is not one of the files whose hashes it records. No generated manifest hashes itself.

The manifest records each bundled file's canonical relative path, SHA-256, byte size, and executable mode where relevant, plus the Python interpreter identity needed to reconstruct control. Provider executable and capability identities are not inserted into this already-published manifest; they live in the immutable post-re-exec probe record bound by `run.json`.

The active control directory is reconstructed only from the verified bundle. After re-execution, Python imports must resolve under active frozen control. Modified or deleted STT source in the target workspace cannot affect the active Run.

---

## 9. Persistent layout

```text
<workspace>/.stt/runs/<run-id>/
├── run.lock
├── run.json
├── start-spec.json
├── provider-probes.json
├── runtime/
│   ├── manifest.json
│   └── bundle/
└── root/
    ├── task.json
    ├── mission.md
    ├── workspace-index.json
    ├── ledger.jsonl
    ├── planning/
    │   └── attempt-001/
    ├── validation/
    │   ├── attempt-001/
    │   └── fallback-001/
    └── steps/
        └── 000-<step-id>/
```

A child Task always lives at:

```text
steps/<index>-<step-id>/task/
```

All attempt directories are monotonically numbered and create-only.

---

## 10. Task identity and authority

`task.json` is immutable after `TASK_CREATED`.

It binds:

- Run and Task IDs;
- canonical Task path;
- parent Task, accepted parent Plan, and parent step when applicable;
- mission identity;
- runtime manifest identity;
- workspace index identity;
- declared initial inputs;
- required output names and artifact types;
- exact read and write authority;
- Planner, Validator, and allowed Worker routes;
- attempt limits.

A child authority must be a subset of its parent authority. Authority expansion is invalid.

The mission and Task identity are immutable. A parent cannot replace a child's mission after publication.

---

## 11. Workspace index and path admission

Each Task owns a bounded deterministic `workspace-index.json` over its read authority.

The common path-admission primitive applies when an object is opened, not only when a path string is parsed.

Semantic workspace references reject:

- absolute paths;
- traversal;
- containment escapes;
- `.git` and `.stt` components;
- symlink components or leaves;
- special files;
- unauthorized paths.

The index never grants authority. When enumeration exceeds a configured limit, it contains deterministic directory summaries and explicit overflow markers rather than silent truncation.

Exact Task artifacts under `.stt` may be read only through declared identity-bound artifact references containing path, hash, size, type, producer, and authority.

---

## 12. Plan

A Plan candidate is written only inside its unique Planner attempt `out/`. After the provider process tree is confirmed terminated, Boundary seals and verifies the candidate. `PLAN_ACCEPTED` selects one exact candidate by path, SHA-256, and byte size. The selected bytes are the immutable accepted Plan; there is no second canonical Plan copy at the Task root.

There are exactly four step kinds:

```text
worker
command
mutation
task
```

Every step has a stable unique lowercase ID, description, exact inputs, named outputs, and success contract. References may point only to authorized workspace inputs or accepted outputs from earlier steps.

A Plan may not contain:

- future references;
- conditions;
- loops;
- arbitrary operation plugins;
- implicit authority expansion;
- model-invented output paths.

Boundary assigns every writable attempt and artifact path.

If planning produces no acceptable Plan, Boundary writes the failure result inside the unique Planner attempt and `PLANNING_FAILED` selects that exact result. The Task then proceeds directly to Validator.

---

## 13. Fresh semantic attempt environments

Every Planner, Worker, and Validator attempt runs independently in a fresh Boundary-created attempt root:

```text
attempt-NNN/
├── request.json
├── disposition.json
├── in/                         # exact materialized inputs, read-only
├── out/                        # the only writable semantic output location
├── stdout.log
├── stderr.log
└── raw-return.bin
```

Boundary:

1. resolves and verifies declared inputs;
2. materializes exact copies or stable read-only bindings under `in/`;
3. creates empty `out/`;
4. invokes the provider with the attempt root as its complete working context;
5. confines semantic writes to `out/`;
6. persists the raw return and observed process metadata;
7. validates output schemas, paths, hashes, sizes, types, and authority;
8. confirms the provider process group has terminated;
9. seals and re-verifies accepted files in the unique attempt `out/`;
10. commits exact path, hash, size, type, and producer references to the Task ledger.

“Seal” means close all provider-owned handles, fsync where supported, reject non-regular output objects, make files read-only where supported, and bind their exact bytes by hash and size. Read-only mode is defense in depth; every later read revalidates identity.

There is no second copy step between validated attempt output and ledger commitment. The ledger selects which immutable attempt files are authoritative.

The target workspace and authoritative `.stt` Task directories are not writable by semantic attempts. A supported live route requires Boundary-controlled operating-system or equivalent host enforcement that makes `out/` the only writable semantic path; provider prompt or tool-permission flags alone are not treated as proof. Bootstrap verifies the configured confinement with a controlled non-model canary. Before every invocation, Launcher revalidates the probed executable identity and reconstructs the same confinement configuration. If identity or confinement no longer matches, the operation becomes `BLOCKED_UNKNOWN`; that live route is not invoked.

A failed or abandoned attempt is never selected by the ledger. A retry always receives a new attempt root and no mutable state from an earlier attempt except explicitly declared persisted evidence. Every created attempt consumes one unit of the applicable finite budget.

---

## 14. Attempt outcomes and retry policy

Boundary persists one disposition for every attempt.

Closed outcome classes:

```text
ACCEPTED
OPERATION_FAILED
INTERRUPTED_CONFIRMED_TERMINATED
TERMINATION_UNKNOWN
```

### `ACCEPTED`

A structurally and identity-valid semantic output was produced. Boundary seals it and the ledger selects it.

### `OPERATION_FAILED`

The operation produced usable failure evidence, including:

- explicit provider failure;
- malformed or schema-invalid output;
- dispatch or identity mismatch;
- rejected or semantically unsuccessful output;
- unavailable executable discovered after Task creation.

For Planner and Worker, it is not retried. Boundary maps explicit semantic failure and structurally unusable content to `FAILED`; it maps identity, integrity, confinement, or authority uncertainty to `BLOCKED_UNKNOWN`. It then advances the Task toward Validator.

For Validator, a structurally valid negative or uncertain judgment is accepted and is not retried. A malformed, schema-invalid, identity-mismatched, or otherwise unusable Validator return receives the one permitted fresh Validator retry; after that, Boundary uses the mechanical `VALIDATOR_UNAVAILABLE` fallback.

### `INTERRUPTED_CONFIRMED_TERMINATED`

No usable result exists and process termination is positively established.

### `TERMINATION_UNKNOWN`

No usable result exists and termination cannot be established. The attempt is abandoned and never adopted.

For Planner and Worker, either interruption class permits a fresh isolated retry only while the finite start-spec budget remains. This is safe at the Task boundary because supported semantic routes prove both isolated writes and absence of side-effecting semantic tools. Possible duplicate provider calls, cost, and lingering provider work are recorded. When the budget is exhausted, the operation becomes `BLOCKED_UNKNOWN` and proceeds to Validator.

Validator uses the same no-usable-result principle but a fixed maximum of two attempts: the initial attempt plus one fresh retry after either interruption class or any other unusable return. If the retry also yields no usable result, Boundary emits mechanical `VALIDATOR_UNAVAILABLE`. A valid negative Validator result is never retried.

Completed Planner or Worker failure evidence is never retried.

---

## 15. Boundary crash and semantic orphan rule

The Task ledger is the lifecycle commitment boundary.

For Planner, Worker, and Validator attempts:

```text
no committing ledger event
→ no accepted lifecycle result
```

Attempt files may remain as forensic evidence. STT does not adopt orphan semantic outputs.

After restart, Boundary:

1. validates the ledger;
2. classifies any uncommitted semantic attempt as abandoned;
3. records or completes its disposition when mechanically possible;
4. applies the ordinary semantic interruption policy: start a fresh attempt within the finite budget even when old remote completion is unknown, because the abandoned attempt cannot promote, mutate, execute commands, or perform independent external actions;
5. otherwise records the operation as `FAILED` or `BLOCKED_UNKNOWN` and proceeds to Validator.

Restart does not create a special retry rule. It reconstructs the same finite semantic-attempt policy from the ledger and attempt directories. Possible duplicate provider calls, cost, and lingering provider work are recorded; no duplicate semantic output is adopted.

This rule does not apply to mutation and applies to commands only under their stricter replay contract.

---

## 16. Worker step

Boundary creates the fresh Worker attempt root, persists the request containing exact declared references, and appends `STEP_STARTED` before materializing those references into `in/`. A Worker then receives one immutable step, exact materialized inputs, exact write scope, output schema, and its fresh attempt environment. A valid request whose inputs can no longer be materialized finishes `BLOCKED_UNKNOWN`; corrupted accepted references make the Run invalid.

It may:

- analyze inputs;
- produce replacement bytes;
- produce reports or other named artifacts;
- return a structured failure.

It may not:

- edit the target workspace;
- write authoritative Task state;
- invoke commands;
- change the Plan;
- write the ledger;
- decide Task completion.

Boundary accepts only declared artifacts by committing their exact attempt-owned references. Large artifact bodies remain file-backed.

---

## 17. Command step

A command is an explicit argument vector with canonical working directory, sanitized environment, timeout, expected exit codes, and mandatory `replay_safe`.

Commands are authorized as non-mutating. The MVP does not claim that arbitrary or hostile commands are prevented from writing. It detects covered changes for cooperative commands.

Before fallible command preparation, Boundary creates one dedicated command-attempt control directory, persists the exact command request and immutable exclusion manifest, and appends `STEP_STARTED`. It then resolves and verifies the executable, canonical working directory, and sanitized environment before computing the baseline. The exclusion manifest names that exact directory, its permitted files, and each file's mutability class. The entire named command-control directory is outside the target-workspace pre/post identity so the snapshot never contains or depends on itself. The same manifest defines both scans.

Boundary independently validates the excluded directory: immutable request, executable, environment, manifest, and pre-state files must retain their bound identities; only explicitly mutable stdout/stderr files may change during execution; no undeclared control path may appear. Every other `.stt`, `.git`, or workspace change remains covered. Any unexpected covered change, including relevant mode-only changes, yields `BLOCKED_UNKNOWN`.

Workspace identity covers, where supported:

- canonical path;
- object type;
- regular-file bytes and SHA-256;
- symlink target;
- relevant regular-file and directory mode bits.

ACL, ownership, extended attributes, external network effects, subprocess effects outside the workspace, and write-then-restore behavior are not universally observed. The plan makes no stronger claim.

The already-durable `STEP_STARTED` binds the command request and exclusion manifest before executable resolution and the pre-command scan. Boundary then computes the baseline, keeps its expected identity in the live Boundary process, and persists a copy inside the excluded control directory for evidence. No lifecycle or non-excluded workspace file is changed between that baseline and the post-command scan.

If Boundary itself crashes after `STEP_STARTED`, STT does not try to reconstruct whether the command launched or what external effects occurred. The command step becomes `BLOCKED_UNKNOWN` and is not replayed. This conservative rule avoids a command-specific recovery protocol.

Command replay during a live Boundary invocation requires all of:

- `replay_safe: true`;
- prior `INTERRUPTED_CONFIRMED_TERMINATED`;
- unchanged covered workspace identity;
- remaining finite attempt budget.

Otherwise the command step becomes `BLOCKED_UNKNOWN`.

Intentional workspace changes must use Worker staging followed by Mutation.

---

## 18. Mutation step

Only deterministic STT mutation code is authorized to change the target workspace.

A mutation installs one exact replacement manifest produced by an earlier accepted Worker output.

Before mutation, Boundary:

1. validates the accepted replacement-manifest reference and constructs the exact immutable mutation request;
2. appends `STEP_STARTED` binding that request;
3. validates canonical paths and exact write authority;
4. rejects `.git`, `.stt`, traversal, symlinks, and special files;
5. verifies current identities match admitted before-state;
6. on a current-state mismatch, finishes the step `BLOCKED_UNKNOWN` without `MUTATION_INTENT`;
7. persists exact before-images and absence markers;
8. persists exact replacement bytes and manifest;
9. appends durable `MUTATION_INTENT`.

Then deterministic code performs create, replace, or delete operations for regular files, creates only required real directories, and verifies final identities.

The MVP makes no multi-file atomicity claim.

A mutation with `STEP_STARTED` but no `MUTATION_INTENT` has made no authorized live change and may safely resume its deterministic preparation. After `MUTATION_INTENT` without `STEP_FINISHED`:

- never replay the mutation;
- inspect current destinations;
- persist uncertainty evidence;
- finish the step `BLOCKED_UNKNOWN`;
- skip later steps;
- run Validator;
- validate every ancestor normally.

No automatic rollback occurs.

---

## 19. Task step and durable depth-first execution

A Task step declares a child mission, narrowed authority, exact inputs, and required outputs.

Boundary first persists the exact child-creation request and appends `STEP_STARTED` binding the parent Plan identity, child mission identity, delegated authority references, inputs, required outputs, and canonical child path. It then resolves those references and creates the child at that path if absent. A valid request whose current inputs cannot be materialized finishes the parent step `BLOCKED_UNKNOWN`; corrupted accepted references make the Run invalid. Lead descends into the child until terminal. Boundary then validates the child result, output names, types, paths, hashes, sizes, provenance, and parent binding before finishing the parent step.

A non-`COMPLETE` child result finishes the parent step with the same floor, marks all later parent steps `SKIPPED`, and invokes the parent Validator.

No global scheduler, stack file, waiting protocol, or child registry exists. Task directories form the durable depth-first call stack.

---

## 20. Boundary

Every substantive operation passes through one Boundary façade:

```text
Lead
→ Boundary
→ Planner / Worker / Command / Mutation / Task operation / Validator
→ Boundary
→ persisted complete evidence
→ ledger commitment
→ compact receipt
→ Lead
```

Boundary is deterministic. It validates identities, authority, paths, schemas, confinement, references, hashes, sizes, attempt eligibility, child bindings, and terminal-output provenance.

Boundary does not decide whether a mission is wise, whether a Plan is elegant, or whether semantic work satisfies the mission. Planner and Validator think.

Boundary may mechanically:

- classify operation failures;
- apply status floors;
- record skipped steps;
- create `VALIDATOR_UNAVAILABLE`;
- reject invalid or uncertain state.

---

## 21. Lead algorithm

Conceptually:

```text
advance(task):

    validate Task, runtime, ledger, and immutable artifacts

    if no committed planning outcome:
        Boundary.plan(task)
        return

    if planning outcome is non-COMPLETE:
        Boundary.validate_and_finish(task)
        return

    step = first Plan step without STEP_FINISHED

    if no step:
        Boundary.validate_and_finish(task)
        return

    if any earlier step is non-COMPLETE:
        Boundary.finish_remaining_steps_skipped(task, cause)
        Boundary.validate_and_finish(task)
        return

    if step.kind == task:
        create or resume canonical child
        if child nonterminal:
            advance(child)
            return
        Boundary.finish_parent_step_from_child(task, step, child)
    else:
        Boundary.execute_step(task, step)

    if current step is non-COMPLETE:
        Boundary.finish_remaining_steps_skipped(task, current step)
        Boundary.validate_and_finish(task)
```

The outer loop repeatedly calls `advance(root)` until the root is terminal or an invalid Run is detected.

Lead carries references and compact receipts, never full Plans, source files, logs, patches, child histories, or model conversations.

---

## 22. Validator

Validator receives a bounded final index referring to:

- mission and Task authority;
- accepted Plan, or planning failure evidence when no Plan was accepted;
- every completed and skipped step result;
- verified child results;
- command and mutation evidence;
- required-output contract;
- selected substantive artifacts;
- final covered workspace identities.

It receives no Planner or Worker conversation and no full child ledger.

Validator returns a concise reason, status, validation-report artifact, material findings, and a selection of terminal outputs. The validation report is the only new Validator-authored artifact. Every selected Task output must reference an already accepted step output with the required name, type, path, hash, size, and producer; Validator prose or files cannot invent or replace mission outputs. Boundary verifies and seals the report, verifies every selected output, and `TASK_FINISHED` commits the exact result, report, and output references.

Boundary computes the terminal status as the more severe of the Validator judgment and the mechanical floor. It may move `COMPLETE` to `FAILED` or `BLOCKED_UNKNOWN`, or `FAILED` to `BLOCKED_UNKNOWN`; it never makes a Validator judgment less severe.

---

## 23. Ledger

Each Task owns one append-only hash-chained JSONL ledger. It is the lifecycle authority.

Event vocabulary:

```text
TASK_CREATED
PLAN_ACCEPTED
PLANNING_FAILED
STEP_STARTED
MUTATION_INTENT
STEP_FINISHED
TASK_FINISHED
```

When the next accepted Plan step is structurally eligible, Boundary first constructs and persists its exact immutable request from Plan references alone. `STEP_STARTED` then durably commits the accepted Plan identity, step ID, step kind, and request identity before any fallible input materialization, current-state observation, executable resolution, Worker invocation, Command launch, Mutation preparation, or child Task publication that can become a step result. Structural corruption that prevents construction of this request is `INVALID_RUN`, not a semantic step result. Repeating `STEP_STARTED` is valid only for an exact identity match.

`STEP_FINISHED` records `COMPLETE`, `FAILED`, `BLOCKED_UNKNOWN`, or `SKIPPED`. A `SKIPPED` step is never started and therefore validly has no preceding `STEP_STARTED`; every other step result requires its matching start event. Because a skipped result contains only bounded causal metadata and no outputs, that metadata lives directly in the ledger event and needs no separate result file.

`PLANNING_FAILED` records `FAILED` or `BLOCKED_UNKNOWN` and the exact failure evidence.

`TASK_FINISHED` records whether the terminal result came from an accepted Validator result or the mechanical `VALIDATOR_UNAVAILABLE` fallback. Boundary fallback directories are create-only and monotonically numbered; a fallback file without `TASK_FINISHED` is uncommitted, ignored, and may be replaced only by a new fallback directory.

Whenever an event references an external artifact, it binds canonical path, SHA-256, and byte size. Substantive bodies are not inlined.

Current state is derived from the validated ledger and immutable referenced files. There is no mutable cursor file.

---

## 24. Publication and interruption semantics

Control-bearing files are written to same-directory temporary siblings, flushed and synced where supported, atomically published, reread, and verified. Each bounded ledger event is appended in one write and synced before success is reported.

A single torn trailing ledger fragment may be preserved and removed under the writer lock after validating the complete prefix. Interior corruption, hash mismatch, sequence gaps, or conflicting canonical files fail closed.

Task creation uses complete same-parent temporary-directory construction containing `TASK_CREATED`, then atomic rename. Temporary residue is non-authoritative and never adopted.

For isolated semantic attempts, an artifact written without its committing ledger event may be ignored and the operation repeated according to the finite retry policy.

For commands, replay uses the stricter command contract.

For mutation, `MUTATION_INTENT` is the durable non-replay boundary.

---

## 25. Context discipline

Every semantic invocation is reconstructible from persisted files and fixed instructions.

- Planner receives mission, authority, role choices, required outputs, explicit initial inputs, workspace index, and schema.
- Worker receives one step, exact inputs, exact write scope, output schema, and fresh attempt root.
- Validator receives the bounded final index and selected evidence.
- Parent receives child references, not child bodies.
- Lead receives compact receipts only.

No correctness property depends on hidden model-session state.

---

## 26. Provider routing

Routes are frozen in `start-spec.json` and `run.json`.

Recommended default:

```text
strong Planner
→ economical bounded Workers by default
→ strong Worker only when selected by the accepted Plan from the frozen allowed set
→ strong independent Validator
```

Actual observed provider, model, and effort are recorded per attempt when observable; otherwise they are `UNKNOWN`. Requested routing is never presented as observed routing.

No execution-time escalation to an unbound route exists.

---

## 27. CLI

Canonical CLI:

```text
stt start --start-spec <path>
stt run --run-root <path>
stt status --run-root <path>
stt diagnose --run-root <path>
```

The start specification identity-binds the host-materialized mission file. Bootstrap verifies it before persisting the Run contract, re-verifies the same bytes after frozen re-execution, and persists them in the root Task. `run.json` binds the start-spec identity. A host adapter may construct the start specification from a conversation.

`start` freezes and re-executes first, then probes providers and confinement through frozen adapters, publishes the Run binding, creates the root Task, and starts Lead.

`run` reconstructs frozen control, acquires the writer lock, validates state, and resumes Lead without changing bindings.

`status` and `diagnose` are read-only. `diagnose` reports but does not repair invalid state.

Git is optional and never lifecycle authority.

---

## 28. Implementation shape

Recommended package:

```text
concepts/stt/
├── bootstrap.py
├── runtime.py
├── run_lock.py
├── task.py
├── plan.py
├── ledger.py
├── boundary.py
├── lead.py
├── attempt.py
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
    ├── fake.py
    ├── claude_code.py
    └── codex.py
```

Modules may be consolidated when that is genuinely clearer. No abstraction exists merely to match this map.

---

## 29. Qualification obligations

The implementation plan owns one canonical qualification inventory with stable IDs. The earlier draft's raw count of 101 scenarios is superseded: duplicates and overlapping transport cases are merged, while every protected behavior remains tied to an explicit architecture obligation and proof target.

Architecture obligations are:

| ID | Obligation |
|---|---|
| A01 | Root, child, and grandchild Tasks each attempt Planner and Validator. |
| A02 | Planning failure is persisted and proceeds to Validator without invented Plan steps. |
| A03 | Execution is sequential depth-first and later steps become recorded `SKIPPED` after first non-`COMPLETE`. |
| A04 | Every ordinary failure reaches the current Validator and then every ancestor Validator. |
| A05 | Validator no-result gets one fresh retry; a second no-result becomes mechanical `VALIDATOR_UNAVAILABLE`. |
| A06 | Plans accept exactly four kinds and enforce backward references, named outputs, and authority. |
| A07 | Every substantive operation passes through Boundary and returns compact references. |
| A08 | Planner, Worker, and Validator attempts use fresh confined roots; failed attempts are never promoted. |
| A09 | Orphan semantic attempts without ledger commitment are safely ignored and retried or failed within budget. |
| A10 | Commands use explicit argv, sanitized environment, exact exclusions, independent control verification, and covered mutation detection. |
| A11 | Command replay occurs only under the complete replay-safe contract. |
| A12 | Mutation intent is durable before live mutation and uncertain mutation is never replayed. |
| A13 | Task publication never exposes an authoritative Task without `TASK_CREATED`. |
| A14 | Ledger torn-tail handling is narrow; interior corruption fails closed. |
| A15 | Child identity, authority, inputs, outputs, and provenance are verified before parent promotion. |
| A16 | Runtime manifest does not hash itself; reconstruction uses only the verified bundle. |
| A17 | Provider executable, capabilities, routes, semantic confinement, and absence of side-effecting semantic tools are probed before Task creation. |
| A18 | Plain directories and Git repositories both work without Git as authority. |
| A19 | Model contexts are bounded and file-backed; no substantive bodies leak into Lead receipts. |
| A20 | Active STT has no archived Target Task lifecycle reachability. |
| A21 | Qualification IDs map mechanically to unique proof targets with no missing, duplicate, or unknown IDs. |
| A22 | Full repository tests and frozen-runtime self-modification tests pass. |
| A23 | Mission and initial-input identities survive frozen re-execution without rereading changed bytes. |
| A24 | Required-output floors and Validator output provenance are deterministic and cannot promote invented artifacts. |
| A25 | Every started Worker, Command, Mutation, or Task step durably binds its exact request or operation identity before execution. |

Promotion requires all obligations and their mapped cases to pass. A prose claim that “all scenarios pass” is insufficient.

---

## 30. Remaining implementation parameters

These are implementation choices, not architecture conflicts:

- conservative byte and collection limits;
- timeout defaults;
- exact supported POSIX lock and durability hosts;
- provider-specific confinement and capability probes;
- complete-workspace observation performance;
- conversational host integration.

Implementation must choose explicit conservative defaults, document them, and test them.

---

## 31. Authoritative statement

```text
STT has one recursive construct: Task.

Bootstrap persists an immutable identity-bound start specification, freezes one
runtime, re-executes, then proves the selected provider routes,
semantic-attempt confinement, and no-side-effect tool contract through the frozen
adapters. It creates the root Task from the exact bound mission and inputs and
starts one mechanical Lead.

Every Task attempts its Planner. An accepted Plan executes sequentially. The
first non-COMPLETE result is persisted, every later Plan step is recorded
SKIPPED, and the Task Validator analyzes the complete evidence. Planning failure
also proceeds directly to Validator.

Every substantive operation passes through deterministic Boundary. Planner,
Worker, and Validator attempts run in fresh confined roots. Their outputs become
authoritative only after Boundary validation, sealing, and ledger commitment.
Uncommitted semantic attempt output may be ignored and safely repeated within a
finite budget.

A Validator that produces no usable result is retried once independently,
under the same side-effect-free semantic interruption rule. If the retry also fails, Boundary emits visible
mechanical VALIDATOR_UNAVAILABLE / BLOCKED_UNKNOWN evidence so the parent
Validator can continue the same upward analysis.

Commands are authorized non-mutating and are checked for covered changes; hostile
command containment is not claimed. Only deterministic mutation code is
authorized to change the target workspace. MUTATION_INTENT is durable before
mutation and uncertain mutation is never replayed.

Validator may author its validation report but may select Task outputs only
from accepted step outputs. Every Task owns one append-only ledger. The ledger
and immutable referenced artifacts, not model memory, determine state.

All Tasks in a Run use one frozen runtime whose external manifest never hashes
itself. Git is optional. Concurrency, rollback, generalized recovery, archived
compatibility, and review ceremonies are outside the MVP.
```
