"""Static contract tests for Task Prompt builder alias routing.

These tests prove only the written Layer 1 contract, not model behavior.
"""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
BUILDER = ROOT / "agents" / "task-prompt-builder.md"


class TaskPromptBuilderRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        agents = AGENTS.read_text(encoding="utf-8")
        cls.alias_entry = agents.split(
            "- Create a Task Prompt from a user objective or plan", 1
        )[1].split("- Select model class", 1)[0]
        cls.builder = BUILDER.read_text(encoding="utf-8")

    def test_aliases_point_to_builder(self) -> None:
        self.assertIn("-> `agents/task-prompt-builder.md`", self.alias_entry)
        for alias in [
            "`TP: <objective>`",
            "`Create task prompt for: <objective>`",
            "`Create a task prompt for: <objective>`",
            "`Task prompt for: <objective>`",
        ]:
            self.assertIn(alias, self.alias_entry)

    def test_trigger_requires_reading_builder_before_processing_request(self) -> None:
        self.assertIn(
            "first read `agents/task-prompt-builder.md` before interpreting or responding",
            self.alias_entry,
        )
        self.assertIn(
            "process the complete user request according to it", self.alias_entry
        )

    def test_missing_builder_fails_closed_with_named_status(self) -> None:
        self.assertIn("If the file cannot be read, stop visibly", self.alias_entry)
        self.assertIn("`TASK_PROMPT_BUILDER_UNAVAILABLE`", self.alias_entry)

    def test_alias_does_not_route_directly_to_task_prompt(self) -> None:
        self.assertNotIn("-> `agents/task-prompt.md`", self.alias_entry)
        self.assertIn(
            "Do not route an alias directly to `agents/task-prompt.md`",
            self.alias_entry,
        )

    def test_builder_creates_but_does_not_execute_task_prompt(self) -> None:
        self.assertIn(
            "The builder creates the prompt; it does not execute it.", self.builder
        )
        self.assertIn("Return the Task Prompt unexecuted.", self.builder)


if __name__ == "__main__":
    unittest.main()
