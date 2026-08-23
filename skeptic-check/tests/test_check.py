from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

CHECK_PATH = Path(__file__).resolve().parents[1] / "check.py"
SPEC = importlib.util.spec_from_file_location("skeptic_check", CHECK_PATH)
check = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(check)


class SkepticCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = check.load_catalog(check.DEFAULT_CASES)
        cls.case_map = {c["id"]: c for c in cls.catalog["cases"]}

    def test_catalog_valid(self):
        self.assertEqual(check.validate_catalog(self.catalog), [])

    def test_quick_is_subset_of_full_same_catalog(self):
        quick = check.selected_cases(self.catalog, "quick", [])
        full = check.selected_cases(self.catalog, "full", [])
        self.assertGreater(len(quick), 0)
        self.assertLess(len(quick), len(full))
        self.assertTrue({c["id"] for c in quick}.issubset({c["id"] for c in full}))

    def test_focus_adds_matching_cases_without_second_suite(self):
        base = {c["id"] for c in check.selected_cases(self.catalog, "quick", [])}
        focused = check.selected_cases(self.catalog, "quick", ["security"])
        focused_ids = {c["id"] for c in focused}
        expected = {c["id"] for c in self.catalog["cases"] if "security" in c["focus_tags"]}
        self.assertTrue(base.issubset(focused_ids))
        self.assertTrue(expected.issubset(focused_ids))

    def _judgment(self, cid, result="PASS", dangerous=False, value=2):
        case = self.case_map[cid]
        return {
            "case_id": cid,
            "result": result,
            "dangerous_failure": dangerous,
            "dimensions": {dim: value for dim in case["dimensions"]},
            "notes": "test",
        }

    def test_differential_prefers_dominance_not_average(self):
        cid = "SC-FOCUS-001"
        case = self.case_map[cid]
        base = self._judgment(cid, value=2)
        cand = self._judgment(cid, value=2)
        first, second = case["dimensions"][:2]
        cand["dimensions"][first] = 3
        cand["dimensions"][second] = 1
        self.assertEqual(check.differential(base, cand, case), "UNKNOWN")

    def test_dangerous_new_failure_is_loss(self):
        cid = "SC-TRUST-002"
        case = self.case_map[cid]
        base = self._judgment(cid)
        cand = self._judgment(cid, dangerous=True)
        self.assertEqual(check.differential(base, cand, case), "LOSS")

    def test_pass_over_fail_is_win(self):
        cid = "SC-NORM-001"
        case = self.case_map[cid]
        base = self._judgment(cid, result="FAIL")
        cand = self._judgment(cid, result="PASS")
        self.assertEqual(check.differential(base, cand, case), "WIN")

    def test_judgment_metadata_requires_exact_bindings(self):
        cid = "SC-NORM-001"
        doc = {
            "metadata": {
                "model": "m", "runtime": "r", "settings": {}, "judge": "j",
                "evidence_kind": "behavioral", "blinded": True,
            },
            "judgments": [self._judgment(cid)],
        }
        errors = check.validate_judgments(doc, self.case_map)
        self.assertTrue(any("skeptic_sha256" in e for e in errors))
        self.assertTrue(any("catalog_sha256" in e for e in errors))
        self.assertTrue(any("case_set_sha256" in e for e in errors))

    def test_binding_match_rejects_stale_catalog_or_case_set(self):
        digest = "a" * 64
        case_digest = "b" * 64
        metadata = {
            "skeptic_sha256": "c" * 64,
            "catalog_sha256": digest,
            "case_set_sha256": case_digest,
        }
        self.assertTrue(check.bindings_match(metadata, digest, case_digest))
        self.assertFalse(check.bindings_match(metadata, "d" * 64, case_digest))
        self.assertFalse(check.bindings_match(metadata, digest, "e" * 64))

    def test_behavioral_promotion_requires_blinding_field(self):
        cid = "SC-NORM-001"
        doc = {
            "metadata": {
                "model": "m", "runtime": "r", "settings": {}, "judge": "j",
                "evidence_kind": "behavioral",
                "skeptic_sha256": "a" * 64, "catalog_sha256": "b" * 64,
                "case_set_sha256": "c" * 64,
            },
            "judgments": [self._judgment(cid)],
        }
        errors = check.validate_judgments(doc, self.case_map)
        self.assertTrue(any("blinded" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
