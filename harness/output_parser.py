"""Parse LLM responses into structured Finding objects."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Finding:
    id: str
    description: str
    location: str
    classification: str  # ACTION, CONFLICT, PASS
    severity: str  # high, medium, low
    triggered_by: list[str] = field(default_factory=list)  # question IDs
    evidence: str = ""
    confidence: str = "medium"  # high, medium, low


def parse_response(response_text: str) -> list[Finding]:
    """Parse LLM response into Finding objects.

    Try JSON first, fall back to regex extraction.
    """
    findings = _try_json_parse(response_text)
    if findings is not None:
        return findings

    return _regex_fallback(response_text)


def _try_json_parse(text: str) -> list[Finding] | None:
    """Attempt to parse response as JSON."""
    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove opening fence (with optional language tag)
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        # Remove closing fence
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find a JSON object embedded in the text
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if not match:
            return None
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return None

    if not isinstance(data, dict):
        return None

    raw_findings = data.get("findings", [])
    if not isinstance(raw_findings, list):
        return None

    findings = []
    for item in raw_findings:
        if not isinstance(item, dict):
            continue
        try:
            finding = Finding(
                id=str(item.get("id", f"F{len(findings) + 1}")),
                description=str(item.get("description", "")),
                location=str(item.get("location", "")),
                classification=str(item.get("classification", "PASS")).upper(),
                severity=str(item.get("severity", "medium")).lower(),
                triggered_by=_ensure_str_list(item.get("triggered_by", [])),
                evidence=str(item.get("evidence", "")),
                confidence=str(item.get("confidence", "medium")).lower(),
            )
            findings.append(finding)
        except (TypeError, ValueError):
            continue

    return findings


def _regex_fallback(text: str) -> list[Finding]:
    """Extract findings from unstructured text using regex patterns."""
    findings = []

    # Pattern: look for finding-like blocks with IDs
    # Match blocks that start with F<number> or Finding <number>
    blocks = re.split(r"(?=\bF\d+\b|(?:Finding\s+\d+))", text)

    for block in blocks:
        if not block.strip():
            continue

        # Extract ID
        id_match = re.match(r"(F\d+)", block)
        if not id_match:
            continue

        finding_id = id_match.group(1)

        # Extract description: first sentence or line after ID
        desc_match = re.search(
            r"(?:description|desc)[:\s]*(.+?)(?:\n|$)", block, re.IGNORECASE
        )
        description = desc_match.group(1).strip() if desc_match else ""
        if not description:
            # Take first substantial line after ID
            lines = block.split("\n")
            for line in lines[1:]:
                line = line.strip()
                if len(line) > 10:
                    description = line
                    break

        # Extract location
        loc_match = re.search(
            r"(?:location|loc|line|at)[:\s]*(.+?)(?:\n|$)", block, re.IGNORECASE
        )
        location = loc_match.group(1).strip() if loc_match else ""

        # Extract classification
        class_match = re.search(
            r"\b(ACTION|CONFLICT|PASS)\b", block, re.IGNORECASE
        )
        classification = class_match.group(1).upper() if class_match else "ACTION"

        # Extract severity
        sev_match = re.search(r"\b(high|medium|low)\b", block, re.IGNORECASE)
        severity = sev_match.group(1).lower() if sev_match else "medium"

        # Extract triggered_by question IDs
        triggered = re.findall(
            r"\b([A-Z]{2,3}\d+)\b", block
        )
        # Filter to known prefixes
        known_prefixes = (
            "UQ", "CH", "OM", "FE", "PO", "KT", "SH",
            "ST", "SEC", "CPX", "REL", "DAT", "ARC", "CFT",
        )
        triggered = [
            t for t in triggered
            if any(t.startswith(p) for p in known_prefixes)
        ]

        # Extract evidence
        ev_match = re.search(
            r"(?:evidence)[:\s]*(.+?)(?:\n\n|\n[A-Z]|$)",
            block, re.IGNORECASE | re.DOTALL,
        )
        evidence = ev_match.group(1).strip() if ev_match else ""

        # Extract confidence
        conf_match = re.search(
            r"(?:confidence)[:\s]*(high|medium|low)", block, re.IGNORECASE
        )
        confidence = conf_match.group(1).lower() if conf_match else "medium"

        findings.append(
            Finding(
                id=finding_id,
                description=description,
                location=location,
                classification=classification,
                severity=severity,
                triggered_by=triggered,
                evidence=evidence,
                confidence=confidence,
            )
        )

    return findings


def _ensure_str_list(value) -> list[str]:
    """Ensure value is a list of strings."""
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        return [value]
    return []
