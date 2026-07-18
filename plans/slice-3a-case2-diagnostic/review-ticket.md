# Neutral Review Ticket — Independent Diagnostic Reviewer

Neutral evidence packet, part 3 of 3. This ticket follows the Dispatch
Ticket schema of `agents/task-prompt.md`. It intentionally contains no
Lead conclusion, no provisional diagnosis, no proposed correction, and no
preferred disposition.

```text
Role: Independent Diagnostic Reviewer (CLEAN ROOM — fresh protected
  context; no access to the Lead's session, chat history, or provisional
  conclusions).

Objective: From the verified evidence packet and the current runtime
  contracts alone, independently assess: (a) for each of the four cause
  classes named in the inbound task prompt (test-design weakness;
  candidate-contract weakness; Generator-following variance; Judge
  interpretation or scoring-contract mismatch), whether the available
  evidence can CONFIRM, EXCLUDE, or NOT RESOLVE that class, with the
  evidence level for each; (b) which of the five candidate dispositions
  (NO_FURTHER_CHANGE; DOCUMENTATION_OR_INTERFACE_CORRECTION;
  NARROW_R1_CANDIDATE; REDESIGNED_BEHAVIORAL_TEST; CONFLICT) the evidence
  can and cannot support, with reasons. Do not assume any disposition is
  expected; more than one may be supportable, and saying so is a valid
  answer.

Source of truth: files at repository HEAD 369c841 —
  plans/slice-3a-case2-diagnostic/recovery-report.md,
  plans/slice-3a-case2-diagnostic/architecture-map.md,
  plans/slice-3a-case2-diagnostic/inbound-task-prompt.md (evidence packet);
  AGENTS.md, skeptic.md, agents/lead-agent-prompt.md,
  agents/task-prompt.md (current runtime contracts). You may also read
  plans/skeptic-consolidation-and-dogfood-plan.md and
  plans/dogfood-log.md, which the evidence packet cites.

Scope: assessment only, over the named files.

Allowed actions: read the named files; reason; return the receipt.

Forbidden actions: any file write or mutation; any git command that
  changes state; reading any other file under
  plans/slice-3a-case2-diagnostic/ beyond the three named packet files;
  treating the inbound task prompt's claims about Slice 3A as verified
  fact (they are uncorroborated, as the recovery report states);
  substituting your own repository search for the recovery report's
  Checker results (you may note gaps you believe the searches left, but
  identify them as such).

Budget / context / output limit: single pass; receipt ≤ 700 words.

Required evidence and durable destination: cite file/section for every
  material claim. The Lead persists your receipt verbatim to
  plans/slice-3a-case2-diagnostic/review-receipt.md.

Acceptance and disconfirming checks: the receipt must state, for each of
  the four cause classes, an explicit CONFIRM / EXCLUDE / NOT RESOLVE
  verdict with evidence level; it must state at least one way its own
  disposition assessment could be wrong.

Stop conditions: stop after one receipt; if the evidence packet is
  internally contradictory or insufficient to answer (a) or (b) at all,
  say so and stop rather than guessing.

Return receipt: the Agent Receipt schema of agents/task-prompt.md
  (Role and task; Scope completed; Files or objects read; Commands or
  tools used; Evidence and durable locations; Changes made; Verification
  and disconfirming checks; Failures, unknowns, and blockers;
  Budget / context result; Recommended next action; Confidence and
  evidence level).
```
