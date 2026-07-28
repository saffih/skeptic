## Task understood

- task identity: TT-BODY-BOUNDED-EXECUTION-SLICE-002
- objective: add a bounded execution envelope and file-backed command receipts while preserving Slice 1 metadata-only state.
- scope: one contract document, one standard-library helper, examples, focused tests, and minimal template/entry-map updates.
- authoritative inputs: `AGENTS.md`, `agents/body-state.md`, `harness/body_state.py`, `experiments/body-brain-artifacts/brain.md`, `skeptic.md`, and the supplied Target Task.
- prohibitions: do not edit `skeptic.md`; do not add checkpoint, resume, rotation, pressure, retrieval, service, dependency, or unrelated cleanup behavior; do not modify protected local-main evidence.

## Material assumptions and unknowns

- The feature worktree is isolated at `/private/tmp/skeptic-bounded-execution-slice-2-wt` on branch `claude/bounded-execution-slice-2-20260728`.
- `origin/main` was fetched and equals `a2703a2a548d9fb24210039054d18f580a80a9ad`.
- No separate model-agent dispatch surface is observable; requested Brain routing is recorded separately from observed routing.

## Ordered execution steps

1. **S2-ENVELOPE** — BODY — Read Slice 1 helpers and define fixed, canonical, size-bounded task and role-return schemas with verified artifact references. Validate paths, hashes, sizes, UTF-8, and external-content boundaries. Stop on malformed or oversized input.
2. **S2-RUNNER** — BODY — Implement one-command execution with complete external logs, compact receipts, nonzero failure signaling, and mandatory Git repository/worktree/branch/HEAD/cleanliness/authorization preflight for mutations. Stop before subprocess execution on preflight mismatch.
3. **S2-ARTIFACTS** — BODY — Add the concise contract, examples, and minimal Body–Brain/entry-map references. Keep all detailed content in files.
4. **S2-TESTS** — DETERMINISTIC_TOOL — Add focused tests for all required task, role, runner, preflight, and Slice 1 compatibility cases. Validate exact limits and no-retry behavior.
5. **S2-VERIFY** — DETERMINISTIC_TOOL — Run focused tests once, full tests once, and `git diff --check`; store complete output in external logs and retain compact receipts.
6. **S2-REVIEW-INTEGRATE** — BODY — Run the authorized RunSkeptic Fix Loop, repair only valid findings, preserve same-candidate qualifying evidence, push the clean candidate, and exact-test fast-forward integration into an isolated worktree. Stop with `INTEGRATION_BASE_CHANGED` if current main changes materially.

## Decision points

- If any expected repository/worktree/branch/HEAD/cleanliness value differs before mutation, emit a blocked receipt and do not execute the command.
- If a required artifact reference is absent, unsafe, noncanonical, oversized, or hash/size mismatched, fail closed.
- If current `origin/main` differs from the reviewed integration base, stop and report `INTEGRATION_BASE_CHANGED`; do not rebase silently.

## Final validation

- Focused command: `python3 -m unittest discover -s tests -p 'test_execution_envelope.py'`.
- Full command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`.
- `git diff --check` passes.
- Slice 1 tests remain passing; plan hash is unchanged after execution; candidate is clean and pushed; three qualifying RunSkeptic passes and exact integration are evidenced.

## Success criteria

Task and role payloads have fixed fields and deterministic byte limits; detailed content stays external; command output is preserved in hashed logs; failed commands fail visibly; every tested mutation preflight mismatch prevents mutation; compatibility and full validation pass; Slice 2 is merged into authoritative main.

BRAIN_PLAN_COMPLETE
