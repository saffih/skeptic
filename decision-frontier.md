# Decision Frontier — experimental Skeptic invocation profile

Status: **OPTIONAL CANDIDATE / NOT ADOPTED / NOT A SKEPTIC RUNTIME CHANGE**.

This is a standalone invocation instruction for testing dependency-aware, resolution-first questioning using the **current governing Skeptic runtime**. It introduces no new Skeptic review depth, Thinker, DECIDE authority, action permission, required state store, or dependency on this file for ordinary RunSkeptic.

## Invocation

**Use Decision Frontier for `<goal>`.** Read and bind the current Skeptic runtime selected by the governing context, along with the goal, governing requirements, evidence, authority and permissions. Use **read-only** review by default. Follow the runtime's complete RunSkeptic and InnoSkeptic contracts when invoked; do not represent an ordinary reasoning pass as a formal Skeptic review.

## Procedure

1. **Discover independently.** Derive material obligations, decisions, unknowns, assumptions, failure cases and dependencies from the goal and authoritative inputs. Maintain a lightweight, evolving dependency model. A DAG may describe acyclic prerequisite relationships, but do not require a persistent graph or force circular/conditional dependencies into a false DAG. Resolve or escalate a dependency cycle before treating affected decisions as ready.

2. **Form the ready frontier.** Find every unresolved issue whose prerequisites permit a meaningful next step now. Unsettled prerequisites block only dependent issues. Continue independent factual investigation where available; do not ask the user to retrieve facts the assistant can obtain.

3. **Skeptic-review candidate resolutions.** Apply the current **complete RunSkeptic**, read-only, to every material proposed resolution, individually or in a coherent group sharing evidence or dependencies, explicitly covering each affected decision. Challenge evidence scope, unsupported confidence, assumptions, competing alternatives, authority, consequences and premature closure. Independently ATTACK the *decision model itself* for missing material questions, obligations, affected parties, boundaries and failure modes. Use InnoSkeptic only when materially different solutions may improve the outcome, eliminate branches or reveal missing requirements; preserve nondominated alternatives and necessary owner decisions.

4. **Resolve and propagate.** Mark an issue resolved or inapplicable only when the **exact conclusion** is supported by sufficient current evidence and legitimate authority; a clean review or model confidence alone never closes an issue. Retain unsupported or owner-dependent matters as explicit unknowns. Reconsider affected dependents, invalidate stale conclusions, prune only branches demonstrably unnecessary for the bound goal, and recompute the frontier. Reuse unaffected evidence; avoid repeated review of unchanged dependencies while honoring the governing Skeptic assurance obligations.

5. **Select the next necessary human decision.** Prefer the ready unresolved owner question with the greatest consequential decision leverage relative to burden, considering severity, shared dependencies, ability to discriminate viable options and cost. Required safety, coverage, verification and authority obligations override convenience. Immediately before asking, recheck its prerequisites, current evidence, necessity, recommendation and affected branches. Present **one pivotal question** by default: why it matters, the evidence-supported recommended answer, relevant alternatives or uncertainty, and what the answer will settle or unlock. Group independent owner questions only when doing so clearly reduces burden without obscuring decisions.

6. **Iterate and close honestly.** Incorporate the owner's answer without silently widening it; return to discovery and recompute the frontier. Continue while justified investigation or material owner decisions remain. Before claiming completion, conduct an independent Skeptic omission/false-closure challenge against the original goal and governing obligations, not just the represented graph. Report material supported resolutions, unresolved or blocked matters and their consequences. Obtain user confirmation of shared understanding **before any consequential action**; substantive changes additionally require their normal authorization and verification gates.

**Stopping discipline:** An empty ready frontier is **not** proof of completeness if required issues remain blocked, undiscovered, unsupported or assigned to another authority. Do not manufacture certainty or open-ended questions to keep the interaction going.

## Attribution, originality and license boundary

**Conceptual inspiration:** Matt Pocock's [Grilling skill](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md), specifically dependency-aware decisions, a ready frontier, and iterative questioning. The inspiration is **the idea**, not a copy of its skill text, implementation or presentation format. This profile was independently written for Hartal and does not claim endorsement or authorship by Matt Pocock.

**Upstream license reference:** [Matt Pocock's `skills` repository LICENSE](https://github.com/mattpocock/skills/blob/main/LICENSE) (MIT; copyright (c) 2026 Matt Pocock). This profile does not incorporate upstream code or substantial expressive text; the citation is acknowledgment, not a claim that this profile is MIT-licensed by inheritance. If future revisions actually copy upstream material, independently review license obligations and include the required copyright and permission notice.

## Evaluation and adoption boundary

The effectiveness of this profile is **UNTESTED**. Compare it with unchanged governing Skeptic and, where available, original Grilling under equivalent ambiguous design cases. Pre-register tests for: missing critical obligation; supported auto-resolution; false confidence; shared dependency/pruned branch; cyclic or conditional dependency; genuine owner preference; unnecessary high-burden questioning; and incorrectly clean frontier.

Judge **critical false negatives, false closures, false positives, necessary owner decisions retained, avoidable questions eliminated, decision quality and review cost**. Do not infer success from fewer questions alone, a plausible written analysis, or non-independent same-context role-play.

This candidate is not executable Skeptic runtime authority or a public release. Promotion or any canonical `skeptic.md` edit requires the governed benchmark, exact diff, preservation/rollback analysis and explicit owner approval. The original Grilling skill, original Skeptic runtime, and Hartal public exports remain unchanged.
