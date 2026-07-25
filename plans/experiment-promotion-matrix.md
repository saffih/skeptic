# Experiment Promotion Matrix

## Purpose

Classify the archived Skeptic experiments without restoring old branch structure,
generated outputs, private evidence, or procedural complexity.

This audit is documentation only. It does not authorize changes to `skeptic.md`,
`agents/`, `benchmarks/`, tests, candidates, or runtime behavior.

## Current clean main

Clean `main` contains:

1. the compact updated `skeptic.md`;
2. the consolidated proportional agent layer;
3. the stable Scorer V2 golden-case benchmark.

## Promotion criteria

Promote an experiment only when:

1. it addresses a material and reproducible failure;
2. current clean `main` misses or weakly handles that failure;
3. the intervention has a falsifiable causal hypothesis;
4. it beats no change, deterministic tooling, domain guidance, or escalation;
5. its context, process, false-positive, and maintenance costs are acceptable;
6. it can be introduced and tested independently.

Statuses:

- `ALREADY_PROMOTED`
- `PROMOTE_INSTRUMENT`
- `RETEST`
- `REDESIGN`
- `PARK`
- `REJECT`
- `ARCHIVE_EVIDENCE`

## Promotion matrix

| Experiment or mechanism | Current evidence | Clean-main coverage | Destination | Status | Minimum next test | Main risk |
|---|---|---|---|---|---|---|
| Stable Scorer V2 golden benchmark | Twelve cases, deterministic scoring, blinded packet tool, historical V1 baseline and focused tests | Present | `benchmarks/` | `ALREADY_PROMOTED` | Generate a fresh current-main baseline when model credits return | Visible cases and deterministic matching can be gamed or mis-score wording |
| QuickCompare v1 | Four verdict paths, schema and budget gates, anonymous A/B judging, cache identity and private raw-file tests | Missing | `harness/` with focused tests | `PROMOTE_INSTRUMENT` | Restore the smallest final verified instrument and run deterministic calibration | Infrastructure growth and duplication of the golden benchmark |
| QuickCompare protected holdouts | Protected-slot contract exists; old private evidence was fragile and environment-bound | Missing by design | Runtime-supplied external evidence | `PARK` | Reconsider only for a live decision where visible cases are insufficient | Custody work may cost more than the decision |
| Stage 6E private comparison | Accepted responses existed, but no final promotion-authority result | Absent | Archive only | `PARK` | Resume only when an exact decision depends on it and a smaller protocol exists | Sunk-cost continuation and fragile private state |
| Compact Candidate 1 | Candidate and repair experiments existed, but the intended substantial size reduction was not established | Selected reasoning gains already retained | Fresh candidate branch | `REDESIGN` | Establish a new baseline and create a genuinely smaller single-variable candidate | Reintroducing complexity or measuring wording instead of behavior |
| Pareto frontier and dominance | Repeated design and benchmark work | Present as `SH:PF` | `skeptic.md` | `ALREADY_PROMOTED` | Add regression coverage only if current cases are insufficient | Overlap with constraint and leverage reasoning |
| Constraint versus leverage clarification | Wrong-constraint experiments and fixtures | Present through `CH:CR`, `SH:WL`, and `SH:PF` | Existing core and cases | `ALREADY_PROMOTED` | Verify current cases distinguish constraint, leverage, and dominance | Repetitive findings |
| Smallest credible alternative | Simplification experiments and false-deletion concerns | Present conditionally | `skeptic.md` | `ALREADY_PROMOTED` | Add paired bloated-design and unsafe-deletion cases | False simplicity |
| Receipt is not proof | RunSkeptic and delegated-return experiments | Present | Existing core and agent return contract | `ALREADY_PROMOTED` | Preserve structural-validity versus substantive-acceptance tests | Receipt ceremony |
| Stateless Lead orchestration | Stateless and boundary experiments | Present | `agents/` | `ALREADY_PROMOTED` | Test a practical multi-step task when credits return | Insufficient durability for interrupted work |
| Conditional Boundary Agent | Context and trust-boundary experiments | Present | `agents/boundary-agent.md` | `ALREADY_PROMOTED` | Compare direct and boundary-assisted delegation on one large-context case | Becoming a mandatory wrapper |
| Cost-aware routing | Routing experiments and compact taxonomy | Present | `agents/model-routing.md` | `ALREADY_PROMOTED` | Verify exact runtime routing only when observable | Inventing unavailable routes or prices |
| Completion-feasibility preflight | Completion-budget and terminal-DONE experiments | Weakly covered | Possible compact Lead rule | `RETEST` | Pair a feasible plan with one that exhausts resources before useful completion | Rebuilding numerical reserves and planning bureaucracy |
| Progressive durability | Checkpoint and artifact-first experiments | Partially covered | Conditional agent guidance | `RETEST` | Interrupt a multi-phase task after an expensive accepted result | Mandatory persistence for trivial work |
| No unnecessary replay | Closure and replay-cost experiments | Partially covered | Agent guidance | `RETEST` | Compare repair-only and full replay after a transport defect | Preserving stale or invalid work |
| Terminal-DONE preservation | Multiple premature handoff and partial-completion failures | Indirectly covered | Tests and possibly one compact sentence | `RETEST` | Distinguish a legitimate blocker from premature stopping | Forcing completion without authority |
| Shadow discovery scenarios | Archived cases cover stale evidence, injection, hidden burden, minority harm, simplification, worker promotion, and completion failure | Mostly absent | Discovery suite first | `RETEST` | Deduplicate, freeze, run current baseline, and retain only distinct mechanisms | Tuning to historical candidates and suite bloat |
| Scorer V3 dignity/coercion logic | Experimental dignity, retaliation, consent, and agency matching | Not present | Separate scorer experiment | `RETEST` | Freeze cases first and compare V2 with a minimal scorer change against manual labels | Encoding preferred wording and confusing scorer gains with Skeptic gains |
| Persons as ends and hidden burden | Repeated coercion and minority-harm discussions | Partially covered by Kant | Core only after repeated misses | `RETEST` | Pair aggregate benefit with hidden burden and voluntary language with career pressure | Overfiring on ordinary incentives |
| Non-maleficence | Concept discussed but not settled | Partially covered by consequences and Kant | Possible cross-cutting rule | `RETEST` | Find repeated cases where existing lenses miss avoidable harm | Redundancy and moralizing noise |
| Impact concentration / vital few | Pareto and priority discussions | Partially covered | Discovery benchmark first | `RETEST` | Show repeated failures not handled by constraint, leverage, or dominance | Duplicate lens and causal overclaiming |
| Full Priority Scan | Structured prioritization discussed but not validated | Missing | Optional routine or domain pack | `PARK` | Demonstrate repeated prioritization failures that current rules cannot solve | Context and process footprint |
| Glossary and Thinker questions | Usability discussions | Limited | Documentation | `RETEST` | Human comprehension review without changing normative behavior | Documentation drift |
| Historical outputs and calibration directories | Useful for reconstructing experiments | Excluded by design | Archive branch | `ARCHIVE_EVIDENCE` | Retrieve only for a specific audit question | Polluting runtime source with stale evidence |
| Old lifecycle state machine | Large historical implementation with substantial friction | Deliberately excluded | Archive only | `REJECT` | Test individual mechanisms separately, never the whole state machine | Process cost obscures substantive work |
| Repeated fix-until-PASS loops | Historical repeated-review workflows | Deliberately excluded | Archive only | `REJECT` | None as a universal rule | Correlated repetition without new evidence |
| Universal workspace layout and mandatory persistence | Historical checkpoint and handoff machinery | Deliberately excluded | Archive only | `REJECT` | None as a universal requirement | Repository-owned runtime state and ceremony |

## Promotion order

### 1. Measurement

Restore QuickCompare as a separate minimal instrument. Exclude generated outputs,
private evidence, provider runners, candidate-specific manifests, and historical
calibration reports.

### 2. Discovery coverage

Extract and deduplicate archived shadow scenarios. Run current clean `main` before
changing Skeptic or agents.

### 3. Compact agent reliability experiments

Test independently:

1. completion-feasibility preflight;
2. progressive durability;
3. repair without unnecessary replay;
4. terminal-DONE preservation.

### 4. Core reasoning experiments

Test independently:

1. persons-as-ends and hidden burden;
2. non-maleficence;
3. impact concentration;
4. Full Priority Scan.

Do not change the scorer and Skeptic in the same controlled comparison.

### 5. Usability

Evaluate headings, glossary, terminology, and Thinker questions only after runtime
behavior is stable.

## Explicit non-promotions

Do not restore wholesale:

- archived ancestry;
- historical candidate directories;
- raw provider responses;
- private holdout content;
- calibration working directories;
- checkpoint hierarchies;
- lifecycle state machines;
- mandatory completion reserves;
- universal persistence;
- repeated identical PASS requirements;
- candidate-specific scorer wording.

## Next recommended branch

`reorg/quickcompare-instrument`

Scope:

- final verified `harness/quickcompare.py`;
- `harness/quickcompare.schema.json`;
- frozen QuickCompare manifest;
- six visible fixtures;
- focused deterministic tests;
- deterministic calibration tests that validate the instrument.

Exclude:

- `calibration/quickcompare-20260724/`;
- `analysis/`;
- generated `results/`;
- private holdout contents;
- provider-specific runners;
- candidate-specific manifests;
- modifications to `skeptic.md`, `agents/`, or `benchmarks/`.

## Decision

QuickCompare is the next bounded implementation candidate.

Behavioral changes remain unapproved until current-baseline discovery cases show
a repeated material gap.

## Archive evidence index

The following commit subjects are navigation evidence only. Their titles do not prove their claims.

```text
197bf70 2026-07-24 Fix QuickCompare cache identity and raw privacy
195c500 2026-07-24 Add QuickCompare resume and calibration guards
765e032 2026-07-24 Add conditional boundary agent governance
3c1d07f 2026-07-24 Repair dignity recognition in benchmark scorer v3
04c8460 2026-07-24 Add cost routing and agent return validation
534aab2 2026-07-23 Repair benchmark scorer interpretation
5f205b4 2026-07-23 Add minimal RunSkeptic golden benchmark
f60a731 2026-07-23 Further simplify task prompt governance
d3063c0 2026-07-23 agents: replace lead-agent-prompt.md with orchestration-only contract (#16)
a3569b0 2026-07-22 Merge pull request #15 from saffih/agents/lead-dispatch-first-entry-sliceA1
68b387a 2026-07-22 agents: add dispatch-first execution entry for the stateless Lead
74cc0fc 2026-07-22 Merge pull request #14 from saffih/agents/lead-stateless-orchestrator-sliceA
64597c1 2026-07-22 agents: define the Lead as a practically stateless orchestrator
126c444 2026-07-22 Merge pull request #13 from saffih/harness/quickcompare-v1
24450c0 2026-07-22 harness: add QuickCompare v1 A/B comparison instrument
6e8b013 2026-07-22 fix: forbid post-acceptance rereview under constrained Lead capacity
d72d9b2 2026-07-21 docs: define stateless runtime boundary
e2fa2a9 2026-07-20 fix: resume task prompts from checkpoints
ad9e42f 2026-07-20 fix: resume lead packages from checkpoints
369c841 2026-07-18 Merge branch 'claude/skeptic-routing-clarification-1efkvx'
7de5ef6 2026-07-18 plans: revise git-hygiene prompt to v2 after review; start dogfood log
015226e 2026-07-18 Merge branch 'main' into claude/skeptic-routing-clarification-1efkvx
c6df30f 2026-07-18 plans: complete routing slice closure receipt
e0a3653 2026-07-18 plans: add gated Task Prompt for git-hygiene slice
ac221cb 2026-07-18 skeptic: add constraint/leverage/dominance routing contract
17a9616 2026-07-18 plans: add consolidation, git-hygiene, and dogfood forward plan
e5494db 2026-07-18 agents: add end-to-end task prompt contract
dd0bd7c 2026-07-18 agents: add completion-budget and progressive-delivery safeguards
3c119a6 2026-07-13 Merge pull request #8 from saffih/feat/feynman-trust-boundary-transition
d847ca6 2026-07-13 skeptic: add trust-boundary transition lens
b62b2c6 2026-07-13 Merge pull request #6 from saffih/feat/skeptic-effort-value-alignment
b3d6d9e 2026-07-13 skeptic: align effort with value and completion
```

Archive ref at audit creation:

```text
197bf70d35ce791de7de7499a58bb2a4f970450e
```
