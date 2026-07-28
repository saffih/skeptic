"""Structural contracts and a controlled context-pressure validation."""
from __future__ import annotations

import unittest
from pathlib import Path

from harness.target_task_context_pressure import HANDOFF_FIELDS, run_context_pressure_experiment

ROOT = Path(__file__).resolve().parents[1]
CORE = (ROOT / "agents/target-task.md").read_text(encoding="utf-8")
BOUNDARY = (ROOT / "agents/boundary-agent.md").read_text(encoding="utf-8")
LEAD = (ROOT / "agents/lead-agent-prompt.md").read_text(encoding="utf-8")


class TargetTaskContextContractTests(unittest.TestCase):
    def test_body_is_slim_and_brain_is_planning_focused(self) -> None:
        for phrase in ("slim Lead/orchestrator", "must not redo Brain planning",
                       "must not ... ingest all" if False else "ingest all\nreferenced artifacts"):
            self.assertIn(phrase, CORE)
        self.assertIn("Brain plans only", CORE)
        self.assertIn("not all raw execution material", CORE)

    def test_bounded_worker_view_and_plan_traceability(self) -> None:
        for phrase in ("sealed-plan step", "hash-bound", "global invariants",
                       "success criteria", "required handoff"):
            self.assertIn(phrase, CORE)

    def test_complete_sufficient_handoff_contract(self) -> None:
        for field in HANDOFF_FIELDS:
            self.assertIn(field, CORE)
        self.assertIn("next authorized", CORE.lower())
        self.assertIn("worker-reported facts", CORE)
        self.assertIn("deterministically\nvalidated facts", CORE)
        self.assertIn("unresolved claims", CORE)

    def test_evidence_references_need_summary_and_retrieval_guidance(self) -> None:
        for phrase in ("ARTIFACT_REFERENCES", "RETRIEVAL_GUIDANCE", "stable paths",
                       "compact summaries"):
            self.assertIn(phrase, CORE)

    def test_recipient_sufficiency_is_independent_and_explicit(self) -> None:
        for phrase in ("HANDOFF_SUFFICIENT: YES", "HANDOFF_SUFFICIENT: NO",
                       "MISSING:", "RETRIEVE:", "REASON:",
                       "never replaces this recipient check"):
            self.assertIn(phrase, CORE)

    def test_progressive_retrieval_precedes_full_artifact(self) -> None:
        for phrase in ("compact handoff", "artifact metadata", "focused\nsearch",
                       "narrow surrounding context", "complete artifact only"):
            self.assertIn(phrase, CORE)
        self.assertIn("never requires whole-artifact reading", CORE)

    def test_limitations_and_uncertainty_survive_compression(self) -> None:
        self.assertIn("LIMITATIONS", CORE)
        self.assertIn("UNRESOLVED", CORE)
        self.assertIn("runtime facts remain `UNKNOWN`", CORE)

    def test_context_isolation_claims_are_truthful(self) -> None:
        for status in ("FRESH_CONTEXT_CONFIRMED", "PARENT_CONTEXT_INHERITED",
                       "CONTEXT_ISOLATION_UNKNOWN"):
            self.assertIn(status, CORE)
            self.assertIn(status, BOUNDARY)
        self.assertIn("does not prove runtime isolation", CORE)

    def test_scratch_state_cannot_override_global_constraints(self) -> None:
        for phrase in ("security", "privacy", "data-location", "no-write",
                       "filesystem constraint", "all writes"):
            self.assertIn(phrase, CORE)

    def test_receipt_and_terminal_vocabulary_are_canonical(self) -> None:
        for status in ("TARGET_TASK_ACCEPTED", "TARGET_TASK_REJECTED",
                       "TARGET_TASK_BLOCKED", "TARGET_TASK_INTEGRITY_FAILURE"):
            self.assertIn(status, CORE)
        for phrase in ("requested and\nobserved routing", "planning-cycle count",
                       "RunSkeptic convergence", "repository/workspace state"):
            self.assertIn(phrase, CORE)

    def test_existing_lead_boundary_contracts_are_referenced_not_replaced(self) -> None:
        self.assertIn("agents/boundary-agent.md", CORE)
        self.assertIn("agents/agent-return.md", CORE)
        self.assertIn("agents/model-routing.md", CORE)
        self.assertIn("Boundary Agent is not required", CORE)
        self.assertIn("does not prove runtime isolation", LEAD)

    def test_pressure_experiment_preserves_correctness_and_limits_reads(self) -> None:
        result = run_context_pressure_experiment()
        self.assertEqual(result["status"], "TARGET_TASK_ACCEPTED")
        self.assertEqual(result["receipt"]["planning_cycles"], 1)
        self.assertEqual(result["receipt"]["context_status"], "CONTEXT_ISOLATION_UNKNOWN")
        self.assertEqual(result["sufficiency"]["HANDOFF_SUFFICIENT"], "NO")
        self.assertEqual(result["handoffs"][0]["HANDOFF_SUFFICIENT"], "NO")
        self.assertEqual(result["handoffs"][1]["HANDOFF_SUFFICIENT"], "YES")
        self.assertEqual(result["focused_extractions"], ("relevant.md:authoritative value",))
        self.assertEqual(set(result["large_artifacts_not_read"]), {"irrelevant.md", "validation.log"})
        self.assertLessEqual(result["repeated_reads"], 1)
        self.assertTrue(result["state"]["plan_unchanged"])
        self.assertEqual(tuple(result["handoff_fields"]), HANDOFF_FIELDS)
        self.assertLess(result["body_state_size"], result["baseline"]["bytes"])
        self.assertEqual(result["body_rotation"]["status"], "BODY_ROTATION_REQUIRED")
        self.assertTrue(result["body_rotation"]["verified"])
        self.assertTrue(result["body_rotation"]["stopped_before_resume"])
        self.assertEqual(result["body_rotation"]["resume_owner"], "FRESH_LUNA_BODY")
        self.assertEqual(result["body_rotation"]["checkpoint"]["PLAN_HASH"], result["plan_hash"])


if __name__ == "__main__":
    unittest.main()
