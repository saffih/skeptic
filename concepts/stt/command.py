from __future__ import annotations

import os
import selectors
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from .canonical import sha256_file
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
    if sys.platform == "darwin" and {"sandbox-exec", "python"} <= tool_ids:
        return "macos-seatbelt"
    return None


def _seatbelt_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _write_macos_profile(*, candidate: Path, scratch: Path, tool_path: Path) -> Path:
    # Seatbelt is deprecated by Apple but remains the only deterministic local
    # filesystem/network sandbox shipped with supported macOS releases. The
    # profile is deny-by-default, permits only the candidate, scratch, and
    # immutable operating-system runtime paths, and grants no network class.
    read_roots = [
        candidate.resolve(),
        scratch.resolve(),
        Path("/System"),
        Path("/usr"),
        Path("/bin"),
        Path("/sbin"),
        Path("/Library/Apple"),
        Path("/private/var/db/dyld"),
        tool_path.resolve().parent,
        Path(__file__).with_name("sandbox_child.py").resolve(),
    ]
    literals = [Path("/dev/null"), Path("/dev/urandom"), Path("/dev/random")]
    read_rules = "\n".join(
        f"    (subpath {_seatbelt_quote(str(path))})" for path in dict.fromkeys(read_roots) if path.exists()
    )
    literal_rules = "\n".join(
        f"    (literal {_seatbelt_quote(str(path))})" for path in literals if path.exists()
    )
    profile = f"""(version 1)
(deny default)
(allow process*)
(allow signal (target self))
(allow sysctl-read)
(allow mach-lookup)
(allow ipc-posix-shm)
(allow file-read*
{read_rules}
{literal_rules})
(allow file-write*
    (subpath {_seatbelt_quote(str(scratch.resolve()))})
    (literal \"/dev/null\"))
"""
    profile_path = scratch / "seatbelt.sb"
    profile_path.write_text(profile, encoding="utf-8")
    os.chmod(profile_path, 0o600)
    return profile_path


def run_command(
    *,
    candidate: Path,
    command: dict[str, Any],
    catalog: dict[str, Any],
    logs_dir: Path,
    mode: str,
    max_log_bytes: int,
) -> dict[str, Any]:
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
    }
    Path(env["HOME"]).mkdir()
    Path(env["TMPDIR"]).mkdir()
    cwd = candidate / ("" if command["cwd"] == "." else command["cwd"])

    if mode == "sandbox_required":
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
                "--",
                *command["args"],
            ]
            cwd = candidate
        elif backend == "macos-seatbelt":
            sandbox_exec = _tool(catalog, "sandbox-exec")["path"]
            profile = _write_macos_profile(candidate=candidate, scratch=scratch, tool_path=Path(entry["path"]))
            python = _tool(catalog, "python")["path"]
            argv = [
                sandbox_exec, "-f", str(profile), python,
                str(Path(__file__).with_name("sandbox_child.py")),
                "--direct", "--readiness-fd", str(readiness_write),
                "--candidate", str(candidate), "--scratch", str(scratch),
                "--root", str(scratch / "root"), "--mount", "/bin/false",
                "--tool", entry["path"], "--cwd", command["cwd"], "--",
                *command["args"],
            ]
        else:
            os.close(readiness_read)
            os.close(readiness_write)
            raise STTError(
                "HOST_CAPABILITY_UNAVAILABLE",
                "sandbox_required but no supported sandbox backend is available",
                {"supported_backends": ["linux-unshare", "macos-seatbelt"]},
            )
    elif mode == "owner_risk_accepted":
        argv = [entry["path"], *command["args"]]
    else:
        raise STTError("DYNAMIC_VALIDATION_AUTHORIZATION_REQUIRED", "unknown dynamic execution mode")

    if mode != "sandbox_required":
        readiness_read = readiness_write = None
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
            "sandbox_backend": backend if mode == "sandbox_required" else "owner-risk-accepted",
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
    sandbox_ready = mode != "sandbox_required"
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
                    return {"outer_status": "COMPLETE", "result_status": "TERMINATION_UNKNOWN", "sandbox_backend": backend if mode == "sandbox_required" else "owner-risk-accepted", "operation_id": op}
        else:
            process.wait()
    finally:
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
            "sandbox_backend": backend if mode == "sandbox_required" else "owner-risk-accepted",
            "reason": "COMMAND_LOG_LIMIT_EXCEEDED",
            "operation_id": op,
            "accepted_log_bytes": accepted,
        }
    if timed_out:
        return {
            "outer_status": "COMPLETE",
            "result_status": "TIMED_OUT" if sandbox_ready else "SANDBOX_SETUP_FAILED",
            "reason": "COMMAND_TIMED_OUT",
            "sandbox_backend": backend if mode == "sandbox_required" else "owner-risk-accepted",
            "operation_id": op,
        }
    if mode == "sandbox_required" and not sandbox_ready:
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
        "sandbox_backend": backend if mode == "sandbox_required" else "owner-risk-accepted",
        "exit_code": process.returncode,
        "stdout": {"path": str(stdout_path), "sha256": sha256_file(stdout_path), "size": stdout_path.stat().st_size},
        "stderr": {"path": str(stderr_path), "sha256": sha256_file(stderr_path), "size": stderr_path.stat().st_size},
    }
    if reason:
        result["reason"] = reason
    return result
