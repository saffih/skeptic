"""Single-range, metadata-bound, streamed UTF-8 text retrieval."""

from __future__ import annotations

import codecs
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from capabilities.body_state.body_state import (
    BodyStateError,
    MAX_STATE_BYTES,
    SHA256_RE,
    _path,
    validate_state_structure_bytes,
)

REQUEST_LIMIT = 8192
RESULT_LIMIT = 8192
FAILURE_LIMIT = 4096
SHORT_STRING_LIMIT = 256
MAX_REQUESTED_LINES = 64
MAX_EXCERPT_BYTES = 4096
STREAM_CHUNK_SIZE = 65536
REQUEST_FIELDS = {
    "REQUEST_ID", "TASK_ID", "STEP_ID", "PURPOSE", "BODY_STATE_PATH",
    "BODY_STATE_SHA256", "BODY_STATE_BYTE_SIZE", "ARTIFACT_REFERENCE_ID",
    "START_LINE", "END_LINE", "MAX_EXCERPT_BYTES",
}
RESULT_FIELDS = {
    "REQUEST_ID", "STATUS", "TASK_ID", "STEP_ID", "BODY_STATE_SHA256",
    "ARTIFACT_REFERENCE_ID", "SOURCE_PATH", "SOURCE_SHA256", "SOURCE_BYTE_SIZE",
    "REQUESTED_START_LINE", "REQUESTED_END_LINE", "RETURNED_START_LINE",
    "RETURNED_END_LINE", "RETURNED_LINE_COUNT", "EXCERPT", "EXCERPT_BYTE_SIZE",
    "EXCERPT_SHA256",
}
FAILURE_FIELDS = {"REQUEST_ID", "STATUS", "ERROR_CODE", "SUMMARY"}


class RetrievalError(ValueError):
    def __init__(self, code: str, summary: str, request_id: str = "UNKNOWN") -> None:
        self.code, self.summary, self.request_id = code, summary, request_id
        super().__init__(f"{code}: {summary}")


def _canonical(value: dict[str, Any], limit: int) -> bytes:
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(raw) > limit:
        raise RetrievalError("RESULT_TOO_LARGE", "canonical result exceeds its limit")
    return raw


def _short(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > SHORT_STRING_LIMIT:
        raise RetrievalError("INVALID_REQUEST", f"invalid {field}")
    return value


def _positive_integer(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise RetrievalError("INVALID_LINE_RANGE", f"invalid {field}")
    return value


def _request_id_from(raw: bytes) -> str:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "UNKNOWN"
    candidate = value.get("REQUEST_ID") if isinstance(value, dict) else None
    return candidate if isinstance(candidate, str) and candidate and len(candidate.encode()) <= SHORT_STRING_LIMIT else "UNKNOWN"


def _parse_request(raw: bytes) -> dict[str, Any]:
    request_id = _request_id_from(raw)
    if len(raw) > REQUEST_LIMIT:
        raise RetrievalError("REQUEST_TOO_LARGE", "request exceeds 8192 bytes", request_id)
    try:
        text = raw.decode("utf-8")
        value = json.loads(text, object_pairs_hook=lambda pairs: _pairs(pairs))
    except RetrievalError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RetrievalError("INVALID_REQUEST", "request is not canonical UTF-8 JSON", request_id)
    if not isinstance(value, dict) or set(value) != REQUEST_FIELDS:
        raise RetrievalError("INVALID_REQUEST_FIELDS", "request fields are not exact", request_id)
    if not raw.endswith(b"\n") or _canonical(value, REQUEST_LIMIT) != raw:
        raise RetrievalError("NONCANONICAL_REQUEST", "request encoding is not canonical", request_id)
    try:
        request_id = _short(value["REQUEST_ID"], "REQUEST_ID")
        for field in ("TASK_ID", "STEP_ID", "PURPOSE", "ARTIFACT_REFERENCE_ID"):
            _short(value[field], field)
        body_path = _short(value["BODY_STATE_PATH"], "BODY_STATE_PATH")
        _path(body_path, "$.BODY_STATE_PATH")
        if not isinstance(value["BODY_STATE_SHA256"], str) or not SHA256_RE.fullmatch(value["BODY_STATE_SHA256"]):
            raise RetrievalError("INVALID_REQUEST", "invalid BODY_STATE_SHA256")
        if not isinstance(value["BODY_STATE_BYTE_SIZE"], int) or isinstance(value["BODY_STATE_BYTE_SIZE"], bool) or value["BODY_STATE_BYTE_SIZE"] < 0:
            raise RetrievalError("INVALID_REQUEST", "invalid BODY_STATE_BYTE_SIZE")
        start = _positive_integer(value["START_LINE"], "START_LINE")
        end = _positive_integer(value["END_LINE"], "END_LINE")
        if start > end or end - start + 1 > MAX_REQUESTED_LINES:
            raise RetrievalError("INVALID_LINE_RANGE", "line range is reversed or exceeds 64 lines")
        max_excerpt = value["MAX_EXCERPT_BYTES"]
        if not isinstance(max_excerpt, int) or isinstance(max_excerpt, bool) or not 1 <= max_excerpt <= MAX_EXCERPT_BYTES:
            raise RetrievalError("INVALID_EXCERPT_LIMIT", "MAX_EXCERPT_BYTES must be between 1 and 4096")
    except BodyStateError as exc:
        raise RetrievalError("INVALID_REQUEST", f"invalid request path: {exc.code}", request_id) from exc
    except RetrievalError as exc:
        exc.request_id = request_id
        raise
    return value


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RetrievalError("DUPLICATE_REQUEST_KEY", "duplicate request field", _request_id_from(b""))
        result[key] = value
    return result


def _bounded_file(path: Path, limit: int) -> bytes:
    with path.open("rb") as stream:
        return stream.read(limit + 1)


def _failure(error: RetrievalError) -> bytes:
    value = {"REQUEST_ID": error.request_id, "STATUS": "FAILED", "ERROR_CODE": error.code, "SUMMARY": error.summary}
    return _canonical(value, FAILURE_LIMIT)


def _source_excerpt(stream: Any, start: int, end: int, max_excerpt: int) -> tuple[bytes, str, int, str, int, str | None]:
    digest = hashlib.sha256()
    decoder = codecs.getincrementaldecoder("utf-8")("strict")
    size = 0
    line_number = 1
    line_count = 0
    line_has_bytes = False
    retained = bytearray()
    source_error: str | None = None
    utf8_decoder: Any | None = decoder
    while True:
        chunk = stream.read(STREAM_CHUNK_SIZE)
        if not chunk:
            break
        size += len(chunk)
        digest.update(chunk)
        if b"\x00" in chunk:
            source_error = source_error or "NUL_SOURCE"
        if utf8_decoder is not None:
            try:
                utf8_decoder.decode(chunk, final=False)
            except UnicodeDecodeError:
                source_error = source_error or "INVALID_UTF8"
                utf8_decoder = None
        for byte in chunk:
            if start <= line_number <= end and len(retained) <= max_excerpt:
                retained.append(byte)
            if byte == 0x0A:
                line_count = line_number
                line_number += 1
                line_has_bytes = False
            else:
                line_has_bytes = True
    if utf8_decoder is not None:
        try:
            utf8_decoder.decode(b"", final=True)
        except UnicodeDecodeError:
            source_error = source_error or "INVALID_UTF8"
    if line_has_bytes:
        line_count = line_number
    excerpt_bytes = bytes(retained)
    if len(retained) > max_excerpt:
        source_error = source_error or "EXCERPT_TOO_LARGE"
    elif end > line_count:
        source_error = source_error or "RANGE_BEYOND_EOF"
    return excerpt_bytes, hashlib.sha256(excerpt_bytes).hexdigest(), size, digest.hexdigest(), line_count, source_error


def retrieve(request: dict[str, Any], *, repository_root: Path | str = ".") -> dict[str, Any]:
    root = Path(repository_root).resolve()
    request_id = request["REQUEST_ID"]
    try:
        body_rel = _path(request["BODY_STATE_PATH"], "$.BODY_STATE_PATH")
        body_path = (root / body_rel).resolve()
        if os.path.commonpath((str(root), str(body_path))) != str(root):
            raise RetrievalError("UNSAFE_PATH", "Body-state path escapes repository", request_id)
        body_raw = _bounded_file(body_path, MAX_STATE_BYTES)
        if len(body_raw) > MAX_STATE_BYTES:
            raise RetrievalError("BODY_STATE_TOO_LARGE", "Body-state exceeds 32768 bytes", request_id)
        if len(body_raw) != request["BODY_STATE_BYTE_SIZE"] or hashlib.sha256(body_raw).hexdigest() != request["BODY_STATE_SHA256"]:
            raise RetrievalError("BODY_STATE_MISMATCH", "Body-state hash or size does not match", request_id)
        state = validate_state_structure_bytes(body_raw, expected_task_id=request["TASK_ID"])
        if request["STEP_ID"] != state["CURRENT_STEP"]:
            raise RetrievalError("STEP_MISMATCH", "STEP_ID does not match CURRENT_STEP", request_id)
        refs = {ref["reference_id"]: ref for ref in state["ARTIFACT_REFERENCES"]}
        if request["ARTIFACT_REFERENCE_ID"] not in refs:
            raise RetrievalError("UNKNOWN_ARTIFACT_REFERENCE", "artifact reference ID is unknown", request_id)
        ref = refs[request["ARTIFACT_REFERENCE_ID"]]
        source_rel = _path(ref["repository_relative_path"], "$.ARTIFACT_REFERENCES.repository_relative_path")
        source_path = (root / source_rel).resolve()
        if os.path.commonpath((str(root), str(source_path))) != str(root):
            raise RetrievalError("UNSAFE_PATH", "source path escapes repository", request_id)
        try:
            with source_path.open("rb") as stream:
                excerpt_bytes, excerpt_hash, source_size, source_hash, line_count, source_error = _source_excerpt(stream, request["START_LINE"], request["END_LINE"], request["MAX_EXCERPT_BYTES"])
        except FileNotFoundError as exc:
            raise RetrievalError("SOURCE_MISSING", "requested source is missing", request_id) from exc
        except IsADirectoryError as exc:
            raise RetrievalError("SOURCE_MISSING", "requested source is not a file", request_id) from exc
        if source_size != ref["byte_size"] or source_hash != ref["sha256"]:
            raise RetrievalError("SOURCE_MISMATCH", "source hash or size does not match metadata", request_id)
        if source_error == "NUL_SOURCE":
            raise RetrievalError("NUL_SOURCE", "source contains a NUL byte", request_id)
        if source_error == "INVALID_UTF8":
            raise RetrievalError("INVALID_UTF8", "source is not valid UTF-8", request_id)
        if source_error == "RANGE_BEYOND_EOF":
            raise RetrievalError("RANGE_BEYOND_EOF", "requested line range is not fully available", request_id)
        if source_error == "EXCERPT_TOO_LARGE":
            raise RetrievalError("EXCERPT_TOO_LARGE", "requested excerpt exceeds MAX_EXCERPT_BYTES", request_id)
        try:
            excerpt = excerpt_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise RetrievalError("INVALID_UTF8", "requested excerpt is not valid UTF-8", request_id) from exc
        excerpt_size = len(excerpt_bytes)
        result = {
            "REQUEST_ID": request_id, "STATUS": "SUCCESS", "TASK_ID": request["TASK_ID"], "STEP_ID": request["STEP_ID"],
            "BODY_STATE_SHA256": request["BODY_STATE_SHA256"], "ARTIFACT_REFERENCE_ID": request["ARTIFACT_REFERENCE_ID"],
            "SOURCE_PATH": source_rel, "SOURCE_SHA256": source_hash, "SOURCE_BYTE_SIZE": source_size,
            "REQUESTED_START_LINE": request["START_LINE"], "REQUESTED_END_LINE": request["END_LINE"],
            "RETURNED_START_LINE": request["START_LINE"], "RETURNED_END_LINE": request["END_LINE"],
            "RETURNED_LINE_COUNT": request["END_LINE"] - request["START_LINE"] + 1, "EXCERPT": excerpt,
            "EXCERPT_BYTE_SIZE": excerpt_size, "EXCERPT_SHA256": excerpt_hash,
        }
        raw = _canonical(result, RESULT_LIMIT)
        if len(raw) > RESULT_LIMIT:
            raise RetrievalError("RESULT_TOO_LARGE", "canonical result exceeds 8192 bytes", request_id)
        return result
    except BodyStateError as exc:
        code = "TASK_MISMATCH" if exc.code == "TASK_ID_MISMATCH" else "BODY_STATE_INVALID"
        summary = "TASK_ID does not match Body state" if code == "TASK_MISMATCH" else f"Body-state validation failed: {exc.code}"
        raise RetrievalError(code, summary, request_id) from exc


def process_request(raw_request: bytes, *, repository_root: Path | str = ".") -> tuple[int, bytes]:
    try:
        request = _parse_request(raw_request)
        result = retrieve(request, repository_root=repository_root)
        return 0, _canonical(result, RESULT_LIMIT)
    except RetrievalError as exc:
        return 2, _failure(exc)
    except (OSError, TypeError, ValueError) as exc:
        return 2, _failure(RetrievalError("RETRIEVAL_FAILED", "retrieval failed safely"))


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("request_path")
    parser.add_argument("--repository-root", default=".")
    args = parser.parse_args(argv)
    try:
        raw = _bounded_file(Path(args.request_path), REQUEST_LIMIT)
    except OSError:
        code, output = 2, _failure(RetrievalError("REQUEST_MISSING", "request file is missing"))
    else:
        code, output = process_request(raw, repository_root=args.repository_root)
    sys.stdout.buffer.write(output)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
