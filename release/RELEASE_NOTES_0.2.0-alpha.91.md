# SuperLuna 0.2.0-alpha.91

Controller 147 / Skill `2026-08-19.104` closes the exact Alpha 90 real-App
legacy-state mismatch.

- The migration candidate now includes `rollover_pending` with no rollover
  failure code when the review is `external_blocked/controller_error`.
- A strictly matching live account cooldown atomically records
  `rollover_blocked/account_rate_limited`, restores the unsent submission, and
  creates one RDATE-bound recovery identity.
- Guard cannot return ordinary turn-entry during that cooldown. Platform wait
  creation and binding remain a same-turn barrier; once bound, subsequent
  guards reuse the same automation.
- Cooldown still permits no browser or Chat access and never asks for a product
  decision.

This is locally verified controller behavior. A real App retest remains the
release-evidence boundary.
