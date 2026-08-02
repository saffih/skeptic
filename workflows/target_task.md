# STT v25 product and lifecycle contract

STT is a repository-native, provider-neutral task protocol. It is invoked only
when the first meaningful token is exactly `STT:` and the suffix is nonblank.
The active host remains the active host: Codex uses `STT_PROVIDER=codex` and
Claude Code uses `STT_PROVIDER=claude-code`; neither launches the other. The
target is the current Git repository. The public CLI is `scripts/stt.py` and
Task state defaults to `<repo>/.stt/tasks`, with `STT_TASKS_ROOT` as the only
state-root override.

## Accepted MVP architecture

STT uses one sequential shared workspace and one Task abstraction for roots,
children, and deeper descendants. The protocol is:

```text
Lead
  -> compact reference-only intent
  -> deterministic Boundary
  -> immutable admitted request
  -> Planner / Reviewer / Worker / contained Command
  -> frozen result and provider evidence
  -> deterministic Boundary
  -> append-only JSONL ledger
  -> compact receipt
  -> Lead
```

Planner, Reviewer, and Worker are semantic roles. Command is deterministic
local execution. Boundary is mandatory for every substantive ingress and
egress. `ledger.jsonl` is the sole lifecycle authority; Runner's ledger
projection is the one status derivation implementation. The durable Lead
carries references and compact receipts, never substantive bodies.

The supported command surface is:

```text
stt start --repo <path> --mission-file <path> [--include-ignored <path> ...]
stt run --task-root <path>
stt status --task-root <path>
stt reconcile --task-root <path>
stt retry --task-root <path>
stt replan --task-root <path>
stt stop --task-root <path>
stt resume --task-root <path>
stt diagnose --task-root <path>
stt restore --task-root <path> --destination <path>  # always unsupported
```

The compatibility flag `--allow-unconfined-candidate-execution` is rejected
with `UNCONFINED_SHARED_WORKSPACE_EXECUTION_UNSUPPORTED` before Task state is
created. Unconfined command execution is unsupported.

## Atomic bootstrap

A Task is assembled under a private sibling
`.<task-id>.creating-<uuid>` directory. Task JSON, ledger, mission, routing,
persisted baseline, inventory, toolchain, methodology, and the initial Planner
admission must all validate there. Only then is the directory atomically
renamed to `<task-id>` and the state-root directory fsynced. A failed bootstrap
removes only its private creation directory. The final Task root is never
published partially, and the persisted baseline in `task.json` is the baseline
used by later admissions.

## Semantic operation transitions

Each successful semantic operation has one precise sequence:

```text
OPERATION_ADMITTED
  -> validate and freeze provider output
  -> one role-effect event bound to operation_id
  -> OPERATION_ACCEPTED bound to that exact effect
  -> deterministic advancement admits the successor, if any
```

The role-effect events are:

- `PLAN_CANDIDATE_RECORDED`
- `PLAN_REVIEW_RECORDED`
- `FINAL_REVIEW_RECORDED`
- `EVIDENCE_BUNDLE_EXTENDED`
- `OPERATION_RESULT`

Every role effect binds exact ArtifactRefs for the admitted request, frozen
semantic result, and frozen provider evidence, plus its role-specific fields.
Provider-authored result, evidence, Plan, finding map, review receipt, and
review findings are staging files only. Boundary reads bounded owned regular
files and publishes unique trusted copies under `accepted/<operation-id>/`.
Only the trusted copies enter effects and accepted history.

A role effect without `OPERATION_ACCEPTED` is a recoverable crash window. The
next run verifies the effect's frozen references, appends the one missing
acceptance, and does not reread staging or repeat the role effect. An operation
is consumed only by `OPERATION_ACCEPTED`, `OPERATION_SUPERSEDED`, or a terminal
or nonresumable-block event explicitly bound to that operation.

Role processors never create successors. One deterministic advancement
function derives the next action from accepted ledger state:

- accepted Plan candidate -> Plan review;
- accepted clean review below three passes -> another independent review;
- three accepted unchanged Plan reviews -> unique Plan seal attempt;
- accepted `ACTION` review -> supersede the candidate and request repair;
- accepted evidence bundle -> same role and purpose with accumulated bundles;
- accepted Worker result -> next sealed step;
- accepted final review below three passes -> next final review;
- three accepted unchanged final reviews -> verify and complete.

Consequently, a crash after acceptance and before successor admission is
idempotent. Accepted semantic operations are never redispatched.

`OPERATION_UNKNOWN` is separate: every provider observation is frozen
independently, no semantic result is redispatched, and later conclusive staging
evidence may be reconciled. Malformed output remains a bounded `STTError` and
does not consume the admission.

## Worker mutation intent and direct delta

A Worker edits a sparse capsule. Capsule admission freezes the pre-Worker
identity of every admitted path, including the write baseline. Delta derivation
compares that frozen baseline with the final capsule, never with a mutable live
workspace. Every delta entry contains exact `before` and `after` identities.

After result validation and delta derivation, but before the first workspace
mutation, STT appends `WORKER_DELTA_INTENT_RECORDED` with the operation, step,
delta, frozen Worker result, frozen provider evidence, and capsule admission.
Normal order is:

```text
WORKER_DELTA_INTENT_RECORDED
  -> apply direct scoped delta
  -> declared validations
  -> OPERATION_RESULT
  -> OPERATION_ACCEPTED
```

An intent with no Worker result, terminal event, or nonresumable block is never
rederived or reapplied after restart. It becomes honest `partial_or_unknown`
evidence followed by `TASK_BLOCKED_UNKNOWN`; the only next action is
`DIAGNOSE`. This classification is permitted even if interruption happened
before the first actual write. STT performs no filesystem inference and no
automatic reconciliation.

Before applying any item, every current workspace target must still equal its
declared `before` identity. Creates and replacements use a temporary file in
the target directory, exact-byte copy, file fsync, admitted mode, atomic
replacement, and directory fsync. Directory deletion is leaf-first with
`rmdir()`. There is no recursive delete, whole-delta transaction, or rollback;
a later failure honestly reports possible partial application.

## Plan protocol and review information

Only Plan schema version 2 is accepted. Every Plan declares
`delivery_kind`, typed mandatory done clauses, bounded steps, exact scopes, and
bound commands. Version 1 has no compatibility path.

Plan review requests bind immutable refs for mission, candidate Plan, finding
map, baseline, inventory, toolchain, methodology, prior findings, and evidence
bundles. The request hash covers all of them. A Plan is sealed only after three
independent, unchanged, source-bound qualifying reviews.

`delivery_kind: inspect` rejects change steps. It permits read-only validation,
inspect, and Task steps. Read-only authority propagates in the canonical child
binding; every descendant must also seal an inspect Plan, so a descendant
change is rejected before Worker admission or workspace mutation.

The final frozen subject has exactly:

```json
{
  "schema_version": 1,
  "mission": {"ref": "...", "sha256": "...", "size": 1},
  "sealed_plan": {"ref": "...", "sha256": "...", "size": 1},
  "plan_seal": {"ref": "...", "sha256": "...", "size": 1},
  "evidence": {"ref": "...", "sha256": "...", "size": 1},
  "result": {"ref": "...", "sha256": "...", "size": 1},
  "accepted_task_results": [],
  "inspection_results": [],
  "done_proof": []
}
```

It is frozen before final reviews and therefore makes no claim that those
reviews already exist. Final reviewers review this exact frozen evidence
subject. Completion requires three independent unchanged final passes with
every reviewer-claim done clause required by the sealed Plan (including
`report_bound_to_baseline` for inspect delivery).

## Evidence selectors and control-state privacy

`NEEDS_EVIDENCE` has an exact schema and bounded rounds, refs, and bytes.
`workspace_path` is Planner-only and must be canonical relative, contained,
owned, uniquely linked, regular, bounded, and free of symlink parents. A path
with `.git` or `.stt` at any depth, a nested repository/submodule, or an escape
is rejected before copying. Reviewers cannot request mutable workspace paths
after a subject is frozen.

`exported_task_artifact` requires one exact ArtifactRef already disclosed in
the same request. Its hash and size are reverified. Ledger, `task.json`,
routing internals, semantic admissions and requests, mutable semantic results,
and raw provider-evidence staging are not exportable. Evidence bytes are
republished as trusted mode-0600 bundle artifacts; metadata is not copied.

Every committed ledger event references an existing canonical Task-relative,
owned, uniquely linked, owner-controlled regular JSON file with exact size and
SHA-256. Missing, symlinked, malformed, or non-JSON payloads are corruption.
One active event allowlist is authoritative. No ledger event may follow a
terminal receipt or `TASK_BLOCKED_UNKNOWN`.

## Nested repositories, capsules, and inspection

Bootstrap and later boundary checks mechanically discover descendant `.git`
directories and gitfile markers without descending into them. `.git` and
`.stt` are pruned from all walks. A Worker scope is rejected if it equals,
contains, or is contained by a nested repository root. The same rule covers
Plan scopes, capsule materialization, delta derivation/application, evidence,
and inspection. Command working directories cannot enter a nested repository;
root-scoped contained commands see nested repositories overlaid inaccessible.

Sparse capsules enforce single-file bytes, read-scope bytes, capsule bytes,
capsule entries, changed paths, task-state bytes, and free-space reserve.
Unicode NFC and case-fold collisions are rejected across the declared write
scope. Declared files and required ancestors remain writable in the capsule;
unrelated materialized objects are read-only. Capsule writability is not
authority to import an undeclared delta.

`repository_inventory` resolves only its declared workspace scope. It emits
bounded path/type/size metadata and excludes Git control, STT control, nested
repository contents, and sibling Tasks. `git_state` requires scope `.` and
runs only fixed read-only Git observations with optional locks disabled and
untracked Task state omitted. Inspection and transition reports use unique
attempt paths; an orphan published before its ledger event never becomes
authority and never strands restart.

## Pause, retry, replan, and blocked states

`retry` reuses the same pending operation and attempt; it creates no concurrent
admission. `replan` first appends `OPERATION_SUPERSEDED` for the exact rejected
Planner operation, then admits its replacement. A crash between those events
is repaired deterministically.

`TASK_STOPPED` and `TASK_RESUMED` are nonterminal ledger facts. Stop is
idempotent, a stopped Task dispatches nothing, and a pending operation remains
pending. Resume requires an unmatched stop and records no workspace work. For
an active root, resume targets the deepest stopped descendant. Terminal and
nonresumable-blocked Tasks cannot resume.

`TASK_BLOCKED_UNKNOWN` is automatic, nonresumable state:

```json
{"status":"BLOCKED_UNKNOWN","resumable":false,"next_action":"DIAGNOSE"}
```

It never advertises reconciliation and closes the ledger. `OPERATION_UNKNOWN`
remains the only reconcilable unknown-provider state.

## Completion verifier

The reusable verifier runs before `COMPLETE` and again for every external or
parent verification. It proves exact step completion with no duplicates; no
pending operation, unresolved Worker intent, unreconciled unknown, active
rejected/superseded operation, or active child; Plan/review/seal agreement;
subject and freeze-receipt agreement; exact reviewed terminal result; all
result, Worker, validation, inspection, and child refs; frozen workspace path
identities; child mission hash; and equality between canonical and duplicated
parent-binding fields.

## Command sandbox truth

Dynamic commands require `candidate_dynamic_execution` with value exactly
`sandbox_required`.
There is no unconfined fallback.

Linux is the only eligible MVP backend. Before `STT_SANDBOX_READY`, it creates
private user, mount, network, and PID namespaces; makes mount propagation
private; uses ordinary read-only bind mounts; mounts the workspace read-only;
hides workspace `.git`, `.stt`, and nested repositories; exposes only writable tmpfs
scratch; makes the chroot root read-only; chroots; clears
ambient, bounding, permitted, effective, and inheritable capabilities; sets
`no_new_privs`; and installs a seccomp filter denying mount, remount,
namespace-regain, and handle-based filesystem syscalls. `/proc` is not mounted.
Writable tmpfs bytes, process count, address space, open files, output-file
size, CPU time, wall time, and captured logs are bounded before readiness.
The child environment sets `GIT_OPTIONAL_LOCKS=0` and
`PYTHONDONTWRITEBYTECODE=1`. Contained-success qualification additionally
probes remount, capability, nested-namespace, alternate-path, network,
workspace-write, `.git`, `.stt`, nested-repository, and host-path denial.

macOS containment is disabled for this MVP because equivalent seatbelt
readiness and adversarial qualification have not been demonstrated. macOS
returns `HOST_CAPABILITY_UNAVAILABLE` before command launch. A Linux setup that
cannot reach readiness returns fail-closed setup evidence. A blocked backend
is not containment success.

Command cwd rejects escapes, symlink components, control paths, and nested
repositories. Absolute staging log paths are internal only; before any ledger
publication, log bytes become verified Task-relative ArtifactRefs.

## Enforced limits

The runtime mechanically enforces Plan candidates and steps, Plan reviews,
final reviews, evidence rounds/refs/bytes, scope entries, read bytes,
single-file bytes, capsule bytes/entries, inventory entries, changed paths,
commands, request/result/log sizes, operation timeout, Task depth, Task-state
bytes, command scratch/process/address-space resources, and free-space reserve.
Preflightable failures occur before workspace mutation.

## Recursive Tasks and explicit limitations

A Task step has exactly `id`, `kind`, and mission. Child identity is
deterministic from parent Task ID, sealed parent Plan hash, step ID, and bounded
workspace observation. Bootstrap is atomic, execution is depth-first, and the
parent accepts only a child result that passes the reusable terminal verifier.
Root, child, and grandchild all use the same lifecycle and shared workspace.

STT does not provide checkpoints. This MVP also provides no snapshots, preservation
copies, cutover, rollback, restoration, operation replay, whole-Task
transactions, concurrent Tasks in one workspace, database, or generalized
workflow/filesystem framework. External filesystem mutation and concurrent
Task execution remain unsupported. Live provider hidden context and live
Codex/Claude containment remain `UNKNOWN` unless directly evidenced.
