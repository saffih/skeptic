from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class RepositoryContractCompatibilityTests(unittest.TestCase):
    def test_preserves_preexisting_repository_contract_markers(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        planner = (ROOT / "agents" / "planner.md").read_text(encoding="utf-8")
        for marker in (
            "metadata-only Body state",
            "`agents/model_routing_policy.md` is authoritative for portable cost-aware model routing",
            "`TP: <objective>`",
            "`Create task prompt for: <objective>`",
            "`Create a task prompt for: <objective>`",
            "`Task prompt for: <objective>`",
            "first read `workflows/task_prompt_builder.md` before interpreting or responding",
            "process the complete user request according to it",
            "If the file cannot be read, stop visibly",
            "`TASK_PROMPT_BUILDER_UNAVAILABLE`",
            "Do not route an alias directly to `workflows/task_prompt.md`",
        ):
            self.assertIn(marker, agents)
        for marker in (
            "one complete replacement Plan",
            "may not approve",
            "execute steps",
            "claim terminal `DONE`",
            "Lead independently",
        ):
            self.assertIn(marker, planner)


if __name__ == "__main__":
    unittest.main()
