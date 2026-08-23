from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = (ROOT / "skeptic-check" / "README.md").read_text(encoding="utf-8")
import importlib.util
CHECK_PATH = ROOT / "skeptic-check" / "check.py"
SPEC = importlib.util.spec_from_file_location("skeptic_check", CHECK_PATH)
check = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(check)
CASES = check.load_catalog(ROOT / "skeptic-check" / "catalog.json")


class GovernanceTests(unittest.TestCase):
    def test_single_authority_and_runtime_separation(self):
        self.assertIn("single canonical system", README)
        self.assertIn("one active case catalog", README)
        self.assertIn("`skeptic.md` remains the runtime source of truth", README)
        self.assertIn("never overrides `skeptic.md`", README)
        self.assertIn("supersedes the former separate `skeptic-tests.md`, `benchmarks/`, and QuickCompare/`harness/` authorities", README)

    def test_quick_and_full_are_modes_not_separate_suites(self):
        self.assertIn("Quick and Full never maintain separate scenarios or oracles", README)
        quick_ids = {c["id"] for c in CASES["cases"] if c["quick"]}
        all_ids = {c["id"] for c in CASES["cases"]}
        self.assertTrue(quick_ids)
        self.assertTrue(quick_ids < all_ids)

    def test_boolean_differential_and_degrees_are_separate(self):
        for marker in ["check_pass", "promotion_ready", "WIN", "TIE", "LOSS", "UNKNOWN", "0..3"]:
            self.assertIn(marker, README)
        self.assertIn("not collapsed into one promotion score", README)

    def test_cases_are_maintainable_not_candidate_tuned(self):
        for case in CASES["cases"]:
            self.assertTrue(case["why_exists"].strip())
            self.assertTrue(case["stale_when"].strip())
            self.assertTrue(case["provenance"])
            self.assertTrue(case["must_detect"])
            self.assertTrue(case["must_not"])
        self.assertIn("Candidate behavior is never by itself a reason to rewrite a case.", README)

    def test_change_acceptance_and_learning_rules_exist(self):
        for marker in [
            "Change acceptance rule",
            "Section Test",
            "Skeptic Self-Review",
            "Static representation evidence must never be reported as behavioral proof.",
            "Learning: how Skeptic improves",
            "Staleness rule",
            "Run targeted deterministic tests",
            "Run full unittest discovery",
        ]:
            self.assertIn(marker, README)


if __name__ == "__main__":
    unittest.main()
