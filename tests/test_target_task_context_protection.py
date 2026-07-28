"""Behavioral and structural checks for the canonical Target Task adapter."""
from __future__ import annotations

import unittest
from pathlib import Path

from harness.target_task_context_pressure import progressive_retrieve, sufficient_handoff


ROOT = Path(__file__).resolve().parents[1]
CORE = (ROOT / "agents/target-task.md").read_text(encoding="utf-8")
ADAPTER = (ROOT / "agents/target-task-repository-adapter.md").read_text(encoding="utf-8")


class TargetTaskContextProtectionTests(unittest.TestCase):
    def test_canonical_core_owns_naming_and_protection(self) -> None:
        for phrase in ("Target Task", "Sufficient Handoff", "Retrieve progressively", "Context is a constrained"):
            self.assertIn(phrase, CORE)
        self.assertIn("skeptic.md", ADAPTER)

    def test_progressive_retrieval_stays_within_pressure_budget(self) -> None:
        source = "# Metadata\nowner\n# Relevant\ncontext handoff decision\n" + "# Noise\n" + ("irrelevant " * 80)
        result = progressive_retrieve(source, "handoff decision", 96)
        payload = "".join(result.headings) + "".join(result.excerpts)
        self.assertLessEqual(len(payload), 96)
        self.assertTrue(any("handoff" in item.lower() for item in result.excerpts))
        self.assertFalse(any("irrelevant irrelevant" in item for item in result.excerpts))

    def test_sufficient_handoff_is_reference_first_and_bounded(self) -> None:
        handoff = sufficient_handoff("TT-1", ("agents/target-task.md#Context protection",), "validate retrieval")
        self.assertEqual(handoff["task_id"], "TT-1")
        self.assertEqual(handoff["source_refs"], ("agents/target-task.md#Context protection",))
        self.assertNotIn("content", handoff)
        self.assertEqual(handoff["context_status"], "CONTEXT_ISOLATION_UNKNOWN")

    def test_portable_core_does_not_own_repository_state(self) -> None:
        self.assertIn("owns no repository state", CORE)
        self.assertIn("repository adapter", CORE)
        self.assertNotIn("/Users/", CORE)


if __name__ == "__main__":
    unittest.main()
