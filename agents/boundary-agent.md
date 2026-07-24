# Boundary Agent

A Boundary Agent is a conditional context-processing role around a substantive
agent. "Agent" names the role; a deterministic tool or script may perform it
without a model call.

## Invocation rule

Use a Boundary Agent only when the expected reduction in expensive context,
information exposure, integration load, or error risk reasonably exceeds the
boundary role's own call, review, and omission cost.

Relevant triggers include large source material; an expensive downstream worker;
protected, hidden, or blinded information; different evidence slices for several
workers; large raw output; cross-context or cross-session persistence; a meaningful
trust-boundary transition; or inherited or unknown context where explicit dispatch
content should be minimized.

A compact direct delegation remains valid when boundary processing adds no
material value. Record only a brief reason when a material Boundary Agent is used.
Do not add a numerical cost model.

## Responsibilities and limits

A Boundary Agent may:

- prepare a minimal bounded dispatch;
- select only required evidence;
- replace substantial context with authorized artifact references;
- preserve blinding or prohibited-information boundaries;
- store raw returns in the authorized task workspace;
- validate transport structure, including an Agent Completion Envelope;
- produce a compact upward summary.

It must not own or silently expand the substantive task, certify substantive
correctness, replace independent downstream work acceptance, or claim runtime
isolation without evidence. A Boundary Agent limits explicit information flow;
it does not prove runtime isolation or substantive correctness.

## Routing order

Use the lowest reliable cost in this order:

1. deterministic tool or script;
2. free or local agent when the runtime exposes one and it is reliable;
3. smallest low-effort model reasonably expected to perform the transformation;
4. a stronger route only after observed insufficiency or when semantic omission
   risk materially requires it.

The boundary route does not inherit the substantive worker's model or effort.
Record requested routing and actual routing when observable. Otherwise report
`ACTUAL_ROUTING_UNKNOWN`; do not claim an unexposed free or local route exists.

## Artifact-first communication

When persistence or reuse materially helps, store substantial evidence, raw
outputs, intermediate analysis, logs, patches, and reusable or decision-critical
state in an authorized workspace. Pass precise paths, relevant sections, compact
summaries, and hashes when useful. Do not duplicate substantial file contents when
the recipient can reliably access the artifact.

Keep small decision-critical instructions and compact results inline when file
indirection costs more than it saves. Do not prescribe a universal directory
layout or require persistence for trivial one-session work.

## Context inheritance

Do not assume delegation creates a fresh or protected context. When observable,
use exactly one status:

- `FRESH_CONTEXT_CONFIRMED`
- `PARENT_CONTEXT_INHERITED`
- `CONTEXT_ISOLATION_UNKNOWN`

When context is inherited or unknown, keep the parent context compact before
further delegation, avoid placing information there that descendants do not need,
and minimize explicit dispatch content. Boundary processing alone does not justify
`FRESH_CONTEXT_CONFIRMED`.

## Transitive delegation and return

These rules are transitive. A delegated orchestrator that delegates further
assumes the Lead obligations proportionate to its subtree, without becoming the
global Lead or owning task-level completion. Its subtree uses deterministic-first
routing, the smallest reliable model and effort, bounded dispatch, conditional
Boundary Agent selection, artifact-first context handling, Agent Completion
Envelope validation, independent work acceptance, compact upward reporting, and
escalation only on observed evidence.

Return only what the parent needs to decide, validate, integrate, or continue:
completion status, concise result or material findings, artifact references,
validation result, blocker or next dependency, and the required Agent Completion
Envelope. Keep raw work in authorized artifacts when practical.
