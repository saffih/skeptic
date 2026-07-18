# Slice Record: Constraint / Leverage / Dominance Routing

Record of the executed Task Prompt for the CH:CR / SH:WL / SH:PF routing
clarification. This is history and evidence, not runtime context. It is not
hash-pinned by any test (per the consolidation plan's tag-not-hash rule).

## Compact Task Prompt (as gated)

- **Execution header**: single Lead agent in one remote session; no worker
  delegation (bounded single-file prose plus deterministic tests - delegation
  cost would exceed value). NOT CLEAN ROOM, same-context, labeled as such.
  No model escalation; forbidden to compensate for defects with more roles.
  Mutation authority: `skeptic.md` (SH section), `skeptic-tests.md`
  (coverage list), `tests/` (one new file), `plans/` (slice record and two
  plan corrections). Merge and push to `main` explicitly authorized by the
  owner's terminal-DONE instruction and second-opinion confirmation.
- **Objective**: executable-tested routing among CH:CR (wrong constraint),
  SH:WL (wrong lever inside a trade-off), SH:PF (proven dominance among
  live options).
- **Exact terminal DONE**: (1) routing subsection in the SH section,
  <= 30 net lines, no new Thinker or verdict token, no mandatory universal
  sequence; (2) eight agreed scenarios executable plus duplication and
  ceremony guards, with intentional red before green; (3) governance
  coverage binding; (4) plan-file corrections (PR #2 overclaim softened,
  harvest rule broadened); (5) focused and full regression green;
  (6) RunSkeptic on the change reaches HANDLED; (7) commit merged to local
  `main`, pushed, and fresh `origin/main` fetched and verified to contain
  it. Branch-only commit, open PR, or unverified push is not DONE.
- **Verified starting state**: `origin/main` = `52cd8226`; branch
  `claude/skeptic-routing-clarification-1efkvx` at `17a9616` (plan file
  only); 77/77 tests green.
- **Authority order**: owner instruction (this session) > `skeptic-tests.md`
  change-acceptance governance > current repo state > this record.
- **Budget**: single session; retry bound 2 per failure class, then
  redesign; completion reserve: merge + remote verification run before any
  optional polish; futility stop if red-to-green fails twice.

## Skeptic Prompt Gate receipt

- Source read: working-tree `skeptic.md` (from `52cd8226` baseline);
  companions `agents/task-prompt.md`, `agents/lead-agent-prompt.md`,
  `skeptic-tests.md`.
- Permission mode: fix-if-valid with explicit publication authority.
- Review level: Task Prompt (Level 2).
- Pass 1 findings (ACTION): PO:OC - consolidation plan called the PR #2
  pilot "direct evidence" for the line-budget principle (13 runs,
  incomplete matrix, confounded variables); KT:HU/OM:FS - plan's harvest
  rule made dogfood failures the only admissible justification for new
  capability, blocking credible external evidence and proven structural
  gaps; missing `skeptic-tests.md` coverage binding for the new tests.
- Fixes applied: all three folded into this slice.
- Pass 2: PASS. Feasibility high (deterministic tests, small bounded
  diff, authority explicit). Protocol cost proportionate to a runtime
  behavior contract. Thinkers considered: CH, OM, FE, PO, KT, SH.

## Red-before-green evidence

Before editing `skeptic.md`, `tests/test_constraint_leverage_dominance_routing.py`
ran 9 tests: 5 self-contained oracle scenarios passed; all 4 tests binding
the prose contract failed as intended:

```text
test_governance_binds_the_coverage ... FAIL
test_no_mandatory_universal_sequence ... ERROR
test_routing_contract_stays_compact ... ERROR
test_runtime_contains_the_routing_contract ... ERROR
Ran 9 tests ... FAILED (failures=1, errors=3)
```

After implementation: 9/9 focused pass; full suite 86/86 pass
(77 baseline + 9 new). `skeptic.md` delta: +16 net lines.

## Scenario coverage (executable, `tests/test_constraint_leverage_dominance_routing.py`)

- RT01 wrong bottleneck, nothing else -> CH:CR only.
- RT02 correct bottleneck, wrong lever in a trade-off -> SH:WL only.
- RT03 options with one proven dominated, no constraint doubt ->
  ELIMINATE_DOMINATED, no other finding.
- RT04 wrong bottleneck plus apparently dominated options -> CH:CR and
  SH:PF deferred (DEFER_EXISTING); elimination blocked as premature.
- RT05 real trade-off, frontier options, no dominance -> SH:WL,
  PRESERVE_FRONTIER, no elimination.
- RT06 ordinary task -> all three silent.
- RT07 constraint and lever defects both material -> exactly two distinct
  findings, no duplicate.
- RT08 incomplete dominance evidence -> DOMINANCE_UNPROVEN; invents no
  constraint or leverage finding.

Guards: routing subsection capped at 30 lines by test; no
mandatory-universal-sequence phrasing; governance binding asserted.

## RunSkeptic receipt (final change)

- Source read: current `skeptic.md` working tree; companions listed above.
- Major steps: GATE -> FUNDAMENTAL SCAN -> MAP -> CONFIDENCE -> STABILIZE
  -> EVIDENCE -> DECIDE -> ACT -> VERIFY.
- Thinkers: CH (CH:EV proportionate at +16 lines; CH:SM reversible single
  commit), OM (no new entities; reuses DEFER_EXISTING and
  DOMINANCE_UNPROVEN; no restatement of the SH:PF rule), FE (mechanism is
  entity-based routing; markers bound by tests), PO (falsifiable via 8
  scenarios; disconfirming case RT04 is dominated-yet-deferred), KT (rule
  is symmetric across lenses; no special pleading), SH (subject of the
  change; NOT_APPLICABLE fallback preserved).
- Evidence: REPRODUCED (red-to-green), OBSERVED (diff, test output).
- Decision path: FIX; verified; no unresolved conflicts or unknowns.
- Known limit, stated per plan principle 1: these tests freeze the
  specification and its decision table; they do not prove that an agent
  reading the prose routes correctly at runtime. Behavioral evidence is
  Track 3 (dogfood) work.
- Output category: HANDLED.

## Task Closure Receipt

- Task Prompt created and gated: yes (pass 2 PASS above).
- Implementation complete: yes (`skeptic.md` +16 lines, tests, governance
  binding, plan corrections).
- Required verification passed: yes (red-before-green recorded; 9/9
  focused; 86/86 full regression).
- RunSkeptic HANDLED: yes (receipt above).
- Integration/publication: filled at merge - commit merged to `main`,
  pushed, fresh `origin/main` fetched and compared.
- Protected state preserved: yes (no files outside declared scope changed;
  `git status` clean of unexpected mutation).
- Unresolved blockers: none.
- Residual risk: runtime-behavior gap named above; routing prose could
  still be misread by an agent - detectable only via dogfood log entries.
