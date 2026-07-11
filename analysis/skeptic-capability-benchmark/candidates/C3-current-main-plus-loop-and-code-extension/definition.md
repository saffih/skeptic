# Candidate C3-current-main-plus-loop-and-code-extension

- Candidate ID: `C3-current-main-plus-loop-and-code-extension`
- Base format: `versions/F5-current-main`
- Candidate text location: this definition only; source files are not edited.
- Intended capability target: combined `LOOP`, `CODE`, `WEAK`, `SILENT`, `SPOT`, `ACTIONABLE`

## Composition Rule

Combine the optional `loop: collect` runtime extension from `C1` with the optional code-specific domain extension from `C2`.

## Minimality Constraint

- `loop: collect` remains optional and runtime-related.
- Code-specific probes remain in the domain-question layer.
- Normal single-pass Skeptic behavior must remain unchanged when neither optional mode is activated.
- Disqualification capabilities must not weaken: `PERM`, `FIXAUTH`, `SRC`, `EVID`, `WORKER`.
