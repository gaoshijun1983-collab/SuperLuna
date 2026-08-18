# SuperLuna 0.2.0-alpha.64

Controller 120 / Skill revision `2026-08-16.77` removes the routine manual
reviewer-mode step from browser-first setup.

After SuperLuna has bound one exact reviewer Chat and holds its live startup
account slot, the controller may authorize one foreground selection of
`极高/Extreme`. The browser must then read the visible selector back and return
the same task, slot, browser, Chat, target, and state revision for confirmation.

This remains fail-closed: missing or ambiguous UI, stale authorization, a
different Chat, or a different browser cannot confirm the mode or advance the
workflow. Automatic Codex implementation-model switching remains disabled.

Local tests prove the controller contract only. Real macOS and Windows evidence
is still required before Public Beta.
