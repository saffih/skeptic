"""Small domain-blind runtime for the Task Prompt workflow."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping


class TPResultError(ValueError):
    """A compact control envelope was malformed or incompatible."""


@dataclass(frozen=True)
class DispatchOutcome:
    """Only observable transport facts; provider diagnoses remain transport-owned."""

    launched: bool
    worker_started: bool
    result_text: str | None = None
    error: str | None = None


HostAdapter = Callable[[str, str, Mapping[str, str]], DispatchOutcome]
MAX_CONTROL_REASON_LENGTH = 240


def _fields(text: str, expected: set[str]) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "TP_RESULT":
        raise TPResultError("MALFORMED_ENVELOPE")
    values: dict[str, str] = {}
    for line in lines[1:]:
        if not line or ": " not in line:
            raise TPResultError("MALFORMED_ENVELOPE")
        key, value = line.split(": ", 1)
        if key not in expected or key in values or not value.strip():
            raise TPResultError("MALFORMED_ENVELOPE")
        values[key] = value.strip()
    if set(values) != expected:
        raise TPResultError("MISSING_OR_UNEXPECTED_FIELD")
    return values


def _compact_reason(values: Mapping[str, str]) -> None:
    if len(values["reason"]) > MAX_CONTROL_REASON_LENGTH:
        raise TPResultError("CONTROL_REASON_TOO_LONG")


def parse_brain_result(text: str, *, run_root: Path) -> dict[str, object]:
    values = _fields(text, {"role", "status", "route", "next", "blocks", "result_ref", "reason"})
    _compact_reason(values)
    if values["role"] != "BRAIN" or values["status"] not in {"CONTINUE", "COMPLETE", "BLOCKED", "CONFLICT"}:
        raise TPResultError("BRAIN_ROLE_OR_STATUS")
    if values["status"] == "CONTINUE":
        if values["next"] == "SEQUENCE":
            if values["route"] not in {"LOW", "MEDIUM", "STRONG"} or values["blocks"] == "NONE" or values["result_ref"] != "NONE":
                raise TPResultError("BRAIN_SEQUENCE_SHAPE")
            blocks = tuple(part.strip() for part in values["blocks"].split(","))
            if not all(blocks) or len(set(blocks)) != len(blocks):
                raise TPResultError("BRAIN_BLOCKS")
            for block_ref in blocks:
                _resolve(run_root, block_ref)
        elif values["next"] == "BRAIN":
            if values["route"] != "STRONG" or values["blocks"] != "NONE":
                raise TPResultError("BRAIN_ESCALATION_SHAPE")
            _resolve(run_root, values["result_ref"])
            blocks = ()
        else:
            raise TPResultError("BRAIN_CONTINUE_SHAPE")
    else:
        if values["route"] != "NONE" or values["next"] != "NONE" or values["blocks"] != "NONE":
            raise TPResultError("BRAIN_TERMINAL_SHAPE")
        if values["result_ref"] != "NONE":
            _resolve(run_root, values["result_ref"])
        blocks = ()
    return {**values, "blocks": blocks}


def _resolve(run_root: Path, reference: str) -> Path:
    if reference == "NONE":
        raise TPResultError("RESULT_REF_NONE")
    candidate = (run_root / reference).resolve()
    artifacts = (run_root / "artifacts").resolve()
    if os.path.commonpath((str(artifacts), str(candidate))) != str(artifacts) or not candidate.is_file():
        raise TPResultError("RESULT_REF_UNRESOLVABLE")
    return candidate


def parse_block_result(text: str, *, assigned_block_ref: str, run_root: Path) -> dict[str, str]:
    values = _fields(text, {"role", "status", "block_ref", "result_ref", "reason"})
    _compact_reason(values)
    if values["role"] != "BLOCK" or values["status"] not in {"DONE", "BLOCKED", "CONFLICT"}:
        raise TPResultError("BLOCK_ROLE_OR_STATUS")
    if values["block_ref"] != assigned_block_ref:
        raise TPResultError("BLOCK_REF_MISMATCH")
    _resolve(run_root, values["result_ref"])
    return values


def _git_head(repository_root: Path) -> str | None:
    result = subprocess.run(["git", "-C", str(repository_root), "rev-parse", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


class TPRuntime:
    def __init__(self, repository_root: Path | str, mission: str, adapter: HostAdapter, *, runtime_base: Path | str | None = None) -> None:
        self.repository_root = Path(repository_root).resolve()
        if not self.repository_root.is_dir() or not mission.strip():
            raise ValueError("repository root and nonblank mission are required")
        base = Path(runtime_base) if runtime_base is not None else Path(tempfile.gettempdir()) / "skeptic-tp"
        identity = hashlib.sha256(str(self.repository_root).encode()).hexdigest()[:16]
        self.run_root = (base / identity / uuid.uuid4().hex).resolve()
        if os.path.commonpath((str(self.repository_root), str(self.run_root))) == str(self.repository_root):
            raise ValueError("runtime root must be outside target repository")
        self.adapter, self.mission = adapter, mission
        self.run_root.mkdir(parents=True)
        (self.run_root / "artifacts").mkdir()
        (self.run_root / "mission.md").write_text(mission, encoding="utf-8")
        (self.run_root / "repository.json").write_text(json.dumps({"repository_root": str(self.repository_root), "git_head": _git_head(self.repository_root)}, sort_keys=True) + "\n", encoding="utf-8")
        self.event("RUN_CREATED", host=platform.system())

    def event(self, event: str, **fields: object) -> None:
        with (self.run_root / "events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"event": event, **fields}, sort_keys=True) + "\n")

    def _packet(self, *, condition: str = "NORMAL", result_ref: str | None = None) -> dict[str, str]:
        packet = {"run_ref": str(self.run_root), "mission_ref": str(self.run_root / "mission.md"), "condition": condition}
        if result_ref is not None:
            packet["result_ref"] = result_ref
        return packet

    def _dispatch(self, role: str, route: str, packet: Mapping[str, str]) -> DispatchOutcome:
        self.event("DISPATCH_ADMITTED", role=role, route=route)
        outcome = self.adapter(role, route, packet)
        if not outcome.launched:
            self.event("DISPATCH_REJECTED_BEFORE_START", role=role, error=outcome.error or "UNKNOWN")
        elif not outcome.worker_started:
            self.event("DISPATCH_REJECTED_BEFORE_WORKER", role=role, error=outcome.error or "UNKNOWN")
        elif outcome.result_text is None:
            self.event("WORKER_FAILED_AFTER_START", role=role, error=outcome.error or "UNKNOWN")
        return outcome

    def run(self) -> str:
        condition, route, handoff_result_ref = "NORMAL", "MEDIUM", None
        while True:
            brain = self._dispatch("BRAIN", route, self._packet(condition=condition, result_ref=handoff_result_ref))
            handoff_result_ref = None
            if not brain.launched or not brain.worker_started or brain.result_text is None:
                self.event("BRAIN_CONTROL_UNAVAILABLE", condition=condition)
                return "BRAIN_UNAVAILABLE"
            try:
                decision = parse_brain_result(brain.result_text, run_root=self.run_root)
            except TPResultError as exc:
                self.event("BRAIN_RESULT_INVALID", error=str(exc))
                return "BRAIN_REQUIRED"
            self.event("BRAIN_RETURN_VALID", status=decision["status"], result_ref=decision["result_ref"])
            if decision["status"] != "CONTINUE":
                self.event("TERMINAL_BRAIN_OUTCOME", status=decision["status"])
                return str(decision["status"])
            if decision["next"] == "BRAIN":
                self.event("BRAIN_ESCALATION", result_ref=decision["result_ref"])
                condition, route, handoff_result_ref = "BRAIN_ESCALATION", str(decision["route"]), str(decision["result_ref"])
                continue
            for block_ref in decision["blocks"]:
                block = self._dispatch("BLOCK", str(decision["route"]), {**self._packet(condition="BLOCK_ASSIGNED"), "block_ref": str(block_ref)})
                if not block.launched or not block.worker_started or block.result_text is None:
                    self.event("BLOCK_CONTROL_TO_BRAIN", block_ref=block_ref, condition="ADMISSION_OR_WORKER_FAILURE")
                    condition, route = "BLOCK_ADMISSION_OR_WORKER_FAILURE", "MEDIUM"
                    break
                try:
                    result = parse_block_result(block.result_text, assigned_block_ref=str(block_ref), run_root=self.run_root)
                except TPResultError as exc:
                    self.event("BLOCK_RESULT_INVALID", block_ref=block_ref, error=str(exc))
                    self.event("BLOCK_CONTROL_TO_BRAIN", block_ref=block_ref, condition="INVALID_RETURN")
                    condition, route = "INVALID_BLOCK_RETURN", "MEDIUM"
                    break
                self.event("BLOCK_RETURN_VALID", block_ref=block_ref, status=result["status"], result_ref=result["result_ref"])
                if result["status"] != "DONE":
                    self.event("BLOCK_CONTROL_TO_BRAIN", block_ref=block_ref, condition=result["status"])
                    condition, route = "BLOCK_" + result["status"], "MEDIUM"
                    break
            else:
                self.event("SEQUENCE_EXHAUSTED")
                condition, route = "SEQUENCE_EXHAUSTED", "MEDIUM"
                continue
            continue
