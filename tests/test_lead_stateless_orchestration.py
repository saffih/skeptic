# made by AI
"""The Lead as a practically stateless orchestrator.

Covers the current `agents/lead-agent-prompt.md` top-of-file orchestration
statement plus the "## Lead responsibilities", "## State", and "## Final
rule" sections: the Lead performs orchestration only and never substantive
work itself; it may only maintain compact orchestration state, select the
next authorized task, dispatch one fresh Boundary Agent, receive and
validate its compact receipt, update orchestration state, and dispatch the
next Boundary Agent or stop -- it must not inspect, analyze, summarize,
interpret, or perform the underlying work. Lead state is limited to a small
allowlist of orchestration fields, never substantive task content. The Lead
never discovers or produces substantive facts; it only receives
already-filtered orchestration facts from Boundary Agent receipts.

Two kinds of coverage, matching repository convention:

- A self-contained frozen decision table encodes the permitted-action and
  state allowlists so the contract cannot silently regress toward the Lead
  performing underlying work or retaining substantive content in its state.
- Marker tests freeze the governing prose in `agents/lead-agent-prompt.md`.
"""
from __future__ import annotations

import re
import unittest
from dataclasses import dataclass
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


# --------------------------------------------------------------------------
# Executable reference decision table
# --------------------------------------------------------------------------

LEAD_PERMITTED_ACTIONS = frozenset(
    {
        "maintain_compact_orchestration_state",
        "select_next_authorized_task",
        "dispatch_one_fresh_boundary_agent",
        "receive_and_validate_compact_receipt",
        "update_orchestration_state",
        "dispatch_next_boundary_agent_or_stop",
    }
)

LEAD_FORBIDDEN_ACTIONS = frozenset(
    {"inspect", "analyze", "summarize", "interpret", "perform_underlying_work"}
)


def lead_may_perform(action: str) -> bool:
    """The Lead may only perform the six enumerated responsibilities; it
    must not inspect, analyze, summarize, interpret, or perform the
    underlying work."""
    if action in LEAD_FORBIDDEN_ACTIONS:
        return False
    return action in LEAD_PERMITTED_ACTIONS


STATE_FIELD_ALLOWLIST = frozenset(
    {
        "current_stage",
        "candidate_identity",
        "consecutive_passes",
        "next_action",
        "blocker",
        "receipt_identities",
    }
)


def state_field_is_permitted(field_name: str) -> bool:
    """Lead state keeps only the minimum orchestration fields; it must not
    retain substantive task content."""
    return field_name in STATE_FIELD_ALLOWLIST


@dataclass(frozen=True)
class FactOrigin:
    """Where a fact entering Lead reasoning actually came from. No field
    has a default: an incomplete case must fail to construct."""

    from_boundary_agent_receipt: bool
    lead_discovered_or_produced_it_directly: bool


def fact_is_admissible(origin: FactOrigin) -> bool:
    """The Lead never discovers or produces substantive facts itself; it
    only receives already-filtered orchestration facts from Boundary Agent
    receipts."""
    if origin.lead_discovered_or_produced_it_directly:
        return False
    return origin.from_boundary_agent_receipt


class LeadPermittedActionTests(unittest.TestCase):
    def test_all_six_responsibilities_are_permitted(self) -> None:
        for action in LEAD_PERMITTED_ACTIONS:
            with self.subTest(action=action):
                self.assertTrue(lead_may_perform(action))

    def test_forbidden_actions_are_rejected(self) -> None:
        for action in LEAD_FORBIDDEN_ACTIONS:
            with self.subTest(action=action):
                self.assertFalse(lead_may_perform(action))

    def test_unlisted_action_is_not_permitted(self) -> None:
        self.assertFalse(lead_may_perform("write_the_implementation_itself"))

    def test_exactly_six_permitted_responsibilities_are_named(self) -> None:
        self.assertEqual(len(LEAD_PERMITTED_ACTIONS), 6)


class StateAllowlistTests(unittest.TestCase):
    def test_all_named_state_fields_are_permitted(self) -> None:
        for field_name in STATE_FIELD_ALLOWLIST:
            with self.subTest(field=field_name):
                self.assertTrue(state_field_is_permitted(field_name))

    def test_substantive_content_field_is_not_permitted(self) -> None:
        self.assertFalse(state_field_is_permitted("full_diff"))
        self.assertFalse(state_field_is_permitted("implementation_notes"))

    def test_exactly_six_state_fields_are_named(self) -> None:
        self.assertEqual(len(STATE_FIELD_ALLOWLIST), 6)


class SubstantiveFactAdmissibilityTests(unittest.TestCase):
    def test_fact_from_receipt_and_not_lead_discovered_is_admissible(self) -> None:
        self.assertTrue(fact_is_admissible(FactOrigin(True, False)))

    def test_fact_lead_discovered_directly_is_never_admissible(self) -> None:
        self.assertFalse(fact_is_admissible(FactOrigin(True, True)))
        self.assertFalse(fact_is_admissible(FactOrigin(False, True)))

    def test_fact_from_neither_source_is_not_admissible(self) -> None:
        self.assertFalse(fact_is_admissible(FactOrigin(False, False)))

    def test_incomplete_origin_raises(self) -> None:
        with self.assertRaises(TypeError):
            FactOrigin(from_boundary_agent_receipt=True)  # type: ignore[call-arg]


# --------------------------------------------------------------------------
# Marker tests: the governing prose must be present in lead-agent-prompt.md
# --------------------------------------------------------------------------


class OrchestrationOnlyMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")

    def test_lead_role_is_orchestration_only(self) -> None:
        self.assertIn("Your role is orchestration only.", self.lead)

    def test_lead_does_not_perform_substantive_work_itself(self) -> None:
        self.assertIn("You do not perform substantive work yourself.", self.lead)


class LeadResponsibilitiesMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.responsibilities = section(cls.lead, "## Lead responsibilities")

    def test_six_permitted_responsibilities_are_enumerated_in_order(self) -> None:
        steps = [
            "maintain compact orchestration state",
            "select the next authorized task",
            "dispatch one fresh Boundary Agent with a bounded objective",
            "receive and validate its compact receipt",
            "update orchestration state",
            "dispatch the next Boundary Agent or stop",
        ]
        last_index = -1
        for step in steps:
            index = self.responsibilities.index(step)
            self.assertGreater(
                index, last_index, f"step out of order or missing: {step}"
            )
            last_index = index

    def test_lead_must_not_perform_underlying_work(self) -> None:
        self.assertIn(
            "The Lead must not inspect, analyze, summarize, interpret, or "
            "perform the underlying work.",
            self.responsibilities,
        )


class StateSectionMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.state = section(cls.lead, "## State")

    def test_minimum_orchestration_state_is_named(self) -> None:
        self.assertIn(
            "Keep only the minimum orchestration state, such as:", self.state
        )
        for field_name in STATE_FIELD_ALLOWLIST:
            self.assertIn(field_name, self.state)

    def test_substantive_task_content_is_excluded_from_state(self) -> None:
        self.assertIn(
            "Do not retain substantive task content in Lead state.", self.state
        )


class FinalRuleMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.final = section(cls.lead, "## Final rule")

    def test_lead_never_discovers_or_produces_substantive_facts(self) -> None:
        self.assertIn(
            "The Lead never discovers or produces substantive facts.",
            self.final,
        )

    def test_lead_only_uses_already_filtered_orchestration_facts(self) -> None:
        self.assertIn(
            "It only receives already-filtered orchestration facts from "
            "Boundary Agents and uses them to choose the next workflow "
            "transition.",
            self.final,
        )


if __name__ == "__main__":
    unittest.main()
