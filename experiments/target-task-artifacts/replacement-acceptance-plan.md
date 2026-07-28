# Replacement Acceptance Plan

TASK_ID: TT-REPAIR-2026-07-28
STATUS: ACCEPTED_REPLACEMENT
OBJECTIVE: Repair and validate the Target Task Body-pressure gate and
context-rotation lifecycle without changing `skeptic.md` or local `main`.
DONE: Pressure gate, checkpoint/stop/resume contract, deterministic tests,
fresh Luna Body verification, and required independent RunSkeptic review are
evidenced; unresolved runtime or promotion limits remain explicit.
SCOPE: target-task worktree only; architecture, Target Task/Lead contracts,
lifecycle/context harnesses, focused tests, and evidence artifacts.
PROHIBITIONS: no `skeptic.md` edit; no main mutation; no cleanup, reset,
stash, merge, commit, push, or fabricated runtime claims.
SOURCE_OF_TRUTH_ORDER: user authority, skeptic.md, this plan, architecture,
verified checkpoint, deterministic evidence, fresh Body handoff.

## Ordered steps

### S0 — Baseline and preservation

Record worktree identity, complete status/diff, untracked inventory, protected
main status, and source SHA. Stop on drift or integrity mismatch.

### S1 — Pressure gate contract

Define `BODY_ROTATION_REQUIRED` as a bounded state-management boundary. The
gate may use deterministic byte evidence but must not claim token reduction or
runtime isolation.

### S2 — Checkpoint, stop, and fresh resume

Persist and verify compact identity/hash/step/claim/next-action state; stop
the predecessor Body before continuation. Resume only through a fresh Luna
Body, with completed work not repeated. If fresh evidence is unavailable,
remain blocked.

### S3 — Validation and evidence

Run targeted tests, full discovery, pressure output, diff checks, and preserve
the exact fresh-Body handoff and limitations.

### S4 — Independent review

Run the current `skeptic.md` Fix Loop with fresh GPT-5.6 Sol HIGH reviews.
Repair runs never qualify; any mutation resets convergence. Three independent
complete qualifying passes on one unchanged commit are required for promotion.

### S5 — Terminal receipt

Report exact commit, source SHA, review receipts, pressure/rotation state,
checkpoint/resume state, runtime unknowns, and workspace state. Do not claim
main readiness unless every promotion condition passes.

## Acceptance

This replacement plan supersedes the rejected incomplete plan only for the
scoped repair above. It does not authorize publication or cleanup.
