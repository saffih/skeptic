# Slice 3B — Architecture Map and Cross-File Contract Matrix

Neutral evidence packet, part 2 of 3. Descriptive facts drawn from the
contract files at HEAD `369c841` (blob/SHA identities in
`recovery-report.md`). No diagnosis and no recommended disposition appear
in this file.

## Part 1 — Runtime discovery and load order

```text
(any agent, first contact)
AGENTS.md  (263 bytes)
  ├─ "Lead agents should read: agents/lead-agent-prompt.md"
  └─ "When RunSkeptic ... is required, use the current skeptic.md
      as the source of truth."

agents/lead-agent-prompt.md  (Lead role)
  ├─ for serious multi-phase / terminal work → read and apply
  │   agents/task-prompt.md   (explicit: "read and apply the current
  │   agents/task-prompt.md"; also listed in Core job flow)
  └─ when Skeptic is invoked → read current skeptic.md (never memory)

skeptic.md  (RunSkeptic framework)
  └─ when the artifact under review is a Task Prompt → read
      agents/task-prompt.md as a REQUIRED companion
      ("If the required companion is unavailable, do not claim
      task-level PASS.")

plans/   — decisions and history; "never runtime context"
tests/   — contract regression (85 tests at baseline)
```

Observed properties of the discovery chain (verbatim-grounded):

- D1. `AGENTS.md` is the sole entry pointer. Its operative sentence is
  "Lead agents **should** read `agents/lead-agent-prompt.md`". No file
  defines when an agent must classify itself as a Lead agent; an agent
  handed a concrete task (rather than asked to construct prompts) receives
  no mandatory trigger to load the Lead contract.
- D2. `skeptic.md` has a strong mandatory load condition, but it triggers
  only on explicit invocation ("RunSkeptic" or aliases).
- D3. `agents/task-prompt.md` has two mandatory load conditions: when the
  Lead constructs/executes serious work (lead-agent-prompt.md), and when a
  Task Prompt is under Skeptic review (skeptic.md §Prompt Review Levels).
  Both conditions presuppose that the Lead contract or Skeptic was already
  loaded — the chain roots in D1's "should".
- D4. The consolidation plan (Track 1) already schedules an "Entry-points
  section in AGENTS.md" and doctrine dedup as Slice 3, i.e., the repository
  has itself recorded that the entry pointer is thinner than the file set
  it fronts.

## Part 2 — Execution ownership and artifact/control flow

```text
User objective
  → Lead (agents/lead-agent-prompt.md): intent → bounded prompt(s)
      → Skeptic Prompt Gate (skeptic.md; Level 1 or Level 2)
          → gate receipt (lead-agent-prompt.md §Gate receipt)
  → Task Prompt (agents/task-prompt.md) for serious terminal work
      → phases with Dispatch Tickets → Workers / Checkers / Judges
          → Agent Receipts (evidence, not authority)
          → Checker verifies material deterministic claims
      → persisted checkpoints (durable artifacts before dependent phases)
      → system verification → RunSkeptic (skeptic.md)
      → integration/publication when DONE requires
      → Task Closure Receipt (only terminal proof)
```

Ownership boundaries as written:

- The Lead owns objective, authority, routing, evidence custody,
  promotion, closure. Delegation transfers bounded work only.
- Workers return receipts; receipts are evidence, not authority; a Checker
  (deterministic commands) must verify material claims before promotion.
- Judges are used only when independence materially affects the decision;
  clean-room claims require genuinely separate protected contexts
  (lead-agent-prompt.md §Genuine independence; task-prompt.md §10).
- Durability rule (task-prompt.md §9): "Every expensive or decision-critical
  phase must persist an authoritative artifact before dependent work
  begins. Temporary chat, worker memory, transient context, and unverified
  summaries are not durable evidence." The same doctrine appears in
  lead-agent-prompt.md §Context protection ("Authoritative evidence must
  not exist only in transient context, temporary paths, worker memory, or
  chat prose").
- Closure rule (task-prompt.md §14): the Task Closure Receipt is the only
  terminal proof; `Overall DONE: yes` requires every terminal condition
  verified. The routing-clarification slice record additionally documents
  (post-publication correction) that closure receipts must carry concrete
  observed values, never forward references.

## Cross-file contract matrix

| File | Reader | Authority (scope) | Mandatory load condition | Delegation interface | Receipt interface | Fail-closed behavior | Duplicate/conflicting rules |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `AGENTS.md` | every agent, first read | entry routing only | none (it IS the entry) | none | none | none defined | none (but see D1: "should", not "must") |
| `skeptic.md` | any agent asked to review | RunSkeptic behavior, output categories | explicit invocation (RunSkeptic/aliases); companion `task-prompt.md` required for Task Prompt review | none (review-only) | RunSkeptic Receipt (13 fields) | "If the source under review is unavailable, say so and do not claim compliance"; no task-level PASS without required companion; CONFLICT paths throughout | duplicates: proportionality/effort doctrine overlaps CH:EV + lead-prompt §Proportional execution |
| `agents/lead-agent-prompt.md` | the Lead agent | Lead role, prompt architecture, prompt gating | `AGENTS.md` "should read" only (D1) | Bounded dispatch ticket — 9 fields (Role, Task/question, Source of truth, Scope, Allowed, Forbidden, Required evidence, Stop conditions, Return format); micro-ticket exception | Default worker receipt — 11 fields (Task, Scope, Files read, Commands run, Evidence found, Changed files, Verification, Blockers, Risk, Recommended next action, Confidence); Gate receipt — 19 fields | `MODEL_ROUTING_UNRESOLVED`, `AUTHORITY_CONFLICT`, stop-on-unexpected-mutation, gate blocks on unresolved ACTION/DECOMPOSE/CONFLICT | ticket/receipt schemas differ from `task-prompt.md` (below); proportional-execution & context-protection doctrine restated in both files (consolidation plan Track 1 flags this) |
| `agents/task-prompt.md` | the Lead when executing serious work | Task Prompt construction, execution control, closure | Lead constructing serious/terminal work; Skeptic reviewing a Task Prompt | Dispatch Ticket — 11 fields (adds "Budget / context / output limit", "Acceptance and disconfirming checks", "Required evidence and durable destination" vs the 9-field form) | Agent Receipt — 11 fields (adds "Budget / context result", "Verification and disconfirming checks"); Task Closure Receipt (11 items) | `MODEL_ROUTING_UNRESOLVED`; no dependent phase on unpersisted output; unexpected mutation stop; CONFLICT on blocked publication | two ticket schemas and two receipt schemas coexist (9-field vs 11-field; worker receipt vs Agent Receipt); doctrine restated across three runtime files |
| `plans/` | humans, planning agents | history/decisions only | never runtime context | n/a | n/a | n/a | consolidation plan is the only slice-numbering source of truth |
| `tests/` | CI / verification phases | contract regression | test execution | n/a | n/a | red suite blocks | tests freeze prose, not behavior (plan principle 1) |

Schema-relationship note (fact): `agents/task-prompt.md` says its ticket
and receipt forms are what "delegated work" uses within a Task Prompt;
`agents/lead-agent-prompt.md` §Worker handoff standard presents the
9-field ticket as the "minimum ticket" for consequential delegation. The
two schemas are compatible (the 11-field form is a superset) but both are
presented as the operative form in their own file, and neither names the
other as the authoritative copy. The consolidation plan's Track 1
("one authoritative home per doctrine") lists this family of duplication
as pending Slice 3 work.
