from __future__ import annotations

import os
import selectors
import signal
import stat
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from .boundary import discover_nested_repositories, scope_overlaps_nested
from .canonical import ensure_no_symlink_components, safe_relpath, sha256_file
from .errors import STTError, require


def _tool(catalog: dict[str, Any], tool_id: str) -> dict[str, Any]:
    matches = [entry for entry in catalog["tools"] if entry["tool_id"] == tool_id]
    require(len(matches) == 1, "TOOLCHAIN_INVALID", f"tool catalog mismatch: {tool_id}")
    entry = matches[0]
    path = Path(entry["path"])
    st = path.stat()
    require(
        sha256_file(path) == entry["sha256"]
        and st.st_dev == entry["device"]
        and st.st_ino == entry["inode"],
        "TOOLCHAIN_DRIFT",
        f"tool drift: {tool_id}",
    )
    return entry


def sandbox_backend(catalog: dict[str, Any]) -> str | None:
    tool_ids = {entry["tool_id"] for entry in catalog.get("tools", [])}
    if sys.platform.startswith("linux") and {"unshare", "mount", "python"} <= tool_ids:
        return "linux-unshare"
    return None


def run_command(
    *,
    candidate: Path,
    command: dict[str, Any],
    catalog: dict[str, Any],
    logs_dir: Path,
    mode: str,
    max_log_bytes: int,
    max_scratch_bytes: int = 268435456,
    max_processes: int = 256,
    max_address_space_bytes: int = 4294967296,
) -> dict[str, Any]:
    # Dynamic commands may reach the shared workspace only through a ready
    # sandbox. Reject compatibility and unknown modes before any launch setup.
    if mode == "owner_risk_accepted":
        raise STTError(
            "UNCONFINED_SHARED_WORKSPACE_EXECUTION_UNSUPPORTED",
            "Unconfined command execution is unsupported because STT operates directly on the shared workspace. Dynamic commands require a successfully initialized sandbox.",
        )
    if mode != "sandbox_required":
        raise STTError("DYNAMIC_VALIDATION_AUTHORIZATION_REQUIRED", "unknown dynamic execution mode")

    candidate = candidate.resolve(strict=True)
    ensure_no_symlink_components(candidate)
    candidate_state = candidate / ".stt"
    if candidate_state.exists() or candidate_state.is_symlink():
        state_value = os.lstat(candidate_state)
        require(stat.S_ISDIR(state_value.st_mode) and not stat.S_ISLNK(state_value.st_mode), "STT_CONTROL_PATH_UNSAFE", "workspace .stt must be a real directory before sandboxing")
    cwd_rel = safe_relpath(command["cwd"], allow_dot=True)
    nested_roots = tuple(discover_nested_repositories(candidate))
    if cwd_rel != ".":
        overlap = scope_overlaps_nested(cwd_rel, nested_roots)
        require(overlap is None, "NESTED_REPOSITORY_SCOPE_FORBIDDEN", "command working directory overlaps nested repository", cwd=cwd_rel, nested_root=overlap)
    cwd_target = candidate if cwd_rel == "." else candidate / cwd_rel
    ensure_no_symlink_components(cwd_target)
    require(cwd_target.is_dir() and not cwd_target.is_symlink(), "COMMAND_CWD_INVALID", "command working directory must be a real directory")
    entry = _tool(catalog, command["tool_id"])
    logs_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    op = uuid.uuid4().hex
    stdout_path, stderr_path = logs_dir / f"{op}.stdout", logs_dir / f"{op}.stderr"
    scratch = logs_dir / f"{op}.scratch"
    scratch.mkdir(mode=0o700)
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(scratch / "home"),
        "TMPDIR": str(scratch / "tmp"),
        "LANG": "C",
        "LC_ALL": "C",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_OPTIONAL_LOCKS": "0",
    }
    Path(env["HOME"]).mkdir()
    Path(env["TMPDIR"]).mkdir()
    cwd = cwd_target

    backend = sandbox_backend(catalog)
    readiness_read, readiness_write = os.pipe()
    os.set_blocking(readiness_read, False)
    if backend == "linux-unshare":
        unshare = _tool(catalog, "unshare")["path"]
        mount = _tool(catalog, "mount")["path"]
        python = _tool(catalog, "python")["path"]
        sandbox_root = scratch / "root"
        argv = [
            unshare,
            "--user",
            "--map-root-user",
            "--mount",
            "--net",
            "--pid",
            "--fork",
            python,
            str(Path(__file__).with_name("sandbox_child.py")),
            "--readiness-fd",
            str(readiness_write),
            "--root",
            str(sandbox_root),
            "--candidate",
            str(candidate),
            "--scratch",
            str(scratch),
            "--mount",
            mount,
            "--tool",
            entry["path"],
            "--cwd",
            command["cwd"],
            "--timeout-seconds",
            str(command["timeout_seconds"]),
            "--scratch-bytes",
            str(max_scratch_bytes),
            "--max-processes",
            str(max_processes),
            "--address-space-bytes",
            str(max_address_space_bytes),
            "--",
            *command["args"],
        ]
        cwd = candidate
    else:
        os.close(readiness_read)
        os.close(readiness_write)
        raise STTError(
            "HOST_CAPABILITY_UNAVAILABLE",
            "sandbox_required but no supported sandbox backend is available",
            {"supported_backends": ["linux-unshare"], "macos": "disabled_unqualified"},
        )
    try:
        process = subprocess.Popen(
            argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True,
            pass_fds=() if readiness_write is None else (readiness_write,),
        )
    except OSError as exc:
        if readiness_read is not None:
            os.close(readiness_read)
            os.close(readiness_write)
        return {
            "outer_status": "COMPLETE", "result_status": "SANDBOX_SETUP_FAILED",
            "sandbox_backend": backend,
            "reason": "SANDBOX_LAUNCH_FAILED", "reason_detail": type(exc).__name__,
            "operation_id": op,
        }
    if readiness_write is not None:
        os.close(readiness_write)
    assert process.stdout and process.stderr
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ, "stdout")
    selector.register(process.stderr, selectors.EVENT_READ, "stderr")
    if readiness_read is not None:
        selector.register(readiness_read, selectors.EVENT_READ, "readiness")
    outputs = {"stdout": stdout_path.open("xb"), "stderr": stderr_path.open("xb")}
    accepted = 0
    limit_hit = False
    deadline = time.monotonic() + command["timeout_seconds"]
    timed_out = False
    sandbox_ready = False
    readiness = b""
    try:
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                os.killpg(process.pid, signal.SIGTERM)
                break
            for key, _ in selector.select(min(0.2, remaining)):
                chunk = os.read(key.fileobj, 65536) if key.data == "readiness" else key.fileobj.read1(65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    if key.data == "readiness":
                        os.close(key.fileobj)
                    continue
                if key.data == "readiness":
                    readiness += chunk
                    if b"STT_SANDBOX_READY\n" in readiness:
                        sandbox_ready = True
                    continue
                accepted += len(chunk)
                if accepted > max_log_bytes:
                    limit_hit = True
                    os.killpg(process.pid, signal.SIGTERM)
                    break
                outputs[key.data].write(chunk)
            if limit_hit:
                break
            if process.poll() is not None and not selector.get_map():
                break
        if timed_out or limit_hit:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    return {"outer_status": "COMPLETE", "result_status": "TERMINATION_UNKNOWN", "sandbox_backend": backend, "operation_id": op}
        else:
            process.wait()
    finally:
        try:
            selector.close()
        finally:
            try:
                os.close(readiness_read)
            except OSError:
                pass
        for handle in outputs.values():
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
        process.stdout.close()
        process.stderr.close()
    if limit_hit:
        return {
            "outer_status": "COMPLETE",
            "result_status": "COMMAND_FAILED" if sandbox_ready else "SANDBOX_SETUP_FAILED",
            "sandbox_backend": backend,
            "reason": "COMMAND_LOG_LIMIT_EXCEEDED",
            "operation_id": op,
            "accepted_log_bytes": accepted,
        }
    if timed_out:
        return {
            "outer_status": "COMPLETE",
            "result_status": "TIMED_OUT" if sandbox_ready else "SANDBOX_SETUP_FAILED",
            "reason": "COMMAND_TIMED_OUT",
            "sandbox_backend": backend,
            "operation_id": op,
        }
    if not sandbox_ready:
        status = "SANDBOX_SETUP_FAILED"
        reason = "SANDBOX_READINESS_NOT_REACHED"
    elif process.returncode in command["accepted_exit_codes"]:
        status = "SUCCEEDED"
        reason = None
    else:
        status = "COMMAND_FAILED"
        reason = "COMMAND_EXIT_NOT_ACCEPTED"
    result = {
        "outer_status": "COMPLETE",
        "result_status": status,
        "operation_id": op,
        "sandbox_backend": backend,
        "exit_code": process.returncode,
        "stdout": {"path": str(stdout_path), "sha256": sha256_file(stdout_path), "size": stdout_path.stat().st_size},
        "stderr": {"path": str(stderr_path), "sha256": sha256_file(stderr_path), "size": stderr_path.stat().st_size},
    }
    if reason:
        result["reason"] = reason
    return result
