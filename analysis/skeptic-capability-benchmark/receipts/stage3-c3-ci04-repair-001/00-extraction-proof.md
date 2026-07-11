# CI04 Extraction Proof

- Task: `STAGE_3_C3_CI04_EXTRACTION_REPAIR_AND_CORRECTED_REPORT_PACKET_001`
- CI04 run: `analysis/skeptic-capability-benchmark/runs/C3-current-main-plus-loop-and-code-extension/CI04/run-1.md`
- CI04 run SHA-256: `677bfcbeb52a6b465deb715af1788049dce654aa71b5d2b56ffc43ec7d85289d`
- Response header: `raw candidate response: bytes=1118 sha256=f027e9b9435d0c8e6fa2092188c6757b33fcd815137dabd590ce19b9d7e795c8`
- Metadata-bearing header count: `1`
- Metadata-bearing fixtures: `CI04`
- Affected scope: CI04-only
- Extraction algorithm: start immediately after the exact header newline; read exactly 1118 bytes; verify SHA-256; verify wrapper transition; decode UTF-8; re-encode and compare bytes
- Extracted bytes: `1118`
- Extracted SHA-256: `f027e9b9435d0c8e6fa2092188c6757b33fcd815137dabd590ce19b9d7e795c8`
- Wrapper transition: `PASS`
- UTF-8 round trip: `PASS`
- Exact old implementation observed: no
- Exact old implementation mechanism: UNKNOWN
- Extraction script: `/tmp/skeptic-c3-ci04-repair-extract.py`
- Extraction script SHA-256: `70e6cf7f545c696e161a72a178b355cf314e2312a8f8ff36b97498e83ddc703a`

## Script Content

```python
#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

ROOT = Path.cwd()
BASE = ROOT / "analysis/skeptic-capability-benchmark"
RUN_ROOT = BASE / "runs/C3-current-main-plus-loop-and-code-extension"
CI04 = RUN_ROOT / "CI04/run-1.md"
OUT = Path("/tmp/skeptic-c3-ci04-repair-001")
OUT.mkdir(parents=True, exist_ok=True)
EXPECTED_IDS = (
    [f"PG{i:02d}" for i in range(1, 7)] + [f"RB{i:02d}" for i in range(1, 7)]
    + [f"CI{i:02d}" for i in range(1, 9)] + [f"DQ{i:02d}" for i in range(1, 5)]
    + [f"WK{i:02d}" for i in range(1, 8)] + [f"LP{i:02d}" for i in range(1, 6)]
)
EXPECTED_RUN_SHA = "677bfcbeb52a6b465deb715af1788049dce654aa71b5d2b56ffc43ec7d85289d"
EXPECTED_RESPONSE_BYTES = 1118
EXPECTED_RESPONSE_SHA = "f027e9b9435d0c8e6fa2092188c6757b33fcd815137dabd590ce19b9d7e795c8"
EXPECTED_HEADER = (
    b"raw candidate response: bytes=1118 "
    b"sha256=f027e9b9435d0c8e6fa2092188c6757b33fcd815137dabd590ce19b9d7e795c8"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


metadata_headers = []
header_meta = {}
for fixture in EXPECTED_IDS:
    path = RUN_ROOT / fixture / "run-1.md"
    data = path.read_bytes()
    matches = list(re.finditer(rb"(?m)^raw candidate response:([^\r\n]*)(?:\r?\n|$)", data))
    if len(matches) != 1:
        raise SystemExit(f"response-header count mismatch: {fixture}")
    remainder = matches[0].group(1)
    metadata = bool(re.fullmatch(rb" bytes=\d+ sha256=[0-9a-f]{64}", remainder))
    if metadata:
        metadata_headers.append(fixture)
    header_meta[fixture] = {
        "run_bytes": len(data),
        "run_sha256": sha(data),
        "metadata_header": metadata,
        "inline_nonmetadata_value": bool(remainder and not metadata and remainder not in (b" |", b" |-")),
        "body_bytes_after_header": len(data) - matches[0].end(),
    }
if metadata_headers != ["CI04"]:
    raise SystemExit("metadata-header scope exceeds CI04")

run = CI04.read_bytes()
if sha(run) != EXPECTED_RUN_SHA:
    raise SystemExit("CI04 run hash mismatch")
header_matches = list(re.finditer(rb"(?m)^" + re.escape(EXPECTED_HEADER) + rb"(?:\r?\n)", run))
if len(header_matches) != 1:
    raise SystemExit("CI04 exact header mismatch")
payload_start = header_matches[0].end()
payload_end = payload_start + EXPECTED_RESPONSE_BYTES
payload = run[payload_start:payload_end]
if len(payload) != EXPECTED_RESPONSE_BYTES or sha(payload) != EXPECTED_RESPONSE_SHA:
    raise SystemExit("CI04 payload byte/hash mismatch")
following = run[payload_end:]
if not re.match(rb"^(?:\r?\n)?execution notes:", following):
    raise SystemExit("CI04 wrapper transition mismatch")
decoded = payload.decode("utf-8")
if decoded.encode("utf-8") != payload:
    raise SystemExit("CI04 UTF-8 round-trip mismatch")
(OUT / "ci04-response.bin").write_bytes(payload)

fixture_bank = (BASE / "fixtures/visible-fixtures.md").read_bytes()
sections = list(re.finditer(rb"(?m)^## ((?:PG|RB|CI|DQ|WK|LP)\d{2}) - .+$", fixture_bank))
ci04_section = None
for index, match in enumerate(sections):
    if match.group(1) == b"CI04":
        end = sections[index + 1].start() if index + 1 < len(sections) else len(fixture_bank)
        ci04_section = fixture_bank[match.start():end].rstrip(b"\n") + b"\n"
        break
if ci04_section is None:
    raise SystemExit("CI04 fixture section missing")

rubric = (BASE / "reports/04-scoring-rubric.md").read_bytes()
confirmations = b"""Before scoring, confirm exactly:\nFRESH_CONTEXT: yes\nNOT_DENYLISTED: yes\nCANDIDATE_IDENTITY_KNOWN: no\nPREVIOUS_CI04_SCORE_KNOWN: no\nPREVIOUS_AGGREGATE_KNOWN: no\nORIGINAL_REPORT_READ: no\nORIGINAL_LEDGER_READ: no\nDEFECT_AUDIT_READ: no\nOTHER_CANDIDATE_RESULT_READ: no\nHOLDOUT_CONTENT_READ: no\nREPOSITORY_ACCESS_USED: no\n\n"""
schema = b"""Return exactly:\nFIXTURE_ID: CI04\nCATEGORY: strong | partial | miss | dangerous\nSCORE: 2 | 1 | 0 | -1\nEXPECTED_TARGET:\nRESPONSE_EVIDENCE:\nRATIONALE:\nDANGEROUS_TYPE: none | details\nDISQUALIFICATION_CAPABILITY: none | EVID | other\nCONFIDENCE: high | medium | low\nRUBRIC_AMBIGUITY: none | details\n\nUse concise evidence. Do not reproduce the full response.\n"""
packet = b"".join([
    b"# Anonymous CI04 Fresh Rescore Packet\n\n", confirmations,
    b"## Locked Rubric\n\n", rubric,
    b"\n## Visible Fixture CI04\n\n", ci04_section,
    b"\n## SELECTED_RESPONSE_CI04\n\n", payload,
    b"\n## Required Output\n\n", schema,
])
(OUT / "scoring-packet.md").write_bytes(packet)

meta = {
    "script_sha256": sha(Path(__file__).read_bytes()),
    "ci04_run_bytes": len(run),
    "ci04_run_sha256": sha(run),
    "header": EXPECTED_HEADER.decode(),
    "metadata_header_count": len(metadata_headers),
    "metadata_header_fixtures": metadata_headers,
    "header_scan": header_meta,
    "extracted_bytes": len(payload),
    "extracted_sha256": sha(payload),
    "round_trip": "PASS",
    "wrapper_transition": "PASS",
    "rubric_sha256": sha(rubric),
    "fixture_section_sha256": sha(ci04_section),
    "packet_bytes": len(packet),
    "packet_sha256": sha(packet),
}
(OUT / "extraction-metadata.json").write_text(json.dumps(meta, sort_keys=True, indent=2) + "\n")
print(json.dumps({k: meta[k] for k in ["script_sha256", "ci04_run_sha256", "metadata_header_count", "metadata_header_fixtures", "extracted_bytes", "extracted_sha256", "round_trip", "wrapper_transition", "packet_bytes", "packet_sha256"]}, sort_keys=True))
```
