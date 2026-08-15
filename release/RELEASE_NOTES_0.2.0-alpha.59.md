# SuperLuna 0.2.0-alpha.59

Alpha 59 fixes two failures found during the long-running NPC AI loop.

- Review submission now validates any user-visible `Round N` or `第 N 轮`
  title against `STATE_REVIEW_ROUND` before browser access. A work-iteration
  label can no longer masquerade as the formal reviewer round.
- Waiting reads must select the complete assistant message after the current
  request. A partial message is recorded as a fragment, not as proof that no
  reply exists.
- The fixed reviewer Chat remains open as the visible browser handoff. Waiting
  work must not close all tabs with `keep:[]`.

This remains an early technical-testing Alpha. Local tests do not establish the
real macOS/Windows consecutive-cycle evidence required for Public Beta.
