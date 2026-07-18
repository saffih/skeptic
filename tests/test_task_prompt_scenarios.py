# made by AI
from __future__ import annotations

import unittest
from dataclasses import dataclass, replace
from enum import Enum


class GateDecision(str, Enum):
    PASS = "PASS"
    ACTION = "ACTION"
    DECOMPOSE = "DECOMPOSE"
    CONFLICT = "CONFLICT"


class RoutingState(str, Enum):
    RESOLVED = "resolved"
    REPAIRABLE = "repairable"
    REQUIRED_UNAVAILABLE = "required-unavailable"


@dataclass(frozen=True)
class TaskPromptScenario:
    child_prompts_valid: bool = True
    exact_done: bool = True
    verified_start: bool = True
    authority_clear: bool = True
    dependency_graph_complete: bool = True
    feasible_as_one_task: bool = True
    protected_completion_reserve: bool = True
    durable_evidence_checkpoints: bool = True
    retries_and_gates_bounded: bool = True
    routing: RoutingState = RoutingState.RESOLVED
    integration_required: bool = True
    integration_and_fresh_verification: bool = True
    protocol_proportionate: bool = True
    closure_receipt_complete: bool = True


def task_level_gate(scenario: TaskPromptScenario) -> GateDecision:
    """Executable reference for the documented Task Prompt decision table."""
    if not scenario.authority_clear:
        return GateDecision.CONFLICT
    if scenario.routing is RoutingState.REQUIRED_UNAVAILABLE:
        return GateDecision.CONFLICT
    if not scenario.feasible_as_one_task:
        return GateDecision.DECOMPOSE

    repairable_requirements = [
        scenario.child_prompts_valid,
        scenario.exact_done,
        scenario.verified_start,
        scenario.dependency_graph_complete,
        scenario.protected_completion_reserve,
        scenario.durable_evidence_checkpoints,
        scenario.retries_and_gates_bounded,
        scenario.routing is RoutingState.RESOLVED,
        not scenario.integration_required or scenario.integration_and_fresh_verification,
        scenario.protocol_proportionate,
        scenario.closure_receipt_complete,
    ]
    if not all(repairable_requirements):
        return GateDecision.ACTION
    return GateDecision.PASS


class TaskPromptScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.complete = TaskPromptScenario()

    def test_complete_feasible_task_prompt_passes(self) -> None:
        self.assertEqual(task_level_gate(self.complete), GateDecision.PASS)

    def test_valid_children_cannot_hide_missing_integration_owner(self) -> None:
        scenario = replace(self.complete, integration_and_fresh_verification=False)
        self.assertTrue(scenario.child_prompts_valid)
        self.assertEqual(task_level_gate(scenario), GateDecision.ACTION)

    def test_vague_done_is_action(self) -> None:
        self.assertEqual(
            task_level_gate(replace(self.complete, exact_done=False)),
            GateDecision.ACTION,
        )

    def test_missing_completion_reserve_is_action(self) -> None:
        self.assertEqual(
            task_level_gate(replace(self.complete, protected_completion_reserve=False)),
            GateDecision.ACTION,
        )

    def test_transient_decision_evidence_is_action(self) -> None:
        self.assertEqual(
            task_level_gate(replace(self.complete, durable_evidence_checkpoints=False)),
            GateDecision.ACTION,
        )

    def test_unbounded_retry_loop_is_action(self) -> None:
        self.assertEqual(
            task_level_gate(replace(self.complete, retries_and_gates_bounded=False)),
            GateDecision.ACTION,
        )

    def test_repairable_routing_is_action(self) -> None:
        self.assertEqual(
            task_level_gate(replace(self.complete, routing=RoutingState.REPAIRABLE)),
            GateDecision.ACTION,
        )

    def test_required_unavailable_routing_is_conflict(self) -> None:
        self.assertEqual(
            task_level_gate(
                replace(self.complete, routing=RoutingState.REQUIRED_UNAVAILABLE)
            ),
            GateDecision.CONFLICT,
        )

    def test_clear_infeasible_task_decomposes(self) -> None:
        self.assertEqual(
            task_level_gate(replace(self.complete, feasible_as_one_task=False)),
            GateDecision.DECOMPOSE,
        )

    def test_stopping_at_commit_when_remote_main_is_done_is_action(self) -> None:
        scenario = replace(
            self.complete,
            integration_required=True,
            integration_and_fresh_verification=False,
        )
        self.assertEqual(task_level_gate(scenario), GateDecision.ACTION)

    def test_disproportionate_protocol_is_action(self) -> None:
        self.assertEqual(
            task_level_gate(replace(self.complete, protocol_proportionate=False)),
            GateDecision.ACTION,
        )

    def test_missing_closure_receipt_is_action(self) -> None:
        self.assertEqual(
            task_level_gate(replace(self.complete, closure_receipt_complete=False)),
            GateDecision.ACTION,
        )

    def test_authority_conflict_is_not_decomposed_away(self) -> None:
        scenario = replace(
            self.complete,
            authority_clear=False,
            feasible_as_one_task=False,
        )
        self.assertEqual(task_level_gate(scenario), GateDecision.CONFLICT)


if __name__ == "__main__":
    unittest.main()
