from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from concepts.stt.command import run_command, sandbox_backend
from concepts.stt.errors import STTError
from concepts.stt.inventory import derive_toolchain
from concepts.stt.sandbox_child import _protected_workspace_directories


class CommandTests(unittest.TestCase):
    def test_git_and_stt_control_directories_are_bounded_for_hiding(self):
        with tempfile.TemporaryDirectory() as td:
            candidate = Path(td) / "candidate"; candidate.mkdir()
            (candidate / ".git").mkdir(); (candidate / ".stt").mkdir(); (candidate / "src" / ".stt").mkdir(parents=True)
            nested = candidate / "vendor"; nested.mkdir(); (nested / ".git").mkdir()
            submodule = candidate / "submodule"; submodule.mkdir(); (submodule / ".git").write_text("gitdir: ../.git/modules/submodule\n")
            self.assertEqual(
                _protected_workspace_directories(candidate),
                [Path(".git"), Path(".stt"), Path("src/.stt"), Path("submodule"), Path("vendor")],
            )
            with self.assertRaises(OSError):
                _protected_workspace_directories(candidate, maximum=1)
        with tempfile.TemporaryDirectory() as td:
            candidate = Path(td) / "candidate"; candidate.mkdir(); (candidate / ".stt").write_text("unsafe")
            with self.assertRaises(OSError):
                _protected_workspace_directories(candidate)
        with tempfile.TemporaryDirectory() as td:
            candidate = Path(td) / "candidate"; candidate.mkdir(); (candidate / ".git").write_text("gitdir: elsewhere\n")
            with self.assertRaises(OSError):
                _protected_workspace_directories(candidate)

    def test_unsupported_backend_fails_before_launch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate"
            candidate.mkdir()
            catalog = derive_toolchain()
            catalog["tools"] = [entry for entry in catalog["tools"] if entry["tool_id"] == "python"]
            with patch("concepts.stt.command.subprocess.Popen") as popen:
                with self.assertRaises(STTError) as raised:
                    run_command(
                        candidate=candidate,
                        command={"tool_id": "python", "args": ["-c", "raise SystemExit(9)"], "cwd": ".", "timeout_seconds": 5, "accepted_exit_codes": [0]},
                        catalog=catalog,
                        logs_dir=root / "logs",
                        mode="sandbox_required",
                        max_log_bytes=1024 * 1024,
                    )
            self.assertEqual(raised.exception.code, "HOST_CAPABILITY_UNAVAILABLE")
            popen.assert_not_called()

    def test_sandbox_hides_host_and_network_or_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate"
            candidate.mkdir()
            secret = root / "host-secret"
            secret.write_text("secret")
            script = candidate / "probe.py"
            script.write_text(
                "from pathlib import Path\n"
                "import os\n"
                "import socket\n"
                f"assert not Path({str(secret)!r}).exists(), 'host path visible'\n"
                "try:\n"
                " Path('candidate-write').write_text('forbidden'); raise AssertionError('workspace writable')\n"
                "except OSError:\n"
                " pass\n"
                "Path(os.environ['TMPDIR'], 'scratch-write').write_text('ok')\n"
                "s=socket.socket(); s.settimeout(0.2)\n"
                "try:\n"
                " s.connect(('1.1.1.1', 53)); raise AssertionError('network available')\n"
                "except OSError:\n"
                " pass\n"
                "print('contained')\n"
            )
            catalog = derive_toolchain()
            backend = sandbox_backend(catalog)
            try:
                result = run_command(
                    candidate=candidate,
                    command={
                        "tool_id": "python",
                        "args": ["probe.py"],
                        "cwd": ".",
                        "timeout_seconds": 30,
                        "accepted_exit_codes": [0],
                    },
                    catalog=catalog,
                    logs_dir=root / "logs",
                    mode="sandbox_required",
                    max_log_bytes=1024 * 1024,
                )
            except STTError as exc:
                self.assertIsNone(backend)
                self.assertEqual(exc.code, "HOST_CAPABILITY_UNAVAILABLE")
            else:
                self.assertIsNotNone(backend)
                self.assertEqual(result["sandbox_backend"], backend)
                if result["result_status"] == "SUCCEEDED":
                    self.assertIn("contained", Path(result["stdout"]["path"]).read_text())
                    self.assertFalse((candidate / "candidate-write").exists())
                else:
                    self.assertIn(result["result_status"], {"SANDBOX_UNAVAILABLE", "SANDBOX_SETUP_FAILED"}, result)
                    self.assertTrue(result.get("reason"), result)
                    self.assertFalse((candidate / "candidate-write").exists())

    def test_owner_risk_mode_is_rejected_before_launch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate"
            candidate.mkdir()
            with patch("concepts.stt.command.subprocess.Popen") as popen:
                with self.assertRaises(STTError) as raised:
                    run_command(
                        candidate=candidate,
                        command={"tool_id": "python", "args": ["ok.py"], "cwd": ".", "timeout_seconds": 30, "accepted_exit_codes": [0]},
                        catalog=derive_toolchain(),
                        logs_dir=root / "logs",
                        mode="owner_risk_accepted",
                        max_log_bytes=1024 * 1024,
                    )
            self.assertEqual(raised.exception.code, "UNCONFINED_SHARED_WORKSPACE_EXECUTION_UNSUPPORTED")
            popen.assert_not_called()
            self.assertFalse((root / "logs").exists())

    def test_unknown_mode_is_rejected_before_launch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate"
            candidate.mkdir()
            with patch("concepts.stt.command.subprocess.Popen") as popen:
                with self.assertRaises(STTError) as raised:
                    run_command(
                        candidate=candidate,
                        command={"tool_id": "python", "args": ["ok.py"], "cwd": ".", "timeout_seconds": 30, "accepted_exit_codes": [0]},
                        catalog=derive_toolchain(),
                        logs_dir=root / "logs",
                        mode="future-mode",
                        max_log_bytes=1024 * 1024,
                    )
            self.assertEqual(raised.exception.code, "DYNAMIC_VALIDATION_AUTHORIZATION_REQUIRED")
            popen.assert_not_called()

    def test_macos_backend_is_disabled_before_launch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = root / "candidate"
            candidate.mkdir()
            with patch("concepts.stt.command.sys.platform", "darwin"), patch("concepts.stt.command.subprocess.Popen") as popen:
                with self.assertRaises(STTError) as caught:
                    run_command(
                        candidate=candidate,
                        command={"tool_id": "python", "args": ["ok.py"], "cwd": ".", "timeout_seconds": 30, "accepted_exit_codes": [0]},
                        catalog=derive_toolchain(),
                        logs_dir=root / "logs",
                        mode="sandbox_required",
                        max_log_bytes=1024 * 1024,
                    )
            self.assertEqual(caught.exception.code, "HOST_CAPABILITY_UNAVAILABLE")
            popen.assert_not_called()
