# Safe Target Task workflow

Trigger: the first meaningful token is exactly `TT:` followed by a nonblank mission suffix.

The installed runtime is `concepts/stt/`; `scripts/target_task.py` is only a compatibility alias for `scripts/stt.py`.

## Host sequence

1. Persist the exact mission with `python3 scripts/stt.py start --repo <repo> --mission-file <file>`.
2. Retain only the compact receipt: task ID/root, mission hash/size, ledger head, artifact references, next action, or terminal outcome.
3. For `DISPATCH_PLANNER`, `DISPATCH_PLAN_REVIEW`, `DISPATCH_WORKER`, or `DISPATCH_FINAL_REVIEW`, resolve the immutable request through Boundary, launch exactly one matching semantic role, and require that role to write its complete body to the declared result artifact.
4. Never inline mission, Plan, patch, review, finding, provider transcript, command log, test output, or Worker-result bodies into the durable Lead.
5. Continue with `python3 scripts/stt.py run --task-root <path>`.
6. On an unknown admitted operation, use `reconcile`; never blindly redispatch.
7. Do not implement before the Plan has three qualifying unchanged reviews and an immutable seal.
8. Run all semantic edits in sparse capsules and every dynamic command in a disposable candidate sandbox unless explicit owner-risk acceptance was recorded before bootstrap.
9. Freeze and review the final candidate before one deterministic cutover.
10. No commit, stage, checkout, reset, merge, rebase, push, PR, publication, or task-runtime network effect is authorized.

Canonical CLI:

```text
stt start --repo <path> [--include-ignored <path> ...] [--allow-unconfined-candidate-execution] --mission-file <path>
stt run --task-root <path>
stt status --task-root <path>
stt reconcile --task-root <path>
stt retry --task-root <path>
stt replan --task-root <path>
stt stop --task-root <path>
stt resume --task-root <path>
stt diagnose --task-root <path>
stt restore --task-root <path> --destination <empty-directory>
```

The exact architecture and qualification requirements remain those bound by the signed STT v24 artifacts. The runtime must fail closed when host enforcement or evidence is unavailable.
