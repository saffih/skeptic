from __future__ import annotations

import unittest
from pathlib import Path


class PlanningControlContractTests(unittest.TestCase):
    def test_stt_has_three_semantic_roles_and_no_command_agent(self) -> None:
        agents = Path('.claude/agents')
        self.assertTrue((agents / 'stt-planner.md').is_file())
        self.assertTrue((agents / 'stt-reviewer.md').is_file())
        self.assertTrue((agents / 'stt-worker.md').is_file())
        self.assertFalse(any('command' in path.name for path in agents.glob('stt-*.md')))

    def test_planner_contract_points_to_strict_plan(self) -> None:
        text = Path('agents/planner.md').read_text('utf-8')
        self.assertIn('concepts.stt.plan.validate_plan', text)
        self.assertIn('change', text)
        self.assertIn('validation', text)

    def test_workflow_requires_pre_cutover_review(self) -> None:
        text = Path('workflows/target_task.md').read_text('utf-8')
        self.assertIn('Freeze and review the final candidate before one deterministic cutover', text)
        self.assertIn('ledger.jsonl', Path('AGENTS.md').read_text('utf-8'))
