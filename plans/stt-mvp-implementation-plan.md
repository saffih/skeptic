# STT MVP Complete Implementation Plan

**Status:** Corrected implementation plan; execute only against the companion architecture in the same documentation revision  
**Architecture source of truth:** `plans/stt-mvp-architecture-plan.md`  
**Repository:** `saffih/skeptic`  
**Implementation authority:** STT MVP only

---

## 1. Objective

Implement the smallest complete STT described by the architecture plan.

The implementation must prove the ordinary and failure-shortened lifecycle for root, child, and grandchild Tasks:

```text
Mission
→ Planner attempt
→ accepted Plan or persisted planning failure
→ sequential steps until first non-COMPLETE
→ recorded SKIPPED later steps
→ Validator
→ terminal result
```

The implementation stops when the canonical qualification inventory, focused STT suite, and full repository suite pass.

Do not restore or adapt the archived Target Task lifecycle.

---

## 2. Starting conditions

Before implementation:

1. verify both plans are read from the same documentation commit;
2. record their blob identities in implementation evidence;
3. verify the working tree and preserve unrelated work;
4. leave the archive unchanged;
5. confirm no active STT implementation is being silently treated as authoritative;
6. begin with the smallest vertical slice.

If either plan changes materially during implementation, stop, review the change, and explicitly rebind the implementation to the new document identities.

---

## 3. Build rules

Each slice must:

- implement one coherent vertical behavior;
- include focused deterministic tests;
- preserve all earlier STT tests;
- keep schemas and path rules single-sourced;
- end in a reviewable commit;
- prove its invariant before the next slice.

Do not:

- create a generalized workflow engine;
- add conditions, loops, plugins, or concurrency;
- add recovery beyond the specified interruption cases;
- make Git lifecycle authority;
- add automatic rollback or publication;
- let provider adapters define core architecture;
- claim prevention where only detection exists;
- hide failures by retrying completed failure evidence;
- continue implementation after an unresolved architecture conflict.

---

## 4. Planned commits

Recommended sequence:

1. `stt: add canonical persistence and run locking`
2. `stt: add start spec and frozen runtime`
3. `stt: add task plan and confined attempts`
4. `stt: add boundary and recursive lead`
5. `stt: add command and mutation safety`
6. `stt: add cli and diagnostics`
7. `stt: qualify mvp architecture`

Split a commit only when it improves reviewability. Do not combine unrelated slices.

---

## 5. Target package

```text
concepts/stt/
├── __init__.py
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
    ├── __init__.py
    ├── fake.py
    ├── claude_code.py
    └── codex.py
```

CLI entry:

```text
scripts/stt.py
```

Tests:

```text
tests/concepts/stt/
├── helpers.py
├── qualification_inventory.py
├── test_canonical.py
├── test_ledger.py
├── test_run_lock.py
├── test_runtime.py
├── test_bootstrap.py
├── test_task.py
├── test_plan.py
├── test_attempt.py
├── test_launcher.py
├── test_provider_claude_code.py
├── test_provider_codex.py
├── test_boundary.py
├── test_lead.py
├── test_recursive_tasks.py
├── test_command.py
├── test_mutation.py
├── test_context_bounds.py
├── test_cli.py
└── test_qualification.py
```

Modules may be consolidated when two responsibilities are clearer together. The invariants and tests, not this exact module count, are authoritative.

---

## 6. Cross-cutting primitives

### 6.1 Canonical JSON

Use one serializer and parser:

- UTF-8;
- sorted keys;
- compact stable separators;
- exactly one final LF;
- no NaN or Infinity;
- explicit schema field;
- configured byte and collection limits.

### 6.2 References

Every persisted artifact reference contains:

```text
path
sha256
byte_size
artifact_type
producer
```

Use lowercase SHA-256.

### 6.3 Publication

Immutable control-bearing files use:

1. same-directory temporary sibling;
2. write;
3. flush;
4. file sync where supported;
5. atomic publication;
6. parent directory sync where supported;
7. reread and verify.

Ledger events use one bounded canonical append while the writer lock is held, followed by flush and sync before success is reported.

Do not claim universal power-loss durability.

### 6.4 Errors

Use a small typed hierarchy:

```text
STTError
InvalidRun
InvalidStartSpec
InvalidRuntime
InvalidTask
InvalidPlan
InvalidLedger
AuthorityViolation
ArtifactMismatch
AttemptFailure
ProviderFailure
WorkspaceSafetyError
MutationUnknown
```

Do not create a generalized error-state machine.

---

# Slice 1 — Canonical persistence and Run locking

## 7. Goal

Implement:

- canonical JSON;
- immutable artifact references;
- hash-chained JSONL ledger;
- narrow torn-tail handling;
- create-only and atomic publication helpers;
- one OS-backed Run writer lock;
- compact receipts.

## 8. Ledger schema

Every event contains:

```json
{
  "schema": "stt.ledger-event.v1",
  "sequence": 1,
  "event": "TASK_CREATED",
  "payload": {},
  "previous_hash": null,
  "event_hash": "..."
}
```

Allowed event names:

```text
TASK_CREATED
PLAN_ACCEPTED
PLANNING_FAILED
STEP_STARTED
MUTATION_INTENT
STEP_FINISHED
TASK_FINISHED
```

For an eligible Plan step, persist an exact immutable request built from accepted Plan references, then append `STEP_STARTED` before any fallible input materialization, executable resolution, current-state observation, invocation, mutation preparation, or child publication that can produce a step result. Structural corruption that prevents request construction is `INVALID_RUN`. Repeating `STEP_STARTED` is valid only for the identical bound identity.

`STEP_FINISHED SKIPPED` is the only step result that has no preceding `STEP_STARTED`; every other step result requires one.

Reject:

- unknown events;
- missing, duplicate, or non-contiguous sequence;
- invalid chain or event hash;
- malformed interior lines;
- oversized events;
- illegal status vocabulary;
- event payloads that inline substantive bodies;
- event ordering impossible under Task semantics.

A single incomplete trailing append may be preserved as diagnosis evidence and removed under the writer lock after the complete prefix validates. Every other corruption fails closed.

## 9. Run lock

Implement one exclusive filesystem lock held by every mutating `start` or `run` process before lifecycle state is read or written.

Read-only operations use a shared nonblocking lock. While a writer exists, they return `RUN_BUSY` without reading changing state.

Unsupported lock hosts fail closed. Do not implement leases or stale-lock recovery.

## 10. Slice 1 tests

Prove:

- canonical round trip and stable bytes;
- one-byte change alters identity;
- valid ledger chain;
- historical modification, reorder, duplicate, gap, and interior corruption fail;
- one torn trailing append is handled narrowly;
- first writer succeeds and second writer fails before lifecycle action;
- read-only query reports `RUN_BUSY`;
- large bodies are rejected from ledger payloads;
- compact receipts contain only references and state.

## 11. Slice 1 acceptance

Focused tests pass.

Commit:

```text
stt: add canonical persistence and run locking
```

---

# Slice 2 — Start specification and frozen runtime

## 12. Goal

Implement:

- canonical immutable `start-spec.json`;
- literal runtime allowlist;
- external runtime manifest;
- persistent bundle;
- active-control reconstruction and re-execution;
- post-re-exec provider and confinement probes through frozen adapters;
- immutable probe record and `run.json` binding;
- unique Run creation.

## 13. Start specification

Implement an exact parser for:

```json
{
  "schema": "stt.start-spec.v1",
  "workspace_root": "/absolute/path",
  "mission": {
    "path": "/path",
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

Validate canonical workspace-relative authority paths; unique initial-input and required-output names; exact `workspace` versus `host-file` input schemas; unique route names; common route fields; mission and input identities; output contracts; the positive finite operation attempt limit; and authorization before Run publication. The operation limit applies to Planner, Worker, and replay-safe Command attempts. The Validator limit is not configurable: it is exactly two attempts, one initial attempt plus one fresh retry when no usable result exists.

The host adapter may create this file, but Bootstrap consumes only the persisted canonical object. The mission and every `host-file` input must be explicitly supplied absolute regular files with no symlink component. A `workspace` input must pass ordinary object-open path admission. Host files are materialized as evidence without granting workspace authority. `UNSPECIFIED` model or effort remains explicit. After frozen re-execution, Bootstrap may reread mission or input paths only through no-follow object-open validation and exact hash-and-size verification; changed or missing bytes fail before `TASK_CREATED`.

## 14. Provider probe

Freeze and re-execute first. Before `TASK_CREATED`, probe every selected route using only the frozen adapter modules.

Persist:

- executable realpath and file identity;
- version when observable;
- required noninteractive and structured-output support;
- model/effort validation where observable;
- live-provider authorization;
- the exact Boundary-controlled semantic-attempt confinement mechanism, including a controlled non-model write-escape canary;
- proof that semantic roles receive no command, connector, network-action, or other side-effecting tool authority beyond provider transport and confined `in/`/`out/`;
- probe result identity.

Publish one immutable probe record and bind its identity with the start specification and runtime manifest in `run.json`. The probe is local and deterministic where possible. It must not require a paid semantic provider call.

A missing executable, unsupported required flag or capability, unresolved route, unproven semantic write confinement, or exposed side-effecting semantic tool fails before Task creation.

Provider-specific CLI syntax remains inside its adapter.

Publish canonical `provider-probes.json`, then canonical create-only `run.json`:

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

Validate every reference before root Task publication. `root_task_path` is deterministic metadata only; Task lifecycle starts with the root `TASK_CREATED` event.

## 15. Runtime allowlist and manifest

Maintain one literal list of exact active runtime paths.

The generated layout is:

```text
runtime/
├── manifest.json
└── bundle/
```

`manifest.json` is not copied into `bundle/` and does not hash itself.

Freeze:

1. validates allowlist entries;
2. copies exact bytes to a temporary bundle;
3. records each bundled path, hash, size, and relevant mode;
4. records the Python interpreter identity needed for control reconstruction;
5. verifies the bundle;
6. publishes it create-only;
7. creates and verifies active control;
8. re-executes under active control.

Provider executable and capability identities live in the later immutable probe record, not in the already-published runtime manifest. Reconstruction reads only the persistent bundle and manifest, never current workspace STT source; route use additionally verifies the probe record and current executable identity.

## 16. Slice 2 tests

Prove:

- valid and invalid exact start specifications, including route/input/output uniqueness and field validation;
- workspace versus host-file input admission;
- mission and initial-input hash/size mismatches fail before Task creation, including after frozen re-execution;
- route choices and attempt limits are frozen;
- provider probe success and fail-before-Task behavior;
- probes execute from frozen adapter module paths, not target-workspace adapter source;
- canonical probe record and `run.json` bind start-spec, runtime, and route identities;
- `run.json` cannot imply root Task creation before `TASK_CREATED`;
- fake and controlled live-adapter probes without paid calls;
- literal allowlist and required-file coverage;
- manifest never lists itself;
- bundle corruption fails;
- missing active control reconstructs;
- reconstruction does not read target workspace source;
- unique Run IDs do not collide.

## 17. Slice 2 acceptance

Slices 1–2 pass.

Commit:

```text
stt: add start spec and frozen runtime
```

---

# Slice 3 — Task, Plan, and confined semantic attempts

## 18. Goal

Implement:

- atomic Task publication;
- workspace index and path admission;
- Task and Plan schemas;
- four step kinds;
- named inputs and outputs;
- fresh semantic attempt roots;
- dispositions and bounded retry classification.

## 19. Common path admission

Implement one object-open-time primitive for semantic workspace reads and workspace writes.

Reject:

- absolute and empty control paths;
- traversal and containment escape;
- `.git` and `.stt`;
- symlink components and leaves;
- special files;
- unauthorized paths.

Exact Task artifacts under `.stt` use a separate identity-bound reference path and never grant arbitrary `.stt` access.

## 20. Workspace index

Build deterministic `workspace-index.json` over Task read authority.

When the configured bound is exceeded, use deterministic directory summaries and explicit overflow markers. Never silently truncate and never treat the index as permission.

## 21. Task publication

Implement:

```python
create_task(
    task_root,
    run_identity,
    task_id,
    mission_bytes,
    authority,
    role_bindings,
    attempt_policy,
    initial_inputs,
    required_outputs,
    parent_binding=None,
)
```

Construct the complete initial Task under a same-parent temporary directory containing:

- `task.json`;
- `mission.md`;
- `workspace-index.json`;
- required directories;
- first valid `TASK_CREATED` event.

Validate, sync where supported, atomically rename, reread, and verify.

A visible final Task always contains `TASK_CREATED`. Temporary residue is non-authoritative and never adopted. A pre-existing final path fails closed.

## 22. Plan schema

Implement exact types:

```text
WorkerStep
CommandStep
MutationStep
TaskStep
```

Validate:

- exact schema and allowed fields;
- unique stable IDs;
- exact four kinds;
- backward-only references;
- named outputs;
- required-output types;
- authorized canonical paths;
- narrowed child authority;
- allowed frozen Worker route;
- explicit command `replay_safe`;
- mutation replacement input from one earlier Worker output;
- no conditions, loops, or arbitrary operation plugins.

A Plan candidate stays inside its unique Planner attempt `out/`. `PLAN_ACCEPTED` selects that exact path, hash, and size; there is no Task-root Plan copy. The selected bytes are immutable.

Planning failure stays inside its unique Planner attempt and `PLANNING_FAILED` selects that exact failure result; it does not invent an empty Plan.

## 23. Attempt root

Implement in `attempt.py`:

```text
attempt-NNN/
├── request.json
├── disposition.json
├── in/
├── out/
├── stdout.log
├── stderr.log
└── raw-return.bin
```

Rules:

- attempt numbers are monotonic;
- directories are create-only;
- `in/` contains exact verified materialized inputs and is read-only;
- `out/` begins empty and is the only semantic writable location;
- target workspace and authoritative Task state are outside semantic write authority;
- the adapter launches with only the attempt context and fixed role contract;
- Launcher revalidates the probed executable identity and confinement before every invocation;
- Launcher owns a process group and acceptance requires confirmed termination of that group;
- after confirmed provider-process termination, Boundary closes provider-owned handles, syncs where supported, rejects non-regular output objects, makes outputs read-only where supported, and seals their exact hash and size;
- the ledger selects exact attempt-owned files by path, hash, size, type, and producer;
- no second canonical artifact copy is published;
- an attempt never writes the ledger.

Use Boundary-controlled operating-system or equivalent host enforcement to make `out/` the only writable semantic path. Provider prompt or tool-permission flags alone are insufficient for filesystem confinement. Separately, the adapter must expose no command, connector, network-action, or other side-effecting semantic tool; provider transport to the selected model service is not a semantic tool. Bootstrap records both proofs, and supported-route tests must prove them; otherwise the route fails before `TASK_CREATED`.

## 24. Attempt disposition

Closed classes:

```text
ACCEPTED
OPERATION_FAILED
INTERRUPTED_CONFIRMED_TERMINATED
TERMINATION_UNKNOWN
```

Persist:

```text
dispatch_id
role
attempt_number
request_identity
completion_kind
termination_state
retry_permitted
blocker_code
raw_return_reference
observed_provider
observed_model
observed_effort
```

Rules:

- completed failure evidence becomes `OPERATION_FAILED` and is not retried;
- confirmed terminated or unknown-termination Planner/Worker interruption may retry in a fresh root within budget because supported routes are confined and expose no side-effecting semantic tools;
- exhausted Planner/Worker interruption budget becomes `BLOCKED_UNKNOWN`;
- Validator no-usable-result receives one fresh retry after either interruption class or another unusable return, then falls back to `VALIDATOR_UNAVAILABLE`;
- actual routing is `UNKNOWN` when unobservable;
- attempts are never overwritten;
- every created attempt consumes one unit of the applicable finite budget.

## 25. Provider protocol

Use a small protocol:

```python
class Provider:
    def probe(self, route: Route) -> ProbeResult:
        ...

    def invoke(self, request: ProviderRequest, attempt_root: Path) -> ProviderReturn:
        ...
```

`ProviderReturn` contains dispatch identity, process status, raw return reference, observed routing metadata, and structured-output reference. Large bytes remain file-backed.

The fake provider supports success, explicit failure, malformed result, mismatch, confirmed interruption, unknown termination, oversized output, executable-identity drift, and confinement violation.

Claude Code and Codex remain thin adapters. Do not build a plugin framework.

## 26. Slice 3 tests

Prove:

- root and child Task publication;
- no final Task without `TASK_CREATED`;
- authority narrowing and expansion rejection;
- workspace index overflow behavior;
- all path rejections;
- every valid Plan kind and all invalid reference cases;
- planning failure without Plan;
- fresh attempt directories and no shared mutable state;
- confinement violation fails;
- accepted outputs become authoritative only through ledger selection after sealing and validation;
- failed attempt output is never promoted;
- disposition classification and finite retry;
- requested versus observed routing truthfulness;
- executable identity and confinement are revalidated before each attempt.

## 27. Slice 3 acceptance

Slices 1–3 pass.

Commit:

```text
stt: add task plan and confined attempts
```

---

# Slice 4 — Boundary and recursive Lead

## 28. Goal

Implement:

- one mandatory Boundary façade;
- bounded request construction;
- Planner, Worker, Validator paths;
- failure-to-Validator semantics;
- recorded skipped steps;
- mechanical Validator-unavailable fallback;
- recursive depth-first Lead.

## 29. Boundary API

Expose only narrow entry points:

```python
plan_task(task_ref)
execute_worker_step(task_ref, step_ref)
execute_command_step(task_ref, step_ref)
execute_mutation_step(task_ref, step_ref)
create_child_task(task_ref, step_ref)
finish_parent_step_from_child(task_ref, step_ref, child_ref)
finish_remaining_steps_skipped(task_ref, cause_ref)
validate_and_finish_task(task_ref)
```

Lead must not call providers, command, mutation, workspace, ledger, or publication helpers directly.

## 30. Planner path

1. verify Task needs planning;
2. build and persist bounded request;
3. create fresh attempt root;
4. invoke Planner route;
5. persist raw evidence and disposition;
6. on `ACCEPTED`, validate and seal the attempt-owned Plan, then append `PLAN_ACCEPTED` selecting its exact reference;
7. on `OPERATION_FAILED`, persist planning failure and append `PLANNING_FAILED FAILED`;
8. on exhausted confirmed interruptions or unknown termination, append `PLANNING_FAILED BLOCKED_UNKNOWN`;
9. return compact receipt.

A planning failure proceeds to Validator.

## 31. Worker path

1. verify the step is structurally eligible and construct its request from accepted references;
2. create the fresh attempt root and persist that exact request;
3. append `STEP_STARTED` binding the step, attempt root, request identity, and route;
4. materialize and verify declared inputs into `in/`;
5. if a valid input can no longer be materialized, finish `BLOCKED_UNKNOWN`; if an accepted reference is corrupt, stop `INVALID_RUN`;
6. invoke the allowed Worker route;
7. persist raw evidence and disposition;
8. validate output scope and schemas;
9. seal and re-verify accepted attempt-owned outputs;
10. append `STEP_FINISHED COMPLETE`, `FAILED`, or `BLOCKED_UNKNOWN` selecting their exact references;
11. return compact receipt.

Malformed, rejected, identity-mismatched, explicit, or semantic failure is a persisted failed step, not an indefinitely unfinished step.

## 32. Skipped steps

After the first non-`COMPLETE` Plan step, Boundary appends one `STEP_FINISHED SKIPPED` result for each later step in order.

Each skipped result is bounded ledger metadata with no separate result file. It binds:

- skipped step ID;
- causal step ID;
- causal status;
- no outputs;
- reason `EARLIER_STEP_NON_COMPLETE`.

This is idempotent. Existing matching skipped records are accepted; conflicts fail closed.

## 33. Validator path

Build a bounded final index containing:

- mission and authority;
- accepted Plan or planning-failure evidence;
- every complete, failed, blocked, and skipped step;
- child terminal results;
- selected command and mutation evidence;
- required outputs;
- final covered workspace identities.

Invoke Validator in a fresh confined attempt with no Planner or Worker conversation.

A valid structurally conforming negative or uncertain result is accepted without retry. A malformed, schema-invalid, identity-mismatched, interrupted, or otherwise unusable Validator attempt counts as no usable result. The second attempt is permitted by the same confined, no-side-effect semantic-attempt contract.

When no usable result exists:

1. persist the failed Validator attempt;
2. make one fresh retry if no retry has yet occurred;
3. if the retry also yields no usable result, create a unique Boundary-owned `validation/fallback-NNN/result.json` with:
   - status `BLOCKED_UNKNOWN`;
   - blocker `VALIDATOR_UNAVAILABLE`;
   - both attempt references;
   - no invented semantic outputs;
4. append `TASK_FINISHED` selecting that exact fallback reference;
5. return compact receipt.

Fallback directories are monotonically numbered and create-only. A complete fallback file without `TASK_FINISHED` is uncommitted and ignored; resume creates a new fallback directory rather than adopting or overwriting it.

The Validator may author only its validation report. Its terminal output list must select already accepted step outputs; Boundary rejects invented, rewritten, mismatched, or unproven mission outputs. Apply these output checks and the exact mechanical floors before accepting any Validator result:

- known missing, mismatched, unauthorized, or unproven required output → `FAILED`;
- required-output identity or provenance cannot be established → `BLOCKED_UNKNOWN`;
- any earlier `BLOCKED_UNKNOWN` → `BLOCKED_UNKNOWN`;
- otherwise any earlier `FAILED` → at least `FAILED`.

## 34. Semantic orphan handling

On restart, if attempt files exist without their committing ledger event:

- validate the ledger first;
- mark the attempt abandoned when mechanically classifiable;
- never adopt its semantic outputs;
- retry only in a fresh confined root and within the finite budget;
- apply the same finite semantic interruption policy after restart, including when prior remote completion is unknown; record possible duplicate provider calls, cost, and lingering provider work;
- otherwise commit the operation as `FAILED` or `BLOCKED_UNKNOWN` and continue to Validator.

Restart adds no special retry exception. Do not overwrite or adopt the orphan.

## 35. Lead

Implement:

```python
advance_once(root_task_ref)
run_until_terminal(run_root)
```

`advance_once` performs one bounded transition.

For a Task step, Boundary persists the exact child-creation request and appends `STEP_STARTED` before resolving current input bytes or publishing/resuming the canonical child. The event binds parent Plan, step, child mission, authority references, inputs, required outputs, and child path. A valid input that can no longer be materialized finishes the parent step `BLOCKED_UNKNOWN`; corrupted accepted references make the Run invalid.

The Lead:

- derives state from ledger and immutable artifacts;
- descends only through the canonical current child;
- returns to parent after child terminal result;
- records skipped later steps after first non-`COMPLETE`;
- calls Validator after planning or execution failure;
- never writes lifecycle state directly;
- carries compact references only.

## 36. Recursive interruption cases

Prove:

```text
parent STEP_STARTED + child absent
→ create canonical child

child TASK_CREATED + parent step unfinished
→ resume child

child TASK_FINISHED + parent step unfinished
→ validate child and finish parent step

parent STEP_FINISHED + child terminal
→ continue parent

conflicting child identity
→ invalid Run
```

## 37. Slice 4 tests

Prove:

- exact root, child, and grandchild event order;
- planning failure reaches Validator;
- Worker failure records later steps skipped;
- child failure reaches parent and root Validators;
- `BLOCKED_UNKNOWN` floors propagate;
- valid negative Validator result is not retried;
- no-result Validator after either interruption class succeeds on one fresh retry;
- two no-result attempts produce mechanical `VALIDATOR_UNAVAILABLE`;
- Validator cannot invent or rewrite required Task outputs;
- known output defects floor to `FAILED`, while unresolvable provenance floors to `BLOCKED_UNKNOWN`;
- orphan semantic output is not adopted;
- compact receipts and contexts contain no substantive bodies;
- no scheduler or mutable cursor exists.

## 38. Slice 4 acceptance

Slices 1–4 pass.

Commit:

```text
stt: add boundary and recursive lead
```

---

# Slice 5 — Command and mutation safety

## 39. Goal

Implement:

- covered complete-workspace identities;
- exact command-control exclusions;
- cooperative non-mutating command detection;
- strict command replay;
- staged replacement manifests;
- before-images;
- durable mutation intent;
- deterministic mutation and uncertainty handling.

## 40. Command-control exclusion manifest

Before the pre-command scan, create one dedicated command-attempt control directory and an immutable manifest naming that exact directory, its permitted file set, and each file's mutability class.

Exclude that entire exact control directory from both target-workspace scans. This avoids a snapshot containing or depending on its own pre-state file. Independently verify the excluded directory: request, resolved executable record, sanitized environment, manifest, and pre-state identities are immutable; only declared stdout/stderr files may change; no undeclared path may appear.

All other `.stt`, `.git`, and workspace paths remain inside the comparison.

The command receives no `.stt` path as an input. Hostile command behavior remains outside the guarantee.

## 41. Workspace identity

Record, where supported:

```text
canonical path
object type
regular-file size and SHA-256
symlink target
relevant regular-file mode
relevant directory mode
```

Include `.git` and `.stt` except exact command exclusions.

Document unsupported ACL, ownership, extended attributes, outside-workspace side effects, network effects, and write-then-restore behavior.

## 42. Command runner

1. validate the accepted command-step schema and construct the immutable command request;
2. create the command-control directory and exclusion manifest;
3. append `STEP_STARTED` binding the request and exclusion manifest;
4. resolve and verify executable realpath and identity;
5. validate current canonical cwd;
6. create the sanitized explicit environment;
7. validate timeout and `replay_safe`;
8. compute the complete pre-state, retain its expected identity in the live Boundary process, and persist an evidence copy inside the excluded directory;
9. invoke without shell;
10. stream logs to Boundary-owned files;
11. enforce timeout and classify termination;
12. record post-state before any other lifecycle or non-excluded workspace write;
13. detect unexpected covered changes;
14. write step result.

Nonzero expected-status failure becomes `FAILED`. Unexpected covered mutation or unsafe interruption becomes `BLOCKED_UNKNOWN`. Any Boundary-process crash after `STEP_STARTED` makes the command `BLOCKED_UNKNOWN` without replay; STT does not reconstruct whether launch or external side effects occurred.

Replay requires:

- `replay_safe: true`;
- confirmed terminated interruption;
- unchanged covered workspace identity;
- remaining finite attempt budget.

## 43. Replacement manifest

Use:

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

Replacement bytes live in accepted Worker artifacts.

Validate unique sorted paths, exact authority, correct before-state, replacement identities, and no file/directory contradiction.

## 44. Mutation

Before live change:

1. validate the accepted replacement-manifest reference and construct the immutable mutation request;
2. append `STEP_STARTED` binding that request;
3. validate manifest paths and authority;
4. re-observe destinations;
5. compare admitted before-state;
6. on mismatch, append `STEP_FINISHED BLOCKED_UNKNOWN` without intent;
7. persist and verify before-images and absence markers;
8. persist and verify replacement bytes;
9. append durable `MUTATION_INTENT`.

Then perform regular-file create, replace, or delete one path at a time and verify final identities.

After all entries verify, publish the mutation result and append `STEP_FINISHED COMPLETE`.

## 45. Mutation interruption

Inject deterministic test interruptions:

- before intent;
- immediately after intent;
- before first installation;
- after one installation;
- after all installations before verification;
- after result write before `STEP_FINISHED`;
- after `STEP_FINISHED`.

`STEP_STARTED` without `MUTATION_INTENT` safely resumes preparation. After intent without finish:

- never rerun installation;
- inspect current state;
- persist uncertainty evidence;
- append `STEP_FINISHED BLOCKED_UNKNOWN`;
- skip later steps;
- run Validator.

This transition is idempotent.

## 46. Slice 5 tests

Prove:

- command explicit argv, resolved executable, sanitized environment;
- exact command-control directory exclusion avoids self-reference, is symmetric, and is independently verified;
- stdout and stderr persistence;
- nonzero exit and timeout;
- unexpected file, directory, and mode changes detected;
- replay-safe confirmed interruption retry;
- replay blocked by false flag, changed state, unknown termination, exhausted budget, or Boundary-process crash after `STEP_STARTED`;
- replacement create, replace, delete;
- out-of-authority, traversal, symlink, special-file, `.git`, and `.stt` rejection;
- exact before-images and absence markers;
- current-state mismatch becomes `BLOCKED_UNKNOWN` after `STEP_STARTED` and before intent;
- `STEP_STARTED` without intent safely resumes preparation;
- no mutation before intent;
- no replay after intent;
- partial multi-file change becomes `BLOCKED_UNKNOWN`;
- plain-directory and Git-directory behavior.

## 47. Slice 5 acceptance

Slices 1–5 pass.

Commit:

```text
stt: add command and mutation safety
```

---

# Slice 6 — CLI and diagnostics

## 48. Goal

Expose the implemented lifecycle without adding orchestration.

## 49. Commands

```text
stt start --start-spec <path>
stt run --run-root <path>
stt status --run-root <path>
stt diagnose --run-root <path>
```

### `start`

1. validate the start specification, workspace, authority, inputs, outputs, routes, and attempts, including the initial mission and input identities;
2. create a unique Run root and persist the canonical start specification;
3. freeze and re-execute from runtime;
4. acquire the writer lock;
5. probe providers and confinement through frozen adapters;
6. reopen the mission and every `host-file` input with no-follow validation and re-verify their exact hashes and sizes;
7. publish the immutable probe record and `run.json` binding;
8. create the root Task from the re-verified exact mission and input bytes;
9. run until terminal;
10. print compact result.

A failure before `TASK_CREATED` leaves a diagnosable non-lifecycle Run root and requires a new `start`; it is not resumed as a Task.

### `run`

- reconstruct frozen control before lifecycle reads;
- acquire writer lock;
- validate Run and Task state;
- resume Lead;
- never modify bindings or authorization.

### `status`

- reconstruct frozen control;
- acquire shared nonblocking lock;
- return `RUN_BUSY` while writer active;
- otherwise report validated compact state without mutation.

### `diagnose`

- strictly read-only;
- report identity mismatch, ledger corruption, provider failure, confinement failure, mutation uncertainty, or missing runtime;
- never repair automatically.

## 50. Output and exit codes

Support canonical JSON and concise readable output. Never print full logs or artifacts.

Stable exits:

```text
0 COMPLETE or successful read-only query
2 FAILED
3 BLOCKED_UNKNOWN
4 INVALID_RUN
5 USAGE_ERROR
```

## 51. Slice 6 tests

Prove:

- start to each terminal status;
- planning failure still reaches terminal Validator result;
- unfinished child resume;
- semantic orphan resume;
- mutation uncertainty resume;
- status and diagnose do not mutate;
- `RUN_BUSY`;
- path with spaces;
- multiple Runs without collisions;
- no body leakage to stdout.

## 52. Slice 6 acceptance

Slices 1–6 pass.

Commit:

```text
stt: add cli and diagnostics
```

---

# Slice 7 — Canonical qualification

## 53. Goal

Mechanically prove every architecture obligation, remove accidental complexity, and stop.

## 54. Qualification inventory format

Create:

```text
tests/concepts/stt/qualification_inventory.py
```

It defines records:

```python
Qualification(
    id="Q001",
    primary_obligation="A01",
    proof_kind="test",
    target="tests.concepts.stt.test_qualification::test_root_lifecycle",
    case="root-success",
    description="Root Task attempts Planner and Validator.",
)
```

Rules enforced by a meta-test:

- every architecture obligation `A01`–`A25` appears;
- every qualification ID is unique;
- every qualification has exactly one primary obligation;
- every `test` target exists;
- every `command` target is one of the explicit repository acceptance commands;
- every `(proof_kind, target, case)` tuple is unique;
- no unknown obligation or proof reference exists;
- no inventory item is silently skipped;
- the qualification runner executes every test item and records every command item.

Secondary obligation tags may exist but do not replace the one primary owner.

## 55. Canonical qualification cases

### Lifecycle and propagation

| ID | Primary | Required proof |
|---|---|---|
| Q001 | A01 | Root successful lifecycle. |
| Q002 | A01 | Child successful lifecycle. |
| Q003 | A01 | Grandchild successful lifecycle and exact depth-first order. |
| Q004 | A02 | Planner explicit failure is persisted and Validator runs without a Plan. |
| Q005 | A02 | Malformed Planner output becomes planning failure, not an accepted Plan. |
| Q006 | A03 | Worker failure records every later step `SKIPPED`. |
| Q007 | A03 | Blocked command records every later step `SKIPPED`. |
| Q008 | A04 | Failed child causes child, parent, and root Validators. |
| Q009 | A04 | Grandchild `BLOCKED_UNKNOWN` validates every ancestor. |
| Q010 | A05 | Valid negative Validator result is accepted without retry. |
| Q011 | A05 | Validator no-result succeeds on one fresh retry. |
| Q012 | A05 | Two Validator no-results create mechanical `VALIDATOR_UNAVAILABLE`. |

### Plan, authority, and Boundary

| ID | Primary | Required proof |
|---|---|---|
| Q013 | A06 | Exactly four Plan step kinds are accepted. |
| Q014 | A06 | Future references, duplicate IDs, and unknown fields fail. |
| Q015 | A06 | Child authority expansion fails. |
| Q016 | A06 | Required outputs and named artifact types bind correctly. |
| Q017 | A07 | Lead reaches every substantive operation only through Boundary. |
| Q018 | A07 | Boundary rejects dispatch, identity, hash, size, or provenance mismatch. |
| Q019 | A19 | Lead receipts and provider requests obey configured byte bounds. |
| Q020 | A19 | Parent references child outputs without copying child history. |

### Fresh attempts, failures, and retry

| ID | Primary | Required proof |
|---|---|---|
| Q021 | A08 | Planner attempts use distinct fresh roots. |
| Q022 | A08 | Worker attempts share no mutable output state. |
| Q023 | A08 | A controlled non-model canary cannot write outside `out/`, and no side-effecting semantic tool is exposed, or the route fails before Task creation. |
| Q024 | A08 | Failed attempt artifacts are never selected by the ledger. |
| Q025 | A09 | A Boundary-crash orphan, including one with unknown remote completion, is never adopted and resumes under the same finite confined retry policy. |
| Q026 | A09 | Confirmed terminated semantic interruption retries in a fresh root within budget. |
| Q027 | A09 | Exhausted budget finishes operation blocked and proceeds to Validator. |
| Q028 | A09 | Planner or Worker unknown-termination interruption retries only in a fresh confined root within budget; old output is never adopted. |
| Q029 | A09 | Attempt directories are create-only and never overwritten. |

### Command

| ID | Primary | Required proof |
|---|---|---|
| Q030 | A10 | Explicit argv, resolved executable, and sanitized environment. |
| Q031 | A10 | Exact exclusion manifest is identical for pre/post comparison. |
| Q032 | A10 | Excluded Boundary control artifacts are independently verified. |
| Q033 | A10 | Unexpected file or directory mutation is detected. |
| Q034 | A10 | Relevant mode-only mutation is detected. |
| Q035 | A10 | Unsupported metadata and external side-effect limits are reported honestly. |
| Q036 | A11 | Replay-safe confirmed interruption retries with unchanged state. |
| Q037 | A11 | Replay is blocked by false flag, changed state, unknown termination, exhausted budget, or Boundary crash after `STEP_STARTED`. |

### Mutation and publication

| ID | Primary | Required proof |
|---|---|---|
| Q038 | A12 | Create, replace, and delete use accepted Worker replacements. |
| Q039 | A12 | Current-state mismatch occurs after `STEP_STARTED`, finishes `BLOCKED_UNKNOWN`, and never writes intent. |
| Q040 | A12 | `MUTATION_INTENT` is durable before first live change. |
| Q041 | A12 | Every post-intent interruption avoids replay and becomes blocked. |
| Q042 | A12 | Partial multi-file mutation is visible and not rolled back. |
| Q043 | A13 | Root Task publishes atomically with `TASK_CREATED`. |
| Q044 | A13 | Child Task publishes atomically with `TASK_CREATED`. |
| Q045 | A13 | Temporary Task residue is non-authoritative and pre-existing final path fails. |
| Q046 | A14 | One torn trailing ledger append is handled narrowly. |
| Q047 | A14 | Interior corruption and conflicting canonical artifacts fail closed. |

### Child, runtime, provider, environment

| ID | Primary | Required proof |
|---|---|---|
| Q048 | A15 | Child identity, input, authority, and parent binding are verified. |
| Q049 | A15 | Child output and terminal-output provenance are verified. |
| Q050 | A16 | Runtime manifest is outside bundle and never hashes itself. |
| Q051 | A16 | Active generation survives workspace STT modification and deletion. |
| Q052 | A16 | Generation B freezes later changed source with a different identity. |
| Q053 | A17 | Exact route schemas, executable identities, and capabilities are probed through frozen adapters and bound in `run.json` before Task creation. |
| Q054 | A17 | Unsupported confinement, exposed side-effecting semantic tool, or unsupported route fails before `TASK_CREATED`. |
| Q055 | A17 | Requested versus observed provider/model/effort is reported truthfully. |
| Q056 | A18 | Complete successful Run in a plain directory. |
| Q057 | A18 | Complete successful Run in Git without using Git as lifecycle authority. |
| Q058 | A20 | Active modules cannot import archived Target Task lifecycle namespaces. |
| Q059 | A21 | Inventory meta-test detects missing, duplicate, unknown, or nonexistent mappings. |
| Q060 | A22 | Qualification runner records frozen-runtime dogfood, focused suite, and full repository suite commands as passing. |
| Q061 | A23 | Frozen re-execution uses the exact identity-bound mission and initial inputs; changed source bytes fail before Task creation. |
| Q062 | A24 | Known required-output defects floor to `FAILED`; unresolvable identity or provenance floors to `BLOCKED_UNKNOWN`. |
| Q063 | A24 | Validator may author its report but cannot invent, rewrite, or replace Task outputs. |
| Q064 | A25 | Every Worker, Command, Mutation, and Task step commits its exact request before fallible preparation; only structural corruption can fail earlier as `INVALID_RUN`. |

This table is the one canonical qualification inventory. Q1-style prose scenarios elsewhere are explanatory only and may not compete with it.

## 56. Additional deterministic checks

Add:

- static active-reachability scan;
- context-size instrumentation;
- exact event-order assertions;
- compile checks;
- repository formatting and lint checks already in use;
- shell syntax checks;
- `git diff --check`.

No new tool is added solely for ceremony.

## 57. Complexity review

Before final acceptance inspect:

- duplicate schemas;
- duplicate path checks;
- duplicate lifecycle logic;
- provider-specific behavior leaking into Boundary;
- hidden Git assumptions;
- broad exception catches;
- unused abstractions;
- compatibility code;
- unbounded context;
- retry loops not justified by a qualification case.

Remove anything not required by an architecture obligation or qualification case.

## 58. Slice 7 acceptance

All Q001–Q064 cases, inventory meta-test, focused STT suite, and full repository suite pass.

Commit:

```text
stt: qualify mvp architecture
```

Stop. Do not begin concurrency, rollback, generalized recovery, compatibility, or publication work.

---

## 59. Invariant-to-code map

| Architecture obligation | Primary production code | Primary qualification |
|---|---|---|
| A01–A05 lifecycle and Validator | `boundary.py`, `lead.py`, `task.py` | Q001–Q012 |
| A06 Plan | `plan.py`, `task.py` | Q013–Q016 |
| A07 Boundary | `boundary.py`, `receipt.py` | Q017–Q018 |
| A08–A09 attempts and orphans | `attempt.py`, `launcher.py`, `boundary.py` | Q021–Q029 |
| A10–A11 command | `command.py`, `workspace.py` | Q030–Q037 |
| A12 mutation | `mutation.py`, `ledger.py` | Q038–Q042 |
| A13–A14 publication and ledger | `task.py`, `ledger.py` | Q043–Q047 |
| A15 children and provenance | `task.py`, `boundary.py`, `lead.py` | Q048–Q049 |
| A16 runtime | `runtime.py`, `bootstrap.py` | Q050–Q052 |
| A17 provider probes | `launcher.py`, `providers/` | Q053–Q055 |
| A18 environment | `workspace.py`, CLI | Q056–Q057 |
| A19 context bounds | `boundary.py`, `receipt.py` | Q019–Q020 |
| A20 archive exclusion | package imports | Q058 |
| A21 traceability | qualification inventory | Q059 |
| A22 whole-system proof | qualification runner and repository commands | Q060 |
| A23 bound bootstrap inputs | `bootstrap.py`, `task.py` | Q061 |
| A24 output floors and provenance | `boundary.py`, `task.py` | Q062–Q063 |
| A25 started-operation binding | `boundary.py`, `command.py`, `mutation.py`, `task.py` | Q064 |

---

## 60. Definition of done

STT MVP is done when:

1. both plan identities are recorded;
2. all required production behavior exists or is deliberately consolidated;
3. all Q001–Q064 cases execute and pass;
4. the mapping meta-test passes;
5. focused and full repository suites pass;
6. every ordinary failure reaches Validator and every ancestor Validator;
7. later steps are visibly `SKIPPED`;
8. Validator no-result behavior is bounded and visible;
9. semantic attempts are fresh and confined;
10. orphan semantic output is never adopted;
11. command limitations are stated truthfully and covered mutations are detected;
12. mutation uncertainty is never replayed;
13. runtime manifest does not hash itself;
14. provider capabilities, confinement, and absence of side-effecting semantic tools are proved before Task creation;
15. frozen re-execution uses the exact identity-bound mission and initial inputs;
16. required-output floors are deterministic and Validator cannot invent Task outputs;
17. every started operation binds its exact identity before execution;
18. plain and Git directory scenarios pass;
19. active code has no archived lifecycle reachability;
20. no unexplained mechanism remains;
21. implementation stops.

---

## 61. Final execution instruction

```text
Implement only the STT MVP architecture in
plans/stt-mvp-architecture-plan.md.

Use this file as the ordered vertical build map.

Begin from the documentation revision containing both corrected plans.

For every slice:
- implement the smallest complete behavior;
- add deterministic focused tests;
- run all prior STT tests;
- inspect the diff for unnecessary machinery and overclaims;
- commit only after the slice invariant is proven.

Do not copy the archived Target Task lifecycle.
Do not add compatibility, concurrency, rollback, generalized recovery,
RunSkeptic runtime loops, Git publication, or remote integration.

Stop after Q001–Q064, the mapping meta-test, the focused STT suite, and the full
repository suite pass.
```
