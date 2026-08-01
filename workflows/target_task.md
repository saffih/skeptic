# STT v25 product and lifecycle contract

STT is a repository-native, provider-neutral task execution protocol invoked
by a mission whose first meaningful token is exactly `STT:` followed by a
nonblank suffix:

```text
STT: <mission>
```

The active host remains the active host. Codex uses the Codex adapter and
Claude Code uses the Claude Code adapter. Neither host launches the other.
The target is the current Git repository, resolved from the current session.
The repository-native public CLI is `scripts/stt.py`. Task state defaults to
`<repo>/.stt/tasks`; `STT_TASKS_ROOT` may explicitly override that location.

## Architecture

The protocol is:

```text
Lead
  -> compact reference-only intent
  -> deterministic Boundary
  -> validated immutable request
  -> Planner / Reviewer / Worker / Command
  -> complete file-backed result and evidence
  -> deterministic Boundary
  -> validate, accept or reject
  -> append-only ledger
  -> compact receipt
  -> Lead
```

Planner, Reviewer, and Worker are semantic model roles. Command is
deterministic local execution, not a model role. Boundary is the mandatory
protocol firewall: every substantive ingress and egress passes through it.
The durable Lead carries references and compact receipts, not substantive
bodies. `ledger.jsonl` is the sole lifecycle authority, and state is derived
from that ledger by one authoritative reducer.

The supported command surface is:

```text
stt start --repo <path> [--include-ignored <path> ...] [--allow-unconfined-candidate-execution] --mission-file <path>
stt run --task-root <path>
stt status --task-root <path>
stt reconcile --task-root <path>
stt retry --task-root <path>
stt replan --task-root <path>
stt stop --task-root <path>
stt resume --task-root <path>
stt diagnose --task-root <path>
stt restore --task-root <path> --destination <empty-directory>
```

## Atomic acceptance

Provider output is staged first. Boundary then validates the result, provider
evidence, operation binding, schemas, paths, file types, sizes, hashes,
authority, and referenced artifacts. Malformed output does not consume the
pending operation. Accepted output becomes protocol truth through one
authoritative acceptance transition. Rejected output remains diagnosable and
retryable. Manual ledger editing is never a recovery mechanism.

## Recovery

The supported recovery actions are `retry`, `replan`, `stop`, `resume`, and
`diagnose`. Accepted operations cannot be replayed. Stopped or failed tasks
remain inspectable, and an unknown admitted operation must be reconciled
before any possible redispatch.

## Delivery kinds

STT has two explicit delivery kinds.

### Inspect

Inspect is for repository inspection, diagnosis, inventory, review, cleanup
groundwork, or reporting. A Task whose Plan performs inspection is read-only with respect to the
target repository, do not require source cutover, do not require
installed-tree equality, and do not require source-changing Worker steps.
They finish with evidence-backed reporting and final review, then terminate
as `COMPLETE`.

### Workspace change

Workspace-change tasks perform bounded source modifications. They operate in
disposable filesystem capsules while the authoritative source remains
read-only during semantic execution. They validate a frozen candidate, run
final unchanged reviews, perform one deterministic reviewed cutover, and
terminate as `COMPLETE`. Freeze and review the final candidate before one deterministic cutover.

Linked Git worktrees are not STT capsules. No commit, stage, checkout, reset,
merge, rebase, push, PR, or publication is part of STT authority.

## Boundary responsibilities

Boundary verifies mechanically:

- pending operation identity and immutable request binding;
- provider, role, and exact schema;
- artifact containment, regular-file status, and required symlink and
  hard-link rejection;
- size, SHA-256, provider evidence, authority, and declared outputs;
- Plan schema and review subject identity;
- review count and unchanged binding;
- duplicate and replay protection;
- legal ledger transitions and compact receipt constraints.

Boundary does not decide whether a Plan is good or whether a mission is
substantively satisfied. Planner and Reviewer make those semantic judgments;
Boundary verifies their protocol and evidence bindings.

## Sandbox contract

Sandbox behavior is authoritative; backend names are diagnostic metadata only.
When `sandbox_required` is requested, the result is exactly one of:

```text
SUCCEEDED
SANDBOX_UNAVAILABLE
SANDBOX_SETUP_FAILED
COMMAND_FAILED
TIMED_OUT
TERMINATION_UNKNOWN
```

Supported backend names currently include `linux-unshare` and
`macos-seatbelt`; future supported backends may be added. Sandbox setup
failure is distinct from a contained command failure. Readiness must be
reached before a failure can be classified as `COMMAND_FAILED`. Sandbox
failure never silently falls back to unconfined execution. Unsupported hosts
fail with `HOST_CAPABILITY_UNAVAILABLE` before launching the admitted
command.

`owner_risk_accepted` is explicitly unconfined. It must never be described as
sandboxed, contained, network-denied, or external-side-effect safe, and it
proves no isolation.

## Qualification truthfulness

Successful containment requires evidence that the command ran inside the
selected sandbox, the authoritative host path was unavailable, network access
was denied, the candidate and scratch storage were readable and writable,
the selected backend matched capability selection, the contained-success
marker was printed, and the exit code was accepted. A blocked backend is a
fail-closed result, not proof of successful containment. Provider identity,
hidden host context, and live semantic execution remain `UNKNOWN` unless
directly evidenced.

## Recursive Tasks

The executed unit is one `Task`, whether it is the root invocation or a
descendant. A Task owns its mission, input checkpoint, authority, sealed Plan,
append-only ledger, execution artifacts, final validation, and immutable
terminal receipt. A Plan may contain this exact primitive step:

```json
{"id":"inspect-before-cleanup","kind":"task","mission":"Inspect local state and return a reviewed manifest."}
```

The step has exactly `id`, `kind`, and `mission`. The child Planner decides
the sealed Plan, including whether it performs inspection or workspace change.
Planner output cannot select authority, identity, child IDs, or an outcome.
Every Task uses the same lifecycle and successful terminal outcome: `COMPLETE`.
Child Tasks use the same lifecycle and limits as the root; `max_task_depth: 4`
and `max_plan_steps` are sufficient for the MVP.

A child identity is deterministic from the parent Task ID, sealed parent Plan
SHA-256, parent step ID, and parent checkpoint SHA-256. The child records an
immutable binding in `task.json` and the parent ledger records only these two
Task-specific events:

- `TASK_BOUND`: the parent step, child Task ID/root, sealed Plan hash, and
  checkpoint hash.
- `TASK_RESULT_ACCEPTED`: the verified terminal receipt and imported generic
  result, plus a new parent checkpoint when the reviewed child checkpoint
  advances the parent.

Execution is depth-first. Parent locks are released while the deepest child
runs. Every child returns one reviewed immutable result with a checkpoint and
artifact references; read-only Plans preserve the input checkpoint and
changing Plans return the validated resulting checkpoint. Only the root Task
may perform the final deterministic cutover. A child is consumable only after
the reusable terminal verifier confirms its identity, binding, ledger chain,
sealed Plan, three unchanged Plan reviews, frozen subject, three unchanged
final reviews, terminal receipt, and the exact frozen result artifacts.

Inspect execution is a closed read-only capability. It records immutable
evidence and freezes its report before final reviews; it does not invoke the
generic command or candidate sandbox path and terminates as
`COMPLETE`.
