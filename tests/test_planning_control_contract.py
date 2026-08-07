"""Contract probes; these do not prove runtime lifecycle enforcement."""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    return " ".join((ROOT / path).read_text(encoding="utf-8").split())


class PlanningControlContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agents = text("AGENTS.md")
        cls.lead = text("agents/lead_agent.md")
        cls.planner = text("agents/planner.md")
        cls.task = text("workflows/task_prompt.md")
        cls.builder = text("workflows/task_prompt_builder.md")

    def test_target_task_gate_is_ordered_and_scoped(self) -> None:
        sequence = (
            "distinct bounded Planner dispatch",
            "Agent Completion Envelope validation",
            "complete Planner-produced plan",
            "RunSkeptic review and receipt validation",
            "Planner repair after every material plan change",
            "bounded qualifier acceptance of the final unchanged plan",
        )
        for value in (self.task,):
            positions = [value.index(item) for item in sequence]
            self.assertEqual(positions, sorted(positions))
        self.assertIn("Every substantive ordinary or Target action uses a bounded child", self.task)

    def test_target_task_has_no_substitute_path(self) -> None:
        for value in (self.task, self.builder):
            self.assertIn("supplied", value)
            self.assertIn("same-runtime", value)
        self.assertIn("supplied", self.planner)
        self.assertIn("planning-not-required", self.task)
        self.assertIn("cannot substitute", self.builder)

    def test_repair_and_authority_boundaries_are_explicit(self) -> None:
        self.assertIn("new unique Planner repair dispatch", self.planner)
        for phrase in (
            "may not approve a Plan",
            "execute steps",
            "integrate or publish changes",
            "alter the task objective",
            "claim terminal `DONE`",
            "must not recursively dispatch another Planner",
        ):
            self.assertIn(phrase, self.planner)
        self.assertIn("return `CONFLICT`", self.planner)

    def test_lead_safeguards_are_preserved(self) -> None:
        for phrase in (
            "Prefer deterministic child execution",
            "smallest model and reasoning effort",
            "Boundary Agent",
            "These obligations are transitive",
            "unique Lead-issued dispatch ID",
            "Agent Completion Envelope",
            "bounded role-specific qualification",
            "Store the exact request",
            "FRESH_CONTEXT_CONFIRMED",
            "CONTEXT_ISOLATION_UNKNOWN",
            "Run broader checks",
            "When material routing or delegation was used",
            "Keep only enough state to continue safely",
            "Stop when the task is complete",
        ):
            self.assertIn(phrase, self.lead)

    def test_ordinary_work_and_cost_controls_remain_proportional(self) -> None:
        self.assertIn("Every substantive action uses a bounded child", self.lead)
        self.assertIn("Delegation is mandatory", self.task)
        self.assertIn("Boundary processing is optional", self.task)
        self.assertIn("trivial read-only work", self.task)
        self.assertIn("MODEL_ESCALATION_CHECKPOINT", self.task)
        self.assertIn("PROMPT_CONFORMANCE_ACTION_REQUIRED", self.builder)

    def test_target_task_replaces_ordinary_sequence_as_a_whole(self) -> None:
        self.assertIn(
            "entire ordinary plan/review/repair/execution path as a whole",
            self.task,
        )
        for value in (self.task,):
            self.assertIn("entire ordinary plan/review/repair/execution path as a whole", value)
        self.assertIn("parent control plane dispatches a bounded qualifier", self.planner)

    def test_lead_and_task_share_preflight_exclusive_path_and_closeout(self) -> None:
        self.assertIn("### Control-plane preflight", self.lead)
        self.assertIn("### Common substantive preflight", self.task)
        self.assertIn("mutually exclusive", self.task)
        for value in (self.lead, self.task):
            self.assertIn("Common post-execution closeout", value)

    def test_shared_cross_cutting_duties_remain_applicable(self) -> None:
        self.assertIn("Follow `agents/model_routing_policy.md`", self.lead)
        self.assertIn("Agent Completion Envelope validation", self.lead)
        self.assertIn("bounded role-specific qualification", self.lead)
        self.assertIn("Dispatch a bounded deterministic child for deterministic evidence", self.lead)
        self.assertIn("## Reporting", self.lead)
        self.assertIn("## State and stopping", self.lead)

    def test_execution_exactly_once_present_in_all_target_surfaces(self) -> None:
        # Static text probe only; does not prove runtime enforcement.
        for value in (self.task, self.builder):
            self.assertIn("execution exactly once", value)

    def test_builder_conformance_requires_exactly_once_before_ready(self) -> None:
        self.assertIn("omits execution exactly once", self.builder)
        self.assertIn("must not receive `PROMPT_CONFORMANCE_READY`", self.builder)

    def test_planner_uses_actual_routing_unknown(self) -> None:
        # Static text probe only; does not prove runtime enforcement.
        self.assertIn("ACTUAL_ROUTING_UNKNOWN", self.planner)

    def test_planner_plain_unknown_limited_to_identity(self) -> None:
        self.assertNotIn("routing facts; report them as `UNKNOWN`", self.planner)
        self.assertIn("session or context identity as `UNKNOWN`", self.planner)

    def test_agents_entry_map_and_ownership_are_not_duplicated(self) -> None:
        self.assertEqual(self.agents.count("Build a Task Prompt"), 1)
        self.assertIn("Boundary processing", self.agents)
        self.assertIn("Do not read implementation source", self.agents)
        self.assertIn("## Ownership", self.agents)
        self.assertIn("## Portability", self.agents)
        self.assertIn("Substantive plan construction or repair", self.agents)
        self.assertNotIn("global Planner", self.agents)

    def test_builder_target_conformance_and_output_contract(self) -> None:
        self.assertIn("Target Task", self.builder)
        self.assertIn("supplied plans are Planner input only", self.builder)
        self.assertIn("PROMPT_CONFORMANCE_READY", self.builder)
        self.assertIn("PROMPT_CONFORMANCE_UNVERIFIABLE", self.builder)
        self.assertIn("Return the Task Prompt unexecuted", self.builder)
        self.assertIn("recommended starting model or class", self.builder)

    def test_superseded_optional_planning_state_is_absent_from_contracts(self) -> None:
        for value in (self.agents, self.lead, self.planner, self.task, self.builder):
            for stale in (
                "PLANNING_OUTCOME",
                "INDEPENDENCE_REQUIREMENT",
                "INDEPENDENCE_STATUS",
                "PLANNING_PATH",
                "PLANNER_IMPLEMENTATION",
                "SUPPLIED_APPROVED_PLAN",
                "SAME_RUNTIME_SEPARATED",
            ):
                self.assertNotIn(stale, value)

    def test_contract_probes_are_not_runtime_proof(self) -> None:
        module = (ROOT / "tests/test_planning_control_contract.py").read_text(encoding="utf-8")
        self.assertIn("do not prove runtime lifecycle enforcement", module)


if __name__ == "__main__":
    unittest.main()
