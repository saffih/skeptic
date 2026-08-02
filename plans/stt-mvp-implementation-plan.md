# STT MVP Complete Implementation Plan

**Status:** Complete implementation plan; ready for execution after owner acceptance
**Architecture source of truth:** `plans/stt-mvp-architecture-plan.md`
**Repository:** `saffih/skeptic`
**Planning base:** `ec9e8771e4bf9a4ecd03d3d9cd5ff0b1486d9887` plus the documentation-only commit that installs the corrected architecture plan
**Historical parent:** `31451c8f45d5e9f2fe63434b37a2b7b02626a403`
**Archived overbuilt history:** `archive/target-task-overbuilt-20260802`
**Implementation authority:** STT MVP only

This document does not restate the architecture. Every normative rule —
Task lifecycle, component responsibilities, retry rule, command and mutation
semantics, crash reconciliation, ledger events — lives in
`plans/stt-mvp-architecture-plan.md` and is referenced here by section number.
This document defines build order, the four vertical proofs, the smallest
necessary modules, and proof-of-done criteria.

---

## 1. Objective

Implement the smallest complete STT MVP described by the architecture plan
(architecture §2, §3). The implementation stops when the four vertical
proofs (§3 below) and their 15 qualification scenarios (§46 below) pass. It
must not restore, adapt, or maintain compatibility with the archived Target
Task system.

---

## 2. Starting conditions

Before implementation:

1. verify current branch descends from the final documentation commit containing the corrected architecture plan and this implementation plan;
2. verify the architecture file hash and record it in the first implementation commit message;
3. do not modify the archive;
4. do not merge or copy the old Target Task implementation wholesale.

---

## 3. Build order: four vertical proofs

Do not build horizontal frameworks (a generic retry engine, a generic
recovery framework, a generic diagnostics layer) before Proof 1 passes
end to end. Each proof is a complete vertical slice through Lead, Boundary,
the relevant role(s), and the ledger — not a layer shared across all four.

### Proof 1 — One root Task, fake semantic provider

Prove the complete path in architecture §2–§3, §12, §19, §20, §23 for a
single root Task with no children: Run and root Task creation; ledger
events; Planner returns one Plan; Worker returns one artifact; Boundary
materializes it; Validator finishes the Task; Lead receives compact
receipts only.

### Proof 2 — Recursive Task and recovery

Prove, using architecture §17, §21, §22, §26: child and grandchild Task
creation; deterministic depth-first execution; authority narrowing; child
completion before parent continuation; child failure with child and
ancestor validation; restart after child completion; adoption of a complete
immutable prepared result when its ledger event is missing (architecture
§26.2, §26.3).

Do not generalize beyond serial depth-first recursion. No scheduler, no
waiting protocol, no child registry.

### Proof 3 — Authorized effects

Prove, using architecture §15, §16, §26.4: one explicitly authorized
retry-safe command with known success and known failure outcomes; staged
file mutation with a durable `MUTATION_INTENT`; successful mutation
verification; interruption after intent resulting in `BLOCKED_UNKNOWN`; no
automatic uncertain-mutation replay.

### Proof 4 — Dogfood

Prove, using architecture §8, §29, §33: frozen runtime; one real semantic
provider adapter (Claude Code) alongside the fake provider; immutable Run
specification; STT performs a small change to its own source tree; the
runtime executing the Run does not change underneath the Run; the final
Validator evaluates the actual result.

A fake provider plus one proven real provider adapter is sufficient for
MVP. A second live adapter is not required before MVP completion.

---

## 4. Run specification

One immutable root Run specification is created at `stt start` and never
changed by `stt run` (architecture §29, §31). It contains only what is
needed to start: workspace root, Mission, root authority, required outputs,
initial evidence references, Planner/Worker/Validator routes, retry limits
(`maximum_attempts`), authorized commands and their `replay_safe`
declarations, and size/resource limits. `run.json` is the one place these
values live.

---

## 5. Target file map

### 5.1 Production package

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
    └── claude_code.py
```

Every module in this list exists to serve one of the four vertical proofs;
none is speculative. The recorded launcher (architecture §33) is
provider-neutral; Claude Code is the one mandatory live adapter (Proof 4)
and fails closed before launch without `--allow-live-provider`.

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
├── test_cli.py
└── test_qualification.py
```

Each module holds the focused unit tests for the production module of the
same stem, proving that module's contribution to the proof it supports. Use
the repository's existing test runner and naming conventions where they
differ.

### 5.4 Optional documentation pointer

Only if required for discoverability, `AGENTS.md` may receive one compact
pointer: `STT runtime and architecture -> plans/stt-mvp-architecture-plan.md
and concepts/stt/`. Do not rewrite the current general Lead, Planner,
Boundary, or Task Prompt contracts to behave like STT.

### 5.5 Excluded as runtime architecture

Do not import or depend on `archive/target-task-overbuilt-20260802/` or the
old Target Task lifecycle in `agents/lead_agent.md`, `agents/planner.md`,
`agents/boundary_agent.md`, `workflows/task_prompt.md`. Reimplement small
deterministic primitives from first principles rather than reuse code that
carries old contracts or state.

---

## 6. Cross-cutting implementation rules

Follow architecture §7, §24, §25 for canonical JSON, hash identities
(lowercase SHA-256), and create-only/atomic publication. Provide one
canonical serializer and one shared path-admission primitive; do not
duplicate either. Use a small typed error hierarchy (for example `STTError`,
`InvalidRun`, `InvalidTask`, `InvalidPlan`, `InvalidLedger`,
`AuthorityViolation`, `ArtifactMismatch`, `ProviderFailure`,
`WorkspaceSafetyError`, `MutationUnknown`) mapped by the CLI to bounded
output. Avoid a generalized error-state machine. Prefer the standard
library (`dataclasses`, `pathlib`, `json`, `hashlib`, `subprocess`,
`tempfile`, `os`, `shutil`, `stat`, `time`, `uuid`, `fcntl`); add no
dependency unless it materially simplifies correctness.

---

# Slice 1 — Canonical files and ledger (supports Proof 1)

## 7. Goal

Implement the smallest trustworthy persistent primitives per architecture
§7, §24, §25: canonical JSON; artifact references; hash-chained JSONL
ledger (architecture §24 defines the event schema and vocabulary); create-only
publication; one OS-backed exclusive Run writer lock; narrow torn-tail
diagnosis (architecture §25.1).

## 8. Production files

```text
concepts/stt/ledger.py
concepts/stt/run_lock.py
concepts/stt/receipt.py
```

## 9. Tests

Focused unit tests in `test_ledger.py` and `test_run_lock.py` prove:
canonical round-trip and hash-chain integrity (valid chain passes,
tampering fails); the torn-trailing-fragment diagnosis and truncation from
architecture §25.1; and single-writer exclusivity.

## 10. Commit acceptance

Focused tests pass. No Task orchestration exists yet.

Commit: `stt: add canonical data and ledger core`

---

# Slice 2 — Task and Plan contracts (supports Proof 1, Proof 2)

## 11. Goal

Implement Task paths; immutable `task.json`; immutable `mission.md`; Plan
schema; the four exact step kinds; authority validation; cursor derivation
from Plan and ledger — per architecture §10, §11, §13–§18, §25.

## 12. Production files

```text
concepts/stt/task.py
concepts/stt/plan.py
concepts/stt/workspace.py
concepts/stt/contracts/planner.md
concepts/stt/contracts/worker.md
concepts/stt/contracts/validator.md
```

Before Task creation, implement the common path-admission primitive and
bounded `workspace-index.json` generation in `workspace.py` (architecture
§6 bootstrap step 11, §28). It never silently truncates and never grants
authority.

## 13. Task creation

`create_task(task_root, run_identity, task_id, mission_bytes, authority,
role_bindings, initial_inputs, required_outputs, parent_binding=None)`
follows the atomic same-parent temporary-directory publication protocol in
architecture §25.1. Root and child Tasks use the same protocol. Temporary
residue is non-authoritative and is never adopted.

## 14. Plan schema and validation

Implement the four step-kind schemas from architecture §13–§17 as
dataclasses or typed dictionaries. Validate per architecture §13: unique
stable step IDs, no future references, resolved named-output references,
child authority subset, path admission. Plan acceptance persists the raw
provider return, publishes `plan.json`, and appends `PLAN_ACCEPTED`; on
resume, a complete valid Plan is never re-requested from the Planner
(architecture §26.2).

## 15. Cursor derivation

Implement a pure function `derive_task_state(task_root) -> TaskState`
returning one of `NEEDS_PLAN`, `NEEDS_STEP`, `NEEDS_VALIDATION`,
`TERMINAL`, `INVALID`, and the exact next step. No mutable cursor file.

## 16. Tests

Focused unit tests in `test_task.py` and `test_plan.py` prove: Task
creation and child authority narrowing/expansion-rejection; one valid Plan
per step kind plus the corresponding rejections (unknown kind, duplicate
ID, future reference, unauthorized path); an accepted Plan cannot be
replaced; state derivation before and after each ledger event.

## 17. Commit acceptance

All Slice 1 and Slice 2 tests pass.

Commit: `stt: add task and plan contracts`

---

# Slice 3 — Provider invocation and Boundary (supports Proof 1)

## 18. Goal

Implement one mandatory Boundary façade (architecture §19) around Planner,
Worker, and Validator calls, deterministic operations, child creation and
return, persistence, and compact receipts.

## 19. Production files

```text
concepts/stt/launcher.py
concepts/stt/boundary.py
concepts/stt/providers/__init__.py
concepts/stt/providers/fake.py
```

`launcher.py` is the provider-neutral invocation-recording wrapper Boundary
uses for every role call. The live `claude_code.py` adapter is built and
qualified in Slice 6 (Proof 4); Slice 3 and Proof 1 need only the fake
provider.

## 20. Provider protocol and retry rule

Define the smallest interface, `Provider.invoke(request) -> ProviderReturn`,
with the request/return fields from architecture §12 and §29. Apply
architecture §12's one retry rule uniformly across Planner, Worker, and
Validator: only a confirmed terminated timeout within finite
`maximum_attempts` may retry; every other completed provider return is
persisted and not retried. Provider unavailability never creates a fake
semantic result (architecture §19.3).

The fake provider reads deterministic fixture responses keyed by dispatch
ID or role, and supports valid and invalid returns per role, timeout,
malformed/mismatched/oversized returns. It is the qualification provider
for Proofs 1–3.

## 21. Boundary API

```python
plan_task(task_ref)
execute_worker_step(task_ref, step_ref)
execute_command_step(task_ref, step_ref)
execute_mutation_step(task_ref, step_ref)
create_child_task(task_ref, step_ref)
finish_task_step_from_child(task_ref, step_ref, child_ref)
validate_and_finish_task(task_ref)
```

The Lead calls no provider or workspace function directly (architecture
§20). Boundary resolves declared inputs through the workspace path-
admission primitive (architecture §19.1) and writes `request.json` before
every invocation; requests contain references, not bodies (architecture
§28). Follow the Planner, Worker, and Validator Boundary paths exactly as
specified in architecture §12.1, §14, §23, including the mechanical
`BLOCKED_UNKNOWN` finish when Validator's attempt budget is exhausted
(architecture §19.3) — this is qualification scenario 13 (§46).

## 22. Tests

Focused unit tests in `test_boundary.py` prove: unique dispatch IDs and
mismatched-return rejection; malformed Plan never becomes accepted state;
workspace path admission rejects `.git`, `.stt`, symlinks, special files,
and containment escapes for semantic roles; Worker cannot write outside
assigned scope; Validator receives no Planner/Worker conversation; Validator
`COMPLETE` is rejected when a step failed; provider outages remain
nonterminal and resumable; receipts carry no substantive bodies.

## 23. Commit acceptance

Slices 1–3 pass using the fake provider only. `test_provider_claude_code.py`
and `test_launcher.py` for the live adapter are owned by Slice 6 (Proof 4)
and do not gate this commit.

Commit: `stt: add provider boundary`

---

# Slice 4 — Mechanical Lead and recursive Tasks (supports Proof 1, Proof 2)

## 24. Goal

Implement the one Lead loop (architecture §20) and durable DFS recursion
(architecture §21, §22).

## 25. Production files

```text
concepts/stt/lead.py
```

Use `task.py` and `boundary.py`; do not duplicate lifecycle logic.

## 26. Lead API and child handling

`run_until_terminal(run_root)` / `advance_once(root_task_ref)` implement
architecture §20.1's algorithm exactly, including the Task-step child
handling from architecture §17 and the crash/resume cases from architecture
§21 and §26 (Cases A–E: child absent, child created but unfinished, child
finished but parent step unfinished, parent step finished, conflicting
child identity). No separate child-state enum; no direct
"propagate failure" shortcut — ancestor Validators must actually run
(architecture §22).

## 27. Tests

Focused unit tests in `test_lead.py` and `test_recursive_tasks.py` prove
the exact depth-first event order (root Planner → root step start → child
Planner → child steps → child Validator → parent step finish → root later
step → root Validator) and each crash/resume case from §26 above.

## 28. Commit acceptance

Recursive lifecycle tests pass. This completes Proof 1 and Proof 2 end to end.

Commit: `stt: add mechanical lead and recursive tasks`

---

# Slice 5 — Command and workspace mutation safety (supports Proof 3)

## 29. Goal

Implement the one canonical read/write path admission primitive, staged
replacement validation, authorized non-mutating commands, before-images,
mutation intent, deterministic installation, and uncertainty handling —
per architecture §15, §16, §26.4.

## 30. Production files

```text
concepts/stt/workspace.py  # extend Slice 2's path/index primitive with file and tree identities
concepts/stt/command.py
concepts/stt/mutation.py
```

## 31. Implementation

Follow architecture §15 (command runner: authorized-argv only, resolved
executable identity, sanitized environment, no shell, timeout,
`COMPLETE`/`FAILED`/`BLOCKED_UNKNOWN` outcomes, replay only under the
confirmed-timeout-and-`replay_safe` policy) and architecture §16 (mutation
sequence: validate manifest, re-observe destinations, write before-images,
append durable `MUTATION_INTENT` before any live write, install per-file
atomically, verify, finish). File identities include mode bits so a
mode-only change is detected as an unauthorized mutation. On resume, a
`MUTATION_INTENT` without `STEP_FINISHED` is never replayed — observe
current state, finish `BLOCKED_UNKNOWN`, run Validator (architecture
§26.4). Add deterministic test hooks around the mutation sequence solely to
prove this resume behavior, not as a production recovery framework.

## 32. Tests

Focused unit tests in `test_command.py` and `test_mutation_interruptions.py`
prove: create/replace/delete with before-image exactness; out-of-scope,
`.git`/`.stt`, traversal, symlink, and special-file rejection; interruption
before intent permits clean retry, interruption after intent never
replays; command timeout, nonzero exit, and the replay-safety matrix from
architecture §15; plain-directory and Git-repository success without using
Git as authority.

## 33. Commit acceptance

Workspace safety and interruption matrix pass. This completes Proof 3.

Commit: `stt: add safe workspace mutation`

---

# Slice 6 — Frozen runtime and dogfooding (supports Proof 4)

## 34. Goal

Implement one frozen runtime per Run and prove self-modification safety
(architecture §8).

## 35. Production files

```text
concepts/stt/runtime.py
concepts/stt/bootstrap.py
concepts/stt/providers/claude_code.py
```

## 36. Implementation

Follow architecture §8 for the runtime allowlist (`collect_runtime_files`,
one maintained literal path list, no glob reconstruction), `freeze_runtime`,
and `reconstruct_runtime`. Persist source provenance as informational
metadata only; the bundle manifest, not Git, is authoritative for
reconstruction correctness.

Implement `claude_code.py` and `launcher.py` as thin adapters over the
common recorded-launcher contract (architecture §33): fails closed before
launch without `--allow-live-provider`; deterministic controlled-executable
tests qualify argv construction, request/return persistence, timeout
classification, and truthful `UNKNOWN` routing without a paid live call.

## 37. Dogfood scenario

A fake-provider root mission whose Plan: prepares a change to one active
STT source file, installs it via mutation, verifies it, continues and
validates generation A successfully, then a new Run freezes generation B
from the changed workspace. Prove generation A's runtime manifest and
imports remain unchanged and unaffected by deleting the target workspace's
STT source, while generation B's runtime identity includes the new source.

## 38. Tests

Focused unit tests in `test_runtime.py`, `test_launcher.py`, and
`test_provider_claude_code.py` prove: the exact literal allowlist (no
glob); manifest and bundle verification; source modification/deletion does
not affect the active runtime; generation B sees later source.

## 39. Commit acceptance

Frozen runtime, dogfood, and live-adapter tests pass. This completes Proof 4.

Commit: `stt: add frozen runtime`

---

# Slice 7 — CLI

## 40. Goal

Expose the MVP without adding orchestration complexity.

## 41. Production files

```text
concepts/stt/cli.py
scripts/stt.py
```

## 42. Commands

Implement `start`, `run`, `status`, `diagnose` exactly per architecture
§31, including: `provider` required and `fake`/`claude-code` authorization
rules; `live_provider_authorized` frozen at start; freeze-then-lock-then-
publish ordering; `status`/`diagnose` are strictly read-only and report
`RUN_BUSY` under a shared nonblocking lock without reading changing state.

Use canonical JSON and readable text output modes; no full logs or bodies
on stdout. Define a small stable exit-code set (for example: `0` COMPLETE
or successful read-only query, `2` FAILED, `3` BLOCKED_UNKNOWN, `4`
INVALID_RUN, `5` USAGE_ERROR).

## 43. Tests

Focused unit tests in `test_cli.py` prove: start to `COMPLETE`/`FAILED`/
`BLOCKED_UNKNOWN` with the fake provider; resume of an unfinished child;
no body leakage to stdout; competing writer rejected; `status`/`diagnose`
report `RUN_BUSY` while a writer is active.

## 44. Commit acceptance

CLI scenarios pass.

Commit: `stt: add cli and diagnostics`

---

# Slice 8 — Qualification and cleanup

## 45. Goal

Prove the 15 end-to-end qualification scenarios below, remove accidental
complexity, and stop.

## 46. Qualification scenarios

Create one top-level qualification module,
`tests/concepts/stt/test_qualification.py`, composing existing helpers
rather than duplicating low-level assertions. Prove exactly these 15
end-to-end scenarios, matching the four proofs above. Do not add further
named or numbered end-to-end scenarios beyond this list; together they are
the sole qualification catalogue for the MVP (architecture §34).

1. root Task completes
2. invalid Planner response retries successfully
3. Planner retry exhaustion proceeds to Validator
4. invalid Worker response retries successfully
5. Worker retry exhaustion proceeds to Validator
6. child Task completes before parent continuation
7. child failure triggers child and ancestor validation
8. complete immutable semantic result is adopted after a crash before its ledger commit
9. explicitly authorized retry-safe command succeeds
10. known command failure is recorded and validated
11. staged mutation succeeds
12. interruption after MUTATION_INTENT becomes BLOCKED_UNKNOWN
13. Validator retry exhaustion produces mechanical BLOCKED_UNKNOWN
14. frozen-runtime self-modification succeeds
15. Lead receives compact receipts only

Focused unit tests for the modules that support each scenario live in the
per-module test files listed in §5.3, referenced briefly under the slice
that builds them; they are not repeated here as a second catalogue.

## 47. Supporting checks

Add: a deterministic reachability test that active STT modules do not
import archived Target Task namespaces or reference archived lifecycle
terms (`Fix Loop`, `Find Loop`, `three-pass`, `ADVANCE`, `candidate
commit`, `rollback`, `scheduler`) as active behavior; context-bound tests
in `test_context_bounds.py` asserting each role receives only the bounded
context architecture §28 specifies. Run the focused STT suite, the full
repository test suite, and the repository's existing lint/format checks
before the final commit.

## 48. Complexity review

Before final commit, inspect module count, duplicated schema or path
logic, unused abstractions, dead compatibility code, and unbounded context.
Remove mechanisms not required by an invariant or one of the four proofs.
Do not optimize for an arbitrary line-count target; explain any unusually
large module.

## 49. Final commit

Commit: `stt: qualify mvp invariants`

Stop after the 15 qualification scenarios and the full repository suite
pass. Do not begin later recovery, concurrency, rollback, publication, or
generalized orchestration work.

---

## 50. Definition of done

The STT MVP is done when:

1. the corrected architecture file remains the source of truth;
2. all planned production files are implemented or deliberately consolidated;
3. all four vertical proofs (§3) pass with the 15 qualification scenarios (§46);
4. focused STT tests and the full repository test suite pass;
5. active STT has no archived Target Task reachability;
6. plain-directory and Git-directory scenarios both pass;
7. competing writer and torn-tail proofs pass; Task publication never adopts temporary residue;
8. root, child, and grandchild lifecycle proofs pass, including provenance and ancestor-validation guarantees;
9. mutation uncertainty is never replayed;
10. frozen runtime dogfood passes with the fake provider plus the one Claude Code live adapter;
11. CLI start/run/status/diagnose pass;
12. no compatibility or deferred feature was added;
13. all Planner, Worker, and Validator retry paths have finite `maximum_attempts` and require `TIMED_OUT_CONFIRMED_TERMINATED`;
14. the recorded launcher and Claude Code adapter tests pass with `--allow-live-provider` enforcement and no paid call;
15. implementation stops.

---

## 51. Final execution instruction

```text
Implement only plans/stt-mvp-architecture-plan.md, using this file as the
ordered build map.

Begin from the final documentation commit containing both plans.

Build the four vertical proofs in order: root Task (fake provider),
recursion and recovery, authorized effects, dogfood. Do not build a
horizontal framework (generic retry engine, generic recovery layer,
generic diagnostics) ahead of the proof that needs it.

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

Stop when the four proofs, their 15 qualification scenarios, and the full
repository test suite pass. Do not continue into later features.
```
