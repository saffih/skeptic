# Acceptance Plan

TASK_ID: TT-REPAIR-2026-07-28
OBJECTIVE: Repair and validate Target Task architecture and lifecycle contracts.
DONE: Every authorized finding is implemented or explicitly blocked with evidence; targeted and full tests pass; review receipts converge.
SCOPE: canonical architecture, Lead/routing/Target Task contracts, lifecycle harness, tests, durable evidence.
PROHIBITIONS: do not edit skeptic.md; do not modify main; do not claim runtime isolation or real exercises without observation.
SOURCE_OF_TRUTH_ORDER: user task, skeptic.md, architecture, sealed plan, repository contracts, verified evidence.
ASSUMPTIONS: isolated target-task worktree is the mutation target; local main evidence is protected.
UNKNOWNS: actual model/runtime routing and genuine invocation capability.
STEPS: S1 inspect and gap-map; S2 repair routing/loop and lifecycle; S3 deterministic validation; S4 independent Brain review; S5 receipt and integration readiness.
VALIDATION: targeted tests, full discovery, git diff check, repository validation, independent RunSkeptic receipts.
HANDOFF: compact status, evidence references, limitations, next action, and acceptance basis.
STOP_CONDITIONS: integrity failure, unresolved conflict, blocking unknown, unauthorized main mutation.
RETRIEVAL_CONDITIONS: retrieve exact file/symbol/test evidence before accepting a claim.
ESCALATION_CONDITIONS: HIGH review inadequate only; recommend one bounded XHIGH and stop.
REVIEW_MODE: RUNSKEPTIC_REVIEW
SUCCESS_CRITERIA: clean branch, exact final receipt, no open material findings, main untouched.

## Stable identity

PLAN_HASH: `51406b017bb17c20fdc0082c39684291a075061920234b491872f8afc7408c2c`
HASH_RULE: SHA-256 of this file with the PLAN_HASH value replaced by `<SEALED_PLAN_HASH>`.
SEALING_RULE: this plan is accepted as written; the Body may reject it but may not semantically repair it.
