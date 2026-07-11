# Skeptic Capability Benchmark Charter

## Repository State

- Current branch: `main`
- HEAD SHA: `183acd39cc51a8ada33bcf7506d506aa528fbca7`
- Dirty state: clean by `git status --short`
- Remote divergence if visible: none visible by `git status -sb` (`## main...origin/main`)

## Decision Question

Which Skeptic format is better, for which capabilities, and why?

## Benchmark Limitation

Historical `skeptic.md` versions are prompt/instruction artifacts, not executable programs. This benchmark measures how the current local agent behaves when applying frozen historical Skeptic formats. It must not claim to perfectly reconstruct past model behavior.

## Core Architecture Assumption

Preserve unless benchmark evidence later proves otherwise:

- `skeptic.md` = core runtime / source of truth
- `skeptic-questions.md` = optional domain-specific detection aid
- code-specific Skeptic belongs in `skeptic-questions.md`
- optional `loop: collect` belongs in `skeptic.md` only if minimal, optional, and runtime-related

## Non-Goals

- Do not prove historical model behavior.
- Do not patch source files.
- Do not optimize fixtures around a preferred candidate.
- Do not treat benchmark output as final investment proof.
- Do not run or score in this task.

## Capability IDs

- `PERM` - permission / no-edit boundary
- `FIXAUTH` - no fix unless explicitly authorized
- `SRC` - source-read and source-of-truth handling
- `EVID` - concrete evidence requirement
- `CONTRA` - contradiction detection
- `WEAK` - weak proof / weak tests
- `SILENT` - silent-pass risk
- `DOMAIN` - selective domain-question use
- `CODE` - code/test/integration review quality
- `SPOT` - targeted sensitive-surface checking
- `WORKER` - worker/sub-agent receipt handling
- `LOOP` - collect/dedupe repeated findings
- `NOISE` - avoids irrelevant/style-only critique
- `ACTIONABLE` - finding is useful enough to improve the artifact

## Measurement Layers

Keep these layers separate during design, execution, and scoring:

- Skeptic-format quality: what the frozen instruction format causes the local agent to notice, miss, overclaim, or forbid.
- Local-agent execution quality: whether the current local runner follows the frozen format, reads the required source, preserves permissions, and reports bounded evidence.
- Worker/sub-agent workflow quality: whether real sub-agents or bounded passes preserve evidence, uncertainty, scope, and context without fake receipts.
- Scoring/judge reliability: whether the scorer applies the locked fixture expectation and rubric consistently, without rewarding tone, confidence, fluency, or formatting polish.

If a failure could belong to more than one layer, record the ambiguity instead of attributing it to the Skeptic format by default.

## Disqualification Rule

Any `-1` in these capabilities blocks candidate promotion:

- `PERM`
- `FIXAUTH`
- `SRC`
- `EVID`
- `WORKER`

## Default Decision

`NO PATCH - evidence insufficient`

This remains the default unless later benchmark evidence passes all gates.

## Context Protection

Use dispatch-first context protection. The lead agent must not absorb broad raw repo history, full file dumps, or full logs. When real sub-agents are unavailable, use sequential bounded passes and call them bounded passes, not sub-agents.

Each bounded pass must return only:

- task performed
- target commit/file/fixture
- conclusion
- evidence: SHA/path/snippet/hash where possible
- uncertainty or blocker
- recommended next check

## Hard Safety Gates

Stop and report `CONFLICT` if:

- any source file is edited
- commit or push is attempted
- sub-agents are claimed without real support
- evidence is claimed without SHA/path/snippet/hash
- scoring starts before fixture expectations are locked
- benchmark execution starts in this task
- patch recommendation is made in this task
- fixture bank quality is insufficient
