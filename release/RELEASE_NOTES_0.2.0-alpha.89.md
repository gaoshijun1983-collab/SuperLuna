# SuperLuna 0.2.0-alpha.89

Controller 145 / Skill `2026-08-19.102` closes the status and recovery gap
exposed by the Alpha 88 real-App replacement-startup rate limit.

- A real “too many requests” result retains the stable
  `account_rate_limited` reason through top-level error handling, rollover
  state, and Chinese/English status projection.
- The shared account gate's exact cooldown deadline is authoritative. During
  cooldown SuperLuna cannot access Chat, initialize the browser, or probe.
- The controller creates or reuses exactly one RDATE-bound recovery check and
  reports whether that recovery has already been bound. Duplicate failure
  recording retains the same token and does not create recurring automation.
- Missing platform-wait capability remains a concrete technical blocker with
  `user_choice_required=false`.

This candidate has local controller evidence only. The one-shot recovery after
a real account cooldown still requires a real App retest.
