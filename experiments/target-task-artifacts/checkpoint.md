# Durable checkpoint

The Body writes this artifact after plan acceptance and every accepted
material step. It is compact control state, not a transcript or raw-output
archive.

```text
TARGET_TASK_ID:
TASK_REFERENCE:
AUTHORITY_REFERENCE:
PLAN_REFERENCE:
PLAN_HASH:
EXECUTION_MODE:
OBSERVED_CONTEXT_STATUS:
CURRENT_STEP:
COMPLETED_STEPS_AND_EVIDENCE:
ACCEPTED_VALIDATED_CLAIMS:
OPEN_FINDINGS:
OPEN_BLOCKERS:
MATERIAL_DEVIATIONS:
ARTIFACT_REFERENCES:
NEXT_AUTHORIZED_ACTION:
LAST_VALIDATION_STATE:
CHECKPOINT_VERSION: 1
```

Resume must validate every identity, the schema/version, material evidence,
authorization, and integrity before continuing. A mismatch blocks; accepted
completed steps are not silently repeated.
