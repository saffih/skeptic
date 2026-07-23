"""Deterministic tests for the lightweight RunSkeptic benchmark."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"
sys.path.insert(0, str(BENCHMARKS))

import benchmark as bm  # noqa: E402
import judge  # noqa: E402


class CaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = bm.load_cases()

    def test_cases_validate(self) -> None:
        summary = bm.validate_cases(self.cases)
        self.assertEqual(summary["case_count"], 12)

    def test_case_ids_are_unique(self) -> None:
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))

    def test_all_current_thinker_families_have_meaningful_coverage(self) -> None:
        summary = bm.validate_cases(self.cases)
        self.assertEqual(set(summary["thinker_families"]), bm.CURRENT_THINKER_FAMILIES)
        family_counts = {family: 0 for family in bm.CURRENT_THINKER_FAMILIES}
        for case in self.cases:
            for tag in case["thinkers"]:
                family_counts[tag.split(":", 1)[0]] += 1
        self.assertTrue(all(count >= 1 for count in family_counts.values()))

    def test_case_thinker_tags_exist_in_current_skeptic(self) -> None:
        for case in self.cases:
            for tag in case["thinkers"]:
                with self.subTest(case=case["id"], tag=tag):
                    self.assertIn(tag, bm.CURRENT_THINKER_TAGS)

    def test_critical_cases_never_expect_pass(self) -> None:
        for case in self.cases:
            if case["critical"]:
                with self.subTest(case=case["id"]):
                    self.assertNotIn("PASS", case["expected_decisions"])

    def test_alternative_patterns_are_case_insensitive(self) -> None:
        concept = {"patterns": [["trust boundary"], ["UNTRUSTED", "boundary"]]}
        self.assertTrue(bm.concept_matches("A TRUST BOUNDARY exists", concept))
        self.assertTrue(bm.concept_matches("untrusted data crossed the Boundary", concept))
        self.assertFalse(bm.concept_matches("trusted internal data", concept))


class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = bm.load_cases()
        cls.good_value = bm.read_json(BENCHMARKS / "example_outputs" / "expected-good.json")
        cls.bad_value = bm.read_json(BENCHMARKS / "example_outputs" / "expected-bad.json")
        cls.good = bm.score_run(cls.cases, cls.good_value)
        cls.bad = bm.score_run(cls.cases, cls.bad_value)

    def test_good_fixture_clearly_outscores_bad(self) -> None:
        self.assertGreater(self.good["aggregate"]["quality_points"], self.bad["aggregate"]["quality_points"] + 20)
        self.assertGreater(self.good["aggregate"]["required_concept_recall"], 0.85)
        self.assertEqual(self.good["aggregate"]["forbidden_findings"], 0)

    def test_receipt_detection_accepts_compliant_receipt(self) -> None:
        response = self.good_value["responses"][0]["response"]
        self.assertTrue(bm.has_runskeptic_receipt(response))

    def test_missing_receipt_is_detected(self) -> None:
        self.assertFalse(bm.has_runskeptic_receipt("Decision: ACTION\nFinal output category: HANDLED"))

    def test_internal_decision_is_distinct_from_final_category(self) -> None:
        internal, final = bm.extract_decisions(
            "Decision: ACTION\nDecision path: fix\nFinal output category: HANDLED"
        )
        self.assertEqual(internal, "ACTION")
        self.assertEqual(final, "HANDLED")

    def test_critical_regression_prevents_candidate_better(self) -> None:
        baseline = copy.deepcopy(self.good)
        base_case = next(case for case in baseline["cases"] if case["critical"])
        first, second = base_case["required_matched"][:2]
        base_case["required_matched"].remove(first)
        base_case["required_missed"].append(first)
        candidate = copy.deepcopy(baseline)
        critical = next(case for case in candidate["cases"] if case["case_id"] == base_case["case_id"])
        critical["required_missed"].remove(first)
        critical["required_matched"].append(first)
        critical["required_matched"].remove(second)
        critical["required_missed"].append(second)
        critical["quality_points"] += 100
        candidate["aggregate"]["quality_points"] += 100
        result = bm.compare_scores(baseline, candidate)
        self.assertNotEqual(result["verdict"], "candidate_better")
        self.assertEqual(result["reason"], "critical regression hard override")

    def test_different_metadata_is_uncontrolled(self) -> None:
        candidate = copy.deepcopy(self.good)
        candidate["metadata"]["settings"] = {"temperature": 1}
        result = bm.compare_scores(self.good, candidate)
        self.assertEqual(result["verdict"], "uncontrolled")
        self.assertFalse(result["controlled"])

    def test_missing_required_metadata_is_uncontrolled(self) -> None:
        baseline = copy.deepcopy(self.good)
        candidate = copy.deepcopy(self.good)
        baseline["metadata"] = candidate["metadata"] = {"model": "same"}
        result = bm.compare_scores(baseline, candidate)
        self.assertEqual(result["verdict"], "uncontrolled")

    def test_longer_output_alone_cannot_make_candidate_better(self) -> None:
        candidate = copy.deepcopy(self.good)
        candidate["aggregate"]["median_estimated_output_tokens"] += 1000
        for case in candidate["cases"]:
            case["estimated_token_count"] += 1000
        result = bm.compare_scores(self.good, candidate)
        self.assertEqual(result["verdict"], "equivalent")


class BlindJudgingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.a = {
            "responses": [
                {"case_id": "c1", "response": "alpha answer"},
                {"case_id": "c2", "response": "alpha second"},
            ]
        }
        self.b = {
            "responses": [
                {"case_id": "c1", "response": "beta answer"},
                {"case_id": "c2", "response": "beta second"},
            ]
        }

    def test_blinding_is_deterministic_for_fixed_seed(self) -> None:
        packet1, key1 = judge.build_blind_packet(self.a, self.b, 12345)
        packet2, key2 = judge.build_blind_packet(self.a, self.b, 12345)
        self.assertEqual(packet1, packet2)
        self.assertEqual(key1, key2)

    def test_blind_packet_does_not_expose_input_identity(self) -> None:
        packet, key = judge.build_blind_packet(self.a, self.b, 12345)
        packet_text = json.dumps(packet)
        self.assertNotIn("input_a", packet_text)
        self.assertNotIn("input_b", packet_text)
        self.assertIn("input_a", json.dumps(key))


if __name__ == "__main__":
    unittest.main()
