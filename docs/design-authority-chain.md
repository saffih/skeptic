# Design Authority Chain

This document defines how planning and design authority flows from accepted needs into realization and evidence, because incremental work fails when required meaning is missing, duplicated, or introduced too late.

Every planning or design artifact that defines or justifies design must conform to WELL, because its propositions must remain warranted, explicit, lean, and linked.

The Design Authority Chain is the logical path governing one bounded change rather than a required set of files, because authority depends on owned meaning rather than document count.

## Links

The chain assigns one distinct role to each link, because each normative meaning and evidence obligation needs a canonical owner:

| Link | Owns | Boundary |
|---|---|---|
| Governing Inputs | accepted objectives, constraints, requirements, and external authority, each with an accountable owner | design may interpret but not silently redefine them |
| Architecture Description | system-wide semantics, boundaries, invariants, authority, quality constraints, and architecturally significant decisions | every conforming realization preserves this meaning |
| Software Design Description | architecture-permitted shared or durable realization choices, including components, contracts, schemas, mechanisms, dependencies, and qualification strategy | dependent scopes use one canonical realization |
| Implementation Plan | exact construction, verification, pass, stop, and escalation conditions for one bounded scope, derived from current governing design | realization requires no new system-wide, shared, durable, or externally required decision |
| Realization | work that enacts accepted design plus local replaceable choices | material design meaning remains owned by a governing link |
| Verification Evidence | observations, tests, and checks of the Realization against Governing Inputs, design, and plan | evidence may corroborate or refute but does not own design |

## Rules

The chain obeys the following rules, because missing, duplicated, or bypassed links create drift:

| Rule | Protection |
|---|---|
| one current owner for each normative meaning | no competing authority |
| downstream refinement only within variation permitted upstream | detail cannot redefine governing meaning |
| newly discovered objectives, constraints, requirements, or external authority return to Governing Inputs before dependent work continues | design cannot acquire product authority |
| newly discovered system-wide design decisions return to the Architecture Description before dependent work continues | local work cannot acquire architecture authority |
| newly discovered shared or durable realization decisions return to the Software Design Description before dependent work continues | local work cannot acquire shared design authority |
| local replaceable choices unused outside one realization unit may remain in the realization | incidental choices do not create documentation ceremony |
| links may share an artifact, and an inapplicable link may be omitted, when ownership and derivation remain explicit | the chain is logical rather than ceremonial |
| completed Implementation Plans become historical evidence unless retained without duplicating current authority | obsolete instructions cannot compete with maintained design |

`verification-and-qualification-ownership` — Verification and qualification do not own design authority, because evidence evaluates governed meaning rather than defining it. Each governing link must nevertheless state the verification or qualification obligations appropriate to the meaning it owns, because shared qualification strategy belongs to the Software Design Description and exact verification procedures, evidence outputs, and pass, stop, and escalation conditions belong to the applicable Implementation Plan. Resulting Verification Evidence records observations against those obligations and returns any material contradiction or unresolved result to the link that owns the affected meaning, because downstream evidence may challenge authority but must not silently replace it.

## Incremental use

Incremental work uses the following gates, because complete governing meaning and bounded execution detail prevent both gaps and premature design:

| Gate | Requirement |
|---|---|
| Governing basis | Governing Inputs are identified and accepted by accountable owners; each applicable Architecture Description or Software Design Description covers the meaning it owns; any unresolved governing unknown or conflict that could invalidate the selected scope blocks it |
| Current scope | when an Implementation Plan is applicable, only the selected scope requires exact detail; later scopes require enough design to expose dependencies that could invalidate the selected scope |
| Plan contents | an applicable Implementation Plan identifies governing links; exact scope and exclusions; affected artifacts and interfaces; mechanisms and ordering; verification procedures; pass, stop, and escalation conditions |
| Start | realization begins only from the recorded unchanged applicable governing links accepted for that scope; Realization and Verification Evidence are downstream results |
| Change | a change to a governing input, design, or plan link invalidates dependent acceptance until the changed chain is reviewed again |
| Completion | observed evidence supports the claimed result, or each discrepancy returns to the link responsible for the affected governing input, design, plan, realization, or evidence before dependent work continues |

The governing project defines required artifacts, review methods, and promotion gates, because the Design Authority Chain defines authority and refinement rather than one universal delivery process.
