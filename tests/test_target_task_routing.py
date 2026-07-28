"""Static routing and compatibility contracts for canonical Target Task."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
CORE = (ROOT / "agents/target-task.md").read_text(encoding="utf-8")
ALIAS = (ROOT / "agents/otp-protocol.md").read_text(encoding="utf-8")


class TargetTaskRoutingTests(unittest.TestCase):
    def test_tt_is_canonical_and_otp_is_subordinate(self) -> None:
        self.assertIn("canonical Target Task protocol", AGENTS)
        self.assertIn("`TT: <Target Task>` is canonical", AGENTS)
        self.assertIn("`OTP: <Target Task>` is a compatibility alias", AGENTS)
        self.assertIn("only a compatibility stub", AGENTS)
        self.assertNotIn("Optimized Task Prompt", AGENTS)

    def test_entry_map_routes_to_canonical_file(self) -> None:
        self.assertIn("-> `agents/target-task.md`", AGENTS)
        self.assertIn("first read `agents/target-task.md`", AGENTS)

    def test_plain_text_does_not_activate(self) -> None:
        self.assertIn("Plain text does not activate Target Task", CORE)
        self.assertIn("never infer activation", CORE)

    def test_redundant_compatibility_forms_activate_once(self) -> None:
        self.assertIn("activates exactly once", CORE)
        self.assertIn("OTP:+TT:", CORE)

    def test_alias_is_a_stub_not_a_second_protocol(self) -> None:
        self.assertIn("canonical Target Task", ALIAS)
        self.assertIn("no competing protocol definition", ALIAS)
        self.assertLess(len(ALIAS), 1200)

    def test_legacy_statuses_map_to_canonical_statuses(self) -> None:
        for status in ("ACCEPTED", "REJECTED", "BLOCKED", "INTEGRITY_FAILURE"):
            self.assertIn(f"OTP_{status}", ALIAS)
            self.assertIn(f"TARGET_TASK_{status}", ALIAS)

    def test_provider_neutrality(self) -> None:
        forbidden = ("openai", "chatgpt", "codex", "gpt-")
        for text in (CORE, AGENTS):
            lowered = text.lower()
            for token in forbidden:
                self.assertNotIn(token, lowered)

    def test_tp_builder_route_is_unchanged(self) -> None:
        self.assertIn("`TP: <objective>`", AGENTS)
        self.assertIn("agents/task-prompt-builder.md", AGENTS)
        self.assertIn("TP:", CORE)

    def test_no_active_canonical_reference_to_removed_otp_filename(self) -> None:
        canonical = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "agents").glob("*.md")
            if path.name != "otp-protocol.md"
        )
        self.assertNotIn("agents/otp-protocol.md` is authoritative", canonical)


if __name__ == "__main__":
    unittest.main()
