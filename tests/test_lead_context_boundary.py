# made by AI
"""Context-boundary contract: the Lead retains only orchestration facts and
routes all substantive work through fresh bounded Context Boundary Agents.

These marker tests freeze the governing prose consolidated into the
"## Stateless orchestration" section of `agents/lead-agent-prompt.md`. They
pin the literal tokens (stop condition, classification values, ticket and
receipt field names) so the contract cannot silently regress, and confirm the
new doctrine was folded into the existing section rather than appended beside
it. They do not restate the AGENTS.md verification vocabulary; they only check
that the Lead prompt references it.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"


def section(document: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^##\s|\Z)",
        document,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group("body")


class ContextBoundaryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.orch = section(cls.lead, "## Stateless orchestration")

    def test_lead_is_an_orchestration_controller(self) -> None:
        self.assertIn("orchestration controller", self.orch)
        self.assertIn("never needs to understand the task domain", self.orch)

    def test_transition_necessity_test_defines_orchestration_facts(self) -> None:
        self.assertIn("transition-necessity test", self.orch)
        self.assertIn(
            "Information may enter Lead context only if the Lead needs that exact information",
            self.orch,
        )

    def test_substantive_information_distinction_and_governing_test(self) -> None:
        self.assertIn("substantive information", self.orch)
        self.assertIn(
            "does the Lead require this exact information to select, validate, or record the next workflow transition?",
            self.orch,
        )
        self.assertIn(
            "not admitted because it was discovered, is relevant, is useful, or is explanatory",
            self.orch,
        )

    def test_context_boundary_agent_is_a_contract_over_existing_roles(self) -> None:
        self.assertIn("Context Boundary Agent", self.orch)
        self.assertIn("not a new role", self.orch)
        self.assertIn("specializations of one behavioral contract", self.orch)

    def test_dispatch_ticket_allowlist_fields_required(self) -> None:
        for field in [
            "`task_id`",
            "`objective`",
            "`minimum_inputs`",
            "`permitted_work`",
            "`required_orchestration_facts`",
            "`artifact_requirement`",
            "`completion_condition`",
            "`blocker_condition`",
        ]:
            self.assertIn(field, self.orch)
        # The specialized ticket must subordinate to the existing one, not fork it.
        self.assertIn('the "Bounded dispatch ticket" expressed with the fields', self.orch)
        self.assertIn("not a second format", self.orch)

    def test_open_ended_ticket_is_invalid(self) -> None:
        self.assertIn("A ticket is invalid if it requests a general summary", self.orch)
        for phrase in ['"anything relevant"', "all findings", "open-ended recommendation"]:
            self.assertIn(phrase, self.orch)

    def test_receipt_allowlist_fields_required(self) -> None:
        for field in [
            "`outcome`",
            "`artifact_identity`",
            "`orchestration_facts`",
            "`blocker`",
            "`receipt_identity`",
        ]:
            self.assertIn(field, self.orch)
        self.assertIn("only facts named by `required_orchestration_facts` are allowed", self.orch)

    def test_detailed_output_is_referenced_not_returned(self) -> None:
        self.assertIn("detailed results are referenced rather than returned", self.orch)
        self.assertIn(
            "Detailed output stays external or referenced; it is never returned into Lead context.",
            self.orch,
        )

    def test_forward_looking_capability_coverage(self) -> None:
        self.assertIn(
            "newly available or necessary task, role, tool, source, model, or interface",
            self.orch,
        )
        self.assertIn(
            "gains no authority to expand scope merely by existing or by offering a suggestion",
            self.orch,
        )

    def test_new_findings_route_through_classification_only(self) -> None:
        for value in [
            "`acceptance_required`",
            "`blocker_required`",
            "`optional`",
            "`scope_or_authority_change`",
        ]:
            self.assertIn(value, self.orch)
        self.assertIn("never the substantive content", self.orch)
        self.assertIn("A discovery cannot silently expand scope.", self.orch)

    def test_uncertainty_does_not_authorize_lead_investigation(self) -> None:
        self.assertIn("Uncertainty does not authorize Lead investigation.", self.orch)
        self.assertIn(
            "every follow-up question needs a new task identity and its own exact output allowlist",
            self.orch,
        )

    def test_enforceability_stop_condition_is_named(self) -> None:
        self.assertIn("`CONTEXT_BOUNDARY_UNENFORCEABLE`", self.orch)
        self.assertIn("input isolation may be real while return filtering may be only instruction-level", self.orch)

    def test_material_change_invalidates_verification_by_reference(self) -> None:
        self.assertIn("creates a new artifact identity and invalidates prior verification", self.orch)
        self.assertIn("returns to the Prompt Builder when the Task Prompt itself changed", self.orch)
        self.assertIn("behavioral canary", self.orch)
        # Reset rule is referenced, not forked.
        self.assertIn("it does not define a second reset", self.orch)

    def test_one_transition_and_dispatch_first_preserved(self) -> None:
        self.assertIn(
            "One Lead invocation performs at most one lifecycle transition", self.orch
        )
        self.assertIn(
            "must not own two substantive stages in one invocation", self.orch
        )
        self.assertIn("dispatch-first entry", self.orch)


if __name__ == "__main__":
    unittest.main()
