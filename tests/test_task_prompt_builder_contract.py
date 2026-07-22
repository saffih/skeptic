# made by AI
"""Contract/marker tests for the Task-Prompt Builder.

These tests check that required text exists in the doctrine files. They do
not prove agent behavior, genuine independence between reviewer contexts, or
review quality -- only that the written contract is present.
"""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "agents" / "task-prompt-builder.md"
AGENTS = ROOT / "AGENTS.md"
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"
TASK_PROMPT = ROOT / "agents" / "task-prompt.md"
SKEPTIC = ROOT / "skeptic.md"


class BuilderExistenceAndAliasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = BUILDER.read_text(encoding="utf-8")
        cls.agents = AGENTS.read_text(encoding="utf-8")

    def test_builder_file_exists(self) -> None:
        self.assertTrue(BUILDER.exists())

    def test_all_four_aliases_defined_in_builder(self) -> None:
        for alias in [
            "`TP: <objective>`",
            "`Create task prompt for: <objective>`",
            "`Create a task prompt for: <objective>`",
            "`Task prompt for: <objective>`",
        ]:
            self.assertIn(alias, self.builder)

    def test_all_four_aliases_routed_in_agents_md(self) -> None:
        for alias in [
            "`TP: <objective>`",
            "`Create task prompt for: <objective>`",
            "`Create a task prompt for: <objective>`",
            "`Task prompt for: <objective>`",
        ]:
            self.assertIn(alias, self.agents)

    def test_explicit_route_and_precedence_in_agents_md(self) -> None:
        self.assertIn(
            "Create an execution Task Prompt from a user objective or verified plan",
            self.agents,
        )
        self.assertIn("`agents/task-prompt-builder.md`", self.agents)
        self.assertIn("take precedence over the generic prompt-construction route", self.agents)
        self.assertIn(
            "`agents/task-prompt-builder.md` is authoritative for the objective/verified-plan-to-Task-Prompt build operation",
            self.agents,
        )


class InputClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = BUILDER.read_text(encoding="utf-8")

    def test_objective_only_path_defined(self) -> None:
        for marker in [
            "Objective-only input",
            "TASK_PROMPT_NOT_REQUIRED",
            "return a truthful conflict rather than guessing",
        ]:
            self.assertIn(marker, self.builder)

    def test_verified_plan_path_requires_full_package(self) -> None:
        for marker in [
            "Verified-plan input",
            "exact plan bytes, or an authorized immutable artifact reference",
            "the plan's SHA-256",
            "three consecutive same-hash Plan Skeptic PASS receipts",
            'An unsupported "verified plan" label alone is insufficient.',
        ]:
            self.assertIn(marker, self.builder)


class PlanSkepticVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = BUILDER.read_text(encoding="utf-8")

    def test_definition_same_hash_reset_and_receipts(self) -> None:
        for marker in [
            "Run the actual current RunSkeptic procedure",
            "Apply only fixes authorized by Skeptic's `DECIDE` stage.",
            "three consecutive `PASS` verdicts",
            "Any plan-byte change resets the consecutive-pass count to zero.",
            "Preserve every required RunSkeptic receipt and the plan SHA-256",
        ]:
            self.assertIn(marker, self.builder)

    def test_bounds_and_blocked_outcome(self) -> None:
        for marker in [
            "at most two plan-changing repair cycles",
            "at most seven RunSkeptic reviews total",
            "`PLAN_VERIFICATION_BLOCKED`",
        ]:
            self.assertIn(marker, self.builder)

    def test_non_independent_reviews_must_be_labeled(self) -> None:
        self.assertIn(
            "must not be described as independent",
            self.builder,
        )


class ContractApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = BUILDER.read_text(encoding="utf-8")

    def test_required_current_reads_include_all_governing_files(self) -> None:
        for marker in [
            "`AGENTS.md`",
            "`agents/lead-agent-prompt.md`",
            "`agents/task-prompt.md`",
            "`skeptic.md`",
            "Do not substitute memory, conversation summaries, or copied excerpts",
        ]:
            self.assertIn(marker, self.builder)

    def test_contract_drift_returns_to_plan_production(self) -> None:
        self.assertIn(
            "return to plan production and repeat Plan Skeptic verification",
            self.builder,
        )

    def test_prompt_lead_design_package_mode(self) -> None:
        for marker in [
            "Use a Prompt Lead in `DESIGN_PACKAGE` mode",
            "agents/task-prompt.md` contract and template",
        ]:
            self.assertIn(marker, self.builder)

    def test_semantic_traceability_required(self) -> None:
        for marker in [
            "semantic traceability map",
            "silent omission, weakening, or unauthorized expansion is not",
        ]:
            self.assertIn(marker, self.builder)


class UnifiedPromptBuildVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = BUILDER.read_text(encoding="utf-8")

    def test_all_nine_categories_present(self) -> None:
        for marker in [
            "**A. Plan fidelity and provenance**",
            "**B. Task-Prompt completeness**",
            "**C. Dependency integrity**",
            "**D. Lead-Agent application**",
            "**E. Lead-context protection**",
            "**F. Execution feasibility**",
            "**G. Internal consistency and authority**",
            "**H. End-to-end Lead dry run**",
            "**I. Proportionality**",
        ]:
            self.assertIn(marker, self.builder)

    def test_verdicts_and_repair_routing(self) -> None:
        for marker in [
            "`READY` — freeze the exact final Task-Prompt SHA-256",
            "`REPAIR_REQUIRED` — the Prompt Lead repairs the Task Prompt",
            "`PLAN_DEFECT` — return to plan production",
            "`BLOCKED` — preserve the exact candidate identity",
        ]:
            self.assertIn(marker, self.builder)

    def test_plan_defect_returns_to_plan_verification(self) -> None:
        self.assertIn("repeat full Plan Skeptic verification", self.builder)

    def test_ready_ties_to_exact_final_hash(self) -> None:
        self.assertIn(
            "`READY` applies only to the exact final Task-Prompt SHA-256.",
            self.builder,
        )

    def test_verification_bounds(self) -> None:
        for marker in [
            "at most two Task-Prompt repair cycles",
            "at most three complete Prompt-Build Verification runs",
        ]:
            self.assertIn(marker, self.builder)


class NonExecutionAndProportionalityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = BUILDER.read_text(encoding="utf-8")

    def test_non_execution_boundary_stated(self) -> None:
        for marker in [
            "never executes the Task Prompt",
            "confirmation that the Task Prompt was not executed",
            "Executing that Task Prompt is a separate, later authorization",
        ]:
            self.assertIn(marker, self.builder)

    def test_no_forbidden_machinery_introduced(self) -> None:
        self.assertIn(
            "does not add a script, controller, permanent state or receipt directory, or separate checklist files",
            self.builder,
        )

    def test_operational_outcomes_do_not_redefine_skeptic_verdicts(self) -> None:
        self.assertIn(
            "are operational outcomes of this builder, not new Skeptic categories",
            self.builder,
        )
        for verdict in ["`PASS`", "`ACTION`", "`DECOMPOSE`", "`CONFLICT`"]:
            self.assertIn(verdict, self.builder)

    def test_builder_output_list_is_complete(self) -> None:
        for marker in [
            "the three same-hash Plan Skeptic PASS receipts",
            "the final Task Prompt and its SHA-256",
            "the compact semantic traceability map",
            "the Prompt-Build Verification verdict and its checklist receipt",
            "explicit confirmation that the Task Prompt was not executed",
        ]:
            self.assertIn(marker, self.builder)


class ContextProtectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = BUILDER.read_text(encoding="utf-8")

    def test_lead_context_protection_markers_present(self) -> None:
        for marker in [
            "Lead receives compact authoritative inputs, not full histories",
            "raw logs/discussions/large outputs stay outside Lead context absent a named dispute",
            "closure capacity protected by a measurable reserve or substitute",
        ]:
            self.assertIn(marker, self.builder)


if __name__ == "__main__":
    unittest.main()
