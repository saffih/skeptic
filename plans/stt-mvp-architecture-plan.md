# STT MVP Architecture Plan

**Status:** Accepted architecture plan for implementation  
**Purpose:** Define the smallest robust Safe Target Task system that can plan, execute, verify, recurse through subtasks, preserve low context usage, and safely dogfood itself.

---

## 1. Core invariant

STT has one recursive construct:

```text
Task
```

Every Task always follows exactly this lifecycle:

```text
Mission
→ Planner
→ ordered Plan steps
→ Validator
→ terminal result
```

This invariant applies to:

- the root Task;
- every subtask;
- every nested descendant;
- research Tasks;
- implementation Tasks;
- inspection Tasks;
- diagnostic Tasks.

There are no alternative Task lifecycles.

A Task may not:

- skip its Planner;
- inherit an executable Plan from its parent;
- let the Lead invent or change Plan steps during execution;
- skip final validation;
- continue after terminal failure.

---

## 2. Plan execution and recursive subtasks

The Planner converts the Task mission into an ordered Plan.

Most Plan steps are bounded mechanical operations.

A Plan step may also be another Task, represented by a subtask mission.

Example:

```json
{
  "id": "investigate-provider-contract",
  "kind": "task",
  "mission": "Determine the correct provider result contract and return a verified result."
}
```

When the Lead reaches a Task step:

1. create a separate Task space for the child;
2. give the child its mission and delegated authority;
3. run the child Planner;
4. persist the child Plan;
5. execute the child Plan sequentially;
6. run the child Validator;
7. persist the child terminal result;
8. return to the parent;
9. record the child result as the result of the parent step;
10. continue with the next parent Plan step.

Execution is naturally depth-first:

```text
root Task
→ child Task
→ grandchild Task
→ return to child
→ return to root
```

Only the deepest unfinished Task progresses.

The parent does not require a special waiting engine. Its Plan cursor remains on the child step until that child has a terminal result.

---

## 3. The Lead loop

The Lead is deliberately simple and mechanical.

It repeatedly performs this loop:

```text
current = deepest unfinished Task

if current has no Plan:
    call current Planner through Boundary
    persist accepted Plan

else if current has an unfinished step:
    if step is mechanical:
        execute it through Boundary
        persist result
        advance cursor

    if step is a Task:
        create child Task through Boundary
        switch current to child

else:
    call current Validator through Boundary
    persist terminal result

    if current is a successful child:
        return to parent
        complete parent step with child result
        continue parent

    if current failed or is blocked:
        propagate failure upward

    if current is the root:
        finish
```

The Lead does not:

- redefine missions;
- redesign Plans;
- interpret broad evidence;
- mutate files directly;
- call roles or commands directly;
- retain substantive Task bodies in active context.

---

## 4. Task-local space

Every Task owns its own durable directory.

Recommended layout:

```text
<task-root>/
├── task.json
├── mission.md
├── plan.json
├── ledger.jsonl
├── result.json
├── planning/
├── steps/
├── validation/
├── artifacts/
└── tasks/
```

Each Task independently owns:

- Task identity;
- parent reference when applicable;
- originating parent step;
- mission;
- delegated authority;
- immutable accepted Plan;
- Plan cursor derived from the ledger;
- append-only ledger;
- artifacts;
- nested Task directories;
- validation report;
- terminal result.

A subtask lives beneath its parent step or Task directory but follows the exact same layout and lifecycle.

The filesystem acts as a durable call stack.

---

## 5. Bootstrap

Bootstrap is the pre-Task execution context.

It is not itself a Task.

Bootstrap responsibilities:

1. recognize the exact `STT:` trigger;
2. determine whether the user requests a new STT run or resume;
3. use the intelligence level of the invoking agent to define or refine the root mission;
4. bind the host adapter and agent roles;
5. prepare the frozen runtime;
6. create the persistent run directory;
7. create the root Task space;
8. launch the simple Lead;
9. restore a run later when requested.

Bootstrap may perform special thinking about:

- mission definition;
- scope;
- resuming an interrupted run;
- choosing role/model bindings;
- explaining setup failures.

Once the root Task is created, its mission is immutable.

A materially changed mission creates a new root Task or run.

---

## 6. Trigger behavior

The user invokes STT with:

```text
STT: <mission>
```

Bootstrap recognizes the exact prefix and treats the remaining content as the proposed mission.

The agent currently serving the user performs Bootstrap. Therefore the intelligence used for mission definition remains under user control.

After mission definition, Bootstrap hands control to the simple mechanical Lead.

---

## 7. Frozen runtime and dogfooding

Dogfooding is normal execution, not a separate mode.

Every root STT invocation freezes its control implementation before planning begins.

Recommended active control path:

```text
${TMPDIR:-/tmp}/stt/<run-id>/control/
```

Recommended persistent run path:

```text
<workspace>/.stt/runs/<run-id>/
```

The frozen control bundle contains only the runnable STT control plane:

```text
concepts/stt/
required package initializers
provider adapters
scripts/stt.py
skeptic.md
skeptic-questions.md when present
STT workflow and role instructions
runtime manifest
```

It excludes:

```text
.git/
.stt/
tests/
caches/
unrelated project source
```

Bootstrap:

1. copies the required control files;
2. creates a manifest with path, size, mode, and SHA-256;
3. persists an immutable runtime bundle under the run data path;
4. makes the active control copy read-only;
5. re-executes STT from that frozen copy.

All Tasks in one root Task tree use the same frozen runtime.

Children do not create new runtime generations.

If the temporary runtime disappears, Bootstrap reconstructs it from the persisted immutable bundle, verifies the manifest, and resumes from that copy.

It must never reconstruct from the possibly modified target workspace.

This allows generation A to modify the STT source in the target workspace while the active Task tree continues running from generation A. A later root invocation freezes generation B.

---

## 8. Control path and data path

The architecture separates executable control from persistent Task data.

### Control path

Contains the frozen executable STT implementation.

### Data path

Contains:

- mission;
- Plans;
- ledgers;
- artifacts;
- requests;
- results;
- command logs;
- before-images;
- validation reports;
- child Tasks;
- the persistent frozen-runtime bundle.

Invariant:

```text
Control executes.
Data persists.
Control does not import executable code from Data.
Data never controls imports.
```

The run data directory should be ignored by Git.

Recommended `.stt/.gitignore`:

```gitignore
*
!.gitignore
```

---

## 9. Boundary Agent

The Boundary Agent is the mandatory gateway between the Lead and every substantive operation.

The Lead never directly calls:

- Planner;
- Worker;
- Validator;
- command runner;
- workspace mutation;
- evidence retrieval;
- child Task creation;
- child Task return.

Every call follows:

```text
Lead
→ Boundary
→ operation
→ Boundary
→ persisted complete result
→ compact receipt
→ Lead
```

Boundary is deterministic. It is not a planning or reviewing role.

### Boundary request flow

1. Lead identifies the next required action.
2. Lead sends a compact reference-based request.
3. Boundary validates Task, Plan, step, authority, and artifact references.
4. Boundary loads only the bounded context required by the operation.
5. Boundary invokes the role or deterministic operation.
6. Boundary receives the complete output.
7. Boundary validates schema, paths, hashes, scope, identity, and size.
8. Boundary persists the complete result.
9. Boundary appends the accepted fact to the current Task ledger.
10. Boundary returns a compact receipt.

### Boundary responsibilities

Boundary enforces:

- request identity;
- Task identity;
- Plan and step identity;
- runtime identity;
- authority;
- read and write scope;
- artifact containment;
- path safety;
- file type;
- hashes;
- size bounds;
- result schema;
- replay prevention;
- ledger appends;
- child-parent binding;
- compact receipts.

Boundary does not decide:

- whether a Plan is wise;
- whether implementation is elegant;
- whether the mission is substantively satisfied;
- how to repair failed work.

Those decisions belong to Planner and Validator.

---

## 10. Planner

Every Task always calls its Planner.

The Planner receives:

- `mission.md`;
- Task authority and constraints;
- explicitly selected evidence;
- relevant verified child results when applicable;
- previous Plan and findings only during a bounded corrective planning attempt.

The Planner produces one ordered Plan.

Conceptually, Plan steps are:

```text
mechanical operation
or
Task
```

Mechanical steps may include:

- inspect;
- retrieve bounded evidence;
- prepare a change;
- apply a validated change;
- run a command;
- check a deterministic condition.

The Planner may create a Task step when work requires its own mission, planning, execution, and validation.

The Planner does not:

- execute the Plan;
- modify the workspace;
- write the ledger;
- choose its own authority;
- create arbitrary artifact paths.

The Plan hash identifies the accepted immutable Plan.

---

## 11. Worker and mechanical execution

The Worker receives one bounded Plan step.

It receives only:

- the step instructions;
- declared input files;
- relevant verified child results;
- exact write scope;
- exact Boundary-assigned output paths.

The Worker writes staged replacement artifacts.

It does not:

- edit the live workspace;
- run commands;
- modify the Plan;
- review its own work;
- write Task state;
- write outside declared scope.

Deterministic code performs:

- evidence retrieval;
- path validation;
- hashing;
- copying;
- ledger operations;
- command execution;
- before-image storage;
- mutation intent;
- atomic file installation;
- result verification.

---

## 12. Workspace mutation

Only deterministic STT code may mutate the live workspace.

For every mutation:

1. validate every path;
2. reject absolute paths;
3. reject `..`;
4. reject `.git` and `.stt` path components;
5. reject symlink parents;
6. reject special files;
7. verify accepted write scope;
8. verify the current live identity matches the admitted before-state;
9. persist exact before-images;
10. persist intended replacements;
11. append durable `MUTATION_INTENT`;
12. apply regular-file changes atomically where possible;
13. verify installed state;
14. record step completion.

MVP supports:

- create regular file;
- replace regular file;
- delete regular file;
- create required real directories.

MVP does not provide automatic rollback.

---

## 13. Interruption semantics

There is one non-replayable uncertainty window:

```text
MUTATION_INTENT recorded
→ workspace mutation may have begun
→ completion not recorded
```

After restart, STT must not replay that mutation.

The Task becomes:

```text
BLOCKED_UNKNOWN
```

Diagnosis references:

- before-images;
- intended replacements;
- current live identities;
- interrupted step;
- relevant logs.

Operations before mutation intent are retryable because they only create staged immutable artifacts.

---

## 14. Validator and validation propagation

Every Task always ends by calling its Validator through Boundary.

The Validator checks:

- mission;
- accepted Plan;
- step results;
- verified child Task results;
- applied changes;
- deterministic validation evidence;
- final workspace state.

The Validator returns:

```text
COMPLETE
FAILED
BLOCKED_UNKNOWN
```

Each child Task owns its validation report.

The parent references the child result and report rather than copying the child ledger or full history.

Validation therefore propagates naturally upward:

```text
child Validator
→ child result
→ parent continues
→ parent Validator includes child result
→ root Validator covers the full verified Task tree
```

A failed or blocked child causes the parent step to fail and propagates toward the root.

MVP does not automatically run repeated Fix Loops after final validation failure.

---

## 15. Ledger

Each Task owns one append-only hash-chained JSONL ledger.

The ledger is the lifecycle authority.

Substantive bodies live in files. Ledger entries commit facts about those files.

Minimal event vocabulary:

```text
TASK_CREATED
PLAN_ACCEPTED
STEP_STARTED
MUTATION_INTENT
STEP_COMPLETED
VALIDATION_COMPLETED
TASK_FINISHED
```

No special recursive event family is required.

For a Task step, the parent `STEP_COMPLETED` references the child `result.json`.

The child ledger contains the child’s complete history.

Current state and Plan cursor are derived from:

- ledger events;
- immutable Plan;
- persisted artifacts;
- validated child result;
- terminal report.

---

## 16. Context-size invariant

The active Bootstrap and Lead sessions must remain small.

Substantive information moves through files:

```text
agent produces complete output
→ Boundary persists it
→ ledger records reference and hash
→ Lead receives compact receipt
→ later agent reads only the exact required files
```

The Lead carries only:

- run ID;
- current Task path;
- current Plan step;
- ledger head;
- frozen runtime identity;
- relevant artifact references;
- compact status;
- next action.

The Lead must not carry:

- complete Plans;
- full source files;
- complete agent outputs;
- command logs;
- child Task ledgers;
- full validation reports;
- unrelated evidence;
- prior model conversations.

Correctness must not depend on preserving conversation history.

Every Planner, Worker, and Validator call must be independently reconstructible from persisted files and fixed instructions.

---

## 17. Artifact-use invariant

Every substantive artifact should have one clear purpose and normally one principal consumer.

An artifact may be reused for a second closely related purpose when necessary, but it must not become a general context bundle.

Examples:

| Artifact | Producer | Principal consumer |
|---|---|---|
| Mission | Bootstrap or parent Planner | Planner and Validator |
| Plan | Planner | Lead and Validator |
| Step request | Boundary | One operation |
| Step result | Worker or command | Lead and Validator |
| Child result | Child Validator | Parent step and parent Validator |
| Command log | Command runner | Validator when needed |
| Before-image | Boundary | Diagnosis |
| Validation report | Validator | Parent or Bootstrap |

Boundary constructs every operation request from an explicit list of references.

Agents never receive all available artifacts merely because they exist.

---

## 18. Naming conventions

Predictable paths prevent context discovery and broad searches.

Every Task uses fixed names:

```text
task.json
mission.md
plan.json
ledger.jsonl
result.json
```

Planning attempts:

```text
planning/
├── attempt-001/
│   ├── request.json
│   ├── result.json
│   ├── plan.json
│   └── findings.json
└── accepted-plan.json
```

Plan steps:

```text
steps/
├── 000-inspect-provider/
├── 001-research-contract/
├── 002-apply-repair/
└── 003-run-tests/
```

Each step may contain:

```text
request.json
result.json
receipt.json
artifacts/
stdout.log
stderr.log
before/
replacement/
task/
```

Rules:

- step IDs are unique within a Task;
- use lowercase ASCII letters, digits, and hyphens;
- step directories use a three-digit Plan index plus stable step ID;
- attempts use monotonically increasing three-digit numbers;
- standard outputs use fixed names;
- Boundary supplies every writable output path;
- agents never invent output locations.

A child Task for a Task step is always located at:

```text
steps/<index>-<step-id>/task/
```

Its result is always:

```text
steps/<index>-<step-id>/task/result.json
```

---

## 19. Corrective planning

When a Plan requires correction, the next Planner run receives only:

```text
mission.md
previous plan
corrective findings
newly admitted evidence
```

It does not receive:

- previous Planner conversation;
- every prior attempt;
- complete Task ledger;
- entire workspace;
- unrelated evidence.

Persisting the previous Plan and findings makes the corrective run effective without retaining a large model session.

Corrective planning should be bounded.

Final validation failure ends the Task honestly in the MVP.

---

## 20. Model routing

Model strength should match decision leverage.

### Bootstrap

Runs in the agent selected by the user.

Bootstrap intelligence is therefore user-controlled.

### Planner

Use a strong reasoning model by default.

The Planner makes high-leverage decisions:

- decomposition;
- subtask creation;
- scope;
- sequencing;
- validation design;
- risk reduction.

### Validator

Use a strong reasoning model by default.

The Validator independently judges:

- mission completion;
- Plan compliance;
- sufficiency of child results;
- validation evidence;
- omissions and harm.

### Worker

Use an economical model for bounded implementation work.

Escalate only when:

- the Planner marks the step as semantically difficult;
- the economical Worker fails;
- Boundary receives repeated malformed output;
- the step cannot be reduced to bounded mechanics.

### Lead and Boundary

Use deterministic code or extremely simple mechanical agents.

They do not need expensive reasoning models.

### Commands and file operations

Always use deterministic code.

---

## 21. Cost and quality forecast

The expected model cost of one Task is approximately:

```text
one strong Planner call
+ bounded economical Worker calls
+ one strong Validator call
```

Each subtask recursively adds the same unit.

Evidence retrieval, Boundary processing, hashing, commands, ledger writes, and file mutation require no model calls.

This provides a useful cost forecast:

- number of Tasks estimates strong Planner and Validator calls;
- number of semantic change steps estimates economical Worker calls;
- mechanical steps add little model cost.

Expected losses from economical Workers include:

- less architectural awareness;
- weaker handling of ambiguity;
- poorer cross-file consistency;
- inability to repair underspecified instructions.

Mitigations:

```text
strong planning
→ narrow persisted instructions
→ economical bounded execution
→ deterministic checks
→ strong independent validation
```

The architecture must not allow a cheap Worker to improvise broadly.

---

## 22. Git behavior

Git is optional.

STT must work in:

- a Git repository;
- a Git worktree;
- a plain directory.

When available, STT may record:

- repository root;
- HEAD;
- branch;
- status;
- final diff.

Git is not used for:

- Task state;
- runtime identity;
- before-images;
- rollback;
- correctness;
- workspace locking.

STT does not commit, stage, push, merge, rebase, or publish.

Its job is to produce and verify a working-directory change.

---

## 23. Public interface

MVP commands:

```text
stt start --workspace <path> --mission-file <path>
stt run --run-root <path>
stt status --run-root <path>
stt diagnose --run-root <path>
```

The conversational `STT:` trigger invokes Bootstrap, which then performs the equivalent setup and dispatch.

There is no separate dogfood command.

---

## 24. Explicit non-goals

MVP does not provide:

- automatic rollback;
- whole-workspace snapshots;
- transactional cutover;
- recovery packs;
- restoration into another workspace;
- concurrent Tasks;
- distributed execution;
- repeated three-pass reviews;
- automated Fix Loops;
- hostile-code containment;
- generalized workflow expressions;
- arbitrary filesystem-object support;
- compatibility with obsolete STT internals.

---

## 25. Implementation shape

Target core modules:

```text
bootstrap.py
runtime.py
lead.py
task.py
ledger.py
boundary.py
plan.py
workspace.py
provider.py
cli.py
```

Responsibilities:

- `bootstrap.py`: trigger, mission definition, role binding, run creation, resume;
- `runtime.py`: freeze, verify, reconstruct, and launch control runtime;
- `lead.py`: generic DFS Task loop;
- `task.py`: Task-local paths and Task state;
- `ledger.py`: append-only events and cursor derivation;
- `boundary.py`: request/result firewall and compact receipts;
- `plan.py`: Plan schema and validation;
- `workspace.py`: safe paths, before-images, mutations, optional Git;
- `provider.py`: Planner, Worker, and Validator dispatch;
- `cli.py`: public commands and receipts.

Design targets:

```text
approximately 1,200–1,800 production lines
no orchestration file near 1,000 lines
one Task construct
one Lead loop
one Boundary behavior
one frozen runtime per root Task tree
```

Exceeding the range requires a feature-level explanation.

---

## 26. Qualification scenarios

The MVP is accepted only after proving:

1. `STT:` trigger creates a Bootstrap context.
2. Bootstrap can define and persist a root mission.
3. Root Task always runs Planner.
4. Root Task executes ordered Plan steps.
5. Root Task always runs Validator.
6. Subtask always runs its own Planner.
7. Subtask executes its own Plan.
8. Subtask always runs its own Validator.
9. Parent resumes seamlessly after child completion.
10. Nested execution is depth-first.
11. Each Task owns its own ledger and artifacts.
12. Child result is referenced, not copied into parent context.
13. Root and children use the same frozen runtime.
14. Active Task survives modification or deletion of workspace STT source.
15. Temporary runtime reconstructs from the persistent bundle.
16. Plain-directory change succeeds.
17. Git-repository change succeeds.
18. Git remains optional.
19. Out-of-scope writes fail.
20. `.git` and `.stt` writes fail.
21. Symlink-parent writes fail.
22. Before-images are persisted.
23. Mutation uncertainty is never replayed.
24. Command logs remain file-backed.
25. Planner context is bounded.
26. Worker context is bounded.
27. Validator receives a compact final index.
28. Lead receipts do not inline substantive bodies.
29. Child failure propagates to root.
30. Generation A can modify STT and generation B can later run the improved source.

---

## 27. Authoritative architecture statement

```text
Bootstrap recognizes STT:, defines the root mission, binds the roles, freezes
the STT runtime, creates the persistent run context, and launches the Lead.

STT has one recursive construct: Task.

Every Task receives a mission, always calls its Planner, executes the generated
Plan sequentially, always calls its Validator, and produces a terminal result.

A Plan step is normally mechanical, but it may be another Task with a mission.

When the Lead reaches a Task step, it creates that Task in its own durable
space and switches to it. The child follows the same lifecycle. When the child
finishes successfully, the Lead returns to the parent, records the verified
child result as the parent step result, advances the parent cursor, and
continues.

Execution is sequential and depth-first.

Every substantive call passes through Boundary. Boundary validates requests,
loads only bounded context, persists complete results, records accepted facts,
and returns compact receipts.

All substantive data lives in predictable files. The Lead carries references
and next actions, not bodies.

Planner and Validator use strong reasoning. Bounded Workers may use economical
models. Mechanical operations use deterministic code.

All Tasks in one root Task tree use the same frozen STT runtime.

Uncertain mutations are never replayed.
```
