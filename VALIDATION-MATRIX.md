# Acceptance-to-evidence matrix

Task: `TT-CONCEPT-OWNED-STRUCTURE-001`; repository: `saffih/skeptic`; base commit/tree: `305fc1a33f4fd40e8db05eda3420c3991e09f66c` / `20881bb258af2dd6c1f334f36b3d34b9344f76ff`.

| criterion | direct evidence |
|---|---|
| exact feature branch/base | Git preflight log and candidate HEAD/tree |
| Slice 5 red/green independent repair | `SLICE5-RED.log`, `SLICE5-GREEN.log`, commit `9e5aff1` |
| frozen mapping | external `MIGRATION-MANIFEST.md`, SHA-256 `3c340c10d061d3855ce615b2a0dc42d7722dfe72afe31354bcf8ad34da9bdfb7` |
| ownership and same-stem pairs | `rg` inventory, tree listing, stale-path scan |
| selective loading | `AGENTS.md`, `CONTEXT-BEFORE.json`, `CONTEXT-AFTER.json`; hidden runtime context UNKNOWN |
| behavior and stable outputs | full unittest log, capability suite log, CLI smoke logs |
| no duplicate implementation/shim | path inventory and no old active paths |
| skeptic.md unchanged | base-to-candidate hash and diff check |
| negative validation probes | `NEGATIVE-PROBES.log`, each probe expected failure |
| structural hygiene | `git diff --check`, stale-reference scan, test discovery count |

Validation loop commands, exit statuses, test counts, candidate commit/tree, manifest hash, matrix hash, and log SHA-256 values are recorded in `RECEIPT.json`.
