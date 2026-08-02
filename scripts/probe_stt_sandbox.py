#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import platform
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from concepts.stt.command import run_command, sandbox_backend
from concepts.stt.errors import STTError
from concepts.stt.inventory import derive_toolchain


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="stt-sandbox-probe-") as td:
        root = Path(td)
        candidate = root / "candidate"
        candidate.mkdir()
        secret = root / "secret"
        secret.write_text("host-only")
        (candidate / ".git").mkdir()
        (candidate / ".git" / "config").write_text("git-secret")
        (candidate / ".stt").mkdir()
        (candidate / ".stt" / "task-secret").write_text("hidden")
        (candidate / "nested" / ".stt").mkdir(parents=True)
        (candidate / "nested" / ".stt" / "nested-secret").write_text("hidden")
        (candidate / "vendor" / ".git").mkdir(parents=True)
        (candidate / "vendor" / "nested-repository-secret").write_text("hidden")
        (candidate / "probe.py").write_text(
            "from pathlib import Path\nimport ctypes\nimport errno\nimport os\nimport socket\n"
            f"assert not Path({str(secret)!r}).exists(), 'host path visible'\n"
            "assert not Path('/workspace/.git/config').exists(), '.git visible'\n"
            "assert not Path('/workspace/.stt/task-secret').exists(), '.stt visible'\n"
            "assert not Path('/workspace/nested/.stt/nested-secret').exists(), 'nested .stt visible'\n"
            "assert not Path('/workspace/vendor/nested-repository-secret').exists(), 'nested repository visible'\n"
            "assert not Path('/proc').exists(), '/proc unexpectedly mounted'\n"
            "assert os.environ.get('GIT_OPTIONAL_LOCKS') == '0'\n"
            "assert os.environ.get('PYTHONDONTWRITEBYTECODE') == '1'\n"
            "try:\n Path('workspace-write').write_text('forbidden'); raise AssertionError('workspace writable')\n"
            "except OSError:\n pass\n"
            "try:\n Path('/root-write').write_text('forbidden'); raise AssertionError('chroot root writable')\n"
            "except OSError:\n pass\n"
            "Path(os.environ['TMPDIR'], 'scratch-write').write_text('ok')\n"
            "libc=ctypes.CDLL(None,use_errno=True)\n"
            "assert libc.prctl(23,21,0,0,0) == 0, 'CAP_SYS_ADMIN remains in bounding set'\n"
            "assert libc.prctl(47,1,21,0,0) == 0, 'ambient CAP_SYS_ADMIN remains'\n"
            "assert libc.unshare(0x10000000|0x00020000) == -1 and ctypes.get_errno() == errno.EPERM, 'namespace regain succeeded'\n"
            "ctypes.set_errno(0)\n"
            "assert libc.mount(None,b'/workspace',None,32|1,None) == -1 and ctypes.get_errno() == errno.EPERM, 'workspace remount succeeded'\n"
            "s=socket.socket(); s.settimeout(0.2)\n"
            "try:\n s.connect(('1.1.1.1',53)); raise AssertionError('network available')\n"
            "except OSError:\n pass\nprint('contained-remount-capability-probe-pass')\n"
        )
        catalog = derive_toolchain()
        backend = sandbox_backend(catalog)
        try:
            result = run_command(
                candidate=candidate,
                command={"tool_id": "python", "args": ["probe.py"], "cwd": ".", "timeout_seconds": 30, "accepted_exit_codes": [0]},
                catalog=catalog,
                logs_dir=root / "logs",
                mode="sandbox_required",
                max_log_bytes=1024 * 1024,
            )
        except STTError as exc:
            if exc.code != "HOST_CAPABILITY_UNAVAILABLE" or backend is not None:
                raise
            print(json.dumps({"status": "PASS_FAIL_CLOSED", "sandbox_backend": None, "error_code": exc.code}, sort_keys=True))
            return 0
        if result.get("result_status") == "SUCCEEDED":
            if (candidate / "workspace-write").exists():
                print(json.dumps({"status": "FAIL_CONTAINMENT", "sandbox_backend": backend, "result": result}, sort_keys=True))
                return 1
            stdout = Path(result["stdout"]["path"]).read_text("utf-8", errors="replace")
            if "contained-remount-capability-probe-pass" not in stdout:
                print(json.dumps({"status": "FAIL_CONTAINMENT", "sandbox_backend": backend, "result": result}, sort_keys=True))
                return 1
            status = "PASS_CONTAINED_ADVERSARIAL"
        else:
            if result.get("result_status") not in {"SANDBOX_UNAVAILABLE", "SANDBOX_SETUP_FAILED"}:
                print(json.dumps({"status": "FAIL_CONTAINMENT", "sandbox_backend": backend, "result": result}, sort_keys=True))
                return 1
            status = "PASS_FAIL_CLOSED_BACKEND_BLOCKED"
        print(json.dumps({"status": status, "platform": platform.system(), "sandbox_backend": backend, "result": result}, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
