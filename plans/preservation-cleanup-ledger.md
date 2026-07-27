# Preservation and cleanup ledger — 2026-07-27

## Mandatory preservation checkpoint

Checkpoint status: `PRESERVATION_PASS` for the economical, documentation-first
consolidation. The primary worktree was clean at start and remains protected.
No remote branch, pull request, tag, worktree, candidate, calibration output,
or uncertain local artifact was deleted.

- Local authoritative state: final HEAD is recorded in the consolidation receipt (`main`, six commits ahead)
- Remote `origin/main`: `b812f86a52577cb7604e5bd8fdd25aa8e37972f4`
- Repository: `git@github.com:saffih/skeptic.git`
- Primary worktree: `/Users/saffi/code/skeptic`, `main`
- Inventory: `docs/repository-inventory-2026-07-27.json`
- Backlog: `plans/backlog-ledger.md`
- PR reconciliation: read-only GitHub access was restored during continuation; PR #2 and PR #20 are open, PR #4 and PR #18 are closed, and PR #21 is merged. Remote actions remain unauthorized.

## Preservation ledger

| Artifact / area | Unique value | Main contains it? | Destination / evidence | Disposition |
|---|---|---:|---|---|
| `skeptic.md` | Canonical portable Skeptic source | yes | current main SHA above | KEEP_CANONICAL |
| `AGENTS.md` and `agents/` | Repository entry map and lightweight orchestration contracts | yes | current tracked files and 145-test suite | KEEP_CANONICAL |
| `harness/quickcompare.py` and visible fixtures | Fast A/B instrument and safeguards | yes | `harness/`, QuickCompare tests | KEEP_CANONICAL |
| `benchmarks/` | Stable golden benchmark, scorer, discovery inventory | yes | `benchmarks/` and benchmark tests | KEEP_CANONICAL |
| `benchmarks/baselines/v1` | Historical baseline evidence | yes | immutable historical directory | KEEP_CANONICAL |
| `docs/compact-skeptic-wrapup-2026-07-26.md` | Candidate history and known gaps | yes | docs; now indexed by this ledger | DOCUMENT_ONLY |
| commit `f587069` candidate bundle | Exact 504-line candidate payload, calibration fixtures/results | no | reachable from candidate history; SHA-256 `4b9a690e...28f5b9` | PARKED_PENDING_DECISION |
| commit `6107264` candidate branch | 511-line compatibility revision and audit tooling | no | `origin/repair/candidate1-compat` | PARKED_PENDING_DECISION |
| commit `57382a2` repaired candidate | Compatibility repair and deterministic audit history | no | `origin/agent/promote-compact-skeptic-candidate1-clean` | PARKED_PENDING_DECISION |
| commit `197bf70` QuickCompare calibration | Cache identity and raw privacy repair | partly | remote branch and current harness history | MERGE_UNIQUE_VALUE already represented; retain history |
| commit `b55e3a0` scorer V3 | Semantic-equivalence repair history | no | remote branch; conflict-sensitive | UNKNOWN_DO_NOT_REMOVE |
| Lead/hierarchical branches | Alternative orchestration experiments | no | refs/worktrees and inventory | UNKNOWN_DO_NOT_REMOVE |
| ignored caches and `__pycache__` | Regenerable local output | no | ignored paths; not source | REGENERABLE_OUTPUT |

## Cleanup decision

Approved cleanup count: zero. The available evidence supports documentation
and canonical-path clarification, but not deletion. Remote deletion is
excluded, and several local worktrees are
registered or contain potentially unique evidence. Deleting them would violate
the safe default of preservation.

## Canonical ownership

| Function | Canonical owner |
|---|---|
| Skeptic specification | `skeptic.md` |
| Optional questions/tests | `skeptic-questions.md`, `skeptic-tests.md` |
| Lead/task/routing/boundary contracts | `AGENTS.md`, `agents/` |
| QuickCompare | `harness/quickcompare.py` and `harness/fixtures/quick-v1/` |
| Golden benchmark | `benchmarks/benchmark.py`, `benchmarks/cases.json` |
| Blinded human packet | `benchmarks/judge.py` |
| Backlog and consolidation evidence | `plans/backlog-ledger.md`, this file |
| Candidate status | this file plus `docs/compact-skeptic-wrapup-2026-07-26.md` |
| Generated results | ignored `benchmarks/results/` or runtime-owned external paths |

## Reproduction commands

```bash
uv run python -m unittest discover -s tests
python3 benchmarks/benchmark.py validate
python3 benchmarks/benchmark.py prepare --skeptic skeptic.md --output /tmp/skeptic-prompts.json
python3 benchmarks/benchmark.py score --responses benchmarks/example_outputs/expected-good.json --output /tmp/skeptic-good-score.json
python3 harness/quickcompare.py --help
git status --short --branch
```
