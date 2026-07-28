"""Static contract tests for the OTP: / TT: protocol triggers.

These tests prove only the written contract, not model behavior. Live model
behavior (activation, planning, sealing, validation, final review,
acceptance, and receipt) requires a controlled manual or agent-dispatched
verification, as with the `TP:` builder alias contract.
"""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
PROTOCOL = ROOT / "agents" / "otp-protocol.md"

# Provider-specific tokens the protocol must not depend on to remain usable
# by any capable model, including Claude.
FORBIDDEN_PROVIDER_TOKENS = [
    "gpt",
    "chatgpt",
    "openai",
    "codex",
    "luna",
]


class OtpProtocolRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        agents = AGENTS.read_text(encoding="utf-8")
        cls.trigger_entry = agents.split(
            "- Activate the Optimized Task Prompt protocol", 1
        )[1].split("- Select model class", 1)[0]
        cls.agents_full = agents
        cls.protocol = PROTOCOL.read_text(encoding="utf-8")

    def test_triggers_point_to_otp_protocol(self) -> None:
        self.assertIn("-> `agents/otp-protocol.md`", self.trigger_entry)
        self.assertIn("`OTP: <Target Task>`", self.trigger_entry)
        self.assertIn("`TT: <Target Task>`", self.trigger_entry)

    def test_trigger_requires_reading_protocol_before_processing(self) -> None:
        self.assertIn(
            "first read `agents/otp-protocol.md` before interpreting or responding",
            self.trigger_entry,
        )
        self.assertIn(
            "process the complete Target Task according to it", self.trigger_entry
        )

    def test_missing_protocol_fails_closed_with_named_status(self) -> None:
        self.assertIn("If the file cannot be read, stop visibly", self.trigger_entry)
        self.assertIn("`OTP_PROTOCOL_UNAVAILABLE`", self.trigger_entry)

    def test_ownership_recorded(self) -> None:
        self.assertIn(
            "`agents/otp-protocol.md` is authoritative for the `OTP:`/`TT:` triggers",
            self.agents_full,
        )

    def test_otp_remains_explicit_trigger(self) -> None:
        self.assertIn("`OTP:` is the explicit trigger.", self.protocol)

    def test_tt_is_compact_equivalent_trigger(self) -> None:
        self.assertIn("`TT:` is the compact trigger.", self.protocol)
        self.assertIn("fully equivalent to", self.protocol)

    def test_otp_tt_redundant_sequence_is_valid(self) -> None:
        self.assertIn("`OTP:\\nTT:`", self.protocol)
        self.assertIn("It is redundant, not a double activation", self.protocol)

    def test_plain_task_does_not_autoinvoke(self) -> None:
        self.assertIn("does not invoke OTP, no matter", self.protocol)
        self.assertIn("Do not infer activation from content or intent.", self.protocol)

    def test_trigger_recognition_tolerant_of_case_and_whitespace(self) -> None:
        self.assertIn("tolerant of ordinary capitalization", self.protocol)
        self.assertIn("surrounding whitespace", self.protocol)

    def test_exactly_one_planning_cycle_unless_replanning(self) -> None:
        self.assertIn(
            "Exactly one planning cycle runs unless replanning is required.",
            self.protocol,
        )

    def test_replanning_is_bounded(self) -> None:
        self.assertIn("Replanning is automatic at most once.", self.protocol)
        self.assertIn("`OTP_BLOCKED`", self.protocol)

    def test_sealed_plan_and_body_acceptance(self) -> None:
        self.assertIn("Body seals it", self.protocol)
        self.assertIn("treat it as\n     immutable", self.protocol.replace("\n   ", "\n   "))

    def test_sealing_bookkeeping_is_distinct_from_deliverable_scope(self) -> None:
        self.assertIn("protocol bookkeeping, not part of the Target Task's own deliverable", self.protocol)
        self.assertIn(
            "which bind the deliverable, not OTP's own record-keeping.",
            self.protocol,
        )

    def test_deterministic_validation_precedes_judgment_review(self) -> None:
        self.assertIn(
            "Deterministic validation always runs before judgment review.",
            self.protocol,
        )

    def test_final_review_mode_is_planned_and_executed(self) -> None:
        self.assertIn("final-review mode", self.protocol)
        self.assertIn("Body executes the mode the plan named.", self.protocol)
        for mode in ("DETERMINISTIC_ONLY", "SELF_REVIEW", "RUNSKEPTIC_REVIEW"):
            self.assertIn(mode, self.protocol)

    def test_final_acceptance_statuses(self) -> None:
        for status in ("OTP_ACCEPTED", "OTP_REJECTED", "OTP_BLOCKED"):
            self.assertIn(status, self.protocol)

    def test_receipt_distinguishes_requested_and_observed_routing(self) -> None:
        self.assertIn("requested routing:", self.protocol)
        self.assertIn("observed routing:", self.protocol)
        self.assertIn("ACTUAL_ROUTING_UNKNOWN", self.protocol)
        self.assertIn("never merged into one", self.protocol)

    def test_body_brain_files_are_optional(self) -> None:
        self.assertIn("experiments/body-brain-artifacts/", self.protocol)
        self.assertIn(
            "not required for a bounded single-session\nOTP task", self.protocol
        )

    def test_no_provider_specific_dependency(self) -> None:
        self.assertIn("provider-neutral", self.protocol)
        lowered = self.protocol.lower()
        for token in FORBIDDEN_PROVIDER_TOKENS:
            self.assertNotIn(token, lowered)
        lowered_entry = self.trigger_entry.lower()
        for token in FORBIDDEN_PROVIDER_TOKENS:
            self.assertNotIn(token, lowered_entry)

    def test_otp_compatibility_preserved(self) -> None:
        self.assertIn(
            "`OTP:` remains fully supported on its own", self.protocol
        )
        self.assertIn(
            "`TT:` is an additional, equivalent compact trigger, not a separate",
            self.protocol,
        )

    def test_runskeptic_contract_not_weakened(self) -> None:
        self.assertIn(
            "OTP does not weaken `skeptic.md`'s RunSkeptic contract",
            self.protocol,
        )


if __name__ == "__main__":
    unittest.main()
