# Claude Code project instructions

@AGENTS.md

When the first meaningful token of a user message is exactly `STT:` followed
by a nonblank mission, Claude Code is the active host: set
`STT_PROVIDER=claude-code`, resolve the current Git root, persist the exact
mission, and invoke `python3 scripts/stt.py`. Do not launch Codex or select a
historical runtime. Follow the complete product and lifecycle contract in
`workflows/target_task.md`.
