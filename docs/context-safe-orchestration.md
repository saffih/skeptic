# Context-Safe Orchestration Contract

This document defines the standalone `context-safe-orchestration` contract, because bounded orchestration needs one portable authority for context minimization, file-backed artifact transfer, routing, and failure gates even when Skeptic is absent.

This contract governs orchestration-local authority, statuses, receipts, freshness, independence, retries, coverage, merge, fragment rules, content references, and bounded delegation, because those meanings must remain inspectable without importing another framework.

This contract does not govern task ownership, final task completion, publication, or mutation authority, because an orchestration contract can transport bounded work products without owning the larger workflow.

When Skeptic uses `context-safe-orchestration`, `skeptic.md` still governs Skeptic meanings, loop ownership, convergence, and Skeptic dispositions, because Skeptic-specific authority remains with Skeptic.

When a non-Skeptic bounded orchestrator uses `context-safe-orchestration`, that orchestrator remains the control-plane loop owner and must define its own task-level meanings, because orchestration support does not create a hidden parent framework.

## Purpose and authority

The top user-interactive Lead is an orchestration-only control plane, because an open-ended user session cannot provide a bounded cumulative context budget.

Every substantive action uses one bounded child invocation, because even individually small actions can cumulatively exhaust the Lead context.

Substantive action includes domain reading, analysis, decomposition, planning, routing judgment, editing, command execution, implementation, validation, review, RunSkeptic, integration, synthesis, and semantic acceptance, because each action can import or generate domain content.

The Lead may create the run workspace, assign dispatch identities, validate envelope structure, track compact status, and select the next control transition, because those mechanics do not require domain content.

There is no trivial-work or small-task exception, because context safety depends on the invariant rather than on a prediction about future session growth.

One private run-scoped workspace exists before the first substantive action under `<host-temp>/skeptic/context-safe-orchestration/<run-id>/` or its host-equivalent, because the workspace must be the data plane from orchestration start.

The exact user request is persisted in that workspace before substantive dispatch, because child inputs and later receipts must bind to the original bytes without importing them into the Lead context.

All orchestration-generated substantive artifacts are written to that workspace unless the actual task explicitly authorizes repository writes, because runtime evidence must not silently modify the repository.

`context-safe-orchestration` coordinates bounded side work through file-backed artifacts rather than retained coordinator memory, because substantive content must survive boundaries without silently expanding session context.

The top user-interactive agent must protect its own live context as a scarce control surface, because the loop owner loses reliability when it keeps large substantive work inline.

The coordinator persists substantive outputs, partial work products, and delegated reports to exact admitted files and compact receipts, because later reuse is safe only when the next agent can inspect stable external artifacts instead of inferring hidden prior context.

The coordinator keeps only the minimum control context needed to route and validate work, because retained summaries of substantive content weaken isolation and can drift from the bound files.

The top user-interactive agent keeps compact receipts, indexes, file identities, and status facts rather than substantive delegated content, because later steps should reopen named artifacts instead of inheriting an expanded session narrative.

Later agents read only the named fragments, content references, and receipts admitted for their step, because reuse remains safe only when each invocation has an explicit bounded corpus.

Later agents must read named files or exact fragments rather than rely on inherited session context, because delegated safety depends on explicit artifact re-admission instead of conversational carryover.

Missing, stale, mismatched, ambiguous, or unbound files block reuse, because an orchestration result cannot remain trustworthy when its supporting artifacts are not exact, current, and explicitly admitted.

`context-safe-orchestration` is report-and-receipt authority only, because a transportable result cannot authorize mutation, promotion, publication, delegation expansion, or terminal task success by itself.

## Orchestration model

The Lead owns control-plane orchestration but not substantive task execution or semantic judgment, because those responsibilities must remain inside bounded child contexts.

The Lead dispatches a bounded planner, router, reviewer, qualifier, worker, validator, integrator, or Skeptic child whenever the next control decision requires domain understanding, because routing and acceptance are substantive when they depend on task content.

The coordinator should choose the orchestrator shape and the least expensive reliable subagent early, because early routing and decomposition avoid a late context spike in the user-interactive loop.

The coordinator applies deterministic routing policy for bounded child dispatch, because low-cost routing is preferred when it preserves the required result.

When route selection requires domain understanding, a bounded router child makes that selection and returns only a compact route receipt, because the Lead must not inspect domain content to choose a route.

A more expensive route is permitted only when the receipt records why a cheaper reliable route was insufficient, because cost expansion must remain inspectable.

The coordinator dispatches bounded decomposition before substantive execution whenever decomposition requires domain understanding, because the Lead must not read domain content merely to decide how to split it.

The coordinator may use a mini-orchestrator for a bounded subproblem only when the parent owner admits that layer explicitly, because hidden orchestration nesting weakens authority and traceability.

A mini-orchestrator remains subject to the same file binding, freshness, routing, and failure gates as any other bounded delegate, because a smaller coordinator does not earn weaker controls.

Skeptic-hosted use remains optional and subordinate to `skeptic.md`, because Skeptic may consume orchestration support without yielding its own meanings, convergence, or receipts.

## Session-context minimization

The coordinator admits only the smallest control packet needed for one bounded step, because session context should contain routing, scope, and file identities rather than substantive document content.

The user-interactive top-agent context differs from delegated bounded contexts, because the top loop must preserve room for control-plane judgment while delegated packets may carry only the exact local corpus needed for one step.

Substantive analyses, plans, findings, merges, and intermediate outputs are written to bounded files instead of retained in coordinator context, because durable file-backed transfer is safer than narrative memory carryover.

The coordinator treats unbounded or unknown substantive work as unsafe to keep inline, because unknown growth in live context can collapse later routing, review, and failure handling.

Coordinator context may retain exact file paths, hashes, fragment identifiers, route requests, prohibition sets, and status facts, because those control facts are needed to bind later reads without reloading full content.

A later agent reads only the exact files or fragments named for its step and must not assume access to earlier full-session prose, because bounded orchestration depends on explicit re-admission rather than conversational residue.

If a bounded step would require substantive content that is not present in admitted files or fragments, the coordinator must stop or create a new admitted artifact before reuse, because hidden context reconstruction is not authorized.

If an artifact is missing, stale, ambiguous, or not yet bound to an admitted path and hash, the coordinator must stop, refresh, or rebind before delegation or reuse, because later steps must fail closed on artifact uncertainty.

## File-backed artifacts and exact binding

Every orchestration artifact binds to exact admitted file paths, byte content, terminal-newline state, and SHA-256 hashes, because later consumers must distinguish a reusable artifact from an unbound summary.

Every receipt records the exact governing artifact or invocation that admitted the orchestration event, because later review must know which workflow owned the side work.

Every output path is admitted before execution and rejected if it falls outside the authorized set, because bounded side work must not acquire implicit write scope.

An artifact with a missing file, changed hash, missing terminal-newline record, or ambiguous path identity is stale for reuse, because exact-file binding is part of the evidence rather than incidental metadata.

Compact receipts summarize identity and status but do not replace the bound files, because a compact index is not the full substantive evidence record.

## Fragment model and `content_ref` rules

`fragment-model` means that a bounded payload consists of independently inspectable fragments with explicit lineage and support, because later merging and review require item-level rather than blob-level authority.

A fragment is the smallest carried unit that may be cited, validated, merged, retried, or rejected independently, because bounded reuse depends on independently inspectable units.

Each fragment has one exact `content_ref` that names the authoritative bounded content file or byte span it represents, because later agents must read named content rather than infer it from prose summaries.

`content_ref` binds path, hash, and the addressed fragment region together, because a path alone is insufficient when files can change or contain multiple independent units.

Each later agent reads only the `content_ref` values explicitly admitted for that step, because bounded orchestration requires named fragment reads instead of broad file rereads by default.

Every admitted byte is covered by one primary fragment or an explicit non-propositional classification, because silent uncovered source weakens completeness claims.

Duplicated support is marked `support_only`, because one source unit must not acquire multiple primary owners during merge.

Missing, stale, or ambiguous `content_ref` targets block reuse and merge, because a fragment without exact retrievable content cannot support trustworthy downstream judgment.

## Delegation, mini-orchestrators, and Skeptic-hosted use

Delegation names one exact role, one exact corpus, one exact output target set, and one exact prohibition set, because a worker must not infer missing authority.

Each bounded child packet also names one bounded objective, admitted input file or fragment references, requested route/model/effort, validation obligation, escalation condition, and the run-workspace reference, because a child must not receive unrelated conversation or reconstruct missing context.

A child communicates substantive data by writing the admitted output files and returning only a compact receipt with status, hashes, and exact references, because the Lead must not shuttle a substantive body from one child to another.

The next child receives the prior child output reference directly and reads the authoritative file itself, because reference handoff preserves the data-plane boundary.

Delegation is mandatory for every substantive action and never transfers control-plane ownership, because one Lead remains accountable while every domain action stays bounded.

The Lead must not perform substantive work directly even when the work is small, deterministic-looking, or expected to fit inline, because cumulative session growth makes that exception unsafe.

`context-safe-orchestration` does not use Luna and does not replace host task authority, because bounded child qualification supplies domain judgment while the Lead retains only control-plane ownership.

When a bounded step is itself orchestration-shaped, the owner may admit one mini-orchestrator packet with tighter limits than the parent packet, because nested coordination should narrow rather than widen scope.

Standalone Skeptic loops, mini-orchestrators, and other bounded orchestrators may all use this contract without changing control-plane ownership, because the contract distinguishes portable orchestration mechanics from the host workflow's terminal authority.

An independent bounded qualifier or reviewer reads authoritative result files and returns a compact bound decision receipt when semantic acceptance is required, because envelope validity proves structure and correlation but not correctness.

The Lead consumes only the qualifier receipt, artifact references, hashes, and status, because rereading substantive child output would restore the prohibited domain-data path into the control plane.

The Boundary Agent remains an optional context-processing layer around a mandatory bounded child, because information reduction can add value without becoming a prerequisite for child isolation.

Absence of a Boundary Agent never permits direct substantive Lead execution, because the mandatory child boundary and the optional trust-boundary transformation solve different problems.

When Skeptic hosts the work, a bounded Skeptic child owns each complete Find or Fix invocation and returns only a compact bound receipt, because `skeptic.md` still owns recipe execution, convergence, reset criteria, and final dispositions.

## Freshness and independence

Freshness requires a later invocation to reread the current governing source and any complete artifact that the host workflow requires when fresh review is claimed, because an earlier read cannot satisfy a later review obligation.

Independence requires a fresh bounded invocation when independent review is claimed, because same-context reuse does not establish reviewer independence.

A schema-correction retry is not an independent semantic qualification pass, because it receives deterministic feedback about an earlier output.

A reused orchestration artifact supports fresh review but never counts as that review, because evidence transport and source-fresh cognition are different properties.

If a fresh substantive reread or review is required, a fresh bounded child performs it and returns only a bound receipt, because file reuse cannot authorize the Lead to reacquire domain content.

## Routing and route evidence

Routing evidence records requested and observed route separately, because downstream qualification must distinguish intent from host-level fact.

Routing evidence binds provider, model, effort, packet hash, prompt hash, raw-result hash, and host-evidence reference when those facts are observable, because route claims without bound inputs are weak.

Observed provider fields permit `CODEX`, `OTHER`, or `UNKNOWN`, because some hosts expose incomplete routing facts.

Routing status is one of `OBSERVED_MATCH`, `OBSERVED_MISMATCH`, or `UNOBSERVED`, because qualification needs closed categories.

Model self-report does not authenticate routing, because self-description is not host-level observation.

Unobserved routing may still support a report when the owner permits that mode, because diagnostic support can remain useful while qualification is blocked.

Unobserved or mismatched routing blocks semantic qualification unless an owner-approved weaker outcome exists, because routing uncertainty must not become inferred trust.

## Coverage, decomposition, and merge

Every admitted source unit appears exactly once as primary coverage or explicitly as non-propositional, because otherwise completeness cannot be verified.

When the corpus exceeds the admitted semantic-byte ceiling, decomposition proceeds by document, section, then source-unit boundary, because stable coarse-to-fine splitting limits semantic distortion.

Each decomposed result is `PROVISIONAL` until merge, because one slice cannot resolve whole-corpus contradictions or cross-slice dependencies.

Merge uses the same governing-context identity and corpus-hash family, because cross-basis merging can fabricate false consistency.

Merge detects duplicate primary assignment, uncovered bytes, contradictory assignments, dependency conflicts, stale fragment bindings, and unsupported cross-slice conclusions, because decomposition introduces those failure modes.

If admitted decomposition depth is exhausted before coverage is complete, orchestration stops with a qualification conflict, because silent truncation would misrepresent scope.

## Structural validation and semantic qualification

Structural validation and semantic qualification are separate authorities, because hashes and fields cannot prove semantic correctness or readiness.

Structural validation checks schema identity, required fields, hashes, output-path admission, fragment lineage, coverage, exact file binding, and closed statuses, because these properties are mechanically inspectable.

Semantic qualification checks whether the bounded result is acceptable for its intended downstream use, because placement and adequacy exceed structural validity.

A structurally valid artifact may remain semantically unusable, because routing, corpus sufficiency, authority, freshness, coverage, or cross-fragment consistency may remain unresolved.

Structural status is `STRUCTURALLY_VALID` or `STRUCTURALLY_INVALID`, because deterministic validation must not overclaim semantic success.

Qualification status is `QUALIFIED_PASS`, `QUALIFIED_FAIL`, or `QUALIFICATION_CONFLICT`, because downstream use needs a separate closed decision vocabulary.

## Retries and failure gates

Retries are controlled by explicit policy, because repeated semantic attempts can simulate confidence without new evidence.

The default policy is zero semantic retries and at most one explicitly authorized schema-correction retry, because deterministic formatting repair can be separated from semantic re-judgment.

A transport retry, if authorized, reuses the exact packet, prompt, and route request, because altered inputs create a new semantic event rather than a replay.

Preparation rejects unknown schemas, missing hashes, unauthorized output paths, missing admitted files, stale admitted files, malformed coverage, ambiguous `content_ref` bindings, and unbound artifacts, because malformed packets cannot support trustworthy reuse.

Structural failure remains structural rather than becoming semantic disagreement, because each failure class needs different remediation.

Semantic conflict remains unresolved when authority, routing, coverage, freshness, file identity, artifact binding, or owner decisions are insufficient, because safe progress cannot continue by convenience.

## Orchestration-local statuses

These statuses are orchestration-local rather than task-level, because support state must not masquerade as the host orchestrator's terminal disposition.

```text
REQUEST_RECEIVED
PREPARE_REJECTED
CORPUS_BOUND
CONTEXT_MINIMIZED
FILES_BOUND
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
REUSE_BLOCKED_STALE
REUSE_BLOCKED_AMBIGUOUS
```

`REQUEST_RECEIVED` means the owner has accepted an orchestration request for evaluation, because later states should not imply that binding or execution already happened.

`PREPARE_REJECTED` means preparation failed before a valid packet existed, because malformed or unauthorized inputs must stop before semantic work begins.

`CORPUS_BOUND` means the admitted corpus and governing context are fixed for this orchestration event, because later validation depends on a stable input basis.

`CONTEXT_MINIMIZED` means the coordinator reduced the live session packet to bounded control facts and named file references, because substantive content should move to files before delegation.

`FILES_BOUND` means exact admitted files, hashes, and output paths are fixed for the current packet, because later reuse depends on stable file identity.

`DECOMPOSITION_REQUIRED` means the admitted corpus exceeded the authorized semantic envelope, because bounded work cannot proceed honestly as one opaque packet.

`SLICE_RESULTS_PROVISIONAL` means decomposed slice outputs exist but still require merge, because per-slice success does not establish whole-corpus coherence.

`MERGE_REQUIRED` means the orchestration has enough provisional material to attempt whole-result reconciliation, because support is incomplete until merge runs.

`RESULT_RECEIVED` means a raw bounded output was returned for the current packet, because receipt of output does not yet prove structural or semantic acceptability.

`STRUCTURALLY_INVALID` means deterministic validation failed, because malformed or mismatched artifacts cannot advance to semantic qualification.

`STRUCTURALLY_VALID` means deterministic validation passed, because the packet satisfied its structural checks.

`QUALIFICATION_REQUIRED` means semantic downstream adequacy still needs a bounded designated-qualifier judgment, because structural validity alone is insufficient.

`QUALIFIED_PASS` means the bounded result satisfied its declared qualification gate, because the orchestration artifact can support downstream use within its stated scope.

`QUALIFIED_FAIL` means the bounded result was reviewed semantically and found inadequate for its declared downstream use, because a structurally valid artifact can still fail its purpose.

`QUALIFICATION_CONFLICT` means routing, authority, freshness, scope, contradiction, or owner decisions remained insufficient, because the orchestration must stop rather than fabricate closure.

`REUSE_BLOCKED_STALE` means a required admitted file or fragment no longer matches its bound identity, because reuse cannot continue across stale evidence.

`REUSE_BLOCKED_AMBIGUOUS` means the required file, fragment, or `content_ref` cannot be identified uniquely, because orchestration cannot guess among competing candidates.

## Compact receipts and suggested schemas

`ContextSafeOrchestrationReceipt@1` is the compact auditable record for one orchestration production or review event, because later consumers need a stable summary of what was attempted and what was proven.

```text
ContextSafeOrchestrationReceipt@1
  request_id
  produced_at
  permission_mode
  governing_context:
    owner_artifact_ref
    owner_artifact_sha256 | UNKNOWN
    owner_framework: SKEPTIC | OTHER | NONE | UNKNOWN
    owner_framework_ref | null
    owner_framework_blob_sha256 | null
  admitted_files:
    paths[]
    file_sha256s[]
    terminal_lf[]
  admitted_fragments[]
  packet_sha256
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

A compact receipt summarizes but does not replace the full bound artifact set, because a compact index is not the complete substantive evidence record.

These schemas are structural rather than mandatory host semantics, because stable fields make orchestration artifacts mechanically inspectable without claiming that every host framework must adopt every field name.

```text
ContextSafeOrchestrationBundle@1
  schema
  request_id
  produced_at
  permission_mode
  governing_context
  admitted_files {items[], file_sha256s[], terminal_lf[]}
  fragment_items[]
  session_context
  retry_policy
  prohibition_set[]
  output_paths[]
  declared_authority_scope
  payload_sha256

ContextSafeFragment@1
  item_id
  kind
  primary_coverage[]
  support_only_coverage[]
  decision_basis[]
  content_ref
  lineage_refs[]
  status

ContextSafeSessionContext@1
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

ContextSafeValidationReport@1
  schema
  request_id
  bundle_sha256
  raw_result_sha256 | null
  canonical_result_sha256 | null
  status: STRUCTURALLY_VALID | STRUCTURALLY_INVALID
  input_binding: MATCHES_PACKET | CHANGED | NOT_CHECKED
  output_path_admission: ADMITTED | REJECTED
  errors[]

ContextSafeQualificationRecord@1
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

This contract is complete on its own, because a bounded orchestrator should be able to adopt orchestration mechanics without importing Skeptic.

A host framework may add stricter task-level gates outside orchestration-local meanings, because optional integration can strengthen task ownership without weakening orchestration-local safety.

When Skeptic supplies the host framework, `skeptic.md` remains the authority for Skeptic meanings and loop ownership while this contract supplies optional orchestration mechanics, because the two artifacts own different layers of meaning.
