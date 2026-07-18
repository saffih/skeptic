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
            "A Task Prompt is the complete Lead-owned execution contract",
            "User objective",
            "-> Task Prompt",
            "-> Lead Agent Prompt",
            "-> Agent Prompts / Dispatch Tickets",
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
        self.assertIn("Do not duplicate its full contract here or in `skeptic.md`.", self.lead)

    def test_lead_routes_terminal_work_through_task_prompt(self) -> None:
        for marker in [
            "read and apply the current `agents/task-prompt.md`",
            "Construct a Task Prompt rather than treating one Agent Prompt as the whole task.",
            "first construct and gate the Task Prompt, then execute it",
            "Task Closure Receipt",
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
            "Temporary chat, worker memory, transient context, and unverified summaries are not durable evidence.",
            "Compression must preserve dissent, contradictions, failed cases, unknowns, and minority evidence",
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
        self.assertIn(
            'unresolved "ACTION", "DECOMPOSE", or "CONFLICT"',
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


if __name__ == "__main__":
    unittest.main()
