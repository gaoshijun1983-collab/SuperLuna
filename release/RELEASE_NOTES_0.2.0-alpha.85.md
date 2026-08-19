# SuperLuna 0.2.0-alpha.85

Controller 141 / Skill `2026-08-19.98` closes the turn-entry gap that could
leave an old attachment-blocked reviewer rollover waiting forever even though
the exact repository was available.

- Ordinary turn entry now returns one stable repository preparation action
  instead of `wait_for_supported_attachment_upload_capability`.
- `prepare-repository-rollover-recovery` verifies the original task identity,
  clean worktree, canonical HTTPS origin, remote-tracked exact HEAD, anonymous
  exact-commit reachability, full tree manifest, and root+nested canaries.
- Preparation never opens the browser and never claims a replacement Chat
  receipt. Successful preparation restores only the unique `rollover_pending`
  continuation; incomplete facts remain fail closed.

All evidence in this candidate is local automated evidence. Real Codex App
replacement creation and repository access receipt remain pending.
