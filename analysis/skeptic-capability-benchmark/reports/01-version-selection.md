# Version Selection

## Selection Rule

Freeze 5-7 historical Skeptic formats that represent distinct capability boundaries. Do not test every commit.

## Frozen Formats

| Format ID | SHA | Date | Why selected |
|---|---:|---|---|
| `F0-earliest-usable` | `c5e2931` | `2026-05-02T18:08:21+03:00` | Earliest usable format with both `skeptic.md` and `skeptic-questions.md`. |
| `F1-pre-invocation-contract` | `3e72bf0` | `2026-05-10T10:05:12+03:00` | Pre-contract checkpoint before formal invocation rules. |
| `F2-run-skeptic-contract` | `a30772e` | `2026-05-22T13:55:00+03:00` | Adds explicit `RunSkeptic` source-of-truth and no-edit contract. |
| `F3-worker-receipts` | `4481290` | `2026-05-27T12:09:25+03:00` | Adds compact receipt requirements. |
| `F4-questions-to-lenses` | `54c9890` | `2026-05-28T13:33:20+03:00` | Major shift from questions to lenses. |
| `F5-current-main` | `183acd39cc51a8ada33bcf7506d506aa528fbca7` | `2026-05-29T12:19:48+03:00` | Current main; adds lens/aspect and domain compatibility updates. |

## Identification Notes

- Earliest usable Skeptic: `F0-earliest-usable`.
- Before major rewrite: `F1-pre-invocation-contract`.
- After domain questions were introduced: represented by `F0-earliest-usable` because `skeptic-questions.md` exists there; semantic compatibility later changes are represented by `F5-current-main`.
- After thinker lenses were introduced: `F4-questions-to-lenses`.
- After aspect tags were introduced: `F5-current-main`.
- Current `main`: `F5-current-main`.
- Suspicious capability boundary: `F3-worker-receipts`, where receipt requirements may affect evidence and worker claims.

## Extraction Evidence

Snapshots were extracted with `git show <sha>:<file>` into `analysis/skeptic-capability-benchmark/versions/<format-id>/`. SHA-256 hashes are recorded in each `metadata.md`.

## Limitation

This freeze selection measures current-agent behavior under historical instruction snapshots. It does not reconstruct historical model outputs.
