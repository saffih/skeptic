# Target Task MVP deferred hardening

The Claude Code MVP enforces and tests reference-only behavior at observable
protocol boundaries. It does not prove that the host platform never internally
exposes a child body to a parent context.

- `BOUNDARY_PROTOCOL_ISOLATION`: testable PASS/FAIL.
- `HIDDEN_HOST_CONTEXT_ISOLATION`: UNKNOWN.

A later hardening task may replace protocol discipline with host-enforced
direct-to-file output capture if such a primitive becomes available. Do not
claim that hardening complete without direct runtime evidence.
