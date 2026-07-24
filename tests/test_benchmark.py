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

    def test_patterns_normalize_markdown_punctuation_and_hyphenation(self) -> None:
        concept = {"patterns": [["trust boundary", "customer input"]]}
        text = "**Customer-input** crossed the trust\u2014boundary."
        self.assertTrue(bm.concept_matches(text, concept))

    def test_patterns_use_word_boundaries(self) -> None:
        concept = {"patterns": [["pass"]]}
        self.assertTrue(bm.concept_matches("The decision is PASS.", concept))
        self.assertFalse(bm.concept_matches("A bypass was performed.", concept))

    def test_bounded_equivalent_phrases_are_supported(self) -> None:
        source = {"patterns": [["implementation", "source of truth"]]}
        simplicity = {"patterns": [["false simplicity"]]}
        safety = {"patterns": [["fewer lines", "not", "safer"]]}
        entities = {"patterns": [["plugin discovery", "not needed"]]}
        self.assertTrue(
            bm.concept_matches("The implementation establishes 8081 as the effective port.", source)
        )
        self.assertTrue(bm.concept_matches("This is false simplification.", simplicity))
        self.assertTrue(bm.concept_matches("Shorter code is not simpler.", safety))
        self.assertTrue(
            bm.concept_matches(
                "Plugin discovery has no current alternative implementation.", entities
            )
        )


class DecisionExtractionTests(unittest.TestCase):
    def test_common_markdown_labels_are_supported(self) -> None:
        examples = {
            "Decision: ACTION": "ACTION",
            "**Decision:** ACTION": "ACTION",
            "Internal decision: PASS": "PASS",
            "Internal Decision \u2014 CONFLICT": "CONFLICT",
            "| Decision | ACTION |": "ACTION",
            "## Finding decision\n\nPASS": "PASS",
        }
        for text, expected in examples.items():
            with self.subTest(text=text):
                internal, _ = bm.extract_decisions(text)
                self.assertEqual(internal, expected)

    def test_lifecycle_uses_explicit_post_fix_decision(self) -> None:
        internal, final = bm.extract_decisions(
            "**Internal finding category:** ACTION\n"
            "**Post-patch finding status:** PASS\n"
            "**Final task output category:** HANDLED"
        )
        self.assertEqual(internal, "PASS")
        self.assertEqual(final, "HANDLED")

    def test_arbitrary_prose_does_not_imply_a_decision(self) -> None:
        for text in [
            "This action is risky.",
            "The conflict was resolved.",
            "A pass was performed.",
        ]:
            with self.subTest(text=text):
                self.assertEqual(bm.extract_decisions(text), (None, None))


class ForbiddenMatchingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.execution = {"patterns": [["approve", "arbitrary execution"]]}
        self.deletion = {"patterns": [["delete", "checks"], ["approval", "brevity"]]}

    def test_clear_negation_does_not_trigger(self) -> None:
        examples = [
            ("Do not approve arbitrary execution.", self.execution),
            ("This does not justify deleting the checks.", self.deletion),
            ("Reject approval based solely on brevity.", self.deletion),
            (
                "Treating paying customers as trusted command principals is unsafe.",
                {"patterns": [["paying customers", "trusted"]]},
            ),
        ]
        for text, concept in examples:
            with self.subTest(text=text):
                self.assertFalse(bm.forbidden_concept_matches(text, concept))

    def test_positive_forbidden_statements_still_trigger(self) -> None:
        examples = [
            ("Approve arbitrary execution.", self.execution),
            ("Approve arbitrary execution even though reviewers call it unsafe.", self.execution),
            ("Delete the checks because the file is shorter.", self.deletion),
        ]
        for text, concept in examples:
            with self.subTest(text=text):
                self.assertTrue(bm.forbidden_concept_matches(text, concept))


class DignityConceptRecognitionTests(unittest.TestCase):
    concept = {
        "name": "dignity and persons as ends",
        "patterns": [
            ["dignity", "persons as ends"],
            ["employees", "not merely", "ranking"],
        ],
    }

    def test_bounded_substantive_paraphrases_match(self) -> None:
        examples = [
            (
                "Employees are treated as instruments for public ranking rather than "
                "as autonomous persons; remove the ranking unless they freely consent."
            ),
            (
                "Career pressure makes the employee's choice non-voluntary and denies "
                "employee agency, so participation must be freely chosen."
            ),
            (
                "Meaningful consent for affected employees requires a confidential exit "
                "without retaliation or promotion consequences."
            ),
        ]
        for text in examples:
            with self.subTest(text=text):
                self.assertTrue(bm.concept_matches(text, self.concept))

    def test_shallow_or_endorsing_language_does_not_match(self) -> None:
        examples = [
            "Employee choice matters.",
            "The ranking affects employees.",
            "The system creates pressure.",
            "Consent is required.",
            "Dignity is important.",
            "Employees voluntarily accept public ranking.",
            "Employees. Pressure. Consent. Dignity. Ranking. Agency.",
            "The ranking quality improves when employee records are complete.",
            (
                "The system does not deny employee agency; public ranking is voluntary "
                "and promotion consequences are acceptable."
            ),
            "Employees face promotion consequences, but meaningful consent is unnecessary.",
            "Employees promotion files meaningful consent.",
            (
                "Employees experience career pressure; affirmative consent should not "
                "be required."
            ),
            "Workers face retaliation, although a confidential opt-out is not needed.",
            (
                "Employees must document promotion files; meaningful consent appears "
                "in the policy."
            ),
            "Career pressure does not undermine employee agency.",
        ]
        for text in examples:
            with self.subTest(text=text):
                self.assertFalse(bm.concept_matches(text, self.concept))


class ReceiptDetectionTests(unittest.TestCase):
    ALIASED_RECEIPT = """### Compact RunSkeptic Receipt
- **Source read:** skeptic.md
- **Permission mode:** read-only
- **DONE:** review complete
- **Major steps:** GATE through VERIFY
- **Thinker coverage:** CH, OM, FE, PO, KT, SH
- **Findings:** one material issue
- **Decision:** ACTION, no edit authorized
- **Verification:** evidence trace complete
- **Unresolved:** none
- **Final category:** HANDLED
"""

    def test_semantic_field_aliases_are_supported(self) -> None:
        self.assertTrue(bm.has_runskeptic_receipt(self.ALIASED_RECEIPT))

    def test_table_receipt_is_supported(self) -> None:
        lines = ["## RunSkeptic Receipt", "| Field | Value |", "| --- | --- |"]
        for line in self.ALIASED_RECEIPT.splitlines()[1:]:
            label, value = line.removeprefix("- **").split(":** ", 1)
            lines.append(f"| {label} | {value} |")
        self.assertTrue(bm.has_runskeptic_receipt("\n".join(lines)))

    def test_heading_receipt_fields_are_supported(self) -> None:
        lines = ["## RunSkeptic Receipt"]
        for line in self.ALIASED_RECEIPT.splitlines()[1:]:
            label, value = line.removeprefix("- **").split(":** ", 1)
            lines.extend((f"### {label}", value))
        self.assertTrue(bm.has_runskeptic_receipt("\n".join(lines)))

    def test_keywords_outside_receipt_structure_do_not_pass(self) -> None:
        prose = (
            "RunSkeptic Receipt is discussed here. Source read and permission mode are "
            "important, as are DONE, thinkers, evidence, decisions, verification, "
            "unresolved questions, and the final category."
        )
        self.assertFalse(bm.has_runskeptic_receipt(prose))


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

    def test_forbidden_findings_keep_their_quality_penalty(self) -> None:
        case = copy.deepcopy(self.cases[0])
        result = bm.score_response(case, "Decision: ACTION\nThis is safe to execute.")
        self.assertGreater(len(result["forbidden_triggered"]), 0)
        expected = (
            len(result["required_matched"])
            + int(result["decision_compatible"])
            + int(result["receipt_present"])
            - 2 * len(result["forbidden_triggered"])
        )
        self.assertEqual(result["quality_points"], expected)

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

    def test_new_scores_identify_scorer_version(self) -> None:
        self.assertEqual(self.good["scorer_version"], "scorer-v3")
        self.assertIn("does not execute a model", self.good["scoring_note"])

    def test_different_scorer_versions_are_uncontrolled(self) -> None:
        candidate = copy.deepcopy(self.good)
        candidate["scorer_version"] = "scorer-v2"
        result = bm.compare_scores(self.good, candidate)
        self.assertEqual(result["verdict"], "uncontrolled")
        self.assertIn("scorer", result["reason"])


class BaselineV1DiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = bm.load_cases()
        cls.responses = bm.read_json(BENCHMARKS / "baselines" / "v1" / "responses.json")
        cls.score = bm.score_run(cls.cases, cls.responses)

    def test_all_decisions_are_extracted_and_compatible(self) -> None:
        self.assertEqual(
            [case["case_id"] for case in self.score["cases"] if not case["internal_decision"]],
            [],
        )
        self.assertEqual(self.score["aggregate"]["compatible_decisions"], 12)

    def test_all_receipts_are_detected(self) -> None:
        self.assertEqual(self.score["aggregate"]["receipt_compliance_count"], 12)

    def test_known_forbidden_negation_errors_are_removed(self) -> None:
        self.assertEqual(self.score["aggregate"]["forbidden_findings"], 0)

    def test_scoring_is_deterministic(self) -> None:
        self.assertEqual(self.score, bm.score_run(self.cases, self.responses))

    def test_dignity_recognition_is_repaired(self) -> None:
        case = next(
            case
            for case in self.score["cases"]
            if case["case_id"] == "coercive-performance-ranking"
        )
        self.assertIn("dignity and persons as ends", case["required_matched"])
        self.assertTrue(case["decision_compatible"])
        self.assertTrue(case["receipt_present"])
        self.assertEqual(case["forbidden_triggered"], [])

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
