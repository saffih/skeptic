"""Run question sets against test cases using the Anthropic API."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from harness.config import MODEL, TEMPERATURE, MAX_TOKENS, CONCURRENCY, API_KEY, RESULTS_DIR
from harness.prompt_builder import build_prompt
from harness.output_parser import parse_response, Finding
from harness.question_sets import QUESTION_SETS
from harness.scorer import score_findings, Score


async def run_single(
    question_set_name: str,
    test_case: dict,
    client,  # anthropic.AsyncAnthropic
    semaphore: asyncio.Semaphore,
) -> dict:
    """Run one question set against one test case.

    Args:
        question_set_name: Key into QUESTION_SETS.
        test_case: Dict with keys:
            - id: str
            - name: str
            - artifact_content: str
            - artifact_name: str
            - manifest: dict (ground truth for scoring)
        client: Anthropic async client.
        semaphore: Concurrency-limiting semaphore.

    Returns:
        Dict with raw response, parsed findings, and score.
    """
    question_set = QUESTION_SETS[question_set_name]
    artifact_content = test_case["artifact_content"]
    artifact_name = test_case["artifact_name"]

    system_prompt, user_prompt = build_prompt(
        question_set, artifact_content, artifact_name
    )

    async with semaphore:
        try:
            response = await client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            response_text = response.content[0].text
        except Exception as rate_err:
            import anthropic as _anthropic
            if not isinstance(rate_err, _anthropic.RateLimitError):
                raise
            # Back off and retry once
            await asyncio.sleep(5)
            try:
                response = await client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                response_text = response.content[0].text
            except Exception as e:
                return {
                    "question_set": question_set_name,
                    "test_case_id": test_case["id"],
                    "error": f"Rate limit retry failed: {e}",
                    "raw_response": "",
                    "findings": [],
                    "score": None,
                }
        except Exception as e:
            return {
                "question_set": question_set_name,
                "test_case_id": test_case["id"],
                "error": str(e),
                "raw_response": "",
                "findings": [],
                "score": None,
            }

    findings = parse_response(response_text)

    manifest = test_case.get("manifest", {})
    score = score_findings(findings, manifest) if manifest else None

    return {
        "question_set": question_set_name,
        "test_case_id": test_case["id"],
        "error": None,
        "raw_response": response_text,
        "findings": findings,
        "score": score,
    }


def _load_test_cases(test_case_ids: list[str] | None = None) -> list[dict]:
    """Load test cases from harness/test_cases/ directory.

    Layout: test_cases/<category>/tc01_name.ext + tc01_name.manifest.json
    The tc_id is extracted from the manifest filename (e.g. tc01 from tc01_bare_except.manifest.json).

    Args:
        test_case_ids: Optional list to filter by. If None, loads all.

    Returns:
        List of test case dicts.
    """
    test_cases_dir = Path(__file__).parent / "test_cases"
    if not test_cases_dir.exists():
        return []

    test_cases = []
    for category_dir in sorted(test_cases_dir.iterdir()):
        if not category_dir.is_dir():
            continue

        for manifest_path in sorted(category_dir.glob("*.manifest.json")):
            base_name = manifest_path.name.replace(".manifest.json", "")
            with open(manifest_path) as f:
                manifest = json.load(f)

            tc_id = manifest.get("id", base_name.split("_")[0])
            if test_case_ids and tc_id not in test_case_ids:
                continue

            artifact_file = manifest.get("artifact_file", "")
            artifact_path = category_dir / artifact_file
            if not artifact_path.exists():
                candidates = [
                    f for f in category_dir.iterdir()
                    if f.name.startswith(base_name) and not f.name.endswith(".manifest.json")
                ]
                if not candidates:
                    continue
                artifact_path = candidates[0]

            test_cases.append({
                "id": tc_id,
                "name": manifest.get("name", base_name),
                "artifact_content": artifact_path.read_text(),
                "artifact_name": artifact_path.name,
                "manifest": manifest,
            })

    return test_cases


async def run_all(
    question_set_names: list[str] | None = None,
    test_case_ids: list[str] | None = None,
    runs: int = 1,
) -> dict:
    """Run all combinations with concurrency control.

    Args:
        question_set_names: List of question set names. If None, uses all.
        test_case_ids: List of test case IDs. If None, uses all.
        runs: Number of repetitions per combination (for variance analysis).

    Returns:
        Dict with structure:
            {
                "run_dir": str,
                "results": {qs_name: {tc_id: [result_dict]}},
                "scores": {qs_name: {tc_id: Score}},
                "findings": {qs_name: {tc_id: [Finding]}},
            }
    """
    if question_set_names is None:
        question_set_names = list(QUESTION_SETS.keys())

    test_cases = _load_test_cases(test_case_ids)
    if not test_cases:
        print("No test cases found. Create test cases in harness/test_cases/")
        return {"run_dir": "", "results": {}, "scores": {}, "findings": {}}

    # Create run directory
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = RESULTS_DIR / f"run_{timestamp}"
    raw_dir = run_dir / "raw_responses"
    raw_dir.mkdir(parents=True, exist_ok=True)

    import anthropic
    client = anthropic.AsyncAnthropic(api_key=API_KEY)
    semaphore = asyncio.Semaphore(CONCURRENCY)

    # Build task list
    tasks = []
    for run_idx in range(runs):
        for qs_name in question_set_names:
            if qs_name not in QUESTION_SETS:
                print(f"Warning: unknown question set '{qs_name}', skipping.")
                continue
            for tc in test_cases:
                tasks.append((qs_name, tc, run_idx))

    total = len(tasks)
    print(f"Running {total} combinations ({len(question_set_names)} sets x "
          f"{len(test_cases)} cases x {runs} runs)...")

    # Execute
    async_tasks = []
    for qs_name, tc, run_idx in tasks:
        async_tasks.append(run_single(qs_name, tc, client, semaphore))

    results_list = await asyncio.gather(*async_tasks)

    # Organize results
    all_results: dict = {}
    all_scores: dict = {}
    all_findings: dict = {}

    for i, result in enumerate(results_list):
        qs_name = result["question_set"]
        tc_id = result["test_case_id"]

        # Store raw response
        raw_file = raw_dir / f"{qs_name}__{tc_id}__{i}.json"
        with open(raw_file, "w") as f:
            json.dump({
                "question_set": qs_name,
                "test_case_id": tc_id,
                "error": result["error"],
                "raw_response": result["raw_response"],
                "findings": [
                    {
                        "id": finding.id,
                        "description": finding.description,
                        "location": finding.location,
                        "classification": finding.classification,
                        "severity": finding.severity,
                        "triggered_by": finding.triggered_by,
                        "evidence": finding.evidence,
                        "confidence": finding.confidence,
                    }
                    for finding in result["findings"]
                ],
                "score": {
                    "tp": result["score"].tp,
                    "fp": result["score"].fp,
                    "fn": result["score"].fn,
                    "tn": result["score"].tn,
                    "precision": result["score"].precision,
                    "recall": result["score"].recall,
                    "f1": result["score"].f1,
                } if result["score"] else None,
            }, f, indent=2)

        # Aggregate (use last run's results for simplicity; multi-run analysis TBD)
        all_results.setdefault(qs_name, {})[tc_id] = result
        if result["score"]:
            all_scores.setdefault(qs_name, {})[tc_id] = result["score"]
        all_findings.setdefault(qs_name, {})[tc_id] = result["findings"]

    # Write summary
    from harness.reporter import generate_matrix, generate_summary, generate_thinker_attribution_detailed

    matrix = generate_matrix(all_scores)
    summary = generate_summary(all_scores)
    attribution = generate_thinker_attribution_detailed(all_scores, all_findings)

    report_path = run_dir / "report.md"
    with open(report_path, "w") as f:
        f.write("# Skeptic Harness Run Report\n\n")
        f.write(f"Timestamp: {timestamp}\n\n")
        f.write("## Coverage Matrix\n\n")
        f.write(matrix)
        f.write("\n\n")
        f.write("## Question Attribution\n\n")
        f.write(attribution)
        f.write("\n\n")
        f.write(summary)
        f.write("\n")

    print(f"\nResults saved to: {run_dir}")
    print(f"Report: {report_path}")

    return {
        "run_dir": str(run_dir),
        "results": all_results,
        "scores": all_scores,
        "findings": all_findings,
    }
