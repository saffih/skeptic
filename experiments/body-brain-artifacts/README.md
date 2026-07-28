# Body-Brain Artifacts

These templates define a minimal file-based protocol for a future task-specific workspace. The Body coordinates and executes, the temporary Brain reasons and plans, and files carry durable state.

The compact Body boundary is defined in [`capabilities/body_state/body_state.md`](../../capabilities/body_state/body_state.md) and validated by [`capabilities/body_state/body_state.py`](../../capabilities/body_state/body_state.py). Large evidence remains external and is referenced by verified path, SHA-256, byte size, type, description, and read condition.

For one authorized exact text range, use [`capabilities/focused_retrieval/focused_retrieval.md`](../../capabilities/focused_retrieval/focused_retrieval.md) and [`capabilities/focused_retrieval/focused_retrieval.py`](../../capabilities/focused_retrieval/focused_retrieval.py); it validates Body structure without opening unrequested artifacts and streams only the selected source.

For one immutable persistence point, use [`capabilities/immutable_checkpoint/immutable_checkpoint.md`](../../capabilities/immutable_checkpoint/immutable_checkpoint.md) and [`capabilities/immutable_checkpoint/immutable_checkpoint.py`](../../capabilities/immutable_checkpoint/immutable_checkpoint.py). Checkpoints are self-contained, create-only, atomically published, and structurally valid without the original Body-state file; this slice does not resume execution.

For fresh-process admission from one exact checkpoint, use [`capabilities/restart_admission/restart_admission.md`](../../capabilities/restart_admission/restart_admission.md) and [`capabilities/restart_admission/restart_admission.py`]. Restart admission binds checkpoint identity, revalidates referenced artifacts, rejects a completed current step, materializes the exact nested Body snapshot create-only, and returns READY or BLOCKED without executing an action. BLOCKED is not execution authority, and neither status provides exactly-once side-effect guarantees.

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
