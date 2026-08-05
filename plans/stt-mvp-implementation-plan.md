# STT MVP Implementation Plan

**Status:** Implementation-ready canonical implementation design derived from the accepted architecture
**Architecture source of truth:** `plans/stt-mvp-architecture-plan.md`
**Repository:** `saffih/skeptic`
**Historical reconstruction base:** `74c4f6a2c34da501101141525c8a34d691c384a1`
**Implementation-base rule:** branch from the exact repository commit that contains the accepted unchanged canonical architecture and implementation pair, as recorded in the implementation handoff or execution receipt
**Canonical reconstruction source:** W5 implementation SHA-256 `7a619bd454a7349609cf66ac313aa3aa5236f397ab2df6d9803f8d5b848572da`
**Document profile:** `docs/well.md`
**Implementation authority:** STT MVP only

This is an architecture-derived implementation design document, because it defines how the accepted STT architecture will be constructed, divided into responsibilities, and proved without redefining runtime meaning.

This document must be WELL-formed, because implementation planning can weaken or contradict the architecture when its decisions, reasons, boundaries, and proof links are unclear.

WELL means **Warranted, Explicit, Lean, and Linked**, because every retained implementation proposition must have a recoverable reason, state every material qualification, avoid unnecessary duplication, and remain connected to its architectural source and executable checks.

WELL formation protects the integrity of the architecture-to-implementation relationship, because it exposes orphan mechanisms, weakened protections, duplicated authority, unjustified complexity, and missing proof.

The complete normative WELL profile is defined in `docs/well.md`, because one canonical definition prevents this document from creating a competing writing standard.

---

## 1. Objective and authority

Implement the smallest complete runtime that satisfies architecture decisions `D1`–`D23`, because implementation must preserve architecture semantics without creating a competing authority.

The architecture owns runtime meaning, contracts, limitations, and warrants; the implementation plan owns responsibility boundaries, construction order, and executable proof, because duplicated normative authority would drift and weaken the design.

When code, this plan, or a proposed simplification conflicts with architecture, stop and repair the design documents before implementation, because implementation must preserve architecture semantics without creating a competing authority.

Silent interpretation is forbidden because it would create an unreviewed architecture branch inside code.

Implementation must stop when the canonical qualification catalog passes, repository regression passes, and every production mechanism maps to a current architecture decision, because the design claim must remain executable and falsifiable.

It must not restore archived Target Task behavior or add speculative compatibility, because implementation must preserve architecture semantics without creating a competing authority.

---

## 2. Entry gate

Do not begin production code until all are true, because construction must begin only from an accepted unchanged document pair and bounded scope:

1. the architecture status is explicitly implementation-ready under architecture §31, which requires a complete feasible design path but not preexisting runtime qualification results;
2. its lineage matrix is complete;
3. WELL review and RunSkeptic gates have passed on the unchanged document pair, because future edits must preserve each proposition and its reason without creating competing authority;
4. the exact architecture and implementation SHA-256 values are recorded;
5. the implementation branch starts from the exact accepted document-pair commit rather than the historical reconstruction base;
6. unrelated work is preserved;
7. the scope is limited to active STT code, STT-private contracts, CLI integration, and focused tests, because proof must remain focused on architecture-relevant code without dispersing into unrelated test fixtures.

Failure of any condition is `CONFLICT`, not permission to implement an assumed design, because construction must begin only from an accepted unchanged document pair and bounded scope.

---

## 3. Build discipline

Build vertical, reversible slices because cross-cutting framework scaffolding can conceal missing behavior.

Each slice must satisfy the following requirements, because vertical reversible slices expose missing behavior and limit speculative abstraction:

- implement one coherent responsibility boundary;
- introduce only abstractions required by current decisions;
- include its canonical qualification scenarios;
- demonstrate at least one known-bad case when practical;
- preserve all earlier passing scenarios;
- end in a reviewable commit whose subject names the behavior proved;
- leave no partial alternate lifecycle.

Module and commit boundaries may change when a smaller shape preserves responsibility and proof, because the design claim must remain executable and falsifiable.

The following are prohibited unless architecture changes first, because vertical reversible slices expose missing behavior and limit speculative abstraction:

- generic workflow or state-machine framework;
- plugin system beyond named provider/command profiles;
- automatic operation retry or replay;
- semantic progress scoring;
- mutable cursor or scheduler;
- target sandbox or rollback claim;
- archive runtime imports;
- duplicate normative schemas or lifecycle rules, because independent implementations need one mechanically decidable contract.

---

## 4. Responsibility map

The implementation must provide these responsibilities; file names are suggested rather than normative, because each production mechanism needs one clear owner and architecture link.

| Responsibility | Suggested primary area | Architecture |
|---|---|---|
| canonical JSON, hashes, create-only files, transition packages | `storage.py`, `transition.py` | `D7`, `D20` |
| Task ledger and state derivation | `ledger.py`, `state.py` | `D3`, `D7`, `D20` |
| supported-host probes and writer lock | `host.py`, `run_lock.py` | `D6` |
| frozen runtime manifest and Bootstrap | `runtime.py`, `bootstrap.py` | `D1`, `D5`, `D6` |
| RootTaskSpec, routing, TaskAuthority, path-free TaskAuthorityView, full profiles, and path-free CapabilityProfileView | `contracts.py`, `authority.py`, `routing.py` | `D1`, `D9`, `D10`, `D18` |
| Task, Round, Plan, PlanInput, PlanInputResolution, EvidenceBinding, InputRef, OutputRequirement, ArtifactRef, StepResult, and role-result schemas | `task.py`, `round.py`, `plan.py`, `artifact.py` | `D2`, `D3`, `D12` |
| workspace index and target observations | `workspace.py` | `D9`, `D13` |
| exchange preparation and output import | `exchange.py` | `D5`, `D8` |
| provider/command launch and call classification | `launcher.py`, `command.py`, `providers/` | `D13`, `D14`, `D15` |
| mandatory Boundary façade | `boundary.py` | `D4` |
| mechanical depth-first Lead | `lead.py` | `D3`, `D4`, `D17`, `D20` |
| private role contracts | `contracts/planner.md`, `worker.md`, `validator.md` | `D10`, `D11`, `D16`, `D18` |
| CLI, status, diagnosis, prior evidence, and call/cost visibility | `cli.py`, `scripts/stt.py` | `D1`, `D19`, `D20`, `D23` |
| qualification catalog and static lineage checks | `tests/concepts/stt/`, document checks | `D21`, `D22`, `D23` |

Consolidate files when ownership stays clear, because code structure should follow responsibility and proof rather than speculative framework boundaries.

Split them only when tests or coupling show a concrete need, because the design claim must remain executable and falsifiable.

---

## 5. Cross-cutting implementation rules

### 5.1 Standard library first

Prefer Python standard-library primitives such as `dataclasses`, `pathlib`, `json`, `hashlib`, `subprocess`, `tempfile`, `os`, `shutil`, `stat`, and supported locking, because minimizing dependencies reduces supply, compatibility, installation, and runtime-closure risk for the MVP.

Add no dependency unless it materially reduces a verified correctness risk and fits repository policy, because the MVP should minimize supply and compatibility risk until a dependency proves a correctness benefit.

### 5.2 One canonical serializer

All control JSON uses one bounded canonical serializer and parser, because identity bytes must be deterministic and parsing must remain bounded across implementations:

- UTF-8;
- sorted keys;
- stable compact separators;
- one final LF;
- no NaN or Infinity;
- explicit schema IDs;
- duplicate-key rejection;
- configured byte and nesting limits.

Identity hashes are over exact canonical bytes, not reconstructed objects, because resume and substitution checks require exact facts to remain uniquely bound.

### 5.3 One schema source

Implement architecture schemas once, because independent implementations need one mechanically decidable contract.

Provider adapters, CLI, Boundary, state derivation, and tests import the same schema definitions, because duplicate schema sources can disagree.

Do not duplicate field vocabularies in prompts or adapters; generate role output schemas from the canonical contracts where practical, because independent implementations need one mechanically decidable contract.

### 5.4 Error vocabulary

Use a narrow typed error/blocker set that distinguishes at least, because shared primitives must not fork identity, schema, path, or error semantics:

```text
InvalidSpecification
UnsupportedHost
InvalidRuntime
InvalidTarget
InvalidAuthority
InvalidRouting
InvalidTask
InvalidRound
InvalidPlan
InvalidLedger
InvalidTransition
ArtifactMismatch
ScopeViolation
PrelaunchBlocked
RejectedReturn
NoReturn
UnsettledOperation
OperationallyBlocked
OperationallyStopped
RunBusy
NonResumableRun
InvalidRun
```

Do not mirror every state transition with a new exception class, because shared primitives must not fork identity, schema, path, or error semantics.

### 5.5 No hidden containment

Path admission, profiles, exchange isolation, and effect reports are orchestration protections, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

Tests and user output must not call them a sandbox or complete effect boundary, because these mechanisms do not constrain arbitrary operating-system or external behavior.

---

# Slice 1 — Canonical storage, transition packages, ledger, and host floor

## 6. Goal

Implement the persistence and host primitives required by `D6`, `D7`, and `D20` before semantic behavior, because later slices depend on trustworthy commit and resume boundaries.

## 7. Required behavior

Implement the following behavior, because later semantic behavior depends on trustworthy persistence and resume boundaries:

- canonical JSON and byte identities;
- create-only regular-file publication;
- same-parent temporary directories and atomic rename;
- flush, reread, and verification helpers;
- supported-host capability probe with recorded durability level;
- exclusive Run writer lock and nonblocking read-only status strategy;
- hash-chained Task ledger with exactly `TASK_CREATED | ROUND_CREATED | PLANNING_STARTED | PLANNING_FINISHED | STEP_STARTED | STEP_FINISHED | VALIDATION_STARTED | VALIDATION_RECORDED | ROUND_FINISHED | TASK_FINISHED` and the ordering defined by architecture §22;
- phase-specific request commits before launch markers;
- transition package containing payload manifest, expected ledger head, and exact pending event bytes;
- narrow commit completion from architecture §22;
- narrow torn-tail handling;
- pure derivation of `NEEDS_ROUND | NEEDS_PLANNING | NEEDS_STEP | NEEDS_VALIDATION | AWAITING_REPEAT | OPERATIONALLY_BLOCKED | OPERATIONALLY_STOPPED | NON_RESUMABLE | INVALID | TERMINAL` from committed facts, with transient `PRELAUNCH_BLOCKED` and `RUN_BUSY` kept outside persisted state, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

A package without its event is not generally adopted, because later semantic behavior depends on trustworthy persistence and resume boundaries.

The implementation may append its precomputed event only through the exact eligibility predicate in architecture §22, because later semantic behavior depends on trustworthy persistence and resume boundaries.

## 8. Proof links

Implement `Q01`–`Q03` from §39; `Q04` is completed by Slices 6 and 7, because each persistence claim needs an executable proof link.

---

# Slice 2 — RootTaskSpec, supported Bootstrap, frozen runtime, and Run identity

## 9. Goal

Implement `D1`, `D5`, `D6`, and the Run-level portions of `D9`, `D10`, and `D19`, because root identities and host assumptions must be frozen before lifecycle publication.

## 10. Required behavior

Implement exact parsers and validators for, because Bootstrap must reject ambiguous or incomplete root contracts before lifecycle publication:

- `RootTaskSpec`, including RootAuthoritySpec, target-relative and task-spec-parent-relative initial selectors, prior selectors, exact count fields `maximum_task_depth | maximum_tasks_per_run | maximum_rounds_per_task | maximum_steps_per_round`, the complete byte/depth/entry fields of `capture_limits` including total per-call exchange-input bytes, the role-seconds and termination-grace fields of `wait_limits`, and `host_profile = LOCAL_MVP_V1`;
- routing and named capability/command profiles;
- prior-Run root plus exact selectors and create-only import of selected committed evidence into the new Run;
- live-provider authorization;
- finite depth/Round/capture/wait policy.

Bootstrap must satisfy the following requirements, because root semantics and host assumptions must be frozen before semantic execution:

1. resolve and verify the source root mechanically from the canonical active `scripts/stt.py` path and maintained runtime-manifest root, freeze exact task-spec and routing bytes, parse only the frozen copies, require `RootTaskSpec.routing_identity` to equal the frozen routing identity, require `host_profile = LOCAL_MVP_V1`, and then validate target, prior evidence, and every fixed host capability before lifecycle publication;
2. permit source-equals-target for self-modification while creating authoritative Run and exchange locations disjoint from each other and from source/target;
3. copy the maintained explicit runtime manifest;
4. reject symlinks and special files;
5. verify bytes and normalized executable mode;
6. detect mixed-generation copying;
7. re-execute from the copy;
8. acquire the writer lock;
9. publish `run.json`, then atomically publish the original root Task from frozen RootTaskSpec; on resume, a verified run with no canonical or conflicting root path may complete that exact root publication, while a conflicting or incomplete canonical root is invalid;
10. resolve TARGET_PATH selectors under the admitted target and BOOTSTRAP_FILE selectors under the canonical task-spec parent with no absolute path, traversal, symlink, special-file, `.git`, or escape, then freeze each admitted input into a Boundary-owned current-Run ArtifactRef and create the root Task-scoped EvidenceBindings before root Task publication;
11. require a prior Run root exactly when prior selectors are nonempty, reject an unused prior root, and copy each verified selected prior artifact into a Boundary-owned current-Run ArtifactRef with origin provenance before root Task publication;
12. never reread mutable original spec, routing, initial selector source, or prior Run evidence after root Task publication;
13. perform no model call, semantic defaulting, or mission completion during Bootstrap, because root semantics and host assumptions must be frozen before semantic execution.

Publish `run.json` with every identity and observation required by architecture §9, including exact RootTaskSpec, source, target-root, runtime-manifest, routing, live authorization, finite policy, host profile/observations, structural call bounds, and optional prior-root identity, because resume must reconstruct the exact frozen Run without mutable external inputs.

Choose documented conservative hard ceilings for every count, byte, depth, entry, and duration field; reject nonpositive or above-ceiling values without changing architecture units, because independent implementations need one mechanically decidable contract.

Compute conservative overflow-safe structural upper bounds for Planner, Validator, and total step-operation launches from the frozen Task/Round/step policy and bind them into `run.json`, because finite policy must expose worst-case call and cost shape before execution.

Maintain one explicit runtime allowlist and tests for import/data closure, because the design claim must remain executable and falsifiable.

Do not derive the runtime only from observed imports, because root identities and host assumptions must be frozen before lifecycle publication.

## 11. Proof links

Implement `Q05`–`Q07`, because Bootstrap behavior needs executable proof before later slices depend on it.

---

# Slice 3 — Authority, trust order, Task/Round, and canonical schemas

## 12. Goal

Implement `D2`, `D3`, `D9`, `D10`, and `D12` as deterministic validation before any provider launch, because provider launches must not occur before deterministic authority and binding validation.

## 13. Required behavior

Implement canonical types and identities for, because provider launches must not occur before deterministic authority and binding validation:

- RunPolicyView, RootAuthoritySpec, declarative ChildAuthoritySpec, resolved TaskAuthority, path-free TaskAuthorityView, full Worker/command profiles with canonical purpose and single route-to-profile binding, path-free WorkerRouteView and CapabilityProfileView, selectors, and effect classes;
- Worker routes, and command profiles including closed executable resolution, reusable slot schemas, step-time single-token bindings, fixed environment, accepted exits, and slot-specific bounds;
- Task, Round, and parent binding;
- Plan identity header and exactly three fully specified step kinds, including route-derived Worker profile plus instructions, command profile/cwd/slot bindings, and child mission/relation/ChildAuthoritySpec/output fields;
- declarative PlanInput, the complete closed Boundary-owned PlanInputResolution schema, EvidenceBinding, path-free EvidenceBindingView, and exact-consumer InputRef;
- OutputRequirement;
- ArtifactRef with closed provenance and canonical purpose, path-free ArtifactRefView, and bounded ArtifactView;
- the closed StepOutcome vocabulary, including the TaskStep-only `OPERATIONAL_INDETERMINATE` case;
- PlannerResult, WorkerResult, CommandResult, ValidatorResult, and the discriminated Boundary-owned StepResult for outer-operation and child-task completion;
- role-request, call-outcome, StepResult, and role-result binding, because provider launches must not occur before deterministic authority and binding validation.

Authority validation must use component-aware canonical target-relative paths and full ChildAuthoritySpec subset checks across paths, step kinds, routes, command profiles, environment names, and effect classes; Boundary constructs child TaskAuthority with the unchanged parent target identity, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Every selected Worker route or command profile must also be a subset of the current TaskAuthority effect classes and inherited environment names, and each Worker route resolves to exactly one frozen capability profile, because live execution requires admitted profiles and truthful evidence without a containment claim.

Task publication atomically includes task identity, exact mission, structured required outputs, Task-scoped EvidenceBindings, frozen role/routing references, predetermined create-only child locations, and the initial `TASK_CREATED` event, because resume requires one complete immutable starting identity for each Task.

Root Task counts as task 1 at depth 0; Round 0 and every Plan element count toward their respective finite limits, because finite policy must prevent unbounded work and keep resource use structurally visible.

A valid Task with no Round derives `NEEDS_ROUND`, because a pre-Round Task is a valid recoverable state.

Round creation binds Task/mission/authority/output/runtime/routing/policy identities, contiguous number, fresh workspace-index identity, selected evidence, and exact predecessor Validator/report/repeat evidence where applicable, because mission judgment must remain separate from continuation and operational failure.

It enforces mission equality and every finite policy limit, because finite policy must prevent unbounded work and keep resource use structurally visible.

Implement one canonical output matcher that enforces satisfaction mode, producer constraint, write/read authority, requirement identity, exact artifact-type label equality, and exact purpose equality, because provider launches must not occur before deterministic authority and binding validation.

Plan validation separately enforces the architecture’s structural `principal_consumer` compatibility rules without requiring an optional downstream use to occur, because planning must remain immutable, bounded, and unable to redefine runtime authority.

A Plan contains only declarative PlanInputs; Plan validation rejects fabricated ArtifactRefs/InputRefs and future step outputs, because planning must remain immutable, bounded, and unable to redefine runtime authority.

Boundary publishes immutable PlanInputResolutions when accepting the Plan, leaves prior-step outputs as requirement references until committed, reverifies resolved target/evidence identities before launch, returns transient `PRELAUNCH_BLOCKED` on named target-input mismatch, and only then creates the role/Task/Round/step-bound InputRef, because accepted Plans must bind every declared dependency without partial publication or silent rebinding.

Task and Round publication store EvidenceBindings rather than consumption references, because resume and substitution checks require exact facts to remain uniquely bound.

Implement one deterministic ArtifactView builder for `FULL_BYTES | BOUNDED_TEXT | METADATA_ONLY`; every truncated or incomplete representation is labelled and cannot satisfy a completeness claim, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

Accepted Plans and all identity-bearing role results are create-only and immutable, because planning must remain immutable, bounded, and unable to redefine runtime authority.

Planner and Validator request builders receive only RunPolicyView, TaskAuthorityView, admitted WorkerRouteView, CapabilityProfileView, EvidenceBindingView, authoritative reference hashes, path-free ArtifactRefView, and bounded ArtifactView; structured-field tests must fail if a canonical target path, device/inode observation, resolved executable path, inherited credential/environment name, full TaskAuthority, full profile, full InputRef, or full ArtifactRef serialization appears in either request, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

Admitted artifact/log bodies may contain path-like text and remain untrusted data rather than triggering an impossible universal scrub requirement, because target and prior content must not acquire control authority.

Private role prompts must encode the architecture trust order and label target/prior content as untrusted data, because target and prior content must not acquire control authority.

## 14. Proof links

Implement `Q08`–`Q10`, `Q12`, and `Q13`, because schema and authority behavior needs executable substitution and limit proof.

---

# Slice 4 — Exchange isolation, launcher, call algebra, providers, and command profiles

## 15. Goal

Implement `D8`, `D13`, `D14`, and `D15` through one mandatory launch boundary, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

## 16. Exchange

For each lower-trust call, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access:

- create a disposable owner-exclusive exchange root disjoint from authoritative Run and target;
- copy only exact admitted input bytes and request material;
- omit authoritative Run paths from prompt, argv, env, cwd, and supplied files;
- invoke once;
- revalidate runtime, Run, target-root, Task/Round/request identities, and the prelaunch ledger prefix before result acceptance;
- import accepted outputs by bytes through Boundary;
- verify and publish authoritative RUN ArtifactRefs;
- clean exchange best-effort after evidence is secured, because lower-trust exchange must remain disjoint from authoritative state.

Add inspection hooks in fake providers so tests can assert every exposed path and byte set, because the design claim must remain executable and falsifiable.

## 17. Launcher and call outcome

Implement immutable `OperationRequest` plus one `AttemptEnvelope`; publish launch marker, captures, raw return, and call outcome only through predetermined create-only Attempt locations, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

Commit each `OperationRequest` through the phase-specific start event before publishing the launch marker immediately before the outer launch, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

After a launch marker exists, no path may launch that `OperationRequest` again, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

Implement the exact return and local-settlement table from architecture §18, because one launch algebra must preserve exact request identity and prevent replay.

Reject every invalid return and local-settlement combination, because one launch algebra must preserve exact request identity and prevent replay.

`SETTLED` means local process-group and communication-channel settlement only, because return validity and local process settlement have different safety and recovery consequences.

A prelaunch blocker creates no launch marker, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

A later explicit invocation may reevaluate a prelaunch blocker because launch is mechanically disproved.

A launch marker without a committed call outcome after interruption derives `NON_RESUMABLE`, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

## 18. Providers and commands

Provide the following components, because provider and command adapters must remain thin and mechanically admitted:

- deterministic fake provider;
- thin Claude Code and Codex adapters with fixed minimal inherited credential/environment-name allowlists whose values are never persisted;
- exact argv construction without shell interpolation;
- requested/observed routing recording, with omitted requested model/effort persisted as `UNSPECIFIED` and unobservable actual facts as `UNKNOWN`;
- explicit live authorization;
- bounded stdout/stderr/raw return;
- process-group observation and termination;
- no semantic interpretation, automatic route/model escalation, or fallback selection inside adapters, because provider and command adapters must remain thin and mechanically admitted.

Command execution uses only a named admitted command profile, because provider and command adapters must remain thin and mechanically admitted.

Bootstrap resolves each command profile through `EXACT_PATH` or `PATH_LOOKUP_AT_BOOTSTRAP`, freezes the resolved executable identity, finite nonempty accepted-exit-code set, fixed bounded explicit environment overrides, cwd scopes, slot schemas, and wait/termination policy, and every launch reverifies the executable, because independent implementations need one mechanically decidable contract.

Reject any command-profile wait or termination grace above the root command/grace limits, because finite policy must prevent unbounded work and keep resource use structurally visible.

A CommandStep supplies one admitted target-relative cwd and binds each named slot exactly once: target path, unique PlanInput name, RUN/BOUNDARY_ASSIGNED OutputRequirement ID, enum, integer, or bounded text according to the profile kind, because live execution requires admitted profiles and truthful evidence without a containment claim.

Boundary resolves exchange paths only after exact InputRefs and output locations exist, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Plan data never supplies an arbitrary executable, free-form argv, extra token, inherited environment name, environment override, or multi-token slot expansion, because persisted requests must not acquire or disclose undeclared host credentials.

Fixed explicit environment values carry a caller/host non-secret assertion; enforce field placement, bounds, and known prohibited credential fields without claiming semantic secret detection, because persisted requests must not acquire or disclose undeclared host credentials.

Model-supplied bounded text has no trusted non-secret status, because persisted requests must not acquire or disclose undeclared host credentials.

Inherited environment values are supplied by admitted name and are never persisted or hashed, because persisted requests must not acquire or disclose undeclared host credentials.

## 19. Proof links

Implement `Q11`, `Q15`, `Q16`, and the launcher portions of `Q32` and `Q33`, because launch and adapter behavior needs executable proof rather than prose confidence.

---

# Slice 5 — Planner, live Worker/command steps, output matching, and planning stop

## 20. Goal

Implement `D11`, `D12`, and `D13` without adding retry or a second success language, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

## 21. Planner

Construct a closed Planner request from exact persisted context using only RunPolicyView, path-free EvidenceBindingViews, admitted reference identities, path-free ArtifactRefViews, bounded ArtifactViews, TaskAuthorityView, WorkerRouteViews, and CapabilityProfileViews, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

The Planner request contains no canonical target root, authoritative RUN path, full InputRef/ArtifactRef serialization, provider launch metadata, or interactive tool capability, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

Accept only a correctly bound `PLAN` or `DECLINE`, because planning must remain immutable, bounded, and unable to redefine runtime authority.

PLAN validation uses the shared schemas and authority/profile checks, publishes the complete immutable PlanInputResolution set in the same `PLANNING_FINISHED` transition package, and classifies a missing or unresolvable current input as a rejected return rather than a partial Plan, because mission judgment must remain separate from continuation and operational failure.

DECLINE creates no steps; state derivation reads the accepted Decline directly and permits validation but no REPEAT, so no duplicate mutable or persisted repeat-forbidden flag exists, because mission judgment must remain separate from continuation and operational failure.

Any launched Planner operation has one Attempt only, because a second post-launch attempt could repeat external or hidden effects.

A settled non-OK outcome also proceeds to validation with no Plan; unsettled/unknown blocks, because return validity and local process settlement have different safety and recovery consequences.

## 22. Worker

Resolve the WorkerStep’s PlanInputs into exact InputRefs, then construct one Worker request with accepted step, admitted target root, exchange inputs, responsibility scopes, output requirements, and route profile, because live execution requires admitted profiles and truthful evidence without a containment claim.

Persist one bounded result and best-effort effect report, because reported effects are evidence for Validator judgment while integrity and unsettled activity remain mechanical blockers.

Provider-internal Worker tools remain inside that one opaque outer operation and never create nested STT steps or Boundary transitions, because live execution requires admitted profiles and truthful evidence without a containment claim.

Boundary must satisfy the following requirements, because trusted lifecycle mutation must remain centralized and mechanically verifiable:

- reject returned artifacts outside admitted requirement/path/type;
- persist a reported scope violation for Validator judgment without mechanically overriding the accepted Worker outcome, because the violation may be a reportable qualification rather than a reason to stop the sealed Plan; classify authoritative-state mutation as `INVALID`, because lifecycle integrity is compromised; classify unresolved local activity as `OPERATIONALLY_BLOCKED`, because later semantic validation cannot safely proceed;
- import RUN artifacts from exchange rather than trusting exchange paths;
- reverify TARGET artifacts before use;
- commit a Boundary-owned StepResult for every Worker or command completion; map a settled non-OK call to `INDETERMINATE` unless accepted role-specific facts conclusively establish `NOT_SATISFIED`, retain no fabricated role result, and never fabricate `SATISFIED`;
- stop later steps after any non-satisfied local outcome, because Worker evidence must preserve live-target truth without fabricating mission judgment.

## 23. Command

Resolve the CommandStep’s PlanInputs into exact InputRefs, validate its target-relative cwd, bind input/output exchange slots to exact InputRefs and OutputRequirements, validate scalar slot values, apply the profile’s frozen environment and accepted-exit-code policy, render and run the exact argv template, apply the architecture command judgment, and produce deterministic observation artifacts, because command behavior must remain reproducible from one frozen profile and exact runtime bindings.

Do not implement generic expressions or stdout-regex success, because command execution must remain within one frozen profile and exact argv.

## 24. Proof links

Implement `Q14`, `Q17`, `Q18`, and the role-context portions of `Q31`, because role behavior needs executable proof linked to its architecture decisions.

---

# Slice 6 — Mechanical Lead, child Tasks, and deterministic finalization

## 25. Goal

Implement `D3`, `D4`, `D17`, and the deterministic portions of `D20`, because depth-first orchestration and child finalization must remain deterministic.

## 26. Lead algorithm

At invocation start, because Lead must derive one mechanical next action without acquiring semantic authority:

1. validate that exactly one nonterminal root-to-leaf frontier exists, reject multiple incomparable active Tasks as `INVALID`, and then validate that root-to-deepest path, ledgers, packages, and identities;
2. record the deepest Task that was already `AWAITING_REPEAT`;
3. permit at most one consumption of that pre-existing transition;
4. repeatedly derive one mechanical next action until the invocation must stop, because mission judgment must remain separate from continuation and operational failure.

The loop may advance within one current Round, but it stops when any Round newly returns `REPEAT`, because creation of the next Round must remain caller-mediated rather than an internal loop.

Lead uses only Boundary entry points and compact receipts, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Add a test hook that fails when Lead imports provider, launcher, storage mutation, or broad workspace helpers directly, because orchestration must remain mechanical rather than acquire semantic authority.

## 27. Child behavior

Create child identity only from one accepted TaskStep, because delegation and same-mission continuation need distinct identity and failure rules.

Resolve its PlanInputs into parent TaskStep InputRefs, validate the declarative ChildAuthoritySpec as a full subset, construct child TaskAuthority with the unchanged target identity, create new child-scoped EvidenceBindings, and enforce mission relation floor, depth, and output contract, because delegation and same-mission continuation need distinct identity and failure rules.

Implement the mapping in architecture §20 exactly, including, because child identity and failure propagation must preserve parent audit without unsafe races:

- terminal child semantic mapping;
- child `OPERATIONALLY_STOPPED` after settled failure, then a Boundary-owned `OPERATIONAL_INDETERMINATE` parent StepResult without fabricating a child judgment;
- whole-Run `OPERATIONALLY_BLOCKED` for unsettled/unknown child work;
- whole-Run invalidity for conflicting child identity, because delegation and same-mission continuation need distinct identity and failure rules.

Implement deterministic child-to-parent finalization when child evidence is committed but parent `STEP_FINISHED` is absent, because crash recovery must complete the uniquely determined parent transition without rerunning the child.

## 28. Proof links

Implement the child/Lead portions of `Q04`, `Q19`–`Q21`, and `Q26`, because Lead and child behavior needs executable proof for every admitted lifecycle edge.

---

# Slice 7 — Validator, evidence novelty, FINISH, and finite REPEAT

## 29. Goal

Implement `D16`, the Validator portion of `D18`, and Round/Task finalization from `D20`, because mission judgment must remain separate from continuation and operational failure.

## 30. Validator request

Boundary first performs only the deterministic pre-Validator observations admitted by architecture §24, including required exact target outputs and already declared current-Round outputs, then builds one bounded Validator evidence index, because Validator judgment must depend on one closed reconstructible evidence set rather than hidden investigation.

The Validator request contains RunPolicyView with remaining Round capacity, admitted reference identities, path-free ArtifactRefViews, and bounded ArtifactViews; it contains no canonical target root, authoritative RUN path, full InputRef/ArtifactRef serialization, interactive tools, or command callback, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

When capacity is zero, the exact request output schema permits only `FINISH`, while the frozen private contract states why, because policy cannot authorize another Round.

The fake provider must expose the exact Validator request for context assertions, because qualification must prove the bounded request contains exactly the admitted evidence and no hidden authority.

## 31. Evidence eligibility

Implement the architecture §19 predicate as a deterministic mechanical floor, because repeat evidence must prove mechanical novelty without pretending to decide semantic materiality:

- current non-Decline Round producer;
- eligible producer kind;
- imported frozen RUN ArtifactRef, including a Boundary-frozen copy of a declared current-Round TARGET output when that exact output is selected;
- admitted requirement/observation binding;
- novelty identity absent from selected Round inputs, binding content SHA-256, artifact type, purpose, and originating requirement or observation method, so copy/rename/rewrap cannot create novelty;
- exact current-Round provenance;
- explicit Validator selection.

Materiality remains semantic and is qualified through adversarial fixtures rather than a scoring engine, because repeat evidence must represent materially new current-Round information rather than relabelled prior content.

## 32. Publication

Treat `FINISH + SATISFIED` as successful termination, because the mission is satisfied and no further Round is required.

Treat `FINISH + NOT_SATISFIED` as failed termination, because the mission is unsatisfied and another Round is not justified.

Treat `FINISH + INDETERMINATE` as inconclusive termination, because the available evidence is insufficient and another Round is not credibly useful.

Treat `REPEAT` as nonterminal only when a concrete remaining gap has a credible fresh-Round basis to close, because repetition without such a gap is not progress.

For every completed Validator call, validate binding, schema, judgment/disposition combination, remaining-capacity rule, terminal outputs, mechanically eligible repeat evidence, and every deterministic floor before classifying a ValidatorResult as accepted, because only a fully admitted result may enter lifecycle state.

Then publish/commit `VALIDATION_RECORDED` with the call outcome and an accepted ValidatorResult only when all floors pass, because return validity and local process settlement have different safety and recovery consequences.

A returned result that violates a floor is `RETURNED + REJECTED`, commits no accepted ValidatorResult, and yields settled `OPERATIONALLY_STOPPED` without semantic coercion, because return validity and local process settlement have different safety and recovery consequences.

On accepted ValidatorResult, apply the following deterministic finalization, because accepted judgment and continuation must be committed without semantic reinterpretation:

- publish/commit Round result;
- if REPEAT, derive `AWAITING_REPEAT` and stop invocation;
- if FINISH, deterministically publish/commit Task result.

Implement safe Round finalization when `VALIDATION_RECORDED` contains an accepted result but `ROUND_FINISHED` is absent, and safe Task finalization when `ROUND_FINISHED + FINISH` exists but `TASK_FINISHED` is absent, because resume must complete uniquely determined transitions without relaunching Validator or changing its judgment.

A Validator with unsettled or unknown local work blocks the Run, because later semantic execution cannot safely proceed while the operation may remain active.

A Validator launch without an accepted result uses the same Boundary call-failure and settlement classification as every other outer operation, because the failed operation produced no mission judgment.

Boundary never converts that failure into `FINISH + NOT_SATISFIED` or another fabricated judgment, because operational failure is not semantic evidence.

A settled Validator launch without an accepted OK result makes the Task `OPERATIONALLY_STOPPED`, because no accepted Validator judgment exists.

## 33. Proof links

Implement the validation portions of `Q04`, `Q22`–`Q26`, and `Q33`, because Validator and finalization behavior needs executable proof for every terminal and repeat edge.

---

# Slice 8 — CLI, status, diagnosis, prior evidence, and integration

## 34. Goal

Expose the accepted architecture without adding alternate flags or hidden policy, because public interfaces must expose exact architecture state without adding alternate policy.

## 35. CLI

Implement exactly, because CLI behavior must preserve immutable Run identity and truthful operator actions:

```text
stt start --workspace <target> --task-spec <file> --routing-file <file>
          [--prior-run <run-root>] [--allow-live-provider]
stt run --run-root <run-root>
stt status --run-root <run-root>
stt diagnose --run-root <run-root>
```

`start` validates and freezes all inputs, prepares runtime, publishes the Run and root Task, and advances until semantic finish, newly produced repeat, transient prelaunch block, operational stop/block, non-resumability, or invalidity, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

`run` changes no immutable field, because resumption must preserve the frozen Run identity and policy.

It reports `OPERATIONALLY_BLOCKED`, `OPERATIONALLY_STOPPED`, `NON_RESUMABLE`, or `INVALID` without launching a settlement probe or semantic operation, because CLI behavior must preserve immutable Run identity and truthful operator actions.

When an exact request is committed with no marker, `run` reevaluates current launch prerequisites and may return transient `PRELAUNCH_BLOCKED`; it does not persist that outcome as lifecycle state, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

`status` and `diagnose` are read-only, attempt the Run lock nonblocking, return `RUN_BUSY` without reading lifecycle files while a writer holds the lock, and otherwise report exact state, blocker, result references, permitted caller action, actual role/route/model/effort OperationRequest and launch counts, and Run-root retention warnings, because operators need truthful state visibility without causing lifecycle mutation.

For `OPERATIONALLY_BLOCKED` or `NON_RESUMABLE`, the permitted action is operator intervention to establish quiescence or choose an isolated replacement target before any new Run; the CLI must not present immediate restart on the same target as safe, because operators need truthful state visibility without causing lifecycle mutation.

Terminal receipts report the same call/launch visibility, because CLI behavior must preserve immutable Run identity and truthful operator actions.

Do not retain competing mission/provider/model/effort/attempt flags from superseded plans, because CLI behavior must preserve immutable Run identity and truthful operator actions.

The core performs no automatic polling; any automated host wrapper must require a finite caller-owned invocation budget and surface exhaustion explicitly, because finite policy must prevent unbounded work and keep resource use structurally visible.

The core never prunes a Run root automatically, because deletion would destroy same-Run resume and authoritative evidence.

## 36. Prior evidence

Validate only selectors supplied in RootTaskSpec against the optional prior root, because root semantics and host assumptions must be frozen before semantic execution.

Accept only prior RUN artifacts/reports/logs with exact bytes under the prior root, or a prior Boundary-frozen RUN copy of target bytes; reject direct live TARGET references, because mutable external target state cannot serve as immutable prior evidence.

Before root Task publication, copy every accepted selected artifact into a create-only current-Run ArtifactRef that preserves prior origin and committed-event provenance, because resume and substitution checks require exact facts to remain uniquely bound.

After publication, never reread the prior root, because prior evidence must remain selected, frozen, advisory, and separate from lifecycle state.

Never choose evidence semantically, merge lifecycle state, or accept uncommitted prior files as outputs or progress, because resume and operators need one deterministic interpretation of committed facts.

## 37. Public exit and query outcomes

Use a small stable public mapping for semantic judgments, lifecycle states, and transient query/invocation outcomes, because mission judgment must remain separate from continuation and operational failure:

```text
SATISFIED
NOT_SATISFIED
INDETERMINATE
AWAITING_REPEAT
PRELAUNCH_BLOCKED
OPERATIONALLY_BLOCKED
OPERATIONALLY_STOPPED
RUN_BUSY
NON_RESUMABLE
INVALID
USAGE_OR_SPECIFICATION_ERROR
```

Internal exceptions do not each receive a public exit code, because public outcomes must remain small and stable while preserving material distinctions.

## 38. Proof links

Implement `Q27`–`Q30`; final integration completes `Q31`–`Q36`, because CLI and integration behavior needs executable proof rather than interface description alone.

---

## 39. Canonical qualification scenario catalog

This is the only numbered scenario catalog, because one canonical scenario catalog prevents competing proof authority and orphaned requirements.

Each scenario is parameterized over its listed positive and known-bad cases, because separate IDs for every malformed field would repeat the same invariant rather than improve proof.

### Persistence and resume

- `Q01` **Canonical control data and ledger:** canonical UTF-8/sorted-key/compact/LF bytes, duplicate-key and nonfinite-number rejection, one-byte identity changes, bounded parsing, exact event vocabulary/order, exact lifecycle-state derivation, transient-outcome exclusion, valid chains, duplicate/gap/history mutation rejection, and narrow torn-tail handling, because parser or serializer disagreement would make identity and ledger validation implementation-dependent.
- `Q02` **Supported-host admission:** only `LOCAL_MVP_V1` is accepted; required lock, create-only publication, atomic rename, directory sync and honest durability observations, `lstat`, hashing, local-filesystem behavior, and process observation pass or fail before Run publication; weaker or unknown profiles reject, because unsupported host primitives can invalidate publication, locking, and settlement guarantees before a Run exists.
- `Q03` **Transition-package and request commit:** valid package/event commit, phase-start request event before marker, narrow package-without-event completion, stale head, competing package, and event/package mismatch, because packages and events must remain synchronized to prevent state corruption or lost mutations.
- `Q04` **Lifecycle crash windows:** verified run without root Task, conflicting/incomplete canonical root publication, pre-Round Task, prelaunch request, complete call package before event, ambiguous launched call, child-to-parent finalization, Validator-record-to-Round finalization, FINISH Round-to-Task finalization, committed REPEAT resume, and operator-quiescence/isolated-target requirements before recovery from ambiguous launch, because crash recovery must reconstruct exact state unambiguously from committed packages.

### Root, runtime, and identity

- `Q05` **RootTaskSpec:** exact task-spec/routing bytes freeze before parsing and RootTaskSpec routing identity must match; complete specification starts; root Task is count 1 at depth 0 and Round 0/Plan elements count toward their limits; `host_profile` is exactly `LOCAL_MVP_V1`; every named count/capture/wait field exists with fixed byte/second units, finite positive values, and conservative ceiling rejection; structured required_outputs always governs artifact matching while mission prose is never parsed as an output contract; selector purpose and type are explicit; TARGET_PATH resolves only under target; BOOTSTRAP_FILE resolves only under the canonical task-spec parent and rejects absolute/traversal/symlink/special/`.git`/escape cases; prior selectors require exactly one prior root and an unused prior root rejects; missing, structurally inconsistent, mutable, or unresolved fields reject without claiming semantic prose-conflict detection, because root configuration must freeze before any semantic execution begins.
- `Q06` **Frozen runtime:** source root resolves uniquely from the active entry point and manifest root; explicit manifest closure, bytes/mode, symlink/special-file, mixed-generation, target self-update, dynamic data/import, and archive reachability cases, because runtime must be immutable and closed during execution to prevent semantic drift.
- `Q07` **Location, retention, target identity, and external-evidence independence:** source may equal target or otherwise be mutually non-containing; Run and exchange remain disjoint; same-path target replacement is detected or the host is rejected; selected prior evidence is imported before Task publication; deletion or mutation of the prior root after publication does not change current evidence; no automatic pruning occurs and deletion warnings are explicit, because location separation protects control state, root identity prevents silent rebinding, frozen imports remove dependence on prior roots, and explicit retention keeps evidence loss operator-visible.

### Authority, trust, and schemas

- `Q08` **Path and child authority:** component-aware containment plus absolute, traversal, symlink, special, `.git`, Run path, and every child-expansion case, because path scope must be mechanically enforceable without silent escape.
- `Q09` **Capability and secret admission:** unique Worker-route-to-profile binding; command `EXACT_PATH` and `PATH_LOOKUP_AT_BOOTSTRAP` resolution; executable identity revalidation; finite accepted exits; fixed explicit environment overrides; target-relative cwd; reusable slot schemas plus step-time target-path/PlanInput/OutputRequirement/enum/integer/bounded-text bindings; effect classes; inherited environment names; fixed provider credential-name allowlists; declared-nonsecret fixed-field placement and known-prohibited-field rejection without treating model-supplied text as proven non-secret; and reported out-of-scope effects, because secrets and capabilities must be mechanically bounded and verifiable at admission.
- `Q10` **Instruction trust and private contracts:** target/prior injection cannot alter mission, authority, routing, policy, schema, or role contract; Planner/Validator receive path-free TaskAuthorityView, WorkerRouteView, and CapabilityProfileView rather than canonical target, executable, adapter, or credential-launch metadata; general repository contracts do not govern STT runtime, because target data must not become executable control authority.
- `Q11` **Exchange and post-call integrity:** exchange roots are owner-exclusive and disjoint; no authoritative Run path is exposed; only admitted bytes cross; outputs remain non-authoritative until import; post-call runtime/target/Run/ledger mutation invalidates before acceptance, because minimizing control-state exposure and revalidating it after the call prevents contaminated evidence from being accepted without claiming hostile containment.
- `Q12` **Input/output/artifact binding:** PlanInputs remain declarative and cannot contain authoritative ArtifactRefs or InputRefs; Boundary-owned immutable PlanInputResolutions bind current evidence/target identities and defer prior-step requirements; initial, prior, child, and repeat EvidenceBindings remain availability records rather than consumption authority and expose only path-free EvidenceBindingViews to Planner; every use reverifies the resolution and creates a complete role/Task/Round/step-bound InputRef; named target mutation yields transient prelaunch mismatch rather than rebinding; discriminated provenance covers Bootstrap/prior/existing-target/step/child/command/Boundary origins; `EXISTING_ALLOWED` versus produced-output authority, closed producer constraints, exact purpose, structural principal-consumer compatibility without mandatory downstream consumption, canonical OutputRequirement matching, discriminated Boundary-owned StepResult binding without fabricated role/child results, exact artifact-type label equality without plugin semantics, mode/path, mutation-before-use, and special-file rejection all qualify, because artifact provenance must remain distinct and verifiable to prevent substitution.
- `Q13` **Plan schema and limits:** identity header; exact common and kind-specific fields; route-derived Worker profile without a second profile field; command cwd and slot bindings; declarative ChildAuthoritySpec without resolved target identity or duplicate route/profile fields; exact StepOutcome vocabulary; TaskStep-only `OPERATIONAL_INDETERMINATE`; complete PlanInputResolution variants; accepted-Plan and resolution immutability; declarative EVIDENCE_BINDING/TARGET_PATH/STEP_OUTPUT PlanInputs; future/cross-Task references; fabricated authoritative references; duplicate step/input/output IDs or names; unknown profiles; generic success expression; and per-Round step cap, because Plan structure must be unambiguous and finite to prevent semantic drift during execution.

### Semantic roles and operations

- `Q14` **Planner:** exact RunPolicyView and remaining Task/depth/Round/step capacity, EXECUTE, INVESTIGATE, zero-step, DECLINE, complete PlanInputResolution publication with the accepted Plan, missing/unresolvable input rejection, settled non-OK, rejected return, and unsettled block; Decline never creates steps or REPEAT, because Planner semantics may be judgmental while its authority, inputs, outputs, limits, and persistence must remain closed and finite.
- `Q15` **Call and local-settlement algebra:** every valid and invalid post-launch return/result/settlement combination, no persisted call outcome before a marker, Worker/command role-result versus Boundary-owned StepResult separation, settled non-OK mapping to `INDETERMINATE` unless accepted facts establish `NOT_SATISFIED`, no fabricated success, bounded capture, truthful local-only settlement, accepted structured binding, and same-Run stopping on unsettled or unknown work without a settlement-probe transition, because return values must be truthful and distinguishable to preserve mission judgment integrity.
- `Q16` **Exactly one launch:** marker ordering, no second launch for any role, transient non-persisted `PRELAUNCH_BLOCKED` on current prerequisite failure, explicit prelaunch reevaluation while no marker exists, and non-resumable ambiguous launch, because a second post-launch attempt could replay target, billing, network, remote, or escaped-child effects.
- `Q17` **Worker:** satisfied/not-satisfied/indeterminate outcomes, live target create/edit/move/delete, admitted output import, opaque provider-internal tools, effect-report limits, persistence of a reported scope violation for Validator judgment without automatic Worker-outcome override, continued ordered execution when no mechanical blocker exists, authoritative-state mutation to `INVALID`, and unresolved local activity to `OPERATIONALLY_BLOCKED`, because Worker outcomes must be truthful and reported effects must inform Validator judgment without automated override.
- `Q18` **Command:** named reusable profile, admitted target-relative cwd, step-time unique-input and RUN/BOUNDARY_ASSIGNED output slot bindings, single-token scalar validation, exact rendered argv, no shell by default, fixed explicit environment and finite accepted exits, profile wait/grace bounded by root policy, accepted nonzero exit, failed/unstable output, bounded logs, admitted target change, inherited environment handling, no replay, and representative build, test, and file-transformation profile usability, because command execution must be deterministic and profile-based without hidden shell semantics.

### Lead, child, and validation

- `Q19` **Mechanical Lead:** exactly one nonterminal root-to-leaf frontier, multiple active-branch rejection, ordered depth-first execution, compact receipts, no direct provider/storage mutation dependency, no scheduler/cursor, and newly produced REPEAT stop, because Lead must execute exactly one deterministic path without semantic drift or multiple active branches.
- `Q20` **Child identity and limits:** deterministic path, distinct/narrower mission floor, relation reason, declarative ChildAuthoritySpec, Boundary construction with unchanged target identity, full authority/profile subset, depth, total-Task budget, and later-step waiting, because child identity must be distinct and scoped from parent to prevent authority leakage.
- `Q21` **Child failure propagation:** semantic mapping, settled child `OPERATIONALLY_STOPPED` to parent `OPERATIONAL_INDETERMINATE` StepResult and parent audit, unsettled/unknown whole-Run block, and invalid child, because settled child failure must remain auditable without racing active child work or fabricating a judgment.
- `Q22` **Validator context and independence:** RunPolicyView plus bounded evidence index with authoritative reference hashes, path-free ArtifactRefViews, and ArtifactViews, no canonical target/authoritative Run path or interactive tools, separate invocation, truthful `UNKNOWN` isolation, and explicit `INDETERMINATE + FINISH` when omitted evidence cannot be gathered safely, because Validator must remain independent and evidence-bounded to prevent semantic drift or hidden authority.
- `Q23` **Terminal judgment and outputs:** all Validator mechanical floors execute before accepted-result classification, `VALIDATION_RECORDED` records every call outcome, `FINISH + SATISFIED` proves successful termination, `FINISH + NOT_SATISFIED` proves failed termination, `FINISH + INDETERMINATE` proves inconclusive termination, `REPEAT` requires a concrete credibly closable gap, Validator operation failure uses the common Boundary call/settlement mechanism without fabricated judgment, floor-violating returns become rejected and settled `OPERATIONALLY_STOPPED` without judgment, accepted-result Round finalization, required-output floor, wrong terminal selection, and Validator unsettled operational block as a same-Run stop, because terminal decisions must be mutually exclusive and final without replay.
- `Q24` **REPEAT evidence:** current PLAN Round producer, frozen RUN import including a declared current-Round TARGET output copied deterministically by Boundary, mechanical novelty by exact file content/type or canonical observation identity, and rejection of prose, prior evidence, byte-identical copy/rename, repeated observations, arbitrary freezes, and no-Plan/Decline cases; representative changed-byte wrappers are challenged semantically without a universal wrapper-detection claim, because repeat evidence must be mechanically new current-Round work before Validator can judge whether it is materially useful.
- `Q25` **REPEAT semantic boundary:** Validator-policy rejection of semantically unchanged wrappers, restatement, cosmetic activity, far failure, hard blocker, and circular replay; positive material leverage, incidentally satisfied investigation, partial execution progress, and next-Planner independence; Boundary performs no semantic replay-wording detector, because REPEAT must not loop on unchanged work or circular replay.
- `Q26` **Finite continuation:** identical mission/fresh Plan, contiguous Rounds, Round/step/Task/depth limits, RunPolicyView remaining-capacity input to Planner/Validator, FINISH-only schema at zero capacity, violating REPEAT classified rejected without coercion, one pre-existing repeat consumption per invocation, and child Round 0 exemption, because REPEAT budget must be finite and mechanically enforced to prevent runaway loops.

### Prior evidence, CLI, and repository integration

- `Q27` **Prior evidence:** caller-selected committed compatible prior RUN artifacts/reports/logs, including Boundary-frozen RUN copies of target bytes, are copied into current-Run ArtifactRefs before Task publication and remain advisory; direct live TARGET references reject; prior-root deletion after publication does not affect current evidence; unselected, uncommitted, incompatible, injected, externally rebound, or lifecycle-merging material rejects, because prior evidence must remain advisory and separate from current-Run lifecycle state.
- `Q28` **CLI immutability:** task-spec/routing entry, prior-root/selector consistency, no superseded semantic flags, resume cannot change policy/routing/auth, `RUN_BUSY` query behavior, and exact exit-state mapping, because CLI must preserve Run identity through all operations without hidden mutation.
- `Q29` **Status and diagnosis:** nonblocking read-only locking with `RUN_BUSY`, exact state/blocker/next action, OperationRequest and launch counts, terminal receipt visibility, retention warning, same-Run operational-stop reporting, no unsafe immediate-restart advice after unknown settlement or ambiguous launch, missing root, and no automatic repair, because status must be truthful and unsuggestive of repair to prevent operator confusion.
- `Q30` **Plain and Git targets:** both work without Git lifecycle authority or target `.stt`; a change to an exact target identity that Boundary later reuses yields a visible mismatch rather than silent rebinding, while unrelated or unobserved external changes may remain unknown, because STT must preserve evidence it consumes without claiming control over the open target.
- `Q31` **Bounded context:** the canonical ArtifactRefView/ArtifactView builder emits path-free metadata plus full, bounded-text, or metadata-only content through deterministic range/truncation/metadata policy and no Boundary-generated semantic summary; Planner receives EvidenceBindingView and Planner/Validator receive RunPolicyView, TaskAuthorityView, WorkerRouteView, CapabilityProfileView, and authoritative reference hashes but never full InputRef/ArtifactRef, canonical target, authoritative RUN path, device/inode, executable, adapter, credential, or launch metadata, while path-like strings inside admitted untrusted bodies remain data; Planner/Worker/Validator receive only role-specific admitted views; truncation is visible and cannot masquerade as complete evidence; Lead carries references only, because lower-trust roles must not receive authoritative metadata or control-state paths.
- `Q32` **Provider adapters and routing truth:** fake and controlled Claude/Codex launchers, explicit live authorization, requested versus observed routing including `UNSPECIFIED` requested fields and truthful `UNKNOWN` observations, fixed inherited credential-name allowlists, secret-value non-persistence, no automatic model/route escalation, and no semantic adapter logic, because provider translation must preserve request identity and report unobservable routing facts as unknown.
- `Q33` **Resource, capture, and call visibility:** finite Task/Round/step budgets, complete fixed-unit capture/wait schemas including structured-request and total exchange-input separation, conservative hard-ceiling rejection, byte/time/entry enforcement, deterministic overflow, structural semantic-call bounds, actual role/route/model/effort OperationRequest and launch counts, terminal receipt visibility, a separately persisted finite automated-host polling budget when such a host exists, retention warnings, and honest stop at policy boundaries, because resource budgets must be finite and mechanically enforced to prevent runaway work.
- `Q34` **Static superseded-concept rejection:** §40 patterns fail active docs/code while ordinary non-contract English is tolerated narrowly, because superseded concepts must fail early to prevent silent reentry into implementation.
- `Q35` **Repository regression:** focused STT, compile, formatting/lint, shell fixtures, `git diff --check`, runtime closure, and full repository suite, because regression testing must remain comprehensive to catch implementation drift.
- `Q36` **Design lineage and promotion:** decision/subdecision disposition, architecture-to-implementation and decision-to-Q links, no dependency on unavailable external audits, accepted document-pair commit recorded externally as implementation base without changing accepted file bytes, WELL review, RunSkeptic receipts, and no readiness status with unresolved blocker, because design decisions must be traceable and promotion must be auditable without lost context.

---

## 40. Static design-consistency checks

Fail qualification when active STT documents or code contain, because static checks must prevent superseded concepts from silently reentering implementation:

- free-form root submission as the source of mission/authority/outputs;
- runtime parsing of mission prose as an artifact-output contract or semantic contradiction detector;
- unresolved RootTaskSpec selectors or a pre-Bootstrap TaskAuthority that pretends target identity is already known;
- `maximum_attempts`, a call-visibility disable switch, or automatic post-launch retry;
- launch marker without a ledger-committed phase-specific OperationRequest;
- persisted `PRELAUNCH_BLOCKED` lifecycle state or event;
- same-mission child continuation;
- multiple incomparable nonterminal Task frontiers;
- mutation or replacement of an accepted Plan;
- automatic provider/model escalation or fallback;
- Validator interactive tool or command callback;
- lower-trust authoritative Run-root path exposure;
- duplicate Worker route/profile selection, resolved child TaskAuthority in Plan output, duplicate child route/profile fields, or a command profile that binds runtime InputRef identities before a step exists;
- arbitrary command executable, free-form argv, untyped argument slot, model-supplied environment override, or inherited environment selection;
- generic command success expressions;
- Decline followed by REPEAT;
- Validator prose, byte-identical copy/rename, repeated canonical observation, or other mechanically non-novel identity as repeat evidence;
- unbounded per-Task Round count;
- whole-Run blocking for a child `OPERATIONALLY_STOPPED` state without the parent-audit rule;
- competing architecture semantics in the implementation plan;
- parallel Task or step execution inside one Run, a second active frontier, built-in cross-Run coordination, or target-wide writer exclusion;
- automatic Git commit, staging, push, merge, rebase, or publication;
- automatic rollback, target restoration, or multi-resource transaction;
- RunSkeptic or archived Target Task execution inside the STT runtime;
- target `.stt` authority;
- archive runtime import;
- sandbox, rollback, complete-effect, actual-routing, or actual-isolation overclaim, because static checks must prevent superseded concepts from silently reentering implementation.

Allow ordinary English uses only when they do not name active lifecycle contracts, because static checks must prevent superseded concepts from silently reentering implementation.

---

## 41. Invariant-to-proof map

The following table records the section's structured relationships, because every decision needs executable coverage and every mechanism needs architecture authority.

| Decisions | Scenarios |
|---|---|
| `D1` | `Q05`, `Q28` |
| `D2`–`D3` | `Q04`, `Q13`, `Q19`, `Q20`, `Q26`, `Q33` |
| `D4` | `Q19` |
| `D5`–`D6` | `Q02`, `Q06`, `Q07`, `Q11`, `Q30` |
| `D7` | `Q01`, `Q03`, `Q04` |
| `D8` | `Q11` |
| `D9`–`D10` | `Q08`–`Q10`, `Q31`, `Q32` |
| `D11` | `Q14` |
| `D12` | `Q12`–`Q14` |
| `D13` | `Q17`, `Q18`, `Q30` |
| `D14`–`D15` | `Q15`, `Q16`, `Q32` |
| `D16` | `Q22`–`Q26` |
| `D17` | `Q20`, `Q21` |
| `D18` | `Q10`, `Q22`, `Q31`, `Q32` |
| `D19` | `Q27` |
| `D20` | `Q03`, `Q04`, `Q21`, `Q29` |
| `D21`–`D22` | `Q34`–`Q36` |
| `D23` | `Q33`, `Q36` |

Every production mechanism must map to at least one decision and one scenario, because every decision needs executable coverage and every mechanism needs architecture authority.

An unmapped mechanism is removed or the architecture is amended before acceptance, because every decision needs executable coverage and every mechanism needs architecture authority.

---

## 42. Full verification

Run, in repository-native form, because acceptance requires repository-wide proof rather than focused tests alone:

- canonical STT qualification suite;
- Python compile checks;
- existing formatting and lint checks;
- shell syntax checks for launch fixtures;
- `git diff --check`;
- full repository suite;
- static design-consistency checks;
- import/runtime-manifest closure checks;
- no-archive and no-target-state checks.

Tests must use controlled fake providers and executables for call, path, effect, settlement, and routing observations, because acceptance requires repository-wide proof rather than focused tests alone.

Paid live calls are not required for qualification, because acceptance requires repository-wide proof rather than focused tests alone.

---

## 43. Complexity review

Before each commit and final acceptance, remove, because unnecessary mechanisms obscure failure modes and create new drift:

- duplicate schema or state derivation;
- duplicate path or identity logic;
- speculative provider abstraction;
- semantic progress score;
- hidden retry/replay path;
- mutable cursor, scheduler, or task registry;
- broad exception catch that erases the blocker;
- broad Run or target context passed to a model;
- hidden Git assumption;
- dead compatibility code;
- module whose only role is forwarding without a boundary or proof benefit, because unnecessary mechanisms obscure failure modes and create new drift.

Retained complexity must point to the specific decision and failure mode it protects, because unnecessary mechanisms obscure failure modes and create new drift.

---

## 44. Definition of implementation done

The STT MVP is done only when, because implementation must stop only after every accepted architecture and proof obligation is satisfied:

1. the accepted architecture and this plan have unchanged recorded hashes and their containing repository commit is the recorded implementation base;
2. every scenario `Q01`–`Q36` passes;
3. full repository verification passes;
4. every production mechanism maps to a decision and scenario;
5. no static superseded concept remains;
6. no lower-trust process receives authoritative Run-state paths;
7. no OperationRequest launches twice after a marker;
8. RootTaskSpec is the only source of root semantics;
9. finite Task depth and Round limits are enforced;
10. settled `OPERATIONALLY_STOPPED` versus unsettled `OPERATIONALLY_BLOCKED` child failure follows architecture exactly;
11. prior evidence is selected, verified, advisory, and non-merged;
12. status and diagnosis report uncertainty, `RUN_BUSY`, OperationRequest/launch counts, terminal receipt visibility, and retention risk without repair or semantic fabrication;
13. implementation contains no archive dependency, target `.stt` authority, sandbox claim, or automatic publication;
14. final WELL and RunSkeptic review finds no unresolved promotion blocker, and any status-line change has restarted and completed those reviews on the final unchanged bytes;
15. per-Run writer locking, target non-locking, caller-managed cross-Run non-overlap, and point-in-time target observations follow the architecture exactly;
16. implementation stops.

The implementation-done definition is executable acceptance rather than proof that every provider or arbitrary process behaves honestly, because implementation must stop only after every accepted architecture and proof obligation is satisfied.
