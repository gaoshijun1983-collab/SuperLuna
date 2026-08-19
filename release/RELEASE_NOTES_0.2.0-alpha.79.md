# SuperLuna 0.2.0-alpha.79

Technical-testing Alpha. This is not a Public Beta.

- Packages Controller 135 and Skill revision `2026-08-19.92`.
- Fixes the real waiting-occurrence path that could repeatedly move the same
  reply heartbeat by about five minutes after `round_budget` had already
  forbidden access to the old reviewer Chat.
- Atomically converts that occurrence to `rollover_continuation`, rejects
  ordinary reply rearm, releases any acquired `waiting_read` slot, and returns
  the exact one-time replacement-Chat `startup` request.
- Keeps the original one-shot identity until the replacement Chat is durably
  bound, then requires real platform deletion proof before rollover finalization.
- Keeps Public Beta blocked pending fresh real macOS/Windows evidence.
