# Model and Cost Findings — 2026-07-27

This is an auxiliary handoff note, not a normative protocol file. Recheck official rate cards before making cost-sensitive decisions.

## OpenAI Codex

Official current tiers and token-based credit rates per 1M tokens:

| Model | Input | Cached input | Output | Legacy average local task |
|---|---:|---:|---:|---:|
| GPT-5.6 Luna | 25 credits | 2.5 | 150 | ~3 credits |
| GPT-5.6 Terra | 62.5 credits | 6.25 | 375 | ~7 credits |
| GPT-5.6 Sol | 125 credits | 12.5 | 750 | ~14 credits |

At equal token counts, Terra is 2.5× Luna and Sol is 2× Terra / 5× Luna. Actual task cost depends on input, cache, output/reasoning, speed mode, and task length.

The official rate card currently lists Luna, Terra, and Sol. A displayed `Tara` label has not been mapped to an official tier and must remain `UNKNOWN` until verified.

## Claude

Current relevant regular API prices per 1M tokens:

| Model | Input | Output | Practical role |
|---|---:|---:|---|
| Haiku 4.5 | $1 | $5 | Fast inexpensive execution |
| Sonnet 5 | $2 introductory / $3 standard | $10 introductory / $15 standard | Default agentic planning and implementation |
| Opus 4.8 | $5 | $25 | Difficult planning and sustained reasoning |
| Fable 5 | $10 | $50 | Exceptional long-running frontier work |

Sonnet 5 introductory pricing ends August 31, 2026. Anthropic supports effort controls; higher effort can improve results but consumes more tokens. No fixed cost multiplier by effort is published.

## Approximate role parallels

- Luna ↔ Haiku: strongest price/role parallel.
- Terra ↔ Sonnet: default cost-efficient working tier.
- Sol ↔ Opus: expensive difficult-work tier.
- Fable sits above the normal Sol/Opus class and should be exceptional.

These are operational parallels, not capability-equivalence claims.

## Current protocol recommendation

- Keep the already validated OpenAI default: Luna MEDIUM Body + Sol LOW Brain.
- Test Claude separately rather than assuming equivalence: Haiku MEDIUM Body + Sonnet 5 MEDIUM Brain.
- Escalate Brain effort/model only from observed failure, high-risk scope, or explicit authorization.
- Always record requested and observed provider/model/effort independently.

## Validated Body–Brain evidence

BBE-001 through BBE-006 established:

- successful deterministic execution;
- byte-preserved payload handling;
- malformed-plan rejection without repair;
- post-seal tamper detection before execution;
- resistance to unauthorized delegation;
- controlled failure without fabrication.

Observed Brain routing remained `UNKNOWN`; this is correct evidence handling, not a protocol failure.
