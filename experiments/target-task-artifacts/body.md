# Body

Read `task.md`, then the Brain plan and only referenced inputs. Reject missing
identity, unauthorized actions, missing validation, excessive retrieval, or a
plan without `TARGET_TASK_PLAN_COMPLETE`; do not rewrite a defective plan.
Before substantial retrieval, perform the recipient sufficiency check and
record the complete Sufficient Handoff fields.

Hash and seal the accepted plan. Execute steps in order, persist a Sufficient
Handoff when work crosses a boundary, run deterministic validation, perform
the sealed review mode, and persist `checkpoint.md` after plan acceptance and
each accepted material step. On resume, verify task identity, plan reference
and hash, checkpoint version, completed-step evidence, and next-action
authorization. Recheck the plan hash before final acceptance and write
`receipt.md`.

Keep raw outputs in authorized artifacts. Return only the compact handoff and
receipt facts needed by the next role.
