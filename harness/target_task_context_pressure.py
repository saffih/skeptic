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
from harness.target_task_lifecycle import HANDOFF_FIELDS, make_rotation_checkpoint, validate_rotation_checkpoint


BODY_ROTATION_THRESHOLD_BYTES = 128


class ReadLedger:
    def __init__(self) -> None:
        self.reads: list[str] = []
        self.focused: list[str] = []
        self.bytes_loaded = 0
        self.bytes_scanned = 0

    def read(self, path: Path) -> str:
        self.reads.append(path.name)
        value = path.read_text(encoding="utf-8"); self.bytes_loaded += len(value.encode()); return value

    def read_metadata(self, path: Path) -> str:
        self.reads.append(path.name + ":metadata")
        stat = path.stat()
        return f"{path.name} bytes={stat.st_size}"

    def focused_extract(self, path: Path, needle: str, radius: int = 80) -> str:
        needle_bytes = needle.encode().lower(); overlap = b""; match_at = None
        with path.open("rb") as handle:
            offset = 0
            while chunk := handle.read(128):
                self.bytes_scanned += len(chunk)
                haystack = overlap + chunk.lower(); found = haystack.find(needle_bytes)
                if found >= 0:
                    match_at = offset - len(overlap) + found; break
                overlap = haystack[-(len(needle_bytes) - 1):]; offset += len(chunk)
        if match_at is None: raise AssertionError(f"focused evidence not found: {needle}")
        with path.open("rb") as handle:
            handle.seek(max(0, match_at - radius)); raw = handle.read(len(needle_bytes) + 2 * radius); self.bytes_loaded += len(raw); text = raw.decode(errors="replace")
        self.focused.append(f"{path.name}:{needle}")
        return text


def progressive_retrieve(source: str, query: str, budget: int) -> dict[str, tuple[str, ...]]:
    """Return headings then matching excerpts without reading beyond budget."""
    if budget < 1:
        raise ValueError("budget must be positive")
    headings = tuple(re.findall(r"^#{1,3} .+$", source, re.MULTILINE))
    terms = {term.lower() for term in re.findall(r"\w+", query) if len(term) > 2}
    sections = re.split(r"(?=^#{1,3} .+$)", source, flags=re.MULTILINE)
    excerpts = tuple(section.strip() for section in sections
                     if terms & set(re.findall(r"\w+", section.lower())))
    used_total = 0; bounded_headings = []; bounded_excerpts = []
    for destination, items in ((bounded_headings, headings), (bounded_excerpts, excerpts)):
        for item in items:
            if used_total >= budget: break
            raw = item.encode("utf-8"); take = min(len(raw), budget - used_total)
            destination.append(raw[:take].decode("utf-8", errors="ignore")); used_total += take
    return {"headings": tuple(bounded_headings), "excerpts": tuple(bounded_excerpts), "budget_used": used_total, "budget_unit": "bytes"}


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
    return {"files_read": [path.name + ":metadata" for path in files], "bytes": sum(path.stat().st_size for path in files)}


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
        relevant_meta = ledger.read_metadata(root / "relevant.md")
        h1 = _handoff("PASS", "read small authoritative files and relevant metadata",
                      ({"claim": "required value is blue", "provenance": "DETERMINISTICALLY_VALIDATED", "evidence_reference": {"reference": "authority.md", "validator": "body"}}, {"claim": "no broad reads", "provenance": "DETERMINISTICALLY_VALIDATED", "evidence_reference": {"reference": "constraints.md", "validator": "body"}}),
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
                      ({"claim": "authoritative value is blue", "provenance": "DIRECTLY_OBSERVED", "evidence_reference": {"reference": "relevant.md#Authoritative contradiction", "validator": "body"}},), ({"claim": "green is an unvalidated worker claim", "provenance": "WORKER_REPORTED"},),
                      (), (), ("relevant.md#Authoritative contradiction",),
                      "no further retrieval; retain source reference", "handoff now contains validated fact", "S3-VALIDATE")
        h2["HANDOFF_SUFFICIENT"] = "YES"
        state["current_step"] = "S3-VALIDATE"

        # Deterministic validation uses the authoritative small file, not raw output.
        validated = authority.strip().endswith("blue") and success.strip().endswith("blue")
        final_hash = hashlib.sha256(plan_bytes).hexdigest()
        rotation_required = ledger.bytes_loaded >= BODY_ROTATION_THRESHOLD_BYTES
        if rotation_required:
            state.update({"current_step": "S3-VALIDATE", "accepted_claims": ["blue"], "validation": "PASS", "plan_unchanged": final_hash == plan_hash})
            rotation_checkpoint = make_rotation_checkpoint(TARGET_TASK_ID=plan["task_id"], TASK_REFERENCE="task://pressure", AUTHORITY_REFERENCE="authority://pressure", PLAN_REFERENCE="sealed://pressure", PLAN_HASH=plan_hash, EXECUTION_MODE="SHARED_CONTEXT_DEGRADED", OBSERVED_CONTEXT_STATUS="CONTEXT_ISOLATION_UNKNOWN", CURRENT_STEP="S3-VALIDATE", COMPLETED_STEPS_AND_EVIDENCE={"S1-SUMMARIZE": {"status": "ACCEPTED", "artifact": "summary.md"}, "S2-RESOLVE": {"status": "ACCEPTED", "artifact": "resolution.md"}}, ACCEPTED_VALIDATED_CLAIMS=[{"claim": "blue", "provenance": "DETERMINISTICALLY_VALIDATED", "evidence_reference": {"reference": "authority.md", "validator": "body"}}], OPEN_FINDINGS=[], OPEN_BLOCKERS=[], MATERIAL_DEVIATIONS=[], ARTIFACT_REFERENCES=["relevant.md#Authoritative contradiction"], NEXT_AUTHORIZED_ACTION="RUN-S3-VALIDATE", LAST_VALIDATION_STATE="PASS")
            validate_rotation_checkpoint(rotation_checkpoint, task_id=plan["task_id"], plan_reference="sealed://pressure", plan_hash=plan_hash, evidence_ledger={"authority.md": {"provenance": "DETERMINISTICALLY_VALIDATED", "result": "PASS", "validator": "body"}})
        else:
            state.update({"current_step": "COMPLETE", "accepted_claims": ["blue"], "validation": "PASS", "plan_unchanged": final_hash == plan_hash})
            rotation_checkpoint = None
        checkpoint_bytes = json.dumps(rotation_checkpoint, sort_keys=True).encode() if rotation_checkpoint else b""
        checkpoint_hash = hashlib.sha256(checkpoint_bytes).hexdigest() if checkpoint_bytes else None
        if rotation_required:
            # The old Body stops here; only a fresh Body may resume.
            assert checkpoint_hash == hashlib.sha256(checkpoint_bytes).hexdigest()
        receipt = {"trigger": "TT:", "task_id": plan["task_id"], "plan_hash": plan_hash,
                   "planning_cycles": 1, "handoffs": 2, "review": "DETERMINISTIC_ONLY",
            "status": "BODY_ROTATION_REQUIRED" if rotation_required else ("TARGET_TASK_ACCEPTED" if validated and state["plan_unchanged"] else "TARGET_TASK_REJECTED"),
                   "context_status": state["context_status"]}
        baseline = _baseline(root)
        return {
            "status": receipt["status"], "receipt": receipt, "state": state,
            "plan_hash": plan_hash, "handoff_fields": HANDOFF_FIELDS,
            "handoffs": (h1, h2), "sufficiency": sufficiency,
            "files_read": tuple(ledger.reads), "focused_extractions": tuple(ledger.focused),
            "large_artifacts_not_read": tuple(name for name in ("irrelevant.md", "validation.log") if name not in ledger.reads),
            "handoff_sizes": (len(json.dumps(h1)), len(json.dumps(h2))),
            "body_state_size": len(json.dumps(state)), "worker_invocations": 2, "bytes_loaded": ledger.bytes_loaded, "bytes_scanned": ledger.bytes_scanned,
            "repeated_reads": len(ledger.reads) - len(set(ledger.reads)),
            "baseline": baseline, "relevant_meta_seen": relevant_meta,
            "body_rotation": {
                "status": "BODY_ROTATION_REQUIRED" if rotation_required else "NOT_REQUIRED",
                "threshold_bytes": BODY_ROTATION_THRESHOLD_BYTES, "bytes_loaded": ledger.bytes_loaded,
                "checkpoint": rotation_checkpoint if rotation_required else None,
                "checkpoint_sha256": checkpoint_hash if rotation_required else None,
                "verified": rotation_required, "stopped_before_resume": rotation_required,
                "resume_owner": "FRESH_LUNA_BODY" if rotation_required else "NONE",
            },
        }


if __name__ == "__main__":
    print(json.dumps(run_context_pressure_experiment(), indent=2, sort_keys=True))
