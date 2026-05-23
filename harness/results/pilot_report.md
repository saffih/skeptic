# Skeptic Detection Effectiveness — Pilot Report

Date: 2026-05-23
Model: Claude Sonnet (via Claude Code subagents)
Temperature: not controllable (subagent default)

## Method

Ran 3 question set variants against 3 test cases (9 combinations), then ran 2 more sets against 2 SH-targeted cases (4 more combinations). Total: 13 runs.

Question sets tested:
- **razor** (4 questions): OM1, KT1, PO1, CH8
- **ch_po** (14 questions): CH1-CH8, PO1-PO6
- **full_skeptic** (86 questions): all thinkers + structural + domains
- **sh_only** (6 questions): SH1-SH6

Test cases:
- **tc01** (code/easy): bare except, magic retry, silent None return
- **tc06** (design/medium): hidden SPOF, undocumented assumption, no circuit breaker
- **tc17** (mixed/hard): silent except, no monitoring, no transaction, race condition
- **tc08** (requirements/medium): solution-without-problem, tech mandates, R-3 vs R-7 contradiction
- **tc11** (agent instructions/medium): validation-vs-speed contradiction, stale API ref, no rationale

## Coverage Matrix — Main (3 sets x 3 cases)

| Question Set | tc01 code/easy | tc06 design/med | tc17 mixed/hard | Prec | Recall | F1 | TP/q |
|---|---|---|---|---|---|---|---|
| razor (4q) | 3/3 | 2/3 | 2/4 | 0.88 | 0.70 | 0.78 | 1.75 |
| ch_po (14q) | 3/3 | 2/3 | 3/4 | 0.73 | 0.80 | 0.76 | 0.57 |
| full_skeptic (86q) | 3/3 | 3/3 | 3/4 | 0.60 | 0.90 | 0.72 | 0.10 |

## Coverage Matrix — SH Focus (2 sets x 2 cases)

| Question Set | tc08 requirements | tc11 agent instructions |
|---|---|---|
| razor (4q) | 3/3 | 1/3 |
| sh_only (6q) | 3/3 | 1/3 |

## Efficiency Analysis

| Set | Questions | Total TP | Total Findings | TP/question | Noise |
|---|---|---|---|---|---|
| razor | 4 | 7/10 | 15 | 1.75 | 8 |
| ch_po | 14 | 8/10 | 27 | 0.57 | 19 |
| full_skeptic | 86 | 9/10 | 36 | 0.10 | 27 |

## What Each Set Missed (main matrix)

### razor (4q) — 3 misses
- tc06_i3: No circuit breaker, graceful degradation, or fallback behavior
- tc17_i2: No monitoring, alerting, or health reporting
- tc17_i3: write_results inserts records without a transaction

### ch_po (14q) — 2 misses
- tc06_i3: No circuit breaker, graceful degradation, or fallback behavior
- tc17_i2: No monitoring, alerting, or health reporting

### full_skeptic (86q) — 1 miss
- tc17_i2: No monitoring, alerting, or health reporting

## SH Analysis

SH and razor scored identically on the SH-targeted cases (tc08, tc11). Both caught the core contradictions, both missed the same issues (stale API reference, missing rationale).

The misses are expected: SH is about trade-off resolution, not staleness (FE domain) or rationale checking (FE domain). SH's value is in diagnosis quality (naming the trade-off structure, identifying which side should dominate), not in finding issues other thinkers miss.

## Key Findings

1. **Diminishing returns are steep.** Razor's 4 questions catch 70% of issues. Going from 4→86 only gains +20% recall while precision drops from 88%→60%.

2. **The efficiency cliff is dramatic.** Razor: 1.75 TP/question. Full Skeptic: 0.10 TP/question. The last 72 questions collectively find only 2 more issues.

3. **Thinkers can't fill domain gaps.** All sets missed monitoring/alerting (tc17_i2). This requires REL1: "how would you know this is silently broken?" No thinker framing naturally triggers it.

4. **SH adds diagnostic depth, not detection breadth.** It finds the same issues as razor through a richer analytical lens but doesn't catch new ones.

5. **The sweet spot is ~10-15 questions.** Razor core (4) + targeted domain questions (REL1 for monitoring, DAT for atomicity, FE for staleness) would likely hit 90%+ recall without the precision drop.

## Next Steps

- Test razor+FE (10q) to see if FE fills the staleness/rationale gap
- Test razor+REL1+DAT2 (6q) to see if 2 domain questions fix the monitoring/atomicity gaps
- Run full 17-set x 18-case matrix for comprehensive data
- Build fused question sets and measure against this baseline
