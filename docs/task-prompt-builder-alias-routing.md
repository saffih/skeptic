# Task Prompt builder alias routing decision

## Decision

`TP:` and the three equivalent aliases are builder invocations. The builder
layer, `agents/task-prompt-builder.md`, creates an unexecuted Task Prompt; the
worker/execution layer follows `agents/task-prompt.md`. The aliases remain at the
builder layer because they request prompt construction. Routing them directly to
the worker layer would turn that request into task-execution authority.

## Layer 1 contract

For every alias, the initiating agent must:

1. read `agents/task-prompt-builder.md` before interpreting or responding;
2. process the complete user request according to that file;
3. stop visibly with `TASK_PROMPT_BUILDER_UNAVAILABLE` if the file cannot be read;
4. never route the alias directly to `agents/task-prompt.md`.

## Verification boundary

`tests/test_task_prompt_builder_routing.py` proves that the entry map contains
all aliases, routes them to the builder, requires the read, fails closed with the
named status, rejects direct worker routing, and preserves the builder's
create-but-do-not-execute boundary. It is a static contract test; it does not
prove that a model follows the contract.

Manual weak-agent verification remains responsible for confirming that Luna
Medium actually reads the builder before interpreting the full aliased request
and returns a Task Prompt without executing it. Missing-file behavior also
requires a controlled environment in which the builder is genuinely unreadable;
it must not be inferred from the static test.
