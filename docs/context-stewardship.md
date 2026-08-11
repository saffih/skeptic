# Context Stewardship Contract

`context-stewardship` treats model context as scarce reasoning capacity. Its purpose is to keep each recipient's working context sufficient for the current obligation without repeatedly carrying durable state that can be resolved when needed.

This contract governs context handling only. It neither grants nor reduces authority, and a host must not use context economy to weaken required evidence, freshness, completeness, independence, completion criteria, or access to source material already authorized for the obligation.

This document is superseded by `docs/context-rules.md` for every purpose except one, because one subject must end with exactly one current authority. The sole surviving exception is STT's own still-standing adoption of this document by path in `plans/stt-mvp-governing-inputs.md:50`, because that reference is owned by STT rather than by this document and only its owner may retire it. Full retirement of this document is deferred to the later STT Governing Inputs conformance task, because that task, not this one, decides when STT's own reference is updated.

## Core

### Context respect

Model context is scarce reasoning capacity. Material belongs in the active context because it contributes to the recipient's current obligation, not merely because it exists or was present upstream. This is the root principle for external state, curation, bounded context, and succession.

### Durable external state

Persist task-local exact intent, raw substantive results, decisions, and other reusable state in durable host-authorized artifacts when they must survive an invocation boundary. Existing durable authoritative sources should remain in place and be referenced when they are receiver-accessible; do not copy existing source data merely for Stewardship. Keep raw or authoritative state available independently of any summary, because model context and derived artifacts are not durable sources of truth.

Carry a substantive body in model context only while it contributes to the current reasoning. Otherwise carry a resolvable reference to its durable form.

Reusable artifacts should preserve stable identifiers and retrieval anchors, and should keep independent material propositions separately findable where practical, so later recipients can selectively retrieve authoritative detail.

### Receiver-resolvable references

A reference crossing a context boundary must let its intended receiver locate and read the authorized artifact. It must identify the relevant whole or fragment and provide identity or freshness evidence proportionate to the risk when that evidence is observable.

A reference saves context only when the receiver can resolve it at the time of use. Missing, inaccessible, ambiguous, stale, or changed references cannot be guessed through; they must be rebound or exposed as a context blocker. When references are not resolvable or indirection would cost more context than it saves, bounded inline material is permitted.

### Recipient-specific curation

Context curation is an obligation-driven, recipient-specific stewardship action. Curate when doing so materially improves the recipient's starting context. Direct references are sufficient when authoritative material is already appropriately focused and receiver-accessible; do not create derivatives merely to demonstrate Stewardship.

Curation selects an economical starting context; it does not grant authority, certify correctness or isolation, define an exclusive evidence boundary, or restrict the recipient's access to any source the host has already authorized for the obligation.

The semantic recipient owns source selection and evidence sufficiency. It may independently resolve and load any already-authorized source needed to address uncertainty, contradiction, missing support, or a fresh, complete, or independent obligation. If needed evidence is unavailable or unauthorized, the recipient exposes that condition rather than silently omitting it.

### Source-bound derivatives

A digest or other curated derivative may be created from authoritative sources when it materially reduces expected total context cost. Each derivative is the smallest faithful form sufficient for its expected downstream reuse, not a fixed-size summary. Use the smallest number of faithful derivatives needed for likely reuse, bind each derivative to resolvable source references, and preserve material conclusions, uncertainty, supporting and disconfirming evidence, and retrieval anchors relevant to that reuse.

A derivative has no greater authority than its sources. It never substitutes for a source read required for freshness, completeness, absence, contradiction, independent review, or decision-critical support. Do not build authority through derivative chains; return to authoritative sources.

### Bounded working context

Bound the recipient's working context to what is sufficient for its semantic obligation. Working context includes inherited runtime context, startup material, every source loaded afterward, intermediate reasoning state, and generated artifacts retained in context; a compact startup does not prove that this later working context fits.

Account for known subsequent loading when defining an obligation. Where safe fit is not established, decompose into bounded semantic obligations that can continue through durable references. Decomposition must preserve the original obligation, authorized source access, and every required freshness, completeness, and independence property. If those properties cannot be preserved, expose a context blocker instead of omitting evidence.

A control plane may enforce structural limits but cannot determine semantic sufficiency or choose decomposition boundaries from domain meaning. Those judgments belong to a semantic role.

### Admission and observability

Reference-first startup proves only that the bootstrap was admitted. It does not prove working-context fit, source loading, freshness, isolation, or semantic correctness.

A context-window rejection or equivalent capacity failure is a context-admission failure, not evidence that the semantic role failed its obligation. Preserve completed durable artifacts, reduce the bootstrap, or have a semantic role decompose the obligation into genuinely smaller bounded work. Never move semantic work into an orchestrator to escape a context failure. If bounded semantic work still cannot be admitted without losing required properties, expose an explicit context blocker.

Runtime inheritance, hidden loading, isolation, and fit are reported only when observable; otherwise they remain `UNKNOWN`.

## Orchestration

### Domain-blind control plane

A Lead or mini-orchestrator is a domain-blind control plane. It may retain exact intent references, dispatch and artifact references, statuses, and other compact control metadata, and may perform deterministic mechanics such as persisting inputs, checking reference presence, and following a fixed transition.

It must not read substantive bodies to understand the task or decide what happens next. Any action or choice whose correctness depends on domain meaning—including interpretation, discovery, source selection, applicability, planning, decomposition, implementation, review, evidence sufficiency, acceptance, readiness, blocker interpretation, or semantic continuation—belongs to a bounded semantic role.

A host-fixed first role or transition may be dispatched directly. Once continuation depends on meaning, the control plane delegates that judgment and follows the resulting durable successor reference without interpreting the underlying domain artifacts. Structural validity never proves semantic correctness or completion.

### Reference-first startup

Before semantic startup, persist the bounded obligation, governing intent and authority references, starting artifact references, and output destination in durable host-authorized state. When the recipient can resolve that state, the startup message contains only the minimum bootstrap needed to identify and load it.

Prefer references when they are resolvable and context-cheaper. Bounded inline material is legitimate when it is the better faithful working context. Self-containment is not a reason to copy large bodies unnecessarily. After startup, the semantic recipient resolves its starting references and selectively expands to any other already-authorized source required by the obligation.

### File-backed succession

Persist initial and superseding intent in identity-preserving durable records before it controls later semantic work. Persist substantive results outside the orchestrator's context and return compact control metadata with resolvable output references.

When the next action depends on meaning, a semantic role writes the successor instruction and any supporting reasoning to durable artifacts. The successor reference must identify the intent state it serves and must let the next recipient resolve its obligation, governing authority, starting sources, and output destination without conversation residue. Superseding intent requires semantic rebinding before an unexecuted successor tied to older intent may be used.

Hosts own handoff serialization, scheduling, routing, review procedures, and terminal states. Every boundary in a delegated subtree nevertheless preserves this contract's durable-state, resolvability, source-access, non-substitution, bounded-context, and observability rules.
