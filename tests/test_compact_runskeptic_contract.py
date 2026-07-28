from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))
import context_compactness  # noqa: E402


class CompactContractTests(unittest.TestCase):
    def test_planner_is_bounded(self) -> None:
        text = (ROOT / "agents/planner.md").read_text(encoding="utf-8")
        for marker in ("one complete replacement Plan", "may not approve", "execute steps", "claim terminal `DONE`", "Lead independently"):
            self.assertIn(marker, text)

    def test_benchmark_is_strictly_smaller_and_unknowns_are_explicit(self) -> None:
        result = context_compactness.compare()
        self.assertTrue(result["strictly_smaller_bytes"])
        self.assertTrue(result["strictly_smaller_characters"])
        self.assertEqual(result["hidden_runtime_context"], "UNKNOWN")

    def test_compact_packet_has_no_history_material(self) -> None:
        value = json.loads((ROOT / "benchmarks/context/compact_current_state.json").read_text())
        self.assertNotIn("raw_logs", value)
        self.assertNotIn("reports", value)
        self.assertNotIn("plan_versions", value)

    def test_planner_cannot_claim_execution_or_terminal_ownership(self) -> None:
        text = (ROOT / "agents/planner.md").read_text(encoding="utf-8")
        for marker in ("may not approve", "execute steps", "may not", "Lead independently"):
            self.assertIn(marker, text)

    def test_body_packet_excludes_raw_reasoning_and_logs(self) -> None:
        value = json.loads((ROOT / "benchmarks/context/compact_current_state.json").read_text())
        forbidden = {"raw_reasoning", "transcript", "logs", "raw_logs", "diff", "reports"}
        self.assertTrue(forbidden.isdisjoint(value))

    def test_only_root_active_skeptic_definition_exists(self) -> None:
        root_source = (ROOT / "skeptic.md").read_text(encoding="utf-8")
        self.assertIn("RunSkeptic", root_source)
        for path in ROOT.rglob("*.md"):
            if path == ROOT / "skeptic.md" or ".git" in path.parts or "experiments" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("# Skeptic - Detect, Reason, Fix, Verify", text, str(path))


if __name__ == "__main__":
    unittest.main()
