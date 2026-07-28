"""Deterministic Target Task context-pressure experiment.

The fixture records observable file reads and bounded handoffs. It does not
pretend to measure model tokens or runtime context isolation.
"""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

HANDOFF_FIELDS = (
    "STATUS", "WORK_PERFORMED", "VALIDATED_FACTS",
    "DECISION_RELEVANT_FINDINGS", "LIMITATIONS", "UNRESOLVED",
    "ARTIFACT_REFERENCES", "RETRIEVAL_GUIDANCE", "READ_CONDITIONS",
    "NEXT_AUTHORIZED_ACTION",
)


class ReadLedger:
    def __init__(self) -> None:
        self.reads: list[str] = []
        self.focused: list[str] = []

    def read(self, path: Path) -> str:
        self.reads.append(path.name)
        return path.read_text(encoding="utf-8")

    def focused_extract(self, path: Path, needle: str, radius: int = 80) -> str:
        text = self.read(path)
        match = re.search(re.escape(needle), text, flags=re.IGNORECASE)
        if match is None:
            raise AssertionError(f"focused evidence not found: {needle}")
        self.focused.append(f"{path.name}:{needle}")
        return text[max(0, match.start() - radius):match.end() + radius]


def progressive_retrieve(source: str, query: str, budget: int) -> dict[str, tuple[str, ...]]:
    """Return headings then matching excerpts without reading beyond budget."""
    if budget < 1:
        raise ValueError("budget must be positive")
    headings = tuple(re.findall(r"^#{1,3} .+$", source, re.MULTILINE))
    terms = {term.lower() for term in re.findall(r"\w+", query) if len(term) > 2}
    sections = re.split(r"(?=^#{1,3} .+$)", source, flags=re.MULTILINE)
    excerpts = tuple(section.strip() for section in sections
                     if terms & set(re.findall(r"\w+", section.lower())))
    payload = headings + excerpts
    used = 0
    bounded: list[str] = []
    for item in payload:
        if used >= budget:
            break
        bounded.append(item[:budget - used])
        used += len(bounded[-1])
    return {"headings": tuple(headings), "excerpts": tuple(bounded)}


def sufficient_handoff(task_id: str, source_refs: tuple[str, ...], next_action: str) -> dict[str, Any]:
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


def _handoff(status: str, work: str, facts: tuple[str, ...], findings: tuple[str, ...],
             limitations: tuple[str, ...], unresolved: tuple[str, ...], refs: tuple[str, ...],
             guidance: str, conditions: str, next_action: str) -> dict[str, Any]:
    result = {
        "STATUS": status, "WORK_PERFORMED": work, "VALIDATED_FACTS": facts,
        "DECISION_RELEVANT_FINDINGS": findings, "LIMITATIONS": limitations,
        "UNRESOLVED": unresolved, "ARTIFACT_REFERENCES": refs,
        "RETRIEVAL_GUIDANCE": guidance, "READ_CONDITIONS": conditions,
        "NEXT_AUTHORIZED_ACTION": next_action,
    }
    if tuple(result) != HANDOFF_FIELDS:
        raise AssertionError("incomplete sufficient handoff")
    return result


def _baseline(root: Path) -> dict[str, Any]:
    files = sorted(root.glob("*.md"))
    contents = [path.read_text(encoding="utf-8") for path in files]
    return {"files_read": [path.name for path in files], "bytes": sum(map(len, contents))}


def run_context_pressure_experiment() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="target-task-pressure-") as raw:
        root = Path(raw)
        (root / "relevant.md").write_text(
            "# Relevant source\nworker report: green\n"
            "# Authoritative contradiction\nauthoritative value: blue\n"
            + ("context noise " * 1200), encoding="utf-8")
        (root / "irrelevant.md").write_text("# Irrelevant\n" + ("unrelated " * 5000), encoding="utf-8")
        (root / "validation.log").write_text("validation raw log\n" + ("trace " * 4000), encoding="utf-8")
        (root / "authority.md").write_text("# Authority\nrequired value is blue\n", encoding="utf-8")
        (root / "constraints.md").write_text("# Constraints\nno broad reads\n", encoding="utf-8")
        (root / "success.md").write_text("# Success\naccept only blue\n", encoding="utf-8")

        plan = {
            "task_id": "TT-CONTEXT-PRESSURE-001", "trigger": "TT:",
            "steps": ["S1-SUMMARIZE", "S2-RESOLVE", "S3-VALIDATE"],
            "worker_views": "hash-bound minimum sufficient context",
            "review": "DETERMINISTIC_ONLY",
        }
        plan_bytes = json.dumps(plan, sort_keys=True).encode()
        plan_hash = hashlib.sha256(plan_bytes).hexdigest()
        ledger = ReadLedger()

        # Brain receives the task and references only; Body retains this compact state.
        state = {"task_id": plan["task_id"], "plan_hash": plan_hash,
                 "current_step": "S1-SUMMARIZE", "context_status": "CONTEXT_ISOLATION_UNKNOWN"}
        authority = ledger.read(root / "authority.md")
        constraints = ledger.read(root / "constraints.md")
        success = ledger.read(root / "success.md")
        relevant_meta = ledger.read(root / "relevant.md")[:120]
        h1 = _handoff("PASS", "read small authoritative files and relevant metadata",
                      ("required value is blue", "no broad reads"),
                      ("worker report says green",), (), ("contradiction unresolved",),
                      ("relevant.md#Authoritative contradiction",),
                      "search exact 'authoritative value' and retrieve narrow context",
                      "retrieve only if worker claim conflicts with authority", "S2-RESOLVE")
        h1.update({"HANDOFF_SUFFICIENT": "NO", "MISSING": "authoritative value",
                   "RETRIEVE": "relevant.md#Authoritative contradiction",
                   "REASON": "worker claim conflicts with authority"})
        state["current_step"] = "S2-RESOLVE"

        # Recipient sufficiency is explicitly NO, then the exact contradiction is retrieved.
        sufficiency = {"HANDOFF_SUFFICIENT": "NO", "MISSING": "authoritative value",
                       "RETRIEVE": "relevant.md#Authoritative contradiction",
                       "REASON": "worker report conflicts with authoritative fact"}
        focused = ledger.focused_extract(root / "relevant.md", "authoritative value", radius=70)
        assert "blue" in focused
        h2 = _handoff("PASS", "focused retrieval of the contradiction only",
                      ("authoritative value is blue",), ("green is an unvalidated worker claim",),
                      (), (), ("relevant.md#Authoritative contradiction",),
                      "no further retrieval; retain source reference", "handoff now contains validated fact", "S3-VALIDATE")
        h2["HANDOFF_SUFFICIENT"] = "YES"
        state["current_step"] = "S3-VALIDATE"

        # Deterministic validation uses the authoritative small file, not raw output.
        validated = authority.strip().endswith("blue") and success.strip().endswith("blue")
        final_hash = hashlib.sha256(plan_bytes).hexdigest()
        state.update({"current_step": "COMPLETE", "accepted_claims": ["blue"],
                      "validation": "PASS", "plan_unchanged": final_hash == plan_hash})
        receipt = {"trigger": "TT:", "task_id": plan["task_id"], "plan_hash": plan_hash,
                   "planning_cycles": 1, "handoffs": 2, "review": "DETERMINISTIC_ONLY",
                   "status": "TARGET_TASK_ACCEPTED" if validated and state["plan_unchanged"] else "TARGET_TASK_REJECTED",
                   "context_status": state["context_status"]}
        baseline = _baseline(root)
        return {
            "status": receipt["status"], "receipt": receipt, "state": state,
            "plan_hash": plan_hash, "handoff_fields": HANDOFF_FIELDS,
            "handoffs": (h1, h2), "sufficiency": sufficiency,
            "files_read": tuple(ledger.reads), "focused_extractions": tuple(ledger.focused),
            "large_artifacts_not_read": tuple(name for name in ("irrelevant.md", "validation.log") if name not in ledger.reads),
            "handoff_sizes": (len(json.dumps(h1)), len(json.dumps(h2))),
            "body_state_size": len(json.dumps(state)), "worker_invocations": 2,
            "repeated_reads": len(ledger.reads) - len(set(ledger.reads)),
            "baseline": baseline, "relevant_meta_seen": relevant_meta,
        }


if __name__ == "__main__":
    print(json.dumps(run_context_pressure_experiment(), indent=2, sort_keys=True))
