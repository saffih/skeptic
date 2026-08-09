"""Fail-closed preparation and structural validation for authority-layer placement."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

try:
    from capabilities.body_state.body_state import BodyStateError, _hash_file, _path, _short
except ModuleNotFoundError:
    if __package__ not in {None, ""}:
        raise
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from capabilities.body_state.body_state import BodyStateError, _hash_file, _path, _short

SCHEMA_REQUEST = "AuthorityPlacementRequest@1"
SCHEMA_PACKET = "AuthorityPlacementPacket@1"
SCHEMA_PREPARE_REPORT = "AuthorityPlacementPrepareReport@1"
SCHEMA_RESULT = "AuthorityPlacementResult@1"
SCHEMA_VALIDATION_REPORT = "AuthorityPlacementValidationReport@1"

CHAIN_PROFILE = "STANDARD_6"
CHAIN_LINKS = (
    "GOVERNING_INPUTS",
    "ARCHITECTURE",
    "SOFTWARE_DESIGN",
    "IMPLEMENTATION_PLAN",
    "REALIZATION",
    "VERIFICATION_EVIDENCE",
)
CHAIN_BYTES = (
    "STANDARD_6\n"
    "GOVERNING_INPUTS\n"
    "ARCHITECTURE\n"
    "SOFTWARE_DESIGN\n"
    "IMPLEMENTATION_PLAN\n"
    "REALIZATION\n"
    "VERIFICATION_EVIDENCE\n"
).encode("utf-8")
CHAIN_SHA256 = hashlib.sha256(CHAIN_BYTES).hexdigest()
CHAIN_BYTE_SIZE = len(CHAIN_BYTES)

REQUEST_FIELDS = {
    "schema",
    "request_id",
    "repository_root",
    "authority_chain",
    "documents",
    "item_selectors",
    "output_dir",
    "limits",
    "mode",
}
ROOT_FIELDS = {"path", "canonical_path"}
CHAIN_REQUEST_FIELDS = {"profile", "path", "sha256", "byte_size"}
DOCUMENT_FIELDS = {"document_id", "path", "sha256", "byte_size", "declared_link"}
SELECTOR_FIELDS = {"document_id", "line_start", "line_end"}
LIMIT_FIELDS = {
    "max_documents",
    "max_document_bytes",
    "max_items",
    "max_output_bytes",
    "max_semantic_input_bytes",
    "max_decomposition_depth",
}
PACKET_FIELDS = {
    "schema",
    "request_id",
    "repository_root",
    "authority_chain",
    "documents",
    "source_units",
    "output_dir",
    "limits",
    "packet_sha256",
}
CHAIN_PACKET_FIELDS = {"profile", "path", "sha256", "byte_size", "bytes"}
SOURCE_UNIT_FIELDS = {"unit_id", "document_id", "line_start", "line_end", "kind", "bytes", "sha256"}
PREPARE_REPORT_FIELDS = {"schema", "request_id", "status", "packet_sha256", "errors"}
ERROR_FIELDS = {"code", "field", "detail"}
RESULT_FIELDS = {"schema", "request_id", "packet_sha256", "execution", "items", "summary"}
EXECUTION_FIELDS = {
    "semantic_attempts",
    "schema_correction_retries",
    "schema_correction_evidence",
    "transport_retries",
    "routing_observation",
    "routing_host_evidence",
}
ITEM_FIELDS = {
    "item_id",
    "parent_item_id",
    "source",
    "normalized_proposition",
    "candidate_links",
    "selected_link",
    "disposition",
    "return_target",
    "move_target",
    "authority_reason",
    "upstream_dependencies",
    "downstream_consumers",
    "evidence_level",
    "confidence",
    "open_unknowns",
    "required_next_action",
    "conflict",
}
SOURCE_FIELDS = {"document_id", "line_start", "line_end", "quote", "quote_sha256"}
CONFLICT_FIELDS = {
    "competing_interpretations",
    "tradeoffs",
    "blocking_unknowns",
    "missing_evidence",
    "safe_recommendation",
    "decision_owner",
}
SUMMARY_FIELDS = {"assigned", "split", "returned", "moved", "conflicts"}
VALIDATION_REPORT_FIELDS = {
    "schema",
    "request_id",
    "packet_sha256",
    "result_sha256",
    "status",
    "errors",
    "mutation_scope",
    "qualification_blockers",
}
BLOCKER_FIELDS = {"code", "detail"}
SCHEMA_CORRECTION_EVIDENCE_FIELDS = {"failed_result_sha256"}
ROUTING_HOST_EVIDENCE_FIELDS = {"host_receipt_sha256"}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VALID_DECLARED_LINKS = set(CHAIN_LINKS)
RETURN_TARGETS = {"GOVERNING_INPUTS", "ARCHITECTURE", "SOFTWARE_DESIGN"}
MOVE_TARGETS = {"IMPLEMENTATION_PLAN", "REALIZATION", "VERIFICATION_EVIDENCE"}
SOURCE_KINDS = {"CODE", "TABLE", "STRUCTURE", "PROSE"}
DISPOSITIONS = {"ASSIGN", "SPLIT", "RETURN_UPSTREAM", "MOVE_DOWNSTREAM", "CONFLICT"}
EVIDENCE_LEVELS = {"OBSERVED", "REPRODUCED", "INFERRED_RISK", "UNKNOWN"}
CONFIDENCE_LEVELS = {"HIGH", "MEDIUM", "LOW"}
MAX_DOCUMENTS_CAP = 64
MAX_DOCUMENT_BYTES_CAP = 2 * 1024 * 1024
MAX_ITEMS_CAP = 2048
MAX_OUTPUT_BYTES_CAP = 8 * 1024 * 1024
MAX_DECOMPOSITION_DEPTH_CAP = 2


class AuthorityPlacementError(ValueError):
    def __init__(self, code: str, path: str = "$", detail: str = "") -> None:
        self.code, self.path, self.detail = code, path, detail
        super().__init__(f"{code} at {path}{': ' + detail if detail else ''}")


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise AuthorityPlacementError("DUPLICATE_KEY")
        result[key] = value
    return result


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    except AuthorityPlacementError:
        raise
    except Exception as exc:
        raise AuthorityPlacementError("JSON", "$", str(exc)) from exc


def _canonical_bytes(value: Any, *, exclude: str | None = None) -> bytes:
    if exclude is not None:
        if not isinstance(value, dict):
            raise AuthorityPlacementError("FIELDS")
        value = {k: v for k, v in value.items() if k != exclude}
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _canonical_write(path: Path, value: Any) -> None:
    path.write_bytes(_canonical_bytes(value))


def _error(code: str, field: str, detail: str = "") -> dict[str, str]:
    return {"code": code, "field": field, "detail": detail}


def _check_obj(value: Any, fields: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise AuthorityPlacementError("FIELDS", path)
    return value


def _check_sha(value: Any, path: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise AuthorityPlacementError("SHA256", path)
    return value


def _check_int(value: Any, path: str, *, minimum: int = 0, maximum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum or (maximum is not None and value > maximum):
        raise AuthorityPlacementError("INTEGER", path)
    return value


def _check_output_path(output_path: Path, output_dir: Path) -> None:
    resolved_dir = output_dir.resolve()
    resolved = output_path.resolve()
    if os.path.commonpath((str(resolved_dir), str(resolved))) != str(resolved_dir):
        raise AuthorityPlacementError("FORBIDDEN_OUTPUT_MUTATION", "$.output")
    if output_path.exists() and not output_path.is_file():
        raise AuthorityPlacementError("FORBIDDEN_OUTPUT_MUTATION", "$.output")
    if output_path.name in {"", ".", ".."}:
        raise AuthorityPlacementError("FORBIDDEN_OUTPUT_MUTATION", "$.output")


def _repo_rel_path(value: Any, path: str) -> str:
    try:
        return _path(value, path)
    except BodyStateError as exc:
        raise AuthorityPlacementError(exc.code, exc.path) from exc


def _unit_id(document_id: str, line_start: int, line_end: int, line_bytes: bytes) -> str:
    parts = [
        b"authority-unit-v1",
        len(document_id.encode("utf-8")).to_bytes(8, "big"),
        document_id.encode("utf-8"),
        line_start.to_bytes(8, "big"),
        line_end.to_bytes(8, "big"),
        len(line_bytes).to_bytes(8, "big"),
        line_bytes,
    ]
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part)
    return digest.hexdigest()


def _line_kind(line: str, in_code: bool) -> str:
    stripped = line.lstrip()
    if in_code:
        return "CODE"
    if stripped.startswith("#") or stripped.startswith("- ") or stripped.startswith("* ") or re.match(r"^\d+\.\s", stripped):
        return "STRUCTURE"
    if "|" in line or re.match(r"^\s*[:\-| ]+\s*$", line):
        return "TABLE"
    return "PROSE"


def _packet_sha(packet: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(packet, exclude="packet_sha256")).hexdigest()


def _result_sha(result: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(result)).hexdigest()


def _validate_repository_root(root_obj: Any) -> tuple[Path, dict[str, str]]:
    root = _check_obj(root_obj, ROOT_FIELDS, "$.repository_root")
    path = Path(_short(root["path"], "$.repository_root.path", 512))
    canonical = str(path.resolve())
    expected = _short(root["canonical_path"], "$.repository_root.canonical_path", 1024)
    if canonical != expected:
        raise AuthorityPlacementError("CANONICAL_PATH_MISMATCH", "$.repository_root.canonical_path")
    return path.resolve(), {"path": str(path), "canonical_path": canonical}


def _validate_limits(limits_obj: Any) -> dict[str, int]:
    limits = _check_obj(limits_obj, LIMIT_FIELDS, "$.limits")
    checked = {
        "max_documents": _check_int(limits["max_documents"], "$.limits.max_documents", minimum=1, maximum=MAX_DOCUMENTS_CAP),
        "max_document_bytes": _check_int(limits["max_document_bytes"], "$.limits.max_document_bytes", minimum=1, maximum=MAX_DOCUMENT_BYTES_CAP),
        "max_items": _check_int(limits["max_items"], "$.limits.max_items", minimum=1, maximum=MAX_ITEMS_CAP),
        "max_output_bytes": _check_int(limits["max_output_bytes"], "$.limits.max_output_bytes", minimum=1, maximum=MAX_OUTPUT_BYTES_CAP),
        "max_semantic_input_bytes": _check_int(limits["max_semantic_input_bytes"], "$.limits.max_semantic_input_bytes", minimum=1),
        "max_decomposition_depth": _check_int(limits["max_decomposition_depth"], "$.limits.max_decomposition_depth", minimum=0, maximum=MAX_DECOMPOSITION_DEPTH_CAP),
    }
    return checked


def _validate_packet_limits(limits_obj: Any) -> dict[str, int]:
    limits = _check_obj(limits_obj, LIMIT_FIELDS, "$.packet.limits")
    return {
        "max_documents": _check_int(limits["max_documents"], "$.packet.limits.max_documents", minimum=1),
        "max_document_bytes": _check_int(limits["max_document_bytes"], "$.packet.limits.max_document_bytes", minimum=1),
        "max_items": _check_int(limits["max_items"], "$.packet.limits.max_items", minimum=1),
        "max_output_bytes": _check_int(limits["max_output_bytes"], "$.packet.limits.max_output_bytes", minimum=1),
        "max_semantic_input_bytes": _check_int(limits["max_semantic_input_bytes"], "$.packet.limits.max_semantic_input_bytes", minimum=1),
        "max_decomposition_depth": _check_int(limits["max_decomposition_depth"], "$.packet.limits.max_decomposition_depth", minimum=0),
    }


def _validate_chain(chain_obj: Any) -> dict[str, Any]:
    chain = _check_obj(chain_obj, CHAIN_REQUEST_FIELDS, "$.authority_chain")
    if chain["profile"] != CHAIN_PROFILE:
        raise AuthorityPlacementError("CHAIN_PROFILE", "$.authority_chain.profile")
    _short(chain["path"], "$.authority_chain.path", 512)
    if _check_sha(chain["sha256"], "$.authority_chain.sha256") != CHAIN_SHA256:
        raise AuthorityPlacementError("CHAIN_HASH_MISMATCH", "$.authority_chain.sha256")
    if _check_int(chain["byte_size"], "$.authority_chain.byte_size", minimum=1) != CHAIN_BYTE_SIZE:
        raise AuthorityPlacementError("CHAIN_SIZE_MISMATCH", "$.authority_chain.byte_size")
    return {
        "profile": CHAIN_PROFILE,
        "path": chain["path"],
        "sha256": CHAIN_SHA256,
        "byte_size": CHAIN_BYTE_SIZE,
        "bytes": CHAIN_BYTES.decode("utf-8"),
    }


def _read_document_lines(path: Path) -> list[bytes]:
    raw = path.read_bytes()
    return raw.splitlines(keepends=True)


def _validate_documents(docs_obj: Any, repository_root: Path, limits: dict[str, int]) -> list[dict[str, Any]]:
    if not isinstance(docs_obj, list) or len(docs_obj) > limits["max_documents"]:
        raise AuthorityPlacementError("DOCUMENTS", "$.documents")
    seen: set[str] = set()
    docs: list[dict[str, Any]] = []
    for i, raw_doc in enumerate(docs_obj):
        doc = _check_obj(raw_doc, DOCUMENT_FIELDS, f"$.documents[{i}]")
        doc_id = _short(doc["document_id"], f"$.documents[{i}].document_id", 128)
        if doc_id in seen:
            raise AuthorityPlacementError("DUPLICATE_DOCUMENT_ID", f"$.documents[{i}].document_id")
        seen.add(doc_id)
        rel = _repo_rel_path(doc["path"], f"$.documents[{i}].path")
        target = (repository_root / rel).resolve()
        if os.path.commonpath((str(repository_root), str(target))) != str(repository_root):
            raise AuthorityPlacementError("PATH_ESCAPE", f"$.documents[{i}].path")
        if not target.is_file():
            raise AuthorityPlacementError("DOCUMENT_MISSING", f"$.documents[{i}].path")
        if doc["declared_link"] not in VALID_DECLARED_LINKS:
            raise AuthorityPlacementError("DECLARED_LINK", f"$.documents[{i}].declared_link")
        digest, size = _hash_file(target)
        if size > limits["max_document_bytes"]:
            raise AuthorityPlacementError("DOCUMENT_TOO_LARGE", f"$.documents[{i}]")
        if _check_sha(doc["sha256"], f"$.documents[{i}].sha256") != digest:
            raise AuthorityPlacementError("DOCUMENT_HASH_MISMATCH", f"$.documents[{i}].sha256")
        if _check_int(doc["byte_size"], f"$.documents[{i}].byte_size", minimum=0) != size:
            raise AuthorityPlacementError("DOCUMENT_SIZE_MISMATCH", f"$.documents[{i}].byte_size")
        docs.append(
            {
                "document_id": doc_id,
                "path": rel,
                "sha256": digest,
                "byte_size": size,
                "declared_link": doc["declared_link"],
                "_target": target,
            }
        )
    return docs


def _validate_selectors(selectors_obj: Any, docs: list[dict[str, Any]]) -> dict[str, list[tuple[int, int]]]:
    if selectors_obj is None:
        return {}
    if not isinstance(selectors_obj, list):
        raise AuthorityPlacementError("SELECTORS", "$.item_selectors")
    known = {doc["document_id"] for doc in docs}
    lines_by_doc = {doc["document_id"]: len(_read_document_lines(doc["_target"])) for doc in docs}
    selectors: dict[str, list[tuple[int, int]]] = {}
    for i, raw_selector in enumerate(selectors_obj):
        selector = _check_obj(raw_selector, SELECTOR_FIELDS, f"$.item_selectors[{i}]")
        doc_id = _short(selector["document_id"], f"$.item_selectors[{i}].document_id", 128)
        if doc_id not in known:
            raise AuthorityPlacementError("UNKNOWN_DOCUMENT_ID", f"$.item_selectors[{i}].document_id")
        start = _check_int(selector["line_start"], f"$.item_selectors[{i}].line_start", minimum=1)
        end = _check_int(selector["line_end"], f"$.item_selectors[{i}].line_end", minimum=start)
        if end > lines_by_doc[doc_id]:
            raise AuthorityPlacementError("SELECTOR_RANGE", f"$.item_selectors[{i}]")
        selectors.setdefault(doc_id, []).append((start, end))
    return selectors


def _source_units(docs: list[dict[str, Any]], selectors: dict[str, list[tuple[int, int]]], max_items: int) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    for doc in docs:
        lines = _read_document_lines(doc["_target"])
        selected = selectors.get(doc["document_id"])
        selected_lines: set[int] | None = None
        if selected is not None:
            selected_lines = set()
            for start, end in selected:
                selected_lines.update(range(start, end + 1))
        in_code = False
        for line_no, raw_line in enumerate(lines, start=1):
            if selected_lines is not None and line_no not in selected_lines:
                if raw_line.decode("utf-8", errors="strict").lstrip().startswith("```"):
                    in_code = not in_code
                continue
            line = raw_line.decode("utf-8", errors="strict")
            fence = line.lstrip().startswith("```")
            kind = _line_kind(line.rstrip("\n\r"), in_code)
            if fence:
                kind = "CODE"
            if line.strip():
                sha = hashlib.sha256(raw_line).hexdigest()
                units.append(
                    {
                        "unit_id": _unit_id(doc["document_id"], line_no, line_no, raw_line),
                        "document_id": doc["document_id"],
                        "line_start": line_no,
                        "line_end": line_no,
                        "kind": kind,
                        "bytes": raw_line.decode("utf-8"),
                        "sha256": sha,
                    }
                )
                if len(units) > max_items:
                    raise AuthorityPlacementError("TOO_MANY_SOURCE_ITEMS", "$.source_units")
            if fence:
                in_code = not in_code
    return units


def prepare_request(request: dict[str, Any], output_path: Path) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    try:
        request = _check_obj(request, REQUEST_FIELDS, "$")
        if request["schema"] != SCHEMA_REQUEST:
            raise AuthorityPlacementError("SCHEMA", "$.schema")
        request_id = _short(request["request_id"], "$.request_id", 128)
        repository_root, root_record = _validate_repository_root(request["repository_root"])
        chain = _validate_chain(request["authority_chain"])
        limits = _validate_limits(request["limits"])
        if request["mode"] != "REPORT_ONLY":
            raise AuthorityPlacementError("MODE", "$.mode")
        output_dir = (repository_root / _repo_rel_path(request["output_dir"], "$.output_dir")).resolve()
        if os.path.commonpath((str(repository_root), str(output_dir))) != str(repository_root):
            raise AuthorityPlacementError("PATH_ESCAPE", "$.output_dir")
        output_dir.mkdir(parents=True, exist_ok=True)
        _check_output_path(output_path, output_dir)
        docs = _validate_documents(request["documents"], repository_root, limits)
        selectors = _validate_selectors(request["item_selectors"], docs)
        units = _source_units(docs, selectors, limits["max_items"])
        packet = {
            "schema": SCHEMA_PACKET,
            "request_id": request_id,
            "repository_root": root_record,
            "authority_chain": chain,
            "documents": [{k: doc[k] for k in DOCUMENT_FIELDS} for doc in docs],
            "source_units": units,
            "output_dir": _repo_rel_path(request["output_dir"], "$.output_dir"),
            "limits": limits,
            "packet_sha256": "",
        }
        raw_without_hash = _canonical_bytes(packet, exclude="packet_sha256")
        if len(raw_without_hash) > limits["max_output_bytes"] or len(raw_without_hash) > limits["max_semantic_input_bytes"]:
            raise AuthorityPlacementError("SEMANTIC_INPUT_BYTE_CEILING_EXCEEDED", "$.limits.max_semantic_input_bytes")
        packet["packet_sha256"] = _packet_sha(packet)
        raw = _canonical_bytes(packet)
        if len(raw) > limits["max_output_bytes"]:
            raise AuthorityPlacementError("OUTPUT_TOO_LARGE", "$.packet")
        _canonical_write(output_path, packet)
        report = {
            "schema": SCHEMA_PREPARE_REPORT,
            "request_id": request_id,
            "status": "PREPARED",
            "packet_sha256": packet["packet_sha256"],
            "errors": [],
        }
        return packet, report
    except AuthorityPlacementError as exc:
        report = {
            "schema": SCHEMA_PREPARE_REPORT,
            "request_id": request.get("request_id", "") if isinstance(request, dict) else "",
            "status": "PREPARE_REJECTED",
            "packet_sha256": None,
            "errors": [_error(exc.code, exc.path, exc.detail)],
        }
        return None, report


def _validate_packet(packet: Any) -> dict[str, Any]:
    packet = _check_obj(packet, PACKET_FIELDS, "$.packet")
    if packet["schema"] != SCHEMA_PACKET:
        raise AuthorityPlacementError("SCHEMA", "$.packet.schema")
    _short(packet["request_id"], "$.packet.request_id", 128)
    _validate_repository_root(packet["repository_root"])
    chain = _check_obj(packet["authority_chain"], CHAIN_PACKET_FIELDS, "$.packet.authority_chain")
    if chain["profile"] != CHAIN_PROFILE or chain["bytes"].encode("utf-8") != CHAIN_BYTES:
        raise AuthorityPlacementError("CHAIN_PROFILE", "$.packet.authority_chain")
    if chain["sha256"] != CHAIN_SHA256 or chain["byte_size"] != CHAIN_BYTE_SIZE:
        raise AuthorityPlacementError("CHAIN_HASH_MISMATCH", "$.packet.authority_chain")
    docs = packet["documents"]
    if not isinstance(docs, list):
        raise AuthorityPlacementError("DOCUMENTS", "$.packet.documents")
    known_docs: set[str] = set()
    for i, doc in enumerate(docs):
        doc = _check_obj(doc, DOCUMENT_FIELDS, f"$.packet.documents[{i}]")
        doc_id = _short(doc["document_id"], f"$.packet.documents[{i}].document_id", 128)
        if doc_id in known_docs:
            raise AuthorityPlacementError("DUPLICATE_DOCUMENT_ID", f"$.packet.documents[{i}].document_id")
        known_docs.add(doc_id)
        _path(doc["path"], f"$.packet.documents[{i}].path")
        _check_sha(doc["sha256"], f"$.packet.documents[{i}].sha256")
        _check_int(doc["byte_size"], f"$.packet.documents[{i}].byte_size", minimum=0)
        if doc["declared_link"] not in VALID_DECLARED_LINKS:
            raise AuthorityPlacementError("DECLARED_LINK", f"$.packet.documents[{i}].declared_link")
    _path(packet["output_dir"], "$.packet.output_dir")
    limits = _validate_packet_limits(packet["limits"])
    units = packet["source_units"]
    if not isinstance(units, list) or len(units) > limits["max_items"]:
        raise AuthorityPlacementError("SOURCE_UNITS", "$.packet.source_units")
    for i, unit in enumerate(units):
        unit = _check_obj(unit, SOURCE_UNIT_FIELDS, f"$.packet.source_units[{i}]")
        _check_sha(unit["unit_id"], f"$.packet.source_units[{i}].unit_id")
        if unit["document_id"] not in known_docs:
            raise AuthorityPlacementError("UNKNOWN_DOCUMENT_ID", f"$.packet.source_units[{i}].document_id")
        _check_int(unit["line_start"], f"$.packet.source_units[{i}].line_start", minimum=1)
        _check_int(unit["line_end"], f"$.packet.source_units[{i}].line_end", minimum=unit["line_start"])
        if unit["kind"] not in SOURCE_KINDS:
            raise AuthorityPlacementError("SOURCE_KIND", f"$.packet.source_units[{i}].kind")
        if not isinstance(unit["bytes"], str):
            raise AuthorityPlacementError("BYTES", f"$.packet.source_units[{i}].bytes")
        if hashlib.sha256(unit["bytes"].encode("utf-8")).hexdigest() != unit["sha256"]:
            raise AuthorityPlacementError("SOURCE_HASH_MISMATCH", f"$.packet.source_units[{i}].sha256")
        if _unit_id(unit["document_id"], unit["line_start"], unit["line_end"], unit["bytes"].encode("utf-8")) != unit["unit_id"]:
            raise AuthorityPlacementError("UNIT_ID_MISMATCH", f"$.packet.source_units[{i}].unit_id")
    return packet


def _list_of_strings(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        raise AuthorityPlacementError("LIST", path)
    result = []
    for i, item in enumerate(value):
        result.append(_short(item, f"{path}[{i}]", 512))
    return result


def _validate_result(result: Any) -> dict[str, Any]:
    result = _check_obj(result, RESULT_FIELDS, "$.result")
    if result["schema"] != SCHEMA_RESULT:
        raise AuthorityPlacementError("SCHEMA", "$.result.schema")
    _short(result["request_id"], "$.result.request_id", 128)
    _check_sha(result["packet_sha256"], "$.result.packet_sha256")
    execution = _check_obj(result["execution"], EXECUTION_FIELDS, "$.result.execution")
    _check_int(execution["semantic_attempts"], "$.result.execution.semantic_attempts", minimum=0)
    schema_retries = _check_int(execution["schema_correction_retries"], "$.result.execution.schema_correction_retries", minimum=0)
    _check_int(execution["transport_retries"], "$.result.execution.transport_retries", minimum=0)
    if execution["routing_observation"] not in {"OBSERVED", "UNOBSERVED"}:
        raise AuthorityPlacementError("ROUTING_OBSERVATION", "$.result.execution.routing_observation")
    correction_evidence = execution["schema_correction_evidence"]
    if schema_retries == 0:
        if correction_evidence is not None:
            raise AuthorityPlacementError("SCHEMA_CORRECTION_EVIDENCE", "$.result.execution.schema_correction_evidence")
    elif schema_retries == 1:
        if correction_evidence is None:
            raise AuthorityPlacementError("SCHEMA_CORRECTION_EVIDENCE", "$.result.execution.schema_correction_evidence")
        evidence = _check_obj(
            correction_evidence,
            SCHEMA_CORRECTION_EVIDENCE_FIELDS,
            "$.result.execution.schema_correction_evidence",
        )
        _check_sha(
            evidence["failed_result_sha256"],
            "$.result.execution.schema_correction_evidence.failed_result_sha256",
        )
    else:
        raise AuthorityPlacementError("SCHEMA_CORRECTION_RETRIES", "$.result.execution.schema_correction_retries")
    routing_evidence = execution["routing_host_evidence"]
    if routing_evidence is not None:
        evidence = _check_obj(routing_evidence, ROUTING_HOST_EVIDENCE_FIELDS, "$.result.execution.routing_host_evidence")
        _check_sha(evidence["host_receipt_sha256"], "$.result.execution.routing_host_evidence.host_receipt_sha256")
    if not isinstance(result["items"], list):
        raise AuthorityPlacementError("LIST", "$.result.items")
    summary = _check_obj(result["summary"], SUMMARY_FIELDS, "$.result.summary")
    for key in SUMMARY_FIELDS:
        _check_int(summary[key], f"$.result.summary.{key}", minimum=0)
    return result


def validate_packet_and_result(packet: dict[str, Any], result: dict[str, Any], output_path: Path) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    blockers: list[dict[str, str]] = []
    mutation_scope = "MUTATION_SCOPE_VERIFIED"
    try:
        packet = _validate_packet(packet)
        result = _validate_result(result)
    except AuthorityPlacementError as exc:
        packet_sha = packet.get("packet_sha256", "") if isinstance(packet, dict) else ""
        result_sha = _result_sha(result) if isinstance(result, dict) else ""
        return {
            "schema": SCHEMA_VALIDATION_REPORT,
            "request_id": result.get("request_id", packet.get("request_id", "")) if isinstance(result, dict) and isinstance(packet, dict) else "",
            "packet_sha256": packet_sha,
            "result_sha256": result_sha,
            "status": "INVALID",
            "errors": [_error(exc.code, exc.path, exc.detail)],
            "mutation_scope": "EXTERNAL_MUTATION_UNKNOWN",
            "qualification_blockers": [],
        }
    if result["request_id"] != packet["request_id"]:
        errors.append(_error("REQUEST_ID_MISMATCH", "$.result.request_id"))
    if result["packet_sha256"] != packet["packet_sha256"]:
        errors.append(_error("PACKET_HASH_MISMATCH", "$.result.packet_sha256"))
    if result["execution"]["semantic_attempts"] != 1:
        errors.append(_error("SEMANTIC_ATTEMPTS", "$.result.execution.semantic_attempts"))
    if result["execution"]["transport_retries"] != 0:
        errors.append(_error("TRANSPORT_RETRIES", "$.result.execution.transport_retries"))
    if packet["limits"]["max_decomposition_depth"] > MAX_DECOMPOSITION_DEPTH_CAP:
        errors.append(_error("DECOMPOSITION_DEPTH", "$.packet.limits.max_decomposition_depth"))
    semantic_size = len(_canonical_bytes(packet))
    if semantic_size > packet["limits"]["max_semantic_input_bytes"]:
        errors.append(_error("SEMANTIC_INPUT_BYTE_CEILING_EXCEEDED", "$.packet.limits.max_semantic_input_bytes"))
    if packet["packet_sha256"] != _packet_sha(packet):
        errors.append(_error("PACKET_HASH_MISMATCH", "$.packet.packet_sha256"))
    routing_evidence = result["execution"]["routing_host_evidence"]
    if result["execution"]["routing_observation"] != "OBSERVED":
        blockers.append({"code": "ROUTING_UNOBSERVED", "detail": "qualification blocked"})
        errors.append(_error("ROUTING_UNOBSERVED", "$.result.execution.routing_observation"))
    elif routing_evidence is None:
        blockers.append({"code": "ROUTING_HOST_EVIDENCE_MISSING", "detail": "qualification blocked"})
        errors.append(_error("ROUTING_HOST_EVIDENCE_MISSING", "$.result.execution.routing_host_evidence"))

    units_by_key: dict[tuple[str, int, int], dict[str, Any]] = {
        (unit["document_id"], unit["line_start"], unit["line_end"]): unit for unit in packet["source_units"]
    }
    items_by_id: dict[str, dict[str, Any]] = {}
    child_ids_by_parent: dict[str, list[str]] = {}
    root_coverage: dict[tuple[str, int, int], str] = {}
    split_parents: set[str] = set()
    summary_counts = {"assigned": 0, "split": 0, "returned": 0, "moved": 0, "conflicts": 0}

    for idx, item in enumerate(result["items"]):
        item_path = f"$.result.items[{idx}]"
        try:
            item = _check_obj(item, ITEM_FIELDS, item_path)
            item_id = _short(item["item_id"], f"{item_path}.item_id", 128)
            if item_id in items_by_id:
                errors.append(_error("DUPLICATE_ITEM_ID", f"{item_path}.item_id"))
                continue
            items_by_id[item_id] = item
            source = _check_obj(item["source"], SOURCE_FIELDS, f"{item_path}.source")
            doc_id = _short(source["document_id"], f"{item_path}.source.document_id", 128)
            start = _check_int(source["line_start"], f"{item_path}.source.line_start", minimum=1)
            end = _check_int(source["line_end"], f"{item_path}.source.line_end", minimum=start)
            quote = source["quote"]
            if not isinstance(quote, str):
                raise AuthorityPlacementError("QUOTE", f"{item_path}.source.quote")
            if hashlib.sha256(quote.encode("utf-8")).hexdigest() != _check_sha(source["quote_sha256"], f"{item_path}.source.quote_sha256"):
                raise AuthorityPlacementError("QUOTE_HASH_MISMATCH", f"{item_path}.source.quote_sha256")
            key = (doc_id, start, end)
            unit = units_by_key.get(key)
            if unit is None:
                errors.append(_error("MISSING_SOURCE_ITEM", f"{item_path}.source"))
            elif unit["bytes"] != quote:
                errors.append(_error("QUOTE_MISMATCH", f"{item_path}.source.quote"))
            disposition = item["disposition"]
            if disposition not in DISPOSITIONS:
                raise AuthorityPlacementError("DISPOSITION", f"{item_path}.disposition")
            _short(item["normalized_proposition"], f"{item_path}.normalized_proposition", 2048)
            candidates = _list_of_strings(item["candidate_links"], f"{item_path}.candidate_links")
            if any(candidate not in VALID_DECLARED_LINKS for candidate in candidates):
                errors.append(_error("CANDIDATE_LINK", f"{item_path}.candidate_links"))
            _short(item["authority_reason"], f"{item_path}.authority_reason", 2048)
            _list_of_strings(item["upstream_dependencies"], f"{item_path}.upstream_dependencies")
            _list_of_strings(item["downstream_consumers"], f"{item_path}.downstream_consumers")
            if item["evidence_level"] not in EVIDENCE_LEVELS:
                errors.append(_error("EVIDENCE_LEVEL", f"{item_path}.evidence_level"))
            if item["confidence"] not in CONFIDENCE_LEVELS:
                errors.append(_error("CONFIDENCE", f"{item_path}.confidence"))
            _list_of_strings(item["open_unknowns"], f"{item_path}.open_unknowns")
            _short(item["required_next_action"], f"{item_path}.required_next_action", 2048)

            parent_id = item["parent_item_id"]
            if parent_id is not None:
                parent_id = _short(parent_id, f"{item_path}.parent_item_id", 128)
                child_ids_by_parent.setdefault(parent_id, []).append(item_id)

            if disposition == "ASSIGN":
                summary_counts["assigned"] += 1
                if item["selected_link"] not in VALID_DECLARED_LINKS or item["return_target"] is not None or item["move_target"] is not None or item["conflict"] is not None:
                    errors.append(_error("ASSIGN_STRUCTURE", item_path))
            elif disposition == "SPLIT":
                summary_counts["split"] += 1
                split_parents.add(item_id)
                if item["selected_link"] is not None or item["return_target"] is not None or item["move_target"] is not None or item["conflict"] is not None:
                    errors.append(_error("SPLIT_STRUCTURE", item_path))
            elif disposition == "RETURN_UPSTREAM":
                summary_counts["returned"] += 1
                if item["return_target"] not in RETURN_TARGETS or item["move_target"] is not None or item["conflict"] is not None:
                    errors.append(_error("INVALID_RETURN_TARGET", f"{item_path}.return_target"))
            elif disposition == "MOVE_DOWNSTREAM":
                summary_counts["moved"] += 1
                if item["move_target"] not in MOVE_TARGETS or item["return_target"] is not None or item["conflict"] is not None:
                    errors.append(_error("INVALID_MOVE_TARGET", f"{item_path}.move_target"))
            elif disposition == "CONFLICT":
                summary_counts["conflicts"] += 1
                conflict = item["conflict"]
                if conflict is None:
                    errors.append(_error("INCOMPLETE_CONFLICT", f"{item_path}.conflict"))
                else:
                    conflict = _check_obj(conflict, CONFLICT_FIELDS, f"{item_path}.conflict")
                    _list_of_strings(conflict["competing_interpretations"], f"{item_path}.conflict.competing_interpretations")
                    _list_of_strings(conflict["tradeoffs"], f"{item_path}.conflict.tradeoffs")
                    _list_of_strings(conflict["blocking_unknowns"], f"{item_path}.conflict.blocking_unknowns")
                    _list_of_strings(conflict["missing_evidence"], f"{item_path}.conflict.missing_evidence")
                    _short(conflict["safe_recommendation"], f"{item_path}.conflict.safe_recommendation", 2048)
                    _short(conflict["decision_owner"], f"{item_path}.conflict.decision_owner", 256)
            if item["selected_link"] is not None:
                if item["selected_link"] not in candidates:
                    errors.append(_error("SELECTED_LINK_NOT_CANDIDATE", f"{item_path}.selected_link"))
                elif candidates:
                    selected_rank = CHAIN_LINKS.index(item["selected_link"])
                    strongest_rank = min(CHAIN_LINKS.index(candidate) for candidate in candidates)
                    if selected_rank != strongest_rank:
                        errors.append(_error("SELECTED_LINK_PRECEDENCE", f"{item_path}.selected_link"))
            if parent_id is None and unit is not None:
                if key in root_coverage:
                    errors.append(_error("DUPLICATE_ASSIGNMENT", item_path))
                root_coverage[key] = item_id
        except AuthorityPlacementError as exc:
            errors.append(_error(exc.code, exc.path, exc.detail))

    for item_id, item in items_by_id.items():
        children = child_ids_by_parent.get(item_id, [])
        if item["disposition"] == "SPLIT" and not children:
            errors.append(_error("MISSING_SPLIT_CHILD", item_id))
        if item["disposition"] != "SPLIT" and children:
            errors.append(_error("INVALID_SPLIT_PARENT", item_id))
        parent_id = item["parent_item_id"]
        if parent_id is not None:
            parent = items_by_id.get(parent_id)
            if parent is None:
                errors.append(_error("UNKNOWN_PARENT_ITEM", item_id))
                continue
            if parent["disposition"] != "SPLIT":
                errors.append(_error("INVALID_PARENT_DISPOSITION", item_id))
            if parent["parent_item_id"] is not None:
                errors.append(_error("DECOMPOSITION_DEPTH", item_id))
            parent_source = parent["source"]
            source = item["source"]
            if (
                source["document_id"] != parent_source["document_id"]
                or source["line_start"] != parent_source["line_start"]
                or source["line_end"] != parent_source["line_end"]
            ):
                errors.append(_error("SPLIT_SOURCE_MISMATCH", item_id))
            elif source["quote"] not in parent_source["quote"]:
                errors.append(_error("SPLIT_QUOTE_OUT_OF_RANGE", item_id))

    covered_keys: set[tuple[str, int, int]] = set(root_coverage)
    for parent_id in split_parents:
        parent = items_by_id[parent_id]
        parent_source = parent["source"]
        parent_key = (
            parent_source["document_id"],
            parent_source["line_start"],
            parent_source["line_end"],
        )
        unit = units_by_key.get(parent_key)
        if unit is None:
            continue
        if root_coverage.get(parent_key) != parent_id:
            errors.append(_error("MISSING_SOURCE_ITEM", parent_id))
            continue
        child_ids = child_ids_by_parent.get(parent_id, [])
        if not child_ids:
            continue
        child_quotes = []
        for child_id in child_ids:
            child = items_by_id.get(child_id)
            if child is None:
                continue
            child_quotes.append(child["source"]["quote"])
        if "".join(child_quotes) != parent_source["quote"]:
            errors.append(_error("SPLIT_COVERAGE_MISMATCH", parent_id))
            continue
        covered_keys.add(parent_key)

    for key in units_by_key:
        if key not in covered_keys:
            errors.append(_error("MISSING_SOURCE_ITEM", "$.result.items"))
    if summary_counts != result["summary"]:
        errors.append(_error("SUMMARY_MISMATCH", "$.result.summary"))

    admitted_output_dir = (Path(packet["repository_root"]["canonical_path"]) / packet["output_dir"]).resolve()
    try:
        _check_output_path(output_path, admitted_output_dir)
    except AuthorityPlacementError:
        errors.append(_error("FORBIDDEN_OUTPUT_MUTATION", "$.output"))
    mutation_scope = "EXTERNAL_MUTATION_UNKNOWN"

    report = {
        "schema": SCHEMA_VALIDATION_REPORT,
        "request_id": packet["request_id"],
        "packet_sha256": packet["packet_sha256"],
        "result_sha256": _result_sha(result),
        "status": "VALID" if not errors else "INVALID",
        "errors": errors,
        "mutation_scope": mutation_scope,
        "qualification_blockers": blockers,
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    p_prepare = sub.add_parser("prepare")
    p_prepare.add_argument("--request", required=True)
    p_prepare.add_argument("--output", required=True)
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--packet", required=True)
    p_validate.add_argument("--result", required=True)
    p_validate.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    if args.action == "prepare":
        request_path = Path(args.request)
        output_path = Path(args.output)
        packet, report = prepare_request(_load_json(request_path), output_path)
        sys.stdout.write(_canonical_bytes(report).decode("utf-8"))
        return 0 if packet is not None else 2

    packet = _load_json(Path(args.packet))
    result = _load_json(Path(args.result))
    report_output = Path(args.output)
    report = validate_packet_and_result(packet, result, report_output)
    _canonical_write(report_output, report)
    sys.stdout.write(_canonical_bytes(report).decode("utf-8"))
    return 0 if report["status"] == "VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
