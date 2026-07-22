# made by AI
"""Substantive-action delegation and RunSkeptic verification handling.

Covers the current `agents/lead-agent-prompt.md` "## Core rule" and
"## Verification" sections. The orchestration-only contract has no named
execution-mode packages; the equivalent concept is that every category of
substantive work named in the Core rule -- including testing, review,
RunSkeptic, repair, verification, integration, pushing changes, and
remote-state checks -- is always performed by a fresh Boundary Agent, never
executed inline by the Lead, and role names never create an alternative
execution path. Verification is a specific instance of that rule: RunSkeptic
runs inside a Boundary Agent, its receipt is limited to a stricter allowlist,
the PASS streak resets on an ACTION verdict or any candidate change, and an
ACTION verdict routes only `finding_ids` (via `report_identity`, never the
full report) to a fresh repair Boundary Agent.

Two kinds of coverage, matching repository convention:

- A self-contained frozen decision table encodes the delegation and
  PASS-streak rules so the contract cannot silently regress toward the Lead
  performing a substantive action itself or treating a narrated/reused
  candidate as a genuine consecutive PASS.
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

# The concrete, named substantive actions enumerated in "## Core rule".
# ("any future task that requires domain reasoning or produces detailed
# output" is a forward-looking catch-all, tested separately as prose.)
SUBSTANTIVE_ACTIONS = frozenset(
    {
        "repository_inspection",
        "planning",
        "implementation",
        "testing",
        "review",
        "run_skeptic",
        "interpretation_of_findings",
        "repair",
        "verification",
        "integration",
        "pushing_changes",
        "remote_state_checks",
        "tool_use",
        "external_system_interaction",
    }
)

ROLE_NAMES = frozenset(
    {"implementer", "reviewer", "checker", "advisor", "verifier", "integrator"}
)


def requires_fresh_boundary_agent(action: str) -> bool:
    """Every substantive action must be performed by a fresh Boundary
    Agent, without exception."""
    if action not in SUBSTANTIVE_ACTIONS:
        raise ValueError(f"unknown action: {action}")
    return True


def is_alternative_execution_path(role_name: str) -> bool:
    """Role names are optional descriptions of a Boundary Agent's
    objective. None of them is an alternative execution path that would let
    the Lead perform the work itself under that label."""
    if role_name not in ROLE_NAMES:
        raise ValueError(f"unknown role name: {role_name}")
    return False


@dataclass(frozen=True)
class VerificationState:
    """Consecutive-PASS tracking for one candidate under review. No field
    has a default: an incomplete case must fail to construct."""

    consecutive_passes: int
    candidate_identity: str


def apply_verdict(
    state: VerificationState, verdict: str, new_candidate_identity: str
) -> VerificationState:
    """Any candidate change resets the PASS count to zero. Otherwise, PASS
    increments the streak and ACTION resets it to zero."""
    if verdict not in ("PASS", "ACTION"):
        raise ValueError(f"unknown verdict: {verdict}")
    candidate_changed = new_candidate_identity != state.candidate_identity
    if candidate_changed or verdict == "ACTION":
        return VerificationState(
            consecutive_passes=0, candidate_identity=new_candidate_identity
        )
    return VerificationState(
        consecutive_passes=state.consecutive_passes + 1,
        candidate_identity=new_candidate_identity,
    )


def should_stop_verification(state: VerificationState) -> bool:
    """Stop verification after three consecutive PASS results on the same
    unchanged candidate."""
    return state.consecutive_passes >= 3


RUNSKEPTIC_RECEIPT_ALLOWLIST = frozenset(
    {"candidate_identity", "verdict", "finding_ids", "report_identity", "receipt_identity"}
)


def runskeptic_receipt_is_valid(returned_fields: frozenset) -> bool:
    """A RunSkeptic Boundary Agent receipt may contain only this stricter
    allowlist; the full report must never enter the Lead context."""
    return returned_fields.issubset(RUNSKEPTIC_RECEIPT_ALLOWLIST)


def repair_dispatch_fields(verdict: str) -> frozenset:
    """On ACTION, repair is dispatched to a fresh Boundary Agent using only
    the identified finding_ids (reachable via report_identity) -- never the
    full report body."""
    if verdict != "ACTION":
        raise ValueError("repair is dispatched only on an ACTION verdict")
    return frozenset({"report_identity", "finding_ids"})


class SubstantiveActionDelegationTests(unittest.TestCase):
    def test_every_named_substantive_action_requires_a_boundary_agent(self) -> None:
        for action in SUBSTANTIVE_ACTIONS:
            with self.subTest(action=action):
                self.assertTrue(requires_fresh_boundary_agent(action))

    def test_unknown_action_is_rejected_rather_than_silently_permitted(self) -> None:
        with self.assertRaises(ValueError):
            requires_fresh_boundary_agent("undocumented_future_action")

    def test_no_role_name_is_an_alternative_execution_path(self) -> None:
        for role in ROLE_NAMES:
            with self.subTest(role=role):
                self.assertFalse(is_alternative_execution_path(role))


class VerificationStreakTests(unittest.TestCase):
    def test_pass_increments_streak_on_unchanged_candidate(self) -> None:
        state = VerificationState(consecutive_passes=1, candidate_identity="c1")
        state = apply_verdict(state, "PASS", "c1")
        self.assertEqual(state.consecutive_passes, 2)

    def test_action_resets_streak_to_zero(self) -> None:
        state = VerificationState(consecutive_passes=2, candidate_identity="c1")
        state = apply_verdict(state, "ACTION", "c1")
        self.assertEqual(state.consecutive_passes, 0)

    def test_any_candidate_change_resets_streak_even_on_pass(self) -> None:
        state = VerificationState(consecutive_passes=2, candidate_identity="c1")
        state = apply_verdict(state, "PASS", "c2")
        self.assertEqual(state.consecutive_passes, 0)
        self.assertEqual(state.candidate_identity, "c2")

    def test_three_consecutive_passes_on_unchanged_candidate_stops_verification(
        self,
    ) -> None:
        state = VerificationState(consecutive_passes=0, candidate_identity="c1")
        for _ in range(3):
            state = apply_verdict(state, "PASS", "c1")
        self.assertTrue(should_stop_verification(state))

    def test_two_consecutive_passes_does_not_stop_verification(self) -> None:
        state = VerificationState(consecutive_passes=0, candidate_identity="c1")
        for _ in range(2):
            state = apply_verdict(state, "PASS", "c1")
        self.assertFalse(should_stop_verification(state))

    def test_pass_streak_across_a_candidate_change_never_reaches_three(self) -> None:
        state = VerificationState(consecutive_passes=2, candidate_identity="c1")
        # A repaired/edited candidate is a new identity even after two prior
        # passes; the streak must not carry over.
        state = apply_verdict(state, "PASS", "c2")
        self.assertFalse(should_stop_verification(state))

    def test_unknown_verdict_is_rejected(self) -> None:
        state = VerificationState(consecutive_passes=0, candidate_identity="c1")
        with self.assertRaises(ValueError):
            apply_verdict(state, "MAYBE", "c1")


class RunSkepticReceiptTests(unittest.TestCase):
    def test_allowlisted_fields_are_valid(self) -> None:
        self.assertTrue(
            runskeptic_receipt_is_valid(
                frozenset({"candidate_identity", "verdict", "receipt_identity"})
            )
        )

    def test_full_report_field_is_not_in_the_allowlist(self) -> None:
        self.assertFalse(runskeptic_receipt_is_valid(frozenset({"report"})))
        self.assertNotIn("report", RUNSKEPTIC_RECEIPT_ALLOWLIST)

    def test_repair_dispatch_uses_only_report_identity_and_finding_ids(self) -> None:
        fields = repair_dispatch_fields("ACTION")
        self.assertEqual(fields, frozenset({"report_identity", "finding_ids"}))
        self.assertNotIn("report", fields)

    def test_repair_dispatch_is_only_valid_on_action_verdict(self) -> None:
        with self.assertRaises(ValueError):
            repair_dispatch_fields("PASS")


# --------------------------------------------------------------------------
# Marker tests: the governing prose must be present in lead-agent-prompt.md
# --------------------------------------------------------------------------


class CoreRuleMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.core = section(cls.lead, "## Core rule")

    def test_every_substantive_action_must_be_delegated(self) -> None:
        self.assertIn(
            "Every substantive action must be performed by a fresh Boundary "
            "Agent.",
            self.core,
        )
        self.assertIn("This includes, without exception:", self.core)

    def test_named_substantive_actions_are_enumerated(self) -> None:
        for item in [
            "repository inspection",
            "planning",
            "implementation",
            "testing",
            "review",
            "RunSkeptic",
            "interpretation of findings",
            "repair",
            "verification",
            "integration",
            "pushing changes",
            "remote-state checks",
            "tool use",
            "external-system interaction",
        ]:
            self.assertIn(item, self.core)

    def test_forward_looking_catch_all_is_present(self) -> None:
        self.assertIn(
            "any future task that requires domain reasoning or produces "
            "detailed output",
            self.core,
        )

    def test_role_names_are_not_alternative_execution_paths(self) -> None:
        for role in [
            "implementer",
            "reviewer",
            "checker",
            "advisor",
            "verifier",
            "integrator",
        ]:
            self.assertIn(role, self.core)
        self.assertIn(
            "Role names such as implementer, reviewer, checker, advisor, "
            "verifier, or integrator are optional descriptions of a "
            "Boundary Agent's objective.",
            self.core,
        )
        self.assertIn("They are not alternative execution paths.", self.core)


class VerificationMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.verification = section(cls.lead, "## Verification")

    def test_verification_is_always_performed_by_boundary_agents(self) -> None:
        self.assertIn(
            "Verification is always performed by Boundary Agents.",
            self.verification,
        )

    def test_lead_must_never_list_is_enumerated(self) -> None:
        for must_not in [
            "run RunSkeptic",
            "read a RunSkeptic report",
            "interpret findings",
            "choose a repair strategy",
            "run tests",
            "analyze test output",
        ]:
            self.assertIn(must_not, self.verification)

    def test_runskeptic_receipt_allowlist_is_named(self) -> None:
        for field in RUNSKEPTIC_RECEIPT_ALLOWLIST:
            self.assertIn(field, self.verification)
        self.assertIn(
            "The full report must remain outside the Lead context.",
            self.verification,
        )

    def test_pass_increments_and_action_resets_streak(self) -> None:
        self.assertIn(
            "If the verdict is PASS, increment the consecutive PASS count.",
            self.verification,
        )
        self.assertIn(
            "If the verdict is ACTION, reset the PASS count to zero and "
            "dispatch a fresh Boundary Agent to repair only the identified "
            "findings.",
            self.verification,
        )

    def test_candidate_change_resets_streak(self) -> None:
        self.assertIn(
            "Any candidate change resets the PASS count to zero.",
            self.verification,
        )

    def test_stop_after_three_consecutive_passes(self) -> None:
        self.assertIn(
            "Stop verification after three consecutive PASS results on the "
            "same unchanged candidate.",
            self.verification,
        )


if __name__ == "__main__":
    unittest.main()
