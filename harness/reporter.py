"""Generate reports from scored harness runs."""

from harness.scorer import Score


def generate_matrix(all_scores: dict) -> str:
    """Generate coverage matrix as markdown table.

    Args:
        all_scores: Nested dict of {question_set_name: {test_case_id: Score}}.

    Returns:
        Markdown table string.

    Rows: question sets
    Columns: test cases + aggregate metrics (Precision, Recall, F1, Efficiency)
    Cells: TP/total planted issues
    """
    if not all_scores:
        return "No scores to report."

    # Collect all test case IDs
    test_case_ids: list[str] = sorted(
        {tc for scores in all_scores.values() for tc in scores}
    )
    question_set_names = sorted(all_scores.keys())

    # Header
    headers = ["Question Set"] + test_case_ids + ["Precision", "Recall", "F1", "Efficiency"]
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"

    rows = [header_line, separator]

    for qs_name in question_set_names:
        scores = all_scores[qs_name]
        row_cells = [qs_name]

        # Per-test-case TP counts
        total_tp = 0
        total_fp = 0
        total_fn = 0
        total_planted = 0

        for tc_id in test_case_ids:
            if tc_id in scores:
                s = scores[tc_id]
                planted = s.tp + s.fn
                total_planted += planted
                total_tp += s.tp
                total_fp += s.fp
                total_fn += s.fn
                row_cells.append(f"{s.tp}/{planted}")
            else:
                row_cells.append("-")

        # Aggregate metrics
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        # Efficiency: how many questions in the set
        from harness.question_sets import QUESTION_SETS
        q_count = len(QUESTION_SETS.get(qs_name, {}).get("questions", {}))
        efficiency = f1 / q_count if q_count > 0 else 0.0

        row_cells.extend([
            f"{precision:.2f}",
            f"{recall:.2f}",
            f"{f1:.2f}",
            f"{efficiency:.4f}",
        ])

        rows.append("| " + " | ".join(row_cells) + " |")

    return "\n".join(rows)


def generate_thinker_attribution(all_scores: dict) -> str:
    """Which question IDs contributed to TPs most often.

    Args:
        all_scores: Nested dict of {question_set_name: {test_case_id: Score}}.

    Returns:
        Markdown table of question IDs ranked by TP contribution.
    """
    qid_tp_count: dict[str, int] = {}
    qid_total_count: dict[str, int] = {}

    for qs_name, tc_scores in all_scores.items():
        for tc_id, score in tc_scores.items():
            for match in score.matches:
                if match["type"] == "TP":
                    # We need to look up which finding triggered this TP
                    # and get its triggered_by list. Since we only have
                    # match details, we store finding_id. The caller should
                    # pass richer data if available.
                    # For now, use the finding_id as a proxy and note
                    # that attribution requires the raw findings.
                    pass

    # Since detailed triggered_by info requires the raw findings,
    # we build attribution from all match details that include finding info
    for qs_name, tc_scores in all_scores.items():
        for tc_id, score in tc_scores.items():
            for match in score.matches:
                if match["type"] == "TP":
                    # Track the question set that contributed
                    qid_tp_count[qs_name] = qid_tp_count.get(qs_name, 0) + 1

    if not qid_tp_count:
        return "No true positives to attribute."

    # Sort by TP count descending
    ranked = sorted(qid_tp_count.items(), key=lambda x: x[1], reverse=True)

    lines = [
        "| Question Set | TP Contributions |",
        "| --- | --- |",
    ]
    for qid, count in ranked:
        lines.append(f"| {qid} | {count} |")

    return "\n".join(lines)


def generate_thinker_attribution_detailed(
    all_scores: dict, all_findings: dict
) -> str:
    """Detailed attribution: which question IDs contributed to TPs most often.

    Args:
        all_scores: Nested dict of {question_set_name: {test_case_id: Score}}.
        all_findings: Nested dict of {question_set_name: {test_case_id: [Finding]}}.

    Returns:
        Markdown table of question IDs ranked by TP contribution.
    """
    qid_tp_count: dict[str, int] = {}

    for qs_name, tc_scores in all_scores.items():
        for tc_id, score in tc_scores.items():
            findings = all_findings.get(qs_name, {}).get(tc_id, [])
            # Build finding lookup
            finding_map = {f.id: f for f in findings}

            for match in score.matches:
                if match["type"] == "TP":
                    finding_id = match.get("finding_id", "")
                    finding = finding_map.get(finding_id)
                    if finding:
                        for qid in finding.triggered_by:
                            qid_tp_count[qid] = qid_tp_count.get(qid, 0) + 1

    if not qid_tp_count:
        return "No true positives to attribute."

    ranked = sorted(qid_tp_count.items(), key=lambda x: x[1], reverse=True)

    lines = [
        "| Question ID | TP Contributions |",
        "| --- | --- |",
    ]
    for qid, count in ranked:
        lines.append(f"| {qid} | {count} |")

    return "\n".join(lines)


def generate_summary(all_scores: dict) -> str:
    """Overall summary with recommendations.

    Args:
        all_scores: Nested dict of {question_set_name: {test_case_id: Score}}.

    Returns:
        Markdown summary string.
    """
    if not all_scores:
        return "No results to summarize."

    lines = ["## Harness Run Summary", ""]

    # Aggregate stats per question set
    set_stats: list[tuple[str, float, float, float, int]] = []

    for qs_name in sorted(all_scores.keys()):
        tc_scores = all_scores[qs_name]
        total_tp = sum(s.tp for s in tc_scores.values())
        total_fp = sum(s.fp for s in tc_scores.values())
        total_fn = sum(s.fn for s in tc_scores.values())
        total_tn = sum(s.tn for s in tc_scores.values())

        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        set_stats.append((qs_name, precision, recall, f1, total_tp + total_fn))

    # Best F1
    if set_stats:
        best = max(set_stats, key=lambda x: x[3])
        lines.append(f"**Best overall F1**: `{best[0]}` with F1={best[3]:.2f} "
                      f"(P={best[1]:.2f}, R={best[2]:.2f})")
        lines.append("")

    # Sets with perfect recall
    perfect_recall = [s for s in set_stats if s[2] >= 1.0 and s[4] > 0]
    if perfect_recall:
        lines.append("**Perfect recall**:")
        for s in perfect_recall:
            lines.append(f"  - `{s[0]}` (P={s[1]:.2f}, F1={s[3]:.2f})")
        lines.append("")

    # Sets with zero recall
    zero_recall = [s for s in set_stats if s[2] == 0.0 and s[4] > 0]
    if zero_recall:
        lines.append("**Zero recall (missed everything)**:")
        for s in zero_recall:
            lines.append(f"  - `{s[0]}`")
        lines.append("")

    # Efficiency ranking
    from harness.question_sets import QUESTION_SETS
    efficiency_list = []
    for name, p, r, f1, total in set_stats:
        q_count = len(QUESTION_SETS.get(name, {}).get("questions", {}))
        eff = f1 / q_count if q_count > 0 else 0.0
        efficiency_list.append((name, eff, q_count, f1))

    efficiency_list.sort(key=lambda x: x[1], reverse=True)
    lines.append("**Efficiency ranking** (F1 / question count):")
    for name, eff, q_count, f1 in efficiency_list[:5]:
        lines.append(f"  - `{name}`: {eff:.4f} ({q_count} questions, F1={f1:.2f})")
    lines.append("")

    # Recommendations
    lines.append("### Recommendations")
    lines.append("")
    if best[3] < 0.5:
        lines.append("- Overall detection is weak. Consider expanding question coverage "
                      "or improving prompt quality.")
    if perfect_recall:
        high_precision_perfect = [s for s in perfect_recall if s[1] >= 0.8]
        if high_precision_perfect:
            lines.append(f"- `{high_precision_perfect[0][0]}` achieves high precision "
                          "with perfect recall. Consider as primary question set.")
    if efficiency_list:
        top_eff = efficiency_list[0]
        lines.append(f"- Most efficient set: `{top_eff[0]}` with only {top_eff[2]} questions.")

    return "\n".join(lines)
