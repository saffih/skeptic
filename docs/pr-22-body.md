## Summary

- Preserves the current provider-neutral Target Task lifecycle, immutable task root, append-only ledger, cursor, receipt validation, and review gates.
- Adds a hash-bound executable companion for each sealed Plan at `plans/execution/<sealed-plan-sha256>.json`; a minimal sealed Plan alone is not executable.
- Adds one thin reference-only controller and CLI for bootstrap, status, prepare, accept, advance, retry, stop, handoff, resume, and execution validation.
- Adds adapter-owned provider/model aliases, truthful provider-neutral route resolution, and deterministic `RELAUNCH_REQUIRED` for an unavailable economical Lead route.
- Adds a host-owned deterministic recorded launcher that persists raw provider evidence and returns only validated compact receipts.
- Replaces the schema-only generic smoke with a real two-step Worker/Command lifecycle through `STEP_VALIDATED`.
- Hardens the live-smoke validator against prose-bearing Agent returns, incomplete review-loop bindings, arbitrary manifest discovery, and wrapper-created remote state.

## Deterministic evidence

Final candidate evidence:

- Base head: `6c7957e7599cd800f6f4d79c55fad807e1b50fcd`.
- Complete candidate binding: persisted in the exact closeout receipt; it is not duplicated here to avoid self-referential hash drift.
- Three source-fresh, complete, unchanged RunSkeptic Fix Loop passes: PASS.
- Full repository test suite: 327 tests, PASS.

The closeout receipt records the exact final commit/tree and remote commit/tree after publication. Required checks:

- Python compileall for modified Target Task modules, adapters, scripts, and tests.
- Focused Target Task tests.
- `python3 scripts/generic_host_smoke.py`.
- Full repository unit-test suite.
- `bash -n scripts/target_task_smoke.sh`.
- `git diff --check`.
- Three consecutive qualifying RunSkeptic Fix Loop passes on the exact unchanged final candidate.

## Truthful scope

The deterministic generic smoke proves two separately admitted, accepted, and advanced steps, provider route resolution, raw generic provider evidence, compact receipts, fresh-session resume, and execution validation.

It does **not** prove:

- a paid live Claude Code or Codex run;
- terminal `CLOSED` through final Find Loop, integration, and remote verification;
- hidden host context isolation.

Report these exactly as:

- `LIVE_PROVIDER_SMOKE: NOT_RUN` unless separately authorized and executed;
- `HIDDEN_HOST_CONTEXT_ISOLATION: UNKNOWN`.
