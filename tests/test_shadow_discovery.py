from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = ROOT / "benchmarks" / "discovery"
MANIFEST_PATH = DISCOVERY / "manifest.json"
CASES_DIR = DISCOVERY / "cases"
GOLDEN_CASES = ROOT / "benchmarks" / "cases.json"
QUICK_MANIFEST = ROOT / "harness" / "quick-v1-manifest.json"
QUICK_FIXTURE_ROOT = ROOT / "harness"

EXPECTED_MAIN = "8d99e3bf5c8b41e5c52eabadaf14b3abef835d38"
EXPECTED_ARCHIVE = "197bf70d35ce791de7de7499a58bb2a4f970450e"
EXPECTED_IDS = [f"SD0{i}" for i in range(1, 7)]

REQUIRED_CASE_FIELDS = {
    "id",
    "title",
    "category",
    "version",
    "status",
    "original_authorship",
    "provenance",
    "artifact",
    "review_request",
    "expected_material_mechanism",
    "acceptable_alternative_findings",
    "prohibited_false_positives",
    "dangerous_failures",
    "notes",
}

LIST_FIELDS = {
    "expected_material_mechanism",
    "acceptable_alternative_findings",
    "prohibited_false_positives",
    "dangerous_failures",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value) -> str:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    return " ".join(text.lower().split())


class ShadowDiscoverySuiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_json(MANIFEST_PATH)
        cls.entries = cls.manifest["cases"]
        cls.cases = {
            entry["id"]: load_json(DISCOVERY / entry["path"])
            for entry in cls.entries
        }

    def test_manifest_is_explicitly_non_gating(self) -> None:
        self.assertEqual(self.manifest["suite_id"], "shadow-discovery-v1")
        self.assertEqual(self.manifest["version"], 1)
        self.assertEqual(self.manifest["status"], "non-gating")
        self.assertIs(self.manifest["gating"], False)
        self.assertEqual(self.manifest["pinned_main"], EXPECTED_MAIN)
        self.assertEqual(self.manifest["archive_source"], EXPECTED_ARCHIVE)

    def test_manifest_lists_exactly_six_ordered_cases(self) -> None:
        ids = [entry["id"] for entry in self.entries]
        self.assertEqual(ids, EXPECTED_IDS)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.cases), 6)

    def test_manifest_paths_are_local_unique_json_files(self) -> None:
        paths = [entry["path"] for entry in self.entries]
        self.assertEqual(len(paths), len(set(paths)))
        for path_text in paths:
            self.assertRegex(path_text, r"^cases/SD0[1-6]-[a-z0-9-]+\.json$")
            path = DISCOVERY / path_text
            self.assertTrue(path.is_file())
            self.assertEqual(path.parent, CASES_DIR)

    def test_cases_have_complete_typed_structure(self) -> None:
        for case_id, case in self.cases.items():
            with self.subTest(case_id=case_id):
                self.assertEqual(set(case), REQUIRED_CASE_FIELDS)
                self.assertEqual(case["id"], case_id)
                self.assertRegex(case_id, r"^SD0[1-6]$")
                self.assertEqual(case["version"], 1)
                self.assertEqual(case["status"], "non-gating")

                for field in REQUIRED_CASE_FIELDS - LIST_FIELDS - {"version", "provenance"}:
                    self.assertIsInstance(case[field], str)
                    self.assertTrue(case[field].strip())

                for field in LIST_FIELDS:
                    value = case[field]
                    self.assertIsInstance(value, list)
                    self.assertGreaterEqual(len(value), 2)
                    self.assertTrue(all(isinstance(item, str) and item.strip() for item in value))

    def test_provenance_is_pinned_and_contains_source_ids(self) -> None:
        for case_id, case in self.cases.items():
            with self.subTest(case_id=case_id):
                provenance = case["provenance"]
                self.assertEqual(
                    set(provenance),
                    {"archive_commit", "source_paths", "source_ids"},
                )
                self.assertEqual(provenance["archive_commit"], EXPECTED_ARCHIVE)
                self.assertTrue(provenance["source_paths"])
                self.assertTrue(provenance["source_ids"])
                self.assertTrue(
                    all(isinstance(path, str) and path for path in provenance["source_paths"])
                )
                self.assertTrue(
                    all(isinstance(source_id, str) and source_id for source_id in provenance["source_ids"])
                )

    def test_cases_are_original_discovery_fixtures_not_historical_outputs(self) -> None:
        forbidden = re.compile(
            r"\b(model response|judge output|baseline score|candidate win|"
            r"baseline win|three consecutive pass)\b",
            re.IGNORECASE,
        )
        for case_id, case in self.cases.items():
            with self.subTest(case_id=case_id):
                combined = "\n".join(
                    [
                        case["artifact"],
                        case["review_request"],
                        *case["expected_material_mechanism"],
                        *case["acceptable_alternative_findings"],
                        *case["prohibited_false_positives"],
                        *case["dangerous_failures"],
                    ]
                )
                self.assertIsNone(forbidden.search(combined))
                self.assertIn("Original discovery fixture", case["original_authorship"])

    def test_artifacts_are_unique(self) -> None:
        artifacts = [normalize(case["artifact"]) for case in self.cases.values()]
        self.assertEqual(len(artifacts), len(set(artifacts)))

    def test_artifacts_do_not_duplicate_stable_golden_cases(self) -> None:
        golden = {
            normalize(case["artifact"])
            for case in load_json(GOLDEN_CASES)
        }
        for case_id, case in self.cases.items():
            with self.subTest(case_id=case_id):
                self.assertNotIn(normalize(case["artifact"]), golden)

    def test_artifacts_do_not_duplicate_quickcompare_visible_fixtures(self) -> None:
        quick_manifest = load_json(QUICK_MANIFEST)
        quick_artifacts = set()
        for relative in quick_manifest["visible_fixtures"]:
            fixture = load_json(QUICK_FIXTURE_ROOT / relative)
            quick_artifacts.add(normalize(fixture["artifact"]))

        for case_id, case in self.cases.items():
            with self.subTest(case_id=case_id):
                self.assertNotIn(normalize(case["artifact"]), quick_artifacts)

    def test_categories_and_primary_mechanisms_are_distinct(self) -> None:
        categories = [case["category"] for case in self.cases.values()]
        first_mechanisms = [
            normalize(case["expected_material_mechanism"][0])
            for case in self.cases.values()
        ]
        self.assertEqual(len(categories), len(set(categories)))
        self.assertEqual(len(first_mechanisms), len(set(first_mechanisms)))

    def test_manifest_contains_no_scorer_or_verdict_contract(self) -> None:
        text = MANIFEST_PATH.read_text(encoding="utf-8").lower()
        self.assertNotIn("scorer_version", text)
        self.assertNotIn('"verdict"', text)
        self.assertIn("cannot gate promotion", text)

    def test_readme_preserves_non_gating_boundary(self) -> None:
        readme = normalize(
            (DISCOVERY / "README.md").read_text(encoding="utf-8")
        )
        for marker in [
            "non-gating",
            "does not have a scorer",
            "fresh current-main baseline",
            "Do not commit historical model answers",
        ]:
            self.assertIn(normalize(marker), readme)


if __name__ == "__main__":
    unittest.main()
