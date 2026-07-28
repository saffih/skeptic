from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = (ROOT / "architecture/target-task-architecture.md").read_text(encoding="utf-8")
CORE = (ROOT / "agents/target-task.md").read_text(encoding="utf-8")
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")


class TargetTaskArchitectureTests(unittest.TestCase):
    def test_canonical_architecture_is_persisted_and_referenced(self) -> None:
        self.assertIn("source of truth for the intended Target Task design", ARCH)
        self.assertIn("architecture/target-task-architecture.md", AGENTS)
        self.assertIn("architecture/target-task-architecture.md", CORE)

    def test_architecture_covers_all_control_boundaries(self) -> None:
        for phrase in (
            "Correct context", "A slim Body", "Context-growth invariant",
            "No reasoning reconstruction", "### Body", "### Brain", "### Worker",
            "Boundary processing", "Information flow", "References before copied material",
            "Sufficient Handoff", "Source of truth", "Plan acceptance and sealing",
            "Runtime context and execution mode", "Durable checkpoint and resume",
            "Acceptance semantics", "Testable DONE", "Repair sequence",
            "Ultimate success criterion",
        ):
            self.assertIn(phrase, ARCH)

    def test_body_field_contract_is_complete(self) -> None:
        for field in (
            "TARGET_TASK_ID", "TASK_REFERENCE", "AUTHORITY_AND_GLOBAL_CONSTRAINTS",
            "SEALED_PLAN_REFERENCE", "SEALED_PLAN_HASH", "EXECUTION_MODE",
            "OBSERVED_CONTEXT_STATUS", "CURRENT_STEP", "COMPLETED_STEP_IDENTITIES",
            "ACCEPTED_VALIDATED_CLAIMS", "OPEN_FINDINGS", "OPEN_BLOCKERS",
            "MATERIAL_DEVIATIONS", "ARTIFACT_REFERENCES", "NEXT_AUTHORIZED_ACTION",
            "VALIDATION_STATUS", "REVIEW_STATUS",
        ):
            self.assertIn(field, ARCH)
