# SuperLuna 0.2.0-alpha.78

Controller 134 / Skill revision `2026-08-19.91` closes the waiting-occurrence
rollover deadlock found in the real macOS NPC retest.

- A round-budget rollover keeps the current one-shot wait as its sole recovery
  anchor until exactly one replacement reviewer Chat is durably bound.
- The old wait may be deleted only after that binding succeeds. A matching
  deletion-proof finalizer then atomically continues the single pending review
  packet on the replacement Chat.
- Replacement creation failure stays `rollover_blocked`, retains one idempotent
  technical recovery, and never requests a product choice.
- Status and doctor projections reject an incomplete rollover without an
  executable future action.

This is local Alpha controller evidence only. No real Chat was accessed, and
the real macOS/Windows and Public Beta gates remain blocked.
