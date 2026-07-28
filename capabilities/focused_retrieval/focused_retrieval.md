# Verified single-range text retrieval

`capabilities/focused_retrieval/focused_retrieval.py` accepts one canonical UTF-8 JSON request and returns one canonical success or bounded failure result. The request binds an exact metadata-only Body-state file by safe relative path, SHA-256, and byte size. Body-state structure and cross-references are validated without opening referenced artifacts; only the selected reference is then opened.

The selected source is read exactly once in 65,536-byte-or-smaller chunks. The same stream supplies complete source size, SHA-256, UTF-8 and NUL validation, LF-defined line counting, and exact retained bytes. CRLF is preserved. A range is 1-based, inclusive, and at most 64 lines. Excerpts are never silently truncated and are limited to 4,096 bytes; canonical results are limited to 8,192 bytes. Failures exit nonzero and contain only `REQUEST_ID`, `STATUS`, `ERROR_CODE`, and `SUMMARY`.

The artifact `read_condition` is metadata for the Lead's authorization decision; this helper does not interpret natural language conditions.
