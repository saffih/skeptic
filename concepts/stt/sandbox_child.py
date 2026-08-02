from __future__ import annotations

import argparse
import ctypes
import errno
import os
import platform
import resource
import stat
import subprocess
from pathlib import Path


PR_SET_NO_NEW_PRIVS = 38
PR_SET_SECCOMP = 22
PR_CAPBSET_READ = 23
PR_CAPBSET_DROP = 24
PR_CAP_AMBIENT = 47
PR_CAP_AMBIENT_CLEAR_ALL = 4
SECCOMP_MODE_FILTER = 2
LINUX_CAPABILITY_VERSION_3 = 0x20080522


class CapHeader(ctypes.Structure):
    _fields_ = [("version", ctypes.c_uint32), ("pid", ctypes.c_int)]


class CapData(ctypes.Structure):
    _fields_ = [("effective", ctypes.c_uint32), ("permitted", ctypes.c_uint32), ("inheritable", ctypes.c_uint32)]


class SockFilter(ctypes.Structure):
    _fields_ = [("code", ctypes.c_ushort), ("jt", ctypes.c_ubyte), ("jf", ctypes.c_ubyte), ("k", ctypes.c_uint32)]


class SockFprog(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ushort), ("filter", ctypes.POINTER(SockFilter))]


def _prctl(option: int, arg2: int = 0, arg3: int = 0) -> int:
    libc = ctypes.CDLL(None, use_errno=True)
    result = libc.prctl(option, arg2, arg3, 0, 0)
    if result != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))
    return result


def _drop_capabilities() -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    _prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL)
    for capability in range(64):
        result = libc.prctl(PR_CAPBSET_DROP, capability, 0, 0, 0)
        if result != 0 and ctypes.get_errno() != errno.EINVAL:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))
    header = CapHeader(LINUX_CAPABILITY_VERSION_3, 0)
    data = (CapData * 2)()
    if libc.capset(ctypes.byref(header), ctypes.byref(data)) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))
    for capability in range(64):
        value = libc.prctl(PR_CAPBSET_READ, capability, 0, 0, 0)
        if value > 0:
            raise OSError(errno.EPERM, "capability remained in bounding set")
        if value < 0 and ctypes.get_errno() != errno.EINVAL:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))
    _prctl(PR_SET_NO_NEW_PRIVS, 1)


def _seccomp_syscalls() -> tuple[int, int, list[int], int]:
    machine = platform.machine().lower()
    common_new = [428, 429, 430, 432, 433, 442]
    if machine in {"x86_64", "amd64"}:
        return 0xC000003E, 56, [155, 161, 165, 166, 272, 303, 304, 308, 435, *common_new], 0x7E020000
    if machine in {"aarch64", "arm64"}:
        return 0xC00000B7, 220, [39, 40, 41, 51, 97, 264, 265, 268, 435, *common_new], 0x7E020000
    raise OSError(errno.ENOTSUP, f"unsupported seccomp architecture: {machine}")


def _install_seccomp() -> None:
    audit_arch, clone_nr, denied, namespace_mask = _seccomp_syscalls()
    load_abs = 0x20
    jump_eq = 0x15
    alu_and = 0x54
    ret = 0x06
    kill_process = 0x80000000
    errno_action = 0x00050000 | errno.EPERM
    allow = 0x7FFF0000
    instructions: list[SockFilter] = [
        SockFilter(load_abs, 0, 0, 4),
        SockFilter(jump_eq, 1, 0, audit_arch),
        SockFilter(ret, 0, 0, kill_process),
        SockFilter(load_abs, 0, 0, 0),
    ]
    for syscall_number in sorted(set(denied)):
        instructions.extend((SockFilter(jump_eq, 0, 1, syscall_number), SockFilter(ret, 0, 0, errno_action)))
    instructions.extend(
        (
            SockFilter(jump_eq, 0, 4, clone_nr),
            SockFilter(load_abs, 0, 0, 16),
            SockFilter(alu_and, 0, 0, namespace_mask),
            SockFilter(jump_eq, 1, 0, 0),
            SockFilter(ret, 0, 0, errno_action),
            SockFilter(ret, 0, 0, allow),
        )
    )
    array_type = SockFilter * len(instructions)
    array = array_type(*instructions)
    program = SockFprog(len(instructions), array)
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ctypes.byref(program), 0, 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def _mount(mount_tool: str, *arguments: str) -> None:
    subprocess.run(
        [mount_tool, *arguments],
        check=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
    )


def _bind_read_only(mount_tool: str, source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    _mount(mount_tool, "--bind", str(source), str(destination))
    _mount(mount_tool, "-o", "remount,bind,ro,nosuid,nodev", str(destination))


def _protected_workspace_directories(candidate: Path, *, maximum: int = 10000) -> list[Path]:
    protected: list[Path] = []
    for base, dirs, files in os.walk(candidate, topdown=True, followlinks=False):
        current = Path(base)
        if current == candidate and ".git" in files:
            raise OSError(errno.EPERM, f"root Git file marker cannot be hidden safely: {current / '.git'}")
        if current != candidate and ".git" in {*dirs, *files}:
            marker = current / ".git"
            marker_value = os.lstat(marker)
            if not (stat.S_ISDIR(marker_value.st_mode) or stat.S_ISREG(marker_value.st_mode)):
                raise OSError(errno.EPERM, f"unsafe nested Git marker: {marker}")
            protected.append(current.relative_to(candidate))
            if len(protected) > maximum:
                raise OSError(errno.E2BIG, "too many protected workspace directories")
            dirs[:] = []
            continue
        if ".stt" in files:
            raise OSError(errno.EPERM, f"non-directory .stt control path: {current / '.stt'}")
        kept: list[str] = []
        for name in dirs:
            path = current / name
            value = os.lstat(path)
            if current == candidate and name == ".git":
                if not stat.S_ISDIR(value.st_mode):
                    raise OSError(errno.EPERM, f"unsafe root Git marker: {path}")
                protected.append(path.relative_to(candidate))
                if len(protected) > maximum:
                    raise OSError(errno.E2BIG, "too many protected workspace directories")
                continue
            if name == ".stt":
                if not os.path.isdir(path) or os.path.islink(path):
                    raise OSError(errno.EPERM, f"unsafe .stt control path: {path}")
                protected.append(path.relative_to(candidate))
                if len(protected) > maximum:
                    raise OSError(errno.E2BIG, "too many protected workspace directories")
                continue
            if name == ".git" or os.path.islink(path):
                continue
            kept.append(name)
        dirs[:] = kept
    return sorted(protected)


def _set_resource_limits(args: argparse.Namespace) -> None:
    def bound(which: int, requested: int) -> None:
        _, hard = resource.getrlimit(which)
        effective = requested if hard == resource.RLIM_INFINITY else min(requested, hard)
        resource.setrlimit(which, (effective, effective))

    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    bound(resource.RLIMIT_NOFILE, 256)
    bound(resource.RLIMIT_FSIZE, args.scratch_bytes)
    bound(resource.RLIMIT_AS, args.address_space_bytes)
    bound(resource.RLIMIT_CPU, args.timeout_seconds + 1)
    bound(resource.RLIMIT_NPROC, args.max_processes)


def run(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    candidate = Path(args.candidate).resolve()
    scratch = Path(args.scratch).resolve()
    runtime_roots = tuple(
        path.resolve()
        for path in (Path("/usr"), Path("/bin"), Path("/lib"), Path("/lib64"))
        if path.exists()
    )
    if any(
        candidate == host or candidate in host.parents or host in candidate.parents
        for host in runtime_roots
    ):
        raise OSError(errno.EPERM, "workspace overlaps a sandbox runtime mount")
    root.mkdir(parents=True, exist_ok=True)
    _mount(args.mount, "--make-rprivate", "/")
    for name in ("workspace", "tmp", "home", "usr", "bin", "lib", "lib64"):
        (root / name).mkdir(exist_ok=True)
    _bind_read_only(args.mount, root, root)
    _bind_read_only(args.mount, candidate, root / "workspace")
    for index, relative in enumerate(_protected_workspace_directories(candidate)):
        hidden = scratch / f"hidden-workspace-{index:05d}"
        hidden.mkdir(mode=0o700)
        os.chmod(hidden, 0o000)
        _bind_read_only(args.mount, hidden, root / "workspace" / relative)
    for host in (Path("/usr"), Path("/bin"), Path("/lib"), Path("/lib64")):
        if host.exists():
            _bind_read_only(args.mount, host, root / host.relative_to("/"))
    writable_partition = max(8 * 1024 * 1024, args.scratch_bytes // 2)
    _mount(args.mount, "-t", "tmpfs", "-o", f"nosuid,nodev,noexec,mode=0700,size={writable_partition}", "tmpfs", str(root / "tmp"))
    _mount(args.mount, "-t", "tmpfs", "-o", f"nosuid,nodev,noexec,mode=0700,size={writable_partition}", "tmpfs", str(root / "home"))
    os.chroot(root)
    os.chdir("/workspace" if args.cwd == "." else "/workspace/" + args.cwd)
    _set_resource_limits(args)
    try:
        os.setgroups([])
    except PermissionError:
        pass
    _drop_capabilities()
    _install_seccomp()
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": "/home",
        "TMPDIR": "/tmp",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_OPTIONAL_LOCKS": "0",
    }
    os.write(args.readiness_fd, b"STT_SANDBOX_READY\n")
    os.close(args.readiness_fd)
    os.execve(args.tool, [args.tool, *args.command_args], env)
    return 127


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--scratch", required=True)
    parser.add_argument("--mount", required=True)
    parser.add_argument("--tool", required=True)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--timeout-seconds", required=True, type=int)
    parser.add_argument("--scratch-bytes", required=True, type=int)
    parser.add_argument("--max-processes", required=True, type=int)
    parser.add_argument("--address-space-bytes", required=True, type=int)
    parser.add_argument("--readiness-fd", required=True, type=int)
    parser.add_argument("command_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command_args and args.command_args[0] == "--":
        args.command_args = args.command_args[1:]
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
