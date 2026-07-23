#!/usr/bin/env python3
"""Score replicated canary runs with frozen Scorer V2 and apply the
pre-registered early-rejection rules.

Uses benchmarks/benchmark.py score_response() unmodified (per-response
scoring; score_run() requires full 12-case sets and does not apply to a
6-case canary). Deterministic; no model execution.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "benchmarks"))

import benchmark  # noqa: E402  (frozen scorer-v2, imported read-only)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    raw = json.loads(args.raw.read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in benchmark.load_cases()}

    scored_runs = []
    for run in raw["runs"]:
        case = cases[run["case_id"]]
        detail = benchmark.score_response(case, run["response"])
        scored_runs.append({
            "case_id": run["case_id"],
            "arm": run["arm"],
            "rep": run["rep"],
            "order_index": run["order_index"],
            "elapsed_seconds": run["elapsed_seconds"],
            **{k: detail[k] for k in (
                "critical", "required_matched", "required_missed",
                "forbidden_triggered", "internal_decision",
                "final_output_category", "decision_compatible",
                "receipt_present", "word_count", "estimated_token_count",
                "quality_points")},
        })

    by_case_arm: dict[tuple[str, str], list[dict]] = {}
    for run in scored_runs:
        by_case_arm.setdefault((run["case_id"], run["arm"]), []).append(run)

    case_ids = raw["case_ids"]
    reps = raw["reps"]
    per_case = []
    early_rejection_triggers = []
    for case_id in case_ids:
        control = sorted(by_case_arm.get((case_id, "control"), []),
                         key=lambda r: r["rep"])
        candidate = sorted(by_case_arm.get((case_id, "candidate"), []),
                           key=lambda r: r["rep"])
        critical = cases[case_id]["critical"]

        def missed_counts(runs):
            counter: Counter = Counter()
            for run in runs:
                counter.update(run["required_missed"])
            return counter

        def matched_counts(runs):
            counter: Counter = Counter()
            for run in runs:
                counter.update(run["required_matched"])
            return counter

        def forbidden_counts(runs):
            counter: Counter = Counter()
            for run in runs:
                counter.update(run["forbidden_triggered"])
            return counter

        cand_missed = missed_counts(candidate)
        ctrl_matched = matched_counts(control)
        cand_forbidden = forbidden_counts(candidate)
        ctrl_forbidden = forbidden_counts(control)
        ctrl_compatible = sum(r["decision_compatible"] for r in control)
        cand_compatible = sum(r["decision_compatible"] for r in candidate)
        ctrl_receipt = sum(r["receipt_present"] for r in control)
        cand_receipt = sum(r["receipt_present"] for r in candidate)

        repeated_concept_regressions = sorted(
            concept for concept, count in cand_missed.items()
            if count >= 2 and ctrl_matched.get(concept, 0) >= 2
        )
        repeated_forbidden = sorted(
            concept for concept, count in cand_forbidden.items()
            if count >= 2 and ctrl_forbidden.get(concept, 0) == 0
        )
        repeated_decision_regression = (
            ctrl_compatible >= 2 and cand_compatible <= 1
        )
        repeated_receipt_regression = (
            ctrl_receipt >= 2 and cand_receipt <= 1
        )

        if critical and repeated_concept_regressions:
            early_rejection_triggers.append(
                {"case_id": case_id,
                 "rule": "repeated critical concept miss (>=2/3 candidate, control retains >=2/3)",
                 "concepts": repeated_concept_regressions})
        if repeated_decision_regression:
            early_rejection_triggers.append(
                {"case_id": case_id, "rule": "repeated decision regression"})
        if repeated_forbidden:
            early_rejection_triggers.append(
                {"case_id": case_id,
                 "rule": "repeated new forbidden finding",
                 "concepts": repeated_forbidden})
        if repeated_receipt_regression:
            early_rejection_triggers.append(
                {"case_id": case_id, "rule": "repeated receipt regression"})

        per_case.append({
            "case_id": case_id,
            "critical": critical,
            "control": {
                "decisions": [r["internal_decision"] for r in control],
                "compatible": ctrl_compatible,
                "receipts": ctrl_receipt,
                "missed_by_rep": [sorted(r["required_missed"]) for r in control],
                "forbidden": sorted(ctrl_forbidden.elements()),
                "quality_points": [r["quality_points"] for r in control],
                "median_tokens": statistics.median(
                    r["estimated_token_count"] for r in control),
            },
            "candidate": {
                "decisions": [r["internal_decision"] for r in candidate],
                "compatible": cand_compatible,
                "receipts": cand_receipt,
                "missed_by_rep": [sorted(r["required_missed"]) for r in candidate],
                "forbidden": sorted(cand_forbidden.elements()),
                "quality_points": [r["quality_points"] for r in candidate],
                "median_tokens": statistics.median(
                    r["estimated_token_count"] for r in candidate),
            },
            "repeated_concept_regressions": repeated_concept_regressions,
            "repeated_forbidden": repeated_forbidden,
            "repeated_decision_regression": repeated_decision_regression,
            "repeated_receipt_regression": repeated_receipt_regression,
            "isolated_variance_notes": sorted(
                concept for concept, count in cand_missed.items()
                if count == 1 and ctrl_matched.get(concept, 0) >= 2
            ),
        })

    result = {
        "schema_version": "skeptic-exp-v2-canary-scores/1",
        "scorer_version": benchmark.SCORER_VERSION,
        "reps": reps,
        "runtime_metadata": raw["runtime_metadata"],
        "runs": scored_runs,
        "per_case": per_case,
        "early_rejection_triggers": early_rejection_triggers,
        "early_rejection": bool(early_rejection_triggers),
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({"early_rejection": result["early_rejection"],
                      "triggers": early_rejection_triggers}, indent=2))
    for entry in per_case:
        print(f"{entry['case_id']}: control_q={entry['control']['quality_points']} "
              f"candidate_q={entry['candidate']['quality_points']} "
              f"ctrl_dec={entry['control']['decisions']} "
              f"cand_dec={entry['candidate']['decisions']} "
              f"receipts C/K={entry['control']['receipts']}/{entry['candidate']['receipts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
