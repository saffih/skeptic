# WELL — Warranted, Explicit, Lean, Linked

WELL is a normative profile for design and architecture documents, including software design documents (SDDs), because design reasoning must remain inspectable and resistant to drift. WELL governs this document, because an exempt standard cannot demonstrate feasibility.

## Scope, purpose, and boundaries

WELL applies only to architecture descriptions, SDDs, design specifications, architecture decision records, and similar artifacts that define or justify a design, because those decisions must survive implementation.

WELL does not govern prompts, code, reviews, reports, status updates, test results, runbooks, user documentation, or ordinary communication, because those artifacts serve different purposes. Scope follows function, because naming cannot extend authority.

WELL prevents unsupported statements gaining authority, decisions losing reasons, repeated rationale drifting, compression deleting meaning, and explanation hiding the design chain, because each failure weakens maintenance.

WELL governs design-writing structure rather than Skeptic review, because overlapping authority would create drift. WELL is not a language, proof system, demand for hidden reasoning, proof of design correctness, or requirement for visible sentence metadata, because structure is neither truth nor mandatory formalism.

## Primary invariant and roles

Every retained sentence in a WELL-governed design document must have a recoverable reason for existing, because arbitrary, unsupported, or purpose-disconnected statements cannot preserve rational integrity.

A sentence satisfies the invariant only when it performs a necessary role, because nonoperative text cannot justify maintenance:

- **Ground** — objective, constraint, observation, authority, assumption, or unknown.
- **Definition** — stable meaning needed by later reasoning.
- **Proposition** — design claim, requirement, recommendation, or decision.
- **Qualification** — scope, condition, boundary, or exception.
- **Consequence** — effect, cost, risk, or trade-off.
- **Check** — evidence, acceptance, verification, or falsification.
- **Open item** — unresolved unknown, conflict, or decision.
- **Structure** — connection or navigation for reasoning.

A sentence may combine roles, because forced separation adds length. Labels are optional when roles are clear, because ceremony can imitate rigor. Remove a sentence with no role, because unnecessary text creates noise and drift.

## Sentence warrant and termination

A sentence is reason-bearing when it uses `because`, `to`, `so that`, `therefore`, an equivalent causal construction, or one explicit local warrant, because readers must not reconstruct distant intent. Prefer a direct reason when natural, but share a local warrant when repetition adds nothing, because WELL must remain Explicit and Lean.

A support path may end at an objective, constraint, observation, authoritative input, definition, assumption, or unknown, because finite documents need stopping points. Mark assumptions and unknowns, because status does not prove them. Grounds and definitions may end locally, but still need inclusion reasons, because necessity differs from evidence. Do not justify reasons recursively, because infinite regress is unusable.

## Dimensions

**Warranted.** Give design claims, requirements, recommendations, and decisions sufficient relevant grounds, because unsupported propositions cannot be assessed reliably.

**Explicit.** State scope, conditions, assumptions, limits, exceptions, consequences, conflicts, and unknowns when omission could change interpretation or implementation, because incomplete design prose can mislead.

**Lean.** Use the shortest form that preserves operative design meaning, because extra text hides distinctions and increases drift. Do not remove necessary reasoning, qualification, uncertainty, consequence, or verification, because brevity without integrity is false simplicity.

**Linked.** Make relationships among propositions, grounds, qualifications, consequences, checks, and open items recoverable, because disconnected statements cannot form a maintainable design chain. Use any unambiguous representation, because no format is mandatory.

## Normative rules

Ground every derived or normative design proposition and end its support path explicitly, because implementation must not depend on unsupported premises. State qualifications and consequences that could change a design choice, because unbounded statements and hidden costs can mislead. Give checkable propositions a verification or falsification path, and mark assumptions, unknowns, conflicts, and unresolved decisions, because claims must be able to fail and uncertainty must remain visible.

Define shared terms and rationale once, keep enough reasoning local to prevent guessing, and reference detail instead of repeating it, because canonical meaning reduces drift. Remove nonoperative content, prefer readable prose over metadata, and add structure only for a credible design-document failure, because WELL should improve understanding rather than create forms.

## Searchability guidance

For material design content, prefer one complete proposition per paragraph and keep that proposition, including its local reason, on one physical source line, because `grep`, diffs, and agents can then retrieve it as one bounded reasoning unit.

Separate proposition paragraphs with blank lines, because clear source boundaries make propositions easier to add, remove, move, and review independently.

Choose one canonical term when a material concept is first defined, and reuse that term in related propositions instead of relying only on pronouns or changing synonyms, because exact-text search should find the concept’s relevant claims, constraints, decisions, and checks.

Prefer explicit relationship phrases such as `depends on`, `constrains`, `supports`, `verifies`, `contradicts`, and `supersedes`, because directional wording helps readers and agents understand what a change may affect.

Use editor soft wrapping rather than inserting source line breaks inside a proposition, because visual readability can be preserved without weakening search results.

Depart from this guidance when it would materially harm clarity or force one connected piece of reasoning into unnatural fragments, because searchability supports WELL but does not override reasoning integrity.

## Document obligations and verification boundary

A WELL-governed design document must establish applicable purpose, scope, grounds, constraints, decisions, qualifications, consequences, checks, and unresolved matters, because these make reasoning inspectable. Omit inapplicable obligations, because ceremony violates Lean.

WELL review may identify unsupported propositions, hidden assumptions, undefined terms, missing qualifications, consequences, or checks, contradictions, broken links, repeated rationale, and removable text, because these are structurally inspectable. Conformance cannot prove evidence true, grounds sufficient, inference valid, a design correct or optimal, context complete, or wording maximally lean, because inspectable reasoning is not correct reasoning.

## Application

1. Establish purpose, because sentence necessity depends on the design outcome.
2. Identify material propositions, because grounds and checks attach to them.
3. Establish grounds, qualifications, consequences, and checks, because they form the reasoning chain.
4. Expose assumptions, unknowns, and conflicts, because concealed uncertainty causes false confidence.
5. Consolidate definitions and rationale, because canonical statements reduce drift.
6. Apply the searchability guidance where it preserves reasoning integrity, because bounded source units improve retrieval and review.
7. Remove repetition and nonoperative text, because unnecessary content weakens Lean.
8. Verify preserved meaning after compression, because deletion can create false simplicity.
9. Review the complete document, because locally valid sections can conflict globally.
10. Review every sentence’s reason, because WELL applies at sentence and document levels.

## Conformance

A design document is WELL-conformant only when sentences have recoverable reasons, material propositions have sufficient grounds, limits and consequences are explicit, assumptions and unknowns remain visible, checkable propositions have checks, reasoning links are recoverable, no sentence is removable without loss, applicable obligations are discharged, and unresolved matters remain unresolved, because partial compliance cannot preserve the design chain.

Conformance requires judgment, because sufficiency, necessity, validity, and justified departures from searchability guidance are not fully mechanical.

## Examples

### Example 1 — unsupported design proposition

“Use event sourcing” fails because it gives no design ground. “Use event sourcing for the audit ledger, because immutable history is required for reconstruction” adds one.

### Example 2 — definition without inclusion rationale

“Boundary is the validation façade” fails because its design function is unstated. “Boundary means the validation façade, because later interface rules assign trust transitions to that role” explains its need.

### Example 3 — excessive repeated reasoning

Repeating “because the controller must remain deterministic” after every controller rule violates Lean because one local warrant can govern the group. State it once before the rules, because local scope preserves the link without noise.

### Example 4 — search-fragmented proposition

A material proposition split across several hard-wrapped source lines is harder to retrieve as one reasoning unit. Keep the complete proposition and its local reason on one source line when clarity permits, because editors can soft-wrap the line for display.

## Self-application

Every retained sentence in this document has a direct or unambiguous local reason for existing, because sentence-level warrant is WELL’s primary integrity mechanism. The searchability section uses one proposition paragraph per physical source line and canonical terms, because self-application requires the profile to demonstrate its own guidance. This claim rests on sentence review, rationale consolidation, explicit scope limits, and source-format inspection, because self-application requires inspection rather than assertion.
