# Plan target-task-replacement-plan-002

- plan_id: target-task-replacement-plan-002
- version: 2 (complete replacement of `target-task-replacement-plan-001.md`,
  which is superseded and kept only as review history)
- purpose: REPAIR
- mission_binding: TP-REPLACE-TARGET-TASK-REFERENCE-ONLY-001
- supersedes: `plans/target-task-replacement-plan-001.md`
- repair_basis: independent RunSkeptic review (SINGLE, read-only) of plan-001,
  FINAL_OUTPUT_CATEGORY: CONFLICT, three findings — F1 (CONFLICT), F2
  (ACTION), F3 (ACTION). See "Findings addressed" below.

## Objective

Unchanged from plan-001: build a clean, reference-only replacement for the
Target Task lifecycle — mission → Planner → Plan RunSkeptic Fix Loop → seal
→ execute sealed plan exactly once → deterministic validation → freeze →
read-only RunSkeptic Find Loop → integrate only if clean and mechanically
possible → close with a compact receipt — composing this repository's
existing tested capabilities instead of duplicating them.

## Findings addressed (material changes from plan-001)

- **F1 (CONFLICT) — root-parameter ambiguity, resolved.** `body_state`'s
  validator resolves every `ARTIFACT_REFERENCES` entry, including
  `SEALED_PLAN_REFERENCE`, against a single `repository_root`; it cannot
  mix a real-repo reference with a workspace-only reference in one object.
  Resolution, now Decision D1' below and documented in
  `concepts/target_task/target_task_contract.md` ("Two roots"): a sealed
  Plan is a real `repository_root`-relative file; the ledger, mission text,
  step results, checkpoints, and command logs are `workspace_root`-only and
  never appear in a `body_state` object's `ARTIFACT_REFERENCES`. Luna's
  receipt does not need a literal ledger-head reference — Boundary is the
  sole ledger reader/writer and derives the receipt's status fields from it
  internally. Every module signature that touches the filesystem now takes
  `repository_root` and/or `workspace_root` explicitly, never one
  conflated `task_root`.
- **F2 (ACTION) — declared-but-unused capabilities, resolved.**
  `capabilities.focused_retrieval` is composed as `boundary.retrieve_evidence`
  (Boundary's "select only required evidence" behavior). `capabilities.restart_admission`
  is composed as `trigger.resume_task` (thin re-export of `admit_restart`,
  the Phase-17 interruption/resume path). Both now appear in the ordered
  steps below; no capability is claimed as in-scope without a concrete use.
- **F3 (ACTION) — unverified "frozen" claim, resolved.** Constraint 1's
  basis is restated as the actual, verifiable basis: no modification is
  proposed to these capabilities and none is needed; composing them avoids
  duplicating tested logic (`OM:UE`). The prior "frozen, per their own
  preservation history" phrasing is dropped; no such governance statement
  was found for these specific files.

## Constraints (unchanged except Constraint 1's basis, see F3)

1. Do not duplicate `capabilities/body_state`, `capabilities/execution_envelope`,
   `capabilities/immutable_checkpoint`, `capabilities/restart_admission`,
   `capabilities/focused_retrieval`, or `capabilities/runskeptic_receipt`.
   Compose them. No modification is proposed to any of them, and none is
   needed for this design; duplicating tested logic instead would be
   unjustified structure (`OM:UE`).
2. Do not modify `skeptic.md`, `agents/boundary_agent.md`,
   `agents/model_routing_policy.md`, or `agents/agent_return_contract.md`.
3. Runtime task state is never committed to this repository. A sealed Plan
   is the one exception by construction (D1'): it is a real repository file
   because `body_state` requires it to be. Everything else (mission,
   ledger, step results, checkpoints, command logs) lives under an external
   `workspace_root`, disjoint from the repository, per
   `capabilities.restart_admission`'s own enforced invariant.
4. New code is reference-only, matching the existing `concepts/` convention:
   example modules with mirrored tests proving the contracts. `runtime.py`
   is a narrow adapter with an injected executor callable; no live model
   dispatch exists in this repository.
5. Non-circular construction: this Plan is executed by ordinary direct
   work, never by invoking the Target Task lifecycle being built.

## Decisions

- D1'. Two explicit roots everywhere (see "Findings addressed" F1 and
  `target_task_contract.md`, "Two roots"). Luna's compact receipt remains
  `capabilities.body_state`'s existing ten fields, reused verbatim; it
  simply never carries a workspace-only reference.
- D2. `command.py` wraps `capabilities.execution_envelope.run_command`;
  logs are written under `workspace_root` (`repository_root` argument to
  that call), while the Git mutation preflight targets the real repository
  (`worktree`/`cwd` argument).
- D3. New surface: `TT:` trigger + mission bootstrap (`trigger.py`), the
  phase/action legal-transition table (`flow.py`), the append-only ledger
  (`store.py`), and the Boundary composition that guarantees only a valid
  `body_state` object ever reaches Luna (`boundary.py`). Everything else is
  thin delegation to existing capabilities.
- D4. `agents/boundary_agent.md` is unchanged; `concepts/target_task/boundary.py`
  is a distinct, Target-Task-specific deterministic firewall, not a
  restatement of that general policy.
- D5. The Find Loop's completion predicate (stable finding set) differs in
  kind from the Fix Loop's (all-PASS), so `boundary.py` adds a small local
  `advance_find_loop`/`find_loop_complete` pair rather than reusing
  `capabilities.runskeptic_receipt`'s FIX_LOOP-hardcoded functions for a
  purpose they were not built for.

## Ordered steps (implementation status: drafted before this repair;
## verified consistent with D1'-D5 as part of this repair)

1. `concepts/target_task/contracts.py` — `LedgerEvent`, `Phase`,
   `LunaAction`, canonical serialization. **Done.**
2. `concepts/target_task/flow.py` — `LEGAL_TRANSITIONS`, `next_phase`.
   **Done.**
3. `concepts/target_task/store.py` — `write_immutable_artifact` (takes
   `workspace_root`), `AppendOnlyLedger`. **Done; parameter names corrected
   to `workspace_root` under this repair.**
4. `concepts/target_task/runtime.py` — `dispatch_specialist`, now taking
   `repository_root` (task envelope's input references) and
   `workspace_root` (captured output) separately. **Done; split under this
   repair.**
5. `concepts/target_task/command.py` — `run_task_command`,
   `build_mutation_preflight`. **Done; parameter renamed to
   `workspace_root` under this repair.**
6. `concepts/target_task/boundary.py` — `admit_transition`,
   `build_luna_receipt` (now `repository_root`-based per D1'),
   `retrieve_evidence` (new, composes `focused_retrieval`, addresses F2),
   Fix Loop re-exports, `advance_find_loop`/`find_loop_complete` (D5).
   **Done.**
7. `concepts/target_task/trigger.py` — `parse_trigger`, `bootstrap_task`,
   `resume_task` (new, composes `restart_admission`, addresses F2).
   **Done.**
8. `concepts/target_task/target_task_contract.md` — the reference contract
   doc, including the "Two roots" section this repair introduced. **Done.**
9. `tests/concepts/target_task/test_{contracts,flow,store,runtime,command,
   boundary,trigger}.py` — one mirrored test module per file above,
   including a test proving a `body_state` object with a real
   `repository_root`-relative `SEALED_PLAN_REFERENCE` validates end-to-end
   through the pieces that touch it. **Done.**
10. `workflows/target_task.md` — the authoritative lifecycle doc AGENTS.md
    already points to. **Done.**
11. Run `python3 -m unittest discover -s tests -t .`; all tests pass.
    **Done.**

## Unknown treatment

Unchanged from plan-001: no live agent runtime exists in this repository;
`runtime.py` is proven with an injected executor and this is recorded, not
hidden.

## Post-review code repair log

A second independent review (SINGLE, read-only) verified F1/F2/F3 resolved
(all PASS, FINAL_OUTPUT_CATEGORY: HANDLED) and additionally found, in the
already-drafted implementation rather than in this Plan's own text:

- `flow.next_phase`'s `BLOCKED` → `RECOVER` transition accepted any
  `resume_phase` present in `LEGAL_TRANSITIONS`, including `Phase.CLOSED`
  and `Phase.BLOCKED` itself — letting a recovery silently bypass
  deterministic validation, the frozen-candidate Find Loop, and
  integration. REPRODUCED. Fixed: `resume_phase` may not be `CLOSED` or
  `BLOCKED`; regression tests added
  (`test_recover_cannot_bypass_the_lifecycle_straight_to_closed`,
  `test_recover_cannot_resume_into_blocked_itself`).
- `boundary.py`'s docstring still asserted `capabilities/runskeptic_receipt`
  is "frozen" — the same unverified-governance phrasing F3 already
  corrected in this Plan's own text. Fixed: reworded to the verifiable
  basis (no modification proposed or needed).
- `FindLoopState` (a dataclass) was defined and exported but never
  constructed; the Find Loop functions operate on plain `Mapping`,
  matching `runskeptic_receipt`'s own external-state convention. Fixed:
  removed as unnecessary structure (`OM:UE`). The no-op
  `try/except IllegalTransitionError: raise` in `admit_transition` was
  removed for the same reason.

These are implementation-level fixes to code this Plan's steps already
described (not a change to the Plan's objective, constraints, decisions, or
step scope), so they are logged here rather than issued as
`target-task-replacement-plan-003.md`. `python3 -m unittest discover -s
tests -t .` passes (334 tests) after the fix.

A third independent review (SINGLE, read-only, a genuinely fresh pass, not a
checklist against the above) confirmed all three repairs above and found the
design sound overall (FINAL_OUTPUT_CATEGORY: HANDLED), with two further
low-severity findings, both fixed:

- `trigger.bootstrap_task`'s `os.rename` and `store.recover_torn_tail`'s
  `os.replace` published a directory-entry change without the
  parent-directory `fsync` this codebase's own comparable publish
  operations (`capabilities.immutable_checkpoint`,
  `capabilities.restart_admission`) treat as mandatory for crash durability.
  Fixed with a shared `store._fsync_dir` helper (same ENOTSUP/EOPNOTSUPP/
  EINVAL/ENOSYS fallback as those capabilities), applied at both flagged
  call sites and, for the same reason, at `write_immutable_artifact`'s
  create-only write too (not separately flagged, but the identical
  directory-entry-durability gap — leaving it unfixed would reintroduce the
  same asymmetry the finding was about). Regression tests assert the fsync
  call occurs (mock-based; a real crash cannot be reproduced in a unit
  test, matching the reviewer's own recommended verification approach).
- This Plan's own "Ordered steps" section still marked steps 9-11 "Next"
  after they were completed and logged as such earlier in this same repair
  log — a stale, self-contradictory status marker. Fixed in place (steps
  9-11 now read "Done"); this is a documentation-accuracy correction, not a
  change to objective, constraints, decisions, or step scope.

`python3 -m unittest discover -s tests -t .` passes (340 tests) after these
fixes.

## Stop / replan conditions

Stop and report `CONFLICT` if a step requires modifying a frozen-in-practice
capability to work correctly, or a further independent review finds a
`CONFLICT`-level issue this repair does not resolve. A further material
change to this Plan requires `target-task-replacement-plan-003.md`, not an
in-place edit.
