# Target Task reference contract

Reference-only illustration of the Target Task lifecycle: `TT: <mission>` →
Planner → Plan RunSkeptic Fix Loop → sealed plan → execution of the sealed
plan exactly once → deterministic validation → frozen candidate → read-only
RunSkeptic Find Loop → integration only if clean and mechanically possible →
close with a compact receipt. No live agent runtime in this repository
executes this automatically; an invoking runtime implements equivalent
behavior against these contracts, which are proven here by tests with an
injected executor.

## Two roots

Every function in this package that touches the filesystem takes one or
both of:

- **`repository_root`** — the real Git repository. `capabilities.body_state`
  requires every `ARTIFACT_REFERENCES` entry, including
  `SEALED_PLAN_REFERENCE` itself, to resolve as a real file under this root
  (`body_state.py` lines 72-88). A sealed Plan is therefore a real,
  `repository_root`-relative file — for this task, for example, a plan
  committed under `plans/` — not a workspace-only artifact.
- **`workspace_root`** — an external directory, disjoint from
  `repository_root`, exactly as `capabilities.restart_admission` already
  requires (`_validate_roots` rejects a workspace nested in the repository).
  Mission text, ledger events, step results, command logs, and checkpoints
  are workspace-only bookkeeping. They are never placed in a `body_state`
  object's `ARTIFACT_REFERENCES` list, because that list only resolves
  against `repository_root`.

This is a real constraint discovered by independent review of an earlier
draft of this design (which proposed representing the ledger head as an
`ARTIFACT_REFERENCES` entry): `body_state.validate_state_bytes` validates
every reference in one object against one root, so a single Luna receipt
cannot mix a real-repo reference (the sealed plan) with a workspace-only
reference (the ledger head) even though both are legal `artifact_type`
values individually. The resolution is that Luna's receipt never needs a
literal ledger-head reference — Boundary is the sole ledger reader/writer
and derives `NEXT_AUTHORIZED_ACTION`/`CURRENT_STEP`/`VALIDATION_STATUS` from
it internally; Luna trusts Boundary's compact, validated receipt rather than
walking the ledger itself.

## Modules

- `contracts.py` — `LedgerEvent`, `Phase`, `LunaAction`. Owns the ledger
  event shape and the phase/action vocabulary; imports rather than redefines
  `body_state`'s and `execution_envelope`'s field sets.
- `flow.py` — the fixed, closed legal-transition table. No task-specific
  instructions; the sealed-plan invariant is enforced mechanically (there is
  no transition from `PLAN_SEALED` back to `PLAN_DRAFTED`/`PLAN_REVIEW`).
- `store.py` — `write_immutable_artifact` (create-only, hashed, under
  `workspace_root`) and `AppendOnlyLedger` (append/read/verify/recover a
  hash-chained `ledger.jsonl`). Nothing else in this repository is an event
  log; `capabilities.immutable_checkpoint` publishes one snapshot of current
  state, not an ordered history.
- `runtime.py` — `dispatch_specialist`: validates a
  `capabilities.execution_envelope` task envelope against `repository_root`,
  runs an injected executor, captures its raw output directly to an
  immutable workspace artifact, and returns only the validated,
  ≤4,096-byte `role_return` referencing it. The raw body is not part of
  this function's return value.
- `command.py` — thin wrapper around
  `capabilities.execution_envelope.run_command` with the
  `commands/<command_id>.log` workspace convention; the Git mutation
  preflight always runs against the real repository (`worktree`), never the
  workspace.
- `boundary.py` — `admit_transition` (delegates to `flow.next_phase`);
  `build_luna_receipt` (the one place a Luna-bound object is assembled and
  validated via `capabilities.body_state`, which mechanically guarantees no
  body can leak into it); `retrieve_evidence` (delegates to
  `capabilities.focused_retrieval`); the Plan's Fix Loop gating (re-exports
  `capabilities.runskeptic_receipt` verbatim); and a small, locally-owned
  Find Loop counterpart (`advance_find_loop`/`find_loop_complete`), added
  because `runskeptic_receipt`'s loop-state functions are hardcoded to
  `INVOCATION_KIND == "FIX_LOOP"` and its PASS-only qualifying rule is the
  wrong completion predicate for a Find Loop, whose convergence means
  detection stabilized on a stable finding set, not that the artifact
  passed (`skeptic.md`, "Loop Invocations").
- `trigger.py` — `parse_trigger` (`TT:` recognition), `bootstrap_task`
  (build-in-temp-dir-then-atomic-rename publication of the task workspace,
  mirroring the crash-safety `capabilities.immutable_checkpoint` already
  demonstrates for single files), and `resume_task` (a re-export of
  `capabilities.restart_admission.admit_restart` for interruption/resume).

## What is deliberately not here

`capabilities.body_state`, `capabilities.execution_envelope`,
`capabilities.immutable_checkpoint`, `capabilities.restart_admission`,
`capabilities.focused_retrieval`, and `capabilities.runskeptic_receipt` are
composed, not duplicated or modified. A second parallel receipt schema
using the mission-brief's own field names (`TASK_ROOT_REF`/`LEDGER_HEAD_REF`/
etc.) is deliberately not built: `body_state`'s existing ten fields already
serve as Luna's compact receipt, and adding a second authoritative state
shape would be exactly the "second authoritative mutable state file" this
design's own governing rule forbids.

## Non-circular construction

Changes to this contract, `workflows/target_task.md`, or the modules listed
above are ordinary Task Prompt work. They must not be made by invoking the
Target Task lifecycle this package implements.
