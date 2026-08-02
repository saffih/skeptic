# STT MVP Complete Implementation Plan

**Status:** Complete implementation plan; ready for execution after owner acceptance  
**Architecture source of truth:** `plans/stt-mvp-architecture-plan.md`  
**Repository:** `saffih/skeptic`  
**Planning base:** `ec9e8771e4bf9a4ecd03d3d9cd5ff0b1486d9887` plus the documentation-only commit that installs the corrected architecture plan  
**Historical parent:** `31451c8f45d5e9f2fe63434b37a2b7b02626a403`  
**Archived overbuilt history:** `archive/target-task-overbuilt-20260802`  
**Implementation authority:** STT MVP only

---

## 1. Objective

Implement the smallest complete STT MVP described by:

```text
plans/stt-mvp-architecture-plan.md
```

The implementation must prove:

```text
Mission
→ Planner
→ ordered Plan steps
→ Validator
→ terminal result
```

for the root Task and every child Task.

The implementation stops when all MVP qualification scenarios pass.

It must not restore, adapt, or maintain compatibility with the later archived Target Task system.

---

## 2. Starting conditions

Before implementation:

1. verify current branch descends from the final documentation commit containing:
   - corrected `plans/stt-mvp-architecture-plan.md`;
   - this `plans/stt-mvp-implementation-plan.md`;
2. verify the architecture file hash and record it in the first implementation commit message or implementation evidence;
3. verify the working tree is understood;
4. preserve unrelated work;
5. do not modify the archive;
6. do not merge or copy the old Target Task implementation wholesale.

The original accepted architecture commit `ec9e877…` is historical context. The corrected architecture file in the final documentation commit is the implementation source of truth.

---

## 3. Execution strategy

Build in small vertical slices.

Each slice must:

- add one coherent capability;
- include focused tests;
- preserve all previously passing STT tests;
- avoid speculative abstractions;
- end in a reviewable commit;
- provide a deterministic proof of the slice invariant.

Do not create the full directory skeleton before behavior requires it.

Do not implement later phases early.

---

## 4. Planned commits

Recommended commit sequence:

1. `stt: add canonical data and ledger core`
2. `stt: add task and plan contracts`
3. `stt: add provider boundary`
4. `stt: add mechanical lead and recursive tasks`
5. `stt: add safe workspace mutation`
6. `stt: add frozen runtime`
7. `stt: add cli and diagnostics`
8. `stt: qualify mvp invariants`

A commit may be split when review clarity improves. Do not combine unrelated slices.

No implementation commit should include archived Target Task compatibility.

---

## 5. Target file map

### 5.1 New production package

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

The recorded launcher is provider-neutral and performs exact executable
resolution, explicit argv invocation without shell interpolation, timeout and
termination classification, dispatch identity, request/raw-return persistence,
exit status, executable identity, truthful routing metadata, bounded returns,
and no semantic interpretation. Claude Code and Codex are thin mandatory
adapters translating the common request/return contract to each host CLI.
Without `--allow-live-provider`, both fail closed before launch. Actual
provider/model/effort values are recorded only when observable; otherwise they
are `UNKNOWN`. Deterministic controlled-executable tests qualify both adapters
without a paid live call.

### 5.2 CLI entry

```text
scripts/stt.py
```

### 5.3 Tests

```text
tests/concepts/stt/
├── __init__.py
├── helpers.py
├── test_ledger.py
├── test_run_lock.py
├── test_task.py
├── test_plan.py
├── test_boundary.py
├── test_lead.py
├── test_recursive_tasks.py
├── test_workspace.py
├── test_command.py
├── test_mutation_interruptions.py
├── test_runtime.py
├── test_context_bounds.py
├── test_launcher.py
├── test_provider_claude_code.py
├── test_provider_codex.py
├── test_cli.py
└── test_qualification.py
```

Use the repository’s existing test runner and naming conventions where they differ.

### 5.4 Optional small routing documentation change

Only if required for discoverability:

```text
AGENTS.md
```

may receive one compact pointer:

```text
STT runtime and architecture -> plans/stt-mvp-architecture-plan.md and concepts/stt/
```

Do not rewrite the current general Lead, Planner, Boundary, or Task Prompt contracts to behave like STT.

### 5.5 Files explicitly not used as runtime architecture

Do not import or depend on:

```text
archive/target-task-overbuilt-20260802/
```

Do not make active STT depend on the old Target Task lifecycle in:

```text
agents/lead_agent.md
agents/planner.md
agents/boundary_agent.md
workflows/task_prompt.md
```

Small deterministic code may be reimplemented from first principles after inspection. Prefer reimplementation when reuse would carry old contracts or state.

---

## 6. Cross-cutting implementation rules

### 6.1 Standard library first

Prefer:

- `dataclasses`;
- `pathlib`;
- `json`;
- `hashlib`;
- `subprocess`;
- `tempfile`;
- `os`;
- `shutil`;
- `stat`;
- `time`;
- `uuid`;
- `fcntl` on supported POSIX hosts for the Run writer lock.

Add no dependency unless it materially simplifies correctness and is already compatible with the repository.

### 6.2 Canonical JSON

All control-bearing JSON files use:

- UTF-8;
- sorted keys;
- compact stable separators;
- exactly one final LF;
- no NaN or Infinity;
- explicit schemas;
- bounded sizes.

Provide one canonical serializer and parser. Do not duplicate JSON canonicalization.

### 6.3 Hash identities

Use lowercase SHA-256.

Every persisted reference includes:

- relative path;
- SHA-256;
- byte size;
- artifact type.

### 6.4 Create-only or atomic publication

Control-bearing immutable files are written:

1. to a same-directory temporary file;
2. flushed;
3. file-fsynced where supported;
4. atomically renamed only when final publication semantics are safe;
5. directory-fsynced where supported;
6. reread and verified.

Append-only ledgers use one bounded canonical write, flush, and fsync per event while the Run writer lock is held. `MUTATION_INTENT` must be durable before live mutation begins.

Do not claim universal power-loss durability.

### 6.5 Errors

Use a small typed error hierarchy, for example:

```text
STTError
InvalidRun
InvalidTask
InvalidPlan
InvalidLedger
AuthorityViolation
ArtifactMismatch
ProviderFailure
WorkspaceSafetyError
MutationUnknown
```

CLI maps errors to bounded machine-readable and human-readable output.

Avoid a generalized error-state machine.

---

# Slice 1 — Canonical files and ledger

## 7. Goal

Implement the smallest trustworthy persistent primitives:

- canonical JSON;
- artifact references;
- hash-chained JSONL ledger;
- create-only publication;
- ledger validation;
- next sequence derivation;
- one OS-backed exclusive Run writer lock;
- narrow torn-tail diagnosis; incomplete artifacts are non-authoritative.

## 8. Production files

Create:

```text
concepts/stt/ledger.py
concepts/stt/run_lock.py
concepts/stt/receipt.py
```

A small shared utility module may be added only if both modules genuinely need it.

## 9. Ledger event schema

Every ledger line contains:

```json
{
  "schema": "stt.ledger-event.v1",
  "sequence": 1,
  "event": "TASK_CREATED",
  "timestamp": "informational",
  "payload": {},
  "previous_hash": null,
  "event_hash": "..."
}
```

Hash input excludes `event_hash` and uses canonical bytes.

Allowed events:

```text
TASK_CREATED
PLAN_ACCEPTED
STEP_STARTED
MUTATION_INTENT
STEP_FINISHED
TASK_FINISHED
```

Reject:

- missing sequence;
- non-contiguous sequence;
- duplicate sequence;
- unknown event;
- invalid previous hash;
- invalid event hash;
- malformed interior JSON;
- oversized line;
- event illegal for current lifecycle facts.

A single incomplete trailing fragment is diagnosed as an uncommitted torn append. Under the exclusive Run writer lock, preserve the fragment as diagnosis evidence, validate the complete prefix, and truncate only that tail. Any other corruption fails closed.

Implement `RunWriterLock` as one OS-backed exclusive file lock held by every mutating `start` or `run` invocation. A competing writer fails before reading or appending lifecycle state. On hosts without the supported lock primitive, mutating execution fails closed; do not implement leases or stale-lock recovery.

Do not yet implement full lifecycle transition policy in the ledger module. Keep event structural validation and provide hooks for Task-level semantic validation.

## 10. Tests

Prove:

- canonical round trip;
- identical objects produce identical bytes;
- one-byte change alters hash;
- valid chain passes;
- modified historical line fails;
- reordered lines fail;
- duplicate line fails;
- one torn trailing fragment is preserved, removed under lock, and the valid prefix survives;
- malformed interior or hash-corrupt line fails;
- unsupported event fails;
- first writer acquires the lock and a second writer is rejected;
- append returns new head;
- full bodies are rejected from ledger payloads by size or schema.

## 11. Commit acceptance

Focused tests pass.

No Task orchestration exists yet.

Commit:

```text
stt: add canonical data and ledger core
```

---

# Slice 2 — Task and Plan contracts

## 12. Goal

Implement:

- Task paths;
- immutable `task.json`;
- immutable `mission.md`;
- Plan schema;
- four exact step kinds;
- input and output references;
- authority validation;
- cursor derivation from Plan and ledger.

## 13. Production files

Create:

```text
concepts/stt/task.py
concepts/stt/plan.py
concepts/stt/workspace.py
concepts/stt/contracts/planner.md
concepts/stt/contracts/worker.md
concepts/stt/contracts/validator.md
```

Before Task creation, implement the common path-admission primitive and bounded `workspace-index.json` generation in `workspace.py`. The index covers the Task read authority, obeys the common path-admission exclusions for `.git`, `.stt`, symlinks, special files, and containment escape, uses deterministic entries, and emits explicit directory-summary overflow markers when its configured limit is reached. It never silently truncates and never grants authority.

## 14. Task creation

Implement:

```python
create_task(
    task_root,
    run_identity,
    task_id,
    mission_bytes,
    authority,
    role_bindings,
    initial_inputs,
    required_outputs,
    parent_binding=None,
)
```

It must validate all paths and authority before construction, then construct
the complete initial Task under a same-parent temporary directory. The
temporary directory contains `task.json`, `mission.md`, initial-input
bindings, the required-output contract, `workspace-index.json`, required
initial directories, and a valid first `TASK_CREATED` ledger event. Flush and
file-fsync where supported; reread and verify bytes, schemas, hashes, and the
ledger; fsync the temporary directory where supported; verify the final
deterministic path does not exist; atomically rename the complete temporary
directory; fsync its parent where supported; reread and verify the published
Task; only then return the compact reference. Root and child Tasks use this
same protocol. If same-parent atomic directory rename is unavailable or unsafe,
fail before publishing. A visible final Task always has `TASK_CREATED`.
Temporary residue is non-authoritative, may be diagnosed, and is never adopted
through recovery logic. A pre-existing final path fails closed.

## 15. Plan step schemas

Implement explicit dataclasses or typed dictionaries for:

```text
WorkerStep
CommandStep
MutationStep
TaskStep
```

Common fields:

```text
id
kind
description
inputs
outputs
success
```

Worker-only:

```text
worker_binding
instructions
write_scope
```

Command-only:

```text
argv
cwd
environment
timeout_seconds
expected_exit_codes
workspace_mutation=false
replay_safe
```

Mutation-only:

```text
replacement_input
```

Task-only:

```text
mission
authority
inputs
required output names and artifact types through common outputs
```

## 16. Plan validation

Validate:

- schema;
- Task and mission binding;
- unique stable step IDs;
- nonempty ordered steps where mission requires work;
- exact allowed fields;
- step-kind-specific required fields;
- no unknown step kinds;
- no future references;
- named-output references resolve;
- child authority subset;
- Worker binding exists in allowed frozen bindings;
- command mutation flag is false and `replay_safe` is explicit;
- mutation replacement input points to the same prior named output declared in common `inputs`;
- Task inputs resolve backward and its output contract is bound into the child Task;
- paths pass the common read/write admission primitive and are canonical and authorized.

Plan acceptance:

1. persist raw provider return separately;
2. parse exact Plan object;
3. canonicalize;
4. publish `plan.json`;
5. append `PLAN_ACCEPTED`;
6. on resume, use only a complete `PLAN_ACCEPTED` event and its verified canonical `plan.json`;
7. never replace accepted Plan; incomplete or conflicting publication content fails closed.

## 17. Cursor derivation

Implement a pure function:

```python
derive_task_state(task_root) -> TaskState
```

It reads:

- immutable Task identity;
- Plan when accepted;
- ledger;
- referenced results only as required.

It returns:

```text
NEEDS_PLAN
NEEDS_STEP
NEEDS_VALIDATION
TERMINAL
INVALID
```

and exact next step when applicable.

No mutable cursor file.

## 18. Tests

Prove:

- Task creation;
- root initial-input and bounded workspace-index binding, including overflow markers;
- child identity, initial-input, and required-output binding;
- authority narrowing;
- authority expansion rejection;
- valid Plan per step kind;
- unknown step kind rejection;
- duplicate ID rejection;
- future reference rejection;
- unauthorized path rejection;
- mutation input validation;
- accepted Plan cannot be replaced;
- incomplete and conflicting publication state fails closed;
- state derivation before and after each event.

## 19. Commit acceptance

All Slice 1 and Slice 2 tests pass.

Commit:

```text
stt: add task and plan contracts
```

---

# Slice 3 — Provider invocation and Boundary

## 20. Goal

Implement one mandatory Boundary façade around:

- Planner calls;
- Worker calls;
- Validator calls;
- deterministic operations;
- child creation and child return;
- persistence;
- compact receipts.

## 21. Production files

Create:

```text
concepts/stt/launcher.py
concepts/stt/boundary.py
concepts/stt/providers/__init__.py
concepts/stt/providers/fake.py
concepts/stt/providers/claude_code.py
concepts/stt/providers/codex.py
```

## 22. Provider protocol

Define the smallest interface:

```python
class Provider:
    def invoke(self, request: ProviderRequest) -> ProviderReturn:
        ...
```

Request fields:

```text
dispatch_id
role
provider
requested_model
requested_effort
maximum_attempts
attempt_number
live_provider_authorized
instruction_paths
input_references
output_schema
timeout_seconds
```

Return fields:

```text
dispatch_id
status
raw_bytes
provider_metadata
error
```

Provider unavailability never creates a fake semantic result:

- no accepted Planner output leaves `NEEDS_PLAN`;
- no accepted Worker output leaves the step unfinished;
- no accepted Validator output leaves `NEEDS_VALIDATION`.

The current run invocation returns an operational blocker and resume reuses persisted requests. Every attempt also persists `attempt-disposition.json` with `dispatch_id`, `role`, `attempt_number`, `request_identity`, `completion_kind`, `termination_state`, `retry_permitted`, `blocker_code`, and `raw_return_reference`. Boundary reads the latest disposition before every Planner, Worker, or Validator invocation and applies the closed vocabulary `ACCEPTED`, `COMPLETED_NONRETRIABLE`, `TIMED_OUT_CONFIRMED_TERMINATED`, `TERMINATION_UNKNOWN`. Only the third permits another attempt within finite `maximum_attempts`; all other blockers are returned without reinvocation, including after restart. No ledger event or retry state machine is added.

Do not require the current general Agent Completion Envelope when the provider already supplies equivalent structured identity and status.

Persist every raw return.

Only accepted structured outputs enter Task state.

## 23. Fake provider

The fake provider reads deterministic fixture responses keyed by dispatch ID or role.

It must support:

- valid Planner return;
- valid Worker return;
- valid Validator return;
- timeout;
- malformed return;
- mismatched dispatch;
- failure;
- oversized return.

It is the primary qualification provider.

Claude Code and Codex are thin translators over the common recorded-launcher
contract. Each maps the immutable request to host-specific argv and maps the
bounded return back; neither performs semantic interpretation or creates a
general plugin framework. Slice 3 owns both adapters and their deterministic
tests, and its acceptance gate requires all three launcher/provider tests to
pass.

## 24. Boundary API

Expose narrow methods:

```python
plan_task(task_ref)
execute_worker_step(task_ref, step_ref)
execute_command_step(task_ref, step_ref)
execute_mutation_step(task_ref, step_ref)
create_child_task(task_ref, step_ref)
finish_task_step_from_child(task_ref, step_ref, child_ref)
validate_and_finish_task(task_ref)
```

The Lead calls no provider or workspace function directly.

## 25. Bounded request construction

Boundary resolves each declared input through one of two explicit paths: workspace references use the common path-admission primitive and reject absolute paths, traversal, symlinks, special files, `.git`, `.stt`, and containment escape; accepted Task-artifact references under `.stt` are allowed only when declared and are validated by path, hash, size, type, producer, and authority. Deterministic Git observation, when used, is isolated from semantic role context.

It writes:

```text
<attempt-or-step>/request.json
```

before invocation.

A request contains references, not large bodies.

The provider adapter may load the referenced files for the actual model call, but the exact request remains reconstructible.

Enforce configurable conservative limits for:

- request bytes;
- raw provider return;
- Plan bytes;
- Worker result index;
- Validator result index;
- count of references;
- individual referenced artifact size where needed.

Large artifact bodies remain file-backed.

## 26. Planner Boundary path

1. validate Task state is `NEEDS_PLAN`;
2. load only the Task's persisted initial inputs, required-output contract, and deterministic workspace index;
3. construct and persist request;
4. invoke strong Planner binding;
5. persist raw return;
6. validate dispatch and provider status;
7. validate Plan;
8. accept first valid Plan;
9. append `PLAN_ACCEPTED`;
10. return compact receipt.

Retry policy: persist a finite explicit `maximum_attempts`. Do not retry any
completed provider return, including malformed, schema-invalid,
identity-mismatched, rejected, explicit failure, or semantically unsuccessful
returns. Retry only `transport timeout` with
`TIMED_OUT_CONFIRMED_TERMINATED` and `attempt_count < maximum_attempts`.
Persist `TERMINATION_UNKNOWN` and fail closed when termination is not positively
established. Each attempt has a monotonically numbered create-only directory;
no semantic corrective planning or replanning exists.

## 27. Worker Boundary path

1. validate current step;
2. resolve exact inputs;
3. persist request;
4. append `STEP_STARTED`;
5. invoke allowed Worker binding;
6. persist raw return;
7. validate replacement outputs and scope;
8. persist accepted result;
9. append `STEP_FINISHED`;
10. return compact receipt.

If Worker returns an accepted semantic failure, finish the step `FAILED`.
Completed malformed, schema-invalid, identity-mismatched, rejected, explicit,
or semantic failure returns are persisted and are not retried. Only a confirmed
terminated transport timeout within `maximum_attempts` may retry; unknown
termination fails closed. Other provider failures leave the step unfinished
and the current invocation stopped.

## 28. Validator Boundary path

1. validate Task requires validation;
2. create compact final index;
3. persist request in a monotonic attempt directory;
4. invoke a separate Validator role with Validator-specific instructions, no Planner or Worker conversation, and only persisted referenced evidence;
5. persist raw return;
6. validate result schema;
7. apply mechanical status floors, including failure when any required Task output is missing or mismatched;
8. verify every terminal output is either an accepted step output or a Boundary-assigned Validator artifact, including name, type, path, hash, and size;
9. publish validation report;
10. publish `result.json`;
11. verify only complete atomically published canonical artifacts; never adopt temporary residue;
12. append `TASK_FINISHED`;
13. return compact receipt.

Record requested provider/model/effort always; record actual provider/model/effort
only when observable, otherwise `UNKNOWN`. Never infer routing.

## 29. Tests

Prove:

- every provider call has unique dispatch ID;
- mismatched return rejected;
- raw return persists;
- malformed Plan never becomes accepted state;
- bounded request contains references, not bodies;
- oversized return fails;
- semantic roles cannot request `.git`, `.stt`, symlinks, special files, or containment escapes as workspace paths;
- exact declared Task-artifact references under `.stt` are accepted and arbitrary `.stt` reads are rejected;
- Worker cannot write outside assigned step output;
- child and Task terminal output provenance and required-output completeness are enforced;
- Validator receives no Planner or Worker conversation and hidden isolation is reported `UNKNOWN`;
- Validator `COMPLETE` is rejected when a step failed;
- failed step forces final `FAILED`;
- blocked step forces final `BLOCKED_UNKNOWN`;
- Planner/Worker/Validator provider outages remain nonterminal and resumable;
- compact receipts do not inline substantive content.

## 30. Commit acceptance

Slices 1–3 pass.

Slice 3 acceptance additionally requires `tests/concepts/stt/test_launcher.py`,
`tests/concepts/stt/test_provider_claude_code.py`, and
`tests/concepts/stt/test_provider_codex.py` to pass.

Commit:

```text
stt: add provider boundary
```

---

# Slice 4 — Mechanical Lead and recursive Tasks

## 31. Goal

Implement the one Lead loop and durable DFS recursion.

## 32. Production files

Create:

```text
concepts/stt/lead.py
```

Use `task.py` and `boundary.py`; do not duplicate lifecycle logic.

## 33. Lead API

```python
run_until_terminal(run_root)
advance_once(root_task_ref)
```

`advance_once` performs one bounded transition and returns one compact receipt.

`run_until_terminal` loops until:

- root terminal;
- genuine invalid state;
- operator interruption;
- provider/host boundary requires external intervention.

## 34. Child creation

When current step is `task`:

1. derive canonical child path;
2. resolve and validate declared child inputs and required-output contract;
3. if absent, Boundary creates child with those bindings;
4. if present, validate exact identity, inputs, outputs, and authority binding;
5. if unfinished, recurse/descend;
6. if terminal, Boundary validates output provenance and records parent step result;
7. return to the parent after every terminal child result, continuing later steps only after `COMPLETE`.

No separate child-state enum beyond ordinary Task state.

## 35. Failure path

If any step is non-`COMPLETE`:

- do not advance to later steps;
- call current Validator;
- return terminal result to parent through ordinary child result processing.

Prohibit a direct “propagate failure” function that writes ancestor terminal state.

## 36. Crash and resume cases

Implement and test:

### Case A

```text
parent STEP_STARTED
child absent
```

Safe action: create canonical child.

### Case B

```text
child TASK_CREATED
parent step unfinished
```

Safe action: resume child.

### Case C

```text
child TASK_FINISHED
parent step unfinished
```

Safe action: validate child and finish parent step.

### Case D

```text
parent STEP_FINISHED
child terminal
```

Safe action: continue parent.

### Case E

Conflicting child identity or duplicate child location.

Safe action: invalid run; stop.

## 37. Tests

Use realistic root/child/grandchild Plans.

Prove exact event order for:

```text
root Planner
root Task step start
child Planner
child Worker/Command steps
child Validator
parent child-step finish
root later step
root Validator
```

Prove:

- depth-first ordering;
- parent cursor remains on child step;
- no later parent step before child terminal success;
- child initial inputs and required outputs are bound;
- child result provenance is verified and referenced, not copied;
- failed child still leads to parent Validator;
- failed parent still leads to root Validator;
- grandchild failure validates every ancestor;
- no scheduler data file.

## 38. Commit acceptance

Recursive lifecycle tests pass.

Commit:

```text
stt: add mechanical lead and recursive tasks
```

---

# Slice 5 — Command and workspace mutation safety

## 39. Goal

Implement:

- one canonical read/write path admission primitive;
- read identity;
- staged replacement validation;
- non-mutating commands;
- before-images;
- mutation intent;
- deterministic installation;
- uncertainty handling.

## 40. Production files

Extend/create:

```text
concepts/stt/workspace.py  # extend the Slice 2 path/index primitive with file and tree identities
concepts/stt/command.py
concepts/stt/mutation.py
```

## 41. Path validation

Implement one shared canonical path admission primitive used at object-open time for all model-visible reads and all workspace writes.

Reject:

- absolute paths;
- empty control-bearing paths;
- `.` where a file is required;
- `..`;
- NUL;
- `.git` component;
- `.stt` component;
- any symlink path component;
- symlink leaf;
- special files;
- paths outside workspace after resolution;
- nested repository control paths when relevant.

Do not require Git.

## 42. File identities

The complete workspace identity for every entry is represented by:

```text
path
object_type
regular-file bytes/sha256 when applicable
symlink target when applicable
relevant regular-file mode bits where supported
relevant directory mode bits where supported
```

Use canonical `path`, `object_type`, regular-file `bytes`/`sha256` when
applicable, `symlink_target` when applicable, and relevant regular-file and
directory `mode_bits` where supported and meaningful, so a mode-only change
such as `chmod` is an unauthorized mutation and yields
`BLOCKED_UNKNOWN`. The MVP does not claim universal ACL, ownership, extended
attribute, or platform metadata coverage; unsupported required observations fail
closed or are explicitly outside the supported host contract.

Represent absence explicitly.

Before-image manifests must distinguish:

- existing file;
- absent path;
- existing required directory.

## 43. Replacement manifest

Define canonical schema:

```json
{
  "schema": "stt.replacement-manifest.v1",
  "entries": [
    {
      "path": "src/file.py",
      "operation": "create|replace|delete",
      "before": {},
      "replacement": {}
    }
  ]
}
```

Replacement bytes live in step-owned files.

Validate:

- unique paths;
- sorted canonical order;
- operation matches before-state;
- replacement hash/size;
- exact write authority;
- no overlapping file/directory contradiction.

## 44. Non-mutating command runner

Command runner:

1. validates exact argv;
2. resolves `argv[0]` to an absolute executable and records its observable identity;
3. validates cwd;
4. constructs a sanitized explicit environment plus bounded declared overrides;
5. validates mandatory `replay_safe`;
6. records pre-command complete workspace identity;
7. runs without shell;
8. streams complete stdout/stderr to files;
9. enforces timeout;
10. records exit code;
11. records post-command complete workspace identity;
12. detects unexpected mutation.

Workspace identity strategy for MVP:

- inspect the complete workspace tree, including `.git` and `.stt`;
- exclude only the exact Boundary-owned stdout, stderr, and temporary files expected to change during that command;
- record canonical path, object type, regular-file bytes, symlink target, and
  relevant regular-file and directory mode bits where supported;
- optimize implementation later only if the correctness scope remains complete;
- document that hostile processes are out of scope.

Unexpected change:

```text
BLOCKED_UNKNOWN
```

because the command’s effects may not be safely reversible or fully known.

A process disappearance or host interruption after command start but before a
durable result is fail-closed. Persist `TERMINATION_UNKNOWN` unless positive
termination is established. Replay requires all of: `replay_safe: true`, prior
state `TIMED_OUT_CONFIRMED_TERMINATED`, unchanged complete workspace identity,
and `attempt_count < maximum_attempts`; otherwise record `BLOCKED_UNKNOWN`.
Never infer that the command did not complete.

## 45. Mutation operation

Before writing:

1. validate replacement manifest;
2. re-observe every destination;
3. compare with admitted before-state;
4. write before-images and absence markers;
5. verify preserved before data;
6. append `MUTATION_INTENT`.

Installation:

- create parent directories only when real and authorized;
- write replacement to same-directory temporary sibling;
- fsync file where supported;
- atomically replace one file at a time;
- unlink only for declared delete;
- verify each final identity.

After all entries verify:

- write mutation result;
- append `STEP_FINISHED COMPLETE`.

No multi-file atomicity claim.

## 46. Interruption injection

Add deterministic test hooks at:

1. before `MUTATION_INTENT`;
2. immediately after `MUTATION_INTENT`;
3. before first file installation;
4. after one file installation;
5. after all installations before verification;
6. after result write before `STEP_FINISHED`;
7. after `STEP_FINISHED`.

Test hooks must not appear as a production recovery framework. They exist only to prove resume behavior.

## 47. Resume after uncertainty

When ledger contains `MUTATION_INTENT` without `STEP_FINISHED`:

- never call installation again;
- observe current destinations;
- write `uncertainty.json`;
- write step result `BLOCKED_UNKNOWN`;
- append `STEP_FINISHED`;
- run Validator.

This transition must be idempotent.

## 48. Tests

Prove:

- create/replace/delete;
- before-image exactness;
- absent-before marker;
- out-of-scope rejection;
- `.git` and `.stt` semantic read/write rejection;
- traversal and containment rejection;
- symlink-component and symlink-leaf read/write rejection;
- special-file read/write rejection;
- current-state mismatch rejection before intent;
- no mutation before intent;
- interruption before intent permits clean retry;
- interruption after intent never replays;
- partial multi-file mutation becomes `BLOCKED_UNKNOWN`;
- command stdout/stderr complete;
- command timeout;
- command nonzero exit;
- resolved executable identity and sanitized environment;
- full-workspace command accidental mutation detection;
- mode-only workspace mutation detection;
- malformed Planner output and completed provider failure are not retried;
- confirmed terminated timeout retries only within finite `maximum_attempts`;
- unknown termination blocks retry;
- `replay_safe: false`, changed workspace identity, and exhausted attempt budget each block command replay;
- replay-safe interrupted command retry only under the complete confirmed-timeout policy;
- non-replay-safe interrupted command `BLOCKED_UNKNOWN`;
- plain-directory success;
- Git repository success without using Git as authority.

## 49. Commit acceptance

Workspace safety and interruption matrix pass.

Commit:

```text
stt: add safe workspace mutation
```

---

# Slice 6 — Frozen runtime and dogfooding

## 50. Goal

Implement one frozen runtime per Run and prove self-modification safety.

## 51. Production files

Create:

```text
concepts/stt/runtime.py
concepts/stt/bootstrap.py
```

## 52. Runtime dependency allowlist

Define the runtime allowlist from explicit package files.

Do not recursively copy the repository.

Provide a function:

```python
collect_runtime_files(source_root) -> list[RuntimeFile]
```

It uses one maintained literal list of exact runtime paths. Do not use globs during reconstruction and do not derive a dynamic import graph for the MVP.

Tests must fail when a required runtime file is absent from the allowlist.

## 53. Freeze operation

`freeze_runtime`:

1. determines source root;
2. validates allowlist paths;
3. copies bytes into a temporary persistent bundle;
4. records exact file manifest plus Python interpreter realpath/version and observable provider/dependency identities;
5. verifies all bytes;
6. publishes bundle create-only;
7. creates active temporary control copy;
8. verifies active copy;
9. re-executes from active control.

Persist source provenance as informational metadata:

- source workspace path;
- source commit when Git is available;
- source file identities.

Runtime correctness for STT-owned control source relies on the bundle manifest, not Git. The operating system, interpreter installation, provider service, and complete host environment are not frozen.

## 54. Reconstruction

`reconstruct_runtime`:

1. reads persistent manifest;
2. validates bundle and required recorded external dependency compatibility;
3. creates fresh active control directory;
4. copies only bundle files;
5. verifies active identities;
6. re-executes.

It must not read runtime source from the target workspace.

## 55. Dogfood scenario

Create a fake-provider root mission whose Plan:

1. Worker prepares a change to one active STT source file in the target workspace;
2. mutation installs it;
3. command/test verifies target workspace content;
4. active generation A continues and validates successfully;
5. a new Run freezes generation B from the changed workspace.

Proofs:

- generation A runtime manifest remains unchanged;
- generation A imports remain under temporary control;
- deleting target workspace STT source after root creation does not stop generation A;
- generation B runtime identity differs and includes the new source.

## 56. Tests

Prove:

- exact literal allowlist and no reconstruction glob;
- manifest verification;
- interpreter and observable provider/dependency recording;
- incompatible required dependency fails visibly;
- excluded archive/tests/plans;
- missing active runtime reconstruction;
- corrupted persistent bundle rejection;
- no reconstruction from workspace;
- all child Tasks share root runtime identity;
- source modification does not affect active runtime;
- source deletion does not affect active runtime;
- generation B sees later source.

## 57. Commit acceptance

Frozen runtime and dogfood tests pass.

Commit:

```text
stt: add frozen runtime
```

---

# Slice 7 — CLI, status, and diagnosis

## 58. Goal

Expose the MVP without adding orchestration complexity.

## 59. Production files

Create:

```text
concepts/stt/cli.py
scripts/stt.py
```

## 60. Commands

### `start`

```text
stt start --workspace <path> --mission-file <path> --provider <fake|claude-code|codex> [--model <value>] [--effort <value>] [--maximum-attempts <positive-integer>] [--allow-live-provider] [--evidence <relative-path>]...
```

`provider` is required. `maximum_attempts` is finite and positive; omitted
model/effort persist as `UNSPECIFIED`. `fake` never requires live authorization;
`claude-code` and `codex` fail before launch without `--allow-live-provider`.
Unsupported provider/model/effort combinations fail closed. `live_provider_authorized`
is frozen in `run.json` at start; `stt run` cannot add or remove it, and any
binding change requires a new Run.

Behavior:

1. validate workspace;
2. read mission;
3. validate explicit evidence references;
4. bind provider routes;
5. create unique Run root;
6. freeze runtime and re-execute from frozen control without reading Task lifecycle state;
7. acquire the exclusive writer lock in the frozen process before lifecycle publication;
8. build and persist the deterministic root workspace index;
9. create root Task with initial inputs and required outputs;
10. run until terminal;
11. print compact terminal receipt.

### `run`

```text
stt run --run-root <path>
```

Behavior:

- validate and reconstruct the persistent runtime without reading Task lifecycle state;
- re-execute from frozen control;
- acquire the exclusive Run writer lock in the frozen process or fail without lifecycle action;
- validate persistent lifecycle state;
- resume Lead;
- do not change provider, model, effort, maximum attempts, or authorization;
- print compact receipt.

### `status`

```text
stt status --run-root <path>
```

Behavior:

- reconstruct and re-execute from the Run's frozen control without reading Task lifecycle state;
- acquire a shared nonblocking Run lock;
- report `RUN_BUSY` without reading changing lifecycle state when a writer is active;
- otherwise remain read-only and validate ledgers;
- report:
  - run ID;
  - runtime identity;
  - root status;
  - deepest active Task;
  - next action;
  - blocker;
  - terminal result reference.

### `diagnose`

```text
stt diagnose --run-root <path>
```

Behavior:

- reconstruct and re-execute from the Run's frozen control without reading Task lifecycle state;
- acquire a shared nonblocking Run lock;
- report `RUN_BUSY` when a writer is active;
- otherwise remain strictly read-only and report invalid identity, missing file, ledger corruption, mutation uncertainty, or provider failure;
- never write diagnosis artifacts or repair automatically.

## 61. Output

Use canonical JSON option and readable text option.

No full logs or bodies on stdout.

Print precise paths and hashes.

## 62. Exit codes

Define a small stable set, for example:

```text
0 COMPLETE or successful read-only query
2 FAILED
3 BLOCKED_UNKNOWN
4 INVALID_RUN
5 USAGE_ERROR
```

Avoid mapping every internal error to a public exit code.

## 63. Tests

Prove:

- start to COMPLETE with fake provider;
- start to FAILED;
- start to BLOCKED_UNKNOWN;
- resume unfinished child;
- status no mutation;
- diagnose ledger corruption;
- no body leakage to stdout;
- plain directory;
- path with spaces;
- multiple Runs without collisions;
- competing writer rejected;
- status and diagnose report `RUN_BUSY` without reading changing state while a writer exists.

## 64. Commit acceptance

CLI scenarios pass.

Commit:

```text
stt: add cli and diagnostics
```

---

# Slice 8 — Full qualification and cleanup

## 65. Goal

Prove every architecture qualification scenario, remove accidental complexity, and stop.

## 66. Qualification test

Create one top-level qualification module:

```text
tests/concepts/stt/test_qualification.py
```

It should compose existing helpers rather than duplicate all low-level assertions.

Run at least these end-to-end scenarios.

### Q1 — Simple research Task

```text
root Planner
→ command/worker evidence step
→ root Validator
→ COMPLETE
```

### Q2 — Root mutation Task

```text
Planner
→ Worker staged replacement
→ mutation
→ command test
→ Validator
→ COMPLETE
```

### Q3 — Child Task

```text
root Planner
→ child Task
→ child Planner
→ child steps
→ child Validator
→ parent continuation
→ root Validator
```

### Q4 — Grandchild Task

Prove exact DFS order.

### Q5 — Child semantic failure

Prove:

- child Validator runs;
- parent Validator runs;
- root Validator runs;
- no later sibling step runs.

### Q6 — Mutation uncertainty

Interrupt after `MUTATION_INTENT`.

Prove:

- no replay;
- current Task `BLOCKED_UNKNOWN`;
- every ancestor Validator runs;

### Q7 — Retry and provider contracts

Prove malformed Planner output and completed provider failure are not retried;
only a confirmed terminated timeout retries within finite `maximum_attempts`;
unknown termination blocks; and command replay is blocked by
`replay_safe: false`, changed workspace identity, or exhausted budget. Use
controlled fake executables to prove launcher argv, request/raw-return
persistence, timeout classification, bounded output, dispatch mismatch,
requested routing, observable actual routing, truthful `UNKNOWN`, unavailable
executable failure, and `--allow-live-provider` enforcement for both Claude
Code and Codex. No paid live call is made.

### Q8 — Atomic Task publication

Prove root and child creation constructs all initial authoritative files under a
same-parent temporary directory, including `TASK_CREATED`, then publishes by
atomic rename and verifies the final directory. Inject interruption before
temporary construction completes, after temporary files exist, and immediately
after rename; prove temporary residue is non-authoritative, a pre-existing final
path fails closed, complete published Tasks resume normally, no visible final
Task lacks `TASK_CREATED`, and parent-directory fsync limitations are reported
honestly.

### Q9 — Command safety

Prove resolved executable identity, sanitized environment, complete-workspace accidental-mutation detection, replay-safe interruption retry, and non-replay-safe `BLOCKED_UNKNOWN`.

### Q10 — Plain directory

No `.git` exists.

Full successful change and validation.

### Q11 — Git repository

Git exists but STT does not commit, stage, or use Git as lifecycle authority.

### Q12 — Dogfood generation

Generation A modifies target STT source and completes from frozen A. Generation B freezes changed source.

### Q13 — Writer and durable publication

Prove a competing writer is rejected and one torn trailing ledger append is
recovered under lock. Task temporary residue is non-authoritative and is never
adopted; conflicting or incomplete publication state fails closed, and
mutation uncertainty is never bypassed.

### Q14 — Child evidence and output provenance

Prove root/child initial-input ownership, child required-output binding, and rejection of Validator-invented or mismatched terminal outputs.

The complete qualification set is 101 scenarios: baseline scenarios 1–74 and
the explicit added scenarios 75–101 below.

#### Added numbered scenarios

#### Retry and persisted blocker behavior

75. Malformed Planner is not retried in process.
76. Malformed Planner remains blocked after restart.
77. Completed Worker failure remains blocked after restart.
78. Completed Validator failure remains blocked after restart.
79. Confirmed terminated timeout retries within budget.
80. Exhausted timeout remains blocked after restart.
81. Unknown termination remains blocked after restart.

#### Recorded launcher and provider adapters

82. The canonical attempt disposition persists.
83. Request identity binds the attempt disposition.
84. The Claude Code adapter translates the common request.
85. The Codex adapter translates the common request.
86. Both live adapters fail before launch without authorization.
87. Omitted model and effort remain explicitly unspecified.
88. Unsupported provider combinations fail closed.

#### Permission-only mutation detection

89. Regular-file mode-only mutation is detected.
90. Directory mode-only mutation is detected.
91. Canonical path and object type are recorded.
92. Regular-file bytes and symlink target are recorded where applicable.
93. ACL, ownership, and extended-attribute limits are reported honestly.

#### Atomic Task publication

94. Root publication has `TASK_CREATED` before rename.
95. Child publication has `TASK_CREATED` before rename.
96. Interruption before temporary construction leaves no authoritative final Task.
97. Temporary residue is non-authoritative.
98. Post-rename interruption verifies the final directory.
99. A pre-existing final path fails closed.
100. Complete publication resumes normally.
101. No visible final Task lacks `TASK_CREATED`.

## 67. Active reachability check

Add a deterministic test that imports or statically scans active STT modules and fails if they import:

```text
archive.target-task-overbuilt
concepts.target_task
```

Adapt exact prohibited namespaces to actual repository paths.

Also reject references to archived lifecycle terms in production STT source when they imply active behavior:

```text
Fix Loop
Find Loop
three-pass
ADVANCE
candidate commit
rollback
scheduler
```

Documentation comments explaining exclusions are allowed.

## 68. Context-bound tests

Instrument fake provider requests.

Assert:

- Lead receipt maximum remains small;
- Planner receives only mission, authority, required outputs, explicit initial inputs, and deterministic workspace index;
- Worker receives only declared inputs;
- Validator receives final index plus selected files;
- child ledger is not included in parent provider requests;
- command logs are referenced, not inlined.

Use byte limits as test configuration constants rather than hidden magic numbers.

## 69. Full repository tests

Run:

- focused STT suite;
- full repository test suite;
- Python compile checks;
- formatting/lint checks already used by the repository;
- shell syntax for scripts;
- `git diff --check`.

Do not add a new tool solely for this implementation unless necessary.

## 70. Complexity review

Before final commit, inspect:

- module count;
- duplicated schema logic;
- duplicated path logic;
- duplicated lifecycle logic;
- unused abstractions;
- dead compatibility code;
- broad exception catches;
- unbounded context;
- hidden Git assumptions.

Remove mechanisms that are not required by an invariant or qualification test.

Do not optimize for an arbitrary line-count target. Explain any unusually large module.

## 71. Final commit

Commit:

```text
stt: qualify mvp invariants
```

Stop after all qualification scenarios and the full repository suite pass.

Do not begin later recovery, concurrency, rollback, publication, or generalized orchestration work.

---

## 72. Detailed invariant-to-code map

| Architecture invariant | Primary code | Primary tests |
|---|---|---|
| one Task lifecycle | `task.py`, `lead.py` | `test_lead.py`, `test_qualification.py` |
| one Run writer | `run_lock.py`, CLI/bootstrap | `test_run_lock.py`, qualification |
| durable publication and non-authoritative temporary residue | `launcher.py`, `task.py`, `boundary.py` | torn-tail/publication tests |
| every Task plans | `boundary.py`, `lead.py` | `test_lead.py`, `test_recursive_tasks.py` |
| four step kinds | `plan.py` | `test_plan.py` |
| every call through Boundary | `lead.py`, `boundary.py` | `test_boundary.py`, call spies |
| durable DFS | `task.py`, `lead.py` | `test_recursive_tasks.py` |
| child evidence/output contract and result return | `boundary.py`, `task.py` | `test_recursive_tasks.py` |
| every Task validates | `lead.py`, `boundary.py` | failure propagation tests |
| failure does not bypass ancestors | `lead.py` | child/grandchild failure tests |
| Task-local ledger | `ledger.py`, `task.py` | `test_ledger.py`, recursion tests |
| context references, not bodies | `boundary.py`, `receipt.py` | `test_context_bounds.py` |
| common read/write path admission | `workspace.py`, `boundary.py` | `test_workspace.py`, boundary tests |
| separate Validator role invocation | `boundary.py`, provider | validator context tests |
| Workers stage only | `boundary.py`, `workspace.py` | `test_boundary.py`, `test_workspace.py` |
| commands non-mutating and replay-explicit | `command.py` | `test_command.py` |
| deterministic mutation only | `mutation.py` | `test_workspace.py` |
| before-images | `mutation.py` | before-image tests |
| intent before mutation | `mutation.py`, `ledger.py` | interruption matrix |
| uncertainty never replayed | `mutation.py`, `lead.py` | `test_mutation_interruptions.py` |
| one frozen runtime | `runtime.py`, `bootstrap.py` | `test_runtime.py` |
| reconstruction from bundle | `runtime.py` | runtime deletion tests |
| plain directories | `workspace.py` | plain-directory E2E |
| Git optional | `workspace.py` | Git/plain comparison |
| no archived compatibility | package imports | active reachability test |

---

## 73. Schema and file acceptance checklist

Before declaring MVP complete, verify:

### Run

- `run.json` canonical;
- runtime identity present;
- root path fixed;
- bindings fixed;
- mutating execution holds one exclusive writer lock.

### Task

- `task.json` immutable;
- mission hash correct;
- `workspace-index.json` bounded, deterministic, and identity-bound;
- parent binding correct;
- initial inputs and required outputs bound;
- authority canonical;
- ledger begins with matching `TASK_CREATED`.

### Plan

- canonical;
- four kinds only;
- references backward only;
- outputs named;
- authority valid;
- Task input/output contract valid;
- command replay safety explicit;
- immutable after acceptance.

### Step

- deterministic directory;
- request persisted before invocation;
- raw return preserved;
- accepted result canonical;
- one terminal `STEP_FINISHED`;
- incomplete or temporary result is non-authoritative and conflicting publication fails;
- mutation orphan results never bypass `MUTATION_INTENT` uncertainty.

### Child

- canonical path;
- parent Plan hash bound;
- initial inputs and required outputs bound;
- result provenance verified before parent finish;
- no child history copied upward.

### Validator

- final index bounded;
- separate role invocation with no Planner/Worker conversation;
- hidden isolation reported honestly;
- report persisted;
- output provenance and mechanical status/required-output floors applied;
- `TASK_FINISHED` commits report and result.

### Mutation

- before-images;
- replacement bytes;
- intent event;
- installed verification;
- no replay after uncertainty.

### Runtime

- literal exact allowlist;
- interpreter and observable external dependency identity recorded;
- persistent bundle verified;
- active copy verified;
- no workspace import after freeze.

---

## 74. Expected implementation risks and smallest responses

### Risk: Plan schema becomes a workflow language

Response:

- keep only four kinds;
- no conditions;
- no loops;
- no dynamic branching;
- no arbitrary operation plugins.

### Risk: Boundary becomes a monolith

Response:

- Boundary remains the single façade;
- delegate deterministic algorithms to focused modules;
- do not create multiple gateways or agent roles.

### Risk: Provider adapter dictates architecture

Response:

- keep a small provider protocol;
- isolate host details under `providers/`;
- qualify with fake provider.

### Risk: economical Worker causes bad mutation

Response:

- narrow step;
- exact scope;
- staged output;
- deterministic manifest validation;
- allow strong Worker only when frozen and selected;
- independent final Validator;
- honest failure.

### Risk: command mutates unexpectedly or is replayed ambiguously

Response:

- command steps declare non-mutation and `replay_safe`;
- resolve executable and sanitize environment;
- complete-workspace before/after identity;
- `BLOCKED_UNKNOWN` on unexpected mutation or unsafe interrupted replay;
- no rollback.

### Risk: self-update imports changed workspace code

Response:

- re-exec early;
- assert module paths are under frozen control;
- runtime tests delete workspace STT source.

### Risk: old Target Task code is tempting to reuse

Response:

- active reachability test;
- no compatibility imports;
- reimplement small primitives with STT schemas.

### Risk: two processes advance one Run

Response:

- one OS-backed exclusive writer lock;
- second writer fails before lifecycle action;
- no scheduler, lease, or distributed lock.

### Risk: resume logic grows into recovery framework

Response:

- derive state from ledger;
- support only specified interruption cases and one torn trailing append; temporary residue is never adopted;
- diagnose all other invalid state;
- no automatic generalized repair.

---

## 75. Definition of done

The STT MVP is done when:

1. the corrected architecture file remains the source of truth;
2. all planned production files are implemented or deliberately consolidated;
3. every qualification scenario passes;
4. focused STT tests pass;
5. full repository tests pass;
6. active STT has no archived Target Task reachability;
7. plain-directory and Git-directory scenarios both pass;
8. competing writer and torn-tail proofs pass; Task publication uses complete
   same-parent temporary directories and never adopts temporary residue;
9. root, child, and grandchild lifecycle proofs pass;
10. child evidence and terminal-output provenance proofs pass;
11. every failure path still calls every ancestor Validator;
12. mutation uncertainty is never replayed;
13. frozen runtime dogfood passes with honest external-dependency limits;
14. CLI start/run/status/diagnose pass;
15. no compatibility or deferred feature was added;
16. final diff contains no unexplained mechanism;
17. all Planner, Worker, and Validator retry paths have finite
    `maximum_attempts` and require `TIMED_OUT_CONFIRMED_TERMINATED`;
18. mandatory recorded launcher, Claude Code adapter, and Codex adapter tests
    pass with `--allow-live-provider` enforcement and no paid call;
19. complete workspace identity observes supported mode bits and detects a
    mode-only mutation;
20. root and child Task creation has no visible final directory without
    `TASK_CREATED`;
21. implementation stops.

---

## 76. Final execution instruction

```text
Implement only plans/stt-mvp-architecture-plan.md.

Use this implementation plan as the ordered build map.

Begin from the final documentation commit containing both plans.

Make small reviewable commits.

For each slice:
- implement the smallest vertical behavior;
- add focused deterministic tests;
- run prior STT tests;
- inspect the diff for unnecessary machinery;
- commit only when the slice invariant is proven.

Do not copy the archived Target Task lifecycle.
Do not add compatibility.
Do not add concurrency, rollback, generalized recovery, RunSkeptic loops,
three-pass convergence, ADVANCE protocols, Git publication, or remote
integration.

Stop when the STT MVP qualification scenarios and full repository tests pass.
Do not continue into later features.
```
