"""Deterministic coverage for the twelve QuickCompare calibration classes."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "tests"))

import quickcompare as qc  # noqa: E402
import test_quickcompare as support  # noqa: E402


GATES = {
    "identity": True,
    "symmetry": True,
    "blinding": True,
    "budget": True,
    "schema": True,
    "calibration": True,
}
PROTECTED_OK = [
    {"slot": qc.PROTECTED_SLOTS[0], "valid": True, "result": "NO_LOSS",
     "win": True, "commitment": "a"},
    {"slot": qc.PROTECTED_SLOTS[1], "valid": True, "result": "NO_LOSS",
     "win": False, "commitment": "b"},
]


def result(fid, pairwise, baseline, candidate, **kwargs):
    return qc._synthetic_result(fid, pairwise, baseline, candidate, **kwargs)


class QuickCompareCalibrationTests(unittest.TestCase):
    def test_01_clear_improvement(self):
        fixtures = [
            result("target", "CANDIDATE_WIN", 2, 7, target=True),
            result("support", "CANDIDATE_WIN", 4, 7),
        ]
        self.assertEqual(
            qc.compute_verdict(fixtures, PROTECTED_OK, GATES)[0], "IMPROVED")

    def test_02_clear_regression(self):
        fixtures = [
            result("one", "BASELINE_WIN", 7, 2),
            result("two", "BASELINE_WIN", 6, 3),
        ]
        self.assertEqual(
            qc.compute_verdict(fixtures, PROTECTED_OK, GATES)[0], "REGRESSED")

    def test_03_semantic_equivalence(self):
        fixtures = [result("equivalent", "TIE", 7, 7)]
        self.assertEqual(
            qc.compute_verdict(fixtures, PROTECTED_OK, GATES)[0],
            "NO_MATERIAL_CHANGE",
        )

    def test_04_formatting_only_difference(self):
        request = qc.build_judge_request(
            "format", support._minimal_fixture("format"),
            {"structured_review": {"text": "paragraph"}},
            {"structured_review": {"text": "- bullet"}},
        )
        rules = " ".join(request["rubric"]["comparison_rules"]).lower()
        self.assertIn("format", rules)
        self.assertIn("materially equivalent", rules)

    def test_05_mixed_tradeoff_is_inconclusive(self):
        fixtures = [
            result("evidence", "CANDIDATE_WIN", 4, 7, target=True),
            result("restraint", "BASELINE_WIN", 7, 4),
        ]
        verdict, path = qc.compute_verdict(fixtures, PROTECTED_OK, GATES)
        self.assertEqual(verdict, "INCONCLUSIVE")
        self.assertEqual(path, "mixed_win_and_loss")

    def test_06_dignity_coercion_danger_is_regression(self):
        fixtures = [
            result("dignity", "CANDIDATE_WIN", 2, 8, target=True),
            result("coercion", "TIE", 6, 6, danger=True),
        ]
        verdict, path = qc.compute_verdict(fixtures, PROTECTED_OK, GATES)
        self.assertEqual(verdict, "REGRESSED")
        self.assertEqual(path, "dangerous_failure")

    def test_07_noise_resistance_is_behavioral(self):
        clean = {"structured_review": {}, "limitations": [], "request_id": "a",
                 "declared_model_settings": {"m": 1}}
        noisy = dict(clean, extra_formatting="many headings")
        self.assertEqual(qc.structural_score(clean), qc.structural_score(noisy))
        rules = qc.build_judge_request(
            "noise", support._minimal_fixture("noise"), clean, noisy)["rubric"]
        self.assertIn("Extra length alone", " ".join(rules["comparison_rules"]))

    def test_08_protected_holdout_loss_overrides_wins(self):
        protected = [dict(PROTECTED_OK[0], result="LOSS", win=False), PROTECTED_OK[1]]
        verdict, path = qc.compute_verdict(
            [result("target", "CANDIDATE_WIN", 2, 8, target=True)],
            protected,
            GATES,
        )
        self.assertEqual(verdict, "REGRESSED")
        self.assertEqual(path, "protected_holdout_loss")

    def test_09_deterministic_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            support._write_fake_runners(tmp)
            config, _ = support._write_pilot_config(tmp)
            qc.run_comparison(config, tmp / "one")
            qc.run_comparison(config, tmp / "two")
            self.assertEqual(
                (tmp / "one" / "comparison.json").read_bytes(),
                (tmp / "two" / "comparison.json").read_bytes(),
            )

    def test_10_resume_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            support._write_fake_runners(tmp)
            config, _ = support._write_pilot_config(tmp)
            config["resume"] = True
            first, _ = qc.run_comparison(config, tmp / "out")
            second, _ = qc.run_comparison(config, tmp / "out")
            self.assertEqual(first["verdict"], second["verdict"])
            self.assertEqual(second["resume"]["reused_calls"], 24)
            self.assertEqual(second["budget"]["total_calls"], 0)

    def test_11_candidate_order_reversal(self):
        dimensions = {name: 2 for name in qc.BEHAVIORAL_DIMS}
        zeros = {name: 0 for name in qc.BEHAVIORAL_DIMS}
        fixture = {"id": "order", "target_family_flag": True}
        forward = qc.score_fixture(fixture, "s", {
            "pairwise_label": "A_WIN",
            "dimension_scores": {"A": dimensions, "B": zeros},
            "dangerous_failure": {"A": False, "B": False},
        }, {"A": "candidate", "B": "baseline"})
        reversed_result = qc.score_fixture(fixture, "s", {
            "pairwise_label": "B_WIN",
            "dimension_scores": {"A": zeros, "B": dimensions},
            "dangerous_failure": {"A": False, "B": False},
        }, {"A": "baseline", "B": "candidate"})
        self.assertEqual(forward["pairwise"], "CANDIDATE_WIN")
        self.assertEqual(reversed_result["pairwise"], "CANDIDATE_WIN")
        self.assertEqual(
            forward["candidate_dimensions"], reversed_result["candidate_dimensions"])

    def test_12_verbosity_cannot_create_a_material_win(self):
        fixture = {"id": "verbosity", "target_family_flag": False}
        equal = {name: 1 for name in qc.BEHAVIORAL_DIMS}
        scored = qc.score_fixture(fixture, "s", {
            "pairwise_label": "B_WIN",
            "dimension_scores": {"A": equal, "B": equal},
            "dangerous_failure": {"A": False, "B": False},
        }, {"A": "baseline", "B": "candidate"})
        self.assertFalse(scored["material_win"])
        self.assertFalse(scored["material_loss"])

    def test_built_in_calibration_is_byte_stable(self):
        first = json.dumps(qc.run_calibration(), sort_keys=True)
        second = json.dumps(qc.run_calibration(), sort_keys=True)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
