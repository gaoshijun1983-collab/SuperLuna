# macOS browser-first acceptance plan

Run on a real Mac before public Beta. Record macOS, Codex Desktop, Python,
visible reviewer selector, date, and `pass`/`fail`/`not available` for each item.

## 1. Installation

- Install from a clean local copy and start a new Codex task.
- Run repository tests, controller selftest, Skill validator, and plugin validator.
- Expect no Windows-path, encoding, permission, or metadata mismatch.

## 2. Fixed browser binding

- Open one existing ChatGPT conversation in Codex's in-app browser.
- Confirm the URL conversation id and claim the same tab.
- Manually select and confirm the visible reviewer mode.
- Start SuperLuna with `in_app_browser`; expect one implementation writer and no
  App Chat fallback, new Chat, or recurring recovery task.

## 3. One full cycle

- Complete a small local change, submit once through the visible composer, wait,
  consume the complete paired reply, and continue in the same Codex task.
- Expect no coordinator relay, user “continue”, duplicate send, replacement tab,
  or unrelated Chat read.

## 4. Long reasoning

- Keep the reviewer visibly streaming beyond one wait interval.
- Expect inspection without reload, then one future check only while waiting.
- When complete, consume the reply once; repeating the same response is a no-op.

## 5. Ordinary network/load failure

- Interrupt the page while safely waiting.
- Expect no resend. The next check is scheduled 180 seconds later and may reload
  only the same tab once, then must verify the same conversation before reading.

## 6. Rate limit

- If ChatGPT naturally shows “requests are too frequent”, do not provoke it.
- Expect no reload, history read, or send. Verify a single probe after 15 minutes;
  repeated notices back off to 30 and 60 minutes. A readable page resets backoff.

## 7. Stale and queued checks

- Leave waiting before a preserved occurrence runs.
- Expect `waiting_check_expired`, no page read, no project write, no lease, and no
  state mutation. A phase may have only one stable wait identity.

## 8. Restart and sleep/wake

- Restart Codex and sleep/wake while waiting.
- Expect identity preservation, no duplicate submission, and fail-closed behavior
  if the original tab or conversation can no longer be proven.

## 9. Attachment visibility

- Review once inline, then with one small visible attachment.
- Expect a filename mismatch or missing visible artifact to block only that
  submission; do not claim visual review from a local-only path.

## 10. Ten-cycle gate

- Complete ten consecutive browser-first cycles on one frozen candidate.
- Require zero coordinator wakeups, user “continue” prompts, duplicate sends,
  cross-Chat reads, replacement tasks/Chats, and unexplained model changes.

Sanitize diagnostic state before sharing. Never include credentials, cookies,
private project source, personal Chat content, or real task/Chat identifiers.
