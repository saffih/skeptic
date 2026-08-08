"""Static contract tests for Task Prompt builder alias routing and the
TP: execution bootstrap.

These tests prove only the written contract, not model behavior.
"""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
BUILDER = ROOT / "workflows" / "task_prompt_builder.md"
TASK_PROMPT = ROOT / "workflows" / "task_prompt.md"


class TaskPromptBuilderRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agents = AGENTS.read_text(encoding="utf-8")
        cls.builder = BUILDER.read_text(encoding="utf-8")
        cls.task_prompt = TASK_PROMPT.read_text(encoding="utf-8")

    def test_entry_map_points_build_a_task_prompt_to_builder(self) -> None:
        self.assertIn(
            "- Build a Task Prompt: use `workflows/task_prompt_builder.md`.",
            self.agents,
        )

    def test_builder_aliases_are_the_three_prose_forms_only(self) -> None:
        for alias in [
            "`Create task prompt for: <objective>`",
            "`Create a task prompt for: <objective>`",
            "`Task prompt for: <objective>`",
        ]:
            self.assertIn(alias, self.builder)
        self.assertNotIn("TP:", self.builder)

    def test_builder_creates_but_does_not_execute_task_prompt(self) -> None:
        self.assertIn(
            "The builder creates the prompt; it does not execute it.", self.builder
        )
        self.assertIn("Return the Task Prompt unexecuted.", self.builder)

    def test_agents_md_binds_tp_to_task_prompt_execution_as_lead(self) -> None:
        self.assertIn("`TP:`", self.agents)
        self.assertIn("activates the Task Prompt workflow", self.agents)
        self.assertIn("acts as the Lead", self.agents)
        self.assertIn("`agents/lead_agent.md`", self.agents)
        self.assertIn("`workflows/task_prompt.md`", self.agents)
        self.assertIn("## Orchestration", self.agents)

    def test_task_prompt_workflow_defines_tp_invocation_syntax(self) -> None:
        self.assertIn("`TP: <task>`", self.task_prompt)
        self.assertIn("is the governing user task input", self.task_prompt)
        self.assertIn("activates this workflow", self.task_prompt)
        self.assertIn("Lead contract", self.task_prompt)

    def test_tp_is_not_ambiguous_between_builder_and_execution(self) -> None:
        # TP: must bind exactly once across the two files: as the AGENTS.md
        # execution/Lead entry, never also as a task_prompt_builder.md alias.
        combined_tp_mentions = self.agents.count("TP:") + self.builder.count("TP:")
        self.assertEqual(combined_tp_mentions, 1)


if __name__ == "__main__":
    unittest.main()
