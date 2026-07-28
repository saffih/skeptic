"""Small deterministic probe for progressive Target Task retrieval.

This is a behavioral contract probe, not a model benchmark. It verifies that
retrieval narrows under a byte budget and that a sufficient handoff carries
references and state rather than copied source content.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Retrieval:
    headings: tuple[str, ...]
    excerpts: tuple[str, ...]


def progressive_retrieve(source: str, query: str, budget: int) -> Retrieval:
    if budget < 1:
        raise ValueError("budget must be positive")
    headings = tuple(re.findall(r"^#{1,3} .+$", source, re.MULTILINE))
    sections = re.split(r"(?=^#{1,3} .+$)", source, flags=re.MULTILINE)
    terms = {term.lower() for term in re.findall(r"\w+", query) if len(term) > 2}
    matches = [section.strip() for section in sections if terms & set(re.findall(r"\w+", section.lower()))]
    excerpts: list[str] = []
    used = sum(len(item) for item in headings)
    for section in matches:
        remaining = budget - used
        if remaining <= 0:
            break
        excerpt = section[:remaining]
        excerpts.append(excerpt)
        used += len(excerpt)
    return Retrieval(headings=headings, excerpts=tuple(excerpts))


def sufficient_handoff(task_id: str, source_refs: tuple[str, ...], next_action: str) -> dict[str, object]:
    return {
        "task_id": task_id,
        "source_refs": source_refs,
        "candidate_identity": "NONE",
        "completed_steps": ("retrieval",),
        "open_findings": (),
        "next_action": next_action,
        "constraints": ("no broad discovery",),
        "context_status": "CONTEXT_ISOLATION_UNKNOWN",
    }
