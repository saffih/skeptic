# STT MVP Implementation Plan

**Status:** Confirmed implementation plan; execute only against the exact bound architecture and private contracts from the same reviewed revision
**Architecture source of truth:** `plans/stt-mvp-architecture-plan.md`
**Private role contracts:** `concepts/stt/contracts/{planner,worker,validator}.md`
**Repository:** `saffih/skeptic`

---

## 1. Objective and DONE

Implement the smallest complete low-dependency STT described by the companion architecture:

```text
immutable start specification
→ frozen Run
→ root Task
→ one Planner operation or planning failure
→ sequential finite Plan
→ one Validator path
→ terminal evidence
```

DONE requires:

- the exact bound architecture and three STT-private role contracts are implemented;
- one plain-directory Run succeeds with the fake provider using only the Python standard library and no Git, network, daemon, or external service;
- one intended host adapter passes deterministic contract tests and an explicitly authorized live smoke before that host is declared deployable;
- root, child, and grandchild lifecycle, failure, interruption, and resume obligations pass;
- frozen direct-bundle resume works after target-workspace STT source modification and deletion;
- active STT has no runtime dependency on archived or superseded lifecycle code;
- focused STT tests and the full repository suite pass;
- no unresolved architecture conflict, qualification blocker, or unexplained mechanism remains.

Core mechanical completion does not require Claude Code and Codex simultaneously. Each claimed adapter qualifies independently.

---

## 2. Source binding and branch discipline

Before implementation:

1. create a new repair or implementation branch from current `main`;
2. verify and record the exact Git blob and SHA-256 identities of:
   - `plans/stt-mvp-architecture-plan.md`;
   - `plans/stt-mvp-implementation-plan.md`;
   - `concepts/stt/contracts/planner.md`;
   - `concepts/stt/contracts/worker.md`;
   - `concepts/stt/contracts/validator.md`;
   - `skeptic.md` used for the final plan review;
3. preserve unrelated working-tree changes;
4. inspect current code only as needed to identify namespace collisions and reusable deterministic leaf primitives;
5. do not import or wrap archived or superseded lifecycle implementations;
6. stop and rebind if a governing document changes materially.

Historical implementations are evidence only. Reuse requires a short table:

```text
source
protected property
copy/adapt/reject decision
new owning module
focused proof
```

Prefer reimplementation when reuse would carry old lifecycle, retry, Git, capsule, review-loop, or recovery contracts.

---

## 3. Build rules

Each slice must:

- deliver one executable end-to-end behavior;
- include focused deterministic tests;
- preserve all prior passing STT tests;
- keep schemas, path admission, canonical JSON, and lifecycle derivation single-sourced;
- persist complete failure evidence;
- remain standard-library first;
- stop before the next slice when its invariant is not proven.

Do not:

- build empty layers or the full directory skeleton before behavior requires them;
- add same-Run semantic replanning or repair;
- add a scheduler, daemon, database, queue, lease, or distributed lock;
- add a generalized provider, command, workflow, or recovery plugin framework;
- add Git authority, commits, staging, worktrees, pushes, or publication;
- require both Claude Code and Codex for core completion;
- claim hostile-code, network, or external-side-effect containment;
- preserve compatibility with an older STT lifecycle;
- add mechanisms merely to satisfy a proposed file map or scenario count.

Commits follow coherent verified slices. No fixed commit count is required.

---

## 4. Minimal implementation shape

Start with the smallest package that supports the slices:

```text
concepts/stt/
├── __init__.py
├── model.py          # closed schemas, statuses, references, limits
├── store.py          # canonical JSON, create-only publication, ledger
├── locks.py          # workspace and Run locks
├── workspace.py      # path admission, materialization, identities, indexes
├── runtime.py        # freeze, manifest, direct reconstruction
├── providers.py      # small Provider protocol, fake, selected adapters
├── command.py        # frozen Command routes and disposable execution
├── mutation.py       # deterministic replacement installation
├── boundary.py       # mandatory façade and lifecycle commitments
├── lead.py           # mechanical depth-first driver
├── bootstrap.py      # start specification and Run publication
├── cli.py
└── contracts/
    ├── planner.md
    ├── worker.md
    └── validator.md
```

The three contract files are copied byte-for-byte from the bound reviewed documentation artifacts. Role-contract content is not authored or repaired during implementation. A material contract change returns to architecture and plan review.

Public entry:

```text
scripts/stt.py
```

The launcher resolves its own repository or frozen-bundle root, imports STT only from that root, and verifies the resolved module paths. Direct script execution must not depend on an installed package or ambient `PYTHONPATH`.

Split a module only when a concrete responsibility or test boundary requires it. Consolidate where clarity improves.

Tests live under:

```text
tests/concepts/stt/
```

---

## 5. Cross-cutting primitives

### 5.1 Canonical JSON

Provide one serializer/parser:

- UTF-8;
- sorted keys;
- compact stable separators;
- exactly one final LF;
- no NaN or Infinity;
- exact allowed fields;
- conservative byte and collection limits.

### 5.2 Artifact reference

Every authoritative reference contains:

```text
path
sha256
byte_size
artifact_type
producer
authority
```

Paths are canonical relative to the owning Run or Task root.

### 5.3 Immutable publication

Control-bearing files use same-directory temporary files, flush, file sync where supported, atomic publication, parent-directory sync where supported, reread, and verification.

Task and initial Run publication use complete same-parent temporary directories and atomic rename where supported. A visible authoritative Task always contains `TASK_CREATED`.

Do not claim universal power-loss durability.

### 5.4 Run-data privacy

Create Run directories and evidence files with restrictive owner-only permissions where supported, without relying on ambient umask. Validate existing store-path components and reject symlinks or special files. Do not persist provider secret values; persist only required key names and non-secret observable identity. Document the host confidentiality boundary. If equivalent user-private Run data cannot be enforced, fail Run publication and mark that host unsupported.

### 5.5 Typed errors

Use a small hierarchy such as:

```text
STTError
UsageError
InvalidRun
InvalidTask
InvalidLedger
InvalidPlan
AuthorityViolation
ArtifactMismatch
ProviderBlocked
WorkspaceSafetyError
MutationUnknown
```

Avoid an error-state framework. CLI maps errors to a small stable public set.

---

# Slice 1 — Durable root lifecycle with fake provider

## 6. Goal

Build the first complete executable path:

```text
start specification
→ published Run and root Task
→ fake Planner
→ one Worker step
→ fake Validator
→ terminal result
→ restart reconstruction
```

This slice proves architecture shape before recursion, commands, mutation, live adapters, or self-update.

## 7. Persisted model

Implement closed schemas for:

- `start-spec.json`;
- `run.json` and finite limits;
- provider routes, observable destination identities, sanitized environment-key allowlists, declared credential/config exposure, role bindings, and route-specific semantic-disclosure authorization;
- Command catalog entries, even if commands are not yet executed;
- artifact references;
- Task identity, authority, inputs, and required outputs;
- workspace index with exact entry and bounded tree identities;
- Plan and four step kinds;
- operation requests, dispositions, and results;
- Task terminal result;
- ledger events.

Unknown fields fail unless explicitly allowed by the schema.

## 8. Start specification validation

Validate before Run publication:

- absolute normalized workspace and store roots;
- workspace is an accessible real directory;
- mission and evidence source hash/size;
- authority path syntax and write/read relationship;
- unique required outputs;
- provider route references, observable destination identities, sanitized environment-key allowlists, and declared minimal credential/config exposure;
- one Planner and one Validator route;
- nonempty allowed Worker route set;
- explicit disclosure authorization for every live semantic route and every Task semantic-content category sent to it;
- Command route schema;
- finite positive limits, including workspace object-count and hash-byte observation limits.

One route may bind every semantic role. No route substitution or disclosure authorization is inferred.

## 9. Run publication

Before any in-repository default-store Run, add `.stt/` to the repository `.gitignore`. This is repository hygiene only; runtime safety must not depend on Git or ignore behavior.

Implement:

1. unique Run ID;
2. same-parent temporary Run root;
3. one-time mission and evidence materialization;
4. minimal runtime bundle for current slice;
5. canonical start and Run bindings;
6. atomic final Run-directory rename as the bootstrap-readiness commitment;
7. frozen-control re-execution;
8. workspace lock then Run lock;
9. atomic root Task creation with `TASK_CREATED` as the lifecycle-readiness commitment;
10. Lead entry.

`stt run` completes interrupted bootstrap only from a complete verified final Run directory; temporary Run residue is never adopted.

## 10. Task publication

Create the complete initial Task under a same-parent temporary directory containing:

- `task.json`;
- `mission.md`;
- initial-input bindings;
- required-output contract;
- bounded `workspace-index.json`;
- planning, validation, and steps directories;
- a valid first `TASK_CREATED` ledger event.

Validate and atomically rename only when the deterministic final path is absent. Temporary residue is non-authoritative and never adopted.

## 11. Ledger

Implement exactly:

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

Every event binds sequence, previous hash, canonical payload, and event hash.

One torn trailing fragment may be preserved and removed under the Run lock after the complete prefix verifies. Every other corruption fails closed.

State is derived from ledger plus immutable referenced artifacts. No cursor file.

## 12. Plan contract

Implement four closed step schemas:

```text
worker
command
mutation
task
```

Common fields:

```text
id
kind
description
inputs
outputs
```

There is no generic `success` object.

Worker fields:

```text
worker_route
instructions
replacement_write_scope when applicable
```

Command fields:

```text
command_route
parameters
```

Mutation fields:

```text
replacement_input
```

Task fields:

```text
mission source or exact current-mission reference
authority
inputs
required outputs through common outputs
```

Validate unique IDs, backward references, Task-wide unique output names, exact output types, authority, route membership, finite Plan length, and resolution of every workspace input to an exact Task-index identity. Every required Task output must be declared by exactly one step. Zero steps are valid only when the required-output contract is empty.

## 13. Fake provider and call directory

Define a small Provider protocol:

```python
class Provider:
    def probe(self, route: ProviderRoute) -> ProbeResult: ...
    def invoke_once(self, request: ProviderRequest, call_root: Path) -> ProviderReturn: ...
```

Call directory:

```text
call/
├── request.json
├── in/
├── out/
├── stdout.log
├── stderr.log
├── raw-return.bin
└── disposition.json
```

The fake provider supports valid Planner, Worker, and Validator returns plus deterministic failure modes needed by later slices.

## 14. Boundary and Lead root path

Expose narrow Boundary methods:

```python
plan_once(task_ref)
execute_worker_once(task_ref, step_ref)
record_skipped_steps(task_ref, cause_ref)
validate_once_and_finish(task_ref)
resume_from_ledger(task_ref)
```

Lead calls no provider, store, lock, path, or workspace helper directly.

Root success sequence:

1. reverify the immutable Task workspace-index identity and materialize Planner inputs;
2. preflight provider;
3. persist request and append the single operation-level `PLANNER_STARTED`;
4. invoke the first launched attempt;
5. validate Plan and append `PLAN_ACCEPTED` by reference;
6. materialize one Worker step;
7. append the single operation-level `STEP_STARTED` immediately before the first launched attempt;
8. accept outputs and append `STEP_FINISHED COMPLETE`;
9. build Validator final index;
10. append `VALIDATOR_STARTED`;
11. accept result/report and append `TASK_FINISHED`;
12. reconstruct the same terminal state after process restart.

## 15. Slice 1 tests

Prove:

- canonical JSON and reference identity;
- valid and corrupt ledger behavior;
- `.stt/` repository-ignore coverage without making Git a runtime dependency;
- Run and Task atomic publication;
- root workspace index, explicit overflow, source-drift rejection before Planner launch, and exact Plan input identity binding;
- authority and required-output binding;
- Plan validation for all four kinds;
- root success calls Planner, Worker, and Validator once;
- accepted artifacts are promoted by ledger reference, not copied to a second canonical path;
- Lead receipts contain references, not bodies;
- restart reconstructs identical terminal state;
- competing workspace or Run writer is rejected.

Slice 1 is complete only when the fake-provider root path runs end to end.

---

# Slice 2 — Failure, blocker, and interruption semantics

## 16. Goal

Close every root lifecycle failure path without introducing retries, replanning, or recovery machinery beyond the architecture.

## 17. Provider dispositions

Implement exactly:

```text
PRELAUNCH_BLOCKED
ACCEPTED
COMPLETED_NONRETRIABLE
TIMED_OUT_CONFIRMED_TERMINATED
TERMINATION_UNKNOWN
```

Every create-only launched-attempt record binds:

```text
dispatch_id
role
attempt_number
request identity
launch state
completion kind
termination state
blocker code
raw-return reference
requested and observed routing
```

Rules:

- prelaunch failure stops the current invocation, consumes no launched attempt, and may be checked again on later `run`;
- accepted return is eligible for the matching ledger promotion; only that ledger event advances lifecycle state;
- completed non-retriable return is never relaunched;
- confirmed terminated timeout may relaunch only within the finite launched-attempt limit;
- unknown termination never relaunches.

Persist prelaunch blocking in one bounded atomically replaced diagnostic status file outside the launched-attempt sequence. No provider client retry is enabled by STT. Record `UNKNOWN` when remote retry behavior is unobservable.

## 18. Start-event boundary

Perform deterministic preparation and provider/command preflight before appending the lifecycle start event. Append exactly one operation-level start event immediately before the first launched attempt. Confirmed-timeout retries reuse the same immutable request and do not append another lifecycle start event.

On restart after a start event without a committed lifecycle outcome:

- retry only when the latest complete disposition is `TIMED_OUT_CONFIRMED_TERMINATED`, the finite budget remains, and any Command replay/input conditions still verify;
- otherwise derive Planner or step failure from a known complete failure disposition;
- use `BLOCKED_UNKNOWN` when launch, completion, identity, integrity, or termination is uncertain;
- for Validator, use mechanical `VALIDATOR_UNAVAILABLE` after non-retryable or exhausted state.

Do not infer that launch did not occur. Do not adopt an accepted semantic output whose matching ledger promotion is absent.

## 19. Planning failure

Planner output may be a Plan or planning failure.

Use:

```text
FAILED
```

for an established contradiction, prohibition, impossibility, or authority mismatch.

Use:

```text
BLOCKED_UNKNOWN
```

for missing or uncertain evidence, capability, authority, or trustworthy provider result.

A schema-valid Planner failure keeps its declared status. Malformed, schema-invalid, dispatch-mismatched, or explicit completed provider failure becomes `FAILED`. Exhausted confirmed-timeout attempts or identity, integrity, or termination uncertainty becomes `BLOCKED_UNKNOWN`. Persist `PLANNING_FAILED` and proceed to Validator.

Only prelaunch blocking leaves planning unstarted and resumable.

## 20. Step failure and skipped steps

A valid Worker semantic failure and any known completed schema, route, exit, or output failure becomes `FAILED`. Integrity, identity, launch, or termination uncertainty becomes `BLOCKED_UNKNOWN`.

After the first non-`COMPLETE` step:

- no later step starts;
- every later step gets one `STEP_FINISHED SKIPPED` event with the causal reference;
- Validator receives every result and skip cause.

## 21. Validator unavailable

Prelaunch Validator block leaves `NEEDS_VALIDATION` and may resume.

After `VALIDATOR_STARTED`, retry only a confirmed-terminated timeout while the finite budget remains. Any unusable or completed-failure return, exhausted timeout, interruption, or termination/integrity uncertainty then mechanically commits:

```text
TASK_FINISHED
status: BLOCKED_UNKNOWN
reason: VALIDATOR_UNAVAILABLE
```

Preserve all evidence. Never fabricate semantic validation.

## 22. Slice 2 tests

Inject interruption or failure:

- before every start event;
- immediately after every start event;
- after raw return before acceptance;
- after acceptance artifact write before ledger event;
- after ledger event before return;
- malformed Planner;
- explicit Planner failure;
- Worker semantic failure;
- Validator unusable return;
- prelaunch executable unavailable and workspace-index drift before Planner launch;
- confirmed timeout within and beyond budget;
- termination unknown;
- process restart after every case.

Prove no completed or uncertain operation is dispatched twice and every non-prelaunch path reaches honest terminal Task evidence.

---

# Slice 3 — Recursive Tasks, Commands, and Mutation

## 23. Goal

Add the remaining three step behaviors while keeping one Task lifecycle and one Boundary.

## 24. Path admission and materialization

Implement one no-follow object-open primitive for semantic reads and Mutation destinations.

Reject:

- absolute semantic paths;
- traversal and containment escape;
- `.git` and active Run-store components;
- symlink components and leaves;
- hard-linked regular files;
- special files;
- unauthorized objects.

Bind every consumed object by canonical path, object type, regular-file hash/size, supported relevant mode bits, and explicit absence where applicable. A Plan workspace input must match the exact index identity resolved at Plan acceptance; path authorization alone is insufficient. Directory inputs use deterministic bounded enumeration, exact copy, and a complete source-set re-observation; membership or identity drift becomes `BLOCKED_UNKNOWN`. Before placing any material in a semantic call, verify disclosure authorization for that exact bound route.

Fail closed when safe object-open-time admission is unavailable on the host.

## 25. Recursive Task path

Add Boundary methods:

```python
create_or_resume_child(task_ref, step_ref)
finish_parent_from_child(task_ref, step_ref, child_ref)
```

Before child publication, persist the exact Task-step request and append the parent `STEP_STARTED`.

A child:

- lives at the deterministic step path;
- inherits runtime, provider routes, Command catalog, and finite Run limits;
- receives authority no broader than the parent;
- receives exact declared inputs and required outputs;
- owns its own Planner, Plan or planning failure, ledger, Validator, and terminal result.

Support:

- narrower execution-composition children;
- same-mission evidence-refinement children with the exact mission and output contract plus newly accepted evidence.

Enforce maximum depth and total Task count mechanically.

Parent later steps run only after child `COMPLETE`. Every non-`COMPLETE` child reaches every ancestor Validator.

## 26. Command catalog and execution

Implement the frozen Command route schema:

```text
id
purpose
executable resolution and observed identity
fixed argv template
typed bounded parameters
sanitized environment allowlist
accepted exit codes
maximum timeout
declared outputs
confirmed-timeout replay permission
```

Command execution:

1. validate route and parameters;
2. materialize exact inputs into a fresh disposable command directory;
3. render explicit argv without shell interpretation;
4. pass no target-workspace or authoritative Task path;
5. persist request;
6. append `STEP_STARTED` immediately before launch;
7. capture stdout and stderr under frozen limits, preserving complete logs within limits or bounded overflow/termination evidence otherwise;
8. validate declared outputs;
9. append `STEP_FINISHED`.

Do not implement complete live-workspace before/after scans. Command safety comes from disposable inputs and no target write path.

Document the cooperative-command threat model and lack of network/external-side-effect containment.

## 27. Replacement manifest

Define one closed schema:

```json
{
  "schema": "stt.replacement-manifest.v1",
  "directories": [
    {"path": "src/new_package", "before": "absent", "mode_bits": "0755"}
  ],
  "files": [
    {
      "path": "src/new_package/file.py",
      "operation": "create|replace|delete",
      "before": {},
      "replacement": {
        "path": "artifacts/replacements/file.py",
        "sha256": "...",
        "byte_size": 123,
        "mode_bits": "0644"
      }
    }
  ]
}
```

Replacement bytes remain step-owned files. `replacement` is absent for delete.

Validate unique sorted directory and file paths, shallow-first directory order, expected absence for new directories, operation/before-state consistency, replacement identity and mode, exact write authority, hard-link rejection, existing/declared parent availability, and no file/directory contradiction. Directory replacement and deletion are unsupported.

## 28. Mutation operation

Before `STEP_STARTED`, validate the static replacement manifest, replacement source identities, canonical destinations, and authority, and persist the immutable Mutation request.

Then:

1. append `STEP_STARTED`;
2. observe and verify the current destination before-state;
3. persist exact before-images or absence markers;
4. persist exact replacement bytes;
5. re-observe every destination and verify it still matches the persisted before-state;
6. append and sync `MUTATION_INTENT`;
7. immediately before each individual write or delete, reverify the destination against the admitted state expected at that point; stop further writes as `BLOCKED_UNKNOWN` on mismatch;
8. create, atomically replace, or delete exact regular files;
9. verify final identities and supported mode bits;
10. publish Mutation result references;
11. append `STEP_FINISHED`.

Interruption before intent may resume deterministic preparation. Interruption after intent never replays or rolls back automatically; it records current evidence and finishes `BLOCKED_UNKNOWN`.

Before-images are surfaced by `diagnose` for manual recovery evidence. Do not add `restore`.

## 29. Slice 3 tests

Prove:

- child and grandchild depth-first success;
- narrower-child composition;
- same-mission evidence refinement;
- recursion limits;
- child failure reaches every ancestor Validator;
- child terminal output and validation-report provenance;
- frozen Command route and parameter validation;
- no shell, sanitized environment, disposable cwd, no target path;
- command outputs, log/return overflow, and timeout/termination rules;
- explicit directory creation plus regular-file create/replace/delete Mutation;
- before-images and absence markers;
- traversal, symlink, hard-link, special-file, `.git`, and Run-store rejection;
- directory materialization rejects membership or identity drift instead of accepting a mixed-time copy;
- a changed Plan workspace input becomes `BLOCKED_UNKNOWN` rather than silently supplying newer bytes;
- before-state mismatch before intent;
- every interruption point around `MUTATION_INTENT` and an external destination change between intent and a later per-file write;
- no replay or rollback after intent.

---

# Slice 4 — Frozen runtime, CLI, and deployable host adapter

## 30. Goal

Make the Run self-contained enough to survive target-workspace STT modification or deletion and expose the minimal public interface.

## 31. Runtime allowlist

Maintain one literal exact list of runtime source files and selected adapter files.

The generated runtime manifest is outside the bundle and does not hash itself.

Do not use recursive copies, reconstruction globs, dynamic import-graph discovery, or repository-wide freezing.

Tests fail when a required runtime file is missing from the allowlist.

## 32. Freeze and reconstruction

`freeze_runtime`:

1. validates exact source files;
2. copies them into a temporary persistent bundle;
3. records paths, hashes, sizes, modes, Python implementation/version, and observable external dependency identities;
4. verifies and publishes the bundle and manifest create-only;
5. writes the exact direct resume command;
6. reconstructs temporary active control;
7. verifies active identities;
8. re-executes from frozen control.

`reconstruct_runtime` reads no executable source from the target workspace.

A compatible interpreter is required. Record exact observed interpreter facts; define and test the supported compatibility rule rather than requiring an unexplained binary-path equality.

## 33. CLI

Implement exactly:

```text
stt start --start-spec <path>
stt run --run-root <path>
stt status --run-root <path>
stt diagnose --run-root <path>
stt check-reachability
```

`start` creates and may immediately run one Run.

`run` may complete interrupted bootstrap, resume deterministic state, or return one visible prelaunch blocker. It never changes bindings.

`status` and `diagnose` are read-only. `diagnose` reports exact evidence and before-image paths but performs no repair.

`check-reachability` fails if active STT reaches archived or superseded lifecycle modules.

Stable exit classes:

```text
0 success or COMPLETE
2 FAILED
3 BLOCKED_UNKNOWN or resumable prelaunch blocker
4 INVALID_RUN
5 USAGE_ERROR
```

## 34. Provider adapters

The fake provider remains mandatory.

Implement only adapters currently claimed as supported. Each adapter is a thin translation over the common Provider request/return contract and must not define lifecycle semantics.

For each claimed adapter, prove deterministically:

- exact argv generation;
- noninteractive mode;
- tool/connector/command disabling or absence;
- output-only call directory behavior;
- bounded raw return and explicit overflow termination evidence;
- requested and observed routing facts;
- route-specific invocation, sanitized provider environment/config exposure, secret non-persistence, and semantic-disclosure authorization enforcement;
- timeout and local termination classification;
- client-side retry disablement where exposed;
- truthful `UNKNOWN` for unobservable facts.

Before declaring a host deployable, run one explicitly authorized live end-to-end smoke on that host. A paid or network call is not required for core fake-provider qualification and is never run silently.

## 35. Frozen-runtime dogfood

Using the fake provider:

1. generation A starts from current source;
2. Worker stages a change to active STT target source;
3. Mutation installs it;
4. Command verifies materialized changed source;
5. generation A completes from frozen control;
6. delete target-workspace STT source and resume generation A directly from its bundle;
7. a new Run freezes generation B from changed source.

Prove A identity is unchanged and B identity differs.

## 36. Slice 4 tests

Prove:

- plain-directory and external store-root operation with restrictive Run-data permissions;
- default in-workspace store-root operation with restrictive Run-data permissions;
- exact allowlist and bundle verification;
- direct resume command and launcher import isolation from ambient `PYTHONPATH`;
- workspace-source modification and deletion survival;
- missing/corrupt bundle failure;
- compatible/incompatible interpreter handling;
- CLI start/run/status/diagnose;
- `RUN_BUSY` behavior;
- path with spaces;
- multiple Run ID collision resistance;
- no body leakage to stdout and no provider secret values in persisted metadata;
- one claimed host adapter deterministic suite;
- live smoke evidence or explicit `NOT_RUN`, with deployability withheld when not run.

---

# Slice 5 — Qualification, cleanup, and documentation routing

## 37. Goal

Prove every architecture obligation, remove accidental complexity, and stop.

## 38. Canonical qualification matrix

Create one human-readable test matrix, not a scenario registry framework. Each row binds:

```text
invariant
focused test or test set
fault injection when applicable
expected ledger/result state
```

The matrix covers the 20 architecture qualification obligations exactly once at the invariant level. Individual tests may contain multiple cases and assertions.

Do not require an artificial total scenario count.

## 39. End-to-end qualification runs

At minimum run:

1. standard-library-only core and plain-directory root success without Git, network, daemon, or external service;
2. planning failure and Validator closure;
3. Worker failure with explicit skipped steps;
4. prelaunch blocker repaired and resumed;
5. completed/unknown call no-repeat across restart;
6. child and grandchild DFS success;
7. descendant failure through every Validator;
8. same-mission evidence refinement within limits;
9. disposable Command route success and failure;
10. Mutation success and every intent interruption boundary;
11. path-admission hostile fixture set including hard links;
12. atomic Run and Task publication interruptions;
13. writer-lock contention;
14. ledger torn tail and interior corruption;
15. frozen direct resume after source deletion;
16. required-output and provenance rejection;
17. context-bound request inspection including route-specific disclosure rejection;
18. active reachability rejection;
19. fake-provider full suite;
20. claimed host adapter suite and authorized live smoke when declaring deployment readiness.

## 40. Context tests

Instrument fake-provider requests and assert:

- Planner receives only route-authorized mission, authority, required outputs, allowed routes, selected initial evidence, and bounded workspace index;
- Worker receives only one step and exact materialized inputs authorized for its route;
- Command receives only disposable materialized paths and frozen parameters;
- Validator receives the bounded final index and selected referenced evidence authorized for its route;
- Lead receipts do not inline substantive bodies;
- child ledgers and model conversations are not copied upward;
- instruction-like evidence remains data and cannot alter role contracts, routes, schemas, authority, or output paths.

Use explicit configurable byte limits.

## 41. Full repository checks

Run:

- focused STT suite;
- full repository test suite;
- Python compile checks;
- repository formatting/lint checks already in use;
- shell syntax checks for scripts;
- `git diff --check`;
- standard-library dependency and import/reachability checks;
- documentation path-integrity check.

Do not install a new tool solely for this implementation unless correctness requires it.

## 42. Complexity review

Before final promotion, inspect:

- module count and ownership;
- duplicated schemas, path logic, and lifecycle logic;
- broad exception catches;
- unused abstractions;
- hidden Git or worktree assumptions;
- generated `.stt/` state that could be staged or committed accidentally;
- unbounded collections or context;
- duplicated canonical files competing with ledger promotion;
- compatibility code;
- unnecessary provider adapters;
- recovery behavior beyond the specified interruption cases.

Remove every mechanism not justified by an architecture invariant or qualification proof.

## 43. Routing documentation

After active STT exists, add one compact repository routing pointer, for example:

```text
STT runtime and contract -> plans/stt-mvp-architecture-plan.md and concepts/stt/
```

Do not rewrite ordinary Lead, Planner, Boundary, or Task Prompt contracts to become STT.

Do not publish routing that points to nonexistent code before the implementation lands.

---

## 44. Stop conditions

Stop rather than inventing behavior when:

- architecture, role contracts, and implementation plan disagree;
- start-spec authority or required outputs are ambiguous;
- safe no-follow path admission cannot be established on the claimed host;
- live-provider output-only behavior cannot be proved for a claimed adapter;
- a required deterministic primitive is not understood well enough to reuse;
- active old-lifecycle reachability remains;
- a ledger or bootstrap state has multiple plausible interpretations;
- Mutation state after intent is uncertain;
- full repository regression cannot be explained or repaired within scope.

Record exact evidence and return `CONFLICT` at the implementation-task level. Do not hide it with retries, compatibility, or broader automation.

---

## 45. Definition of done

The implementation is complete when:

1. exact governing document identities are recorded;
2. all five slices pass their focused tests;
3. the canonical qualification matrix covers every architecture obligation;
4. plain-directory and inside/outside store-root Runs pass;
5. root, child, grandchild, same-mission refinement, and every failure path pass;
6. prelaunch blocker and no-repeat semantics pass across restart;
7. atomic Run/Task publication and ledger corruption behavior pass;
8. workspace and Run writer locks pass;
9. Command never receives a target-workspace write path;
10. Mutation before-images, intent durability, and no-replay uncertainty pass;
11. frozen direct resume survives source modification and deletion;
12. required-output identity, provenance, and route-specific disclosure checks prevent false success or unapproved transmission;
13. fake-provider qualification passes;
14. every claimed live adapter passes deterministic tests;
15. at least one intended deployment host has an explicitly authorized live smoke before deployment readiness is claimed;
16. active STT has no archived or superseded lifecycle reachability, and default `.stt/` state is ignored by repository Git hygiene;
17. focused and full repository suites pass;
18. final documentation and code contain no unexplained mechanism;
19. no deferred feature was accidentally implemented;
20. implementation stops.

---

## 46. Final execution instruction

```text
Implement only the exact bound STT architecture.

Use this document as the ordered build map, not as authority to change the
architecture.

Build five vertical slices. For each slice:
- implement the smallest complete behavior;
- add focused deterministic tests and fault injection;
- run all prior STT tests;
- inspect the diff for unnecessary machinery;
- stop on unresolved conflict;
- commit only when the slice invariant is proven.

Keep Python standard-library first. Require only one usable semantic provider
route. Treat each live adapter as an independently qualified integration.

Do not add Git workflows, worktree isolation, containers, databases, daemons,
concurrency, rollback, generalized recovery, automatic replanning, RunSkeptic
runtime loops, or publication.

Stop after the architecture obligations, claimed-host qualification, and full
repository suite pass.
```
