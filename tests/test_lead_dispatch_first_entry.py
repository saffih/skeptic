# made by AI
"""One-transition rule: exactly one Boundary Agent dispatch per Lead
invocation, and the next transition requires a fresh Lead context.

Covers the current `agents/lead-agent-prompt.md` "## One-transition rule"
section: each Lead invocation reads the compact current state, dispatches
one Boundary Agent, receives one compact receipt, updates and persists the
compact state, and terminates. The Lead must not continue through multiple
substantive stages in the same invocation, and the next transition must
begin in a fresh Lead context containing only the compact state and
required receipt identities.

Two kinds of coverage, matching repository convention:

- A self-contained frozen decision table encodes the one-transition rule so
  the contract cannot silently regress toward chaining multiple dispatches
  or substantive stages inside one invocation.
- Marker tests freeze the governing prose in `agents/lead-agent-prompt.md`.
"""
from __future__ import annotations

import hashlib
import json
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


@dataclass(frozen=True)
class LeadInvocation:
    """One Lead invocation under the one-transition rule. No field has a
    default: an incomplete case must fail to construct rather than resolve
    to 'well-formed'."""

    read_current_state: bool
    boundary_agents_dispatched: int
    receipts_received: int
    state_updated_and_persisted: bool
    terminated: bool


def invocation_wellformed(inv: LeadInvocation) -> bool:
    """A well-formed invocation performs each of the five steps exactly
    once: read the compact current state, dispatch one Boundary Agent,
    receive one compact receipt, update and persist the compact state, and
    terminate. Zero or multiple dispatches or receipts, or a missing step,
    all break the rule."""
    return (
        inv.read_current_state
        and inv.boundary_agents_dispatched == 1
        and inv.receipts_received == 1
        and inv.state_updated_and_persisted
        and inv.terminated
    )


@dataclass(frozen=True)
class ContinuationContext:
    """The context available to the next orchestration transition."""

    is_fresh_lead_context: bool
    carries_only_compact_state_and_receipt_identities: bool
    carries_prior_substantive_content: bool


def continuation_is_valid(ctx: ContinuationContext) -> bool:
    """The next transition must begin in a fresh Lead context containing
    only the compact state and required receipt identities -- never prior
    substantive content."""
    return (
        ctx.is_fresh_lead_context
        and ctx.carries_only_compact_state_and_receipt_identities
        and not ctx.carries_prior_substantive_content
    )


# Frozen regression fixture: the anti-pattern this rule forbids -- one Lead
# invocation dispatches multiple Boundary Agents (chains multiple
# substantive stages) before terminating. Any change to this scenario must
# change the hash.
CHAINED_DISPATCH_FIXTURE = {
    "scenario": "lead_dispatches_multiple_boundary_agents_in_one_invocation",
    "read_current_state": True,
    "boundary_agents_dispatched": 3,
    "receipts_received": 3,
    "state_updated_and_persisted": True,
    "terminated": True,
    "expected_wellformed": False,
}
CHAINED_DISPATCH_FIXTURE_SHA256 = (
    "6631123c8c39d69559cf89e6cde41e3a10921ec0b9fc581a28cbf8dfa43b318a"
)


class ChainedDispatchRegressionFixtureTests(unittest.TestCase):
    def test_fixture_is_frozen(self) -> None:
        canonical = json.dumps(CHAINED_DISPATCH_FIXTURE, sort_keys=True).encode(
            "utf-8"
        )
        digest = hashlib.sha256(canonical).hexdigest()
        self.assertEqual(digest, CHAINED_DISPATCH_FIXTURE_SHA256)

    def test_chained_dispatch_is_not_wellformed(self) -> None:
        inv = LeadInvocation(
            read_current_state=CHAINED_DISPATCH_FIXTURE["read_current_state"],
            boundary_agents_dispatched=CHAINED_DISPATCH_FIXTURE[
                "boundary_agents_dispatched"
            ],
            receipts_received=CHAINED_DISPATCH_FIXTURE["receipts_received"],
            state_updated_and_persisted=CHAINED_DISPATCH_FIXTURE[
                "state_updated_and_persisted"
            ],
            terminated=CHAINED_DISPATCH_FIXTURE["terminated"],
        )
        self.assertEqual(
            invocation_wellformed(inv),
            CHAINED_DISPATCH_FIXTURE["expected_wellformed"],
        )


class OneTransitionRuleTests(unittest.TestCase):
    def _clean(self, **overrides) -> LeadInvocation:
        fields = dict(
            read_current_state=True,
            boundary_agents_dispatched=1,
            receipts_received=1,
            state_updated_and_persisted=True,
            terminated=True,
        )
        fields.update(overrides)
        return LeadInvocation(**fields)

    def test_single_dispatch_single_receipt_is_wellformed(self) -> None:
        self.assertTrue(invocation_wellformed(self._clean()))

    def test_zero_dispatches_is_not_wellformed(self) -> None:
        self.assertFalse(
            invocation_wellformed(self._clean(boundary_agents_dispatched=0))
        )

    def test_two_dispatches_is_not_wellformed(self) -> None:
        self.assertFalse(
            invocation_wellformed(self._clean(boundary_agents_dispatched=2))
        )

    def test_two_receipts_is_not_wellformed(self) -> None:
        self.assertFalse(invocation_wellformed(self._clean(receipts_received=2)))

    def test_missing_state_read_is_not_wellformed(self) -> None:
        self.assertFalse(
            invocation_wellformed(self._clean(read_current_state=False))
        )

    def test_missing_state_update_is_not_wellformed(self) -> None:
        self.assertFalse(
            invocation_wellformed(self._clean(state_updated_and_persisted=False))
        )

    def test_missing_termination_is_not_wellformed(self) -> None:
        self.assertFalse(invocation_wellformed(self._clean(terminated=False)))

    def test_incomplete_invocation_raises(self) -> None:
        with self.assertRaises(TypeError):
            LeadInvocation(read_current_state=True)  # type: ignore[call-arg]


class FreshContextContinuationTests(unittest.TestCase):
    def test_fresh_context_with_only_compact_state_is_valid(self) -> None:
        self.assertTrue(continuation_is_valid(ContinuationContext(True, True, False)))

    def test_same_context_continuation_is_invalid(self) -> None:
        self.assertFalse(
            continuation_is_valid(ContinuationContext(False, True, False))
        )

    def test_carrying_prior_substantive_content_is_invalid(self) -> None:
        self.assertFalse(
            continuation_is_valid(ContinuationContext(True, True, True))
        )

    def test_missing_compact_state_carry_over_is_invalid(self) -> None:
        self.assertFalse(
            continuation_is_valid(ContinuationContext(True, False, False))
        )


# --------------------------------------------------------------------------
# Marker tests: the governing prose must be present in lead-agent-prompt.md
# --------------------------------------------------------------------------


class OneTransitionRuleMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.rule = section(cls.lead, "## One-transition rule")

    def test_section_exists_and_is_singular(self) -> None:
        self.assertEqual(self.lead.count("## One-transition rule"), 1)

    def test_only_one_orchestration_transition_per_invocation(self) -> None:
        self.assertIn(
            "Each Lead invocation performs only one orchestration transition:",
            self.rule,
        )

    def test_five_steps_are_enumerated_in_order(self) -> None:
        steps = [
            "read the compact current state",
            "dispatch one Boundary Agent",
            "receive one compact receipt",
            "update and persist the compact state",
            "terminate",
        ]
        last_index = -1
        for step in steps:
            index = self.rule.index(step)
            self.assertGreater(
                index, last_index, f"step out of order or missing: {step}"
            )
            last_index = index

    def test_multiple_substantive_stages_in_one_invocation_is_forbidden(self) -> None:
        self.assertIn(
            "Do not continue through multiple substantive stages in the "
            "same Lead invocation.",
            self.rule,
        )

    def test_next_transition_requires_fresh_lead_context(self) -> None:
        self.assertIn(
            "The next transition must begin in a fresh Lead context "
            "containing only the compact state and required receipt "
            "identities.",
            self.rule,
        )


if __name__ == "__main__":
    unittest.main()
