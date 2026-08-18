# SuperLuna 0.2.0-alpha.65

Controller 121 / Skill revision `2026-08-17.78` fixes the handoff from automatic
reviewer-mode confirmation to formal submission recovery.

Controller 120 could securely persist a visible `极高/Extreme` confirmation as
`in_app_browser_automatic`, but the later submission-reopen gate still accepted
only the legacy manual `in_app_browser` source. The same exact bound reviewer
Chat could therefore stop before its first formal request despite valid evidence.

The reopen gate now accepts both trusted browser confirmation sources while
retaining every existing constraint: exact task, live `submission` account slot,
browser, reviewer Chat, fingerprint, visible foreground surface, empty request
identity, and no active waiting check. Cross-Chat, stale, wrong-operation, or
background evidence remains fail-closed.

Local tests prove the controller contract only. The resumed NPC AI loop is the
real macOS verification target and must not be counted as passed until it sends,
waits, reads, and continues successfully.
