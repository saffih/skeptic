# Plan target-task-replacement-plan-001

- plan_id: target-task-replacement-plan-001
- version: 1
- purpose: CREATE
- mission_binding: TP-REPLACE-TARGET-TASK-REFERENCE-ONLY-001 ("Remove the
  Existing Target Task and Build the Clean Reference-Only Target Task")
- depends_on: removal commit `bfd1148` (old `concepts/target_task/` and the
  old prose gate already removed), investigation note
  `docs/target-task-replacement-investigation-2026-07-30.md`

## Objective

Build a clean, reference-only replacement for the Target Task lifecycle that
(a) implements the universal flow — mission → Planner → Plan RunSkeptic Fix
Loop → seal → execute sealed plan exactly once → deterministic validation →
freeze → read-only RunSkeptic Find Loop → integrate only if clean and
mechanically possible → close with a compact receipt — and (b) keeps
substantive bodies in files and durable Lead ("Luna") context to compact
receipts only, without duplicating capabilities this repository already has,
tested, and marked frozen.

## Constraints

1. Do not duplicate `capabilities/body_state`, `capabilities/execution_envelope`,
   `capabilities/immutable_checkpoint`, `capabilities/restart_admission`,
   `capabilities/focused_retrieval`, or `capabilities/runskeptic_receipt`.
   Compose them. Do not modify them (frozen, per their own preservation
   history).
2. Do not modify `skeptic.md`, `agents/boundary_agent.md`,
   `agents/model_routing_policy.md`, or `agents/agent_return_contract.md`
   (general-purpose, still correct, out of this task's ownership).
3. Runtime task state (mission, plan, steps, ledger, checkpoints) is never
   committed to this repository — `AGENTS.md` already states "Runtime state,
   plans, checkpoints, logs, receipts, and validation evidence remain outside
   this repository." New code takes an external `tasks_root`/`workspace_root`
   parameter, exactly like `immutable_checkpoint`/`restart_admission`
   already do; it never creates a `tasks/` directory inside the repo.
4. New code is reference-only: example modules with mirrored tests proving
   the contracts, matching the existing `concepts/` convention. No file in
   this repository currently dispatches a live model agent, so `runtime.py`
   cannot be more than a narrow adapter with an injected executor callable.
5. Non-circular construction: this Plan is executed by ordinary direct work
   (Bash, Edit, Write, one independent reviewer dispatch), never by invoking
   the Target Task lifecycle being built.

## Decisions

- D1. Luna's compact receipt is `capabilities/body_state`'s existing
  `TASK_ID`/`SEALED_PLAN_REFERENCE`/`SEALED_PLAN_SHA256`/`CURRENT_STEP`/
  `COMPLETED_STEP_IDS`/`VALIDATED_FACTS`/`OPEN_BLOCKERS`/`ARTIFACT_REFERENCES`/
  `NEXT_AUTHORIZED_ACTION`/`VALIDATION_STATUS` object, reused verbatim rather
  than a new parallel schema with the mission text's field names
  (`TASK_ROOT_REF`/`LEDGER_HEAD_REF`/...). Basis: body_state already forbids
  body content, already carries a sealed-plan reference+hash, and its
  `ARTIFACT_REFERENCES` list already accommodates a ledger-head pointer
  (`artifact_type: "ledger_head"`) with no schema change. Adding a second,
  near-identical authoritative receipt schema would violate PHASE 10's own
  "do not add a second authoritative mutable state file" rule and this
  repo's Occam's-razor discipline (`OM:UE`).
- D2. `command.py` wraps `capabilities/execution_envelope/execution_envelope.py`'s
  `run_command` (argument-vector execution, Git mutation preflight, complete
  stdout/stderr capture) instead of reimplementing subprocess handling.
- D3. The genuinely new surface is: (a) the `TT:` trigger and mission
  bootstrap, (b) the phase/action legal-transition table, (c) an
  append-only, hash-chained ledger (no existing capability is an event log —
  `immutable_checkpoint` publishes one snapshot of current state), and (d)
  the Boundary composition that guarantees only a valid `body_state` object
  ever reaches Luna. Everything else is thin delegation.
- D4. `agents/boundary_agent.md` (general Boundary Agent policy) is
  unchanged; `concepts/target_task/boundary.py` is a distinct,
  Target-Task-specific *deterministic* firewall implementation, not a
  restatement of that general policy.

## Ordered steps

1. `concepts/target_task/contracts.py` — `LedgerEvent` dataclass and
   canonical-serialization helpers; `Phase` and `LunaAction` enums; no
   duplication of `ARTIFACT_FIELDS`/state fields already owned by
   `body_state`/`execution_envelope` (import, don't redefine).
2. `concepts/target_task/flow.py` — `LEGAL_TRANSITIONS` table and
   `next_phase(current, action) -> Phase` raising `IllegalTransitionError`
   on an illegal request; owns no task-specific instructions.
3. `concepts/target_task/store.py` — `write_immutable_artifact` (create-only,
   hashed, using `body_state`'s path/hash helpers) and `AppendOnlyLedger`
   (`append`, `read_ledger`, `verify_chain`, `recover_torn_tail`); freeze/
   checkpoint operations delegate to `capabilities.immutable_checkpoint`.
4. `concepts/target_task/runtime.py` — `dispatch_specialist(envelope,
   executor, output_path)` using `execution_envelope.validate_task_envelope`/
   `validate_role_return`; captures the executor's return directly to
   `output_path` and returns only a produced-artifact reference, never the
   raw text, to the caller.
5. `concepts/target_task/command.py` — thin re-export/convenience wrapper
   around `execution_envelope.run_command` with the task-workspace log-path
   convention.
6. `concepts/target_task/boundary.py` — `validate_lead_request` (calls
   `flow.next_phase`), `build_receipt` (produces/validates a `body_state`
   object), `assert_no_body_leak`, and Fix/Find Loop gating via
   `capabilities.runskeptic_receipt`.
7. `concepts/target_task/trigger.py` — `parse_trigger(message) ->
   str | None` (exact `TT:` prefix, non-empty mission, `ValueError` on empty
   mission) and `bootstrap_task(mission, tasks_root)` (temp-dir-then-atomic-
   publish, per Chesterton's-fence-respecting crash safety already
   demonstrated by `immutable_checkpoint.create_checkpoint`).
8. `concepts/target_task/target_task_contract.md` — the reference contract
   doc for the whole design (mirrors old `reference_contract.md`'s role).
9. `tests/concepts/target_task/test_{contracts,flow,store,runtime,command,
   boundary,trigger}.py` — one mirrored test module per file above.
10. `workflows/target_task.md` — the authoritative lifecycle doc AGENTS.md
    now points to; includes the "previous implementation removed" note.
11. Run `python3 -m unittest discover -s tests -t .`; all tests pass.

## Unknown treatment

No live agent runtime exists in this repository to dispatch a real Planner/
Worker/Reviewer/Skeptic model. `runtime.py` therefore accepts an injected
executor callable and is proven by tests with a fake executor, exactly as
the mission spec's own PHASE 9 concedes ("A deterministic tool may omit this
model-agent envelope when the runtime already returns equivalent structured
... metadata" — `agents/agent_return_contract.md`). This is recorded, not
hidden.

## Stop / replan conditions

Stop and report `CONFLICT` if: a step requires modifying a frozen capability
to work correctly (would mean the composition design is wrong), or the
independent Plan reviewer finds a `CONFLICT`-level issue that cannot be
resolved by a bounded Planner repair. A material change to this Plan
(objective, decisions, or step scope) requires a complete replacement plan
(`target-task-replacement-plan-002.md`), not an in-place edit.
