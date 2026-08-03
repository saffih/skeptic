# STT MVP Implementation Plan

**Status:** Complete implementation plan for the corrected live-execution architecture
**Architecture source of truth:** `plans/stt-mvp-architecture-plan.md`
**Repository:** `saffih/skeptic`
**Documentation base:** `c3be467ec71924f63ea5bafa8f97908b594e8d15`
**Implementation authority:** STT MVP only

---

## 1. Objective

Implement the smallest complete STT described by the architecture plan.

The implementation must prove this lifecycle for the root Task and every child Task whose orchestration state remains valid:

```text
Mission
→ planning phase
→ immutable planning outcome
→ sequential ordered steps, when any
→ Validator
→ terminal result
```

Stop when the architecture qualification scenarios and the full repository suite pass.

Do not restore, adapt, or depend on the archived Target Task lifecycle.

---

## 2. Starting conditions

Before implementation:

1. verify the branch contains the final documentation commit installing both corrected plans;
2. record the architecture-plan SHA-256 in implementation evidence;
3. inspect the repository test conventions and only the direct files needed for integration;
4. preserve unrelated work;
5. leave `archive/` unchanged;
6. do not copy the old Target Task implementation wholesale;
7. implement from the current architecture, not historical summaries.

---

## 3. Build strategy

Build small vertical behavior slices.

Each slice must:

- implement one coherent runtime capability;
- add focused deterministic tests;
- preserve previously passing STT tests;
- avoid speculative abstractions;
- end with a reviewable commit;
- prove its declared invariant;
- remove unnecessary mechanism discovered during implementation.

Do not pre-create a large directory skeleton before behavior needs it.

---

## 4. Planned commit sequence

Recommended commits:

1. `stt: add canonical state and ledger core`
2. `stt: add task and planning contracts`
3. `stt: add copied run runtime`
4. `stt: add provider boundary`
5. `stt: add mechanical lead and recursive tasks`
6. `stt: add live workers commands and give-up handling`
7. `stt: add validation and prior-run evidence`
8. `stt: add cli and qualify mvp`

A commit may be split when review clarity improves. Do not combine unrelated slices.

---

## 5. Target production shape

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

CLI entry:

```text
scripts/stt.py
```

Tests:

```text
tests/concepts/stt/
```

The exact module count may be reduced when consolidation is simpler. Do not create a generic plugin framework, workflow engine, scheduler, or recovery subsystem.

Active STT must not import archived Target Task modules.

---

## 6. Cross-cutting rules

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
- supported OS filesystem locking.

Add no dependency unless it materially simplifies correctness and fits repository policy.

### 6.2 Canonical control data

Control-bearing JSON uses:

- UTF-8;
- sorted keys;
- stable compact separators;
- exactly one final LF;
- no NaN or Infinity;
- explicit schema identifiers;
- bounded sizes.

Provide one canonical serializer and parser.

### 6.3 Identity references

Persisted artifact references include, where applicable:

```text
relative or target-bound path
SHA-256
byte size
artifact type
producer identity
```

### 6.4 Publication

Immutable control files are create-only or atomically published through a same-directory temporary sibling, flushed, reread, and verified where supported.

Task creation publishes a complete same-parent temporary Task directory containing `TASK_CREATED` before the final rename.

Do not claim universal power-loss durability.

### 6.5 Errors

Use a small typed hierarchy, such as:

```text
STTError
InvalidRun
InvalidRuntime
InvalidTarget
InvalidTask
InvalidPlanningResult
InvalidPlan
InvalidLedger
ArtifactMismatch
ProviderFailure
OperationGaveUp
UnsettledOperation
```

Avoid a generalized error-state machine.

### 6.6 No hidden safety claim

Scope, path checks, and output verification do not imply process containment. Tests and documentation must use the architecture’s precise safety statement.

---

# Slice 1 — Canonical state, ledger, and writer lock

## 7. Goal

Implement:

- canonical JSON;
- artifact references;
- hash-chained Task ledger;
- create-only and atomic publication helpers;
- ledger validation;
- narrow torn-tail handling;
- one exclusive writer lock per Run;
- compact receipts.

## 8. Production files

Create:

```text
concepts/stt/ledger.py
concepts/stt/run_lock.py
concepts/stt/receipt.py
```

A small shared utility may be added only when it removes real duplication.

## 9. Ledger schema

Allowed events:

```text
TASK_CREATED
PLANNING_FINISHED
STEP_STARTED
STEP_FINISHED
TASK_FINISHED
```

Every line includes:

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

The event hash covers canonical event bytes without `event_hash`.

Reject:

- missing or non-contiguous sequence;
- duplicate sequence;
- unknown event;
- invalid previous hash;
- invalid event hash;
- oversized line;
- malformed interior JSON;
- lifecycle-illegal event order.

One incomplete trailing fragment may be preserved as diagnosis evidence and removed only under the exclusive writer lock after validating the complete prefix. Any other corruption fails visibly.

## 10. Writer lock

All lifecycle-changing `start` and `run` behavior holds one OS-backed exclusive lock on `<run-root>/run.lock`.

A competing writer fails before reading or changing lifecycle state.

Read-only status and diagnosis use a shared nonblocking lock where supported and return `RUN_BUSY` without reading changing state while a writer exists.

Do not implement leases, stale-lock recovery, distributed locking, or concurrent Task execution.

## 11. Tests

Prove:

- canonical round trip;
- equal objects produce equal bytes;
- one-byte changes alter identity;
- valid hash chain passes;
- historical modification fails;
- sequence gaps and duplicates fail;
- one torn tail is preserved and narrowly removed under lock;
- interior corruption fails;
- unsupported event fails;
- first writer acquires and second writer is rejected;
- compact receipt contains references rather than substantive bodies.

## 12. Commit acceptance

Focused Slice 1 tests pass.

Commit:

```text
stt: add canonical state and ledger core
```

---

# Slice 2 — Task and planning contracts

## 13. Goal

Implement:

- immutable Task identity;
- immutable mission;
- initial evidence and required-output binding;
- deterministic bounded workspace index;
- planning-result schema;
- `PLAN`, `DECLINE`, and `GAVE_UP` dispositions;
- exactly three step schemas;
- pure cursor derivation.

## 14. Production files

Create:

```text
concepts/stt/task.py
concepts/stt/plan.py
concepts/stt/workspace.py
concepts/stt/contracts/planner.md
```

## 15. Task creation

Implement one root-and-child creation path, conceptually:

```python
create_task(
    task_root,
    run_identity,
    task_identity,
    mission_bytes,
    authority,
    role_bindings,
    initial_inputs,
    required_outputs,
    parent_binding=None,
)
```

It must:

1. validate every input before publication;
2. build the complete initial Task under a same-parent temporary directory;
3. include `task.json`, `mission.md`, input bindings, required-output contract, workspace index, required directories, and the first valid ledger event;
4. flush, reread, and verify;
5. atomically publish only when the final deterministic path is absent;
6. reread and verify the published Task;
7. return a compact reference.

Temporary residue is non-authoritative and never adopted automatically.

## 16. Planning-result schema

Use one immutable `planning-result.json`.

### PLAN

Contains:

```text
disposition = PLAN
ordered steps
Planner reason or summary
```

A zero-step Plan is valid.

### DECLINE

Contains:

```text
disposition = DECLINE
reason
blocking facts
missing requirements
why further investigation or delegation is not useful
steps = []
```

### GAVE_UP

Boundary constructs this operational outcome from persisted attempt evidence:

```text
disposition = GAVE_UP
launch state
completion state
give-up reason
settlement state
log and raw-return references
steps = []
```

A malformed Planner return cannot become `PLAN` or `DECLINE`.

## 17. Step schemas

Implement explicit schemas for:

```text
WorkerStep
CommandStep
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

Worker fields:

```text
worker_binding
instructions
responsibility_scope
```

Command fields:

```text
argv
cwd
environment
give_up_policy
expected_result
```

Task fields:

```text
mission
authority
inputs
required child outputs
allowed child bindings
```

Do not add effect classification or automatic replay declarations.

## 18. Plan validation

Validate:

- schema and Task binding;
- disposition-specific fields;
- no steps for Decline or Gave Up;
- unique stable step IDs;
- only three step kinds;
- backward references only;
- named-output reference resolution;
- same or narrower child authority;
- valid allowed Worker binding;
- explicit command argv and cwd;
- canonical target references;
- immutable first accepted planning result.

Plan validation does not judge semantic wisdom or detect recursive non-progress.

## 19. Cursor derivation

Implement a pure function returning:

```text
NEEDS_PLANNING
NEEDS_STEP
NEEDS_VALIDATION
TERMINAL
INVALID
```

Rules:

- no planning result → `NEEDS_PLANNING`;
- Plan with first unfinished step → `NEEDS_STEP`;
- zero-step Plan, Decline, Gave Up, all steps complete, or any non-complete step → `NEEDS_VALIDATION`;
- committed terminal result → `TERMINAL`;
- conflicting identity or publication → `INVALID`.

There is no mutable cursor file.

## 20. Tests

Prove:

- root and child creation;
- bounded deterministic workspace index with explicit overflow markers;
- immutable mission and identity;
- child parent binding;
- byte-identical child mission accepted;
- equal or narrower child authority accepted;
- authority expansion rejected;
- valid Plan, Decline, and Gave Up;
- zero-step Plan accepted;
- steps rejected for Decline and Gave Up;
- unknown step kind rejected;
- future reference rejected;
- accepted planning result cannot be replaced;
- state derivation for every planning disposition and step state.

## 21. Commit acceptance

Slices 1 and 2 pass.

Commit:

```text
stt: add task and planning contracts
```

---

# Slice 3 — Copied Run runtime

## 22. Goal

Implement:

- unique temporary Run directory;
- owner-only permissions where supported;
- copied runnable Skeptic/STT checkout;
- copy manifest and verification;
- source-change-during-copy detection;
- re-execution from copied runtime;
- target/runtime disjointness;
- self-modification proof.

## 23. Production files

Create:

```text
concepts/stt/runtime.py
concepts/stt/bootstrap.py
```

## 24. Runtime copy

Implement conceptually:

```python
prepare_run_runtime(source_root, target_root, temp_root=None) -> RunRuntime
```

It must:

1. canonicalize source and target;
2. create `${TMPDIR}/stt/<run-id>/`;
3. reject a Run root inside the target;
4. copy the runnable repository into `runtime/`;
5. exclude `.git`, caches, previous Run state, and generated temporary files;
6. record source identities used for the copy;
7. record copied identities;
8. verify copied bytes;
9. re-observe source identities and reject mixed-generation copies;
10. write `runtime-manifest.json`;
11. re-execute from the copied entry point.

Copying the repository does not authorize importing archived runtime code. Active-import tests enforce that separately.

## 25. Bootstrap

`start` Bootstrap must:

- freeze submission bytes;
- bind source and target identities;
- validate optional prior Run;
- freeze provider and role bindings;
- prepare and re-execute the copied runtime;
- acquire the writer lock in the copied process;
- create immutable `run.json`;
- create the root Task;
- start the Lead;
- print the exact Run path and resume command.

No authoritative state is written under the target.

## 26. Resume

`run`, `status`, and `diagnose` execute from `<run-root>/runtime/`.

They never reconstruct executable code from the current source or target.

A missing Run directory is reported as non-resumable. Do not invent reconstruction from the modified source.

## 27. Tests

Prove:

- unique Run directories do not collide;
- Run root is outside target;
- expected exclusions are absent;
- copied manifest matches bytes;
- source change during copy fails visibly;
- imports resolve under copied runtime;
- target Skeptic source can be changed and deleted while generation A continues;
- a later generation B copies the changed source;
- missing Run directory is non-resumable;
- no authoritative target `.stt` state is created.

## 28. Commit acceptance

Runtime tests pass.

Commit:

```text
stt: add copied run runtime
```

---

# Slice 4 — Launcher, providers, and Boundary

## 29. Goal

Implement one mandatory Boundary façade around outer operations and one recorded launcher for providers and explicit commands.

## 30. Production files

Create:

```text
concepts/stt/launcher.py
concepts/stt/boundary.py
concepts/stt/providers/__init__.py
concepts/stt/providers/fake.py
concepts/stt/providers/claude_code.py
concepts/stt/providers/codex.py
```

## 31. Common outer-operation observations

Every launcher outcome records:

```text
dispatch identity
operation role
request identity
launch_state: NOT_LAUNCHED | LAUNCHED | UNKNOWN
completion_state: RETURNED | GAVE_UP
settlement_state: SETTLED | UNSETTLED | UNKNOWN
start and end timing
exit or provider status when available
stdout/stderr or raw-return references
adapter-specific observations
```

Adapter-internal bounded attempts may occur before returning the final outer outcome.

Do not expose a generic orchestration retry machine.

## 32. Provider protocol

Use the smallest interface:

```python
class Provider:
    def invoke(self, request: ProviderRequest) -> ProviderOutcome:
        ...
```

Requests contain:

```text
dispatch identity
role
requested provider/model/effort
fixed instruction references
bounded input references
output schema
give-up policy
```

Persist every raw return and launcher log.

Only schema-valid accepted semantic returns become Planner, Worker, or Validator results.

## 33. Fake provider

Support deterministic fixtures for:

- Planner Plan;
- Planner Decline;
- Planner malformed return leading to planning Gave Up;
- Worker complete report;
- Worker failed report;
- Worker give-up settled;
- Worker give-up unsettled;
- Validator Complete;
- Validator Failed;
- Validator Blocked Unknown;
- Validator give-up;
- dispatch mismatch;
- oversized return.

The fake provider is the primary qualification provider.

## 34. Live adapters

Claude Code and Codex adapters are thin translators over the common request and outcome contract.

They must:

- construct exact argv without shell interpretation;
- persist request and raw return;
- record truthful requested and observable actual routing;
- record `UNKNOWN` when actual routing is unobservable;
- enforce explicit live-provider authorization;
- enforce bounded output;
- classify launch, return, give-up, and settlement observations;
- perform no semantic interpretation beyond host-protocol translation.

Qualify them with controlled fake executables. No paid call is required.

## 35. Boundary API

Expose narrow methods, conceptually:

```text
finish_planning(task_ref)
execute_worker_step(task_ref, step_ref)
execute_command_step(task_ref, step_ref)
create_child_task(task_ref, step_ref)
finish_task_step_from_child(task_ref, step_ref, child_ref)
validate_and_finish_task(task_ref)
```

The Lead calls no provider, launcher, workspace, or persistence helper directly.

## 36. Boundary responsibilities

Boundary must:

- validate Run, runtime, target, Task, planning, and step identity;
- resolve declared input references;
- persist exact outer requests before launch;
- invoke adapters;
- preserve complete raw returns and logs;
- validate accepted semantic schemas;
- build planning Gave Up when required;
- verify named target outputs;
- create child Tasks;
- bind child returns;
- publish immutable accepted results;
- append lifecycle events;
- return compact receipts.

Boundary does not classify target changes as forbidden merely because they occurred.

## 37. Tests

Prove:

- every outer call has a unique dispatch identity;
- request identity binds return evidence;
- mismatched dispatch is rejected;
- raw returns persist;
- malformed Planner return becomes planning Gave Up, not Plan;
- oversized return is rejected and preserved as evidence;
- launch, completion, and settlement observations persist;
- named target outputs are verified by containment and identity;
- compact receipts contain no substantive body;
- live adapters require authorization;
- controlled Claude Code and Codex adapter tests pass.

## 38. Commit acceptance

Slices 1–4 pass.

Commit:

```text
stt: add provider boundary
```

---

# Slice 5 — Mechanical Lead and recursive Tasks

## 39. Goal

Implement one mechanical depth-first Lead and ordinary recursive Task execution.

## 40. Production file

Create:

```text
concepts/stt/lead.py
```

## 41. Lead algorithm

Conceptually:

```text
advance(task):
    validate task and ledger

    state = derive_task_state(task)

    if state == NEEDS_PLANNING:
        Boundary.finish_planning(task)
        return

    if state == NEEDS_STEP:
        step = first unfinished step

        if step.kind == task:
            child = Boundary.create_or_verify_child(task, step)

            if child is not terminal:
                advance(child)
                return

            Boundary.finish_task_step_from_child(task, step, child)
            return

        if step.kind == worker:
            Boundary.execute_worker_step(task, step)
            return

        if step.kind == command:
            Boundary.execute_command_step(task, step)
            return

    if state == NEEDS_VALIDATION:
        Boundary.validate_and_finish_task(task)
        return
```

The outer loop repeats until root terminal, invalid, or operationally blocked.

The Lead does not scan arbitrary Task directories or maintain a separate scheduler or stack file.

## 42. Child behavior

Prove these interruption cases:

```text
parent step started, child absent
→ create deterministic child

child created, parent unfinished
→ resume child

child terminal, parent unfinished
→ validate and finish parent step

parent step finished
→ continue parent

conflicting child identity
→ invalid Run
```

A byte-identical child mission is valid.

The Lead does not detect semantic recursion or impose depth limits.

## 43. Non-complete step behavior

After Worker, command, or child status `FAILED` or `GAVE_UP`:

- do not run later steps;
- derive `NEEDS_VALIDATION`;
- invoke the current Task Validator.

Every valid ancestor performs its own Validator after a non-complete child returns.

## 44. Tests

Prove:

- root Plan execution order;
- child and grandchild depth-first order;
- deterministic child paths;
- parent cursor remains on child until child terminal;
- later parent steps wait for child Complete;
- byte-identical child mission with richer inputs;
- no Task-depth guard;
- child Failed triggers parent and root Validators;
- child Gave Up triggers parent and root Validators;
- no scheduler or mutable stack file.

## 45. Commit acceptance

Recursive lifecycle tests pass.

Commit:

```text
stt: add mechanical lead and recursive tasks
```

---

# Slice 6 — Live Worker, command, and give-up handling

## 46. Goal

Implement live target execution without claiming containment or complete effect observation.

## 47. Production files

Extend/create:

```text
concepts/stt/workspace.py
concepts/stt/command.py
concepts/stt/contracts/worker.md
```

## 48. Worker invocation

Boundary constructs a bounded Worker request containing:

- one step;
- target root;
- exact inputs;
- responsibility scope;
- named outputs;
- fixed Worker contract;
- report schema;
- give-up policy.

A valid Worker report contains:

```text
status
summary
named outputs
best-effort created paths
best-effort changed paths
best-effort deleted paths
verification performed
warnings
unknowns
```

Boundary validates the report schema and verifies named outputs against the current target.

Do not attempt to prove the reported changed-path list is exhaustive.

## 49. Explicit command runner

The command runner must:

1. validate explicit argv;
2. resolve executable information where supported;
3. validate explicit cwd;
4. build a bounded environment;
5. persist the request before launch;
6. stream stdout and stderr to files;
7. apply the declared adapter give-up policy;
8. record launch, completion, settlement, exit, and timing observations;
9. record best-effort target before-and-after evidence;
10. verify declared named outputs;
11. never automatically repeat an abandoned command.

A target change does not automatically fail the step.

Do not create a complete-tree scan whose purpose is permission enforcement. Target observations are evidence for the Validator.

## 50. Give-up behavior

For Worker and command outer outcomes:

- `RETURNED` with local success → step `COMPLETE`;
- `RETURNED` with conclusive local failure → step `FAILED`;
- `GAVE_UP` → step `GAVE_UP`.

After `FAILED` or `GAVE_UP`, later steps stop and validation begins.

When settlement is `UNSETTLED` or `UNKNOWN`, persist that fact prominently. The Validator cannot produce Task Complete.

Same-Run resume never automatically re-invokes the step.

## 51. Scope implementation

Scope controls:

- context selection;
- responsibility wording;
- expected path reporting;
- named output validation;
- audit findings.

It does not claim to prevent arbitrary process access outside scope.

Tests must not assert sandbox behavior.

## 52. Tests

Prove:

- Worker creates, edits, moves, and deletes target files;
- Worker runs an internal command and reports it;
- named outputs are verified;
- omitted or incorrect named output fails local acceptance;
- changed-path report is persisted as evidence;
- command changes target and may still Complete;
- command nonzero exit may Fail according to declared local conditions;
- stdout and stderr are complete and file-backed;
- settled Worker give-up stops later steps;
- unsettled command give-up stops later steps and prevents Task Complete;
- same-Run resume does not replay abandoned work;
- plain-directory and Git-directory target observations both work;
- no target `.stt` orchestration state is written.

## 53. Commit acceptance

Live execution and give-up tests pass.

Commit:

```text
stt: add live workers commands and give-up handling
```

---

# Slice 7 — Validator and prior-Run evidence

## 54. Goal

Implement independent investigation, fact-based terminal judgment, reusable reports, and verified prior-Run evidence.

## 55. Production files

Extend/create:

```text
concepts/stt/boundary.py
concepts/stt/task.py
concepts/stt/contracts/validator.md
```

## 56. Final evidence index

Boundary creates a bounded Validator index referencing:

- mission;
- planning result;
- every step result;
- Worker reports;
- command logs;
- child results and reports;
- current target observations;
- required outputs;
- selected prior evidence;
- active or unsettled-operation facts.

Do not inline complete logs, child ledgers, or broad target bodies.

## 57. Validator return

Require:

```text
terminal status: COMPLETE | FAILED | BLOCKED_UNKNOWN
concise reason
material findings
unknowns
named terminal outputs
validation report
```

Boundary validates schema and verifies terminal outputs against current target or accepted Task artifacts.

## 58. Mechanical floors

Boundary overrides an attempted Validator Complete only when:

- orchestration state is invalid;
- an outer operation may still be active;
- a required terminal output is missing or unverifiable.

Do not force terminal status solely from an intermediate step status.

Tests must prove that Validator may independently establish Complete after a settled interrupted operation changed the target successfully.

## 59. Validator give-up

If the Validator adapter returns Gave Up without an accepted semantic result:

- preserve all evidence;
- do not append `TASK_FINISHED`;
- leave Task state `NEEDS_VALIDATION` with an operational blocker;
- do not silently retry on same-Run resume;
- allow a new Run to consume the evidence.

## 60. Prior-Run evidence

`start --prior-run` must:

1. validate the prior Run directory and runtime-independent evidence identities;
2. select verified prior references;
3. never merge ledgers or cursor state;
4. bind selected evidence into the new root Task;
5. allow the new Planner to decide whether to verify, continue, repair, replace, or decline.

Eligible prior references include:

- submission;
- planning result;
- terminal result;
- Validator report;
- selected step reports and logs;
- named outputs.

Uncommitted prior files may be labeled diagnostic evidence but never accepted facts.

## 61. Tests

Prove:

- normal Complete, Failed, and Blocked Unknown;
- Planner Decline still runs Validator;
- planning Gave Up still runs Validator;
- settled interrupted work may be independently validated Complete;
- insufficient interruption evidence becomes Blocked Unknown;
- intermediate Failed does not mechanically force Task Failed;
- unsettled operation rejects Validator Complete;
- missing required output rejects Validator Complete;
- Validator does not repair target in deterministic fixtures;
- Validator report reaches ancestor Validator evidence;
- new Run consumes verified prior Validator report;
- prior state is not merged;
- invalid prior reference is rejected;
- Validator give-up leaves operational Needs Validation.

## 62. Commit acceptance

Validation and prior-Run tests pass.

Commit:

```text
stt: add validation and prior-run evidence
```

---

# Slice 8 — CLI, diagnostics, qualification, and cleanup

## 63. Goal

Expose the complete MVP, prove the architecture, remove accidental complexity, and stop.

## 64. Production files

Create:

```text
concepts/stt/cli.py
scripts/stt.py
```

## 65. CLI

### Start

```text
stt start \
  --workspace <target-path> \
  --submission <submission-file> \
  --provider <provider> \
  [--model <model>] \
  [--effort <effort>] \
  [--prior-run <run-directory>]
```

Behavior:

1. validate source, target, submission, and optional prior Run;
2. freeze role and provider bindings;
3. prepare copied Run runtime;
4. re-execute from the copy;
5. acquire writer lock;
6. create `run.json` and root Task;
7. execute until root terminal, invalid, or operationally blocked;
8. print compact result, Run path, and resume command.

### Run

```text
stt run --run-root <run-directory>
```

Behavior:

- execute from copied runtime;
- acquire writer lock;
- validate identities and ledgers;
- resume without replanning or replaying abandoned work;
- print compact receipt.

### Status

```text
stt status --run-root <run-directory>
```

Report:

- Run and runtime identity;
- target identity;
- root state;
- deepest active Task;
- next action;
- give-up or invalid blocker;
- terminal result reference;
- exact resume command.

Remain read-only.

### Diagnose

```text
stt diagnose --run-root <run-directory>
```

Report:

- missing Run directory;
- copied-runtime corruption;
- target mismatch;
- ledger corruption;
- conflicting publication;
- planning or operation give-up;
- unsettled operation;
- Validator give-up;
- missing or mismatched artifact.

Never repair automatically.

## 66. Public exit codes

Use a small stable set, for example:

```text
0  COMPLETE or successful read-only query
2  FAILED
3  BLOCKED_UNKNOWN
4  OPERATIONALLY_BLOCKED
5  INVALID_RUN
6  USAGE_ERROR
```

Do not expose every internal exception as a distinct public code.

## 67. End-to-end qualification

Create a top-level qualification module that composes focused helpers rather than duplicating all assertions.

Prove at least:

1. root Worker success;
2. root command success that changes target;
3. Worker edits target and returns verified output;
4. target changes are not automatic command failure;
5. evidence gathering followed by byte-identical child mission;
6. child and grandchild depth-first order;
7. Planner Decline;
8. planning Gave Up and audit;
9. child failure validates every ancestor;
10. Worker give-up stops later steps;
11. unsettled command give-up prevents Task Complete;
12. settled interruption independently validates Complete;
13. insufficient evidence becomes Blocked Unknown;
14. same-Run resume preserves planning result;
15. new Run consumes prior Validator report;
16. generation A survives target Skeptic edits and deletion;
17. source copy race is detected;
18. deleted Run root is non-resumable;
19. competing writer is rejected;
20. torn tail is handled narrowly and interior corruption fails;
21. invalid publication never yields semantic success;
22. plain directory succeeds;
23. Git repository succeeds without Git lifecycle authority;
24. archived runtime imports are absent;
25. controlled provider-adapter tests pass;
26. full repository suite passes.

## 68. Static consistency checks

Fail qualification if active production STT contains obsolete architecture concepts or dependencies.

Check that:

- only `worker`, `command`, and `task` step kinds exist;
- no fourth target-change installation step exists;
- commands have no effect classification field;
- commands have no automatic replay declaration;
- Workers operate against the live target;
- Run state is outside the target;
- same-Run resume never replans;
- same-mission child delegation has no depth field;
- Validator terminal judgment is not mechanically copied from step status;
- active STT imports no archived Target Task package.

Comments explaining exclusions are allowed.

## 69. Context tests

Instrument fake provider requests and assert:

- Lead receipts remain compact;
- Planner receives only its bounded planning inputs;
- Worker receives one step and exact inputs;
- Validator receives a bounded evidence index;
- child ledgers are referenced rather than copied;
- command logs remain file-backed;
- prior Run evidence is selected rather than recursively loaded.

Use explicit configurable byte limits in tests.

## 70. Full repository checks

Run:

- focused STT suite;
- full repository suite;
- Python compile checks;
- repository formatting and lint checks already in use;
- shell syntax checks for scripts;
- `git diff --check`.

Do not introduce a new tool solely for this implementation unless required.

## 71. Complexity review

Before final acceptance, inspect:

- duplicated schema logic;
- duplicated lifecycle derivation;
- duplicated path and identity logic;
- unnecessary provider abstractions;
- hidden target containment claims;
- automatic replay paths;
- mutable cursors;
- dead compatibility code;
- broad exception catches;
- unbounded model context;
- hidden Git assumptions;
- unused modules.

Delete mechanisms not required by an architecture invariant or qualification.

## 72. Final commit

Commit:

```text
stt: add cli and qualify mvp
```

Stop after all qualification scenarios and the full repository suite pass.

---

## 73. Invariant-to-code map

| Architecture invariant | Primary code | Primary tests |
|---|---|---|
| one Task lifecycle | `task.py`, `lead.py` | lead and qualification tests |
| copied Run runtime | `runtime.py`, `bootstrap.py` | runtime and self-update tests |
| authoritative state outside target | Bootstrap and Task paths | runtime and CLI tests |
| immutable planning outcome | `plan.py`, `task.py` | planning tests |
| Plan, Decline, Gave Up | `plan.py`, `boundary.py` | planning and provider tests |
| three step kinds | `plan.py` | Plan-schema tests |
| same-mission recursion without cap | `lead.py`, `task.py` | recursive Task tests |
| every outer call through Boundary | `lead.py`, `boundary.py` | Boundary call-spy tests |
| live Worker execution | Boundary and Worker contract | Worker E2E tests |
| exact command execution | `command.py`, `launcher.py` | command tests |
| give-up stops later steps | Lead and Boundary | interruption tests |
| no automatic replay | Lead and cursor derivation | resume tests |
| fact-based Validator | Boundary and Validator contract | validation tests |
| unsettled operation blocks Complete | Boundary | validation-floor tests |
| Task-local ledger | `ledger.py`, `task.py` | ledger and recursion tests |
| deterministic child path | `task.py`, `lead.py` | child resume tests |
| compact context | `boundary.py`, `receipt.py` | context tests |
| new Run prior evidence | Bootstrap and Boundary | prior-Run tests |
| plain directory and Git optional | `workspace.py` | target comparison tests |
| one writer | `run_lock.py` | locking tests |
| no archive reachability | package imports | static reachability test |

---

## 74. Definition of done

The STT MVP is done when:

1. architecture and implementation match;
2. all implemented production modules are necessary;
3. all qualification scenarios pass;
4. focused STT tests pass;
5. full repository tests pass;
6. copied runtime self-update proof passes;
7. source-copy race detection passes;
8. plain-directory and Git-directory scenarios pass;
9. same-mission delegation and Planner Decline pass;
10. settled and unsettled give-up behavior pass;
11. same-Run resume never replans or replays abandoned work;
12. prior-Run evidence starts a distinct new lifecycle;
13. Validator may independently establish completion from facts;
14. unsettled execution cannot yield Complete;
15. no authoritative state is written under the target;
16. active STT imports no archived Target Task code;
17. no containment, rollback, or complete-effect-detection claim is made;
18. CLI start, run, status, and diagnose pass;
19. final diff contains no unexplained mechanism;
20. implementation stops.

---

## 75. Final execution instruction

```text
Implement only plans/stt-mvp-architecture-plan.md.

Use this implementation plan as the ordered build map.

Build small vertical slices. Add deterministic tests with each slice. Preserve
prior passing behavior. Remove unnecessary machinery before each commit.

Do not restore archived Target Task behavior. Do not add concurrency, rollback,
a scheduler, a workflow language, automatic Git publication, target sandboxing,
semantic recursion limits, dynamic Plan editing, or automatic replay of
abandoned work.

Stop when the focused qualification scenarios and the full repository suite
pass. Do not continue into later features.
```
