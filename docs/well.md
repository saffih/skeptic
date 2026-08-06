# WELL — Warranted, Explicit, Lean, Linked

WELL is the normative profile for architecture, software-design, architecture-decision, and equivalent design documents, because design meaning must remain inspectable and resistant to drift.

WELL governs this document, because a design standard must demonstrate that its own requirements are usable.

## Scope and purpose

WELL applies to documents that define or justify a design, because their propositions must survive implementation, review, extraction, movement, and later modification.

WELL does not govern prompts, source code, reviews, reports, status updates, test output, runbooks, user documentation, or ordinary communication, because those artifacts serve different functions and require different forms.

Scope follows function rather than filename, because renaming an artifact must not silently extend or remove normative authority.

WELL protects document integrity, because unsupported claims, detached reasons, hidden qualifications, duplicated rationale, and disconnected checks can cause a later edit to change the design unintentionally.

WELL governs design-writing structure rather than Skeptic review or executable qualification, because inspectable reasoning, adversarial criticism, and runtime proof are complementary authorities rather than substitutes.

WELL is not a proof system, a demand for hidden reasoning, or proof that a design is correct, because explicit structure can expose an error without resolving it.

## Self-contained design propositions

A design proposition is the smallest prose unit that independently asserts a design fact, definition, requirement, decision, qualification, consequence, check, assumption, unknown, or relationship, because independently changeable meaning needs an independently recoverable warrant.

A WELL-governed design document expresses each independent design proposition as a self-contained unit, because searching, quoting, moving, reviewing, or modifying the proposition must not separate its claim from its reason.

Every complete prose sentence must contain the literal word `because`, because the proposition and its warrant must remain recoverable when the sentence is read outside its surrounding prose.

The `because` clause must state a concrete local reason, protection, consequence, dependency, or inclusion rationale, because ceremonial or circular wording cannot preserve design integrity.

A clause that merely cites the standard or labels the proposition important is nonconforming, because it does not explain why the proposition belongs in the design.

Headings, metadata fields, schemas, tables, code, formulas, diagrams, identifiers, state vocabularies, and genuine list fragments do not require their own `because`, because they are structural notation rather than independent prose propositions.

A list may inherit one explicit warrant from its introductory sentence only when every child item is a subordinate fragment, because an independently meaningful list sentence must preserve its own reason.

A complete prose sentence inside a list must contain its own literal `because`, because list formatting does not remove the sentence's independent meaning.

A quoted nonconforming sentence may omit `because` only when the surrounding warranted proposition identifies it explicitly as a failure example, because examples must be able to display the defect they explain.

WELL formation protects modification integrity, because cohesive and locally warranted propositions can be searched, extracted, moved, compared, replaced, and updated without silently losing the reasoning that constrains them.

## Proposition roles

Every retained design proposition performs at least one necessary role, because nonoperative prose cannot justify maintenance:

- ground: objective, constraint, observation, authority, assumption, or unknown
- definition: stable meaning needed by later reasoning
- proposition: design claim, requirement, recommendation, or decision
- qualification: scope, condition, boundary, or exception
- consequence: effect, cost, risk, or trade-off
- check: evidence, acceptance, verification, or falsification path
- open item: unresolved unknown, conflict, or decision
- structure: explicit connection or navigation needed by the reasoning chain

A proposition may combine roles when the roles share one reason, because forced separation can add noise without improving integrity.

A proposition must be split when its independently changeable claims need different reasons, because one `because` clause must not conceal unrelated decisions.

A proposition with no necessary role must be removed, because unnecessary prose increases search noise and drift.

## Warrant termination

A support path may terminate at an objective, constraint, direct observation, authoritative input, stable definition, explicit assumption, or explicit unknown, because finite design documents need legitimate stopping points.

A ground or definition still needs a local inclusion reason, because being foundational does not explain why that particular foundation is required here.

Assumptions and unknowns must remain labelled, because their presence in a design document does not make them true or resolved.

Reasons do not require infinite recursive justification, because an explicit terminal ground is sufficient for a finite recoverable design chain.

## WELL dimensions

**Warranted.** A design claim, requirement, recommendation, or decision states sufficient relevant grounds, because an unsupported proposition cannot be assessed or safely preserved.

**Explicit.** A proposition states every scope, condition, assumption, limit, exception, consequence, conflict, and unknown whose omission could change implementation or interpretation, because hidden qualifications create false certainty.

**Lean.** A proposition uses the shortest form that preserves operative meaning and its reason, because excess text hides distinctions and creates duplicate places to update.

Necessary reasoning, qualification, uncertainty, consequence, and verification must not be removed for brevity, because compression without integrity creates false simplicity.

**Linked.** Relationships among propositions, grounds, qualifications, consequences, checks, and open items remain recoverable, because isolated sentences cannot form a maintainable design.

`stable-semantic-references` — A material proposition that is referenced outside its paragraph should use one unique lowercase kebab-case canonical name enclosed in backticks, because semantic names remain grep-friendly and stable when sections move.

`name-only-when-useful` — A proposition should remain unnamed when no external reference or graph inspection needs a name, because naming every proposition would add ceremony contrary to Lean.

A canonical name describes the proposition's meaning rather than its location and should not use numeric or positional identifiers when a stable semantic name is sufficient, because positional identifiers drift without conveying design meaning.

Every canonical reference repeats the exact backticked name, because exact search should locate the definition and every dependent proposition.

Renaming a canonical proposition is a material edit that updates every reference, because the name is the stable key in the document's reasoning graph.

Another unambiguous representation may replace canonical names only when it provides equal or better stability, searchability, and graph inspection, because formatting serves design integrity rather than becoming an end in itself.

## Normative writing rules

Each material proposition states its concrete local warrant and explicit support terminus, because implementation must not depend on distant or guessed intent.

Each material qualification and consequence remains attached to the proposition it constrains, because extraction or movement must not silently broaden the claim.

Each checkable proposition identifies a verification or falsification path directly or through an explicit canonical link, because a design claim must be able to fail.

Shared terms and reusable rationale have one canonical definition with explicit references from dependent propositions, because repeated definitions and reasons can diverge.

`connected-reasoning-graph` — Every material proposition connects directly or transitively to an authoritative input, purpose, constraint, assumption, or explicit unknown and to a decision, consequence, check, or downstream obligation when applicable, because a design document should form one recoverable reasoning graph rather than disconnected assertions.

`detached-graph-review` — A disconnected proposition or cluster remains review-required until it is linked, moved to the artifact that owns it, removed, or explicitly established as a separate design scope, because detachment usually reveals a missing relation, duplicate authority, or wrong document level.

Enough reasoning remains local to make an extracted proposition coherent, because a reference cannot substitute for the proposition's immediate reason.

Nonoperative content and duplicate authority are removed, because WELL should improve understanding rather than create ceremonial documentation.

## Misunderstanding resistance

A proposition may be recoverable yet still need clarification when a competent reader can reasonably derive a materially different interpretation, because reliable design communication should not depend on reconstructing an unstated controlling contrast.

When related concepts differ by timing, scope, authority, lifecycle position, or evidentiary role, their canonical definitions must state the controlling contrast explicitly, because separate names may not reveal which distinction governs later rules.

A rejected review finding may still justify a narrow clarification when it exposes a plausible and materially consequential misunderstanding, because rejecting the finding establishes the stronger interpretation but does not prove that the document communicated that interpretation reliably.

Adding such a clarification does not retroactively validate the rejected finding, because the clarification improves misunderstanding resistance rather than admitting that both interpretations were authorized.

Clarification is required only when the alternative reading is plausible to a competent reader, would materially change implementation or verification, and can be eliminated through one small canonical distinction, because documenting remote or harmless misunderstandings would violate Lean.

The clarification must be placed at the canonical definition or controlling rule rather than repeated at every dependent use, because one authoritative contrast prevents recurrence without creating duplicate authority or defensive prose.

A named reusable schema, record, manifest, or structure must be introduced explicitly at its canonical definition before dependent propositions use that name, because recoverable fields do not by themselves establish the name's authoritative referent.

A requirement whose satisfaction depends on the order of edits, reviews, approvals, or publications must identify the observable evidence that establishes that order, because a final snapshot proves resulting state but ordinarily cannot prove the sequence that produced it.

## Searchability and encapsulation

One complete proposition per paragraph is preferred, because bounded source units are easier to search, compare, move, and review.

A material proposition and its local `because` clause should remain on one physical source line when practical, because exact-text tools should retrieve the claim and warrant together.

Blank lines should separate proposition paragraphs, because visible source boundaries reduce accidental partial edits.

One canonical term should name each material concept, because changing synonyms and unqualified pronouns can hide related propositions from search.

Canonical proposition names should be introduced at their authoritative definitions rather than maintained in a separate registry, because a duplicate name index can get out of sync with the content it names.

Cross-document references should qualify the owning artifact when the same canonical name could exist in more than one authority, because exact names must remain unambiguous across the design chain.

Directional terms such as `depends on`, `constrains`, `supports`, `verifies`, `contradicts`, and `supersedes` should be explicit when material, because readers and tools need to recover change impact.

Editor soft wrapping should be preferred over inserted hard line breaks inside one proposition, because visual readability need not fragment the searchable source unit.

A justified departure from the preferred physical form is allowed when the alternative materially improves reasoning clarity, because searchability supports rather than overrides semantic integrity.

## Document obligations

A WELL-governed design document establishes its purpose, scope, authority, grounds, constraints, decisions, qualifications, consequences, checks, and unresolved matters when applicable, because those elements make the design chain inspectable.

An inapplicable obligation may be omitted explicitly or by clear structure, because mandatory empty sections would violate Lean without preserving meaning.

A document must distinguish current authority from historical evidence, because lineage must inform the design without competing with it.

A document must identify which artifact owns each normative meaning and which artifact owns executable proof, because duplicated authority creates drift.

## Conformance and verification

A design document is WELL-conformant only when every complete prose sentence contains a substantive literal `because`, every material proposition is sufficiently warranted and qualified, canonical references are exact and unique when used, no unexplained disconnected reasoning component remains, reasoning links and checks are recoverable, duplicate authority and nonoperative prose are absent, and unresolved matters remain unresolved, because partial compliance cannot preserve the design chain.

A mechanical sentence checker is required as an aid, because a complete pass over a large document is easy to perform inconsistently by inspection alone.

A mechanical link checker must verify canonical-name uniqueness, exact references, and missing targets when a document uses canonical names, because these properties are mechanically inspectable even though the adequacy of the reasoning graph still requires human review.

The checker must ignore only genuine structural notation and subordinate fragments, because broad exemptions can hide independent propositions.

Every mechanical exemption requires manual review, because Markdown classification cannot determine semantic independence reliably.

A mechanical checker result must identify the exact reviewed artifact, the checker source or identity, the applied rules, and every exemption, because human review cannot reproduce or inspect a pass whose inputs or skipped content are hidden.

Repository residence, ongoing maintenance, and CI integration are requirements only when the governing document states them explicitly, because reviewers must not strengthen a verification gate beyond the properties that the document actually protects.

Human review remains required after a zero-violation checker result, because the presence of `because` does not prove that the warrant is relevant, sufficient, true, local, or non-circular.

WELL review can identify unsupported propositions, hidden assumptions, missing qualifications, broken links, repeated rationale, and removable prose, because those defects are structurally inspectable.

WELL conformance cannot prove evidence true, inference valid, context complete, or a design correct or optimal, because inspectable reasoning is not the same as correct reasoning.

## Application

Apply WELL in this order, because early identification of proposition boundaries prevents later ceremonial repair:

1. establish document purpose and authority
2. identify independently changeable propositions
3. identify each proposition's concrete ground, qualification, consequence, and check
4. split propositions whose claims require different reasons
5. expose assumptions, unknowns, conflicts, and authority boundaries
6. consolidate repeated definitions and rationale behind canonical links
7. assign unique lowercase kebab-case canonical names only to propositions that need cross-reference or graph inspection
8. repeat each canonical name exactly in backticks at every reference
9. inspect the reasoning graph and resolve every unexplained disconnected component
10. convert only genuine subordinate enumerations into fragments under one warranted introduction
11. remove nonoperative and duplicated prose
12. run the sentence and link checkers and inspect every exemption
13. review the complete document for cross-section contradiction and semantic drift

## Examples

`Use event sourcing` is nonconforming when asserted alone, because the sentence states a design choice without its design ground.

`Use event sourcing for the audit ledger, because immutable history is required for reconstruction` is locally warranted, because the sentence keeps the choice and the protected need in one proposition.

`Boundary is the validation façade` is nonconforming when asserted alone, because the definition does not explain why the role is needed.

`Boundary means the validation façade, because later interface rules assign every trust transition to that role` is locally warranted, because the definition includes its architectural function.

Repeating `because the controller must remain deterministic` after unrelated controller rules is nonconforming, because one reason cannot justify independently changeable claims merely by repetition.

A warranted introductory sentence may govern a list of subordinate fields, because the fields are structural components of the proposition rather than independent claims.

`connected-reasoning-graph` illustrates a useful canonical name when other propositions reference that rule, because it remains meaningful after section movement and reveals what the dependency concerns.

`A-17` is a poor canonical name when a stable semantic name is available, because insertion or reordering can make the identifier misleading while preserving no design meaning.

## Self-application

Every complete prose sentence in this document contains a substantive literal `because`, because sentence-level local warrant is WELL's primary encapsulation mechanism.

Every structural exemption in this document is limited to headings or subordinate list fragments, because the standard must not evade its own rule through formatting.

The document uses canonical terms and proposition-sized paragraphs, because self-application must demonstrate cohesive search, extraction, and modification units.

The named propositions `stable-semantic-references`, `name-only-when-useful`, `connected-reasoning-graph`, and `detached-graph-review` demonstrate exact semantic cross-reference without naming every sentence, because WELL must demonstrate Linked and Lean together.
