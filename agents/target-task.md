# Target Task execution and context-protection protocol

This is the canonical, provider-neutral contract for one Target Task. `TT:`
is the compact entry trigger. `OTP:` remains a compatibility trigger and
activates this same protocol through `agents/otp-protocol.md`.

## Activation

Recognize only a leading `TT:` or `OTP:` token, case-insensitively, after
surrounding blank or whitespace-only lines. Remove the token, its optional
colon, and following whitespace; the remainder is the Target Task. A plain
task does not activate this protocol. If the canonical file is unavailable,
stop with `TARGET_TASK_PROTOCOL_UNAVAILABLE`.

Record exactly one trigger form: `TT:`, `OTP:`, or `OTP:+TT:`. The redundant
`OTP:` followed by a `TT:` line activates once and uses the `TT:` payload.

## Portable core lifecycle

The lifecycle is provider-neutral and has two functional roles:

* **Body** coordinates, accepts, seals, executes, validates, reviews, accepts,
  and records the receipt.
* **Brain** plans only. It produces one Acceptance Plan; it does not execute,
  browse broadly, or become the task owner.

The same runtime may perform both roles sequentially when no delegation is
used. A delegated role follows the Agent Completion Envelope and reports
requested and observed routing separately.

1. Parse the Target Task and record identity, authority, scope, prohibitions,
   outputs, validation, and success criteria.
2. Brain performs exactly one planning cycle. Replan at most once after a
   material Body rejection; a second rejection returns `TARGET_TASK_BLOCKED`.
3. Body checks identity, required sections, authorization, executability,
   retrieval boundaries, and handoff requirements. It does not rewrite the
   plan. On acceptance it records a stable plan hash and seals the plan.
4. Body executes sealed steps in order, preferring deterministic tools.
5. Deterministic validation runs before judgment review.
6. Execute the one review mode named by the sealed plan:
   `DETERMINISTIC_ONLY`, `SELF_REVIEW`, or `RUNSKEPTIC_REVIEW`.
7. Recheck the plan hash, compare every success criterion, and return
   `TARGET_TASK_ACCEPTED`, `TARGET_TASK_REJECTED`, or `TARGET_TASK_BLOCKED`.

## Context protection

Context is a constrained working set, not an implicit repository mirror.

* Start with the task file and its explicitly authoritative inputs.
* Retrieve progressively: metadata and headings first, the smallest relevant
  section next, and full content only when a named decision requires it.
* Do not perform broad recursive discovery, duplicate authoritative content,
  or carry raw logs, full transcripts, or rejected alternatives into the next
  role.
* Replace substantial handoff content with an authorized path, byte identity,
  status, and the next decision. A summary never replaces its source.
* When context pressure rises, narrow retrieval and persist a sufficient
  handoff; do not silently drop a required source or invent a fact.
* Boundary processing limits explicit information flow but does not prove
  fresh runtime isolation or substantive correctness. Record one of
  `FRESH_CONTEXT_CONFIRMED`, `PARENT_CONTEXT_INHERITED`, or
  `CONTEXT_ISOLATION_UNKNOWN`.

## Sufficient Handoff

Every cross-role or cross-session handoff contains only the minimum durable
state needed to continue:

```text
task_id: <stable identity>
source_refs: <authoritative paths and hashes>
candidate_identity: <hash or explicit NONE>
completed_steps: <ids and statuses>
open_findings: <ids or NONE>
next_action: <one bounded action>
constraints: <active prohibitions and budgets>
context_status: FRESH_CONTEXT_CONFIRMED | PARENT_CONTEXT_INHERITED | CONTEXT_ISOLATION_UNKNOWN
```

The receiver re-reads authoritative sources as needed. It must reject a
handoff with missing identity, source provenance, next action, or constraints;
it must not treat a prose summary as permission or evidence.

## Receipt

Report trigger and Target Task, requested and observed routing, planning cycle
count, sealed plan identity, retrieval and handoff status, execution outputs,
deterministic validation, review result, terminal status, blockers, candidate
identity, and protected repository-state facts. Unknown runtime facts remain
`UNKNOWN`.

This core intentionally owns no repository state or task workspace. The
repository adapter and templates below provide examples without changing the
portable contract.
