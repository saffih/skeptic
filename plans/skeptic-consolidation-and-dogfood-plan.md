# Skeptic Consolidation and Dogfood Plan

## Objective

Make this repository a practical instrument for generating safe designs and
code, while stopping runtime-file growth, clearing git leftovers, and
grounding future capability work in real usage evidence instead of
self-referential tests.

This plan orders work; it does not itself change `skeptic.md`, close PRs, or
delete branches. Each track below becomes its own bounded slice with its own
DONE.

## Evidence checkpoint

- `main` at `52cd8226c276186530a32a52b36d5a3943434faa`; 77/77 tests green.
- Runtime file sizes: `skeptic.md` ~761 lines, `agents/lead-agent-prompt.md`
  ~572 lines, `agents/task-prompt.md` ~439 lines.
- Open PRs: #4 (stale lead-context patch, base `b071899`, 14 behind), #2
  (fork: Karpathy integration + detection-effectiveness harness, base
  `43021c3`, May 2026).
- Ten non-main remote branches; four are fully merged (0 ahead), six carry
  unmerged commits (see disposition table).
- `plans/skeptic-next-capability-sh-pf.md` is pinned byte-for-byte by
  `FROZEN_CONTRACT_SHA256` inside `tests/test_pareto_frontier.py`.

## Governing principles (agreed in review)

1. **Tests freeze the contract; they do not prove behavior.** The Python
   oracles and marker checks are specification regression. Behavioral claims
   about agent decisions require dogfood evidence or planted-issue runs.
   Closure receipts must state which kind of evidence they carry.
2. **Scenario-first legislation.** No new lens, Thinker, or cross-cutting
   rule without at least one concrete recorded case the current framework
   handled wrongly. This gate applies to non-maleficence and Kant
   persons-as-ends work.
3. **One authoritative home per doctrine.** Shared doctrine is stated once
   and referenced elsewhere, never restated in three files.
4. **Runtime line budget.** Every capability slice states its net line delta
   on `skeptic.md` up front; the SH:PF slice (~24 net lines) is the
   reference size.
5. **Frozen artifacts are git tags, not live-file hashes in tests.**
6. **Reversible cleanup only.** Archive-tag before any branch deletion;
   close PRs with an explanatory comment, never silently.

## Track 1 - File architecture and separation of uses

Current roles, kept:

| File | Use | Reader |
| --- | --- | --- |
| `skeptic.md` | RunSkeptic review framework: lenses, flow, output categories | any agent asked to review |
| `agents/lead-agent-prompt.md` | Lead role: turn intent into gated prompts | the Lead agent |
| `agents/task-prompt.md` | Whole-task execution contract through terminal DONE | the Lead when executing serious work |
| `AGENTS.md` | entry pointer | every agent, first read |
| `plans/` | decisions and history; never runtime context | humans and planning agents |
| `tests/` | contract regression | CI / verification phases |

Changes:

- **Doctrine ownership map.** Proportional execution, context protection,
  completion reserve, and model-strength discipline currently appear in all
  three runtime files. Assign `agents/task-prompt.md` as the authoritative
  home for execution doctrine; `agents/lead-agent-prompt.md` keeps only its
  role-specific application; `skeptic.md` keeps only what a reviewer needs
  to check. Deduplicate as one bounded slice reporting net line deltas per
  file. Do not create a fourth doctrine file unless deduplication proves
  insufficient (OM:SS).
- **Entry-points section in `AGENTS.md`**: three sentences mapping use case
  to file, so a new agent or human loads only what the task needs.

## Track 2 - Git leftovers disposition

Policy going forward: one slice = one branch = one PR; delete the branch on
merge; parked work gets `archive/<branch-name>` tag, then the branch is
deleted; frozen evaluation contracts are pinned by tag.

| Branch | State | Disposition |
| --- | --- | --- |
| `andrei`, `feat/skeptic-effort-value-alignment`, `plan/skeptic-practical-improvement-reset`, `promotion-check` | 0 ahead of main | delete (already merged; nothing lost) |
| `benchmark/skeptic-capability-stage2-2026-07-04` | 6 ahead; parked Stage 6E evidence explicitly preserved by the reset plan | archive-tag, keep branch until the reset plan's resume condition is formally closed |
| `experiment/skeptic-meta-process-value-ab-001`, `experiment/skeptic-trust-boundary-fe-tb-ab-001` | 8-9 ahead; closed experiments whose conclusions already landed | archive-tag, then delete |
| `claude/lead-agent-prompt-artifact-9rd2na` (PR #4 head) | 3 ahead, 14 behind | close PR #4 with harvest note; archive-tag; delete |
| `pattern-classification`, `revised-questions` | 1-4 ahead, stale since May | archive-tag, then delete |

PR dispositions:

- **PR #4** (lead-context hardening): do not merge. Most of its intent
  (receipt limits, context protection, delegation boundaries) has since
  landed on main via other commits. Before closing, diff its rules against
  current main and harvest anything still missing (candidate: the explicit
  `CONTEXT_PROTECTION_FAILURE` stop token and numeric receipt caps) into a
  fresh small slice only if a dogfood entry shows the gap matters.
- **PR #2** (fork; Karpathy discipline + detection harness): do not merge
  as-is - stale base, two unrelated concerns in one PR. But its
  detection-effectiveness harness (18 planted-issue cases, TP/FP/FN scoring,
  question-set variants) is exactly the behavioral instrument this repo
  lacks. Its pilot result - razor's 4 questions at F1 0.78 vs the full
  86-question set at F1 0.72 - is a limited-pilot association consistent
  with the line-budget principle (13 runs, incomplete matrix, older
  baseline, question count varied together with content and structure); it
  does not prove that file growth caused the lower score. Harvest the
  harness design as candidate tooling in a fresh
  slice once Track 3 justifies it; reply on the PR with that disposition.
- **Frozen-hash fix**: tag the SH:PF contract state
  (`archive/sh-pf-frozen-contract` at the commit whose hash the test pins),
  then change `test_frozen_contract_has_not_changed_after_candidate_output`
  to reference the tag or retire it, so the plan file can be archived or
  annotated without breaking the suite.

## Track 3 - Dogfooding: real usage before new capability

The two self-hosting successes are the friendliest possible domain (the
framework editing its own repo). Evidence that transfers requires using the
framework on external design and code tasks.

- **Dogfood log**: `plans/dogfood-log.md`, one bounded entry per real task
  (max ~15 lines): task and repo, prompt level used (Razor / Agent Prompt /
  Task Prompt), gate verdicts, what materially helped, what was ceremony,
  any failure or near-harm the framework missed, net verdict. The log is
  data, not doctrine; bureaucracy in the log is itself a finding.
- **Harvest rule**: new capability requires a concrete demonstrated failure
  from dogfooding, planted-issue testing, credible external evidence, or a
  proven structural gap - not speculation alone. This applies to
  non-maleficence and persons-as-ends. Three or more log entries are
  required before the next capability decision after routing.
- **Behavioral measurement**: if the log shows detection or routing
  problems, build a planted-issue harness (PR #2 model) as tooling under
  `tests/` or a new `harness/` directory - deterministic scoring, frozen
  cases, tagged contract - rather than adding more prose.

## Work sequence

1. **Slice 1 - CH:CR / SH:WL / SH:PF routing clarification** (current
   branch). Minimal form: a routing paragraph in the SH section keyed on
   entity type (system constraint vs trade-off decision vs comparable
   option set), reuse of `DEFER_EXISTING` for constraint-blocks-elimination,
   one line in STABILIZE, executable scenarios including the eight agreed
   cases, red-before-green evidence. Budget: <= 30 net lines in
   `skeptic.md`; no new verdict tokens; no mandatory sequence.
2. **Slice 2 - Git hygiene** (Track 2): PR closures with comments,
   archive tags, branch deletions, frozen-hash-to-tag migration. Every step
   reversible via tags.
3. **Slice 3 - Doctrine dedup** (Track 1): ownership map applied,
   reference-not-restate, tests pin the single authoritative copy.
4. **Slice 4 - Dogfood** (Track 3): >= 3 real-task entries in the log.
5. **Then**: bounded priority re-scan from the new baseline; evaluate
   non-maleficence / minority-harm scenario-first from harvested failures,
   comparing cross-cutting rule vs lens extension vs seventh Thinker only
   against recorded cases.

Slices 2 and 3 may run in either order after Slice 1; Slice 4 gates
everything after it.

## Using the repo today (until the tracks land)

- Review an artifact or decision: invoke `RunSkeptic` against current
  `skeptic.md`; ordinary small tasks use the Razor pass only.
- Build a prompt for another agent: apply `agents/lead-agent-prompt.md`;
  gate consequential prompts before use.
- Execute serious multi-phase work to a terminal state: instantiate the
  `agents/task-prompt.md` template; proportionality may shrink fields but
  never removes exact DONE, authority, scope limits, verification, or stop
  conditions.

## DONE for this plan document

- Plan committed and pushed to the working branch, readable by the owner.
- Each track executed later under its own slice DONE; this file is updated
  with per-slice outcomes as they merge, or superseded by a successor plan
  with an explicit pointer.
