"""CLI for the Skeptic detection harness.

Usage:
    python -m harness run [--sets SET1,SET2] [--cases tc01,tc02] [--runs 3]
    python -m harness report [--run-dir results/run_XXXX]
    python -m harness list-sets
    python -m harness list-cases
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from harness.question_sets import QUESTION_SETS


def cmd_run(args):
    """Run question sets against test cases."""
    from harness.runner import run_all

    question_set_names = None
    if args.sets:
        question_set_names = [s.strip() for s in args.sets.split(",")]
        unknown = [s for s in question_set_names if s not in QUESTION_SETS]
        if unknown:
            print(f"Error: unknown question sets: {', '.join(unknown)}")
            print(f"Available: {', '.join(sorted(QUESTION_SETS.keys()))}")
            sys.exit(1)

    test_case_ids = None
    if args.cases:
        test_case_ids = [s.strip() for s in args.cases.split(",")]

    runs = args.runs or 1

    result = asyncio.run(run_all(question_set_names, test_case_ids, runs))

    if not result["scores"]:
        print("\nNo scores produced. Check that test cases exist in harness/test_cases/")
        sys.exit(1)

    print("\nDone.")


def cmd_report(args):
    """Generate report from a previous run."""
    from harness.reporter import generate_matrix, generate_summary, generate_thinker_attribution
    from harness.scorer import Score

    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"Error: run directory not found: {run_dir}")
        sys.exit(1)

    raw_dir = run_dir / "raw_responses"
    if not raw_dir.exists():
        print(f"Error: no raw_responses in {run_dir}")
        sys.exit(1)

    # Reconstruct scores from raw response files
    all_scores: dict[str, dict[str, Score]] = {}

    for raw_file in sorted(raw_dir.glob("*.json")):
        with open(raw_file) as f:
            data = json.load(f)

        qs_name = data["question_set"]
        tc_id = data["test_case_id"]
        score_data = data.get("score")

        if score_data:
            score = Score(
                tp=score_data["tp"],
                fp=score_data["fp"],
                fn=score_data["fn"],
                tn=score_data["tn"],
                precision=score_data["precision"],
                recall=score_data["recall"],
                f1=score_data["f1"],
                matches=score_data.get("matches", []),
            )
            all_scores.setdefault(qs_name, {})[tc_id] = score

    if not all_scores:
        print("No scored results found.")
        sys.exit(1)

    matrix = generate_matrix(all_scores)
    attribution = generate_thinker_attribution(all_scores)
    summary = generate_summary(all_scores)

    print("## Coverage Matrix\n")
    print(matrix)
    print("\n## Question Attribution\n")
    print(attribution)
    print("\n")
    print(summary)


def cmd_list_sets(args):
    """List available question sets."""
    print(f"{'Name':<20} {'Questions':>9}  Description")
    print("-" * 70)
    for name in sorted(QUESTION_SETS.keys()):
        qs = QUESTION_SETS[name]
        q_count = len(qs["questions"])
        desc = qs.get("description", "")
        print(f"{name:<20} {q_count:>9}  {desc}")


def cmd_list_cases(args):
    """List available test cases."""
    test_cases_dir = Path(__file__).parent / "test_cases"
    if not test_cases_dir.exists():
        print("No test_cases directory found.")
        return

    found = False
    for category_dir in sorted(test_cases_dir.iterdir()):
        if not category_dir.is_dir():
            continue

        for manifest_path in sorted(category_dir.glob("*.manifest.json")):
            found = True
            with open(manifest_path) as f:
                manifest = json.load(f)

            tc_id = manifest.get("id", "?")
            name = manifest.get("name", manifest_path.stem)
            artifact_file = manifest.get("artifact_file", "?")
            n_issues = len(manifest.get("planted_issues", []))
            difficulty = manifest.get("difficulty", "?")

            print(f"{tc_id:<6} {category_dir.name:<20} {name:<35} {artifact_file:<30} {n_issues} issues  {difficulty}")

    if not found:
        print("No test cases found.")


def main():
    parser = argparse.ArgumentParser(
        prog="harness",
        description="Skeptic detection effectiveness test harness",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # run
    run_parser = subparsers.add_parser("run", help="Run detection tests")
    run_parser.add_argument(
        "--sets", type=str, default=None,
        help="Comma-separated question set names (default: all)",
    )
    run_parser.add_argument(
        "--cases", type=str, default=None,
        help="Comma-separated test case IDs (default: all)",
    )
    run_parser.add_argument(
        "--runs", type=int, default=1,
        help="Number of runs per combination (default: 1)",
    )
    run_parser.set_defaults(func=cmd_run)

    # report
    report_parser = subparsers.add_parser("report", help="Generate report from previous run")
    report_parser.add_argument(
        "--run-dir", type=str, required=True,
        help="Path to run directory (e.g. harness/results/run_20240101_120000)",
    )
    report_parser.set_defaults(func=cmd_report)

    # list-sets
    list_sets_parser = subparsers.add_parser("list-sets", help="List available question sets")
    list_sets_parser.set_defaults(func=cmd_list_sets)

    # list-cases
    list_cases_parser = subparsers.add_parser("list-cases", help="List available test cases")
    list_cases_parser.set_defaults(func=cmd_list_cases)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
