# Agent Instructions

Entry map. Load only the artifact needed for the current use:

- Review an artifact or decision (including "RunSkeptic" or Skeptic review)
  -> `skeptic.md`
- Orchestrate work as the Lead (compact state, one Boundary Agent dispatch per transition)
  -> `agents/lead-agent-prompt.md`
- Execute serious multi-phase work through terminal DONE
  -> `agents/task-prompt.md`
- Create an execution Task Prompt from a user objective or verified plan
  -> `agents/task-prompt-builder.md`
  - Aliases (text after the alias is the objective): `TP: <objective>`, `Create task prompt for: <objective>`, `Create a task prompt for: <objective>`, `Task prompt for: <objective>`
  - These four aliases route here first; Task Prompt construction is `agents/task-prompt-builder.md`'s job, performed by a fresh Boundary Agent dispatched for that bounded objective.

Ownership:

- `skeptic.md` is authoritative for RunSkeptic behavior and output categories.
- `agents/lead-agent-prompt.md` is authoritative for the Lead role: an orchestration-only contract of compact state, one Boundary Agent dispatch per transition, and structural receipt validation.
- `agents/task-prompt.md` is authoritative for Task Prompt construction, execution control, and closure.
- `agents/task-prompt-builder.md` is authoritative for the objective/verified-plan-to-Task-Prompt build operation and its four aliases.
- Editing `skeptic.md` requires explicit authority. Do not edit "skeptic.md" unless explicitly authorized.

Architectural boundary:

This repository is a reusable, normally read-only prompt and review library. It defines portable execution contracts; it does not own runtime state, workflow storage, or task workspaces. Task-specific state is selected and owned by the invoking runtime or actual task environment, not by this checkout.

## Verification vocabulary

`AGENTS.md` is the canonical home for these four verification terms. `agents/lead-agent-prompt.md`, `agents/task-prompt.md`, and `agents/task-prompt-builder.md` reference or specialize these definitions; they must not restate a competing full definition. `skeptic.md` remains authoritative for the internal mechanics of one RunSkeptic pass -- its stages, Thinkers, evidence levels, decisions, receipts, and output categories -- which these terms do not redefine.

### Verification

Verification is an evidence-based pass/fail process that checks a declared claim, artifact, phase, or result against explicit acceptance conditions and meaningful disconfirming checks. It may use tests, hashes, traces, inspection, external-state checks, or other proportionate evidence.

Verification is not confidence, repeated prose review, automatically RunSkeptic, or automatically a three-pass process.

### Skeptic verification

Skeptic verification is the orchestration-level completion criterion of three consecutive complete RunSkeptic PASS results on the same unchanged artifact identity.

Each counted pass must:
- read and apply the actual current `skeptic.md`;
- run the complete applicable RunSkeptic flow;
- consider every required Thinker;
- include the required RunSkeptic receipt;
- name the same byte-identical artifact, immutable ref, commit, or cryptographic hash.

A counted PASS is the review-level PASS with no blocking finding; ACTION and CONFLICT do not count as PASS. The report still follows `skeptic.md`'s final task-outcome rules.

Before the third consecutive PASS, the result is provisional. After the third PASS, accept and stop; do not perform a fourth reassurance pass.

These orchestration terms do not redefine `skeptic.md`'s internal VERIFY stage, evidence levels, decision paths, or output categories.

The ordinary Task-level Skeptic readiness gate (see `agents/task-prompt.md`, "Task-level Skeptic readiness gate") is a different, bounded purpose and is not Skeptic verification unless explicitly invoked as pure or fix Skeptic verification.

### Pure Skeptic verification

Pure Skeptic verification is read-only Skeptic verification: no fixes, no artifact changes, no mutation authority. Run only the passes needed to reach the three-PASS streak. ACTION or CONFLICT stops without acceptance.

### Fix Skeptic verification

Fix Skeptic verification is Skeptic verification with explicitly authorized fixes between passes:

1. Run complete RunSkeptic.
2. On ACTION, apply only the smallest authorized evidence-supported fix.
3. Any artifact change resets the consecutive-PASS count to zero.
4. Reverify deterministic acceptance before the next pass.
5. Stop on CONFLICT.
6. Finish only after three consecutive PASS results on the unchanged final artifact.

Every fix workflow must declare before execution: artifact identity; maximum fix cycles; maximum total RunSkeptic passes; an early-stop rule for when the remaining allowance cannot still yield three consecutive passes. Do not enlarge limits because the workflow failed.
