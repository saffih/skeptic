# Slice 2 Task Prompt v2: Git Hygiene (revised after Level 2 review; ACTION findings fixed)

v1 of this prompt (git history at `e0a3653`) received an independent Level 2
review with verdict ACTION, not PASS. This v2 applies all ten findings.
Partial execution already occurred under explicit in-session owner
authorization before the review arrived; the mutation ledger below records
it. No branch was deleted and no tag reached the remote.

## Review findings applied in v2

1. Authority recorded explicitly; external side effects gated on
   `AUTHORITY_PENDING` until the owner authorizes this v2.
2. Exact model labels recorded, including actual labels for already-executed
   phases; effort recorded as `EFFORT_LABEL_UNAVAILABLE`, not invented.
3. P0 pre-execution Task-level Skeptic gate added with persisted receipt.
4. Fresh slice branch replaces reuse of the routing branch.
5. Full 40-character SHAs are the authoritative deletion/tagging contract.
6. Content drift on any target returns `STATE_DRIFT_REQUIRES_OWNER_DECISION`;
   no self-approved retargeting.
7. Per-target absence/presence verification replaces exact global branch
   counts; the slice branch is deleted after verified merge.
8. `BASELINE_TEST_COUNT` recorded at P1; all-pass plus explained delta
   replaces a hardcoded total.
9. The tag-vs-hash evidence difference is stated honestly; tag-object and
   peeled SHAs are both recorded.
10. Clean-room classification made consistent.

## Mutation ledger (executed before this revision, under in-session owner go-ahead)

- P1 re-audit: `origin/main` drift `ac221cb` -> `c6df30f` (known cause: the
  Slice 1 receipt-correction commit); all nine deletion-target tips matched
  the authorized snapshot exactly; ancestry proofs passed for the four
  merged branches.
- P2 executed: PR #4 harvest comment posted (issuecomment-5010882021) and
  PR #4 closed, not merged (read-back: state=closed, merged=false).
  Reversible: PR can be reopened.
- P3 executed: PR #2 disposition comment posted (issuecomment-5010882918);
  PR #2 remains open and unmerged.
- P4 partial: seven annotated tags created locally; push to origin failed
  twice with HTTP 403 (branch pushes succeed in this environment; the
  failure is tag-ref-specific and suggests proxy policy). No tag is on the
  remote. Root cause not yet confirmed; no blind retry performed.
- Not executed: any branch deletion, any test edit, any commit for this
  slice.
- Model labels actually used for the executed phases: Claude Sonnet 5
  (session had been switched by the owner); the session was later returned
  to Claude Fable 5.

## Owner decision required at authorization (tag publication)

If the environment blocks `refs/tags/*` pushes, DONE-3 cannot be met as
written. Options:

- A (recommended): publish `archive/*` branches instead of tags
  (`refs/heads/archive/<name>`). Equally durable and restorable; branch
  pushes are proven to work here. Trade-off honestly noted: a branch
  signals "history" less strongly than a tag - but an unprotected tag is
  also force-movable, so the durability difference is small.
- B: keep tags local, record them in the slice record, defer publication
  to an environment that permits tag pushes; branch deletion then also
  defers (deletion must never precede published archives).
- C: stop with CONFLICT.

P4 first probes one tag push after root-causing the 403; if policy-blocked,
apply the owner-selected option.

---

# Task Prompt: Git hygiene v2

## Execution header

Target runtime/agent: Claude Code remote session with git push authority
and GitHub MCP tools. Single Lead agent; Checker duties via deterministic
git commands; no workers (mechanical operations; delegation adds
coordination cost without independence value). No independent Judge.
Exact model/runtime label: record the actual visible session label at
execution time (expected: Claude Fable 5; actual label must be recorded in
the slice record, per phase if it changes).
Reasoning effort: EFFORT_LABEL_UNAVAILABLE (runtime exposes no effort
setting; reviewer-recommended intent is medium - the risks here are
authority and remote-mutation correctness, which a stronger model does not
reduce). Fallback: none. Forbidden escalation: no second model, no added
agents or reviewers, no higher effort to compensate for a failing step.
Clean-room status: NOT CLEAN ROOM. Independent review: NOT REQUIRED.
Reason: no comparative judgment requiring protected isolation.

External-side-effect authority: AUTHORITY_PENDING.
The remaining phases (P4 completion, P5, P6, P7) perform archive
publication, branch deletion, and a push to main. Do not execute them
until the owner explicitly authorizes this v2 in the current session,
including the tag-vs-archive-branch decision above. The authorization
wording must be quoted verbatim in the slice record. P2 and P3 are already
complete under prior explicit in-session authorization (ledger above).

## P0 - Task Prompt Skeptic gate (pre-execution)

Read the current `skeptic.md` and `agents/task-prompt.md`. Run Level 2
Task Prompt review on this v2. Fix ACTION findings and rerun; maximum
three passes. Persist the gate receipt in the slice record. No external
mutation unless the final verdict is PASS. DECOMPOSE or CONFLICT stops
execution.

## Objective

Remove stale git state that can mislead future agents, preserving every
unmerged commit via verified published archives, and free
`plans/skeptic-next-capability-sh-pf.md` from its byte-level hash pin.

## Working branch

Create `claude/skeptic-git-hygiene-1efkvx` fresh from current
`origin/main`. Do not reuse the routing slice branch (one slice = one
branch, per the consolidation plan). After verified merge to `main`,
delete this slice branch. The prior routing branch
(`claude/skeptic-routing-clarification-1efkvx`) is the session-designated
branch; its deletion is deferred to the owner or session end - recorded as
a deferred item, not silently kept.

## Exact terminal DONE

1. PR #4 closed, not merged, with the harvest comment. STATUS: already
   complete (verified read-back; comment 5010882021). Re-verify state at
   closure; do not repeat the comment.
2. PR #2 open and unmerged with one disposition comment. STATUS: already
   complete (comment 5010882918). Re-verify open state at closure; no
   further comments.
3. Seven archives published and verified on the remote, each against its
   full authoritative SHA below - as annotated tags (recording both
   tag-object SHA and peeled commit SHA), or as `archive/*` branches if
   the owner selected option A. Authoritative targets:
   - experiment/skeptic-meta-process-value-ab-001 ->
     `9c24f6f3a8a8c9f75d060ccef07f49e736866689`
   - experiment/skeptic-trust-boundary-fe-tb-ab-001 ->
     `fce98e3505eda14b2588869eeef44528f81c7a2e`
   - claude/lead-agent-prompt-artifact-9rd2na ->
     `ff08a84707441b7d19971ef663a04a5dc280e6c3`
   - pattern-classification ->
     `d5f2bdc54b6cf076b5d7ab836ab0b49e40960045`
   - revised-questions ->
     `f76ba4d68ed090b768778ed415f0004f4bf6fecb`
   - benchmark/skeptic-capability-stage2-2026-07-04 ->
     `fcd1fa31a40fea050dc1f0699948e5e2c7cfebd4` (branch also retained)
   - sh-pf-frozen-contract ->
     `52cd8226c276186530a32a52b36d5a3943434faa`
   If any name resolves differently from these full SHAs at execution:
   STATE_DRIFT_REQUIRES_OWNER_DECISION.
4. Deleted remote branches, each only after its published archive is
   verified (or, for the merged four, after a fresh
   `merge-base --is-ancestor <full-SHA> origin/main` proof): `andrei`
   (`33bcb0e34294da2a39465bfbdb80f2ea54c7f701`),
   `feat/skeptic-effort-value-alignment`
   (`b3d6d9ea63bfa6e60c968bcd90c58311eb447fbc`),
   `plan/skeptic-practical-improvement-reset`
   (`eb06396624ed237ad0df0e43ce1afaa51b26e01e`), `promotion-check`
   (`6b69e35335d66a6d42e78929e769981711d1756e`), plus the five archived
   unmerged branches listed in DONE-3 (excluding benchmark).
5. `benchmark/skeptic-capability-stage2-2026-07-04` still present at its
   full SHA AND archived (protected state; disconfirming check required).
6. `tests/test_pareto_frontier.py` no longer contains
   `FROZEN_CONTRACT_SHA256` or the frozen-contract test; the
   `skeptic-tests.md` SH:PF section states honestly: the archive preserves
   the historical promotion contract and replaces active byte-level
   immutability enforcement with historical recoverability and
   traceability. All tests pass; the count delta from
   `BASELINE_TEST_COUNT` is exactly -1 and is explained in the record.
7. Slice record `plans/skeptic-git-hygiene-slice-record.md` (verbatim
   authorization quote, P0 gate receipt, dispositions, archive restore
   table with full SHAs, per-phase model labels, receipts, RunSkeptic
   result) committed on the slice branch, merged to `main`, pushed, fresh
   `origin/main` verified; slice branch then deleted.

Not DONE: local-only archives; any deletion before its per-target
verification; branch-only commit; push without fresh remote verification.

Final-state verification is per-target: every targeted deletion absent;
every protected ref present at its full SHA; no unlisted ref mutated. No
exact global branch count is asserted.

## Verified starting state (P1 must re-verify)

`origin/main` = `c6df30f6ec9e2d6bb309b817178fbcb45ca0b1aa`; record
`BASELINE_TEST_COUNT` from a fresh full-suite run (last observed: 86, all
passing). Target tips: the full SHAs in DONE-3/DONE-4. PR #4 closed with
1 comment; PR #2 open with the disposition comment.
Drift rules: `origin/main` advancing by new verified work -> re-audit and
record, then continue if no deletion target is affected. Any change to a
deletion-target tip, PR head, or ancestry ->
STATE_DRIFT_REQUIRES_OWNER_DECISION; do not retarget an archive or delete
the changed branch without renewed owner authorization. Network or
metadata-only drift may be retried within limits.

## Authority and source-of-truth order

1. Explicit owner authorization of this v2 in the current session
   (verbatim quote required in the slice record).
2. Live remote/GitHub state observed at execution.
3. Consolidation plan Track 2 (merged in `main`) as the source of intended
   work - not, by itself, execution authority.
4. This Task Prompt.
PR #2 belongs to an external contributor: comment authority only (already
used); closing or merging it requires a separate explicit owner decision.

## Scope and mutation boundary

Allowed: fetch --prune; ancestry checks; one root-cause probe of the
tag-push 403; publish the seven archives per the owner-selected mechanism;
delete exactly the nine listed branches; edit the two listed files; add
the slice record; commit/push the fresh slice branch; ff-merge and push
`main`; delete the slice branch after verified merge.
Forbidden: force push; deleting `main`, the benchmark branch, or the
session-designated routing branch; deleting any unlisted ref; deleting
archives; merging any PR; further PR comments or closures; editing
`skeptic.md` or `agents/*`; any write to the fork.
Rollback: restore any branch via
`git push origin <archive-ref>^{}:refs/heads/<original-branch-name>`
(restore table with full SHAs persisted before deletions); reopen PR #4;
revert file edits via git.

## Completion-feasibility and budget

Envelope: single session, ~20 deterministic operations, one bounded test
edit. Protected completion reserve: merge-to-main and fresh remote
verification before any optional polish. Limits: max 2 retries per failure
class then redesign; network retries x4 backoff. Futility: policy or
permission refusal that the owner-selected option cannot resolve ->
CONFLICT with state preserved (published archives are the safe partial
state; deletions defer).

## Execution graph

P0 Skeptic gate (above). -> P1.
P1 Preflight re-audit: fetch --prune; resolve every target name to its
   full SHA and compare; PR states; BASELINE_TEST_COUNT; drift rules
   applied. -> P4 (P2, P3 already complete - verify only).
P4 Archive publication: root-cause the 403 (proxy status probe); apply
   owner-selected mechanism; publish seven archives; verify each on the
   remote against its full SHA (tags: dereferenced ^{} value; record tag
   object + peeled SHAs). Persist the restore table in the slice record
   draft before any deletion. Accept: 7/7 verified.
P5 Branch deletion: per-target - archive verified (or fresh ancestry
   proof for the merged four), then delete; verify absence; benchmark
   never touched. Accept: nine absent, protected refs present.
P6 Frozen-hash migration: remove the constant and its test; add the
   honest governance note; full suite; explain the -1 delta. Accept: all
   pass; only the two intended files changed.
P7 Record and publish: finalize slice record; commit on the slice branch;
   push; ff-merge to `main`; push; fetch; verify fresh `origin/main`;
   rerun suite; delete the slice branch; verify deletion.

## Context, evidence, independence, failure handling

Lead context holds this prompt, the re-audited full-SHA table, and
per-phase acceptance results. Deterministic outputs (ls-remote listings,
ancestry checks, test results) are the evidence; the restore table is
persisted before deletions depend on it; gap ledger in the slice record
if a phase blocks. Failure classes: policy/permission refusal ->
owner-selected option, else CONFLICT with state preserved; network ->
retry x4 backoff; target drift -> STATE_DRIFT_REQUIRES_OWNER_DECISION;
suite failure after P6 -> revert, re-diagnose, max 2 attempts then
CONFLICT. Pre-exhaustion handoff: commit and push the slice record with a
completed-phase table; deferred deletions are safe once archives are
published and verified.

## System verification

Per-target ls-remote checks (absence and presence at full SHA);
disconfirming protected-state checks (benchmark, main, routing branch);
full suite after P6 and on merged `main`; RunSkeptic on the change, max 3
passes, ending HANDLED or CONFLICT.

## Task Closure Receipt

Enumerate DONE-1..7 yes/no with evidence (verbatim authorization quote,
P0 receipt, comment IDs and PR read-back states, per-target ls-remote
values with full SHAs, tag-object and peeled SHAs where applicable,
ancestry proofs, BASELINE_TEST_COUNT and explained delta, fresh
origin/main SHA, slice-branch deletion proof); per-phase model labels;
protected-state results; unresolved blockers; residual risk (including:
archives preserve history but do not enforce current-file immutability).
Overall DONE: yes only when all seven verify.

# PONYTAIL / KISS - NON-NEGOTIABLE EXECUTION CHECKSUM

No external mutation while AUTHORITY_PENDING; quote the authorization verbatim.
Never delete a branch before its published archive (or fresh ancestry proof) is verified.
Full 40-char SHAs are the only deletion contract; any target drift = owner decision.
Never touch benchmark/skeptic-capability-stage2-2026-07-04, main history, or the routing branch.
PR #2 and PR #4: no further actions beyond re-verification.
No force push. No archive deletion. Fresh slice branch only; delete it after verified merge.
Merged-to-remote-main with fresh verification is the only DONE.

# END OF PROMPT
