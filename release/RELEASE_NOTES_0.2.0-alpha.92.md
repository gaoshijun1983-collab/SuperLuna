# SuperLuna 0.2.0-alpha.92

Controller 148 / Skill `2026-08-19.105` closes the replacement startup-slot
identity loss found after the Alpha 91 real-App cooldown.

- Rollover completion promotes the live startup slot and its unique
  provisioning authorization to the final reviewer Chat, generation, state,
  and repository identity before release.
- A later rate-limit release therefore retires the exact replacement Chat and
  allows the one authorized rollover after cooldown.
- An old `reviewer_thread_id=none` release can reconcile one retirement only
  from the same startup lease's durable mode-selection/browser binding receipt,
  one matching prior-generation authorization, and zero slot or Chat conflict.
- Repeated reconciliation is idempotent and never creates a second retirement
  record or grants browser access.

This is local controller evidence. Real App retirement and post-cooldown
rollover remain outside this validation boundary.
