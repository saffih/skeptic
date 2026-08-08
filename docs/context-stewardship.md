# Context Stewardship Contract

`context-stewardship` treats model context as a scarce execution resource that must remain sufficient for the current obligation and useful to the next agent, because correctness suffers both when context is flooded and when necessary evidence is removed.

This contract owns portable context-handling and bounded-orchestration rules only, because the host workflow must retain task authority, completion semantics, mutation authority, and any stricter review obligations.

When a host adopts this contract, host-specific authority and required fresh or complete reads remain controlling, because context economy must never weaken evidence, permission, or completion rules.

## Core

### `filesystem-offload` — Filesystem offload

Durable substantive state belongs in authoritative readable files or explicitly authorized task artifacts rather than retained model context, because reusable state should survive invocation boundaries without being repeatedly copied through prompts.

An agent retains only the substantive content needed for its current bounded reasoning and otherwise retains exact artifact references, because knowing where authoritative information is should normally cost less context than carrying the information itself.

### `artifact-reference` — Artifact reference

Substantive inputs and outputs cross agent boundaries by exact artifact reference rather than body copying when a reference is sufficient, because reference handoff preserves one inspectable source while avoiding repeated context cost.

A reusable reference identifies an authorized artifact and, when economically observable, its content identity such as a hash or version; it may identify an exact fragment when only part of the artifact is admitted, because later consumers must detect stale, ambiguous, or changed evidence.

Missing, stale, ambiguous, changed, or unauthorized references block reuse until rebound, because context savings cannot justify guessing which evidence was intended.

### `bounded-working-set` — Bounded working set

Each semantic invocation receives a deliberately bounded working set judged sufficient for its obligation by the responsible semantic role or fixed by an already-authorized host plan, because unrelated history wastes context while evidence sufficiency is a semantic judgment.

A semantic role expands its working set when uncertainty, contradiction, missing support, or a host-required fresh or complete review demands more evidence, because the smallest context is not better when it prevents the obligation from being discharged reliably.

A control plane may enforce structural admission but must not decide semantic evidence sufficiency, because context isolation would be broken if routing mechanics interpreted domain evidence.

### `source-bound-digest` — Source-bound digest

An agent that has already paid to understand substantial reusable material leaves one source-bound digest to an admitted output path in the same invocation when expected downstream rereading savings materially exceed the creation cost and omission risk, because reusable understanding should not be needlessly recomputed without widening write authority.

The digest is the smallest faithful downstream-useful derivative rather than a fixed-size summary, because compression should follow the likely reuse obligation rather than an arbitrary token target.

The digest identifies its exact authoritative source references and preserves material conclusions, uncertainty, supporting and disconfirming evidence, and retrieval anchors, because downstream agents need a cheap path back to evidence that can confirm or refute it.

Store the digest adjacent to its authoritative result as `<source-name>.digest.md` when the host layout permits or link it through a deterministic artifact reference otherwise, because one predictable derivative name makes downstream discovery cheap without creating multiple compression levels.

A digest has no greater authority than its sources and never substitutes for a source read required for freshness, completeness, absence, contradiction, independent review, or decision-critical support, because derived context must not become a second source of truth.

Do not launch a separate compressor by default, derive a digest from another digest, or generate a digest for material that is already compact or unlikely to be reused, because context stewardship must reduce total cost rather than manufacture duplicate artifacts.

### `grep-friendly-artifact` — Grep-friendly artifact

Reusable artifacts preserve stable canonical search tokens, exact identifiers, paths, symbols, finding IDs, and evidence anchors where practical, because downstream agents should be able to locate authoritative detail with cheap exact search before broad rereading.

Use the host's canonical naming convention and prefer stable `kebab-case` semantic names when that convention applies, because grepability needs consistent tokens without imposing one serialization style on every artifact or machine field.

Important independent findings or propositions should remain separately searchable when practical, because one opaque prose blob makes selective retrieval unnecessarily expensive.

## Orchestration

### `control-plane-isolation` — Control-plane isolation

The Lead and every admitted mini-orchestrator perform deterministic orchestration mechanics only, because accumulating domain understanding in an open-ended control context creates both context waste and hidden semantic authority.

Orientation, task understanding, discovery, source selection, applicability, domain reading, analysis, planning, decomposition, routing judgment, editing, command execution, implementation, review, semantic validation, integration, synthesis, acceptance, and completion judgment are meaning-dependent work and therefore execute in bounded semantic children, because no substantive category receives an inline Lead exception.

A host-fixed first role or transition may be dispatched directly without adding planning ceremony, but any choice that depends on task meaning, evidence, quality, risk, readiness, priority, or route adequacy must itself be delegated, because deterministic control should stay cheap while semantic control stays outside the orchestrator.

There is no small-task exception to semantic child isolation, but deterministic mechanics need not be delegated merely to satisfy process form, because the invariant protects meaning-dependent context rather than maximizing agent count.

### `sequential-delegation` — Sequential delegation

At most one substantive model reasoning invocation is active in an orchestration tree at a time, because sequential succession bounds live context and keeps control ownership inspectable.

A bounded child may act as a mini-orchestrator when its admitted task requires further decomposition or when semantic judgment determines that nesting will materially reduce total context, cost, exposure, integration load, or failure risk, because nesting is useful only when it offloads a real bounded process.

A mini-orchestrator inherits this contract, may have at most one active model child, and suspends while that child or deeper admitted subtree runs, because recursive offload must preserve the same sequential context boundary instead of creating parallel sibling contexts.

Nested authority, disclosure, and write scope may only preserve or narrow the parent admission, because delegation must not manufacture capability.

### `file-backed-succession` — File-backed succession

Before substantive orchestration, establish one host-authorized run-scoped workspace and persist the exact initial user or task input and every later user message there as immutable intent events before they can affect a later substantive dispatch, because one stable data plane keeps semantic state outside the control context and prevents the control plane from deciding which user input is material.

Every semantic dispatch binds one bounded objective, current intent reference, inherited authority and prohibitions, admitted input references, authorized output paths, route request, validation obligation, and escalation condition, because a child must not reconstruct authority or missing context from conversation residue.

Every child writes substantive work to admitted artifacts and returns only compact control metadata plus output references, because the parent should not absorb the child's domain body merely to continue orchestration.

When the next transition depends on meaning, an authorized semantic child writes the successor instruction and its supporting reasoning to files; the orchestrator validates only the control envelope and follows the machine-readable transition, because substantive continuation must not require Lead interpretation.

A later intent event invalidates unexecuted semantic continuation bound to an older intent state; completed artifacts remain evidence but must be explicitly readmitted by subsequent semantic judgment, because new intent should change future work without erasing history or letting stale plans proceed silently.

A minimal interoperable control vocabulary is sufficient, because the contract needs machine-followable handoffs without owning a host serialization:

```text
Packet
  dispatch-id
  intent-ref
  objective-ref
  authority-ref
  prohibition-refs[]
  input-refs[]
  output-paths[]
  route-requested

Receipt
  dispatch-id
  status: complete | partial | blocked | failed
  output-refs[]
  digest-refs[]
  next-ref | null
  blocker-ref | null

Next
  action: continue | stop | escalate | conflict
  packet-ref | null
  blocker-ref | null
```

The exact serialization belongs to the host unless separately governed, because this contract needs observable handoff semantics without owning implementation format.

### `structural-and-semantic-gates` — Structural and semantic gates

Deterministic checks may validate identities, schemas, hashes, admitted paths, inherited authority, preserved prohibitions, route authorization, closed statuses, and reference freshness, because those facts do not require domain interpretation.

Structural success never proves semantic correctness, acceptance, evidence sufficiency, or completion, because semantic meaning remains owned by the authorized semantic role.

Routing and context-isolation claims are recorded only when observable and remain unknown otherwise, because orchestration must not convert an unavailable runtime fact into a guarantee.

Retries remain narrow and host-authorized; exact transport replay or harmless structural correction does not justify silently repeating semantic judgment, because repetition without new evidence can add cost while simulating confidence.

Fail closed when required authority, intent binding, artifact identity, output admission, semantic continuation, or required evidence remains unresolved, because the orchestrator must not repair uncertainty by importing the underlying domain problem into its own context.

## Host integration

The host may add stricter requirements but must not cite this contract to weaken required authority, evidence, freshness, independence, or task-completion rules, because `context-stewardship` optimizes the path to reliable work rather than redefining what reliable work means.

When Skeptic adopts this contract, `skeptic.md` remains authoritative for Skeptic invocation, ownership, source freshness, loop convergence, findings, and dispositions, because a context companion cannot override the framework it serves.
