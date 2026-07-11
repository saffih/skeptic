# Candidate C2-current-main-plus-code-skeptic-domain-extension

- Candidate ID: `C2-current-main-plus-code-skeptic-domain-extension`
- Base format: `versions/F5-current-main`
- Candidate text location: this definition only; source files are not edited.
- Intended capability target: `CODE`, `WEAK`, `SILENT`, `SPOT`, `ACTIONABLE`

## Minimal Domain Extension Under Test

Code-specific Skeptic belongs in `skeptic-questions.md`, not core `skeptic.md`.

Optional code review probes:

- Tests: do tests assert behavior, failure paths, integration seams, and negative cases rather than only "does not crash"?
- Mocks: does a mocked test still exercise the production contract, or only verify the mock?
- Mapping: can representative data hide swapped fields, dropped fields, stale defaults, or lossy transforms?
- State: can cache, concurrency, retry, or lifecycle behavior silently pass normal tests?
- Boundaries: is ownership clear between caller, callee, storage, external service, and renderer?
- Sensitive surfaces: check auth, filesystem, subprocess, network, deserialization, secrets, and privilege boundaries first when present.

## Activation Rule

Run these probes only after normal Skeptic indicates code/test/integration risk, weak confidence, or high impact. Do not activate them blindly for non-code artifacts.
