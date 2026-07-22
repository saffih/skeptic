"""Score findings against ground-truth manifests."""

from dataclasses import dataclass, field
from harness.output_parser import Finding


@dataclass
class Score:
    tp: int = 0       # true positives
    fp: int = 0       # false positives
    fn: int = 0       # false negatives
    tn: int = 0       # true negatives
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    matches: list[dict] = field(default_factory=list)  # detailed match info


def _keyword_overlap(finding: Finding, issue: dict) -> int:
    """Count keyword matches between a finding and a planted issue."""
    keywords = [kw.lower() for kw in issue.get("keywords", [])]
    if not keywords:
        return 0

    finding_text = " ".join([
        finding.description,
        finding.location,
        finding.evidence,
    ]).lower()

    return sum(1 for kw in keywords if kw in finding_text)


def _parse_line_range(text: str) -> set[int]:
    """Extract line numbers from text like 'lines 31-32', 'line 5', 'L5-L10'."""
    import re
    lines = set()
    for match in re.finditer(r"(?:lines?\s*|L|:)(\d+)(?:\s*[-–,]\s*(?:L)?(\d+))?", text):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        lines.update(range(start, end + 1))
    return lines


def _location_overlap(finding: Finding, issue: dict) -> bool:
    """Check if a finding's location overlaps with a planted issue's location."""
    issue_location = issue.get("location", "")
    if not issue_location:
        return False

    issue_lines = _parse_line_range(issue_location)
    if not issue_lines:
        return False

    finding_lines = _parse_line_range(finding.location)
    if not finding_lines:
        return False

    return bool(finding_lines & issue_lines)


def _matches_clean_area(finding: Finding, clean_area: dict) -> bool:
    """Check if a finding incorrectly flags a clean area."""
    area_location = clean_area.get("location", "")
    if area_location:
        area_lines = _parse_line_range(area_location)
        finding_lines = _parse_line_range(finding.location)
        if area_lines and finding_lines and (finding_lines & area_lines):
            return True

    area_keywords = [kw.lower() for kw in clean_area.get("keywords", [])]
    if area_keywords:
        finding_text = " ".join([
            finding.description, finding.location, finding.evidence,
        ]).lower()
        if sum(1 for kw in area_keywords if kw in finding_text) >= 2:
            return True

    return False


def score_findings(findings: list[Finding], manifest: dict) -> Score:
    """Score findings against manifest ground truth.

    Manifest structure:
        {
            "planted_issues": [
                {
                    "id": "PI1",
                    "description": "...",
                    "keywords": ["keyword1", "keyword2", ...],
                    "lines": [start, end],
                    "severity": "high|medium|low",
                }
            ],
            "clean_areas": [
                {
                    "id": "CA1",
                    "description": "...",
                    "keywords": ["keyword1", "keyword2", ...],
                }
            ]
        }

    Matching algorithm:
        1. For each planted issue, check if any finding matches by:
           - keyword overlap >= 2 keywords from the issue's keyword list
           - OR location overlap (same line range)
        2. A match is TP. Unmatched planted issue is FN.
        3. A finding that matches a clean_area is FP.
        4. A clean_area with no findings is TN.
    """
    planted_issues = manifest.get("planted_issues", [])
    clean_areas = manifest.get("clean_areas", [])

    # Filter to non-PASS findings for matching
    active_findings = [f for f in findings if f.classification != "PASS"]

    matched_issues: set[str] = set()
    matched_findings: set[str] = set()
    match_details: list[dict] = []

    # Step 1: Match findings to planted issues
    for issue in planted_issues:
        issue_id = issue.get("issue_id", issue.get("id", ""))
        for finding in active_findings:
            kw_count = _keyword_overlap(finding, issue)
            loc_match = _location_overlap(finding, issue)

            if kw_count >= 2 or loc_match:
                matched_issues.add(issue_id)
                matched_findings.add(finding.id)
                match_details.append({
                    "type": "TP",
                    "issue_id": issue_id,
                    "finding_id": finding.id,
                    "keyword_overlap": kw_count,
                    "location_overlap": loc_match,
                    "finding_description": finding.description,
                    "issue_description": issue.get("description", ""),
                })
                break  # One match per planted issue is sufficient

    tp = len(matched_issues)
    fn = len(planted_issues) - tp

    # Step 2: Check for false positives (findings matching clean areas)
    fp = 0
    flagged_clean: set[str] = set()
    for finding in active_findings:
        if finding.id in matched_findings:
            continue  # Already matched to a TP
        for area in clean_areas:
            area_id = area.get("area_id", area.get("id", ""))
            if _matches_clean_area(finding, area):
                fp += 1
                flagged_clean.add(area_id)
                match_details.append({
                    "type": "FP",
                    "finding_id": finding.id,
                    "clean_area_id": area_id,
                    "finding_description": finding.description,
                    "area_description": area.get("description", ""),
                })
                break

    # Step 3: True negatives (clean areas with no findings against them)
    tn = len(clean_areas) - len(flagged_clean)

    # Log FN details
    for issue in planted_issues:
        if issue.get("issue_id", issue.get("id", "")) not in matched_issues:
            match_details.append({
                "type": "FN",
                "issue_id": issue.get("issue_id", issue.get("id", "")),
                "issue_description": issue.get("description", ""),
            })

    # Compute metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return Score(
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn,
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
        matches=match_details,
    )
