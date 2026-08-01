from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def run(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    candidate = Path(args.candidate).resolve()
    scratch = Path(args.scratch).resolve()
    root.mkdir(parents=True, exist_ok=True)
    for name in ("workspace", "tmp", "home", "usr", "bin", "lib", "lib64"):
        (root / name).mkdir(exist_ok=True)
    if args.direct:
        os.chdir(candidate if args.cwd == "." else candidate / args.cwd)
        env = {"PATH": "/usr/bin:/bin", "HOME": str(scratch / "home"), "TMPDIR": str(scratch / "tmp"), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "PYTHONNOUSERSITE": "1"}
    else:
        subprocess.run([args.mount, "--bind", str(candidate), str(root / "workspace")], check=True)
        for host in ("/usr", "/bin", "/lib", "/lib64"):
            if Path(host).exists():
                subprocess.run([args.mount, "--rbind", host, str(root / host.lstrip("/"))], check=True)
                subprocess.run([args.mount, "-o", "remount,ro,bind", str(root / host.lstrip("/"))], check=True)
        subprocess.run([args.mount, "-t", "tmpfs", "tmpfs", str(root / "tmp")], check=True)
        subprocess.run([args.mount, "-t", "tmpfs", "tmpfs", str(root / "home")], check=True)
        os.chroot(root)
        os.chdir("/workspace" if args.cwd == "." else "/workspace/" + args.cwd)
        env = {"PATH": "/usr/bin:/bin", "HOME": "/home", "TMPDIR": "/tmp", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "PYTHONNOUSERSITE": "1"}
    os.write(args.readiness_fd, b"STT_SANDBOX_READY\n")
    os.close(args.readiness_fd)
    os.execve(args.tool, [args.tool, *args.command_args], env)
    return 127


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--direct", action="store_true")
    parser.add_argument("--root", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--scratch", required=True)
    parser.add_argument("--mount", required=True)
    parser.add_argument("--tool", required=True)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--readiness-fd", required=True, type=int)
    parser.add_argument("command_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command_args and args.command_args[0] == "--": args.command_args = args.command_args[1:]
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
