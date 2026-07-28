# Target Task repository adapter

This file adapts the portable Target Task protocol to this repository. It does
not replace `agents/target-task.md` or `skeptic.md`.

The approved design source of truth is
`architecture/target-task-architecture.md`; this adapter only identifies
repository entry points and validation artifacts.

* `AGENTS.md` is the repository entry map.
* `skeptic.md` is the authoritative Skeptic review source.
* `agents/` contains repository-specific orchestration contracts.
* `experiments/target-task-artifacts/` contains optional durable templates.
* `tests/` and `harness/` provide deterministic validation; generated runtime
  state remains outside the reusable prompt library unless explicitly scoped.

For substantive work, use the Lead and routing contracts, run the planned
RunSkeptic review with its receipt, and preserve protected worktrees and
untracked evidence. This adapter must not turn the repository into the owner
of a caller's task state.
