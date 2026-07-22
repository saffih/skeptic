# made by AI
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_PROMPT = ROOT / "agents" / "task-prompt.md"
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"
SKEPTIC = ROOT / "skeptic.md"
GOVERNANCE = ROOT / "skeptic-tests.md"


class TaskPromptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.skeptic = SKEPTIC.read_text(encoding="utf-8")
        cls.governance = GOVERNANCE.read_text(encoding="utf-8")

    def test_canonical_artifact_and_hierarchy_exist(self) -> None:
        self.assertTrue(TASK_PROMPT.exists())
        for marker in [
            "A Task Prompt is the complete execution contract",
            "User objective",
            "-> Task Prompt",
            "-> orchestration-only Lead",
            "-> Boundary Agent Dispatch Tickets",
            "-> Task Closure Receipt",
        ]:
            self.assertIn(marker, self.task)

    def test_contracts_have_distinct_authority(self) -> None:
        self.assertIn(
            "`agents/task-prompt.md` is authoritative for Task Prompt construction",
            self.task,
        )
        self.assertIn(
            "`skeptic.md` is authoritative for RunSkeptic review behavior",
            self.task,
        )
        self.assertIn("Do not copy this entire file", self.task)
        self.assertIn(
            "authoritative for the orchestration-only Lead role and Boundary Agent routing",
            self.task,
        )
        # The Lead's own contract actually matches that description.
        self.assertIn("Your role is orchestration only.", self.lead)
        self.assertIn("## Compact receipt", self.lead)

    def test_lead_routes_terminal_work_through_task_prompt(self) -> None:
        self.assertIn(
            "Every inspection, plan, implementation, test, review, judgment, repair, "
            "verification, integration, publication, remote check, and closure "
            "operation belongs to a fresh Boundary Agent.",
            self.task,
        )
        for marker in [
            "select the next authorized task",
            "dispatch one fresh Boundary Agent with a bounded objective",
            "receive and validate its compact receipt",
        ]:
            self.assertIn(marker, self.lead)

    def test_task_prompt_has_executable_state_machine(self) -> None:
        for marker in [
            "INTAKE",
            "PREFLIGHT",
            "TASK-LEVEL SKEPTIC GATE",
            "VERIFY AND PERSIST CHECKPOINT",
            "REASSESS FEASIBILITY AND BUDGET",
            "INTEGRATION / PUBLICATION when required by DONE",
            "TASK CLOSURE RECEIPT",
        ]:
            self.assertIn(marker, self.task)

    def test_completion_budget_is_operational_not_advisory(self) -> None:
        for marker in [
            "protected completion reserve",
            "Exploration, workers, optional reviews, and repeated gates must not consume",
            "When token or context counters are exposed, use numeric allocations and stop thresholds.",
            "use measurable substitutes",
            'Saying only "protect context" or "leave headroom" is not an allocation.',
            "maximum retry/gate counts",
            "pre-exhaustion checkpoint",
        ]:
            self.assertIn(marker, self.task)

    def test_phase_contract_is_dependency_and_evidence_bounded(self) -> None:
        for marker in [
            "Phase ID and objective:",
            "Dependencies:",
            "Owner / role:",
            "Budget / context / output limit:",
            "Required output and durable evidence location:",
            "Acceptance and disconfirming checks:",
            "Failure, retry, and rollback path:",
            "Next-state rule:",
        ]:
            self.assertIn(marker, self.task)

    def test_context_and_evidence_custody_block_transient_dependencies(self) -> None:
        for marker in [
            "Every expensive or decision-critical phase must persist an authoritative artifact",
            "Temporary chat, Boundary Agent memory, transient context, and unverified summaries are not durable evidence.",
            "External artifacts must preserve dissent, contradictions, failed cases, unknowns, and minority evidence",
            "Remaining budget / feasibility:",
        ]:
            self.assertIn(marker, self.task)

    def test_retries_gates_and_handoff_are_bounded(self) -> None:
        for marker in [
            "declare retry and Skeptic-gate limits before execution",
            "same failure class repeating twice",
            "one initial pass plus at most two materially revised reruns",
            "lack of improvement returns DECOMPOSE or CONFLICT",
            "Handoff is not DONE.",
        ]:
            self.assertIn(marker, self.task)

    def test_remote_main_terminal_state_cannot_silently_pass(self) -> None:
        for marker in [
            "a patch, branch, commit, pull request, local merge, push attempt, or stale remote-tracking ref is not DONE",
            "pushed, fetched again, and matched against fetched remote state",
            "a successful push command",
            "freshly observed external state",
        ]:
            self.assertIn(marker, self.task)

    def test_skeptic_has_two_prompt_review_levels(self) -> None:
        for marker in [
            "### Prompt Review Levels",
            "#### Level 1 - Agent Prompt review",
            "#### Level 2 - Task Prompt review",
            "A Task Prompt must not receive PASS merely because its individual Agent Prompts are locally valid.",
            "Read it as a required companion when reviewing a Task Prompt.",
        ]:
            self.assertIn(marker, self.skeptic)

    def test_task_level_gate_has_all_decisions_without_changing_final_outcomes(self) -> None:
        for verdict in ["`PASS`", "`ACTION`", "`DECOMPOSE`", "`CONFLICT`"]:
            self.assertIn(verdict, self.task)
            self.assertIn(verdict, self.skeptic)
        self.assertIn("Full Skeptic still ends as HANDLED or CONFLICT.", self.skeptic)
        self.assertIn("Every task ends as HANDLED or CONFLICT.", self.skeptic)

    def test_task_level_silent_pass_is_an_invariant_violation(self) -> None:
        self.assertIn(
            "Never give a Task Prompt task-level PASS merely because its child Agent Prompts pass locally.",
            self.skeptic,
        )
        self.assertIn(
            "Never let exploration, delegation, or repeated gates silently consume the completion reserve",
            self.skeptic,
        )
        # The Lead's own PASS-streak rule mirrors the no-silent-pass
        # invariant: an ACTION verdict or any candidate change resets the
        # streak, so a task cannot coast to PASS on a stale or locally
        # passing candidate.
        self.assertIn(
            "If the verdict is ACTION, reset the PASS count to zero and "
            "dispatch a fresh Boundary Agent to repair only the identified "
            "findings.",
            self.lead,
        )
        self.assertIn(
            "Stop verification after three consecutive PASS results on the "
            "same unchanged candidate.",
            self.lead,
        )

    def test_governance_has_disconfirming_task_prompt_scenarios(self) -> None:
        for marker in [
            "Complete feasible Task Prompt",
            "Locally valid child prompts with no end-to-end integration owner",
            "Task Prompt with vague or intermediate DONE",
            "Task Prompt with no protected completion reserve",
            "decision-critical evidence exists only in transient context",
            "blind-reruns the same failure class",
            "unresolved model or effort routing",
            "Clear task too large for available resources",
            "Merge-to-main task that stops at branch, commit, or pull request",
            "protocol cost approaches the result's value",
        ]:
            self.assertIn(marker, self.governance)

    def test_copyable_template_contains_terminal_contract(self) -> None:
        for marker in [
            "## Copyable Task Prompt template",
            "## Exact terminal DONE",
            "## Completion-feasibility and budget",
            "## Execution graph",
            "## Agent Prompts / Dispatch Tickets",
            "## Context and evidence custody",
            "## Failure, retry, redesign, and handoff",
            "## Integration / publication / remote verification",
            "Fresh external or remote state verified: yes/no/not applicable + evidence",
            "Overall DONE: yes/no",
            "# PONYTAIL / KISS — NON-NEGOTIABLE EXECUTION CHECKSUM",
            "# END OF PROMPT",
        ]:
            self.assertIn(marker, self.task)

    def test_resumed_state_machine_routes_from_authoritative_checkpoint(self) -> None:
        for marker in [
            "New execution:",
            "Resumed execution:",
            "RESUME ENTRY",
            "VERIFY AUTHORITATIVE CHECKPOINT",
            "first incomplete dependency-ready phase",
            "CLOSURE_ONLY when substantive work is complete",
            "smallest evidenced backward transition after deterministic invalidation",
            "CHECKPOINT_CONFLICT when state cannot be reconciled",
            "A lifecycle written from phase zero does not authorize replay",
        ]:
            self.assertIn(marker, self.task)

    def test_closure_only_missing_fields_do_not_reopen_execution(self) -> None:
        for marker in [
            "When substantive work is complete, enter `CLOSURE_ONLY`.",
            "fill only missing receipt fields",
            "Missing procedural evidence does not reopen completed phases.",
        ]:
            self.assertIn(marker, self.task)
        for marker in [
            "Closure-only missing procedural fields",
            "do not replay completed phases",
        ]:
            self.assertIn(marker, self.governance)

    def test_accepted_result_is_verified_without_independent_recomputation(self) -> None:
        for marker in [
            "verify identity, input and result hashes, acceptance, and required counts",
            "Do not recreate inventories, scores, ledgers, or conclusions",
            "Raw evidence may be opened only for one named unresolved dispute.",
        ]:
            self.assertIn(marker, self.task)
        self.assertIn("Accepted result and extra confidence", self.governance)
        self.assertIn("then close without recomputation", self.governance)

    def test_checkpoint_invalidation_reopens_smallest_evidenced_phase(self) -> None:
        for marker in [
            "hash mismatch",
            "corrupt or missing accepted artifact",
            "failed acceptance",
            "changed immutable input",
            "contradictory authoritative state",
            "smallest phase reopened",
            "preserved unaffected evidence",
            "renewed feasibility",
            "Otherwise return `CHECKPOINT_CONFLICT`.",
        ]:
            self.assertIn(marker, self.task)
        self.assertIn("Deterministic checkpoint invalidation", self.governance)

    def test_closure_ready_state_forbids_optional_review_expansion(self) -> None:
        self.assertIn(
            'do not dispatch an optional review, new inventory, broad analysis, or "one more check"',
            self.task,
        )
        self.assertIn("Optional review after closure-ready", self.governance)
        self.assertIn("do not call it; close", self.governance)

    def test_checkpoint_proven_p0_to_p5_resumes_at_p6(self) -> None:
        self.assertIn("Resume at the first incomplete dependency-ready phase.", self.task)
        self.assertIn("Resume at P6", self.governance)
        self.assertIn("start at P6 without replaying earlier phases", self.governance)

    def test_context_exhaustion_after_completion_fails_task_execution(self) -> None:
        for marker in [
            "`prompt too long`",
            "session exhaustion",
            "forced compression",
            "unplanned handoff",
            "failed Task Prompt execution path",
        ]:
            self.assertIn(marker, self.task)
        self.assertIn("Context exhaustion after substantive completion", self.governance)
        self.assertIn(
            "surviving artifacts do not convert that execution into success",
            self.governance,
        )

    def test_resume_record_is_bound_to_contract_and_copyable_template(self) -> None:
        for marker in [
            "authoritative checkpoint path or ref and hash",
            "highest completed phase",
            "first incomplete phase",
            "closure-ready status",
            "Boundary-Agent artifact references opened and reason",
            "backward-transition authorization and evidence",
            "## Resume / checkpoint state",
            "Checkpoint / resume state:",
            "Checkpoint conflict / backward-transition rule:",
            "Execution mode / `CLOSURE_ONLY` status:",
        ]:
            self.assertIn(marker, self.task)

    def test_stateless_library_boundary_is_stated(self) -> None:
        for marker in [
            "## Stateless library and runtime-owned state",
            "does not own runtime state, workflow storage, or task workspaces",
            "State handling belongs to the invoking runtime and the actual task environment",
        ]:
            self.assertIn(marker, self.task)
        # The Lead's own state contract matches that boundary: it keeps only
        # a minimal orchestration allowlist and never substantive content.
        self.assertIn("Keep only the minimum orchestration state", self.lead)
        self.assertIn(
            "Do not retain substantive task content in Lead state.", self.lead
        )

    def test_persistence_is_conditional_not_automatic(self) -> None:
        for marker in [
            "Persistence is conditional, not automatic:",
            "may remain entirely session-only",
            "Persistence is required when evidence or state must survive handoff, interruption, context clearing, independent review, delegation, repeated execution, or cross-session continuation.",
        ]:
            self.assertIn(marker, self.task)

    def test_environment_selects_authorized_persistence_location(self) -> None:
        self.assertIn(
            "the environment selects an authorized location: the current runtime, the target repository or workspace, authorized temporary storage, runtime-managed storage, or another user-selected store.",
            self.task,
        )
        # Choosing where to persist is itself repository/external-system
        # work; the Lead's Core rule delegates it rather than deciding the
        # location directly.
        self.assertIn("repository inspection", self.lead)
        self.assertIn("external-system interaction", self.lead)

    def test_skeptic_checkout_is_not_default_workspace(self) -> None:
        self.assertIn("The Skeptic checkout is not the default task workspace.", self.task)
        self.assertIn(
            "Writing to it is valid only when Skeptic itself is the explicit "
            "target and mutation is authorized.",
            self.task,
        )
        # The Lead never decides workspace identity itself: repository
        # inspection and external-system interaction (which would include
        # checking out or writing to Skeptic) are always delegated.
        self.assertIn("repository inspection", self.lead)
        self.assertIn("external-system interaction", self.lead)

    def test_location_fields_may_be_not_applicable_for_session_only_work(self) -> None:
        self.assertIn(
            'may be marked `NOT_APPLICABLE` with a stated reason when the task is valid session-only work.',
            self.task,
        )
        self.assertIn(
            'may read `NOT_APPLICABLE` with a stated reason for valid session-only work',
            self.task,
        )

    def test_skeptic_distinguishes_session_only_from_material_survival(self) -> None:
        for marker in [
            "Persistence is conditional, not automatic.",
            "Skeptic does not prescribe a canonical state directory, receipt directory, controller, filesystem layout, database, or storage mechanism",
            "the Skeptic checkout is not the default writable workspace",
            "may receive task-level PASS without a controller, checkpoint file, state directory, or durable artifact store",
            "missing or inadequate authorized persistence is ACTION",
        ]:
            self.assertIn(marker, self.skeptic)

    def test_governance_has_conditional_persistence_scenarios(self) -> None:
        for marker in [
            "Bounded one-session task with no handoff, resume, delegation, or cross-context consumer",
            "task-level PASS without a controller, checkpoint file, state directory, or durable artifact store",
            "Delegated, resumable, cross-session, or independently reviewed task whose required evidence exists only in transient context",
            "task-level ACTION until an adequate authorized persistence mechanism exists",
        ]:
            self.assertIn(marker, self.governance)

    def test_operational_resume_stops_preserve_skeptic_verdicts(self) -> None:
        self.assertIn(
            "`PACKAGE_INCOMPLETE` and `CHECKPOINT_CONFLICT` are operational stop reasons, not Skeptic verdicts.",
            self.task,
        )
        for verdict in ["`PASS`", "`ACTION`", "`DECOMPOSE`", "`CONFLICT`"]:
            self.assertIn(verdict, self.task)


if __name__ == "__main__":
    unittest.main()
