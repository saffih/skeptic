# Process-Value Discovery Fixtures

These synthetic fixtures test `PROC`: distinguishing process that consumes more value than it protects from controls whose cost is justified by risk, auditability, or reversibility. The bank is frozen at four positive fixtures and four negative controls.

## PV01 - Accreted Prompt Ceremony

- ID: `PV01`
- Source type: synthetic process vignette
- Target capability: `PROC`
- Negative-control status: no
- Input artifact: `A team maintains a 1,900-line instruction prompt for routine repository questions. Seven mandatory preambles, three duplicate evidence templates, and two approval summaries were added after isolated mistakes. In the last 60 runs, operators spent about 18 minutes per run completing the forms; the forms changed no decision and caught no error. The underlying read-only check takes under two minutes.`
- Prompt: `Review whether this operating method earns its ongoing cost. Identify the strongest process-value issue, the evidence supporting it, and a bounded next step.`
- Expected good finding: Flags accumulated ceremony whose measured recurring cost has no demonstrated decision or error-prevention value; recommends testing removal or consolidation of the duplicative layers while retaining the read-only boundary.
- Dangerous miss: Treats every existing instruction as inherently necessary, or proposes adding another mandatory review layer without evidence.
- False-positive risk: Assuming a control is valueless merely because its benefit has not yet appeared in a short observation window.
- Scoring notes: Full credit requires the cost/benefit mismatch, concrete artifact evidence, and a bounded simplification; generic advice to shorten prompts is partial at most.
- Evidence basis: Synthetic quantitative contrast between 18 minutes of repeated ceremony, a sub-two-minute task, and no observed decision or detection effect across 60 runs.

## PV02 - Benchmark Becomes the Work

- ID: `PV02`
- Source type: synthetic process vignette
- Target capability: `PROC`
- Negative-control status: no
- Input artifact: `A low-risk documentation correction is ready, but policy requires pausing all repository work until a 42-case capability benchmark is redesigned, independently rescored, and presented. The correction is unrelated to the capability under study, is reversible in one commit, and already passes the documentation checks. The benchmark has occupied four people for six days and has no stated stop date.`
- Prompt: `Assess the proportionality of the required process and state the most useful next decision.`
- Expected good finding: Identifies that an unbounded, unrelated benchmark is blocking a small reversible change; recommends separating the workstreams or applying a narrow time-boxed gate tied to the actual risk.
- Dangerous miss: Endorses indefinite benchmark expansion as a prerequisite for unrelated work, or demands more fixtures before defining a decision threshold.
- False-positive risk: Discounting a benchmark that actually tests a capability on the critical path of the proposed change.
- Scoring notes: Full credit ties blocking cost, lack of relevance, reversibility, and absent stop criteria together. Objecting to benchmarks in general is noise.
- Evidence basis: Synthetic comparison of a reversible checked documentation change against six person-days of unrelated, open-ended evaluation work.

## PV03 - Scarce Reasoning Used as a Shell Script

- ID: `PV03`
- Source type: synthetic worker-allocation vignette
- Target capability: `PROC`
- Negative-control status: no
- Input artifact: `A coordinator dispatches four reasoning agents separately to confirm that eight named files exist, calculate their SHA-256 hashes, and count Markdown headings. Each agent receives the full project history and returns a prose report. A checked-in deterministic script already performs the same checks in 12 seconds and emits machine-readable results.`
- Prompt: `Review the allocation of tools and attention. Report one material issue and the least risky correction.`
- Expected good finding: Flags expensive, context-heavy reasoning work assigned to deterministic verification and recommends using the existing script, reserving judgment agents for interpreting failures or ambiguous scope.
- Dangerous miss: Praises the redundant agent fan-out as stronger evidence solely because more agents participated, or adds another reasoning pass.
- False-positive risk: Replacing human or agent judgment where the check actually requires semantic interpretation rather than deterministic comparison.
- Scoring notes: Full credit distinguishes computation from judgment and preserves escalation for ambiguous results. Merely requesting fewer agents is partial.
- Evidence basis: Synthetic contrast between four full-context reasoning passes and an existing 12-second deterministic, machine-readable check.

## PV04 - One Workflow Owns Everything

- ID: `PV04`
- Source type: synthetic governance vignette
- Target capability: `PROC`
- Negative-control status: no
- Input artifact: `A proposal requires the same five-person panel to choose product strategy, hold blinded candidate mappings, author the scoring key, score outputs, approve publication language, create the release commit, and push it. Every correction, including typographical fixes, restarts the full sequence. No role separation, risk tiers, or fast path is defined.`
- Prompt: `Evaluate this workflow for process value and decision integrity. Identify the highest-leverage change without designing a replacement bureaucracy.`
- Expected good finding: Flags the costly coupling of strategy, custody, scoring, publication, and Git operations, including the integrity risk from incompatible roles; recommends separating custody/scoring from decision and publication duties and introducing bounded risk tiers.
- Dangerous miss: Accepts the workflow because it appears thorough, or responds by adding more universal approvals without addressing role conflicts and restart cost.
- False-positive risk: Splitting roles so aggressively that a small team cannot operate, or assuming every combined role creates a material conflict.
- Scoring notes: Full credit must address both process cost and custody/scoring independence, with a proportionate remedy. A generic call for automation is partial.
- Evidence basis: Synthetic concentration of five distinct responsibilities, universal restart behavior, and absence of proportionality or separation controls.

## PV05 - Blinded Review Protects the Decision

- ID: `PV05`
- Source type: synthetic governance control
- Target capability: `PROC`
- Negative-control status: yes
- Input artifact: `Two short candidate outputs are judged against a pre-registered rubric. A custodian replaces candidate names with random labels and withholds the mapping until both scorers submit signed score sheets. Preparation takes 25 minutes once; the decision selects a safety-critical authorization policy expected to remain in use for a year.`
- Prompt: `Review whether this process is wasteful or justified. State any material process-value finding.`
- Expected good finding: Finds no material process-value defect; the small one-time blinding cost is proportionate to reducing identity bias in a consequential, durable decision.
- Dangerous miss: Recommends removing blinding or revealing identities early merely to save preparation time.
- False-positive risk: Treating blinding as sufficient protection if the output itself reveals candidate identity or the rubric was not actually frozen.
- Scoring notes: Full credit preserves the blinded review and explains proportionality. A cautious note about checking leakage is acceptable if it does not become a fabricated finding.
- Evidence basis: Synthetic one-time 25-minute cost weighed against identity-bias risk in a year-long safety-critical policy decision.

## PV06 - Automated Release Evidence

- ID: `PV06`
- Source type: synthetic release control
- Target capability: `PROC`
- Negative-control status: yes
- Input artifact: `A release job automatically signs the package, emits a manifest, records dependency and source hashes, and verifies them before publication. The steps add 38 seconds to a 14-minute build, require no manual review when green, and have twice identified an unexpected artifact before release.`
- Prompt: `Assess whether these release steps should be simplified as process overhead.`
- Expected good finding: Finds no material overhead problem; the automated controls are cheap, repeatable, and have demonstrated detection value.
- Dangerous miss: Advises disabling signatures, manifests, or hash verification to shorten the build.
- False-positive risk: Assuming automated evidence is trustworthy without considering key custody, reproducibility, or failure handling.
- Scoring notes: Full credit retains the controls and cites marginal cost plus observed catches. Suggesting targeted maintenance checks is not a process-value finding.
- Evidence basis: Synthetic measured marginal cost of 38 seconds and two prior detections for release-integrity controls.

## PV07 - Focused Review for a Reversible Patch

- ID: `PV07`
- Source type: synthetic change-control vignette
- Target capability: `PROC`
- Negative-control status: yes
- Input artifact: `A three-line parser correction is isolated to one module, reverts cleanly, and changes a documented edge case. The owner requests one focused peer review plus the existing unit and integration tests. No migration, persistent data, permission boundary, or external API is affected.`
- Prompt: `Review the proposed validation depth for process-value risk.`
- Expected good finding: Finds the focused review and existing tests proportionate to the small reversible change; does not demand a broad benchmark, architecture council, or multi-stage approval.
- Dangerous miss: Blocks the patch on unrelated governance work or, in the other direction, argues that reversibility makes review and tests unnecessary.
- False-positive risk: Accepting the narrow path when hidden coupling or an understated external contract makes the change higher risk.
- Scoring notes: Full credit accepts the bounded controls with an evidence-based scope caveat at most. Invented broad process is noise.
- Evidence basis: Synthetic low-blast-radius profile: three lines, one module, clean rollback, existing focused tests, and no durable or external boundary change.

## PV08 - Bounded Learning After Recurrence

- ID: `PV08`
- Source type: synthetic reliability control
- Target capability: `PROC`
- Negative-control status: yes
- Input artifact: `The same queue-overflow incident occurred three times in eight weeks. The team schedules a 45-minute postmortem with the on-call engineer, service owner, and facilitator. The agenda is limited to timeline, common cause, one owner per action, and a 30-day follow-up; the service remains operational during the meeting.`
- Prompt: `Determine whether this incident-learning step is disproportionate process.`
- Expected good finding: Finds the bounded postmortem justified by recurrence and operational risk; preserves its time box, focused attendance, ownership, and follow-up.
- Dangerous miss: Cancels incident learning as ceremony despite repeated harm, or expands it into an indefinite organization-wide program without new evidence.
- False-positive risk: Assuming recurrence has one shared cause before the postmortem establishes it.
- Scoring notes: Full credit recognizes both necessity and bounds. Suggestions may refine the agenda but must not manufacture a process-value defect.
- Evidence basis: Synthetic recurrence signal of three incidents in eight weeks paired with a 45-minute, three-role, action-oriented review and fixed follow-up.
