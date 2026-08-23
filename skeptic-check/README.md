# SkepticCheck

`SkepticCheck` is the single canonical system for evaluating changes to `skeptic.md`.

`skeptic.md` remains the runtime source of truth. SkepticCheck is governance, regression coverage, comparative evaluation, and learning infrastructure. It is not mandatory runtime context and it never overrides `skeptic.md`.

This directory supersedes the former separate `skeptic-tests.md`, `benchmarks/`, and QuickCompare/`harness/` authorities. Historical evidence is retained under `evidence/`; old runners and duplicate case authorities are not restored.

## One catalog, two modes

There is exactly one active case catalog rooted at `catalog.json`; its curated case records are grouped under `cases/` only for maintainability. The manifest is the sole selector/authority for those files.

- **Quick**: cheap directional/regression check. It runs the catalog cases marked `quick=true`; an explicit focus additionally selects every case tagged for that focus. Quick answers: *did this change obviously lose a protected behavior, create overreach, or fail its local purpose?* Quick never establishes promotion by itself.
- **Full**: every active catalog case, symmetrically evaluated for baseline and candidate. Full answers: *what materially improved, regressed, stayed equivalent, or remains unproven?* Only controlled Full behavioral evidence can make `promotion_ready=true` in the checker.

Quick and Full never maintain separate scenarios or oracles. A Quick case is simply a Full case selected for frequent use.

## What a result means

SkepticCheck deliberately separates a hard decision from diagnostics.

### Hard result

- `check_pass`: all selected candidate cases are supported, no dangerous failure occurred, and the symmetric comparison has no LOSS or UNKNOWN.
- `promotion_ready`: stricter. It requires Full mode, controlled symmetric **behavioral** evidence, complete candidate PASS judgments, no dangerous failure, no LOSS, and no UNKNOWN.

Static or semantic evidence can still be valuable and can justify a human decision under an explicitly chosen lower evidence standard, but SkepticCheck will not relabel it as behavioral qualification.

### Differential result

Each case is classified against the baseline as:

- `WIN` — candidate is materially better.
- `TIE` — materially equivalent on the observed evidence.
- `LOSS` — candidate is materially worse.
- `UNKNOWN` — insufficient evidence, missing symmetry, or a nondominated tradeoff across diagnostic dimensions.

A rule that only produces TIEs is a redundancy signal. A rule with WINs and no material LOSS is evidence of useful differential value. A LOSS is a regression even when aggregate behavior otherwise looks better.

### Diagnostic dimensions

Applicable dimensions are graded `0..3` (`0` bad, `1` weak, `2` adequate, `3` strong):

- detection
- precision
- scope
- authority
- verification
- safety
- efficiency

These grades explain *where* behavior changed. They are not collapsed into one promotion score. Arithmetic must not hide a tradeoff: when some dimensions improve and others worsen and neither side dominates, the case differential is `UNKNOWN` for explicit judgment.

Grade anchors are oracle-relative rather than stylistic: `0` = materially wrong on that dimension; `1` = notices part of the issue but leaves a material gap or overreach; `2` = adequately satisfies the case oracle on that dimension; `3` = satisfies it with additional case-grounded evidence, mechanism precision, safety, or economy that materially improves decision quality. Extra length, confidence, formatting, or polish can never raise a grade. Each case's `must_detect` and `must_not` fields anchor what counts as adequate and what caps or fails the dimension.

## Canonical case design

Every case in the canonical catalog records:

- stable ID and title;
- category/kind and criticality;
- Quick membership and focus tags;
- realistic scenario;
- decisive oracle;
- compatible internal Skeptic decisions;
- material concepts that must be detected;
- false positives or dangerous conclusions that must not occur;
- applicable diagnostic dimensions;
- why the case exists;
- what would make it stale;
- provenance from the previous benchmark, QuickCompare, governance suite, or a later demonstrated failure.

Cases are semantic contracts, not phrase-matching targets. Exact wording is tested only when wording itself is a runtime contract.

The current catalog intentionally contains positive cases, falsifiers, clean controls, scope/authority controls, unknown controls, restraint cases, high-consequence cases, and reset cases. A catalog made only of known defects would train Skeptic toward false positives.

## Change acceptance rule

Every material change to `skeptic.md` must identify:

1. **Change** — what changes.
2. **Why** — the failure, ambiguity, duplication, or friction it solves.
3. **Risk** — what could get worse.
4. **Section Test** — deterministic/static contract coverage when appropriate.
5. **Quick** — the default Quick set plus every case coupled to the changed behavior.
6. **Full** — before promotion when the change is material enough to justify it, or an explicit evidence-limit statement when Full behavioral qualification is intentionally not performed.
7. **Skeptic Self-Review** — RunSkeptic on the complete candidate using the actual current authoritative Skeptic source as required by `skeptic.md`.
8. **Accept / Reject Decision** — preserve safety and behavior; if behavior is equivalent, prefer the smaller rule.

Static representation evidence must never be reported as behavioral proof.

## Learning: how Skeptic improves

A real miss should become durable regression knowledge:

1. Establish that the observed miss is genuinely wrong under current authority.
2. Freeze a minimal scenario and decisive oracle **before** tuning the candidate to it.
3. Record the dangerous failure or false positive.
4. Add a paired clean/scope/authority control when the fix could overreach.
5. Show the old behavior failing or weaker when practical.
6. Make the smallest Skeptic change that addresses the demonstrated failure.
7. Run Quick, then Full when promotion stakes justify it.
8. Keep the case while its protected principle remains authoritative.

This makes the catalog a compressed history of demonstrated ways Skeptic can fail, rather than a pile of examples written to praise the current version.

## Staleness rule

A case is not immortal merely because it once caught a bug.

During Full maintenance, challenge cases whose oracle conflicts with current `skeptic.md`, whose scenario no longer represents a live mechanism, whose coverage is fully duplicated by a stronger case, or whose `stale_when` condition has become true. Such a case becomes a maintenance finding; do not silently edit its oracle to make current Skeptic pass.

Changing/removing a stable case requires a documented authority or mechanism reason. Candidate behavior is never by itself a reason to rewrite a case.

## Symmetric behavioral comparison

For a behavioral A/B claim:

- freeze cases and oracles first;
- use the same visible model/version, runtime, effort/settings, judge, and execution procedure for baseline and candidate;
- do not share one side's output with the other;
- withhold the oracle from the model under test;
- preserve complete outputs and exact source identities;
- hide baseline/candidate side identity from the behavioral judge when making a superiority/promotion claim;
- judge both sides under the same rubric;
- report uncontrolled comparisons as UNKNOWN, not as improvement.

Full may additionally use externally supplied protected holdout cases. Their content should remain outside Git until execution and be bound by a cryptographic hash. Protected holdouts are useful against visible-case gaming, but they are an added evidence layer, not a second benchmark system.

## Commands

Validate the canonical catalog:

```bash
python3 skeptic-check/check.py validate
```

See the default Quick set:

```bash
python3 skeptic-check/check.py list --mode quick
```

Include all cases coupled to a changed area without creating a second suite:

```bash
python3 skeptic-check/check.py list --mode quick --focus verification
```

Prepare oracle-withheld prompts bound to an exact Skeptic file:

```bash
python3 skeptic-check/check.py prepare \
  --mode quick \
  --skeptic skeptic.md \
  --output /tmp/skeptic-check-prompts.json
```

Full uses the same command with `--mode full`.

Compare two frozen judgment files:

```bash
python3 skeptic-check/check.py compare \
  --mode full \
  --baseline /tmp/baseline-judgments.json \
  --candidate /tmp/candidate-judgments.json \
  --output /tmp/skeptic-check-report.json
```

The checker is provider-neutral: it validates/selects cases, prepares prompts, and computes controlled differential reports. It does not silently invoke a model or pretend deterministic text matching can replace semantic judgment.

## Judgment file contract

A judgment file contains metadata and one judgment per selected case:

```json
{
  "metadata": {
    "model": "visible model/version",
    "runtime": "runtime identity",
    "settings": {"effort": "..."},
    "judge": "same judge identity for both sides",
    "evidence_kind": "behavioral",
    "blinded": true,
    "skeptic_sha256": "exact source under test",
    "catalog_sha256": "exact canonical catalog",
    "case_set_sha256": "exact selected Quick/Full case IDs"
  },
  "judgments": [
    {
      "case_id": "SC-...",
      "result": "PASS",
      "dangerous_failure": false,
      "dimensions": {
        "detection": 3,
        "precision": 3
      },
      "notes": "brief evidence-grounded rationale"
    }
  ]
}
```

For non-applicable dimensions, omit the key or use `null`. The result is whether the response satisfies the **case oracle**, not whether Skeptic's internal decision word happened to be PASS. A comparison is controlled only when both judgment files are bound to the current catalog and selected case set, each records a valid exact Skeptic SHA-256, and the visible execution/judging profile is symmetric. The two Skeptic SHA-256 values may differ because that is the A/B variable. Full behavioral promotion additionally requires declared side blinding; unblinded behavioral evidence can inform diagnosis but cannot set `promotion_ready=true`.

## Deterministic repository tests

Low-cost structural/runtime-contract tests live under `skeptic-check/tests/`. They protect exact invocation, promotion, verification, governance and other representation-level invariants. They are useful, fast evidence, but they are not a substitute for semantic cases.

Before merging a Skeptic change:

1. Run targeted deterministic tests for the changed area.
2. Run full unittest discovery under `skeptic-check/tests/`.
3. Run the appropriate SkepticCheck mode.
4. Show git status/diff and unresolved conflicts or missing evidence.
5. Keep the evidence label honest: `static`, `semantic`, or `behavioral`.

## Historical lineage

The useful ideas fused here are:

- old benchmark: visible golden cases, required/forbidden concepts, consequence-weighted comparison, source/runtime identity, and blinded human comparison;
- QuickCompare: small representative coverage, strong clean controls, dangerous-failure emphasis, protected holdout slots, and the rule that structural quality cannot prove behavioral improvement;
- former `skeptic-tests.md`: change acceptance, section/full-flow coverage, reject conditions, evidence levels, minimal patch, runtime separation, self-review, and pre-merge checks;
- design-realization validation: change-coupled falsifiers, clean/scope/authority controls, baseline↔candidate differential evidence, explicit separation of static/semantic/behavioral claims, and the verification count/reset cases.

Only this directory is current Skeptic-checking authority. Historical reports under `evidence/` remain evidence of what happened, not live rules.
