# Claude Code project instructions

@AGENTS.md

When the first meaningful token of a user message is exactly `TT:`, route the
request to `workflows/target_task.md` and follow that file completely. Direct
Claude Code submission necessarily exposes the initial user message to the
current host session; do not claim otherwise. Immediately bootstrap the exact
mission suffix, then keep the durable post-bootstrap Lead reference-only.

STT state is local to the checkout. By default it lives in the private sibling
directory `<checkout>.stt/tasks`; locks, validation material, and install
backups remain under the same `<checkout>.stt/` local runtime root.
