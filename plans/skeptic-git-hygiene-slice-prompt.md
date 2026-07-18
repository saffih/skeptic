# Slice 2 Task Prompt: Git Hygiene (gated PASS, awaiting execution)

Constructed per `agents/lead-agent-prompt.md` and `agents/task-prompt.md`;
gated with RunSkeptic against current `skeptic.md` (two passes; pass 1
findings and fixes recorded below). Execution authority: consolidation plan
Track 2, merged to `main` at `ac221cb`.

## Why this slice is next (reasoning)

- The consolidation plan sequences hygiene immediately after the routing
  slice, and the owner's second opinion confirmed: "After it reaches
  verified remote main, execute Git hygiene as a separate reversible Task
  Prompt."
- Stale state is an active hazard, not just clutter: open PR #4 proposes
  rules partially superseded by current `main`; the frozen-SHA pin blocks
  any annotation of a plans file; nine stale branches invite future agents
  to resume outdated work (the backlog explicitly warns about PR #4).
- It is the safest available slice: deterministic operations, zero
  `skeptic.md` changes, every step reversible via tags or PR reopen.
- Doctrine dedup (Slice 3) touches all three runtime files; doing hygiene
  first means dedup starts from a clean field.

## Skeptic Prompt Gate receipt

- Prompt reviewed: this Task Prompt. Level: Task Prompt (Level 2).
- Skeptic source read: current `skeptic.md` (at `ac221cb`); companions
  `agents/task-prompt.md`, `agents/lead-agent-prompt.md`, `skeptic-tests.md`.
- Permission mode: fix-if-valid with explicit publication authority.
- Pass 1 findings (all ACTION, all fixed in the prompt below):
  1. `KT:IR` - consolidation-plan principle 6 ("archive-tag before any
     branch deletion") conflicts with its own disposition table (merged
     branches: "delete; nothing lost"). Resolved: the principle protects
     reversibility, not tags per se; merged tips stay reachable from `main`
     forever. The prompt requires a `merge-base --is-ancestor` proof before
     any untagged deletion.
  2. `PO:SI` - silent-loss path: a branch could be deleted after a tag was
     created locally but before it landed on the remote. Fixed: per-branch
     acceptance gate - `ls-remote` must show the tag at the recorded SHA
     before that branch's deletion is authorized.
  3. `CH:SO` - deleting PR #4's head branch would auto-close the PR as a
     side effect, losing the explicit disposition comment. Fixed: hard
     ordering - close PR #4 with its comment before its branch is deleted.
  4. `FE:TB`/authority - closing PR #2 acts on an external contributor's
     work without an owner decision. Reduced to comment-only; closing PR #2
     is explicitly out of scope.
  5. `FE:SC` - the preflight branch table is a dated observation that may
     drift before execution. Fixed: P1 re-audit with exact-match
     invalidation; one re-audit allowed, second drift is CONFLICT.
  6. `OM:UE` - replacing the frozen-hash test with a runtime git lookup
     inside unittest adds fragility (fails in shallow clones). Resolved:
     retire the test, preserve the frozen state at an annotated tag, and
     record the pointer in governance.
- Pass 2: PASS. Feasibility: high - ~20 deterministic operations, bounded
  edits, full rollback paths. Protocol cost proportionate. Thinkers
  considered: CH, OM, FE, PO, KT, SH (SH: no live trade-off requiring
  decision; routing lenses NOT_APPLICABLE - no constraint doubt, no option
  comparison beyond already-decided dispositions).
- Gate verdict: PASS. Use decision: execute on owner go-ahead.

---

# Task Prompt: Git hygiene - PR dispositions, archive tags, stale-branch removal, frozen-hash migration

## Execution header

Target runtime/agent: Claude Code remote session with git push authority
and GitHub MCP tools (PR read/comment/close). Single Lead agent; Checker
duties performed by the Lead via deterministic git commands; no workers
(bounded deterministic operations - delegation cost exceeds value).
Model/runtime label and effort: session default model, standard effort.
Sufficient because the work is deterministic git/PR operations plus short
prose comments. Forbidden escalation: no stronger model, no added roles or
reviews to compensate for a failing step.
Clean-room status: NOT CLEAN ROOM (same-context; acceptable - no
independent evaluation in scope).
Mutation/integration/publication authority: push `archive/*` tags; delete
the nine listed remote branches; close PR #4; one comment each on PR #2
and PR #4; edit `tests/test_pareto_frontier.py` and `skeptic-tests.md`;
add the slice record under `plans/`; commit on
`claude/skeptic-routing-clarification-1efkvx`; fast-forward merge to
`main` and push. NO force push anywhere. NO tag deletion.

## Objective

Remove stale git state that can mislead future agents, preserving every
unmerged commit via verified archive tags, and free
`plans/skeptic-next-capability-sh-pf.md` from its byte-level hash pin.

## Exact terminal DONE

1. PR #4 is closed (not merged) with a comment stating: superseded by
   current `main`; harvest result (which of its rules already landed;
   which remain candidates - expected: the explicit
   `CONTEXT_PROTECTION_FAILURE` stop token and numeric receipt caps -
   recorded for a possible future slice, not implemented now); branch
   preserved at its archive tag.
2. PR #2 remains open and unmerged, with one comment: not mergeable as-is
   (stale base, two unrelated concerns); the detection harness is
   recognized as a candidate behavioral instrument to be harvested after
   the dogfood gate (plan Track 3); the pilot result is read as a
   limited-pilot association, not proof. No close.
3. Annotated tags exist on the remote, each verified by `ls-remote` to
   point at its recorded SHA:
   - `archive/experiment-skeptic-meta-process-value-ab-001` -> `9c24f6f3a`
   - `archive/experiment-skeptic-trust-boundary-fe-tb-ab-001` -> `fce98e350`
   - `archive/claude-lead-agent-prompt-artifact-9rd2na` -> `ff08a8470`
   - `archive/pattern-classification` -> `d5f2bdc54`
   - `archive/revised-questions` -> `f76ba4d68`
   - `archive/benchmark-skeptic-capability-stage2-2026-07-04` -> `fcd1fa31a`
   - `archive/sh-pf-frozen-contract` -> `52cd8226`
   (Annotated tags point at tag objects; verify the dereferenced `^{}`
   entry matches the SHA.)
4. These remote branches no longer exist: `andrei`,
   `feat/skeptic-effort-value-alignment`,
   `plan/skeptic-practical-improvement-reset`, `promotion-check` (merged -
   ancestry proof required before deletion), `pattern-classification`,
   `revised-questions`, `experiment/skeptic-meta-process-value-ab-001`,
   `experiment/skeptic-trust-boundary-fe-tb-ab-001`,
   `claude/lead-agent-prompt-artifact-9rd2na` (tag-verified first; PR #4
   closed first).
5. `benchmark/skeptic-capability-stage2-2026-07-04` still exists at
   `fcd1fa31a` AND carries its archive tag (parked Stage 6E evidence;
   protected state).
6. `tests/test_pareto_frontier.py` no longer contains
   `FROZEN_CONTRACT_SHA256` or
   `test_frozen_contract_has_not_changed_after_candidate_output`;
   `skeptic-tests.md` SH:PF section notes the promotion-time contract is
   preserved at `archive/sh-pf-frozen-contract`; full suite green (85
   tests expected).
7. Slice record `plans/skeptic-git-hygiene-slice-record.md` (dispositions,
   tag-to-SHA table with branch-name mapping for restore, PR links,
   receipts, RunSkeptic result) committed, merged to `main`, pushed, and
   fresh `origin/main` fetched and verified to contain the commit.

Intermediate states that are not DONE: tags created locally but not
pushed or not verified; any deletion before its per-branch acceptance;
comments drafted but not posted; branch-only commit; push without fresh
remote verification.

## Verified starting state (P1 must re-verify; observed 2026-07-18)

`origin/main` = `ac221cb57`; 86/86 tests green. Remote tips:
`andrei 33bcb0e34` (merged), `benchmark/... fcd1fa31a` (keep),
`claude/lead-agent-prompt-artifact-9rd2na ff08a8470` (PR #4 head),
`experiment/skeptic-meta-process-value-ab-001 9c24f6f3a`,
`experiment/skeptic-trust-boundary-fe-tb-ab-001 fce98e350`,
`feat/skeptic-effort-value-alignment b3d6d9ea6` (merged),
`pattern-classification d5f2bdc54`,
`plan/skeptic-practical-improvement-reset eb0639662` (merged),
`promotion-check 6b69e3533` (merged), `revised-questions f76ba4d68`.
PR #4 open (head `ff08a84`, base `b071899`); PR #2 open from fork
`EHS-il/skeptic:integrate-karpathy-coding-discipline`.

Invalidation: any tip differs, a "merged" branch gains commits, PR states
changed, or a new open PR references a listed branch -> STOP, re-audit
once, update this table; a second drift -> CONFLICT.

## Authority and source-of-truth order

1. Owner instruction: consolidation plan Track 2 (merged in `main`).
2. Live remote/GitHub state observed at execution.
3. This Task Prompt.
PR #2 belongs to an external contributor: comment authority only. Closing
or merging PR #2 requires an explicit owner decision - out of scope.

## Scope and mutation boundary

Allowed: `git fetch --prune`; ancestry checks; create and push the seven
`archive/*` tags; delete exactly the nine listed remote branches; close
PR #4; one comment per PR (#2, #4); edit the two listed files; add the
slice record; commit/push working branch; ff-merge and push `main`.
Forbidden: force push; deleting `main`, the working branch, or
`benchmark/...`; deleting any unlisted branch; deleting tags; merging any
PR; editing `skeptic.md` or `agents/*`; any write to the fork.
Rollback: restore any branch with `git push origin <tag>^{}:refs/heads/<branch>`
(mapping table in the slice record); reopen PR #4; revert the test edit
via git.
Expected final state: clean tree; `main` == `origin/main` containing the
slice commit; remote has 3 branches (`main`, working branch, benchmark)
plus 7 archive tags.

## Completion-feasibility and budget

Largest useful slice: all of Track 2 - small and deterministic.
Envelope: single session, ~20 git/MCP operations, one bounded test edit.
Protected completion reserve: merge-to-main and fresh remote verification
run before any optional wording polish or extra tidying.
Limits: max 2 retries per failure class, then redesign; network retries
up to 4 with backoff. Futility stop: permission or branch-protection
refusal -> CONFLICT with state preserved (tags already pushed are the
safe partial state; deletions simply defer).

## Execution graph

P1 Preflight re-audit. Deps: none. `git fetch --prune`; recompute tips,
ancestry (merged set), PR states via MCP; compare to table above.
Accept: exact match (or one documented re-audit). Next: P2, P3, P4.

P2 PR #4 disposition. Deps: P1. Diff the branch's rules against current
`agents/lead-agent-prompt.md`; write the harvest note; post close-comment;
close PR #4. Ordering rule: close BEFORE its branch deletion so closure is
an explicit decision, not a side effect. Accept: PR #4 state=closed,
comment visible via MCP read-back.

P3 PR #2 disposition. Deps: P1. Post the comment defined in DONE-2.
Accept: comment visible; PR still open.

P4 Archive tags. Deps: P1. Create the seven annotated tags at the recorded
SHAs; push; verify each via `ls-remote --tags` dereferenced SHA. Accept:
7/7 verified. Record the tag-to-SHA-to-branch table in the slice record
draft now (durable before deletions).

P5 Branch deletion. Deps: P4 (per-branch tag verified) and P2 (for the
PR #4 head branch). For the four merged branches first prove
`git merge-base --is-ancestor <tip> origin/main`; then delete. Delete the
five tagged branches. Never touch `benchmark/...`. Accept: `ls-remote`
shows the nine branches gone, benchmark present, tags present.

P6 Frozen-hash migration. Deps: P4 (sh-pf tag verified). Remove the hash
constant and its test; add the governance pointer line; run the full
suite. Accept: suite green (85 expected); `git status` shows only the two
intended files changed.

P7 Record and publish. Deps: P2-P6. Finalize the slice record with
receipts and RunSkeptic result; commit on the working branch; push;
ff-merge to `main`; push; `git fetch`; verify `origin/main` contains the
commit and equals local `main`; rerun the suite on `main`.

## Context and evidence custody

Lead context: this prompt, the re-audited table, per-phase acceptance
results. Deterministic outputs (ls-remote listings, ancestry checks, test
results) are evidence; the tag table is persisted in the slice record at
P4, before any deletion depends on it. Gap ledger inside the slice record
if any phase blocks.

## Clean-room / independence

NOT_APPLICABLE - no evaluation, comparison, or scoring in scope.

## Failure, retry, redesign, and handoff

Failure classes: permission/protection refusal -> CONFLICT, preserve
state; network -> retry x4 backoff; state drift -> one re-audit then
CONFLICT; suite failure after P6 -> revert the edit, re-diagnose, max 2
attempts then CONFLICT. Pre-exhaustion handoff: commit and push the slice
record with a completed-phase table; deferred deletions are safe because
their tags are already pushed and verified.

## System verification

- Full `ls-remote` (heads and tags) compared against the expected final
  set from DONE-3/4/5.
- Disconfirming check on protected state: `benchmark/...` must still
  resolve, at `fcd1fa31a`.
- Full unittest suite after P6 and again on merged `main`.
- RunSkeptic on the change; maximum 3 passes; end HANDLED or CONFLICT.

## Integration / publication / remote verification

As P7: non-force push, fresh fetch, SHA equality, ancestor check.
Blockers (credentials, protection, drift) -> preserve verified work,
return CONFLICT; never relabel a partial state as DONE.

## Task Closure Receipt

Enumerate DONE-1 through DONE-7 each yes/no with evidence (PR states and
comment URLs, ls-remote excerpts, ancestry proofs, suite counts, fresh
`origin/main` SHA); protected-state result for `benchmark/...` and
`main`; unresolved blockers; residual risk. `Overall DONE: yes` only when
all seven verify.

# PONYTAIL / KISS - NON-NEGOTIABLE EXECUTION CHECKSUM

Never delete an unmerged branch before its remote archive tag is verified.
Never touch benchmark/skeptic-capability-stage2-2026-07-04 or main history.
Close PR #4 with its comment before deleting its head branch.
PR #2: one comment only - no close, no merge.
No force push. No tag deletion. Drift or unexpected mutation = stop.
Merged-to-remote-main with fresh verification is the only DONE.

# END OF PROMPT
