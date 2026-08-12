# Sequential Target Task MVP Governing Inputs

**Accountable owner:** STT product owner, because accepted product decisions need an accountable authority.
**Applies to:** STT MVP Architecture Description and every dependent design or implementation artifact, because downstream work may interpret but not redefine these inputs.
**Authority link:** Governing Inputs in the Design Authority Chain, because this document owns the chain's accepted product meaning.
**Document profile:** WELL, because this document defines and justifies design inputs.

This document owns the accepted objectives, constraints, and trade-offs that warrant the STT architecture, because architecture may interpret product decisions but may not silently create or redefine them.

## Accepted decisions

### `product-identity` — Product identity

The product is named **Sequential Target Task (STT)**, because sequential execution is the objective architectural property while `safe` would imply containment and guarantees that the MVP does not provide.

### `product-objective` — Product objective

STT executes one immutable mission against a live target through trusted planning, Boundary-mediated sequential execution, independent validation, and durable evidence, because ordinary agent work can lose mission identity, exceed admitted authority, depend on hidden context, or claim completion without adequate evidence.

### `simplicity-and-robustness` — Simplicity and robustness

STT uses the smallest architecture that preserves mission identity, admitted authority, durable history, independent judgment, and honest recovery, because unnecessary mechanisms increase implementation risk and obscure the few protections the product actually needs.

### `sequential-lifecycle` — Sequential lifecycle

One Run has one active lifecycle frontier and performs no concurrent STT operation, because sequential control makes ordering, ownership, persistence, and recovery understandable without concurrency coordination.

### `trusted-thinking` — Trusted thinking

Planner owns semantic decomposition and Validator owns Task-level judgment and continuation, because mechanical rules cannot reliably decide how to solve an open mission or whether the accumulated result is sufficient.

### `execution-economy` — Execution economy

Planner selects the deterministic mechanism or lowest permitted agent capability it judges adequate for each planned step, because semantic difficulty belongs to planning judgment while unnecessary model capability adds cost without adding value.

### `planning-and-validation-capability` — Planning and validation capability

Planner and Validator use routes that meet a configured trusted minimum capability, normally a frontier-capable model with only the reasoning and context needed for the mission, because weak planning or validation can make every downstream economy false.

### `mission-routing-constraints` — Mission routing constraints

The mission or Run policy may constrain permitted providers, capability levels, cost preference, or quality preference without prescribing every step route, because product authority should bound Planner judgment without replacing it.

### `boundary-mediation` — Boundary mediation

Every lifecycle transition and every effectful operation passes through Boundary, because one mechanical authority must enforce identity, operational admission, persistence, launch, result binding, and failure visibility.

### `context-rules-adoption` — Context Rules adoption

STT adopts the portable Context Rules contract as an accepted context-handling constraint subject to these Governing Inputs and STT authority, because one portable owner should define the generic rule while STT owns only the product decision to adopt it. The historical Context Stewardship contract is not an STT authority or retained exception, because Context Rules supersedes it for this purpose.

STT keeps durable substantive state in authoritative readable files, exchanges stable artifact references rather than repeated bodies, and gives each semantic operation a bounded working set sufficient for its obligation that the responsible semantic role may expand when evidence requires it, because model context is scarce but context economy is subordinate to correct judgment.

When substantial interpretation is likely to be reused and expected downstream savings materially exceed creation cost and omission risk, the interpreting role must leave a source-bound, grep-friendly digest; the digest remains derived, traceable to authoritative evidence, and insufficient wherever freshness, completeness, absence, contradiction, independence, or decision-critical support requires source review, because reusable understanding should reduce rereading without becoming a second source of truth.

### `semantic-continuation` — Semantic continuation

Architecture defines no independent fixed total within a Run for Task count, Task depth, Plan steps, Rounds, or semantic calls, because arbitrary lifecycle or reasoning counts would override Planner and Validator judgment while finite per-operation representation, transport, capture, wait, and host limits remain legitimate implementation safeguards.

### `interrupted-effects` — Interrupted effects

STT does not automatically relaunch an operation when committed history shows that it started or leaves its launch uncertain, because the operation may already have affected the live target even though the Run is single-threaded.

### `canonical-naming` — Canonical naming

STT accepts one canonical case-sensitive spelling for each STT-owned name and rejects noncanonical spellings, because one spelling prevents internal ambiguity and search collisions while character and separator conventions belong to software design.

### `target-path-authority` — Target-path authority

Every admitted target effect must identify the intended object inside the granted target scope and fail closed when that identity cannot be established, because textual path permission must not reach protected or out-of-scope state through host-specific resolution behavior.

### `honest-outcomes` — Honest outcomes

Transport completion, local process settlement, and semantic mission judgment remain distinct, because an operation can return or stop without proving that the mission was satisfied.

### `non-goals` — Non-goals

STT does not promise sandbox containment, rollback, exclusive target access, complete external-effect detection, remote quiescence, hostile same-user protection, mission completion, or a fixed total cost, duration, storage size, or reasoning-cycle count, because the MVP coordinates admitted work rather than controlling the operating system, providers, or open target completely.

## Change authority

A proposed change to any named Governing Input requires explicit product-owner acceptance before dependent architecture or design changes, because downstream artifacts may refine Governing Inputs but may not silently alter them.
