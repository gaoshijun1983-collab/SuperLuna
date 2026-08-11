#!/usr/bin/env python3
"""Own one bounded reviewer-only ChatGPT App process for SuperLuna."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterator


APP_BINARY = Path("/Applications/ChatGPT.app/Contents/MacOS/ChatGPT")


class NativeSessionError(RuntimeError):
    pass


SESSION_LOCK_POLL_SECONDS = 0.01
_SESSION_THREAD_LOCKS: dict[str, threading.Lock] = {}
_SESSION_THREAD_LOCKS_GUARD = threading.Lock()


def _session_lock_path(session_path: Path) -> Path:
    return session_path.parent / f".{session_path.name}.lock"


@contextmanager
def _acquire_session_lock(session_path: Path, timeout: float) -> Iterator[None]:
    """Serialize one session file across threads and processes.

    The lock covers the complete load/start/persist or load/stop/remove
    lifecycle. It is intentionally scoped to one resolved session path, so
    independent reviewer sessions do not block one another.
    """
    session_path.parent.mkdir(parents=True, exist_ok=True)
    lock_key = str(session_path)
    with _SESSION_THREAD_LOCKS_GUARD:
        thread_lock = _SESSION_THREAD_LOCKS.setdefault(lock_key, threading.Lock())
    deadline = time.monotonic() + max(0.0, float(timeout))
    if not thread_lock.acquire(timeout=max(0.0, deadline - time.monotonic())):
        raise NativeSessionError("native App session lifecycle is busy")
    fd: int | None = None
    locked = False
    try:
        lock_file = _session_lock_path(session_path)
        fd = os.open(str(lock_file), os.O_RDWR | os.O_CREAT, 0o644)
        if os.fstat(fd).st_size == 0:
            os.write(fd, b"0")
            os.lseek(fd, 0, os.SEEK_SET)
        while True:
            try:
                if os.name == "nt":  # pragma: no cover - exercised on Windows
                    import msvcrt

                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                else:  # pragma: no cover - exercised on macOS/Linux
                    import fcntl

                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise NativeSessionError("native App session lifecycle is busy") from None
                time.sleep(SESSION_LOCK_POLL_SECONDS)
        yield
    finally:
        if fd is not None:
            if locked:
                try:
                    if os.name == "nt":  # pragma: no cover - exercised on Windows
                        import msvcrt

                        os.lseek(fd, 0, os.SEEK_SET)
                        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                    else:  # pragma: no cover - exercised on macOS/Linux
                        import fcntl

                        fcntl.flock(fd, fcntl.LOCK_UN)
                except OSError:
                    pass
            os.close(fd)
        thread_lock.release()


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _pid_command(pid: int) -> str:
    if sys.platform != "darwin":
        return ""
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            check=False,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _session_process_matches(session: dict[str, Any]) -> bool:
    command = _pid_command(int(session.get("pid", 0)))
    return bool(
        command
        and str(APP_BINARY) in command
        and f"--user-data-dir={session.get('profile_dir')}" in command
        and f"--remote-debugging-port={session.get('port')}" in command
    )


def _endpoint_ready(endpoint: str) -> bool:
    try:
        with urllib.request.urlopen(endpoint + "/json/version", timeout=1) as response:
            value = json.load(response)
        return isinstance(value.get("webSocketDebuggerUrl"), str)
    except (OSError, ValueError, urllib.error.URLError):
        return False


def _load_session(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise NativeSessionError("native App session file is invalid") from error
    return value if isinstance(value, dict) else None


def _start_session_locked(session_file: str, timeout: float = 30) -> dict[str, Any]:
    path = Path(session_file).expanduser().resolve()
    existing = _load_session(path)
    if existing is not None:
        endpoint = str(existing.get("endpoint", ""))
        if _session_process_matches(existing) and _endpoint_ready(endpoint):
            return {"action": "native_app_session_ready", "reused": True, **existing}
        raise NativeSessionError("stale native App session must be closed before replacement")
    if not APP_BINARY.is_file():
        raise NativeSessionError("ChatGPT desktop App is not installed in /Applications")
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix=".superluna-native-app-", dir=path.parent)).resolve()
    marker = profile / ".superluna-owned-profile"
    marker.write_text("owned by SuperLuna native App session\n", encoding="utf-8")
    port = _free_port()
    endpoint = f"http://127.0.0.1:{port}"
    log_path = profile / "native-app.log"
    log_handle = log_path.open("ab", buffering=0)
    process: subprocess.Popen[bytes] | None = None
    try:
        process = subprocess.Popen(
            [
                str(APP_BINARY),
                f"--user-data-dir={profile}",
                "--remote-debugging-address=127.0.0.1",
                f"--remote-debugging-port={port}",
            ],
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise NativeSessionError("native ChatGPT App exited during startup")
            if _endpoint_ready(endpoint):
                break
            time.sleep(0.2)
        else:
            raise NativeSessionError("native ChatGPT App did not expose its loopback endpoint")
        session = {
            "session_id": "native-session-" + secrets.token_hex(8),
            "pid": process.pid,
            "process_group_id": process.pid,
            "profile_dir": str(profile),
            "port": port,
            "endpoint": endpoint,
            "session_file": str(path),
        }
        _atomic_json(path, session)
        return {"action": "native_app_session_ready", "reused": False, **session}
    except Exception:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
        shutil.rmtree(profile, ignore_errors=True)
        raise
    finally:
        log_handle.close()


def start_session(session_file: str, timeout: float = 30) -> dict[str, Any]:
    path = Path(session_file).expanduser().resolve()
    with _acquire_session_lock(path, timeout=max(5.0, float(timeout) + 5.0)):
        return _start_session_locked(str(path), timeout)


def _invalidate_review_mode(state_file: str) -> None:
    controller = Path(__file__).with_name("lcrl.py")
    subprocess.run(
        [
            sys.executable,
            "-B",
            str(controller),
            "invalidate-review-mode",
            "--state",
            str(Path(state_file).expanduser().resolve()),
            "--reason",
            "reviewer_app_session_closed",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )


def _profile_processes(profile: str) -> list[int]:
    if sys.platform != "darwin":
        return []
    result = subprocess.run(
        ["ps", "ax", "-o", "pid=,command="],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    found: list[int] = []
    for line in result.stdout.splitlines():
        pid_text, _, command = line.strip().partition(" ")
        if profile in command and pid_text.isdigit():
            found.append(int(pid_text))
    return found


def _close_session_locked(session_file: str, state_file: str | None = None) -> dict[str, Any]:
    path = Path(session_file).expanduser().resolve()
    session = _load_session(path)
    if session is None:
        return {"action": "native_app_session_closed", "closed": False, "reason": "already_closed"}
    profile = Path(str(session.get("profile_dir", ""))).resolve()
    marker = profile / ".superluna-owned-profile"
    if not marker.is_file() or profile.parent != path.parent:
        raise NativeSessionError("refusing to clean an unverified native App profile")
    pid = int(session.get("pid", 0))
    if state_file:
        _invalidate_review_mode(state_file)
    if _session_process_matches(session):
        os.killpg(int(session.get("process_group_id", pid)), signal.SIGTERM)
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and _profile_processes(str(profile)):
        time.sleep(0.2)
    leftovers = _profile_processes(str(profile))
    for leftover in leftovers:
        os.kill(leftover, signal.SIGTERM)
    if leftovers:
        time.sleep(1)
    stubborn = _profile_processes(str(profile))
    for leftover in stubborn:
        os.kill(leftover, signal.SIGKILL)
    if stubborn:
        time.sleep(0.5)
    if _profile_processes(str(profile)):
        raise NativeSessionError("native App session processes could not be stopped")
    shutil.rmtree(profile)
    path.unlink(missing_ok=True)
    return {
        "action": "native_app_session_closed",
        "closed": True,
        "profile_removed": True,
        "review_mode_invalidated": bool(state_file),
        "pid": pid,
    }


def close_session(session_file: str, state_file: str | None = None) -> dict[str, Any]:
    path = Path(session_file).expanduser().resolve()
    with _acquire_session_lock(path, timeout=45.0):
        return _close_session_locked(str(path), state_file)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Own a SuperLuna native ChatGPT App session")
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start")
    start.add_argument("--session-file", required=True)
    start.add_argument("--timeout", type=float, default=30)
    close = commands.add_parser("close")
    close.add_argument("--session-file", required=True)
    close.add_argument("--state")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = (
            start_session(args.session_file, args.timeout)
            if args.command == "start"
            else close_session(args.session_file, args.state)
        )
    except (NativeSessionError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"action": "needs_user_decision", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
