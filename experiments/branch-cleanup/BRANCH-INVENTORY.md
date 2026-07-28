# Deterministic branch inventory

Snapshot of the repository state at baseline `c48010ce7da7af645c7ad9cef79e5c9a33f71cdc` on 2026-07-28. This artifact classifies every local branch, every `origin/*` remote-tracking branch, every registered worktree, and the live remote branch advertisement. No local or remote branch was deleted, removed, pruned, or pushed. `origin/HEAD` is a symbolic pointer and is excluded from branch counts.

## Evidence and gates

- Authority: baseline commit `c48010ce7da7af645c7ad9cef79e5c9a33f71cdc`, current local refs/worktrees, and fresh `git ls-remote origin 'refs/heads/*'`.
- Local `main`: `c48010ce7da7af645c7ad9cef79e5c9a33f71cdc`; `origin/main`: `f7ae13754fb100eadcce58567eb4decf09fd8878`.
- Current branch: `main`; local `main` is ahead of `origin/main` by 4 commits.
- Untracked `experiments/body-brain-runs/` was preserved untouched.
- Branch inventory validation: `python3 experiments/branch-cleanup/validate_inventory.py`.

## Closed classification taxonomy

Each unique branch name has exactly one class: `MAIN`, `LOCAL_ONLY`, `LOCAL_AND_REMOTE_EQUAL`, `LOCAL_AND_REMOTE_DIVERGED`, or `REMOTE_ONLY`. `Ahead` and `Behind` are relative to local `main`; `MAIN_HEAD` is the special relation for `main`.

Counts: `MAIN` 1; `LOCAL_ONLY` 13; `LOCAL_AND_REMOTE_EQUAL` 7; `LOCAL_AND_REMOTE_DIVERGED` 2; `REMOTE_ONLY` 30. Total unique branches: **53** (23 local and 40 remote-tracking).

## Live remote reconciliation

The live remote query completed successfully at this inventory pass. Exact verification covered all 40 `origin/*` tracking refs: live advertisements 40; stale tracking refs 0; missing tracking refs 0; tracking/live SHA mismatches 0. The partition below is mutually exclusive and totals all 40 live remote branches:

| Classification | Count | Deterministic meaning |
|---|---:|---|
| Protected live `main` | 1 | `origin/main` is live and is never a deletion candidate in this task |
| Merged into live `origin/main` | 1 | `origin/agent/cost-aware-model-escalation`; exact tip is an ancestor of live `origin/main` |
| Exact-tip equivalent remote refs | 8 | Four equivalence groups: archive/benchmark with benchmark/capability, each archive/experiment ref with its matching local experiment ref, archive/main-pre-clean with calibration, and repair/candidate1 with local agent/candidate1 |
| Unresolved unique remote work | 30 | Live branches with no deterministic merged/equivalent proof; preserve and investigate separately |

Remote deletion candidates are proposed only where the remote tip has an exact equivalent. A candidate deletion must retain its equivalent; the registered calibration worktree and `experiments/body-brain-runs/` remain protected and untouched:

| Proposed remote ref | SHA | Evidence |
|---|---|---|
| `origin/archive/benchmark-skeptic-capability-stage2-2026-07-04` | `fcd1fa31a40fea050dc1f0699948e5e2c7cfebd4` | exact tip equals `origin/benchmark/skeptic-capability-stage2-2026-07-04`; no worktree |
| `origin/archive/experiment-footprint-report-prose-v1` | `8fc1f612dc6ffd5accc179fc553bcc7ada311611` | exact tip equals local `experiment/footprint-report-prose-v1`; no worktree; archive counterpart retained |
| `origin/archive/experiment-footprint-report-prose-v2` | `e9cc8cbcbdb0687883ffd190d9a3be9101d73a06` | exact tip equals local `experiment/footprint-report-prose-v2`; no worktree; archive counterpart retained |
| `origin/archive/main-pre-clean-197bf70` | `197bf70d35ce791de7de7499a58bb2a4f970450e` | exact tip equals `origin/calibration/quickcompare-20260724`, whose worktree remains protected |
| `origin/benchmark/skeptic-capability-stage2-2026-07-04` | `fcd1fa31a40fea050dc1f0699948e5e2c7cfebd4` | exact tip equals `origin/archive/benchmark-skeptic-capability-stage2-2026-07-04`; archive counterpart retained |
| `origin/calibration/quickcompare-20260724` | `197bf70d35ce791de7de7499a58bb2a4f970450e` | exact tip equals `origin/archive/main-pre-clean-197bf70`; registered calibration worktree means defer deletion |
| `origin/repair/candidate1-compat` | `61072641d4a7375723d15c3dd26a8b075bc6a662` | exact tip equals local `agent/promote-compact-skeptic-candidate1`; no worktree |

The seven rows are safe candidates individually for later owner-authorized remote deletion on current evidence; paired refs must not be deleted together. No deletion, prune, worktree removal, or push was performed.

Excluded unresolved example: `origin/agent/promote-compact-skeptic-candidate1` at `f587069c5494b3721c3ad5c6110a332eea05831c` differs from local `agent/promote-compact-skeptic-candidate1` at `61072641d4a7375723d15c3dd26a8b075bc6a662` and has no exact equivalent; preserve it.

## Branch records

| Ref | Inventory class | SHA | Remote counterpart | Worktree | Main relation | Ahead | Behind |
|---|---|---|---|---|---|---:|---:|
| `main` | MAIN | `c48010ce7da7af645c7ad9cef79e5c9a33f71cdc` | `origin/main@f7ae13754fb100eadcce58567eb4decf09fd8878` | `/Users/saffi/code/skeptic` | MAIN_HEAD | 0 | 0 |
| `agent/cost-aware-model-escalation` | LOCAL_AND_REMOTE_EQUAL | `189a24d7f7411fba2a76866b78a881d13a39c3f5` | `origin/agent/cost-aware-model-escalation@189a24d7f7411fba2a76866b78a881d13a39c3f5` | NONE | ANCESTOR_OF_MAIN | 0 | 7 |
| `agent/promote-compact-skeptic-candidate1` | LOCAL_AND_REMOTE_DIVERGED | `61072641d4a7375723d15c3dd26a8b075bc6a662` | `origin/agent/promote-compact-skeptic-candidate1@f587069c5494b3721c3ad5c6110a332eea05831c` | NONE | DIVERGED_FROM_MAIN | 49 | 20 |
| `agent/promote-compact-skeptic-candidate1-clean` | LOCAL_AND_REMOTE_EQUAL | `57382a230f8a4175ad42aba54ab2554073b6b5a8` | `origin/agent/promote-compact-skeptic-candidate1-clean@57382a230f8a4175ad42aba54ab2554073b6b5a8` | `/Users/saffi/code/skeptic-candidate1-validation` | DIVERGED_FROM_MAIN | 48 | 20 |
| `agents/hierarchical-context-contract` | LOCAL_ONLY | `9fc75c83bf42018c146c590ad4b8d33249dbfb0c` | NONE | NONE | DIVERGED_FROM_MAIN | 27 | 20 |
| `agents/hierarchical-context-slice-h1h2` | LOCAL_AND_REMOTE_EQUAL | `f174a09c7ad0ff43404ec635821ff01395d8b485` | `origin/agents/hierarchical-context-slice-h1h2@f174a09c7ad0ff43404ec635821ff01395d8b485` | NONE | DIVERGED_FROM_MAIN | 30 | 20 |
| `agents/lead-agent-prompt-orchestration-only` | LOCAL_AND_REMOTE_DIVERGED | `af58ffaa1e68030e77a8dd95089cab9b22e6caaf` | `origin/agents/lead-agent-prompt-orchestration-only@d849572c90c7071ea57b5f37d17481d6672458c8` | `/Users/saffi/code/skeptic-ab-plan` | DIVERGED_FROM_MAIN | 43 | 20 |
| `agents/lead-dispatch-first-entry-sliceA1` | REMOTE_ONLY | `68b387a421873fdda71ecef9bdce79bb6a0e85c4` | `origin/agents/lead-dispatch-first-entry-sliceA1@68b387a421873fdda71ecef9bdce79bb6a0e85c4` | — | DIVERGED_FROM_MAIN | 31 | 20 |
| `agents/lead-stateless-orchestrator-sliceA` | REMOTE_ONLY | `64597c16ae334f1d29f91f4b5c80406be3e17dae` | `origin/agents/lead-stateless-orchestrator-sliceA@64597c16ae334f1d29f91f4b5c80406be3e17dae` | — | DIVERGED_FROM_MAIN | 29 | 20 |
| `archive/benchmark-skeptic-capability-stage2-2026-07-04` | REMOTE_ONLY | `fcd1fa31a40fea050dc1f0699948e5e2c7cfebd4` | `origin/archive/benchmark-skeptic-capability-stage2-2026-07-04@fcd1fa31a40fea050dc1f0699948e5e2c7cfebd4` | — | DIVERGED_FROM_MAIN | 6 | 29 |
| `archive/claude-lead-agent-prompt-artifact-9rd2na` | REMOTE_ONLY | `ff08a84707441b7d19971ef663a04a5dc280e6c3` | `origin/archive/claude-lead-agent-prompt-artifact-9rd2na@ff08a84707441b7d19971ef663a04a5dc280e6c3` | — | DIVERGED_FROM_MAIN | 3 | 29 |
| `archive/experiment-footprint-report-prose-v1` | REMOTE_ONLY | `8fc1f612dc6ffd5accc179fc553bcc7ada311611` | `origin/archive/experiment-footprint-report-prose-v1@8fc1f612dc6ffd5accc179fc553bcc7ada311611` | — | DIVERGED_FROM_MAIN | 40 | 20 |
| `archive/experiment-footprint-report-prose-v2` | REMOTE_ONLY | `e9cc8cbcbdb0687883ffd190d9a3be9101d73a06` | `origin/archive/experiment-footprint-report-prose-v2@e9cc8cbcbdb0687883ffd190d9a3be9101d73a06` | — | DIVERGED_FROM_MAIN | 40 | 20 |
| `archive/experiment-skeptic-meta-process-value-ab-001` | REMOTE_ONLY | `9c24f6f3a8a8c9f75d060ccef07f49e736866689` | `origin/archive/experiment-skeptic-meta-process-value-ab-001@9c24f6f3a8a8c9f75d060ccef07f49e736866689` | — | DIVERGED_FROM_MAIN | 8 | 29 |
| `archive/experiment-skeptic-trust-boundary-fe-tb-ab-001` | REMOTE_ONLY | `fce98e3505eda14b2588869eeef44528f81c7a2e` | `origin/archive/experiment-skeptic-trust-boundary-fe-tb-ab-001@fce98e3505eda14b2588869eeef44528f81c7a2e` | — | DIVERGED_FROM_MAIN | 9 | 29 |
| `archive/main-pre-clean-197bf70` | REMOTE_ONLY | `197bf70d35ce791de7de7499a58bb2a4f970450e` | `origin/archive/main-pre-clean-197bf70@197bf70d35ce791de7de7499a58bb2a4f970450e` | — | DIVERGED_FROM_MAIN | 45 | 20 |
| `archive/pattern-classification` | REMOTE_ONLY | `d5f2bdc54b6cf076b5d7ab836ab0b49e40960045` | `origin/archive/pattern-classification@d5f2bdc54b6cf076b5d7ab836ab0b49e40960045` | — | DIVERGED_FROM_MAIN | 1 | 39 |
| `archive/revised-questions` | REMOTE_ONLY | `f76ba4d68ed090b768778ed415f0004f4bf6fecb` | `origin/archive/revised-questions@f76ba4d68ed090b768778ed415f0004f4bf6fecb` | — | DIVERGED_FROM_MAIN | 4 | 35 |
| `archive/sh-pf-frozen-contract` | REMOTE_ONLY | `52cd8226c276186530a32a52b36d5a3943434faa` | `origin/archive/sh-pf-frozen-contract@52cd8226c276186530a32a52b36d5a3943434faa` | — | DIVERGED_FROM_MAIN | 5 | 20 |
| `audit/shadow-scenario-inventory` | LOCAL_ONLY | `e9168cc2e287fc8301dae72af996ed5b547c518c` | NONE | NONE | DIVERGED_FROM_MAIN | 2 | 15 |
| `benchmark/baseline-v1` | REMOTE_ONLY | `bbdbdf64db30870bdc2ac71481f38569cd6a15e4` | `origin/benchmark/baseline-v1@bbdbdf64db30870bdc2ac71481f38569cd6a15e4` | — | DIVERGED_FROM_MAIN | 38 | 20 |
| `benchmark/minimal-golden-cases` | REMOTE_ONLY | `5f205b47ddca0117f7973c23b8a549150c3ca57a` | `origin/benchmark/minimal-golden-cases@5f205b47ddca0117f7973c23b8a549150c3ca57a` | — | DIVERGED_FROM_MAIN | 37 | 20 |
| `benchmark/scorer-v2` | REMOTE_ONLY | `534aab276bff65d05b4d3129242d61dc87df4c73` | `origin/benchmark/scorer-v2@534aab276bff65d05b4d3129242d61dc87df4c73` | — | DIVERGED_FROM_MAIN | 39 | 20 |
| `benchmark/scorer-v3-dignity-recognition` | REMOTE_ONLY | `a5e29cc4a96b19f25648ec75218631f2b6bce07e` | `origin/benchmark/scorer-v3-dignity-recognition@a5e29cc4a96b19f25648ec75218631f2b6bce07e` | — | DIVERGED_FROM_MAIN | 42 | 20 |
| `benchmark/scorer-v3-semantic-equivalence` | LOCAL_AND_REMOTE_EQUAL | `b55e3a029fcabdd96466fd56012b1bcbdd312a0f` | `origin/benchmark/scorer-v3-semantic-equivalence@b55e3a029fcabdd96466fd56012b1bcbdd312a0f` | NONE | DIVERGED_FROM_MAIN | 40 | 20 |
| `benchmark/skeptic-capability-stage2-2026-07-04` | REMOTE_ONLY | `fcd1fa31a40fea050dc1f0699948e5e2c7cfebd4` | `origin/benchmark/skeptic-capability-stage2-2026-07-04@fcd1fa31a40fea050dc1f0699948e5e2c7cfebd4` | — | DIVERGED_FROM_MAIN | 6 | 29 |
| `calibration/quickcompare-20260724` | LOCAL_AND_REMOTE_EQUAL | `197bf70d35ce791de7de7499a58bb2a4f970450e` | `origin/calibration/quickcompare-20260724@197bf70d35ce791de7de7499a58bb2a4f970450e` | `/private/tmp/claude-501/-Users-saffi-code-skeptic-ab-plan/9aac337e-7e3f-422a-8933-bb77a1b5d219/scratchpad/quickcompare-calibration-wt` | DIVERGED_FROM_MAIN | 45 | 20 |
| `candidate/compact-skeptic-current-main` | LOCAL_ONLY | `47ac9cf4d443fc25eb690586e0190a652596cefa` | NONE | `/Users/saffi/code/skeptic-compact-current-main` | ANCESTOR_OF_MAIN | 0 | 12 |
| `candidate/lead-agent-context-model-discipline` | LOCAL_ONLY | `5def7436abd2d1faffd3096371b6f4b3909bdb92` | NONE | NONE | DIVERGED_FROM_MAIN | 3 | 20 |
| `claude/skeptic-git-hygiene-1efkvx` | REMOTE_ONLY | `c7114e728c95a0fa1f6bce7fbf53244d0e7078b9` | `origin/claude/skeptic-git-hygiene-1efkvx@c7114e728c95a0fa1f6bce7fbf53244d0e7078b9` | — | DIVERGED_FROM_MAIN | 10 | 20 |
| `claude/skeptic-routing-clarification-1efkvx` | REMOTE_ONLY | `7de5ef6dbd0239e8b3d0219c0ef9e9c354b7722e` | `origin/claude/skeptic-routing-clarification-1efkvx@7de5ef6dbd0239e8b3d0219c0ef9e9c354b7722e` | — | DIVERGED_FROM_MAIN | 11 | 20 |
| `claude/skeptic-slice3b-correction-20260719-01` | REMOTE_ONLY | `1f4a9ae3fafd3f8023475efb630b804997bcd2da` | `origin/claude/skeptic-slice3b-correction-20260719-01@1f4a9ae3fafd3f8023475efb630b804997bcd2da` | — | DIVERGED_FROM_MAIN | 20 | 20 |
| `claude/slice-3a-case2-recovery-dr57xb` | REMOTE_ONLY | `29788a48eee3875485fbea6d17356a88d658ec9e` | `origin/claude/slice-3a-case2-recovery-dr57xb@29788a48eee3875485fbea6d17356a88d658ec9e` | — | DIVERGED_FROM_MAIN | 16 | 20 |
| `codex/cleanup-rebaseline-and-validate-current-skeptic` | LOCAL_AND_REMOTE_EQUAL | `4641ff0045984308b3639683c8aee8a91b00804d` | `origin/codex/cleanup-rebaseline-and-validate-current-skeptic@4641ff0045984308b3639683c8aee8a91b00804d` | `/private/tmp/skeptic-cleanup-rebaseline-current-main-wt` | DIVERGED_FROM_MAIN | 3 | 10 |
| `codex/skeptic-cross-file-interface-20260718-001` | LOCAL_ONLY | `04498852d25cbd7f105947655d94d9718cdb49e7` | NONE | NONE | DIVERGED_FROM_MAIN | 11 | 20 |
| `codex/skeptic-cross-file-interface-20260718-01` | LOCAL_ONLY | `e6eaf9d6a4d0abf303360f7d9763cee8bd57be32` | NONE | NONE | DIVERGED_FROM_MAIN | 13 | 20 |
| `docs/verification-workflow-contract` | REMOTE_ONLY | `bc188ee09b94f314a9aa3d43dc69c2a077915e07` | `origin/docs/verification-workflow-contract@bc188ee09b94f314a9aa3d43dc69c2a077915e07` | — | DIVERGED_FROM_MAIN | 25 | 20 |
| `dogfood/agents-path-integrity` | REMOTE_ONLY | `f8db8b50a91b4cacb49edb6953cf704481fa39dd` | `origin/dogfood/agents-path-integrity@f8db8b50a91b4cacb49edb6953cf704481fa39dd` | — | DIVERGED_FROM_MAIN | 23 | 20 |
| `experiment/footprint-report-prose-v1` | LOCAL_ONLY | `8fc1f612dc6ffd5accc179fc553bcc7ada311611` | NONE | NONE | DIVERGED_FROM_MAIN | 40 | 20 |
| `experiment/footprint-report-prose-v2` | LOCAL_ONLY | `e9cc8cbcbdb0687883ffd190d9a3be9101d73a06` | NONE | NONE | DIVERGED_FROM_MAIN | 40 | 20 |
| `governance/conditional-boundary-agent-v1` | REMOTE_ONLY | `765e032fd6f355cfdccc61ed59af5cc764349abd` | `origin/governance/conditional-boundary-agent-v1@765e032fd6f355cfdccc61ed59af5cc764349abd` | — | DIVERGED_FROM_MAIN | 43 | 20 |
| `governance/cost-routing-agent-return-v1` | REMOTE_ONLY | `04c8460238d378c860975ae8937f6205acf06834` | `origin/governance/cost-routing-agent-return-v1@04c8460238d378c860975ae8937f6205acf06834` | — | DIVERGED_FROM_MAIN | 40 | 20 |
| `harness/context-growth-detector-slice1` | LOCAL_ONLY | `d8f7a4d5cf47a3be2ec0ee9ada6a14c5c1eeed13` | NONE | NONE | DIVERGED_FROM_MAIN | 29 | 20 |
| `harness/quickcompare-v1` | REMOTE_ONLY | `24450c0890b00d51f7b4bea1a35daa52f4f16a0e` | `origin/harness/quickcompare-v1@24450c0890b00d51f7b4bea1a35daa52f4f16a0e` | — | DIVERGED_FROM_MAIN | 27 | 20 |
| `integrate/receipt-authority-simplicity` | REMOTE_ONLY | `e4d994c42c6d3b31cbb2200c480bbcf2202a25c3` | `origin/integrate/receipt-authority-simplicity@e4d994c42c6d3b31cbb2200c480bbcf2202a25c3` | — | DIVERGED_FROM_MAIN | 19 | 20 |
| `plan/skeptic-may-current-ab-001` | LOCAL_ONLY | `49f8fb057299897a5b09d417bd6e5e46023b8d5d` | NONE | NONE | DIVERGED_FROM_MAIN | 16 | 20 |
| `plan/skeptic-receipt-authority-consolidation` | LOCAL_AND_REMOTE_EQUAL | `abe029fa79f6698491e851175fb70076844c32ea` | `origin/plan/skeptic-receipt-authority-consolidation@abe029fa79f6698491e851175fb70076844c32ea` | NONE | DIVERGED_FROM_MAIN | 20 | 20 |
| `pr-2-test` | LOCAL_ONLY | `e893014cdb582f6f3b41fd7bc2bc225587ef9ebf` | NONE | NONE | DIVERGED_FROM_MAIN | 1 | 38 |
| `refactor/doctrine-ownership-entrypoints-20260721T085823Z` | REMOTE_ONLY | `13f25b931a2e5fd70b6bbf7c357f27ca046e1adc` | `origin/refactor/doctrine-ownership-entrypoints-20260721T085823Z@13f25b931a2e5fd70b6bbf7c357f27ca046e1adc` | — | DIVERGED_FROM_MAIN | 20 | 20 |
| `refactor/stateless-runtime-boundary-20260721` | REMOTE_ONLY | `d72d9b22d32f1e520c0fa3b44347bcb0ffd68383` | `origin/refactor/stateless-runtime-boundary-20260721@d72d9b22d32f1e520c0fa3b44347bcb0ffd68383` | — | DIVERGED_FROM_MAIN | 21 | 20 |
| `reorg/restore-skeptic-core` | LOCAL_ONLY | `b79a213d51352af2d08666d2c064941c3c4b5a0b` | NONE | NONE | DIVERGED_FROM_MAIN | 46 | 20 |
| `repair/candidate1-compat` | REMOTE_ONLY | `61072641d4a7375723d15c3dd26a8b075bc6a662` | `origin/repair/candidate1-compat@61072641d4a7375723d15c3dd26a8b075bc6a662` | — | DIVERGED_FROM_MAIN | 49 | 20 |
| `split-integrate-balance` | LOCAL_ONLY | `3c11497dd6ee8e6274c96a3c87f866aeda4ecc1d` | NONE | NONE | DIVERGED_FROM_MAIN | 1 | 35 |
## Worktrees

| Path | HEAD | Branch |
|---|---|---|
| `/Users/saffi/code/skeptic` | `c48010ce7da7af645c7ad9cef79e5c9a33f71cdc` | `main` |
| `/private/tmp/claude-501/-Users-saffi-code-skeptic-ab-plan/9aac337e-7e3f-422a-8933-bb77a1b5d219/scratchpad/quickcompare-calibration-wt` | `197bf70d35ce791de7de7499a58bb2a4f970450e` | `calibration/quickcompare-20260724` |
| `/private/tmp/skeptic-baseline-92b8f69-wt` | `92b8f69144af5edd0edb1d20e454f624276c1138` | `detached` |
| `/private/tmp/skeptic-cleanup-rebaseline-current-main-wt` | `4641ff0045984308b3639683c8aee8a91b00804d` | `codex/cleanup-rebaseline-and-validate-current-skeptic` |
| `/Users/saffi/code/skeptic-ab-plan` | `af58ffaa1e68030e77a8dd95089cab9b22e6caaf` | `agents/lead-agent-prompt-orchestration-only` |
| `/Users/saffi/code/skeptic-candidate1-validation` | `57382a230f8a4175ad42aba54ab2554073b6b5a8` | `agent/promote-compact-skeptic-candidate1-clean` |
| `/Users/saffi/code/skeptic-compact-current-main` | `47ac9cf4d443fc25eb690586e0190a652596cefa` | `candidate/compact-skeptic-current-main` |

## Cleanup record

The validated inventory authorized and this cleanup deleted exactly six local-only branches: `audit/experiment-promotion-matrix`, `audit/shadow-scenario-inventory-clean`, `reorg/benchmark-system`, `reorg/clean-main`, `reorg/quickcompare-instrument`, and `reorg/shadow-discovery-suite`. Each had no worktree and no unique commits relative to `main`. All remaining local branches, remote-tracking branches, and registered worktrees remain preserved.

## Future deletion candidates

Seven remote refs are proposed above for later owner-authorized deletion. This inventory records candidates only; deletion remains a separate operation requiring a fresh live-ref recheck. The merged branch and all unresolved unique work remain preserved.

## Terminal state

`REMOTE_RECONCILIATION_COMPLETE`: all 53 branches and all 7 registered worktrees are represented; all 40 remote-tracking refs match the live remote; seven remote deletion candidates are recorded with exact-tip evidence; no branch, remote ref, or worktree was mutated; protected `experiments/body-brain-runs/` remains untouched.
