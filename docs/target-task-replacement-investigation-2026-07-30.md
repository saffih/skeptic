# Target Task replacement — investigation note — 2026-07-30

Read fresh from the clean repository (after the removal commit), not from
memory or the deleted prototype.

## What this repository actually is

`skeptic.md` is a portable review specification; `AGENTS.md` is the entry
map; `agents/`, `workflows/` are prose contracts a Lead/agent reads at
invocation time. There is no live agent runtime here — no process that
actually dispatches a model, no server, no CLI daemon. `concepts/` holds
reference-only illustrative Python; `capabilities/` holds deterministic,
tested, standard-library-only helpers with a same-stem `.md` contract each.
"Reference-only" for the new Target Task therefore means the same thing it
means for every other concept in this repo: example code that proves a
contract is implementable and exercised by tests, not a wired production
orchestrator.

## Reusable capabilities discovered (material to the design)

`capabilities/` already implements most of the primitives the replacement
needs. Building a parallel set under `concepts/target_task/` would duplicate
tested, frozen authority and violate this repo's own Occam's-razor rule
(`OM:UE`) and the prior task's explicit preservation policy ("no modification
of implementation" for these capabilities). Concretely:

- `capabilities/body_state/body_state.py` — the canonical metadata-only Body
  state (≤32,768 bytes): `TASK_ID`, `SEALED_PLAN_REFERENCE`,
  `SEALED_PLAN_SHA256`, `CURRENT_STEP`, `COMPLETED_STEP_IDS`,
  `VALIDATED_FACTS`, `OPEN_BLOCKERS`, `ARTIFACT_REFERENCES`,
  `NEXT_AUTHORIZED_ACTION`, `VALIDATION_STATUS`. This **is** the compact
  receipt the mission spec calls "Luna's" — it already forbids embedding
  bodies, already carries a sealed-plan reference and hash, and its
  `ARTIFACT_REFERENCES` list is open-ended, so a ledger-head pointer needs no
  schema change. It is frozen; the new design reuses it unmodified.
- `capabilities/execution_envelope/execution_envelope.py` — bounded task
  input (8,192 B), bounded role return (4,096 B), bounded command receipt
  (4,096 B), and `run_command`, which executes one argument vector (never a
  shell string), enforces a Git preflight (root/worktree/branch/HEAD/clean
  state) before any mutating command, and writes complete stdout/stderr to a
  requested log path. This is the deterministic command contract and most of
  the specialist-dispatch envelope; it is frozen and reused, not
  reimplemented.
- `capabilities/immutable_checkpoint/immutable_checkpoint.py` — create-only,
  fsynced, atomically published, hash-and-size-verified checkpoint from a
  validated Body state. This is the immutable-artifact and sealed-candidate
  publication mechanism.
- `capabilities/restart_admission/restart_admission.py` — admits a validated
  checkpoint into a fresh process, rejecting duplicate/already-completed
  steps. This is the interruption/resume path (mission spec Phase 17).
- `capabilities/focused_retrieval/focused_retrieval.py` — verified,
  size-bounded, single-range reads bound to an exact Body-state artifact
  reference. This is the Boundary's "select only required evidence"
  behavior.
- `capabilities/runskeptic_receipt/runskeptic_receipt.py` — validates a
  source-bound RunSkeptic receipt and implements the Fix Loop qualifying-pass
  state machine (`validate_loop_state`, `advance_fix_loop`,
  `fix_loop_complete`; three consecutive unchanged qualifying passes by
  default; a repair run or a binding change resets the streak). This is
  exactly `skeptic.md`'s native "RunSkeptic Fix Loop" / "RunSkeptic Find
  Loop" machinery (see `skeptic.md` "Loop Invocations") already wired to a
  deterministic validator. It is reused for both the Plan Fix Loop and the
  final candidate Find Loop rather than re-specified.

## The genuine gap

Nothing existing:

1. recognizes the `TT:` trigger string or persists a mission as the first
   immutable artifact of a new task;
2. enumerates the legal phase sequence of a Target Task run (mission →
   Planner → Plan Fix Loop → seal → execute-once → validate → freeze → Find
   Loop → integrate → close) or rejects an illegal transition;
3. appends a durable, hash-chained, append-only sequence of lifecycle facts.
   `immutable_checkpoint` publishes one create-only snapshot of *current*
   state; it is not an event log, and nothing replays "what happened, in
   order" across retries and rotations;
4. composes the five capabilities above into one enforcement point that
   guarantees the durable Lead only ever receives a body_state-shaped object
   (the actual firewall property Boundary must own — each capability
   validates its own object today, but nothing stops a caller from handing a
   raw plan or patch to the Lead directly).

## Design consequence

The replacement is a thin `concepts/target_task/` composition layer over the
existing capabilities, plus one new artifact class (the append-only ledger)
and the trigger/flow state machine. See
`plans/target-task-replacement-plan-001.md` for the sealed plan.
