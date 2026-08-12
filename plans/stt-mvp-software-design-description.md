# Sequential Target Task MVP Software Design Description

**Repository:** `saffih/skeptic`, because this metadata identifies the repository that owns the design.
**Governing Inputs:** Sequential Target Task MVP Governing Inputs, because that document owns accepted STT product constraints.
**Architecture Description:** Sequential Target Task MVP Architecture Description, because that document owns STT system-wide meaning.
**Authority chain:** Design Authority Chain, because that document assigns design-layer ownership.
**Document profile:** WELL, because that document defines this artifact's mechanical design-document profile.
**Downstream owner:** a bounded current Implementation Plan, because construction detail belongs below this shared design.
**Historical evidence:** the prior STT MVP Implementation Plan, because retained historical material is not current authority.
**Scope:** shared and durable realization choices for the STT MVP, because this SDD owns shared mechanisms rather than bounded construction.

This document owns the architecture-permitted shared realization of STT, because components, contracts, schemas, persistence, lifecycle derivation, adapters, authority admission, recovery, evidence binding, host requirements, and qualification need one current owner before bounded implementation can begin.

The accepted Governing Inputs and Architecture Description govern every proposition here, because the Software Design Description may refine their permitted variation but may not change product or system-wide meaning.

The existing Implementation Plan is stale historical evidence rather than current authority, because it binds a superseded Architecture and previously owned shared decisions assigned here by the accepted Design Authority Chain.

No implementation sequence, source-file allocation, or merge instruction is authoritative here, because a current bounded Implementation Plan must derive those realization details from unchanged accepted governing links.

## Design basis and limits

`design-priority` — STT uses one append-only filesystem history, one deterministic Boundary façade, and one sequential driver around trusted semantic roles, because this is the smallest shared mechanism that preserves the Architecture propositions `authoritative-committed-history`, `boundary-mediated-transitions`, `one-active-frontier`, and `trusted-semantic-roles` together.

`controller-target-separation` — The authoritative Run store and frozen controller reside outside the live target workspace, because target effects must not rewrite the history or runtime that judges and records them.

`honest-control-limit` — The design validates admitted operations and observed results without claiming sandbox containment, rollback, exclusive target access, or complete external-effect detection, because the Governing Input `non-goals` limits STT to coordination rather than operating-system control.

`finite-operation-limits` — Run policy may freeze finite limits for individual records, captures, waits, paths, trees, and provider calls but must not impose a fixed total number of Tasks, Rounds, Plan steps, or semantic calls, because `semantic-continuation` permits implementation safeguards without overriding Planner and Validator judgment.

`canonical-owned-name` — Every STT-owned schema, event, status, disposition, path key, and enum uses one exact case-sensitive spelling made from ASCII letters, digits, and `_`, with lowercase kebab-case reserved for semantic proposition names, because stable spelling prevents internal ambiguity while keeping prose references distinct from machine values.

An unknown shared choice that would alter product behavior, system boundaries, or an Architecture invariant blocks downstream planning, because the Design Authority Chain requires the decision to return to its upstream owner rather than appear implicitly in realization.

Every accepted Architecture proposition has one primary realization location here, because downstream review must recover complete coverage without inferring links from similar vocabulary:

| Architecture Description proposition | Primary SDD realization |
|---|---|
| `sequential-control-loop` | component ownership; event grammar and state derivation |
| `immutable-mission-and-authority` | lifecycle contracts; Bootstrap, frozen runtime, and host floor |
| `trusted-semantic-roles` | component ownership; lifecycle contracts |
| `one-active-frontier` | event grammar and state derivation |
| `boundary-mediated-transitions` | component ownership; persistence and publication |
| `simplest-adequate-execution` | authority and target admission; launch, adapters, and settlement |
| `admitted-operational-authority` | authority and target admission |
| `authoritative-committed-history` | persistence and publication; evidence and history access |
| `context-handling` | component ownership; persistence and publication; evidence and history access |
| `validator-owned-outcome` | lifecycle contracts; event grammar and state derivation |
| `recovery-from-known-facts` | recovery and operator control |
| `qualification-boundary` | qualification strategy |

## Component ownership

The shared component graph has one canonical owner for each responsibility, because duplicate writers or validators would create competing authority:

| Component | Owned responsibility | Excluded responsibility |
|---|---|---|
| Bootstrap | freeze Run basis, target identity, runtime, policy, routing, and imported prior evidence | semantic planning or lifecycle judgment |
| Boundary | validate, admit, authorize and coordinate publication and launch, bind, and return bounded receipts | mission decomposition or Task sufficiency judgment |
| Lead | derive and request the uniquely implied next action | direct state mutation or semantic invention |
| State Deriver | validate committed history and derive one current state and next action | persistence, launch, or repair by preference |
| Ledger Store | canonical encoding, create-only byte installation, transition-package storage, and durable append under Boundary command | admission, lifecycle interpretation, or an independent caller surface |
| Contract Validator | schema and cross-record validation | acceptance of semantically inadequate content |
| Authority Engine | authority subset checks, route admission, and target-object admission | capability expansion or route selection |
| Launcher | perform one Boundary-commanded admitted launch and capture transport facts | admission, retry policy, or semantic acceptance |
| Provider Adapter | translate one canonical request and return one canonical transport envelope | lifecycle publication or silent provider substitution |
| Command Adapter | launch one exact admitted process profile and observe local settlement | shell-policy invention or target-scope expansion |
| History Reader | expose bounded verified committed records to semantic roles | mutation or curated replacement history |
| Target Observer | identify and re-observe target objects without following authority outside scope | containment claims or implicit target mutation |
| Planner | return one finite Plan or decline under admitted routes | lifecycle publication or parent-Task judgment |
| Worker | perform one accepted semantic step and report local outcome and effects | Plan changes or parent-Task judgment |
| Validator | judge Task satisfaction and choose finish or repeat | transport classification or state mutation |

`single-boundary-api` — Bootstrap, Lead, semantic roles, adapters, and public commands interact with authoritative state only through Boundary operations, because `boundary-mediated-transitions` forbids any alternate publication or launch path.

`pure-derived-state` — Contract validation and state derivation are deterministic and side-effect free over an explicit committed-history snapshot, because recovery must produce the same result without hidden cursor state.

`replaceable-adapter-core` — Provider and command adapters depend on canonical Boundary contracts rather than storage internals, because provider volatility must not alter lifecycle semantics or evidence identity.

## Canonical control data

`canonical-control-codec` — Every identity-bearing control record uses UTF-8 canonical JSON with lexicographically sorted object keys, compact separators, exactly one terminal LF, finite integers, no duplicate keys, no non-finite numbers, one required schema identity, and rejection of unknown fields unless that schema names an extension point, because independent readers must derive identical bytes and hashes.

Captured stdout, stderr, raw provider returns, and produced files remain binary artifacts instead of canonical JSON, because arbitrary evidence may not be text and must retain exact bytes.

Schema identifiers use `<name>@<positive-version>` and a version changes whenever accepted bytes or meaning change incompatibly, because readers must reject unknown semantics rather than guess from shape.

`domain-separated-identity` — Stable identities use SHA-256 over the literal domain tag plus canonical identity inputs while excluding the field that stores the resulting identity, because equal bytes in different lifecycle roles must not collide semantically and self-hashing records would be cyclic.

`H` hashes one ASCII domain tag followed by each input encoded as an unsigned 64-bit big-endian byte length and those exact bytes, and renders the digest as lowercase hexadecimal, because concatenation without lengths or one canonical output spelling would leave identity derivation ambiguous.

The required identity families are structural contracts, because independent writers and readers need the same derivation boundaries:

```text
run_id               random lowercase UUIDv4, fixed before Run publication
root_task_id         H("stt-root-task-v1", run_id, root Task spec, authority, required outputs)
child_task_id        H("stt-child-task-v1", parent task, round number, step id, child Task step)
round_id             H("stt-round-v1", task id, round number)
plan_id              H("stt-plan-v1", planner operation request, accepted Plan body)
step_id              H("stt-step-v1", plan id, step ordinal, accepted step body)
input_id             H("stt-input-v1", step id, uint64_be(dependency ordinal), canonical DependencySpec bytes)
requirement_id       H("stt-requirement-v1", step id, uint64_be(requirement ordinal), canonical OutputRequirement bytes)
authority_id         H("stt-authority-v1", canonical TaskAuthority bytes excluding authority_id)
routing_identity     H("stt-routing-v1", canonical RoutingFile bytes excluding routing_identity)
prefix_id            H("stt-prefix-v1", exact RunPrefixManifest JSONL bytes including terminal LF)
operation_request_id H("stt-operation-v1", canonical OperationRequest body)
attempt_id           H("stt-attempt-v1", operation request id, attempt ordinal)
artifact_id          H("stt-artifact-v1", canonical artifact identity body)
record_id            H("stt-record-v1", record kind, logical path, size, content hash)
observation_id       H("stt-observation-v1", canonical observation body)
transition_id        H("stt-transition-v1", canonical TransitionManifest bytes)
event_hash           H("stt-event-v1", canonical committed event preimage)
```

Ordinals and ledger sequence numbers are unsigned contiguous integers beginning at zero, because gaps or alternate starting conventions would make reconstruction ambiguous.

`typed-reference-boundary` — Fixed genesis content uses `ContentRef`, content inside the same uncommitted transition package uses `PayloadRef`, content in a committed package uses `RecordRef`, and arbitrary evidence uses `ArtifactRef`, because publication phase and evidentiary meaning require distinct non-cyclic references.

The reference records use the following exact fields, because a reference must identify both bytes and their authority context without phase-dependent inference:

```text
ContentRef
  schema
  record_id
  relative_path
  size_bytes
  sha256

PayloadRef
  schema
  record_id
  payload_path
  size_bytes
  sha256

RecordRef
  schema
  record_id
  task_id
  ledger_sequence
  event_kind
  transition_id
  payload_path
  size_bytes
  sha256

PrefixRef
  schema
  prefix_id
  run_id
  manifest_path
  sha256
```

## Lifecycle contracts

The canonical contracts are closed schemas with no implicit fields, because Boundary must reject unowned meaning before it enters history:

| Contract | Required meaning |
|---|---|
| `RunRecord` | Run identity, store root identity, target identity, frozen runtime identity, policy, routes, root Task inputs, and imported prior-evidence references |
| `TaskRecord` | Task identity, parent lineage, immutable mission, authority, required outputs, and creation basis |
| `RoundRecord` | Task identity, contiguous Round number, and prior committed-history head |
| `Plan` | Planner operation identity, nonempty ordered steps, route choices, inputs, requirements, expected outputs, and authority requests |
| `Step` | ordinal, kind, mission or command profile, bounded inputs, required outputs, route, and requested authority |
| `OperationRequest` | role, exact instruction/data envelope, exact accepted contract and route/profile references, input/output bindings, and committed prefix; authority, capture, and wait meaning is obtained through those frozen references |
| `AttemptRecord` | operation identity, ordinal, adapter, and launch basis; its exchange directory is deterministic from the admitted Attempt identity and authoritative layout |
| `AttemptOutcome` | launch state, transport state, local settlement, complete-or-truncated capture references, and adapter/settlement evidence; WorkerResult and Command StepResult records own reported semantic effects |
| `StepResult` | bound step, local semantic outcome when present, output-contract status, effect report, accepted artifacts, and operational evidence |
| `ValidatorResult` | Task judgment, lifecycle disposition, reason, findings, unknowns, and cited artifacts |
| `TaskResult` | terminal Task judgment, final Round and Validator result, terminal required-output assessment, satisfied output bindings/artifacts, and terminal evidence references |

The canonical wire schemas use the following exact field vocabulary, because component interoperability must not depend on a downstream plan inventing shared names:

```text
RootTaskSpec
  schema
  mission
  root_authority_spec
  required_outputs[]
  initial_input_selectors[]
  prior_evidence_selectors[]
  run_policy
  routing_constraints | null
  routing_identity

RunRecord
  schema
  run_id
  root_task_spec_ref
  routing_ref
  run_policy_ref
  initial_import_refs[]
  prior_import_refs[]
  source_identity_ref
  target_identity_ref
  store_root_identity
  run_root_relative_path
  frozen_runtime_manifest_ref
  exchange_root_identity
  live_provider_authorized
  created_at

TaskRecord
  schema
  task_id
  run_id
  parent_task_id | null
  parent_round_number | null
  parent_step_id | null
  mission_ref
  authority_ref
  required_outputs_ref
  created_from_ref

RoundRecord
  schema
  round_id
  task_id
  round_number
  predecessor_round_id | null
  continuation_validator_result_ref | null
```

`created_at` uses canonical RFC 3339 UTC with whole seconds and a `Z` suffix but does not participate in a derived identity, because diagnostic time needs one representation without making wall-clock precision a lifecycle input.

Authority and routing use the following exact shared records, because admission must compare one closed structure across Bootstrap, Planner, Boundary, adapters, and children:

```text
PathScope
  root
  kind: EXACT | SUBTREE

RootAuthoritySpec
  schema
  read_scopes[]: PathScope
  write_responsibility_scopes[]: PathScope
  allowed_step_kinds[]: WORKER | COMMAND | TASK
  allowed_worker_routes[]
  allowed_command_profiles[]
  allowed_inherited_env_names[]
  allowed_external_effect_classes[]

TaskAuthority
  schema
  authority_id
  target_identity_ref
  read_scopes[]: PathScope
  write_responsibility_scopes[]: PathScope
  allowed_step_kinds[]: WORKER | COMMAND | TASK
  allowed_worker_routes[]
  allowed_command_profiles[]
  allowed_inherited_env_names[]
  allowed_external_effect_classes[]
  parent_authority_ref | null

ProviderRoute
  schema
  route_name
  adapter_kind: FAKE | CODEX | CLAUDE_CODE
  provider_id
  executable_identity
  fixed_argv_prefix[]
  requested_provider
  requested_model
  requested_effort
  capability_rank
  cost_rank
  quality_rank
  admitted_effect_classes[]
  admitted_inherited_env_names[]
  fixed_env{}
  cwd_policy
  wait_policy
  capture_policy
  local_termination_policy
  read_tool_transport

CommandProfile
  schema
  profile_name
  executable_identity
  argv_template[]
  argument_slots{}
  cwd_policy
  fixed_env{}
  admitted_inherited_env_names[]
  admitted_effect_classes[]
  exit_code_outcomes{}
  wait_policy
  capture_policy
  local_termination_policy
  output_observations{}
  effect_report_target_path | null
```

The shared policy value spaces are closed records, because admission must reject values whose meaning is not defined here:

```text
exit_code_outcomes: map of canonical decimal nonnegative exit code to SATISFIED | UNSATISFIED | INDETERMINATE; an unmapped code is an operational command error, not a semantic outcome
output_observations: map<string, CommandOutputObservation>
CommandOutputObservation { required: boolean, source: STDOUT | STDERR | TARGET, max_bytes: positive integer, preserve_prefix: boolean, target: null for STDOUT or STDERR | { canonical_target_path: string, observation_kind: PATH_IDENTITY | FILE_BYTES | TREE_MANIFEST } for TARGET }
argument_slots: map of slot name to ArgumentSlot
ArgumentSlot: exactly one of { kind: STRING } | { kind: INTEGER, minimum: canonical decimal integer | null, maximum: canonical decimal integer | null } | { kind: BOOLEAN_FLAG, emitted_flag_token: nonempty string } | { kind: ENUM, allowed_values: nonempty array of distinct nonempty strings } | { kind: TARGET_PATH } | { kind: INPUT_PATH }; fields not belonging to the selected kind are forbidden. INTEGER renders as canonical base-10 decimal with no leading `+` or leading zero except `0`, and any present minimum is not greater than any present maximum. BOOLEAN_FLAG emits its exact frozen token only for true and omits it for false. TARGET_PATH resolves by ordinary admitted target-path resolution; INPUT_PATH binds only to a resolved admitted InputRef.
cwd_policy: exactly one of { kind: STORE_ROOT } | { kind: TARGET_ROOT } | { kind: EXACT_ADMITTED_PATH, path: canonical admitted path }
local_termination_policy: WAIT_FOR_EXIT | WAIT_FOR_SETTLEMENT | TERMINATE_AFTER_GRACE
read_tool_transport: FILE_REFERENCE | BOUNDED_JSON_LINES
capability_rank: positive integer where a larger rank represents a route accepted as capable of every obligation accepted at a smaller rank
cost_rank: positive integer where a smaller rank represents lower configured relative cost within the frozen RoutingFile
quality_rank: positive integer where a larger rank represents higher configured relative quality within the frozen RoutingFile
RoutingConstraints: { permitted_provider_ids[]: nonempty distinct strings | null, permitted_route_names[]: nonempty distinct strings | null, planner_minimum_capability_rank: positive integer | null, validator_minimum_capability_rank: positive integer | null, worker_minimum_capability_rank: positive integer | null, cost_preference: NONE | LOWEST_AVAILABLE | BALANCED, quality_preference: NONE | HIGHEST_AVAILABLE | BALANCED }; null permitted sets and minimums impose no additional constraint
host_profile: { filesystem_identity: string, process_identity: string, supports_no_follow: boolean, supports_atomic_same_parent_rename: boolean, supports_exclusive_create: boolean, supports_file_flush: boolean, supports_directory_flush: boolean, supports_append_durability: boolean, supports_advisory_lock: boolean, supports_exact_byte_io: boolean, supports_process_identity: boolean, supports_settlement_observation: boolean, supports_monotonic_time: boolean }
producer_constraint: { kind: ANY_ADMITTED_PRODUCER } | { kind: STEP, step_id: string } | { kind: ROUTE, route_name: string } | { kind: OPERATION_ROLE, role: PLANNER | WORKER | COMMAND | VALIDATOR }
provenance: exactly one of { kind: BOOTSTRAP_IMPORT, source_identity: string, committed_record_ref: RecordRef } | { kind: PRIOR_RUN_IMPORT, source_identity: string, committed_record_ref: RecordRef } | { kind: TARGET_OBSERVATION, source_identity: string, observation_ref: RecordRef } | { kind: WORKER_OUTPUT, operation_request_id: string, committed_record_ref: RecordRef } | { kind: COMMAND_OUTPUT, operation_request_id: string, committed_record_ref: RecordRef } | { kind: CHILD_TASK_OUTPUT, child_task_id: string, child_task_result_ref: RecordRef } | { kind: BOUNDARY_OBSERVATION, source_identity: string, committed_record_ref: RecordRef }; fields not belonging to the selected kind are forbidden
observation_kind: PATH_IDENTITY | FILE_BYTES | TREE_MANIFEST | PROCESS | PROVIDER | TIMING | SETTLEMENT
observed_identity: { kind: TARGET_OBJECT | EXECUTABLE | PROVIDER | PROCESS, identity: string, observed_at: RFC3339_UTC }
prelaunch_identity_snapshot: { target_identity: string | null, executable_identity: string | null, admitted_execution_identity: { kind: PROVIDER_ROUTE, route_identity: string } | { kind: COMMAND_PROFILE, profile_name: string, profile_identity: string }, authority_identity: string, captured_at: RFC3339_UTC }
stt_read_grant: { committed_prefix_ref: PrefixRef, allowed_record_kinds: nonempty array<CanonicalRecordKind>, max_bytes: positive integer, starting_selectors: array<source_selector> }
stt_starting_subtree: { run_root_relative_path: string, subtree_identity: string, manifest_ref: RecordRef }
```

`CanonicalRecordKind` is exactly one Contract Validator-accepted canonical schema identity from `RunRecord`, `TaskRecord`, `RoundRecord`, `Plan`, `OperationRequest`, `AttemptRecord`, `AttemptOutcome`, `CaptureRecord`, `PlannerResult`, `WorkerResult`, `StepResult`, `ValidatorResult`, `TaskResult`, `TaskOutputAssessment`, `ArtifactRef`, `InputRef`, `InputResolution`, `TransitionManifest`, `EventBody`, `LedgerEvent`, `RunPrefixManifest`, or `PrefixTaskHead`, and every `record_kind` and `allowed_record_kinds` field uses this closed set rather than an unknown string, because unknown arbitrary strings must not silently acquire shared record meaning.

`source_selector` is one closed selector record with `kind`, `source_identity`, and kind-specific fields, because every selector must bind to an admitted source rather than to an ambient path:

```text
kind: RECORD | ARTIFACT | PATH | REQUIREMENT | PRIOR_RUN_RECORD
source_identity: required string for every variant
RECORD: record_kind: CanonicalRecordKind, record_id
ARTIFACT: artifact_id
PATH: relative_path, object_type
REQUIREMENT: requirement_id, producer_constraint
PRIOR_RUN_RECORD: source_run_id, record_kind: CanonicalRecordKind, record_id, import_hash
```

`initial_input_selectors` and `prior_evidence_selectors` use this grammar, because their different source sets do not justify different matching semantics. Boundary resolves within the named admitted source and exact identity binding, returns zero matches as `UNRESOLVED_INPUT`, rejects more than one match as `AMBIGUOUS_INPUT`, orders selectors by array position and records within one selector by `record_id`, and never applies semantic fallback, because deterministic resolution must expose stale, missing, and ambiguous sources rather than guess. A missing source, changed source identity, stale import hash, or failed object verification is `STALE_SOURCE` and blocks admission or producer completion as applicable, because an unverified substitute would cross an authority boundary.

`stt_read_grant.committed_prefix_ref` and `allowed_record_kinds` are the complete mechanical authority ceiling for committed-history retrieval, while `starting_selectors` are a receiver-resolvable navigation entrance rather than an exhaustive evidence limit, because the adopted Context Rules reserve evidence sufficiency to the semantic receiver and deny a producer-selected starting context authority over later retrieval.

A Planner, Worker, or Validator may request from History Reader any record or artifact reachable in its admitted committed prefix whose kind its `stt_read_grant` allows, when its obligation requires that evidence, because bounded context must not silently revoke already-admitted evidence authority. `max_bytes` limits one History Reader response rather than the receiver's total permissible retrieval; a response that cannot fit returns exact resolvable references and an explicit `HISTORY_RESPONSE_LIMIT` condition without truncation, substitution, or semantic conclusion, because an operation may make further bounded retrieval requests while unavailable or unauthorized required evidence must remain visible.

Bootstrap converts `RootAuthoritySpec` into the root `TaskAuthority` by binding the frozen target identity and derived authority identity, because caller-owned authority must cross one mechanical admission boundary before semantic execution.

External effect classes are exactly `TARGET_READ`, `TARGET_WRITE`, `LOCAL_PROCESS`, `PROVIDER_CALL`, `NETWORK`, and `REMOTE_MUTATION`, because routes, profiles, Plans, and reported effects need one shared capability vocabulary.

The live adapters are disabled unless Bootstrap freezes explicit live-provider authorization, while `FAKE` is always local and deterministic, because accidental external calls must fail before Run publication.

Executable identity binds an absolute no-follow path plus exact executable bytes or one maintained resolver plus its observed result, because ambient `PATH` lookup could change authority after Bootstrap.

Command argument slots are exactly `STRING`, `INTEGER`, `BOOLEAN_FLAG`, `ENUM`, `TARGET_PATH`, or `INPUT_PATH`, and each template token is either one literal or one whole slot, because concatenation and shell interpretation would create a second unreviewed command language.

Environment construction begins empty, adds frozen non-secret literals, and then adds only admitted inherited names without persisting their values, because ambient environment is an undeclared capability and potential secret channel.

Policy and route registries use the following exact shared fields, because finite safeguards and permitted execution choices must be frozen rather than reconstructed from command defaults:

```text
RunPolicy
  schema
  max_control_record_bytes
  max_control_nesting_depth
  max_path_bytes
  max_capture_bytes_per_stream
  max_raw_return_bytes
  max_input_bytes_per_operation
  max_output_bytes_per_operation
  max_tree_entries_per_object
  max_history_response_bytes
  planner_wait_seconds
  worker_wait_seconds
  command_wait_seconds
  validator_wait_seconds
  settlement_wait_seconds
  termination_grace_seconds
  max_control_transitions_per_public_invocation
  routing_constraints: RoutingConstraints
  host_profile

RoutingFile
  schema
  routing_identity
  planner_route: ProviderRoute
  validator_route: ProviderRoute
  worker_routes{}: ProviderRoute
  command_profiles{}: CommandProfile
```

Every Run-policy limit is a positive finite integer with units fixed by its field name, because zero, infinity, or implicit units would create incompatible host behavior.

`max_control_transitions_per_public_invocation` is a positive finite interruptibility bound frozen in `RunPolicy`, because one public invocation must have an explicit finite control safeguard without imposing a semantic lifecycle total. `RunPolicy` contains no cumulative Task, depth, Round, Plan-step, or semantic-call limit, because Governing Input `semantic-continuation` assigns those totals to Planner and Validator judgment.

Bootstrap derives effective routing constraints by intersecting every non-null permitted-provider and permitted-route set from the Root Task and Run policy and by taking the larger present minimum capability rank for each role, while rejecting an empty intersection or any fixed Planner or Validator route below its effective minimum, because `planning-and-validation-capability` requires a configured trusted floor and `mission-routing-constraints` permits either source to narrow execution without silently weakening the other.

Boundary admits a Planner or Validator operation only when its fixed route is in the effective permitted provider and route sets and its capability rank meets the effective role minimum, and it admits a Worker route only when the same applicable Worker constraints hold, because requested provider, model, and effort identify an execution request but do not prove that its frozen route has the required configured capability.

Planner chooses among Boundary-admissible routes and records the selected route and effective routing constraints in the accepted Plan, because the configured cost and quality preferences guide trusted adequacy judgment while Boundary must remain mechanical. Boundary rejects any Plan route that is unavailable, outside the effective constraints, or below the role minimum and never substitutes another route, because route preference cannot authorize a weaker or different execution than the accepted Plan.

Planning records use the following exact shared fields, because Planner-local readable keys must become Boundary-derived lifecycle identities without changing the accepted Plan:

```text
ReturnedPlan
  schema: ReturnedPlan@1
  planner_operation_request_id
  task_id
  round_id
  steps[1..]

CommonStep
  step_key: nonempty string unique within ReturnedPlan.steps[]
  kind: WORKER | COMMAND | TASK
  description: nonempty string
  declared_read_scopes[]: array of admitted authority read scopes in declared order
  declared_write_responsibility_scopes[]: array of admitted authority write-responsibility scopes in declared order
  dependency_specs[]: DependencySpec in dependency_key order
  output_requirement_specs[]: OutputRequirementSpec in requirement_key order

WorkerStep extends CommonStep
  worker_route: admitted ProviderRoute.route_name
  instruction: nonempty string
  stt_read_grant: stt_read_grant

CommandStep extends CommonStep
  command_profile: admitted CommandProfile.profile_name
  arguments{}: map of CommandProfile.argument_slots names to values valid for their slots; no other key
  output_source_bindings{}: map of requirement_key to profile_observation_name

TaskStep extends CommonStep
  child_mission: nonempty string
  child_authority: TaskAuthority that is a structural subset of the parent Task authority
  stt_starting_subtree | null
```

`ReturnedPlan` contains exactly the fields above and one selected variant for every array member of `steps[]`; `CommonStep` is not itself a returned variant, and fields outside the selected `WorkerStep`, `CommandStep`, or `TaskStep` variant are forbidden, because a tagged returned step must have one complete and non-ambiguous semantic meaning.

`DependencySpec` and `OutputRequirementSpec` are Planner-return records rather than persisted identity-bearing records, because Boundary derives their durable identities. `DependencySpec` has exactly `dependency_key`, `kind`, `source_selector | null`, `producer_step_key | null`, `producer_requirement_key | null`, `purpose`, and `required_media_type`, because those fields are the complete returned dependency meaning. `OutputRequirementSpec` has exactly `requirement_key`, `purpose`, `object_type`, `media_type`, `location`, `path_policy`, `path | null`, `required_mode | null`, `satisfaction_mode`, `expected_sha256 | null`, and `producer_constraint`, because those fields are the complete returned output requirement meaning. `dependency_key` and `requirement_key` are nonempty strings unique in their owning step, because Boundary must be able to derive durable identities without treating a human-readable key as a durable identifier.

Step, dependency, and requirement keys are unique within their owning Plan or step and dependency edges may point only to earlier steps, because readable Planner notation must not create identity ambiguity or cycles. `INITIAL_IMPORT`, `PRIOR_IMPORT`, `RUN_ARTIFACT`, and `TARGET_PATH` require `source_selector` and forbid both producer keys, because those sources are not produced by a prior step. `PREVIOUS_STEP_OUTPUT` and `CHILD_TASK_OUTPUT` require both producer keys and forbid `source_selector`, because their producer must be explicit. Every producer step key names an earlier returned step whose requirement key names one of that step's output requirements, because dependency provenance must not be missing or cyclic.

The one persisted accepted `Plan` is `Plan@1` with exactly `schema`, `plan_id`, `planner_operation_request_id`, `task_id`, `round_id`, `effective_routing_constraints`, and `steps[1..]`, where `steps[]` is the nonempty ordered array of embedded canonical `Step@1` records, because there must be no duplicate persisted Plan form. A canonical `Step` has exactly `schema`, `step_id`, `step_ordinal`, `kind`, `description`, `declared_read_scopes[]`, `declared_write_responsibility_scopes[]`, `inputs[]`, `output_requirements[]`, and the fields of exactly one selected variant, because a persisted step must be complete and exclusive. `WORKER` has `worker_route`, `instruction`, and `stt_read_grant`, `COMMAND` has `command_profile`, `arguments{}`, and `output_source_bindings{}`, and `TASK` has `child_mission`, `child_authority`, and `stt_starting_subtree | null`, because the selected kind fixes the exact variant fields. `step_ordinal` is the zero-based `steps[]` position, `inputs[]` is the `InputRef@1` array in returned dependency order, and `output_requirements[]` is the `OutputRequirement@1` array in returned requirement order, because immutable embedded order is needed for execution and identity.

Boundary accepts `ReturnedPlan@1` only when its planner operation, Task, and Round equal the admitted Planner `OperationRequest`, every selected route or profile is admitted, every declared scope and child authority is a subset of the immutable Task authority, and every returned value satisfies the closed grammar above, because Boundary must reject unadmitted durable meaning. Boundary derives `effective_routing_constraints` from the frozen Run and Task constraints, converts each returned dependency and requirement specification to its canonical `InputRef@1` and `OutputRequirement@1` form, replaces producer keys with their already-derived `step_id` and `requirement_id`, and publishes that one `Plan@1`, because semantic return requires Boundary lifecycle binding. It does not persist `ReturnedPlan`, `step_key`, `dependency_key`, or `requirement_key`, because Planner-return notation is semantic input while the accepted Plan is the Boundary-derived durable lifecycle record.

For identity derivation, the `accepted Plan body` in `plan_id` is the canonical JSON object formed from the `Plan@1` field vocabulary excluding `plan_id`, all `step_id` fields, all `input_id` fields, and all `requirement_id` fields, because stored identities may not be cyclic. Its `steps[]` retain their order and use the returned semantic fields with producer keys resolved to their earlier ordinal and requirement position, because identity inputs must be reconstructible. The `accepted step body` in `step_id` is the corresponding canonical `Step@1` object excluding `step_id`, `inputs[]`, and `output_requirements[]`, because those fields are independently derived. `input_id` uses the canonical `DependencySpec` bytes at that dependency ordinal, and `requirement_id` uses the canonical `OutputRequirement` bytes at that requirement ordinal, because the existing identity family fixes those preimages. Boundary then writes each derived ID only in its owning canonical record, because these non-cyclic preimages make independently reconstructed Plan, Step, input, and requirement identities exact.

The accepted Plan is persisted exactly once at `rounds/<round-number>/plan.json` in the `PLANNING_FINISHED` transition package together with its accepted `PlannerResult`, because History Reader and recovery need one committed source for the embedded canonical Steps. A Worker or Command `OperationRequest` has the exact accepted `plan_id` and `step_id` for its embedded Step, while a Planner or Validator request has null `plan_id` and null `step_id`; a child Task instead binds the parent `step_id` in its immutable `TaskRecord`, because every step-phase, result, child lineage, and later History Reader reference must resolve one unambiguous canonical Plan and Step without persisting another Step copy.

Inputs and outputs use the following exact shared records, because substitution-sensitive consumption and mechanically verified production require canonical bindings:

```text
DependencySpec
  dependency_key
  kind: INITIAL_IMPORT | PRIOR_IMPORT | RUN_ARTIFACT | TARGET_PATH | PREVIOUS_STEP_OUTPUT | CHILD_TASK_OUTPUT
  source_selector | null
  producer_step_key | null
  producer_requirement_key | null
  purpose
  required_media_type

InputRef
  schema: InputRef@1
  input_id
  kind
  source_identity
  source_selector | null
  intended_consumer_step_id
  purpose
  required_media_type

InputResolution
  schema
  input_id
  consumer_step_id
  resolved_artifact_ref
  resolution_phase: PLAN_ACCEPTANCE | PRODUCER_COMPLETION
  target_identity_ref | null
  observed_path_identity | null

OutputRequirement
  schema: OutputRequirement@1
  requirement_id
  purpose
  object_type: REGULAR_FILE | DIRECTORY_TREE
  media_type
  location: RUN | TARGET
  path_policy: EXACT | BOUNDARY_ASSIGNED
  path | null
  required_mode | null
  satisfaction_mode: PRESENT | NONEMPTY | EXACT_SHA256
  expected_sha256 | null
  producer_constraint

ArtifactRef
  schema
  artifact_id
  object_type: REGULAR_FILE | DIRECTORY_TREE
  media_type
  location: RUN | TARGET
  relative_path
  sha256 | null
  size_bytes | null
  mode | null
  provenance
  requirement_id | null
  purpose
  observation_kind
  observed_identity

OutputAssessmentEntry
  requirement_id
  status: SATISFIED | UNSATISFIED | UNREADABLE
  selected_artifact_ref | null
  reason_code | null

TaskOutputAssessment
  schema
  task_id
  round_id
  phase: PRE_VALIDATION | TERMINAL
  entries[]
  all_satisfied
```

`BOUNDARY_ASSIGNED` is valid only for immutable Run artifacts while every target output uses one admitted exact target-relative path, because effectful work must know its live destination before launch and content-derived Run storage need not be selected by a Worker.

`EXACT_SHA256` requires `expected_sha256` while the other satisfaction modes forbid it, because each mode needs one non-overlapping interpretation.

Boundary selects at most one satisfying artifact per requirement using immutable Run artifacts before target observations and then lowest artifact identity, because deterministic bounded assessment must not depend on directory order or unbounded candidate lists. Each assessment is committed by an event whose `event_kind` is `OUTPUT_ASSESSMENT_RECORDED` and whose phase matches the record, because committed history must distinguish the pre-validation assessment from the terminal assessment.

Operations and outcomes use the following exact shared records, because replay, transport, settlement, semantic return, and Task judgment must remain distinct:

```text
OperationRequest
  schema
  operation_request_id
  role: PLANNER | WORKER | COMMAND | VALIDATOR
  run_id
  task_id
  round_id
  plan_id | null
  step_id | null
  exact_contract_ref
  exact_inputs[]
  input_bindings[]
  output_requirements[]
  output_bindings[]
  route_or_profile_ref
  stt_read_grant
  committed_prefix_ref

AttemptRecord
  schema
  attempt_id
  operation_request_id
  attempt_ordinal
  adapter_kind
  requested_routing
  prelaunch_identity_snapshot

AttemptOutcome
  schema
  launch_state: NOT_LAUNCHED | LAUNCHED | LAUNCH_UNCERTAIN
  transport_state: RETURNED | NO_RETURN
  result_kind: OK | ERR | REJECTED | NONE
  local_settlement: SETTLED | UNSETTLED | UNKNOWN
  requested_routing
  observed_routing
  capture_refs[]: RecordRef<CaptureRecord>
  proof_of_non_launch | null
  error_ref | null
  process_observations[]
  timing_observations[]

CaptureRecord
  schema
  source: STDOUT | STDERR | PROVIDER_RAW_RETURN | TOOL_TRANSCRIPT
  completeness: COMPLETE | TRUNCATED | MISSING
  captured_prefix_ref | null
  original_size_bytes | null
  truncation_marker: boolean
  missing_evidence_reason | null

PlannerResult
  schema
  operation_request_id
  kind: PLAN | DECLINE
  plan | null
  reason
  findings[]
  unknowns[]

WorkerResult
  schema
  operation_request_id
  local_outcome: SATISFIED | UNSATISFIED | INDETERMINATE
  reason
  observations[]
  claimed_outputs[]
  reported_effects[]

StepResult
  schema
  step_id
  source_result_ref | null
  child_outcome_ref | null
  verified_artifacts[]
  observations[]
  reported_effects[]
  local_outcome: SATISFIED | UNSATISFIED | INDETERMINATE | OPERATIONAL_INDETERMINATE
  output_contract_status: SATISFIED | UNSATISFIED | NOT_APPLICABLE
  unsatisfied_requirement_ids[]
  scope_violation_ref | null

ValidatorResult
  schema
  operation_request_id
  judgment: SATISFIED | UNSATISFIED | INDETERMINATE
  disposition: FINISH | REPEAT
  reason
  findings[]
  unknowns[]
  cited_artifact_refs[]

TaskResult
  schema
  task_id
  judgment: SATISFIED | UNSATISFIED | INDETERMINATE
  final_round_ref
  final_validator_result_ref
  terminal_output_assessment_ref
  satisfied_outputs[]
  terminal_evidence_refs[]
```

Every returned `CommandStep.output_source_bindings` key is one of that step's returned requirement keys, because a command output must identify its planned requirement. Boundary converts each key to the matching canonical requirement identity, and each value names one `CommandProfile.output_observations` entry whose source and object type are compatible with that requirement, because the accepted Plan records canonical rather than Planner-local identifiers. Each required command-produced output has exactly one such binding, because command-output satisfaction must resolve to one named frozen observation. A `CaptureRecord` preserves whether each capture is complete, truncated, or missing, its retained prefix when any, original-size knowledge when available, and the truncation or missing-evidence marker, because an `AttemptOutcome` capture reference must not conceal incomplete evidence. `TaskResult.final_round_ref`, `final_validator_result_ref`, and `terminal_output_assessment_ref` bind the exact terminal history, while `satisfied_outputs[]` binds the selected `ArtifactRef` for every terminally satisfied required output and `terminal_evidence_refs[]` binds any other terminal evidence required by the accepted design, because a terminal result must prove the history and assessment that establish its output claim.

Diagnostic reason strings and error messages are data rather than control signals while closed enums and validated references drive derivation, because arbitrary prose must not acquire lifecycle authority.

`PlannerResult.kind: PLAN` requires one nonempty Plan while `DECLINE` requires a null Plan, because one tagged result must not contain contradictory planning decisions.

`NOT_LAUNCHED` requires `RETURNED`, `ERR`, `SETTLED`, and one adapter proof code of `LOCAL_PROCESS_CREATE_FAILED_NO_PROCESS` or `PROVIDER_CONNECT_FAILED_ZERO_BYTES_SENT`, because only positive evidence that no local process or provider bytes began can permit another Attempt.

Timeout, response loss, connection reset after sending, unknown sent-byte count, process identity allocation, provider request identity creation, or adapter crash cannot establish `NOT_LAUNCHED`, because each condition permits hidden effects.

`instruction-data-envelope` — Every semantic request separates authoritative instructions from untrusted evidence data and identifies each item by an immutable reference, because persisted reports and target content must not acquire control authority through prompt placement.

Planner receives the immutable Task basis, current committed prefix, its available bounded History Reader access, target observations, routing constraints, and output contract, because decomposition must use the complete admitted obligation without hidden host context.

Worker receives only the accepted step, granted authority, required inputs, its bounded History Reader access, and output contract, because execution economy and least authority forbid inheriting the Planner's full capability implicitly.

Validator receives the immutable Task basis and its bounded History Reader access to committed admissible evidence through one stable prefix, because independent judgment must cover the Task obligation without observing a moving history.

Planner and Validator returns are accepted only when one complete schema-valid semantic result is bound to the exact OperationRequest, because free text or mismatched request identity cannot become lifecycle authority.

Worker return separates `SATISFIED`, `UNSATISFIED`, and `INDETERMINATE` local outcomes from transport and output-contract status, because local semantic judgment, process settlement, and evidence completeness are different facts.

Validator return separates Task judgment `SATISFIED`, `UNSATISFIED`, or `INDETERMINATE` from disposition `FINISH` or `REPEAT`, because `validator-owned-outcome` requires mission meaning and continuation to remain explicit.

`validator-disposition-rules` — Boundary rejects `SATISFIED` with `REPEAT`, accepts `REPEAT` only for `UNSATISFIED` or `INDETERMINATE`, and never fabricates a judgment after Validator failure, because lifecycle control must preserve the Architecture's semantic constraints.

## Authority and target admission

`structured-authority` — Operational authority is a closed structured grant over operation kinds, target roots, target-relative objects, read and write modes, command profiles, providers, routes, history scopes, artifact publication, and child delegation, because prose permission cannot support deterministic subset checks.

A child authority grant must be a structural subset of its parent grant and every accepted Plan or step grant must be a subset of the immutable Task authority, because no downstream role may expand capability through interpretation.

Planner may choose only routes and mechanisms present in both Run policy and Task authority and satisfying effective routing constraints, because `simplest-adequate-execution` permits semantic selection only within admitted constraints.

Boundary rejects an unavailable or forbidden route without substitution, because silent fallback would replace the Planner's accepted cost and capability judgment.

`command-profile-admission` — An effectful command refers to a frozen command profile containing executable identity, argument grammar, environment allowlist, working-directory rule, input mode, capture policy, settlement probe, and effect-report requirement, because arbitrary shell text would bypass structured authority.

Command invocation uses direct argument vectors unless a specifically admitted profile owns shell interpretation, because implicit shell parsing can create effects not represented by the accepted step.

`target-object-identity` — A target object is admitted by target-root identity plus canonical relative path and verified component traversal, because textual prefix checks do not protect against symlinks, aliases, mount changes, or traversal syntax.

Canonical target-relative paths use `/` separators, exclude empty, `.`, and `..` components, exclude absolute and platform-prefixed forms, and use one normalized Unicode form frozen by policy, because equivalent textual paths must not identify different authority objects.

Canonical target-relative paths reject NUL, symlinks, and non-regular or non-directory special objects, because the intended object must be inside admitted scope and have a verifiable identity. `.git` is not rejected categorically, because repository metadata is not itself an upstream product prohibition; aliasing, traversal, unsupported objects, and unverifiable identity still fail closed through the ordinary target-admission mechanism.

Every mutating target operation resolves each existing path component without following links outside the admitted target identity and revalidates the final parent immediately before mutation, because host state can change between planning and effect.

An absent leaf may be created only beneath a verified admitted parent while any identity mismatch, unsupported object type, link ambiguity, or host-inability result fails closed before mutation, because `target-path-authority` requires intended-object identity rather than best-effort path permission.

STT records but does not claim complete detection of unreported effects, because the Architecture limits enforcement to admitted and observed operations.

A reported out-of-authority effect commits a violation record, stops later Plan steps, and remains available to Validator after settlement, because honest evidence must preserve the breach without compounding it.

## Persistence and publication

`authoritative-run-layout` — One Run root contains immutable Bootstrap records, one frozen runtime, lock files, and a Task registry whose post-genesis facts live only in transition packages, because ordinary readable files need one stable navigation and authority convention:

```text
<store-root>/runs/<run-id>/
├── run.json
├── bootstrap/
│   ├── root-task-spec.json
│   ├── routing.json
│   ├── run-policy.json
│   ├── target-identity.json
│   ├── source-identity.json
│   ├── runtime-source-manifest.json
│   ├── initial-inputs/
│   └── prior-imports/
├── runtime/
├── runtime-manifest.json
├── locks/
│   ├── runner.lock
│   └── writer.lock
└── tasks/<task-id>/
    ├── task.json
    ├── mission.md
    ├── authority.json
    ├── required-outputs.json
    ├── ledger.jsonl
    └── transitions/<sequence>-<event-kind>/
        ├── manifest.json
        └── payload/
```

Transition payloads use one closed logical namespace, because independent producers, readers, and references must agree where each accepted fact resides:

```text
rounds/<round-number>/...
prefixes/<prefix-id>.jsonl
operations/<operation-request-id>/...
attempts/<attempt-id>/...
steps/<step-id>/...
artifacts/<artifact-id>/...
observations/<observation-id>.json
results/task-result.json
control/...
```

Each logical path appears in exactly one transition package and later events refer to that committed location by `RecordRef`, because recreating a logical path would duplicate accepted authority.

Provider or process exchange bytes live beneath `<store-root>/exchanges/<run-id>/` and are non-authoritative until Boundary imports and binds them into a committed transition package, because active external writers must not write inside authoritative history.

Bootstrap and Task-genesis files are authoritative at their fixed paths while every later accepted record exists exactly once at a package-relative payload path, because duplicate canonical copies would create competing history.

`create-only-publication` — Every authoritative file other than a Task ledger is written completely to a same-parent temporary path, flushed, atomically installed without replacement, followed by destination-directory flush and no-follow reread verification, because visibility without durability and final identity verification is insufficient for crash-safe authority.

`append-only-ledger` — Each `ledger.jsonl` is the one authoritative file excluded from `create-only-publication` and is extended only by durable append of one canonical line under `writer.lock`, because `transition-package` orders the package before its ledger line and rewriting the ledger through temporary-path installation would destroy the append durability that `host-capability-floor` requires.

The two durability classes are exhaustive and disjoint over authoritative files, because recovery cannot decide whether a partially visible file is a failed create-only install or a torn append without knowing which protocol produced it.

Bootstrap constructs a complete candidate Run in a private staging directory beside the final Run directory, installs all records and payloads there, flushes every file, flushes the staging directory, and atomically renames the staging directory to the final Run directory in the same parent, because same-parent rename is the host-capability-floor mechanism that publishes one complete immutable basis. Readers consider a Run committed only when the final Run directory exists and contains its complete fixed records, and ignore staging-directory names, because the rename itself is the sole publication point. Boundary uses the identical protocol for a candidate Task: it builds a private staging directory beside `tasks/<task-id>`, flushes files and directory, then atomically renames it to that final path, because Run and Task genesis must share one durability semantic.

Before either rename, Boundary flushes each file, flushes all payload subdirectories, flushes the staging directory, performs the same-parent atomic rename without replacement, and flushes the containing parent directory, because readers and recovery need both complete visibility and durable name publication; a crash before rename leaves only private staging, commits nothing, and permits recovery to remove that confined uncommitted staging orphan, because no final name has been published; after rename but before the containing-parent flush, the rename is not necessarily durable and recovery may expose no final directory or the complete final directory, because the name durability barrier has not completed; if it is absent, publication did not survive and Boundary may recreate it from the unchanged deterministic basis, while if it is present Boundary validates the complete fixed basis and treats a partial final basis as `INVALID` without repair by choosing among files, because recovery may not invent a genesis basis; after the containing-parent flush the final name is durably published, and a name collision rejects publication without replacement, because no partial genesis is accepted; no semantic operation may launch from a newly published Run or Task until its containing-parent directory flush has succeeded, because no semantic effect may depend on a genesis name whose durability is not established.

A Task candidate contains its fixed mission, authority, required outputs, Task record, and genesis ledger event, because readers must observe either no Task or one complete immutable Task basis.

`transition-package` — Every post-genesis event is represented by one package manifest binding the exact next event body and every payload path, hash, and size before the ledger line is appended, because a crash must leave either no accepted transition or one uniquely completable package.

An incomplete transition package whose payloads were installed but whose manifest was not installed is an unaccepted orphan, because the ledger contains no committed event that can authorize those payloads.

Recovery removes such an orphan only after verifying that every installed path is confined to that package's create-only directory and that no ledger line references the package, because cleanup must not erase accepted history or traverse outside the package boundary.

Recovery then reconstructs and publishes a complete replacement package from the still-valid operation inputs, because create-only publication forbids replacing an installed payload while an unaccepted package must remain completable.

If reconstruction, confinement verification, or ledger-reference verification fails, recovery preserves the orphan, marks the Task `INVALID`, and stops further authoritative progress, because uncertain package ownership cannot be resolved by deletion or inference.

The transition and event records use the following exact fields, because package integrity and ledger chaining must be independently reproducible:

```text
TransitionManifest
  schema
  task_id
  ledger_sequence
  event_body
  payloads[]
    payload_path
    sha256
    size_bytes

EventBody
  schema
  event_kind
  task_id
  ledger_sequence
  previous_event_hash | null
  payload_refs[]: PayloadRef

LedgerEvent
  schema
  transition_id
  event_body
  event_hash
```

The transition identity hashes the canonical manifest, and the ledger event hashes its schema, transition identity, event body, prior event hash, Task identity, and sequence without hashing its own `event_hash`, because package contents and event order need a non-cyclic integrity chain.

`previous_event_hash` is `null` in exactly the genesis `TASK_CREATED` event of each Task and non-null in every later event of that Task, because the chain root has no predecessor while `canonical-control-codec` forbids implicit optionality that independent writers would resolve differently.

`RunPrefixManifest` is canonical JSONL containing one `PrefixHeader` with the `RunRecord` reference followed by one `PrefixTaskHead` per Task in sorted Task-identity order, because semantic operations need an immutable snapshot of every committed Task head that is finite at the instant it is produced.

The manifest grows with the Task count of the Run rather than staying within a fixed size, because one head per Task is the minimum that lets a reader exclude records appended after the snapshot.

Each `PrefixTaskHead` contains schema, Task identity, ledger sequence, event hash, and ledger byte size, while the manifest identity hashes its exact bytes including the terminal LF, because readers must exclude records appended after the operation snapshot.

External work occurs without `writer.lock`, because a lock held across provider or command waits would prevent durable control progress. Before publication Boundary acquires `writer.lock`, rereads the current committed Task head, and only then allocates the next `ledger_sequence` and `previous_event_hash`, because an invocation must not prepare a transition against a head consumed by operator stop. It installs the package and ledger line under the lock, revalidates the package binding immediately before append, and releases the lock after durable publication, because prepare/revalidate/commit makes stop and advancement serialize without holding a lock across provider or command waits. A changed head discards the uncommitted candidate and requires rederivation from the new committed facts, because stale transition identity cannot be repaired by reuse.

Boundary holds `runner.lock` for one public Run-advancement invocation rather than the lifetime of external work, because one invocation must not race another driver while operator observation and later recovery remain available.

## Event grammar and state derivation

The closed event vocabulary is structural notation, because exact lifecycle names are required for independent derivation:

```text
TASK_CREATED
ROUND_CREATED
PLANNING_STARTED
OPERATION_REQUESTED
ATTEMPT_STARTED
LAUNCH_INTENT_RECORDED
ATTEMPT_FINISHED
SETTLEMENT_OBSERVED
PLANNING_FINISHED
STEP_STARTED
STEP_FINISHED
VALIDATION_STARTED
VALIDATION_RECORDED
OUTPUT_ASSESSMENT_RECORDED
OPERATOR_STOP_REQUESTED
ROUND_FINISHED
TASK_FINISHED
```

`task-event-grammar` — A Task consists of genesis followed by zero or more contiguous Rounds and at most one terminal Task finalization, because `one-active-frontier` requires one legal sequential history:

```text
TASK_CREATED
{ round }*
[ terminal-task-finalization ]

round
  ROUND_CREATED
  PLANNING_STARTED
  planner-operation
  PLANNING_FINISHED
  { step-phase }*
  OUTPUT_ASSESSMENT_RECORDED(PRE_VALIDATION)
  validation-phase

terminal-task-finalization
  OUTPUT_ASSESSMENT_RECORDED(TERMINAL)
  TASK_FINISHED
```

`planner-operation` and `validator-operation` are each `OPERATION_REQUESTED attempt-sequence`, Worker and Command step operations use that same form, `OperationRequest.role` is exactly `PLANNER`, `WORKER`, `COMMAND`, or `VALIDATOR` rather than `TASK`, one operation owns its one `OPERATION_REQUESTED` and one or more Attempts only under the positive-non-launch rule, an `attempt-sequence` may end at the legal interrupted prefix `ATTEMPT_STARTED` or continue through `LAUNCH_INTENT_RECORDED`, `ATTEMPT_FINISHED`, and settlement evidence, a later `ATTEMPT_STARTED` is legal only after the preceding Attempt has committed positive `NOT_LAUNCHED` evidence with no fixed Attempt count, and the enclosing grammar owns `PLANNING_FINISHED` and `VALIDATION_RECORDED` without duplicating either phase-finalization event in a subgrammar, because operation transport must represent legal interruption and retry without fabricating a second owner for lifecycle finalization.

`PLANNING_FINISHED` binds either one accepted `PlannerResult` including `DECLINE` or one settled Planner operational failure with no fabricated semantic Plan, either settled path may proceed to validation when stop state permits, `validation-phase` is `VALIDATION_STARTED validator-operation VALIDATION_RECORDED` whose finalization binds either one accepted `ValidatorResult` or one settled Validator operational failure with no semantic judgment, only an accepted Validator result authorizes `ROUND_FINISHED`, `REPEAT` closes its Round and permits the next contiguous Round while `FINISH` closes the Round and may proceed to terminal-task-finalization, there is no fixed Round count, and a settled Validator operational failure stops semantic progression without fabricating a Round continuation or `TaskResult`, because planning and validation settlement must remain distinct from accepted semantic results.

`terminal-task-finalization` is legal only after the final accepted Validator result has disposition `FINISH`; `TASK_FINISHED` binds the corresponding exact `TaskResult` and its terminal assessment and evidence references, because terminal output satisfaction cannot be asserted without the committed history that established it.

`step-phase` is either `STEP_STARTED worker-operation STEP_FINISHED`, `STEP_STARTED command-operation STEP_FINISHED`, or `STEP_STARTED child-task-step STEP_FINISHED`, where `child-task-step` publishes the child Task through Boundary, runs its depth-first lifecycle in the child Task ledger, and binds the exact child `TaskResult` or OperationalStop before `STEP_FINISHED` without creating an `OperationRequest` or Attempt for the child lifecycle, because a Task step is not adapter transport; `OUTPUT_ASSESSMENT_RECORDED(PRE_VALIDATION)` occurs after all step phases and immediately before `VALIDATION_STARTED`, `OUTPUT_ASSESSMENT_RECORDED(TERMINAL)` occurs immediately before `TASK_FINISHED`, and every listed Task event is emitted only at one of these positions, because assessments must be ordered and the closed vocabulary must not duplicate lifecycle ownership.

`root-stop-overlay` — `OPERATOR_STOP_REQUESTED` is Run-wide, committed only in the root Task ledger, occurs at most once, and is legal after any committed root frontier at which Boundary can serialize the request safely, because cancellation is a root-level control fact; if a Run was published but its root Task was not, Boundary first publishes the already-determined root Task only when the exact root Task basis is uniquely derivable from frozen Run facts and then commits the stop, while missing, conflicting, or non-unique basis derives `INVALID` and stop never invents semantic Task content, because cancellation cannot create an authority basis; after committed stop there is no new Round, Planner/Worker/Command/Validator `OperationRequest`, Attempt, child Task, `STEP_STARTED`, or `VALIDATION_STARTED`, while already-started work may publish only causally pre-stop `ATTEMPT_FINISHED`, `SETTLEMENT_OBSERVED`, already-determined phase finalization, child-result binding and `STEP_FINISHED`, permitted output assessment, `ROUND_FINISHED`, or terminal `TASK_FINISHED`, because cancellation preserves evidence without authorizing future work; every post-stop fact is causally rooted in work existing at the committed stop frontier and a child Task never owns a stop event, because root cancellation must not become child-owned lifecycle meaning.

An accepted nonempty Plan executes in ordinal order until completion or the first operational failure, output-contract failure, authority violation, unresolved child, or unsettled operation, because later steps must not build on a failed or changing frontier.

A child Task is published only after its parent step starts and is run depth-first until a semantic outcome or blocking stop can be bound back to that step, because parent progression must wait for its deepest unresolved frontier.

`derived-lifecycle-state` — The State Deriver validates every ledger and transition package, then returns one `DerivedState` and one public `RunView` from committed facts alone, because Lead and operators require stable views without an independently mutable cursor.

`DerivedState` identifies the Run, root Task, active Task, active Round, active step, operator-stop reference, blockers, semantic judgment, public outcome, transient outcome, and exactly one next action, because deterministic orchestration must make ambiguity visible.

`RunView` omits internal next-action vocabulary but preserves committed stop, judgment, outcome, active frontier, and blockers, because public status should expose durable meaning without making implementation labels normative.

`DerivedState` has fields `run_id`, `root_task_id`, `active_task_id`, `active_round_id`, `active_step_id`, `operator_stop_ref`, `blockers[]`, `semantic_judgment`, `public_outcome`, `transient_outcome`, and `next_action`, because every derived value must have one named slot. `RunView` has fields `run_id`, `root_task_id`, `committed_prefix`, `active_frontier`, `operator_stop_ref`, `judgment`, `outcome`, and `blockers[]`, because status must expose the durable subset without exposing an internal action vocabulary.

The next-action precedence is fixed by safety class, because corruption and already-produced facts must dominate future launches:

1. invalid or conflicting history
2. commit one uniquely eligible complete transition package
3. observe settlement or recover one sealed adapter outcome
4. wait for active or unknown local settlement
5. stop after actual or uncertain unrecoverable launch
6. finalize one settled operation phase
7. bind one completed child outcome
8. finalize one accepted Validator result, Round, or Task
9. return one finished root judgment
10. honor committed operator stop
11. continue an unlaunched Attempt or start a later Attempt after proven non-launch
12. create the next repeated Round
13. execute the next accepted step
14. call Validator after settled execution or Planner decline or failure
15. call Planner for a new Round
16. create a Round or the uniquely derived root Task

Any history that implies zero or multiple actions where one is required derives `INVALID`, because Lead must not repair authority ambiguity by preference.

Lead performs one derived action at a time through Boundary and derives again from newly committed history, because the sequential loop must never rely on an in-memory anticipated cursor.

## Launch, adapters, and settlement

`operation-attempt-separation` — One immutable `OperationRequest` may have multiple numbered Attempts only when every prior Attempt is positively proven not launched, because request meaning must remain stable while uncertain or actual launch forbids replay.

Boundary commits `ATTEMPT_STARTED` before adapter preparation and commits `LAUNCH_INTENT_RECORDED` immediately before the first action that may reach the provider or process, because recovery needs a durable distinction between preparation and possible effect.

An Attempt launch state is exactly `NOT_LAUNCHED`, `LAUNCH_UNCERTAIN`, or `LAUNCHED`, while local settlement is exactly `SETTLED`, `UNSETTLED`, or `UNKNOWN`, because transport return and continuing local activity are independent facts.

Positive `NOT_LAUNCHED` requires adapter-specific evidence that no request, process, tool call, or target effect could have begun, because absence of a success return does not prove non-launch.

`sealed-adapter-exchange` — Each adapter writes request, launch, raw return, tool events, routing facts, process facts, timing, and settlement observations to one Attempt exchange directory using create-only files, because Boundary may recover a uniquely completed call without trusting mutable process memory.

Boundary imports an exchange outcome only when its request identity, Attempt identity, adapter identity, file closure, and hashes match the admitted launch, because orphaned or cross-request bytes cannot become evidence.

Provider adapters expose exact provider/model identity, route actually used, request id when available, usage, stop reason, tool transcript completeness, and raw return completeness, because requested routing and observed execution must remain distinguishable.

An adapter never retries, changes model, changes provider, repairs semantic output, or invokes tools outside the admitted request, because those choices belong to Planner, Boundary admission, or a later explicit Attempt after proven non-launch.

Command adapters use the admitted executable and argument vector, sanitized allowlisted environment, admitted working directory, separate byte captures, process identity, exit status, signal status, and local settlement probe, because process return alone cannot prove effect completion or target compliance.

Capture truncation preserves the captured prefix, original-size knowledge when available, truncation marker, and missing-evidence status, because bounded storage must not masquerade as complete evidence.

Stdout, stderr, and raw provider returns are retained as bounded ordinary authoritative evidence with exact capture metadata and no automatic semantic redaction, because redaction could alter evidence. Structurally identifiable known secrets and forbidden persisted values are excluded at producer or admission boundaries before capture, while callers must treat Run storage according to its exposure class, because this rule limits accidental persistence without making a broader privacy promise.

## Evidence and history access

`bound-evidence` — Evidence becomes admissible only through a committed record that binds producer, request or observation identity, exact bytes or target identity, provenance, capture completeness, and applicable requirement, because plausible content without lineage cannot support Validator judgment.

A Run artifact stores immutable regular-file bytes or a canonical directory-tree manifest and file set beneath its committing package, because durable evidence must remain reproducible from one authoritative location.

A target artifact stores target identity, canonical relative path, object type, content or tree hash, size, metadata selected by policy, observation time, and observation mechanism without copying mutable target bytes unless the Plan requests an immutable import, because an observation and a retained artifact have different evidentiary meaning.

Externally mutable target facts are re-observed immediately before authoritative use and again when a satisfied output claim depends on them, because elapsed work may invalidate earlier observations.

`required-output-assessment` — Boundary records mechanical presence, identity, provenance, and freshness for every required output before validation and again before accepting `SATISFIED`, because Validator judgment cannot substitute for missing or changed required evidence.

A semantic result may cite only records available in its admitted committed prefix plus target observations created for that operation, because later history must not retroactively support an earlier decision.

History Reader verifies ledger and reference integrity before returning exact bounded records, and every response identifies the committed prefix, requested source, returned references, and any omitted material or response-limit condition, because on-demand context must not become a curated alternate truth or silently narrow a receiver's evidence basis.

Summaries and indexes are disposable navigation aids that cite underlying records and are never accepted as sole evidence, because `authoritative-committed-history` assigns authority to committed records rather than convenience views.

Imported prior-Run evidence is copied as immutable advisory input with source Run identity, source record references, import hashes, and current-Run selector, because useful history may inform reasoning without merging lifecycle authority.

## Bootstrap, frozen runtime, and host floor

`bootstrap-admission` — `start` validates all immutable Run inputs, resolves target and store identities, probes host support, freezes policy and routes, imports selected prior evidence, freezes the controller runtime, and publishes no Run unless the complete candidate is valid, because semantic work must begin from one admitted basis.

The frozen runtime manifest covers every controller, schema, role-contract, and adapter byte that can affect same-Run behavior plus interpreter and dependency identities, because source-tree drift must not replace controller semantics after Run publication.

Same-Run commands re-execute from the frozen runtime and reject a runtime-manifest mismatch, because `immutable-mission-and-authority` fixes controller identity for the lifecycle.

`host-capability-floor` — Bootstrap requires one filesystem and process host that can provide no-follow metadata, canonical path inspection, exclusive create, same-directory atomic rename without replacement, file and directory flush, append durability, advisory locking, exact byte I/O, process identity, local settlement observation, and monotonic time, because the persistence and interrupted-effect mechanisms depend on those observable capabilities.

Bootstrap tests required host behaviors in private probe objects under the selected store and target roots rather than trusting platform names, because capability support can vary by filesystem, mount, or execution environment.

The target and store must be distinct verified object identities and the store must not reside beneath the admitted target tree, because target mutation must not reach authoritative history through ordinary granted scope.

Unsupported no-follow resolution, durability, locking, process observation, or path identity blocks Run creation with explicit capability evidence, because emulation that weakens an Architecture invariant is not a conforming fallback.

Run policy freezes maximum bytes per canonical record, capture, imported artifact, tree entry count, path length, nesting depth, provider wait, settlement observation, and one public invocation, because bounded resource use is legitimate per-operation protection under `finite-operation-limits`.

Expired waits produce explicit unsettled or unknown evidence and never manufacture settlement, non-launch, or semantic failure, because time limits constrain observation rather than external reality.

## Recovery and operator control

`known-fact-recovery` — Resume first validates Bootstrap, runtime identity, every Task ledger, every referenced package, and exchange closure before deriving an action, because recovery may advance only from committed or uniquely sealed facts.

A complete package with the exact next sequence and prior hash may be committed if no competing package exists, because package-first publication makes this one non-effectful completion uniquely implied.

An incomplete final ledger line may be removed only when it is an uncommitted torn append not referenced by any valid package, because truncating any committed or interior history would rewrite accepted facts.

A launched Attempt resumes only by importing one uniquely sealed adapter outcome or by observing later local settlement, because actual or uncertain launch may already have changed the live target.

An actual or uncertain launch with no active work and no uniquely recoverable outcome derives a non-resumable operational stop, because relaunch would violate `interrupted-effects` and fabricated completion would violate `honest-outcomes`.

An Attempt proven not launched may permit a later explicit Attempt while the current public invocation ends first, because positive non-launch supports retry without creating an automatic internal loop.

Corrupt, missing, duplicated, conflicting, or mutated authoritative history derives `INVALID` and preserves all evidence for diagnosis, because deterministic recovery cannot choose among competing pasts.

`operator-stop` — Operator stop commits one root-Task event binding the validated Task-head set observed at request start and immediately before stop commitment, because cross-Task cancellation order must be reconstructable from append-only history.

After committed stop, Boundary permits only settlement, evidence import, and uniquely implied non-effectful finalization causally rooted in operations or child work already present at the committed frontier, because cancellation prevents new work without discarding already-produced facts.

Operator stop never changes Task judgment and remains visible even when already-produced evidence later permits terminal finalization, because operational cancellation and semantic outcome are distinct facts.

## Public operations and receipts

The public command surface is exactly `start`, `run`, `status`, `diagnose`, and `stop`, because the SDD owns these shared names and their interface behavior for this realization. Architecture owns lifecycle capabilities and semantics, while a future change to product-visible required capabilities returns upstream, because implementation may not silently rename the shared surface.

`start` returns the immutable Run identity, authoritative Run root, root Task identity when published, and one compact Bootstrap receipt, because callers need a durable handle without treating console prose as authority.

`run` performs at most one sequential public-invocation loop bounded by policy and returns when it reaches judgment, blocker, transient prelaunch stop, busy state, or invocation limit, because host control must remain interruptible without imposing a semantic lifecycle total.

`status` derives one read-only `RunView` from committed history, because observation must use the same validator as execution without advancing state.

`diagnose` reports exact invalid records, missing references, unsettled Attempts, sealed exchanges, and next safe evidence requirement without repair, because operators need actionable facts without implicit history mutation.

`stop` requests Run-wide cancellation through `operator-stop`, because cancellation is a committed control fact rather than deletion or fabricated failure.

Every Boundary and public receipt identifies Run, Task, committed prefix, requested action, performed action, published records, observed route, launch and settlement status, blockers, and public outcome while marking unavailable facts `UNKNOWN`, because compact output must remain traceable and honest.

## Qualification strategy

`qualification-matrix` — Qualification maps every mechanical design proposition to deterministic falsification and every semantic-role proposition to representative real-model evaluation, because schema tests cannot prove judgment and model demonstrations cannot prove persistence integrity.

Deterministic unit tests cover canonical codec rejection, identity domain separation, schema closure, authority subset checks, trusted-minimum capability admission, constraint intersection, route non-substitution, path traversal and link rejection, transition hashing, ledger grammar, state precedence, reference binding, History Reader access to an additional authorized source beyond `starting_selectors`, and output assessment, because these properties are exact and mechanically falsifiable.

Fault-injection tests interrupt every durable publication boundary before and after file flush, directory flush, rename, package installation, ledger append, launch intent, adapter return, settlement observation, and phase finalization, because `known-fact-recovery` must be demonstrated at each crash-visible prefix.

Host-contract tests run against the actual selected store and target filesystems and report each probe result, because platform-family success cannot establish mount-specific durability or path semantics.

Adapter conformance tests use deterministic fake providers and processes to exercise non-launch, uncertain launch, launched success, malformed return, truncated capture, continuing process, unknown settlement, route mismatch, tool-event incompleteness, and sealed-outcome recovery, because `operation-attempt-separation` depends on transport distinctions that happy-path tests omit.

Integration tests exercise Planner decline, one-step success, multi-step stop, child depth-first completion, child operational stop, Validator repeat, Validator failure, operator stop at each frontier, target mutation between observations, and imported prior evidence, because the complete sequential loop must preserve component contracts across boundaries.

Real-model evaluation uses frozen missions that challenge decomposition, cheapest-adequate route choice within effective routing constraints, authority narrowing, evidence use, continuation, stagnation, and independent validation across permitted providers and trusted minimum capabilities, because `trusted-semantic-roles` assigns those choices to model judgment.

Real-model results record exact model and provider identity when observable, policy, prompt contract, committed input prefix, returned bytes, tool transcript completeness, and human-scored criteria, because a pass without execution identity and evidence cannot qualify the configured route.

The qualification suite includes negative searches for direct ledger writers, direct adapter launches, mutable cursor state, silent route fallback, target-root store placement, automatic replay, duplicated accepted artifacts, and references that treat the stale Implementation Plan as current authority, because forbidden mechanisms can re-enter through otherwise passing local behavior.

WELL qualification runs a mechanical sentence and canonical-reference check, because WELL conformance is mechanical. Meaning-aware design review is separate, because mechanical conformance does not establish design acceptance. The SDD owns shared qualification strategy, while a future Implementation Plan owns exact verification procedures, commands, evidence outputs, and pass, stop, and escalation conditions, because Verification Evidence owns observations against those obligations.

Promotion evidence binds exact hashes of the Governing Inputs, Architecture Description, this SDD, current bounded Implementation Plan, implementation candidate, test sources, host-probe output, deterministic results, and real-model results, because a passing observation applies only to the unchanged design and realization it exercised.

No implementation is ready while a required deterministic test fails, a host capability is unknown, a route claim is unobserved, a real-model gate is missing, an authority conflict remains, or qualification evidence refers to different bytes, because unresolved evidence cannot support the claimed realization.

## Downstream obligations and unresolved matters

A current bounded Implementation Plan must identify exact realization scope, source owners, construction order, verification commands, pass criteria, stop conditions, and escalation conditions while citing unchanged hashes of this design chain, because the SDD owns shared design but not execution authority.

Local replaceable choices unused outside one realization unit may remain in implementation, because the Design Authority Chain does not require ceremonial design ownership for incidental detail.

A proposed change to a shared schema, path convention, event grammar, publication rule, adapter contract, authority algorithm, recovery rule, host floor, or qualification obligation returns here before dependent work continues, because those choices are durable or shared realization authority.

A proposed change to lifecycle semantics, role authority, system boundary, outcome meaning, or product constraint returns to the Architecture Description or Governing Inputs as applicable, because this document cannot acquire upstream authority.

### Unresolved shared design decisions

No SDD-owned shared or durable design decision is currently unresolved, because the value spaces, routing-constraint admission, selector and event grammars, atomic publication, lock sequencing, invocation bound, output-assessment identity, capture policy, target admission, public commands, and qualification ownership are defined above. The next authority link is a new bounded current Implementation Plan, because implementation detail and exact verification procedure belong downstream under the unchanged Governing Inputs, Architecture, and this SDD.
