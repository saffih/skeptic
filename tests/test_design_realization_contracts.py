# made by AI
from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKEPTIC = (ROOT / "skeptic.md").read_text(encoding="utf-8")
CASES = json.loads((ROOT / "tests" / "design_realization_cases.json").read_text(encoding="utf-8"))


class DesignRealizationContractTests(unittest.TestCase):
    def test_suite_has_balanced_change_coupled_falsifiers_and_controls(self) -> None:
        cases = CASES["cases"]
        self.assertEqual(len(cases), 12)
        counts = Counter(case["change"] for case in cases)
        self.assertEqual(
            counts,
            {
                "boundary-grounding": 3,
                "additive-focus": 3,
                "normative-warrant": 3,
                "claim-driven-verification": 3,
            },
        )
        for case in cases:
            self.assertTrue(case["scenario"].strip())
            self.assertTrue(case["oracle"].strip())
            self.assertTrue(case["dangerous_failure"].strip())
        self.assertTrue(any(case["kind"] == "clean-control" for case in cases))
        self.assertTrue(any(case["kind"] == "falsifier" for case in cases))

    def test_boundary_is_positively_grounded_and_falsified(self) -> None:
        self.assertIn("positively ground the material review boundary", SKEPTIC)
        self.assertIn("do not infer a safe boundary merely because no wider coupling was discovered", SKEPTIC)
        self.assertIn("challenge the assumed boundary with evidence capable of exposing materially plausible invalidating conditions", SKEPTIC)

    def test_additive_focus_preserves_complete_review_inside_bound_scope(self) -> None:
        self.assertIn("Within the bound scope", SKEPTIC)
        self.assertIn("additional adversarial attention", SKEPTIC)
        self.assertIn("without narrowing the otherwise applicable review", SKEPTIC)

    def test_normative_warrant_does_not_confuse_permission_with_norm(self) -> None:
        prefix = "the applicable normative basis:"
        line = next(line for line in SKEPTIC.splitlines() if prefix in line)
        self.assertIn("requirement", line)
        self.assertIn("contract", line)
        self.assertIn("design", line)
        self.assertIn("policy", line)
        self.assertIn("Skeptic-owned rule", line)
        self.assertNotIn("permission", line)
        self.assertIn("the established current fact and evidence that conflict with that normative basis", SKEPTIC)

    def test_permission_remains_a_separate_action_gate(self) -> None:
        self.assertIn("Do not modify files unless DECIDE says FIX and edits are explicitly allowed.", SKEPTIC)
        self.assertIn("Runs are read-only unless fixing is explicitly authorized", SKEPTIC)

    def test_verification_is_claim_driven_not_count_driven(self) -> None:
        self.assertIn("checks that directly exercise the intended result and material preserved constraints", SKEPTIC)
        for dimension in [
            "consequence",
            "dependency reach",
            "irreversibility",
            "uncertainty",
            "trust elevation",
            "claim strength",
        ]:
            self.assertIn(dimension, SKEPTIC)
        self.assertNotIn("3-5 targeted spot checks", SKEPTIC)

    def test_small_change_and_high_consequence_cases_both_exist(self) -> None:
        by_id = {case["id"]: case for case in CASES["cases"]}
        self.assertIn("arbitrary minimum number of checks", by_id["VR01"]["oracle"])
        self.assertIn("dependency reach", by_id["VR02"]["oracle"])
        self.assertIn("test count cannot substitute", by_id["VR03"]["oracle"])

    def test_permission_only_case_explicitly_refutes_fix_authority(self) -> None:
        by_id = {case["id"]: case for case in CASES["cases"]}
        self.assertIn("Permission alone does not establish", by_id["NW03"]["oracle"])
        self.assertIn("Use edit permission itself as the normative basis", by_id["NW03"]["dangerous_failure"])


if __name__ == "__main__":
    unittest.main()
