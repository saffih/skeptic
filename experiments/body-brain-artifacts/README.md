# Body-Brain Artifacts

These legacy templates are retained for compatibility. The canonical
file-based protocol is in `experiments/target-task-artifacts/`; the Body
coordinates and executes, the temporary Brain reasons and plans, and files
carry durable state.

- `task.md` identifies the task, authority, evidence, constraints, and requested routing.
- `body.md` tells a cheap Body how to dispatch planning, accept and seal a plan, execute it, and record results.
- `brain.md` tells a temporary Brain how to create the complete plan without executing the task.
- `plan.md` is the Brain's output and becomes immutable after Body acceptance.
- `receipt.md` records dispatch, routing, the accepted plan hash, execution, and final verification.

The future workflow is:

Task is written to `task.md`
→ cheap Body reads `task.md`
→ cheap Body invokes temporary Brain
→ Brain reads referenced files
→ Brain writes `plan.md`
→ Body performs bounded acceptance checks
→ Body records the accepted plan hash
→ Body executes the plan
→ Body writes `receipt.md`

Handoffs use file references. Large sources remain in referenced authoritative files; summaries may aid navigation but do not replace those files. The accepted `plan.md` is sealed by recording its SHA-256, which the Body verifies again at completion. `receipt.md` is the execution record.

These are templates, not active runtime state. No Body-Brain execution experiment has yet proven this artifact set.

`agents/target-task.md` defines the canonical Target Task lifecycle. The
legacy `agents/otp-protocol.md` and this directory remain readable
compatibility surfaces for existing callers; neither is a competing protocol.
