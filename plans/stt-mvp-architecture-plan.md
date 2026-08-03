# STT MVP Architecture Plan

**Status:** Candidate architecture source of truth; documentation rewrite for implementation readiness
**Repository:** `saffih/skeptic`
**Repository base:** `702b480dc55ef935970fd60031f80d4320e43ad8`
**Companion:** `plans/stt-mvp-implementation-plan.md`
**Scope:** STT MVP only

---

## 1. Purpose

Safe Target Task (STT) executes one immutable mission against a live target through planned, sequential, evidence-backed work.

STT protects:

- separation of planning, execution, and validation;
- immutable accepted planning decisions;
- append-only orchestration evidence;
- deterministic sequential execution;
- bounded model context through persisted references;
- independent validation of current facts;
- honest distinction between returned errors, missing returns, semantic failure, and uncertainty;
- a frozen active runtime when the Skeptic repository is itself the target.

STT does not promise to prevent, discover, classify, or reverse every filesystem, process, network, credential, service, remote, or external side effect caused by a Worker or command.

Archived Target Task material is historical evidence only. Active STT does not import or inherit that lifecycle.

---

## 2. Core model

STT has one recursive construct:

```text
Task
```

A Task owns one immutable mission and one or more immutable **Rounds**.

```text
Task mission
→ Round 0
→ optionally REPEAT the Task through Round 1
→ optionally REPEAT through later Rounds
→ terminal Task judgment
```

Each Round is one complete semantic cycle:

```text
same immutable mission
+ selected verified evidence
+ current bounded workspace index
→ Planner
→ immutable planning outcome
→ ordered immutable Plan steps, when any
→ Validator
→ FINISH or REPEAT
```

A new Round is not a replay of the previous Plan, Worker, command, provider call, or child Task. It is a fresh planning cycle for the same Task mission using current target reality and selected verified evidence.

A child Task exists only for a genuinely distinct or narrower mission. Repeating the same mission remains inside the same Task.

---

## 3. Why Round and REPEAT

`Round` names each planning/execution/validation cycle without implying failure.

`REPEAT` names an exceptional pragmatic decision:

> The Task is not yet good enough to finish, but this Round produced material verified progress that gives a fresh Planner a credible better basis.

`REPEAT` is intentionally not the default.

Use:

```text
SATISFIED
→ FINISH

not satisfied, but materially closer and fresh planning has a credible next path
→ REPEAT

far from the mission, no useful new leverage, a hard blocker remains, or another Round is unlikely to help
→ FINISH with NOT_SATISFIED

evidence cannot establish either conclusion, and another Round is not credibly expected to resolve that
→ FINISH with INDETERMINATE
```

Activity, effort, changed files, or a persuasive Validator explanation alone do not justify `REPEAT`.

---

## 4. Explicit non-goals

The MVP does not provide:

- concurrency or parallel Task execution;
- distributed scheduling;
- a general workflow language;
- dynamic editing of an accepted Plan;
- automatic operation replay;
- automatic provider retry after an outer call may have launched;
- automatic model escalation;
- automatic repair loops;
- automatic Git commits, staging, pushes, merges, rebases, or publication;
- automatic rollback or target restoration;
- filesystem or process sandboxing;
- hostile-code containment;
- semantic effect classification;
- semantic proof that a repeated Round made intellectual progress;
- a mandatory maximum Task depth or Round count;
- recovery of a Run after an ambiguous active-call process crash;
- compatibility with archived Target Task runtimes;
- RunSkeptic as part of STT runtime execution.

These exclusions are not partially implemented.

---

## 5. Physical locations

STT uses three disjoint locations.

### 5.1 Source repository

The original Skeptic repository whose STT code is used to prepare a Run.

### 5.2 Target workspace

The plain directory or Git repository the mission concerns. It may be the source repository itself.

### 5.3 Run root

A unique temporary directory, normally:

```text
${TMPDIR:-/tmp}/stt/<run-id>/
```

It contains the frozen runtime and all authoritative orchestration state.

Authoritative STT state never lives under `<target>/.stt/`.

The Run root must be outside both source and target and must be owner-only where supported. A Run is resumable only while the Run root remains available and valid.

---

## 6. Frozen runtime

Before root Task creation, Bootstrap:

1. resolves source and target;
2. creates a unique Run root outside both;
3. copies only the self-contained active STT runtime;
4. rejects symlinks and special files in the copied runtime set;
5. preserves and verifies regular-file bytes and normalized executable mode;
6. excludes `.git`, caches, bytecode, previous Run state, and generated temporary files;
7. records a manifest containing path, size, SHA-256, and normalized mode;
8. verifies copied files;
9. re-observes source identities and rejects a mixed-generation copy;
10. re-executes only from `<run-root>/runtime/`.

The copied runtime contains only what the active entry point requires, conceptually:

```text
scripts/stt.py
concepts/stt/**
required package __init__.py files
```

Active STT must not import archived Target Task code or unrelated repository packages.

The frozen runtime prevents ordinary target edits from replacing the code driving the current Run. It is not an operating-system security boundary.

---

## 7. Bootstrap handoff and Run identity

Before re-execution, Bootstrap publishes an immutable bounded handoff containing:

- frozen submission bytes and SHA-256;
- source identity;
- target identity;
- frozen routing bytes and SHA-256;
- live-provider authorization;
- optional prior-Run identity;
- runtime-manifest identity.

The copied runtime never rereads the mutable original submission or routing file.

A new `run.json` binds:

- Run ID;
- source and target roots;
- target-root identity;
- runtime-manifest identity;
- submission identity;
- routing identity;
- live-provider authorization;
- optional prior Run.

A materially changed submission, target identity, runtime, authority, or routing requires a new Run.

Before root Task publication, the Bootstrap handoff is authoritative. After publication, `run.json` and Task state are authoritative; the handoff remains evidence.

---

## 8. Terms and roles

### Run

One root Task tree sharing one Run identity, frozen runtime, target identity, routing configuration, Run root, and exclusive writer lock.

### Task

One immutable mission with immutable authority, required terminal outputs, frozen role bindings, one Task ledger, one or more Rounds, and optional child Tasks for distinct missions.

### Round

One immutable Planner → Plan → steps → Validator cycle for the Task mission.

### Lead

A deterministic driver. It derives the next mechanical action from validated state and calls Boundary.

### Boundary

The mandatory deterministic façade for identity validation, request construction, outer calls, persistence, schema checks, artifact verification, ledger appends, and compact receipts.

### Planner

A semantic role that decides whether current evidence supports an executable Plan, an investigative Plan, or Decline.

### Worker

A semantic executor that performs one bounded step against the live target and returns a bounded report.

### Command

An exact Planner-selected process invocation executed as one Plan step.

### Child Task

A recursive Task with a genuinely distinct or narrower mission.

### Validator

An independent semantic investigator that judges the Task mission after the Round stops and chooses `FINISH` or, exceptionally, `REPEAT`.

### ArtifactRef

A verified identity-bound reference to a regular file in the target or Run.

### Receipt

A compact structured reference returned to the Lead. Substantive bodies remain file-backed.

---

## 9. Task identity

Each Task owns immutable `task.json` and `mission.md`.

Task identity binds:

- Run identity;
- Task identity and deterministic path;
- exact mission bytes and hash;
- runtime and target identity;
- parent Task and parent step, where applicable;
- immutable authority;
- initial verified evidence;
- required terminal outputs;
- allowed Worker routes;
- Planner and Validator routes.

A child mission must be genuinely different from every ancestor mission. Boundary rejects a child whose mission hash equals an ancestor mission hash.

The parent supplies child mission, authority, evidence, and required outputs, never a child Plan.

---

## 10. Round identity

Each Round lives at a deterministic path:

```text
rounds/000/
rounds/001/
...
```

Round identity binds:

- Task identity;
- Round number;
- exact Task mission identity;
- current target identity;
- selected initial evidence;
- fresh workspace-index identity;
- frozen role bindings;
- predecessor Round, if any;
- predecessor Validator report and selected continuation artifacts, if any.

A Round is immutable once published.

One caller invocation may resume unfinished work and may consume at most one pre-existing `AWAITING_REPEAT` transition across the entire root Task tree, creating one repeated Round whose number is greater than zero.

This repeat guard does not restrict creation of Round 0 for a newly created root or child Task. Initial child-Task Rounds are ordinary recursive execution, not repetition.

---

## 11. Planner contract

The Planner receives only bounded persisted inputs:

- exact `mission.md`;
- Task authority and target root;
- required terminal outputs;
- allowed Worker routes;
- selected verified evidence;
- previous Validator report when repeating, labelled advisory evidence rather than instruction;
- a fresh deterministic bounded workspace index;
- fixed Planner instructions;
- output schema.

The Planner returns a semantic value:

```text
PLAN
DECLINE
```

The outer call may instead return a structured error or no accepted return; those are call mechanics, not Planner dispositions.

### 11.1 PLAN

A Plan has one intent:

```text
EXECUTE
INVESTIGATE
```

#### EXECUTE

The Planner has a credible complete path from current evidence.

This is not certainty and uses no confidence score.

#### INVESTIGATE

A specific decision-critical unknown prevents a credible complete Plan, but bounded work may produce evidence that gives a later fresh Planner a materially better basis.

An investigative Plan states:

- the exact unknown;
- why it blocks a credible complete path;
- the bounded probe;
- expected named evidence artifacts.

An investigative Plan does not promise Task success or automatic repetition.

A zero-step Plan is valid when the mission may already be satisfied.

### 11.2 DECLINE

The Planner concludes that neither a credible execution path nor useful bounded investigation exists under current authority, evidence, capabilities, dependencies, and constraints.

Decline includes:

- concise reason;
- blocking facts;
- missing requirements;
- why another investigation or Round is not credibly useful.

The Planner may Decline in any Round, including after earlier progress.

### 11.3 Planner limits

The Planner does not:

- execute commands;
- edit the target;
- write orchestration state;
- change authority or routing;
- approve Task completion;
- prescribe Validator judgment;
- create another Round;
- directly call another Planner.

---

## 12. Planning persistence

Every Planner phase has a durable `planning/outcome.json` recording call mechanics and evidence.

When the call returns an accepted semantic value, Boundary also publishes immutable `planning-result.json` containing `PLAN` or `DECLINE`.

This split prevents resume from invoking the Planner again after a settled call error or accepted negative result.

A malformed, mismatched, truncated, oversized, or schema-invalid return never becomes a Plan or Decline.

---

## 13. Plan schema

A Plan contains an ordered array of exactly three possible step kinds:

```text
worker
command
task
```

Common fields:

```json
{
  "id": "stable-lowercase-id",
  "kind": "worker|command|task",
  "description": "bounded purpose",
  "inputs": [],
  "outputs": []
}
```

Rules:

- step IDs are unique within the Round;
- array order is execution order;
- later steps reference only target inputs or accepted earlier outputs;
- future references are invalid;
- output names are unique within a step;
- Worker route names must be frozen allowed routes;
- child authority is equal to or narrower than parent authority;
- child mission differs from every ancestor mission;
- Boundary owns all orchestration paths;
- Plan validation checks structure, references, routing, and authority, not semantic wisdom.

There is no generic `success: {}` expression.

---

## 14. Call and Result mechanics

Every outer Planner, Worker, command, and Validator invocation records:

```text
call_state:
  NOT_STARTED
  RETURNED
  NO_RETURN
```

When `call_state = RETURNED`, it also records:

```text
result:
  OK(value)
  ERR(error)
```

Meaning:

- `NOT_STARTED`: Boundary proved the call did not launch;
- `RETURNED + OK(value)`: an accepted role-specific value was received;
- `RETURNED + ERR(error)`: an accepted structured error was received;
- `NO_RETURN`: launch may have occurred, but no accepted return was obtained.

A completed call may return an error. That is different from a call that did not return.

For operations that may outlive communication, record:

```text
settlement_state:
  SETTLED
  UNSETTLED
  UNKNOWN
```

Malformed, mismatched, truncated, oversized, or schema-invalid raw output is evidence for `NO_RETURN`; it is never promoted into a semantic value.

---

## 15. Step judgments

Worker, command, and child-Task steps have a local judgment:

```text
SATISFIED
NOT_SATISFIED
INDETERMINATE
```

Later Plan steps run only after:

```text
RETURNED
+ OK(value)
+ SATISFIED
```

Any other local result stops later steps and invokes the current Round Validator.

A local step judgment answers whether that step's declared local assignment is established. It does not decide the Task mission.

---

## 16. Worker step

A Worker may inspect and modify the live target, invoke internal tools or commands, run tests, gather evidence, and return named outputs.

A Worker does not change the accepted Plan, write the ledger, change identity or routing, publish terminal Task state, or decide overall mission satisfaction.

A Worker returns a bounded structured value containing:

- local judgment;
- concise summary;
- named `ArtifactRef` outputs;
- best-effort created, changed, and deleted paths;
- verification performed;
- warnings;
- unknowns.

Changed-path reporting is evidence, not proof of complete effect observation.

Boundary verifies every named output.

---

## 17. Command step

A command step defines only:

- explicit argv array;
- explicit cwd;
- accepted exit codes, default `[0]`;
- declared inputs;
- required named outputs;
- bounded environment declaration;
- bounded wait and termination policy.

There is no shell interpretation by default.

A command returning any exit code is:

```text
RETURNED + OK(command_result)
```

Boundary derives its local judgment:

```text
accepted exit code
+ all required outputs verify
→ SATISFIED

returned exit code not accepted
or a required output is conclusively missing or mismatched
→ NOT_SATISFIED

no accepted return
or required output identity cannot be observed stably
→ INDETERMINATE
```

No arbitrary expression language, stdout-regex success engine, plugin evaluator, or effect classifier exists in the MVP.

A command may affect target, local, process, service, network, or remote state. STT records only what it can observe.

---

## 18. Environment and credentials

A command declares:

```text
env_overrides
inherited_env_names
```

Rules:

- `env_overrides` contains explicit non-secret values only;
- the complete ambient environment is not passed automatically;
- inherited values are not persisted or hashed;
- provider adapters own a minimal required inherited-name allowlist;
- credentials and secrets must not appear in routing files, Plans, `run.json`, persisted requests, command argv, or explicit environment values.

STT does not claim arbitrary commands, agents, stdout, or stderr cannot disclose secrets.

---

## 19. ArtifactRef

Every named output and reusable evidence item uses:

```text
name
location: TARGET | RUN
relative_path
sha256
byte_size
artifact_type
normalized executable mode where supported
producer identity
```

### TARGET

A regular file inside the target. Boundary verifies:

- no symlink path component;
- canonical containment;
- regular-file type;
- current bytes;
- size;
- SHA-256;
- normalized mode when relevant.

### RUN

A Boundary-owned create-only regular file under the assigned Round or step artifacts directory.

Typical Run artifacts include:

- Worker and Validator reports;
- provider raw returns;
- command stdout and stderr;
- discovered contracts;
- bounded evidence summaries;
- Boundary-generated observation records for verified non-file facts such as absence, deletion, exit behavior, or target metadata.

A Validator report by itself is not material progress. A fact used to justify `REPEAT` must be captured before Boundary accepts the disposition as a separate verified `RUN` ArtifactRef. It may come from an earlier step, a Boundary observation, or a read-only Validator investigation; prose in the Validator report does not substitute for the artifact.

Evidence selected across the caller boundary for a repeated Round must use frozen `RUN` ArtifactRefs produced in the finishing Round. A live `TARGET` ArtifactRef may support current-Round validation, but it is not carried as repeat evidence; current target reality is supplied by the next Round's fresh workspace index.

Directory, symlink, socket, device, and other special-file outputs are unsupported.

Every ArtifactRef is reverified before each consumption boundary. STT never silently rebinds a changed target file.

A semantic role receives only exact declared artifacts or bounded selected contents, not unrestricted Run-root context.

Run artifacts exposed to a Worker or command are reverified after use.

---

## 20. Bounded capture

Stdout, stderr, raw provider returns, reports, and returned Run artifacts have configured byte limits.

When a limit is reached:

1. persist bytes received up to the limit;
2. record `truncated = true`;
3. reject the semantic return;
4. attempt bounded termination where applicable;
5. record settlement truthfully.

STT never silently truncates and never claims unlimited complete capture.

---

## 21. Validator contract

Every semantically processable Round ends through an independent Validator.

The Validator receives bounded references to:

- exact Task mission;
- current Round identity;
- planning outcome and semantic planning result, if any;
- every step result;
- Worker reports;
- command logs and observations;
- child results;
- current target observations;
- required terminal outputs;
- selected prior evidence;
- unsettled-operation facts.

The Validator may investigate with read-oriented tools and verification commands. It must not intentionally repair the target, continue Plan execution, invent Plan steps, alter routing, or create the next Round.

It returns two independent semantic fields.

### 21.1 Judgment

```text
SATISFIED
NOT_SATISFIED
INDETERMINATE
```

### 21.2 Disposition

```text
FINISH
REPEAT
```

Valid combinations:

```text
SATISFIED + FINISH

NOT_SATISFIED + FINISH
NOT_SATISFIED + REPEAT

INDETERMINATE + FINISH
INDETERMINATE + REPEAT
```

Invalid:

```text
SATISFIED + REPEAT
```

---

## 22. REPEAT threshold

`REPEAT` is accepted only when all are true:

1. the mission is not proven satisfied;
2. all relevant outer operations are `SETTLED`;
3. orchestration state is valid;
4. the Round produced at least one new verified `RUN` ArtifactRef;
5. the Validator identifies a concrete remaining gap;
6. the new evidence materially reduces, narrows, or changes that gap;
7. the Validator explains why a fresh Planner now has a credible better basis;
8. no known hard blocker makes another Round futile under current authority;
9. the request is not merely to repeat the previous Plan or operation;
10. the evidence is more than Planner or Validator prose.

Use `FINISH + NOT_SATISFIED` when work is still far from the mission, new evidence gives no material leverage, a hard blocker remains, or another Round is unlikely to help.

Use `FINISH + INDETERMINATE` when facts cannot establish the mission and another Round is not credibly expected to resolve the uncertainty.

A Planner Decline with no new material verified evidence cannot yield `REPEAT`.

Boundary validates the mechanical floors. It does not decide whether the Validator's reasoning is wise beyond required structure and evidence binding.

---

## 23. Repeating the Task

A valid `REPEAT` means:

> Run the same Task mission through one repeated Round with current reality and selected verified evidence.

It never means:

- replay the previous Plan;
- repeat a failed Worker or command;
- automatically call the same provider again;
- automatically upgrade model or effort;
- assume the next Round will succeed.

The next Planner receives:

- exact same mission bytes;
- same Task authority;
- same frozen role bindings;
- a fresh bounded workspace index;
- latest Validator report labelled advisory evidence;
- exact selected frozen `RUN` ArtifactRefs;
- required terminal outputs.

The Planner independently returns `PLAN` or `DECLINE`.

Older history is supplied only when the latest Validator explicitly selects exact references. Complete Round histories are not copied into model context.

---

## 24. Caller boundary for REPEAT

One invocation of `stt start` or `stt run` consumes at most one pre-existing repeat transition and therefore creates at most one repeated Round numbered greater than zero.

When a Round returns `REPEAT`:

```text
ROUND_FINISHED
→ Task state AWAITING_REPEAT
→ current CLI invocation stops
```

A later explicit caller invocation:

```text
stt run --run-root <run-root>
```

may create exactly one repeated Round.

At invocation start, Lead derives the deepest active Task across the root Task tree. Only an `AWAITING_REPEAT` state that already existed on that deepest active Task may consume the invocation's single repeated-Round allowance.

Creation of Round 0 for a newly created child Task does not consume this allowance.

A `REPEAT` produced by any root or child Task during the current invocation stops the entire invocation. It is never consumed immediately.

This prevents hidden internal repetition loops across recursion as well as at the root.

An automated host may call `stt run` repeatedly only under its own explicit finite policy.

---

## 25. Child Tasks

A child Task is used for a genuinely separate or narrower mission.

Example:

```text
parent mission: release version 1.2
child mission: verify package metadata
```

A child has its own immutable mission, Rounds, Planner, steps, Validator, ledger, and terminal result.

A child mission whose hash equals any ancestor mission hash is rejected. Same-mission work uses `REPEAT` inside the original Task.

Child-to-parent mapping is:

```text
child SATISFIED
→ parent task step SATISFIED

child NOT_SATISFIED
→ parent task step NOT_SATISFIED

child INDETERMINATE
→ parent task step INDETERMINATE

child operationally blocked, all child operations settled
→ no child terminal judgment is fabricated
→ parent task step INDETERMINATE with child evidence
→ parent Validator may audit

child operationally blocked by UNSETTLED or UNKNOWN operation
→ entire Run OPERATIONALLY_BLOCKED
→ no ancestor semantic Validator is launched

child INVALID
→ Run INVALID
```

Parent and ancestor Validators independently audit semantically processable child results.

---

## 26. Failure detection and propagation

Failure and uncertainty move through explicit boundaries:

```text
decision-critical unknown
→ Planner INVESTIGATE Plan

step NOT_SATISFIED / INDETERMINATE / ERR / NO_RETURN
→ stop later steps
→ current Round Validator

material verified progress with a credible better basis
→ Validator REPEAT
→ caller

far failure, hard blocker, or no useful leverage
→ Validator FINISH + NOT_SATISFIED

unresolvable uncertainty
→ Validator FINISH + INDETERMINATE

child negative or indeterminate result
→ parent step result
→ parent Validator
→ repeat upward

root operational blocker
→ operator
```

Every valid ancestor performs its own semantic audit. No direct propagation operation fabricates ancestor terminal judgments.

---

## 27. Planner or Validator operational failure

A Planner call that returns `ERR`, `NO_RETURN`, or `NOT_STARTED` produces durable planning outcome evidence but no semantic Plan or Decline.

The Round proceeds to validation only when the call is known settled. A Planner call with `settlement_state = UNSETTLED | UNKNOWN` makes the Task operationally blocked.

If the Validator returns `ERR`, `NO_RETURN`, or `NOT_STARTED`, no Round judgment or disposition is fabricated. The Task becomes operationally blocked.

A blocked root Validator does not create `REPEAT`, `FINISH`, or a semantic terminal Task result.

---

## 28. Settlement floor

When any relevant outer operation has:

```text
settlement_state = UNSETTLED | UNKNOWN
```

then:

- later Plan steps do not run;
- no new semantic Validator invocation is launched;
- no Round judgment is accepted;
- `FINISH` is forbidden;
- `REPEAT` is forbidden;
- the Task becomes `OPERATIONALLY_BLOCKED`.

A `NO_RETURN` operation that is confirmed `SETTLED` may proceed to Validator because no operation is still changing reality.

This prevents validation or a new Round from racing a possibly active prior operation.

---

## 29. Process crash and same-Run resume

Before every outer semantic or command launch, Boundary persists a create-only launch marker bound to exact request identity.

On process restart:

```text
no launch marker
→ launch could not have occurred
→ same-Run resume may proceed

marker + committed accepted outcome
→ same-Run resume may proceed

marker without committed accepted outcome
→ Run is non-resumable

control result file without committing ledger event
→ conflicting publication
→ Run is non-resumable
```

STT does not determine whether an interrupted operation actually ran.

Recovery is a new Run against current target reality, optionally using verified prior-Run evidence.

No Git dependency, replay, rollback, process reconciliation, or TT-style recovery subsystem is required.

A crash after a fully committed `REPEAT` leaves the Task safely resumable in `AWAITING_REPEAT`.

---

## 30. Boundary contract

Every outer operation passes through Boundary:

```text
Lead
→ Boundary
→ Planner / Worker / command / child Task / Validator
→ Boundary
→ persisted evidence
→ accepted outcome
→ ledger event
→ compact receipt
→ Lead
```

Boundary owns:

- Run, runtime, target, Task, Round, Plan, and step identity checks;
- current-action eligibility;
- declared-input resolution;
- request construction;
- launch-marker publication;
- provider and command invocation;
- raw-return and log persistence;
- call/result and settlement observation;
- schema validation;
- artifact verification;
- child creation and binding;
- Round and Task lifecycle publication;
- ledger appends;
- compact receipts.

Boundary does not judge mission wisdom, Plan quality, target elegance, or whether another Round is intellectually worthwhile beyond the mechanical `REPEAT` floors.

Internal tools used inside a Worker or Validator invocation are not separate STT Plan steps.

---

## 31. Lead behavior

The Lead is mechanical and depth-first.

For the deepest active Task:

1. validate the complete root-to-deepest path, current Task, Round, and ledgers;
2. resume unfinished current-Round work when safely resumable;
3. if the deepest active Task was already `AWAITING_REPEAT` at invocation start and the invocation has not consumed a repeat transition, create exactly one repeated Round for that Task;
4. invoke Planner when the current Round needs planning;
5. execute the first eligible unfinished step;
6. descend into a child Task step until it reaches a usable terminal result;
7. invoke Validator when planning or execution stops;
8. stop the current CLI invocation after Round `REPEAT`;
9. finish the Task after Round `FINISH`;
10. stop on invalid or operationally blocked state.

The Lead never invents steps, changes a Plan, chooses a semantic judgment, or loops internally across newly requested repeats.

---

## 32. Ledger

Each Task owns one append-only hash-chained JSONL ledger.

Minimal event vocabulary:

```text
TASK_CREATED
ROUND_CREATED
PLANNING_FINISHED
STEP_STARTED
STEP_FINISHED
ROUND_FINISHED
TASK_FINISHED
```

`PLANNING_FINISHED` binds durable call outcome and optional semantic planning result.

`ROUND_FINISHED` binds accepted Validator judgment and disposition.

When disposition is `REPEAT`, no `TASK_FINISHED` event is written and Task state derives as `AWAITING_REPEAT`.

When disposition is `FINISH`, Boundary appends `TASK_FINISHED` with final mission judgment and verified terminal outputs.

A single incomplete trailing fragment may be handled narrowly under the writer lock after validating the complete prefix. Interior corruption, hash mismatch, sequence gaps, or conflicting publication fail visibly.

---

## 33. Layout

```text
<run-root>/
├── runtime/
├── runtime-manifest.json
├── bootstrap/
│   ├── request.json
│   ├── submission.md
│   └── routing.json
├── run.json
├── run.lock
└── root/
    ├── task.json
    ├── mission.md
    ├── ledger.jsonl
    ├── rounds/
    │   ├── 000/
    │   │   ├── round.json
    │   │   ├── workspace-index.json
    │   │   ├── planning/
    │   │   │   ├── request.json
    │   │   │   ├── launch.json
    │   │   │   ├── raw-return.txt
    │   │   │   └── outcome.json
    │   │   ├── planning-result.json
    │   │   ├── steps/
    │   │   ├── validation/
    │   │   │   ├── request.json
    │   │   │   ├── launch.json
    │   │   │   ├── raw-return.txt
    │   │   │   ├── outcome.json
    │   │   │   └── report.json
    │   │   └── result.json
    │   └── 001/
    └── result.json
```

Child Tasks live under their owning step:

```text
rounds/<round>/steps/<index>-<step-id>/task/
```

Semantic roles do not invent control-state locations.

---

## 34. Routing and CLI

Bootstrap freezes a routing file containing:

- one Planner route;
- named allowed Worker routes;
- one independent Validator route;
- provider, model, effort, and adapter for each route.

A Plan selects a Worker only by an allowed route name.

Public CLI:

```text
stt start \
  --workspace <target> \
  --submission <file> \
  --routing-file <file> \
  [--prior-run <run-root>] \
  [--allow-live-provider]

stt run --run-root <run-root>
stt status --run-root <run-root>
stt diagnose --run-root <run-root>
```

There are no competing generic `--provider`, `--model`, or `--effort` flags.

Changing routing requires a new Run. Fake-provider qualification does not require live-provider authorization.

`status` and `diagnose` are read-only and report exact current state, blocker, and next caller action.

---

## 35. Workspace index

The workspace index is deterministic and bounded.

It:

- uses `lstat`-style observations;
- never follows symlinks;
- records symlinks as metadata only;
- indexes regular files and directories;
- does not read file bodies solely to build the index;
- emits explicit deterministic overflow markers.

A fresh index is created for every Round.

---

## 36. Prior-Run evidence

A new Run may receive an optional prior Run.

Boundary exposes only selected verified references such as:

- prior mission;
- prior planning results;
- prior Validator reports;
- selected Worker reports;
- selected command logs;
- named artifacts;
- terminal or blocked outcomes.

Lifecycle state is never merged across Runs. Prior reports are evidence, not authority.

Uncommitted prior files may be labelled diagnostic evidence but never accepted as lifecycle facts.

---

## 37. Context discipline

Every outer model invocation is reconstructible from persisted files and fixed role instructions.

The Lead receives compact receipts only.

The Planner receives bounded mission, authority, role choices, selected evidence, previous advisory Validator report where applicable, and fresh workspace index.

A Worker receives one step and exact declared inputs.

The Validator receives a bounded evidence index and selected referenced bodies.

Child and prior histories are referenced, not copied wholesale.

Actual hidden provider context and isolation are reported as unknown unless the host exposes proof.

---

## 38. Terminal and operational states

A finished Task has exactly one semantic judgment:

```text
SATISFIED
NOT_SATISFIED
INDETERMINATE
```

Non-semantic lifecycle states include:

```text
ACTIVE
AWAITING_REPEAT
OPERATIONALLY_BLOCKED
INVALID
```

`AWAITING_REPEAT` has one same-Run next action: a later explicit caller may run one repeated Round.

`OPERATIONALLY_BLOCKED` and `INVALID` are same-Run stopping states. `stt run` refuses further lifecycle execution; diagnosis preserves the reason, and the operator may start a new Run using current target reality and selected verified prior evidence.

Neither state is fabricated as a semantic terminal Task judgment.

---

## 39. Qualification scenarios

The MVP must prove at least:

1. direct `EXECUTE` Plan succeeds;
2. zero-step Plan succeeds through Validator;
3. `INVESTIGATE` produces verified Run evidence;
4. Validator validly returns `REPEAT`;
5. current invocation stops after `REPEAT`;
6. later explicit `stt run` consumes exactly one pre-existing repeat transition and creates one repeated Round;
7. a `REPEAT` produced during that repeated Round stops the same invocation;
8. next Planner receives identical mission bytes;
9. latest Validator report is advisory evidence, not instruction;
10. selected repeat artifacts are reverified;
11. next Planner may Decline;
12. `SATISFIED + REPEAT` is rejected;
13. `REPEAT` without a new verified current-Round `RUN` ArtifactRef is rejected;
14. `REPEAT` with no materially narrowed or changed gap is rejected by semantic qualification fixtures;
15. `REPEAT` with unsettled or unknown operations is rejected;
16. Planner or Validator prose alone cannot justify repeat;
17. far failure finishes `NOT_SATISFIED` rather than repeating;
18. hard authority or dependency blocker finishes rather than repeating;
19. an `EXECUTE` Round may make partial progress and validly repeat;
20. an `INVESTIGATE` Round may incidentally satisfy the mission and finish;
21. exact ancestor-mission child recursion is rejected;
22. distinct narrower child Tasks work and may create their initial Round 0 without consuming the repeat allowance;
23. accepted nonzero command exit code may satisfy a step;
24. command error evidence may support a later repeat;
25. Planner call error is durably recorded and not automatically reinvoked;
26. Validator operational failure fabricates no judgment or repeat;
27. child Validator failure is audited by parent Validator;
28. crash before outer-call marker is resumable;
29. crash after marker without committed outcome is non-resumable;
30. crash after committed repeat resumes as `AWAITING_REPEAT`;
31. ArtifactRef mutation before consumption is rejected;
32. runtime-copy symlink is rejected;
33. source/Run and target/Run overlap are rejected;
34. bounded capture truncation is visible and cannot become semantic return;
35. live adapters require explicit authorization;
36. plain-directory and Git targets both work without Git lifecycle authority;
37. active STT imports no archived Target Task package;
38. competing writer is rejected;
39. torn ledger tail is handled narrowly and interior corruption fails;
40. full repository suite passes.

---

## 40. Remaining implementation parameters

These are implementation choices, not architecture blockers:

- conservative byte limits;
- per-adapter wait and termination defaults;
- exact target-root identity observations available per platform;
- locking and durability guarantees on non-local filesystems;
- temporary Run pruning policy;
- host policy for how many explicit `stt run` invocations an automation may make.

Implementation must choose conservative defaults, document them, and test them.

---

## 41. Authoritative statement

```text
STT has one recursive construct: Task.

A Task owns one immutable mission and one or more immutable Rounds. Each Round
performs fresh planning, executes one immutable ordered Plan when present, and
ends through an independent Validator.

The Planner returns PLAN or DECLINE. A Plan intent is EXECUTE when current
evidence supports a credible complete path, or INVESTIGATE when a bounded probe
is needed before a credible complete path exists.

The Validator returns a mission judgment and FINISH or exceptional REPEAT.
REPEAT is allowed only when the Task is not yet good enough, the Round produced
material verified progress, and a fresh Planner has a credible better basis.
Far failure, hard blockers, or progress without leverage finish rather than
repeat.

A repeat never replays the previous Plan or operation. It asks the caller to
invoke the same Task through one repeated Round. STT core never loops automatically
across newly requested repeats.

Every outer call records NOT_STARTED, RETURNED with OK or ERR, or NO_RETURN,
plus settlement when applicable. Completed errors and missing returns are not
the same condition.

Workers and commands may change the live target. Boundary owns identity,
persistence, call evidence, artifact verification, lifecycle transitions, and
receipts. The Validator owns semantic judgment.

Child Tasks are only for distinct or narrower missions. Same-mission work stays
inside the Task through REPEAT.

Same-Run resume never replans an accepted Round or automatically replays work
that may have launched. An ambiguous active-call crash makes the Run
non-resumable; a new Run may use verified prior evidence.

STT protects orchestration evidence and honest uncertainty. It is not a sandbox
and does not prevent or roll back every target or external side effect.
```
