#!/usr/bin/env python3
"""Minimal deterministic RunSkeptic golden-case benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = Path(__file__).with_name("cases.json")
SKEPTIC_PATH = ROOT / "skeptic.md"
REQUIRED_METADATA_FIELDS = {"model", "version", "effort", "runtime", "settings"}
MANDATORY_CASE_FIELDS = {
    "id",
    "title",
    "category",
    "critical",
    "thinkers",
    "artifact",
    "expected_decisions",
    "required_concepts",
    "forbidden_concepts",
    "notes",
}
INTERNAL_DECISIONS = {"PASS", "ACTION", "CONFLICT"}
FINAL_CATEGORIES = {"HANDLED", "CONFLICT"}


class BenchmarkError(ValueError):
    pass


def current_thinker_contract(path: Path = SKEPTIC_PATH) -> tuple[set[str], set[str]]:
    text = path.read_text(encoding="utf-8")
    try:
        section = text.split("## 3. Thinkers", 1)[1].split("## 4. Structural Checks", 1)[0]
    except IndexError as exc:
        raise BenchmarkError("cannot locate current Thinkers section in skeptic.md") from exc
    families = set(re.findall(r"(?m)^### .+ \(([A-Z]{2})\)", section))
    tags = set(re.findall(r"`([A-Z]{2}:[A-Z]{2})`", section))
    if not families or any(not any(tag.startswith(family + ":") for tag in tags) for family in families):
        raise BenchmarkError("current Thinker families/aspects could not be derived")
    return families, tags


CURRENT_THINKER_FAMILIES, CURRENT_THINKER_TAGS = current_thinker_contract()


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BenchmarkError(f"cannot read JSON {path}: {exc}") from exc


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cases(path: Path = CASES_PATH) -> list[dict]:
    value = read_json(path)
    if not isinstance(value, list):
        raise BenchmarkError("cases.json must contain a JSON array")
    return value


def _validate_concepts(case_id: str, field: str, concepts, errors: list[str]) -> None:
    if not isinstance(concepts, list):
        errors.append(f"{case_id}: {field} must be a list")
        return
    for index, concept in enumerate(concepts):
        label = f"{case_id}: {field}[{index}]"
        if not isinstance(concept, dict) or not isinstance(concept.get("name"), str):
            errors.append(f"{label} needs a string name")
            continue
        groups = concept.get("patterns")
        if not isinstance(groups, list) or not groups:
            errors.append(f"{label}.patterns must be a nonempty list")
            continue
        for group_index, group in enumerate(groups):
            if not isinstance(group, list) or not group or not all(
                isinstance(term, str) and term.strip() for term in group
            ):
                errors.append(
                    f"{label}.patterns[{group_index}] must contain nonempty strings"
                )


def validate_cases(cases: list[dict]) -> dict:
    errors: list[str] = []
    ids: list[str] = []
    covered: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"case[{index}] must be an object")
            continue
        case_id = case.get("id", f"case[{index}]")
        missing = sorted(MANDATORY_CASE_FIELDS - set(case))
        if missing:
            errors.append(f"{case_id}: missing fields {', '.join(missing)}")
        if isinstance(case.get("id"), str) and case["id"]:
            ids.append(case["id"])
        else:
            errors.append(f"case[{index}]: id must be a nonempty string")
        if not isinstance(case.get("critical"), bool):
            errors.append(f"{case_id}: critical must be boolean")
        decisions = case.get("expected_decisions")
        if not isinstance(decisions, list) or not decisions:
            errors.append(f"{case_id}: expected_decisions must be nonempty")
        elif not set(decisions) <= INTERNAL_DECISIONS:
            errors.append(f"{case_id}: invalid expected decision")
        elif case.get("critical") and "PASS" in decisions:
            errors.append(f"{case_id}: critical cases cannot expect PASS")
        thinkers = case.get("thinkers")
        if not isinstance(thinkers, list) or not thinkers:
            errors.append(f"{case_id}: thinkers must be nonempty")
        else:
            for thinker in thinkers:
                if not isinstance(thinker, str):
                    errors.append(f"{case_id}: thinker tags must be strings")
                    continue
                family = thinker.split(":", 1)[0]
                if family not in CURRENT_THINKER_FAMILIES:
                    errors.append(f"{case_id}: unknown current Thinker family {family}")
                elif ":" in thinker and thinker not in CURRENT_THINKER_TAGS:
                    errors.append(f"{case_id}: unknown current Thinker tag {thinker}")
                else:
                    covered.add(family)
        _validate_concepts(case_id, "required_concepts", case.get("required_concepts"), errors)
        _validate_concepts(case_id, "forbidden_concepts", case.get("forbidden_concepts"), errors)
    duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
    if duplicates:
        errors.append(f"duplicate case IDs: {', '.join(duplicates)}")
    missing_families = sorted(CURRENT_THINKER_FAMILIES - covered)
    if missing_families:
        errors.append(f"missing Thinker family coverage: {', '.join(missing_families)}")
    if errors:
        raise BenchmarkError("\n".join(errors))
    return {
        "case_count": len(cases),
        "critical_count": sum(bool(case["critical"]) for case in cases),
        "required_concept_count": sum(len(case["required_concepts"]) for case in cases),
        "thinker_families": sorted(covered),
    }


def concept_matches(text: str, concept: dict) -> bool:
    lowered = text.casefold()
    return any(all(term.casefold() in lowered for term in group) for group in concept["patterns"])


def extract_decisions(text: str) -> tuple[str | None, str | None]:
    internal = None
    final = None
    internal_patterns = (
        r"(?im)^\s*(?:case|finding|internal)?\s*decision\s*:\s*(PASS|ACTION|CONFLICT)\b",
        r"(?im)^\s*finding category\s*:\s*(PASS|ACTION|CONFLICT)\b",
    )
    for pattern in internal_patterns:
        match = re.search(pattern, text)
        if match:
            internal = match.group(1).upper()
            break
    final_match = re.search(
        r"(?im)^\s*final output category\s*:\s*(HANDLED|CONFLICT)\b", text
    )
    if final_match:
        final = final_match.group(1).upper()
    return internal, final


def has_runskeptic_receipt(text: str) -> bool:
    anchors = (
        "source read:",
        "permission mode:",
        "done statement:",
        "major steps run:",
        "thinkers considered:",
        "evidence used:",
        "decision path:",
        "verification performed:",
        "unresolved conflicts / unknowns:",
        "final output category:",
    )
    lowered = text.casefold()
    count = sum(anchor in lowered for anchor in anchors)
    return (
        "runskeptic receipt" in lowered
        and "source read:" in lowered
        and "final output category:" in lowered
        and count >= 8
    )


def normalize_response_set(value) -> tuple[dict | None, list[dict]]:
    if isinstance(value, list):
        return None, value
    if isinstance(value, dict) and isinstance(value.get("responses"), list):
        metadata = value.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise BenchmarkError("response metadata must be an object")
        return metadata, value["responses"]
    raise BenchmarkError("responses must be a list or an object containing responses")


def metadata_is_complete(metadata) -> bool:
    return (
        isinstance(metadata, dict)
        and REQUIRED_METADATA_FIELDS <= set(metadata)
        and all(metadata[field] not in (None, "") for field in REQUIRED_METADATA_FIELDS)
        and isinstance(metadata["settings"], dict)
    )


def score_response(case: dict, response: str) -> dict:
    matched = [
        concept["name"]
        for concept in case["required_concepts"]
        if concept_matches(response, concept)
    ]
    missed = [
        concept["name"]
        for concept in case["required_concepts"]
        if concept["name"] not in matched
    ]
    forbidden = [
        concept["name"]
        for concept in case["forbidden_concepts"]
        if concept_matches(response, concept)
    ]
    internal, final = extract_decisions(response)
    compatible = internal in case["expected_decisions"]
    receipt = has_runskeptic_receipt(response)
    characters = len(response)
    words = len(response.split())
    estimated_tokens = math.ceil(characters / 4)
    quality_points = len(matched) + int(compatible) + int(receipt) - 2 * len(forbidden)
    return {
        "case_id": case["id"],
        "critical": case["critical"],
        "required_matched": matched,
        "required_missed": missed,
        "forbidden_triggered": forbidden,
        "internal_decision": internal,
        "final_output_category": final,
        "decision_compatible": compatible,
        "receipt_present": receipt,
        "word_count": words,
        "character_count": characters,
        "estimated_token_count": estimated_tokens,
        "estimated_token_note": "ceil(character_count / 4); not provider billing data",
        "quality_points": quality_points,
    }


def score_run(cases: list[dict], response_value) -> dict:
    metadata, responses = normalize_response_set(response_value)
    by_id: dict[str, str] = {}
    for record in responses:
        if not isinstance(record, dict) or not isinstance(record.get("case_id"), str):
            raise BenchmarkError("each response needs a string case_id")
        if record["case_id"] in by_id:
            raise BenchmarkError(f"duplicate response case_id: {record['case_id']}")
        if not isinstance(record.get("response"), str):
            raise BenchmarkError(f"{record['case_id']}: response must be a string")
        by_id[record["case_id"]] = record["response"]
    case_ids = {case["id"] for case in cases}
    if set(by_id) != case_ids:
        missing = sorted(case_ids - set(by_id))
        extra = sorted(set(by_id) - case_ids)
        raise BenchmarkError(f"response IDs mismatch; missing={missing}, extra={extra}")
    results = [score_response(case, by_id[case["id"]]) for case in cases]
    required_total = sum(
        len(result["required_matched"]) + len(result["required_missed"])
        for result in results
    )
    required_matched = sum(len(result["required_matched"]) for result in results)
    forbidden_count = sum(len(result["forbidden_triggered"]) for result in results)
    compatible_count = sum(result["decision_compatible"] for result in results)
    receipt_count = sum(result["receipt_present"] for result in results)
    aggregate = {
        "case_count": len(results),
        "required_concepts_total": required_total,
        "required_concepts_matched": required_matched,
        "required_concept_recall": required_matched / required_total if required_total else 1.0,
        "forbidden_findings": forbidden_count,
        "compatible_decisions": compatible_count,
        "compatibility_rate": compatible_count / len(results) if results else 1.0,
        "receipt_compliance_count": receipt_count,
        "receipt_compliance_rate": receipt_count / len(results) if results else 1.0,
        "median_estimated_output_tokens": statistics.median(
            result["estimated_token_count"] for result in results
        ) if results else 0,
        "quality_points": sum(result["quality_points"] for result in results),
    }
    critical_misses = [
        {"case_id": result["case_id"], "concepts": result["required_missed"]}
        for result in results
        if result["critical"] and result["required_missed"]
    ]
    critical_forbidden = [
        {"case_id": result["case_id"], "concepts": result["forbidden_triggered"]}
        for result in results
        if result["critical"] and result["forbidden_triggered"]
    ]
    return {
        "schema_version": "skeptic-golden-score/1",
        "metadata": metadata,
        "cases": results,
        "aggregate": aggregate,
        "critical_misses": critical_misses,
        "critical_forbidden_findings": critical_forbidden,
    }


def compare_scores(baseline: dict, candidate: dict) -> dict:
    base_meta = baseline.get("metadata")
    cand_meta = candidate.get("metadata")
    controlled = (
        metadata_is_complete(base_meta)
        and metadata_is_complete(cand_meta)
        and base_meta == cand_meta
    )
    if not controlled:
        return {
            "verdict": "uncontrolled",
            "controlled": False,
            "reason": "model/runtime/settings metadata are missing or differ",
            "critical_regressions": [],
            "per_case": [],
        }
    base_cases = {case["case_id"]: case for case in baseline.get("cases", [])}
    cand_cases = {case["case_id"]: case for case in candidate.get("cases", [])}
    if set(base_cases) != set(cand_cases):
        raise BenchmarkError("score files contain different case IDs")
    per_case = []
    critical_regressions = []
    for case_id in sorted(base_cases):
        base = base_cases[case_id]
        cand = cand_cases[case_id]
        delta = cand["quality_points"] - base["quality_points"]
        per_case.append({"case_id": case_id, "quality_delta": delta})
        if cand.get("critical") and (
            bool(set(cand["required_missed"]) - set(base["required_missed"]))
            or bool(set(cand["forbidden_triggered"]) - set(base["forbidden_triggered"]))
            or (base["decision_compatible"] and not cand["decision_compatible"])
        ):
            critical_regressions.append(case_id)
    base_agg = baseline["aggregate"]
    cand_agg = candidate["aggregate"]
    if critical_regressions:
        verdict = "baseline_better"
        reason = "critical regression hard override"
    else:
        improved = cand_agg["quality_points"] > base_agg["quality_points"]
        degraded = cand_agg["quality_points"] < base_agg["quality_points"]
        quality_preserved = (
            cand_agg["compatibility_rate"] >= base_agg["compatibility_rate"]
            and cand_agg["forbidden_findings"] <= base_agg["forbidden_findings"]
        )
        reverse_preserved = (
            base_agg["compatibility_rate"] >= cand_agg["compatibility_rate"]
            and base_agg["forbidden_findings"] <= cand_agg["forbidden_findings"]
        )
        if improved and quality_preserved:
            verdict, reason = "candidate_better", "quality improved without gate regression"
        elif degraded and reverse_preserved:
            verdict, reason = "baseline_better", "candidate quality regressed"
        elif not improved and not degraded:
            verdict, reason = "equivalent", "quality metrics are equal"
        else:
            verdict, reason = "mixed", "quality signals move in different directions"
    return {
        "verdict": verdict,
        "controlled": True,
        "reason": reason,
        "critical_regressions": critical_regressions,
        "per_case": per_case,
        "efficiency": {
            "baseline_median_estimated_tokens": base_agg["median_estimated_output_tokens"],
            "candidate_median_estimated_tokens": cand_agg["median_estimated_output_tokens"],
            "note": "shorter output is secondary and never establishes candidate_better alone",
        },
    }


def build_prompt(case: dict, skeptic_text: str, skeptic_hash: str) -> dict:
    prompt = f"""Apply the complete current RunSkeptic contract below to the case artifact.
Use current Thinker tags, distinguish the internal finding decision from the final task output
category, and include the required compact RunSkeptic Receipt. Do not optimize for benchmark
keywords; report only evidence-supported material findings.

CASE ID: {case['id']}
CASE TITLE: {case['title']}
ARTIFACT:
{case['artifact']}

CURRENT SKEPTIC SOURCE (SHA-256 {skeptic_hash}):
{skeptic_text}
"""
    return {
        "case_id": case["id"],
        "skeptic_sha256": skeptic_hash,
        "prompt_sha256": sha256_text(prompt),
        "prompt": prompt,
    }


def command_validate(args) -> int:
    summary = validate_cases(load_cases(args.cases))
    print(
        "VALID: {case_count} cases, {critical_count} critical, "
        "{required_concept_count} required concepts, families={thinker_families}".format(
            **summary
        )
    )
    return 0


def command_prepare(args) -> int:
    cases = load_cases(args.cases)
    validate_cases(cases)
    skeptic_text = args.skeptic.read_text(encoding="utf-8")
    skeptic_hash = sha256_text(skeptic_text)
    packet = {
        "schema_version": "skeptic-golden-prompts/1",
        "metadata": {
            "skeptic_path": str(args.skeptic),
            "skeptic_sha256": skeptic_hash,
            "case_count": len(cases),
        },
        "prompts": [build_prompt(case, skeptic_text, skeptic_hash) for case in cases],
    }
    write_json(args.output, packet)
    print(f"PREPARED: {len(cases)} prompts -> {args.output}")
    return 0


def command_score(args) -> int:
    cases = load_cases(args.cases)
    validate_cases(cases)
    result = score_run(cases, read_json(args.responses))
    write_json(args.output, result)
    agg = result["aggregate"]
    print(
        f"SCORED: recall={agg['required_concept_recall']:.3f} "
        f"compatibility={agg['compatibility_rate']:.3f} "
        f"forbidden={agg['forbidden_findings']} -> {args.output}"
    )
    return 0


def command_compare(args) -> int:
    result = compare_scores(read_json(args.baseline), read_json(args.candidate))
    if args.output:
        write_json(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--cases", type=Path, default=CASES_PATH)
    validate.set_defaults(func=command_validate)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--skeptic", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--cases", type=Path, default=CASES_PATH)
    prepare.set_defaults(func=command_prepare)
    score = sub.add_parser("score")
    score.add_argument("--responses", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--cases", type=Path, default=CASES_PATH)
    score.set_defaults(func=command_score)
    compare = sub.add_parser("compare")
    compare.add_argument("--baseline", type=Path, required=True)
    compare.add_argument("--candidate", type=Path, required=True)
    compare.add_argument("--output", type=Path)
    compare.set_defaults(func=command_compare)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (BenchmarkError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
