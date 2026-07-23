# RunSkeptic Baseline V1

Baseline V1 records the empirical behavior of the authoritative `skeptic.md` at repository commit `5f205b47ddca0117f7973c23b8a549150c3ca57a`. It is a control for future bounded Skeptic experiments, not a claim that the current Skeptic is perfect.

## Frozen execution

- Provider/runtime: OpenAI through Codex CLI `0.145.0`, authenticated with ChatGPT.
- Model: `gpt-5.6-sol`.
- Model version: not exposed by Codex CLI `0.145.0`.
- Effort: `high`.
- Context window exposed by the model catalog: 272,000 tokens.
- Temperature, top-p, and maximum output tokens: not exposed.
- Isolation: a new `codex exec --ephemeral` process and empty working directory for every case.
- User configuration and execution rules: ignored with `--ignore-user-config` and `--ignore-rules`.
- Sandbox: read-only.
- Web search: not enabled.
- Tool use: no tool calls occurred in any recorded case.

The command shape was identical for every case:

```text
codex exec --ephemeral --ignore-user-config --ignore-rules \
  --skip-git-repo-check -C <fresh-empty-directory> \
  -m gpt-5.6-sol -c model_reasoning_effort="high" \
  -s read-only --json -o <case-response-path> -
```

The prompt was passed unchanged on standard input from one verified prompt packet. Twelve distinct runtime thread IDs confirmed fresh contexts. The event stream contained only final agent messages and usage records.

## Inputs and integrity

| Artifact | SHA-256 |
|---|---|
| `skeptic.md` | `18ec8655724fcf1e35238c5fc0547414aa389d999467a2002f9d4e82f59f3169` |
| `benchmarks/cases.json` | `d05687857a66fc6b4ada02b272ed29ed98ddcdbeec0827bb4293387e5629b4de` |
| Generated prompt packet | `2b3efaec2ff5b254eba1a7535f0fc51b74f231ca5268b5fe33cb7e90a5f501b7` |
| `responses.json` | `0bc01bd19ecfd9fbd4699fa5d46c91707eed007d27129c205aaaf8b94158fec0` |
| `score.json` | `45a99625d0d1ac5d5e1da025c6a118d1a47ece8595ed286730575d3fd1a04e03` |

Recreate the prompt packet with:

```bash
python3 benchmarks/benchmark.py prepare \
  --skeptic skeptic.md \
  --output <temporary-output>/prompts.json
```

Confirm its SHA-256 before using it. The packet is not committed because it deterministically embeds twelve copies of the pinned Skeptic source and is therefore reconstructible generated noise.

## Results

- Required-concept recall: `32 / 52` (`0.6153846154`) by substring scoring.
- Machine-compatible decisions: `0 / 12`; manual audit found `12 / 12` substantively compatible. The scorer does not recognize the model's recurring Markdown labels such as `Finding decision` or `Internal finding category`.
- Forbidden findings: `2`; both are negation errors from recommendations that explicitly reject the forbidden action.
- Receipt compliance: `10 / 12` by structural detection; manual audit found all twelve receipts materially complete.
- Median estimated output size: `1,374` tokens using `ceil(characters / 4)`; this is not provider billing usage.
- Actual runtime usage exposed: `284,271` input tokens and `33,148` output tokens.
- Total case runtime: `851.550678` seconds; median: `69.392804` seconds.
- Actual cost: not exposed.

See `manual-audit.md` for per-case classification. The manual audit identified nineteen concept-matcher false negatives, two forbidden-pattern negation errors, two receipt-label false negatives, twelve decision-label extraction failures, and one genuine Skeptic miss.

## Retention decision

- `responses.json` is committed unchanged at the response-text level. It contains synthetic benchmark reviews, timings, and directly exposed token usage, with no credentials or private source data.
- `score.json` is committed so future candidates can be compared without rescoring the historical run.
- `metadata.json` records the frozen configuration, hashes, and acceptance evidence.
- The deterministic prompt packet is not committed; its hash and reconstruction command are retained.
- Canary outputs, CLI event streams, warning logs, and the temporary runner are not committed. They are execution evidence but contain unstable runtime identifiers and add no material input or output unavailable from the committed artifacts.

## Limitations

The model slug and exposed configuration are frozen, but the provider did not expose a dated model build. A future comparison can prove equality of exposed metadata, not hidden backend revision identity. One model/configuration does not establish provider-general performance. The benchmark is small and directional. Substring scoring produces false positives and false negatives, receipt detection is structural, estimated tokens are not billing tokens, and human review remains necessary for close decisions.
