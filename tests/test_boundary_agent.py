from __future__ import annotations

import sys
import unittest
from pathlib import Path

from harness.governance_checks import (
    BOUNDARY_INVALID,
    BOUNDARY_VALID,
    check_agent_envelope,
    check_boundary_governance,
    check_skeptic_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY = (ROOT / "agents" / "boundary-agent.md").read_text(encoding="utf-8")
LEAD = (ROOT / "agents" / "lead-agent-prompt.md").read_text(encoding="utf-8")
TASK = (ROOT / "agents" / "task-prompt.md").read_text(encoding="utf-8")
BOUNDARY_COMPACT = " ".join(BOUNDARY.split())
sys.path.insert(0, str(ROOT / "benchmarks"))
import benchmark as bm  # noqa: E402


class BoundaryGovernanceTests(unittest.TestCase):
    def test_compact_direct_delegation_needs_no_boundary_agent(self) -> None:
        prompts = (
            "Delegate this compact formatting task directly and validate the output.",
            "Do not use a Boundary Agent for every delegation.",
            "Do not claim that a Boundary Agent proves substantive correctness.",
        )
        for prompt in prompts:
            with self.subTest(prompt=prompt):
                self.assertEqual(check_boundary_governance(prompt)["result"], BOUNDARY_VALID)

    def test_material_boundary_accepts_low_cost_routing(self) -> None:
        self.assertIn("1. deterministic tool or script", BOUNDARY)
        self.assertIn("2. free or local agent", BOUNDARY)
        self.assertIn("3. smallest low-effort model", BOUNDARY)
        self.assertEqual(check_boundary_governance(BOUNDARY)["result"], BOUNDARY_VALID)

    def test_correctness_proof_claim_is_rejected(self) -> None:
        result = check_boundary_governance(
            "The Boundary Agent proves substantive correctness."
        )
        self.assertEqual(result["result"], BOUNDARY_INVALID)

    def test_universal_fresh_context_claim_is_rejected(self) -> None:
        result = check_boundary_governance("Delegated contexts are always fresh.")
        self.assertEqual(result["result"], BOUNDARY_INVALID)

    def test_recursive_delegation_requires_transitive_obligations(self) -> None:
        invalid = check_boundary_governance("Delegated agents may delegate further.")
        valid = check_boundary_governance(
            "Recursive delegation is transitive within the subtree: use "
            "deterministic-first routing, conditional Boundary Agent selection, "
            "Agent Completion Envelope validation, independent work acceptance, "
            "and compact upward reporting."
        )
        self.assertEqual(invalid["result"], BOUNDARY_INVALID)
        self.assertEqual(valid["result"], BOUNDARY_VALID)

    def test_artifact_first_guidance_is_conditional(self) -> None:
        self.assertIn("when persistence or reuse materially helps", BOUNDARY.lower())
        self.assertIn("Keep small decision-critical instructions", BOUNDARY)
        self.assertIn("Do not prescribe a universal directory layout", BOUNDARY_COMPACT)

    def test_boundary_does_not_inherit_worker_model(self) -> None:
        self.assertIn(
            "does not inherit the substantive worker's model or effort",
            BOUNDARY,
        )

    def test_false_isolation_and_universal_boundary_claims_are_rejected(self) -> None:
        for prompt in (
            "A Boundary Agent proves runtime isolation.",
            "We must use a Boundary Agent for every delegation.",
            "The Boundary Agent must use the strongest model.",
        ):
            with self.subTest(prompt=prompt):
                self.assertEqual(
                    check_boundary_governance(prompt)["result"], BOUNDARY_INVALID
                )

    def test_context_statuses_and_truth_limit_exist(self) -> None:
        for status in (
            "FRESH_CONTEXT_CONFIRMED",
            "PARENT_CONTEXT_INHERITED",
            "CONTEXT_ISOLATION_UNKNOWN",
        ):
            self.assertIn(status, BOUNDARY)
        self.assertIn("does not prove runtime isolation or substantive correctness", BOUNDARY)

    def test_transitive_rule_does_not_create_global_lead(self) -> None:
        self.assertIn("These rules are transitive", BOUNDARY)
        self.assertIn("without becoming the global Lead", BOUNDARY_COMPACT)
        self.assertIn("does not become the global Lead", TASK)

    def test_agent_envelope_semantics_remain_intact(self) -> None:
        envelope = """BEGIN_AGENT_RETURN
dispatch_id: BA-1
status: COMPLETE
output: artifact-ref
validation: PASS
blocker: NONE
END_AGENT_RETURN
"""
        self.assertEqual(
            check_agent_envelope(envelope, "BA-1", True)["result"],
            "AGENT_ENVELOPE_VALID",
        )

    def test_runskeptic_receipt_semantics_remain_intact(self) -> None:
        receipt = """## RunSkeptic report
Final task output category: HANDLED

### RunSkeptic Receipt
- **Source read:** skeptic.md SHA 63602be10e0e532ce512aaac0ea6a4d3cd67ce09
- **Companion files read:** agents/task-prompt.md
- **Permission mode:** read-only
- **DONE:** complete
- **Prompt review / feasibility:** Task Prompt / feasible
- **Major steps run:** GATE -> FUNDAMENTAL SCAN -> MAP -> CONFIDENCE -> STABILIZE -> EVIDENCE -> DECIDE -> ACT skipped -> VERIFY -> LEARN
- **Thinkers considered:** CH, OM, FE, PO, KT, SH
- **Evidence used:** artifact
- **Decision path:** PASS
- **Verification performed:** tests
- **Unresolved conflicts / unknowns:** none
- **Final output category:** HANDLED
"""
        self.assertEqual(
            check_skeptic_receipt(receipt, "skeptic.md", None, True)["result"],
            "SKEPTIC_RECEIPT_VALID",
        )

    def test_frozen_benchmark_behavior_remains_unchanged(self) -> None:
        score = bm.score_run(
            bm.load_cases(),
            bm.read_json(ROOT / "benchmarks" / "baselines" / "v1" / "responses.json"),
        )
        aggregate = score["aggregate"]
        self.assertEqual(aggregate["required_concepts_matched"], 52)
        self.assertEqual(aggregate["compatible_decisions"], 12)
        self.assertEqual(aggregate["receipt_compliance_count"], 12)
        self.assertEqual(aggregate["forbidden_findings"], 0)


if __name__ == "__main__":
    unittest.main()
