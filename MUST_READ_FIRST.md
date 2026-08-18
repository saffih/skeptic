# MUST READ FIRST

Repository-wide orientation. Read this before routing or executing repository
work. It is deliberately short: it states only what applies to every task here,
and it contains no workflow's procedure.

## Context

- Model context is scarce working capacity, not storage. Material belongs in an
  active context because it contributes to that context's current obligation,
  not because it exists or was present upstream.
- Keep substantial or reusable state file-backed and pass receiver-resolvable
  references across invocation boundaries instead of copying bodies through a
  parent.
- Substantive semantic work — understanding, discovery, decomposition,
  implementation, review — should run in fresh bounded invocations rather than
  accumulate in the session controlling the work.
- A bounded semantic invocation may independently retrieve any source already
  authorized for its obligation. A small starting reference set is an
  economical start, not an evidence boundary.
- Report hidden runtime facts — actual model, routing, isolation, inherited
  context — as `UNKNOWN` unless they are directly observable.

## Naming

A workflow or role name used by one system does not imply a shared contract
  with a same-named role in another system. Bind every role to the authority file
  that owns it, and never infer one system's contract from another's vocabulary.

## Triggers

- `TP:` routes to `workflows/task_prompt.md`, which is the canonical source for
  Task Prompt authority. Before any TP semantic invocation, the host binds the
  exact authority snapshot required by that workflow; active TP roles use the
  run's `tp_authority_ref`.
- `RunSkeptic` routes to `skeptic.md`, which owns Skeptic behavior and
  receipts.
- STT is a separate system with its own runtime and authorities. It is not
  implicitly governed by Task Prompt roles.

Everything else routes through `AGENTS.md`.
