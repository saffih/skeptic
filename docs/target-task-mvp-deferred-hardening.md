# Target Task MVP deferred hardening

The Claude Code MVP enforces reference-only behavior after mission bootstrap at
observable protocol boundaries. It does not prove that the host platform never
internally exposes child content to a parent context.

- `BOUNDARY_PROTOCOL_ISOLATION`: testable PASS/FAIL after bootstrap.
- `INITIAL_MISSION_CONTEXT_ISOLATION`: UNAVAILABLE for direct `TT:` submission.
- `HIDDEN_HOST_CONTEXT_ISOLATION`: UNKNOWN.

A later hardening pass may add a trusted pre-model launcher or a host primitive
that persists and replaces the initial prompt before model receipt. Do not claim
hard isolation without direct runtime evidence.
