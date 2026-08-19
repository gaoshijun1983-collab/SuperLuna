# SuperLuna 0.2.0-alpha.80

Technical-testing Alpha. This is not a Public Beta.

- Packages Controller 136 and Skill revision `2026-08-19.93`.
- Fixes the real macOS path where stale platform-wait recovery rotated the
  existing reply token and RDATE before round-budget rollover migration.
- `found` and `not_found` recovery now preserve the exact wait identity, deny
  ordinary wait update/create/rearm, and return the single replacement-Chat
  startup continuation.
- A found platform wait remains the recovery anchor until the replacement Chat
  is durably bound, then must be deleted before rollover finalization.
- Local validation does not satisfy any real-device or Public Beta gate.
