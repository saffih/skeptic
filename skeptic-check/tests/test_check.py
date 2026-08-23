from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
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
        focused = check.selected_cases(self.catalog, "quick", ["authority"])
        focused_ids = {c["id"] for c in focused}
        expected = {c["id"] for c in self.catalog["cases"] if "authority" in c["focus_tags"]}
        self.assertTrue(base.issubset(focused_ids))
        self.assertTrue(expected.issubset(focused_ids))

    def _judgment(self, cid, result="PASS", dangerous=False, value=2, response="response"):
        case = self.case_map[cid]
        return {
            "case_id": cid,
            "result": result,
            "dangerous_failure": dangerous,
            "response_sha256": check.sha256_text(response),
            "dimensions": {dim: value for dim in case["dimensions"]},
            "notes": "test",
        }

    def _metadata(self, skeptic="a", evidence="semantic", blinded=False):
        return {
            "model": "m", "runtime": "r", "settings": {"effort": "low"}, "judge": "j",
            "evidence_kind": evidence, "blinded": blinded,
            "skeptic_sha256": skeptic * 64, "catalog_sha256": "b" * 64,
            "case_set_sha256": "c" * 64,
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

    def test_semantic_judgment_requires_response_hash(self):
        cid = "SC-NORM-001"
        item = self._judgment(cid)
        item.pop("response_sha256")
        doc = {"metadata": self._metadata(), "judgments": [item]}
        errors = check.validate_judgments(doc, self.case_map)
        self.assertTrue(any("response_sha256" in e for e in errors))

    def test_judgment_metadata_requires_exact_bindings(self):
        cid = "SC-NORM-001"
        metadata = self._metadata()
        for key in ("skeptic_sha256", "catalog_sha256", "case_set_sha256"):
            metadata.pop(key)
        doc = {"metadata": metadata, "judgments": [self._judgment(cid)]}
        errors = check.validate_judgments(doc, self.case_map)
        self.assertTrue(any("skeptic_sha256" in e for e in errors))
        self.assertTrue(any("catalog_sha256" in e for e in errors))
        self.assertTrue(any("case_set_sha256" in e for e in errors))

    def test_response_bundle_must_hash_match_judgment(self):
        cid = "SC-NORM-001"
        expected = {cid}
        meta = self._metadata()
        judgments = {"metadata": meta, "judgments": [self._judgment(cid, response="actual")]}
        responses = {
            "metadata": {k: meta[k] for k in ("model", "runtime", "settings", "skeptic_sha256", "catalog_sha256", "case_set_sha256")},
            "responses": [{"case_id": cid, "response": "actual"}],
        }
        self.assertTrue(check.response_bundle_matches(responses, judgments, expected, "b" * 64, "c" * 64))
        responses["responses"][0]["response"] = "different"
        self.assertFalse(check.response_bundle_matches(responses, judgments, expected, "b" * 64, "c" * 64))

    def test_binding_match_rejects_stale_catalog_or_case_set(self):
        digest = "a" * 64
        case_digest = "b" * 64
        metadata = {"skeptic_sha256": "c" * 64, "catalog_sha256": digest, "case_set_sha256": case_digest}
        self.assertTrue(check.bindings_match(metadata, digest, case_digest))
        self.assertFalse(check.bindings_match(metadata, "d" * 64, case_digest))
        self.assertFalse(check.bindings_match(metadata, digest, "e" * 64))

    def test_default_promotion_evidence_is_semantic_not_behavioral(self):
        parser = check.parser()
        args = parser.parse_args(["compare", "--mode", "full", "--baseline", "a.json", "--candidate", "b.json"])
        self.assertEqual(args.required_evidence, "semantic")
        self.assertTrue(check.evidence_satisfies("semantic", "semantic", False))
        self.assertFalse(check.evidence_satisfies("static", "semantic", False))

    def test_behavioral_promotion_requires_blinding(self):
        self.assertFalse(check.evidence_satisfies("behavioral", "semantic", False))
        self.assertFalse(check.evidence_satisfies("behavioral", "behavioral", False))
        self.assertTrue(check.evidence_satisfies("behavioral", "behavioral", True))

    def test_semantic_compare_requires_response_bundles(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            chosen = check.selected_cases(self.catalog, "full", [])
            catalog_digest = check.catalog_sha256(check.DEFAULT_CASES, self.catalog)
            case_digest = check.case_set_sha256(chosen)
            ids = [c["id"] for c in chosen]
            def doc(s):
                meta = {
                    "model": "m", "runtime": "r", "settings": {}, "judge": "j",
                    "evidence_kind": "semantic", "blinded": False,
                    "skeptic_sha256": s * 64,
                    "catalog_sha256": catalog_digest,
                    "case_set_sha256": case_digest,
                }
                return {"metadata": meta, "judgments": [self._judgment(cid) for cid in ids]}
            (td / "a.json").write_text(json.dumps(doc("a")), encoding="utf-8")
            (td / "b.json").write_text(json.dumps(doc("d")), encoding="utf-8")
            args = argparse.Namespace(
                cases=check.DEFAULT_CASES, mode="full", focus=[], baseline=td / "a.json",
                candidate=td / "b.json", baseline_responses=None, candidate_responses=None,
                required_evidence="semantic", output=None,
            )
            with self.assertRaisesRegex(SystemExit, "requires --baseline-responses"):
                check.cmd_compare(args)


if __name__ == "__main__":
    unittest.main()
