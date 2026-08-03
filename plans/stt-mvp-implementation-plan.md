# STT MVP Implementation Plan

**Status:** Complete implementation plan for the Round-and-Repeat architecture
**Architecture source of truth:** `plans/stt-mvp-architecture-plan.md`
**Repository:** `saffih/skeptic`
**Repository base:** `702b480dc55ef935970fd60031f80d4320e43ad8`
**Implementation authority:** STT MVP only

---

## 1. Objective

Implement the smallest complete STT described by the architecture plan.

The implementation must prove:

```text
Task mission
→ one immutable Round
→ Planner
→ immutable planning outcome
→ sequential ordered steps
→ Validator
→ FINISH or exceptional REPEAT
```

A later explicit caller invocation may run the same Task through one repeated Round after `REPEAT`.

Stop when focused STT qualification, static consistency checks, and the full repository suite pass.

Do not restore, adapt, or depend on archived Target Task behavior.

---

## 2. Starting conditions

Before implementation:

1. verify the branch contains the final architecture and implementation documents;
2. record both plan SHA-256 values;
3. inspect repository test conventions and only direct integration files;
4. preserve unrelated work;
5. leave `archive/` unchanged;
6. do not copy archived Target Task implementation wholesale;
7. implement from the current architecture, not conversation history;
8. fail if either plan still contains superseded lifecycle contracts.

---

## 3. Build strategy

Build vertical behavior slices.

Each slice must:

- implement one coherent runtime capability;
- include focused deterministic tests;
- preserve prior passing behavior;
- use the smallest sufficient abstraction;
- end in a reviewable commit;
- prove its declared invariant;
- remove mechanism not required by an architecture invariant.

Do not pre-create a large framework skeleton. Consolidate modules when simpler.

---

## 4. Recommended commit sequence

1. `stt: add canonical state artifact and ledger core`
2. `stt: add frozen runtime and bootstrap handoff`
3. `stt: add task round and planning contracts`
4. `stt: add call boundary and provider adapters`
5. `stt: add live worker and command steps`
6. `stt: add mechanical lead and distinct child tasks`
7. `stt: add validator finish and repeat`
8. `stt: add prior evidence cli and diagnostics`
9. `stt: qualify round and repeat mvp`

A commit may be split only when review clarity improves.

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
├── round.py
├── ledger.py
├── plan.py
├── boundary.py
├── launcher.py
├── workspace.py
├── command.py
├── artifact.py
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

The exact module count may be reduced when consolidation is simpler. Do not add a generic plugin framework, scheduler, workflow engine, expression evaluator, recovery subsystem, or semantic progress engine.

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
- supported OS locking.

Add no dependency unless it materially simplifies correctness and fits repository policy.

### 6.2 Canonical control data

Control JSON uses:

- UTF-8;
- sorted keys;
- stable compact separators;
- exactly one final LF;
- no NaN or Infinity;
- explicit schema identifiers;
- bounded sizes.

Provide one canonical serializer/parser.

### 6.3 Publication

Immutable control files are create-only or atomically published through a same-directory temporary sibling, flushed, reread, and verified where supported.

Task and Round creation build complete same-parent temporary directories before final atomic publication.

Do not claim universal power-loss durability.

### 6.4 Small error hierarchy

Use a narrow typed hierarchy such as:

```text
STTError
InvalidRun
InvalidRuntime
InvalidTarget
InvalidTask
InvalidRound
InvalidPlanningOutcome
InvalidPlan
InvalidLedger
ArtifactMismatch
ProviderFailure
NoAcceptedReturn
UnsettledOperation
OperationallyBlocked
NonResumableRun
```

Do not create a generalized state-machine exception hierarchy.

### 6.5 No hidden containment claim

Path checks, scopes, reports, and ArtifactRefs are evidence and orchestration protections, not process containment.

---

# Slice 1 — Canonical state, ArtifactRef, ledger, and writer lock

## 7. Goal

Implement:

- canonical JSON;
- ArtifactRef;
- create-only and atomic publication helpers;
- hash-chained Task ledger;
- ledger validation;
- narrow torn-tail handling;
- one exclusive writer lock per Run;
- compact receipts.

## 8. Production files

Create or consolidate:

```text
concepts/stt/artifact.py
concepts/stt/ledger.py
concepts/stt/run_lock.py
concepts/stt/receipt.py
```

## 9. ArtifactRef

Schema:

```text
name
location: TARGET | RUN
relative_path
sha256
byte_size
artifact_type
normalized_mode
producer_identity
```

Implement:

- target containment with no symlink component;
- regular-file requirement;
- current size and SHA-256 verification;
- normalized executable-mode verification where supported;
- Boundary-owned create-only Run artifacts;
- revalidation before every consumption boundary;
- post-call revalidation for Run artifacts exposed to a Worker or command.

Reject directories, symlinks, sockets, devices, and special files as named artifacts.

Provide a Boundary helper that captures verified non-file observations—such as path absence, deletion, exit behavior, or target metadata—as canonical create-only Run ArtifactRefs. The observation may be prepared before Validator invocation or accepted from a bounded read-only Validator investigation, but it must exist and verify before `REPEAT` is accepted. Validator prose is never substituted for such evidence.

## 10. Ledger

Allowed events:

```text
TASK_CREATED
ROUND_CREATED
PLANNING_FINISHED
STEP_STARTED
STEP_FINISHED
ROUND_FINISHED
TASK_FINISHED
```

Each event includes canonical sequence, previous hash, and event hash.

Reject:

- missing or duplicate sequence;
- unknown event;
- invalid previous or event hash;
- oversized line;
- malformed interior JSON;
- lifecycle-illegal event order.

A single incomplete trailing fragment may be preserved for diagnosis and removed only under exclusive writer lock after validating the complete prefix.

## 11. Writer lock

All lifecycle-changing `start` and `run` behavior holds one OS-backed exclusive lock.

Competing writers fail before lifecycle mutation.

Read-only status and diagnosis use a nonblocking read strategy and return `RUN_BUSY` rather than reading changing state when a writer is active.

Do not implement leases, stale-lock recovery, distributed locking, or concurrency.

## 12. Tests

Prove:

- canonical round trip;
- one-byte identity changes;
- target ArtifactRef containment and symlink rejection;
- Run artifact create-only publication;
- artifact mutation detected before consumption;
- valid ledger chain;
- historical mutation, gaps, duplicates, and interior corruption fail;
- one torn tail is handled narrowly;
- first writer succeeds and competing writer fails;
- compact receipt contains references rather than substantive bodies.

---

# Slice 2 — Frozen runtime, Bootstrap handoff, routing, and Run identity

## 13. Goal

Implement:

- unique disjoint Run root;
- owner-only permissions where supported;
- minimal copied runtime;
- runtime manifest;
- source-change-during-copy detection;
- immutable Bootstrap handoff;
- frozen routing;
- re-execution from copied runtime;
- immutable `run.json`.

## 14. Production files

```text
concepts/stt/runtime.py
concepts/stt/bootstrap.py
```

## 15. Runtime copy

Conceptual API:

```python
prepare_run_runtime(source_root, target_root, temp_root=None) -> RunRuntime
```

It must:

1. canonicalize source and target;
2. create `${TMPDIR}/stt/<run-id>/`;
3. reject Run root inside source or target;
4. copy only active STT runtime files;
5. reject symlinks and special files;
6. exclude `.git`, caches, bytecode, previous Run state, and temporary files;
7. preserve regular-file bytes and normalized executable mode;
8. record manifest path, size, SHA-256, and mode;
9. verify copied files;
10. re-observe source and reject mixed generations;
11. re-execute from copied `scripts/stt.py`.

Active-import tests reject archive and unrelated-package reachability.

## 16. Bootstrap handoff

Before re-execution publish:

```text
bootstrap/request.json
bootstrap/submission.md
bootstrap/routing.json
```

Bind:

- frozen submission;
- source and target identities;
- routing identity;
- live-provider authorization;
- optional prior Run;
- runtime manifest.

The copied runtime never rereads original mutable submission or routing files.

## 17. Routing

`routing.json` binds:

- one Planner route;
- named allowed Worker routes;
- one Validator route;
- provider, model, effort, and adapter for each.

Changing routing creates a new Run.

Fake-provider tests do not require live authorization.

## 18. Tests

Prove:

- Run root outside source and target;
- owner-only creation where supported;
- runtime symlink and special-file rejection;
- expected exclusions;
- manifest byte and mode verification;
- source copy race rejection;
- imports resolve under copied runtime;
- generation A survives target source edits/deletion;
- generation B sees later source;
- immutable Bootstrap handoff;
- mutable original submission/routing are not reread;
- no target `.stt` state.

---

# Slice 3 — Task, Round, workspace index, and planning contracts

## 19. Goal

Implement:

- immutable Task identity and mission;
- deterministic child binding;
- immutable Round identity;
- fresh bounded workspace index per Round;
- durable Planner call outcome;
- semantic `PLAN` and `DECLINE`;
- `EXECUTE` and `INVESTIGATE`;
- exactly three step kinds;
- pure lifecycle derivation.

## 20. Production files

```text
concepts/stt/task.py
concepts/stt/round.py
concepts/stt/plan.py
concepts/stt/workspace.py
concepts/stt/contracts/planner.md
```

## 21. Task creation

Conceptually:

```python
create_task(
    task_root,
    run_identity,
    mission_bytes,
    authority,
    role_bindings,
    initial_evidence,
    required_outputs,
    parent_binding=None,
)
```

Validate all inputs, build complete initial Task in a temporary sibling, append `TASK_CREATED`, flush/reread/verify, atomically publish, then verify published identity.

Reject a child mission whose hash equals any ancestor mission.

## 22. Round creation

Conceptually:

```python
create_round(
    task_ref,
    round_number,
    selected_evidence,
    predecessor_round=None,
)
```

It must:

- preserve exact Task mission;
- bind current target identity;
- build a fresh bounded workspace index;
- bind predecessor Validator report as advisory evidence when repeating;
- bind exact selected ArtifactRefs;
- append `ROUND_CREATED`;
- publish atomically;
- prevent gaps and duplicates;
- permit Round 0 for newly created Tasks;
- permit at most one Round numbered greater than zero from a pre-existing repeat transition per invocation.

## 23. Workspace index

Use deterministic `lstat` observations.

Never follow symlinks.

Record regular files, directories, and symlink metadata. Do not read bodies only to index. Emit deterministic overflow markers.

## 24. Planner persistence

Every Planner phase publishes:

```text
planning/request.json
planning/launch.json
planning/raw-return.txt
planning/outcome.json
```

`outcome.json` records call state, returned result kind, settlement, logs, and evidence.

Only an accepted `OK(PLAN|DECLINE)` creates `planning-result.json`.

This prevents same-Run resume from calling Planner again after a durable settled call error or accepted semantic value.

## 25. PLAN

Schema includes:

```text
disposition = PLAN
intent = EXECUTE | INVESTIGATE
summary
steps
```

`INVESTIGATE` additionally requires:

```text
decision_critical_unknown
why_it_blocks_full_plan
bounded_probe
expected_evidence_outputs
```

A zero-step Plan is valid.

## 26. DECLINE

Requires:

```text
disposition = DECLINE
reason
blocking_facts
missing_requirements
why_execution_is_not_credible
why_investigation_or_repeat_is_not_useful
steps = []
```

## 27. Step schemas

Exactly:

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
```

Worker fields:

```text
worker_route
instructions
responsibility_scope
```

Command fields:

```text
argv
cwd
accepted_exit_codes
env_overrides
inherited_env_names
wait_policy
inputs
required_outputs
```

Task fields:

```text
mission
authority
inputs
required_child_outputs
allowed_child_worker_routes
```

No generic success expression.

## 28. State derivation

Implement a pure function deriving:

```text
NEEDS_ROUND
NEEDS_PLANNING
NEEDS_STEP
NEEDS_VALIDATION
AWAITING_REPEAT
TERMINAL
OPERATIONALLY_BLOCKED
INVALID
```

Important rules:

- no Round and Task active → `NEEDS_ROUND`;
- durable Planner outcome without semantic Plan/Decline → `NEEDS_VALIDATION`;
- first unfinished eligible step → `NEEDS_STEP`;
- any non-satisfied step → `NEEDS_VALIDATION`;
- accepted Validator `REPEAT` → `AWAITING_REPEAT`;
- accepted Validator `FINISH` + Task result → `TERMINAL`;
- Planner, Worker, or command has `UNSETTLED | UNKNOWN` settlement → `OPERATIONALLY_BLOCKED`;
- Validator has no accepted semantic return → `OPERATIONALLY_BLOCKED`;
- conflicting identity/publication → `INVALID`.

`OPERATIONALLY_BLOCKED` and `INVALID` are same-Run stopping states. A later `stt run` reports the blocker and performs no semantic lifecycle action.

There is no mutable cursor file.

## 29. Tests

Prove:

- root and distinct child Task creation;
- ancestor-equal child mission rejected;
- Round 0 and later deterministic publication;
- no Round gaps or duplicates;
- fresh workspace index each Round;
- valid EXECUTE, INVESTIGATE, Decline, zero-step Plan;
- missing investigative rationale rejected;
- unknown step kind and future reference rejected;
- command generic success field rejected;
- accepted planning result immutable;
- durable Planner call error does not trigger automatic Planner reinvocation;
- all derived states.

---

# Slice 4 — Launcher, call mechanics, providers, and Boundary

## 30. Goal

Implement one mandatory Boundary façade and truthful common call mechanics.

## 31. Production files

```text
concepts/stt/launcher.py
concepts/stt/boundary.py
concepts/stt/providers/__init__.py
concepts/stt/providers/fake.py
concepts/stt/providers/claude_code.py
concepts/stt/providers/codex.py
```

## 32. Common call outcome

Record:

```text
dispatch_identity
role
request_identity
call_state: NOT_STARTED | RETURNED | NO_RETURN
result_kind: OK | ERR | NONE
settlement_state: SETTLED | UNSETTLED | UNKNOWN
start/end timing
native exit/provider status
stdout/stderr/raw-return refs
truncated flags
adapter observations
```

A completed error is `RETURNED + ERR`. Missing accepted return is `NO_RETURN`.

Before launch, publish a create-only launch marker bound to request identity.

## 33. Provider protocol

Use the smallest interface:

```python
class Provider:
    def invoke(self, request: ProviderRequest) -> ProviderCallOutcome:
        ...
```

Persist exact request, launch marker, raw return, logs, and outcome.

Only schema-valid accepted role values become Planner, Worker, or Validator semantic results.

Do not expose a generic orchestration retry machine.

## 34. Bounded capture

Apply explicit byte limits to raw return, stdout, stderr, reports, and returned Run artifacts.

On limit:

- preserve prefix;
- set `truncated = true`;
- reject semantic return;
- attempt bounded termination;
- record settlement.

## 35. Fake provider

Support deterministic fixtures for:

- Planner EXECUTE;
- Planner INVESTIGATE;
- Planner Decline;
- Planner `ERR`;
- Planner `NO_RETURN`;
- Worker satisfied/not-satisfied/indeterminate;
- Validator all valid judgment/disposition pairs;
- invalid `SATISFIED + REPEAT`;
- repeat without artifacts;
- far failure finishing;
- hard blocker finishing;
- Validator `ERR` and `NO_RETURN`;
- dispatch mismatch;
- oversized/truncated return.

## 36. Live adapters

Claude Code and Codex adapters are thin translators.

They must:

- build exact argv without shell interpretation;
- persist request and raw return;
- truthfully record requested and observable actual routing;
- use `UNKNOWN` when actual routing is unobservable;
- require explicit live authorization;
- enforce bounded output;
- record call and settlement observations;
- perform no semantic interpretation beyond host translation.

Qualify with controlled fake executables. No paid call required.

## 37. Boundary API

Conceptually:

```text
create_round(task_ref)
finish_planning(round_ref)
execute_worker_step(round_ref, step_ref)
execute_command_step(round_ref, step_ref)
create_child_task(round_ref, step_ref)
finish_task_step_from_child(round_ref, step_ref, child_ref)
validate_round(round_ref)
finish_task(task_ref, round_ref)
```

Lead calls no provider, launcher, workspace, or persistence helper directly.

## 38. Tests

Prove:

- unique dispatch identity;
- request-return binding;
- launch marker precedes call;
- mismatched dispatch rejected;
- completed error differs from no return;
- malformed/oversized return becomes no accepted return;
- settlement recorded;
- live authorization enforced;
- controlled adapters pass;
- compact receipts contain references only.

---

# Slice 5 — Live Worker and command steps

## 39. Goal

Implement live target execution without claiming containment or complete effect detection.

## 40. Production files

```text
concepts/stt/command.py
concepts/stt/contracts/worker.md
```

Extend workspace and Boundary modules as needed.

## 41. Worker invocation

Boundary supplies:

- one step;
- target root;
- exact verified inputs;
- scope and responsibility;
- allowed route;
- required outputs;
- fixed Worker contract;
- bounded report schema.

Valid Worker value contains:

```text
judgment
summary
named ArtifactRefs
best-effort created/changed/deleted paths
verification
warnings
unknowns
```

Boundary verifies named outputs. It does not prove changed-path reporting exhaustive.

## 42. Command runner

The command runner must:

1. validate explicit argv and cwd;
2. reject shell interpretation by default;
3. resolve executable observation where supported;
4. construct minimal environment from explicit values and inherited names;
5. persist request and launch marker;
6. stream bounded stdout/stderr to Run artifacts;
7. apply bounded wait and termination policy;
8. record call, settlement, exit, timing, and truncation;
9. verify declared outputs;
10. never automatically repeat a command that may have launched.

Local command judgment:

```text
accepted exit code + required outputs verify
→ SATISFIED

returned unaccepted exit code
or required output conclusively missing/mismatched
→ NOT_SATISFIED

no accepted return
or output identity cannot be observed stably
→ INDETERMINATE
```

## 43. Environment

Implement:

```text
env_overrides
inherited_env_names
```

Do not persist inherited values.

Reject credentials in explicit persisted environment or routing fixtures.

Document that arbitrary commands may still disclose secrets.

## 44. Tests

Prove:

- Worker creates/edits/moves/deletes target files;
- named outputs verified;
- changed-path report persisted as evidence;
- accepted nonzero command exit may satisfy;
- unaccepted exit is not satisfied;
- target changes are not automatic failure;
- bounded stdout/stderr;
- truncation prevents semantic acceptance;
- settled no-return stops later steps and reaches Validator;
- unsettled or unknown operation becomes operationally blocked before Validator;
- no automatic command replay;
- plain and Git directory targets;
- no target `.stt` state.

---

# Slice 6 — Mechanical Lead and distinct child Tasks

## 45. Goal

Implement deterministic depth-first execution with one-new-Round-per-invocation discipline.

## 46. Production file

```text
concepts/stt/lead.py
```

## 47. Invocation token

At the start of each `start` or `run`, validate the root Task tree and identify the deepest active Task.

Capture whether that Task already had state `AWAITING_REPEAT`.

Only that pre-existing deepest-Task state may authorize creation of one repeated Round numbered greater than zero. The repeat allowance is global to the CLI invocation, not one allowance per Task.

Creation of Round 0 for a newly created root or child Task is allowed and does not consume the repeat allowance.

A `REPEAT` produced by any root or child Task during the current invocation stops the entire invocation and cannot be consumed immediately.

## 48. Lead algorithm

Conceptually:

```text
advance(root_task, invocation_context):
    validate root-to-deepest Task path and ledgers
    task = deepest active Task

    if task was AWAITING_REPEAT at invocation start
       and invocation has not consumed a repeat transition:
        Boundary.create_repeated_round(task)
        mark invocation consumed one repeat transition globally

    state = derive_task_state(task)

    if state == NEEDS_ROUND:
        Boundary.create_initial_round(task)
        return

    if state == NEEDS_PLANNING:
        Boundary.finish_planning(current_round)
        return

    if state == NEEDS_STEP:
        step = first eligible unfinished step

        if task step:
            create or verify distinct child
            descend until child usable result
            bind parent step
            return

        if worker:
            execute once
            return

        if command:
            execute once
            return

    if state == NEEDS_VALIDATION:
        Boundary.validate_round(current_round)
        return

    if state == AWAITING_REPEAT:
        stop current invocation
        return

    if state == TERMINAL | OPERATIONALLY_BLOCKED | INVALID:
        stop
```

The outer mechanical loop may continue within the current Round until the Round finishes, but it must not cross a newly produced `REPEAT`.

## 49. Child behavior

Prove:

```text
parent step started, child absent
→ create deterministic distinct child

child active
→ resume child depth-first

child SATISFIED / NOT_SATISFIED / INDETERMINATE
→ map directly to parent local judgment

child Validator fails after all child operations settled
→ parent local judgment INDETERMINATE with child evidence
→ parent Validator may audit

child has UNSETTLED or UNKNOWN operation
→ entire Run OPERATIONALLY_BLOCKED

conflicting child identity
→ INVALID
```

Same-ancestor mission is rejected.

No scheduler or mutable stack file.

## 50. Tests

Prove:

- root step order;
- child and grandchild depth-first order;
- deterministic child path;
- exact ancestor-mission child rejection;
- distinct narrower child accepted;
- later parent steps wait for child satisfaction;
- child negative/indeterminate result invokes parent Validator;
- settled child Validator failure yields an indeterminate parent step without fabricating child terminal judgment;
- unsettled child operation blocks the whole Run before ancestor validation;
- one invocation consumes no more than one pre-existing repeat transition across the root Task tree;
- newly created child Tasks may each create Round 0 without consuming that repeat allowance;
- a newly produced root or child repeat stops the entire invocation;
- a pre-existing deepest child awaiting-repeat may create exactly one child Round;
- pre-existing root awaiting-repeat creates exactly one root Round;
- no scheduler or stack file.

---

# Slice 7 — Validator, FINISH, and exceptional REPEAT

## 51. Goal

Implement independent fact-based validation, explicit finishing, and tightly guarded Task repetition.

## 52. Production files

```text
concepts/stt/contracts/validator.md
```

Extend `boundary.py`, `task.py`, and `round.py`.

## 53. Validator evidence index

Boundary creates a bounded index referencing:

- Task mission;
- Round identity;
- Planner call outcome;
- Plan or Decline;
- every step result;
- Worker reports;
- command logs;
- child results;
- current target observations;
- required outputs;
- selected prior evidence;
- active/unsettled facts.

Do not inline complete logs, child ledgers, or broad target bodies.

## 54. Validator semantic return

Require:

```text
judgment: SATISFIED | NOT_SATISFIED | INDETERMINATE
disposition: FINISH | REPEAT
reason
material_findings
unknowns
named_terminal_outputs
validation_report
```

For `REPEAT`, additionally require:

```text
verified_progress
remaining_gap
selected_repeat_artifact_refs
why_fresh_planning_has_better_basis
known_hard_blockers = []
```

## 55. REPEAT mechanical floors

Boundary does not launch semantic validation while a relevant outer operation is unsettled or has unknown settlement. That state is operationally blocked.

For a semantically processable settled Round, Boundary rejects repeat unless:

- judgment is not satisfied;
- all relevant operations are settled;
- orchestration state is valid;
- at least one selected new `RUN` ArtifactRef was produced in this Round;
- referenced artifacts verify;
- required fields are nonempty;
- Planner/Validator prose is not the only evidence;
- prior Plan or operation is not requested for replay;
- no declared hard blocker remains.

Boundary does not implement a semantic novelty algorithm.

## 56. Semantic qualification behavior

Fake-provider and end-to-end fixtures must prove the intended distinction:

```text
materially closer + credible better Planner basis
→ REPEAT

far from mission
→ FINISH + NOT_SATISFIED

hard authority/dependency blocker
→ FINISH + NOT_SATISFIED

uncertainty not credibly resolvable by another Round
→ FINISH + INDETERMINATE
```

`REPEAT` remains exceptional.

## 57. Validator operational failure

If Validator call returns `ERR`, `NO_RETURN`, or `NOT_STARTED`:

- preserve all evidence;
- do not append `ROUND_FINISHED`;
- do not append `TASK_FINISHED`;
- do not fabricate repeat;
- derive `OPERATIONALLY_BLOCKED`.

## 58. Round and Task publication

On accepted Validator return:

- publish immutable Round `result.json`;
- append `ROUND_FINISHED`.

If disposition is `REPEAT`:

- verify selected repeat artifacts;
- do not append `TASK_FINISHED`;
- derive `AWAITING_REPEAT`;
- return a compact caller action.

If disposition is `FINISH`:

- verify terminal outputs;
- publish Task `result.json`;
- append `TASK_FINISHED`;
- derive `TERMINAL`.

## 59. Tests

Prove:

- all valid judgment/disposition pairs;
- `SATISFIED + REPEAT` rejected;
- repeat with no new artifact rejected;
- repeat with unsettled operation rejected;
- repeat with prior artifact but no current-Round producer rejected;
- repeat selecting a live TARGET ArtifactRef instead of a frozen RUN ArtifactRef rejected;
- far failure finishes;
- hard blocker finishes;
- investigate may incidentally finish satisfied;
- execute may partially progress and repeat;
- Planner Decline may finish;
- Planner call error proceeds to Validator;
- Validator operational failure blocks without semantic fabrication;
- terminal outputs verified;
- only frozen current-Round `RUN` repeat artifacts are supplied to the next Planner;
- live target reality is supplied separately by the fresh workspace index;
- next Planner may Decline.

---

# Slice 8 — Prior evidence, CLI, status, diagnosis, and crash handling

## 60. Goal

Expose the lifecycle and preserve honest resume boundaries.

## 61. Production files

```text
concepts/stt/cli.py
scripts/stt.py
```

## 62. Start

```text
stt start \
  --workspace <target> \
  --submission <file> \
  --routing-file <file> \
  [--prior-run <run-root>] \
  [--allow-live-provider]
```

Behavior:

1. validate source, target, submission, routing, prior Run;
2. prepare copied runtime and Bootstrap handoff;
3. re-execute from copy;
4. acquire writer lock;
5. publish `run.json` and root Task;
6. create Round 0;
7. execute until Round FINISH, Round REPEAT, operational block, or invalid state;
8. print compact result, Run root, and exact next caller command.

## 63. Run

```text
stt run --run-root <run-root>
```

Behavior:

- execute from copied runtime;
- acquire writer lock;
- validate identities and ledgers;
- capture the invocation-start deepest active Task and state;
- resume unfinished current-Round work when safe;
- otherwise create exactly one repeated Round for the pre-existing deepest `AWAITING_REPEAT` Task;
- allow initial Round 0 creation for newly created Tasks without counting it as repetition;
- never replan an accepted current Round;
- never replay possibly launched work;
- stop at newly produced repeat, terminal, operational block, or invalid state;
- refuse further lifecycle action when the invocation begins operationally blocked or invalid.

## 64. Status

Read-only. Report:

- Run/runtime/target identity;
- root and deepest active Task;
- current Round;
- state;
- next action;
- repeat count;
- blocker;
- semantic result reference;
- exact command the caller may run.

Do not infer readiness from repeat count.

## 65. Diagnose

Read-only. Report:

- missing Run root;
- runtime corruption;
- target mismatch;
- ledger corruption;
- conflicting publication;
- ambiguous launch marker;
- unsettled operation;
- Planner or Validator call failure;
- artifact mismatch;
- operationally blocked or non-resumable state.

Never repair automatically.

## 66. Process crash

Before each outer launch, persist marker.

On restart:

```text
no marker
→ safe to resume before launch

marker + committed accepted outcome
→ safe to resume after outcome

marker without committed outcome
→ non-resumable Run

result file without committing ledger event
→ conflicting publication and non-resumable
```

A committed repeat remains safely resumable as `AWAITING_REPEAT`.

Recovery from non-resumable state is a new Run with current target reality and optional verified prior evidence.

## 67. Prior Run

`--prior-run` validates and selects exact evidence references.

Never merge ledgers, Rounds, cursors, or lifecycle state.

Uncommitted files may be diagnostic evidence only.

## 68. Exit codes

Use a small stable set, for example:

```text
0  SATISFIED or successful read-only query
2  NOT_SATISFIED
3  INDETERMINATE
4  AWAITING_REPEAT
5  OPERATIONALLY_BLOCKED
6  INVALID_OR_NONRESUMABLE_RUN
7  USAGE_ERROR
```

Do not expose every internal exception.

## 69. Tests

Prove:

- start executes Round 0;
- repeat returns dedicated public state;
- later run creates exactly one Round;
- a new repeat does not loop;
- status prints exact caller action;
- crash before marker resumable;
- crash after marker non-resumable;
- crash after committed repeat resumable;
- new Run consumes selected prior evidence without state merge;
- missing Run root honest;
- read-only commands never mutate.

---

# Slice 9 — Qualification, consistency, and cleanup

## 70. Qualification scenarios

Compose focused helpers rather than duplicate assertions.

Prove at least the architecture's 40 scenarios, including:

- direct execute;
- zero-step validation;
- investigate and repeat;
- repeat caller boundary;
- next Planner Decline;
- far failure finishing;
- hard blocker finishing;
- command nonzero accepted success;
- call error versus no return;
- Validator blocker;
- distinct child Tasks;
- artifact mutation;
- runtime copy safety;
- crash boundaries;
- prior Run evidence;
- full repository suite.

## 71. Static consistency checks

Fail qualification when either plan or active production contains obsolete concepts:

- `GAVE_UP` as lifecycle disposition;
- step or Task status `COMPLETE`, `FAILED`, `BLOCKED_UNKNOWN`;
- same-mission child delegation;
- generic command `success` or `expected_result`;
- competing `--provider`, `--model`, `--effort` CLI flags;
- automatic repeat loop;
- automatic operation replay;
- target-only ArtifactRef model;
- unlimited complete capture claim;
- archive runtime import.

Allow ordinary English uses only when not naming lifecycle contracts; prefer avoiding them in active STT docs and code.

## 72. Context tests

Instrument fake provider requests and assert:

- Lead receipts compact;
- Planner receives bounded current Round inputs;
- repeat Validator report is advisory;
- only selected ArtifactRefs cross to next Round;
- Worker receives one step;
- Validator receives bounded evidence index;
- child and prior histories are referenced;
- logs remain file-backed;
- byte limits enforced.

## 73. Full repository checks

Run:

- focused STT suite;
- full repository suite;
- Python compile checks;
- existing formatting/lint checks;
- shell syntax checks;
- `git diff --check`.

Do not add tools solely for this implementation.

## 74. Complexity review

Before acceptance inspect and remove:

- duplicated schema logic;
- duplicated state derivation;
- duplicated path/identity handling;
- unnecessary provider abstractions;
- semantic progress scoring;
- hidden automatic repeat or replay;
- mutable cursors;
- hidden target containment claims;
- dead compatibility code;
- broad exception catches;
- unbounded model context;
- hidden Git assumptions;
- unused modules.

---

## 75. Invariant-to-code map

| Architecture invariant | Primary code | Primary tests |
|---|---|---|
| immutable Task mission | `task.py` | Task identity tests |
| sequential immutable Rounds | `round.py`, `lead.py` | Round lifecycle tests |
| one repeated Round per consumed repeat transition | `lead.py`, `cli.py` | repeat boundary tests |
| Planner PLAN/DECLINE | `plan.py`, `boundary.py` | planning tests |
| EXECUTE/INVESTIGATE | `plan.py`, Planner contract | intent tests |
| durable Planner outcome | `boundary.py`, `round.py` | resume tests |
| call OK/ERR/no-return split | `launcher.py` | provider/command tests |
| exact command result | `command.py` | command tests |
| ArtifactRef at target and Run | `artifact.py` | artifact tests |
| exceptional REPEAT threshold | Validator contract, Boundary | validation tests |
| far failure finishes | Validator fixtures | repeat-decision tests |
| no automatic repeat loop | `lead.py`, `cli.py` | invocation tests |
| distinct child missions only | `task.py`, `lead.py` | recursion tests |
| copied runtime | `runtime.py`, `bootstrap.py` | self-update tests |
| Bootstrap immutable handoff | `bootstrap.py` | mutation tests |
| Task-local ledger | `ledger.py` | ledger tests |
| one writer | `run_lock.py` | lock tests |
| prior Run evidence only | Bootstrap/Boundary | prior evidence tests |
| no archive reachability | imports | static test |

---

## 76. Definition of done

The STT MVP is done when:

1. architecture and implementation match exactly;
2. every production module is necessary;
3. focused qualification passes;
4. full repository suite passes;
5. copied-runtime self-update and copy-race proofs pass;
6. Task mission remains immutable across Rounds;
7. one invocation consumes at most one pre-existing repeat transition;
8. initial Round 0 for new child Tasks remains allowed;
9. newly produced repeat always stops that invocation;
10. repeat requires material verified progress and credible better planning basis;
11. far failure and hard blockers finish rather than repeat;
12. Planner may Decline after repeat;
13. same-mission child Task is rejected;
14. command returned error and no return remain distinct;
15. same-Run resume never replans an accepted Round or replays possibly launched work;
16. ambiguous active-call crash is non-resumable;
17. prior Run evidence starts a distinct lifecycle;
18. no authoritative state is written under target;
19. active STT imports no archived Target Task code;
20. no sandbox, rollback, complete-effect-detection, or automatic publication claim is made;
21. final diff contains no unexplained mechanism;
22. implementation stops.

---

## 77. Final execution instruction

```text
Implement only plans/stt-mvp-architecture-plan.md.

Use this implementation plan as the ordered build map.

Build small vertical slices with deterministic tests. Preserve prior passing
behavior. Remove unnecessary machinery before each commit.

Do not restore archived Target Task behavior. Do not add concurrency, rollback,
a scheduler, a workflow language, dynamic Plan editing, semantic progress
scoring, automatic provider retry, automatic operation replay, automatic model
escalation, automatic repeat loops, or target sandboxing.

Treat REPEAT as exceptional: use it only when the Task is not yet good enough,
this Round produced material verified leverage, and a fresh Planner has a
credible better basis. Far failure, hard blockers, and progress without leverage
finish rather than repeat.

Stop when focused qualification and the full repository suite pass.
```
