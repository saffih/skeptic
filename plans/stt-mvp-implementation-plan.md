# STT MVP Implementation Plan

**Status:** Retained historical evidence only; not a current Implementation Plan or implementation authority
**Historical companion Architecture:** `plans/stt-mvp-architecture-plan.md`
**Recorded historical Architecture SHA-256:** `921ee38e92a1f1a9df7ac2a977fd46877ccdfde75965d274479d6f51432f079d`
**Current shared/durable realization authority:** `plans/stt-mvp-software-design-description.md`
**Current Implementation Plan:** None exists yet
**Repository:** `saffih/skeptic`
**Historical reconstruction base:** `74c4f6a2c34da501101141525c8a34d691c384a1`
**Document profile:** `docs/well.md`
**Implementation scope:** STT MVP only

Every following proposition is retained historical evidence from the prior canonical-pair candidate and is not current authority, instruction, start, completion, or merge authorization, because the accepted SDD now owns STT shared and durable realization decisions and no bounded current Implementation Plan has been created.

This document owns the exact construction contract, including serialization, filesystem conventions, algorithms, state derivation, and executable proof, because implementers must not guess how to realize architecture-owned meaning.

The architecture remains the sole authority for runtime semantics, because an implementation detail may specialize but may not redefine mission judgment, operational authority, retry safety, context freedom, or lifecycle meaning.

Implementation stops and the architecture is repaired first whenever this plan cannot derive one unambiguous mechanism from the architecture, because silent interpretation would create an unreviewed design branch inside code.

---

## 1. Entry, change, and stop gates

Production implementation may begin only from the externally recorded commit containing the unchanged accepted architecture and implementation plan, because construction requires one reviewed semantic and mechanical base.

A change to architecture-owned meaning requires an architecture repair before this plan changes, because implementation review cannot authorize a semantic design decision.

A change limited to serialization, layout, algorithm, construction order, or proof updates this plan without changing architecture, because those mechanisms are implementation-owned when they preserve every architecture invariant.

Implementation is complete only when every canonical qualification scenario passes, repository regression passes, the real-model evaluation has no unresolved material finding, and no production mechanism lacks an architecture owner, because partial proof cannot support promotion.

Archived Target Task code and contracts are not imported, because compatibility with superseded semantics would create a second lifecycle.

---

## 2. Build discipline and ownership

Build the runtime as the following vertical slices, because each slice ends in executable behavior rather than broad unproved scaffolding:

1. canonical storage, ledgers, transition packages, and state derivation
2. Bootstrap, Run publication, frozen runtime, target identity, and prior import
3. canonical contracts, authority admission, artifacts, and read-only STT tools
4. launcher, exchanges, provider adapters, commands, settlement, and proven non-launch
5. Planner admission, step execution, child Tasks, and depth-first Lead
6. Validator judgment, repeated Rounds, terminalization, and operator stop
7. CLI, diagnosis, integration, adversarial qualification, and promotion

Each slice preserves all earlier scenarios and lands as one reviewable commit, because reversible proof-bearing increments expose contract drift early.

The following mechanisms are prohibited unless architecture changes first, because they would add semantic or operational authority absent from the accepted MVP:

- mutable lifecycle cursor
- automatic retry after actual or uncertain launch
- model or provider fallback hidden from the accepted Plan
- semantic progress score or novelty gate
- runtime cap on Plan steps, Task count, Task depth, or Round count
- same-mission child rejection
- caller approval between Validator `REPEAT` and the next Round
- curated history package as the only semantic context
- target sandbox, rollback, or complete-effect claim
- archive-runtime compatibility layer

One production owner implements each responsibility, because duplicate paths would create competing lifecycle or schema authority:

| Responsibility | Canonical owner |
|---|---|
| canonical bytes, hashing, create-only publication | `storage.py` |
| transition packages and Task ledgers | `transition.py`, `ledger.py` |
| pure validation and state derivation | `state.py` |
| schemas and identity derivation | `contracts.py`, `identity.py` |
| authority, routes, and command profiles | `authority.py`, `routing.py` |
| host probes, locks, target identity, frozen runtime | `host.py`, `runtime.py`, `bootstrap.py` |
| read-only STT filesystem tools | `history_tools.py` |
| target workspace index and observation | `workspace.py` |
| exchange, launcher, providers, and commands | `exchange.py`, `launcher.py`, `providers/`, `command.py` |
| mandatory lifecycle façade | `boundary.py` |
| deterministic depth-first driver | `lead.py` |
| role contracts | `contracts/planner.md`, `worker.md`, `validator.md` |
| CLI, status, diagnosis, and stop | `cli.py`, `scripts/stt.py` |
| qualification and document checks | `tests/concepts/stt/` |

Files may be consolidated when one authority and one proof path remain, because filenames are conventions rather than architecture boundaries.

The production `Boundary` façade exposes only the following lifecycle methods, because Lead and CLI must not reach storage, launchers, adapters, or phase-finalization code through alternate paths:

```text
publish_run
publish_root_task
publish_round
commit_eligible_package
call_planner
continue_prelaunch_attempt
start_next_attempt
recover_attempt_outcome
observe_settlement
finalize_operation_phase
execute_step
map_child_result
call_validator
finalize_round
finalize_task
request_stop
derive_status
derive_diagnosis
```

`publish_round` serves both an initial Round and a Validator-authorized successor Round, while `derive_status` and `derive_diagnosis` are read-only, because one method may implement mechanically identical publication without creating duplicate lifecycle paths.

Every method accepts exact immutable references and returns a compact typed receipt, because callers must not reconstruct authoritative state from incidental files or model prose.

---

## 3. Canonical data and identity rules

### 3.1 Canonical control encoding

Every identity-bearing control record uses one canonical JSON codec, because independent readers must derive identical bytes and hashes:

```text
encoding                  UTF-8
object keys               sorted lexicographically
separators                compact and stable
terminal newline          exactly one LF
numbers                   finite JSON integers only for identity-bearing fields
duplicate keys            rejected
NaN and Infinity          rejected
schema identity           required
unknown fields            rejected unless the schema explicitly permits extensions
maximum record bytes      frozen in run_policy
maximum nesting depth     frozen in run_policy
```

Identity hashes bind exact canonical bytes including the final LF, because reparsing and reserializing must not silently change identity.

Arbitrary captured bytes remain binary artifacts rather than canonical JSON, because stdout, stderr, provider returns, and produced files may not be valid text.

### 3.2 Identity derivation

Identity derivation uses domain-separated SHA-256 over canonical inputs, because equal bytes in different lifecycle roles must not collide semantically:

```text
run_id              = lowercase UUIDv4 generated once by `start` before candidate publication
root_task_id        = H("stt-root-task-v1" || run_id || root_task_spec_ref || root_authority_ref || required_outputs_ref)
child_task_id       = H("stt-child-task-v1" || parent_task_id || round_number || step_id || accepted_task_step_ref)
round_id            = H("stt-round-v1" || task_id || uint64_be(round_number))
plan_id             = H("stt-plan-v1" || planner_request_id || canonical_returned_plan_body_bytes)
step_id             = H("stt-step-v1" || plan_id || uint64_be(step_ordinal) || canonical_returned_step_body_bytes)
input_id            = H("stt-input-v1" || step_id || uint64_be(dependency_ordinal) || canonical_dependency_spec_bytes)
requirement_id      = H("stt-requirement-v1" || step_id || uint64_be(requirement_ordinal) || canonical_requirement_spec_bytes)
authority_id        = H("stt-authority-v1" || canonical_task_authority_bytes_excluding_authority_id)
routing_identity    = H("stt-routing-v1" || canonical_routing_file_bytes_excluding_routing_identity)
prefix_id           = H("stt-prefix-v1" || exact_committed_prefix_jsonl_bytes)
operation_request_id= H("stt-operation-v1" || canonical_operation_request_body_bytes)
attempt_id          = H("stt-attempt-v1" || operation_request_id || uint64_be(attempt_ordinal))
artifact_id         = H("stt-artifact-v1" || canonical_artifact_identity_body_bytes)
record_id           = H("stt-record-v1" || record_kind || canonical_record_body_bytes)
observation_id      = H("stt-observation-v1" || canonical_observation_body_bytes)
transition_id       = H("stt-transition-v1" || canonical_transition_manifest_bytes)
```

Every derived-identity preimage excludes the field that will contain the derived identity and uses the named canonical body form, because hashing a record that contains its own identity would create a cycle.

A Run-artifact identity body excludes both `artifact_id` and its derived package storage path but includes content hash, size, media type, provenance, requirement, purpose, and producer identity, while a target-artifact identity body additionally includes the canonical target-relative path and observation identity, because `BOUNDARY_ASSIGNED` storage must not create an artifact-id/path cycle and live-target location is semantically material.

`start` rejects a generated `run_id` whose final Run or exchange path already exists and generates a replacement only before any candidate publication, because identity collision must not overwrite an existing Run or change identity after publication begins.


Round numbers, step ordinals, Attempt ordinals, and ledger sequence numbers are unsigned contiguous integers starting at zero unless explicitly stated otherwise, because gaps create ambiguous reconstruction.

A second Attempt ordinal is legal only after the immediately preceding Attempt has a committed `PROVEN_NOT_LAUNCHED` outcome, because actual or uncertain launch forbids replay.

### 3.3 Reference rule

A fixed Bootstrap or Task-genesis file is referenced by `ContentRef`, a payload referenced from another payload in the same uncommitted transition package uses `PayloadRef`, and a payload referenced after ledger commitment uses `RecordRef`, because including a not-yet-known transition identity inside its own package would create a hash cycle while cross-transition use must bind the committing event.

Every arbitrary-artifact record additionally carries media type, object type, location class, provenance, and observation facts through `ArtifactRef`, because later consumers must distinguish immutable verified bytes from an observation of mutable target state.

---

## 4. Canonical Run filesystem contract

### 4.1 Authoritative layout

Every create-only file or directory publication writes and flushes complete temporary content, flushes the temporary directory when applicable, atomically installs the final same-parent name, flushes the destination parent directory, and rereads the final no-follow object to verify identity, because rename visibility without parent durability or final verification is insufficient for crash-safe authority.

The implementation uses the following authoritative layout exactly, because tools, resume, diagnosis, and independent review need one stable convention without duplicate record authority:

```text
<run-root>/
├── run.json
├── bootstrap/
│   ├── root-task-spec.json
│   ├── routing.json
│   ├── run-policy.json
│   ├── target-identity.json
│   ├── source-identity.json
│   ├── runtime-source-manifest.json
│   ├── initial-inputs/
│   │   └── <selector-id>/
│   │       ├── import.json
│   │       ├── bytes                         # regular-file import only
│   │       └── tree/                         # directory-tree import only
│   │           ├── manifest.json
│   │           └── files/<canonical-relative-path>
│   └── prior-imports/
│       └── <selector-id>/
│           ├── import.json
│           ├── bytes                         # regular-file import only
│           └── tree/                         # directory-tree import only
│               ├── manifest.json
│               └── files/<canonical-relative-path>
├── runtime/
├── runtime-manifest.json
├── locks/
│   ├── runner.lock
│   └── writer.lock
└── tasks/
    └── <task-id>/
        ├── task.json
        ├── mission.md
        ├── authority.json
        ├── required-outputs.json
        ├── ledger.jsonl
        └── transitions/
            └── <seq>-<event-kind>/
                ├── manifest.json
                └── payload/
                    ├── rounds/<round-number>/...
                    ├── prefixes/<prefix-id>.jsonl
                    ├── operations/<operation-request-id>/...
                    ├── attempts/<attempt-id>/...
                    ├── steps/<step-id>/...
                    ├── artifacts/<artifact-id>/...
                    ├── observations/<observation-id>/...
                    ├── results/task-result.json
                    └── control/
                        ├── operator-stop.json
                        └── stop-prefixes/
                            ├── request-start/<prefix-id>.jsonl
                            └── commit-frontier/<prefix-id>.jsonl
```

Bootstrap and Task-genesis files are authoritative at their fixed paths, while every later lifecycle record or artifact exists exactly once beneath the committing transition package’s `payload/`, because one byte location must own every accepted fact.

Payload logical paths follow the templates in the layout and are globally unique within one Task, because a later transition may reference an earlier record but may never recreate or replace its path.

Each event kind uses the following required package-relative payload paths, because an implementation must not invent filenames or place the same accepted fact in multiple locations:

| Event | Required payload paths |
|---|---|
| `ROUND_CREATED` | `rounds/<round-number>/round.json` |
| `PLANNING_STARTED` | `rounds/<round-number>/workspace-index.json` |
| `OPERATION_REQUESTED` | `prefixes/<prefix-id>.jsonl` and `operations/<operation-request-id>/request.json` |
| `ATTEMPT_STARTED` | `attempts/<attempt-id>/attempt.json` |
| `LAUNCH_INTENT_RECORDED` | `attempts/<attempt-id>/launch-intent.json` |
| `ATTEMPT_FINISHED` | `attempts/<attempt-id>/outcome.json` plus the applicable optional capture paths defined below |
| `SETTLEMENT_OBSERVED` | `attempts/<attempt-id>/settlement/<observation-ordinal>.json` |
| `PLANNING_FINISHED` | `rounds/<round-number>/planner-result.json`; accepted `PLAN` also adds `rounds/<round-number>/accepted-plan.json` and `rounds/<round-number>/input-resolutions/<input-id>.json` |
| `STEP_STARTED` | `steps/<step-id>/step-start.json` plus `steps/<step-id>/deferred-input-resolutions/<input-id>.json` when applicable |
| `STEP_FINISHED` | `steps/<step-id>/step-result.json` plus newly committed artifact and observation paths |
| `VALIDATION_STARTED` | `rounds/<round-number>/validation-start.json`, `rounds/<round-number>/output-assessment.json`, applicable `rounds/<round-number>/target-revalidations/pre/<artifact-id>.json`, and any new Boundary-observed artifact or observation paths |
| `VALIDATION_RECORDED` | `rounds/<round-number>/validator-result.json` or `rounds/<round-number>/validator-stop.json`; accepted `SATISFIED` also adds `rounds/<round-number>/output-assessment-post.json` plus applicable `rounds/<round-number>/target-revalidations/post/<artifact-id>.json` |
| `OPERATOR_STOP_REQUESTED` | `control/operator-stop.json`, `control/stop-prefixes/request-start/<prefix-id>.jsonl`, and `control/stop-prefixes/commit-frontier/<prefix-id>.jsonl` in the root Task |
| `ROUND_FINISHED` | `rounds/<round-number>/round-result.json` |
| `TASK_FINISHED` | `results/task-result.json` |

An `ATTEMPT_FINISHED` package may add only `attempts/<attempt-id>/capture/stdout.bin`, `stderr.bin`, `raw-return.bin`, `tool-events.jsonl`, `routing.json`, `process.json`, `timing.json`, `reported-effects.json`, and `claimed-outputs.json`, and `outcome.json` identifies every present, omitted, or truncated capture path, because optional transport evidence still needs one closed filename vocabulary and truthful completeness record.

A committed Run regular-file artifact uses `artifacts/<artifact-id>/bytes`, a committed Run directory-tree artifact uses `artifacts/<artifact-id>/tree/manifest.json` plus `tree/files/<canonical-relative-path>`, and both use `artifacts/<artifact-id>/artifact.json`, while a target observation stores only `artifact.json` and every other structured observation uses `observations/<observation-id>.json`, because immutable files, immutable trees, and mutable-target observations require distinct physical forms.


The canonical reference schemas are as follows, because fixed files, same-package edges, and committed cross-event edges need distinct non-cyclic authority:

```text
ContentRef
  schema
  record_id
  relative_path
  size_bytes
  sha256

PayloadRef
  schema
  record_id
  payload_path
  size_bytes
  sha256

RecordRef
  schema
  record_id
  task_id
  ledger_sequence
  event_kind
  transition_id
  payload_path
  size_bytes
  sha256
```

`record_id` is derived from the canonical body containing record kind, logical fixed or payload path, exact size, and SHA-256 and excludes Task, sequence, event kind, transition identity, and physical package prefix, because the same accepted payload needs one stable identity before and after ledger commitment without conflating equal bytes stored for different purposes.

Every same-package reference and every `event_body` payload entry uses `PayloadRef`; after the ledger event commits, Boundary derives the corresponding `RecordRef` by adding the committing Task, sequence, event kind, and transition identity without changing `record_id`, payload path, size, or SHA-256, because package construction and later consumption need one stable content edge at different lifecycle stages.

The physical path is derived as `tasks/<task-id>/transitions/<seq>-<event-kind>/payload/<payload-path>`, because excluding `transition_id` from the directory name prevents a content-hash cycle while the ledger line still binds the exact manifest hash.

Tasks live in one flat Run-level registry and carry parent references in `task.json`, because unlimited semantic depth must not create unbounded host path depth.

All stored paths inside control records are normalized Run-relative or target-relative POSIX-style paths, because host-specific absolute paths would weaken portability and containment checks.

Active provider, process, and read-tool capture lives only in a disposable exchange outside the authoritative Run root until Boundary classifies and imports it into an `ATTEMPT_FINISHED` package, because partially written current-operation bytes must not appear as committed history.

Incidental temporary names begin with `.tmp-` in the same parent directory and are never authoritative, because only verified final create-only names participate in reconstruction.

Optional navigation indexes may be rebuilt from validated ledgers and manifests but are never consulted for state derivation, because convenience must not become a second lifecycle authority.

The authoritative Run root is `<store-root>/runs/<run-id>/`, while the exchange root is `<store-root>/exchanges/<run-id>/` and each outer operation uses `<attempt-id>/` beneath it, because the caller-selected store root needs one deterministic separation between immutable evidence and active mutable capture.

Each Attempt exchange uses the following nonauthoritative mutable layout, because adapters and `stt stop` still need one predictable working convention outside the append-only Run tree:

```text
<store-root>/exchanges/<run-id>/<attempt-id>/
├── request-ref.json
├── live-operation.json                 # optional create-only local termination handle
├── completion.json                     # optional create-only recoverable outcome
├── inputs/<input-id>/bytes             # read-only regular-file input copy
├── inputs/<input-id>/tree/             # read-only directory-tree input copy
├── outputs/<requirement-id>/bytes      # Worker Run regular-file output
├── outputs/<requirement-id>/tree/      # Worker Run directory-tree output
├── capture/                            # adapter-owned bounded capture
└── adapter/                            # adapter-private disposable work
```

`request-ref.json` contains only the exact authoritative OperationRequest `RecordRef`, and every other exchange byte is lower-trust mutable capture until Boundary imports and verifies it, because exchange convenience must not create duplicate control authority.

`live-operation.json` is atomically published at most once after the local process or channel obtains a verifiable termination identity, because `stt stop` must never consume a partially written or later-retargeted process handle.

`completion.json` is atomically published at most once only after every referenced capture is closed, hashed, locally settled as recorded, and no longer writable; it binds Attempt identity, launch state, call state, result kind, local settlement, capture manifest, routing observations, proof of non-launch when applicable, and adapter identity, because crash recovery needs one self-contained lower-trust claim that Boundary can revalidate before authoritative import.

`RECOVER_ATTEMPT_OUTCOME` is permitted only when `completion.json`, every referenced capture hash, Attempt and launch-intent identity, adapter identity, process or channel settlement, frozen runtime, target, and ledger prefix all revalidate exactly, because an incomplete or merely plausible exchange must not become accepted call history.

After actual or uncertain launch, absent, partial, mutable, conflicting, or unverifiable completion evidence derives `NON_RESUMABLE` rather than another launch or inferred result, because the architecture forbids guessing across a possible-effect crash window.


Boundary removes a settled imported exchange only after the `ATTEMPT_FINISHED` event is durably committed, while uncertain or unimported exchanges remain for diagnosis and operator cleanup, because cleanup must not erase the closest available evidence of an unresolved call.

A launched local adapter writes an ephemeral `live-operation.json` in its exchange containing Attempt identity, runner identity, process-group identifier, process-start identity, and channel kind, because `stt stop` needs a best-effort termination target without treating mutable exchange state as authoritative history.

`stt stop` verifies the recorded process-start identity before signaling and ignores a stale or mismatched process identifier, because PID reuse must not terminate an unrelated process.

### 4.2 Run publication

`--store-root` must name a pre-existing caller-owned no-follow directory with the supported identity and durability profile; Bootstrap may create only missing create-only `runs/` and `exchanges/` child directories beneath it and rejects a conflicting entry, symlink, special file, or insufficient permission, because STT must not invent or recursively create the caller’s evidence authority root.

Bootstrap resolves and freezes that store root, rejects a store root or derived Run or exchange root that violates source/target separation, and create-only publishes one empty `<store-root>/exchanges/<run-id>/` directory with the shared durability rule before constructing `run.json`, because the immutable Run record must bind an exchange-root object identity that already exists rather than a future path guess.

A crash after exchange-root publication but before Run publication leaves a nonauthoritative orphan that is never reused for another Run and may be removed only by operator cleanup, because two sibling directory publications cannot be atomic together and an orphan is safer than a Run record whose active-capture root was never created.

Bootstrap then constructs a complete candidate Run directory beside `<store-root>/runs/<run-id>`, because publication must not expose a partially initialized or unauthorized authority base.

The candidate contains verified Bootstrap inputs, copied initial and prior evidence, frozen runtime, runtime manifest, `run.json`, lock directory, and an empty `tasks/` registry with no Task entry, because root Task publication has its own recoverable identity boundary while its atomic rename requires a stable parent directory.

Bootstrap flushes every candidate file, rereads and verifies every hash, flushes the candidate directory, and atomically renames the candidate to the final Run root, because `run.json` becomes authoritative only with its complete frozen dependencies.

Bootstrap then re-executes from the frozen runtime and publishes the root Task through the Task publication rule, because same-Run execution must use the frozen controller rather than the mutable source tree.

A crash after Run publication but before root Task publication is resumable by publishing the uniquely implied root Task, because no semantic or effectful operation has begun.

### 4.3 Task publication

A Task is published as one same-parent candidate directory containing `task.json`, mission, authority, required outputs, and a genesis ledger with `TASK_CREATED`, because a Task ledger cannot precede the Task identity it records.

The genesis `TASK_CREATED` event uses `transition_id: null`, references every fixed Task-genesis file by `ContentRef`, and computes `event_hash` from the canonical null-transition event preimage, because the first ledger hash must bind the complete atomic Task publication even though no post-genesis transition package exists yet.


Boundary verifies the complete candidate, flushes files and directories, and atomically renames it into `tasks/<task-id>`, because readers must observe either no Task or one complete Task genesis.

An existing equal Task directory is idempotent while any byte difference is `INVALID`, because deterministic resume may recognize prior completion but may not choose between competing Tasks.

Child publication occurs only after the parent Task step is committed as started, because the child identity derives from that accepted parent step.

### 4.4 Writer and runner locks

`writer.lock` serializes every authoritative publication and ledger append but is not held while waiting for a provider or process, because `stt stop`, status, and settlement recording must remain possible during an outer call.

Boundary holds `writer.lock` continuously across the final derived-state and stop-frontier check, `LAUNCH_INTENT_RECORDED` commitment, and the immediate local launch handoff that either creates the command/provider process or adapter worker, proves no such launch occurred, or reports uncertainty, because cancellation must not commit between intent and handoff and then allow new work to start afterward.

Boundary releases `writer.lock` immediately after that bounded handoff and never holds it while the launched operation runs or while remote completion is awaited, because launch ordering needs serialization while operation duration must not block stop or observation.

Lock paths contain no lifecycle data and are excluded from canonical hashes and persisted evidence, because operating-system synchronization state is mutable coordination rather than an accepted fact.


`runner.lock` prevents two `start` or `run` drivers from advancing the same Run concurrently but does not authorize state mutation, because execution ownership and authoritative write serialization are different concerns.

`stt stop` uses `writer.lock` and may coexist with the runner lease, because the operator must be able to record cancellation while one driver is active.

`status` and `diagnose` attempt `writer.lock` nonblockingly, read and validate one committed snapshot only after acquisition, release it immediately, and perform no publication or ledger append, because read-only observation needs stable heads without waiting behind an unbounded writer-held operation.

A failed nonblocking acquisition of either `runner.lock` by `start` or `run` or `writer.lock` by `status` or `diagnose` returns `RUN_BUSY`, because temporary execution or publication ownership is transient rather than a persisted lifecycle state.

---

## 5. Transition packages, ledgers, and event grammar

### 5.1 Transition package construction

Every post-genesis lifecycle transition is prepared as one create-only package before its ledger event is appended, because crashes must leave a verifiable non-effectful completion path.

All records and artifacts created by that transition live only under the package `payload/` directory, because copying accepted bytes into separate lifecycle directories would create duplicate authority.

The package manifest has the following shape, because the manifest must bind both the pending event body and every payload without a hash cycle:

```text
TransitionManifest
  schema
  task_id
  ledger_sequence
  event_body
  payloads[]
    payload_path
    sha256
    size_bytes
```

`event_body` contains `schema`, `event_kind`, `task_id`, `ledger_sequence`, `previous_event_hash`, and package-relative payload references that exclude `transition_id`, because the event and manifest must bind accepted meaning without hashing a path that contains their own hash.

The manifest payload list and `event_body` payload references must be identical after canonical sorting by package-relative `payload_path`, because a package must not contain uncommitted extra bytes or omit an event-bound record.

`transition_id` is SHA-256 of canonical `TransitionManifest`, and the event-hash preimage is the canonical object containing only `schema`, `transition_id`, and `event_body`, because the payload package must be bound without hashing the resulting `event_hash` field itself.

`event_hash` is SHA-256 of that preimage, and the final canonical ledger line contains the same three preimage fields plus `event_hash`, because an independent reader must prove that the committed event and every later `previous_event_hash` bind exactly one complete package without a self-hash cycle.

Boundary builds the complete package in a same-parent temporary directory, flushes and verifies every payload and the manifest, atomically renames the package to `transitions/<seq>-<event-kind>`, appends the exact ledger line with one durable write, flushes and rereads the ledger tail, and then releases `writer.lock`, because package-first publication permits narrow crash completion without a hash-cycle path or a committed event whose payload is absent.

A complete package with the exact next sequence, exact prior head, and no competing package may be committed during resume, because that completion is uniquely implied and non-effectful.

A stale, conflicting, incomplete, or multiply eligible package makes the Run `INVALID`, because deterministic recovery cannot select among histories.

### 5.2 Ledger validation

Each Task ledger is a hash-chained JSONL sequence whose first event is `TASK_CREATED`, because every later state must derive from one immutable Task genesis.

Validation rejects malformed canonical bytes, sequence gaps, wrong prior hashes, wrong Task identities, missing packages, package mismatches, duplicate terminal events, and interior corruption, because any of those defects destroys unique derivation.

Only a final unterminated or partial ledger line may be removed during narrow torn-tail recovery when its bytes are not referenced by any complete package, because incomplete append bytes are not a committed event.

### 5.3 Event vocabulary

The implementation uses the architecture events plus the following mechanical subevents, because request, launch, Attempt, and operator-stop boundaries also require durable reconstruction:

```text
TASK_CREATED
ROUND_CREATED
PLANNING_STARTED
OPERATION_REQUESTED
ATTEMPT_STARTED
LAUNCH_INTENT_RECORDED
ATTEMPT_FINISHED
SETTLEMENT_OBSERVED
PLANNING_FINISHED
STEP_STARTED
STEP_FINISHED
VALIDATION_STARTED
VALIDATION_RECORDED
OPERATOR_STOP_REQUESTED
ROUND_FINISHED
TASK_FINISHED
```

`OPERATION_REQUESTED`, `ATTEMPT_STARTED`, `LAUNCH_INTENT_RECORDED`, `ATTEMPT_FINISHED`, and `SETTLEMENT_OBSERVED` are mechanical evidence events rather than semantic decisions, because they preserve the replay and settlement boundary without expanding architecture outcomes.

### 5.4 Legal Task grammar

The pure ledger validator enforces one Round grammar plus a Run-wide stop overlay, because a syntactically valid event sequence must still represent one legal lifecycle:

```text
TASK_CREATED
{
  ROUND_CREATED
  PLANNING_STARTED
  planner-operation
  PLANNING_FINISHED
  { step-phase }*
  [ VALIDATION_STARTED validator-operation VALIDATION_RECORDED ROUND_FINISHED ]
}*
[TASK_FINISHED]
```

`OPERATOR_STOP_REQUESTED` is an orthogonal one-time root-ledger overlay that may appear after any committed root event and may appear after `TASK_FINISHED` only under the narrow §12 rule, because cancellation orders later work without satisfying, reopening, or replacing any semantic grammar element.

A semantic `planner-operation`, Worker or command `step-phase`, and `validator-operation` each use one `OPERATION_REQUESTED` followed by one or more Attempts, because every outer call needs one frozen request while positive non-launch may permit a later Attempt:

```text
OPERATION_REQUESTED
ATTEMPT_STARTED
[LAUNCH_INTENT_RECORDED ATTEMPT_FINISHED]
{ATTEMPT_STARTED LAUNCH_INTENT_RECORDED ATTEMPT_FINISHED}*
```

An open Attempt may end temporarily after `ATTEMPT_STARTED` and before launch intent, because `PRELAUNCH_BLOCKED` permits the same Attempt to resume without claiming an operation occurred.

An `ATTEMPT_FINISHED` with `PROVEN_NOT_LAUNCHED` leaves the operation phase open, returns `PRELAUNCH_BLOCKED` for that public invocation, and permits only a later invocation to create the next Attempt ordinal, because positive non-launch must not become an automatic retry loop or Validator evidence.

Any other completed Attempt closes transport for that OperationRequest and is followed by one deterministic phase-finalization event, because accepted or failed call evidence must become exactly one Planner, step, or Validator result without another semantic launch.

After `ATTEMPT_FINISHED`, zero or more monotonic `SETTLEMENT_OBSERVED` events may record later local-process or channel settlement, and phase finalization waits until effective local settlement is `SETTLED`, because an accepted role result or settled failure must not advance while relevant local work is still active or unknown.


A Planner `DECLINE` or settled Planner failure commits `PLANNING_FINISHED` and proceeds to Validator when no Run-wide stop or operational block exists, because Validator retains the Task-level mandate without an accepted Plan.

An accepted `PLAN` contains at least one step and executes accepted steps in ordinal order until completion or the first architecture stop condition, because later steps may not build on failed, blocked, or violating work.

A Worker or command step commits `STEP_STARTED`, one operation phase, and `STEP_FINISHED`, while a Task step commits `STEP_STARTED`, publishes and runs the child, and then commits `STEP_FINISHED` from the exact child outcome, because effectful calls and child lifecycles have different transport mechanisms but one parent-step boundary.

An accepted Validator `REPEAT` commits `VALIDATION_RECORDED` and `ROUND_FINISHED`, after which a later deterministic transition creates the next contiguous `ROUND_CREATED`, because continuation is a new Round rather than a retry.

An accepted Validator `FINISH` commits `VALIDATION_RECORDED`, `ROUND_FINISHED`, and `TASK_FINISHED`, because the Validator result closes both the Round and Task.

A settled Validator failure commits `VALIDATION_RECORDED` with no semantic judgment and no later Round or Task terminal event, because the Task is operationally stopped rather than semantically finished.

`OPERATOR_STOP_REQUESTED` is committed at most once in the root Task ledger and is visible to every child through Run derivation, because cancellation is Run-wide rather than a child-local result.

If the Run exists without a root Task, `stt stop` may invoke `CREATE_ROOT_TASK` only when the exact root Task bytes are uniquely derivable from the frozen `RunRecord`, `RootTaskSpec`, root authority, and required outputs; it publishes those already-determined bytes before committing the stop request, while any missing or conflicting derivation is `INVALID`, because one canonical root ledger must own Run-wide cancellation without letting `stop` invent Task semantics.

`OPERATOR_STOP_REQUESTED` binds one streamed request-start manifest containing every validated Task head when `stop` acquired the writer lock and one streamed commit-frontier manifest containing every validated Task head immediately before the stop event; both use the same `PrefixHeader`, sorted `PrefixTaskHead` JSONL format, and `prefix_id` derivation as `RunPrefixManifest`, because deterministic review must prove both that the request began before any closure-produced terminal and which later records are causally ordered before cancellation without inventing a second snapshot format.

After `OPERATOR_STOP_REQUESTED`, no new OperationRequest, Attempt, child Task, or Round may be created, while an operation whose request and current Attempt existed at or below the commit frontier bound by `stop_prefix_ref` and every uniquely implied non-effectful transition caused by such pre-stop facts may still be recorded and finalized, because cancellation stops future work without discarding facts already produced.

A post-stop event in any Task ledger is valid only when it is `ATTEMPT_FINISHED`, `SETTLEMENT_OBSERVED`, phase finalization, child-result mapping, Round finalization, or Task finalization causally rooted in an OperationRequest, Attempt, child, or Validator result present at the commit frontier bound by `stop_prefix_ref`; every other event beyond a captured Task head is `INVALID`, because the writer lock alone serializes publication but does not leave a durable cross-ledger order.

Every committed prefix ending at one of these event boundaries is legal only when pure state derivation names exactly one next action or public outcome, because interruption may leave an in-progress phase but may not create ambiguous authority.

### 5.5 Phase finalization

`ATTEMPT_FINISHED` imports the immutable raw return, routing facts, tool transcript, process and settlement observations, reported effects, claimed outputs, and Boundary observations needed to classify that call, because later phase finalization must not reread mutable exchange bytes or invent evidence after a crash.

`FINALIZE_OPERATION_PHASE` validates the committed Attempt payload and creates exactly one of `PLANNING_FINISHED`, `STEP_FINISHED`, or `VALIDATION_RECORDED`, because a crash after transport completion must resume through deterministic non-effectful work rather than another call.

Effective settlement is the AttemptOutcome settlement followed by the latest valid settlement observation; only `UNSETTLED` or `UNKNOWN` may advance to `SETTLED`, and any reversal, conflicting observation, wrong Attempt, or duplicate ordinal is `INVALID`, because append-only observation may add certainty but may not rewrite a settled fact.


Planner finalization accepts one bound nonempty `PLAN` or `DECLINE`, otherwise preserves rejection or failure evidence with no accepted Planner result, because malformed model bytes cannot become an execution decision.

Worker and command finalization records the accepted local outcome when present, mechanical output-contract status, exact reported effects, and operational evidence in one `StepResult`, because local semantic return and structured completion facts must remain distinguishable.

A step with accepted `SATISFIED` local outcome but unsatisfied required outputs remains locally `SATISFIED` while `output_contract_status` is `UNSATISFIED` and later steps stop, because Boundary may enforce the artifact contract without rewriting the role’s semantic return.

Validator finalization accepts one bound judgment and disposition or records an operational stop with no judgment, because no lower component may fabricate Task completion.

A phase cannot finalize from live target state that was not captured or observed in the committed Attempt payload, because a later observation could silently substitute changed bytes for the operation’s evidence.

### 5.6 Pure state derivation

`state.py` returns one internal `DerivedState` and projects one public `RunView`, because Lead needs an exact `NextAction` while operators must not receive implementation vocabulary as public lifecycle meaning:

```text
DerivedState
  run_id
  root_task_id | null
  active_task_id | null
  active_round_id | null
  active_step_id | null
  operator_stop_ref | null
  blocker_refs[]
  semantic_judgment | null
  public_outcome | null
  transient_outcome | null
  next_action

RunView
  schema
  run_id
  root_task_id | null
  active_task_id | null
  active_round_number | null
  active_step_id | null
  operator_stop_requested
  operator_stop_ref | null
  semantic_judgment | null
  public_outcome | null
  transient_outcome: PRELAUNCH_BLOCKED | RUN_BUSY | null
  blocker_refs[]
```

The public projection omits `next_action` but always projects a committed operator-stop record independently from semantic judgment and nonsemantic outcome, because internal derivation labels must not become public commitments while an operator action must not disappear when already-produced semantic facts finish afterward.

The internal `NextAction` vocabulary is implementation-owned, because architecture requires deterministic next action without prescribing internal labels:

```text
COMMIT_ELIGIBLE_PACKAGE
CREATE_ROOT_TASK
CREATE_ROUND
CALL_PLANNER
CONTINUE_PRELAUNCH_ATTEMPT
START_NEXT_ATTEMPT
RECOVER_ATTEMPT_OUTCOME
OBSERVE_SETTLEMENT
FINALIZE_OPERATION_PHASE
EXECUTE_STEP
MAP_CHILD_RESULT
CALL_VALIDATOR
FINALIZE_ROUND
CREATE_REPEAT_ROUND
FINALIZE_TASK
WAIT_FOR_SETTLEMENT
STOP_OPERATIONALLY
STOP_NON_RESUMABLE
STOP_INVALID
RETURN_JUDGMENT
```

Derivation precedence is fixed as follows, because corruption, already-produced facts, and unsafe uncertainty must dominate future work:

1. invalid Run or Task evidence → `STOP_INVALID`
2. complete uniquely eligible transition package → `COMMIT_ELIGIBLE_PACKAGE`
3. completed Attempt whose latest effective settlement can now be positively observed as settled → `OBSERVE_SETTLEMENT`
4. launched Attempt with a uniquely recoverable sealed adapter outcome → `RECOVER_ATTEMPT_OUTCOME`
5. known active local work that remains unsettled or whose settlement is unknown → `WAIT_FOR_SETTLEMENT`
6. actual or uncertain launch with no active work and no uniquely recoverable outcome → `STOP_NON_RESUMABLE`
7. completed non-`PROVEN_NOT_LAUNCHED` Attempt with effective `SETTLED` and missing phase result → `FINALIZE_OPERATION_PHASE`
8. committed child outcome missing parent mapping → `MAP_CHILD_RESULT`
9. accepted Validator result missing Round finalization → `FINALIZE_ROUND`
10. finished `FINISH` Round missing Task finalization → `FINALIZE_TASK`
11. semantically finished root Task → `RETURN_JUDGMENT`
12. committed operator stop request → `STOP_OPERATIONALLY`
13. open Attempt without launch intent → `CONTINUE_PRELAUNCH_ATTEMPT`
14. latest Attempt is `PROVEN_NOT_LAUNCHED` → `START_NEXT_ATTEMPT`
15. accepted `REPEAT` Round missing its successor → `CREATE_REPEAT_ROUND`
16. unfinished accepted Plan → `EXECUTE_STEP`
17. finished execution, `DECLINE`, or settled Planner failure → `CALL_VALIDATOR`
18. new Round without planning → `CALL_PLANNER`
19. Task without Round → `CREATE_ROUND`
20. Run without root Task → `CREATE_ROOT_TASK`

Before deriving any post-stop action, `state.py` validates every Task ledger against the commit frontier bound by `stop_prefix_ref` and the closed causal whitelist, because a forbidden child-ledger event after cancellation must derive `INVALID` rather than appear as ordinary history.

A stop request suppresses every action below precedence item 12 but not items 1–11, and every resulting `RunView` preserves `operator_stop_requested: true` plus the exact stop reference even when `RETURN_JUDGMENT` wins, because cancellation forbids future semantic work while preserving both valid results already produced and the operator action that stopped later work.

Any Boundary receipt returning `PRELAUNCH_BLOCKED` instructs Lead to end that current public invocation before deriving another action; a later invocation derives `CONTINUE_PRELAUNCH_ATTEMPT` when launch intent is absent or `START_NEXT_ATTEMPT` after committed `PROVEN_NOT_LAUNCHED`, because transient retry timing must not become an automatic loop or make pure state derivation depend on hidden mutable cursor state.


A state derivation conflict returns `INVALID` rather than choosing a branch, because deterministic Lead must never repair ambiguity through preference.

---

## 6. Canonical contracts

### 6.1 Root, Run, Task, and Round

The canonical schema source defines the following required semantic records, because every implementation component must agree on one field vocabulary:

```text
RootTaskSpec
  schema
  mission
  root_authority_spec
  required_outputs[]
  initial_input_selectors[]
  prior_evidence_selectors[]
  run_policy
  routing_identity

RunRecord
  schema
  run_id
  root_task_spec_ref
  routing_ref
  run_policy_ref
  initial_import_refs[]
  prior_import_refs[]
  source_identity_ref
  target_identity_ref
  store_root_identity
  run_root_relative_path
  frozen_runtime_manifest_ref
  exchange_root_identity
  live_provider_authorized
  created_at

TaskRecord
  schema
  task_id
  run_id
  parent_task_id | null
  parent_round_number | null
  parent_step_id | null
  mission_ref
  authority_ref
  required_outputs_ref
  created_from_ref

RoundRecord
  schema
  round_id
  task_id
  round_number
  predecessor_round_id | null
  continuation_validator_result_ref | null

FilesystemRootIdentity
  schema
  host_profile
  canonical_absolute_path
  filesystem_device_id
  object_id
  object_type: DIRECTORY

ImportRecord
  schema
  selector_id
  source_root_identity
  source_relative_path
  object_type: REGULAR_FILE | DIRECTORY_TREE
  imported_object_ref
  origin_run_id | null
  origin_record_ref | null
  purpose
```

`created_at` is canonical RFC 3339 UTC with whole seconds and a `Z` suffix, because diagnostic timestamps need one portable representation even though they do not affect identity.

`store_root_identity` contains the no-follow canonical absolute path plus the observed root object identity supported by the host profile, `run_root_relative_path` is exactly `runs/<run-id>`, and `exchange_root_identity` binds the corresponding `exchanges/<run-id>` parent under the same store root, because resume must not redirect authoritative or active capture paths by changing path text alone.

The MVP `POSIX_LOCAL_V1` host profile uses no-follow canonical path, `st_dev`, `st_ino`, and directory type for `FilesystemRootIdentity`, rejects filesystems whose probe does not preserve stable directory identity and required durability primitives, and compares identities before every protected use, because path text alone cannot detect root replacement while mutable directory contents must not change the root identity.

An `ImportRecord` binds the selector, observed source root and relative path, exact imported file or tree `ArtifactRef`, origin Run metadata when applicable, and purpose, because copied evidence needs one accountable bridge from mutable or prior source to current immutable bytes.



The remaining frozen root records use the following schemas, because selectors, safeguards, and routing must not be inferred from prose:

```text
InitialInputSelector
  selector_id
  source_path
  expected_type
  expected_sha256 | null
  purpose

PriorEvidenceSelector
  selector_id
  prior_run_identity
  committed_reference
  expected_type
  expected_sha256 | null
  purpose

RunPolicy
  schema
  max_control_record_bytes
  max_control_nesting_depth
  max_path_bytes
  max_capture_bytes_per_stream
  max_raw_return_bytes
  max_input_bytes_per_operation
  max_output_bytes_per_operation
  max_tree_entries_per_object
  max_tool_request_bytes
  max_tool_response_bytes
  max_workspace_index_entries
  max_workspace_index_bytes
  planner_wait_seconds
  worker_wait_seconds
  command_wait_seconds
  validator_wait_seconds
  termination_grace_seconds
  host_profile

RoutingFile
  schema
  routing_identity
  planner_route: ProviderRoute
  validator_route: ProviderRoute
  worker_routes{}: ProviderRoute
  command_profiles{}
```

All byte, depth, path, capture, input, output, tree-entry, tool, index, wait, and termination fields are positive finite integers with explicit units in their field names or schema definition, because ambiguous units create incompatible implementations.

`RunPolicy` contains no cumulative semantic-call, Task, depth, Round, or Plan-step limit, because production continuation remains under Planner and Validator judgment.

`expected_type` is exactly `REGULAR_FILE` or `DIRECTORY_TREE`, because Bootstrap needs one closed import representation rather than guessing from the source path.

A `REGULAR_FILE` import stores exact bytes at `bytes` and forbids `tree/`, while a `DIRECTORY_TREE` import stores a canonical no-follow manifest plus copied regular files beneath `tree/files/` and forbids `bytes`, because each selected source must have one unambiguous immutable form.

The canonical tree manifest lists every descendant in sorted canonical relative-path order with type, mode, size, and SHA-256 and rejects symlinks, special files, traversal, duplicate normalized paths, and source changes during copy, because directory imports must bind complete exact content rather than a mutable path snapshot.


### 6.2 Authority, routes, and command profiles

`RootAuthoritySpec` and `TaskAuthority` implement the architecture fields exactly, because semantic roles may not create operational capability:

```text
PathScope
  root
  kind: EXACT | SUBTREE

RootAuthoritySpec
  schema
  read_scopes[]: PathScope
  write_responsibility_scopes[]: PathScope
  allowed_step_kinds[]
  allowed_worker_routes[]
  allowed_command_profiles[]
  allowed_inherited_env_names[]
  allowed_external_effect_classes[]

TaskAuthority
  schema
  authority_id
  target_identity_ref
  read_scopes[]: PathScope
  write_responsibility_scopes[]: PathScope
  allowed_step_kinds[]
  allowed_worker_routes[]
  allowed_command_profiles[]
  allowed_inherited_env_names[]
  allowed_external_effect_classes[]
  parent_authority_ref | null
```

Planner, Validator, and Worker model calls use one `ProviderRoute` contract, because Boundary must not implement three subtly different provider-routing vocabularies:

```text
ProviderRoute
  schema
  route_name
  adapter_kind: FAKE | CLAUDE_CODE | CODEX
  executable_resolution
  fixed_argv_prefix[]
  requested_provider
  requested_model
  requested_effort
  admitted_effect_classes[]
  admitted_inherited_env_names[]
  fixed_env{}
  cwd_policy
  wait_policy
  capture_policy
  local_termination_policy
  read_tool_transport
```

`FAKE` is deterministic and never requires live authorization, while `CLAUDE_CODE` and `CODEX` are live adapters and reject at Bootstrap unless `--allow-live-provider` was supplied and frozen as `live_provider_authorized: true`, because an accidental provider call must fail before Run publication rather than consume external capability silently.

A command profile has the following frozen contract, because a named profile must determine the entire command except admitted typed values:

```text
CommandProfile
  schema
  profile_name
  executable_resolution
  argv_template[]
  argument_slots{}
    type: STRING | INTEGER | BOOLEAN_FLAG | ENUM | TARGET_PATH | INPUT_PATH
    required
    minimum | null
    maximum | null
    pattern | null
    choices[] | null
  cwd_policy
  fixed_env{}
  admitted_inherited_env_names[]
  admitted_effect_classes[]
  exit_code_outcomes{}
  wait_policy
  capture_policy
  local_termination_policy
  output_observations{}
    kind: STDOUT | STDERR | TARGET_PATH_TEMPLATE
    target_path_template | null
  effect_report_target_path | null
```

Executable resolution freezes either exact absolute executable bytes or a maintained resolver plus observed executable identity, because name-only PATH resolution could change authority between Bootstrap and launch.

Each `argv_template` element is exactly one literal token or one whole-slot token and forbids string concatenation, option splitting, shell syntax, and slot reuse unless the profile states it explicitly, because typed arguments must expand to a deterministic argv rather than a second command language.

`TARGET_PATH` slots undergo the ordinary no-follow target-path admission before rendering, `INPUT_PATH` slots name one step-local `dependency_key` and render only its Boundary-created exchange input path, `INTEGER` values use canonical base-10 text, `BOOLEAN_FLAG` emits either one frozen literal flag or no token, and `ENUM` must match one frozen choice, because each slot type needs one closed encoding without permitting arbitrary host paths.

`cwd_policy` is exactly `TARGET_ROOT` or a frozen target-relative directory template using admitted `TARGET_PATH` slots, because working-directory selection must not become ambient filesystem authority.

Each named `output_observations` entry freezes `STDOUT`, `STDERR`, or one target-path template, and CommandStep `output_source_bindings` maps each step-local `requirement_key` to exactly one such name, while `effect_report_target_path` optionally names one exact target-relative JSON report path, because Bootstrap cannot know future requirement identities but Boundary must still derive one unambiguous command evidence source.


Environment construction starts empty, adds fixed values, and then adds only explicitly admitted inherited names, because ambient environment is otherwise an undeclared capability and secret channel.

`exit_code_outcomes` maps each accepted integer exit code to `SATISFIED`, `NOT_SATISFIED`, or `INDETERMINATE`, while an unmapped exit code is a settled command `ERR`, because command-step meaning must be frozen by the profile rather than guessed from conventional exit-code folklore.

Fixed environment values may contain only reviewed non-secret literals, while inherited secret-capable values are supplied by admitted environment name and never persisted by value, because STT should not intentionally copy credentials into its history.

Operational path admission normalizes one target-relative path, rejects absolute syntax, empty interior components, `.` or `..`, `.git` at any component, NUL, overlong bytes, symlinks, and non-regular/non-directory special files, then performs a no-follow component walk beneath the frozen target root, because lexical normalization alone cannot prevent replacement or escape.

An `EXACT` scope admits only its normalized root path, while a `SUBTREE` scope admits that root and descendants separated by whole path components; a child scope is equal or narrower only when every admitted child path is a subset of one parent scope of the same authority class, because prefix text without component and kind rules can expand authority accidentally.

Read and write-responsibility scopes are evaluated independently, and write responsibility does not imply read authority unless a matching read scope exists, because capability to change a path and permission to inspect it are distinct grants.

Plan admission requires every step kind, declared path scope, selected Worker route or command profile, inherited environment name, and admitted external effect class to be a subset of the current `TaskAuthority`, and requires the selected route or profile’s own declared effects and environment names to remain within that same authority, because checking only the Plan or only the profile would leave a capability-composition escape.

Planner and Validator ProviderRoutes run from their disposable exchange, receive no target mutation tool, and reject `TARGET_WRITE` or `REMOTE_MUTATION` in their route effect declarations, because semantic freedom and provider transport do not grant direct effectful mission authority.

A Worker route name must appear in `allowed_worker_routes`, a command profile name must appear in `allowed_command_profiles`, and a child TaskAuthority must pass the equal-or-narrower subset test before child publication, because frozen names and declarative grants must meet at one mechanical admission point.



### 6.3 Plans and steps

Planner returns exactly one `DECLINE` or one nonempty `Plan`, because execution requires one immutable accepted decision and no-step planning is represented by `DECLINE`:

```text
ReturnedPlan
  schema
  planner_operation_request_id
  task_id
  round_id
  steps[1..]

CommonStep
  schema
  step_key
  kind: worker | command | task
  description
  declared_read_scopes[]
  declared_write_responsibility_scopes[]
  dependency_specs[]
  output_requirement_specs[]

WorkerStep extends CommonStep
  worker_route
  instruction
  stt_read_grant

CommandStep extends CommonStep
  command_profile
  arguments{}
  output_source_bindings{}

TaskStep extends CommonStep
  child_mission
  child_authority
  stt_starting_subtree | null
```

`step_key` is a Planner-local unique label used only inside the returned Plan, `dependency_key` and `requirement_key` are unique within their owning step, and references to prior outputs use producer step and requirement keys and may point only backward, because Planner needs readable dependency notation without choosing lifecycle identities or creating cycles.

A Task step’s common `output_requirement_specs` become the child Task’s required-output contract after Boundary derives their canonical requirement identities, because a second `required_child_outputs` field would create duplicate authority.

Plan acceptance rejects an empty `PLAN`, derives `plan_id`, contiguous step ordinals, `step_id`, `input_id`, and step-owned `requirement_id` values, resolves every local key to an exact identity, and publishes one canonical accepted Plan record with exact step and contract references, because Planner should choose semantic structure while Boundary owns lifecycle and binding identities.

Root `required_outputs` retain the caller-supplied frozen unique identifiers, while Planner-created step requirements use Boundary-derived identifiers, because Bootstrap inputs already cross the caller trust boundary before any Plan exists.

Plan acceptance rejects only schema, binding, dependency, ordering, and operational-admission defects, because semantic quality and similarity remain Planner and Validator concerns.

### 6.4 Read grants

`stt_read_grant` has the following closed form, because effectful entities must not receive ambient history access by accident:

```text
kind: NONE | FULL | SUBTREE
roots: []
```

Planner and Validator receive `FULL` automatically, because complete current-Run context is part of their architecture mandate.

A child Planner and child Validator receive `FULL` for the same Run automatically, while `stt_starting_subtree` is only a navigation hint and never a visibility restriction, because child Tasks are semantic roles inside the current lifecycle.

A Worker defaults to `NONE` and receives only the accepted WorkerStep grant, while a command receives no read-tool capability, because broad persisted history may contain sensitive returned bytes and commands consume only exact admitted inputs.

`NONE` and `FULL` require an empty `roots` list, while `SUBTREE` requires one or more unique sorted canonical STT-relative directory prefixes and cannot include glob, traversal, symlink, or host-absolute syntax, because each grant kind needs one non-overlapping representation and the tool surface must remain read-only and Run-contained.

### 6.5 Inputs and exact resolution

Contextual STT reads need no `InputRef`, while authoritative effectful consumption uses the following closed input kinds, because visibility and substitution-sensitive use have different integrity requirements:

```text
INITIAL_IMPORT
PRIOR_IMPORT
RUN_ARTIFACT
TARGET_PATH
PREVIOUS_STEP_OUTPUT
CHILD_TASK_OUTPUT
```

Each returned `DependencySpec` contains kind, source selector or prior `step_key`, purpose, and required media type, and Boundary converts it into an `InputRef` with exact producer or source identity and intended consumer step, because Planner-local notation must become substitution-safe canonical binding before execution.

`INITIAL_IMPORT`, `PRIOR_IMPORT`, `RUN_ARTIFACT`, and `TARGET_PATH` require `source_selector` and forbid producer keys, while `PREVIOUS_STEP_OUTPUT` and `CHILD_TASK_OUTPUT` require one earlier `producer_step_key` plus its `producer_requirement_key` and forbid `source_selector`, because each input kind must have one non-overlapping source form.

An import selector requires its exact `selector_id` and permits `imported_relative_path` only for a directory-tree import; a Run-artifact selector requires one exact `ArtifactRef`; and a target selector requires one canonical target-relative path, while every field belonging to another selector kind is null, because tagged source forms must not admit contradictory combinations.


A `CHILD_TASK_OUTPUT` source key must name an earlier TaskStep and a `PREVIOUS_STEP_OUTPUT` source key must name an earlier Worker or command step, because dependency kind must agree with the producer lifecycle.


```text
DependencySpec
  dependency_key
  kind
  source_selector | null
  producer_step_key | null
  producer_requirement_key | null
  purpose
  required_media_type

SourceSelector
  kind: INITIAL_IMPORT | PRIOR_IMPORT | RUN_ARTIFACT | TARGET_PATH
  selector_id | null
  imported_relative_path | null
  artifact_ref | null
  target_relative_path | null

InputRef
  schema
  input_id
  kind
  source_identity
  source_selector | null
  intended_consumer_step_id
  purpose
  required_media_type

InputResolution
  schema
  input_id
  consumer_step_id
  resolved_artifact_ref
  resolution_phase: PLAN_ACCEPTANCE | PRODUCER_COMPLETION
  target_identity_ref | null
  observed_path_identity | null

InputBinding
  input_id
  object_type: REGULAR_FILE | DIRECTORY_TREE
  execution_path
  size_bytes
  sha256
```

At Plan acceptance Boundary resolves and publishes exact `InputResolution` records for initial imports, prior imports, existing Run artifacts, and current target paths, because accepted Plan meaning must not silently bind to bytes observed only later.

A target-path resolution records canonical path, target-root identity, object identity, type, mode, size, and content hash, because the same path may change between planning and launch.

A regular-file input hashes exact bytes, while a directory input hashes a canonical sorted no-follow tree manifest containing every admitted descendant path, type, mode, size, and file hash, because directory identity cannot be represented by path text alone.

`PREVIOUS_STEP_OUTPUT` and `CHILD_TASK_OUTPUT` remain deferred until the producer finishes, because their exact bytes do not exist at Plan acceptance.

Immediately before launch Boundary revalidates every pre-resolved target input and resolves every deferred producer input, because changed or absent required bytes must stop the step rather than silently rebind it.

Boundary copies every final resolved regular file or directory tree into `inputs/<input-id>/` in the disposable exchange, verifies its canonical hash against the `InputResolution`, enforces the frozen aggregate input-byte and per-tree-entry bounds for that operation, marks the adapter-visible binding read-only where the host supports it, and records unavailable isolation as `UNKNOWN`, because Worker and command execution need stable exact bytes without direct authority to mutate, silently reread authoritative Run evidence, or exhaust the caller-selected store through one operation.

A Worker adapter receives every `InputBinding` as an explicit read-only attachment or file binding, while a command may reference one only through a frozen `INPUT_PATH` slot whose argument value is the matching `dependency_key`, because exact inputs must reach each execution mechanism through a closed path rather than provider or command convention.

A target revalidation mismatch stops later steps and proceeds to Validator as exact operational evidence, because the accepted Plan dependency no longer exists as bound.

### 6.6 Outputs and artifacts

The implementation uses separate Planner-returned requirement specs and Boundary-owned canonical output and artifact records, because output existence alone does not prove requirement satisfaction and Planner must not choose derived identities:

```text
OutputRequirementSpec
  requirement_key
  purpose
  object_type: REGULAR_FILE | DIRECTORY_TREE
  media_type
  location: RUN | TARGET
  path_policy: EXACT | BOUNDARY_ASSIGNED
  path | null
  required_mode | null
  satisfaction_mode
  expected_sha256 | null
  producer_policy: BOUNDARY | ANY_ACCEPTED_STEP | null

OutputRequirement
  schema
  requirement_id
  purpose
  object_type: REGULAR_FILE | DIRECTORY_TREE
  media_type
  location: RUN | TARGET
  path_policy: EXACT | BOUNDARY_ASSIGNED
  path | null
  required_mode | null
  satisfaction_mode
  expected_sha256 | null
  producer_constraint

ArtifactRef
  schema
  artifact_id
  object_type: REGULAR_FILE | DIRECTORY_TREE
  media_type
  location
  relative_path
  sha256 | null
  size_bytes | null
  mode | null
  provenance
  requirement_id | null
  purpose
  observation_kind
  observed_identity

TargetArtifactRevalidation
  schema
  artifact_id
  phase: PRE_VALIDATOR | POST_VALIDATOR
  status: MATCH | MISMATCH | UNREADABLE
  prior_observed_identity
  current_observed_identity | null
  current_sha256 | null
  current_size_bytes | null
  current_mode | null
  reason_code | null

OutputAssessmentCandidate
  artifact_ref
  basis: ACCEPTED_RUN_ARTIFACT | REVALIDATED_TARGET_ARTIFACT | BOUNDARY_TARGET_OBSERVATION

OutputAssessmentEntry
  requirement_id
  status: SATISFIED | UNSATISFIED | UNREADABLE
  selected_candidate: OutputAssessmentCandidate | null
  reason_code

TaskOutputAssessment
  schema
  task_id
  round_id
  entries[]
  all_satisfied
```

The MVP satisfaction modes are `PRESENT`, `NONEMPTY`, and `EXACT_SHA256`, because mechanical output checks should remain small, deterministic, and independent from Validator content judgment.

For a regular file, `NONEMPTY` means positive byte size and `EXACT_SHA256` hashes exact file bytes; for a directory tree, `NONEMPTY` means at least one admitted descendant and `EXACT_SHA256` hashes the canonical sorted tree manifest, because each object type needs one deterministic interpretation of the same satisfaction vocabulary.

Every directory-tree artifact uses the same no-follow sorted manifest and copied-file convention as a directory import and rejects symlinks, special files, duplicate normalized paths, and source mutation during observation or import, because output verification must not be weaker than input identity.


`EXACT_SHA256` requires an `expected_sha256` in the requirement, while `PRESENT` and `NONEMPTY` forbid that field, because each mode must have one unambiguous validation rule.

Boundary derives `EXACT_STEP` for every Worker or command requirement and therefore requires `producer_policy: null`, while a TaskStep requires `BOUNDARY` or `ANY_ACCEPTED_STEP` and carries that policy into the child Task’s root output contract, because the child’s internal producer is not known when the parent Plan is accepted.

Frozen root requirements permit only `BOUNDARY` or `ANY_ACCEPTED_STEP`, because future exact step or child identities do not exist at Bootstrap and cannot be frozen honestly.

A parent TaskStep is satisfied only from the exact child `TaskResult` and its mechanically satisfied output references, because `ChildOutcomeRef` rather than an invented artifact producer identity binds the child lifecycle to the parent step.

```text
ProducerConstraint
  kind: BOUNDARY | ANY_ACCEPTED_STEP | EXACT_STEP
  producer_id | null

OutputBinding
  requirement_id
  execution_location: EXCHANGE | TARGET | CAPTURE_SOURCE
  execution_path_or_source
```

`producer_id` is required only for `EXACT_STEP` and forbidden for the other kinds, because a nullable identity must not create two interpretations of the producer constraint.

`BOUNDARY_ASSIGNED` is permitted only for `RUN` location and resolves to `artifacts/<artifact-id>/bytes` for a regular file or `artifacts/<artifact-id>/tree/` for a directory tree, while every `TARGET` requirement uses one `EXACT` target-relative path, because effectful work must know its live destination before launch and immutable Run artifacts can use content-derived storage.

For a Worker, each Run `BOUNDARY_ASSIGNED` requirement receives `outputs/<requirement-id>/bytes` for a regular file or `outputs/<requirement-id>/tree/` for a directory tree, each target requirement receives its exact admitted target-relative path, and no other writable output location is exposed, because lower-trust work needs a concrete destination without choosing authoritative Run storage.

For a command, each requirement is bound through CommandStep `output_source_bindings` to one compatible frozen profile observation and uses `CAPTURE_SOURCE`, while an exact target requirement may instead bind directly to its declared target path when the profile observation is `TARGET_PATH_TEMPLATE`, because process output must be mechanically observed rather than inferred from stdout prose.

`STDOUT` and `STDERR` are compatible only with regular-file Run requirements, while `TARGET_PATH_TEMPLATE` may observe either admitted object type and must match the requirement’s exact target path after rendering, because stream captures cannot represent a directory tree and profile mappings must not redirect output observation.


Boundary enforces the frozen aggregate output-byte and per-tree-entry bounds while observing target or exchange outputs and imports a settled verified exchange output to the content-derived authoritative artifact path only during `STEP_FINISHED`, because active or unbounded mutable bytes must not become accepted Run evidence before output verification.


The provenance kind is one of `INITIAL_IMPORT`, `PRIOR_IMPORT`, `TARGET_OBSERVATION`, `WORKER_OUTPUT`, `COMMAND_OUTPUT`, `CHILD_TASK_OUTPUT`, or `BOUNDARY_OBSERVATION`, because independent reviewers need one closed origin vocabulary.

Run artifacts are Boundary-owned, create-only, immutable bytes, because accepted evidence must not change after commitment.

Target artifacts are observations that Boundary reverifies before authoritative use, because the live target may change after output verification.

Revalidation requires the same target root, canonical path, object identity, object type, mode, size, and content or tree-manifest hash as the accepted `ArtifactRef`; a merely present replacement does not match even when the requirement mode is `PRESENT`, because producer-bound output evidence must remain the same observed object rather than any later occupant of the path.

Boundary alone decides whether an `ArtifactRef` mechanically satisfies an `OutputRequirement`, because Validator may judge mission meaning but may not waive the structured artifact contract.

Task-level assessment does not require an artifact’s originating `requirement_id` to equal the Task requirement ID; Boundary re-evaluates exact bytes, purpose, type, media type, location, path, mode, satisfaction mode, and producer constraint against the Task requirement, because a step requirement and the Task contract are different bindings even when one produced artifact fulfills both.

When multiple artifacts satisfy one Task requirement, Boundary selects an immutable Run artifact before any target artifact and then the lowest `artifact_id` within that location class, because one bounded deterministic candidate prevents control-record growth and avoids letting directory order choose terminal evidence.

### 6.7 OperationRequest, Attempt, and call outcome

Every semantic or effectful outer operation uses the following records, because replay, return, and local settlement require separate identities:

```text
OperationRequest
  schema
  operation_request_id
  role: PLANNER | WORKER | COMMAND | VALIDATOR
  run_id
  task_id
  round_id
  step_id | null
  exact_contract_ref
  exact_inputs[]
  input_bindings[]
  output_requirements[]
  output_bindings[]
  route_or_profile_ref
  stt_read_grant
  committed_prefix_ref

Attempt
  schema
  attempt_id
  operation_request_id
  attempt_ordinal
  adapter_kind
  requested_routing
  prelaunch_identity_snapshot

AttemptOutcome
  schema
  launch_state: PROVEN_NOT_LAUNCHED | LAUNCHED | LAUNCH_UNKNOWN
  call_state: RETURNED | NO_RETURN
  result_kind: OK | ERR | REJECTED | NONE
  local_settlement: SETTLED | UNSETTLED | UNKNOWN
  requested_routing
  observed_routing
  capture_refs[]
  proof_of_non_launch | null
  error_ref | null
  process_observations[]
  timing_observations[]

OperationError
  schema
  code
  stage
  message
  adapter_details{}

SettlementObservation
  schema
  attempt_id
  observation_ordinal
  prior_effective_settlement: UNSETTLED | UNKNOWN
  observed_settlement: SETTLED
  process_or_channel_identity
  observation_method
```

`OperationError.message` is diagnostic data rather than a control signal, while `code` and `stage` come from closed implementation enums, because arbitrary error prose must not drive retry or lifecycle decisions.

`PROVEN_NOT_LAUNCHED` requires `RETURNED + ERR + SETTLED` and a valid proof record, while `LAUNCHED` or `LAUNCH_UNKNOWN` permits only the architecture’s four valid call/result combinations with any truthfully observed settlement, because the non-launch exception must not use contradictory transport evidence.


`RunPrefixManifest` is the canonical content-addressed JSONL structure stored at `prefixes/<prefix-id>.jsonl`, while `committed_prefix_ref` is its same-package `PayloadRef`, because the request and each parsed control record must remain bounded without placing a not-yet-known transition identity inside the OperationRequest that the transition itself hashes:

```text
line 0: PrefixHeader
  schema
  run_record_ref

line 1..n: PrefixTaskHead
  schema
  task_id
  ledger_sequence
  event_hash
  ledger_size_bytes
```

Boundary writes one bounded canonical JSON object per line in sorted Task-id order while streaming validated ledgers immediately before `OPERATION_REQUESTED`, and the exact file size and SHA-256 live in `committed_prefix_ref`, because snapshot binding must scale with real history without one oversized JSON record or an architecture-defined Task cap.

Boundary completes and hashes the prefix file first, derives `prefix_id`, constructs its `PayloadRef`, and only then derives `operation_request_id`, because that ordering removes both the prefix-path and transition-reference cycles while the committing event still publishes both atomically.


The read-tool adapter exposes only Tasks listed in the manifest, ledger bytes through each recorded `ledger_size_bytes`, and payloads committed by events at or below each recorded sequence, because later Attempt, stop, or settlement records may exist physically while the role is still running but are not part of its stable prefix.

A manifest construction I/O or storage failure returns `PRELAUNCH_BLOCKED` before `OPERATION_REQUESTED` rather than truncating the prefix, because “complete committed history” must not silently become a partial visibility boundary.

Observed routing uses `UNKNOWN` for facts the adapter cannot verify, because requested model, effort, isolation, and provider are not proof of supplied execution.

When an adapter positively observes a provider, model, effort, or route identity that contradicts the frozen request, Boundary preserves the raw return as `REJECTED`, records the mismatch, and applies the ordinary settled-role-failure path without launching a fallback, because truthful observation must not authorize execution under a different route.


A Planner or Validator `OperationRequest` contains `FULL`, a Worker request contains the accepted WorkerStep grant, and a command request contains `NONE`, because the serialized request must exactly reflect each role’s read authority rather than relying on adapter convention.

A Worker or command OperationRequest contains exactly one `InputBinding` for every final resolved dependency and exactly one `OutputBinding` for every declared output requirement with no extras, while Planner and Validator requests contain neither, because execution inputs, output destinations, and observation authority must be total, role-appropriate, and closed before launch.



### 6.8 Proven non-launch

`PROVEN_NOT_LAUNCHED` is accepted only through a closed adapter-specific proof code, because a generic error or absent return cannot disprove launch:

```text
LOCAL_PROCESS_CREATE_FAILED_NO_PROCESS
PROVIDER_CONNECT_FAILED_ZERO_BYTES_SENT
```

Each proof record includes adapter kind, proof code, stage, observed OS or transport result, and an assertion that no process identifier, provider request identifier, or sent-byte count was created, because the exception must be auditable rather than inferred from failure wording.

Command admission, executable resolution, argument rendering, environment construction, provider-request construction, and other failure-prone preparation complete before launch intent is committed, because failures wholly before the marker should resume the same prelaunch Attempt rather than consume the non-launch exception.

Timeout, lost response, connection reset after send began, unknown sent-byte count, process identifier allocation, partial process creation, provider request identifier creation, or adapter crash cannot prove non-launch, because each permits hidden effects.

### 6.9 Role and Boundary results

Planner, Worker, command, and Validator returns are accepted only when bound to the exact OperationRequest and schema, because plausible bytes from another invocation are not authoritative.

The closed accepted result forms are as follows, because each role or Boundary-owned command interpretation contributes different semantic content:

```text
EffectRecord
  effect_class
  operation: READ | CREATE | MODIFY | DELETE | MOVE | EXECUTE | CONNECT | SEND | REMOTE_CHANGE | OTHER_REPORTED
  location: TARGET | STT | LOCAL | NETWORK | REMOTE
  target_relative_path | null
  external_resource_id | null
  observed_result

ScopeViolation
  effect_record_ref
  violated_authority_field
  admitted_scope_refs[]
  reason_code

PlannerResult
  kind: PLAN | DECLINE
  plan | null
  reason
  findings[]
  unknowns[]

WorkerResult
  local_outcome: SATISFIED | NOT_SATISFIED | INDETERMINATE
  reason
  observations[]
  claimed_outputs[]
  reported_effects[]

CommandResult
  local_outcome: SATISFIED | NOT_SATISFIED | INDETERMINATE
  reason
  process_observations[]
  claimed_outputs[]
  reported_effects[]

ValidatorResult
  judgment: SATISFIED | NOT_SATISFIED | INDETERMINATE
  disposition: FINISH | REPEAT
  reason
  findings[]
  unknowns[]
  cited_artifact_refs[]

OperationalStopRef
  task_id
  round_id | null
  public_outcome: OPERATIONALLY_BLOCKED | OPERATIONALLY_STOPPED | NON_RESUMABLE | INVALID
  committing_event_ref
  attempt_outcome_ref | null

ChildOutcomeRef
  kind: TASK_RESULT | OPERATIONAL_STOP
  reference

StepResult
  step_id
  source_result_ref | null
  child_outcome_ref | null
  verified_artifacts[]
  observations[]
  local_outcome: SATISFIED | NOT_SATISFIED | INDETERMINATE | OPERATIONAL_INDETERMINATE
  output_contract_status: SATISFIED | UNSATISFIED | NOT_APPLICABLE
  unsatisfied_requirement_ids[]
  reported_scope_violation | null

RoundResult
  round_id
  planner_result_ref | null
  completed_step_results[]
  validator_result_ref

TaskResult
  task_id
  judgment
  final_validator_result_ref
  satisfied_outputs[]
    requirement_id
    artifact_ref
```

`SATISFIED + REPEAT` rejects, while every other judgment and disposition pair is structurally legal, because the architecture reserves continuation judgment to Validator.

A Validator `SATISFIED` result rejects unless the current `TaskOutputAssessment` has exactly one entry per required output and every entry contains one valid selected candidate, because semantic judgment cannot erase or reinterpret the structured output contract while citations remain explanatory rather than output-selection authority.

A Worker, command, or child step uses `NOT_APPLICABLE` only when its accepted step declares no output requirements, while every declared requirement appears exactly once in the satisfied or unsatisfied calculation, because omission must not masquerade as successful output verification.


A target effect requires a canonical target-relative path, an STT effect identifies the Run-relative authoritative path, and local, network, or remote effects require the matching closed effect class plus a bounded diagnostic resource identifier when observable, while fields belonging to another location are null, because one effect record must not admit contradictory locations.

Boundary derives `ScopeViolation` by comparing each reported effect class and target path with the accepted step, Task authority, route or profile, and write-responsibility scopes; role-provided violation labels are ignored, because lower-trust work may report facts but may not decide whether its own authority was exceeded.

`CommandResult` is generated by Boundary from the frozen exit-code mapping, captured streams, declared output observations, and an optional valid structured effect report rather than parsed from arbitrary stdout, because a raw process has no trusted semantic-return channel unless its profile defines one.

A missing or invalid optional command effect report records `UNKNOWN` reported effects without changing the exit-derived local outcome, because lack of cooperative reporting cannot be laundered into proof that no effects occurred.

A settled invalid or rejected role return is preserved as evidence but produces no accepted role result, because diagnosis must not promote malformed bytes into semantic state.

`RoundResult` exists only after an accepted Validator result, while `TaskResult` exists only after accepted `FINISH`, because operational stop and semantic terminal judgment must not share one ambiguous result file.

A child stopped without judgment is mapped through an exact `OperationalStopRef` rather than a fabricated `TaskResult`, because parent validation must preserve the absence of child semantic judgment.

### 6.10 Instruction and data envelope

Every semantic OperationRequest is constructed in the following precedence order, because lower-trust persisted or target content must not acquire control authority:

```text
1. frozen runtime role contract
2. immutable mission, authority, policy, routing, output schema, and accepted step
3. structured references to persisted history and target context
4. read-tool and target-tool results labelled as untrusted data
```

Provider adapters must preserve separate system/developer and user/tool channels when the provider supports them, while a route that cannot preserve an equivalent precedence envelope is unsupported, because flattening untrusted data into controlling instructions would violate the architecture trust order.

Role contracts state that embedded instructions inside history, target files, prior imports, reports, artifacts, and tool output are data only, because complete context access must not become prompt-injection authority.

---

## 7. Bootstrap, host floor, and target observation

Bootstrap validates the complete `RootTaskSpec`, authority, routes, command profiles, run policy, source, target, and selectors before Run publication, because deterministic startup must fail before semantic execution when the root contract is incomplete.

When `--prior-run` is present, Bootstrap validates that every selected reference is committed by the named prior Run, copies only the selected immutable bytes and origin metadata beneath `bootstrap/prior-imports/`, and never copies prior Task directories, ledgers, Round state, mutable cursors, or active exchanges into the current `tasks/` registry, because prior evidence is advisory data rather than current lifecycle state.


Source and target may resolve to the same root, while otherwise neither may contain the other and the Run and exchange roots must be disjoint from both, because partial overlap would make frozen-runtime and live-target mutation boundaries ambiguous.

The active root schema contains finite per-operation byte, wait, and termination safeguards but no semantic count limits, because bounded transport protects the host without capping Planner or Validator continuation.

Per-operation limits apply independently to each outer operation and do not form a hidden cumulative Run budget, because cumulative enforcement would recreate a semantic continuation cap.

The host probe proves same-parent atomic rename, create-only regular files, file and directory flush, no-follow observation, executable launch without shell interpolation, process-group observation, and read-only history-tool behavior, because unsupported primitives invalidate the promised integrity boundary.

The maintained runtime source manifest and frozen `runtime-manifest.json` use the following canonical schema, because re-execution must prove the exact controller closure rather than copy an incidental directory:

```text
RuntimeManifest
  schema
  interpreter_absolute_path
  interpreter_sha256
  interpreter_version
  standard_library_root_identity
  entries[]
    disposition: COPIED | HOST_BOUND
    absolute_or_source_relative_path
    frozen_relative_path | null
    mode
    size_bytes
    sha256
```

Runtime entries are sorted regular files only and reject symlinks and special files; STT-owned and third-party production files are `COPIED` beneath `runtime/`, while the exact interpreter and loaded standard-library modules are `HOST_BOUND` and revalidated by path, size, mode, and SHA-256 on every invocation, because mixed-generation copied code or host runtime substitution must fail before semantic work without pretending a Python executable is self-contained.

Frozen re-execution disables `PYTHONPATH`, user-site packages, current-directory imports, bytecode writes, and ambient site customization, constructs `sys.path` only from the copied runtime and verified standard-library roots, and rejects any imported module whose resolved no-follow file identity is absent from `runtime-manifest.json`, because a complete manifest would not freeze execution if ambient import resolution could load mutable code after startup.

Runtime-closure qualification imports every production entry point and representative dynamic path under tracing and fails when any loaded production or standard-library module is absent from the maintained manifest, because a closure that omits dynamic or host-bound code would give false frozen-runtime confidence.


The target workspace index has a configured per-entry and total-byte bound and records explicit truncation or omission entries rather than silently dropping paths, because Planner must distinguish complete structural context from bounded observation.

The persisted index at `rounds/<round-number>/workspace-index.json` uses the following canonical schema and sorted no-follow traversal, because Planner context and qualification need one reproducible structural snapshot:

```text
WorkspaceIndex
  schema
  target_identity_ref
  complete
  entries[]
    relative_path
    type: REGULAR_FILE | DIRECTORY
    mode
    size_bytes | null
  omissions[]
    relative_path_prefix
    reason: ENTRY_LIMIT | BYTE_LIMIT | SYMLINK | SPECIAL_FILE | READ_ERROR
```


Workspace-index overflow does not cap Planner reasoning and may be investigated through admitted target-read work, because an index is convenience context rather than the only target view.

Boundary reverifies target-root identity before every effectful launch and after every outer call, because same-path replacement must not redirect authority unnoticed.

A mismatch in frozen runtime, authoritative Run root, caller-selected store root, target-root identity, or current Task/Round/request control identity derives `INVALID` and rejects the lower-trust return, because continuing after control or authority redirection would make later evidence untrustworthy.


---

## 8. Read-only STT history tools

Semantic roles receive a virtual root `/stt` backed by the committed Run tree snapshot, because complete history access does not require disclosure of unrelated host paths.

The minimum operations are closed and structured, because raw shell utilities could expose mutating flags or path escape:

```text
list(path)
stat(path)
find(root, name_pattern, type_filter, max_results)
read(path, max_bytes)
read_range(path, offset, length)
grep(root, pattern, literal_or_regex, max_results, max_match_bytes)
json_query(path, expression, max_result_bytes)
```

Every operation rejects writes, traversal, symlinks, special files, host-absolute paths, and paths outside the accepted grant, because read freedom does not include lifecycle mutation or host authority.

Each request and response is bounded by frozen per-call transport limits and reports truncation truthfully, because one read tool call must not exhaust host memory or hide incomplete results.

Tool requests, source identities or byte ranges, responses, failures, and truncation facts append to the disposable exchange transcript and are imported as `tool-events.jsonl` in the enclosing `ATTEMPT_FINISHED` package, because reconstructing model context does not require a separate lifecycle transition for every read or mutable authoritative capture.

A failed tool request returns a closed structured error and remains in the transcript, because missing or unreadable context must be visible rather than converted into empty success:

```text
NOT_FOUND
NOT_REGULAR_FILE
OUTSIDE_GRANT
PATH_ESCAPE
SYMLINK_REJECTED
INVALID_QUERY
RESULT_LIMIT
READ_ERROR
```

Each tool-event JSONL line obeys the per-request and per-response bounds while the transcript has no configured cumulative read count or byte ceiling, because per-operation audit must remain streamable without becoming a semantic reading budget.

A real exchange-storage write failure returns `READ_ERROR`, prevents the affected tool result from being delivered as successful context, and remains visible to the role and Attempt outcome, because STT must not permit an unrecorded read merely to keep reasoning alive.

The role sees only the committed prefix bound by its OperationRequest’s `RunPrefixManifest`, because current-operation and concurrent stop files must not appear gradually while the role is reasoning.

---

## 9. Launcher, adapters, commands, and settlement

Boundary commits the exact OperationRequest and Attempt before launch intent, because the identity to be launched must already be durable.

For the launch handoff Boundary reacquires `writer.lock`, revalidates the complete active frontier and absence of a stop request, commits `LAUNCH_INTENT_RECORDED`, and invokes only the adapter’s bounded local handoff primitive before releasing the lock, because the marker and the first action capable of creating effects need one serialization boundary against `stt stop`.

A successful handoff returns a verifiable local process or adapter-worker identity and establishes `LAUNCHED`; an immediate failure that satisfies the closed proof codes is committed as `PROVEN_NOT_LAUNCHED` before lock release; and a handoff whose launch status cannot be proved is committed or later derived as `LAUNCH_UNKNOWN`, because every exit from the serialized boundary must preserve the replay decision.

An Attempt with no launch-intent event may be resumed using the same Attempt identity, because no launch-capable action was authorized yet.

A failed prerequisite before launch intent returns transient `PRELAUNCH_BLOCKED`, leaves that Attempt open, and permits a later invocation to reevaluate the same frozen request, because no operation occurred and mutable external availability may change.

A prerequisite failure caused by an immutable request or authority defect rejects before `OPERATION_REQUESTED`, because a permanently inadmissible request must not enter the launch lifecycle.

An Attempt with launch intent and committed `PROVEN_NOT_LAUNCHED` ends the current public invocation as `PRELAUNCH_BLOCKED`, while only a later `start` or `run` invocation may create the next Attempt ordinal for the same OperationRequest, because positive non-launch permits reconsideration but must not become an automatic retry loop.

An Attempt with `LAUNCHED`, `LAUNCH_UNKNOWN`, or interruption before a trustworthy outcome permanently forbids another launch of that OperationRequest, because hidden effects may already exist.

Boundary records call state, result kind, and local settlement independently, because a returned value and a stopped process prove different facts.

A later `run` or `stop` invocation may probe the exact `live-operation.json` identity and commit `SETTLEMENT_OBSERVED` only after positive local settlement, while inability to prove settlement leaves the Run blocked and creates no observation, because absence of evidence must not become a false settled fact.


Boundary collects bounded stdout, stderr, raw return, tool transcript, routing observations, timing, process-group observations, capture omissions, and truncation facts in the disposable exchange, seals them through `completion.json`, and imports immutable copies through the Attempt-finish transition, because Validator and operators need the closest available account of reality without observing partial authoritative files.

Boundary never interprets `SETTLED` as remote quiescence, because escaped children, remote work, billing, logging, and provider-side effects may continue.

Provider adapters contain transport translation only and never change Plan semantics, because fallback or semantic repair inside adapters would evade Boundary and Validator review.

Command argv is rendered directly from the frozen profile and admitted typed arguments without a shell, because shell interpolation would create undeclared executable syntax.

After every outer call Boundary revalidates frozen runtime, Run root, target root, active Task, Round, OperationRequest, and pre-call ledger heads before accepting a return, because lower-trust work must not mutate authoritative context unnoticed.

---

## 10. Planner, steps, children, and Lead

Planner receives exact Task mission, authority, required outputs, current Round, workspace index, route/profile descriptions, and full `/stt` tools, because it must reason from the complete persisted current-Run context without inheriting operational authority.

Planner returns `DECLINE` or a finite serialized nonempty Plan, because each individual accepted planning decision must be persistable and no-step work is represented by `DECLINE` rather than an empty executable contract.

Boundary publishes exact input resolutions and accepted Plan bytes before any step starts, because execution must not guess what the Planner selected.

A Worker receives only its accepted step, exact `InputBinding` attachments, admitted target scopes, output requirements and bindings, route, and accepted read grant, while a command receives its accepted step, exact `INPUT_PATH` bindings, profile, output-source bindings, and no read-tool capability, because effectful roles must not inherit lifecycle control, ambient history authority, mutable-source substitution, or freedom to choose output destinations.

Boundary launches a Worker with the frozen target root as its admitted working root, supplies canonical allowed read and write-responsibility scopes in the private contract, configures provider-native tool restrictions when available, and records unavailable isolation as `UNKNOWN`, because the MVP constrains constructed access without claiming hostile-process containment.

A Worker must return a best-effort effect report whose paths and effect classes Boundary validates against the accepted step before committing `StepResult`, while a command may supply only the profile-declared structured effect report, because reported out-of-scope activity must be exact even though unreported effects remain undetectable.

A reported mutation of authoritative STT state derives `INVALID`; relevant unsettled or unknown local work derives `OPERATIONALLY_BLOCKED` and suppresses every Validator; otherwise Boundary persists the exact violation, stops later Plan steps, and permits Validator to judge the Task from the settled valid history, because the architecture assigns different consequences to corrupted evidence, active effects, and settled scope breach.

Boundary stops later Plan steps after a non-satisfied accepted local outcome, unsatisfied output contract, settled non-OK call, dependency mismatch, reported scope violation, or operational block, because later steps must not assume a failed, incomplete, or unsafe prerequisite.

A child Task uses the parent Task step’s mission, authority, and output requirements and is published before child execution, because the parent Plan contains the complete child contract.

The child Task ledger reaches a semantic terminal or operational stop before the parent commits `STEP_FINISHED`, because depth-first execution must expose one active frontier.

The parent `StepResult` binds an exact `ChildOutcomeRef` to either the child `TaskResult` or its committed `OperationalStopRef` and never fabricates a child role return, because operational absence of judgment differs from child semantic judgment.

Child outcome mapping is closed as follows, because every ancestor must derive the same consequence without interpreting child prose:

```text
child SATISFIED       -> parent step SATISFIED
child NOT_SATISFIED   -> parent step NOT_SATISFIED
child INDETERMINATE   -> parent step INDETERMINATE
settled child OPERATIONALLY_STOPPED not caused by Run stop
                      -> parent step OPERATIONAL_INDETERMINATE
                      -> stop later parent steps
                      -> permit parent Validator
child OPERATIONALLY_BLOCKED or relevant UNKNOWN/UNSETTLED
                      -> whole Run OPERATIONALLY_BLOCKED
                      -> no ancestor Validator
child NON_RESUMABLE   -> whole Run NON_RESUMABLE
                      -> no ancestor Validator
child INVALID         -> whole Run INVALID
Run-wide operator stop while child active
                      -> no child-to-parent failure mapping
                      -> no new ancestor semantic call
```


Lead repeatedly asks `state.py` for one `NextAction` and invokes only the corresponding Boundary method, because deterministic orchestration must not inspect model prose or invent lifecycle transitions.

Lead uses an explicit iterative stack of Task references rather than Python recursion, because unlimited semantic depth must not exhaust the host call stack.

---

## 11. Validator, Rounds, and Task completion

Before `VALIDATION_STARTED`, Boundary evaluates every current Task `OutputRequirement` into one ordered `TaskOutputAssessment`, because Validator must receive a total mechanical account rather than infer artifact satisfaction from directory contents.

Boundary considers accepted immutable Run artifacts and matching target artifacts whose exact facts satisfy the Task requirement and producer constraint, applies the deterministic selection rule, creates one `PRE_VALIDATOR` revalidation only when the selected candidate is a target artifact, and marks the entry `SATISFIED` only when that selected candidate remains valid, because stale, wrong-producer, order-dependent, or unbounded candidate evidence must not become mechanically eligible.

For a still-unsatisfied `BOUNDARY` requirement with an exact target path, Boundary may observe that path directly, create a `BOUNDARY_OBSERVATION` `ArtifactRef` only when the object passes the complete requirement check, and include it in the same `VALIDATION_STARTED` package, while `ANY_ACCEPTED_STEP` and `EXACT_STEP` requirements cannot be satisfied by such discovery, because caller-authorized pre-existing output may be valid but Boundary observation must not bypass a producer constraint.

Validator receives exact Task mission, required outputs, current Round facts, the complete `TaskOutputAssessment`, all committed operational evidence including revalidations, and full `/stt` tools, because Task-level judgment requires independent access to both semantic history and the current mechanical output contract.

Validator runs as a fresh outer operation without hidden Planner or Worker conversation state, because independent judgment must depend on persisted evidence rather than private invocation memory.

Boundary accepts the Validator result structurally but does not apply novelty, similarity, progress, or better-basis gates, because those semantic judgments belong to Validator.

Before committing an otherwise valid `SATISFIED` Validator result, Boundary preserves every pre-Validator selected candidate, repeats exact revalidation for each selected target artifact, writes `output-assessment-post.json`, and accepts only when every selected candidate remains valid, because changing the chosen evidence during the Validator call would make terminal satisfaction depend on facts the Validator did not judge.

An accepted `REPEAT` commits the current Round result and, when no Run-wide stop is committed, creates the next contiguous Round, binds the preceding Validator report as its immediate continuation reason, and continues the same driver invocation, because continuation is internally authorized by Validator but operator cancellation forbids future semantic work.

When an operator stop is committed after the Validator call launched but before successor-Round publication, Boundary finalizes the accepted Validator and Round records but does not create the successor Round, because cancellation preserves already-produced facts without starting new work.

All earlier Task records remain readable rather than copied into a cumulative prompt package, because the filesystem already provides complete history.

An accepted `FINISH` commits the Round and Task result, and a `SATISFIED` TaskResult copies the post-Validator assessment’s sorted one-artifact-per-requirement map while other judgments carry an empty `satisfied_outputs`, because terminal output lineage must remain exact, bounded, and independent from Validator prose.

A settled Validator non-OK outcome records an operational stop with no Task judgment, because no lower role may fabricate semantic completion.

Unsettled or unknown relevant work blocks Validator and every ancestor Validator, because semantic judgment must not race possibly active effects.

---

## 12. Operator stop and public CLI

The stop request uses the following canonical body, because cancellation needs one idempotent Run-wide meaning without timestamps or free-form fields changing identity:

```text
OperatorStopRequest
  schema
  run_id

OperatorStopRecord
  schema
  request
  request_start_prefix_ref
  stop_prefix_ref
```

In this plan, `stop frontier` means only the commit-frontier manifest referenced by `stop_prefix_ref`, while `request_start_prefix_ref` records only the validated state from which the operator request began, because post-stop event admissibility must be evaluated against the final committed Task heads immediately before cancellation became authoritative.

The public CLI implements the architecture commands exactly, because startup, advancement, observation, diagnosis, and cancellation have different authority:

```text
stt start --workspace <target> --store-root <store-root> --task-spec <spec> --routing-file <routing> [--prior-run <run-root>] [--allow-live-provider]
stt run --run-root <run-root>
stt status --run-root <run-root>
stt diagnose --run-root <run-root>
stt stop --run-root <run-root>
```

`start` publishes the Run and advances it, while `run` advances an existing Run, because creation and continuation need separate preconditions.

`status` returns the validated `RunView` and compact active-frontier receipt, while `diagnose` returns detailed evidence and conflict locations, because routine observation and forensic explanation serve different users.

`diagnose` may inspect a surviving exchange read-only but labels every such fact `UNCOMMITTED_EXCHANGE_OBSERVATION` and never uses it for state derivation, because uncertain mutable capture can aid an operator without becoming authoritative lifecycle truth.


`status` and `diagnose` never complete packages, append ledgers, or repair state, because read-only observation must not change the lifecycle being reported.

`stop` acquires `writer.lock`, records whether the initial validated state is already semantically finished, `INVALID`, or `NON_RESUMABLE`, invokes `CREATE_ROOT_TASK` only through the exact frozen derivation when needed, and runs to a fixed point only the immediately available non-effectful actions `COMMIT_ELIGIBLE_PACKAGE`, `RECOVER_ATTEMPT_OUTCOME` from valid sealed completion, `OBSERVE_SETTLEMENT` from positive local evidence, `FINALIZE_OPERATION_PHASE`, `MAP_CHILD_RESULT`, `FINALIZE_ROUND`, and `FINALIZE_TASK`, because cancellation must preserve deterministic facts already produced without launching a role, creating a child, or creating a successor Round.

A stop request whose initial validated state is already semantically finished, `INVALID`, or `NON_RESUMABLE` returns that state without appending cancellation, because an operator action requested after completion or irrecoverable corruption cannot change the accepted lifecycle.

If deterministic closure newly derives `INVALID` or `NON_RESUMABLE`, `stop` returns that outcome without appending cancellation, because an untrustworthy or irrecoverable lifecycle cannot safely receive a later control overlay.

When the initial validated state was nonterminal and the closure remains valid and resumable, Boundary stores the captured initial heads as `control/stop-prefixes/request-start/<prefix-id>.jsonl`, streams and hashes the current validated heads as `control/stop-prefixes/commit-frontier/<prefix-id>.jsonl`, binds both same-package `PayloadRef` values in `OperatorStopRecord`, and commits one `OPERATOR_STOP_REQUESTED` package in the root Task ledger even when the closure has just produced a semantic terminal, because the authoritative history must preserve both the operator request’s original position and every deterministic fact committed before cancellation became authoritative.

`OPERATOR_STOP_REQUESTED` is the sole event permitted after root `TASK_FINISHED`, and only when its `request_start_prefix_ref` validates a nonterminal state while its `stop_prefix_ref` validates the closure-produced terminal immediately before the stop event, because this narrow mechanically provable overlay records operator intent without reopening or altering semantic completion.

A repeated stop after the same committed request is idempotent while any conflicting cancellation record is `INVALID`, because cancellation must not create competing control facts.

When no outer operation is active, Lead derives `OPERATIONALLY_STOPPED` without a mission judgment and creates no later OperationRequest, because operator control must not be misreported as mission failure.

When an outer operation may be active, `stop` uses the verified exchange `live-operation.json` to request best-effort local process-group or channel termination and records settlement honestly, because cancellation cannot prove remote or escaped work ended.

Active cancellation derives `OPERATIONALLY_STOPPED` only after relevant local work is `SETTLED`, `OPERATIONALLY_BLOCKED` while work is `UNSETTLED` or `UNKNOWN`, and `NON_RESUMABLE` when the launched outcome cannot be reconstructed, because public state must follow the ordinary settlement and replay rules.

---

## 13. Construction slices and proof links

### Slice 1 — storage and derivation

Implement §§3–5 and complete `Q01`–`Q09`, because no semantic operation should depend on unproved persistence, publication, locking, or replay boundaries.

### Slice 2 — Bootstrap and frozen base

Implement §7 and complete `Q10`–`Q13`, because semantic execution requires one immutable runtime, target identity, import contract, and root authority base.

### Slice 3 — contracts, authority, artifacts, and history tools

Implement §§6 and 8 and complete `Q14`–`Q19`, because admission, exact binding, and free persisted context must use one canonical contract set.

### Slice 4 — launch and adapters

Implement §9 and complete `Q20`–`Q25`, because one-launch safety and truthful settlement must be proven before orchestration uses live routes.

### Slice 5 — Planner, steps, children, and Lead

Implement §10 and complete `Q26`–`Q29`, because semantic freedom must operate through mechanically admitted sequential execution.

### Slice 6 — Validator, Rounds, and stop

Implement §§11–12 and complete `Q30`–`Q33`, because Task judgment, automatic continuation, crash closure, and operator control must coexist without hidden semantic caps.

### Slice 7 — integration and promotion

Complete `Q34`–`Q36`, repository regression, document gates, and accepted-pair recording, because implementation readiness is an end-to-end claim.

---

## 14. Canonical qualification catalog

This is the only numbered executable scenario catalog, because duplicate proof lists would create competing coverage authority.

Each deterministic scenario includes positive, known-bad, interruption, and identity-substitution variants where relevant, because confirmation-only testing can pass while the contract is wrong.

The qualification harness may impose a finite wall-clock, provider-call, Task, and Round budget per test case, because a test runner must terminate even though production STT has no semantic count cap.

Harness-budget exhaustion fails the test and does not create a production lifecycle outcome, because qualification containment must not leak into runtime semantics.

### Persistence and publication

- `Q01` canonical JSON, record bounds, duplicate-key rejection, and identity hashes
- `Q02` transition manifest, event hash, transition hash, payload verification, and no hash cycle
- `Q03` ledger grammar, sequence and prior-hash validation, terminal exclusivity, and torn-tail handling
- `Q04` package-first crash completion, stale package, competing package, and package/event mismatch
- `Q05` pure state derivation precedence, active frontier, conflicts, and no mutable cursor
- `Q06` create-only exchange-root identity, nonauthoritative orphan handling, atomic Run publication, and crash before root Task publication
- `Q07` atomic root and child Task publication, equal idempotence, and conflicting directory rejection
- `Q08` flat Task registry and child-to-parent result mapping after interruption
- `Q09` runner overlap rejection, writer serialization, stable read-only status, and `RUN_BUSY`

### Bootstrap, authority, and contracts

- `Q10` complete `RootTaskSpec`, no active semantic count fields, and frozen per-operation control, input, output, tree, wait, and capture safeguards
- `Q11` runtime closure, isolated import path, unmanifested-module rejection, re-execution, mixed-generation rejection, and self-modification survival
- `Q12` source, target, Run-root, no-follow, special-file, `.git`, and replacement-identity checks
- `Q13` initial and prior import selection, copied-byte independence, provenance, and no state merge
- `Q14` equal-or-narrower child authority, effect classes, environment admission, and route/profile closure
- `Q15` Plan, step, read-grant, input, output, artifact, role-result, and Boundary-result schema substitution cases

### History and target context

- `Q16` Planner and Validator full committed-prefix access through every read-only tool, including a large streamed prefix manifest beyond one control-record limit
- `Q17` delegated `NONE`, `FULL`, and `SUBTREE` access with write, escape, symlink, and ungranted rejection
- `Q18` tool transcript reconstruction, structured failures, source identity, range capture, result limits, and truthful truncation
- `Q19` deterministic workspace index, explicit omission, target change, and authoritative reobservation

### Launch, providers, and commands

- `Q20` OperationRequest and Attempt identity, writer-serialized stop check plus launch handoff, launch-intent ordering, and same-Attempt resume before intent
- `Q21` every accepted `PROVEN_NOT_LAUNCHED` proof and every forbidden ambiguous proof
- `Q22` actual or uncertain launch permanently forbids another launch of the same OperationRequest
- `Q23` call/result/settlement algebra, monotonic settlement observations, local-only settlement meaning, capture limits, and post-call identity revalidation
- `Q24` deterministic fake provider plus controlled Claude Code and Codex adapters with truthful requested and observed routing
- `Q25` command profile resolution, typed argv, empty-base environment, cwd admission, accepted exits, outputs, and executable revalidation

### Planner, steps, children, Validator, and stop

- `Q26` direct, investigative, and decline Planner behavior with no similarity, Task-count, depth, Plan-step, or continuation rejection
- `Q27` exact Plan-time input resolution, deferred producer outputs, launch-time reverification, bounded read-only exchange input materialization, `INPUT_PATH` rendering, and wrong-consumer substitution rejection
- `Q28` Worker and command local outcomes, bounded file and tree output verification, reported effects, later-step stop, and no fabricated role result
- `Q29` same-mission child acceptance, deep iterative traversal, semantic mapping, operational stop mapping, whole-Run block, and invalid child
- `Q30` Validator independence, complete context, total Task-requirement-to-artifact assessment after execution or `DECLINE`, deterministic bounded candidate selection, Boundary observation under producer constraints, stable pre/post target-artifact revalidation, stale-output rejection, all legal judgment/disposition pairs, and no novelty gate
- `Q31` automatic repeated Rounds beyond prior caps, contiguous identities, readable history, immediate continuation reason, and eventual `FINISH`
- `Q32` settled Planner, Worker, command, and Validator failures plus unsettled and unknown propagation
- `Q33` operator stop between operations, exact root-Task derivation before stop, stop-versus-launch-handoff race, streamed request-start and commit-frontier manifests, legal and illegal post-stop child-ledger events, semantic completion during stop with the same durable stop overlay visible in `RunView`, stop during local work, best-effort termination, blocked and non-resumable outcomes, idempotence, and no fabricated judgment

### Integration and promotion

- `Q34` caller-selected store root, CLI start/run/status/diagnose/stop, nonblocking `status` and `diagnose` with `RUN_BUSY` under temporary writer ownership, plain and Git targets, public outcomes, durable operator-stop visibility, and no internal `NextAction` leakage
- `Q35` exhaustive crash-window and derivation-precedence matrix, including launch-intent/handoff interruption, atomic exchange completion recovery, absent or conflicting completion, delayed settlement observation, package closure, phase finalization, child mapping, cross-ledger stop ordering, accepted `REPEAT` plus stop, active cancellation, and every conflict-to-`INVALID` path
- `Q36` architecture-to-plan and plan-to-architecture trace, superseded-concept rejection, focused and full regression, WELL, independent RunSkeptic convergence, and exact accepted-pair commit recording

### Real-model adversarial evaluation

The real-model evaluation cases and rubric are committed before execution, because post-hoc criteria could turn any result into success.

The evaluation covers history discovery, same-mission continuation, satisfied, not-satisfied, indeterminate, productive repeat, stagnation, circularity, far failure, instruction injection, and sensitive-history delegation, because these behaviors exercise semantic risks deterministic schemas cannot prove.

Each case records exact frozen prompts, architecture and contract refs, route, requested and observed routing, complete retained transcript, result, independent adjudication, and material findings, because empirical evidence must be reproducible and honestly scoped.

A runtime-contract violation fails qualification immediately, because deterministic safety and truthfulness are implementation obligations rather than model-quality preferences.

A semantic failure becomes a material finding and blocks promotion until the receiving Core classifies it as repaired, accepted residual risk, or architecture conflict through RunSkeptic, because real-model evaluation must have consequences without pretending to prove general correctness.

No aggregate score or one favorable model run can override an unresolved material finding, because averages can conceal a critical failure mode.

---

## 15. Superseded-concept checks

Static checks reject the following concepts from active architecture, implementation, contracts, schemas, state derivation, and user-facing runtime text except in explicit rejection tests, because their reappearance would silently restore superseded semantics:

```text
maximum_task_depth
maximum_tasks_per_run
maximum_rounds_per_task
maximum_steps_per_round
AWAITING_REPEAT
caller-mediated REPEAT
one repeat per invocation
distinct or narrower child mission
ancestor mission hash rejection
mandatory mission relation reason
Validator remaining Round capacity
REPEAT novelty floor
selected evidence as Validator visibility boundary
Planner or Validator has no read tools
TaskHistoryView
zero-step validation
```

Internal `NextAction` names are permitted only inside implementation and tests and must not appear as architecture-owned public outcomes, because the repaired architecture intentionally removed internal derivation vocabulary.

---

## 16. Definition of done and merge gate

The implementation plan is ready to merge with the architecture only when all of the following document gates hold, because merge should preserve one internally consistent candidate pair:

- exact architecture commit and SHA-256 match this header
- mechanical WELL checker passes both documents, with exact document identities, checker identity, applied rules, violations, and every exemption recorded
- manual WELL review finds every material proposition warranted, explicit, lean, and linked
- architecture-to-plan trace finds no architecture rule without one mechanism and proof path
- plan-to-architecture trace finds no production mechanism that invents semantic meaning
- RunSkeptic Find Loop converges on the unchanged architecture
- RunSkeptic Find Loop converges on the unchanged pair
- PR remains unmerged until every unresolved ACTION, CONFLICT, or review-required item is closed

Production implementation is done only when `Q01`–`Q36`, focused tests, compile, formatting, lint, shell fixtures, runtime closure, `git diff --check`, the full repository suite, real-model adjudication, and promotion review pass, because the document merge approves a build contract rather than proving its future implementation.

Implementation stops at that point, because additional framework or generalization would exceed the accepted MVP.
