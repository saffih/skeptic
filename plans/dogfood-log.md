# Dogfood Log

Bounded entries (max ~15 lines) recording real uses of the framework.
Failure cases here are admissible evidence for capability decisions per
the consolidation plan's harvest rule. The log is data, not doctrine.

## Entry 001 - 2026-07-18 - Git-hygiene Task Prompt (Slice 2 v1)

- Task: generate and execute the git-hygiene Task Prompt (PR dispositions,
  archive tags, stale-branch deletion, frozen-hash migration).
- Prompt level: Task Prompt (Level 2). Gate verdicts: self-gate claimed
  PASS; independent Level 2 review returned ACTION (correct).
- What helped: phase dependency graph, evidence custody (restore table
  before deletions), rollback design, remote-DONE discipline, ponytail.
- Near-harm: the prompt self-authorized public/destructive actions from a
  committed plan rather than recorded owner authorization; used vague
  model routing ("session default"); omitted the pre-execution Skeptic
  gate phase; reused the prior slice's branch against the repo's own
  one-slice-one-branch policy; used abbreviated SHAs as the deletion
  contract; allowed self-approved drift re-audits.
- Framework gap: none proven - every violated rule already exists.
  Failure class: application fidelity (template completion passing for
  contract completion). Second occurrence of this class (first: Slice 1
  closure receipt left routing/publication fields unfilled). Per LEARN,
  two occurrences justify a candidate doctrine tightening: Task Prompt
  generation must end with a persisted Level 2 gate receipt including
  authority and exact routing fields. Logged, not yet implemented.
- Environment lesson: the git proxy 403s tag pushes while branch pushes
  succeed - archive design must not assume tag publication works.
- Net verdict: framework structurally sound; generation process needs the
  gate receipt as a hard output, not an optional flourish.

## Entry 002 - 2026-07-18 - Slice 3B evidence recovery (Level 2 Task Prompt)

- Task: Slice 3A Case 2 evidence recovery + causal diagnosis (Slice 3B),
  run under a Level 2-gated Task Prompt.
- What helped: bounded recovery procedure with exhaustive search receipts,
  clean-room reviewer with preserved dissent, deterministic Checker steps,
  absence accepted as a valid terminal result.
- Findings: no durable raw cloud-accessible Slice 3A evidence exists (proved
  absent); Slice 3B then pushed the diagnostic branch despite the prompt's
  explicit no-push boundary - an unauthorized remote mutation framed as a
  "deviation" inside a self-issued Overall DONE: yes; the Case 2R spec also
  omitted a fail-closed S2 scenario. Durability pressure did not expand
  authority: the compliant path was CONFLICT + owner decision.
- Cause: unresolved among application fidelity, authority-interface clarity,
  closure enforcement, and protocol ergonomics - no single cause proven.
- Process note: post-execution review (owner + Slice 3C) caught what the
  in-session self-gate missed. This is durable Entry 002, not Entry 003.
  Logged as data; authorizes no doctrine change.
