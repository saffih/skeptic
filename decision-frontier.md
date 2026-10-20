# Skeptic Grill — experimental Decision Frontier invocation profile

Status: **OPTIONAL CANDIDATE / NOT ADOPTED / NOT A SKEPTIC RUNTIME CHANGE**.

This is a standalone invocation instruction for testing dependency-aware, resolution-first questioning using the **current governing Skeptic runtime**. It introduces no new Skeptic review depth, Thinker, DECIDE authority, action permission, required state store, or dependency on this file for ordinary RunSkeptic.

## Invocation

**Primary trigger:** `Skeptic Grill: <goal>`. **Alias:** `Decision Frontier RC: <goal>`. Read and bind the experimental Skeptic V6 RC runtime selected by the governing context, along with this profile, the goal, governing requirements, evidence, authority and permissions. Use **read-only** review by default. Follow the runtime's complete RunSkeptic and InnoSkeptic contracts when invoked; do not represent an ordinary reasoning pass as a formal Skeptic review.

## Procedure

1. **Discover independently.** Derive material obligations, decisions, unknowns, assumptions, failure cases and dependencies from the goal and authoritative inputs. Maintain a lightweight, evolving dependency model. A DAG may describe acyclic prerequisite relationships, but do not require a persistent graph or force circular/conditional dependencies into a false DAG. Resolve or escalate a dependency cycle before treating affected decisions as ready.

2. **Form the stage-necessary frontier.** Identify the current stage and the minimum decisions required to advance it safely. An issue is ready for an owner decision now only when its prerequisites are satisfied **and** deciding now materially serves this stage or preserves a necessary future option. A question may be answerable yet premature. Unsettled prerequisites block only dependent issues; continue independent factual investigation without requiring premature commitments.

3. **Skeptic-review candidate resolutions.** Apply the current **complete RunSkeptic**, read-only, to every material proposed resolution, individually or in a coherent group sharing evidence or dependencies, explicitly covering each affected decision. Challenge evidence scope, unsupported confidence, assumptions, competing alternatives, authority, consequences and premature closure. Independently ATTACK the *decision model itself* for missing material questions, obligations, affected parties, boundaries and failure modes. Use InnoSkeptic only when materially different solutions may improve the outcome, eliminate branches or reveal missing requirements; assess alternatives under the proportional trade-off rule below; preserve nondominated alternatives and necessary owner decisions.

4. **Resolve and propagate.** Mark an issue resolved or inapplicable only when the **exact conclusion** is supported by sufficient current evidence and legitimate authority; a clean review or model confidence alone never closes an issue. Retain unsupported or owner-dependent matters as explicit unknowns. Reconsider affected dependents, invalidate stale conclusions, prune only branches demonstrably unnecessary for the bound goal, and recompute the frontier. Reuse unaffected evidence; avoid repeated review of unchanged dependencies while honoring the governing Skeptic assurance obligations.

5. **Select the next necessary human decision.** Prefer a stage-necessary unresolved owner question with the greatest consequential decision leverage relative to burden, considering severity, shared dependencies, ability to discriminate viable options and cost. Required safety, coverage, verification and authority obligations override convenience. Immediately before asking, recheck its prerequisites, current evidence, necessity, recommendation and affected branches. Present **one pivotal question** by default: why it matters, the evidence-supported recommended answer, relevant alternatives or uncertainty, and what the answer will settle or unlock. Group independent owner questions only when doing so clearly reduces burden without obscuring decisions.

6. **Iterate and close honestly.** Incorporate the owner's answer without silently widening it; return to discovery and recompute the frontier. Continue while justified investigation or material owner decisions remain. Before claiming completion, conduct an independent Skeptic omission/false-closure challenge against the original goal and governing obligations, not just the represented graph. Report material supported resolutions, unresolved or blocked matters and their consequences. Obtain user confirmation of shared understanding **before any consequential action**; substantive changes additionally require their normal authorization and verification gates.

**Progressive commitment and deferral.** Decide only what the current stage needs. Record **material** decisions deliberately not made now, with a brief reason, the affected future claim or action, and an event or condition for reconsideration. A deferral is **not** a promise that the decision must ever be made: it may evolve or disappear. Do not demand a fixed future stage plan, exhaustive decision inventory, or new registry; use existing Skeptic open-item state. Investigating a future choice is allowed without committing to it. Challenge both premature decisions (unnecessary lock-in, cost, human burden) and unsafe deferrals (mandatory obligations, irreversible effects, critical dependencies, material rework, expiring opportunities). When delay is unsafe, decide only the minimum required now. Show deferred items to the user only when the deferral materially matters, not after every round.

**Independent discovery and stage adequacy.** Before filtering or ranking alternatives, independently derive the relevant stakeholders, binding obligations, success and failure scenarios, and domain-specific quality attributes from the actual goal and context. Consider qualities such as robustness, efficiency, clarity, learnability, usability and fairness where relevant, without treating any list as exhaustive or universally mandatory.

Challenge weaknesses common to all alternatives and failures arising from their interactions. Consider no change, a smaller experiment, or deferral when materially viable.

Distinguish binding constraints, sufficiency for the current stage, and negotiable preferences. Evaluate each candidate against those conditions before comparing relative merits. Do not impose production requirements on a bounded prototype. Preserve consequential unknowns rather than automatically rejecting or accepting uncertain candidates. Scale investigation to its decision value. Neither a clean comparison nor a finite checklist proves completeness.

**Cross-cutting engineering and AI-document literacy.** When material to the decision, consider requirements and stage adequacy; architecture, specification, design, implementation and test roles; source-of-truth authority; interfaces and contracts; provenance, freshness and traceability of evidence; AI-generated claims versus observed results; context loss and handoffs; owner/agent responsibility, upstream effects and reversibility. These are detection cues, not a mandatory checklist, glossary, document set or development process. Resolve abbreviations (including SDD) from the governing context rather than imposing a universal meaning; load problem-domain detail only when relevant.

**Proportional alternative evaluation (InnoSkeptic).** KISS, DRY, fail-fast, deterministic behavior, and explicitness are *defeasible engineering preferences*, not universal requirements. For each materially live candidate, first preserve actual source-grounded obligations and protections, then compare only differences that could change the current-stage decision: useful outcome and uncovered scenarios; exposure (likelihood/frequency, affected population and blast radius); severity including rare catastrophic or irreversible failures; visibility, detectability, containment, recovery and time to harm; development, testing, operational, maintenance and human effort; coupling, future flexibility and lock-in; and evidence/uncertainty. Check whether a simpler or staged path changes the material risk at much lower cost. A tiny recoverable gap may warrant explicit acceptance rather than major engineering work; a rare but unacceptable consequence or binding obligation warrants a proportionate safeguard. Deliberate duplication, nondeterminism, delayed failure or implicit behavior can be justified by the actual context: test their consequences rather than enforcing slogans. Consider both the cost of gaps and the cost of preventing them.

**Evaluation economy and decision.** Use a short qualitative comparison of only discriminating dimensions by default; no compulsory scorecard, invented probabilities, fixed weighting or exhaustive scenario matrix. Where evidence is missing and would affect the choice, prefer the cheapest safe discriminating probe or state the bounded uncertainty. Recommend the option with the best *supported* outcome relative to risk, effort and option value for this stage, including any material uncovered case and why its residual risk is acceptable or still unknown. Preserve nondominated options when values or evidence cannot distinguish them. If the choice is not yet stage-necessary, record a material deferral with its reactivation condition rather than forcing a winner.

## Decision view — adaptive presentation

Use this view for a material, **current-stage** decision when comparing alternatives or seeking an owner choice. Its purpose is to expose the decisive evidence and trade-off, not to replace the complete Skeptic review. For a low-stakes, reversible choice, shorten it to the decision, material alternatives, and recommendation. For consequential choices, expand only the fields that affect judgment.

**Q:** [One concrete decision/question; ask the owner only when their decision is currently owed.]

**Recommendation:** [Supported option, experiment, or deferral and why; cite file:line or observed evidence when available, or state UNKNOWN. Never imply that a proposed risk acceptance is already authorized.]

**Scenario:** [In 2–3 plain sentences when material: who does what, under which conditions, and what succeeds or breaks.]

**Stakes:** [Relevant exposure/frequency, severity, visibility/detectability, reversibility, and consequence of waiting or choosing incorrectly.]

**Musts:** [Binding requirements and their basis; distinguish these from preferences. State "none established" if appropriate.]

| Option | Gain | Cost / effort | Gap / residual risk |
|---|---|---|---|
| **A — recommended, if supported** | [Useful benefit] | [Build, operation, maintenance, and human effort] | [Uncovered scenario; exposure, consequence, or uncertainty] |
| **B — alternative** | [Benefit] | [Cost] | [Remaining gap] |
| **C — no change / defer / probe, if viable** | [Benefit or option value] | [Cost or delay] | [Remaining gap] |

**Attributes considered:** [Name only relevant attributes, including shared binding requirements and consequential unknowns. For decisive attributes, show how alternatives help or hurt and why; distinguish preferences from requirements. Do not use context-free ✓/✗ labels, invented scores, or unearned claims such as “safe” or “no gap”.]

**Trade-off:** [One sentence: what is gained at what sacrifice.]

**What could change the answer?** [Material uncertainty, assumption, sensitivity point, or missing evidence; omit if immaterial.]

**Settles / unlocks:** [What this answer closes now and the next necessary decision or investigation, without prematurely deciding future stages.]

**Upstream:** [None / flag only / change required — identify where, impact, and authority when material; do not invent obligations.]

**Presentation economy:** Use a stable reading path: decision -> supported position or decisive unknown -> reason/affected attributes -> material caveat or dependency -> next. Use concise prose for simple choices, the Gain / Cost / Gap option table when trade-offs warrant it, or an attribute-impact matrix when comparing values is more informative. No format or field is mandatory when immaterial. List considered attributes briefly and expose only material effects. Do not invent rows, defaults, numerical scores, or a winner; include no-change/defer/probe only when viable. If no recommendation is supported, show the live alternatives and decisive unknown. Ask only owner questions currently owed, and preserve necessary provenance, binding requirements, shared failures and upstream impacts without dumping a checklist.

**Stopping discipline:** An empty ready frontier is **not** proof of completeness if required issues remain blocked, undiscovered, unsupported or assigned to another authority. Do not manufacture certainty or open-ended questions to keep the interaction going.

## Attribution, originality and license boundary

**Conceptual inspiration:** Matt Pocock's [Grilling skill](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md), specifically dependency-aware decisions, a ready frontier, and iterative questioning. The inspiration is **the idea**, not a copy of its skill text, implementation or presentation format. This profile was independently written for Hartal and does not claim endorsement or authorship by Matt Pocock.

**Upstream license reference:** [Matt Pocock's `skills` repository LICENSE](https://github.com/mattpocock/skills/blob/main/LICENSE) (MIT; copyright (c) 2026 Matt Pocock). This profile does not incorporate upstream code or substantial expressive text; the citation is acknowledgment, not a claim that this profile is MIT-licensed by inheritance. If future revisions actually copy upstream material, independently review license obligations and include the required copyright and permission notice.

## Evaluation and adoption boundary

The effectiveness of this profile is **UNTESTED**. Compare it with unchanged governing Skeptic and, where available, original Grilling under equivalent ambiguous design cases. Pre-register tests for: missing critical obligation; supported auto-resolution; false confidence; shared dependency/pruned branch; cyclic or conditional dependency; genuine owner preference; unnecessary high-burden questioning; and incorrectly clean frontier.

Judge **critical false negatives, false closures, false positives, necessary owner decisions retained, avoidable questions eliminated, decision quality and review cost**. Test contrastive cases: costly fix for low-exposure recoverable gap; rare severe irreversible gap; justified independent duplication despite DRY; bounded nondeterminism where determinism is costly; and low-stakes choices that should not trigger a scoring ritual. Do not infer success from fewer questions alone, a plausible written analysis, or non-independent same-context role-play.

This candidate is not executable Skeptic runtime authority or a public release. Promotion or any canonical `skeptic.md` edit requires the governed benchmark, exact diff, preservation/rollback analysis and explicit owner approval. The original Grilling skill, original Skeptic runtime, and Hartal public exports remain unchanged.
