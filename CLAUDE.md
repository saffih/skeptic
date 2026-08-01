# Claude Code project instructions

@AGENTS.md

When the first meaningful token of a user message is exactly `TT:`, route the
request to `workflows/target_task.md` and follow that file completely. Direct
Claude Code submission necessarily exposes the initial user message to the
current host session; do not claim otherwise. Immediately bootstrap the exact
mission suffix, then keep the durable post-bootstrap Lead reference-only.

When the first meaningful token is exactly `STT:`, set `STT_PROVIDER=claude-code`, resolve the current Git root, persist the exact mission, and continue through `python3 scripts/stt.py`. Do not launch Codex or use a historical runtime. STT state is local to the checkout at `<checkout>/.stt/tasks` by default, with `STT_TASKS_ROOT` as an explicit override; it is ignored by Git.
