# Context Rules

Context Rules is the portable normative contract governing what enters, stays out of, and moves between semantic invocations, because a receiver's productive reasoning capacity is bounded while the durable material an obligation may legitimately draw on is not.

## Purpose

This document exists to keep an obligation's starting context sized for reasoning rather than for completeness, because a receiver that spends its capacity on arrival material has less of it left for the evidence and inference the obligation was created to produce.

This document is the single current owner of context-handling meaning for every artifact that adopts it, because two documents stating context obligations would let one be edited while the other still governs.

## Scope

These rules apply wherever information crosses from one semantic invocation to another, whether that crossing is a delegation, a succession, a resumption, or a handoff into a different system, because the constraint arises from the receiver's limit rather than from the mechanism that reached it.

These rules are host-independent and system-independent, because a contract that named one runtime's roles or one product's lifecycle could not be adopted by the other artifacts that need the same guarantees.

These rules govern context handling only and change no authority, because economizing on what a receiver reads must never become a way to weaken required evidence, freshness, completeness, or independence.

Role names, lifecycle stages, routing decisions, record schemas, and digest procedures belong to the adopting system rather than to this document, because fixing them here would force unrelated systems into one realization of a constraint they share only in principle.

## Authority and conformance

This document conforms to WELL in full, because the Design Authority Chain states that obligation unconditionally for any artifact that defines or justifies design, and this document defines a cross-cutting design constraint that other design artifacts are expected to adopt.

WELL and the Design Authority Chain own their own rules and are named here rather than restated, because copying their text into this document would create the duplicate authority both of them exist to prevent.

This document owns normative meaning only and owns no executable proof, because each adopting system verifies these rules against its own observable behavior rather than against a check this document could run.

Context Stewardship is the historical input from which this document was derived and which it is intended to replace, because one subject must end with exactly one current authority.

That replacement is incomplete while other artifacts still name Context Stewardship, and retiring those inbound references is a separate change, because a document cannot retire references held by artifacts it does not own.

## Grounds

The rules below answer four observations about receivers, each of which independently changes what a correct handoff looks like, because a contract built to answer only one of them would over-correct against the others:

- accessible information exceeding what one semantic invocation can productively consume;
- startup material and irrelevant bulk displacing the capacity that later reasoning and evidence need;
- relevance the producer already established, paid for a second time by a receiver forced to rediscover it;
- over-curation that starves the receiver of needed material or biases it toward the producer's reading, because curation must not make receiver authority merely nominal.

`finite-reasoning-capacity` — Context is finite reasoning capacity rather than a container to be filled, because every unit of it spent on arrival material is unavailable to the inference the obligation exists to perform.

## Capacity and reachable depth

Durable information may grow without bound while the active context of any single invocation must not have to grow with it, because otherwise every addition to the durable record would shrink the reasoning headroom of every later invocation.

Depth already authorized for an obligation stays reachable without being consumed wholesale, because `finite-reasoning-capacity` would otherwise force a choice between exceeding capacity and losing access to authorized evidence.

## Context Guide and Durable Store

`durable-store` — Substantial reusable semantic state is held in an authoritative store intended for selective retrieval rather than for whole reading, because the authoritative form must stay free to be as large as its subject requires.

`context-guide` — Substantial reusable semantic state also exposes a compact guide intended to be read whole for orientation, because a receiver must learn what exists and where it sits before it can retrieve selectively from `durable-store`.

A `context-guide` carries, as the material warrants, an abstract, the semantic terms in use with brief meanings, the relationships and qualifications that change how the material reads, and precise pointers or search handles into the authoritative depth, because those are the elements that let a receiver choose what to retrieve without first reading `durable-store`.

`guide-is-navigation-not-authority` — A `context-guide` is derived navigation and never competes with the material it points at, because a reader who resolved a disagreement in the guide's favor would be governed by a derivative instead of by the source.

A `context-guide` that is stale or contradicted by `durable-store` is repaired or withdrawn rather than trusted, because `guide-is-navigation-not-authority` leaves it without standing exactly when it disagrees.

## Retrieval

`retrieval-mechanism-not-normative` — Selective retrieval may be realized by ordinary files, by text search, by a structured index, by a database, or by any other mechanism the adopting system chooses, because the property this contract requires is that authorized depth stays reachable without wholesale consumption, and that property does not depend on how reaching is implemented.

Ordinary readable filesystem state is preferred where it is adequate, and that preference makes no particular storage engine or search tool a requirement, because a contract pinned to one tool would fail in systems that cannot adopt that tool while still satisfying `retrieval-mechanism-not-normative`.

## Preparation and sizing

A semantic producer whose output is expected to be reused prepares that output for its later consumer instead of leaving it in whatever shape production happened to end in, because the producer already holds the relevance knowledge the consumer would otherwise pay to rediscover.

`task-sized-entrance` — Preparation gives the receiver an entrance sized to its obligation, which is neither a dump of everything available nor a trail of clues requiring reconstruction, because each of those failures spends the receiver's capacity on work the producer could have done once.

Preparation is justified by expected reuse rather than performed by default, because material that no later invocation will read costs capacity to make and adds a second thing that must be kept true.

`concise-completeness` — Find the simplest clear rephrase of the whole relevant passage for which a competent independent receiver, using only the rephrase and its explicit references, can still correctly complete the same obligation under the same authority and evidence requirements without reconstructing omitted meaning; if that equivalence cannot be established, preserve the meaning or expose the conflict, because compression may reduce expression but not the receiver's obligation.

A table, schema, grammar, or reference is a valid simpler rephrase when it preserves that equivalence, because form may reduce expression without reducing the receiver's obligation.

## Receiver authority

`receiver-evidence-authority` — The receiver determines what evidence its obligation requires and may resolve and load any source already authorized for that obligation, because a starting context chosen by another party cannot be known in advance to be sufficient for the reasoning that follows.

Preparation therefore selects a starting point and never defines the limit of permitted evidence, because treating a curated entrance as an exhaustive one would revoke `receiver-evidence-authority` without anyone deciding to revoke it.

A receiver whose required evidence is unavailable or unauthorized exposes that condition instead of proceeding on what it holds, because a conclusion drawn from knowingly incomplete evidence misrepresents its own support.

## Semantic and control responsibility

`context-preparation-is-semantic-work` — Deciding what a later receiver needs is semantic work, because the decision depends on what the material means and on what the next obligation is for.

`control-plane-meaning-independence` — A control plane acts only on facts that are independent of meaning, such as identities, references, statuses, and fixed transitions, because any content judgement it made would be `context-preparation-is-semantic-work` performed by a role that by construction cannot assess it.

A control plane may enforce structural limits and check mechanical validity, and neither of those establishes semantic sufficiency, because a well-formed handoff can still carry the wrong material.

`durable-data-plane-minimal-control-plane` — Durable data plane, minimal control plane, and references that connect them preserve substantive semantic content across real boundaries, because recovery and continuation must not depend on model memory, inherited conversation, or semantic reconstruction.

Plans, findings, evidence, reports, decisions and their reasoning, research, work products, and implementation or verification outputs are substantive semantic data when a later invocation needs them, because their producing invocation may end before the receiver acts.

Persist that data before it crosses an invocation, delegation, interruption, recovery, or independent-review boundary, and pass receiver-resolvable references rather than its body through a coordinator, because the receiver needs durable authority while the coordinator need only connect it.

Control carries only the minimum coordination state—status, identity, routing, continuation, references, and small diagnostics—and control-plane roles do not absorb substantive content merely to coordinate it, because meaning remains with the semantic producer and receiver.

Information that does not need to cross a real boundary need not be persisted merely for form, because indirection without a recovery or receiver need adds cost without protection.

`durable-semantic-continuation` — Continuation across a boundary rests on durable state and resolvable references rather than on conversation residue, because the next invocation may be fresh, delayed, relocated, or restarted, and residue survives none of those.

A reference that crosses a boundary identifies its material precisely enough for the intended receiver to locate and read it, because a reference the receiver cannot resolve spends the capacity it was meant to save.

An unresolvable, ambiguous, or superseded reference is rebound or exposed rather than approximated, because guessing at a reference substitutes the receiver's invention for the authority that was supposed to govern.

Bounded inline material is legitimate where a reference would be unresolvable or would cost more than the material it replaces, because these rules protect capacity rather than indirection for its own sake.

## Observability

`observable-context-claims` — Runtime inheritance, concealed loading, isolation, and remaining capacity are asserted only when observable and are reported as `UNKNOWN` otherwise, because an unobservable property stated as fact lets a later decision rest on something nobody checked.

## Infeasibility

`context-blocker-not-escape-hatch` — An obligation that cannot be made feasible through proper sizing, selective retrieval, or semantic decomposition is exposed as a blocker, because quietly narrowing it instead would produce an answer whose weakness is invisible to everyone downstream.

Semantic work is never relocated into a control plane to escape a capacity failure, because `control-plane-meaning-independence` makes such a move a transfer of judgement to where it cannot be made rather than a way to make it feasible.

A capacity failure at admission is a failure to admit the work rather than proof that the semantic role fell short of what it was asked to do, because the two have different remedies and treating one as the other discards work that was already correct.

## Checks

Conformance is observable at the points below, because a context contract whose violations left no trace could not constrain anything:

| Rule | Observable check |
|---|---|
| `context-guide` and `durable-store` | the guide's pointers resolve, for the intended receiver, to the authoritative material they name |
| `guide-is-navigation-not-authority` | a decision that conflicts with the source is traceable to the source rather than to the guide |
| `task-sized-entrance` | the receiver reached its obligation without a rediscovery pass and without loading unrelated bulk |
| `concise-completeness` | a materially compressed version leaves an independent receiver able to satisfy the same obligation from the compressed material and its explicit references, under the same authority and evidence requirements, without reconstructing omitted meaning |
| `durable-semantic-continuation` | a fresh invocation given only the durable state and references continued the obligation |
| `receiver-evidence-authority` | an additional already-authorized source the receiver requested was reachable to it |
| `observable-context-claims` | each asserted inheritance, isolation, or fit claim cites its observation, or reads `UNKNOWN` |
| `context-blocker-not-escape-hatch` | an infeasible obligation produced an exposed blocker rather than a silently narrowed result |

## Unresolved matters

One matter is unresolved here: the artifacts that still name Context Stewardship are not updated by this document, because changing them belongs to the artifacts' own owners and to a separate change.

## Omitted obligations

This document states no schedule, no owner assignment, and no tooling requirement, because those are properties of an adopting system rather than of the portable contract, and stating them here would bind systems this document cannot verify.
