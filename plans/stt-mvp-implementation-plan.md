# STT MVP Implementation Plan

**Status:** Corrected implementation plan; execute only against the companion architecture and private role contracts in the same documentation revision
**Architecture source of truth:** `plans/stt-mvp-architecture-plan.md`
**Private role contracts:** `concepts/stt/contracts/{planner,worker,validator}.md`
**Repository:** `saffih/skeptic`

---

## 1. Objective and DONE

Implement the smallest complete STT described by the architecture:

```text
Mission
→ one Planner call
→ accepted Plan or persisted planning failure
→ sequential steps until first non-COMPLETE
→ recorded SKIPPED later steps
→ one Validator call
→ terminal result
```

DONE requires:

- the architecture and three private role contracts are implemented as written;
- active STT has no runtime dependency on the old lifecycle;
- the focused qualification obligations pass;
- frozen-runtime qualification passes;
- Claude Code and Codex adapters pass their contract tests, and at least one authorized live route passes an end-to-end smoke test on a supported host;
- the full repository suite passes;
- no unresolved architecture conflict or blocking unknown remains.

---

## 2. Starting conditions and source binding

Before code changes:

1. read the architecture, this plan, and all three private role contracts from one documentation commit;
2. record their blob identities in implementation evidence;
3. preserve unrelated working-tree changes;
4. inspect the active old STT implementation only to identify replacement boundaries and candidate leaf primitives;
5. have the implementation Planner inspect the actual branch and write a concise primitive-reuse table before choosing concrete keep/copy/reject actions;
6. verify the intended new CLI entry point cannot silently import the old lifecycle;
7. start with one root-Task vertical slice using the fake provider.

If a governing document changes materially, stop implementation, review the change, and explicitly rebind to the new identities.

---

## 3. Replacement and reuse policy

Replace the active old STT lifecycle. Do not refactor it into the new design and do not add a compatibility layer.

The implementation may copy or adapt a small deterministic leaf primitive only after recording:

```text
old source
property being reused
why the old contract is understood
copy/adapt/reject decision
new STT owner
focused proof
```

Do not import or reuse as architecture:

- the old Runner or lifecycle reducer;
- capsule, delta, recovery-pack, or review-loop workflows;
- mandatory Git/worktree behavior;
- old event or Plan schemas;
- direct launcher-to-role paths that bypass Boundary;
- same-Run retry or automatic replanning behavior.

Once the new vertical slice passes, delete obsolete active implementation modules, entry-point imports, and tests whose only purpose is the superseded lifecycle. Do not leave two active STT systems.

Git history is sufficient preservation. Do not create another archive copy.

---

## 4. Build rules

Each implementation slice must:

- implement one end-to-end behavior, not a layer with no executable path;
- add focused deterministic tests that exercise the public behavior;
- keep schemas and path rules single-sourced;
- preserve complete failure evidence;
- verify immediately before moving to the next slice.

Do not:

- add retries, attempt budgets, or retry flags;
- create a generalized workflow or provider plugin framework;
- add mutable cursor or derived state files;
- add automatic rollback, repair, or continuation Runs;
- add arbitrary child-count, Task-depth, or semantic-progress limits; whether another child Task is rational belongs to Planner;
- let provider adapters define lifecycle semantics;
- claim prevention where the host only observes or hopes;
- implement against unresolved role-contract ambiguity;
- add abstractions merely to match a proposed file tree.

Commits should follow coherent verified slices. No fixed commit count is required.

---

## 5. Minimal implementation shape

A reasonable starting package is:

```text
concepts/stt/
├── __init__.py
├── model.py          # exact schemas, references, statuses, events
├── store.py          # canonical JSON, create-only files, ledger, locks
├── runtime.py        # freeze, manifest, frozen reconstruction
├── workspace.py      # path admission, materialization, workspace index
├── providers.py      # small provider protocol and adapters
├── boundary.py       # all substantive operations and validation
├── lead.py           # mechanical depth-first driver
├── cli.py
└── contracts/
    ├── planner.md
    ├── worker.md
    └── validator.md
```

`scripts/stt.py` is the CLI entry point.

Consolidate or split modules only when a concrete responsibility or test boundary requires it.

---

## 6. Exact persisted model

Implement closed schemas for:

- start specification;
- Run binding and frozen runtime manifest;
- artifact references;
- Task identity and parent binding;
- workspace index;
- Plan and the four step kinds;
- Planner, Worker, Command, Mutation, Task, and Validator requests/results, including fixed child-result and child-validation evidence fields on Task-step results;
- call dispositions;
- terminal Task result;
- ledger events.

Use one canonical JSON implementation:

- UTF-8;
- sorted keys;
- stable compact separators;
- exactly one final LF;
- no NaN or Infinity;
- exact allowed fields;
- conservative byte and collection limits.

Every artifact reference contains:

```text
path
sha256
byte_size
artifact_type
producer
authority
```

Reject unknown fields unless a schema explicitly permits them.

---

## 7. Persistence, ledger, and lock

Implement:

- create-only atomic regular-file publication;
- complete same-parent temporary Task construction and atomic publication;
- one append-only hash-chained JSONL ledger per Task;
- one exclusive Run writer lock;
- read-only busy behavior for `status` and `diagnose`;
- one narrow torn-tail repair path;
- fail-closed interior corruption handling;
- state derivation entirely from ledger plus immutable referenced files.

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

Start events bind exact request identity before any corresponding fallible invocation.

---

## 8. Bootstrap and frozen runtime

Implement Bootstrap in this order:

1. validate proposed start fields;
2. create a unique Run root;
3. open, verify, and copy mission and every initial-evidence source exactly once into Run-owned bootstrap evidence;
4. persist the canonical start specification referring to the copies;
5. freeze the literal active-runtime allowlist, private contracts, and selected adapters;
6. reconstruct and re-execute from verified frozen control;
7. acquire the Run writer lock;
8. reverify the persisted start specification and every Run-owned evidence copy;
9. verify selected provider-route capabilities plus exact allowed Command route executable identities, argv templates, parameter schemas, timeout ceilings, and environment allowlists;
10. publish the immutable Run binding;
11. build the root workspace index;
12. atomically create the root Task;
13. enter Lead.

Do not reread the original mission or evidence source paths after materialization.

The runtime manifest is outside the bundle it hashes. Frozen reconstruction must import only from the verified control generation.

A pre-`TASK_CREATED` failure is diagnosable but not resumable Task state.

---

## 9. Path admission and materialization

Implement one no-follow object-open path-admission primitive for live workspace reads and Mutation destinations.

Reject:

- absolute semantic workspace paths;
- empty or traversal paths;
- containment escape;
- `.git` or `.stt` components;
- symlink components or leaves;
- special files;
- unauthorized paths.

Build bounded deterministic workspace indexes with explicit overflow markers.

For every Planner, Worker, Command, and Validator operation, Boundary first persists the request and appends its start event from immutable accepted references, then materializes exact declared inputs into the call directory and binds their hashes and sizes. Materialization is evidence capture, not semantic freshness judgment. A post-start preparation failure consumes the operation and is finished without another call.

---

## 10. Provider protocol and private contracts

Use a small protocol, not a plugin framework:

```python
class Provider:
    def probe(self, route: Route) -> ProbeResult: ...
    def invoke_once(self, request: ProviderRequest, call_root: Path) -> ProviderReturn: ...
```

The fake provider must cover:

- valid success;
- explicit failure;
- malformed output;
- identity mismatch;
- timeout with confirmed termination;
- unknown termination;
- oversized output;
- isolation failure.

Each role request includes the exact frozen private contract and a bounded index of materialized inputs. Provider output is accepted only through Boundary schema and identity validation.

Claude Code and Codex adapters are required integration targets. A live adapter is supported only when its tests prove the architecture provider contract. Disable client-side retries where the provider exposes that control and record whether transport or service retries remain unobservable. If the host cannot enforce output-only semantic writes and absence of side-effecting semantic tools, probe fails before `TASK_CREATED`. Fake-only execution qualifies mechanics but not release readiness.

There is no same-Run retry path in the provider API or persisted schema.

---

## 11. One-call directories and disposition

Use one create-only call directory per operation:

```text
planning/call/
validation/call/
steps/<index>-<step-id>/call/
```

Each contains exact request, disposition, materialized `in/`, output `out/`, raw return, logs, and any observable owned local process identity and termination facts.

Dispositions are exactly:

```text
ACCEPTED
FAILED
BLOCKED_UNKNOWN
```

Rules:

- every operation is dispatched by STT at most once;
- explicit failure or invalid structured content becomes `FAILED` when facts are known;
- identity, isolation, integrity, or termination uncertainty becomes `BLOCKED_UNKNOWN`;
- failed or uncommitted output is never promoted;
- interruption cleanup may signal only an exact owned local process identity and never relaunches the operation;
- no attempt number, maximum-attempt field, retry-permitted flag, or replay-safe command field exists.

---

## 12. Boundary and Lead vertical slice

Expose narrow Boundary operations:

```python
plan_once(task_ref)
execute_worker_once(task_ref, step_ref)
execute_command_once(task_ref, step_ref)
prepare_or_apply_mutation(task_ref, step_ref)
create_or_resume_child(task_ref, step_ref)
finish_parent_from_child(task_ref, step_ref, child_ref)
finish_later_steps_skipped(task_ref, cause_ref)
validate_once_and_finish(task_ref)
resume_from_ledger(task_ref)
```

Lead calls no provider, process, workspace mutation, ledger, or publication helper directly.

Implement root success first:

1. create Task;
2. append `PLANNER_STARTED`;
3. invoke fake Planner once;
4. accept one Plan;
5. execute one Worker step;
6. append `VALIDATOR_STARTED`;
7. invoke fake Validator once;
8. append `TASK_FINISHED`;
9. reconstruct the same terminal result after process restart.

Only after this slice passes, add failure shortening and recursion.

---

## 13. Planner path

1. verify no planning outcome and no prior `PLANNER_STARTED`;
2. build and persist the bounded Planner request from immutable references;
3. append `PLANNER_STARTED`;
4. materialize exact mission, evidence, authority, required outputs, workspace index, Plan schema, and the frozen allowed Command route catalog with typed parameter and output contracts;
5. invoke Planner once only when preparation succeeds;
6. persist raw evidence and disposition;
7. on accepted output, validate and seal the Plan and append `PLAN_ACCEPTED`;
8. otherwise validate one planning-failure result and append `PLANNING_FAILED`:
   - `FAILED` for an established material contradiction, prohibition, impossibility, or authority mismatch;
   - `BLOCKED_UNKNOWN` for a material missing fact, decision, capability, evidence item, or authority that cannot be resolved through authorized work in this Task;
9. proceed to Validator.

On resume after `PLANNER_STARTED` without a planning outcome, do not call Planner again. Append `PLANNING_FAILED / BLOCKED_UNKNOWN` from available evidence and continue to Validator.

---

## 14. Worker and Command paths

### Worker

Before invocation, append `STEP_STARTED` binding the exact Worker request. Invoke once, validate declared artifacts, and append `STEP_FINISHED`.

On failure or uncertainty, append the corresponding non-`COMPLETE` result, record later steps `SKIPPED`, and proceed to Validator.

On resume after a started but unfinished Worker call, do not invoke Worker again. Finish the step `BLOCKED_UNKNOWN`.

### Command

Boundary persists a request selecting one frozen allowed Command route with schema-valid named parameters, expected exit codes, and declared outputs, then appends `STEP_STARTED`. Boundary renders explicit argv from the route's fixed template, resolves typed path parameters only inside the disposable command workspace, applies bounded scalar parameters, the route timeout ceiling, and allowed environment keys, and forbids shell strings or model-authored free-form argv. Boundary next creates the disposable workspace and materializes the exact declared inputs before invoking once.

Pass only disposable paths and no target-workspace or authoritative Task path. Verify this structurally before launch. The command contract permits only cooperative local operations with no intended external side effects; do not claim hostile-process, network, or external-resource containment.

Capture stdout, stderr, exit facts, termination facts, and declared output artifacts. Timeout, crash, invalid output, unknown termination, or Boundary interruption is terminal for the step; no replay occurs. Boundary may terminate only an exact owned local process group whose identity can be re-established, and never relaunches the command.

On resume after a started but unfinished Command call, finish `BLOCKED_UNKNOWN` without another process launch.

---

## 15. Mutation path

Mutation accepts only an exact replacement manifest from an earlier accepted Worker output.

Implement:

1. request persistence and `STEP_STARTED`;
2. exact destination and authority validation;
3. before-state identity verification;
4. create-only before-images or absence markers;
5. exact replacement-byte persistence;
6. durable `MUTATION_INTENT`;
7. deterministic create, replace, or delete of regular files;
8. final identity verification and exact accepted references for declared Mutation outputs;
9. `STEP_FINISHED`.

A current-state mismatch before intent becomes `BLOCKED_UNKNOWN` without live mutation.

Before intent, deterministic preparation may resume. After intent without finish, never replay or roll back automatically; collect current evidence, finish `BLOCKED_UNKNOWN`, skip later steps, and proceed to Validator.

---

## 16. Recursive Task path

A Task step request binds:

- bounded child mission bytes, an exact earlier accepted mission-artifact reference, or an exact reference to the current parent mission;
- read and write authority equal to or narrower than the parent, never broader;
- exact input references;
- either an explicit narrower required-output contract or an exact reference to the parent required-output contract for a same-mission child;
- child Planner, Validator, allowed Worker, and allowed Command bindings equal to or narrower than the parent;
- canonical child path.

Support both Planner-owned forms without adding another step kind:

- **execution composition:** one Plan may contain several narrower child Tasks with stable sub-missions and may continue after their validated results;
- **evidence refinement:** after authorized evidence-producing steps, a Task step may create a child with the exact same mission, normally the same required-output contract, the original selected evidence, and newly accepted evidence for a fresh Planner;
- **hybrid:** one Plan may combine narrower child Tasks and a later same-mission evidence-refinement child.

The runtime does not classify the semantic form, impose a progress score, or enforce an arbitrary child-count or Task-depth budget. It validates only the declared identities, authority, references, schemas, and one-call lifecycle. Implement same-mission refinement through ordinary child creation, never by replaying Planner, mutating the accepted parent Plan, or adding loop state.

Append parent `STEP_STARTED` before child publication. Creating the child does not invoke the parent Validator. The child Validator runs at child completion; the parent Validator runs only after the parent Plan finishes or stops.

Create the complete child atomically when absent. When the exact child already exists, resume it depth-first. Reject conflicting child identity.

After child terminal state, verify the child result, terminal-output identities, types, provenance, parent binding, and either the accepted child validation-report reference or exact `VALIDATOR_UNAVAILABLE` evidence before appending parent `STEP_FINISHED`.

Every Task-step result records fixed system evidence fields for the child terminal result and, when available, the accepted child validation report; otherwise it records the exact validator-unavailable evidence. These fields are separate from declared child mission outputs. Later parent steps may consume fixed evidence from an earlier `COMPLETE` Task step only through explicit backward references.

Every non-`COMPLETE` child result reaches the parent Validator, and the same rule applies at every ancestor.

---

## 17. Validator path and future-Run evidence

Before Validator, capture exact final identities for every Mutation destination, every required workspace output, and every additional live workspace path explicitly requested by the Plan for final validation. Build one bounded final index containing the mission, required outputs, Plan or planning failure, every step result, skipped-step causes, verified child results and child validation reports, selected command and mutation evidence, accepted artifacts, and those final workspace identities.

Persist the request and append `VALIDATOR_STARTED` before the one Validator call. Invoke Validator once only when preparation succeeds.

Accept valid `COMPLETE`, `FAILED`, or `BLOCKED_UNKNOWN` judgments. Validate the report and terminal-output references, apply mechanical floors, and append `TASK_FINISHED`.

If no usable Validator result exists, append mechanical:

```text
TASK_FINISHED / BLOCKED_UNKNOWN / VALIDATOR_UNAVAILABLE
```

On resume after `VALIDATOR_STARTED` without `TASK_FINISHED`, use the same fallback without another Validator call.

Ensure a later `stt start` can accept the prior terminal result, Validator report, and selected artifacts through ordinary explicit initial-evidence sources. Do not add continuation, retry, or repair commands.

---

## 18. CLI and diagnostics

Canonical CLI:

```text
stt start --start-spec <path>
stt run --run-root <path>
stt status --run-root <path>
stt diagnose --run-root <path>
stt check-reachability
```

`start` creates a new Run and may enter Lead after root Task publication.

`run` reconstructs frozen control, acquires the writer lock, validates state, and resumes deterministic progress without changing bindings or repeating calls.

`status` and `diagnose` are read-only. `diagnose` reports invalid state and available forensic evidence but never repairs it.

`check-reachability` fails if the active CLI/package import graph reaches the old STT lifecycle.

Git is optional and never lifecycle authority.

---

## 19. Focused qualification set

Maintain one small test mapped to each architecture obligation. At minimum prove:

1. root success calls Planner and Validator exactly once;
2. child and grandchild depth-first success;
3. one sealed parent Plan executes several narrower child Tasks and continues using their verified results;
4. evidence-producing steps feed a same-mission child with the exact parent mission, normally the exact parent output contract, accumulated accepted evidence, and a fresh Planner;
5. a hybrid Plan combines narrower child Tasks and a later same-mission child without recalling or redispatching any earlier Planner;
6. child terminal results and accepted validation reports, or exact validator-unavailable evidence, are identity-bound fixed Task-step evidence, available through explicit backward references from later parent steps after a `COMPLETE` child, and present in every ancestor Validator index;
7. planning failure distinguishes `FAILED` from `BLOCKED_UNKNOWN` and reaches Validator with no invented Plan;
8. Worker failure and uncertainty skip later steps and reach Validator;
9. child failure reaches every ancestor Validator;
10. restart after each start event never repeats an STT dispatch to Planner, Worker, Command, or Validator; exact-owned process cleanup never relaunches work and does not signal a mismatched or reused process identity;
11. Validator unavailable produces mechanical `BLOCKED_UNKNOWN`;
12. a new Run can consume a prior result and Validator report as ordinary evidence;
13. one-time bootstrap evidence remains exact after original source changes;
14. path, identity, authority, and provenance violations fail closed;
15. Planner request contains the frozen allowed Command route catalog, and Command selects only an allowed route, uses Boundary-rendered typed argv without a shell, and receives only disposable materialized paths;
16. pre-intent Mutation resumes while post-intent Mutation never replays;
17. Task publication, ledger torn-tail handling, and interior-corruption rejection;
18. frozen runtime survives target-workspace STT source modification;
19. active reachability excludes the old lifecycle.

Also run:

- the full focused STT suite;
- deterministic fake-provider qualification;
- integration tests for each supported live adapter;
- the full repository suite;
- diff and whitespace checks.

Do not replace these proofs with a large scenario registry or meta-test framework.

---

## 20. Implementation sequence

Use the smallest vertical order that keeps each state executable:

### Slice 1 — durable root success

Canonical schemas, store, lock, Task publication, ledger, fake provider, one Planner call, one Worker step, one Validator call, restart reconstruction.

### Slice 2 — failure shortening and no-call-repeat resume

Planning failure, Worker failure/uncertainty, skipped steps, Validator unavailable, all crash boundaries around start events.

### Slice 3 — recursive Tasks, disposable Commands, and Mutation

Multiple narrower children, same-mission evidence refinement, hybrid depth-first execution, child-report propagation, ancestor validation, command materialization, mutation intent and post-intent uncertainty.

### Slice 4 — frozen runtime, CLI, old-lifecycle cutover, and live adapters

Runtime freezing, diagnostics, reachability guard, active entry-point replacement, provider-specific supported-host integration.

### Slice 5 — qualification and cleanup

Run all focused and repository tests, remove dead compatibility paths, inspect the final import graph, and record exact evidence.

A slice is complete only when its end-to-end behavior and restart boundary pass.

---

## 21. Stop conditions

Stop rather than inventing behavior when:

- architecture and role contracts disagree;
- live-provider isolation cannot be proved on the claimed host;
- a required old primitive is not understood well enough to reuse;
- active old-lifecycle reachability remains;
- a ledger state has multiple plausible interpretations or is `INVALID_RUN`;
- full repository regression cannot be explained or safely repaired within scope.

Record the conflict and evidence. Do not hide it with retries, compatibility code, or broader automation.
