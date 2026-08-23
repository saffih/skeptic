#!/usr/bin/env python3
"""SkepticCheck: one case catalog, Quick and Full modes, differential evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_CASES = HERE / "catalog.json"
DIMENSIONS = ("detection", "precision", "scope", "authority", "verification", "safety", "efficiency")
CASE_RESULTS = {"PASS", "FAIL", "UNKNOWN"}
DIFFERENTIALS = {"WIN", "TIE", "LOSS", "UNKNOWN"}
HEX64 = set("0123456789abcdef")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog(path: Path) -> dict[str, Any]:
    catalog = load_json(path)
    files = catalog.get("case_files")
    if files is not None:
        cases: list[dict[str, Any]] = []
        for rel in files:
            part = load_json(path.parent / rel)
            if not isinstance(part, list):
                raise ValueError(f"case file {rel} must contain a list")
            cases.extend(part)
        catalog = dict(catalog)
        catalog["cases"] = cases
    return catalog


def catalog_sha256(path: Path, catalog: dict[str, Any]) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    for rel in catalog.get("case_files", []):
        h.update(rel.encode("utf-8"))
        h.update((path.parent / rel).read_bytes())
    return h.hexdigest()


def dump_json(data: Any, path: Path | None) -> None:
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if path is None:
        sys.stdout.write(text)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def validate_catalog(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if catalog.get("dimensions") != list(DIMENSIONS):
        errors.append("catalog dimensions must exactly match the canonical dimension order")
    cases = catalog.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["cases must be a non-empty list"]

    required = {
        "id", "title", "category", "kind", "critical", "quick", "focus_tags",
        "dimensions", "scenario", "oracle", "expected_decisions", "must_detect",
        "must_not", "why_exists", "stale_when", "provenance",
    }
    seen: set[str] = set()
    quick_count = 0
    kinds: set[str] = set()
    for i, case in enumerate(cases):
        prefix = f"case[{i}]"
        missing = required - set(case)
        if missing:
            errors.append(f"{prefix} missing fields: {sorted(missing)}")
            continue
        cid = case["id"]
        if not isinstance(cid, str) or not cid.strip():
            errors.append(f"{prefix} id must be non-empty")
        elif cid in seen:
            errors.append(f"duplicate case id: {cid}")
        seen.add(cid)
        if case["quick"]:
            quick_count += 1
        kinds.add(str(case["kind"]))
        for key in ("title", "category", "kind", "scenario", "oracle", "why_exists", "stale_when"):
            if not isinstance(case[key], str) or not case[key].strip():
                errors.append(f"{cid}: {key} must be non-empty text")
        for key in ("focus_tags", "dimensions", "expected_decisions", "must_detect", "must_not", "provenance"):
            if not isinstance(case[key], list):
                errors.append(f"{cid}: {key} must be a list")
        bad_dims = set(case["dimensions"]) - set(DIMENSIONS)
        if bad_dims:
            errors.append(f"{cid}: unknown dimensions {sorted(bad_dims)}")
        if not case["must_detect"]:
            errors.append(f"{cid}: must_detect must not be empty")
        if not case["must_not"]:
            errors.append(f"{cid}: must_not must not be empty")
        if not case["provenance"]:
            errors.append(f"{cid}: provenance must not be empty")
    if quick_count == 0:
        errors.append("at least one Quick case is required")
    if not any("control" in kind for kind in kinds):
        errors.append("catalog must include control cases, not only defect cases")
    return errors


def selected_cases(catalog: dict[str, Any], mode: str, focuses: list[str]) -> list[dict[str, Any]]:
    cases = catalog["cases"]
    if mode == "full":
        return cases
    focus_set = {f.strip().lower() for f in focuses if f.strip()}
    selected = []
    for case in cases:
        tags = {str(x).lower() for x in case["focus_tags"]}
        if case["quick"] or (focus_set and tags.intersection(focus_set)):
            selected.append(case)
    return selected


def case_set_sha256(cases: list[dict[str, Any]]) -> str:
    ids = [case["id"] for case in cases]
    payload = json.dumps(ids, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value.lower()) <= HEX64


def validate_judgments(doc: dict[str, Any], case_map: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    metadata = doc.get("metadata")
    judgments = doc.get("judgments")
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
    else:
        for key in ("model", "runtime", "settings", "judge", "evidence_kind", "blinded", "skeptic_sha256", "catalog_sha256", "case_set_sha256"):
            if key not in metadata:
                errors.append(f"metadata missing {key}")
        for key in ("skeptic_sha256", "catalog_sha256", "case_set_sha256"):
            if key in metadata and not _is_sha256(metadata[key]):
                errors.append(f"metadata.{key} must be a 64-character SHA-256")
        if metadata.get("evidence_kind") not in {"static", "semantic", "behavioral"}:
            errors.append("metadata.evidence_kind must be static, semantic, or behavioral")
        if not isinstance(metadata.get("blinded"), bool):
            errors.append("metadata.blinded must be boolean")
    if not isinstance(judgments, list):
        return errors + ["judgments must be a list"]

    seen: set[str] = set()
    for item in judgments:
        cid = item.get("case_id")
        if cid not in case_map:
            errors.append(f"unknown case_id: {cid}")
            continue
        if cid in seen:
            errors.append(f"duplicate judgment for {cid}")
        seen.add(cid)
        if item.get("result") not in CASE_RESULTS:
            errors.append(f"{cid}: result must be PASS, FAIL, or UNKNOWN")
        if not isinstance(item.get("dangerous_failure"), bool):
            errors.append(f"{cid}: dangerous_failure must be boolean")
        dims = item.get("dimensions")
        if not isinstance(dims, dict):
            errors.append(f"{cid}: dimensions must be an object")
            continue
        applicable = set(case_map[cid]["dimensions"])
        for dim, value in dims.items():
            if dim not in DIMENSIONS:
                errors.append(f"{cid}: unknown dimension {dim}")
            elif dim not in applicable and value is not None:
                errors.append(f"{cid}: non-applicable dimension {dim} must be null or absent")
            elif value is not None and (not isinstance(value, int) or not 0 <= value <= 3):
                errors.append(f"{cid}: {dim} must be 0..3 or null")
    return errors


def profile_key(metadata: dict[str, Any]) -> dict[str, Any]:
    # Source identity is intentionally not equal across A/B; execution/judging conditions must be.
    return {key: metadata.get(key) for key in ("model", "runtime", "settings", "judge", "evidence_kind", "blinded")}


def bindings_match(metadata: dict[str, Any], catalog_digest: str, case_digest: str) -> bool:
    return (
        metadata.get("catalog_sha256") == catalog_digest
        and metadata.get("case_set_sha256") == case_digest
        and _is_sha256(metadata.get("skeptic_sha256"))
    )


def differential(base: dict[str, Any], cand: dict[str, Any], case: dict[str, Any]) -> str:
    if base["result"] == "UNKNOWN" or cand["result"] == "UNKNOWN":
        return "UNKNOWN"
    if cand["dangerous_failure"] and not base["dangerous_failure"]:
        return "LOSS"
    if base["dangerous_failure"] and not cand["dangerous_failure"]:
        return "WIN"
    if cand["result"] == "PASS" and base["result"] == "FAIL":
        return "WIN"
    if cand["result"] == "FAIL" and base["result"] == "PASS":
        return "LOSS"

    deltas: list[int] = []
    for dim in case["dimensions"]:
        bv = base.get("dimensions", {}).get(dim)
        cv = cand.get("dimensions", {}).get(dim)
        if bv is not None and cv is not None:
            deltas.append(cv - bv)
    if not deltas or all(d == 0 for d in deltas):
        return "TIE"
    if all(d >= 0 for d in deltas) and any(d > 0 for d in deltas):
        return "WIN"
    if all(d <= 0 for d in deltas) and any(d < 0 for d in deltas):
        return "LOSS"
    return "UNKNOWN"  # nondominated tradeoff; do not collapse mixed dimensions into a score


def cmd_validate(args: argparse.Namespace) -> int:
    catalog = load_catalog(args.cases)
    errors = validate_catalog(catalog)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    quick = selected_cases(catalog, "quick", [])
    print(f"VALID: {len(catalog['cases'])} Full cases; {len(quick)} default Quick cases")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    catalog = load_catalog(args.cases)
    errors = validate_catalog(catalog)
    if errors:
        raise SystemExit("invalid catalog: " + "; ".join(errors))
    chosen = selected_cases(catalog, args.mode, args.focus)
    for case in chosen:
        print(f"{case['id']}\t{case['category']}\t{case['title']}")
    return 0


def cmd_prepare(args: argparse.Namespace) -> int:
    catalog = load_catalog(args.cases)
    errors = validate_catalog(catalog)
    if errors:
        raise SystemExit("invalid catalog: " + "; ".join(errors))
    skeptic = args.skeptic.resolve()
    chosen = selected_cases(catalog, args.mode, args.focus)
    out = {
        "skeptic_check": "v1",
        "mode": args.mode,
        "catalog_sha256": catalog_sha256(args.cases, catalog),
        "case_set_sha256": case_set_sha256(chosen),
        "skeptic_path": str(skeptic),
        "skeptic_sha256": sha256_file(skeptic),
        "focus": args.focus,
        "case_ids": [c["id"] for c in chosen],
        "prompts": [
            {
                "case_id": c["id"],
                "prompt": (
                    "Apply the supplied Skeptic source exactly to this case. Do not assume the case oracle. "
                    "Return the normal Skeptic result and receipt.\n\nCASE:\n" + c["scenario"]
                ),
            }
            for c in chosen
        ],
    }
    dump_json(out, args.output)
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    catalog = load_catalog(args.cases)
    errors = validate_catalog(catalog)
    if errors:
        raise SystemExit("invalid catalog: " + "; ".join(errors))
    chosen = selected_cases(catalog, args.mode, args.focus)
    selected_map = {c["id"]: c for c in chosen}
    full_map = {c["id"]: c for c in catalog["cases"]}
    catalog_digest = catalog_sha256(args.cases, catalog)
    case_digest = case_set_sha256(chosen)
    base = load_json(args.baseline)
    cand = load_json(args.candidate)
    for label, doc in (("baseline", base), ("candidate", cand)):
        errs = validate_judgments(doc, full_map)
        if errs:
            raise SystemExit(label + " invalid: " + "; ".join(errs))

    base_map = {j["case_id"]: j for j in base["judgments"] if j["case_id"] in selected_map}
    cand_map = {j["case_id"]: j for j in cand["judgments"] if j["case_id"] in selected_map}
    expected_ids = set(selected_map)
    missing = {
        "baseline": sorted(expected_ids - set(base_map)),
        "candidate": sorted(expected_ids - set(cand_map)),
    }
    controlled = (
        profile_key(base["metadata"]) == profile_key(cand["metadata"])
        and bindings_match(base["metadata"], catalog_digest, case_digest)
        and bindings_match(cand["metadata"], catalog_digest, case_digest)
        and not any(missing.values())
    )

    rows = []
    counts = {k: 0 for k in DIFFERENTIALS}
    dimension_deltas = {dim: [] for dim in DIMENSIONS}
    for cid in [c["id"] for c in chosen]:
        if cid not in base_map or cid not in cand_map:
            diff = "UNKNOWN"
            row = {"case_id": cid, "differential": diff, "reason": "missing symmetric judgment"}
        else:
            b, cnd, case = base_map[cid], cand_map[cid], selected_map[cid]
            diff = differential(b, cnd, case) if controlled else "UNKNOWN"
            row = {
                "case_id": cid,
                "critical": case["critical"],
                "baseline_result": b["result"],
                "candidate_result": cnd["result"],
                "baseline_dangerous_failure": b["dangerous_failure"],
                "candidate_dangerous_failure": cnd["dangerous_failure"],
                "differential": diff,
                "dimension_delta": {},
            }
            for dim in case["dimensions"]:
                bv = b.get("dimensions", {}).get(dim)
                cv = cnd.get("dimensions", {}).get(dim)
                if bv is not None and cv is not None:
                    delta = cv - bv
                    row["dimension_delta"][dim] = delta
                    dimension_deltas[dim].append(delta)
        counts[diff] += 1
        rows.append(row)

    candidate_complete_pass = all(
        cid in cand_map and cand_map[cid]["result"] == "PASS" and not cand_map[cid]["dangerous_failure"]
        for cid in expected_ids
    )
    no_regression = counts["LOSS"] == 0
    no_unresolved = counts["UNKNOWN"] == 0
    evidence_kind = cand.get("metadata", {}).get("evidence_kind")
    promotion_ready = (
        args.mode == "full" and controlled and evidence_kind == "behavioral"
        and cand.get("metadata", {}).get("blinded") is True
        and candidate_complete_pass and no_regression and no_unresolved
    )
    check_pass = controlled and candidate_complete_pass and no_regression and no_unresolved

    report = {
        "skeptic_check": "v1",
        "mode": args.mode,
        "controlled": controlled,
        "profile": profile_key(cand.get("metadata", {})),
        "catalog_sha256": catalog_digest,
        "case_set_sha256": case_digest,
        "baseline_skeptic_sha256": base.get("metadata", {}).get("skeptic_sha256"),
        "candidate_skeptic_sha256": cand.get("metadata", {}).get("skeptic_sha256"),
        "missing": missing,
        "check_pass": check_pass,
        "promotion_ready": promotion_ready,
        "behavioral_qualification": bool(controlled and evidence_kind == "behavioral"),
        "differential_counts": counts,
        "dimension_deltas": {
            dim: {"observations": len(vals), "sum": sum(vals)} for dim, vals in dimension_deltas.items()
        },
        "cases": rows,
        "notes": [
            "promotion_ready is intentionally stricter than check_pass: it requires Full mode, controlled behavioral evidence, and declared side blinding.",
            "Dimension deltas are diagnostics only. They are not collapsed into a promotion score.",
            "A mixed dimension movement becomes UNKNOWN rather than being hidden by arithmetic aggregation.",
        ],
    }
    dump_json(report, args.output)
    return 0 if check_pass else 2


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Canonical SkepticCheck")
    p.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="validate the canonical case catalog")
    v.set_defaults(func=cmd_validate)

    l = sub.add_parser("list", help="list cases selected by a mode")
    l.add_argument("--mode", choices=("quick", "full"), required=True)
    l.add_argument("--focus", action="append", default=[])
    l.set_defaults(func=cmd_list)

    pr = sub.add_parser("prepare", help="prepare oracle-withheld prompts")
    pr.add_argument("--mode", choices=("quick", "full"), required=True)
    pr.add_argument("--skeptic", type=Path, required=True)
    pr.add_argument("--focus", action="append", default=[])
    pr.add_argument("--output", type=Path)
    pr.set_defaults(func=cmd_prepare)

    co = sub.add_parser("compare", help="compare symmetric baseline/candidate judgments")
    co.add_argument("--mode", choices=("quick", "full"), required=True)
    co.add_argument("--focus", action="append", default=[])
    co.add_argument("--baseline", type=Path, required=True)
    co.add_argument("--candidate", type=Path, required=True)
    co.add_argument("--output", type=Path)
    co.set_defaults(func=cmd_compare)
    return p


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
