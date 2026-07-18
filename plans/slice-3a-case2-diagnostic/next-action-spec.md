# Slice 3B — Selected Disposition and Bounded Next-Action Specification

Lead-only file (not part of the reviewer's packet). This specification is
produced but NOT executed; execution requires separate owner authorization.

## Selected disposition (exactly one)

**REDESIGNED_BEHAVIORAL_TEST**

## Why this disposition (evidence-supported, not score-dependent)

- All four Slice 3A cause classes are permanently NOT RESOLVED for the
  original run (diagnosis.md): the artifacts are proved absent, so no
  disposition that presumes knowledge of the original failure mechanism is
  supportable. That excludes NARROW_R1_CANDIDATE (nothing evidences what
  a narrow correction should say) and NO_FURTHER_CHANGE (the behavioral
  question the evaluation existed to answer is still open, and a
  confirmed custody failure would be silently accepted).
- DOCUMENTATION_OR_INTERFACE_CORRECTION is not selected because the two
  candidate corrections it would carry (making the
  `agents/lead-agent-prompt.md` load condition explicit in `AGENTS.md`;
  tightening closure/persistence enforcement) would legislate from an
  unproven cause: D1 is a real OBSERVED ambiguity, but its causal role in
  Case 2 is only INFERRED RISK, and the consolidation plan's harvest rule
  (≥3 dogfood entries; currently 1) gates doctrine changes. Both are
  recorded below as deferred owner-decision candidates instead.
- CONFLICT is not selected because no blocking authority question remains
  within this task's scope: the frozen decision stands untouched, absence
  was a valid terminal result of the recovery procedure, and the next
  action is specifiable and separately authorizable.
- REDESIGNED_BEHAVIORAL_TEST is the only option that can convert the
  four-way NOT RESOLVED into an evidence-backed diagnosis, and it is
  independently permitted even under the task's degraded-independence
  fallback rule. No aggregate score exists or is used anywhere in this
  selection.

## Bounded specification: "Case 2R — Lead-contract discovery behavioral test"

### Objective

Determine, with persisted evidence, whether an agent given a serious task
in this repository loads and operationalizes
`agents/lead-agent-prompt.md`, and whether an explicit discovery/load
instruction changes that behavior — separating test-design, contract,
variance, and judging causes by construction.

### Design (four-class separability built in)

- **Arms (2):**
  - A (baseline): current contracts byte-for-byte (`AGENTS.md` "should
    read" discovery only).
  - B (candidate): one bounded change — an explicit mandatory load
    condition for `agents/lead-agent-prompt.md` (entry-point rule in
    `AGENTS.md` per the consolidation plan's Track 1 "Entry-points
    section"). The candidate text is committed and pushed BEFORE any run
    (pins cause class 2).
- **Scenario (1, fixed):** a realistic serious-task instruction (multi-
  phase, mutation-bearing, delegation-warranting) that a Lead-contract-
  following agent must answer by constructing a gated prompt/Task Prompt
  rather than executing directly. Frozen verbatim before runs.
- **Runs:** n=3 per arm (6 total), fresh isolated contexts, same scenario
  text (exposes cause class 3; 3/arm is the minimum that distinguishes
  consistent failure from variance while staying proportionate).
- **Tested obligation stated in-scenario materials, not implied**
  (removes cause class 1 ambiguity): the pass criterion is defined
  against the arm's own contract text, so arm A measures discovery under
  "should" and arm B measures discovery under an explicit rule — the
  comparison itself is the finding.
- **Detection, two-layer** (checks cause class 4):
  1. Mechanical signal: transcript evidence that the file was actually
     read (tool-call record), plus presence/absence of the operational
     markers the Lead contract requires (gate receipt fields, ticket
     fields, ponytail footer) — scored by deterministic script where
     possible.
  2. Judge: fresh isolated context, scores only against a per-dimension
     rubric frozen and pushed before runs; Judge receives transcripts and
     rubric only. Judge output is compared against the mechanical signal;
     divergence is itself a recorded finding (Judge-mismatch detector).

### Evidence-custody rules (non-negotiable, from C1/C2)

- Manifest, frozen rubric, scenario, and candidate diff are committed and
  pushed before the first run.
- Every run transcript and Judge packet is committed and pushed before
  the scoring/decision phase begins ("evidence before decision").
- The closure receipt carries concrete observed values only; a run whose
  evidence is not pushed is void and is rerun, not summarized from memory.

### Authority, scope, and limits

- Owner authorization required to execute; this spec confers none.
- Precondition (adopted from the independent reviewer's protected
  receipt): before Case 2R executes, the owner must attest that no
  off-repository Slice 3A evidence exists (local clone, session
  transcript, chat export). If such evidence exists, it supersedes this
  spec: recovery resumes against the supplied artifacts and the four-way
  diagnosis is re-run before any new test is built.
- Writes limited to a fresh branch and a dedicated evidence directory
  (e.g. `plans/case2r-behavioral-test/`); arm B's contract change exists
  only on that branch unless separately promoted afterwards.
- Budget: single session; retry bound 2 per failure class, then redesign;
  futility stop if the harness cannot produce isolated runs.
- Explicit non-goals: no rescoring of Slice 3A; no promotion decision
  inside the test slice (results feed a separate, owner-gated decision);
  no doctrine edits beyond arm B's bounded candidate text on its branch.

### DONE for Case 2R (when executed)

1. Frozen scenario, rubric, manifest, and arm-B diff pushed before runs.
2. 6/6 transcripts + Judge packets pushed.
3. Mechanical-vs-Judge concordance table produced.
4. Four-class diagnosis re-stated with post-test evidence levels.
5. Closure receipt with observed values; RunSkeptic HANDLED.

## Deferred candidates recorded for owner decision (not selected, not executed)

- DC1: `AGENTS.md` entry-point/mandatory-load clarification as a
  permanent change (promoted only if arm B materially outperforms arm A).
- DC2: Closure/persistence enforcement tightening in
  `agents/task-prompt.md` §14 and §9 (pre-authorized in spirit by the
  Slice 1 LEARN note; blocked by the harvest rule until ≥3 dogfood
  entries exist; this task supplies a second recorded custody failure for
  that ledger).
- DC3: A dogfood-log entry for this evidence-loss event (write path
  `plans/dogfood-log.md` is outside this task's mutation authority).
