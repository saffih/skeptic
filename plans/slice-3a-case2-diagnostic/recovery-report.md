# Slice 3B — Slice 3A Case 2 Evidence Recovery Report

Neutral evidence packet, part 1 of 3. Facts and Checker outputs only; no
diagnosis and no recommended disposition appear in this file.

Date: 2026-07-18. Environment: Claude Code managed remote execution
environment (ephemeral container, fresh clone), repository `saffih/skeptic`.

## Verified starting state (Checker outputs)

- Repository: `saffih/skeptic`; remote `origin` (proxied GitHub).
- Checked-out branch: `claude/slice-3a-case2-recovery-dr57xb` at
  `369c84121bd5d0056a935f1eeffa71c6fd4a46d8` — identical to `origin/main`
  (0 unique commits). This branch is session-local: `git ls-remote origin`
  does NOT advertise `refs/heads/claude/slice-3a-case2-recovery-dr57xb`.
- Working tree clean before this task's writes; single worktree; no stashes.
- Baseline tests: `python3 -m unittest discover -s tests` → 85 tests, OK.
  (Prior records cite 86; commit `c7114e7` "retire SH:PF byte-hash pin"
  accounts for the retired test.)
- Protected paths (must remain byte-for-byte unchanged): everything outside
  `plans/slice-3a-case2-diagnostic/`.

## Contract identities (at HEAD `369c841`)

| File | Git blob | SHA-256 | Bytes |
| --- | --- | --- | --- |
| `AGENTS.md` | `da16222` | `00b22a112a971d586d0a68c427c5fea225f128b54f92fcaba0ae39875b2bf381` | 263 |
| `skeptic.md` | `f651a833` | `7c052b21dc4fbeca4c90c18a0b0fc24911618733c8d9bb1a468ce744aafeee8b` | 34097 |
| `agents/lead-agent-prompt.md` | `59d2b240` | `bb685d90ccd6d28ab3739ee9b8aa51acb0b4ec2eee852186854e4328071e27a2` | 22267 |
| `agents/task-prompt.md` | `3d3ca44a` | `14dea51034dd92555310622c21e1b88c4276e864740cc92f63f78e3bfd773f5f` | 18703 |

All four companions were read in full and applied. None was unavailable,
unreadable, or incompatible.

## Bounded recovery procedure — exact searches performed

1. Working-tree content grep (`3A|3a|NO_PROMOTION|Case 2|case-2|case2|R1`,
   case-sensitive, all files): only incidental hex-SHA substring matches in
   `plans/skeptic-git-hygiene-slice-*.md`. No Slice 3A artifact.
2. `git ls-remote origin`: full advertised ref list captured. Refs present:
   `main`, 7 `archive/*` branches, `benchmark/skeptic-capability-stage2-2026-07-04`,
   `claude/skeptic-git-hygiene-1efkvx`, `claude/skeptic-routing-clarification-1efkvx`,
   and `refs/pull/{2,3,4,5,6,7,8,9}/head` (+`pull/2/merge`). No ref whose
   name references slice-3, case2, R1, or candidate evaluation.
3. `git fetch origin '+refs/heads/*' '+refs/pull/*/head'`: every advertised
   ref fetched locally (60 commits reachable in total).
4. Commit-message search across all refs
   (`git log --all --remotes --grep`, case-insensitive, patterns `slice.3a`,
   `Slice 3A`, `3A`, `NO_PROMOTION`, `case 2`): zero matches.
5. Path inventory: `git ls-tree -r --name-only` over every commit reachable
   from every ref → 231 unique paths ever tracked. Zero paths match
   slice-3/case2/judge/manifest-evaluation patterns. (The `harness/test_cases/`
   paths belong to PR #2's detection harness, cases tc01–tc18 — a different,
   older instrument.)
6. Content grep of every ref tip
   (`git grep -l -i 'NO_PROMOTION|slice 3|slice-3|Case 2' <ref>` for all
   `refs/remotes/origin/*` including PR heads): the ONLY match is
   `plans/skeptic-consolidation-and-dogfood-plan.md` (all branches), which
   matches on the phrase "Slice 3 - Doctrine dedup" — a different slice
   definition (see provenance note below).
7. `git fsck --lost-found`: zero dangling commits/blobs.
8. `git tag -l` and remote tags via ls-remote: zero tags (consistent with
   the git-hygiene record: the proxy 403s tag pushes; archives are branches).
9. `git reflog --all`: clone/fetch entries only (fresh container clone).
10. GitHub PRs: all 9 PRs (open+closed) listed with full bodies. No mention
    of Slice 3A, Case 2, R1, six-case evaluation, or NO_PROMOTION.
11. GitHub issues: 2 issues. #1 (question-count mismatch, 2026-05) and #10
    (Operational Pilot ledger, Tasks 1–4, all targeting the separate
    `HLDspec` repository). All 5 comments of #10 read in full: no Slice 3A
    reference. The pilot's "Case 7" / decision numbering concerns HLDspec
    audit-log semantics, not a Skeptic candidate evaluation.
12. Disconfirming completion check (run after independent review flagged
    reliance on searches 1–11): `refs/pull/2/merge` — the one advertised
    ref initially excluded from the fetch refspec — was fetched and
    searched by content grep and path inventory. No match; its only
    manifest-like paths are PR #2's own `harness/test_cases/tc01–tc18`
    files, already accounted for. Every ref advertised by
    `git ls-remote origin` has now been fetched and searched.

## Required Case 2 artifact inventory

Every artifact required by the Slice 3B task, with recovery result:

| # | Required artifact | Result | Where searched |
| --- | --- | --- | --- |
| 1 | Baseline Case 2 input and output | MISSING | searches 1–11 |
| 2 | Candidate Case 2 input and output | MISSING | searches 1–11 |
| 3 | Evaluation manifest | MISSING | searches 1–11 |
| 4 | Frozen behavioral/scoring contract | MISSING | searches 1–11 |
| 5 | Judge packet | MISSING | searches 1–11 |
| 6 | Judge rationale and per-dimension scoring | MISSING | searches 1–11 |
| 7 | Final RunSkeptic receipt (Slice 3A) | MISSING | searches 1–11 |
| 8 | Terminal evidence / closure receipt (Slice 3A) | MISSING | searches 1–11 |
| 9 | Candidate diff | MISSING | searches 1–11 |
| 10 | Protected-file blobs referenced by the evaluation | N/A — no evaluation refs exist; current protected blobs recorded above | — |

Why recovery failed: the artifacts are not present in any object reachable
from any advertised ref, any dangling object, any tag, any stash, any
reflog entry, any PR head, or any GitHub issue/PR text. A fresh-clone
container cannot contain unpushed state from another session. Therefore the
Slice 3A branch and commits are proved ABSENT from cloud-accessible git
state; if they ever existed, they existed only in a transient session
context or an unpushed ephemeral container that has been reclaimed.

## Byte-for-byte evidence preservation

Nothing recoverable existed to copy. The single surviving reference to
Slice 3A is the inbound Slice 3B task prompt itself, preserved as received
(including its own truncation marker) in `inbound-task-prompt.md` in this
directory, classified as: inbound task description, owner-supplied,
uncorroborated by any repository artifact.

## Provenance note (fact, not diagnosis)

`plans/skeptic-consolidation-and-dogfood-plan.md` (on `main`) defines the
slice sequence as: Slice 1 routing clarification (merged), Slice 2 git
hygiene (merged), Slice 3 doctrine dedup, Slice 4 dogfood (≥3 entries),
gating later capability work. No repository artifact defines a "Slice 3A"
candidate evaluation, an "R1" candidate, a six-case A/B protocol for it, or
records the decision "HANDLED — NO_PROMOTION". Those terms enter the record
only via the inbound Slice 3B task prompt. `plans/dogfood-log.md` contains
exactly one entry (Entry 001, git-hygiene) — fewer than the three entries
the consolidation plan requires before the next capability decision.
