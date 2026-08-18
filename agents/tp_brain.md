# TP Brain Agent

TP Brain is defined by `workflows/task_prompt.md`, which is the canonical source
for the Task Prompt workflow. An active TP run supplies the exact snapshotted
`tp_authority_ref` that governs that run; read that reference and do not
substitute a mutable checkout copy.

This file is a routing stub and carries no authority of its own. It exists only
so that a reference to `agents/tp_brain.md` resolves to the owning TP authority.

TP Brain is Task-Prompt-specific. It is not a generic planning role, it does not
replace `agents/planner.md` for non-TP work, and no other workflow acquires it by
reference.
