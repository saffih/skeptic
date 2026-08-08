# Task Prompt builder alias routing decision

## Decision

`TP:` is now a direct Task Prompt execution invocation, bound in `AGENTS.md`
and `workflows/task_prompt.md`: it activates `workflows/task_prompt.md`
directly, and the top-level invocation acts as the Lead. It is no longer a
builder alias.

The three remaining aliases — `Create task prompt for:`, `Create a task
prompt for:`, and `Task prompt for:` — are still builder invocations. The
builder layer, `workflows/task_prompt_builder.md`, creates an unexecuted Task
Prompt; the worker/execution layer follows `workflows/task_prompt.md`. Those
aliases remain at the builder layer because they request prompt construction.
Routing them directly to the worker layer would turn that request into
task-execution authority.

## Layer 1 contract

For each remaining alias, the initiating agent must:

1. read `workflows/task_prompt_builder.md` before interpreting or responding;
2. process the complete user request according to that file;
3. stop visibly with `TASK_PROMPT_BUILDER_UNAVAILABLE` if the file cannot be read;
4. never route the alias directly to `workflows/task_prompt.md`.

## Verification boundary

`tests/test_task_prompt_builder_routing.py` proves that the builder contains
the three remaining aliases and not `TP:`, that the builder preserves its
create-but-do-not-execute boundary, that `AGENTS.md` binds `TP:` to direct
Task Prompt execution as Lead, and that `TP:` appears in exactly one binding
across `AGENTS.md` and the builder — never simultaneously a builder alias and
an execution trigger. It is a static contract test; it does not prove that a
model follows the contract.

Manual weak-agent verification remains responsible for confirming that Luna
Medium actually reads the builder before interpreting the full aliased request
and returns a Task Prompt without executing it. Missing-file behavior also
requires a controlled environment in which the builder is genuinely unreadable;
it must not be inferred from the static test.
