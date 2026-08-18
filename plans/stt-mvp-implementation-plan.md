# STT MVP Implementation Plan

**Status:** Current bounded construction plan, because the accepted design chain now has a downstream implementation-planning authority.
**Repository:** `saffih/skeptic`, because this plan allocates the STT MVP sources maintained in this repository.
**Purpose:** Build and qualify the accepted STT MVP without changing its product, architecture, or shared durable design, because construction must not become an alternate design authority.
**Scope:** The new `stt_mvp/` Python package, its deterministic tests, its frozen real-model evaluation fixtures, and its implementation evidence are in scope, because these are the smallest artifacts that realize the accepted MVP.
**Exclusions:** Product-code delivery, changes to the five accepted design artifacts, legacy Target Task compatibility, sandboxing claims, rollback, concurrent Run execution, and automatic replay after actual or uncertain launch are excluded, because the Governing Inputs and Architecture do not authorize them in this cycle.

## 1. Plan identity and governing basis

STT design is accepted, and this plan owns bounded construction only, because Governing Inputs, Architecture, SDD, Context Rules, and Design Authority Chain already own the meanings that implementation must preserve.

| Accepted artifact | Exact Git blob |
| --- | --- |
| `plans/stt-mvp-governing-inputs.md` | `66e07d85cf5f41158a9b1d1a282330ad6daaae16` |
| `plans/stt-mvp-architecture-description.md` | `660b9a1c7bfcaa6568c4780475ce5d428d301ffc` |
| `plans/stt-mvp-software-design-description.md` | `16f65eb7908e1b824ced1e2473687810fef2a7f4` |
| `docs/context-rules.md` | `ec1f81fc72343554d1b6cdfb03ca84ad941b6297` |
| `docs/design-authority-chain.md` | `d2e2481afd02f58b4d5d1404351ec1b2dbf9a496` |

An implementation discovery that needs a product objective returns to Governing Inputs, one that needs system-wide meaning returns to Architecture, and one that needs a shared schema, durable algorithm, persistence rule, adapter rule, recovery rule, or qualification strategy returns to the SDD, because this plan may not silently resolve an upstream dependency.

## 2. Implementation ownership map

The package has one primary owner for each concern, because duplicate lifecycle writers or validators would create competing authority.

| Concern and accepted proposition | Primary owner and source | Prerequisite | Verification owner |
| --- | --- | --- | --- |
| Canonical codec, closed schemas, enums, references, and identities | Contract Validator: `stt_mvp/codec.py`, `schema.py`, `identity.py`, `records.py` | none | `tests/stt_mvp/test_codec.py`, `test_schema.py`, `test_identity.py` |
| Run, Task, Round, Plan, Operation, package, and event persistence | Ledger Store: `stt_mvp/ledger.py` | contracts and host probes | `tests/stt_mvp/test_ledger.py`, `test_faults.py` |
| Event grammar, prefix snapshots, state precedence, and next action | State Deriver: `stt_mvp/state.py` | records and ledger reader | `tests/stt_mvp/test_state.py` |
| Target admission, authority subset, and routing admission | Authority Engine: `stt_mvp/authority.py`, `observer.py` | contracts and host probes | `tests/stt_mvp/test_authority.py`, `test_observer.py` |
| Bootstrap, target/store distinction, frozen runtime, and host floor | Bootstrap: `stt_mvp/bootstrap.py`, `host.py`, `runtime.py` | contracts, ledger primitives, observer | `tests/stt_mvp/test_bootstrap.py`, `test_host.py` |
| Boundary publication, binding, and lifecycle façade | Boundary: `stt_mvp/boundary.py` | every mechanical owner above | `tests/stt_mvp/test_boundary.py` |
| Provider request/return translation and capture | Provider Adapter: `stt_mvp/provider.py` | operation contracts and exchange store | `tests/stt_mvp/test_provider.py` |
| Exact command launch and local settlement | Command Adapter: `stt_mvp/command.py` | operation contracts and exchange store | `tests/stt_mvp/test_command.py` |
| Admitted launch, attempt separation, and exchange closure | Launcher: `stt_mvp/launcher.py` | Boundary, provider, command | `tests/stt_mvp/test_launcher.py` |
| Bounded verified committed-history expansion | History Reader: `stt_mvp/history.py` | ledger and prefix validator | `tests/stt_mvp/test_history.py` |
| Semantic role wire contracts and result decoding | Planner, Worker, Validator adapters: `stt_mvp/roles.py` | contracts, history, launcher | `tests/stt_mvp/test_roles.py` |
| Unique depth-first action request | Lead: `stt_mvp/lead.py` | State Deriver and Boundary | `tests/stt_mvp/test_lead.py` |
| Known-fact recovery and operational failure/blocker handling | Recovery controller: `stt_mvp/recovery.py` | state, ledger, launcher | `tests/stt_mvp/test_recovery.py` |
| `start`, `run`, `status`, and `diagnose` | Public command adapter: `stt_mvp/cli.py` | Bootstrap, Lead, Recovery, Boundary | `tests/stt_mvp/test_cli.py` |

`stt_mvp/boundary.py` is the only production caller of ledger publication and Launcher launch methods, because the accepted `single-boundary-api` and `boundary-mediated-transitions` propositions forbid bypass paths.

`stt_mvp/state.py` is side-effect free, and `stt_mvp/lead.py` requests exactly the action it derives from committed state, because lifecycle meaning must come from immutable history rather than a mutable cursor.

The source allocation deliberately uses ordinary Python modules rather than a framework, registry, plug-in system, generic storage layer, or abstract controller hierarchy, because no accepted proposition requires those additional mechanisms.

## 3. Source contracts and dependency direction

| Source | Owns | Must not own |
| --- | --- | --- |
| `codec.py` | canonical UTF-8 JSON bytes and strict parsing | lifecycle interpretation |
| `identity.py` | domain-separated SHA-256 and UUID validation | record publication |
| `schema.py` and `records.py` | closed record validation and typed construction | semantic adequacy |
| `host.py` and `runtime.py` | host probes, locks, byte I/O, and frozen runtime manifests | route choice or Task judgment |
| `ledger.py` | packages, create-only installation, append, and verified reads | admission or next-action choice |
| `state.py` | event grammar, prefix manifests, and derived state | mutation, repair, or launch |
| `authority.py` and `observer.py` | subset, route, target-object, and re-observation checks | capability expansion or target mutation |
| `bootstrap.py` | complete pre-publication Run admission | planning or validation |
| `provider.py`, `command.py`, and `launcher.py` | one admitted adapter exchange and observed transport facts | retries, fallback, or evidence publication |
| `history.py` | bounded read-grant responses with omission facts | mutation or curated history |
| `roles.py` | exact role request and result binding | Plan alteration or parent judgment |
| `boundary.py` | admission, coordination, binding, and receipts | semantic decomposition or Task sufficiency |
| `lead.py` | one derived action request and depth-first ordering | direct mutation |
| `recovery.py` | resume validation and safe evidence requirement | guessed repair or replay |
| `cli.py` | public argument handling and read-only outputs | a second lifecycle path |

Dependencies flow from codec and schemas through storage and derivation, then admission and launch, then roles and orchestration, because each downstream concern needs stable bytes and committed facts before it can be falsified.

## 4. Construction slices

Every slice must preserve all earlier passing tests and leave one reviewable change set, because a bounded reversible increment exposes contradiction before later orchestration depends on it.

### Slice A — canonical contracts and deterministic core

**Objective:** Create canonical bytes, closed contracts, references, identities, and event vocabulary, because every later component exchanges these durable facts.

**Design propositions realized:** `canonical-control-codec`, `domain-separated-identity`, `typed-reference-boundary`, the SDD lifecycle-contract tables, and canonical event vocabulary are realized, because these are shared data decisions already accepted by the SDD.

**Files:** Add `stt_mvp/__init__.py`, `codec.py`, `identity.py`, `schema.py`, `records.py`, and `tests/stt_mvp/{__init__.py,test_codec.py,test_identity.py,test_schema.py}`, because these files isolate pure deterministic contracts.

**Prerequisites:** None exist, because this slice establishes the base contract.

**Actions:** Implement strict codec decoding, exact closed-field validators, SDD enums, reference-family validation, and every SDD identity formula without self-hashed fields, because readers and writers must reject ambiguous bytes identically. H is domain-separated with the literal accepted tag, uint64 big-endian length framing where specified, and exact ordered input bytes, because textual concatenation is not an identity encoding. Canonical JSON bodies use accepted canonical UTF-8 bytes, direct strings use exact UTF-8 bytes, direct numeric inputs use `uint64_be`, raw SHA-256 bytes are used only where the SDD says so, and absent or null inputs contribute no implicit bytes unless explicitly defined, because host serialization must not become shared meaning. Implement every SDD identity family with frozen ordering and representation, and exclude each self-derived field from its own preimage, including `requirement_id = H("stt-requirement-v1", step id, uint64_be(requirement ordinal), canonical OutputRequirement body excluding requirement_id)`, because cyclic or accidental preimages are nonconforming. Validate schema identity as `<name>@<positive-version>` separately from the distinct closed version-independent `CanonicalRecordKind`, use only the exact accepted schema-to-kind mapping, and reject unsupported versions, missing, mismatched, inferred, guessed, or embedded-only mappings, because schema identity must not acquire record-kind authority.

**Tests and commands:** Run `python3 -m unittest tests.stt_mvp.test_codec tests.stt_mvp.test_identity tests.stt_mvp.test_schema`, because all Slice A behavior is deterministic and local.

**Pass:** Known-good fixtures round trip to identical bytes and every malformed, duplicate-key, non-finite, unknown-field, noncanonical spelling, domain-collision, reference-binding, self-field, preimage-encoding, unsupported-version, missing-mapping, mismatched-mapping, inferred-mapping, and embedded-schema record-kind fixture is rejected, because acceptance must be falsifiable.

**Stop:** Stop if a required field, value space, identity input, or reference meaning is absent from the accepted SDD, because the plan cannot define shared contracts.

**Escalation:** Return missing shared contract meaning to the SDD, because only that owner can amend it.

**Evidence:** Save test output, fixture hashes, and source SHA in the slice receipt, because later promotion must bind observations to exact bytes.

### Slice B — durable ledger and derived state

**Objective:** Implement package-first persistence, verified ledgers, prefix snapshots, and pure state derivation, because recovery depends on committed history rather than anticipated memory.

**Design propositions realized:** `authoritative-committed-history`, `pure-derived-state`, event grammar, ledger sequencing, hash chain, package publication, and next-action precedence are realized, because the SDD assigns their shared mechanisms.

**Files:** Add `host.py`, `ledger.py`, `state.py`, `tests/stt_mvp/{test_host.py,test_ledger.py,test_state.py,test_faults.py}`, because persistence and derivation must be separately testable while sharing only validated records.

**Prerequisites:** Slice A must pass, because ledger records require canonical bytes and identities.

**Actions:** Implement no-replacement same-directory package installation, file and directory flush hooks, lock ordering, immutable JSONL ledger append, transition and event hashing, prefix manifests, complete grammar validation, and the exact SDD precedence list, because each operation must reconstruct the same next action from a snapshot.

**Tests and commands:** Run `python3 -m unittest tests.stt_mvp.test_host tests.stt_mvp.test_ledger tests.stt_mvp.test_state tests.stt_mvp.test_faults`, because crash-visible prefixes need deterministic fault injection.

**Pass:** A valid prefix derives one action, malformed or competing history derives `INVALID`, ledger sequence and hash-chain checks reject alterations, and prefix snapshots bind exactly their JSONL bytes, because recovery may not select by preference.

**Stop:** Stop if host behavior cannot be observed or a failure point cannot be represented by the package/ledger boundary, because a silent durability substitute is nonconforming.

**Escalation:** Return a missing durable-publication meaning to the SDD, and report unsupported host capability as a Bootstrap blocker, because implementation may not emulate a weaker floor.

**Evidence:** Save fault schedule, expected durable prefix, observed prefix, derived action, and test output, because each interruption result must be reviewable.

### Slice C — Bootstrap, target admission, and authority

**Objective:** Admit one immutable Run basis only when target, store, runtime, routes, and authority are valid, because semantic work must not begin on unresolved operational facts.

**Design propositions realized:** `bootstrap-admission`, `host-capability-floor`, `admitted-operational-authority`, target-path authority, trusted-minimum admission, and Context Rules persistence behavior are realized, because the accepted chain assigns them to Bootstrap, Authority Engine, and Target Observer.

**Files:** Add `authority.py`, `observer.py`, `runtime.py`, `bootstrap.py`, and `tests/stt_mvp/{test_authority.py,test_observer.py,test_bootstrap.py}`, because each module has one distinct mechanical ownership.

**Prerequisites:** Slices A and B must pass, because admission freezes validated records and writes only through Ledger Store.

**Actions:** Probe each required host capability in private store and target probe objects; resolve no-follow object identities; reject a store under or equal to target; freeze runtime bytes, interpreter, and dependencies; intersect routing constraints; enforce authority subsets; and publish no partial Run, because a Run basis is immutable after admission.

Slice C constructs and validates the complete unpublished Bootstrap candidate, while Slice D makes `start` publication occur through Boundary, because Bootstrap must not become an alternate Ledger Store caller before the Boundary façade exists.

**Tests and commands:** Run `python3 -m unittest tests.stt_mvp.test_authority tests.stt_mvp.test_observer tests.stt_mvp.test_bootstrap`, because path, route, and capability errors are deterministic.

**Pass:** Traversal, links, object identity ambiguity, subset widening, untrusted Planner or Validator route, constraint mismatch, silent substitution, and missing capability all block before Run publication, because admission must fail closed.

**Stop:** Stop on a required unsupported host behavior or an SDD ambiguity about target identity, routing, or frozen runtime coverage, because a new fallback would change shared design.

**Escalation:** Return shared mechanism questions to the SDD and host failures to the operator with probe evidence, because neither may be guessed inside a plan.

**Evidence:** Save host-probe records, frozen-runtime manifest, candidate input identities, and admission receipt, because same-Run execution must later validate those exact facts.

### Slice D — Boundary, adapters, attempts, and settlement

**Objective:** Implement the one authorized effect path from admitted request through sealed exchange to observed outcome, because actual, uncertain, and non-launch states must remain distinguishable.

**Design propositions realized:** `single-boundary-api`, `operation-attempt-separation`, `sealed-adapter-exchange`, capture policy, command profiles, and settlement rules are realized, because the SDD gives these mechanisms closed semantics.

**Files:** Add `provider.py`, `command.py`, `launcher.py`, `boundary.py`, deterministic fakes under `tests/stt_mvp/fakes.py`, and `tests/stt_mvp/{test_provider.py,test_command.py,test_launcher.py,test_boundary.py}`, because adapters need conformance tests without a real provider.

**Prerequisites:** Slices A through C must pass, because an adapter receives only an admitted immutable request and exchange location.

**Actions:** Make Boundary commit attempt-started and launch-intent events in order; make adapters create-only write request, raw return, tool, process, timing, and settlement facts; classify launch and settlement exactly; preserve capture prefixes and incompleteness; bind only matching sealed exchanges; and prohibit internal retry, provider/model change, route fallback, or adapter publication, because transport is not semantic judgment.

**Tests and commands:** Run `python3 -m unittest tests.stt_mvp.test_provider tests.stt_mvp.test_command tests.stt_mvp.test_launcher tests.stt_mvp.test_boundary`, because fake transports can deterministically falsify every adapter state.

**Pass:** Tests cover proven non-launch, uncertain launch, launched success, malformed or truncated return, incomplete tool transcript, route mismatch, continuing process, unknown settlement, process settlement, and sealed-outcome recovery, because happy-path transport cannot establish interrupted-effect safety.

**Stop:** Stop if an adapter needs a provider-specific behavior not representable by its accepted canonical envelope, because adding a shared adapter contract belongs to the SDD.

**Escalation:** Return required envelope or capture semantics to the SDD, because implementation cannot invent them.

**Evidence:** Save sealed exchange directory hashes, attempt and outcome record references, captured completeness facts, and conformance output, because later recovery must verify exact bytes.

### Slice E — History, semantic roles, and depth-first control

**Objective:** Give trusted roles bounded verified evidence and execute the uniquely derived Planner, Worker, child Task, and Validator lifecycle path, because semantic judgment must be separate from persistence and control invention.

**Design propositions realized:** `context-handling`, `bound-evidence`, required-output assessment, Planner decline, child authority narrowing, depth-first child execution, Validator repeat, and `validator-owned-outcome` are realized, because Architecture and SDD already specify those boundaries.

**Files:** Add `history.py`, `roles.py`, `lead.py`, and `tests/stt_mvp/{test_history.py,test_roles.py,test_lead.py}`, because history delivery, wire binding, and deterministic orchestration are separate owners.

**Prerequisites:** Slices A through D must pass, because roles consume committed prefixes and Boundary-admitted launches.

**Actions:** Verify ledgers before History Reader returns grant-bounded records; record returned and omitted material including response-limit facts; bind role results to admitted operation and prefix; assess required outputs mechanically before validation; and have Lead call Boundary once per derived action while traversing child Tasks depth first, because no role may mutate parent lifecycle state.

**Tests and commands:** Run `python3 -m unittest tests.stt_mvp.test_history tests.stt_mvp.test_roles tests.stt_mvp.test_lead`, because binding and grammar errors are mechanically falsifiable.

**Pass:** Tests prove authorized History Reader expansion beyond `starting_selectors`, response-limit behavior, Planner decline, required-output failures, Worker result binding, child depth-first behavior, child authority subset rejection, Validator repeat, and no direct role publication, because semantic role contracts still need structural enforcement.

**Stop:** Stop if a role needs an unstated shared result field, lifecycle disposition, or context authority rule, because the plan cannot supply semantic continuation meaning.

**Escalation:** Return role or shared context decisions to Architecture or SDD according to the Design Authority Chain, because the downstream plan has no authority to create them.

**Evidence:** Save role request and returned-byte hashes, committed prefix references, read-grant receipts, output assessments, and test output, because semantic evidence needs lineage.

### Slice F — recovery and public commands

**Objective:** Recover only from known facts, expose read-only diagnosis, and provide the exact public command surface, because an interrupted Run must remain honest without silently progressing.

**Design propositions realized:** `known-fact-recovery`, interrupted-effect non-replay, operational failure/blocker handling, public operations and receipts, and read-only `RunView` behavior are realized, because the SDD owns their shared meanings.

**Files:** Add `recovery.py`, `cli.py`, `tests/stt_mvp/{test_recovery.py,test_cli.py}`, and `tests/stt_mvp/test_integration.py`, because recovery and public behavior require end-to-end verification after their underlying owners exist.

**Prerequisites:** Slices A through E must pass, because recovery validates the complete persisted graph and public commands use Boundary only.

**Actions:** Validate runtime, ledgers, packages, exchanges, and references before deriving recovery; never automatically replay an actual or uncertain launch; require explicit evidence for safe continuation; permit only uniquely eligible package commit, settlement observation, sealed import, and explicitly permitted finalization; make `status` and `diagnose` read-only; and make `run` stop at policy invocation limit or another authorized operational blocker without inventing a lifecycle cap or product-visible cancellation, because public control must not rewrite semantic state.

**Tests and commands:** Run `python3 -m unittest tests.stt_mvp.test_recovery tests.stt_mvp.test_cli tests.stt_mvp.test_integration`, because the observable public and recovery paths require integration traces.

**Pass:** Tests prove torn-final-line handling, corrupt-history `INVALID`, actual/uncertain non-replay, proven-nonlaunch later attempt only after return, status/diagnose nonmutation, recovery, one-step success, multi-step operational stop, child operational stop, Validator failure, target mutation re-observation, exact four-command dispatch, and absence of a public cancellation path, because recovery cannot be accepted from a happy-path restart.

**Stop:** Stop when history has zero or multiple safe actions, a target fact changes, or a launch remains uncertain without sealed outcome or settlement, because the only honest result is blocker or operational stop.

**Escalation:** Report the exact evidence requirement to the operator, and return missing recovery meaning to the SDD, because neither a CLI nor this plan may manufacture facts.

**Evidence:** Save diagnostic output, derived `RunView`, immutable event references, integration trace, and source/test hashes, because promotion needs source-bound results.

### Slice G — qualification and promotion evidence

**Objective:** Assemble deterministic, host, integration, negative-search, and real-model evidence against one candidate, because implementation acceptance requires evidence that exercises the exact bytes.

**Design propositions realized:** `qualification-matrix`, host-contract testing, adapter conformance, integration qualification, and promotion evidence binding are realized, because the SDD assigns shared strategy while this plan owns procedures.

**Files:** Add `tests/stt_mvp/test_negative_searches.py`, `tests/stt_mvp/test_real_model_protocol.py`, `tests/stt_mvp/fixtures/`, and the `analysis/stt_mvp_evaluation` evidence directory, because fixtures and evidence protocol must be versioned independently from production code.

**Prerequisites:** Slices A through F must pass, because qualification must exercise an integrated candidate rather than scaffolding.

**Actions:** Run the complete deterministic suite, host probes on selected filesystems, fault schedules, static forbidden-mechanism searches, and frozen real-model missions; record provider/model identity when observable; and generate one promotion manifest binding accepted design blobs, this plan blob, candidate commit, test sources, results, host probes, and model evidence, because no result applies to different bytes.

**Tests and commands:** Run `python3 -m unittest discover -s tests/stt_mvp -t .`, `git diff --check`, and the command sequence in Section 8, because deterministic checks and evidence identity require separate observations.

**Pass:** Every required deterministic test passes, every required host capability is observed, forbidden searches return zero matches outside explicitly named tests, real-model evidence is complete for applicable routes, and every manifest identity equals the tested candidate, because qualification cannot promote partial or mismatched evidence.

**Stop:** Stop on unavailable provider access, unobservable provider identity, a failed host capability, a missing evidence binding, or a required real-model gate without an authorized route, because contract tests cannot substitute for the missing observation.

**Escalation:** Report `RUNTIME_UNVERIFIED` or the exact blocker without promotion, because real-model evidence is evidence rather than proof and missing evidence must remain visible.

**Evidence:** Produce `analysis/stt_mvp_evaluation/promotion-manifest.json`, raw deterministic output, probe output, frozen mission packets, role transcripts, and human scorecards, because review needs retrievable primary evidence.

## 5. Deterministic test ownership

| Obligation | Falsification owner |
| --- | --- |
| canonical JSON rejection, unknown fields, schema closure, domain-separated identities, and reference binding | Slice A tests |
| event grammar, ledger sequence/hash chain, prefix snapshots, state precedence, atomic create/install/append, and lock sequencing | Slice B tests |
| target object/path admission, authority subset, route constraints, trusted-minimum capability, and no silent route substitution | Slice C tests |
| non-launch, uncertain launch, malformed/truncated provider return, process settlement, and attempt/outcome separation | Slice D tests |
| History Reader expansion, response limits, required-output assessment, child depth-first behavior, Planner decline, and Validator repeat | Slice E tests |
| recovery, operational stops, exact public commands, absence of cancellation, and read-only status/diagnose | Slice F tests |
| integrated paths, forbidden searches, host probes, and real-model protocol binding | Slice G tests |

Each test names the owning source module and the SDD proposition in its docstring or fixture label, because a failure must identify its mechanical owner without creating a parallel design registry.

## 6. Fault-injection matrix

Each injection uses a test-only failpoint supplied by the owning module and asserts the next recovered state from persisted bytes, because an exception alone does not prove crash-prefix safety.

| Durable boundary | Before owner | After owner | Required recovered assertion |
| --- | --- | --- | --- |
| file flush | Slice B Ledger Store | Slice B Ledger Store | no unsealed record is accepted |
| directory flush | Slice B Ledger Store | Slice B Ledger Store | installed bytes are either absent or fully verified |
| rename | Slice B Ledger Store | Slice B Ledger Store | package remains absent or uniquely eligible |
| package installation | Slice B Ledger Store | Slice B Ledger Store | no duplicate competing package is chosen |
| ledger append | Slice B Ledger Store | Slice B Ledger Store | torn final append only receives the SDD-permitted treatment |
| launch intent | Slice D Boundary and Launcher | Slice D Boundary and Launcher | no automatic replay after possible effect |
| adapter return | Slice D Provider or Command Adapter | Slice D Provider or Command Adapter | sealed matching result imports or uncertainty remains visible |
| settlement observation | Slice D Launcher | Slice F Recovery | local settlement is observed or `UNKNOWN`, never fabricated |
| phase finalization | Slice D Boundary | Slice F Recovery | one finalization occurs only when uniquely implied |

No fault-point test is marked complete before its listed owner exists, because planned coverage is not executable evidence.

## 7. Host capability qualification

`stt_mvp/host.py` owns private behavioral probes for no-follow metadata, path identity, exclusive create, same-directory atomic rename without replacement, file flush, directory flush, append durability, advisory lock, exact byte I/O, process identity, local settlement observation, and monotonic time, because platform labels do not establish mount-specific capability.

`stt_mvp/bootstrap.py` runs the probes beneath the selected store and target roots and blocks `start` with each probe result when any required capability is unavailable, because the accepted host floor has no weakening fallback.

`tests/stt_mvp/test_host.py` uses fake probes for deterministic branch coverage, and the Slice G host receipt captures real selected-filesystem results, because unit tests cannot establish the operator's actual mount behavior.

## 8. Verification command contract

Use these commands from the candidate repository root after each affected slice, because commands must be repeatable and their source scope explicit.

```text
python3 -m unittest tests.stt_mvp.test_codec tests.stt_mvp.test_identity tests.stt_mvp.test_schema
python3 -m unittest tests.stt_mvp.test_host tests.stt_mvp.test_ledger tests.stt_mvp.test_state tests.stt_mvp.test_faults
python3 -m unittest tests.stt_mvp.test_authority tests.stt_mvp.test_observer tests.stt_mvp.test_bootstrap
python3 -m unittest tests.stt_mvp.test_provider tests.stt_mvp.test_command tests.stt_mvp.test_launcher tests.stt_mvp.test_boundary
python3 -m unittest tests.stt_mvp.test_history tests.stt_mvp.test_roles tests.stt_mvp.test_lead
python3 -m unittest tests.stt_mvp.test_recovery tests.stt_mvp.test_cli tests.stt_mvp.test_integration
python3 -m unittest discover -s tests/stt_mvp -t .
python3 capabilities/well_check/well_check.py plans/stt-mvp-implementation-plan.md
git diff --check
```

The implementation agent must replace `python3` with the repository's pinned project interpreter only when one is added by a separately accepted dependency change, because this plan may not prescribe an unaccepted environment mechanism.

The public command adapter exposes exactly `start`, `run`, `status`, and `diagnose`, and no `stop` or cancellation command, because product-visible command meaning is fixed upstream. Lead remains domain-blind, derives or requests only the uniquely implied lifecycle action from admitted committed state, does not interpret substantive artifact or content meaning, does not invent semantic continuation, and never directly mutates lifecycle state, because orchestration must remain a mechanical control boundary.

The frozen runtime manifest establishes admitted controller semantics across process invocations, while no particular controller OS or process identity is required to persist, because semantic continuity is a runtime-reference property rather than a persistent controller process. Process identity remains required where command launch and settlement observation need it, because effect observation is distinct from controller continuity. A runtime-manifest mismatch blocks execution because execution under different semantics would violate the admitted Run basis.

Prior-Run evidence is imported only as immutable advisory current-Run input with source binding, and it never merges lifecycle histories, continues the prior Run, establishes current authority, or proves freshness, because current obligations require current observation or source review. History Reader treats `starting_selectors` as navigation, not evidence authority; allowed record kinds and prefixes are the mechanical ceiling; `max_bytes` applies per response; receivers may request additional already-authorized evidence; unavailable or unauthorized required evidence is explicit; and summaries or digests are not authority, because the semantic receiver determines required evidence.

## 9. Real-model evaluation

Slice G freezes representative missions, authority packets, routes, committed prefixes, Context Rules source references, and scoring rubrics before invoking Planner, Worker, or Validator, because a changing mission or context cannot support a repeatable evaluation claim.

The mission set covers decomposition quality, cheapest-adequate permitted route choice, authority narrowing, evidence retrieval, continuation, stagnation, and independent validation, because these are the accepted semantic-role risks that deterministic tests cannot prove.

Each evaluation records requested and observed provider/model identity when observable, configured route, frozen policy, role contract, complete input prefix, returned bytes, tool-transcript completeness, human scoring, and unavailable observations, because requested routing and actual execution remain distinct facts.

An evaluation result is supporting evidence rather than proof of semantic correctness, because model judgment is not mechanically exhaustible.

## 10. Forbidden-mechanism searches

Slice G adds deterministic repository searches that fail when production sources contain direct Ledger Store publication outside `boundary.py`, direct provider or command launch outside `launcher.py`, a mutable lifecycle cursor, silent route fallback, automatic replay after uncertain launch, store placement beneath target root, duplicate accepted-evidence locations, or a reference treating historical plan text as current design authority, because local tests can otherwise leave bypasses unexercised.

The searches allow only narrowly named test fixtures that intentionally model a forbidden condition, because negative tests must not make the production prohibition unsearchable.

## 11. Integration and promotion gates

Integration starts only after every preceding slice has its passing receipt and no upstream contradiction, because later orchestration cannot safely mask a missing lower-level invariant.

Implementation acceptance requires a promotion manifest that binds the five accepted design blobs, current plan blob, implementation candidate commit SHA, test-source SHA, deterministic results, host probe results, frozen real-model evidence, and relevant requested and observed provider/model identities, because evidence about different bytes cannot qualify the candidate.

No promotion is allowed for a deterministic failure, missing or failed host capability, unresolved authority conflict, unavailable required real-model evidence, incomplete fault matrix, forbidden-search failure, or identity mismatch, because the accepted SDD makes each unresolved condition a blocker.

## 12. Plan completion and escalation

This plan is complete when a competent implementation agent can execute Slices A through G with no semantic invention and each cited decision has exactly one accepted upstream owner, because bounded construction requires both implementable detail and preserved authority boundaries.

Implementation stops at the first concrete missing shared/durable decision or upstream contradiction and records the exact source, proposal, and affected slice without editing that source, because downstream work must return the decision to its legitimate owner.

Mechanical WELL PASS and a RunSkeptic Fix Loop are acceptance checks for this plan, not implementation qualification or product-code delivery, because document conformance and review are distinct from the construction work this plan schedules.
