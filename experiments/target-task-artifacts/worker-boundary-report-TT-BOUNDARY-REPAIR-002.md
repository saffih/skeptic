# Worker Boundary Report: TT-BOUNDARY-REPAIR-002

## STATUS

COMPLETE

- Requested routing: GPT-5.6 Sol, LOW reasoning.
- Actual routing: `ACTUAL_ROUTING_UNKNOWN`; the runtime did not expose a verifiable model, version, or effort setting. This follows `agents/model-routing.md:130-134`.
- Claim status: every implementation conclusion below is `WORKER_REPORTED` pending Body acceptance. The focused test result is reported as observed command output, not as independent review or task-level acceptance.

## WORK_PERFORMED

Inspected only the authorized architecture, protocol, routing, lifecycle implementation, and focused lifecycle test files in `/Users/saffi/code/skeptic-target-task`. Evaluated the repaired lifecycle specifically for:

1. plan validation and sealing;
2. handoff provenance validation versus claim acceptance;
3. checkpoint integrity and resume validation;
4. authorization and repetition of completed steps.

Ran only the focused lifecycle test module:

```text
python3 -m unittest tests/test_target_task_lifecycle.py
........
----------------------------------------------------------------------
Ran 8 tests in 0.002s

OK
```

No canonical contract, implementation, or test file was modified. This report is the only requested output artifact.

## DECISION_RELEVANT_FINDINGS

### 1. Plan validation and sealing

`WORKER_REPORTED`: The lifecycle now rejects structurally incomplete plans, task-identity mismatch, unsupported review mode, missing step fields, duplicate or invalid step IDs, missing dependencies, and dependency cycles (`harness/target_task_lifecycle.py:54-90`). Acceptance serializes the validated plan, adds the deterministic first executable step, and hashes the resulting frozen representation (`harness/target_task_lifecycle.py:92-94`). Focused tests exercise valid sealing and rejection of invalid review mode, missing fields, duplicate IDs, missing dependencies, and cycles (`tests/test_target_task_lifecycle.py:37-46`).

Decision: the repaired implementation provides meaningful deterministic plan-shape, graph, identity, review-mode, and hash-boundary checks consistent with the architecture's reject-not-repair direction. It does not establish semantic adequacy of authority, actions, validation instructions, stop conditions, or source-of-truth order; most required fields are presence-checked rather than type- or content-validated. Only final `VALIDATION`, `HANDOFF`, and `SUCCESS_CRITERIA` are explicitly required to be non-empty (`harness/target_task_lifecycle.py:86-87`).

### 2. Provenance acceptance

`WORKER_REPORTED`: Handoff validation requires all required fields and rejects unknown or absent claim provenance (`harness/target_task_lifecycle.py:149-154`). Claim acceptance is separate: it excludes `WORKER_REPORTED`, `INFERRED`, `UNRESOLVED`, and `INDEPENDENTLY_REVIEWED`, accepting only `DIRECTLY_OBSERVED` and `DETERMINISTICALLY_VALIDATED`; directly observed claims additionally require an evidence reference (`harness/target_task_lifecycle.py:19-20,156-162`). The focused test verifies that worker-reported material can remain in a structurally valid handoff without entering the accepted ledger, while deterministic and evidence-referenced direct claims can enter it (`tests/test_target_task_lifecycle.py:79-84`).

Decision: the repair closes the key promotion gap for worker assertions. A remaining integrity limitation is that `DETERMINISTICALLY_VALIDATED` claims need no evidence reference, validator identity, or validation result. Also, `INDEPENDENTLY_REVIEWED` is recognized but never accepted by this reference mechanism; that is conservative, but the intended downstream path for such claims is not represented here.

### 3. Checkpoint integrity and resume

`WORKER_REPORTED`: Checkpoint validation enforces the complete field set, exact checkpoint version, valid execution/context values, accepted completed-step evidence, sealed-plan content/hash agreement, known current/completed steps, non-completion of the current step, coherent dependency completion, exact `RUN-<CURRENT_STEP>` next authorization, and absence of open blockers (`harness/target_task_lifecycle.py:108-126`). Resume then checks task ID, plan hash/reference, and optionally task and authority references (`harness/target_task_lifecycle.py:139-147`). Checkpoint writes use a same-directory temporary file plus atomic replacement (`harness/target_task_lifecycle.py:128-137`). Tests cover successful interruption/resume and rejection of task/authority mismatch, version mismatch, altered plan content, unknown steps, malformed evidence, and blockers (`tests/test_target_task_lifecycle.py:48-68`).

Decision: when `resume_checkpoint` is supplied the sealed plan and both optional references, the repaired path materially enforces identity, plan integrity, graph coherence, evidence shape, next-action authorization, and blocker stops. However, `sealed_plan`, `task_reference`, and `authority_reference` are optional at the API boundary. Omitting them weakens resume checks. `write_checkpoint` validates without the sealed plan, so sealed-plan content binding is deferred until a later resume that actually supplies it.

### 4. Completed-step authorization

`WORKER_REPORTED`: Ordinary authorization permits only the checkpoint's current step and requires its dependencies to be in completed evidence. Unknown steps are rejected. A completed step cannot repeat unless a retry record contains truthy reason, prior status, authority, expected new evidence, and `MAX_ATTEMPTS >= 1` (`harness/target_task_lifecycle.py:164-171`). Accepted results must also carry accepted artifact evidence and `VALIDATION == PASS` (`harness/target_task_lifecycle.py:173-178`). The focused test exercises current-step authorization, rejection of completed and unknown steps without authority, explicit retry authorization, and rejection of missing artifact evidence (`tests/test_target_task_lifecycle.py:70-77`).

Decision: the repair establishes a behavioral non-repetition default and an explicit retry gate. Remaining limitations are that retry authority is only checked for truthiness, no attempt count is persisted or compared with `MAX_ATTEMPTS`, prior-result status is not constrained to a known value, and expected-new-evidence is not compared with the submitted evidence. Thus the mechanism validates retry-envelope presence, not full retry-budget or evidence-novelty semantics.

## LIMITATIONS

- This was a bounded worker inspection, not Body acceptance, independent review, RunSkeptic, or repository-wide validation.
- Only the six authorized files were read; no imports, callers, history, diffs, fixtures, or broader tests were inspected.
- Only `tests/test_target_task_lifecycle.py` was run. Eight tests passed, but this does not prove untested malformed-type, terminal-state, concurrency, durability, or adversarial cases.
- Runtime context isolation was not observable. The shared transcript exists, so no fresh-context or independent-review claim is made.
- Requested model and reasoning settings were not observable; actual routing remains unknown.
- Line references describe the inspected snapshot and may drift if the worktree changes.

## ARTIFACT_REFERENCES

- Report: `/Users/saffi/code/skeptic-target-task/experiments/target-task-artifacts/worker-boundary-report-TT-BOUNDARY-REPAIR-002.md`
- Architecture authority: `/Users/saffi/code/skeptic-target-task/architecture/target-task-architecture.md`
- Protocol summary: `/Users/saffi/code/skeptic-target-task/agents/target-task.md`
- Routing contract: `/Users/saffi/code/skeptic-target-task/agents/model-routing.md`
- Inspected implementation: `/Users/saffi/code/skeptic-target-task/harness/target_task_lifecycle.py`
- Focused validation: `/Users/saffi/code/skeptic-target-task/tests/test_target_task_lifecycle.py`

## RETRIEVAL_GUIDANCE

For Body acceptance, begin with this report. Retrieve implementation ranges `54-94` for plan validation/sealing, `108-147` for checkpoint/resume, `149-162` for provenance handling, and `164-178` for step authorization/result acceptance. Retrieve focused test ranges `37-84` to verify current behavioral coverage. Read the full authorized files only if those focused ranges are insufficient for the acceptance decision.

Suggested acceptance checks:

1. Confirm that conservative exclusion of `INDEPENDENTLY_REVIEWED` claims is intended.
2. Decide whether deterministic claims require evidence references or validator metadata.
3. Decide whether sealed-plan and task/authority references must become mandatory for every resume.
4. Decide whether retry attempt accounting, authority semantics, and new-evidence matching are required before accepting completed-step authorization as complete.

## NEXT_AUTHORIZED_ACTION

Body validates this compact report against the focused references and test receipt, preserves all implementation claims as `WORKER_REPORTED` until accepted, and decides whether the four listed limitations are accepted constraints or require a separately authorized repair step. No canonical contract/test edit or broader test run is authorized by this worker report.
