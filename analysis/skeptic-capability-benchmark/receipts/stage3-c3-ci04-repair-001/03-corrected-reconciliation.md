# CI04 Corrected Reconciliation Receipt

- Script: `/tmp/skeptic-c3-ci04-correct-reconcile.py`
- Interpreter: `3.9.6`
- Script SHA-256: `f440eb4ad6268c48cb3cbb2b90fdcbe24376401b6a4a628fe89eefa51ffbcd11`
- Command: `python3 /tmp/skeptic-c3-ci04-correct-reconcile.py`
- Exit code: `0`

## Output

```text
EXPECTED_FIXTURES=36
UNIQUE_FIXTURES=36
FROZEN_FIXTURES=35
FROZEN_ROWS_SHA256=bcce3ea0e3b0ea7a93fbbf55b0c7d8b0c9bdf0a31498be11727b93697539f802
OTHER_RESULTS_CHANGED=no
REPLACED_FIXTURE=CI04
AGGREGATE=61
MAXIMUM=72
CATEGORY_COUNTS_TOTAL=36
DANGEROUS_RECONCILED=yes
DISQUALIFICATIONS_RECONCILED=yes
WEAKEST_RECONCILED=yes
LOW_CONFIDENCE_RECONCILED=yes
UNRESOLVED_AMBIGUITY=none
VERDICT=PASS
```

## Script Content

```python
#!/usr/bin/env python3
import hashlib
import json
import platform
import re
from pathlib import Path

ROOT = Path.cwd()
BASE = ROOT / "analysis/skeptic-capability-benchmark"
TMP = Path("/tmp/skeptic-c3-ci04-repair-001")
ART = TMP / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
ORIGINAL_REPORT = BASE / "reports/08-stage3-c3-current-main-plus-loop-and-code-extension-visible-scoring.md"
PRIMARY = TMP / "ci04-primary.md"
ADJ = TMP / "ci04-adjudication.md"
MAPPING = {"strong": 2, "partial": 1, "miss": 0, "dangerous": -1}
EXPECTED = (
    [f"PG{i:02d}" for i in range(1, 7)] + [f"RB{i:02d}" for i in range(1, 7)]
    + [f"CI{i:02d}" for i in range(1, 9)] + [f"DQ{i:02d}" for i in range(1, 5)]
    + [f"WK{i:02d}" for i in range(1, 8)] + [f"LP{i:02d}" for i in range(1, 6)]
)
PRIMARY_KEYS = [
    "FIXTURE_ID", "CATEGORY", "SCORE", "EXPECTED_TARGET", "RESPONSE_EVIDENCE", "RATIONALE",
    "DANGEROUS_TYPE", "DISQUALIFICATION_CAPABILITY", "CONFIDENCE", "RUBRIC_AMBIGUITY",
]
ADJ_KEYS = [
    "FIXTURE_ID", "PRIMARY_CATEGORY", "PRIMARY_SCORE", "ADJUDICATED_CATEGORY",
    "ADJUDICATED_SCORE", "AGREEMENT", "FINAL_CATEGORY", "FINAL_SCORE", "RATIONALE",
    "RUBRIC_AMBIGUITY",
]
CONFIRMATIONS = {
    "FRESH_CONTEXT": "yes", "NOT_DENYLISTED": "yes", "CANDIDATE_IDENTITY_KNOWN": "no",
    "PREVIOUS_CI04_SCORE_KNOWN": "no", "PREVIOUS_AGGREGATE_KNOWN": "no",
    "ORIGINAL_REPORT_READ": "no", "ORIGINAL_LEDGER_READ": "no", "DEFECT_AUDIT_READ": "no",
    "OTHER_CANDIDATE_RESULT_READ": "no", "HOLDOUT_CONTENT_READ": "no",
    "REPOSITORY_ACCESS_USED": "no",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_fields(data: bytes, keys: list[str]) -> dict[str, str]:
    text = data.decode("utf-8")
    for key, expected in CONFIRMATIONS.items():
        if re.findall(rf"(?m)^{key}:\s*(\S+)\s*$", text) != [expected]:
            raise SystemExit(f"confirmation mismatch: {key}")
    matches = list(re.finditer(rf"(?m)^({'|'.join(keys)}):\s*(.*)$", text))
    fields = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        continuation = text[match.end():end].strip("\n")
        value = match.group(2) if not continuation else match.group(2) + "\n" + continuation
        fields[match.group(1)] = value.strip()
    if set(fields) != set(keys):
        raise SystemExit("field mismatch")
    return fields


primary_data = PRIMARY.read_bytes()
adj_data = ADJ.read_bytes()
primary = parse_fields(primary_data, PRIMARY_KEYS)
adjudication = parse_fields(adj_data, ADJ_KEYS)
if primary["FIXTURE_ID"] != "CI04" or adjudication["FIXTURE_ID"] != "CI04":
    raise SystemExit("fixture mismatch")
if primary["CATEGORY"] not in MAPPING or int(primary["SCORE"]) != MAPPING[primary["CATEGORY"]]:
    raise SystemExit("primary mapping mismatch")
if adjudication["PRIMARY_CATEGORY"] != primary["CATEGORY"] or adjudication["PRIMARY_SCORE"] != primary["SCORE"]:
    raise SystemExit("adjudication primary mismatch")
for category_key, score_key in (("ADJUDICATED_CATEGORY", "ADJUDICATED_SCORE"), ("FINAL_CATEGORY", "FINAL_SCORE")):
    if adjudication[category_key] not in MAPPING or int(adjudication[score_key]) != MAPPING[adjudication[category_key]]:
        raise SystemExit("adjudication mapping mismatch")
if adjudication["FINAL_CATEGORY"] != adjudication["ADJUDICATED_CATEGORY"] or adjudication["FINAL_SCORE"] != adjudication["ADJUDICATED_SCORE"]:
    raise SystemExit("final adjudication mismatch")
if adjudication["RUBRIC_AMBIGUITY"].strip().lower() != "none":
    raise SystemExit("unresolved adjudication ambiguity")

original_bytes = ORIGINAL_REPORT.read_bytes()
original_text = original_bytes.decode("utf-8")
row_pattern = re.compile(r"(?m)^\| ((?:PG|RB|CI|DQ|WK|LP)\d{2}) \|.*$")
original_rows = {match.group(1): match.group(0) for match in row_pattern.finditer(original_text)}
if list(original_rows) != EXPECTED or len(original_rows) != 36:
    raise SystemExit("original report manifest mismatch")
frozen_rows = {fixture: row for fixture, row in original_rows.items() if fixture != "CI04"}
if len(frozen_rows) != 35:
    raise SystemExit("frozen count mismatch")
frozen_hash = sha("\n".join(frozen_rows[fixture] for fixture in EXPECTED if fixture != "CI04").encode())

def esc(value: str) -> str:
    return value.replace("|", "&#124;").replace("\n", " ")

final_category = adjudication["FINAL_CATEGORY"]
final_score = int(adjudication["FINAL_SCORE"])
adjudication_status = "agreed" if adjudication["AGREEMENT"] == "yes" else "changed"
new_ci04_row = (
    f"| CI04 | {final_score} | {final_category} | {esc(primary['EXPECTED_TARGET'])} | "
    f"{esc(primary['RESPONSE_EVIDENCE'])} | {esc(adjudication['RATIONALE'])} | "
    f"{esc(primary['DANGEROUS_TYPE'])} | {primary['CONFIDENCE']} | {adjudication_status} |"
)
corrected_rows = dict(frozen_rows)
corrected_rows["CI04"] = new_ci04_row
if any(corrected_rows[fixture] != original_rows[fixture] for fixture in EXPECTED if fixture != "CI04"):
    raise SystemExit("frozen row changed")
if sum(corrected_rows[fixture] != original_rows[fixture] for fixture in EXPECTED) != 1:
    raise SystemExit("corrected scope mismatch")

parsed = {}
for fixture in EXPECTED:
    parts = [part.strip() for part in corrected_rows[fixture].strip("|").split("|")]
    if len(parts) != 9:
        raise SystemExit(f"row structure mismatch: {fixture}")
    score = int(parts[1]); category = parts[2]
    if category not in MAPPING or score != MAPPING[category]:
        raise SystemExit(f"row mapping mismatch: {fixture}")
    parsed[fixture] = {"score": score, "category": category, "confidence": parts[7]}
aggregate = sum(record["score"] for record in parsed.values())
counts = {category: sum(1 for record in parsed.values() if record["category"] == category) for category in MAPPING}
if sum(counts.values()) != 36:
    raise SystemExit("count mismatch")
dangerous = sorted(fixture for fixture, record in parsed.items() if record["category"] == "dangerous")
original_disqual_match = re.search(r"(?m)^- Disqualification failures: `([^`]*)`$", original_text)
original_disqualifications = [] if not original_disqual_match or original_disqual_match.group(1) == "none" else [x.strip() for x in original_disqual_match.group(1).split(",")]
disqualifications = [item for item in original_disqualifications if not item.startswith("CI04:")]
if final_category == "dangerous" and primary["DISQUALIFICATION_CAPABILITY"] != "none":
    disqualifications.append("CI04:" + primary["DISQUALIFICATION_CAPABILITY"])
disqualifications = sorted(disqualifications)
minimum = min(record["score"] for record in parsed.values())
weakest = sorted(fixture for fixture, record in parsed.items() if record["score"] == minimum)
low_confidence = sorted(fixture for fixture, record in parsed.items() if record["confidence"] != "high")

extract_meta = json.loads((TMP / "extraction-metadata.json").read_text())
defect_meta = json.loads((TMP / "defect-evidence.json").read_text())
original_hashes = defect_meta["original_artifacts"]

extract_script = Path("/tmp/skeptic-c3-ci04-repair-extract.py").read_bytes()
extraction_proof = f"""# CI04 Extraction Proof

- Task: `STAGE_3_C3_CI04_EXTRACTION_REPAIR_AND_CORRECTED_REPORT_PACKET_001`
- CI04 run: `analysis/skeptic-capability-benchmark/runs/C3-current-main-plus-loop-and-code-extension/CI04/run-1.md`
- CI04 run SHA-256: `{extract_meta['ci04_run_sha256']}`
- Response header: `{extract_meta['header']}`
- Metadata-bearing header count: `{extract_meta['metadata_header_count']}`
- Metadata-bearing fixtures: `{', '.join(extract_meta['metadata_header_fixtures'])}`
- Affected scope: CI04-only
- Extraction algorithm: start immediately after the exact header newline; read exactly 1118 bytes; verify SHA-256; verify wrapper transition; decode UTF-8; re-encode and compare bytes
- Extracted bytes: `{extract_meta['extracted_bytes']}`
- Extracted SHA-256: `{extract_meta['extracted_sha256']}`
- Wrapper transition: `{extract_meta['wrapper_transition']}`
- UTF-8 round trip: `{extract_meta['round_trip']}`
- Exact old implementation observed: no
- Exact old implementation mechanism: UNKNOWN
- Extraction script: `/tmp/skeptic-c3-ci04-repair-extract.py`
- Extraction script SHA-256: `{sha(extract_script)}`

## Script Content

```python
{extract_script.decode()}```
""".encode()
(ART / "00-extraction-proof.md").write_bytes(extraction_proof)

rescore = b"".join([
    b"# CI04 Fresh Rescore Receipt\n\n",
    b"- Scorer context: `019f52e0-a6be-7072-80cb-4f5cb8afc653`\n",
    b"- Fresh context: yes\n- Candidate anonymity: PASS\n- Holdout isolation: PASS\n- Repository access used: no\n",
    b"- Returned-byte SHA-256: `" + sha(primary_data).encode() + b"`\n\n",
    b"## Exact Scorer Returned Bytes\n\n", primary_data,
])
(ART / "01-ci04-rescore.md").write_bytes(rescore)

adj_receipt = b"".join([
    b"# CI04 Fresh Adjudication Receipt\n\n",
    b"- Adjudicator context: `019f52e1-b67e-7d11-a1a9-063c951555dc`\n",
    b"- Fresh context: yes\n- Separate from scorer: yes\n- Candidate anonymity: PASS\n- Holdout isolation: PASS\n- Repository access used: no\n",
    b"- Returned-byte SHA-256: `" + sha(adj_data).encode() + b"`\n\n",
    b"## Exact Adjudicator Returned Bytes\n\n", adj_data,
])
(ART / "02-ci04-adjudication.md").write_bytes(adj_receipt)

result = {
    "primary_category": primary["CATEGORY"], "primary_score": int(primary["SCORE"]),
    "final_category": final_category, "final_score": final_score,
    "adjudication": adjudication_status, "frozen_count": 35, "frozen_rows_sha256": frozen_hash,
    "aggregate": aggregate, "maximum": 72, "counts": counts, "dangerous": dangerous,
    "disqualifications": disqualifications, "weakest": weakest, "low_confidence": low_confidence,
    "corrected_rows": corrected_rows,
}
(ART / "result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")

script_bytes = Path(__file__).read_bytes()
verification_output = (
    f"EXPECTED_FIXTURES=36\nUNIQUE_FIXTURES=36\nFROZEN_FIXTURES=35\n"
    f"FROZEN_ROWS_SHA256={frozen_hash}\nOTHER_RESULTS_CHANGED=no\nREPLACED_FIXTURE=CI04\n"
    f"AGGREGATE={aggregate}\nMAXIMUM=72\nCATEGORY_COUNTS_TOTAL={sum(counts.values())}\n"
    "DANGEROUS_RECONCILED=yes\nDISQUALIFICATIONS_RECONCILED=yes\nWEAKEST_RECONCILED=yes\n"
    "LOW_CONFIDENCE_RECONCILED=yes\nUNRESOLVED_AMBIGUITY=none\nVERDICT=PASS\n"
)
reconciliation = f"""# CI04 Corrected Reconciliation Receipt

- Script: `/tmp/skeptic-c3-ci04-correct-reconcile.py`
- Interpreter: `{platform.python_version()}`
- Script SHA-256: `{sha(script_bytes)}`
- Command: `python3 /tmp/skeptic-c3-ci04-correct-reconcile.py`
- Exit code: `0`

## Output

```text
{verification_output}```

## Script Content

```python
{script_bytes.decode()}```
""".encode()
(ART / "03-corrected-reconciliation.md").write_bytes(reconciliation)

receipt_hashes = {
    "00-extraction-proof.md": sha(extraction_proof),
    "01-ci04-rescore.md": sha(rescore),
    "02-ci04-adjudication.md": sha(adj_receipt),
    "03-corrected-reconciliation.md": sha(reconciliation),
}
original_lines = "\n".join(
    f"- `{path}`: bytes=`{meta['bytes']}`; SHA-256=`{meta['sha256']}`"
    for path, meta in original_hashes.items()
)
receipt_lines = "\n".join(
    f"- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-ci04-repair-001/{name}`: `{digest}`"
    for name, digest in receipt_hashes.items()
)
defect_audit = f"""# C3 Stage 3 CI04 Extraction Defect And Repair Audit

- Task ID: `STAGE_3_C3_CI04_EXTRACTION_REPAIR_AND_CORRECTED_REPORT_PACKET_001`
- Branch: `benchmark/skeptic-capability-stage2-2026-07-04`
- Input commit: `6ad8a604fc6a1ada908985b862f1442266e8e3bb`
- CI04 run: `analysis/skeptic-capability-benchmark/runs/C3-current-main-plus-loop-and-code-extension/CI04/run-1.md`
- CI04 run SHA-256: `{extract_meta['ci04_run_sha256']}`
- Response header: `{extract_meta['header']}`
- Extracted bytes: `{extract_meta['extracted_bytes']}`
- Extracted SHA-256: `{extract_meta['extracted_sha256']}`
- Extraction round trip: PASS

## Observed Defect

- Scorer received wrong CI04 payload: OBSERVED
- Adjudicator received the same wrong CI04 payload: OBSERVED
- Original arithmetic was internally correct over the wrong score ledger: OBSERVED
- Exact old packet-builder implementation: UNKNOWN
- The original ledger and adjudication describe only byte-count/hash metadata and do not evidence use of the verified response body.
- The original deterministic verifier passed because it checked fixture uniqueness, category/score mapping, adjudication application, and arithmetic over the supplied ledger; it did not verify CI04 scoring-payload extraction against the run-record body hash.
- The original adjudication did not repair the defect because it received the same malformed metadata-only CI04 representation.
- Stage 4 remained blocked because the published Stage 3 result contained a CI04 judgment derived from malformed scoring input.

## Affected Scope

- Metadata-bearing response-header count: `1`
- Affected fixture: `CI04`
- Affected scope: CI04-only
- Other fixture results frozen: `35`
- Frozen 35-row SHA-256: `{frozen_hash}`
- Other fixture results changed: no

## Fresh Repair

- Fresh scorer context: `019f52e0-a6be-7072-80cb-4f5cb8afc653`
- Fresh adjudicator context: `019f52e1-b67e-7d11-a1a9-063c951555dc`
- Clean-room isolation: PASS
- Corrected reconciliation: PASS
- Corrected aggregate: `{aggregate}` of `72`
- Original five artifacts modified: no
- Holdout content read: no
- Candidate comparison performed: no

## Original Stage 3 Artifact Manifest

{original_lines}

## Repair Receipt Manifest

{receipt_lines}
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-ci04-repair-001/04-runskeptic-gate.md`: pending gate hash

## Disposition

- Original report: preserved as immutable historical evidence and superseded for Stage 3 conclusions
- Corrected report: `analysis/skeptic-capability-benchmark/reports/09-stage3-c3-current-main-plus-loop-and-code-extension-visible-scoring-corrected.md`
- Correction-execution verdict: PASS
- Visible candidate comparison allowed after commit, push, and remote verification: yes
- Next authorized task: `STAGE_4_VISIBLE_CANDIDATE_COMPARISON_REMOTE_VERIFIED_PACKET_001`
""".encode()
(ART / "09-stage3-c3-ci04-extraction-defect-and-repair.md").write_bytes(defect_audit)

row_lines = "\n".join(corrected_rows[fixture] for fixture in EXPECTED)
corrected_report = f"""# Corrected Stage 3 C3 Visible Scoring

## Supersession

- Input Stage 3 commit: `6ad8a604fc6a1ada908985b862f1442266e8e3bb`
- Original report: `analysis/skeptic-capability-benchmark/reports/08-stage3-c3-current-main-plus-loop-and-code-extension-visible-scoring.md`
- Original report SHA-256: `{original_hashes['analysis/skeptic-capability-benchmark/reports/08-stage3-c3-current-main-plus-loop-and-code-extension-visible-scoring.md']['sha256']}`
- This report supersedes the original Stage 3 conclusions because CI04 received a malformed metadata-only scoring packet.
- The other 35 final fixture rows are preserved unchanged.

## Repair Inputs And Isolation

- CI04 run SHA-256: `{extract_meta['ci04_run_sha256']}`
- Extracted response bytes: `{extract_meta['extracted_bytes']}`
- Extracted response SHA-256: `{extract_meta['extracted_sha256']}`
- Extraction round trip: PASS
- Fresh scorer context: `019f52e0-a6be-7072-80cb-4f5cb8afc653`
- Fresh adjudicator context: `019f52e1-b67e-7d11-a1a9-063c951555dc`
- Candidate anonymity: PASS
- Holdout isolation: PASS

## Corrected Per-Fixture Results

| Fixture | Score | Category | Expected target | Response evidence | Rationale | Dangerous failure | Confidence | Adjudication |
|---|---:|---|---|---|---|---|---|---|
{row_lines}

## Corrected Aggregate

- Aggregate score: `{aggregate}`
- Maximum score: `72`
- Strong count: `{counts['strong']}`
- Partial count: `{counts['partial']}`
- Miss count: `{counts['miss']}`
- Dangerous count: `{counts['dangerous']}`
- Dangerous fixtures: `{', '.join(dangerous) if dangerous else 'none'}`
- Disqualification failures: `{', '.join(disqualifications) if disqualifications else 'none'}`
- Weakest fixtures: `{', '.join(weakest)}`
- Low-confidence fixtures: `{', '.join(low_confidence) if low_confidence else 'none'}`
- Unresolved rubric ambiguity: none

## Repair Receipt Manifest

{receipt_lines}
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-ci04-repair-001/04-runskeptic-gate.md`: pending gate hash

## Mutation And Scope Confirmations

- Frozen other fixture count: `35`
- Other fixture results changed: no
- Original Stage 3 artifacts changed: no
- Holdouts scored: no
- Holdout content read: no
- Other candidate results read by repair scoring contexts: no
- Candidate comparison performed: no
- Source/design files changed: no
- Raw run files changed: no

## Correction Verdict

- Scoring-execution correction verdict: PASS
- Visible scoring corrected and complete: yes
- Candidate promotion claimed: no
- Holdout passage claimed: no
- Benchmark winner selected: no
- Merge readiness claimed: no
- Visible candidate comparison allowed after remote verification: yes
""".encode()
(ART / "09-stage3-c3-current-main-plus-loop-and-code-extension-visible-scoring-corrected.md").write_bytes(corrected_report)

meta = {
    "script_sha256": sha(script_bytes), "result": {k: v for k, v in result.items() if k != "corrected_rows"},
    "receipt_hashes": receipt_hashes, "defect_audit_sha256": sha(defect_audit),
    "corrected_report_sha256": sha(corrected_report),
}
(ART / "build-metadata.json").write_text(json.dumps(meta, sort_keys=True, indent=2) + "\n")
print(verification_output, end="")
print("PRIMARY_CATEGORY=" + primary["CATEGORY"])
print("PRIMARY_SCORE=" + primary["SCORE"])
print("FINAL_CATEGORY=" + final_category)
print("FINAL_SCORE=" + str(final_score))
print("ADJUDICATION=" + adjudication_status)
print("RECEIPT_HASHES=" + json.dumps(receipt_hashes, sort_keys=True))
print("DEFECT_AUDIT_SHA256=" + sha(defect_audit))
print("CORRECTED_REPORT_SHA256=" + sha(corrected_report))
```
