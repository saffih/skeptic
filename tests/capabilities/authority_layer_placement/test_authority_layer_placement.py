import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from capabilities.authority_layer_placement.authority_layer_placement import (
    CHAIN_BYTE_SIZE,
    CHAIN_PROFILE,
    CHAIN_SHA256,
    SCHEMA_PACKET,
    SCHEMA_REQUEST,
    SCHEMA_RESULT,
    prepare_request,
    validate_packet_and_result,
)


class AuthorityLayerPlacementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.output_dir = self.root / "out"
        self.output_dir.mkdir()
        self.doc = self.root / "docs" / "design.md"
        self.doc.parent.mkdir()
        self.doc.write_text(
            "# Title\n"
            "- shared design choice\n"
            "local implementation note\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def request(self):
        raw = self.doc.read_bytes()
        return {
            "schema": SCHEMA_REQUEST,
            "request_id": "REQ-1",
            "repository_root": {"path": str(self.root), "canonical_path": str(self.root.resolve())},
            "authority_chain": {
                "profile": CHAIN_PROFILE,
                "path": "docs/design-authority-chain.md",
                "sha256": CHAIN_SHA256,
                "byte_size": CHAIN_BYTE_SIZE,
            },
            "documents": [
                {
                    "document_id": "doc-1",
                    "path": "docs/design.md",
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "byte_size": len(raw),
                    "declared_link": "SOFTWARE_DESIGN",
                }
            ],
            "item_selectors": None,
            "output_dir": "out",
            "limits": {
                "max_documents": 4,
                "max_document_bytes": 4096,
                "max_items": 16,
                "max_output_bytes": 65536,
                "max_semantic_input_bytes": 65536,
                "max_decomposition_depth": 2,
            },
            "mode": "REPORT_ONLY",
        }

    def valid_result(self, packet):
        units = packet["source_units"]
        return {
            "schema": SCHEMA_RESULT,
            "request_id": packet["request_id"],
            "packet_sha256": packet["packet_sha256"],
            "execution": {
                "semantic_attempts": 1,
                "schema_correction_retries": 0,
                "schema_correction_evidence": None,
                "transport_retries": 0,
                "routing_observation": "OBSERVED",
                "routing_host_evidence": {"host_receipt_sha256": "1" * 64},
            },
            "items": [
                {
                    "item_id": f"item-{i}",
                    "parent_item_id": None,
                    "source": {
                        "document_id": unit["document_id"],
                        "line_start": unit["line_start"],
                        "line_end": unit["line_end"],
                        "quote": unit["bytes"],
                        "quote_sha256": unit["sha256"],
                    },
                    "normalized_proposition": f"prop-{i}",
                    "candidate_links": ["SOFTWARE_DESIGN"],
                    "selected_link": "SOFTWARE_DESIGN",
                    "disposition": "ASSIGN",
                    "return_target": None,
                    "move_target": None,
                    "authority_reason": "shared durable design meaning",
                    "upstream_dependencies": [],
                    "downstream_consumers": [],
                    "evidence_level": "OBSERVED",
                    "confidence": "HIGH",
                    "open_unknowns": [],
                    "required_next_action": "none",
                    "conflict": None,
                }
                for i, unit in enumerate(units, start=1)
            ],
            "summary": {"assigned": len(units), "split": 0, "returned": 0, "moved": 0, "conflicts": 0},
        }

    def test_prepare_and_validate_valid_input_passes(self):
        packet_path = self.output_dir / "packet.json"
        packet, prepare_report = prepare_request(self.request(), packet_path)
        self.assertEqual(prepare_report["status"], "PREPARED")
        self.assertEqual(packet["schema"], SCHEMA_PACKET)
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, self.valid_result(packet), report_path)
        self.assertEqual(report["status"], "VALID")

    def test_prepare_rejects_hash_mismatch(self):
        request = self.request()
        request["documents"][0]["sha256"] = "0" * 64
        packet, report = prepare_request(request, self.output_dir / "packet.json")
        self.assertIsNone(packet)
        self.assertEqual(report["errors"][0]["code"], "DOCUMENT_HASH_MISMATCH")

    def test_prepare_rejects_path_escape(self):
        request = self.request()
        request["documents"][0]["path"] = "../escape.md"
        packet, report = prepare_request(request, self.output_dir / "packet.json")
        self.assertIsNone(packet)
        self.assertEqual(report["errors"][0]["code"], "UNSAFE_PATH")

    def test_prepare_rejects_duplicate_document_ids(self):
        request = self.request()
        request["documents"].append(dict(request["documents"][0]))
        packet, report = prepare_request(request, self.output_dir / "packet.json")
        self.assertIsNone(packet)
        self.assertEqual(report["errors"][0]["code"], "DUPLICATE_DOCUMENT_ID")

    def test_validate_rejects_missing_source_item(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["items"].pop()
        result["summary"]["assigned"] -= 1
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertEqual(report["status"], "INVALID")
        self.assertIn("MISSING_SOURCE_ITEM", [error["code"] for error in report["errors"]])

    def test_validate_rejects_missing_split_child(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        unit = packet["source_units"][0]
        result = self.valid_result(packet)
        result["items"][0] = {
            **result["items"][0],
            "disposition": "SPLIT",
            "selected_link": None,
        }
        result["summary"] = {"assigned": len(packet["source_units"]) - 1, "split": 1, "returned": 0, "moved": 0, "conflicts": 0}
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("MISSING_SPLIT_CHILD", [error["code"] for error in report["errors"]])

    def test_validate_rejects_split_child_with_invalid_lineage_or_coverage(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        parent = packet["source_units"][0]
        result = self.valid_result(packet)
        result["items"][0] = {
            **result["items"][0],
            "item_id": "parent",
            "disposition": "SPLIT",
            "selected_link": None,
        }
        result["items"].append(
            {
                **result["items"][1],
                "item_id": "child",
                "parent_item_id": "parent",
                "source": {
                    "document_id": parent["document_id"],
                    "line_start": parent["line_start"],
                    "line_end": parent["line_end"],
                    "quote": "not-covered\n",
                    "quote_sha256": hashlib.sha256(b"not-covered\n").hexdigest(),
                },
            }
        )
        result["summary"] = {"assigned": len(packet["source_units"]), "split": 1, "returned": 0, "moved": 0, "conflicts": 0}
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        codes = [error["code"] for error in report["errors"]]
        self.assertIn("SPLIT_QUOTE_OUT_OF_RANGE", codes)
        self.assertIn("SPLIT_COVERAGE_MISMATCH", codes)

    def test_validate_rejects_invalid_return_target(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["items"][0]["disposition"] = "RETURN_UPSTREAM"
        result["items"][0]["selected_link"] = "SOFTWARE_DESIGN"
        result["items"][0]["return_target"] = "REALIZATION"
        result["summary"] = {"assigned": len(packet["source_units"]) - 1, "split": 0, "returned": 1, "moved": 0, "conflicts": 0}
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("INVALID_RETURN_TARGET", [error["code"] for error in report["errors"]])

    def test_validate_rejects_invalid_move_target(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["items"][0]["disposition"] = "MOVE_DOWNSTREAM"
        result["items"][0]["selected_link"] = "SOFTWARE_DESIGN"
        result["items"][0]["move_target"] = "ARCHITECTURE"
        result["summary"] = {"assigned": len(packet["source_units"]) - 1, "split": 0, "returned": 0, "moved": 1, "conflicts": 0}
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("INVALID_MOVE_TARGET", [error["code"] for error in report["errors"]])

    def test_validate_rejects_incomplete_conflict(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["items"][0]["disposition"] = "CONFLICT"
        result["items"][0]["selected_link"] = None
        result["items"][0]["conflict"] = None
        result["summary"] = {"assigned": len(packet["source_units"]) - 1, "split": 0, "returned": 0, "moved": 0, "conflicts": 1}
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("INCOMPLETE_CONFLICT", [error["code"] for error in report["errors"]])

    def test_validate_rejects_duplicate_assignment(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["items"].append(dict(result["items"][0], item_id="dup"))
        result["summary"]["assigned"] += 1
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("DUPLICATE_ASSIGNMENT", [error["code"] for error in report["errors"]])

    def test_validate_rejects_summary_mismatch(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["summary"]["assigned"] = 999
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("SUMMARY_MISMATCH", [error["code"] for error in report["errors"]])

    def test_validate_rejects_semantic_ceiling_overflow(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        packet["limits"]["max_semantic_input_bytes"] = 1
        result = self.valid_result(packet)
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("SEMANTIC_INPUT_BYTE_CEILING_EXCEEDED", [error["code"] for error in report["errors"]])

    def test_validate_rejects_decomposition_depth_above_two(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        packet["limits"]["max_decomposition_depth"] = 3
        result = self.valid_result(packet)
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("DECOMPOSITION_DEPTH", [error["code"] for error in report["errors"]])

    def test_validate_rejects_nonzero_transport_retry(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["execution"]["transport_retries"] = 1
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("TRANSPORT_RETRIES", [error["code"] for error in report["errors"]])

    def test_validate_rejects_more_than_one_schema_retry(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["execution"]["schema_correction_retries"] = 2
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("SCHEMA_CORRECTION_RETRIES", [error["code"] for error in report["errors"]])

    def test_validate_rejects_schema_retry_without_evidence(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["execution"]["schema_correction_retries"] = 1
        result["execution"]["schema_correction_evidence"] = None
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("SCHEMA_CORRECTION_EVIDENCE", [error["code"] for error in report["errors"]])

    def test_validate_rejects_semantic_attempts_not_one(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["execution"]["semantic_attempts"] = 2
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("SEMANTIC_ATTEMPTS", [error["code"] for error in report["errors"]])

    def test_validate_rejects_unobserved_routing(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["execution"]["routing_observation"] = "UNOBSERVED"
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("ROUTING_UNOBSERVED", [error["code"] for error in report["errors"]])

    def test_validate_rejects_observed_routing_without_host_evidence(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["execution"]["routing_host_evidence"] = None
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("ROUTING_HOST_EVIDENCE_MISSING", [error["code"] for error in report["errors"]])

    def test_validate_rejects_selected_link_that_violates_standard_6_precedence(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        result["items"][0]["candidate_links"] = ["SOFTWARE_DESIGN", "ARCHITECTURE"]
        result["items"][0]["selected_link"] = "SOFTWARE_DESIGN"
        report_path = self.output_dir / "report.json"
        report_path.write_text("", encoding="utf-8")
        report = validate_packet_and_result(packet, result, report_path)
        self.assertIn("SELECTED_LINK_PRECEDENCE", [error["code"] for error in report["errors"]])

    def test_validate_rejects_forbidden_output_mutation(self):
        packet, _ = prepare_request(self.request(), self.output_dir / "packet.json")
        result = self.valid_result(packet)
        report = validate_packet_and_result(packet, result, self.root / "report.json")
        self.assertIn("FORBIDDEN_OUTPUT_MUTATION", [error["code"] for error in report["errors"]])

    def test_direct_cli_help_from_repository_root_succeeds(self):
        repo_root = Path(__file__).resolve().parents[3]
        script = repo_root / "capabilities" / "authority_layer_placement" / "authority_layer_placement.py"
        proc = subprocess.run(
            [sys.executable, str(script), "--help"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("usage:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
