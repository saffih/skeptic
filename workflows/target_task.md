# Target Task

The previous Target Task implementation has been removed. It is being
replaced by the clean reference-only Target Task described here. Historical
references (in `experiments/`, `docs/`, and `plans/`) to the removed
compact-handoff/rotation prototype are non-authoritative and non-executable.

## Trigger

A user message whose first meaningful token is exactly `TT:` starts a Target
Task. The text after it, exactly as written, is the immutable mission. An
empty mission is rejected. The mission body is never inlined into the
durable Lead's ("Luna's") context — see "Luna" below.

## Universal lifecycle

```text
TT: <mission>
-> mission persisted immutably (trigger.bootstrap_task)
-> distinct bounded Planner dispatch
-> Agent Completion Envelope validation
-> complete Planner-produced plan
-> RunSkeptic Fix Loop on the plan (three consecutive qualifying passes)
-> plan sealed: path, SHA-256, byte size, schema version frozen for the run
-> execution of the sealed plan, exactly once
-> deterministic validation
-> candidate frozen
-> read-only RunSkeptic Find Loop over the frozen candidate
-> integration only when clean and mechanically possible
-> close with a compact receipt
```

This universal sequence lives in `concepts/target_task/flow.py` as a fixed,
closed legal-transition table (`Phase` × `LunaAction` → `Phase`). It holds no
task-specific instructions. Task-specific work belongs to the accepted Plan;
durable progress facts belong to the append-only ledger
(`concepts/target_task/store.py`). These three authorities stay distinct:
`flow.py` never gains task content, the Plan never gains lifecycle rules,
and the ledger never gains either.

## Sealed Plan invariant

Once accepted through three consecutive qualifying RunSkeptic Fix Loop
passes on the same unchanged plan, the Plan is sealed: its path, SHA-256,
exact byte size, and schema version are recorded and frozen for the run.
`flow.py` enforces this mechanically — there is no legal transition from
`PLAN_SEALED` back to `PLAN_DRAFTED` or `PLAN_REVIEW`. If the sealed plan
cannot be completed safely, the run stops and reports the blocker; it is
never repaired, replaced, reordered, or reinterpreted inside the same run.
Because `capabilities.body_state` requires `SEALED_PLAN_REFERENCE` to
resolve as a real file under the same root as every other artifact
reference in a Luna receipt, a sealed Plan is a real file in this
repository (for example, under `plans/`), not a workspace-only artifact —
see `concepts/target_task/target_task_contract.md`, "Two roots".

## Luna: the compact durable Lead

During a Target Task, the durable Lead is Luna: a low-cost control agent
that holds only `capabilities.body_state`'s ten fields — `TASK_ID`,
`SEALED_PLAN_REFERENCE`, `SEALED_PLAN_SHA256`, `CURRENT_STEP`,
`COMPLETED_STEP_IDS`, `VALIDATED_FACTS`, `OPEN_BLOCKERS`,
`ARTIFACT_REFERENCES`, `NEXT_AUTHORIZED_ACTION`, `VALIDATION_STATUS` — and
never a mission, plan, step instruction, patch, review, finding, log, or
command-output body. Luna chooses only `CONTINUE`, `ADVANCE`, `RETRY`,
`RECOVER`, or `STOP` (`concepts/target_task/contracts.py`'s `LunaAction`).
Boundary (`concepts/target_task/boundary.py`) determines whether the
requested transition is legal; Luna never decides substantive correctness.

This is reused, not reinvented: `capabilities.body_state.validate_state_bytes`
already forbids anything outside these ten fields, so it mechanically
guarantees no body can reach Luna. A second, parallel receipt schema is
deliberately not built.

## Boundary

The deterministic firewall between Luna and substantive work
(`concepts/target_task/boundary.py`). It performs no intellectual
judgment: transition legality is a thin call into `flow.next_phase`;
evidence selection delegates to `capabilities.focused_retrieval`; the
Plan's Fix Loop gating reuses `capabilities.runskeptic_receipt` verbatim;
the final candidate's Find Loop uses a small locally owned counterpart
(`advance_find_loop`/`find_loop_complete`) because a Find Loop's
convergence rule — a stable set of findings, not an all-PASS result — is
not the same predicate `runskeptic_receipt`'s Fix-Loop-only functions
implement.

## Roles

- **Planner** — produces the complete Plan. Cannot approve, execute,
  integrate, or claim `DONE`. A material plan change requires a new unique
  Planner repair dispatch and a complete replacement plan (never an
  in-place edit) before the plan may be sealed.
- **Worker** — performs one bounded accepted-Plan step via
  `concepts/target_task/runtime.py`'s `dispatch_specialist`, which captures
  the specialist's raw result directly into an immutable artifact and
  returns only a validated, body-free `role_return`.
- **Reviewer / Skeptic** — the Plan's Fix Loop and the candidate's Find
  Loop, both driven through `skeptic.md`'s own "RunSkeptic Fix Loop" /
  "RunSkeptic Find Loop" semantics (see `skeptic.md`, "Loop Invocations"),
  not a separately invented review process.
- **Command** — deterministic side effects via
  `concepts/target_task/command.py`, which wraps
  `capabilities.execution_envelope.run_command` (one explicit argument
  vector, a Git mutation preflight, complete stdout/stderr capture).

## Interruption and resume

A Target Task session is disposable; everything needed to continue is
file-backed. `concepts/target_task/trigger.py`'s `resume_task` re-exports
`capabilities.restart_admission.admit_restart`, which admits one validated
checkpoint into a fresh process and rejects a duplicate or already-completed
current step.

## Non-circular construction

Do not use the Target Task lifecycle to construct or modify this file,
`concepts/target_task/`, or the Target Task gate in `workflows/task_prompt.md`,
`agents/lead_agent.md`, or `agents/planner.md`. Changes to Target Task itself
are ordinary Task Prompt work — see `workflows/task_prompt.md`.

## Reference-only status

No live agent runtime executes this automatically in this repository (see
`AGENTS.md` — this is a portable prompt/review library, not a running
orchestrator). `concepts/target_task/` is reference-only: example modules
with mirrored tests under `tests/concepts/target_task/` that prove each
contract, matching every other concept in this repository. An invoking
runtime must implement equivalent behavior against these contracts, not
merely cite them.
