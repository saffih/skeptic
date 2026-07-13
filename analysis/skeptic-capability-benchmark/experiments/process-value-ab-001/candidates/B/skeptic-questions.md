# CID Domain Questions

Target-relevant questions loaded at APPLY when relevant to the target.

This file is a detection aid, not a second runtime contract.
The core `skeptic.md` remains authoritative.

Use domain questions only when runtime detail is not enough, confidence is weak, findings cross domains, or risk justifies deeper probing.

Each domain probe can surface:
- PASS: no material issue found with sufficient evidence
- ACTION: fix, safeguard, test, owner, or follow-up needed
- CONFLICT: decision needed

Positive patterns may be noted as observations, but they are not final output categories.

Domains:
- SEC: Security / input / credentials / permissions / exposure
- CPX: Complexity / coupling / state / mental load
- REL: Reliability / scale / operations / ownership
- DAT: Data / I/O / persistence / consistency / timing
- ARC: Architecture / interfaces / contracts / dependencies
- CFT: Craft / tests / errors / mocks

Apply likely relevant domains first.
If relevance is unclear, sample likely domains.
Expand when evidence, weak confidence, cross-domain findings, or high risk require it.

Do not apply all domains by default.

## Parallelization

For broad scope, parallelize by domain group:
- SEC+DAT: Security + Data
- CPX+ARC: Complexity + Architecture
- REL+CFT: Reliability + Craft

Use parallelization to reduce repeated scanning, not to force every domain onto every artifact.

---

## SECURITY (SEC)

SEC1. PII in shared or public files?
SEC2. Subprocess or command from unsanitized user input?
SEC3. File read/written without permission check?
SEC4. Test-data vs real-data boundary enforced?
SEC5. Error messages expose internal paths or stack traces?
SEC6. Authentication check that can be bypassed?
SEC7. Symlinks validated before following?
SEC8. Secrets suppression that can be circumvented?

---

## COMPLEXITY (CPX)

CPX1. Independent concerns tangled in one function?
CPX2. Code that should be data, such as lookup table, config, or enum?
CPX3. State implicit and scattered vs explicit and managed?
CPX4. Simple, with few independent parts, or just familiar?
CPX5. How many things must you hold in your head to understand this?

CPX6. When an artifact creates or expands a process, review,
governance, orchestration, or verification layer, does it prevent
a named material failure or unlock a necessary decision, and is a
simpler control sufficient?

Activation rule:

Apply CPX6 only when a process or control layer is materially part
of the target. Do not activate it for routine tasks or controls
whose necessity is already clear.

---

## RELIABILITY (REL)

REL1. No monitoring: how would you know this is silently broken?
REL2. What fails at 10x scale?
REL3. What external dependency could break this without any code change?
REL4. Bus factor: who knows this, and what if they leave?
REL5. Single source of truth for each important datum?
REL6. Who owns this part or datum, and who is allowed to change it?
REL7. Is ownership/current responsibility clear enough to operate safely?

---

## DATA (DAT)

DAT1. Every external call, such as subprocess, network, or DB, timed out?
DAT2. Race condition? Locks minimal and correct?
DAT3. What happens when disk is full or filesystem is read-only?
DAT4. Encoding explicit, such as UTF-8, or assumed?
DAT5. Where is this data authored?
DAT6. How often is it updated relative to reality?
DAT7. Who consumes it, and is consistency preserved over time?

---

## ARCHITECTURE (ARC)

ARC1. Implicit dependency that would surprise a new contributor?
ARC2. Circular dependency between modules?
ARC3. Data flow traceable from input to output?
ARC4. Interfaces/contracts explicit and correct?
ARC5. Relationship exists but is not written down?
ARC6. Connection missing, accidental, or misplaced?

---

## CRAFT (CFT)

CFT1. Test names describe behavior, not implementation?
CFT2. Error message tells you how to fix it?
CFT3. Test mocks so much it only tests the mock?

---

## When to Apply

Apply domain questions selectively.

Start with likely relevant domains.

Expand only when:
- evidence crosses domains
- confidence remains weak
- risk is high
- a finding exposes security, data, architecture, reliability, complexity, or craft uncertainty

Do not apply all domains by default.
Do not treat this file as a second runtime contract.
The core `skeptic.md` remains authoritative.

Skip domain questions when:
- idle cycles
- monitoring cycles
- task-only cycles
- non-code artifact review where Thinkers and Structural Checks are sufficient

---

## Question Count by Domain

- SEC: 8 questions
- CPX: 5 questions
- REL: 7 questions
- DAT: 7 questions
- ARC: 6 questions
- CFT: 3 questions

Total: target-relevant question set; count varies by selected domains.

---

## Finding Classification

Domain probes can surface:
- PASS: no material issue found with sufficient evidence
- ACTION: fix, safeguard, test, owner, or follow-up needed
- CONFLICT: decision needed

Positive patterns may be noted as observations, but they are not final output categories.

---

Document Owner: Skeptic Methodology
Review Date: Quarterly
Status: ACTIVE
