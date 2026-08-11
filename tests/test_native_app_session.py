from __future__ import annotations

import importlib.util
import json
import multiprocessing
import queue
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "luna-chatgpt-review-loop" / "scripts" / "native_app_session.py"
SPEC = importlib.util.spec_from_file_location("native_app_session", SCRIPT)
native_app_session = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(native_app_session)


def _hold_session_lock_worker(script_path, session_path, acquired, release):
    spec = importlib.util.spec_from_file_location(
        f"native_app_session_worker_{multiprocessing.current_process().pid}", script_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    with module._acquire_session_lock(Path(session_path).resolve(), timeout=5):
        acquired.put(multiprocessing.current_process().pid)
        release.wait(timeout=5)


class NativeAppSessionTests(unittest.TestCase):
    def test_session_lifecycle_lock_excludes_another_process(self):
        with tempfile.TemporaryDirectory() as directory:
            session_path = Path(directory) / "native-session.json"
            context = multiprocessing.get_context("spawn")
            acquired = context.Queue()
            release = context.Event()
            first = context.Process(
                target=_hold_session_lock_worker,
                args=(str(SCRIPT), str(session_path), acquired, release),
            )
            second = context.Process(
                target=_hold_session_lock_worker,
                args=(str(SCRIPT), str(session_path), acquired, release),
            )
            first.start()
            first_pid = acquired.get(timeout=5)
            second.start()
            with self.assertRaises(queue.Empty):
                acquired.get(timeout=0.25)
            release.set()
            second_pid = acquired.get(timeout=5)
            first.join(timeout=5)
            second.join(timeout=5)
            self.assertNotEqual(first_pid, second_pid)
            self.assertEqual(first.exitcode, 0)
            self.assertEqual(second.exitcode, 0)

    def test_concurrent_start_reuses_one_owned_process(self):
        """Two callers for one session file must not launch two reviewer Apps."""

        class FakeProcess:
            def __init__(self, pid):
                self.pid = pid

            def poll(self):
                return None

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session_path = root / "native-session.json"
            fake_binary = root / "ChatGPT"
            fake_binary.write_text("stub", encoding="utf-8")
            original_load = native_app_session._load_session
            initial_reads = threading.Barrier(2)
            process_count = 0
            process_count_lock = threading.Lock()

            def delayed_load(path):
                try:
                    initial_reads.wait(timeout=0.3)
                except threading.BrokenBarrierError:
                    pass
                return original_load(path)

            def fake_popen(*_args, **_kwargs):
                nonlocal process_count
                with process_count_lock:
                    process_count += 1
                    return FakeProcess(1000 + process_count)

            results = []
            errors = []

            def start():
                try:
                    results.append(native_app_session.start_session(str(session_path), timeout=1))
                except Exception as error:  # pragma: no cover - assertion reports details
                    errors.append(error)

            with (
                mock.patch.object(native_app_session, "APP_BINARY", fake_binary),
                mock.patch.object(native_app_session, "_load_session", side_effect=delayed_load),
                mock.patch.object(native_app_session, "_endpoint_ready", return_value=True),
                mock.patch.object(native_app_session, "_session_process_matches", return_value=True),
                mock.patch.object(native_app_session, "_free_port", side_effect=[49331, 49332]),
                mock.patch.object(native_app_session.subprocess, "Popen", side_effect=fake_popen),
            ):
                threads = [threading.Thread(target=start) for _ in range(2)]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(timeout=3)

            self.assertFalse(errors)
            self.assertTrue(all(not thread.is_alive() for thread in threads))
            self.assertEqual(process_count, 1)
            self.assertEqual(sorted(result["reused"] for result in results), [False, True])

    def test_existing_live_session_is_reused_without_starting_another_app(self):
        with tempfile.TemporaryDirectory() as directory:
            session_path = Path(directory) / "native-session.json"
            session = {
                "session_id": "native-session-existing",
                "pid": 101,
                "profile_dir": str(Path(directory) / ".superluna-native-app-existing"),
                "port": 49321,
                "endpoint": "http://127.0.0.1:49321",
                "session_file": str(session_path),
            }
            session_path.write_text(json.dumps(session), encoding="utf-8")
            with (
                mock.patch.object(native_app_session, "_session_process_matches", return_value=True),
                mock.patch.object(native_app_session, "_endpoint_ready", return_value=True),
                mock.patch.object(native_app_session.subprocess, "Popen") as popen,
            ):
                result = native_app_session.start_session(str(session_path))
            self.assertTrue(result["reused"])
            popen.assert_not_called()

    def test_stale_session_fails_closed_instead_of_replacing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            session_path = Path(directory) / "native-session.json"
            session_path.write_text(json.dumps({
                "pid": 999999,
                "profile_dir": str(Path(directory) / ".superluna-native-app-stale"),
                "port": 49322,
                "endpoint": "http://127.0.0.1:49322",
            }), encoding="utf-8")
            before = session_path.read_bytes()
            with self.assertRaisesRegex(native_app_session.NativeSessionError, "stale"):
                native_app_session.start_session(str(session_path))
            self.assertEqual(session_path.read_bytes(), before)

    def test_close_invalidates_reasoning_evidence_when_state_is_supplied(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = root / ".superluna-native-app-owned"
            profile.mkdir()
            (profile / ".superluna-owned-profile").write_text("owned\n", encoding="utf-8")
            session_path = root / "native-session.json"
            session_path.write_text(json.dumps({
                "pid": 101,
                "process_group_id": 101,
                "profile_dir": str(profile),
                "port": 49324,
                "endpoint": "http://127.0.0.1:49324",
            }), encoding="utf-8")
            state_path = root / "state.json"
            state_path.write_text("{}", encoding="utf-8")
            with (
                mock.patch.object(native_app_session, "_session_process_matches", return_value=False),
                mock.patch.object(native_app_session, "_profile_processes", return_value=[]),
                mock.patch.object(native_app_session, "_invalidate_review_mode") as invalidate,
            ):
                result = native_app_session.close_session(str(session_path), str(state_path))
            invalidate.assert_called_once_with(str(state_path))
            self.assertTrue(result["review_mode_invalidated"])

    def test_close_refuses_an_unmarked_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = root / ".superluna-native-app-unowned"
            profile.mkdir()
            session_path = root / "native-session.json"
            session_path.write_text(json.dumps({
                "pid": 999999,
                "process_group_id": 999999,
                "profile_dir": str(profile),
                "port": 49323,
                "endpoint": "http://127.0.0.1:49323",
            }), encoding="utf-8")
            with self.assertRaisesRegex(native_app_session.NativeSessionError, "unverified"):
                native_app_session.close_session(str(session_path))
            self.assertTrue(profile.is_dir())


if __name__ == "__main__":
    unittest.main()
