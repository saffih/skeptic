"""Deterministic recognition of `TT:` and task initialization.

Required because a Target Task needs exactly one unambiguous entrypoint: a
literal `TT:` prefix, with everything after it treated as the immutable
mission, never parsed, summarized, or paraphrased. Bootstrap then creates
the task's external workspace atomically — a crash mid-bootstrap must never
leave a half-created task root that anything downstream could mistake for
authoritative.

`resume_task` is the interruption/resume path: a thin re-export of
`capabilities.restart_admission.admit_restart`, which already implements
validated, non-executing admission of one immutable checkpoint into a fresh
process. It is not reimplemented here.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from capabilities.restart_admission.restart_admission import admit_restart
from concepts.target_task.contracts import LedgerEvent, LunaAction, Phase
from concepts.target_task.store import AppendOnlyLedger, write_immutable_artifact

TRIGGER_PREFIX = "TT:"


class TriggerError(ValueError):
    pass


def parse_trigger(message: str) -> str | None:
    """Return the mission text if `message` starts with the exact `TT:`
    prefix; `None` if it is a different message entirely (not a Target
    Task); raise if the prefix is present but the mission is empty."""
    stripped = message.lstrip()
    if not stripped.startswith(TRIGGER_PREFIX):
        return None
    mission = stripped[len(TRIGGER_PREFIX):].strip()
    if not mission:
        raise TriggerError("EMPTY_MISSION")
    return mission


@dataclass(frozen=True)
class BootstrapResult:
    task_id: str
    workspace_root: Path
    mission_reference_id: str
    mission_sha256: str
    mission_byte_size: int
    ledger_head_hash: str


def bootstrap_task(mission: str, task_id: str, tasks_root: Path) -> BootstrapResult:
    """Persist the exact mission, create the initial ledger event, and
    atomically publish the complete task workspace. Never returns or logs
    the mission body itself — only a compact result referencing it."""
    tasks_root = Path(tasks_root).resolve()
    final_dir = tasks_root / task_id
    if final_dir.exists():
        raise TriggerError("TASK_ALREADY_EXISTS")
    tmp_dir = tasks_root / f".{task_id}.bootstrap.tmp"
    if tmp_dir.exists():
        raise TriggerError("BOOTSTRAP_TMP_EXISTS")
    tmp_dir.mkdir(parents=True)
    try:
        mission_ref = write_immutable_artifact(
            tmp_dir,
            "mission.md",
            mission.encode("utf-8"),
            reference_id="mission",
            artifact_type="mission",
            description="immutable Target Task mission",
            read_condition="read once at Planner dispatch",
        )
        ledger = AppendOnlyLedger(tmp_dir / "ledger.jsonl")
        first_event = LedgerEvent(
            schema_version="1",
            sequence=0,
            event_id=f"{task_id}-bootstrap",
            task_id=task_id,
            phase=Phase.MISSION_PERSISTED.value,
            accepted_plan_ref=None,
            current_step=None,
            operation_id=None,
            attempt=1,
            request_ref=None,
            result_ref="mission.md",
            status="COMPLETE",
            validation="PASS",
            blocker=None,
            allowed_actions=(LunaAction.CONTINUE.value, LunaAction.STOP.value),
            next_action=LunaAction.CONTINUE.value,
            previous_event_hash=None,
            receipt_ref=None,
        )
        append_result = ledger.append(first_event)
    except BaseException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    # Same-parent-directory rename is atomic on a POSIX filesystem: until
    # this line, nothing observes `final_dir`, so a crash before it leaves
    # only an orphaned `.{task_id}.bootstrap.tmp` directory, never a
    # half-created authoritative task.
    os.rename(tmp_dir, final_dir)
    return BootstrapResult(
        task_id=task_id,
        workspace_root=final_dir,
        mission_reference_id=mission_ref["reference_id"],
        mission_sha256=mission_ref["sha256"],
        mission_byte_size=mission_ref["byte_size"],
        ledger_head_hash=append_result.head_hash,
    )


def resume_task(checkpoint_request_raw: bytes, *, repository_root: Path | str, workspace_root: Path | str) -> dict[str, Any]:
    """Admit one validated checkpoint into a fresh process after
    interruption. See `capabilities.restart_admission.restart_admission`
    for the complete contract; this is intentionally not reimplemented."""
    return admit_restart(checkpoint_request_raw, repository_root=repository_root, workspace_root=workspace_root)
