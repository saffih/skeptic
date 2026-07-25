# Lightweight RunSkeptic benchmark

## Purpose and scope

This is the first small golden-case benchmark for comparing a baseline Skeptic with a candidate Skeptic. It checks whether responses detect material concepts, avoid dangerous conclusions, make compatible internal decisions, and include the current RunSkeptic receipt. It is designed for fast directional regression checks and understandable maintenance.

The benchmark is not an academic evaluation framework, model runner, provider integration, automatic LLM judge, database, dashboard, or proof of universal correctness or safety. It does not replace repository tests or human review.

## Files

- `cases.json`: twelve visible golden cases.
- `benchmark.py`: validation, prompt preparation, deterministic scoring, and comparison.
- `judge.py`: deterministic blinded human-comparison packets and reveal processing.
- `example_outputs/`: complete good and intentionally bad response fixtures.
- `results/`: ignored-by-convention working destination; only `.gitkeep` is versioned initially.
- `tests/test_benchmark.py`: deterministic contract and regression tests.

## Case schema and pattern semantics

Each case has a unique ID, title, category, critical flag, current Skeptic Thinker tags, artifact, compatible internal decisions, required concepts, forbidden concepts, and maintenance notes.

A concept contains alternative pattern groups. Matching is case-insensitive. A concept matches when every term in any one group occurs anywhere in the response. Scorer V2 normalizes Markdown, punctuation, Unicode dashes, hyphenation, whitespace, capitalization, and conservative inflections; it then uses word-bounded phrases rather than raw substrings. A small explicit equivalence table covers documented phrasing variants without fuzzy matching. For example, `[["trust boundary"], ["untrusted", "boundary"]]` matches either the first phrase or both terms in the second group. Patterns represent important ideas, not mandatory prose; keep them narrow enough to avoid accidental matches.

Forbidden concepts use the same bounded matching within one clause. Explicit nearby rejection cues such as “do not,” “reject,” or “unsafe” suppress that clause’s forbidden match. This deterministic negation rule is intentionally narrow and cannot resolve every possible linguistic scope.

The current Thinker families are `CH`, `OM`, `FE`, `PO`, `KT`, and `SH`. Systems-flow cases use current aspects such as `CH:CR`, `CH:SO`, and `SH:WL`; this benchmark does not invent a separate family.

## CLI

Validate case structure and family coverage:

```bash
python3 benchmarks/benchmark.py validate
```

Create deterministic prompts without invoking a model:

```bash
python3 benchmarks/benchmark.py prepare \
  --skeptic skeptic.md \
  --output benchmarks/results/prompts.json
```

Score a response set:

```bash
python3 benchmarks/benchmark.py score \
  --responses benchmarks/example_outputs/expected-good.json \
  --output benchmarks/results/good-score.json
```

Compare controlled scored runs:

```bash
python3 benchmarks/benchmark.py compare \
  --baseline benchmarks/results/baseline-score.json \
  --candidate benchmarks/results/candidate-score.json
```

## Response and scoring policy

A response set is an object with nonempty `metadata` and a `responses` list. Metadata should record exact visible model, version, effort, runtime, and exposed settings. Each response contains `case_id` and the complete response text.

Per case, scoring records:

- names of required concepts matched and missed;
- forbidden concepts triggered;
- the internal `PASS`, `ACTION`, or `CONFLICT` decision;
- the separate final `HANDLED` or `CONFLICT` output category;
- decision compatibility;
- presence of a recognizable current RunSkeptic receipt;
- word, character, and estimated token counts.

`HANDLED` is never treated as `PASS`. Scorer V2 extracts only structurally labeled internal and final decisions, including common Markdown/table forms; an explicit post-fix or post-patch status supersedes the corresponding pre-fix decision. Receipt detection requires a receipt heading and all required semantic fields, with bounded label aliases in lists, tables, bold labels, or headings. It does not accept isolated keywords in ordinary prose. Estimated tokens are `ceil(character_count / 4)` and are explicitly not provider billing data.

Benchmark version and scorer version are separate. Every newly generated score records `scorer_version`; the current value is `scorer-v2`. Baseline V1 raw responses and its original `score.json` remain immutable historical evidence. A separate `score.scorer-v2.json` reinterprets those same responses without rerunning a model, changing Skeptic, or changing cases. Original and diagnostic scores may coexist, but their numeric difference is a measurement-layer change, not a behavioral improvement.

Quality points are `required matches + compatible decision + receipt - 2 × forbidden findings`. Aggregates include required-concept recall, critical misses, critical forbidden findings, compatibility rate, receipt compliance rate, and median estimated output tokens.

## Comparison policy

Comparison is controlled only when both score files use the same scorer version and contain equal, nonempty model/runtime/settings metadata. A missing scorer version is treated as historical `scorer-v1`; missing or differing runtime metadata or differing scorer versions produces `uncontrolled`.

For controlled comparisons:

1. Any critical case with newly missed required concepts, newly triggered forbidden concepts, or a newly incompatible decision is a hard override: the candidate cannot be `candidate_better` and the result is `baseline_better`.
2. Otherwise, `candidate_better` requires higher total quality points without worse compatibility or more forbidden findings.
3. The symmetric regression yields `baseline_better`.
4. Equal quality metrics yield `equivalent`; conflicting movements yield `mixed`.
5. Output length is secondary information only. Shorter output cannot excuse quality loss, and longer output alone can never make a candidate better.

Allowed verdicts are `candidate_better`, `baseline_better`, `mixed`, `equivalent`, and `uncontrolled`.

## Blinded human judgment

Create a deterministic packet and separate reveal key:

```bash
python3 benchmarks/judge.py blind \
  --a baseline-responses.json \
  --b candidate-responses.json \
  --output benchmarks/results/blind-packet.json \
  --key-output benchmarks/results/blind-key.json \
  --seed 12345
```

The packet contains only anonymous `A` and `B` responses. Record `A better`, `B better`, `tie`, or `unusable`, then reveal:

```bash
python3 benchmarks/judge.py reveal \
  --judgments judgments.json \
  --key benchmarks/results/blind-key.json \
  --output benchmarks/results/revealed-judgments.json
```

No automatic LLM judge is enabled.

## Adding or changing a case

Add one realistic failure mode or clean false-positive trap, use current Skeptic tags, define narrow concept alternatives, and add or update deterministic tests. Confirm the case adds distinct value rather than duplicating an existing one. Stable golden cases should change only for documented reasons, and cases must not be tuned merely to favor the current Skeptic.

## Establishing a baseline

1. Run `validate` and `prepare` against the exact baseline `skeptic.md`.
2. Execute all prompts with one exact model/runtime/settings configuration outside this provider-neutral repository tool.
3. Save complete responses with the exact visible metadata.
4. Score them, inspect false positives and false negatives manually, and record runtime and actual cost only when directly exposed.
5. Commit an official baseline only when repository policy explicitly supports it.

## Limitations

This benchmark is small and directional; twelve cases are not statistically significant. Deterministic concept matching can produce false positives and false negatives, bounded negation cannot understand arbitrary scope, and synonym expansion can overmatch future wording. Receipt structure does not prove reasoning quality. Human review remains necessary for close comparisons. Visible cases can be gamed, and estimated tokens are not billing data. Results are not proof of universal correctness or safety. Future protected or independently written cases may be needed before high-stakes promotion decisions.

For any Skeptic experiment, freeze one scorer version and use it for both baseline and candidate. Never compare a historical score produced by one scorer directly with a candidate score produced by another as evidence of behavioral change.
