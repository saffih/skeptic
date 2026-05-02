# CID Domain Questions — Target-Relevant Questions

Loaded at APPLY when relevant to the target. Not needed for idle/monitoring cycles.
Each finding → ACTION, CONFLICT, or EXEMPLAR.

Domains: SEC for input/credentials; CPX for code/architecture; REL for broad reviews; DAT for I/O, DB, network; ARC for multi-module; CFT for tests.
Apply relevant domains first. If relevance is unclear, sample likely domains; expand when findings indicate cross-domain impact or high risk.

Parallelize by domain group: SEC+DAT, CPX+ARC, REL+CFT.

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
CPX2. Code that should be data (lookup table, config, enum)?
CPX3. State implicit and scattered vs explicit and managed?
CPX4. Simple (few independent parts), or just familiar?
CPX5. How many things must you hold in your head to understand this?

---

## RELIABILITY (REL)

REL1. No monitoring — how would you know this is silently broken?
REL2. What fails at 10x scale?
REL3. What external dependency could break this without any code change?
REL4. Bus factor — who knows this, and what if they leave?
REL5. Single source of truth for each important datum?
REL6. Who owns this part or datum, and who is allowed to change it?
REL7. Is ownership/current responsibility clear enough to operate safely?

---

## DATA (DAT)

DAT1. Every external call (subprocess, network, DB) timed out?
DAT2. Race condition? Locks minimal and correct?
DAT3. What happens when disk is full or filesystem is read-only?
DAT4. Encoding explicit (UTF-8) or assumed?
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
CFT2. Error message tells you HOW to fix it?
CFT3. Test mocks so much it only tests the mock?

---

## Domain Group Parallelization

For broad scope (>20 files), parallelize by domain group:

- **SEC+DAT**: Security + Data (8 + 4 = 12 questions)
- **CPX+ARC**: Complexity + Architecture (5 + 3 = 8 questions)
- **REL+CFT**: Reliability + Craft (5 + 3 = 8 questions)

This reduces total questions per file while ensuring comprehensive coverage.

---

## When to Apply

**Apply all domains when**:
- Scanning code/artifacts
- Unsure which domain is relevant
- Missed issues cost more than noise

**Skip domain questions when**:
- Idle cycles
- Monitoring cycles
- Task-only cycles
- Non-code artifact review (use Thinkers only)

---

## Question Count by Domain

- **SEC**: 8 questions
- **CPX**: 5 questions
- **REL**: 7 questions
- **DAT**: 7 questions
- **ARC**: 6 questions
- **CFT**: 3 questions

**Total**: target-relevant question set; count varies by selected domains

---

## Finding Classification

Each domain question can result in:
- **[ACTION]**: Fix needed
- **[CONFLICT]**: Decision needed (two reasonable approaches)
- **[EXEMPLAR]**: Pattern worth replicating (OPTIMAL or SATISFICING)

---

**Document Owner**: Skeptic Methodology  
**Review Date**: Quarterly  
**Status**: ACTIVE
