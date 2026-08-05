# STT MVP Architecture Plan

**Status:** Canonical cumulative candidate; historical reconstruction complete; implementation prohibited until the final independent review gates pass
**Repository:** `saffih/skeptic`
**Historical reconstruction base:** `74c4f6a2c34da501101141525c8a34d691c384a1`
**Implementation-base rule:** implementation branches from the exact repository commit that contains the accepted unchanged canonical document pair; that commit is recorded in the implementation handoff or execution receipt after document promotion and is not inserted retroactively into the accepted files
**Canonical reconstruction source:** W5 architecture SHA-256 `e6dad383f1aefce4cb60f6364103ff5a037f68ca49050248ddc5b3865882ce9a`
**Companion implementation plan:** `plans/stt-mvp-implementation-plan.md`
**Document profile:** `docs/well.md`
**Scope:** STT MVP architecture only

This is an architecture document, because it defines the authoritative structure, responsibilities, constraints, boundaries, and lifecycle meaning of the STT MVP.

This document must be WELL-formed, because architecture decisions must preserve their reasons and meaning through implementation, review, maintenance, and later change.

WELL means **Warranted, Explicit, Lean, and Linked**, because every retained design proposition must have a recoverable reason, state every material qualification, avoid unnecessary duplication, and remain connected to its consequences and checks.

WELL formation protects the integrity of this architecture, because it reduces unsupported claims, hidden assumptions, semantic drift, accidental loss, contradictory authority, and implementation by guesswork.

The complete normative WELL profile is defined in `docs/well.md`, because one canonical definition prevents this document from creating a competing writing standard.

---

## 1. Purpose and authority

Safe Target Task (STT) executes one immutable mission against a live target through bounded planning, sequential execution, independent validation, and durable evidence, because live execution requires admitted profiles and truthful evidence without a containment claim.

These controls are required because ordinary agent execution can lose identity, repeat uncertain operations, accept unverified outputs, or claim completion without inspectable support.

The STT MVP architecture is the only source of truth for STT runtime meaning, because runtime meaning needs one canonical owner and an explicit protection boundary.

The implementation plan owns construction order and executable proof, but it may not redefine a lifecycle rule, because two normative descriptions would drift.

The STT MVP architecture is the final cumulative historical integration rather than a wholesale promotion of any one predecessor, because each historical revision corrected one problem while risking unrelated losses.

Every retained proposition is represented in the current contracts and the canonical lineage matrix in §33, because future edits must preserve each proposition and its reason without creating competing authority.

Historical P0–P5 and W0–W4 material is secondary evidence only and cannot override this canonical architecture, because repository implementation needs one current source of truth.

STT protects, because runtime meaning needs one canonical owner and an explicit protection boundary:

- immutable mission, authority, routing, policy, and accepted planning decisions;
- separation of planning, execution, validation, and deterministic orchestration;
- sequential depth-first execution through a mechanical Lead;
- explicit admission of target paths, role routes, command profiles, environment names, and declared external-effect classes;
- append-only lifecycle evidence with recoverable commit boundaries;
- bounded, reconstructible model context through identity-bound references;
- truthful distinctions among returned values, rejected returns, missing returns, semantic failure, and uncertain local settlement;
- exceptional same-mission continuation through finite caller-mediated Rounds;
- a frozen active runtime when Skeptic is itself the target, because runtime meaning needs one canonical owner and an explicit protection boundary.

STT does not prevent or fully observe arbitrary filesystem, process, credential, network, service, remote, or external effects, because persisted requests must not acquire or disclose undeclared host credentials.

It is an orchestration-integrity system rather than an operating-system sandbox, so every enforceable admission rule is separated below from cooperative responsibility and unknown process behavior, because the MVP must not imply protection that it cannot enforce.

Archived Target Task material is historical evidence only, because runtime meaning needs one canonical owner and an explicit protection boundary.

No previous lifecycle is inherited wholesale, because every retained protection must fit the current live-target and Round model.

---

## 2. Entry contract: RootTaskSpec

Bootstrap is deterministic, so every semantic root decision must be supplied before Bootstrap rather than inferred from free-form submission text, because root semantics and host assumptions must be frozen before semantic execution.

A new Run receives one immutable `RootTaskSpec`, because root semantics and host assumptions must be frozen before semantic execution:

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

`mission` contains the objective, scope, constraints, non-artifact success meaning, and prohibited actions, because Bootstrap must freeze accountable root semantics before any semantic execution.

Structured `required_outputs` are the only normative artifact-output contract, because Bootstrap must freeze accountable root semantics before any semantic execution.

Runtime output matching never interprets mission prose as an artifact requirement and always gives the structured contract precedence, because target and prior content must not acquire control authority.

A prose contradiction is a RootTaskSpec authoring defect surfaced by review or static lint where mechanically recognizable; Bootstrap does not claim semantic contradiction detection, because root semantics and host assumptions must be frozen before semantic execution.

`root_authority_spec` supplies the exact admission and capability grants defined in §10 without pretending the target filesystem identity is known before Bootstrap, because root semantics and host assumptions must be frozen before semantic execution.

`required_outputs` uses `OutputRequirement` from §14, because structured output requirements are the canonical artifact-output contract.

`initial_input_selectors` names exact target-relative or Bootstrap-supplied files that Bootstrap must freeze and resolve into Task-scoped `EvidenceBinding` values. `prior_evidence_selectors` names exact committed prior references that Bootstrap imports into the same binding model, because resume and substitution checks require exact facts to remain uniquely bound.

Nonempty `prior_evidence_selectors` require exactly one caller-supplied prior Run root, while a prior Run root with no selectors is rejected, because the prior root is only a location for explicitly selected evidence and must not become ambient history.

`run_policy` freezes at least, because Bootstrap must freeze accountable root semantics before any semantic execution:

```text
maximum_task_depth
maximum_tasks_per_run
maximum_rounds_per_task
maximum_steps_per_round
capture_limits
wait_limits
host_profile: LOCAL_MVP_V1
```

The bounded limit groups have closed minimum schemas, because independent implementations need one mechanically decidable contract:

```text
capture_limits:
  max_control_json_bytes
  max_control_json_depth
  max_request_bytes
  max_exchange_input_bytes
  max_raw_return_bytes
  max_stdout_bytes
  max_stderr_bytes
  max_run_artifact_bytes
  max_artifact_view_bytes
  max_workspace_entries
  max_ledger_line_bytes

wait_limits:
  planner_seconds
  worker_seconds
  command_seconds
  validator_seconds
  termination_grace_seconds
```

`max_request_bytes` bounds structured request material and prompt bytes, while `max_exchange_input_bytes` bounds the total exact artifact bytes copied into one exchange, because Bootstrap must freeze accountable root semantics before any semantic execution.

Every count, byte limit, depth, and duration is a finite positive integer; byte fields use bytes and duration fields use seconds, because independent implementations need one mechanically decidable contract.

The implementation may choose conservative hard ceilings below platform maxima, but it must document and test them and may not reinterpret units or omit a field, because independent implementations need one mechanically decidable contract.

`RunPolicyView` is the immutable path-free projection exposed to Planner and Validator, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

It contains every frozen count/capture/wait limit plus current Task depth, current Task count, current Round number, and mechanically computed remaining Task, depth, Round, and current-Plan step capacity; it carries the exact run-policy identity but no authority to change policy, because finite policy must prevent unbounded work and keep resource use structurally visible.

The host or caller that creates `RootTaskSpec` owns mission finalization, root authority, required outputs, initial evidence, prior evidence selection, and finite resource policy, because current lifecycle evidence must not depend on mutable or ambient history.

STT validates and freezes the specification but does not semantically complete it, because deterministic Bootstrap must not become an undeclared Planner.

Bootstrap first copies and verifies exact task-spec and routing bytes into its bounded handoff, parses only those frozen copies, and requires `RootTaskSpec.routing_identity` to equal the exact frozen routing-file identity, because finite policy must prevent unbounded work and keep resource use structurally visible.

A changed `RootTaskSpec` or routing file starts a new Run, because root semantics and host assumptions must be frozen before semantic execution.

Same-Run resume never rereads or repairs the mutable source from which either was created, because Bootstrap must freeze accountable root semantics before any semantic execution.

---

## 3. Historical reconstruction and degradation finding

The current design combines protections from several revisions because no single prior revision is correct as a whole:

- `c3be467ec71924f63ea5bafa8f97908b594e8d15` preserved concrete authority, output, role-contract, attempt, publication, and depth-first resume rules, but used staged mutation and a one-cycle Task model, because future edits must preserve independently protected failure modes rather than repeat historical loss.
- `702b480dc55ef935970fd60031f80d4320e43ad8` correctly adopted truthful live-target execution, a disjoint temporary Run root, and cooperative rather than sandbox scope, but removed many concrete contracts during a broad rewrite, because future edits must preserve independently protected failure modes rather than repeat historical loss.
- `81da365c035250313c83a957c409845490c7bf1a` correctly introduced fresh Task Rounds, caller-mediated `REPEAT`, and a useful distinction between completed errors and missing returns, but left root specification, capability authority, exchange isolation, and several publication edges incomplete, because future edits must preserve independently protected failure modes rather than repeat historical loss.
- the first WELL repair recovered some lost definitions, but it added unsafe post-launch retries, over-conservative child blocking, duplicated implementation semantics, and an unsupported claim of implementation readiness, because future edits must preserve independently protected failure modes rather than repeat historical loss.

The recurring degradation mechanism was whole-document replacement without a complete decision lineage, because future edits must preserve independently protected failure modes rather than repeat historical loss.

A sentence was removed because one mechanism changed even when the same sentence also protected an independent failure mode.

Future changes must include the lineage entry required by `D22` before promotion, because future edits must preserve independently protected failure modes rather than repeat historical loss.

Compression is valid only after a proposition-level comparison confirms that every material protection is preserved, changed with replacement, or intentionally removed, because future edits must preserve independently protected failure modes rather than repeat historical loss.

---

## 4. Canonical decision index

Stable decision identifiers are required because the implementation plan and future revisions must link to architecture meaning without restating it.

| ID | Decision | Warrant | Primary refutation path |
|---|---|---|---|
| `D1` | A Run begins from one immutable `RootTaskSpec`; Bootstrap never invents semantic root fields. | Root mission, authority, and outputs otherwise have no accountable owner. | Start is rejected when any required root field or identity is missing or mutable. |
| `D2` | `Task`, `Round`, and `Attempt` are distinct identities. | Semantic continuation, sub-mission delegation, and one process launch have different safety rules. | Tests prove no retry creates a Round and no Round reuses an accepted Plan or launch. |
| `D3` | A Task owns zero or more Rounds until Round 0 commits; every repeated Round is fresh and finite. | Atomic Task publication creates a valid pre-Round state, while unbounded repetition can consume resources indefinitely. | Round numbers are contiguous, mission bytes remain equal, and the finite round cap is enforced. |
| `D4` | Lead is mechanical; every lifecycle transition and outer operation is mediated by Boundary. | Semantic authority must not leak into orchestration or persistence. | Instrumentation detects any direct Lead-to-provider or Lead-to-state mutation path. |
| `D5` | The authoritative Run root and per-call exchange are disjoint from source and target; source and target are either exactly equal or neither is an ancestor of the other; the active runtime is frozen. | Self-modification must remain possible without ambiguous partial overlap or letting target edits and lower-trust calls replace the controller. | Runtime survives target edits; provider requests contain no authoritative Run-root path; equal and disjoint source/target cases qualify while ancestor overlap fails. |
| `D6` | STT runs only on a host that satisfies an explicit capability floor. | Locking, atomic publication, and process observation cannot be left as late implementation preferences. | Bootstrap fails before Run publication when a required primitive is unavailable. |
| `D7` | Lifecycle identities and accepted payloads are immutable; ledger events commit verified transition packages. | Resume is unsafe when accepted facts can be overwritten or silently rebound. | Mutation, mismatched package/event, sequence gaps, and conflicting publication fail visibly. |
| `D8` | Lower-trust semantic processes receive non-authoritative exchange copies, never authoritative Run-state paths, and authoritative identities are revalidated after every call. | Reverification of one artifact cannot protect the ledger or runtime from a process given or discovering control-state locations. | Request inspection proves no Run-root path is disclosed; post-call mutation fixtures invalidate the Run before result acceptance. |
| `D9` | TaskAuthority separates enforceable STT admission from cooperative effect responsibility, contains explicit capability profiles, and exposes only path-free TaskAuthorityView and CapabilityProfileView data to non-Worker semantic roles. | Path lists alone cannot authorize or bound commands, environment inheritance, network use, or remote mutation. | Child expansion and undeclared profile use are rejected; reported out-of-scope effects are preserved for Validator judgment, while authoritative-state mutation or unresolved local activity still fails mechanically. |
| `D10` | STT-private Planner, Worker, and Validator contracts govern runtime, and target/prior content is untrusted data. | Repository or prior evidence must not acquire instruction, authority, or routing status. | Injection fixtures cannot alter mission, authority, routing, policy, or control instructions. |
| `D11` | Planner receives closed persisted context and returns `PLAN` or `DECLINE`; `DECLINE` can only finish the current Round. | A decline that later requests repetition contradicts its claim that no useful bounded path exists. | No Decline path creates steps, tools, or `REPEAT`. |
| `D12` | Plan, `PlanInput`, `PlanInputResolution`, `EvidenceBinding`, `InputRef`, `OutputRequirement`, `ArtifactRef`, provenance, Boundary-owned StepResult, and role-result identities have canonical schemas and explicit producer, satisfaction-mode, purpose, and exact-consumer binding. | Named files are insufficient when their origin, producing request, requirement, permitted preexistence, intended purpose, and admitted consumer are ambiguous. | Cross-Task, future-step, wrong-requirement, wrong-provenance, wrong-satisfaction-mode, purpose-incompatible, and wrong-consumer substitutions fail. |
| `D13` | Worker and command steps operate on the live target under admitted profiles, without a containment or complete-effect claim. | Live execution is required, but hidden effects cannot be classified exhaustively. | Declared outputs are verified; reported scope violations are persisted for Validator judgment; authoritative-state mutation and unresolved local activity fail mechanically; unreported effects remain explicitly unknown. |
| `D14` | An operation may launch at most once in one Run; there is no automatic retry after launch for any role. | Confirmed process termination does not prove absence of target, billing, logging, network, remote, or escaped-child effects. | A launch marker prevents every second launch; only a proven prelaunch state can be attempted later. |
| `D15` | Call return acceptance and local settlement are separate closed dimensions. | A rejected return, no return, and a process group that may still run have different consequences. | Every valid/invalid outcome combination is table-tested, and settlement makes no remote-effect claim. |
| `D16` | Validator judges bounded persisted evidence without interactive tools; `REPEAT` requires novel current-Round step evidence and is caller-mediated. | Validator-generated probes can become hidden execution and evidence theater. | Report prose, prior evidence, unchanged wrappers, Decline, and hard blockers cannot justify `REPEAT`. |
| `D17` | Child Tasks own distinct or narrower missions; a settled child `OPERATIONALLY_STOPPED` state may be audited by the parent, while unsettled child work blocks the Run. | Parent audit is useful after settled failure, but no semantic judgment may race a possibly active child operation. | Fixtures distinguish terminal nonsemantic child stop from unsettled/unknown child operation. |
| `D18` | Model context is bounded, reconstructible, role-specific, includes exact path-free policy capacity, and independent only to the degree observed. | Correctness must not depend on Lead memory or an unproved fresh context/model. | Persisted inputs reconstruct calls; actual isolation is `UNKNOWN` unless the host proves it. |
| `D19` | Prior-Run evidence is explicitly selected in `RootTaskSpec`, verified, frozen into the new Run before Task publication, advisory, and never merged as lifecycle state. | Boundary must not choose semantic history, an old report must not become current authority, and a current Run must not depend on later availability of another Run root. | Unselected, uncommitted, incompatible, unfrozen, externally rebound, or state-merging prior material is rejected. |
| `D20` | Explicit narrow resume rules complete uniquely determined transitions, including recorded validation-to-Round finalization, without replaying semantic work. | Crashes between child/parent, Round/Task, package/event, and start/launch boundaries otherwise strand safe work. | Each admitted crash window resumes deterministically; ambiguous launch remains non-resumable. |
| `D21` | Architecture owns requirements and warrants; implementation owns responsibilities and one canonical executable scenario catalog. | Repeating semantic rules and test lists in both plans creates competing truth. | Static checks reject duplicated normative architecture prose and orphaned scenario links. |
| `D22` | Every material design change carries a proposition-level lineage disposition and passes WELL plus RunSkeptic before readiness. | Stable IDs alone do not protect sub-contracts bundled inside a decision. | A change without `PRESERVE | CHANGE | REMOVE`, replacement protection, and checks cannot be promoted. |
| `D23` | Semantic-call and transport-launch cost remains structurally visible without making price data architecture authority. | Finite rounds can still hide expensive routing and repeated calls when expected and actual usage is not reported. | Run creation records structural upper bounds; status and terminal receipts report actual calls and launches by role/route/model/effort, with monetary estimates labelled external and advisory. |

The index is navigational, because implementation and review need stable links to authoritative architecture meaning.

The sections below are authoritative because qualifications and consequences cannot be compressed safely into one-line decisions.

---

## 5. Core model

### 5.1 Task

`Task` is the only recursive execution construct, because Task, Round, Attempt, and child identities need distinct continuation and replay rules.

A Task owns the following responsibilities, because Task, Round, Attempt, and child identities need distinct continuation and replay rules:

- one immutable mission;
- one immutable TaskAuthority;
- one immutable required-output contract;
- frozen Planner, Validator, Worker-route, and capability bindings;
- one append-only Task ledger;
- zero or more Rounds;
- optional child Tasks for distinct or narrower missions, because delegation and same-mission continuation need distinct identity and failure rules.

A newly published Task may have zero Rounds, because Task, Round, Attempt, and child identities need distinct continuation and replay rules.

Semantic execution begins only after Round 0 commits, so the architecture does not call the pre-Round crash state invalid, because Task, Round, Attempt, and child identities need distinct continuation and replay rules.

### 5.2 Round

A Round is one fresh semantic cycle, because Task, Round, Attempt, and child identities need distinct continuation and replay rules:

```text
same immutable Task mission, authority, outputs, and routes
+ selected verified evidence
+ fresh bounded workspace index
→ Planner
→ immutable PLAN or DECLINE
→ ordered immutable Plan steps, when present
→ Validator
→ FINISH or exceptional REPEAT
```

A repeated Round never reuses the previous Plan, step, child Task, provider request, or command launch, because mission judgment must remain separate from continuation and operational failure.

It receives current target observations and selected immutable evidence, because same-mission continuation must still replan against reality.

Round numbers are contiguous from zero, because a gap or duplicate would make the active Round ambiguous.

`maximum_tasks_per_run`, `maximum_rounds_per_task`, and `maximum_steps_per_round` are finite positive values frozen in `RootTaskSpec`; the Plan and child-creation boundaries enforce the finite policy, because finite policy must prevent unbounded work and keep resource use structurally visible.

The root Task counts as task 1, root depth is 0, Round 0 counts toward the per-Task Round limit, and every accepted Plan array element counts toward the per-Round step limit, because off-by-one policy interpretations would change authorized work.

The Validator request includes the remaining Round capacity, because mission judgment must remain separate from continuation and operational failure.

When no repeated Round remains available, Boundary supplies an exact Validator output schema that permits only `FINISH`; the frozen private contract explains the conditional rule, and a returned `REPEAT` is `RETURNED + REJECTED` and the settled Validator operation leaves the Task `OPERATIONALLY_STOPPED`, because Boundary must not coerce a semantic disposition after return.

### 5.3 Attempt and OperationRequest

`OperationRequest` is the immutable semantic request for one Planner, Worker, command, or Validator operation, because mission judgment must remain separate from continuation and operational failure.

It binds role, Task, Round, step where applicable, exact admitted inputs, contract identity, routing/capability profile, limits, and output schema, because independent implementations need one mechanically decidable contract.

`attempt.json` is an immutable Attempt identity binding, because Task, Round, Attempt, and child identities need distinct continuation and replay rules:

```text
attempt_id
operation_request_sha256
dispatch_id
adapter_identity
```

The Attempt directory grows only through predetermined create-only launch-marker, capture, and call-outcome records, because transport evidence must remain append-only.

The MVP permits at most one launched Attempt for an OperationRequest, because a second post-launch Attempt could replay hidden effects.

Attempt identity binds transport evidence and does not create a retry mechanism, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

### 5.4 Child Task

A child Task is a new Task for a distinct or narrower mission, because delegation and same-mission continuation need distinct identity and failure rules.

Same-mission continuation remains inside the original Task through a repeated Round, because otherwise recursion and continuation become indistinguishable.

---

## 6. FINISH and exceptional REPEAT

`FINISH` ends the Task rather than declaring success or failure, because disposition determines whether execution continues while judgment determines whether the mission was satisfied.

`SATISFIED + FINISH` is a successful terminal result, because the Validator judged the mission satisfied and determined that no further Round is required.

`NOT_SATISFIED + FINISH` is a failed terminal result, because the Validator judged the mission unsatisfied and determined that another Round is not justified.

`INDETERMINATE + FINISH` is an inconclusive terminal result, because the available evidence cannot establish whether the mission was satisfied and another Round is not credibly useful.

`REPEAT` is a nonterminal disposition, because the Validator identified a concrete remaining gap that novel current-Round evidence gives a fresh Planner a credible opportunity to close.

A Validator returns one mission judgment, because mission judgment must remain separate from continuation and operational failure:

```text
SATISFIED
NOT_SATISFIED
INDETERMINATE
```

and one disposition, because mission judgment must remain separate from continuation and operational failure:

```text
FINISH
REPEAT
```

Valid combinations are, because mission judgment and continuation must remain independent, explicit, and finite:

```text
SATISFIED + FINISH
NOT_SATISFIED + FINISH
NOT_SATISFIED + REPEAT
INDETERMINATE + FINISH
INDETERMINATE + REPEAT
```

`REPEAT` means the current non-Decline Round produced novel eligible evidence that materially narrows a concrete remaining gap and gives a fresh Planner a credible better basis, because mission judgment must remain separate from continuation and operational failure.

It is exceptional because repeated activity is not progress.

Use `FINISH + NOT_SATISFIED` for far failure, hard authority or dependency blockers, no useful leverage, or likely futility, because mission judgment must remain separate from continuation and operational failure.

Use `FINISH + INDETERMINATE` when the facts cannot establish the mission and another permitted Round is not credibly useful, because mission judgment must remain separate from continuation and operational failure.

`SATISFIED + REPEAT`, a Decline Round with `REPEAT`, or `REPEAT` beyond the finite Round cap is invalid, because mission judgment must remain separate from continuation and operational failure.

---

## 7. Explicit non-goals

The MVP does not provide, because the MVP must not imply protection that it cannot enforce:

- concurrency, parallel Task execution, distributed scheduling, or target-wide writer exclusion;
- a general workflow language or dynamic editing of an accepted Plan;
- automatic retry or replay after any outer operation may have launched;
- automatic model escalation, semantic repair loop, or hidden internal Round loop;
- automatic Git commit, staging, push, merge, rebase, or publication;
- automatic rollback, target restoration, or multi-resource transaction;
- filesystem, process, credential, network, service, remote, or hostile-code containment;
- complete effect detection or proof that a Worker report is exhaustive;
- proof that differently worded child missions are semantically distinct;
- proof that Validator reasoning or `REPEAT` materiality is correct;
- recovery of the same Run after an ambiguous launched-operation crash;
- compatibility with archived Target Task runtimes;
- RunSkeptic as part of STT runtime execution, because the MVP must not imply protections or automation that it cannot enforce safely.

The explicit non-goals are part of the design boundary because careful evidence handling must not imply protections STT cannot deliver.

---

## 8. Locations, supported host, and frozen runtime

### 8.1 Disjoint locations

STT uses four logical locations, because controller and evidence integrity depend on verified locations, host primitives, and a frozen runtime.

Source and target may be the same admitted directory for self-modification; otherwise neither may be an ancestor or descendant of the other, because partial overlap makes runtime-copy and target-mutation boundaries ambiguous.

The authoritative Run root and every exchange root must be disjoint from each other and from both source and target, because controller and evidence integrity depend on verified disjoint locations and supported host primitives:

1. **source repository** — supplies the runtime copied during Bootstrap and is resolved mechanically from the canonical active `scripts/stt.py` path plus the maintained runtime-manifest root; Bootstrap fails before publication when that source root is not unique or cannot be verified, and no semantic input or CLI flag may replace it;
2. **target workspace** — the live plain directory or Git repository the mission concerns and may equal source;
3. **authoritative Run root** — contains frozen runtime and lifecycle state;
4. **per-call exchange root** — contains disposable non-authoritative copies exposed to one lower-trust process, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

A normal Run root is `${TMPDIR:-/tmp}/stt/<run-id>/`, because controller and evidence integrity depend on verified disjoint locations and supported host primitives.

It must be outside source and target, because controller and evidence integrity depend on verified locations, host primitives, and a frozen runtime.

Run and exchange roots use owner-exclusive access control where the supported host exposes it, because controller and evidence integrity depend on verified disjoint locations and supported host primitives.

Exchange roots must be outside the authoritative Run root and target, because controller and evidence integrity depend on verified disjoint locations and supported host primitives.

Authoritative STT state never lives under `<target>/.stt/`, because target cleanup or self-modification must not rewrite lifecycle evidence.

STT does not prune Run roots automatically, because controller and evidence integrity depend on verified disjoint locations and supported host primitives.

The caller or host owns retention and deletion after it no longer needs resume or evidence; status and terminal output warn that deleting the temporary Run root permanently ends same-Run resume, because controller and evidence integrity depend on verified disjoint locations and supported host primitives.

An implementation may accept an explicit Run-root parent, but it may not silently convert temporary evidence into archival durability, because controller and evidence integrity depend on verified locations, host primitives, and a frozen runtime.

### 8.2 Supported-host capability floor

The MVP accepts only the frozen host profile `LOCAL_MVP_V1`, because controller and evidence integrity depend on verified disjoint locations and supported host primitives.

RootTaskSpec names that profile for identity binding but cannot weaken its floor; any additional profile requires an architecture change and qualification, because root semantics and host assumptions must be frozen before semantic execution.

Before Run publication, Bootstrap must establish the following capabilities, because root semantics and host assumptions must be frozen before semantic execution:

- owner-only directory creation where the host supports permissions;
- same-parent atomic rename for Task and transition-package publication;
- create-only regular-file publication;
- file flush and reread verification;
- directory sync and recorded durability observations sufficient for `LOCAL_MVP_V1`, without claiming universal power-loss durability;
- an exclusive local writer-lock primitive;
- `lstat`-style path observation without symlink following;
- stable regular-file byte hashing;
- process launch without shell interpolation;
- process-group termination and local-settlement observation adequate for the chosen adapter;
- a local filesystem behavior compatible with these operations, because controller and evidence integrity depend on verified locations, host primitives, and a frozen runtime.

The Run fails before lifecycle publication when a required primitive is unavailable, because controller and evidence integrity depend on verified locations, host primitives, and a frozen runtime.

Non-local filesystems and advisory-lock semantics are unsupported by `LOCAL_MVP_V1` unless the adapter proves behavior equivalent to every fixed floor item, because the MVP must not imply protection that it cannot enforce.

Power-loss durability is not claimed by the MVP, because the MVP must not imply protection that it cannot enforce.

The architecture does not postpone this feasibility decision to implementation, because controller and evidence integrity depend on verified locations, host primitives, and a frozen runtime.

### 8.3 Frozen runtime

Bootstrap copies an explicit maintained runtime manifest, not a directory-wide or import-discovered guess, because root semantics and host assumptions must be frozen before semantic execution.

The manifest lists exact code, private role contracts, provider adapters, data files, and package initializers required by the active entry point, because controller and evidence integrity depend on verified locations, host primitives, and a frozen runtime.

Bootstrap rejects symlinks and special files, records path/size/SHA-256/normalized executable mode, verifies the copy, re-observes source identities to reject a mixed generation, and re-executes only from `<run-root>/runtime/`, because path admission must not escape the target or reach control-state locations.

Tests must prove import and runtime-data closure and reject archive or unrelated-package reachability, because the design claim must remain executable and falsifiable.

Dynamic imports or data dependencies absent from the maintained manifest are architecture violations rather than runtime surprises, because controller and evidence integrity depend on verified locations, host primitives, and a frozen runtime.

The frozen runtime protects ordinary self-modification, because controller and evidence integrity depend on verified disjoint locations and supported host primitives.

It does not prevent a same-user hostile process from searching the filesystem or attacking the controller, because the MVP must not imply protection that it cannot enforce.

---

## 9. Run identity and routing

`run.json` binds the following fields, because resume must reconstruct the exact frozen execution context without inventing actual routing facts:

- Run ID;
- exact `RootTaskSpec` identity;
- source, target, and observed target-root identity;
- runtime-manifest identity;
- routing identity;
- live-provider authorization;
- finite Task-depth, total-Task, per-Task Round, and per-Round step limits;
- capture and wait limits;
- mandatory structural semantic-call and transport-launch upper bounds;
- supported-host observations;
- optional prior-Run root identity, because current lifecycle evidence must not depend on mutable or ambient history.

Target-root identity is distinct from target contents, because controller and evidence integrity depend on verified disjoint locations and supported host primitives.

Where supported it includes canonical path plus stable filesystem identity such as device/inode or equivalent, because Boundary can safely bind and reverify only the artifact forms admitted by the MVP.

If replacement of the admitted root cannot be detected with the required confidence, Bootstrap fails closed or records the host as unsupported; a same-path replacement must not be silently accepted, because root semantics and host assumptions must be frozen before semantic execution.

Routing binds the following fields, because resume must reconstruct the exact frozen execution context without inventing actual routing facts:

- one Planner route;
- named Worker routes, each with a capability profile;
- one Validator route;
- named command profiles;
- provider, requested model, requested effort, adapter, executable policy, and observable isolation properties, because resume must reconstruct the exact frozen execution context without inventing actual routing facts.

Requested routing is not actual routing, because resume must reconstruct the exact frozen execution context without inventing actual routing facts.

Omitted model or effort is `UNSPECIFIED`; unobservable actual provider/model/effort/context isolation is `UNKNOWN`, because resume must reconstruct the exact frozen execution context without inventing actual routing facts.

Live routes require frozen explicit authorization, because resume must reconstruct the exact frozen execution context without inventing actual routing facts.

Resume cannot add or remove authorization or change a route, because resume must reconstruct the exact frozen execution context without inventing actual routing facts.

Each provider adapter owns a minimal fixed allowlist of inherited credential/environment names needed to launch it; only names and availability observations are persisted, never values, because persisted requests must not acquire or disclose undeclared host credentials.

---

## 10. TaskAuthority and capability profiles

`RootAuthoritySpec` governs the grants supplied before Bootstrap, because root semantics and host assumptions must be frozen before semantic execution.

Bootstrap combines `RootAuthoritySpec` with the resolved target identity to create immutable runtime `TaskAuthority`, because target identity is not available before Bootstrap.

`TaskAuthority` governs what STT may admit into requests, because semantic roles must not acquire hidden path, process, environment, credential, or effect authority.

`TaskAuthority` does not prove what an arbitrary launched process actually does, because semantic roles must not acquire hidden path, process, environment, credential, or effect authority.

Canonical RootAuthoritySpec contains the following fields, because semantic roles must not acquire hidden path, process, environment, credential, or effect authority:

```text
read_scopes
write_responsibility_scopes
allowed_step_kinds
allowed_worker_routes
allowed_command_profiles
allowed_inherited_env_names
allowed_external_effect_classes
```

Runtime TaskAuthority adds the exact resolved `target_root_identity` and the RootAuthoritySpec identity, because semantic roles must not acquire hidden path, process, environment, credential, or effect authority.

`ChildAuthoritySpec` has the same relative grant fields as RootAuthoritySpec and contains no resolved target identity, because independent implementations need one mechanically decidable contract.

A TaskStep may declare only ChildAuthoritySpec; Boundary validates it as a subset of the parent TaskAuthority and combines it with the unchanged parent target identity to construct the child TaskAuthority, because Planner cannot manufacture hidden host identity fields.

`TaskAuthorityView` is the only authority representation exposed to Planner or Validator, because mission judgment must remain separate from continuation and operational failure:

```text
task_authority_sha256
read_scopes
write_responsibility_scopes
allowed_step_kinds
allowed_worker_routes
allowed_command_profiles
allowed_external_effect_classes
```

`CapabilityProfileView` is the only profile representation exposed to Planner or Validator, because mission judgment must remain separate from continuation and operational failure.

It contains profile name, Worker or command kind, relative responsibility/cwd scopes, declared effect classes, command slot names/kinds/bounds where applicable, wait bounds, and a concise caller-authored purpose description, because live execution requires admitted profiles and truthful evidence without a containment claim.

It omits resolved executable paths, adapter argv, inherited environment names, credential names, and provider launch details, because persisted requests must not acquire or disclose undeclared host credentials.

`WorkerRouteView` exposes only, because live execution requires admitted profiles and truthful evidence without a containment claim:

```text
worker_route
capability_profile_name
```

Boundary derives WorkerRouteView from frozen routing and supplies only admitted routes, because Planner must know the unique route-to-profile relation without receiving provider, model, adapter, executable, credential, or host-location metadata.

`task_authority_sha256` already binds the hidden resolved target identity, so the view carries no second target token, because semantic roles must not acquire hidden path, process, environment, credential, or effect authority.

Boundary and Worker retain full TaskAuthority and full profiles where target or launch access is required; Planner and Validator receive TaskAuthorityView plus CapabilityProfileView, because semantic role selection needs relative capabilities without disclosing authoritative host locations or credential-launch metadata.

The closed external-effect classes are, because semantic roles must not acquire hidden path, process, environment, credential, or effect authority:

```text
TARGET_READ
TARGET_WRITE
LOCAL_PROCESS
NETWORK_READ
NETWORK_WRITE
REMOTE_MUTATION
```

A Worker capability profile binds the following fields, because live execution requires admitted profiles and truthful evidence without a containment claim:

```text
profile_name
purpose
allowed_effect_classes
allowed_inherited_env_names
```

Routing binds each named Worker route to exactly one Worker capability profile, because repeating the route inside the profile would create a second route-to-profile authority source.

Provider-specific internal tool configuration belongs to the frozen Worker route and adapter identity rather than TaskAuthority, because STT cannot give one portable semantic meaning to proprietary tool-mode labels.

A command profile binds the following fields, because semantic roles must not acquire hidden path, process, environment, credential, or effect authority:

```text
profile_name
purpose
executable_resolution_policy
argv_template
argument_slots
cwd_scopes
accepted_exit_codes
environment_overrides
allowed_inherited_env_names
allowed_effect_classes
wait_and_termination_policy
```

`accepted_exit_codes` is one finite nonempty set of integers. `environment_overrides` is one bounded fixed name/value map frozen before Run publication; the Plan cannot add or replace environment entries, because finite policy must prevent unbounded work and keep resource use structurally visible.

A command profile may choose a shorter wait or termination grace than RootTaskSpec, but it cannot exceed `wait_limits.command_seconds` or `wait_limits.termination_grace_seconds`, because finite policy must prevent unbounded work and keep resource use structurally visible.

Each `argv_template` is an array of fixed tokens and single-token named slots, because semantic roles must not acquire hidden path, process, environment, credential, or effect authority.

The closed slot kinds are, because independent implementations need one mechanically decidable contract:

```text
TARGET_PATH
EXCHANGE_INPUT_PATH
EXCHANGE_OUTPUT_PATH
LITERAL_ENUM
INTEGER_RANGE
BOUNDED_TEXT
```

The closed executable-resolution policies are `EXACT_PATH` and `PATH_LOOKUP_AT_BOOTSTRAP`, because root semantics and host assumptions must be frozen before semantic execution.

`EXACT_PATH` binds one canonical executable regular file; `PATH_LOOKUP_AT_BOOTSTRAP` resolves one executable name before Run publication through the admitted minimal environment, records the resolved path and identity, and uses that exact reverified executable for every launch, because root semantics and host assumptions must be frozen before semantic execution.

Each slot definition carries a stable slot name and its static mechanical bound: admitted target scope for `TARGET_PATH`, an explicit value set for `LITERAL_ENUM`, inclusive minimum and maximum for `INTEGER_RANGE`, and a maximum UTF-8 byte length for `BOUNDED_TEXT`, because finite policy must prevent unbounded work and keep resource use structurally visible.

Exchange slot definitions declare only whether they accept an admitted input or declared output, because a reusable profile exists before any runtime InputRef or OutputRequirement identity.

A CommandStep binds each slot exactly once, because live execution requires admitted profiles and truthful evidence without a containment claim.

`TARGET_PATH` binds one target-relative path; `EXCHANGE_INPUT_PATH` binds one of that step’s uniquely named PlanInputs; `EXCHANGE_OUTPUT_PATH` binds one of that step’s RUN plus `BOUNDARY_ASSIGNED` OutputRequirement IDs; scalar slots bind one admitted value, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Boundary resolves exchange bindings only after exact InputRefs and Boundary-assigned output locations exist, validates every supplied value, and renders one exact argv array without shell interpolation, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

No slot expands into multiple tokens, because semantic roles must not acquire hidden path, process, environment, credential, or effect authority.

A Worker route or command profile declares the effect classes and environment names it may request, because live execution requires admitted profiles and truthful evidence without a containment claim.

This declaration is an admission and audit contract, not a containment guarantee; STT validates the supported template but does not classify hidden behavior of the executable, because the MVP must not imply protection that it cannot enforce.

Routing, RootTaskSpec, Plan, argv, explicit environment overrides, prompts, and persisted requests must not intentionally contain credential or secret values, because persisted requests must not acquire or disclose undeclared host credentials.

Fixed explicit environment overrides carry a caller/host assertion that each value is non-secret, because persisted requests must not acquire or disclose undeclared host credentials.

A model-supplied `BOUNDED_TEXT` value carries no mechanically trusted non-secret claim; it is merely size-bounded, and profile authors must not use such a slot where argv exposure would be unacceptable, because persisted requests must not acquire or disclose undeclared host credentials.

STT can enforce field placement, length, inherited-name allowlists, and rejection of known prohibited credential fields, but it cannot prove that arbitrary text is not secret, because persisted requests must not acquire or disclose undeclared host credentials.

Inherited environment values are admitted by name, supplied only at launch, and never persisted or hashed, because persisted requests must not acquire or disclose undeclared host credentials.

STT cannot guarantee that an arbitrary provider, command, stdout, stderr, or returned artifact will not disclose a secret it can access, because persisted requests must not acquire or disclose undeclared host credentials.

Path scopes use canonical target-relative component-aware rules, because path admission must not escape the target or reach control-state locations.

Absolute paths, traversal, symlink components or leaves, special files, `.git`, authoritative Run paths, exchange-to-Run traversal, and containment escapes are rejected as semantic target paths, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

Child authority must be a mechanical subset in every field, because delegation and same-mission continuation need distinct identity and failure rules.

A child cannot add a path scope, step kind, Worker route, command profile, inherited environment name, or effect class, because live execution requires admitted profiles and truthful evidence without a containment claim.

Every selected Worker or command profile must itself be a subset of TaskAuthority effect classes and environment names, because live execution requires admitted profiles and truthful evidence without a containment claim.

The Planner may select only profiles already admitted by TaskAuthority, because planning must remain immutable, bounded, and unable to redefine runtime authority.

Arbitrary executable paths, free-form argv arrays, or inherited environment names are not Plan data; executable identity and argv structure must be defined by an admitted command profile, because persisted commands must not request credentials or new host authority by name.

When a Worker reports an effect outside its declared responsibility scope, Boundary records the exact reported observation as a scope violation, because reported effects are evidence for the final mission judgment rather than mechanically decisive by themselves.

The accepted step outcome remains governed by the verified Worker result, because a reported scope violation may be a reportable qualification rather than a reason to stop the sealed Plan.

The Validator may treat the violation as a footnote, a reason for `FINISH + NOT_SATISFIED`, or a concrete closable gap supporting `REPEAT`, because the Validator owns mission judgment.

The Run becomes `INVALID` when the reported effect mutated authoritative STT state, because trustworthy lifecycle evidence has then been compromised.

The Run becomes `OPERATIONALLY_BLOCKED` when the reported effect creates unresolved local activity, because later semantic validation cannot safely proceed while local work may remain active.

STT does not claim to detect unreported effects, because cooperative reporting is not complete effect observation.

The target is not exclusively locked, because semantic roles must not acquire hidden path, process, environment, credential, or effect authority.

Every STT-named TARGET ArtifactRef, PlanInputResolution, command path, and output is identity-checked at its Boundary use; concurrent target change produces a visible mismatch or indeterminate observation rather than silent rebinding, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Opaque Worker reads performed directly inside the admitted live target remain cooperative and are not claimed to be exhaustively observed, because live execution requires admitted profiles and truthful evidence without a containment claim.

---

## 11. STT-private role contracts and instruction trust

The frozen runtime contains private contracts, because controller and evidence integrity depend on verified disjoint locations and supported host primitives:

```text
concepts/stt/contracts/planner.md
concepts/stt/contracts/worker.md
concepts/stt/contracts/validator.md
```

General repository contracts under `agents/`, `workflows/`, or archived Target Task material do not govern STT runtime unless this architecture explicitly imports a rule, because target and prior content must remain data rather than acquire control authority.

This boundary is required because otherwise an unrelated instruction update can change a frozen lifecycle implicitly.

Instruction precedence is defined as follows, because target and prior content must not acquire control authority:

```text
frozen STT runtime and private role contract
→ immutable RootTaskSpec / Task mission / TaskAuthority / routing / policy
→ accepted Plan step for the current role
→ verified evidence and target content as untrusted data
```

Target files, command output, Worker reports, prior-Run reports, and retrieved text can contain apparent instructions, but they cannot change mission, authority, routing, policy, role contract, lifecycle state, or output schema, because live execution requires admitted profiles and truthful evidence without a containment claim.

Provider prompts must label them as data, and qualification must include adversarial instruction-injection fixtures, because target and prior content must not acquire control authority.

---

## 12. Task and Round identity

### 12.1 Task publication

Each Task is atomically published with, because resume and lineage require immutable and uniquely bound Task and Round identities:

- `task.json`;
- exact `mission.md`;
- structured required-output contract;
- initial Task-scoped `EvidenceBinding` values;
- private role/routing references;
- empty predetermined directories;
- one valid `TASK_CREATED` ledger event, because resume and lineage require immutable and uniquely bound Task and Round identities.

The root Task derives these fields mechanically from resolved RootTaskSpec selectors, the resolved target identity, and the verified routing file, because independent implementations need one mechanically decidable contract.

A child derives them from one accepted TaskStep, because delegation and same-mission continuation need distinct identity and failure rules.

Task identity binds Run, parent relation, mission, authority, required outputs, initial inputs, routes, depth, and policy identities, because resume and lineage require immutable and uniquely bound Task and Round identities.

Mission prose does not redefine the structured output contract, because resume and lineage require immutable and uniquely bound Task and Round identities.

### 12.2 Round identity

Each Round lives at `rounds/<contiguous-number>/` and binds the following fields, because resume and lineage require immutable and uniquely bound Task and Round identities:

- Task identity and number;
- mission, authority, required-output, runtime, routing, and policy identities;
- fresh workspace-index identity;
- selected input evidence;
- predecessor Round and Validator report when repeated;
- selected eligible repeat evidence when repeated, because mission judgment must remain separate from continuation and operational failure.

A Round directory is an immutable identity container whose predetermined child locations receive create-only transition packages, because delegation and same-mission continuation need distinct identity and failure rules.

“Immutable Round” therefore means no accepted identity or payload is replaced, not that the directory remains byte-for-byte empty after publication, because Boundary can safely bind and reverify only the artifact forms admitted by the MVP.

---

## 13. PlanInput, EvidenceBinding, InputRef, and Plan identity

RootTaskSpec contains selectors rather than runtime references, because root semantics and host assumptions must be frozen before semantic execution:

```text
InitialInputSelector:
  kind: TARGET_PATH | BOOTSTRAP_FILE
  name
  purpose
  relative_path
  expected_artifact_type

PriorEvidenceSelector:
  name
  purpose
  prior_committed_reference
  expected_artifact_type
```

`TARGET_PATH` is relative to the admitted target root, because artifact availability, resolution, and consumption must not be silently rebound or fabricated.

`BOOTSTRAP_FILE` is relative to the canonical parent directory of the `--task-spec` file; Bootstrap rejects absolute paths, traversal, symlinks, special files, `.git`, and escape from that directory, because otherwise a selector could introduce an unbounded second input root.

Bootstrap resolves initial target and Bootstrap selectors by freezing their bytes into Boundary-owned current-Run ArtifactRefs before Task publication, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Bootstrap also verifies each selected committed prior-Run reference and copies its exact bytes plus origin metadata into a Boundary-owned current-Run ArtifactRef before Task publication, because current lifecycle evidence must not depend on the later availability or mutability of another Run root.

`EvidenceBinding` records that an artifact is available to one Task or Round without authorizing a consumption, because resume and substitution checks require exact facts to remain uniquely bound:

```text
binding_id
kind: TASK_INITIAL | PRIOR_RUN | CHILD_INITIAL | ROUND_REPEAT
name
source_identity
artifact_ref
purpose
owner_task
owner_round   # required only for ROUND_REPEAT
```

A root or child Task is published with Task-scoped bindings; a repeated Round is published with Round-scoped repeat bindings, because mission judgment must remain separate from continuation and operational failure.

A binding is not an `InputRef`, because the exact Round and consuming role may not exist when the binding is created.

Planner receives only a path-free `EvidenceBindingView` for each binding available to the current Round, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access:

```text
binding_id
kind
name
artifact_ref_sha256
artifact_type
purpose
owner_task
owner_round
```

EvidenceBindingView omits the full ArtifactRef, source path, and host observation, because resume and substitution checks require exact facts to remain uniquely bound.

It exists so Planner can name `source_binding_id` without receiving authoritative control objects, because planning must remain immutable, bounded, and unable to redefine runtime authority.

A Planner declares step dependencies through non-authoritative `PlanInput` values, because planning must remain immutable, bounded, and unable to redefine runtime authority:

```text
kind: EVIDENCE_BINDING | TARGET_PATH | STEP_OUTPUT
name
expected_purpose
source_binding_id          # EVIDENCE_BINDING
relative_path              # TARGET_PATH
expected_artifact_type     # TARGET_PATH
source_step_id             # STEP_OUTPUT
source_requirement_id      # STEP_OUTPUT
```

`EVIDENCE_BINDING` must name a binding available to the current Round, because artifact availability, resolution, and consumption must not be silently rebound or fabricated.

`TARGET_PATH` must be inside read authority, because artifact availability, resolution, and consumption must not be silently rebound or fabricated.

`STEP_OUTPUT` must name an earlier step and one of that step’s declared OutputRequirements; it never contains a not-yet-existing ArtifactRef, because resume and substitution checks require exact facts to remain uniquely bound.

Planner output cannot create an ArtifactRef, EvidenceBinding, PlanInputResolution, or authoritative InputRef, because planning must remain immutable, bounded, and unable to redefine runtime authority.

When accepting a Plan, Boundary publishes one immutable `PlanInputResolution` for each PlanInput, because trusted lifecycle mutation must remain centralized and mechanically verifiable:

```text
resolution_id
plan_input_identity
kind: RESOLVED_ARTIFACT | DEFERRED_STEP_OUTPUT
source_identity
artifact_ref                 # RESOLVED_ARTIFACT only
source_step_id               # DEFERRED_STEP_OUTPUT only
source_requirement_id        # DEFERRED_STEP_OUTPUT only
resolution_observation
```

Evidence bindings and target paths use `RESOLVED_ARTIFACT`; target paths resolve to current TARGET ArtifactRefs with exact byte identity, because resume and substitution checks require exact facts to remain uniquely bound.

Prior-step outputs use `DEFERRED_STEP_OUTPUT` until the named earlier step commits the named requirement, because artifact availability, resolution, and consumption must not be silently rebound or fabricated.

Before the consuming outer launch, Boundary resolves any deferred requirement, reverifies every resolved ArtifactRef, and creates the exact consumer InputRef, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

A named target input mismatch or disappearance before launch returns transient `PRELAUNCH_BLOCKED` and never silently rebinds the Plan, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

Every actual consumption then creates a new admitted `InputRef` with the closed schema, because resume and substitution checks require exact facts to remain uniquely bound:

```text
kind: TASK_INITIAL | PRIOR_RUN | TARGET | STEP_OUTPUT | CHILD_OUTPUT | ROUND_EVIDENCE
name
source_identity
artifact_ref
expected_purpose
consumer_role: PLANNER | WORKER | COMMAND | TASK_STEP | VALIDATOR
consumer_task
consumer_round
consumer_step   # required for WORKER, COMMAND, and TASK_STEP; null otherwise
```

Boundary rejects an InputRef whose consumer identity is incomplete, whose source is unavailable to that Task/Round, or whose purpose and requirement constraints do not admit that exact consumption, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Child Task publication creates new child-scoped EvidenceBindings from the parent TaskStep’s admitted InputRefs rather than reusing parent-consumer InputRefs, because delegation and same-mission continuation need distinct identity and failure rules.

A Plan contains an identity header, because artifact availability, resolution, and consumption must not be silently rebound or fabricated:

```text
schema
task_id
round_id
mission_sha256
authority_sha256
required_outputs_sha256
runtime_manifest_sha256
routing_sha256
planner_request_sha256
intent
steps
```

Exactly three step kinds exist, because artifact availability, resolution, and consumption must not be silently rebound or fabricated:

```text
worker
command
task
```

Common step fields are, because independent implementations need one mechanically decidable contract:

```text
id
kind
description
inputs: PlanInput[]
output_requirements: OutputRequirement[]
declared_read_scopes
declared_write_responsibility_scopes
```

A WorkerStep additionally binds the following fields, because live execution requires admitted profiles and truthful evidence without a containment claim:

```text
worker_route
instructions
```

The Worker capability profile is derived uniquely from the frozen routing binding for `worker_route`; the Plan cannot name a second profile, because live execution requires admitted profiles and truthful evidence without a containment claim.

A CommandStep additionally binds the following fields, because live execution requires admitted profiles and truthful evidence without a containment claim:

```text
command_profile
cwd
argument_values
```

`cwd` is target-relative and must be admitted by the selected profile’s `cwd_scopes`, because artifact availability, resolution, and consumption must not be silently rebound or fabricated.

A TaskStep additionally binds the following fields, because artifact availability, resolution, and consumption must not be silently rebound or fabricated:

```text
child_mission
mission_relation_reason
child_authority_spec: ChildAuthoritySpec
required_child_outputs
```

Child Worker routes and command profiles are the subsets declared inside `child_authority_spec`; no parallel child-route field exists, because live execution requires admitted profiles and truthful evidence without a containment claim.

Plan validation rejects future references, cross-Task substitution, duplicate step IDs, duplicate input names within a step, duplicate output requirement IDs or names, step count beyond policy, authority expansion, unknown routes/profiles, unknown schemas, fabricated authoritative references, and any identity mismatch, because planning must remain immutable, bounded, and unable to redefine runtime authority.

Boundary owns PlanInputResolution publication and later exact-consumer InputRef construction, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Plan validation checks structure and admission, not semantic wisdom, because planning must remain immutable, bounded, and unable to redefine runtime authority.

There is no generic `success` expression or stdout-regex evaluator, because local judgment and output matching already own success semantics.

---

## 14. OutputRequirement, ArtifactRef, and role results

### 14.1 OutputRequirement

`OutputRequirement` defines what must be satisfied, because resume and substitution checks require exact facts to remain uniquely bound:

```text
requirement_id
name
purpose
artifact_type
location: TARGET | RUN
path_policy: EXACT | BOUNDARY_ASSIGNED
relative_path   # required for EXACT
mode_requirement: ANY | EXECUTABLE | NON_EXECUTABLE
satisfaction_mode:
  EXISTING_ALLOWED | PRODUCED_IN_TASK | PRODUCED_BY_STEP
producer_constraint
principal_consumer
```

`artifact_type` is a stable restricted identifier compared by exact equality; the MVP does not load a type plugin or infer semantic content from that label. `producer_constraint` is `NONE` for `EXISTING_ALLOWED`, `CURRENT_TASK_TREE` for `PRODUCED_IN_TASK`, or `EXACT_STEP(step_id)` for `PRODUCED_BY_STEP`, because producer admission must be mechanically decidable rather than inferred from prose.

`purpose` is one stable restricted identifier declared by the selector or requirement, and purpose compatibility is exact identifier equality. `principal_consumer` is one structured intended-use label: `TASK_TERMINAL`, `VALIDATOR`, `NEXT_ROUND_PLANNER`, or `STEP(step_id)`, because mission judgment must remain separate from continuation and operational failure.

Plan validation checks structural compatibility: `TASK_TERMINAL` is allowed only on a Task terminal requirement, `STEP(step_id)` must name a later admitted step that references the requirement, and `NEXT_ROUND_PLANNER` must name an output form that can be frozen as repeat evidence, because mission judgment must remain separate from continuation and operational failure.

The label does not force that lifecycle use to occur and does not authorize consumption; every actual use still requires its own admitted InputRef, so early FINISH does not invalidate an otherwise satisfied output merely because its intended downstream use was unnecessary.

`EXISTING_ALLOWED` is valid only for a Task-level exact TARGET requirement inside read authority; it permits zero-step satisfaction without granting write authority, because success and evidence must be mechanically bound to producer, purpose, requirement, and consumer.

`PRODUCED_IN_TASK` requires a Task-tree producer and, for TARGET output, a path inside Task write-responsibility authority, because success and evidence must be mechanically bound to producer, purpose, requirement, and consumer.

Step requirements use `PRODUCED_BY_STEP`; TARGET outputs must be inside the step write-responsibility scope, while RUN outputs are Boundary-assigned imports from the current exchange or deterministic observation, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

`BOUNDARY_ASSIGNED` is allowed only for RUN artifacts whose authoritative path Boundary assigns while importing verified bytes from exchange or deterministic observation, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

A Task, step, or command is not satisfied until every requirement is matched by one verified ArtifactRef with the permitted producer, satisfaction mode, and consumer binding, because resume and substitution checks require exact facts to remain uniquely bound.

### 14.2 ArtifactRef

`ArtifactRef` defines what Boundary observed, because trusted lifecycle mutation must remain centralized and mechanically verifiable:

```text
artifact_id
name
artifact_type
location: TARGET | RUN
relative_path
sha256
byte_size
normalized_mode
provenance
requirement_id
purpose
source_observation
```

`provenance` is a closed discriminated value, because resume and substitution checks require exact facts to remain uniquely bound:

```text
BOOTSTRAP_INPUT(selector_identity)
PRIOR_RUN_IMPORT(prior_run_identity, prior_artifact_identity, import_observation)
EXISTING_TARGET(observation_identity, requirement_identity)
STEP_OUTPUT(operation_request_sha256, task, round, step)
CHILD_OUTPUT(child_task, child_result_identity)
COMMAND_OBSERVATION(operation_request_sha256, task, round, step)
BOUNDARY_OBSERVATION(observation_identity)
```

Only provenance fields required by the selected kind are present, because a preexisting input, existing target output, or imported prior artifact has no current step producer and must not be assigned a fabricated OperationRequest. `requirement_id` is null for selector-derived inputs and observations that do not satisfy an OutputRequirement.

ArtifactRef `purpose` is copied exactly from the selector or matched OutputRequirement; it is not an authorization grant or an exclusive consumer identity, because resume and substitution checks require exact facts to remain uniquely bound.

Every actual use requires a new admitted `InputRef` whose exact role, Task, Round, and step where applicable bind that consumption, because resume and substitution checks require exact facts to remain uniquely bound.

Boundary rejects a use when InputRef `expected_purpose` does not equal ArtifactRef `purpose` or the exact consumer is not otherwise admitted; Plan validation separately checks that the OutputRequirement `principal_consumer` label is structurally compatible with the declared intended use, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

TARGET references are regular files under admitted target paths and are reverified before each consumption, because success and evidence must be mechanically bound to producer, purpose, requirement, and consumer.

RUN references are Boundary-owned create-only imports under the authoritative Run root; semantic processes never write them directly, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Directories, symlinks, sockets, devices, and special-file outputs are unsupported, because path admission must not escape the target or reach control-state locations.

### 14.3 Role-result and StepResult binding

PlannerResult, WorkerResult, CommandResult, and ValidatorResult each bind exact OperationRequest, Task, Round, step where applicable, routing, schema, and raw-return identities, because resume and substitution checks require each role return and lifecycle result to remain exactly bound.

A syntactically valid result with the wrong binding is `RETURNED + REJECTED`, never an accepted semantic value, because return validity and local process settlement have different safety and recovery consequences.

`StepResult` is a Boundary-owned lifecycle result rather than a semantic-role return, because resume and substitution checks require each role return and lifecycle result to remain exactly bound:

```text
task
round
step
kind: OUTER_OPERATION | CHILD_TASK
operation_request           # OUTER_OPERATION only
child_result_or_stop         # CHILD_TASK only
call_outcome                 # OUTER_OPERATION only
accepted_role_result         # optional
outcome: StepOutcome
verified_outputs
observations
```

A Worker or command StepResult may exist without an accepted role result when a settled non-OK call maps mechanically to `INDETERMINATE` or `NOT_SATISFIED`, because resume and substitution checks require each role return and lifecycle result to remain exactly bound.

A TaskStep StepResult binds the exact child terminal result or settled stop evidence, because resume and substitution checks require each role return and lifecycle result to remain exactly bound.

`STEP_FINISHED` commits StepResult, so a local lifecycle outcome never requires fabricating WorkerResult, CommandResult, or child judgment, because resume and substitution checks require each role return and lifecycle result to remain exactly bound.

Artifact reuse occurs only by creating a new admitted `InputRef` for an explicit consumer and verifying exact purpose plus consumer admission; the OutputRequirement’s `principal_consumer` label is checked structurally during Plan validation rather than treated as runtime authority, because planning must remain immutable, bounded, and unable to redefine runtime authority.

A role never receives an artifact merely because it exists in the Run.

### 14.4 Path-free ArtifactRefView and bounded ArtifactView

Planner and Validator never receive a serialization of authoritative ArtifactRef or InputRef, because mission judgment must remain separate from continuation and operational failure.

Boundary supplies the SHA-256 identity of each admitted reference plus a path-free `ArtifactRefView`, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access:

```text
artifact_ref_sha256
artifact_id
name
artifact_type
location: TARGET | RUN
target_relative_path       # TARGET only, when admitted for that role
sha256
byte_size
normalized_mode
provenance_kind
semantic_producer_identity
requirement_id
purpose
```

ArtifactRefView omits authoritative RUN relative paths, canonical target roots, device/inode data, source-observation host locations, prior-root paths, and other launch/control metadata, because resume and substitution checks require exact facts to remain uniquely bound.

A role cannot use ArtifactRefView as authority; Boundary retains and reverifies the full ArtifactRef and InputRef, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Model requests carry bounded content views rather than granting file access, because finite policy must prevent unbounded work and keep resource use structurally visible:

```text
artifact_ref_sha256
artifact_ref_view
representation: FULL_BYTES | BOUNDED_TEXT | METADATA_ONLY
view_sha256
truncated
byte_range_or_metadata_policy
```

Boundary chooses the representation mechanically from artifact type, role contract, and frozen capture limits, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Range selection, truncation, and metadata extraction are deterministic; Boundary does not generate a semantic summary, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

A truncated or metadata-only view is labelled and cannot be treated as complete file evidence, because success and evidence must be mechanically bound to producer, purpose, requirement, and consumer.

Planner and Validator may receive full bounded bodies of exact admitted artifacts, step reports, and terminal outputs when limits permit; broad target bodies remain unavailable, because mission judgment must remain separate from continuation and operational failure.

---

## 15. Exchange isolation and context transport

Boundary constructs one disposable exchange root for each Worker or other lower-trust process call, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

It copies only admitted input bytes and request material into that root, invokes the process without an authoritative Run-root path in prompt, argv, environment, cwd, or supplied files, and imports accepted outputs by bytes after the process ends, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

Exchange files are non-authoritative, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

After every outer call and before accepting or importing its result, Boundary revalidates the frozen runtime identity, Run identity, target-root identity, current Task/Round/request identities, and the complete committed ledger prefix observed before launch, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Any mutation or conflicting append outside the current authorized transition makes the Run `INVALID`, because lower-trust calls must not receive or mutate authoritative control state.

Boundary verifies imported bytes against the returned manifest, publishes accepted bytes as create-only RUN artifacts, and performs best-effort exchange cleanup, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

A lower-trust process may still discover other filesystem locations under its operating-system authority, so exchange isolation detects many integrity violations without claiming hostile containment, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

Planner and Validator structured request metadata does not include full TaskAuthority, full profiles, full InputRef or ArtifactRef serializations, canonical target-root, device/inode, exchange-root, authoritative RUN relative paths, or authoritative Run-root paths, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

Admitted target files, reports, or logs may themselves contain path-like text; that text remains labelled untrusted data and is never promoted into host-location authority, because target and prior content must not acquire control authority.

The MVP defines no interactive Boundary tool callback for Planner or Validator, because interactive callbacks would introduce hidden execution after request publication.

A provider may have opaque host-side behavior that STT cannot observe; requested isolation is recorded, and actual isolation remains `UNKNOWN` unless the host proves it, because the MVP must not imply protection that it cannot enforce.

Worker provider-internal tools are part of one opaque outer Worker operation, because live execution requires admitted profiles and truthful evidence without a containment claim.

They are not hidden STT steps, do not create nested Boundary transitions, and are governed only by the Worker route’s declared capability profile plus the explicit no-containment limitation, because live execution requires admitted profiles and truthful evidence without a containment claim.

---

## 16. Planner contract

The Planner receives only the following inputs, because planning must remain immutable, bounded, and unable to redefine runtime authority:

- exact mission;
- RunPolicyView;
- TaskAuthorityView, admitted WorkerRouteViews, and CapabilityProfileViews;
- required-output contract;
- path-free EvidenceBindingViews, identities of exact admitted InputRefs, path-free ArtifactRefViews, and bounded bodies;
- a fresh workspace index;
- predecessor Validator report marked advisory when repeating;
- private Planner contract;
- exact Plan schema, because independent implementations need one mechanically decidable contract.

The Planner has no canonical target-root or host path, authoritative Run path, interactive tools, command execution, or state-writing capability in the STT contract, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

The Planner returns, because planning must remain immutable, bounded, and unable to redefine runtime authority:

```text
PLAN
DECLINE
```

### 16.1 PLAN

A Plan intent is defined as follows, because planning must remain bounded, reconstructible, immutable, and unable to mutate lifecycle authority:

```text
EXECUTE
INVESTIGATE
```

`EXECUTE` means current evidence supports a credible complete path, because planning must remain bounded, reconstructible, immutable, and unable to mutate lifecycle authority.

`INVESTIGATE` means one named decision-critical unknown blocks a credible complete path, but admitted bounded steps can produce evidence for a later Round, because finite policy must prevent unbounded work and keep resource use structurally visible.

An investigative Plan states the unknown, why it blocks execution, the bounded probe, and expected evidence outputs, because finite policy must prevent unbounded work and keep resource use structurally visible.

A zero-step Plan is valid when existing evidence may already establish the mission, because planning must remain bounded, reconstructible, immutable, and unable to mutate lifecycle authority.

### 16.2 DECLINE

`DECLINE` means no credible execution path or useful bounded investigation exists under current mission, authority, evidence, profiles, dependencies, and policy, because planning must remain immutable, bounded, and unable to redefine runtime authority.

It records reason, blocking facts, missing requirements, and why further admitted work is not useful, because planning must remain bounded, reconstructible, immutable, and unable to mutate lifecycle authority.

A Decline Round runs the Validator against current evidence and must `FINISH`, because mission judgment must remain separate from continuation and operational failure.

It cannot `REPEAT`, because repetition would contradict the Planner’s accepted claim that no useful bounded next path exists.

Changed authority, policy, mission, or dependency assumptions require a new Run, because the MVP should minimize supply and compatibility risk until a dependency proves a correctness benefit.

### 16.3 Planning persistence

The exact request, launch marker, raw return, call outcome, accepted PlannerResult when present, every Boundary-authored PlanInputResolution, and transition package are persisted, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

`PLANNING_FINISHED` commits the accepted Plan and its complete resolution set together; a missing, mismatched, or unresolvable current input makes the returned Plan `RETURNED + REJECTED` rather than publishing a partial Plan, because return validity and local process settlement have different safety and recovery consequences.

Same-Run resume never launches a second Planner Attempt after a launch marker exists, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

A settled Planner error, rejected return, or settled no-return proceeds to the current Validator with no Plan, because return validity and local process settlement have different safety and recovery consequences.

An unsettled or unknown local operation blocks the Run, because return validity and local process settlement have different safety and recovery consequences.

---

## 17. Worker and command steps

The closed `StepOutcome` vocabulary is `SATISFIED | NOT_SATISFIED | INDETERMINATE | OPERATIONAL_INDETERMINATE`, because live execution requires admitted profiles and truthful outcomes without a containment claim.

Worker and command steps may return only the first three values; `OPERATIONAL_INDETERMINATE` is reserved for a TaskStep whose child reached settled `OPERATIONALLY_STOPPED`, because operational absence of a child judgment must remain distinct from semantic uncertainty.

### 17.1 Worker

A Worker receives one accepted WorkerStep, admitted target root, exact exchange inputs, responsibility scopes, output requirements, and one admitted Worker route/capability profile, because live execution requires admitted profiles and truthful evidence without a containment claim.

A Worker may inspect and modify the live target, run tools or commands, and produce outputs, because live execution requires admitted profiles and truthful evidence without a containment claim.

It returns local judgment, summary, output manifest, best-effort effect report, verification, warnings, and unknowns, because mission judgment must remain separate from continuation and operational failure.

Boundary verifies declared outputs and reported scopes, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

The effect report is evidence, not complete observation, because reported effects are evidence for Validator judgment while integrity and unsettled activity remain mechanical blockers.

### 17.2 Command

A CommandStep selects one named admitted command profile and supplies only values for that profile’s typed argument slots, because live execution requires admitted profiles and truthful evidence without a containment claim.

The profile owns executable resolution, argv template, slot schemas, cwd scopes, accepted exit codes, fixed explicit environment overrides, allowed inherited environment names, effect classes, and termination method, because persisted requests must not acquire or disclose undeclared host credentials.

A Plan cannot introduce a different executable, free-form token sequence, extra slot, or secret environment value, because persisted requests must not acquire or disclose undeclared host credentials.

Boundary validates slots and renders the exact explicit argv array without shell interpretation, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

It records resolved executable observations where supported, bounded stdout/stderr, exit status, timing, launch, and local settlement, because return validity and local process settlement have different safety and recovery consequences.

Command local judgment is defined as follows, because mission judgment must remain separate from continuation and operational failure:

```text
accepted exit code + all output requirements matched
→ SATISFIED

returned unaccepted exit code or conclusively failed requirement
→ NOT_SATISFIED

no accepted settled return or unstable required output identity
→ INDETERMINATE
```

A nonzero exit is still `RETURNED + OK(CommandResult)`, because return validity and local process settlement have different safety and recovery consequences.

No command is automatically relaunched after its marker exists, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

---

## 18. Call outcome and local settlement

Every outer operation records two independent dimensions, because return validity and local process settlement have different safety and recovery consequences.

### 18.1 Return dimension

The following block records the section's closed structural notation, because return validity and local process settlement have different safety and recovery consequences.

```text
call_state: RETURNED | NO_RETURN
result_kind: NONE | OK | ERR | REJECTED
```

Valid meanings are, because return validity and local process settlement have different safety and recovery consequences:

| call_state | result_kind | Meaning |
|---|---|---|
| `RETURNED` | `OK` | A role-specific accepted value or command result returned. |
| `RETURNED` | `ERR` | An accepted structured error returned. |
| `RETURNED` | `REJECTED` | Bytes returned, but identity, size, truncation, schema, binding, authority, or role-specific mechanical acceptance failed. |
| `NO_RETURN` | `NONE` | Launch occurred, but no completed return was observed. |

Every other combination is invalid, because return validity and local process settlement have different safety and recovery consequences.

### 18.2 Local-settlement dimension

The following block records the section's closed structural notation, because return validity and local process settlement have different safety and recovery consequences.

```text
local_settlement: SETTLED | UNSETTLED | UNKNOWN
```

`SETTLED` means the adapter positively established that the observed outer process group and communication channel ended, because return validity and local process settlement have different safety and recovery consequences.

It does not prove that no remote request, billing event, log, daemon, escaped child, or external effect remains, because return validity and local process settlement have different safety and recovery consequences.

`UNSETTLED` means observed local work remains active, because return validity and local process settlement have different safety and recovery consequences.

`UNKNOWN` means the adapter cannot establish local settlement, because return validity and local process settlement have different safety and recovery consequences.

A persisted call outcome exists only after a launch marker, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

Valid settlement combinations are, because return validity and local process settlement have different safety and recovery consequences:

```text
RETURNED → SETTLED | UNSETTLED | UNKNOWN
NO_RETURN → SETTLED | UNSETTLED | UNKNOWN
```

Before launch, the authoritative fact is the committed OperationRequest plus absence of a launch marker; `PRELAUNCH_BLOCKED` is derived transiently from that fact rather than encoded as a duplicate `NOT_STARTED` call outcome, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

A returned value with unsettled or unknown local work is persisted as evidence but cannot be accepted into semantic lifecycle state until the settlement floor is satisfied, because return validity and local process settlement have different safety and recovery consequences.

Every other combination is invalid, because return validity and local process settlement have different safety and recovery consequences.

### 18.3 No post-launch retry

After a launch marker exists, the same OperationRequest is never launched again in the same Run, regardless of role, return kind, timeout, or termination observation, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

This rule is smaller and safer than role-specific retry because even a nominally non-mutating provider may produce external or hidden effects.

When no launch marker exists, a later explicit `stt run` may reevaluate prelaunch requirements and attempt the operation, because launch is mechanically disproved.

This is resume before launch, not retry after launch, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

A settled Planner non-OK outcome proceeds to Validator with no accepted Plan, because return validity and local process settlement have different safety and recovery consequences.

A settled Worker or command non-OK outcome commits a Boundary-owned StepResult as `INDETERMINATE` unless accepted role-specific facts conclusively establish `NOT_SATISFIED`; the StepResult contains the exact call outcome and no fabricated role result, because return validity and local process settlement have different safety and recovery consequences.

Later Plan steps stop and Validator receives that evidence, because mission judgment must remain separate from continuation and operational failure.

Boundary never fabricates `SATISFIED` from a missing, rejected, or error return, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

A Validator with `UNSETTLED | UNKNOWN` local work leaves the Run `OPERATIONALLY_BLOCKED`, because return validity and local process settlement have different safety and recovery consequences.

A Validator call that cannot produce an accepted result is returned by Boundary through the same call-failure and local-settlement mechanism used for every other outer operation, because the failed Validator operation produced no mission judgment.

Boundary never converts that operational failure into `FINISH + NOT_SATISFIED` or another mission judgment, because doing so would fabricate semantic evidence.

A settled Validator outcome without an accepted OK result makes the Task `OPERATIONALLY_STOPPED`, because no higher semantic role inside that Task owns judgment; a parent may consume `OPERATIONALLY_STOPPED` under §20, while a root exposes `OPERATIONALLY_STOPPED` to the operator.

Any relevant `UNSETTLED | UNKNOWN` local settlement blocks later steps and semantic validation, because return validity and local process settlement have different safety and recovery consequences.

---

## 19. Evidence and Validator contract

### 19.1 Validator context

Before Validator launch, Boundary builds one bounded immutable evidence index containing exact references to mission, RunPolicyView, required outputs, Round, Planner outcome, Plan or Decline, step results, command observations, child results or operational evidence, current required-output observations, selected prior evidence, and local-settlement facts, because mission judgment must remain separate from continuation and operational failure.

The Validator has no canonical target-root or host path, authoritative Run path, interactive tools, command callback, or repair capability, because semantic roles and lower-trust calls must receive bounded evidence without authoritative host-location access.

It judges persisted evidence through the private Validator contract, because validation must not become hidden execution.

The consequence is that evidence omitted from RootTaskSpec, the accepted Plan, declared outputs, and deterministic Boundary observations cannot be gathered during validation, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

When available evidence cannot establish the mission, the Validator returns `INDETERMINATE + FINISH` unless the current Round already has independently eligible repeat evidence and satisfies every `REPEAT` floor; otherwise better evidence requires a new Run rather than a hidden Validator probe, because mission judgment must remain separate from continuation and operational failure.

### 19.2 Eligible repeat evidence

Eligible repeat evidence must satisfy the following requirements, because mission judgment must remain separate from continuation and operational failure:

- be produced in the current Round under an accepted PLAN by a WorkerStep, CommandStep, or completed child Task; a Round with DECLINE or no accepted Plan cannot repeat;
- be imported and verified as a frozen RUN ArtifactRef;
- bind an admitted OutputRequirement or deterministic command observation;
- have an exact mechanical novelty key absent from all selected Round inputs: `(content_sha256, artifact_type)` for file evidence or the canonical observation identity for deterministic observations;
- record current-Round provenance, purpose, originating requirement or observation method, and exact observation identity;
- be selected explicitly by the Validator, because mission judgment must remain separate from continuation and operational failure.

Boundary mechanically rejects byte-identical copies, renames, and repeated canonical observations even when their path or producer label changes, because mission judgment must remain separate from continuation and operational failure.

A semantically unchanged wrapper whose bytes differ cannot be recognized universally by deterministic orchestration; the private Validator contract must reject such restatement as immaterial, and adversarial fixtures challenge representative wrappers without claiming complete semantic detection, because mission judgment must remain separate from continuation and operational failure.

Validator prose, Planner prose, a prior-Run artifact, a fresh workspace-index entry alone, or an arbitrary Validator-requested freeze is ineligible, because mission judgment must remain separate from continuation and operational failure.

Boundary may freeze a declared current-Round TARGET output into RUN evidence, but it cannot turn arbitrary current target content into new progress evidence after execution stops, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

### 19.3 Validator return and floors

ValidatorResult contains judgment, disposition, reason, material findings, unknowns, and terminal output selections, because Boundary must verify the exact semantic result before committing it.

`FINISH` accepts `SATISFIED`, `NOT_SATISFIED`, or `INDETERMINATE`, because terminal disposition and mission judgment are independent dimensions.

`REPEAT` requires a concrete remaining gap that a fresh Round has a credible basis to close, because repetition without a credibly closable gap would be activity rather than progress.

`REPEAT` additionally contains remaining gap, selected eligible evidence, why fresh planning has a better basis, and no known hard blocker, because the next Round must be justified by inspectable current evidence.

Before recording a ValidatorResult as accepted `RETURNED + OK`, Boundary enforces these mechanical floors, because return validity and local process settlement have different safety and recovery consequences:

- `SATISFIED` requires every Task OutputRequirement to match a verified ArtifactRef, because resume and substitution checks require exact facts to remain uniquely bound;
- `SATISFIED + REPEAT` is invalid, because mission judgment must remain separate from continuation and operational failure;
- Decline + `REPEAT` is invalid, because mission judgment must remain separate from continuation and operational failure;
- `REPEAT` requires all local operations settled and state valid, because return validity and local process settlement have different safety and recovery consequences;
- `REPEAT` requires remaining Round capacity and novel eligible current-Round evidence, because mission judgment must remain separate from continuation and operational failure;
- a nonempty structured hard-blocker list, empty remaining gap, or empty better-basis reason rejects `REPEAT`, because mission judgment must remain separate from continuation and operational failure.

Circular replay, semantic restatement, and cosmetic progress are Validator-policy failures rather than mechanically decidable Boundary facts, because mission judgment must remain separate from continuation and operational failure.

A returned ValidatorResult that violates a floor is `RETURNED + REJECTED`; `VALIDATION_RECORDED` commits the rejected call outcome without an accepted ValidatorResult, and the settled Task becomes `OPERATIONALLY_STOPPED`, because return validity and local process settlement have different safety and recovery consequences.

Boundary does not coerce the judgment or disposition, because mission judgment must remain separate from continuation and operational failure.

Boundary cannot prove semantic materiality, because repeat evidence must represent materially new current-Round information rather than relabelled prior content.

Adversarial qualification fixtures must distinguish real leverage from cosmetic files, restated prose, far failure, and circular plans, because the design claim must remain executable and falsifiable.

---

## 20. Child Tasks and failure propagation

A TaskStep declares child mission, `mission_relation_reason`, declarative `ChildAuthoritySpec`, exact PlanInputs, and required child outputs, because delegation and same-mission continuation need distinct identity and failure rules.

Boundary validates the ChildAuthoritySpec against the parent TaskAuthority, resolves those PlanInputs into parent TaskStep InputRefs, constructs the child TaskAuthority with the unchanged target identity, and creates child-scoped EvidenceBindings, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Boundary rejects exact ancestor mission hashes, missing relation reason, authority or capability expansion, depth overflow, total-Task budget exhaustion, and conflicting deterministic child identity, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Hash inequality is only a mechanical floor; Planner remains responsible for semantic distinctness, because planning must remain immutable, bounded, and unable to redefine runtime authority.

Child-to-parent mapping is defined as follows, because parent audit must distinguish semantic child results from settled and unsettled operational failure:

```text
child SATISFIED
→ parent step SATISFIED

child NOT_SATISFIED
→ parent step NOT_SATISFIED

child INDETERMINATE
→ parent step INDETERMINATE

child reaches OPERATIONALLY_STOPPED after a settled failure prevents semantic completion
→ no child judgment is fabricated
→ Boundary commits parent StepResult as OPERATIONAL_INDETERMINATE with exact child stop evidence
→ later parent steps stop
→ parent Validator may audit the parent mission

child has UNSETTLED or UNKNOWN local operation
→ child and entire Run remain OPERATIONALLY_BLOCKED
→ no ancestor Validator launches

child INVALID
→ entire Run INVALID
```

`OPERATIONALLY_STOPPED` is a terminal nonsemantic Task state: the child has no semantic judgment, all relevant local work is settled, and same-Run semantic execution cannot continue, because return validity and local process settlement have different safety and recovery consequences.

`OPERATIONAL_INDETERMINATE` is the parent-step outcome derived from that state, not a child terminal judgment, because mission judgment must remain separate from continuation and operational failure.

This distinction preserves ancestor audit after settled failure without laundering missing child semantics, because return validity and local process settlement have different safety and recovery consequences.

---

## 21. Boundary and Lead

### 21.1 Boundary

Every lifecycle operation follows the sequence below, because orchestration must remain mechanical while Boundary owns trusted lifecycle transitions:

```text
Lead
→ Boundary
→ deterministic transition or one outer operation
→ Boundary
→ verified transition package
→ ledger commit
→ compact receipt
→ Lead
```

Boundary owns identity checks, authority admission, request construction, exchange preparation, provider/command launch, capture, outcome classification, output import, ArtifactRef verification, child binding, transition-package publication, ledger append, and compact receipts, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Boundary does not choose semantic evidence, create Plans, judge mission satisfaction, decide progress materiality, or repair target work, because repeat evidence must represent materially new current-Round information rather than relabelled prior content.

### 21.2 Lead

A valid Run has exactly one nonterminal root-to-leaf execution frontier; terminal siblings may remain as evidence, but multiple incomparable nonterminal Tasks make the Run `INVALID`, because a depth-first driver cannot choose among competing active branches mechanically.

Lead validates that unique root-to-deepest active Task path and derives exactly one next mechanical action, because orchestration must remain mechanical rather than acquire semantic authority.

It may create Round 0, consume one pre-existing repeat transition, invoke one operation through Boundary, descend to a child, finalize a uniquely completed transition, or stop, because mission judgment must remain separate from continuation and operational failure.

Lead never reads broad target content, invents a step, changes a Plan, selects prior evidence, chooses a judgment, or consumes a newly produced `REPEAT` in the same invocation, because mission judgment must remain separate from continuation and operational failure.

One invocation may consume at most one `AWAITING_REPEAT` state that existed at invocation start across the entire Task tree, because mission judgment must remain separate from continuation and operational failure.

Initial Round 0 creation for new Tasks does not consume that allowance, because orchestration must remain mechanical while Boundary owns trusted lifecycle transitions.

---

## 22. Transition packages, ledger, and commit protocol

Each Task owns one append-only hash-chained JSONL ledger, because crash recovery requires immutable packages and one unique commit relationship.

All identity-bearing control JSON uses one canonical encoding: UTF-8, sorted object keys, stable compact separators, one final LF, no NaN or Infinity, duplicate object keys rejected, explicit schema identity, and frozen byte/depth limits, because independent implementations need one mechanically decidable contract.

Identity hashes bind the exact canonical bytes, because reconstructing objects through parser-dependent behavior would make two implementations disagree about accepted state.

Minimal events are, because crash recovery requires immutable packages and one unique commit relationship:

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

`PLANNING_FINISHED`, `STEP_FINISHED`, and `VALIDATION_RECORDED` commit call outcomes whether or not the call outcomes contain an accepted semantic value, because return validity and local process settlement have different safety and recovery consequences.

`ROUND_FINISHED` exists only for an accepted `ValidatorResult` and commits the Validator judgment and disposition, because mission judgment must remain separate from continuation and operational failure.

A settled non-OK `VALIDATION_RECORDED` derives `OPERATIONALLY_STOPPED`; an unsettled or unknown `VALIDATION_RECORDED` derives `OPERATIONALLY_BLOCKED` without fabricating `ROUND_FINISHED`, because return validity and local process settlement have different safety and recovery consequences.

A lifecycle transition package contains the following fields, because crash recovery requires immutable packages and one unique commit relationship:

- exact immutable payload files;
- package manifest and hashes;
- exact expected prior ledger head;
- exact canonical pending event bytes, because crash recovery requires immutable packages and one unique commit relationship.

The protocol is defined as follows, because crash recovery requires immutable packages and one unique commit relationship:

```text
construct package under same-parent temporary path
→ flush, reread, and verify
→ atomically publish create-only package
→ append the exact pending event bytes
→ flush and verify ledger
→ return compact receipt
```

The ledger event commits the package, because crash recovery requires immutable packages and one unique commit relationship.

A published complete package without its event may be completed on resume only when all are true, because crash recovery requires immutable packages and one unique commit relationship:

- the package verifies completely;
- its expected prior ledger head still equals the current head;
- its transition is the unique mechanically eligible next action;
- no competing package or event exists;
- completing it launches no semantic or external operation, because crash recovery requires immutable packages and one unique commit relationship.

Resume then appends the exact precomputed event bytes, because crash recovery requires immutable packages and one unique commit relationship.

This is narrow commit completion, not generalized orphan adoption, because crash recovery requires immutable packages and one unique commit relationship.

An event with missing or mismatched package, a package that is not uniquely eligible, competing packages, interior ledger corruption, hash mismatch, or sequence gap makes the Run `INVALID`, because crash recovery requires immutable packages and one unique commit relationship.

One incomplete trailing ledger fragment may be removed under the writer lock after validating the complete prefix, because crash recovery requires immutable packages and one unique commit relationship.

Task creation remains an atomic directory publication containing its initial ledger event because the Task ledger does not exist beforehand.

---

## 23. Explicit crash and resume rules

Same-Run resume is allowed only when no semantic or effectful work is replayed, because resume must complete only uniquely determined non-effectful work without replay.

```text
verified run.json and frozen Bootstrap/import payloads,
no canonical root Task path or conflicting root publication
→ atomically publish the original root Task derived from frozen RootTaskSpec

Task committed, no Round
→ create Round 0

phase-specific start event commits OperationRequest, no launch marker
→ explicit later run may launch that exact request once

launch marker + complete uniquely eligible call-outcome transition package,
pending event absent
→ apply narrow commit completion from §22 without relaunch

launch marker, no complete uniquely eligible call-outcome package after interruption
→ Run NON_RESUMABLE

complete non-call transition package, pending event absent
→ apply narrow commit completion from §22

child terminal result or settled operational evidence committed,
parent STEP_FINISHED absent
→ verify child binding and deterministically commit parent step

VALIDATION_RECORDED contains an accepted bound ValidatorResult,
ROUND_FINISHED absent
→ reapply mechanical floors and deterministically commit Round result without relaunch

VALIDATION_RECORDED contains settled non-OK outcome
→ derive OPERATIONALLY_STOPPED; do not fabricate ROUND_FINISHED

VALIDATION_RECORDED contains UNSETTLED or UNKNOWN local settlement
→ derive OPERATIONALLY_BLOCKED; do not launch an ancestor Validator

ROUND_FINISHED with FINISH committed,
TASK_FINISHED absent
→ verify Round result and deterministically publish/commit Task result

ROUND_FINISHED with REPEAT committed
→ derive AWAITING_REPEAT; do not create next Round in same invocation
```

Temporary root-Task construction residue is non-authoritative and may be removed under the writer lock after verifying that no canonical root Task or conflicting publication exists, because the design claim must remain executable and falsifiable.

A canonical root path missing its complete `TASK_CREATED` publication is `INVALID`, because resume must complete only uniquely determined non-effectful work without replay.

A provider result file, command log, or target effect without a committed call outcome remains diagnostic evidence only, because return validity and local process settlement have different safety and recovery consequences.

STT does not infer whether an interrupted launched operation ran successfully, because resume must complete only uniquely determined non-effectful work without replay.

Recovery from a non-resumable Run is operator-owned because the interrupted operation may still have effects.

A new Run may begin only after the operator establishes an acceptably quiescent target or chooses an isolated replacement target, then explicitly selects any prior evidence; STT does not claim to prove escaped-process, remote, or external quiescence, because current lifecycle evidence must not depend on mutable or ambient history.

---

## 24. Workspace index and target observations

A fresh deterministic workspace index is created for every Round within read authority, because context must not be mistaken for permission or immutable evidence.

It uses `lstat`, never follows symlinks, records regular files/directories/symlink metadata, does not read bodies solely to index, and emits deterministic overflow markers, because path admission must not escape the target or reach control-state locations.

The index is context, not permission or immutable evidence, because workspace context must not become permission or unverified immutable evidence.

Every target file consumed later is opened through Boundary admission and identity verification, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

Before Validator, Boundary may deterministically observe required exact target outputs and already declared current-Round outputs, because mission judgment must remain separate from continuation and operational failure.

It does not perform open-ended semantic investigation or choose arbitrary evidence after execution stops, because workspace context must not become permission or unverified immutable evidence.

---

## 25. Prior-Run evidence

`RootTaskSpec.prior_evidence_selectors` names exact committed references from one optional prior Run, because current lifecycle evidence must not depend on mutable or ambient history.

An importable reference must identify a Boundary-owned prior RUN artifact, report, or log whose exact bytes remain under that prior Run; a direct live TARGET ArtifactRef is incompatible unless the prior Run already contains a Boundary-frozen RUN copy of those bytes, because live execution requires admitted profiles and truthful evidence without a containment claim.

The caller owns selection; Boundary validates each reference and imports its exact bytes and origin metadata into a create-only ArtifactRef under the new Run before root Task publication, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

The imported ArtifactRef binds the prior Run identity, prior artifact identity, schema, producer, committed event, bytes, compatibility labels, and current import observation, because current lifecycle evidence must not depend on mutable or ambient history.

After root Task publication, current lifecycle execution consumes only the imported current-Run ArtifactRef and never rereads the prior Run root, because deleting or changing an external Run root must not rewrite current evidence.

Imported prior material is advisory untrusted data and cannot change current mission, authority, routing, policy, Plan, or lifecycle state, because target and prior content must not acquire control authority.

Ledgers, Rounds, cursors, Task states, and uncommitted files are never merged, because current lifecycle evidence must not depend on mutable or ambient external history.

An uncommitted prior file may be surfaced for diagnosis only and cannot be imported as evidence, satisfy an output, or justify `REPEAT`, because mission judgment must remain separate from continuation and operational failure.

---

## 26. Context and independence

Every model invocation is reconstructible from persisted request material and frozen private contracts, because model calls must be reconstructible and independence claims must stop at observable evidence.

- Planner receives mission, RunPolicyView, path-free TaskAuthorityView, admitted WorkerRouteViews and CapabilityProfileViews, output requirements, path-free EvidenceBindingViews, identities of selected InputRefs with path-free ArtifactRefViews and bounded ArtifactViews, workspace index, and advisory prior Validator report, because model calls must be reconstructible and independence claims must stop at observable evidence.
- Worker receives one step, exchange copies of admitted inputs, responsibility scopes, output requirements, target root, and route contract, because model calls must be reconstructible and independence claims must stop at observable evidence.
- Validator receives RunPolicyView and one bounded evidence index plus authoritative reference identities, path-free ArtifactRefViews, and bounded ArtifactViews for exact admitted reports, observations, and outputs, because model calls must be reconstructible and independence claims must stop at observable evidence.
- Lead receives compact receipts only, because model calls must be reconstructible and independence claims must stop at observable evidence.

Planner, Worker, and Validator are separate invocations, because model calls must be reconstructible and independence claims must stop at observable evidence.

Validator receives no Planner or Worker conversation state, because Validator judgment must depend on persisted evidence rather than hidden conversational continuity.

Requested route separation is recorded; actual provider context isolation or model identity is `UNKNOWN` unless the host exposes evidence, because model calls must be reconstructible and independence claims must stop at observable evidence.

Logs and broad child histories remain file-backed, because model calls must be reconstructible and independence claims must stop at observable evidence.

Parent and prior context references exact selected artifacts rather than copying entire histories, because model calls must be reconstructible and independence claims must stop at observable evidence.

### 26.1 Call and cost visibility

Run creation computes and records conservative structural maxima for Planner, Validator, and total step-operation launches from the finite Task/Round/step policy, because model calls must be reconstructible and independence claims must stop at observable evidence.

Status and terminal receipts always report actual OperationRequests and launched Attempts grouped by role, route, requested model, and requested effort, because model calls must be reconstructible and independence claims must stop at observable evidence.

Monetary price estimates are optional external annotations rather than architecture facts, because prices change independently of the frozen Run.

---

## 27. Derived states

Semantic terminal judgments are, because mission judgment must remain separate from continuation and operational failure:

```text
SATISFIED
NOT_SATISFIED
INDETERMINATE
```

Nonterminal or operational states include, because operators and resume logic need one deterministic interpretation of committed facts:

```text
NEEDS_ROUND
NEEDS_PLANNING
NEEDS_STEP
NEEDS_VALIDATION
AWAITING_REPEAT
OPERATIONALLY_BLOCKED
OPERATIONALLY_STOPPED
NON_RESUMABLE
INVALID
TERMINAL
```

State is derived from the validated ledger and committed packages; there is no mutable cursor, because resume and operators need one deterministic interpretation of committed facts.

`PRELAUNCH_BLOCKED` is a transient invocation outcome rather than a ledger-derived state, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

It is returned when an exact OperationRequest is committed, no launch marker exists, and a current launch prerequisite fails; a later explicit invocation may reevaluate that prerequisite because launch remains mechanically disproved.

`OPERATIONALLY_BLOCKED` is a same-Run stopping state in the MVP: unsettled or unknown local work forbids semantic progress, and later `stt run` reports the blocker without launching a settlement probe or semantic operation, because return validity and local process settlement have different safety and recovery consequences.

`OPERATIONALLY_STOPPED` means settled failure ended the Task without a semantic judgment; only a parent may map it under §20, because return validity and local process settlement have different safety and recovery consequences.

`NON_RESUMABLE` and `INVALID` also forbid further lifecycle execution in the same Run, because operators and resume logic need one deterministic interpretation of committed facts.

A settled root `OPERATIONALLY_STOPPED` may lead to a new Run against current reality, because return validity and local process settlement have different safety and recovery consequences.

`OPERATIONALLY_BLOCKED` or `NON_RESUMABLE` requires operator-owned quiescence or an isolated replacement target before a new Run, because the prior operation may still produce effects.

`INVALID` requires diagnosis of the integrity failure and must not donate authoritative lifecycle state, because resume and operators need one deterministic interpretation of committed facts.

---

## 28. Layout

A conceptual layout is defined as follows, because layout must reflect authority boundaries without becoming a competing semantic contract:

```text
<run-root>/
├── runtime/
├── runtime-manifest.json
├── bootstrap/
│   ├── root-task-spec.json
│   └── routing.json
├── run.json
├── run.lock
└── root/
    ├── task.json
    ├── mission.md
    ├── required-outputs.json
    ├── ledger.jsonl
    ├── transitions/
    ├── rounds/
    │   └── 000/
    │       ├── round.json
    │       ├── workspace-index.json
    │       ├── planning/
    │       ├── steps/
    │       ├── validation/
    │       └── result-ref.json
    └── result-ref.json
```

Child Tasks live under the owning step at `rounds/<round>/steps/<index>-<id>/task/`, because delegation and same-mission continuation need distinct identity and failure rules.

Exact module and incidental directory names are implementation choices, because code structure should follow responsibility and proof rather than speculative framework boundaries.

Semantic roles never invent authoritative paths, because layout must reflect authority boundaries without becoming a competing semantic contract.

---

## 29. Public CLI

The CLI consumes a preconstructed RootTaskSpec rather than free-form semantic fragments, because root semantics and host assumptions must be frozen before semantic execution:

```text
stt start \
  --workspace <target> \
  --task-spec <root-task-spec.json> \
  --routing-file <routing.json> \
  [--prior-run <run-root>] \
  [--allow-live-provider]

stt run --run-root <run-root>
stt status --run-root <run-root>
stt diagnose --run-root <run-root>
```

`--prior-run` supplies the root from which selectors in RootTaskSpec are validated; it does not authorize Boundary to choose evidence, because trusted lifecycle mutation must remain centralized and mechanically verifiable.

`start` freezes the spec and routing, validates host/source/target/prior evidence, prepares runtime, publishes Run and root Task, and advances until FINISH, REPEAT, transient `PRELAUNCH_BLOCKED`, operational stop, non-resumability, or invalidity, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

`run` executes only from frozen runtime, acquires the writer lock, validates state, completes admitted deterministic transitions, attempts an exact committed request only when no marker exists, returns transient `PRELAUNCH_BLOCKED` when a current launch prerequisite fails, or consumes one pre-existing repeat transition, because a second launch could replay hidden target, billing, network, remote, or escaped-child effects.

It never changes policy or routing, because public operations must expose the architecture without hidden mutable policy or repair.

`status` and `diagnose` are read-only, because operators need truthful state visibility without causing lifecycle mutation.

They attempt the Run lock nonblocking and return the query outcome `RUN_BUSY` without reading lifecycle files when a writer holds the lock, because a partial observation can report a false next action.

`RUN_BUSY` is a read-query outcome rather than a lifecycle state, because operators need truthful state visibility without causing lifecycle mutation.

`status` and `diagnose` report exact state, deepest active Task, current Round, blocker, committed result references, and the only permitted next caller action, because operators need truthful state visibility without causing lifecycle mutation.

`status` and `diagnose` never repair automatically, because operators need truthful state visibility without causing lifecycle mutation.

---

## 30. Qualification ownership

The architecture requires executable proof for these groups, because each material architecture claim must remain executable and falsifiable through one proof authority:

- root specification and immutable Run identity;
- host-capability rejection and frozen runtime closure;
- authority/capability narrowing and injection resistance;
- no authoritative Run-path disclosure to lower-trust processes;
- canonical schema and identity substitution rejection;
- live Worker/command output verification and honest effect limits;
- closed call/local-settlement algebra and no second post-launch Attempt;
- Planner PLAN/DECLINE behavior;
- Validator FINISH/REPEAT floors and evidence novelty;
- finite Round and Task-depth limits;
- nuanced settled versus unsettled child failure propagation;
- transition-package commit completion and every explicit crash window;
- prior evidence selection without state merge;
- plain-directory and Git targets;
- no archive imports, no target `.stt`, and full repository regression, because each material architecture claim must remain executable and falsifiable through one proof authority.

The implementation plan owns one canonical numbered scenario catalog that covers these proof groups, because duplicating the catalog in the architecture would create competing test authority.

Parameterization may consolidate test IDs, but parameterization may not omit a current architecture proposition, qualification, or falsification path, because compression must preserve canonical protected behavior rather than an unavailable historical count.

`Q01`–`Q36` in the implementation plan are the complete canonical executable proof catalog, because each material architecture claim must remain executable and falsifiable through one proof authority.

Historical scenario counts and external reconstruction audits are non-normative evidence; an earlier scenario protects the current design only when its behavior is represented by a current architecture proposition and a current Q scenario, because canonical readiness must not depend on an unavailable side artifact.

---

## 30.1 Implementation qualification obligations

The following are executable implementation obligations rather than unresolved architecture choices, because each material architecture claim must remain executable and falsifiable through one proof authority:

- at least one supported-host adapter must prove the capability floor, target-root identity, and process-group observation before the implementation is accepted;
- controlled Claude Code and Codex adapters must prove request/return binding and truthful `UNKNOWN` routing or isolation where facts are unobservable before those adapters are accepted;
- command-profile usability must be demonstrated on representative build, test, and file-transformation steps so capability admission does not make ordinary missions infeasible;
- same-user hostile discovery of Run paths remains outside containment; qualification may prove post-call detection, not prevention;
- any automated host that repeatedly invokes a prelaunch-blocked Run must persist, enforce, and surface its own finite invocation budget, because the STT Round budget and Task ledger do not own external polling;
- Run-root retention and deletion remain operator-owned and must be surfaced honestly, because each material architecture claim must remain executable and falsifiable through one proof authority.

These obligations constrain implementation acceptance and may reveal a new architecture conflict, but they do not require implementation evidence before implementation is allowed to begin, because each material architecture claim must remain executable and falsifiable through one proof authority.

Architecture readiness asks whether the contracts are explicit, feasible enough to build, internally consistent, and linked to falsification; implementation qualification later determines whether a concrete runtime satisfies them, because each material architecture claim must remain executable and falsifiable through one proof authority.

---

## 31. Readiness and review gates

The canonical architecture candidate is not implementation-ready merely because its prose is complete.

Promotion to implementation-ready requires all of the following on the same unchanged document pair, because implementation must not begin from an unreviewed or internally inconsistent document pair:

1. §33 disposes every material predecessor protection represented in the canonical design as `PRESERVE`, `CHANGE`, or `REMOVE` with current replacement and checks;
2. every current architecture decision maps to at least one implementation responsibility and Q scenario, with no competing semantic rule or dependency on an unavailable external audit;
3. WELL review finds every material proposition warranted, qualified, linked, checkable, and non-duplicative;
4. a full RunSkeptic review loop converges with no unresolved ACTION, CONFLICT, DECOMPOSE path, review-required status, or blocking design unknown;
5. named architecture conflicts have explicit owner decisions rather than silent compromise;
6. the implementation plan exposes a feasible construction and qualification path without requiring implementation results as a precondition for beginning implementation;
7. any status edit is treated as a document change that resets the review binding; the final unchanged pair whose status says implementation-ready must itself complete WELL review, the full RunSkeptic convergence requirement, and the Promotion Check, and its containing commit is then recorded externally as the implementation base without changing the accepted file bytes, because implementation must not begin from an unreviewed or internally inconsistent document pair.

Executable host, adapter, command-profile, repository, and runtime proofs belong to implementation qualification under §30.1 and the implementation plan, because implementation must not begin from an unreviewed or internally inconsistent document pair.

Failure of those proofs may invalidate an architecture assumption and force a WELL lineage repair, but the proofs are not circular prerequisites for declaring a fully specified design ready to implement, because implementation must not begin from an unreviewed or internally inconsistent document pair.

Until the document gates pass, implementation and any claim of implementation readiness are prohibited; repository publication may identify this document pair only as the canonical candidate, because implementation must not begin from an unreviewed or internally inconsistent document pair.

---

## 32. WELL change rule and lineage template

Every future material change appends or updates a lineage row, because future edits must preserve or explicitly replace each protected proposition:

```text
current decision/subdecision ID
prior source and proposition
PRESERVE | CHANGE | REMOVE
current warrant
failure mode protected
replacement protection, when changed or removed
architecture sections affected
implementation scenarios affected
remaining unknowns
```

A decision ID must be split when one row contains independently removable protections, because coarse IDs can hide partial loss.

WELL conformance remains distinct from correctness, because future edits must preserve or explicitly replace each protected proposition.

The document may be internally inspectable and still wrong; RunSkeptic and executable qualification remain separate checks, because future edits must preserve or explicitly replace each protected proposition.

---

## 33. Canonical proposition-level lineage matrix

The canonical lineage matrix records the material protections examined in the 2026-08-04 gap-first historical pass, because historical protection changes must remain auditable without becoming current authority.

`Partial` means the named revision identified the concern but did not supply the current enforceable contract, because historical protection changes must remain auditable without becoming current authority.

`Absent` means no equivalent protection was found in the reviewed revision; `Absent` does not prove that no related sentence existed elsewhere, because historical protection changes must remain auditable without becoming current authority.

| Current decision | Protected proposition | `c3be467` | `702b480` | `81da365` | First WELL repair | Current disposition |
|---|---|---|---|---|---|---|
| `D1` | Root mission, authority, outputs, evidence, routing, and finite policy have one pre-Bootstrap owner. | Partial: CLI mission/evidence and explicit Task fields, but no unified RootTaskSpec. | Regressed: free-form submission remained while Bootstrap was deterministic. | Regressed: submission/routing identity existed without root semantic construction. | Partial: bound values named, creation source absent. | `CHANGE`: introduce immutable RootTaskSpec plus selectors and RootAuthoritySpec. |
| `D2` | Task, semantic Round, and transport Attempt are different identities. | Task and bounded provider attempts existed; no Round. | Task and outer outcomes existed; no Round. | Strong: Round and caller-mediated repeat introduced. | Partial: distinction present but retry semantics blurred it. | `PRESERVE+CLARIFY`: one launch Attempt, fresh Rounds, distinct child Tasks. |
| `D3` | Task may validly exist before Round 0 and all recursion/repetition is finitely bounded. | Finite attempts; no Round; recursion bounded only indirectly. | Explicitly no depth bound and same-mission recursion allowed. | Exact ancestor mission rejected, but no depth/Round cap. | Added Task depth, but still said one-or-more Rounds and omitted Round/Task/step budgets. | `CHANGE`: zero-or-more Rounds plus finite depth, total Task, Round, and step budgets. |
| `D4` | Lead is mechanical and Boundary is mandatory. | Strong mandatory Boundary and mechanical DFS Lead. | Preserved at high level. | Preserved and expanded. | Preserved. | `PRESERVE`: retain one Boundary façade and compact Lead receipts. |
| `D5` | Frozen runtime survives self-modification; authoritative Run and exchange are disjoint from source/target. | Frozen control and persistent bundle, but authoritative state lived under target. | Strong correction: disjoint temporary Run root and live target. | Preserved. | Preserved Run root but exposed some Run artifacts to lower-trust calls. | `CHANGE`: preserve disjoint Run/frozen runtime; add disjoint exchange; allow source=target. |
| `D6` | Atomic rename, locking, sync, path observation, and process supervision are architecture feasibility requirements. | Many primitives named, but non-local/host support remained dispersed. | Partial. | Left several as implementation parameters. | Still treated key host guarantees as parameters. | `CHANGE`: explicit supported-host capability floor and fail-before-publication rule. |
| `D7` | Accepted payloads are immutable and ledger events have a recoverable commit relation. | Strong atomic Task publication, ledger chain, and create-only attempts; some crash windows remained implicit. | Simplified and lost concrete edges. | Restored payload-before-event and crash invalidity, but stranded deterministic finalization windows. | Added common protocol but made package-without-event broadly non-resumable. | `CHANGE`: precomputed transition package plus narrow deterministic commit completion. |
| `D8` | Lower-trust calls do not receive authoritative Run-state paths and cannot be accepted after control-state mutation. | Strong path admission; avoided broad `.stt` exposure. | Explicitly avoided passing Run directory as ordinary work context. | RUN ArtifactRefs could cross role boundaries. | Reverification of exposed artifact did not protect parent Run state. | `CHANGE`: disjoint non-authoritative exchange, no Run paths, post-call control revalidation. |
| `D9` | Authority covers path admission, step/route/profile selection, environment names, declared external effects, and path-free authority/profile views while disclaiming containment. | Strong read/write paths and role bindings; commands were non-mutating and effects narrower. | Correct cooperative live-effect boundary, but authority became less concrete. | Path/route/step authority named; command/Worker capabilities incomplete. | Mechanical path narrowing restored, but arbitrary executable/env/effect grants remained. | `CHANGE`: RootAuthoritySpec, runtime TaskAuthority, named profiles, env/effect classes, child subset. |
| `D10` | STT-private role contracts govern runtime and target/prior content cannot become instruction. | Strong explicit private-contract and general-contract exclusion. | Role names remained; trust-order rule absent. | Private contract files implied in implementation; architecture authority unclear. | Implementation mentioned contracts; architecture trust order absent. | `PRESERVE+EXTEND`: restore private-contract authority and explicit untrusted-data precedence. |
| `D11` | Planner receives closed persisted context and returns PLAN or DECLINE; Decline ends the Round. | One accepted Plan; operational failures blocked; no Round repeat. | PLAN/DECLINE/GAVE_UP and same-mission delegation. | PLAN/DECLINE plus INVESTIGATE and REPEAT. | Decline claimed no useful next path but could still repeat through Validator evidence. | `CHANGE`: closed-context PLAN/DECLINE; Decline permits Validator FINISH only. |
| `D12` | Plan, PlanInputs, PlanInputResolutions, selectors, EvidenceBindings, InputRefs, output requirements, artifacts, provenance, purpose, and role results have exact binding. | Strong concrete Plan/input/output/step-result schemas and provenance. | Many schemas compressed. | ArtifactRef improved, but root selectors and Plan/result identity remained incomplete. | OutputRequirement split restored; preexisting/prior producer identity and reusable-consumer semantics remained ambiguous. | `PRESERVE+EXTEND`: selector purpose, current-Run freezing, discriminated provenance, exact purpose equality, producer constraints, principal-consumer labels, InputRef exact consumer, Plan header, and role-result binding. |
| `D13` | Worker and command execute live under admitted profiles; declared outputs verify; hidden effects remain unknown. | Staged Worker plus deterministic mutation and non-mutating commands. | Strong live-execution correction and honest effect limit. | Preserved live Worker/command semantics. | Preserved, but capability admission incomplete. | `PRESERVE+BOUND`: retain live target; add profiles; preserve reported scope violations for Validator judgment; fail mechanically only for authoritative-state mutation or unresolved local activity; retain no effect-completeness claim. |
| `D14` | No outer operation launches twice after a marker. | Confirmed-timeout retries existed for semantic roles and replay-safe commands. | Adapter-internal attempts remained loosely allowed. | Explicitly excluded automatic provider retry after an outer call may have launched. | Reintroduced Planner/Validator timeout retry based on contract non-mutation. | `CHANGE`: adopt the smaller no-post-launch-retry rule for every role. |
| `D15` | Return acceptance and local settlement are separate closed dimensions. | Detailed attempt dispositions and termination states. | Launch/completion/settlement introduced but malformed returns collapsed into give-up. | Useful OK/ERR/NO_RETURN and settlement split. | Added RETURNED+REJECTED but request/envelope and settlement scope remained vague. | `PRESERVE+CLARIFY`: immutable OperationRequest, one AttemptEnvelope, closed algebra, local-only settlement. |
| `D16` | Validator judges persisted evidence without hidden execution; repeat evidence is novel current-Plan output. | Independent Validator, no automatic repair; no Round repeat. | Validator could investigate; same-mission child continuation. | REPEAT floors added; read-only Validator investigation could create evidence. | Report excluded, but arbitrary Validator-requested freezing still enabled wrapper evidence. | `CHANGE`: no interactive Validator tools; `FINISH` carries successful, failed, or indeterminate terminal judgment; `REPEAT` requires a concrete credibly closable gap; no-Plan/Decline cannot repeat; producer/provenance/source novelty floor. |
| `D17` | Settled child operational failure can be audited by parent without fabricating child judgment; unsettled child work blocks the Run. | Ancestor Validators always ran after child terminal failure; operational provider blockers often stranded child. | Parent audit preserved generally. | Strong nuanced mapping: settled child failure→parent indeterminate evidence; unsettled→whole Run block. | Changed all child operational failures to whole-Run block without resolving the trade-off. | `CHANGE`: restore nuanced settled/unsettled rule, add child `OPERATIONALLY_STOPPED`, and name parent outcome `OPERATIONAL_INDETERMINATE`. |
| `D18` | Context is bounded/reconstructible and independence claims stop at observable evidence. | Strong compact Lead and separate Validator invocation; hidden isolation unknown. | Preserved bounded context at high level. | Preserved and added advisory prior Round context. | Preserved, but interactive tools conflicted with closed reconstruction. | `PRESERVE+CLARIFY`: bounded ArtifactViews, separate invocation, no conversation state, actual isolation UNKNOWN. |
| `D19` | Caller selects exact committed prior evidence; Boundary validates, imports it into the new Run, and never chooses or merges state. | Prior Run was not central. | Optional prior Run named; selection ownership incomplete. | Prior evidence references allowed; selector owner and lifetime incomplete. | Prior-Run section still said “selected” without canonical selector source or current-Run freezing. | `CHANGE`: selectors in RootTaskSpec, exact validation, create-only current-Run import with origin provenance, advisory data only, no state merge or later prior-root dependency. |
| `D20` | Safe deterministic resume completes child→parent, Round→Task, package→event, and prelaunch boundaries without replay. | Strong durable DFS child adoption and atomic Task publication. | Crash model simplified and lost several finalization edges. | Launch-marker non-resume and committed REPEAT resume restored; child/Task completion windows incomplete. | Publication protocol improved but safe deterministic completion was underdefined. | `PRESERVE+EXTEND`: explicit narrow completion rules, Validator-record-to-Round finalization, and ambiguous launched-call non-resumability. |
| `D21` | Implementation links to architecture and owns one lean parameterized proof catalog. | Architecture and implementation duplicated 101 scenarios. | Both documents were broadly rewritten together. | Architecture had 40 scenarios and implementation repeated them. | Detailed rules, focused proofs, 52 scenarios, invariant map, and done repeated semantics. | `CHANGE`: one 36-scenario parameterized catalog; slices and map reference IDs only. |
| `D22` | Future design changes preserve propositions, not only headings or coarse decisions. | No lineage discipline. | Whole-document replacement caused observed loss. | Second whole-document replacement caused further loss. | Added D1–D12 and a future delta rule, but no complete current matrix and IDs bundled independent protections. | `CHANGE`: granular D1–D23, this current matrix, and mandatory subdecision splitting. |
| `D23` | Semantic-call and transport-launch cost remains visible. | Original architecture forecast model-call shape and later W versions preserved cost instrumentation. | Broad rewrites repeatedly omitted it. | Rounds increased possible semantic calls without restoring a cost contract. | First WELL repair omitted cost from D1–D12 and implementation proof. | `PRESERVE+LEAN`: structural upper bounds and actual role/route call counts; monetary estimates remain advisory. |

The matrix is evidence of the reviewed lineage, not proof that no historical protection was missed, because historical protection changes must remain auditable without becoming current authority.

The readiness gate still requires RunSkeptic to challenge the complete current pair and any additional repository evidence before promotion, because historical protection changes must remain auditable without becoming current authority.
