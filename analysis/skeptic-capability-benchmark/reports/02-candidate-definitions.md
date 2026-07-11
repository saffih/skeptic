# Candidate Definitions

## Candidate Set

| Candidate ID | Base | Minimal change under test | Target capabilities |
|---|---|---|---|
| `C0-current-main` | `F5-current-main` | No change. | Baseline. |
| `C1-current-main-plus-loop-collect` | `F5-current-main` | Optional `loop: collect` runtime behavior. | `LOOP`, `NOISE`, `EVID` |
| `C2-current-main-plus-code-skeptic-domain-extension` | `F5-current-main` | Optional code-specific domain probes in `skeptic-questions.md` layer. | `CODE`, `WEAK`, `SILENT`, `SPOT`, `ACTIONABLE` |
| `C3-current-main-plus-loop-and-code-extension` | `F5-current-main` | Composition of `C1` and `C2`. | `LOOP`, `CODE`, `WEAK`, `SILENT`, `SPOT`, `ACTIONABLE` |

## Guardrails

- Candidate definitions live only under `analysis/skeptic-capability-benchmark/candidates/`.
- No real source file is edited.
- `loop: collect` must be optional and must not change normal Skeptic behavior when absent.
- Code-specific Skeptic belongs in `skeptic-questions.md`, not core `skeptic.md`.
- Candidate promotion is blocked by any `-1` in `PERM`, `FIXAUTH`, `SRC`, `EVID`, or `WORKER`.

## Design Status

Candidate definitions are frozen for later benchmark execution. No candidate has been run or scored in this task.

## Candidate Hashes

Computed with `find analysis/skeptic-capability-benchmark/candidates -type f -print0 | xargs -0 shasum -a 256`.

| Candidate file | SHA-256 |
|---|---|
| `analysis/skeptic-capability-benchmark/candidates/C0-current-main/definition.md` | `bb5a68b3d5aabfcfe875161bf266a2a1078968cefdc23f8c9e6fd6904c09dd6f` |
| `analysis/skeptic-capability-benchmark/candidates/C1-current-main-plus-loop-collect/definition.md` | `3e6b77186277d6a4abf257c5f64e6c5940c2432bb771d82a468029adc2b70aaf` |
| `analysis/skeptic-capability-benchmark/candidates/C2-current-main-plus-code-skeptic-domain-extension/definition.md` | `122874f4a8a9383a045afa913ee255cf97081c07268f3e08a75b85036aebe85c` |
| `analysis/skeptic-capability-benchmark/candidates/C3-current-main-plus-loop-and-code-extension/definition.md` | `9567e6cc9266131bd36fabb4638b4a9fc0c50092aecb853ff8bb31f1f4535c0c` |
