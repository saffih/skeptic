# Sequential Target Task MVP Architecture Description

**Repository:** `saffih/skeptic`
**Governing Inputs:** `plans/stt-mvp-governing-inputs.md`
**Downstream owner:** Software Design Description under `docs/design-authority-chain.md`
**Document profile:** `docs/well.md`
**Scope:** STT MVP system-wide semantics, boundaries, invariants, and architecturally significant decisions

This document owns only system-wide meaning that every conforming realization must preserve, because schemas, directories, algorithms, adapter protocols, command payloads, host probes, and test construction belong to the Software Design Description or a bounded Implementation Plan.

A lower-level decision discovered while discussing architecture must be recorded in the Software Design Description rather than retained here, because `simplicity-and-robustness` and WELL Lean require architecture to contain only meaning that constrains every conforming realization.

## Architecture at a glance

```text
immutable mission and authority
            ↓
         Planner
            ↓ accepted finite Plan and route choices
         Boundary
            ↓ one admitted step at a time
execution entity or child Task
            ↓ persisted result and evidence
         Boundary
            ↓
        Validator
        ↙       ↘
     finish   fresh Round
```

### `sequential-control-loop` — Sequential control loop

The `product-identity` and `product-objective` Governing Inputs define STT as a persisted sequential control loop around trusted reasoning and admitted effects, because one understandable path from mission through evidence to judgment is the smallest architecture that satisfies `simplicity-and-robustness`.

STT coordinates admitted work rather than containing the target or guaranteeing completion, rollback, exclusivity, or a fixed total budget, because `non-goals` bounds the claims made by `sequential-control-loop`.

## Lifecycle vocabulary

The architecture uses the following lifecycle entities, because one stable vocabulary makes the control loop and its ownership understandable:

| Entity | Meaning |
|---|---|
| Run | one frozen root mission, authority, target workspace, store location, policy, routing constraints, and selected prior evidence |
| Task | one immutable mission, authority, required outputs, and lineage inside a Run |
| Round | one planning attempt, any accepted Plan execution, and validation for the same Task |
| Plan | one finite ordered set of admitted steps produced by Planner |
| Operation | one Boundary-admitted semantic or effectful launch |
| Child Task | a new Task selected by Planner whose authority preserves or narrows inherited authority |

## `immutable-mission-and-authority` — Immutable mission and authority

A Run freezes its root mission, required outputs, operational authority, target workspace, authoritative store location, policy constraints, routing constraints, and selected prior evidence before semantic execution, because `product-objective` requires one accountable basis for `sequential-control-loop`.

A Task preserves one immutable mission, authority, required outputs, and lineage across every Round, because `trusted-semantic-roles` and `validator-owned-outcome` must reason about the same obligation rather than a moving target.

Changing the root mission, authority, target workspace, store location, or governing policy creates a new Run, because same-Run continuation must preserve `immutable-mission-and-authority`.

Controller semantics and runtime identity remain fixed for the Run, because target mutation or deployment drift must not replace the component enforcing `boundary-mediated-transitions` during the same lifecycle.

A child Task may receive any mission selected by Planner, including the same mission as an ancestor, but may only preserve or narrow inherited operational authority, because semantic decomposition may vary while `admitted-operational-authority` may not expand implicitly.

## `trusted-semantic-roles` — Trusted semantic roles

Lead advances the uniquely implied lifecycle action without inventing semantic work, because `one-active-frontier` needs deterministic orchestration while `trusted-thinking` assigns judgment elsewhere.

Planner interprets the current Task mission and committed history, creates a finite ordered Plan or declines when it sees no useful path, and may create child Tasks, because `trusted-thinking` assigns decomposition to trusted reasoning rather than mechanical novelty rules.

Validator independently judges the Task from committed admissible evidence and decides whether the Task finishes or receives another Round, because `trusted-thinking` and `honest-outcomes` separate mission meaning from execution return.

Workers and commands perform accepted steps without owning parent-Task judgment or lifecycle state, because `boundary-mediated-transitions` centralizes trust transitions and `validator-owned-outcome` reserves Task judgment for Validator.

Persisted reports, target content, prior evidence, and tool output are data rather than higher-authority instructions, because access to evidence must not alter `immutable-mission-and-authority`, `boundary-mediated-transitions`, or the accepted Plan.

## `context-handling` — Context handling

Durable substantive state crosses semantic-operation boundaries through authoritative filesystem artifacts and exact references rather than inherited model context, because `context-rules-adoption` requires reusable state to remain inspectable without repeatedly occupying live context.

Each semantic operation receives a deliberately bounded working set selected by the responsible semantic role or fixed by an accepted Plan and expands that set when uncertainty, contradiction, missing support, or a required fresh or complete review demands more evidence, because context economy must remain subordinate to the obligation being judged.

Planner and Validator retain semantic authority over evidence sufficiency while Boundary enforces only structural admission and binding, because `trusted-semantic-roles` must not be replaced by a mechanical context-minimization rule.

When substantial interpretation is likely to be reused and expected downstream rereading savings materially exceed creation cost and omission risk, the interpreting role returns a source-bound digest with stable search anchors and exact source references for Boundary to persist, because `context-rules-adoption` requires reusable understanding to reduce later reading cost without moving persistence authority out of `boundary-mediated-transitions`.

Boundary persists an admitted digest as derived navigation data bound to its authoritative sources, because `boundary-mediation` owns persistence and `context-handling` must not create an alternate authoritative path.

A source-bound digest has no greater authority than its sources and never satisfies an obligation that requires fresh, complete, independent, absence-sensitive, contradiction-sensitive, or decision-critical source review, because derived context may accelerate retrieval but may not become a second source of truth.

## `one-active-frontier` — One active frontier

Lead advances one deepest unresolved lifecycle frontier at a time and executes child Tasks depth-first before returning to their parent, because `sequential-lifecycle` makes ordering and ownership explicit without internal concurrency.

Each Round consists of one planning attempt, execution of any accepted Plan, and validation when settlement permits, because `one-active-frontier` connects `trusted-semantic-roles`, `boundary-mediated-transitions`, and `validator-owned-outcome` without pretending that every Planner returns a Plan.

An accepted Plan is immutable and ordered, because `one-active-frontier` and `recovery-from-known-facts` require one stable step sequence after admission.

A Validator request for continuation creates a fresh Round of the same Task using accumulated committed history, because `semantic-continuation` permits continuation while `immutable-mission-and-authority` preserves the Task obligation.

Separate Runs may overlap only under caller responsibility, because `sequential-lifecycle` constrains one Run while `non-goals` excludes coordination of every external writer.

## `boundary-mediated-transitions` — Boundary-mediated transitions

Boundary is the sole façade between semantic decisions, effectful execution, and authoritative state, because `boundary-mediation` requires one mechanical owner for every trust transition in `sequential-control-loop`.

Boundary validates identities and operational authority, admits Plans, routes, target access, and launches, binds returned results, evidence, and child outcomes, and persists lifecycle transitions, because each action can otherwise change trusted meaning or capability outside `immutable-mission-and-authority`.

Boundary enforces structure and integrity without replacing Planner or Validator judgment, because `trusted-semantic-roles` assigns semantic adequacy and mission sufficiency to trusted reasoning.

Only results and artifacts bound to the admitted operation or child Task become accepted evidence, because plausible output from another request must not enter `authoritative-committed-history` or influence `validator-owned-outcome`.

No provider, command, Worker, child Task, or other execution mechanism launches or publishes accepted lifecycle evidence outside Boundary, because bypassing `boundary-mediated-transitions` would invalidate `admitted-operational-authority` and `authoritative-committed-history`.

## `simplest-adequate-execution` — Simplest adequate execution

Planner uses a deterministic mechanism when a step needs no semantic judgment and otherwise selects the lowest permitted agent capability it judges adequate, because `execution-economy` makes semantic difficulty part of planning rather than a mechanical routing algorithm.

Planner and Validator operate at or above their configured trusted minimum capability, because `planning-and-validation-capability` protects the reasoning roles whose errors would undermine `sequential-control-loop`.

Mission and Run policy may constrain permitted providers, capability levels, cost preference, or quality preference, because `mission-routing-constraints` bounds Planner freedom without prescribing every route.

Boundary rejects an unpermitted route and never silently substitutes another route, because `boundary-mediated-transitions` owns admission while Planner owns the choice made under `simplest-adequate-execution`.

The architecture defines no provider names, tier labels, prices, token thresholds, or route-selection algorithm, because those volatile choices belong to the Software Design Description under the variation allowed by `execution-economy`, `planning-and-validation-capability`, and `mission-routing-constraints`.

## `admitted-operational-authority` — Admitted operational authority

Every effectful step executes only through authority admitted by the accepted Plan and inherited from `immutable-mission-and-authority`, because `boundary-mediation` and `boundary-mediated-transitions` forbid operational capability from appearing implicitly.

Every STT-owned name has one canonical case-sensitive spelling, because `canonical-naming` prevents internal ambiguity while exact character and separator rules remain software design.

Every admitted target effect must identify the intended object inside its granted scope or fail before mutation, because `target-path-authority` protects authority independently from host-specific path mechanisms.

A reported effect outside admitted responsibility scope stops later Plan steps and remains visible to Validator, because continuing would compound a known violation of `admitted-operational-authority` while `honest-outcomes` requires honest evidence.

STT does not claim to detect every unreported effect or contain arbitrary process behavior, because `non-goals` limits `admitted-operational-authority` to admitted and observed operations.

## `authoritative-committed-history` — Authoritative committed history

STT persists complete known Run history as ordinary readable files plus append-only ledgers under an authoritative Run root outside the live target, because `context-rules-adoption` requires durable authoritative context that target work cannot rewrite.

Accepted lifecycle facts are immutable and state is derived from committed history rather than an independently mutable cursor, because `recovery-from-known-facts` needs one source of truth.

Each semantic operation reasons from a stable committed history snapshot and later committed facts become available to later operations, because one operation must not observe a moving lifecycle basis.

Planner and Validator may inspect the committed Run history while Planner may grant a Worker only the history access needed for its accepted step, because `trusted-semantic-roles` needs sufficient evidence and `admitted-operational-authority` limits execution authority.

Indexes, source-bound digests, summaries, and compact receipts may aid navigation but never replace the underlying committed records, because `context-handling` rejects a second curated source of truth.

Externally mutable target facts are re-observed before authoritative use while accepted Run evidence remains immutable, because `honest-outcomes` requires evidence to identify what was actually known when a decision was committed.

Selected prior-Run evidence may enter a new Run as immutable advisory data without merging lifecycle histories or changing current authority, because `immutable-mission-and-authority` requires one current Run basis while accumulated evidence may still inform `trusted-semantic-roles`.

## `validator-owned-outcome` — Validator-owned outcome

Validator states whether the Task is satisfied, not satisfied, or indeterminate and separately chooses whether to finish or repeat, because `trusted-thinking` and `honest-outcomes` require semantic outcome and lifecycle continuation to remain explicit.

A satisfied Task cannot repeat, because satisfaction means no remaining mission gap under `immutable-mission-and-authority`.

Validator may judge from accepted results, verified artifacts, child outcomes, failures, a Planner decline, and other committed admissible evidence, because transport success is neither necessary nor sufficient for Task-level meaning.

Validator may request another Round after any unsatisfied or indeterminate settled state, because `semantic-continuation` assigns continuation judgment to Validator rather than an architecture-defined repetition count or novelty test.

A settled Planner or execution operational failure becomes committed evidence, and a settled execution operational failure stops later Plan steps before Validator judges the Task, because `honest-outcomes` separates operational failure from an accepted semantic step result without allowing later work to compound an operation that produced no accepted result.

A settled Validator failure stops the Task without a semantic judgment, because no lower-authority role may fabricate `validator-owned-outcome`.

A child Task semantic outcome becomes its parent step result, because child judgment is accepted evidence for the parent Plan.

A settled child stop without semantic judgment becomes parent operational evidence and stops later parent steps while still permitting parent validation after settlement, because `honest-outcomes` must preserve operational absence of judgment without fabricating a child outcome.

An unsettled child state, or one whose activity or local settlement is unknown, blocks the enclosing Run before ancestor validation, because `one-active-frontier` and `honest-outcomes` forbid ancestor judgment while the child frontier may still change.

An invalid child state invalidates the enclosing Run before ancestor validation, because `authoritative-committed-history` and `honest-outcomes` forbid deriving ancestor state from untrustworthy child history.

No Validator launches while relevant work may still be active or its local settlement is unknown, because `one-active-frontier` forbids concurrent frontiers and `honest-outcomes` forbids judgment against changing effects.

## `recovery-from-known-facts` — Recovery from known facts

Resume advances only from committed facts, may launch an operation only when history establishes that no prior launch occurred, and may otherwise complete only uniquely implied non-effectful transitions, because `authoritative-committed-history`, `interrupted-effects`, and `honest-outcomes` forbid guessing whether an effect already occurred.

Relevant work whose activity or local settlement remains unsettled or unknown blocks later steps and validation, because `one-active-frontier` must not advance while the active frontier may still be changing state.

After relevant work is established settled, recovery may continue through fresh planning from committed facts without relaunching an operation whose prior launch occurred or remains uncertain, because `interrupted-effects` forbids blind effect replay without making semantic continuation itself non-resumable.

Corrupt, conflicting, or mutated authoritative history invalidates the Run, because `authoritative-committed-history` can no longer support deterministic derivation or trustworthy evidence.

Operator cancellation prevents new launches without rewriting already committed facts, because operational control must stop future work while preserving `authoritative-committed-history` and any valid evidence available to `validator-owned-outcome`.

## `qualification-boundary` — Qualification boundary

Mechanical qualification must falsify identity immutability, sequential ordering, Boundary exclusivity, route permission and non-substitution, operational authority, committed-state derivation, outcome handling, and interruption recovery, because the mechanical parts of `immutable-mission-and-authority`, `one-active-frontier`, `boundary-mediated-transitions`, `simplest-adequate-execution`, `admitted-operational-authority`, `authoritative-committed-history`, `validator-owned-outcome`, and `recovery-from-known-facts` must fail visibly.

Representative real-model evaluation must challenge planning, route adequacy, validation, continuation, history use, and stagnation, because deterministic tests cannot prove the semantic competence assigned by `trusted-semantic-roles`.

Real-model evaluation is evidence rather than a correctness guarantee, because finite cases cannot prove general reasoning reliability or universal minimum cost under `non-goals`.

The Software Design Description must define the shared mechanisms needed to realize every architecture proposition without adding or changing architecture, because `docs/design-authority-chain.md` permits downstream refinement only inside the variation allowed here.

A bounded Implementation Plan may begin only from unchanged accepted Governing Inputs, Architecture Description, and applicable Software Design Description, because realization must not invent missing system-wide or durable decisions.
