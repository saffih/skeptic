# Compact Skeptic wrap-up — 2026-07-26

## Status

This slice establishes a safe standalone-capable Skeptic baseline on current
`main`. It is not the final compact Skeptic candidate and is not claimed to be
behaviorally lossless.

The candidate was rebuilt from:

- base commit: `92b8f69144af5edd0edb1d20e454f624276c1138`;
- authoritative starting file: current `main:skeptic.md`.

## Changes included

### Standalone prompt and task validation

Added a compact built-in check for prompts, plans, workflows, and end-to-end
tasks so `skeptic.md` can be supplied and used outside this repository without
requiring `AGENTS.md` or files under `agents/`.

The core checks:

- objective, DONE, authority, scope, source-of-truth order, output,
  verification, and stop conditions;
- feasibility with the context, evidence, tools, permissions, time, and other
  material resources actually available;
- ownership of dependencies, handoffs, integration, and final verification;
- bounded retry and review loops;
- persistence only when decision-critical state must cross a real boundary;
- no task-level PASS when locally valid steps do not provide a credible,
  owned, end-to-end completion path.

The full repository-specific Task Prompt lifecycle remains outside
`skeptic.md`.

### Promotion safety

Added an explicit rule that unresolved `DECOMPOSE` also blocks readiness or
promotion until the resulting scopes return through GATE and reach valid
outcomes.

The existing tested Promotion Check wording remains unchanged.

### Compaction

Compacted:

- invocation aliases;
- repeated Thinker reporting summaries;
- Razor;
- Expert Review;
- SIFT Review;
- Tag Legend.

The Tag Legend now indexes aspect identifiers while §3 remains the full source
of their definitions.

### Usage architecture

`AGENTS.md` now distinguishes:

1. standalone or externally supplied Skeptic;
2. repository-integrated Skeptic.

Optional question or domain extensions may expand detection but cannot override
the core.

## Validation evidence

Before integration:

- structural safeguard audit: PASS;
- whitespace and patch checks: PASS;
- focused deterministic tests: PASS;
- full deterministic test suite: PASS;
- changed implementation path before documentation: only `skeptic.md`.

These results establish deterministic compatibility with the current test
suite. They do not establish behavioral losslessness.

## Compaction result

Compared with starting `main:skeptic.md`:

| Metric | Main | Candidate | Change | Reduction |
|---|---:|---:|---:|---:|
| Bytes | 27,050 | 26,464 | -586 | 2.17% |
| Words | 4,037 | 3,874 | -163 | 4.04% |
| Lines | 686 | 608 | -78 | 11.37% |
| Approximate tokens | 6,763 | 6,616 | -147 | 2.17% |

The line reduction overstates the context reduction because several lists were
converted to denser prose. Future comparison should prioritize actual tokenizer
count, then bytes/characters and words. Lines are primarily a readability
measure.

## Decisions

### Retained in core

- standalone prompt/task feasibility;
- source and evidence integrity;
- verified-current-need protection;
- constraint, leverage, and compact Pareto/dominance reasoning;
- unresolved `DECOMPOSE` promotion blocker;
- atomic ACT, VERIFY, evidence, and safety invariants.

### Kept outside core

- complete Task Prompt lifecycle;
- Lead and Boundary Agent orchestration;
- completion reserves;
- detailed checkpoint and handoff protocol;
- repository-owned persistence;
- closure envelopes;
- formal multi-state Pareto routing.

### Deferred

- explicit Kant dignity/persons-as-ends wording;
- Artifact Guide compression;
- Detection Confidence and STABILIZE compression;
- HANDLED/CONFLICT schema compression;
- further invariant deduplication;
- creation of a portable expanded task-review question extension.

## Known gaps and risks

1. **No fresh behavioral A/B**

   Model or agent credits were unavailable. The current tests verify text and
   deterministic contracts but do not prove equal model behavior, instruction
   salience, communication quality, or rare-scenario coverage.

2. **Compaction is modest**

   The current slice reduces the estimated context footprint by only about
   2.17%. It should be treated as a safe functional baseline, not completion of
   the compact-Skeptic objective.

3. **Standalone versus integrated extension boundary**

   The two use cases are now documented, but the best packaging for portable
   expanded task-review questions remains undecided. Options include a general
   optional task-review extension or relying on user-supplied domain files.

4. **Human and communication scenarios**

   Deterministic checks do not fully cover dignity, coercion, respectful
   criticism, hidden burden, stakeholder asymmetry, or communication effects.

5. **Functional repetition versus duplication**

   Some repetition may improve model salience, especially for authority,
   evidence, action, verification, and ending invariants. It should not be
   removed solely because wording appears twice.

6. **Compaction metric discipline**

   Future candidates must not use line count as the primary success measure.

## Next plan

### Slice 2 — genuine low-risk deduplication

Start again from the integrated `main` and measure sections before editing.

Investigate:

- canonicalizing repeated output-category definitions;
- further Razor and Tag Legend micro-deduplication;
- compacting Expert Review and SIFT only where remaining duplication exists;
- shortening non-safety list introductions;
- separating core detection rules from exhaustive examples.

Target: meaningful real token reduction, not merely fewer lines.

### Slice 3 — optional extension boundary

Evaluate whether portable expanded prompt/task questions should live in an
optional file analogous to `skeptic-questions.md`.

The extension must:

- be optional for standalone use;
- add detection detail rather than mandatory process;
- not override `skeptic.md`;
- avoid importing repository-specific orchestration.

### Slice 4 — behavioral validation when credits are available

Run protected baseline-versus-candidate behavioral comparisons covering:

- hidden burden and dignity;
- coercive or unfair instructions;
- respectful but direct criticism;
- trust-boundary transitions;
- speculative infrastructure;
- prompt feasibility and unowned completion;
- Pareto false-elimination and long-tail/minority protection;
- ordinary negative controls where no finding should be invented.

Require deterministic compatibility plus no material behavioral regression.

## Promotion interpretation

This integration records a safe, tested baseline and the current architecture.
It does not close the broader compact-Skeptic program.

The next compact candidate must branch from this integrated `main`, use measured
section-level changes, and preserve standalone operation.
