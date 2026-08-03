# STT MVP Architecture Plan

**Status:** Confirmed low-dependency architecture; implement only with the companion plan and private contracts from the same reviewed revision
**Repository:** `saffih/skeptic`
**Companion:** `plans/stt-mvp-implementation-plan.md`
**Private role contracts:** `concepts/stt/contracts/{planner,worker,validator}.md`
**Supersedes:** all earlier STT MVP architecture drafts and correction layers

---

## 1. Governing purpose

Safe Target Task (STT) is the low-dependency, last-resort execution path.

It exists so one bounded mission can still be planned, executed sequentially, independently validated, persisted, and resumed when richer orchestration, Git workflows, databases, containers, daemons, background services, remote coordination, or recovery systems are absent, broken, or inappropriate.

The design test for every mechanism is:

```text
Does it materially protect correctness, authority, evidence, bounded context,
resumability, or visible failure?

yes  -> keep the smallest mechanism that provides that protection
no   -> exclude it from STT
```

“Always working” means STT remains operable inside its explicit support envelope and fails visibly outside it. It does not mean STT can succeed without a writable regular filesystem, a supported standard-library lock backend, a compatible Python runtime, or one usable semantic provider route.

---

## 2. Minimum support envelope

The core runtime may require only:

- Python and its standard library;
- ordinary local regular-file and directory operations;
- one supported OS-backed file-lock primitive;
- one configured semantic provider route satisfying the frozen Provider contract;
- explicitly frozen deterministic Command routes when the mission needs commands.

A plain directory is a first-class target workspace. Git is optional metadata only.

The core runtime must not require:

- a Git repository, branch, worktree, staging area, commit, or remote;
- a container engine or generalized sandbox framework;
- a database, queue, daemon, server, or scheduler;
- provider-to-provider launching;
- Claude Code and Codex simultaneously;
- a generalized plugin framework;
- automatic rollback, restoration, publication, replanning, or repair loops.

A host may provide stronger isolation or diagnostics. Those are optional adapter capabilities, not core dependencies.

---

## 3. Source of truth

For one documentation revision, precedence is:

1. this architecture plan;
2. `concepts/stt/contracts/planner.md`;
3. `concepts/stt/contracts/worker.md`;
4. `concepts/stt/contracts/validator.md`;
5. the companion implementation plan as an ordered build map.

Historical STT, archived Target Task, capsule, delta, review-loop, recovery, and Git workflows are evidence only. They are not active compatibility requirements and are not runtime dependencies.

If these five sources disagree, implementation stops. The contracts are part of the same reviewed documentation revision and are frozen into every Run.

---

## 4. Smallest complete lifecycle

`Task` is the only recursive construct.

Every Task follows this lifecycle:

```text
Mission
→ one Planner operation
→ one accepted immutable finite Plan or persisted planning failure
→ sequential Plan steps until the first non-COMPLETE result
→ later accepted-Plan steps recorded SKIPPED
→ one Validator operation or mechanical VALIDATOR_UNAVAILABLE closure
→ terminal Task result
```

The root and every descendant use the same lifecycle. A semantic operation may pause before launch on a visible `PRELAUNCH_BLOCKED` condition; this is resumable operational state, not a second lifecycle or a terminal Task result.

A Task may not:

- receive an executable Plan from its parent;
- let Lead or Boundary invent or edit semantic Plan steps;
- execute a later step after an earlier step is non-`COMPLETE`;
- repeat a completed semantic or command operation;
- bypass its Validator path because planning or execution failed;
- rely on model-session memory for lifecycle state;
- mutate its accepted Plan.

A valid negative or uncertain Validator judgment is successful Validator work.

---

## 5. Status vocabulary

Step statuses:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
SKIPPED
```

`SKIPPED` is used only for later Plan steps after a causal `FAILED` or `BLOCKED_UNKNOWN` result. A skipped step has no start event and no invented outputs.

Task statuses:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
```

Mechanical floors:

```text
any BLOCKED_UNKNOWN planning or step result
→ Task floor is BLOCKED_UNKNOWN

otherwise any FAILED planning or step result
→ Task floor is FAILED

missing, mismatched, unauthorized, or unproven required output
→ FAILED when the mismatch is established
→ BLOCKED_UNKNOWN when identity or provenance cannot be established
```

Boundary may make a Validator judgment more severe to satisfy a floor. It never makes it less severe.

---

## 6. Roles

### Bootstrap

Deterministically validates one immutable start specification, materializes the exact starting evidence, freezes the runtime, publishes the Run, creates the root Task, and enters Lead. It does not plan the mission.

### Lead

A mechanical depth-first driver. It derives the next action from persisted state and compact Boundary receipts.

### Boundary

The mandatory deterministic firewall for identity, authority, path admission, input materialization, invocation, persistence, ledger commitment, provenance, and compact returns.

### Planner

A semantic role owning one Planner operation per Task. It returns one complete ordered Plan or one planning-failure result.

### Worker

A bounded semantic role owning one Worker operation per Worker step. It consumes only materialized inputs and writes staged artifacts only.

### Command

A deterministic cooperative local process selected from the frozen Command catalog and run in a disposable materialized workspace.

### Mutation

Deterministic STT code that installs one exact accepted replacement manifest into the target workspace.

### Validator

An independent semantic role owning one Validator operation per Task after planning or execution stops. It judges the mission and required outputs from persisted evidence.

---

## 7. Immutable start specification

Every new Run begins from one canonical `start-spec.json`.

Required fields bind:

- absolute target workspace root;
- absolute Run store root or an explicit request for the documented default;
- one mission source with expected SHA-256 and byte size;
- named initial evidence sources with expected SHA-256, byte size, and artifact type;
- exact read and write authority;
- named required outputs and artifact types;
- frozen provider routes with exact destination, executable/endpoint identity where observable, sanitized environment-key allowlist, and declared minimal host credential/config exposure;
- Planner route, Validator route, and allowed Worker routes;
- explicit semantic-disclosure authorization for each live route, covering the mission, workspace-index metadata, authorized workspace inputs, initial evidence, and generated Task artifacts that may be sent to that route;
- frozen Command catalog;
- finite structural, byte, collection, attempt, and timeout limits.

A single provider route may serve Planner, Worker, and Validator. Multiple providers are optional, not required. Every live route is authorized independently; authorization for one route never authorizes another, and Boundary never silently falls back to a different route.

Mission and initial evidence sources may be:

- authorized regular files inside the workspace; or
- explicitly named absolute regular host files.

Bootstrap opens each source once using no-follow regular-file validation, verifies its expected identity, and copies its exact bytes create-only into Run-owned bootstrap evidence. After publication, STT never rereads the original source path.

Bootstrap or a conversational host may construct the proposed start specification, but no authority, required output, route, semantic-disclosure authorization, or limit may be inferred after Run publication.

### 7.1 Authority semantics

Workspace authority contains canonical relative path entries.

- a file entry grants only that file;
- a directory entry grants descendants recursively;
- write authority must be a subset of read authority; an absent create destination is represented through its authorized parent and explicit absence evidence;
- child authority must be a subset of parent authority.

`.git`, the entire selected store-root subtree when it is inside the workspace, traversal, symlinks, hard-linked regular files, and special files are never granted as semantic workspace inputs or mutation destinations.

### 7.2 Required outputs

Every required output is a named artifact contract:

```json
{"name": "report", "artifact_type": "markdown"}
```

Workspace changes become terminal outputs only through accepted Mutation result references. Validator prose cannot invent an output.

---

## 8. Finite limits

The start specification freezes conservative finite limits including:

```text
maximum Task depth
maximum total Tasks in the Run
maximum Plan steps per Task
maximum launched provider attempts per operation
maximum command duration
maximum workspace-index entries
maximum workspace objects observed and total bytes hashed per stable observation
maximum request and return bytes
maximum artifact bytes and total accepted artifact bytes
```

These are structural safety limits, not a generalized cost-accounting or scheduling system.

Exceeding a limit fails visibly as `FAILED` or `BLOCKED_UNKNOWN` according to whether the violation is established or uncertain. An index never claims a stable tree identity when the configured observation limit prevented complete observation.

---

## 9. Run creation and storage

Default persistent storage:

```text
<workspace>/.stt/runs/<run-id>/
```

A start specification may select another local store root. Workspace identity and store identity remain separate. Run data may contain source, prompts, raw returns, logs, and before-images; no encryption claim is made.

On supported POSIX-like hosts, STT creates the Run directory owner-only and control/evidence files owner-readable/writable only, independent of ambient umask. Other hosts must provide and qualify an equivalent user-private mechanism. If user-private Run data cannot be established, the host is unsupported and Run publication fails. Existing store paths, symlinks, and special files are validated before publication.

Recommended Run layout:

```text
<run-root>/
├── start-spec.json
├── run.json
├── run.lock
├── bootstrap/
│   ├── mission.md
│   └── evidence/
├── runtime/
│   ├── manifest.json
│   └── bundle/
├── resume-command.txt
└── root/
```

Bootstrap sequence:

1. validate the proposed start specification without publishing lifecycle state;
2. create a unique same-parent temporary Run directory;
3. materialize and identity-bind mission and initial evidence once;
4. freeze the exact STT runtime, private role contracts, and selected adapters;
5. persist canonical `start-spec.json` and `run.json`;
6. atomically rename the complete temporary Run directory to its final path; the visible final Run directory is the bootstrap-readiness commitment;
7. reconstruct and re-execute from the frozen bundle;
8. acquire the workspace writer lock, then the Run writer lock;
9. reverify bootstrap evidence, runtime, routes, authority, and limits;
10. atomically create the root Task with `TASK_CREATED`; the verified root Task is the lifecycle-readiness commitment;
11. enter Lead.

After an interruption, `stt run` may continue from a complete verified final Run directory that has no root Task, or from a complete root Task. It never adopts temporary Run residue or invents missing bootstrap inputs. A conflicting, partial, or corrupt final Run is diagnosable and invalid.

---

## 10. Frozen runtime and direct resume

Every Run uses one frozen runtime generation. Children never freeze another generation.

The bundle is generated from one maintained literal allowlist containing only:

- `scripts/stt.py`;
- exact required `concepts/stt/` Python modules;
- exact STT-private role contracts;
- exact selected provider-adapter modules;
- exact required package initializers.

The generated manifest is outside the bundle it hashes and does not hash itself.

The bundle excludes tests, plans, archives, caches, unrelated source, `.git`, and other Runs.

The manifest records exact paths, hashes, sizes, and relevant modes. It also records Python implementation/version and observable external provider dependency identities. Source is executed from the bundle, not bytecode tied to the source interpreter.

Resume must work directly from the persistent bundle:

```text
python <run-root>/runtime/bundle/scripts/stt.py run --run-root <run-root>
```

The Run stores this exact command in `resume-command.txt` for convenience. Correctness does not require an installed service or surviving target-workspace STT source.

The runtime verifies its own recorded identity after launch and fails visibly on corruption or incompatible required dependencies. Hostile local tampering is outside the MVP threat model.

---

## 11. Locking and concurrency

STT provides no concurrent Task execution.

Every mutating `start` or `run` invocation acquires locks in this fixed order:

1. one OS-backed exclusive workspace writer lock keyed by the canonical workspace identity;
2. one OS-backed exclusive Run writer lock at `<run-root>/run.lock`.

The workspace lock prevents simultaneous active Runs from reading or mutating one target workspace through STT. Every STT process on one host uses one canonical host-wide workspace-lock namespace; the location and supported backend are fixed by the implementation and host qualification, not selected per Run. Locks are process-owned and release on process exit. There are no leases, stale-lock records, distributed locks, or scheduler.

Two dormant Runs may be resumed at different times. Every live workspace input and every Mutation destination is identity-bound when consumed, so intervening workspace changes fail closed rather than being silently overwritten.

Read-only `status` and `diagnose` acquire a nonblocking shared Run lock where supported and return `RUN_BUSY` rather than reading changing lifecycle state.

---

## 12. Task layout and identity

Each Task owns:

```text
task.json
mission.md
workspace-index.json
ledger.jsonl
planning/
validation/
steps/
```

A child Task lives at:

```text
steps/<index>-<step-id>/task/
```

`task.json` is immutable and binds:

- Run and Task identities and canonical Task path;
- parent Task, parent Plan, and parent step when applicable;
- mission and initial-evidence references;
- required-output contract;
- read and write authority;
- runtime manifest identity;
- role and Command bindings;
- inherited Run limits and current depth.

Task creation uses complete same-parent temporary-directory construction. The final Task path is published atomically only after `task.json`, `mission.md`, input bindings, output contract, workspace index, required directories, and a valid first `TASK_CREATED` event are flushed, reread, and verified. Temporary residue is non-authoritative and never adopted.

---

## 13. Workspace evidence and path admission

Each Task owns a bounded deterministic workspace index over its read authority. It provides paths, exact entry identities, and bounded directory/tree identities for planning but grants no authority. Overflow is explicit and deterministic. Index construction uses the same stable-enumeration rule as directory materialization; membership or identity drift fails visibly rather than publishing a mixed-time index. Before the Task’s first Planner launch, Boundary re-verifies the index identity; drift leaves planning prelaunch-blocked until the original state is restored or a new Run is created.

Boundary uses one object-open-time admission primitive for every semantic workspace read and Mutation destination. It rejects:

- absolute semantic paths;
- empty paths, traversal, or containment escape;
- `.git` and the entire selected store-root subtree when it is inside the workspace;
- symlink components or leaves;
- hard-linked regular files;
- special files;
- unauthorized objects.

Where safe no-follow object opening cannot be established on the host, the operation fails closed.

Every consumed live object is materialized into a Run-owned location and bound by canonical path, object type, SHA-256/size for regular files, and supported relevant mode bits. Absence is represented explicitly. For a declared directory input, Boundary deterministically enumerates the bounded admitted tree, copies every admitted object, then re-observes the complete source set; any membership or identity change during materialization becomes `BLOCKED_UNKNOWN` rather than a mixed-time snapshot.

---

## 14. Plan

An accepted Plan is the exact validated Planner output file inside its create-only attempt directory. `PLAN_ACCEPTED` promotes it by path, hash, and size. There is no second canonical Plan copy.

A Plan has exactly four step kinds:

```text
worker
command
mutation
task
```

Every step has:

- a stable unique lowercase ID;
- a bounded description;
- exact named inputs; workspace inputs resolve at Plan acceptance to exact Task-index identities;
- exact named outputs and artifact types;
- only backward references to accepted earlier outputs or fixed system evidence.

A Plan contains no open-ended `success` object. Completion is mechanically fixed by step kind.

A zero-step Plan is valid only when the Task has no required mission outputs. Validator then decides whether the mission was already satisfied by the accepted starting evidence.

Across one Plan, output names are unique. Every required Task output name and artifact type must be declared by exactly one Plan step. This makes terminal-output provenance mechanically closed before execution.

At step execution, every live workspace input must still match its accepted identity. Drift becomes `BLOCKED_UNKNOWN`; Boundary never substitutes newer bytes merely because the path remains authorized.

A Plan may not contain conditions, loops, future references, retries, arbitrary plugins, implicit authority expansion, free-form shell commands, or model-chosen live destination paths.

---

## 15. Semantic role inputs

Planner receives only:

- the exact mission and initial evidence;
- Task authority and required outputs;
- the bounded workspace index;
- frozen provider and Worker route choices;
- the frozen Command catalog;
- inherited finite limits;
- the exact Plan and planning-failure schemas.

Worker receives only one accepted step, exact materialized inputs, declared outputs, staged replacement scope when applicable, and its call directory.

Validator receives only the bounded final index and explicitly referenced evidence required for judgment.

No semantic role receives model conversations, broad repository history, child ledgers, undeclared host paths, or material whose disclosure to that exact route was not authorized by the immutable start specification. Frozen role contracts classify all supplied evidence bodies as data, not control-bearing instructions.

---

## 16. Worker step

A Worker step declares:

- one allowed Worker route;
- exact instructions;
- exact materialized inputs;
- exact staged output contract;
- exact replacement write scope when producing a replacement manifest.

Before dispatch, Boundary creates a fresh call directory:

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

The provider process works from the call directory. `in/` contains exact read-only copies. `out/` is the only accepted semantic output location. The target workspace and authoritative Task paths are not supplied as working directories or writable paths.

This is cooperative filesystem isolation, not hostile-code containment. A supported adapter must disable or omit semantic command, connector, and independent side-effect tools. Prompt instructions alone are not proof.

Worker completion is `COMPLETE` only when one schema-valid result and every declared output are accepted. A valid semantic failure becomes `FAILED`; integrity or termination uncertainty becomes `BLOCKED_UNKNOWN`.

---

## 17. Command step

The start specification freezes a Command catalog. Each route binds:

- route ID and purpose;
- resolved executable identity or resolution policy;
- fixed argv template;
- typed and bounded parameter schema;
- sanitized environment allowlist;
- maximum timeout;
- declared output contract;
- whether confirmed-timeout replay is allowed.

A Command step selects one route and supplies schema-valid named parameters. Planner cannot author free-form argv or shell strings.

Boundary:

1. materializes exact declared inputs into a fresh disposable command workspace;
2. renders explicit argv from the frozen template;
3. supplies only disposable paths and bounded scalar parameters;
4. launches without a shell using a sanitized environment;
5. streams stdout and stderr under frozen byte limits and persists complete logs when within limits, or bounded captured bytes plus explicit overflow and termination facts when a limit is exceeded;
6. accepts only declared outputs from the command workspace.

The target workspace is never the command working directory and no target-workspace write path is passed.

Commands are cooperative local inspection, compilation, test, or verification operations with no intended external side effects. STT does not claim containment against a hostile executable, independent host-path discovery, or network/external-resource side effects. Stronger host sandboxing is optional.

Command completion is fixed by the frozen route’s accepted exit codes and output contract. Unexpected or uncertain execution becomes `FAILED` or `BLOCKED_UNKNOWN`; it never mutates the target workspace through STT.

---

## 18. Mutation step

A Mutation step installs one exact replacement manifest produced by an earlier accepted Worker output.

The closed manifest has two sorted collections:

- `directories`: absent real directories to create, each with canonical path and desired supported mode bits;
- `files`: regular-file create, replace, or delete entries, each with exact admitted before-state and, for create/replace, replacement hash, byte size, and desired supported mode bits.

Directory replacement or deletion is unsupported. Missing parents may be created only through declared `directories` entries, ordered shallowest first, and every directory and file destination must be within exact write authority.

Before live change, Boundary:

1. validates sorted unique directory/file entries, canonical destinations, before-states, replacement bytes and modes, parent relationships, and exact write authority;
2. rejects `.git`, the Run store, symlinks, hard links, and special files;
3. persists the immutable Mutation request;
4. appends `STEP_STARTED`;
5. observes and verifies destination identities against the admitted before-state;
6. persists exact before-images or absence markers and exact replacement bytes;
7. re-observes every destination and verifies that it still matches the persisted before-state;
8. appends durable `MUTATION_INTENT` immediately before the first live write.

Then, immediately before each individual write or delete, deterministic code re-verifies that destination against the admitted state expected at that point. A mismatch stops further writes and leaves the post-intent step `BLOCKED_UNKNOWN`. Otherwise it installs each file atomically where supported, verifies final identities and modes, emits accepted Mutation output references, and appends `STEP_FINISHED`.

Before `MUTATION_INTENT`, deterministic preparation may resume. After `MUTATION_INTENT` without `STEP_FINISHED`, mutation is never replayed and no automatic rollback occurs. Boundary records current evidence, finishes the step `BLOCKED_UNKNOWN`, skips later steps, and proceeds to Validator.

The MVP makes no multi-file atomicity claim. Before-images remain directly referenced diagnostic evidence for manual recovery.

---

## 19. Task step and evidence refinement

A Task step declares:

- bounded child-mission text, an earlier accepted mission artifact, or the exact current Task mission;
- authority no broader than the parent;
- exact inputs;
- required outputs;
- the canonical child path.

Children inherit the parent’s frozen provider and Command bindings and Run limits. A Plan cannot broaden them.

Two semantic uses share the same step kind:

### Execution composition

Use a narrower child mission when a stable sub-mission benefits from its own Planner and Validator. The parent may continue after a `COMPLETE` child and consume its verified outputs.

### Evidence refinement

When the correct work cannot yet be determined but authorized evidence can be gathered, the parent may gather that evidence and create a child with the exact same mission and required-output contract plus the newly accepted evidence. The child receives a fresh Planner. The parent Planner does not predict the evidence result or preselect unsupported future work.

A same-mission child is normally the final substantive parent step. Finite Run limits prevent unbounded recursion.

Boundary persists the exact child request and appends the parent `STEP_STARTED` before child publication. The parent step remains unfinished until Boundary verifies the child terminal result, output names, artifact types, identities, provenance, and available validation report or exact Validator-unavailable evidence.

---

## 20. Provider operation contract

Core mechanical qualification uses a deterministic fake provider.

A useful live Run requires one supported semantic provider route, not every known adapter. Claude Code, Codex, or another recorded host are independently optional adapters. Neither may launch the other.

A claimed live adapter must establish before Run publication that it can provide:

- noninteractive bounded invocation;
- exact request persistence and complete raw-return persistence within frozen limits, with bounded captured bytes and explicit overflow facts otherwise;
- an explicit sanitized subprocess environment rather than wholesale ambient inheritance; secret values are never copied into `start-spec.json`, `run.json`, or attempt metadata;
- declared and minimized host credential/config access required by the provider CLI;
- observable local process identity and termination to the degree claimed;
- output-only semantic writes in the call directory;
- no semantic commands, connectors, or independent side-effect tools;
- truthful requested-versus-observed provider/model/effort reporting;
- disabled client-side retries where the provider exposes that control.

Unobservable remote or transport behavior is reported `UNKNOWN`.

### 20.1 Operation dispositions

Closed disposition vocabulary:

```text
PRELAUNCH_BLOCKED
ACCEPTED
COMPLETED_NONRETRIABLE
TIMED_OUT_CONFIRMED_TERMINATED
TERMINATION_UNKNOWN
```

Rules:

- `PRELAUNCH_BLOCKED` means no semantic or Command operation process was launched. It may represent unavailable route capability or deterministic request-input drift detected before launch. Bounded deterministic local capability probes may have run. It consumes no launched operation attempt. The current invocation stops and a later `stt run` may preflight again.
- `ACCEPTED` makes the validated output eligible for the matching ledger promotion; only that ledger event advances lifecycle state.
- `COMPLETED_NONRETRIABLE` is never dispatched again in the same Run.
- `TIMED_OUT_CONFIRMED_TERMINATED` may retry only while the finite launched-attempt limit remains.
- `TERMINATION_UNKNOWN` is never dispatched again.

Launched operations use monotonically numbered create-only attempt directories. Provider stdout, stderr, and raw return are streamed under frozen limits; overflow triggers bounded termination handling and can never be accepted as a complete semantic return. A prelaunch blocker is persisted in one bounded atomically replaced diagnostic status file outside the attempt sequence; it does not create an unbounded series of attempt directories. The attempt budget counts launched processes only.

Deterministic preparation and provider preflight occur before the lifecycle start event. Exactly one lifecycle start event is appended for the semantic or command operation immediately before its first launched attempt. A confirmed-terminated timeout retry uses the same immutable operation request and does not append another lifecycle start event.

Attempt dispositions are durable evidence, but only ledger events commit lifecycle outcomes. An accepted output that was not promoted by the matching ledger event is not adopted after restart. A crash after a start event is resolved from the latest complete attempt disposition under the rules in Section 25; STT never guesses that an unrecorded launch did not occur.

---

## 21. Planning failure and semantic failure

Planner returns exactly one of:

- a schema-valid Plan candidate;
- a schema-valid planning-failure result.

Planning failure uses:

```text
FAILED
→ available evidence establishes a material contradiction, prohibition,
  impossibility, or authority mismatch

BLOCKED_UNKNOWN
→ a material fact, capability, evidence item, authority, or trustworthy
  provider result is unavailable or uncertain
```

After a launched Planner operation:

- a schema-valid Planner failure keeps its declared `FAILED` or `BLOCKED_UNKNOWN` status;
- malformed, schema-invalid, dispatch-mismatched, or explicit completed provider failure becomes `FAILED`;
- exhausted confirmed-timeout attempts or termination/integrity uncertainty becomes `BLOCKED_UNKNOWN`.

Boundary persists `PLANNING_FAILED` and the Task proceeds to Validator; it does not remain permanently in `NEEDS_PLAN`.

For Worker or Command, a known completed semantic, schema, route, exit, or output failure becomes `FAILED`; identity, integrity, or termination uncertainty becomes `BLOCKED_UNKNOWN`. Boundary finishes the step, records later steps `SKIPPED`, and proceeds to Validator.

Only `PRELAUNCH_BLOCKED` leaves the current lifecycle operation unstarted and resumable.

---

## 22. Validator and terminal result

Before Validator, Boundary captures exact final identities for:

- every Mutation destination;
- every required workspace output reference;
- every additional live path explicitly requested by the accepted Plan for final judgment.

Validator receives a bounded final index referring to:

- mission, authority, and required outputs;
- accepted Plan or planning-failure evidence;
- every completed, failed, blocked, and skipped step result;
- verified child results and validation reports;
- selected command and mutation evidence;
- accepted artifacts and final workspace identities.

Validator returns one schema-valid result and one report:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
```

Terminal mission outputs may be selected only from accepted step outputs. The validation report is separate evidence.

If Validator is `PRELAUNCH_BLOCKED`, the Task remains resumable in `NEEDS_VALIDATION`. After `VALIDATOR_STARTED`, a confirmed-terminated timeout may repeat the same immutable Validator request while the launched-attempt limit remains. Any unusable or completed-failure return, exhausted timeout budget, or termination/integrity uncertainty then causes Boundary to finish mechanically:

```text
BLOCKED_UNKNOWN / VALIDATOR_UNAVAILABLE
```

This preserves evidence and guarantees visible closure without pretending the mission succeeded.

---

## 23. Boundary and Lead

Every substantive operation crosses one Boundary façade:

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

Boundary validates identity, authority, semantic-disclosure authorization, paths, references, route bindings, call eligibility, schemas, output provenance, and lifecycle transitions. It does not judge mission wisdom or semantic quality.

Lead carries only references and compact receipts. It does not carry Plans, source bodies, logs, patches, child histories, or model conversations.

Conceptual Lead algorithm:

```text
advance(task):
    validate Run, Task, ledger, runtime, and immutable bindings

    if no committed planning outcome:
        Boundary.plan_once_or_return_prelaunch_blocker(task)
        return

    if planning outcome is non-COMPLETE:
        Boundary.validate_once_or_return_prelaunch_blocker(task)
        return

    step = first Plan step without STEP_FINISHED

    if no step:
        Boundary.validate_once_or_return_prelaunch_blocker(task)
        return

    if an earlier step is non-COMPLETE:
        Boundary.record_later_steps_skipped(task)
        Boundary.validate_once_or_return_prelaunch_blocker(task)
        return

    Boundary.advance_step_once_or_resume_deterministic_state(task, step)
```

The outer loop stops on root terminal state, invalid state, operator interruption, or a visible prelaunch blocker.

---

## 24. Ledger and lifecycle authority

Each Task owns one append-only hash-chained JSONL ledger.

Event vocabulary is exactly:

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

Each start event binds the exact immutable request immediately before the operation’s first fallible launch or, for Mutation, before its live preparation phase. Confirmed-timeout retries do not append another start event.

Accepted artifacts remain in create-only operation directories. Ledger events promote them by canonical relative path, SHA-256, byte size, artifact type, producer, and authority. There is no second canonical copy whose publication can conflict with the ledger.

Current state is derived from the validated ledger and immutable referenced files. There is no mutable cursor.

One torn trailing ledger fragment may be preserved and removed under the Run writer lock after validating the complete prefix. Interior corruption, hash mismatch, sequence gaps, or conflicting immutable bindings make the Run invalid.

---

## 25. Crash and resume rules

```text
complete final Run directory without a root Task
→ frozen control may reverify bootstrap state and create the root Task

PLANNER_STARTED without PLAN_ACCEPTED or PLANNING_FAILED
→ if latest complete disposition is TIMED_OUT_CONFIRMED_TERMINATED and budget remains,
  repeat the same immutable request without another PLANNER_STARTED event
→ otherwise persist PLANNING_FAILED using the known completed-failure mapping,
  or BLOCKED_UNKNOWN when launch/completion/integrity is uncertain
→ proceed to Validator

STEP_STARTED for Worker or Command without STEP_FINISHED
→ if latest complete disposition is TIMED_OUT_CONFIRMED_TERMINATED, immutable inputs
  still verify, budget remains, and a Command route explicitly permits replay when
  applicable, repeat the same request without another STEP_STARTED event
→ otherwise finish from the known completed-failure mapping, or BLOCKED_UNKNOWN when
  launch/completion/integrity is uncertain
→ skip later steps and proceed to Validator

STEP_STARTED for Task without STEP_FINISHED
→ create or resume the exact canonical child when mechanically valid
→ otherwise finish BLOCKED_UNKNOWN

STEP_STARTED for Mutation without MUTATION_INTENT
→ resume deterministic preparation, including before-state verification
→ reverify destinations immediately before intent

MUTATION_INTENT without STEP_FINISHED
→ never replay mutation
→ finish BLOCKED_UNKNOWN

VALIDATOR_STARTED without TASK_FINISHED
→ if latest complete disposition is TIMED_OUT_CONFIRMED_TERMINATED and budget remains,
  repeat the same immutable request without another VALIDATOR_STARTED event
→ otherwise finish BLOCKED_UNKNOWN / VALIDATOR_UNAVAILABLE
```

An accepted semantic output not promoted by its matching ledger event is forensic evidence only and is never adopted after restart. Complete failure and timeout dispositions may still drive the mechanical mappings above; they never authorize semantic output promotion.

---

## 26. CLI

Canonical core surface:

```text
stt start --start-spec <path>
stt run --run-root <path>
stt status --run-root <path>
stt diagnose --run-root <path>
stt check-reachability
```

`start` validates and publishes one immutable Run. A conversational `STT:` host adapter may create the start specification, but the core lifecycle begins only from that persisted specification.

`run` reconstructs frozen control, acquires locks, validates state, completes interrupted bootstrap when safe, and advances deterministic state without changing bindings.

`status` and `diagnose` are read-only. `diagnose` reports invalid state and exact evidence paths; it never repairs automatically.

`check-reachability` fails if active STT imports or invokes archived or superseded lifecycle implementations.

There are no `retry`, `replan`, `reconcile`, `restore`, rollback, publication, or continuation commands. A future independent Run may consume selected prior results and reports as ordinary initial evidence.

---

## 27. Explicit non-goals

The MVP does not provide:

- concurrency, parallel Tasks, or distributed scheduling;
- a general workflow language;
- arbitrary provider or command plugins;
- hostile-provider or hostile-command containment;
- network or external-side-effect containment;
- automatic rollback or restoration;
- multi-file transactional mutation;
- automatic replanning, repair, or continuation Runs;
- Git staging, commits, pushes, merges, rebases, or publication;
- archived lifecycle compatibility;
- RunSkeptic, Fix Loop, Find Loop, or review ceremonies inside STT runtime;
- dynamic escalation to an unbound model;
- automatic adoption of orphan artifacts.

---

## 28. Qualification obligations

Promotion requires deterministic proof of these behaviors:

1. the core imports only the Python standard library, needs no Git/network/daemon for fake-provider operation, and completes plain-directory root success with one Planner, sequential steps, one Validator, and restart reconstruction;
2. root planning failure reaches Validator without an invented Plan;
3. Worker and Command failure or uncertainty record later steps `SKIPPED` and reach Validator;
4. Validator unavailable closes mechanically only after `VALIDATOR_STARTED`;
5. prelaunch provider unavailability is resumable and does not consume an attempt;
6. completed or uncertain calls are never repeated; confirmed terminated timeout retries only within the finite limit;
7. child and grandchild Tasks execute depth-first and every ancestor validates failure;
8. same-mission evidence refinement receives the exact mission, output contract, and newly accepted evidence within finite Run limits;
9. Command uses only a frozen route, rendered argv, sanitized environment, disposable inputs, and no target workspace path; semantic provider subprocesses likewise receive only their declared environment/config exposure;
10. Mutation verifies authority and before-state, persists before-images and `MUTATION_INTENT`, and never replays uncertainty;
11. object-open-time path admission rejects traversal, symlinks, hard links, special files, `.git`, and the active Run store;
12. atomic Run publication never exposes a partial authoritative final Run, and root or child Task publication never exposes an authoritative Task without `TASK_CREATED`;
13. ledger torn-tail handling is narrow and interior corruption fails closed;
14. workspace and Run locks reject simultaneous active writers;
15. frozen generation A survives target-workspace STT source modification or deletion and direct bundle resume works;
16. store-root selection works inside and outside the target workspace, with restrictive Run-data permissions or an explicit unsupported-host failure;
17. active STT has no runtime reachability to archived or superseded lifecycle code;
18. bounded context requests contain references and exact selected inputs, not broad histories; route-specific disclosure prevents unapproved transmission, and instruction-like evidence cannot expand control-bearing contracts;
19. required-output identity and provenance floors prevent false `COMPLETE`;
20. fake-provider qualification passes, and each adapter claimed as supported passes its own deterministic tests plus one explicitly authorized live smoke on its intended host before that host is declared deployable.

Tests may contain many assertions and fault injections. The documentation does not require an artificial scenario count or a scenario registry framework.

---

## 29. Open implementation parameters

These are implementation choices, not architecture decisions:

- conservative numeric limit defaults;
- exact supported lock backends and host matrix;
- exact provider-specific argv and tool-disabling flags;
- exact typed Command parameter vocabulary;
- module consolidation where responsibilities remain clear;
- human-readable CLI formatting.

Implementation must document and test the chosen values.

---

## 30. Authoritative statement

```text
STT is the low-dependency, last-resort runner.

It starts from one immutable specification, materializes exact evidence once,
freezes one standard-library-first runtime, and requires only one usable
semantic provider route.

STT has one recursive construct: Task. Every Task performs one Planner
operation, one immutable finite Plan or planning failure, sequential steps, and
one Validator path. Failure never bypasses ancestor validation.

Every substantive operation crosses deterministic Boundary. Semantic roles
receive only materialized inputs and write only call-owned outputs. Commands use
frozen routes in disposable workspaces. Only deterministic Mutation may change
the target workspace.

The Task ledger and immutable referenced artifacts determine state. Start events
bind fallible operations. Completed or uncertain operations are not repeated.
Prelaunch blockers remain resumable. Mutation uncertainty is never replayed.

A frozen Run resumes directly from its own bundle even after target-workspace STT
source changes or disappears. Git, containers, databases, daemons, rollback,
publication, and review ceremonies are not dependencies.

Inside its declared support envelope, STT either advances from persisted facts,
returns a visible resumable prelaunch blocker, or terminates with honest FAILED,
BLOCKED_UNKNOWN, or COMPLETE evidence. It never guesses success.
```
