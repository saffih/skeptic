#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
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
        (candidate / "probe.py").write_text(
            "from pathlib import Path\nimport os\nimport socket\n"
            f"assert not Path({str(secret)!r}).exists(), 'host path visible'\n"
            "try:\n Path('workspace-write').write_text('forbidden'); raise AssertionError('workspace writable')\n"
            "except OSError:\n pass\n"
            "Path(os.environ['TMPDIR'], 'scratch-write').write_text('ok')\n"
            "s=socket.socket(); s.settimeout(0.2)\n"
            "try:\n s.connect(('1.1.1.1',53)); raise AssertionError('network available')\n"
            "except OSError:\n pass\nprint('contained')\n"
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
            if (candidate / "workspace-write").exists() or not any(path.name == "scratch-write" for path in root.rglob("scratch-write")):
                print(json.dumps({"status": "FAIL_CONTAINMENT", "sandbox_backend": backend, "result": result}, sort_keys=True))
                return 1
            status = "PASS_CONTAINED"
        else:
            stderr = Path(result["stderr"]["path"]).read_text("utf-8", errors="replace")
            if result.get("result_status") not in {"SANDBOX_UNAVAILABLE", "SANDBOX_SETUP_FAILED"}:
                print(json.dumps({"status": "FAIL_CONTAINMENT", "sandbox_backend": backend, "result": result}, sort_keys=True))
                return 1
            status = "PASS_FAIL_CLOSED_BACKEND_BLOCKED"
        print(json.dumps({"status": status, "sandbox_backend": backend, "result": result}, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
