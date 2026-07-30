# Claude Code project instructions

Load the repository's authoritative agent routing and contracts:

@AGENTS.md

When the first meaningful token of a user message is exactly `TT:`, do not
handle it as an ordinary request. Read `workflows/target_task.md` completely
and execute that workflow. Persist the exact mission suffix before substantive
planning. Do not use conversational memory as durable task state.
