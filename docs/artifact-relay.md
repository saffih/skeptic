# Artifact Relay Contract

This document defines the standalone `artifact-relay` contract, because bounded orchestrators need one portable authority for relay mechanics even when Skeptic is absent.

This contract governs relay-local authority, statuses, receipts, freshness, routing, fragmentation, merge, and delegation, because those meanings must remain inspectable without importing another framework.

This contract does not govern task ownership, final task completion, publication, or mutation authority, because a relay can transport bounded results without owning the larger workflow.

When a Skeptic loop uses `artifact-relay`, `skeptic.md` still governs Skeptic meanings, loop ownership, convergence, and Skeptic dispositions, because Skeptic-specific authority remains with Skeptic.

When a non-Skeptic bounded orchestrator uses `artifact-relay`, that orchestrator remains the loop owner and must define its own task-level meanings, because relay support does not create a hidden parent framework.

## Purpose and local authority

`artifact-relay` packages bounded side-work results together with identity, scope, and support evidence, because later reuse is safe only when the receiving owner can inspect what was done and under which limits.

`artifact-relay` exists to reduce repeated reading, bounded analysis, and context exhaustion, because some workflows need reusable intermediate products without transferring loop ownership.

`artifact-relay` is report-and-receipt authority only, because a transportable result cannot authorize mutation, promotion, publication, delegation expansion, or terminal task success by itself.

`artifact-relay` may carry bounded semantic results, deterministic validation results, refusal results, and routing evidence, because those outputs can support later owner review without replacing it.

`artifact-relay` never changes the governing meaning of a host framework's own statuses or loop semantics, because duplicated authority would create drift between the relay and the orchestrator that consumes it.

## Governing-context binding

Every relay binds to the exact governing context that admitted it, because a later consumer must distinguish a reusable artifact from an unbound narrative summary.

The governing context records the owner artifact or invocation that authorized the relay, because later review must know which workflow owned the side work.

The governing context records the exact admitted corpus, request identifier, production timestamp, payload hash, and terminal-newline state, because byte identity and lineage matter across context boundaries.

The governing context records the exact permission mode, prohibition set, requested role, output-path set, and retry policy, because bounded side work must not acquire implicit scope.

The governing context records whether the receiving owner must freshly reread current sources, because reused artifacts never count as fresh independent review by themselves.

If the host framework has its own governing artifact hash, the relay records that hash as an observed field, because the relay should preserve host evidence when it exists without making that field universally mandatory.

## Fragment and session-context model

`fragment-model` means that a relay payload consists of bounded items with explicit identity and support, because later merging and review require item-level lineage rather than one opaque blob.

A relay fragment is the smallest carried unit that can be cited, validated, merged, or rejected independently, because bounded reuse depends on independently inspectable units.

A session-context record captures invocation-local facts such as requested role, route, admitted corpus, permission mode, prohibition set, and retry policy, because later readers cannot safely infer those facts from semantic content.

Fragments cite exact source units or byte spans, because physical line segmentation alone can miss meaningful design or prompt boundaries.

Every admitted byte is covered by one primary fragment or an explicit non-propositional classification, because silent uncovered source weakens completeness claims.

Duplicated support is marked `support_only`, because one source unit must not acquire multiple primary owners during merge.

An ambiguous session context is represented as explicit unknown fields or separate source-bound fragments, because a later agent must not assume that the current session contains the same context as the producing agent.

## Delegation and routing

Artifact Relay delegates only bounded side work, because the loop owner remains responsible for the complete recipe and final task judgment.

Delegation names one exact role, one exact corpus, one exact output target set, and one exact prohibition set, because a worker must not infer missing authority.

Delegation is used only when expected context, cost, or failure-risk savings exceed its overhead, because unnecessary delegation adds coordination without evidence value.

The relay selects the least expensive reliable route for the bounded outcome, because cost-aware routing is preferable when it preserves the required result.

A more expensive route is permitted only when the relay records why a cheaper reliable route was insufficient, because cost expansion must remain inspectable.

Artifact Relay does not use Luna, does not recursively invoke itself as a substitute for owner judgment, and does not delegate loop ownership, because one accountable owner is required.

The loop owner reevaluates every delegated result against current authoritative context, because bounded correctness in one fragment does not prove downstream applicability.

## Freshness and independence

Freshness requires a later invocation to reread the current governing source and complete reviewed artifact when fresh review is claimed, because an earlier read cannot satisfy a later review obligation.

Independence requires a fresh bounded invocation when independent review is claimed, because same-context reuse does not establish reviewer independence.

A schema-correction retry is not an independent semantic qualification pass, because it receives deterministic feedback about an earlier output.

A reused relay supports fresh review but never counts as that review, because evidence transport and source-fresh cognition are different properties.

If the owner cannot freshly reread the governing sources required for its own task-level decision, the relay remains support-only and cannot satisfy that owner's freshness gate, because relay reuse cannot erase missing owner work.

## Routing evidence

Routing evidence records requested and observed route separately, because downstream qualification must distinguish intent from host-level fact.

Routing evidence binds provider, model, effort, packet hash, prompt hash, raw-result hash, and host-evidence reference when those facts are observable, because route claims without bound inputs are weak.

Observed provider fields permit `CODEX`, `OTHER`, or `UNKNOWN`, because some hosts expose incomplete routing facts.

Routing status is one of `OBSERVED_MATCH`, `OBSERVED_MISMATCH`, or `UNOBSERVED`, because qualification needs closed categories.

Model self-report does not authenticate routing, because self-description is not host-level observation.

Unobserved routing may still support a report when the owner permits that mode, because diagnostic support can remain useful while qualification is blocked.

Unobserved or mismatched routing blocks semantic qualification unless an owner-approved weaker outcome exists, because routing uncertainty must not become inferred trust.

## Structural validation and semantic qualification

Structural validation and semantic qualification are separate authorities, because hashes and fields cannot prove semantic correctness or readiness.

Structural validation checks schema identity, required fields, hashes, output-path admission, coverage, lineage, and closed statuses, because these properties are mechanically inspectable.

Semantic qualification checks whether the bounded result is acceptable for its intended downstream use, because placement and adequacy exceed structural validity.

A structurally valid relay may remain semantically unusable, because routing, corpus sufficiency, authority, or cross-fragment consistency may remain unresolved.

Structural status is `STRUCTURALLY_VALID` or `STRUCTURALLY_INVALID`, because deterministic validation must not overclaim semantic success.

Qualification status is `QUALIFIED_PASS`, `QUALIFIED_FAIL`, or `QUALIFICATION_CONFLICT`, because downstream use needs a separate closed decision vocabulary.

## Coverage, decomposition, and merge

Every admitted source unit appears exactly once as primary coverage or explicitly as non-propositional, because otherwise completeness cannot be verified.

When the corpus exceeds the admitted semantic-byte ceiling, decomposition proceeds by document, section, then source-unit boundary, because stable coarse-to-fine splitting limits semantic distortion.

Each decomposed result is `PROVISIONAL` until merge, because one slice cannot resolve whole-corpus contradictions or cross-slice dependencies.

Merge uses the same governing-context identity and corpus-hash family, because cross-basis merging can fabricate false consistency.

Merge detects duplicate primary assignment, uncovered bytes, contradictory assignments, dependency conflicts, and unsupported cross-slice conclusions, because decomposition introduces those failure modes.

If the admitted decomposition depth is exhausted before coverage is complete, the relay stops with a qualification conflict, because silent truncation would misrepresent scope.

## Relay-local statuses

These statuses are relay-local rather than task-level, because support state must not masquerade as the host orchestrator's terminal disposition.

```text
REQUEST_RECEIVED
PREPARE_REJECTED
CORPUS_BOUND
CONTEXT_ADMITTED_FULL
DECOMPOSITION_REQUIRED
SLICE_RESULTS_PROVISIONAL
MERGE_REQUIRED
RESULT_RECEIVED
STRUCTURALLY_INVALID
STRUCTURALLY_VALID
QUALIFICATION_REQUIRED
QUALIFIED_PASS
QUALIFIED_FAIL
QUALIFICATION_CONFLICT
```

`REQUEST_RECEIVED` means the owner has accepted a relay request for evaluation, because later states should not imply that binding or execution already happened.

`PREPARE_REJECTED` means preparation failed before a valid relay packet existed, because malformed or unauthorized inputs must stop before semantic work begins.

`CORPUS_BOUND` means the admitted corpus and governing context are fixed for this relay event, because later validation depends on a stable input basis.

`CONTEXT_ADMITTED_FULL` means the full admitted context fit within the authorized relay packet, because decomposition is not yet required.

`DECOMPOSITION_REQUIRED` means the admitted corpus exceeded the authorized semantic envelope, because bounded work cannot proceed honestly as one opaque packet.

`SLICE_RESULTS_PROVISIONAL` means decomposed slice outputs exist but still require merge, because per-slice success does not establish whole-corpus coherence.

`MERGE_REQUIRED` means the relay has enough provisional material to attempt whole-result reconciliation, because support is incomplete until merge runs.

`RESULT_RECEIVED` means a raw bounded output was returned for the current packet, because receipt of output does not yet prove structural or semantic acceptability.

`STRUCTURALLY_INVALID` means deterministic validation failed, because malformed or mismatched artifacts cannot advance to semantic qualification.

`STRUCTURALLY_VALID` means deterministic validation passed, because the relay packet satisfied its structural checks.

`QUALIFICATION_REQUIRED` means semantic downstream adequacy still needs owner or designated-qualifier judgment, because structural validity alone is insufficient.

`QUALIFIED_PASS` means the bounded result satisfied its declared qualification gate, because the relay can support downstream use within its stated scope.

`QUALIFIED_FAIL` means the bounded result was reviewed semantically and found inadequate for its declared downstream use, because a structurally valid relay can still fail its purpose.

`QUALIFICATION_CONFLICT` means routing, authority, freshness, scope, contradiction, or owner decisions remained insufficient, because the relay must stop rather than fabricate closure.

## Retry and failure handling

Retries are controlled by explicit policy, because repeated semantic attempts can simulate confidence without new evidence.

The default policy is zero semantic retries and at most one explicitly authorized schema-correction retry, because deterministic formatting repair can be separated from semantic re-judgment.

A transport retry, if authorized, reuses the exact packet, prompt, and route request, because altered inputs create a new semantic event rather than a replay.

Preparation rejects unknown schemas, missing hashes, unauthorized output paths, and malformed coverage, because malformed packets cannot support trustworthy reuse.

Structural failure remains structural rather than becoming semantic disagreement, because each failure class needs different remediation.

Semantic conflict remains unresolved when authority, routing, coverage, freshness, or owner decisions are insufficient, because safe progress cannot continue by convenience.

## Relay receipt

`RelayReceipt@1` is the compact auditable record for one relay production or review event, because later consumers need a stable summary of what was attempted and what was proven.

```text
RelayReceipt@1
  request_id
  produced_at
  permission_mode
  governing_context:
    owner_artifact_ref
    owner_artifact_sha256 | UNKNOWN
    owner_framework: SKEPTIC | OTHER | NONE | UNKNOWN
    owner_framework_ref | null
    owner_framework_blob_sha256 | null
  admitted_corpus:
    source_paths[]
    corpus_sha256
    terminal_lf
  relay_payload_sha256
  raw_result_sha256 | null
  canonical_result_sha256 | null
  role_requested
  route_requested:
    provider
    model | null
    effort | null
  route_observed:
    provider: CODEX | OTHER | UNKNOWN
    model: value | UNKNOWN
    effort: value | UNKNOWN
    routing_status: OBSERVED_MATCH | OBSERVED_MISMATCH | UNOBSERVED
  freshness_requirement:
    owner_must_reread_current_sources: TRUE | FALSE | UNKNOWN
    counts_as_fresh_review: FALSE
    counts_as_independent_review: FALSE
  retry_policy
  prohibition_set[]
  output_paths[]
  status
  validation_report_ref | null
  semantic_result_ref | null
  conflicts[]
  exemptions[]
```

A receipt summarizes but does not replace the full bound artifact, because a compact index is not the complete evidence record.

## Suggested bundle schemas

These schemas are structural rather than mandatory host semantics, because stable fields make relay artifacts mechanically inspectable without claiming that the host framework must adopt every name.

```text
RelayArtifactBundle@1
  schema
  request_id
  produced_at
  permission_mode
  governing_context
  admitted_corpus {items[], corpus_sha256, terminal_lf}
  fragment_items[]
  session_context
  retry_policy
  prohibition_set[]
  output_paths[]
  declared_authority_scope
  payload_sha256

RelayFragment@1
  item_id
  kind
  primary_coverage[]
  support_only_coverage[]
  decision_basis[]
  content_ref
  lineage_refs[]
  status

RelaySessionContext@1
  role_requested
  route_requested {provider, model|null, effort|null}
  route_observed {provider, model, effort, routing_status}
  owner_must_reread_current_sources
  counts_as_fresh_review
  counts_as_independent_review
  admitted_max_bytes
  decomposition_depth
  prohibition_set[]
  notes[]

RelayValidationReport@1
  schema
  request_id
  bundle_sha256
  raw_result_sha256 | null
  canonical_result_sha256 | null
  status: STRUCTURALLY_VALID | STRUCTURALLY_INVALID
  input_binding: MATCHES_PACKET | CHANGED | NOT_CHECKED
  output_path_admission: ADMITTED | REJECTED
  errors[]

RelayQualificationRecord@1
  schema
  request_id
  bundle_sha256
  qualification_status:
    QUALIFIED_PASS | QUALIFIED_FAIL | QUALIFICATION_CONFLICT
  basis[]
  blocking_unknowns[]
  routing_status:
    OBSERVED_MATCH | OBSERVED_MISMATCH | UNOBSERVED
```

## Host-framework integration

This contract is complete on its own, because a bounded orchestrator should be able to adopt relay mechanics without importing Skeptic.

When a host framework supplies stricter task-level gates outside relay-local meanings, the host framework may add those gates on top of this contract, because optional integration can strengthen task ownership without weakening relay-local safety.

When Skeptic supplies the host framework, `skeptic.md` remains the authority for Skeptic meanings and loop ownership while this contract supplies relay mechanics, because the two artifacts own different layers of meaning.
