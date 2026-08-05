# STT MVP Implementation Plan

**Status:** Canonical candidate derived from `plans/stt-mvp-architecture-plan.md`
**Architecture authority:** `plans/stt-mvp-architecture-plan.md`
**Repository:** `saffih/skeptic`
**Historical reconstruction base:** `74c4f6a2c34da501101141525c8a34d691c384a1`
**Document profile:** `docs/well.md`
**Implementation scope:** STT MVP only

This document owns construction order, responsibility boundaries, and executable proof, because the architecture must remain the sole owner of runtime meaning.

When this plan conflicts with the architecture, implementation stops and the architecture is repaired first, because silent interpretation would create an unreviewed design branch inside code.

---

## 1. Entry gate and stop rule

Production implementation may begin only after the unchanged architecture and implementation plan pass WELL, RunSkeptic, and promotion review, because construction must start from one accepted semantic base.

The implementation branch must start from the externally recorded commit containing that accepted pair, because the historical reconstruction base is evidence rather than the implementation base.

Implementation stops when every canonical qualification scenario passes, repository regression passes, and no production mechanism lacks an architecture owner, because additional framework work would be speculative.

Archived Target Task code and contracts are not imported, because compatibility with superseded semantics would create a second lifecycle.

---

## 2. Build discipline

Build the smallest vertical slices that prove complete behavior, because broad scaffolding can hide missing lifecycle edges.

Each slice must satisfy the following conditions, because reversible proof-bearing increments expose errors early:

- one coherent responsibility boundary;
- only abstractions required by the current architecture;
- positive and known-bad qualification cases;
- preservation of every earlier passing scenario;
- one reviewable commit whose subject names the behavior proved;
- no partial alternate lifecycle

The following additions are prohibited unless the architecture changes first, because they add semantic or operational authority absent from the MVP:

- generic workflow or scheduler framework;
- mutable cursor;
- automatic post-launch retry or fallback;
- semantic progress score;
- Task, depth, Round, or Plan-step cap;
- runtime novelty gate for Validator `REPEAT`;
- same-mission child rejection;
- curated history package as the only model context;
- target sandbox or rollback claim;
- archive-runtime compatibility

Python standard-library primitives are preferred, because fewer dependencies reduce runtime-closure and installation risk.

A dependency is added only when it removes a demonstrated correctness risk, because speculative dependencies enlarge the frozen runtime without proof value.

---

## 3. Responsibility map

The implementation assigns one primary owner per responsibility, because unclear ownership creates duplicate schemas and lifecycle paths:

| Responsibility | Suggested area | Architecture |
|---|---|---|
| canonical bytes, hashes, create-only files, transition packages | `storage.py`, `transition.py` | §§3, 10 |
| ledger validation and state derivation | `ledger.py`, `state.py` | §§10, 13 |
| host probes, writer lock, frozen runtime | `host.py`, `runtime.py`, `bootstrap.py` | §§3, 11 |
| root, authority, routing, Task/Round, Plan, result schemas | `contracts.py`, `authority.py`, `routing.py` | §§3, 6, 7 |
| STT read-only filesystem tools and audit capture | `history.py`, `history_tools.py` | §5 |
| workspace index and target observation | `workspace.py` | §7 |
| exchange, launcher, providers, commands | `exchange.py`, `launcher.py`, `providers/`, `command.py` | §§6, 8, 11 |
| mandatory Boundary façade | `boundary.py` | §4.2 |
| mechanical depth-first Lead | `lead.py` | §§4.1, 9 |
| private Planner, Worker, Validator contracts | `contracts/planner.md`, `worker.md`, `validator.md` | §§4–5 |
| CLI, prior evidence, status, diagnosis | `cli.py`, `scripts/stt.py` | §§12–13 |
| focused qualification and document checks | `tests/concepts/stt/` | §§14–15 |

Files may be consolidated when one owner and one proof path remain clear, because incidental module boundaries are not architecture.

Files are split only after coupling or tests show a concrete need, because speculative layers make the MVP harder to verify.

---

## 4. Shared implementation rules

### 4.1 Canonical control data

All identity-bearing control JSON uses one bounded canonical serializer and parser, because independent readers must derive identical bytes and hashes:

- UTF-8;
- sorted object keys;
- stable compact separators;
- one final LF;
- duplicate-key rejection;
- no NaN or Infinity;
- explicit schema identity;
- configured byte and nesting safeguards

Identity hashes bind exact canonical bytes rather than reconstructed objects, because parser-dependent reconstruction can silently change identity.

### 4.2 One schema source

Bootstrap, Boundary, Lead, adapters, CLI, and tests import the same canonical schema definitions, because duplicate field vocabularies can diverge.

Prompt output schemas are generated from those definitions where practical, because handwritten prompt copies can weaken mechanical acceptance.

### 4.3 Error and public-state separation

Internal errors remain typed and narrow while public outcomes use the architecture’s semantic judgments and operational states, because implementation detail must not expand the public lifecycle vocabulary.

### 4.4 Architecture-owned meaning

Code comments and tests link to architecture sections rather than restating semantic rules, because duplicated prose becomes competing authority.

---

# Slice 1 — Persistence, ledger, and host floor

## 5. Outcome

Slice 1 produces trustworthy create-only state and pure state derivation before any model call, because later semantic work depends on durable replay boundaries.

## 6. Required implementation

Implement the following mechanisms, because each one is required to commit and reconstruct lifecycle facts:

- canonical control serialization and hashing;
- create-only regular-file publication;
- same-parent temporary construction and atomic rename;
- flush, reread, and verification;
- one per-Run conforming-writer lock;
- append-only hash-chained Task ledger;
- verified transition packages with expected prior head and exact pending event;
- narrow completion of uniquely eligible non-effectful packages;
- narrow torn-tail handling;
- pure derivation of architecture §13 states

Implement the exact event vocabulary from architecture §10 without a mutable cursor, because a second state authority would make resume ambiguous.

Reject stale heads, competing packages, sequence gaps, interior corruption, and identity mismatch, because ambiguous histories cannot be repaired mechanically.

## 7. Proof links

Slice 1 completes `Q01`–`Q03`, because storage and resume primitives must fail before semantic execution depends on them.

---

# Slice 2 — Bootstrap, frozen runtime, root identity, and prior import

## 8. Outcome

Slice 2 publishes one valid Run and root Task from frozen caller-owned semantics, because Bootstrap must not invent mission meaning.

## 9. Required implementation

Implement exact parsing and freezing of `RootTaskSpec`, routing, operational safeguards, target identity, live-provider authorization, and optional prior selectors, because same-Run execution must depend only on immutable current-Run records.

Remove Task-depth, total-Task, Round, and Plan-step count fields from the active root schema, because the architecture delegates semantic continuation to Planner and Validator.

Implement source/target equality or mutual non-containment, disjoint Run root, explicit runtime-manifest closure, symlink and special-file rejection, mixed-generation detection, and re-execution from the frozen copy, because self-modification must not replace the controller.

Implement the supported-host probes from architecture §11 before publication, because unsupported publication, locking, process, or read-tool behavior invalidates the promised integrity boundary.

Resolve and freeze selected initial inputs and selected committed prior-Run evidence before root Task publication, because later source mutation must not rewrite current evidence.

Never reread mutable task-spec, routing, initial-input source, or prior-Run source after publication, because resume must reconstruct from the Run itself.

## 10. Proof links

Slice 2 completes `Q04`–`Q06`, because root identity and runtime closure must be proven before provider work begins.

---

# Slice 3 — Canonical contracts, authority, artifacts, and STT history tools

## 11. Outcome

Slice 3 provides the minimum exact records required for admission and substitution safety while making the complete persisted STT freely readable, because contextual visibility and authoritative use have different contracts.

## 12. Canonical contracts

Implement canonical immutable records for the following concepts, because each participates in identity, authority, or result binding:

- Run, Task, Round, parent lineage, OperationRequest, and Attempt;
- RootAuthoritySpec, TaskAuthority, Worker routes, command profiles, and effect classes;
- Plan and `worker | command | task` steps;
- exact effectful-step dependencies and their resolutions;
- OutputRequirement, ArtifactRef, role results, and Boundary-owned StepResult;
- Validator judgment and disposition

Do not implement `EvidenceBindingView`, `ArtifactView`, `TaskHistoryView`, or another curated visibility layer as the only way to inspect current STT history, because architecture §5 makes the filesystem itself authoritative context.

Keep exact binding only for cross-Run import, exact effectful inputs, output satisfaction, and request/result identity, because contextual reading does not require consumer authorization.

Validate child authority as equal to or narrower than parent authority without comparing mission hashes, because operational delegation must not expand while semantic continuation remains free.

### 12.1 Read-only STT history tools

Implement a provider-usable read-only tool surface rooted logically at the current Run, because Planner and Validator need ordinary filesystem access without write capability or data packaging.

The minimum tool surface supports the following operations, because navigation, targeted reading, and search cover the filesystem workflows discussed in the architecture:

```text
list
stat
find
read
read_range
grep
json_query
```

The tool surface accepts only STT-relative paths and prevents traversal, symlink escape, special-file access, and writes, because free context access does not include lifecycle mutation.

The tool surface supports repeated and ranged reads rather than one global content package, because large histories must remain accessible without one prompt-sized transfer.

Planner and Validator receive full current-Run access automatically, because their semantic mandates require complete history.

Planner may grant full access or an STT-relative starting subtree to an admitted Worker or other planned semantic entity, because delegated reasoning may need earlier context.

Each outer operation receives the complete committed STT prefix that existed at its start, because stable prior history is reconstructible while partially written current-operation capture is not.

Every tool request persists exact source identities or ranges and every generated search result inside the enclosing Attempt capture, because immutable direct-read source bytes need not be duplicated and context use should not create one ledger event per read.

The tool may expose a virtual root rather than the host’s canonical Run path, because complete content access does not require disclosure of unrelated host-location authority.

### 12.2 Workspace context

Persist one deterministic target workspace index before each Planner call, because the Planner needs current structure without broad target mutation capability.

Treat the index as context only and reobserve exact target inputs before effectful launch, because target state can change after planning.

## 13. Proof links

Slice 3 completes `Q07`–`Q11`, because schema binding and free history access must be proven together rather than through competing context systems.

---

# Slice 4 — Exchange, launcher, providers, and commands

## 14. Outcome

Slice 4 provides one mandatory outer-operation boundary, because launch identity, capture, settlement, and replay prevention must have one owner.

## 15. Required implementation

Publish the exact OperationRequest before the launch marker and publish the marker immediately before launch, because absence or presence of the marker decides whether launch is still permitted.

After a marker exists, reject every path that could launch the same OperationRequest again, because post-launch retry can replay hidden target or external effects.

Implement the architecture §8 return and settlement algebra exactly, because malformed return, no return, and unsettled work have different consequences.

Persist bounded stdout, stderr, raw return, tool transcript, timing, process-group observations, and truthful truncation facts, because later Validator and operator reasoning depend on captured reality.

Construct disposable exchanges where needed and import accepted outputs by bytes through Boundary, because lower-trust output locations are not authoritative.

Revalidate frozen runtime, Run, target identity, current Task/Round/request, and committed ledger prefix after each outer call, because lower-trust activity must not mutate control state unnoticed.

Provide a deterministic fake provider plus thin controlled Claude Code and Codex adapters, because qualification needs inspectable behavior and the MVP needs real routes without semantic logic inside adapters.

Adapters record requested routing and truthful `UNKNOWN` for unobservable actual routing or isolation, because requested model and effort are not proof of supplied execution.

Command execution uses one named frozen profile, exact argv rendering without shell interpolation, admitted cwd and typed arguments, fixed environment policy, accepted exit set, and executable identity revalidation, because arbitrary command construction would bypass root authority.

## 16. Proof links

Slice 4 completes `Q12`–`Q15`, because launch and adapter behavior must be proven before semantic orchestration uses it.

---

# Slice 5 — Planner, Worker, commands, and child Tasks

## 17. Outcome

Slice 5 executes Planner-selected work without adding semantic restrictions absent from the architecture, because Planner owns decomposition while Boundary owns admission.

## 18. Planner

Construct each Planner request from the exact mission, required outputs, operational authority/profile descriptions, current Task/Round identity, workspace index location, and full STT read-tool capability, because Planner should navigate persisted history rather than receive a runtime-curated substitute.

Accept only a correctly bound immutable `PLAN` or `DECLINE`, because execution needs one exact planning result even though semantic content remains trusted.

Do not reject a Plan for same-mission children, recursion depth, total child count, step count, continuation style, or semantic similarity, because those decisions belong to Planner.

Plan validation rejects only schema, identity, ordering, dependency, and operational-authority defects, because mechanical admission must not become semantic review.

A settled Planner failure produces no accepted Plan and proceeds to Validator, because Validator still owns Task-level continuation and completion.

### 18.1 Worker and command steps

Resolve exact effectful inputs immediately before launch and reverify target identities, because accepted planning must not silently bind to changed bytes.

Verify declared outputs and persist best-effort effect reports, because local outcomes need exact evidence without a complete-effect claim.

Stop later steps after any non-satisfied accepted step outcome or settled non-OK call, because later work must not assume a failed prerequisite.

Stop later steps after any reported out-of-scope effect even when the accepted local outcome is satisfied, because known violation must not be compounded.

Map settled `ERR`, `REJECTED`, and `NO_RETURN` to `INDETERMINATE` evidence without an accepted role result, because transport failure is not semantic proof.

### 18.2 Child Tasks

Create child identity from the accepted Task step without an ancestor-mission inequality check or mandatory mission-relation justification, because same-mission continuation is valid Planner behavior.

Create child authority from an equal or narrower declarative grant and the unchanged target identity, because child operational capability may not expand.

Execute children depth-first and map their results exactly as architecture §9 requires, because parent validation must distinguish semantic child outcomes from settled or unsettled operational failure.

## 19. Proof links

Slice 5 completes `Q16`–`Q20`, because planning freedom, execution admission, and child propagation must be proven as one vertical path.

---

# Slice 6 — Validator, automatic Rounds, and finalization

## 20. Outcome

Slice 6 gives Validator complete persisted context and implements its judgment without a mechanical progress veto, because Validator owns semantic completion.

## 21. Validator request and tools

Construct each Validator request from the exact mission, required outputs, current Task/Round identity, operational facts, and full STT read-tool capability, because Validator should inspect any persisted record it judges relevant.

Do not build a bounded evidence index as the exclusive context, because omission by Boundary must not masquerade as irrelevance.

Do not prohibit Validator `REPEAT` after `DECLINE`, no accepted Plan, repeated hashes, unchanged observations, or prior Rounds, because those facts inform but do not replace Validator judgment.

### 21.1 Accepted result

Accept a correctly bound result containing architecture §4.4 judgment, disposition, reason, findings, unknowns, and terminal-output selections when applicable, because Boundary needs one exact semantic result to commit.

Reject `SATISFIED + REPEAT` and structurally invalid output selections, because those cases contradict the terminal contract.

Do not enforce a Round-cap, current-Round novelty, selected-evidence, hard-blocker, or better-basis predicate, because those were removed as semantic runtime restrictions.

Persist duplicate identities, previous reports, and all earlier Round files so Validator can inspect them, because semantic detection of repetition belongs to the thinking entity.

### 21.2 Automatic continuation

Commit an accepted `REPEAT` as `ROUND_FINISHED`, derive `NEEDS_ROUND`, create the next contiguous Round, and continue the same `stt start` or `stt run` invocation, because Validator already authorized continuation.

Bind the preceding Validator report as the immediate Round reason without copying the complete history into a new package, because the new Planner can read the existing Task tree directly.

Use fresh Planner, operation, step, child, and Validator identities in every new Round, because automatic continuation is not retry.

A settled Validator non-OK call derives `OPERATIONALLY_STOPPED` without a mission judgment, because no semantic result exists.

An unsettled or unknown operation derives `OPERATIONALLY_BLOCKED` and prevents ancestor validation, because judgment must not race active local work.

## 22. Proof links

Slice 6 completes `Q21`–`Q23`, because Validator freedom and automatic Round mechanics must be tested without reintroducing the removed gates.

---

# Slice 7 — CLI, diagnosis, prior evidence, integration, and qualification

## 23. Outcome

Slice 7 exposes the architecture through stable public operations and proves the whole runtime, because a correct internal lifecycle is insufficient if operators receive misleading behavior.

## 24. CLI and state

Implement the public commands from architecture §13 without superseded semantic flags, because root semantics must enter through one frozen specification.

`start` and `run` continue automatically through children and repeated Rounds until an architecture stop state occurs, because ordinary continuation is internally authorized.

`status` and `diagnose` acquire the read strategy safely, report exact derived state and blocker, and never repair automatically, because observation must not mutate the Run.

Remove `AWAITING_REPEAT` from active state, output, and resume logic, because accepted `REPEAT` now transitions directly to `NEEDS_ROUND`.

### 24.1 Prior evidence

Validate only caller-selected committed prior references and import exact bytes before root Task publication, because cross-Run context must remain explicit and immutable.

Never merge prior ledgers, Tasks, Rounds, or cursors, because current lifecycle state must derive only from the current Run.

### 24.2 Regression and promotion

Run focused STT tests, compile checks, formatting and lint checks, shell fixtures, runtime-closure checks, `git diff --check`, and the full repository suite, because implementation proof must include repository compatibility.

Run the mechanical WELL checker and manual WELL review on both documents, because literal `because` is necessary but not sufficient for valid warrants.

Run the full RunSkeptic loop on the unchanged pair and implementation diff, because convergence rather than one favorable review is the promotion condition.

## 25. Proof links

Slice 7 completes `Q24`–`Q27`, because public integration, semantic evaluation, regression, and promotion close the implementation claim.

---

## 26. Canonical qualification catalog

This is the only numbered executable scenario catalog, because duplicate proof catalogs create competing coverage authority.

Each scenario is parameterized over positive and known-bad cases, because separate IDs for every malformed field would add volume without adding a distinct invariant.

### Persistence, Bootstrap, and identity

- `Q01` **Canonical bytes and ledger** — serializer/parser agreement, one-byte identity change, valid event order, duplicate/gap/history mutation rejection, and narrow torn-tail handling
- `Q02` **Transition packages and state derivation** — valid commit, stale head, competing package, package/event mismatch, pure state derivation, and transient-outcome exclusion
- `Q03` **Crash and resume** — pre-Round Task, prelaunch request, complete package before event, ambiguous launched operation, child-to-parent finalization, Validator-to-Round finalization, FINISH-to-Task finalization, and REPEAT-to-next-Round finalization
- `Q04` **RootTaskSpec and no semantic caps** — complete frozen root starts while missing or mutable fields reject; active schema contains operational safeguards but no Task-depth, Task-count, Round-count, or Plan-step-count limit
- `Q05` **Frozen runtime, locations, and host floor** — source/target equality or disjointness, Run-root separation, runtime-manifest closure, mixed-generation rejection, self-modification survival, lock/publication/process/read-tool probes, and fail-before-publication behavior
- `Q06` **Prior and initial evidence** — exact selection, current-Run import, origin preservation, prior-root independence after publication, and rejection of ambient or uncommitted prior state

### Authority, contracts, and persisted context

- `Q07` **Operational authority** — target-relative containment, symlink/special/`.git` rejection, route/profile/effect/environment admission, equal-or-narrower child authority, and no mission-based child rejection
- `Q08` **Artifact and result binding** — exact effectful dependencies, output requirements, ArtifactRef provenance, target reverification, request/result binding, wrong-producer/consumer substitution rejection, and no fabricated StepResult
- `Q09` **Complete STT persistence** — every Bootstrap, planning, tool, step, child, validation, capture, rejection, violation, and terminal record is retained or explicitly labelled truncated/omitted
- `Q10` **Planner and Validator history access** — both can list, find, read, range-read, grep, and query every retained file in the committed current-Run prefix through a read-only virtual root without prior selection or curated-package dependence
- `Q11` **Delegated history access** — Planner can grant full or subtree read access to an admitted planned semantic entity while writes, path escape, and ungranted access reject; tool transcripts remain within the enclosing Attempt rather than separate ledger steps

### Launch and effectful execution

- `Q12` **Exchange and post-call integrity** — admitted bytes and tool surface only, output import by bytes, control-state revalidation, and invalidation after unauthorized authoritative mutation
- `Q13` **Call and settlement algebra** — every valid and invalid return/result/settlement combination, truthful truncation, local-only settlement meaning, and no semantic coercion
- `Q14` **Exactly one launch** — marker ordering, allowed prelaunch reevaluation, forbidden post-launch replay for every role, and `NON_RESUMABLE` after ambiguous launched interruption
- `Q15` **Provider and command adapters** — fake plus controlled Claude/Codex routes, truthful requested/observed routing, no semantic fallback, exact command profile and argv, inherited-secret non-persistence, and representative command usability
- `Q16` **Worker and command outcomes** — live-target create/edit/move/delete, output verification, accepted local judgments, settled non-OK to `INDETERMINATE`, and later-step stop
- `Q17` **Reported scope violation** — exact persistence, later-step stop even after local success, Validator launch only after settlement, `INVALID` after STT mutation, `OPERATIONALLY_BLOCKED` after unsettled work, and no unreported-effect claim

### Planner, child, Lead, and Validator

- `Q18` **Planner freedom** — direct, investigative, zero-step, and decline Plans; same-mission child; child depth and count beyond prior caps; no semantic similarity, novelty, or continuation rejection; only structural and operational defects reject
- `Q19` **Mechanical Lead** — one active depth-first frontier, ordered steps and children, compact receipts, no direct provider/storage mutation path, and automatic traversal through newly accepted `REPEAT`
- `Q20` **Child propagation** — semantic mapping, settled child stop to parent operational indeterminate and parent audit, unsettled/unknown whole-Run block, invalid child, and same-mission lineage identity
- `Q21` **Validator context and judgment** — complete history tools, independent invocation, all valid judgment/disposition combinations, output-selection checks, and no exclusive bounded evidence index
- `Q22` **Automatic unlimited REPEAT** — controlled fake Validator repeats beyond prior caps, contiguous fresh Rounds, all previous reports readable, latest report bound as immediate reason, no caller gate, no novelty floor, and eventual FINISH
- `Q23` **Failure routing** — settled Planner/Worker/command failure reaches Validator as specified, settled Validator failure stops without judgment, and unsettled/unknown work prevents validation

### Public integration and semantic qualification

- `Q24` **CLI and diagnosis** — immutable start inputs, automatic run advancement, exact public states, read-only status/diagnose, retention warnings, and no `AWAITING_REPEAT`
- `Q25` **Instruction trust and secret boundary** — private-contract precedence, target/prior/report injection resistance, no intentional credential persistence, and honest limits on arbitrary returned secrets
- `Q26` **Representative real-model evaluation** — adversarial cases for history use, same-mission continuation, success/failure/indeterminate judgment, productive repeat, stagnation, circularity, and far failure, with results reported as empirical evidence rather than proof
- `Q27` **Repository and promotion** — plain and Git targets, runtime closure, focused and full regression, active-document superseded-concept rejection, WELL review, RunSkeptic convergence, and exact accepted-pair commit recording

---

## 27. Superseded-concept checks

Static checks reject the following concepts in active STT architecture, implementation, private contracts, schemas, state derivation, and user-facing runtime text, because their reappearance would silently restore rejected semantics:

```text
maximum_task_depth
maximum_tasks_per_run
maximum_rounds_per_task
maximum_steps_per_round
AWAITING_REPEAT
caller-mediated REPEAT
one repeat per invocation
distinct or narrower child mission
ancestor mission hash rejection
mandatory mission relation reason
Validator remaining Round capacity
REPEAT novelty floor
selected evidence as Validator visibility boundary
Planner or Validator has no read tools
TaskHistoryView
```

Tests and migration notes may mention a superseded term only when explicitly asserting its rejection, because proof fixtures must be able to name the behavior they prevent.

---

## 28. Definition of done

The implementation is done only when all of the following conditions hold, because partial compliance would leave unproved architecture behavior:

- `Q01`–`Q27` pass;
- focused STT tests pass;
- compile, formatting, lint, shell, and `git diff --check` pass;
- runtime-manifest closure passes;
- the full repository suite passes;
- no duplicate lifecycle or schema authority remains;
- no active superseded concept remains;
- representative real-model evaluation is recorded honestly;
- the unchanged architecture and implementation plan pass WELL and RunSkeptic;
- the accepted pair’s containing commit is recorded as the implementation base

Implementation stops at that point, because additional generalization would exceed the accepted MVP.
