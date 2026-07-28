# Skeptic repository consolidation receipt — 2026-07-27

## Canonical path

`skeptic.md` is the portable Skeptic specification. `AGENTS.md` is the
repository entry map. `agents/` owns Lead, Task Prompt, routing, return, and
Boundary contracts. `harness/quickcompare.py` owns the lightweight A/B
instrument. `benchmarks/benchmark.py` and `benchmarks/judge.py` own the stable
golden benchmark and blinded human packet flow. `plans/backlog-ledger.md` and
`plans/preservation-cleanup-ledger.md` own this consolidation's open work and
evidence. Generated benchmark results remain runtime-owned and ignored.

## RunSkeptic planning receipt

- Source read: current `skeptic.md`; its content matches the remote-main source at `b812f86a52577cb7604e5bd8fdd25aa8e37972f4`; final local consolidation HEAD is recorded below.
- Companion files: `AGENTS.md`, `workflows/task_prompt.md`, `agents/lead_agent.md`, and `agents/model_routing_policy.md`.
- Permission: read-only review of the execution plan.
- Major steps: Gate, Fundamental Scan, Map, all Thinkers, structural checks, selective domain checks, confidence, stabilization, evidence, decision, and verification planning.
- Thinkers: Charlie Munger, Occam, Feynman, Popper, Kant, and Saffi/SH; SH applied to the preservation-versus-cleanup tradeoff.
- Findings: preservation-first execution is safe; PR/API state and fresh behavioral candidate proof remain unresolved; candidate promotion must stay blocked.
- Decision path: `DECOMPOSE` the broad task into inventory, preservation, canonical documentation, deterministic validation, and reserved review; no semantic redesign or deletion.
- Verification: live Git state, clean worktree, 145 repository tests, benchmark validation/prepare/score, JSON validation, and diff checks.
- Unresolved conflicts/unknowns: fresh model-based QuickCompare/behavioral equivalence and owner decisions about any remote PR action.
- Final output category: `HANDLED` for this read-only planning review; the repository task remains gated on the unresolved evidence above.

## Candidate status

Candidate 1 remains `KEEP_AS_CANDIDATE` / promotion blocked. The historical
original payload is the 504-line file at commit `f587069` (SHA-256
`4b9a690e...28f5b9`); the compatibility branch at `6107264` carries a 511-line
revision, and the repaired branch at `57382a2` is a 526-line artifact with deterministic audit history. Current
main has neither candidate payload as canonical. Mechanical tests and historic
calibration do not establish current behavioral equivalence, communication
quality, minority-harm protection, long-tail behavior, or rare-scenario safety.

## Validation evidence

Observed in this run:

- `uv run python -m unittest discover -s tests` — 145 tests, `OK`.
- `python3 benchmarks/benchmark.py validate` — 12 cases, 4 critical, 52 required concepts, all six families.
- `python3 benchmarks/benchmark.py prepare --skeptic skeptic.md --output /tmp/skeptic-prompts-20260727.json` — 12 prompts prepared.
- `python3 benchmarks/benchmark.py score --responses benchmarks/example_outputs/expected-good.json --output /tmp/skeptic-good-score-20260727.json` — recall 1.000, compatibility 1.000, forbidden 0. This is a deterministic fixture check, not behavioral proof.
- `python3 harness/quickcompare.py --help` — instrument entry point and budget contract available.
- `python3 -m json.tool docs/repository-inventory-2026-07-27.json` and `git diff --check` — pass.

QuickCompare did not execute a generator/judge comparison: no current-main
baseline/candidate response package and no authorized model runtime were
available. The deterministic QuickCompare test coverage was included in the
145-test suite. This is recorded as `UNAVAILABLE`, not as a pass.

## Continuation reconciliation and review loop

Read-only GitHub reconciliation observed PR #2 and PR #20 as `OPEN`, PR #4 and
PR #18 as `CLOSED`, and PR #21 as `MERGED`. Local branch/worktree evidence and
unique-value dispositions are recorded in the inventory and preservation
ledger. No remote mutation was performed.

Three consecutive continuation review passes found no new meaningful
actionable finding after correcting the stale PR/API claim and clarifying
local-versus-remote main provenance. Candidate 1 remains separate and
unpromoted; no fresh external model comparison was available.

Final integrated review: PASS_WITH_EXPLICIT_DEFERRED_ITEMS. The documentation
consolidation, provenance, preservation decision, deterministic validation,
historical reconciliation, and candidate status agree. Fresh behavioral
equivalence remains unproven, and remote PR disposition/integration remains
outside this task's authorization.

## Final receipt

```text
VERDICT: PASS_WITH_EXPLICIT_DEFERRED_ITEMS
MODEL_AND_EFFORT: requested economical deterministic route; actual model/runtime unknown
AUTHORITATIVE_MAIN_BEFORE: b812f86a52577cb7604e5bd8fdd25aa8e37972f4
FINAL_HEAD: recorded by final git verification after this receipt commit
WORKTREE: primary /Users/saffi/code/skeptic, main; clean before patch, final state reported by git status
COMMITS_CREATED: `0430974`, `d49b7f8`, `c4ca870`, `53e3054`, `323819d`, plus this final receipt commit
FILES_ADDED: docs/repository-inventory-2026-07-27.json; plans/backlog-ledger.md; plans/preservation-cleanup-ledger.md; docs/repository-consolidation-2026-07-27.md
FILES_MODIFIED: none
FILES_REMOVED: none
UNIQUE_VALUE_HARVESTED: branch/worktree/candidate/benchmark value recorded in ledgers; no uncertain artifact removed
TECHNICAL_DEBT_REMOVED: none; deletion evidence was insufficient
BACKLOG_COMPLETED: explicit items listed in plans/backlog-ledger.md
BACKLOG_PARKED: explicit items listed in plans/backlog-ledger.md
BACKLOG_SUPERSEDED: none newly asserted
OWNER_DECISIONS_REMAINING: remote PR disposition/integration; semantic items marked NEEDS_OWNER_DECISION
COMPACT_CANDIDATE_STATUS: KEEP_AS_CANDIDATE; PROMOTION BLOCKED pending exact payload and fresh behavioral proof
TESTS: 145 passed via uv run python -m unittest discover -s tests
QUICKCOMPARE: instrument available and deterministic tests pass; model comparison UNAVAILABLE
BENCHMARK: validate/prepare/fixture-score pass; no model behavioral claim
MECHANICAL_AUDIT: current repository tests and JSON/diff checks pass; candidate audit remains historical
BEHAVIORAL_REVIEW: separate review recorded as unavailable for fresh candidate behavior; communication and rare-scenario risk remains open
REMOTE_MUTATIONS: none
KNOWN_LIMITATIONS: no fresh model runtime or candidate payload on main; remote PR mutations are unauthorized
NEXT_RECOMMENDED_TASK: run bounded fresh baseline-vs-candidate behavioral review when an approved model runtime and exact candidate payload are available
```
