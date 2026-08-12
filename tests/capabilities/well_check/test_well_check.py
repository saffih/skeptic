from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).with_name("fixtures")
sys.path.insert(0, str(ROOT))

from capabilities.well_check import well_check as wc  # noqa: E402


def receipt(markdown: str) -> dict[str, object]:
    return wc.check_bytes(markdown.encode("utf-8"), "fixture.md")


def rules(result: dict[str, object]) -> list[str]:
    return [item["rule"] for item in result["violations"]]


class WellSentenceRuleTests(unittest.TestCase):
    def test_structural_syntax_fixture_passes_with_reported_exemptions(self) -> None:
        result = receipt((FIXTURES / "structural-syntax.md").read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "PASS")
        kinds = {item["kind"] for item in result["exemptions"]}
        self.assertTrue({"heading", "fenced-code", "table-row", "list-fragment", "inline-code"}.issubset(kinds))

    def test_warranted_sentence_passes(self) -> None:
        result = receipt("The design uses a ledger because history must remain recoverable.\n")
        self.assertEqual(result["status"], "PASS")

    def test_missing_because_is_a_sentence_violation(self) -> None:
        result = receipt("The design uses a ledger.\n")
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(rules(result), ["WELL-S001"])
        self.assertEqual(result["violations"][0]["line"], 1)

    def test_each_sentence_in_a_paragraph_is_checked(self) -> None:
        result = receipt("The first claim is warranted because it is bounded. The second claim is not.\n")
        self.assertEqual(rules(result), ["WELL-S001"])

    def test_headings_code_and_inline_code_are_not_prose(self) -> None:
        result = receipt(
            "# A heading\n\n```python\nassert value == 'not because'\n```\n\n"
            "The code token `a.b()` is safe because inline code is structural.\n\n`field.name`\n"
        )
        self.assertEqual(result["status"], "PASS")
        kinds = {item["kind"] for item in result["exemptions"]}
        self.assertTrue({"heading", "fenced-code", "inline-code"}.issubset(kinds))

    def test_front_matter_is_an_ast_exemption(self) -> None:
        result = receipt("---\ntitle: Without a warrant\n---\n\nThe design passes because its prose is warranted.\n")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("front-matter", {item["kind"] for item in result["exemptions"]})

    def test_list_fragments_are_exempt_but_complete_list_sentences_are_checked(self) -> None:
        good = receipt("The fields are required because the schema is fixed.\n\n- request id\n- response id\n")
        self.assertEqual(good["status"], "PASS")
        self.assertEqual([item["kind"] for item in good["exemptions"]], ["list-fragment", "list-fragment"])

        bad = receipt("- This item is a complete sentence.\n- This item passes because it has a warrant.\n")
        self.assertEqual(rules(bad), ["WELL-S001"])

    def test_list_fragments_with_decimal_or_abbreviation_are_exempt(self) -> None:
        result = receipt("- version 1.0\n- e.g. metadata\n")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual([item["kind"] for item in result["exemptions"]], ["list-fragment", "list-fragment"])

    def test_tables_schema_notation_and_bare_identifiers_are_exempt(self) -> None:
        result = receipt(
            "field | type\n--- | ---\nrequest-id | string\n\ncanonical-name\n\n"
            "| field | type |\n| --- | --- |\n| result | string |\n"
        )
        self.assertEqual(result["status"], "PASS")
        kinds = [item["kind"] for item in result["exemptions"]]
        self.assertEqual(kinds.count("table-row"), 4)
        self.assertIn("bare-identifier", kinds)

    def test_abbreviations_do_not_create_false_sentence_boundaries(self) -> None:
        result = receipt("The input supports e.g. a stable key because the parser needs one boundary.\n")
        self.assertEqual(result["status"], "PASS")

    def test_ambiguous_blockquote_is_reported_for_manual_review(self) -> None:
        result = receipt("> A quotation has punctuation but no warrant.\n")
        self.assertEqual(result["status"], "REVIEW")
        self.assertIn("WELL-U001", rules(result))
        exemption = result["exemptions"][0]
        self.assertTrue(exemption["requires_manual_review"])
        self.assertEqual(exemption["kind"], "blockquote")

    def test_delimiter_shaped_block_formula_is_fail_closed_for_manual_review(self) -> None:
        result = receipt("$$\nE = mc^2.\n$$\n")
        self.assertEqual(result["status"], "REVIEW")
        self.assertEqual(rules(result), ["WELL-U001"])
        exemption = result["exemptions"][0]
        self.assertTrue(exemption["requires_manual_review"])
        self.assertEqual(exemption["kind"], "possible-block-formula")

    def test_marked_blockquote_example_is_exempt_from_sentence_rule(self) -> None:
        result = receipt("> Example: this quoted text has no warrant of its own.\n")
        self.assertEqual(result["status"], "PASS")
        exemption = result["exemptions"][0]
        self.assertEqual(exemption["kind"], "quoted-example")
        self.assertFalse(exemption["requires_manual_review"])

    def test_fenced_diagram_block_is_structural_syntax(self) -> None:
        # WELL names "diagram blocks" as structurally exempt but defines no
        # diagram grammar; a diagram is only recognized when it is fenced,
        # via the same generic fenced-code path as any other code block.
        result = receipt("```mermaid\ngraph TD; A-->B;\n```\n")
        self.assertEqual(result["status"], "PASS")
        self.assertIn("fenced-code", {item["kind"] for item in result["exemptions"]})


class WellCanonicalNameTests(unittest.TestCase):
    def test_canonical_fixture_passes(self) -> None:
        result = receipt((FIXTURES / "canonical-valid.md").read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "PASS")

    def test_definition_and_exact_reference_pass(self) -> None:
        result = receipt(
            "`stable-name` — This definition is canonical because it remains stable.\n\n"
            "The dependent rule uses `stable-name` because exact lookup is required.\n"
        )
        self.assertEqual(result["status"], "PASS")

    def test_one_word_canonical_name_is_valid(self) -> None:
        # NAME allows zero hyphens; WELL's own text does not require a
        # compound name, so a single lowercase word is a valid canonical name.
        result = receipt(
            "`warrant` — This one-word canonical name is valid because names may be single lowercase words.\n\n"
            "The rule uses `warrant` because exact lookup is required.\n"
        )
        self.assertEqual(result["status"], "PASS")

    def test_heading_definition_and_reference_are_checked_without_sentence_rule(self) -> None:
        result = receipt(
            "### `stable-name` — Canonical heading\n\n"
            "The dependent rule uses `stable-name` because exact lookup is required.\n"
        )
        self.assertEqual(result["status"], "PASS")

    def test_heading_definition_rejects_duplicates_and_malformed_names(self) -> None:
        duplicate = receipt(
            "### `stable-name` — Canonical heading\n\n"
            "### `stable-name` — Duplicate heading\n"
        )
        malformed = receipt("## `Bad_name` — Malformed heading\n")
        self.assertIn("WELL-N002", rules(duplicate))
        self.assertIn("WELL-N001", rules(malformed))

    def test_heading_reference_requires_exact_name(self) -> None:
        result = receipt(
            "`stable-name` — The definition exists because it is canonical.\n\n"
            "## Uses `stable_name`\n"
        )
        self.assertIn("WELL-N003", rules(result))

    def test_malformed_definition_is_rejected(self) -> None:
        result = receipt("`Bad_name` — This definition is malformed because names must be stable.\n")
        self.assertIn("WELL-N001", rules(result))

    def test_duplicate_definition_is_rejected(self) -> None:
        result = receipt(
            "`stable-name` — The first definition exists because it is canonical.\n\n"
            "`stable-name` — The second definition exists because duplicates drift.\n"
        )
        self.assertIn("WELL-N002", rules(result))

    def test_ordinary_backticked_implementation_identifier_is_not_a_reference(self) -> None:
        result = receipt("The parser uses `markdown-it-py` because Markdown parsing is deterministic.\n")
        self.assertEqual(result["status"], "PASS")

    def test_non_exact_reference_is_rejected(self) -> None:
        result = receipt(
            "`stable-name` — The definition exists because it is canonical.\n\n"
            "The rule uses `stable_name` because lookup must be exact.\n"
        )
        self.assertIn("WELL-N003", rules(result))
        self.assertIn("not the exact name `stable-name`", result["violations"][0]["explanation"])

    def test_cross_document_reference_requires_manual_review(self) -> None:
        result = receipt("The rule uses `other.md#stable-name` because ownership is external.\n")
        self.assertEqual(result["status"], "REVIEW")
        self.assertIn("WELL-U001", rules(result))
        self.assertIn("cross-document-reference", {item["kind"] for item in result["exemptions"]})


class WellReceiptAndCliTests(unittest.TestCase):
    def test_receipt_is_deterministic_and_binds_artifact_bytes(self) -> None:
        raw = b"The design is bounded because the fixture is deterministic.\n"
        first = wc.check_bytes(raw, "fixture.md")
        second = wc.check_bytes(raw, "fixture.md")
        self.assertEqual(first, second)
        self.assertEqual(first["artifact_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(first["checker"], {"identity": wc.CHECKER_ID, "version": wc.CHECKER_VERSION})
        self.assertEqual(first["applied_rules"], list(wc.RULES))
        for key in ("artifact", "violations", "exemptions", "status"):
            self.assertIn(key, first)

    def test_cli_emits_json_and_has_pass_fail_review_exit_behavior(self) -> None:
        checker = ROOT / "capabilities" / "well_check" / "well_check.py"
        with tempfile.TemporaryDirectory() as directory:
            good = Path(directory) / "good.md"
            bad = Path(directory) / "bad.md"
            review = Path(directory) / "review.md"
            good.write_text("The document passes because its sentence is warranted.\n", encoding="utf-8")
            bad.write_text("The document fails.\n", encoding="utf-8")
            review.write_text("$$\nE = mc^2.\n$$\n", encoding="utf-8")
            passed = subprocess.run([sys.executable, str(checker), str(good)], text=True, capture_output=True, check=False)
            failed = subprocess.run([sys.executable, str(checker), str(bad)], text=True, capture_output=True, check=False)
            reviewed = subprocess.run([sys.executable, str(checker), str(review)], text=True, capture_output=True, check=False)
        self.assertEqual(passed.returncode, 0)
        self.assertEqual(json.loads(passed.stdout)["status"], "PASS")
        self.assertEqual(failed.returncode, 1)
        failed_receipt = json.loads(failed.stdout)
        self.assertEqual(failed_receipt["status"], "FAIL")
        self.assertIn(f"{bad}:1: WELL-S001:", failed.stderr)
        self.assertEqual(reviewed.returncode, 2)
        self.assertEqual(json.loads(reviewed.stdout)["status"], "REVIEW")

    def test_current_well_authority_is_a_passing_integration_input(self) -> None:
        result = wc.check_document(ROOT / "docs" / "well.md")
        self.assertEqual(result["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
