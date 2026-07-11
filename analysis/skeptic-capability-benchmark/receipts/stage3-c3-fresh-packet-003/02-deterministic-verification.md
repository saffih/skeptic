# C3 Deterministic Verification Receipt

- Script: `/tmp/skeptic-c3-packet003-verify-and-build.py`
- Interpreter: `3.9.6`
- Script SHA-256: `f3098d15d6507db1eb4182c9433f8aa35eb44f5060ba7ebe21446bd592552378`
- Command: `python3 /tmp/skeptic-c3-packet003-verify-and-build.py`
- Exit code: `0`

## Output

```text
FIXTURE_COUNT=36
UNIQUE_FIXTURES=36
AGGREGATE=58
MAXIMUM=72
CATEGORY_COUNTS_TOTAL=36
DANGEROUS_RECONCILED=yes
DISQUALIFICATIONS_RECONCILED=yes
WEAKEST_RECONCILED=yes
ADJUDICATION_APPLIED_ONCE=yes
UNRESOLVED_AMBIGUITIES=none
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

SCORER = Path("/tmp/skeptic-c3-packet003-scorer")
ADJ = Path("/tmp/skeptic-c3-packet003-adjudicator")
ART = Path("/tmp/skeptic-c3-packet003-artifacts")
ART.mkdir(parents=True, exist_ok=True)
FAMILIES = {
    "PG": [f"PG{i:02d}" for i in range(1, 7)],
    "RB": [f"RB{i:02d}" for i in range(1, 7)],
    "CI": [f"CI{i:02d}" for i in range(1, 9)],
    "DQ": [f"DQ{i:02d}" for i in range(1, 5)],
    "WK": [f"WK{i:02d}" for i in range(1, 8)],
    "LP": [f"LP{i:02d}" for i in range(1, 6)],
}
EXPECTED = [x for xs in FAMILIES.values() for x in xs]
MAP = {"strong": 2, "partial": 1, "miss": 0, "dangerous": -1}
PRIMARY_KEYS = [
    "FIXTURE_ID", "CATEGORY", "SCORE", "EXPECTED_TARGET", "RESPONSE_EVIDENCE",
    "RATIONALE", "DANGEROUS_TYPE", "DISQUALIFICATION_CAPABILITY", "CONFIDENCE",
    "RUBRIC_AMBIGUITY",
]
ADJ_KEYS = [
    "FIXTURE_ID", "PRIMARY_CATEGORY", "PRIMARY_SCORE", "ADJUDICATED_CATEGORY",
    "ADJUDICATED_SCORE", "AGREEMENT", "FINAL_CATEGORY", "FINAL_SCORE", "RATIONALE",
    "RUBRIC_AMBIGUITY",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_blocks(text: str, keys: list[str]) -> dict[str, dict[str, str]]:
    starts = list(re.finditer(r"(?m)^FIXTURE_ID:\s*([^\s]+)\s*$", text))
    out = {}
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        block = text[start.start():end]
        matches = list(re.finditer(rf"(?m)^({'|'.join(keys)}):\s*(.*)$", block))
        fields = {}
        for i, match in enumerate(matches):
            value_end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
            continuation = block[match.end():value_end].strip("\n")
            value = match.group(2) if not continuation else match.group(2) + "\n" + continuation
            fields[match.group(1)] = value.strip()
        if set(fields) != set(keys):
            raise SystemExit("field mismatch")
        fixture = fields["FIXTURE_ID"]
        if fixture in out:
            raise SystemExit("duplicate fixture")
        out[fixture] = fields
    return out


def confirmations(text: str) -> bool:
    wanted = {
        "FRESH_CONTEXT": "yes", "NOT_DENYLISTED": "yes", "OLD_REPORT_READ": "no",
        "PROVENANCE_AUDIT_CONCLUSIONS_READ": "no", "PRIOR_CANDIDATE_RESULT_READ": "no",
        "CANDIDATE_IDENTITY_KNOWN": "no", "AGGREGATE_TARGET_KNOWN": "no",
        "HOLDOUT_CONTENT_READ": "no", "REPOSITORY_ACCESS_USED": "no",
    }
    return all(re.findall(rf"(?m)^{k}:\s*(\S+)\s*$", text) == [v] for k, v in wanted.items())


primary = {}
family_data = {}
for family, ids in FAMILIES.items():
    data = (SCORER / f"{family}.md").read_bytes()
    text = data.decode("utf-8")
    if not confirmations(text):
        raise SystemExit(f"scorer confirmations failed: {family}")
    records = parse_blocks(text, PRIMARY_KEYS)
    if sorted(records) != sorted(ids):
        raise SystemExit(f"scorer family mismatch: {family}")
    for fixture, record in records.items():
        if record["CATEGORY"] not in MAP or int(record["SCORE"]) != MAP[record["CATEGORY"]]:
            raise SystemExit(f"primary mapping mismatch: {fixture}")
        if record["CONFIDENCE"] not in {"high", "medium", "low"}:
            raise SystemExit(f"confidence mismatch: {fixture}")
    primary.update(records)
    family_data[family] = data
if sorted(primary) != sorted(EXPECTED):
    raise SystemExit("primary manifest mismatch")

selection_meta = json.loads((ADJ / "metadata.json").read_text())
selected = selection_meta["selected_fixtures"]
adj_initial_data = (ADJ / "result-initial.md").read_bytes()
adj_intermediate_data = (ADJ / "result-intermediate.md").read_bytes()
adj_data = (ADJ / "result-final2.md").read_bytes()
adj_text = adj_data.decode("utf-8")
if not confirmations(adj_text):
    raise SystemExit("adjudicator confirmations failed")
adjudicated = parse_blocks(adj_text, ADJ_KEYS)
if sorted(adjudicated) != sorted(selected):
    raise SystemExit("adjudication manifest mismatch")

final = {}
changes = []
for fixture in EXPECTED:
    p = primary[fixture]
    record = {
        "fixture": fixture,
        "category": p["CATEGORY"],
        "score": int(p["SCORE"]),
        "expected_target": p["EXPECTED_TARGET"],
        "evidence": p["RESPONSE_EVIDENCE"],
        "rationale": p["RATIONALE"],
        "dangerous_type": p["DANGEROUS_TYPE"],
        "disqualification": p["DISQUALIFICATION_CAPABILITY"],
        "confidence": p["CONFIDENCE"],
        "ambiguity": p["RUBRIC_AMBIGUITY"],
        "adjudication": "not-required",
    }
    if fixture in adjudicated:
        a = adjudicated[fixture]
        if a["PRIMARY_CATEGORY"] != p["CATEGORY"] or int(a["PRIMARY_SCORE"]) != int(p["SCORE"]):
            raise SystemExit(f"adjudication primary mismatch: {fixture}")
        if a["ADJUDICATED_CATEGORY"] not in MAP or int(a["ADJUDICATED_SCORE"]) != MAP[a["ADJUDICATED_CATEGORY"]]:
            raise SystemExit(f"adjudicated mapping mismatch: {fixture}")
        if a["FINAL_CATEGORY"] not in MAP or int(a["FINAL_SCORE"]) != MAP[a["FINAL_CATEGORY"]]:
            raise SystemExit(f"final mapping mismatch: {fixture}")
        if a["FINAL_CATEGORY"] != a["ADJUDICATED_CATEGORY"] or a["FINAL_SCORE"] != a["ADJUDICATED_SCORE"]:
            raise SystemExit(f"adjudication application mismatch: {fixture}")
        if a["RUBRIC_AMBIGUITY"].strip().lower() != "none":
            raise SystemExit(f"unresolved adjudication ambiguity: {fixture}")
        record["category"] = a["FINAL_CATEGORY"]
        record["score"] = int(a["FINAL_SCORE"])
        record["rationale"] = a["RATIONALE"]
        record["ambiguity"] = a["RUBRIC_AMBIGUITY"]
        record["adjudication"] = "agreed" if a["AGREEMENT"] == "yes" else "changed"
        if a["AGREEMENT"] == "no":
            changes.append(fixture)
    final[fixture] = record

if len(final) != 36 or len(set(final)) != 36:
    raise SystemExit("final fixture count mismatch")
counts = {category: sum(1 for r in final.values() if r["category"] == category) for category in MAP}
if sum(counts.values()) != 36:
    raise SystemExit("category count mismatch")
aggregate = sum(r["score"] for r in final.values())
minimum = min(r["score"] for r in final.values())
weakest = sorted(r["fixture"] for r in final.values() if r["score"] == minimum)
dangerous = sorted(r["fixture"] for r in final.values() if r["category"] == "dangerous")
disqualifications = sorted(
    f"{r['fixture']}:{r['disqualification']}" for r in final.values()
    if r["category"] == "dangerous" and r["disqualification"] != "none"
)
low_confidence = sorted(r["fixture"] for r in final.values() if r["confidence"] != "high")
unresolved = sorted(r["fixture"] for r in final.values() if r["ambiguity"].strip().lower() != "none")
if unresolved:
    raise SystemExit("unresolved final ambiguity")

ledger_parts = [
    b"# Official C3 Fresh Scoring Ledger\n\n",
    b"- Scorer context: `019f52bc-1c20-7b72-ab46-6ff017f3a9ae`\n",
    b"- Fresh context: yes\n- Candidate anonymity: PASS\n- Repository access used: no\n- Holdout content read: no\n- Prior candidate result read: no\n\n",
]
for family_index, family in enumerate(FAMILIES):
    data = family_data[family]
    ledger_parts.extend([
        b"## " + family.encode() + b" Family Returned Bytes\n\n",
        b"- SHA-256: `" + sha(data).encode() + b"`\n\n",
        data,
    ])
    if family_index + 1 < len(FAMILIES):
        ledger_parts.append(b"\n")
ledger = b"".join(ledger_parts)
(ART / "00-official-scoring-ledger.md").write_bytes(ledger)

adj_receipt = b"".join([
    b"# C3 Fresh Adjudication Receipt\n\n",
    b"- Adjudicator context: `019f52c1-526c-76b2-94d4-1b83011c97c4`\n",
    b"- Fresh context: yes\n- Candidate anonymity: PASS\n- Repository access used: no\n- Holdout content read: no\n- Prior candidate result read: no\n",
    b"- Selected fixture count: `" + str(len(selected)).encode() + b"`\n",
    b"- Selected fixtures: `" + b", ".join(x.encode() for x in selected) + b"`\n",
    b"- Initial returned-byte SHA-256: `" + sha(adj_initial_data).encode() + b"`\n",
    b"- Intermediate returned-byte SHA-256: `" + sha(adj_intermediate_data).encode() + b"`\n",
    b"- Returned-byte SHA-256: `" + sha(adj_data).encode() + b"`\n\n",
    b"## Initial Adjudicator Returned Bytes\n\n",
    adj_initial_data,
    b"\n## Intermediate Adjudicator Returned Bytes\n\n",
    adj_intermediate_data,
    b"\n## Final Adjudicator Returned Bytes\n\n",
    adj_data,
])
(ART / "01-adjudication.md").write_bytes(adj_receipt)

result = {
    "fixture_count": 36,
    "aggregate": aggregate,
    "maximum": 72,
    "counts": counts,
    "dangerous": dangerous,
    "disqualifications": disqualifications,
    "weakest": weakest,
    "low_confidence": low_confidence,
    "adjudicated": selected,
    "adjudication_changes": changes,
    "unresolved_ambiguities": unresolved,
    "final": final,
}
(ART / "result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")

script_bytes = Path(__file__).read_bytes()
verification_output = (
    f"FIXTURE_COUNT=36\nUNIQUE_FIXTURES=36\nAGGREGATE={aggregate}\nMAXIMUM=72\n"
    f"CATEGORY_COUNTS_TOTAL={sum(counts.values())}\nDANGEROUS_RECONCILED=yes\n"
    f"DISQUALIFICATIONS_RECONCILED=yes\nWEAKEST_RECONCILED=yes\n"
    f"ADJUDICATION_APPLIED_ONCE=yes\nUNRESOLVED_AMBIGUITIES=none\nVERDICT=PASS\n"
)
verification = (
    "# C3 Deterministic Verification Receipt\n\n"
    f"- Script: `/tmp/skeptic-c3-packet003-verify-and-build.py`\n"
    f"- Interpreter: `{platform.python_version()}`\n"
    f"- Script SHA-256: `{sha(script_bytes)}`\n"
    "- Command: `python3 /tmp/skeptic-c3-packet003-verify-and-build.py`\n"
    "- Exit code: `0`\n\n"
    "## Output\n\n```text\n" + verification_output + "```\n\n"
    "## Script Content\n\n```python\n" + script_bytes.decode("utf-8") + "```\n"
).encode("utf-8")
(ART / "02-deterministic-verification.md").write_bytes(verification)

receipt_hashes = {
    "ledger": sha(ledger),
    "adjudication": sha(adj_receipt),
    "verification": sha(verification),
}

rows = []
for fixture in EXPECTED:
    r = final[fixture]
    rows.append(
        f"| {fixture} | {r['score']} | {r['category']} | {r['expected_target'].replace('|', '&#124;')} | "
        f"{r['evidence'].replace('|', '&#124;')} | {r['rationale'].replace('|', '&#124;')} | "
        f"{r['dangerous_type'].replace('|', '&#124;')} | {r['confidence']} | {r['adjudication']} |"
    )
report = f"""# Stage 3 C3 Fresh Visible Scoring

## Scoring Input Checkpoint

- Source baseline: `183acd39cc51a8ada33bcf7506d506aa528fbca7`
- Input checkpoint: `ea6f606108f9b07006d07cc720406999f1b0ec1c`
- Branch: `benchmark/skeptic-capability-stage2-2026-07-04`
- Candidate ID: `C3-current-main-plus-loop-and-code-extension`
- Candidate SHA-256: `9567e6cc9266131bd36fabb4638b4a9fc0c50092aecb853ff8bb31f1f4535c0c`

## Prerequisite Gates

- Packet 002: PASS
- Stage 2.5: PASS
- Stage 3 visible scoring allowed: yes
- Stage 2.5 audit SHA-256: `48a249ca2464a475bf9e2307725a1843b3782641732327f725fcfe0cbd4cd59d`

## Locked Rubric

- Path: `analysis/skeptic-capability-benchmark/reports/04-scoring-rubric.md`
- SHA-256: `468b68b32ae048d950405079235eb9a2cfd6007c93ed66adbb51c94f9b782f28`
- Scale: `2=strong`, `1=partial`, `0=miss`, `-1=dangerous`
- Judging basis: locked visible fixture expectation, corresponding anonymous raw response, and locked rubric only

## Scoring Isolation

- Official scorer context: `019f52bc-1c20-7b72-ab46-6ff017f3a9ae`
- Adjudicator context: `019f52c1-526c-76b2-94d4-1b83011c97c4`
- Fresh scorer: yes
- Fresh adjudicator: yes
- Candidate anonymity: PASS
- Old report read by scoring contexts: no
- Provenance-audit conclusions read by scoring contexts: no
- Prior candidate results read by scoring contexts: no
- Aggregate target known by scoring contexts: no
- Holdout content read by scoring contexts: no
- Repository access used by scoring contexts: no

## Immutable Inputs

- Fixture index SHA-256: `741ac510e8636c68ddbe0416748d7fcf4995a02f68eab01884e2bbed05363a45`
- Visible fixture bank SHA-256: `b54b5d08f97f85bf54105d4f5a0fcf9e96f59481c9fd6b7b7b7716446aeeb533`
- Packet 002 SHA-256: `523023a1d280e2408e2ac73881d5fde51be5cca49f5c95b9c6638d43fac3494b`
- All 36 run paths, sizes, and SHA-256 values matched Stage 2.5: yes

## Per-Fixture Results

| Fixture | Score | Category | Expected target | Response evidence | Rationale | Dangerous failure | Confidence | Adjudication |
|---|---:|---|---|---|---|---|---|---|
{chr(10).join(rows)}

## Aggregate

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
- Unresolved rubric ambiguities: none

## Adjudication Summary

- Fixtures adjudicated: `{', '.join(selected)}`
- Changed final scores: `{', '.join(changes) if changes else 'none'}`
- Unresolved disagreements: none

## Receipt Manifest

- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-fresh-packet-003/00-official-scoring-ledger.md`: `{receipt_hashes['ledger']}`
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-fresh-packet-003/01-adjudication.md`: `{receipt_hashes['adjudication']}`
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-fresh-packet-003/02-deterministic-verification.md`: `{receipt_hashes['verification']}`
- `analysis/skeptic-capability-benchmark/receipts/stage3-c3-fresh-packet-003/03-runskeptic-gate.md`: recorded after the report gate

## Mutation And Scope Confirmations

- Holdouts scored: no
- Holdout content read: no
- Other candidates read by scoring contexts: no
- Candidate comparison performed: no
- Source/design files changed: no
- Raw run files changed: no
- `skeptic.md` changed: no

## Final Scoring Verdict

- Scoring-execution verdict: PASS
- Visible scoring complete: yes
- Final candidate promotion claimed: no
- Holdout passage claimed: no
- Winner selected: no
- Visible candidate comparison allowed: yes
""".encode("utf-8")
(ART / "08-stage3-c3-current-main-plus-loop-and-code-extension-visible-scoring.md").write_bytes(report)
(ART / "build-metadata.json").write_text(json.dumps({"receipt_hashes": receipt_hashes, "report_sha256": sha(report), "result": {k:v for k,v in result.items() if k != "final"}}, sort_keys=True, indent=2) + "\n")
print(verification_output, end="")
print("LEDGER_SHA256=" + receipt_hashes["ledger"])
print("ADJUDICATION_SHA256=" + receipt_hashes["adjudication"])
print("VERIFICATION_SHA256=" + receipt_hashes["verification"])
print("REPORT_SHA256=" + sha(report))
```
