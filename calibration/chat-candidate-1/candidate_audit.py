#!/usr/bin/env python3
"""Mechanical preservation guard for Skeptic candidates.

This script checks syntax-level representation and ordering only. It MUST NOT be
used to claim semantic or behavioral equivalence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ASPECT_RE = re.compile(r"\b(?:CH|OM|FE|PO|KT|SH):[A-Z]{2}\b")
MD_REF_RE = re.compile(r"`([^`]+\.md)`")

RECEIPT_FIELDS = [
    "Source read",
    "Companion files read",
    "Permission mode",
    "DONE statement",
    "Prompt review level and task feasibility",
    "Major steps run",
    "Thinkers considered",
    "Evidence used",
    "Decision path",
    "Verification performed",
    "Unresolved conflicts / unknowns",
    "Final output category",
]

OUTPUT_TERMS = ["PASS", "ACTION", "DECOMPOSE", "CONFLICT", "HANDLED"]
STAGES = [
    "## 0. Gate",
    "## 0.5. Fundamental Scan",
    "## 1. Map - Detect Only",
    "## 6. Detection Confidence",
    "## 7. Stabilize",
    "## 8. Evidence Levels",
    "## 9. Decide",
    "## 10. Act",
    "## 11. Verify",
    "## 12. Learn",
]

# Each doctrine is a mechanical group of required textual signals. Passing only
# means the signals remain represented somewhere in the candidate.
DOCTRINES = {
    "source_of_truth": [r"source of truth", r"memory", r"source.*unavailable"],
    "receipt_not_proof": [r"receipt", r"neither proof|not proof", r"evidence"],
    "smallest_credible_alternative": [r"smallest credible alternative", r"CH:EV", r"OM:OD"],
    "false_simplicity": [r"OM:FS", r"proof", r"ownership", r"reversib"],
    "task_prompt_feasibility": [
        r"context", r"tokens", r"time", r"credits", r"tools", r"permissions", r"evidence"
    ],
    "completion_reserve": [r"completion reserve", r"synthesis", r"verification", r"closure"],
    "conditional_persistence": [r"Persistence is conditional", r"authorized", r"transient context"],
    "bounded_retries": [r"retries.*bounded|bounded.*retries", r"redesign", r"futil"],
    "terminal_completion": [r"pull request", r"push attempt", r"DONE requires more"],
    "trust_boundary": [r"FE:TB", r"lower-trust", r"higher-trust", r"validation|authorization"],
    "dignity_persons_as_ends": [r"people as ends", r"dignity"],
    "fairness_hidden_burden": [r"KT:UA", r"KT:HB", r"hidden burden", r"another person|another.*group"],
    "pareto_minority": [
        r"SH:PF", r"minority|subgroup", r"credible bound", r"correlation", r"long-tail",
        r"reversib", r"option value", r"stakeholder weighting"
    ],
    "structural_domain_checks": [r"## 4\. Structural Checks", r"## 5\. Domain Checks", r"selective"],
    "confidence_unknowns": [r"Detection Confidence", r"unknown", r"CONFLICT when confidence"],
    "stabilization": [r"Never decide on raw findings", r"PROVISIONAL", r"root cause"],
    "evidence_levels": [r"OBSERVED", r"REPRODUCED", r"HISTORICAL", r"INFERRED RISK"],
    "decision_paths": [r"### FIX", r"### DECOMPOSE", r"### CONFLICT"],
    "promotion_block": [r"Promotion Check", r"review-required", r"blocking unknown"],
    "act_verify_learn": [r"## 10\. Act", r"## 11\. Verify", r"## 12\. Learn"],
    "razor": [r"Razor", r"read-only", r"(?:not|never) a replacement"],
    "expert_review": [r"## 16\. Expert Review", r"one domain", r"read-only"],
    "sift": [r"## 17\. SIFT Review", r"SCAN", r"INTEGRATE", r"FIRM CONFIDENCE", r"TREAT", r"VERIFY"],
    "tag_semantics": [r"reasoning origin", r"not severity", r"never replace evidence|do not replace evidence"],
    "final_outcomes": [r"Every task ends.*HANDLED.*CONFLICT", r"### HANDLED", r"### CONFLICTS"],
}


def stats(text: str) -> dict[str, int | float]:
    b = text.encode("utf-8")
    return {
        "lines": len(text.splitlines()),
        "words": len(text.split()),
        "bytes": len(b),
        "estimated_tokens_chars4": round(len(b) / 4),
        "estimated_tokens_words133": round(len(text.split()) * 1.33),
    }


def pct_delta(base: float, cand: float) -> float:
    return round((cand - base) / base * 100, 2) if base else 0.0


def git_blob_sha(text: str) -> str:
    b = text.encode("utf-8")
    return hashlib.sha1(f"blob {len(b)}\0".encode() + b).hexdigest()


def check_patterns(text: str, patterns: list[str]) -> list[str]:
    return [p for p in patterns if not re.search(p, text, flags=re.I | re.S)]


def audit(baseline: str, candidate: str) -> dict:
    base_stats = stats(baseline)
    cand_stats = stats(candidate)
    base_tags = sorted(set(ASPECT_RE.findall(baseline)))
    cand_tags = sorted(set(ASPECT_RE.findall(candidate)))
    missing_tags = sorted(set(base_tags) - set(cand_tags))

    base_refs = sorted(set(MD_REF_RE.findall(baseline)))
    cand_refs = sorted(set(MD_REF_RE.findall(candidate)))
    new_refs = sorted(set(cand_refs) - set(base_refs))
    missing_refs = sorted(set(base_refs) - set(cand_refs))

    positions = [candidate.find(stage) for stage in STAGES]
    stage_order_ok = all(p >= 0 for p in positions) and positions == sorted(positions)

    doctrine_results = {
        name: {"pass": not (missing := check_patterns(candidate, pats)), "missing_patterns": missing}
        for name, pats in DOCTRINES.items()
    }

    receipt_missing = [field for field in RECEIPT_FIELDS if field not in candidate]
    output_missing = [term for term in OUTPUT_TERMS if not re.search(rf"\b{term}\b", candidate)]

    checks = {
        "all_baseline_aspect_tags_present": not missing_tags,
        "all_output_terms_present": not output_missing,
        "all_receipt_fields_present": not receipt_missing,
        "all_baseline_companion_refs_present": not missing_refs,
        "no_new_companion_dependency": not new_refs,
        "stage_order_valid": stage_order_ok,
        "protected_doctrines_represented": all(v["pass"] for v in doctrine_results.values()),
    }

    deltas = {
        key: pct_delta(float(base_stats[key]), float(cand_stats[key]))
        for key in base_stats
    }

    return {
        "warning": "Mechanical guard only; passing does not establish semantic or behavioral equivalence.",
        "baseline": {"git_blob_sha": git_blob_sha(baseline), **base_stats},
        "candidate": {"git_blob_sha": git_blob_sha(candidate), **cand_stats},
        "delta_percent": deltas,
        "checks": checks,
        "details": {
            "missing_aspect_tags": missing_tags,
            "missing_output_terms": output_missing,
            "missing_receipt_fields": receipt_missing,
            "baseline_companion_refs": base_refs,
            "candidate_companion_refs": cand_refs,
            "missing_companion_refs": missing_refs,
            "new_companion_refs": new_refs,
            "stage_positions": dict(zip(STAGES, positions)),
            "doctrines": doctrine_results,
        },
        "overall_mechanical_pass": all(checks.values()),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("baseline", type=Path)
    ap.add_argument("candidate", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    result = audit(args.baseline.read_text(encoding="utf-8"), args.candidate.read_text(encoding="utf-8"))
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.json:
        args.json.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["overall_mechanical_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
