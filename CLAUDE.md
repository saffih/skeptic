# Claude Code project instructions

@AGENTS.md

When the first meaningful token of a user message is exactly `TT:`, route the
request to `workflows/target_task.md` and follow that file completely. Direct
Claude Code submission necessarily exposes the initial user message to the
current host session; do not claim otherwise. Immediately bootstrap the exact
mission suffix, then keep the durable post-bootstrap Lead reference-only.

Use `TARGET_TASKS_ROOT` when set; otherwise use `~/.skeptic/target-tasks`.
