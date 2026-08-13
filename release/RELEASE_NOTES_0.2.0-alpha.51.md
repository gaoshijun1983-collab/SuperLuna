# SuperLuna 0.2.0-alpha.51

This technical-testing Alpha packages Controller 104 / Skill revision
`2026-08-13.61`. It addresses the C34 startup dead end without claiming that a
host-owned permission prompt can be approved or bypassed by the plugin.

## Change since alpha.50

- When the user explicitly authorizes a new reviewer Chat, the implementation
  task now completes and minimally verifies its first real project change before
  reading the Browser Skill, acquiring an account-browser slot, or creating the
  Chat.
- A random workspace probe proves only basic directory writability. It no longer
  justifies creating a Chat before the first real edit.
- If the host requests approval, the edit is not durably written, or the minimal
  validation fails, the run stops with zero Chat side effects and does not ask a
  coordinator task to approve it.
- The account-browser gate requires
  `--new-chat-local-work-status completed_and_verified`; missing status cannot
  obtain a browser slot, Browser Skill permission, or home-navigation grant.
- Existing fixed-reviewer-Chat recovery, sending, waiting, and reply-consumption
  contracts are unchanged.

## Validation scope

The 292 repository regressions check the controller gate, packaged Skill, and
protocol ordering. This
is local workflow evidence only: Public Beta remains blocked until real-project
autonomous cycles and the required platform matrix are complete.
