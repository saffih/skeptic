# made by AI
"""Boundary Agent contract and compact receipt allowlist.

Covers the current `agents/lead-agent-prompt.md` "## Boundary Agent contract"
and "## Compact receipt" sections: a Boundary Agent performs the complete
task outside the Lead context, detailed output is persisted externally and
referenced by identity, and a receipt may return only allowlisted fields.
Undeclared or substantive receipt content is rejected with
`CONTEXT_BOUNDARY_VIOLATION`; a runtime that cannot keep detailed Boundary
Agent transcripts out of the Lead context must stop with
`CONTEXT_BOUNDARY_UNENFORCEABLE` rather than proceed on a contaminated
context.

Two kinds of coverage, matching repository convention:

- A self-contained frozen decision table encodes the allowlist/rejection
  rule so the contract cannot silently regress toward accepting undeclared
  or substantive receipt content.
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

ALLOWED_RECEIPT_FIELDS = frozenset(
    {
        "task_id",
        "outcome",
        "candidate_identity",
        "artifact_identity",
        "finding_ids",
        "blocker",
        "next_state",
        "receipt_identity",
    }
)


@dataclass(frozen=True)
class BoundaryAgentReceipt:
    """A receipt as actually returned by a Boundary Agent. No field has a
    default: an incomplete case must fail to construct rather than resolve
    to 'valid'."""

    declared_fields: frozenset
    returned_fields: frozenset
    contains_forbidden_content: bool


def receipt_is_valid(receipt: BoundaryAgentReceipt) -> bool:
    """A Boundary Agent may return only the fields declared in its dispatch,
    and only fields drawn from the compact receipt allowlist. Forbidden
    content (explanations, summaries, reasoning, logs, evidence bodies,
    copied prompts, repository descriptions) invalidates the receipt
    regardless of which field names carried it."""
    if receipt.contains_forbidden_content:
        return False
    if not receipt.returned_fields.issubset(receipt.declared_fields):
        return False
    if not receipt.returned_fields.issubset(ALLOWED_RECEIPT_FIELDS):
        return False
    return True


def outcome_for_invalid_receipt(receipt: BoundaryAgentReceipt) -> str:
    """An invalid receipt is rejected; the Lead stops with
    CONTEXT_BOUNDARY_VIOLATION rather than accepting it."""
    if receipt_is_valid(receipt):
        raise ValueError("receipt is valid; no violation to classify")
    return "CONTEXT_BOUNDARY_VIOLATION"


def stop_condition_for_runtime(can_prevent_detailed_transcripts: bool) -> str | None:
    """If the runtime cannot prevent detailed Boundary Agent transcripts from
    entering the Lead context, stop with CONTEXT_BOUNDARY_UNENFORCEABLE
    rather than proceeding on a contaminated context."""
    if can_prevent_detailed_transcripts:
        return None
    return "CONTEXT_BOUNDARY_UNENFORCEABLE"


class ReceiptAllowlistTests(unittest.TestCase):
    def test_fully_allowlisted_receipt_is_valid(self) -> None:
        receipt = BoundaryAgentReceipt(
            declared_fields=frozenset({"task_id", "outcome", "receipt_identity"}),
            returned_fields=frozenset({"task_id", "outcome", "receipt_identity"}),
            contains_forbidden_content=False,
        )
        self.assertTrue(receipt_is_valid(receipt))

    def test_field_outside_declared_set_is_rejected(self) -> None:
        receipt = BoundaryAgentReceipt(
            declared_fields=frozenset({"task_id", "outcome"}),
            returned_fields=frozenset({"task_id", "outcome", "blocker"}),
            contains_forbidden_content=False,
        )
        self.assertFalse(receipt_is_valid(receipt))
        self.assertEqual(
            outcome_for_invalid_receipt(receipt), "CONTEXT_BOUNDARY_VIOLATION"
        )

    def test_field_outside_global_allowlist_is_rejected_even_if_declared(self) -> None:
        # A dispatch cannot declare a field outside the compact receipt
        # allowlist and thereby authorize it.
        receipt = BoundaryAgentReceipt(
            declared_fields=frozenset({"task_id", "full_diff"}),
            returned_fields=frozenset({"task_id", "full_diff"}),
            contains_forbidden_content=False,
        )
        self.assertFalse(receipt_is_valid(receipt))
        self.assertEqual(
            outcome_for_invalid_receipt(receipt), "CONTEXT_BOUNDARY_VIOLATION"
        )

    def test_substantive_content_invalidates_receipt_regardless_of_fields(self) -> None:
        receipt = BoundaryAgentReceipt(
            declared_fields=frozenset({"task_id", "outcome"}),
            returned_fields=frozenset({"task_id", "outcome"}),
            contains_forbidden_content=True,
        )
        self.assertFalse(receipt_is_valid(receipt))
        self.assertEqual(
            outcome_for_invalid_receipt(receipt), "CONTEXT_BOUNDARY_VIOLATION"
        )

    def test_all_named_allowlist_fields_are_individually_acceptable(self) -> None:
        for allowed_field in ALLOWED_RECEIPT_FIELDS:
            with self.subTest(field=allowed_field):
                receipt = BoundaryAgentReceipt(
                    declared_fields=frozenset({allowed_field}),
                    returned_fields=frozenset({allowed_field}),
                    contains_forbidden_content=False,
                )
                self.assertTrue(receipt_is_valid(receipt))

    def test_incomplete_receipt_raises(self) -> None:
        with self.assertRaises(TypeError):
            BoundaryAgentReceipt(declared_fields=frozenset())  # type: ignore[call-arg]


class UnenforceableBoundaryTests(unittest.TestCase):
    def test_enforceable_runtime_has_no_stop_condition(self) -> None:
        self.assertIsNone(stop_condition_for_runtime(True))

    def test_unenforceable_runtime_stops_with_named_condition(self) -> None:
        self.assertEqual(
            stop_condition_for_runtime(False), "CONTEXT_BOUNDARY_UNENFORCEABLE"
        )


# --------------------------------------------------------------------------
# Marker tests: the governing prose must be present in lead-agent-prompt.md
# --------------------------------------------------------------------------


class BoundaryAgentContractMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.contract = section(cls.lead, "## Boundary Agent contract")

    def test_boundary_agent_receives_bounded_dispatch(self) -> None:
        for item in [
            "one bounded objective",
            "only the minimum inputs required",
            "its permitted authority",
            "the exact receipt fields it may return",
        ]:
            self.assertIn(item, self.contract)

    def test_boundary_agent_performs_complete_task_outside_lead_context(self) -> None:
        self.assertIn(
            "The Boundary Agent performs the complete task outside the Lead context.",
            self.contract,
        )

    def test_detailed_output_stays_out_of_lead_context(self) -> None:
        for item in [
            "Detailed reasoning",
            "repository findings",
            "reports",
            "logs",
            "diffs",
            "test output",
            "evidence",
            "implementation details",
            "advisor discussions",
            "repair strategy",
        ]:
            self.assertIn(item, self.contract)
        self.assertIn("must remain outside the Lead context", self.contract)

    def test_detailed_output_is_persisted_and_referenced_by_identity(self) -> None:
        self.assertIn(
            "the Boundary Agent must persist it as an external artifact and "
            "return only its identity",
            self.contract,
        )


class CompactReceiptMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.receipt = section(cls.lead, "## Compact receipt")

    def test_receipt_limited_to_declared_fields(self) -> None:
        self.assertIn(
            "A Boundary Agent may return only the fields declared in its "
            "dispatch.",
            self.receipt,
        )

    def test_allowlist_fields_are_named(self) -> None:
        for allowed_field in ALLOWED_RECEIPT_FIELDS:
            self.assertIn(allowed_field, self.receipt)

    def test_substantive_content_is_named_and_forbidden(self) -> None:
        for forbidden in [
            "explanations",
            "summaries",
            "reasoning",
            "logs",
            "evidence bodies",
            "copied prompts",
            "repository descriptions",
        ]:
            self.assertIn(forbidden, self.receipt)
        self.assertIn("Do not return", self.receipt)

    def test_undeclared_or_substantive_receipt_is_context_boundary_violation(
        self,
    ) -> None:
        self.assertIn(
            "If a Boundary Agent returns undeclared or substantive "
            "information, reject the receipt and stop with:",
            self.receipt,
        )
        self.assertIn("CONTEXT_BOUNDARY_VIOLATION", self.receipt)

    def test_unenforceable_transcript_boundary_is_named(self) -> None:
        self.assertIn(
            "If the runtime cannot prevent detailed Boundary Agent "
            "transcripts from entering the Lead context, stop with:",
            self.receipt,
        )
        self.assertIn("CONTEXT_BOUNDARY_UNENFORCEABLE", self.receipt)


if __name__ == "__main__":
    unittest.main()
