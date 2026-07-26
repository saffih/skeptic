from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
MODEL_ROUTING = ROOT / "agents" / "model-routing.md"
LEAD = ROOT / "agents" / "lead-agent-prompt.md"
TASK = ROOT / "agents" / "task-prompt.md"
BUILDER = ROOT / "agents" / "task-prompt-builder.md"


class ModelRoutingCostControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agents = AGENTS.read_text(encoding="utf-8")
        cls.routing = MODEL_ROUTING.read_text(encoding="utf-8")
        cls.lead = LEAD.read_text(encoding="utf-8")
        cls.task = TASK.read_text(encoding="utf-8")
        cls.builder = BUILDER.read_text(encoding="utf-8")

    def assertSemanticIn(self, needle: str, text: str) -> None:
        self.assertIn(" ".join(needle.split()), " ".join(text.split()))

    def test_model_routing_owns_detailed_cost_policy(self) -> None:
        self.assertIn(
            "`agents/model-routing.md` is authoritative for portable cost-aware model routing",
            self.agents,
        )
        for marker in [
            "## Default order",
            "EXECUTION_ROUTING_NOTICE",
            "MODEL_ESCALATION_CHECKPOINT",
            "zero automatic premium retries",
            "minimum inputs",
            "least expensive reliable route",
        ]:
            self.assertIn(marker, self.routing)

    def test_substantive_lead_execution_requires_user_visible_notice(self) -> None:
        self.assertIn("At the start of substantive Task Prompt execution", self.lead)
        self.assertIn("EXECUTION_ROUTING_NOTICE", self.lead)
        self.assertSemanticIn("may stop at that checkpoint without losing completed work", self.routing)

    def test_unapproved_premium_work_requires_bounded_checkpoint(self) -> None:
        for marker in [
            "completed durable work and checks passed",
            "preserved artifact or commit location",
            "maximum calls or attempts",
            "context-isolation requirement and minimum inputs",
            "work that must not be repeated",
            "exact resume instruction",
        ]:
            self.assertIn(marker, self.routing)
        self.assertIn("stop for explicit owner authorization", self.routing)
        self.assertIn("silence is not authorization", self.routing)

    def test_premium_retry_and_return_to_low_are_controlled(self) -> None:
        self.assertIn("one premium attempt by default", self.routing)
        self.assertIn("zero automatic premium retries", self.routing)
        self.assertSemanticIn("Do not repeat repository exploration", self.routing)
        self.assertIn("return integration", self.routing)
        self.assertIn("to LOW or", self.routing)

    def test_task_and_builder_require_cost_aware_launch_fields(self) -> None:
        self.assertSemanticIn("starting model or model class", self.task)
        self.assertIn("reasoning effort", self.task)
        self.assertIn("recommended starting model or class", self.builder)
        self.assertSemanticIn("recommended effort", self.builder)
        for text in [self.task, self.builder]:
            self.assertIn("EXECUTION_ROUTING_NOTICE", text)
            self.assertIn("MODEL_ESCALATION_CHECKPOINT", text)
        self.assertIn("compact launch recommendation", self.builder)
        self.assertIn("whether that role is pre-authorized", self.builder)

    def test_trivial_work_is_exempt_from_cost_ceremony(self) -> None:
        self.assertIn("Do not add routing notices or escalation machinery", self.task)
        self.assertSemanticIn("Do not add this cost machinery", self.builder)

    def test_policy_ownership_and_authorization_do_not_contradict(self) -> None:
        self.assertEqual(self.lead.count("MODEL_ESCALATION_CHECKPOINT"), 1)
        self.assertIn("Follow `agents/model-routing.md`.", self.lead)
        for text in [self.routing, self.lead, self.task, self.builder]:
            self.assertIn("explicit owner authorization", text)


if __name__ == "__main__":
    unittest.main()
