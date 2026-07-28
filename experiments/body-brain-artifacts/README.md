# Body-Brain Artifacts

These templates define a minimal file-based protocol for a future task-specific workspace. The Body coordinates and executes, the temporary Brain reasons and plans, and files carry durable state.

The compact Body boundary is defined in [`agents/body-state.md`](../../agents/body-state.md) and validated by [`harness/body_state.py`](../../harness/body_state.py). Large evidence remains external and is referenced by verified path, SHA-256, byte size, type, description, and read condition.

For one authorized exact text range, use [`agents/focused-retrieval.md`](../../agents/focused-retrieval.md) and [`harness/focused_retrieval.py`](../../harness/focused_retrieval.py); it validates Body structure without opening unrequested artifacts and streams only the selected source.

For one immutable persistence point, use [`agents/checkpoint.md`](../../agents/checkpoint.md) and [`harness/checkpoint.py`](../../harness/checkpoint.py). Checkpoints are self-contained, create-only, atomically published, and structurally valid without the original Body-state file; this slice does not resume execution.

For fresh-process admission from one exact checkpoint, use [`agents/resume.md`](../../agents/resume.md) and [`harness/resume.py`]. Restart admission binds checkpoint identity, revalidates referenced artifacts, rejects a completed current step, materializes the exact nested Body snapshot create-only, and returns READY or BLOCKED without executing an action. BLOCKED is not execution authority, and neither status provides exactly-once side-effect guarantees.

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
