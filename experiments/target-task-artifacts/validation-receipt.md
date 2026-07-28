# Target Task validation receipt

Date: 2026-07-28
Implementation route: GPT-5.6 Sol LOW; actual runtime routing is not independently exposed.

## Interruption and resume exercise

- Harness: `harness/target_task_lifecycle.py`
- Test: `tests/test_target_task_lifecycle.py::TargetTaskLifecycleTests.test_interruption_resume_and_completed_step_nonrepetition`
- Observed result: `PASS`
- Evidence: an accepted `S1` remains in `COMPLETED_STEPS_AND_EVIDENCE`; resume continues at `S2` and does not silently repeat `S1`.
- Integrity exercise: `test_plan_and_checkpoint_identity_mismatch_blocks` observed `TargetTaskIntegrityError` (`PASS`).

## Agent-boundary and retrieval exercise

- Harness: `harness/target_task_context_pressure.py`
- Test: `tests/test_target_task_context_contract.py::TargetTaskContextContractTests.test_pressure_experiment_preserves_correctness_and_limits_reads`
- Observed context status: `CONTEXT_ISOLATION_UNKNOWN`
- Observed result: `PASS`
- Evidence: the worker contradiction produced `HANDOFF_SUFFICIENT: NO`; focused retrieval resolved the authoritative value; large irrelevant artifacts were not read; the receipt made no runtime-isolation or token-reduction claim.

## Validation commands

```text
python3 -m unittest tests.test_target_task_lifecycle tests.test_target_task_context_contract tests.test_target_task_routing
python3 -m unittest discover -s tests -p 'test*.py'
git diff --check
```

The full suite passed with 177 tests at the time of this receipt. This harness
is deterministic evidence of protocol mechanics, not proof of model-runtime
isolation.
