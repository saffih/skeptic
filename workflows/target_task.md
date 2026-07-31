# Target Task — provider-neutral deterministic workflow

This is the provider-neutral authoritative workflow when a host recognizes the
`TT:` trigger. `CLAUDE.md` and `.claude/agents/` configure only the Claude Code
adapter; they are not the sole trigger or orchestration authority. Any host
that can read this workflow, invoke canonical roles through an adapter, write
task-root artifacts, and return compact receipts may implement it.

Provider adapters are replaceable. The Boundary consumes canonical references
and normalized receipts only; it never parses Claude, Codex, or another host's
events. Provider evidence is immutable, content-addressed, and correlated to
exactly one durable operation. Hidden host context remains `UNKNOWN` unless
independently proved. Qualification of one adapter does not qualify another;
no adapter is mandatory for the deterministic core.

## Honest boundary

Direct Claude Code submission necessarily places the initial user message in the
receiving host session. Therefore:

- `INITIAL_MISSION_CONTEXT_ISOLATION: UNAVAILABLE_FOR_DIRECT_TT`;
- bootstrap the exact suffix immediately;
- after bootstrap, the durable Lead carries only bounded status and references;
- `HIDDEN_HOST_CONTEXT_ISOLATION: UNKNOWN`.

Do not claim that the initial mission was hidden from the host. The MVP's
reference-only guarantee begins after bootstrap and is observable at role-return
and durable-state boundaries.

## Supported scope

One source repository, one task ID, one canonical linear Plan, one current step,
one unresolved operation, sequential execution, and explicit `ADVANCE`, `RETRY`,
`RECOVER`, or `STOP`. No DAG, parallel workflow engine, daemon, database, queue,
or provider SDK is part of this MVP.

## Task root and trigger

1. Ignore whitespace before `TT:`. Preserve the exact Unicode suffix after it;
   reject only a suffix containing no non-whitespace character.
2. Resolve `TARGET_TASKS_ROOT`; default to `~/.skeptic/target-tasks`.
3. Generate a safe unique task ID matching
   `[A-Za-z0-9][A-Za-z0-9._-]{0,63}`.
4. Call `concepts.target_task.trigger.bootstrap_task` before planning.
5. Record only the returned task ID, task-root reference, mission hash/size, and
   ledger head in durable Lead state. Do not repeat the mission body.

`TARGET_TASKS_ROOT/TASK_ID` is the sole authority for every run artifact. A
fresh session calls `rediscover_task(TARGET_TASKS_ROOT, TASK_ID)` and validates
the exact mission identity, ledger chain, sealed Plan, and complete cursor.

## Host adapter dispatch

Invoke canonical roles through `concepts.target_task.host_adapter.TargetTaskHostAdapter`:

- `planner` — one complete canonical Plan;
- `reviewer` — one independent complete RunSkeptic review;
- `worker` — one sealed Plan step;
- `command` — one bounded command operation.

An adapter maps these roles to provider identifiers, constructs the bounded
request, executes or ingests one invocation, persists raw provider evidence,
validates provider-specific evidence, and normalizes exactly one compact host
receipt. Duplicate, missing, ambiguous, or body-bearing evidence fails closed.
The generic recorded-host adapter is deterministic; Claude and Codex adapters
are separate qualification paths.

## Cost-aware routing

Follow `agents/model_routing_policy.md`.

- Start with the current/economical reliable model and medium or lower effort.
- Do not hardcode or automatically escalate to Opus or XHIGH.
- Use premium routing only after observed insufficiency and an explicit owner
  checkpoint unless the exact premium call was pre-authorized.
- Record requested and observed routing separately; hidden values are `UNKNOWN`.
- Return to the economical route after any bounded premium judgment.

## Immutable role protocol

For each role operation create under the task root:

- `requests/<operation-id>.json` — immutable bounded request;
- `results/<operation-id>.*` — complete substantive result;
- `dispatch/<operation-id>.json` — canonical dispatch evidence;
- `receipts/<operation-id>.json` — compact host receipt.

The canonical request itself has exact fields:

```text
schema_version, task_id, operation_id, attempt, role, step_id, objective,
scope, authority, prohibitions, success_criteria, task_artifact_references,
source_artifact_references, result_relative_path
```

Task-artifact references are validated against `TASK_ROOT`; source-evidence
references are validated separately against the current source worktree. This
explicit split permits bounded code evidence without turning the worktree into
a second task-state authority or copying source bodies into durable Lead state.

Canonical dispatch evidence fields:

```text
schema_version, task_id, operation_id, attempt, role, step_id, request_ref
```

Canonical host receipt fields:

```text
schema_version, task_id, operation_id, attempt, role, step_id, status,
summary, request_ref, result_ref, dispatch_evidence_ref, synthetic
```

Production requires `synthetic=false`. Before any state change, call
`validate_host_role_receipt` through `record_validated_host_outcome` with the
expected task root, source root, task, operation, attempt, role, step, and request reference. Boundary
must reject extra/body fields, oversized returns, wrong bindings, bad artifact
identity, symlink paths, noncanonical dispatch evidence, and synthetic
production receipts.

## Mandatory lifecycle

```text
exact mission persisted
-> independent Planner
-> complete canonical Plan
-> Plan RunSkeptic Fix Loop
-> three consecutive qualifying unchanged passes
-> exact Plan sealed
-> execute every sealed Plan step sequentially
-> real-host smoke is the final open step when qualifying the implementation
-> deterministic validation
-> candidate commit/tree frozen
-> final read-only RunSkeptic Find Loop
-> integration only when clean and mechanically possible
-> remote commit/tree verification
-> compact terminal receipt
```

### 1. Planner and canonical Plan

Dispatch `target-task-planner` using mission and repository evidence references.
The Planner writes one canonical JSON Plan accepted by
`concepts.target_task.contracts.parse_plan_bytes`. The Plan binds:

- schema version;
- unique Plan ID;
- task ID;
- mission SHA-256;
- ordered unique steps with role and testable success criteria.

A material finding requires a new Planner dispatch and complete replacement
Plan. Never patch a Plan in place.

### 2. Plan RunSkeptic Fix Loop

For every pass, dispatch a fresh `target-task-reviewer` that freshly reads
current root `skeptic.md`, runs the complete recipe and every required Thinker,
and writes full review, finding set, and formal receipt under the task root.

Validate each receipt with:

```python
boundary.advance_fix_loop(
    state,
    receipt,
    task_id=TASK_ID,
    material_findings_reference=FINDINGS_REFERENCE,
    source_root=SOURCE_REPOSITORY,
    artifact_root=TASK_ROOT,
)
```

A repair, delta review, changed Plan/source/companion/finding identity, open item,
or invalid receipt resets the count. Seal only after
`fix_loop_complete(state)` is true on three unchanged qualifying passes.

Seal with `store.persist_plan_artifact`. Record exact Plan path, SHA-256, byte
size, schema version, and ordered step IDs. Once sealed, never edit, replace,
reorder, extend, reinterpret, or repair it in the same run.

### 3. Sequential execution and durable cursor

Initialize with `boundary.new_step_cursor_from_plan`. Use only the combined
durable Boundary APIs below; generic cursor persistence is initial serialization
only.

For each step:

1. `admit_and_persist_operation` loads the latest cursor and sealed Plan,
   validates the role, creates a unique operation, and persists the request,
   dispatch evidence, admitted cursor, and ledger event.
3. Dispatch the exact role named by the sealed Plan.
4. `accept_and_persist_operation_outcome` loads and validates all durable
   request, dispatch, receipt, result, and output references, then persists the
   outcome cursor, compact receipt, and ledger event.
6. COMPLETE becomes `STEP_AWAITING_ADVANCE`; it never moves automatically.
7. Luna issues `ADVANCE`; `advance_and_persist_step` operates only on the latest
   durable `AWAITING_ADVANCE` event, revalidates its host receipt, and consumes
   exactly that successful operation once. Duplicate advance fails closed.
8. FAILED permits bounded `RETRY` or `STOP`; retry uses new operation and files.
9. UNKNOWN is STOP-only at operation level. Evidence-bound recovery exists only
   for a durably BLOCKED high-level task.

High-level phase transition from `STEP_EXECUTING` to `STEP_VALIDATED` is legal
only when the persisted cursor is `EXECUTION_COMPLETE` for all sealed steps.

### 4. Commands

Use `concepts.target_task.command.run_task_command` for deterministic commands.
Mutating commands require a freshly observed clean Git preflight, explicit argv,
a timeout, and mutation authority. Logs are private, immutable, and task-root
relative. A dirty worktree cannot produce an admissible mutation preflight.

### 5. Deterministic validation and freeze

After all steps, mechanically verify:

- task and mission identities;
- strict canonical ledger and one task ID throughout;
- exact sealed Plan identity and all ordered steps accepted once;
- complete cursor and no unresolved operation;
- request/result/dispatch/receipt artifact hashes and sizes;
- no child modification of task-control files;
- role-return body rejection and mismatch negative probes;
- focused tests and full repository tests;
- source repository/worktree preservation;
- exact candidate commit and tree.

Persist a canonical task-root `validation_receipt` artifact with exact fields `schema_version`, `task_id`, `gate`, `status`, and `subject_sha256`; `gate` is `deterministic_validation`. Pass its artifact reference and task ID to Boundary. Boundary will not freeze from a bare boolean or unbound path. Freeze the exact candidate; no candidate change is legal afterward.

### 6. Final RunSkeptic Find Loop

Dispatch a fresh `target-task-reviewer` per complete read-only pass. Validate and
advance using `boundary.advance_find_loop(state, receipt, task_id=TASK_ID,
material_findings_reference=FINDINGS_REFERENCE, source_root=SOURCE_REPOSITORY,
artifact_root=TASK_ROOT)`. Stop only after three consecutive complete reviews
add no meaningful finding and make no material change to an existing finding.

Convergence may retain a stable nonempty finding set, but OPEN_ITEMS or any open
canonical material finding blocks integration. Convergence is not cleanliness. Do not
repair after freeze; repair is a new ordinary task/run.

### 7. Integration and close

Boundary admits integration only when the Find Loop is complete, `OPEN_ITEMS` is
empty, the material finding set is empty, and a canonical task-root
`validation_receipt` whose gate is `integration` binds the reviewed subject.
Candidate and remote manifests are exact canonical schemas; remote expected and
observed commit/tree must match the candidate before close. Bare PASS mappings
are rejected.

## Real-host qualification smoke

`scripts/target_task_smoke.sh` runs a disposable, remote-free clone with a cheap
configurable model, low effort, bounded turns, wall-clock timeout, explicit
Agent permission, an added external task directory, and no network/push tools.
`scripts/validate_target_task_smoke.py` must mechanically validate the task root;
a nonempty provider output file is not success.

This workflow claims only compliant-host observable protocol validation; it does
not claim hard platform isolation. Until that smoke passes on the exact
candidate, report `MVP_STATUS: STATICALLY_VALIDATED_AWAITING_REAL_HOST_SMOKE`
and use `TT:` only in disposable experiments.

## Terminal receipt

Return only compact status and references, including task ID/root, mission and
Plan identities, current/final cursor, test evidence, smoke evidence, candidate
commit/tree, review-loop counts, routing evidence reference, integration/remote
verification, `INITIAL_MISSION_CONTEXT_ISOLATION`,
`BOUNDARY_PROTOCOL_ISOLATION`, and `HIDDEN_HOST_CONTEXT_ISOLATION`.

## Working controller surface

The provider-neutral operational surface is `scripts/target_task.py`, backed by
`concepts/target_task/controller.py`. Its commands are `bootstrap`, `status`,
`prepare`, `accept`, `advance`, `retry`, `stop`, `handoff`, `resume`, and
`validate`. Every response is bounded canonical JSON containing control fields
and references only.

A sealed Plan becomes mechanically executable only when the exact Plan SHA has
a canonical companion at `plans/execution/<sealed-plan-sha256>.json`. The
companion binds the exact ordered Plan steps to instruction, input, retrieval,
output-contract, route, authority, prohibition, validation, and result-manifest
references. The sealed Plan remains the lifecycle identity; the companion is not
a second Plan or state machine.

Provider routing uses canonical roles/model classes. Concrete provider roles and
model aliases remain adapter-owned. Route resolution does not prove execution;
actual routing is established only by persisted raw provider evidence. An
unavailable economical top-level Lead route returns `RELAUNCH_REQUIRED` instead
of claiming an in-place model change.

`scripts/generic_host_smoke.py` is the credit-free execution proof. It must
complete two separately admitted and accepted Worker/Command steps, resume from
`TASKS_ROOT + TASK_ID`, and finish `STEP_VALIDATED`. It must report `closed:
false` and `live_provider_not_run: true`; terminal `CLOSED` remains gated by the
final Find Loop, integration, and remote verification.
