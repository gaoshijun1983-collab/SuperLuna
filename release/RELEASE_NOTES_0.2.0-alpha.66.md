# SuperLuna 0.2.0-alpha.66

Controller 122 / Skill revision `2026-08-17.79` completes the handoff from
automatic reviewer-mode confirmation to formal submission.

Controller 120 could securely persist a visible `极高/Extreme` confirmation as
`in_app_browser_automatic`, but the later submission-reopen gate still accepted
only the legacy manual `in_app_browser` source. The same exact bound reviewer
Chat could therefore stop before its first formal request despite valid evidence.

Controller 121 fixed the reopen gate, but real continuation exposed the same
legacy-only check in pre-send reconciliation and final send authorization. That
left the task safely stopped at `review_submit_pending` without sending Round 1.

Reopen, zero/one-request reconciliation, and final one-shot send authorization
now accept both trusted browser confirmation sources while retaining every
existing constraint: exact task, live `submission` account slot, browser,
reviewer Chat, fingerprint, visible foreground surface, empty request identity,
and no active waiting check. Cross-Chat, stale, wrong-operation, or background
evidence remains fail-closed.

Local tests prove the controller contract only. The resumed NPC AI loop is the
real macOS verification target and must not be counted as passed until it sends,
waits, reads, and continues successfully.
