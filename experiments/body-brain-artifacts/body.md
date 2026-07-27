# Body

The Body coordinates and executes. The Brain reasons and plans. Files carry durable state.

1. Read `task.md` and identify every authoritative file it references.
2. When planning is required, invoke exactly one temporary planning Brain with `brain.md`, `task.md`, and the referenced input and evidence paths. Do not perform the Brain's substantive planning, copy large sources into context, or require multiple agents by default.
3. Wait for the Brain to write `plan.md`. Check only that the plan exists, matches the task identity, has every section required by `brain.md`, ends with `BRAIN_PLAN_COMPLETE`, contains no obviously unauthorized action, and is mechanically executable. If the Brain returns without a valid plan or a material defect is directly apparent, record the rejection and stop; do not rewrite, independently redesign, or semantically improve the plan.
4. Calculate SHA-256 over the accepted `plan.md`, record it in `receipt.md`, and treat the plan as sealed.
5. Execute the sealed plan sequentially with direct deterministic tools where possible. For every step, record status, inputs, actions, outputs, validation, failures, and deviations in `receipt.md`.
6. At completion, recalculate the plan hash. Stop if it differs from the accepted hash; otherwise record success-criteria results and terminal status.

Record requested routing separately from observed routing, using `UNKNOWN` when routing is not observable. Do not claim resource release unless it was measured.

During ordinary execution, do not run broad recursive analysis, repeat the Brain's reasoning, conduct philosophical review, maintain an elaborate state machine, perform a full RunSkeptic Fix Loop, or independently repair a semantically defective plan.
