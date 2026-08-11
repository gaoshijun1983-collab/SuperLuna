from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "luna-chatgpt-review-loop" / "scripts" / "app_chat_reasoning.py"
SPEC = importlib.util.spec_from_file_location("app_chat_reasoning", SCRIPT)
app_chat_reasoning = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(app_chat_reasoning)


class AppChatReasoningTests(unittest.TestCase):
    def test_only_explicit_loopback_endpoints_are_allowed(self):
        self.assertTrue(app_chat_reasoning.is_loopback_endpoint("http://127.0.0.1:49321"))
        self.assertTrue(app_chat_reasoning.is_loopback_endpoint("http://localhost:49321"))
        self.assertFalse(app_chat_reasoning.is_loopback_endpoint("https://127.0.0.1:49321"))
        self.assertFalse(app_chat_reasoning.is_loopback_endpoint("http://0.0.0.0:49321"))
        self.assertFalse(app_chat_reasoning.is_loopback_endpoint("http://example.com:49321"))
        self.assertFalse(app_chat_reasoning.is_loopback_endpoint("http://127.0.0.1"))

    def test_sidebar_selector_uses_stable_chat_identity(self):
        selector = app_chat_reasoning.sidebar_selector("6a7073de-2a74-83ea-8d24-e856868eaa3d")
        self.assertIn("chatgpt:conversation:6a7073de-2a74-83ea-8d24-e856868eaa3d", selector)
        with self.assertRaises(app_chat_reasoning.AppChatControlError):
            app_chat_reasoning.sidebar_selector("title-not-an-id")

    def test_public_control_is_narrowly_limited_to_extreme(self):
        self.assertEqual(app_chat_reasoning.LEVEL_LABELS, {"extreme": "极高"})

    def test_fallback_turn_identity_uses_the_real_message_id(self):
        identity = app_chat_reasoning._stable_turn_identity({
            "turn_key": "fallback-turn-4",
            "message_id": "message-real-4",
        })
        self.assertEqual(identity, "message-real-4")

    def test_trusted_turn_identity_rejects_missing_blank_and_fallback(self):
        self.assertIsNone(app_chat_reasoning._trusted_turn_identity({"turn_key": None}))
        self.assertIsNone(app_chat_reasoning._trusted_turn_identity({"turn_key": ""}))
        self.assertIsNone(app_chat_reasoning._trusted_turn_identity({"turn_key": "   "}))
        self.assertIsNone(app_chat_reasoning._trusted_turn_identity({
            "turn_key": "fallback-turn-4", "message_id": "message-real-4",
        }))
        self.assertEqual(
            app_chat_reasoning._trusted_turn_identity({"turn_key": "  turn-real  "}),
            "turn-real",
        )

    def test_logical_composer_text_ignores_app_blank_line_expansion(self):
        expected = "title\n\nbody\nnext"
        rendered = "title\n\n\n\nbody\n\nnext"
        self.assertEqual(
            app_chat_reasoning._logical_composer_text(rendered),
            app_chat_reasoning._logical_composer_text(expected),
        )

    def _fake_read_reply(self, records, request_message_id: str, expected_title="Chat title"):
        class FakeSocket:
            def close(self):
                return None

        with (
            mock.patch.object(
                app_chat_reasoning, "_connect_native_app",
                return_value=(FakeSocket(), "native-app-test"),
            ),
            mock.patch.object(app_chat_reasoning, "_navigate_and_verify"),
            mock.patch.object(app_chat_reasoning, "_message_records", return_value=records),
        ):
            return app_chat_reasoning.read_reply(
                "http://127.0.0.1:49321", "chat-id", expected_title, request_message_id, 10
            )

    def _assert_no_reply_leak(self, result: dict):
        self.assertFalse(result.get("reply_complete"))
        self.assertNotIn("reply", result)
        self.assertNotIn("response_message_id", result)
        self.assertNotIn("response_turn_id", result)

    def test_read_reply_pairs_only_a_complete_assistant_with_the_exact_request(self):
        records = [
            {
                "turn_key": "turn-8", "turn_status": "complete",
                "item_type": "user-message", "message_id": "request-8",
                "completed": True, "content": "review",
            },
            {
                "turn_key": "turn-8", "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-8",
                "completed": True, "content": "clear next step",
            },
            {
                "turn_key": "turn-9", "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-other",
                "completed": True, "content": "wrong turn",
            },
        ]
        result = self._fake_read_reply(records, "request-8")
        self.assertEqual(result["action"], "app_chat_reply_complete")
        self.assertTrue(result["reply_complete"])
        self.assertEqual(result["response_message_id"], "response-8")
        self.assertEqual(result["response_turn_id"], "turn-8")
        self.assertEqual(result["reply"], "clear next step")

    def test_read_reply_does_not_return_an_in_progress_response(self):
        records = [
            {
                "turn_key": "turn-1", "turn_status": "in_progress",
                "item_type": "user-message", "message_id": "request-1",
                "completed": True, "content": "review",
            },
            {
                "turn_key": "turn-1", "turn_status": "in_progress",
                "item_type": "assistant-message", "message_id": "response-1",
                "completed": False, "content": "partial",
            },
        ]
        result = self._fake_read_reply(records, "request-1", expected_title=None)
        self.assertEqual(result["action"], "app_chat_reply_pending")
        self._assert_no_reply_leak(result)

    def test_read_reply_fails_closed_when_request_turn_key_is_none(self):
        records = [
            {
                "turn_key": None, "turn_status": "complete",
                "item_type": "user-message", "message_id": "request-target",
                "completed": True, "content": "review",
            },
            {
                "turn_key": None, "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-unrelated-later",
                "completed": True, "content": "wrong later reply",
            },
        ]
        result = self._fake_read_reply(records, "request-target")
        self.assertEqual(result["action"], "app_chat_reply_identity_unavailable")
        self.assertEqual(result["request_message_id"], "request-target")
        self._assert_no_reply_leak(result)

    def test_read_reply_does_not_pair_assistant_without_turn_identity(self):
        records = [
            {
                "turn_key": "turn-req", "turn_status": "complete",
                "item_type": "user-message", "message_id": "request-a",
                "completed": True, "content": "review",
            },
            {
                "turn_key": None, "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-no-id",
                "completed": True, "content": "should not pair",
            },
        ]
        result = self._fake_read_reply(records, "request-a")
        self.assertEqual(result["action"], "app_chat_reply_pending")
        self._assert_no_reply_leak(result)

    def test_read_reply_ignores_all_assistants_when_their_identities_are_empty(self):
        records = [
            {
                "turn_key": "turn-req", "turn_status": "complete",
                "item_type": "user-message", "message_id": "request-b",
                "completed": True, "content": "review",
            },
            {
                "turn_key": None, "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-empty-1",
                "completed": True, "content": "first empty identity",
            },
            {
                "turn_key": "", "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-empty-2",
                "completed": True, "content": "second empty identity",
            },
            {
                "turn_key": "   ", "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-empty-3",
                "completed": True, "content": "third empty identity",
            },
        ]
        result = self._fake_read_reply(records, "request-b")
        self.assertEqual(result["action"], "app_chat_reply_pending")
        self._assert_no_reply_leak(result)

    def test_read_reply_does_not_pair_by_identical_content_across_turns(self):
        same_body = "same review guidance text"
        records = [
            {
                "turn_key": "turn-current", "turn_status": "complete",
                "item_type": "user-message", "message_id": "request-current",
                "completed": True, "content": "review",
            },
            {
                "turn_key": "turn-prior", "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-prior",
                "completed": True, "content": same_body,
            },
            {
                "turn_key": "turn-other", "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-other",
                "completed": True, "content": same_body,
            },
        ]
        result = self._fake_read_reply(records, "request-current")
        self.assertEqual(result["action"], "app_chat_reply_pending")
        self._assert_no_reply_leak(result)

    def test_read_reply_pairs_matching_nonempty_trusted_turn_identity(self):
        records = [
            {
                "turn_key": "turn-match", "turn_status": "complete",
                "item_type": "user-message", "message_id": "request-match",
                "completed": True, "content": "review",
            },
            {
                "turn_key": "turn-match", "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-match",
                "completed": True, "content": "paired next step",
            },
        ]
        result = self._fake_read_reply(records, "request-match")
        self.assertEqual(result["action"], "app_chat_reply_complete")
        self.assertTrue(result["reply_complete"])
        self.assertEqual(result["response_turn_id"], "turn-match")
        self.assertEqual(result["response_message_id"], "response-match")
        self.assertEqual(result["reply"], "paired next step")

    def test_read_reply_fails_closed_for_blank_and_fallback_request_identities(self):
        for turn_key in ("", "   ", "fallback-turn-9"):
            records = [
                {
                    "turn_key": turn_key, "turn_status": "complete",
                    "item_type": "user-message", "message_id": "request-bad",
                    "completed": True, "content": "review",
                },
                {
                    "turn_key": turn_key, "turn_status": "complete",
                    "item_type": "assistant-message", "message_id": "response-bad",
                    "completed": True, "content": "must not leak",
                },
            ]
            result = self._fake_read_reply(records, "request-bad")
            self.assertEqual(
                result["action"], "app_chat_reply_identity_unavailable",
                msg=f"turn_key={turn_key!r}",
            )
            self._assert_no_reply_leak(result)

    def test_read_reply_selects_only_the_assistant_with_matching_identity(self):
        records = [
            {
                "turn_key": "turn-correct", "turn_status": "complete",
                "item_type": "user-message", "message_id": "request-c",
                "completed": True, "content": "review",
            },
            {
                "turn_key": "turn-wrong", "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-wrong",
                "completed": True, "content": "wrong identity body",
            },
            {
                "turn_key": None, "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-none",
                "completed": True, "content": "missing identity body",
            },
            {
                "turn_key": "turn-correct", "turn_status": "complete",
                "item_type": "assistant-message", "message_id": "response-correct",
                "completed": True, "content": "correct identity body",
            },
        ]
        result = self._fake_read_reply(records, "request-c")
        self.assertEqual(result["action"], "app_chat_reply_complete")
        self.assertEqual(result["response_message_id"], "response-correct")
        self.assertEqual(result["response_turn_id"], "turn-correct")
        self.assertEqual(result["reply"], "correct identity body")

    def test_submit_refuses_if_the_native_app_instance_changes_after_switch(self):
        class FakeSocket:
            def close(self):
                return None

        with (
            mock.patch.object(
                app_chat_reasoning, "set_reasoning",
                return_value={"native_app_instance_id": "native-app-one"},
            ),
            mock.patch.object(
                app_chat_reasoning, "_connect_native_app",
                return_value=(FakeSocket(), "native-app-two"),
            ),
        ):
            with self.assertRaisesRegex(
                app_chat_reasoning.AppChatControlError, "instance changed"
            ):
                app_chat_reasoning.submit_review(
                    "http://127.0.0.1:49321", "chat-id", None, "review", 10
                )

    def test_submit_returns_the_real_request_identity_from_the_same_instance(self):
        class FakeSocket:
            def __init__(self):
                self.inserted = []
                self.clicks = []

            def click_point(self, x, y, _deadline):
                self.clicks.append((x, y))

            def insert_text(self, value, _deadline):
                self.inserted.append(value)

            def close(self):
                return None

        socket = FakeSocket()
        with (
            mock.patch.object(
                app_chat_reasoning, "set_reasoning",
                return_value={"native_app_instance_id": "native-app-one"},
            ),
            mock.patch.object(
                app_chat_reasoning, "_connect_native_app",
                return_value=(socket, "native-app-one"),
            ),
            mock.patch.object(app_chat_reasoning, "_navigate_and_verify"),
            mock.patch.object(app_chat_reasoning, "_message_records", return_value=[{
                "item_type": "user-message", "message_id": "old-request",
            }]),
            mock.patch.object(
                app_chat_reasoning, "_composer_state",
                return_value={"text": "", "disabled": False},
            ),
            mock.patch.object(
                app_chat_reasoning, "_wait_for_submitted_request",
                return_value={"message_id": "new-request", "turn_key": "fallback-turn-12"},
            ),
            mock.patch.object(
                app_chat_reasoning, "_wait_for_value",
                side_effect=[
                    True,
                    {"x": 30, "y": 40},
                ],
            ),
            mock.patch.object(
                app_chat_reasoning, "_point_for", return_value={"x": 10, "y": 20}
            ),
        ):
            result = app_chat_reasoning.submit_review(
                "http://127.0.0.1:49321", "chat-id", "Chat title", "review\n", 10
            )
        self.assertEqual(socket.inserted, ["review"])
        self.assertEqual(socket.clicks, [(10, 20), (30, 40)])
        self.assertEqual(result["native_app_instance_id"], "native-app-one")
        self.assertEqual(result["request_message_id"], "new-request")
        self.assertEqual(result["request_turn_id"], "new-request")

    def test_submit_resumes_an_identical_app_rendered_draft_without_reinserting(self):
        class FakeSocket:
            def __init__(self):
                self.inserted = []
                self.clicks = []

            def click_point(self, x, y, _deadline):
                self.clicks.append((x, y))

            def insert_text(self, value, _deadline):
                self.inserted.append(value)

            def close(self):
                return None

        socket = FakeSocket()
        with (
            mock.patch.object(
                app_chat_reasoning, "set_reasoning",
                return_value={"native_app_instance_id": "native-app-one"},
            ),
            mock.patch.object(
                app_chat_reasoning, "_connect_native_app",
                return_value=(socket, "native-app-one"),
            ),
            mock.patch.object(app_chat_reasoning, "_navigate_and_verify"),
            mock.patch.object(app_chat_reasoning, "_message_records", return_value=[]),
            mock.patch.object(
                app_chat_reasoning, "_composer_state",
                return_value={"text": "title\n\n\n\nbody", "disabled": False},
            ),
            mock.patch.object(
                app_chat_reasoning, "_wait_for_submitted_request",
                return_value={"message_id": "new-request", "turn_key": "turn-12"},
            ),
            mock.patch.object(
                app_chat_reasoning, "_wait_for_value",
                side_effect=[
                    True,
                    {"x": 30, "y": 40},
                ],
            ),
        ):
            result = app_chat_reasoning.submit_review(
                "http://127.0.0.1:49321", "chat-id", "Chat title", "title\n\nbody", 10
            )
        self.assertEqual(socket.inserted, [])
        self.assertEqual(socket.clicks, [(30, 40)])
        self.assertEqual(result["request_message_id"], "new-request")

    def test_uncertain_submit_preserves_pre_click_reconcile_baseline(self):
        class FakeSocket:
            def click_point(self, _x, _y, _deadline):
                return None

            def insert_text(self, _value, _deadline):
                return None

            def close(self):
                return None

        payload = "review packet"
        with (
            mock.patch.object(
                app_chat_reasoning, "set_reasoning",
                return_value={"native_app_instance_id": "native-app-one"},
            ),
            mock.patch.object(
                app_chat_reasoning, "_connect_native_app",
                return_value=(FakeSocket(), "native-app-one"),
            ),
            mock.patch.object(app_chat_reasoning, "_navigate_and_verify"),
            mock.patch.object(app_chat_reasoning, "_message_records", return_value=[{
                "item_type": "user-message", "message_id": "old-request",
            }]),
            mock.patch.object(
                app_chat_reasoning, "_composer_state",
                return_value={"text": "", "disabled": False},
            ),
            mock.patch.object(
                app_chat_reasoning, "_wait_for_submitted_request",
                side_effect=app_chat_reasoning.AppChatControlError("receipt timeout"),
            ),
            mock.patch.object(
                app_chat_reasoning, "_wait_for_value",
                side_effect=[True, {"x": 30, "y": 40}],
            ),
            mock.patch.object(
                app_chat_reasoning, "_point_for", return_value={"x": 10, "y": 20}
            ),
        ):
            with self.assertRaises(app_chat_reasoning.SubmissionReceiptUncertain) as raised:
                app_chat_reasoning.submit_review(
                    "http://127.0.0.1:49321", "chat-id", None, payload, 10
                )
        context = raised.exception.reconcile_context
        self.assertEqual(context["baseline_message_ids"], ["old-request"])
        self.assertEqual(context["native_app_instance_id"], "native-app-one")
        self.assertEqual(context["thread_id"], "chat-id")
        self.assertEqual(
            context["payload_sha256"],
            app_chat_reasoning.hashlib.sha256(payload.encode()).hexdigest(),
        )

    def test_reconcile_submission_recovers_one_exact_message_without_clicking(self):
        class FakeSocket:
            def close(self):
                return None

        records = [{
            "item_type": "user-message", "message_id": "request-42",
            "turn_key": "turn-42", "content": "review packet",
        }]
        with (
            mock.patch.object(
                app_chat_reasoning, "_connect_native_app",
                return_value=(FakeSocket(), "native-app-one"),
            ),
            mock.patch.object(app_chat_reasoning, "_navigate_and_verify"),
            mock.patch.object(app_chat_reasoning, "_message_records", return_value=records),
        ):
            result = app_chat_reasoning.reconcile_submission(
                "http://127.0.0.1:49321", "chat-id", "Chat title", "review packet\n",
                {
                    "version": 1,
                    "native_app_instance_id": "native-app-one",
                    "thread_id": "chat-id",
                    "payload_sha256": app_chat_reasoning.hashlib.sha256(
                        b"review packet"
                    ).hexdigest(),
                    "baseline_message_ids": [],
                },
                10,
            )
        self.assertEqual(result["action"], "app_chat_submission_reconciled")
        self.assertEqual(result["request_message_id"], "request-42")
        self.assertEqual(result["request_turn_id"], "turn-42")

    def test_reconcile_submission_proves_identical_draft_is_unsent(self):
        class FakeSocket:
            def close(self):
                return None

        with (
            mock.patch.object(
                app_chat_reasoning, "_connect_native_app",
                return_value=(FakeSocket(), "native-app-one"),
            ),
            mock.patch.object(app_chat_reasoning, "_navigate_and_verify"),
            mock.patch.object(app_chat_reasoning, "_message_records", return_value=[]),
            mock.patch.object(
                app_chat_reasoning, "_composer_state",
                return_value={"text": "review\n\npacket", "disabled": False},
            ),
        ):
            result = app_chat_reasoning.reconcile_submission(
                "http://127.0.0.1:49321", "chat-id", None, "review\npacket",
                {
                    "version": 1,
                    "native_app_instance_id": "native-app-one",
                    "thread_id": "chat-id",
                    "payload_sha256": app_chat_reasoning.hashlib.sha256(
                        b"review\npacket"
                    ).hexdigest(),
                    "baseline_message_ids": [],
                },
                10,
            )
        self.assertEqual(result["action"], "app_chat_submission_not_sent")
        self.assertTrue(result["safe_to_submit_once"])

    def test_reconcile_submission_ignores_old_same_text_from_baseline(self):
        class FakeSocket:
            def close(self):
                return None

        payload = "same review packet"
        context = {
            "version": 1,
            "native_app_instance_id": "native-app-one",
            "thread_id": "chat-id",
            "payload_sha256": app_chat_reasoning.hashlib.sha256(payload.encode()).hexdigest(),
            "baseline_message_ids": ["old-request"],
        }
        records = [{
            "item_type": "user-message", "message_id": "old-request",
            "turn_key": "old-turn", "content": payload,
        }]
        with (
            mock.patch.object(
                app_chat_reasoning, "_connect_native_app",
                return_value=(FakeSocket(), "native-app-one"),
            ),
            mock.patch.object(app_chat_reasoning, "_navigate_and_verify"),
            mock.patch.object(app_chat_reasoning, "_message_records", return_value=records),
            mock.patch.object(
                app_chat_reasoning, "_composer_state",
                return_value={"text": "", "disabled": False},
            ),
        ):
            with self.assertRaisesRegex(
                app_chat_reasoning.AppChatControlError, "remains uncertain"
            ):
                app_chat_reasoning.reconcile_submission(
                    "http://127.0.0.1:49321", "chat-id", None, payload, context, 10
                )

    def test_reconcile_submission_recovers_only_new_same_text_message(self):
        class FakeSocket:
            def close(self):
                return None

        payload = "same review packet"
        context = {
            "version": 1,
            "native_app_instance_id": "native-app-one",
            "thread_id": "chat-id",
            "payload_sha256": app_chat_reasoning.hashlib.sha256(payload.encode()).hexdigest(),
            "baseline_message_ids": ["old-request"],
        }
        records = [
            {"item_type": "user-message", "message_id": "old-request", "content": payload},
            {"item_type": "user-message", "message_id": "new-request", "turn_key": "new-turn", "content": payload},
        ]
        with (
            mock.patch.object(
                app_chat_reasoning, "_connect_native_app",
                return_value=(FakeSocket(), "native-app-one"),
            ),
            mock.patch.object(app_chat_reasoning, "_navigate_and_verify"),
            mock.patch.object(app_chat_reasoning, "_message_records", return_value=records),
        ):
            result = app_chat_reasoning.reconcile_submission(
                "http://127.0.0.1:49321", "chat-id", None, payload, context, 10
            )
        self.assertEqual(result["request_message_id"], "new-request")
        self.assertEqual(result["request_turn_id"], "new-turn")


if __name__ == "__main__":
    unittest.main()
