# Current-main behavioral-validation summary — 2026-07-26

Terminal verdict: `OWNER_DECISION_REQUIRED`.

## Target and baseline

- Target: `6183953063b5709c10c3459e93bea60246ccaf1a:skeptic.md`, blob `04e899dba10a71a692afe28d1c15476589785e15`, SHA-256 `ca729689fb465f81493be3270a4b6cb3c35507c709e3b0492c90cdaa460bec89`.
- Baseline: `92b8f69144af5edd0edb1d20e454f624276c1138:skeptic.md`, blob `17eea7774dee4db80109fd2e7e0d021244861983`, SHA-256 `7594d7d09a4757bb3f94cf5797d730a1abec8e9f67bf5412bed17c9f97cf0328`.
- Comparison design: a frozen A/B regression screen covering six visible scenarios and two existing protected slots.

The baseline is the immediate pre-sequence Skeptic and coherently isolates the compact standalone, hidden-human-burden, Find/Fix Loop, HANDLED, invocation-permission, repeated-source-read, and companion-authority changes.

## Execution status

A single non-evaluative runtime canary succeeded with Codex CLI `0.145.0`, `gpt-5.6-terra`, medium effort, and `FRESH_CONTEXT_CONFIRMED` from a new ephemeral process in a fresh empty directory with user configuration and rules disabled. Its raw response was not retained and its `ACTION` decision is not treated as behavioral evidence.

Deterministic validation passed: 63 focused tests, 149 full-suite tests, all four QuickCompare calibration verdict paths, the 12-case golden manifest (4 critical, 52 concepts, all six Thinker families), scenario/final-manifest validation, source compilation, scope checks, and the protected leak scan (zero exact-file and zero long-private-string matches across 77 public files). Private roots and files are `0700`/`0600` as required; `skeptic.md` is unchanged.

The frozen 24-call comparison did not start. Before the first protected transmission, the execution gate rejected sending the exact private files bound to slots `protected_code_testing` and `protected_agent_security_procedure` to the external OpenAI Codex model service without destination-specific authorization. Their local paths remain private.

No protected content left the machine. No generator validation scenario, blinded judge call, protected result, material gain, material regression, false-positive comparison, invalid run, or incomparable run exists.

## Interpretation

Deterministic checks can validate the repository contracts, scenario coverage, harness mechanics, privacy controls, and target identity. They cannot establish model behavior. Accordingly, this run makes no claim that current main is behaviorally supported, equivalent, lossless, or free of regression.

## Exact next owner action

Explicitly authorize or decline transmitting the two exact local files bound to the named protected slots to the OpenAI Codex CLI model service for this frozen run. If authorized, resume only when every pre-run identity still matches; otherwise retain `OWNER_DECISION_REQUIRED` and do not substitute unprotected or fabricated cases for the requested protected judgment.
