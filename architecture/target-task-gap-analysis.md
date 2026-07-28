# Target Task gap analysis

Baseline under review: `3d1945f46936366a53a5899e029bf904e37b9544`.
Acceptance-plan identity: recorded in `experiments/target-task-artifacts/acceptance-plan.md`.

| Area | Owner | Implementation/evidence | Status | Required repair | Tests | Residual risk |
|---|---|---|---|---|---|---|
| Body ownership | architecture / target-task | canonical Body fields and bounded protocol | ALIGNED | keep single owner | architecture/context contracts | provider runtime not observable |
| Brain ownership | architecture / target-task | Brain plans; RunSkeptic amendment | ALIGNED | record independent review | routing tests | actual model hidden |
| Worker ownership | target-task / return envelope | bounded step and envelope contracts | ALIGNED | preserve trust boundary | context contracts | worker effectiveness unknown |
| Boundary processing | boundary-agent / harness | deterministic pressure harness plus real-agent evidence | PARTIAL | separate structure from acceptance | context tests | runtime isolation unknown |
| Claim provenance | architecture / lifecycle harness | `accept_claims` transition, six states, validator-backed references | ALIGNED | reject unaccepted provenance | lifecycle tests | reference existence is caller-retrieved |
| Accepted-claims transition | Body / lifecycle harness | `ACCEPTABLE_PROVENANCE` filter | ALIGNED | no worker promotion | lifecycle tests | no external ledger |
| Plan schema | Body / lifecycle harness | complete top-level/step validation and nonblank bounded fields | ALIGNED | reject bad graphs/authority | lifecycle tests | schema is provider-neutral |
| Plan sealing | Body / lifecycle harness | stable canonical hash | ALIGNED | hash before acceptance | lifecycle tests | persistence is caller-owned |
| Checkpoint creation | Body / lifecycle harness | required fields and atomic write | ALIGNED | persist at lifecycle boundaries | lifecycle tests | no real session boundary |
| Checkpoint integrity | Body / lifecycle harness | content hash, references, version, evidence | ALIGNED | focused failure tests | lifecycle tests | external artifact contents not hashed |
| Resume authorization | Body / lifecycle harness | plan-aware `resume_checkpoint` | ALIGNED | block mismatches/blockers | lifecycle tests | actual runtime resume unavailable |
| Completed-step non-repetition | Body / lifecycle harness | authorization, persisted attempts, and new artifact | ALIGNED | explicit retry contract | lifecycle tests | no production runtime |
| Progressive retrieval | target-task / context harness | metadata-only baseline and bounded focused extraction | ALIGNED | preserve distinction | context tests | simulation only |
| Context modes | architecture / target-task | three observed statuses and three modes | ALIGNED | no inferred isolation | context tests | actual isolation unknown |
| Terminal receipts | lifecycle harness / target-task | expanded fields and fail-closed accepted invariant | ALIGNED | regenerate exact final receipt | lifecycle tests | receipt is not runtime proof |
| RunSkeptic routing | architecture / lead / routing | Brain HIGH default and escalation gate | ALIGNED | execute qualifying reviews | routing/static tests + receipts | actual route may be unknown |
| RunSkeptic loop semantics | skeptic.md / lead / target-task | fresh Fix/Find and 3-pass precedence | ALIGNED | preserve independent receipts | review receipts | reviewer context status |
| Real exercises | invoking runtime | delegated boundary PASS; interruption/resume blocked | UNPROVEN | report BLOCKED truthfully | receipt | blocking if promotion requires genuine runtime |
| Validation evidence | repository adapter | targeted/full/diff checks and durable docs | PARTIAL | refresh counts and hashes | full suite | current final commit not yet sealed |
| Integration readiness | Lead / repository | branch isolated, main untouched | PARTIAL | verify/push only after closure | git receipts | remote state may change |
