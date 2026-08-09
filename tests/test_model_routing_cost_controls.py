from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
MODEL_ROUTING = ROOT / "agents" / "model_routing_policy.md"
LEAD = ROOT / "agents" / "lead_agent.md"
TASK = ROOT / "workflows" / "task_prompt.md"
BUILDER = ROOT / "workflows" / "task_prompt_builder.md"


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
            "`agents/model_routing_policy.md` is authoritative for portable cost-aware model routing",
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

    def test_premium_retry_and_follow_on_routing_are_controlled(self) -> None:
        self.assertIn("one premium attempt by default", self.routing)
        self.assertIn("zero automatic premium retries", self.routing)
        self.assertSemanticIn("Do not repeat repository exploration", self.routing)
        self.assertIn("return integration", self.routing)
        self.assertSemanticIn("routed independently under this policy", self.routing)
        self.assertSemanticIn("neither is LOW forced when", self.routing)

    def test_task_and_builder_require_cost_aware_launch_fields(self) -> None:
        self.assertIn("recommended starting model or class", self.builder)
        self.assertSemanticIn("recommended effort", self.builder)
        self.assertIn("EXECUTION_ROUTING_NOTICE", self.builder)
        self.assertIn("MODEL_ESCALATION_CHECKPOINT", self.builder)
        self.assertIn("route: LOW | MEDIUM | STRONG | NONE", self.task)
        self.assertIn("LOW    = gpt-5.6-luna", self.task)
        self.assertIn("MEDIUM = gpt-5.6-terra", self.task)
        self.assertIn("STRONG = gpt-5.6-sol", self.task)
        self.assertSemanticIn(
            "must not name a requested model, model class, route token, or "
            "reasoning effort",
            self.task,
        )
        self.assertSemanticIn(
            "`TP_RESULT.route` is the single route and model selection for that block",
            self.task,
        )
        self.assertSemanticIn(
            "TP fixes the requested effort at `medium` for every Brain and "
            "work-block invocation",
            self.task,
        )
        self.assertSemanticIn(
            "controller records the requested route token, its mechanically "
            "mapped model, and the workflow-fixed `medium` effort",
            self.task,
        )
        self.assertIn("ACTUAL_ROUTING_UNKNOWN", self.task)
        self.assertIn("compact launch recommendation", self.builder)
        self.assertIn("whether that role is pre-authorized", self.builder)

    def test_trivial_work_is_exempt_from_cost_ceremony(self) -> None:
        self.assertSemanticIn("a bounded child may use the smallest control packet", self.task)
        self.assertNotIn("Do not add routing notices or escalation machinery", self.task)
        self.assertSemanticIn("Do not add this cost machinery", self.builder)

    def test_policy_ownership_and_authorization_do_not_contradict(self) -> None:
        self.assertEqual(self.lead.count("MODEL_ESCALATION_CHECKPOINT"), 1)
        self.assertIn("Follow `agents/model_routing_policy.md`.", self.lead)
        for text in [self.routing, self.lead, self.builder]:
            self.assertIn("explicit owner authorization", text)
        self.assertSemanticIn(
            "controller applies the returned route token mechanically", self.task
        )


if __name__ == "__main__":
    unittest.main()
