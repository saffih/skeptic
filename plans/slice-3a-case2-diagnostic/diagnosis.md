# Slice 3B — Lead Causal Diagnosis

Lead-only file. Written after the evidence packet was frozen and after the
Independent Diagnostic Reviewer was dispatched; the reviewer's ticket
forbids reading this file. Grounded in `recovery-report.md` and
`architecture-map.md`.

## Standing constraint

The frozen Slice 3A decision (HANDLED — NO_PROMOTION) is not reopened,
rescored, weakened, or modified by anything below. Absence of the Slice 3A
evidence does not weaken NO_PROMOTION: no-promotion is the conservative
default and needs no evidence to remain in force; it is promotion that
would require evidence.

## The four required cause classes

The decision-critical Case 2 artifacts (baseline/candidate transcripts,
manifest, frozen scoring contract, Judge packet and rationale, RunSkeptic
and closure receipts, candidate diff) are proved absent from all
cloud-accessible state (recovery-report.md, searches 1–11). Consequently:

### 1. Test-design weakness

- Evidence: no direct evidence (test artifacts absent). Structural
  evidence exists that the tested behavior sits on a contract ambiguity:
  no runtime contract mandates loading `agents/lead-agent-prompt.md`; the
  only trigger is `AGENTS.md`'s "Lead agents **should** read", with no
  rule for when an agent must self-classify as Lead (architecture-map D1).
  A behavioral test that fails a candidate for not loading a file no
  contract obliges it to load would be scoring an under-specified
  obligation.
- Evidence level: OBSERVED for the contract ambiguity itself (D1);
  INFERRED RISK for its role in the Case 2 outcome.
- Confidence as the Case 2 cause: LOW (cannot rise without the test spec).
- Disconfirming evidence that would refute it: a recovered or regenerated
  test spec showing the candidate contract itself made the load mandatory
  and unambiguous.
- Unresolved unknowns: the actual Case 2 input, pass criteria, and
  scenario framing.
- Verdict: NOT RESOLVED.

### 2. Candidate-contract weakness

- Evidence: none; the candidate diff is absent. It cannot be determined
  whether the candidate contained a load instruction at all, a weak one,
  or a strong one that was ignored.
- Evidence level: none (no artifact).
- Confidence: NONE either way.
- Disconfirming evidence that would refute it: a candidate diff with an
  explicit, well-placed mandatory load instruction (would exclude the
  "missing instruction" variant; would not exclude "weakly operative
  instruction").
- Unresolved unknowns: the candidate text itself.
- Verdict: NOT RESOLVED.

### 3. Generator-following variance

- Evidence: none. Variance is only assessable across n>1 runs; the
  evaluation manifest is absent, so even the number of runs per arm in
  Slice 3A is unknown. A single-run Case 2 could not distinguish variance
  from contract weakness even if its transcript existed.
- Evidence level: none.
- Confidence: NONE.
- Disconfirming evidence that would refute it: multiple independent runs
  of the same candidate arm agreeing (all loading or all not loading).
- Unresolved unknowns: run count, sampling conditions, transcripts.
- Verdict: NOT RESOLVED.

### 4. Judge interpretation or scoring-contract mismatch

- Evidence: none; both the frozen scoring contract and the Judge rationale
  are absent, so it cannot even be established what the Judge was
  obligated to check, let alone whether it deviated.
- Evidence level: none.
- Confidence: NONE.
- Disconfirming evidence that would refute it: a Judge rationale whose
  per-dimension scoring maps one-to-one onto a recovered frozen rubric.
- Unresolved unknowns: rubric, packet, rationale, scores.
- Verdict: NOT RESOLVED.

## What IS confirmed

- C1 (OBSERVED): Evidence-custody failure. A promotion-relevant decision
  ("HANDLED — NO_PROMOTION") exists with zero durable evidence in any
  cloud-accessible store, in a repository whose own doctrine requires
  decision-critical artifacts to be persisted before dependent work
  (`agents/task-prompt.md` §9; `agents/lead-agent-prompt.md` §Context
  protection: "Authoritative evidence must not exist only in transient
  context, temporary paths, worker memory, or chat prose"). Whatever else
  went wrong in Slice 3A Case 2, this failure is proved by the exhaustive
  absence result and is the direct cause of the present diagnostic
  impasse.
- C2 (OBSERVED): Failure-class recurrence. This is at least the third
  occurrence of the persistence/closure application-fidelity class:
  (1) Slice 1's closure receipt initially persisted with unfilled
  routing/publication fields (routing slice record, post-publication
  correction); (2) dogfood Entry 001's "template completion passing for
  contract completion"; (3) this total evidence loss. Under `skeptic.md`
  §12 LEARN, 3+ occurrences of one fix category triggers DOUBLE-LOOP:
  the detection/enforcement method — not just each instance — is suspect.
  Any doctrine amendment remains gated by the consolidation plan's
  harvest rule (≥3 dogfood entries; currently 1) and by owner decision;
  it is recorded here as a finding, not enacted.
- C3 (OBSERVED): Provenance gap. "Slice 3A", "R1", the six-case protocol,
  and the frozen decision string are uncorroborated by any repository
  artifact; the repo's own slice numbering assigns Slice 3 to doctrine
  dedup. The Slice 3A definition therefore has inbound-prompt provenance
  only. This does not overturn the owner's framing (owner instruction is
  the applicable authority), but every conclusion above is conditioned on
  that framing being accurate.

## Diagnostic conclusion

The four cause classes cannot be separated by any recoverable evidence:
all four are NOT RESOLVED, and they will remain permanently unresolved for
the original Slice 3A run — the transcripts no longer exist anywhere
reachable. The only path to a resolved four-way diagnosis is regeneration:
a redesigned behavioral test whose design makes the four classes
separable (explicit tested obligation to remove class 1 ambiguity;
persisted candidate text to pin class 2; n≥3 runs per arm to expose
class 3; a pre-frozen rubric plus a mechanical load-detection signal to
check class 4), executed under mandatory evidence-persistence rules so
this failure mode cannot recur.
