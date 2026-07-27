# Body-Brain Artifacts

These templates define a minimal file-based protocol for a future task-specific workspace. The Body coordinates and executes, the temporary Brain reasons and plans, and files carry durable state.

`OTP.md` defines the Optimized Task Prompt, the recommended additive economy contract for day-to-day repository work. It bounds planning, agents, models, context, execution, retries, and stop behavior. `TP` remains the compatibility mode and is unchanged when selected.

- `task.md` identifies the task, authority, evidence, constraints, and requested routing.
- `body.md` tells a cheap Body how to dispatch planning, apply TP or OTP acceptance, seal a plan, execute it, and record results.
- `brain.md` tells a temporary Brain how to create the complete plan without executing the task.
- `plan.md` is the Brain's output and becomes immutable after Body acceptance.
- `receipt.md` records dispatch, routing, OTP budget accounting when applicable, the accepted plan hash, execution, and final verification.

The future workflow is:

Task is written to `task.md`
→ cheap Body reads `task.md`
→ if planning is required, cheap Body invokes temporary Brain
→ Brain reads referenced files
→ Brain writes `plan.md`
→ Body performs bounded acceptance checks
→ Body records the accepted plan hash
→ Body executes the plan
→ Body writes `receipt.md`

Handoffs use file references. Large sources remain in referenced authoritative files; summaries may aid navigation but do not replace those files. The accepted `plan.md` is sealed by recording its SHA-256, which the Body verifies again at completion. `receipt.md` is the execution record.

These are templates, not active runtime state. No Body-Brain execution experiment has yet proven this artifact set.
