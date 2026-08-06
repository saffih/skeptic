# STT MVP Architecture Plan

**Status:** Canonical pair candidate — implementation remains prohibited until the unchanged architecture and implementation plan pass WELL, RunSkeptic, and promotion review
**Repository:** `saffih/skeptic`
**Historical reconstruction base:** `74c4f6a2c34da501101141525c8a34d691c384a1`
**Companion implementation plan:** `plans/stt-mvp-implementation-plan.md` — conformance candidate reviewed only as part of the unchanged pair
**Document profile:** `docs/well.md`
**Scope:** STT MVP runtime architecture

This document is the sole authority for STT runtime meaning, because one normative owner prevents architecture and implementation from drifting.

The implementation plan owns construction order and executable proof but may not redefine lifecycle meaning, because proof planning and semantic authority are different responsibilities.

A proposition belongs in this architecture only when omitting it would leave runtime meaning ambiguous, permit a materially unsafe implementation to claim conformance, or remove a necessary falsification path, because architecture should constrain what must be true without prescribing construction.

Concrete serialization schemas, file and directory conventions, algorithms, construction order, and executable proof belong to the implementation plan while this architecture retains required semantic fields and meanings, because implementation must not invent lifecycle semantics yet needs one exact build contract.

---

## 1. Purpose and boundary

Safe Target Task (STT) executes one immutable mission against a live target through trusted planning, sequential effectful execution, independent validation, and durable evidence, because ordinary agent execution can lose identity, exceed admitted authority, replay uncertain operations, or claim unsupported completion.

`Safe` means STT preserves its own identities, operational authority, accepted decisions, history, and replay boundary while reporting uncertainty honestly, because those properties are enforceable without pretending to control the open target completely.

STT is not a sandbox and does not guarantee mission completion, exclusive target access, rollback, complete effect detection, remote quiescence, or protection from a hostile same-user process, because the MVP has no operating-system or external-system containment.

Execution is sequential inside one Run while overlap between separate Runs remains caller-managed, because STT owns one lifecycle history but cannot coordinate every external writer or effect.

---

## 2. Dominating rules

The following rules dominate narrower text, because one general rule should replace repeated special cases unless a material exception is required:

| Rule | Decision | Warrant |
|---|---|---|
| Immutable root semantics | Bootstrap freezes mission, operational authority, required outputs, routing, policy, target workspace, store root, selected initial inputs, and selected prior-Run evidence before semantic execution | same-Run execution needs one accountable semantic and location base |
| Trusted thinking, mechanical control | Planner and Validator own semantic judgment while Lead and Boundary enforce lifecycle integrity and operational admission | mechanical code cannot replace contextual reasoning safely |
| Free persisted context | the authoritative STT filesystem is the history interface, Planner and Validator may read the complete current STT tree, and Planner may delegate that read ability to any planned entity | runtime-selected context can omit information needed for correct reasoning |
| No semantic recursion limits | Planner may create any child-Task structure, including byte-identical parent missions, and Validator may repeat the same Task for as many useful Rounds as it judges necessary | arbitrary count limits would override the thinking roles’ mandates |
| Fresh work, never replay | every Round, child Task, and continuation uses fresh identities while actual or uncertain launch permanently forbids another launch of the same OperationRequest | continuation is legitimate while replay after possible effects is unsafe |
| Live target, bounded admission | effectful work reaches the live target only through admitted Worker routes or command profiles while hidden process behavior remains outside containment claims | STT can constrain constructed requests but not arbitrary process behavior |
| Append-only truth | accepted lifecycle facts are immutable and ledger-backed while resume completes only uniquely determined non-effectful transitions | reconstruction becomes unsafe when accepted facts can be replaced |
| Judgment is not transport | mission success, failure, and uncertainty remain separate from provider/process return and local-settlement facts | operational events do not prove semantic outcomes |
| Known violation stops compounding | a reported effect outside admitted responsibility scope stops later Plan steps and remains evidence for Validator judgment | later work must not build on a known authority breach |
| Architecture first | semantic changes are repaired and reviewed here before the implementation plan changes | architecture errors otherwise ripple into code and proof |

A narrower rule may specialize these rules but may not contradict them, because local detail must not silently defeat the architecture’s dominant protections.

---

## 3. Root contract and identity model

### 3.1 RootTaskSpec

A new Run begins from one immutable `RootTaskSpec` plus caller-selected target workspace and store root, because root semantics and authoritative locations need one accountable base before any semantic execution:

```text
schema
mission
root_authority_spec
required_outputs
initial_input_selectors
prior_evidence_selectors
run_policy
routing_identity
```

`mission` owns the objective, scope, constraints, non-artifact success meaning, and prohibited actions, because Bootstrap must freeze what the Run is accountable for.

Structured `required_outputs` are the only artifact-output contract, because artifact satisfaction must not depend on later interpretation of mission prose.

Bootstrap validates and freezes supplied semantics but does not invent or complete them, because deterministic startup must not become an undeclared Planner.

Changing mission, authority, outputs, routing, policy, target workspace, or store root requires a new Run, because same-Run resume must preserve the exact root contract and authoritative locations.

`run_policy` contains operational safeguards such as capture limits, wait and termination limits, and host profile but does not cap Plan steps, Task depth, total Tasks, or Rounds, because resource mechanics may protect the host without replacing trusted semantic judgment.

A Plan remains finite because its persisted return is finite, while provider and host context limits remain reported facts rather than semantic authority over Planner or Validator.

### 3.2 Identities

The runtime uses distinct identities, because mission continuation, delegation, and one transport launch have different replay and lineage meanings:

- **Run** — one frozen root specification, target identity, store-root identity, runtime, routing, policy, and optional imported prior evidence;
- **Task** — one immutable mission, authority, required outputs, lineage, and append-only ledger;
- **Round** — one fresh plan–execute–validate cycle of the same Task;
- **OperationRequest** — one exact Planner, Worker, command, or Validator request;
- **Attempt** — the transport record for one OperationRequest;
- **Child Task** — a new Task selected by Planner whose mission may differ from or equal an ancestor mission byte for byte

Mission equality does not imply Task equality, because lineage, accumulated history, authority, inputs, and execution point can differ.

A repeated Round reuses the Task mission and authority but never reuses a Plan, step, child identity, OperationRequest, or launch, because continuation must not become replay.

---

## 4. Roles and semantic freedom

### 4.1 Lead

Lead is a deterministic depth-first driver that consumes compact lifecycle receipts and asks Boundary for the uniquely implied next transition, because orchestration must not acquire semantic authority.

Lead does not invent steps, alter Plans, select semantic evidence, or judge the mission, because those choices belong to trusted thinking roles.

### 4.2 Boundary

Boundary is the trusted lifecycle façade, because one component must own every transition between semantic decisions and authoritative state.

Boundary owns the following responsibilities, because each one changes or verifies trusted lifecycle state:

- identity and operational-authority checks;
- request construction;
- read-only STT-history exposure;
- target and exchange admission;
- provider and command launch;
- capture and local-settlement classification;
- output verification and import;
- child publication and result binding;
- transition-package publication;
- ledger append and compact receipts

Boundary checks structure and integrity rather than semantic wisdom, because mechanical code cannot decide whether a Plan is insightful, a mission is too similar, evidence is materially useful, or another Round is worthwhile.

### 4.3 Planner

Planner is a trusted thinking entity with broad semantic freedom inside the immutable mission and operational authority, because useful decomposition and investigation cannot be predetermined mechanically.

Planner may choose the following forms, because each can be the simplest path from current knowledge to the mission:

- direct execution;
- investigation;
- any number or depth of child Tasks;
- a child mission identical to its parent;
- a different approach from earlier Planners;
- `DECLINE` when it currently sees no useful path

Continuation is a recommended pattern rather than a restricted protocol form, because investigation may change the knowledge state enough to make the exact same mission newly actionable.

A typical continuation investigates unknowns, persists the resulting information, and creates a same-mission child Task, because the child can reason from a different accumulated STT history even when mission bytes are identical.

Planner returns an immutable nonempty `PLAN` or `DECLINE`, because execution requires at least one admitted step while a Planner that proposes no execution must state `DECLINE`.

Plan validation checks schema, identity, ordering, and operational admission only, because Boundary must not replace Planner judgment with semantic heuristics.

Private contracts may recommend inspecting history, explaining decisions, and avoiding circular work but may not turn those recommendations into runtime semantic prohibitions, because trusted thinking freedom is an explicit architecture choice.

### 4.4 Validator

Validator is an independent trusted thinking entity that owns Task-level semantic judgment, because completion cannot be reduced to transport success or output existence.

Validator returns one judgment and one disposition, because mission meaning and continuation are separate decisions:

```text
judgment: SATISFIED | NOT_SATISFIED | INDETERMINATE
disposition: FINISH | REPEAT
```

`SATISFIED + REPEAT` is invalid because a satisfied Task has no remaining mission gap, while every other combination is allowed when coherently explained.

Validator may choose `REPEAT` after `PLAN`, `DECLINE`, or settled Planner failure, because Validator rather than the preceding Planner owns continuation judgment.

`REPEAT` means another fresh Round of the same Task can use accumulated history and the Validator’s gap report to progress, because the same mission may become more solvable after additional work or reconsideration.

The next Round starts automatically and records the latest Validator report as its immediate continuation reason, because caller mediation would add a control gate that the Validator already owns.

STT imposes no Round count or mechanical novelty requirement, because duplicate hashes and repeated observations are facts while progress, stagnation, and materiality require semantic judgment.

### 4.5 Worker and command

Workers and commands are effectful execution entities, because target mutation and external operations require narrower operational admission than semantic reasoning.

A Worker receives one accepted step, admitted target access, responsibility scope, output requirements, route/profile, and any read-only STT access granted by Planner, because it needs enough authority to execute without inheriting lifecycle control.

A command step selects one frozen named command profile while the Plan supplies only admitted typed arguments, because free-form executables, shell programs, environment grants, or credentials would bypass frozen authority.

Neither Worker nor command decides the parent Task’s final mission judgment, because local execution evidence must remain subject to independent validation.

### 4.6 Instruction trust

Frozen STT runtime and private role contracts outrank immutable mission, authority, routing, and policy, which outrank the accepted current step, which outranks persisted reports, target content, prior evidence, and tool output, because data must not acquire control authority through embedded instructions.

Persisted and target content may inform reasoning but cannot change role contract, mission, operational authority, routing, policy, lifecycle state, or output schema, because full read access must not become prompt-injection authority.

---


## 5. Persisted STT history and free read access

STT persists its complete known history as ordinary files under the authoritative Run root, because later thinking entities must be able to reconstruct what happened without relying on hidden conversation state.

Persisted history includes Bootstrap records, ledgers, Tasks, Rounds, Plans, operation requests, launch and capture records, accepted and rejected returns, audits, observations, artifacts, violations, child Tasks, Validator reports, and terminal receipts, because each can materially affect later reasoning or integrity review.

The persisted filesystem and ledger are the authoritative history interface, because a second semantic context-delivery system would duplicate and filter information already stored.

### 5.1 Free context reads

Planner and Validator always receive unrestricted read-only access to the complete current STT tree, because the thinking entity rather than the runtime should decide which persisted context is relevant.

Planner may grant the same read-only access or a convenient starting subtree to any Worker, child Task, investigative entity, or other admitted role, because delegated work may need the history that motivated it.

Planner owns the semantic consequences of delegated visibility, because STT cannot promise unrestricted context while independently redacting material the Planner chose to expose.

Roles may use read-only equivalents of listing, tree navigation, finding, file reading, ranged reading, text search, structured JSON querying, and tail inspection, because direct filesystem navigation is simpler and more flexible than a curated history package.

Read-tool use remains part of the entity’s one outer operation and does not become separate lifecycle steps, while the implementation plan owns the exact transcript convention, because contextual navigation must remain reconstructible without expanding lifecycle vocabulary.

STT does not curate the only visible history, require prior declaration of contextual reads, hide records behind summaries, create a cumulative history package, log every individual read as a lifecycle transition, or impose a semantic reading budget, because those mechanisms add cost and can conceal information needed for correct reasoning.

Indexes, manifests, compact receipts, and summaries may aid navigation but never replace the underlying readable files, because convenience must not become a visibility boundary.

### 5.2 Read integrity and meaning

Read access is context rather than operational authority, because seeing a persisted file does not permit mutation of STT state, expansion of target authority, or automatic satisfaction of an output.

The host adapter exposes the complete committed STT prefix that existed when the outer operation began through a read-only tool surface and prevents path escape through that surface, because semantic freedom requires stable prior history rather than partially written current-operation capture.

Missing, corrupt, truncated, omitted, or unreadable records fail or remain labelled visibly, because later reasoning must distinguish complete evidence from bounded capture.

“Complete history” means everything STT retained rather than every real-world action, because STT cannot reconstruct unreported external effects.

STT does not intentionally persist credential values but cannot guarantee that provider, command, or artifact output contains no secret, because an orchestration system cannot classify arbitrary returned bytes perfectly.

---

## 6. Operational authority and live-target execution

`RootAuthoritySpec` defines operational grants before Bootstrap, because semantic freedom must not manufacture new target or external-effect capability:

```text
read_scopes
write_responsibility_scopes
allowed_step_kinds
allowed_worker_routes
allowed_command_profiles
allowed_inherited_env_names
allowed_external_effect_classes
```

Bootstrap binds those grants to the resolved target identity to create `TaskAuthority`, because path grants without one target identity are ambiguous.

A child authority may equal or narrow its parent authority but may not expand it, because delegation must not create operational capability absent from the frozen root.

The child-authority restriction does not restrict mission similarity or semantic reasoning, because operational capability and thinking freedom are different concerns.

Closed effect classes are defined as follows, because route and profile admission need one portable audit vocabulary:

```text
TARGET_READ
TARGET_WRITE
LOCAL_PROCESS
NETWORK_READ
NETWORK_WRITE
REMOTE_MUTATION
```

Worker routes and command profiles declare admitted effect classes and environment names as an admission and audit contract rather than containment, because STT can constrain requests but not prove hidden process behavior.

Operational target paths are canonical target-relative paths while absolute paths, traversal, symlink traversal, special files, `.git`, and admitted-root escape are rejected, because target admission must not reach control state or unintended locations.

### 6.1 Reported scope violations

Boundary persists an exact reported effect outside admitted responsibility scope and stops every later Plan step, because continuing could compound a known violation.

The Run becomes `INVALID` when the reported effect mutated authoritative STT state, because the evidence and control history can no longer be trusted.

The Run becomes `OPERATIONALLY_BLOCKED` when relevant local work is unsettled or unknown, because Validator must not judge while effects may still be changing.

Validator judges the Task from accumulated evidence when STT state remains valid and relevant local work is settled, because the violation is semantically material but does not itself prove the mission outcome.

STT does not claim to detect unreported effects, because cooperative reporting is not complete observation.

---

## 7. Plans, context, inputs, outputs, and evidence

Before each Planner call, Boundary persists a deterministic target workspace index within Task read authority, because Planner needs current structural context without receiving new target-write authority.

The workspace index is context rather than permission or immutable evidence, because later authoritative consumption must re-observe exact target facts.

An accepted Plan is immutable and ordered, because execution and resume require one stable step sequence.

The MVP step kinds are limited to the following forms, because Worker execution, admitted commands, and child Tasks cover the required MVP behavior without a general workflow language:

```text
worker
command
task
```

Every step binds identity, description, declared read and write-responsibility scopes, dependencies, and output requirements, because Boundary must verify admission and later bind results.

A Task step additionally binds child mission, child authority, and required child outputs, because child identity must be complete before publication.

Planner may read any persisted STT history directly for context without a binding, because contextual visibility is not authoritative consumption.

Exact binding is required for cross-Run import, effectful-step inputs whose exact bytes matter, output satisfaction, and request/result identity, because those uses can otherwise be silently substituted or rebound.

The implementation provides one canonical immutable schema source for selected initial and prior evidence, exact Plan dependencies, output requirements, observed artifacts, role returns, and Boundary-owned step results, because lifecycle integrity needs exact identities where substitution would change meaning.

Exact JSON field names and incidental layout are implementation-owned while these semantic fields remain mandatory, because architecture should define meaning without duplicating the code-owned serialization schema.

An `OutputRequirement` identifies purpose, artifact type, location, path policy, mode, satisfaction mode, and producer constraint, because output existence alone does not prove the required artifact was produced correctly.

An `ArtifactRef` identifies exact bytes or observation, type, location, size, mode, provenance, requirement, and purpose, because later use must remain tied to what Boundary actually observed.

Target artifacts are reverified before authoritative consumption while Run artifacts are Boundary-owned, create-only, and immutable, because target state may change while accepted lifecycle evidence must not.

A role return is accepted only when its schema and bindings match the exact OperationRequest, because plausible bytes from the wrong request are not authoritative results.

Returned but invalid bytes are persisted as `REJECTED` and never promoted into semantic state, because diagnosis must preserve evidence without laundering it into acceptance.

A Boundary-owned `StepResult` records the exact call or child result, accepted semantic return when present, verified outputs, observations, and local outcome, because lifecycle progress must not require fabricated role results.

---

## 8. Call outcome, settlement, and retry

Every launched outer operation records return and local-settlement dimensions independently, because a returned value and a stopped local process prove different facts:

```text
call_state: RETURNED | NO_RETURN
result_kind: OK | ERR | REJECTED | NONE
local_settlement: SETTLED | UNSETTLED | UNKNOWN
```

Valid return combinations are limited to the following forms, because every other pairing is contradictory:

- `RETURNED + OK`;
- `RETURNED + ERR`;
- `RETURNED + REJECTED`;
- `NO_RETURN + NONE`

`SETTLED` proves only that the observed local process group and communication channel ended, because remote, billing, logging, daemon, escaped-child, and other external effects may remain.

Before launch intent is persisted, launch is mechanically disproved and a later invocation may re-evaluate prerequisites and launch that exact OperationRequest, because no operation has yet occurred.

After launch intent is persisted, another Attempt for the same OperationRequest is permitted only when the adapter positively proves that it created no process and sent no provider request, because proven absence of launch means no operation occurred.

Positive proof of non-launch returns `PRELAUNCH_BLOCKED` for the current invocation and creates neither role failure nor Validator evidence, because reevaluation may occur later but must not become an automatic transport retry loop.

Actual launch or uncertainty about whether launch occurred permanently forbids another launch of the same OperationRequest in the Run, because a second launch could replay hidden effects.

Interruption after launch intent without either complete proof of non-launch or a uniquely recoverable call outcome makes the Run `NON_RESUMABLE`, because STT cannot infer whether the operation occurred.

After every outer call and before accepting its result, Boundary revalidates frozen runtime, Run, target-root, Task, Round, request, and prelaunch ledger-prefix identities, because lower-trust activity must not alter authoritative context unnoticed.

Settled Planner failure proceeds to Validator with no accepted Plan, because operational failure does not remove the Validator’s semantic mandate.

Settled Worker or command failure stops later Plan steps and proceeds to Validator with exact failure evidence, because partial or failed work may still affect the mission judgment.

Settled Validator failure leaves the Task `OPERATIONALLY_STOPPED` without a mission judgment, because no higher semantic role inside that Task may fabricate one.

Any relevant `UNSETTLED` or `UNKNOWN` operation blocks later steps and Validator execution, because semantic judgment must not race possibly active local work.

Only an accepted WorkerResult or CommandResult may establish the corresponding Worker or command step’s `SATISFIED` or `NOT_SATISFIED` outcome, because settled transport failure is not semantic proof.

Validator alone establishes the Task-level judgment from all committed admissible evidence, including accepted step outcomes, child results, existing verified artifacts, and a Planner `DECLINE`, because Task completion is broader than any one execution result.

Settled `ERR`, `REJECTED`, or `NO_RETURN` always maps to `INDETERMINATE` evidence, because no accepted role result exists.

---

## 9. Child Tasks, Rounds, and failure propagation

Planner may create a child Task for any mission it judges useful, including the exact parent mission, because new history and decisions can make identical mission text represent a different reasoning state.

STT imposes no mission-hash inequality, semantic-distinctness test, Task-count limit, or depth limit, because those mechanical rules would override Planner’s decomposition mandate.

Child execution remains depth-first and sequential, because Lead must derive one unambiguous active frontier.

Child outcomes map into the parent as follows, because parent validation must distinguish semantic results from operational absence of judgment:

```text
child SATISFIED       → parent step SATISFIED
child NOT_SATISFIED   → parent step NOT_SATISFIED
child INDETERMINATE   → parent step INDETERMINATE

settled child OPERATIONALLY_STOPPED not caused by Run-wide operator cancellation
→ parent step OPERATIONAL_INDETERMINATE
→ later parent steps stop
→ parent Validator may judge the parent mission

child UNSETTLED or UNKNOWN
→ entire Run OPERATIONALLY_BLOCKED
→ no ancestor Validator launches

child NON_RESUMABLE
→ entire Run NON_RESUMABLE
→ no ancestor Validator launches

child INVALID
→ Run INVALID
```

A Validator `REPEAT` creates the next contiguous Round automatically and invokes a fresh Planner, because continuation belongs to the same Task rather than a caller-controlled external loop.

The new Round binds its predecessor and Validator report while every earlier persisted record remains freely readable, because later reasoning needs both the immediate gap and the full accumulated history.

Planner-created same-mission children and Validator-created same-Task Rounds are both valid, because Planner owns decomposition while Validator owns whether the current Task itself should undergo another Round.

---

## 10. Persistence, ledger, and resume

Each Task owns one append-only hash-chained JSONL ledger, because crash recovery and audit require one immutable event history.

Identity-bearing control records use one canonical encoding and exact-byte hashes, because independent readers must derive the same identities.

Lifecycle transitions publish immutable payloads through verified create-only transition packages and then append the exact committing ledger event under one per-Run writer lock, because package publication and event commitment need one recoverable relationship.

The minimum event vocabulary is defined as follows, because every semantic and effectful boundary needs a durable commit point:

```text
TASK_CREATED
ROUND_CREATED
PLANNING_STARTED
PLANNING_FINISHED
STEP_STARTED
STEP_FINISHED
VALIDATION_STARTED
VALIDATION_RECORDED
ROUND_FINISHED
TASK_FINISHED
```

State is derived from validated ledgers and committed packages rather than a mutable cursor, because duplicate state authority would create inconsistent resume decisions.

Resume may complete only uniquely implied non-effectful work, because replaying semantic or effectful operations after interruption is unsafe.

Admitted resume actions include the following transitions, because each can be proven from already committed facts:

- publish a uniquely prepared root Task;
- create Round 0 for a committed Task;
- launch a committed request before launch intent or create a fresh Attempt only after committed positive proof that the preceding Attempt did not launch;
- commit a complete uniquely eligible non-effectful transition package;
- map a committed child result into its parent;
- finalize an accepted Validator result into a Round;
- finalize a finished Round into a Task;
- create the next Round after accepted `REPEAT`

Resume may not infer the outcome of an interrupted launched operation, because target or external effects may be unknowable.

A new Run after `NON_RESUMABLE` or unknown settlement requires operator-owned quiescence or an isolated replacement target, because STT cannot prove escaped or remote work has ended.

Interior ledger corruption, identity mismatch, conflicting packages, or mutation of authoritative STT state makes the Run `INVALID`, because trustworthy derivation is no longer possible.

---

## 11. Locations, runtime, and host floor

STT separates source repository, live target workspace, caller-selected store root, authoritative Run root, and per-call exchange or adapter workspace when needed, because controller state and effectful work require distinct trust locations.

Source and target may be identical for self-modification but otherwise neither may contain the other, because partial overlap makes frozen-runtime and target-mutation boundaries ambiguous.

The caller-selected store root is resolved and frozen before Run publication, and the authoritative Run root is created beneath it while remaining disjoint from source and target, because task evidence must live where the caller authorized without target work rewriting lifecycle state.

Authoritative state never lives under `<target>/.stt/`, because a target-local default would defeat caller-selected storage and expose lifecycle evidence to target mutation.

Bootstrap freezes a detectable target-root identity and Boundary reverifies it before effectful operations, because same-path replacement must not silently redirect admitted authority.

A host that cannot detect target-root replacement with required confidence is unsupported, because path text alone is not a stable target identity.

Bootstrap copies and verifies an explicit maintained runtime manifest into the Run root and re-executes from that frozen runtime, because target self-modification must not replace the controller during the Run.

The supported MVP host profile provides the following primitives, because the architecture depends on them rather than on unspecified filesystem behavior:

- same-parent atomic publication;
- create-only regular-file publication;
- flush and reread verification;
- one conforming-writer lock per Run;
- no-follow path observation and hashing;
- launch without shell interpolation;
- process-group termination and local-settlement observation;
- read-only STT-history tools for semantic roles

Bootstrap fails before Run publication when a required primitive is unavailable, because unsupported hosts cannot preserve the promised integrity boundary.

Run-root retention and deletion are operator-owned, because only the operator knows when resume and evidence are no longer required.

Deleting the Run root ends same-Run resume, because the authoritative history has been removed.

---

## 12. Prior-Run evidence

Prior-Run evidence is available only through committed references explicitly selected in `RootTaskSpec`, because cross-Run history must not become ambient authority.

Bootstrap verifies and copies selected bytes and origin metadata into the new Run before root Task publication, because the new Run must not depend on later availability or mutation of the prior Run root.

Imported material is advisory data and cannot change current mission, authority, routing, policy, or lifecycle state, because historical evidence must not become current control authority.

Prior ledgers and cursors are never merged, because one Run must retain one internally derived lifecycle history.

This restriction applies across Runs but does not limit free reading of the complete current Run’s STT tree, because current persisted history already belongs to the active lifecycle.

---

## 13. Derived states and public operations

Semantic terminal judgments are defined as follows, because mission meaning must remain distinct from operational state:

```text
SATISFIED
NOT_SATISFIED
INDETERMINATE
```

Public nonsemantic outcomes are defined as follows, because operators need stable names for conditions that prevent or end advancement without fabricating mission meaning:

```text
OPERATIONALLY_BLOCKED
OPERATIONALLY_STOPPED
NON_RESUMABLE
INVALID
```

A semantically finished Run reports its accepted Task judgment directly rather than a second `TERMINAL` meaning, because duplicate terminal vocabularies would obscure whether the mission was satisfied, not satisfied, or indeterminate.

Lead derives the unique next lifecycle action from committed history without a mutable cursor, while exact internal derivation labels and precedence belong to the implementation plan, because orchestration mechanics must be deterministic without becoming architecture vocabulary.

An accepted `REPEAT` starts the next contiguous Round automatically without `AWAITING_REPEAT`, because Validator already authorized continuation.

`PRELAUNCH_BLOCKED` and `RUN_BUSY` are transient invocation or query outcomes rather than persisted lifecycle states, because absence of launch and temporary lock ownership are current observations rather than committed semantic facts.

Public operations are defined as follows, because startup, advancement, observation, and diagnosis need separate interfaces:

```text
stt start --workspace <target> --store-root <store-root> --task-spec <spec> --routing-file <routing> [--prior-run <run-root>] [--allow-live-provider]
stt run --run-root <run-root>
stt status --run-root <run-root>
stt diagnose --run-root <run-root>
stt stop --run-root <run-root>
```

`start` and `run` advance through deterministic transitions, child Tasks, and Validator-requested Rounds until terminal, blocked, stopped, non-resumable, invalid, or prelaunch-blocked, because ordinary continuation should not require repeated caller approval.

`stop` records an operator cancellation without creating a mission judgment, because operational control must remain available without overriding Planner or Validator semantics.

When a Run has been authoritatively published but its uniquely determined root Task has not yet been published, `stop` may publish that exact root Task before recording cancellation, because completing a deterministic Bootstrap consequence does not create semantic work or grant `stop` authority to invent Task meaning.

Cancellation is Run-wide even when a child Task is active, because an operator stop must prevent new child, parent, or ancestor semantic calls rather than masquerade as an ordinary child failure.

Cancellation forbids new semantic launches but does not discard valid results or uniquely implied non-effectful transitions from operations launched earlier, because operator control must stop future work without rewriting facts already produced.

A committed operator cancellation remains visible in the public Run view independently from any semantic judgment produced from facts that cancellation preserved, because reporting the judgment must not erase the operator action that prohibited later work.

Cancellation between outer operations derives `OPERATIONALLY_STOPPED`, while cancellation during possibly active work follows the ordinary settlement rules and may derive `OPERATIONALLY_BLOCKED` or `NON_RESUMABLE`, because STT must not claim quiescence it cannot prove.

`status` and `diagnose` are read-only and never repair state, because observation must not alter the lifecycle being observed.

---

## 14. Qualification and proof limits

Implementation qualification proves the following mechanical claims, because each one is a falsifiable architecture protection:

- immutable Bootstrap and identity binding;
- operational authority and profile admission;
- read-only complete-STT access for Planner and Validator;
- Planner-delegated STT read access;
- same-mission child acceptance;
- automatic Round continuation without an architecture-defined count cap;
- sequential depth-first execution;
- stop-on-reported-scope-violation behavior;
- exact output and result binding;
- closed call and settlement algebra;
- no second Attempt after actual or uncertain launch, with the positive non-launch exception;
- settled-failure routing to Validator;
- append-only ledger and explicit crash windows;
- frozen runtime and host-floor rejection;
- prior evidence import without state merge;
- caller-selected store-root isolation;
- Run-wide operator cancellation and child non-resumable propagation

Deterministic tests can prove contracts, supplied context, orchestration, and handling of semantic returns but cannot prove Planner or Validator reasoning correct, because semantic competence is not a deterministic runtime property.

Qualification therefore includes representative real-model adversarial evaluation of planning, success and failure judgment, continuation, stagnation, circularity, and use of persisted history, because empirical challenge can expose weaknesses that schema tests cannot.

Real-model evaluation is evidence rather than a correctness guarantee, because finite cases cannot prove general semantic reliability.

---

## 15. Change and readiness rule

A material architecture change records the following lineage fields, because future repair must preserve or explicitly replace protected meaning:

```text
changed rule
prior rule
PRESERVE | CHANGE | REMOVE
warrant
failure mode
replacement protection
implementation obligations affected
remaining unknowns
```

Historical reconstruction is evidence rather than runtime authority and may live outside this normative document, because historical detail must remain available without making the architecture needlessly large.

After any architecture edit, reviewers repair this document first, run a Pareto/WELL review for necessity and dominance, run RunSkeptic to convergence on the unchanged architecture, update the implementation plan only to conform, and then review the unchanged pair, because architecture errors otherwise ripple into executable plans.

Architecture-first convergence is evidenced by a RunSkeptic receipt bound to the exact unchanged architecture bytes and recorded before the implementation plan is updated to conform, because the accepted-pair commit proves final byte state but cannot by itself prove the required review order.

The containing commit of the accepted unchanged pair is recorded externally as the implementation base, because inserting the commit identity into the accepted files would change the reviewed bytes.

Until every gate passes, the pair remains a canonical candidate and implementation is prohibited, because implementation must not start from unresolved or inconsistently reviewed semantics.
