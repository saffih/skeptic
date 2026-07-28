# Legacy OTP compatibility alias

`OTP:` is a historical compatibility trigger for the canonical Target Task
protocol. Read `agents/target-task.md` immediately after this note and apply
that protocol in full. `OTP:` is subordinate to `TT:`; the two names are not
co-equal protocols.

Legacy receipt mappings are:

- `OTP_ACCEPTED` -> `TARGET_TASK_ACCEPTED`
- `OTP_REJECTED` -> `TARGET_TASK_REJECTED`
- `OTP_BLOCKED` -> `TARGET_TASK_BLOCKED`
- `OTP_INTEGRITY_FAILURE` -> `TARGET_TASK_INTEGRITY_FAILURE`

This is a compatibility stub with no competing protocol definition. Do not
use it as a standalone lifecycle definition.
