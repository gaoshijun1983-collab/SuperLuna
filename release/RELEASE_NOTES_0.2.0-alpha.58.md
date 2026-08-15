# SuperLuna 0.2.0-alpha.58

Alpha 58 source packages Controller 114 and Skill revision `2026-08-14.71`.

Every authorized reviewer Chat operation now uses the visible foreground Codex
in-app browser. Startup, submission, waiting reads, and health probes must show
the one exact bound conversation as the user-visible active tab before reading
or writing Chat. Background scripts, hidden pages, cached DOM, and another
task's browser are not accepted substitutes.

Controller authorizations declare `browser_surface_mode=visible_foreground`,
`background_browser_access_allowed=false`, and the foreground conversation
target. An existing exact tab is surfaced in place; the visibility requirement
does not authorize a duplicate tab or replacement Chat.

This remains a technical-testing Alpha. Local contract tests do not prove that
every supported Codex Desktop build will surface the browser correctly, so the
next real Chat operation must be observed on macOS before this counts as device
evidence.
