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
