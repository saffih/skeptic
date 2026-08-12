# WELL — Warranted, Explicit, Lean, Linked

WELL is the normative profile for architecture, software-design, architecture-decision, and equivalent design documents, because design meaning must remain inspectable and resistant to drift.

WELL governs this document, because a design standard must demonstrate that its own requirements are usable.

## Scope and purpose

WELL applies to documents that define or justify a design, because their propositions must survive implementation, review, extraction, movement, and later modification.

WELL does not govern prompts, source code, reviews, reports, status updates, test output, runbooks, user documentation, or ordinary communication, because those artifacts serve different functions and require different forms.

Scope follows function rather than filename, because renaming an artifact must not silently extend or remove normative authority.

WELL protects document integrity, because unsupported claims, detached reason representations, hidden declared qualifications, duplicated rationale, and disconnected checks can cause a later edit to change the represented design unintentionally.

WELL governs design-writing structure rather than Skeptic review or executable qualification, because inspectable reasoning, adversarial criticism, and runtime proof are complementary authorities rather than substitutes.

WELL is not a proof system, a demand for hidden reasoning, or proof that a design is correct, because explicit structure can expose an error without resolving it.

WELL's normative PASS/FAIL obligations concern only represented and mechanically observable structure, while REVIEW reports a mechanically unresolved classification without treating it as a pass, because judgments about the represented meaning are assigned to the governing project's separate meaning-aware design review.

## Self-contained design propositions

A design proposition is a prose unit that the author identifies as a design fact, definition, requirement, decision, qualification, consequence, check, assumption, unknown, or relationship, because the identified unit needs an independently recoverable warrant.

A WELL-governed design document expresses each author-identified design proposition as a self-contained unit, because searching, quoting, moving, reviewing, or modifying the represented unit must not separate its claim from its stated reason.

Every syntactically classified prose sentence must contain the literal word `because`, because the proposition and its warrant must remain recoverable when the sentence is read outside its surrounding prose.

The `because` clause must be a syntactically distinct local reason, protection, consequence, dependency, or inclusion-rationale clause, because the claim and its stated warrant representation must remain mechanically recoverable together, because whether the clause is relevant, sufficient, non-circular, or persuasive is outside mechanical WELL conformance.

A local-warrant representation requires the literal `because` token in the prescribed syntactic position, because whether the surrounding words cite the standard, label importance, or express a genuine reason is a meaning-aware review judgment.

ATX headings, YAML/front-matter metadata, fenced code blocks, table rows, block formulas, diagram blocks, bare identifiers, state-vocabulary items, and list items without sentence punctuation are structural syntax categories exempt from the sentence rule, because these are named structural roles rather than prose that must carry its own warrant.

A Markdown list may inherit one explicit warrant from its introductory sentence only when each child item is a mechanically identified fragment without sentence punctuation, because a complete prose sentence must preserve its own literal token.

A complete prose sentence inside a list must contain its own literal `because`, because list formatting does not remove the sentence syntax that the checker classifies.

A quoted example sentence may omit `because` only inside a blockquote or fenced example explicitly marked as an example, because the checker must have a mechanical exemption boundary for displayed examples.

WELL formation protects modification integrity, because cohesive and locally warranted propositions can be searched, extracted, moved, compared, replaced, and updated without silently losing the reasoning that constrains them.

## Proposition roles

The following role vocabulary is authoring guidance, because WELL does not infer semantic roles or require an unprovided role-annotation syntax:

- ground: objective, constraint, observation, authority, assumption, or unknown
- definition: stable meaning needed by later reasoning
- proposition: design claim, requirement, recommendation, or decision
- qualification: scope, condition, boundary, or exception
- consequence: effect, cost, risk, or trade-off
- check: evidence, acceptance, verification, or falsification path
- open item: unresolved unknown, conflict, or decision
- structure: explicit connection or navigation needed by the reasoning chain

A proposition may combine roles when the document represents those roles together, because the role representation need not impose a one-role-per-proposition form.

A proposition may be split when the author assigns different local warrants to separately represented claims, because one `because` clause must not conceal separately represented decisions, because whether claims should be split for semantic clarity is outside mechanical WELL conformance.

Whether a proposition has a role, is operative, useful, or necessary belongs to authoring and meaning-aware review and does not determine mechanical WELL conformance, because those judgments are not mechanical representation tests.

## Warrant termination

A support path may terminate at an objective, constraint, direct observation, authoritative input, stable definition, explicit assumption, or explicit unknown, because finite design documents need legitimate stopping points.

Authors should give grounds and definitions local inclusion-reason representations, because the stated inclusion reason should be recoverable without requiring a checker to infer the role, and meaning-aware review decides whether the classification and reason are adequate.

Authors should explicitly identify assumptions and unknowns when they matter, because meaning-aware review decides whether uncertainty has been represented correctly and this guidance does not determine mechanical WELL conformance.

Reasons do not require infinite recursive justification, because an explicitly labelled terminal ground is an allowed endpoint for a finite recoverable design chain.

## WELL dimensions

**Warranted.** Authors should give design claims, requirements, recommendations, and decisions an explicit local stated warrant or terminal ground/reference, because the claim and its stated support should be mechanically recoverable together, while meaning-aware review decides whether the warrant actually supports, justifies, or is relevant to the proposition.

**Explicit.** Authors should represent scope, conditions, assumptions, limits, exceptions, consequences, conflicts, and unknowns in an explicit structural form, because mechanically inspectable representation exposes what the document states, while meaning-aware review decides whether important qualifications have been discovered.

**Lean.** Authors should follow bounded structural conventions for proposition separation, canonical naming, repeated definitions, and duplicate authority, because those conventions support inspectability, while meaning-aware review decides whether prose or an entity is substantively unnecessary.

Authors should not remove represented reasoning, qualification, uncertainty, consequence, or verification for brevity, because mechanical conformance preserves the elements present in the document while semantic adequacy remains reviewable.

**Linked.** Any canonical links and structural edges that appear in the document have explicit names, valid targets, and resolvable syntax, because the represented links must be mechanically traversable, while meaning-aware review decides whether relationships are complete or semantically valid.

`stable-semantic-references` — Authors should use one unique lowercase kebab-case canonical name enclosed in backticks when an external reference is useful, because semantic names remain grep-friendly and stable when sections move.

`name-only-when-useful` — Authors may assign canonical names where external reference or graph inspection is useful, because whether a proposition should have a name is authoring and meaning-aware review guidance rather than a mechanical WELL condition.

A canonical name should describe the represented meaning rather than its location and should not use numeric or positional identifiers, because positional identifiers drift without conveying design meaning, while naming adequacy remains outside mechanical WELL.

Every canonical reference repeats the exact backticked name, because exact search should locate the definition and every dependent proposition.

Renaming a canonical proposition is a material edit that updates every reference, because the name is the stable key in the document's reasoning graph.

Another unambiguous representation may replace canonical names only when it provides equal or better stability, searchability, and graph inspection, because formatting serves design integrity rather than becoming an end in itself.

## Normative writing rules

Authors should give propositions local warrants and explicit support termini, because implementation should not depend on distant or guessed intent, while whether a proposition needs a warrant and whether its support is adequate remain outside WELL.

Authors should attach each qualification and consequence to the proposition it constrains, because extraction or movement should not silently broaden the represented claim, while meaning-aware review decides what must be represented.

Authors should provide verification or falsification paths where appropriate, because a check should be recoverable directly or through an explicit canonical link, while meaning-aware review and the Design Authority Chain decide whether a proposition needs one.

Authors should consolidate reusable terms and rationale behind one canonical definition with explicit references, because repeated definitions and reasons can diverge, while semantic reuse decisions remain outside WELL conformance.

`connected-reasoning-graph` — Canonical graph edges that appear in the document have explicit direct or transitive targets and resolvable syntax, because present structural edges must be recoverable, while whether connectivity is required and whether edges represent valid support or dependency belong to meaning-aware review.

`detached-graph-review` — A disconnected represented graph component is a meaning-aware review concern rather than a mechanical WELL violation, because WELL does not infer whether a missing semantic relationship should exist.

The required local warrant remains with an extracted proposition, because a reference cannot substitute for the proposition's immediate reason representation.

Authors should remove nonoperative content and duplicate authority, because mechanical checking can detect exact duplicate identifiers or definitions but cannot decide whether prose is substantively operative or necessary.

## Misunderstanding resistance

A proposition may require separate meaning-aware clarification when a reader could derive a materially different interpretation, because misunderstanding likelihood and consequence are semantic review judgments rather than mechanical WELL criteria.

Authors should represent a controlling contrast explicitly in canonical definitions when related concepts differ by timing, scope, authority, lifecycle position, or evidentiary role, because the distinction should be recoverable while its need and correctness remain review judgments outside WELL.

A meaning-aware review finding may justify a narrow clarification when the reviewer identifies a plausible and materially consequential misunderstanding, because that judgment belongs to review rather than mechanical WELL conformance.

Adding such a clarification does not retroactively validate the earlier finding, because the clarification changes the represented structure without making the earlier semantic judgment a WELL result.

Authors should represent a controlling contrast explicitly in canonical definitions when they distinguish related concepts, because the contrast itself is mechanically inspectable while plausibility, consequence, and adequacy remain outside WELL.

An explicitly required clarification must be placed at the canonical definition or controlling rule rather than repeated at every dependent use, because one represented authoritative contrast avoids duplicate structural definitions, because whether clarification is needed belongs to meaning-aware review.

A schema, record, manifest, or structure that the author declares reusable must be introduced explicitly at its canonical definition before dependent propositions use that name, because recoverable fields do not by themselves establish the name's authoritative referent.

A requirement whose satisfaction depends on the order of edits, reviews, approvals, or publications must identify the observable evidence that establishes that order, because a final snapshot proves resulting state but ordinarily cannot prove the sequence that produced it.

## Searchability and encapsulation

One complete proposition per paragraph is preferred, because bounded source units are easier to search, compare, move, and review.

A proposition with a declared local warrant and its `because` clause should remain on one physical source line when practical, because exact-text tools should retrieve the claim and warrant together.

Blank lines should separate proposition paragraphs, because visible source boundaries reduce accidental partial edits.

One canonical term should name each concept that the author chooses to expose for cross-reference, because changing synonyms and unqualified pronouns can hide related propositions from search.

Canonical proposition names should be introduced at their authoritative definitions rather than maintained in a separate registry, because a duplicate name index can get out of sync with the content it names.

Cross-document references should qualify the owning artifact when the same canonical name could exist in more than one authority, because exact names must remain unambiguous across the design chain.

Directional terms such as `depends on`, `constrains`, `supports`, `verifies`, `contradicts`, and `supersedes` should be explicit for represented relationships, because readers and tools need to recover change impact.

Editor soft wrapping should be preferred over inserted hard line breaks inside one proposition, because visual readability need not fragment the searchable source unit.

A justified departure from the preferred physical form is allowed when the alternative materially improves reasoning clarity, because searchability supports rather than overrides semantic integrity.

## Document obligations

A WELL-governed design document should represent purpose, scope, authority, grounds, constraints, decisions, qualifications, consequences, checks, and unresolved matters, because those structural elements make the document inspectable, while meaning-aware review decides whether the represented design is complete.

An inapplicable obligation may be omitted explicitly or by clear structure, because mandatory empty sections would violate Lean without preserving meaning.

Meaning-aware design review should verify that current authority and historical evidence are clearly distinguished where relevant, because WELL does not define a marker syntax or decide the substantive classification.

Meaning-aware design review should verify ownership of normative meaning and executable proof, because WELL does not discover all normative meanings or determine whether ownership is complete or correct.

## Conformance and verification

A design document is WELL-conformant only when its mechanically checkable structure satisfies the unconditional WELL rules, because WELL conformance must be decidable from the exact document and mechanical checker observations alone.

`mechanical-applicability` — A rule affects WELL PASS/FAIL only when both its applicability and satisfaction can be determined from exact document bytes using syntax the canonical WELL checker deterministically recognizes, because semantic author intent cannot be an input to a deterministic conformance result.

The canonical WELL checker is the executable specification for deterministic mechanical interpretation, because WELL prose fixes the checkable obligations and their semantic boundary while the checker's own deterministic implementation, not additional WELL prose, fixes exact parsing and classification detail.

Ordinary Markdown remains the default document form, because WELL adds a sentence-level warrant obligation and canonical-naming discipline without replacing Markdown's own syntax.

WELL should not gain new author-visible syntax merely to make mechanical classification easier, because only a demonstrated authoring ambiguity, not implementation convenience, justifies a new visible convention.

Those mechanical rules include the literal `because` in every syntactically classified prose sentence, valid canonical names for definitions that appear, canonical-name uniqueness, exact canonical references, missing-reference detection, mechanically identifiable layout rules, and mechanically detectable duplicate identifiers or malformed structural notation, because these properties can be checked without deciding whether the represented design meaning is good, true, sufficient, coherent, or correct.

A mechanical sentence checker is required as an aid, because a complete pass over a large document is easy to perform inconsistently by inspection alone.

A mechanical link checker must verify canonical-name uniqueness, exact references, and missing targets for canonical names that appear, because these properties are mechanically inspectable without judging whether additional names or edges should exist.

The checker may ignore only the structural syntax categories named above and subordinate list items matching the stated punctuation rule, because broad semantic exemptions can hide prose sentences.

WELL names each structural syntax category and cross-document reference form without prescribing its parsing grammar, because the canonical WELL checker owns deterministic recognition and classification, and checker implementation details and Markdown/parser edge cases need not be duplicated normatively in WELL prose.

The checker must deterministically report every skipped or exempted construct and the mechanical rule that excluded it, because an unreported exemption would make the mechanical result irreproducible.

If the checker cannot mechanically determine whether a construct is exempt, it must report that unresolved mechanically undecidable case as REVIEW rather than silently count it as a passing exemption, because semantic review cannot convert an unknown mechanical classification into WELL conformance.

A mechanical checker result must identify the exact artifact, checker identity and version, applied mechanical rules, skipped or exempted constructs, violations, and unresolved mechanically undecidable cases, because the mechanical result must be reproducible from explicit inputs and observations.

Repository residence, ongoing maintenance, and CI integration are requirements only when the governing document states them explicitly, because reviewers must not strengthen a verification gate beyond the properties that the document actually protects.

A zero-violation WELL result establishes only mechanical WELL conformance and does not establish design acceptance, because substantive design judgment belongs to a separate meaning-aware review under the governing project's acceptance process.

Meaning-aware review considers whether warrants are relevant rather than ceremonial or circular, qualifications and assumptions are represented correctly, ownership and authority are correct, propositions cohere with their governing inputs, and material contradictions or unresolved design blockers remain, because design acceptance requires interpretation beyond document structure.

The governing project determines who or what performs the meaning-aware review, the review method, and the acceptance or signing gate, because WELL defines the document-structure contract without prescribing a reviewer or duplicating another authority's methodology.

Mechanical WELL conformance and a separate meaning-aware design review may both be required before the governing project accepts or signs the exact design artifact, because acceptance or signing is a project-governance decision rather than a WELL result.

Acceptance or signing does not prove empirical claims true, the design optimal, the implementation correct, or future realization conformant, because implementation verification and qualification remain downstream activities governed through the Design Authority Chain.

Mechanical WELL checking can identify malformed structure, broken canonical links, duplicate identifiers, and other mechanically detectable violations, because those properties are observable without substantive design judgment.

Meaning-aware design review may inspect whether warrants actually support their propositions, whether assumptions and qualifications are represented correctly, whether authority and dependencies are coherent, whether contradictions or unresolved blockers remain, and whether the design meaning should be accepted, because those judgments belong to the governing project's separate acceptance process.

WELL conformance cannot prove evidence true, inference valid, context complete, or a design correct or optimal, because inspectable reasoning is not the same as correct reasoning.

## Application

Use WELL in three separate stages, because authoring guidance, mechanical checking, and project acceptance have different owners:

1. Authoring guidance: establish purpose and authority, choose proposition boundaries, expose assumptions and qualifications, consolidate rationale, and decide which canonical names, checks, and graph relationships make the design inspectable, because these semantic authoring acts do not determine WELL PASS/FAIL.
2. Mechanical WELL checking: run the sentence and link checkers against the exact artifact, validate every syntax category and canonical reference that appears, and record every exemption and unresolved mechanically undecidable case, because only mechanically applicable rules determine WELL PASS/FAIL.
3. Project review: provide the exact artifact and mechanical result to the separately governed meaning-aware design review when required, because project governance decides acceptance or signing and implementation qualification remains downstream.

## Examples

`Use event sourcing` is a meaning-aware review concern when asserted alone, because the sentence has no represented local warrant even though a checker cannot decide whether a warrant is semantically needed.

`Use event sourcing for the audit ledger, because immutable history is required for reconstruction` has the required literal token, because the example represents a claim and a stated warrant in one proposition.

`Boundary is the validation façade` is a meaning-aware review concern when asserted alone, because a checker cannot decide whether a definition needs a reason beyond the literal sentence structure.

`Boundary means the validation façade, because later interface rules assign every trust transition to that role` is locally warranted, because the definition includes its architectural function.

Repeating `because the controller must remain deterministic` after separately represented rules is a meaning-aware review concern when the author has not represented distinct warrants, because a checker cannot decide whether the rules are semantically unrelated.

A warranted introductory sentence may govern a list of subordinate fields, because the fields are structural components of the proposition rather than independent claims.

`connected-reasoning-graph` illustrates a useful canonical name when other propositions reference that rule, because it remains meaningful after section movement and reveals what the dependency concerns.

`A-17` is a poor canonical name when a stable semantic name is available, because insertion or reordering can make the identifier misleading while preserving no design meaning.

## Self-application

Every syntactically classified prose sentence in this document contains the literal `because`, because sentence-level warrant representation is WELL's primary mechanical encapsulation rule.

Every sentence-rule exemption in this document is limited to the structural syntax categories named above and the list-fragment punctuation rule, because the standard must not evade its own rule through an unclassified semantic exemption.

The document uses canonical definitions and paragraph-sized source units, because self-application must demonstrate exact search, extraction, and modification structure.

The names `stable-semantic-references`, `name-only-when-useful`, `connected-reasoning-graph`, and `detached-graph-review` demonstrate exact canonical cross-reference without naming every sentence, because WELL must demonstrate mechanically resolvable links and bounded naming.
