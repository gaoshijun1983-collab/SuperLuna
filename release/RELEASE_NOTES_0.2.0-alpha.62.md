# SuperLuna 0.2.0-alpha.62

Alpha 62 reduces repeated ChatGPT history access after a real account cooldown.

## What changed

- The one visible health probe now hands the same browser lease and visible
  fixed Chat directly to the pending submission/read/startup operation.
- The follow-up is tail-only. Reinitializing the browser, reopening the Chat,
  reloading the page, or scanning the complete conversation history is denied.
- A false recovery no longer clears the rate-limit streak. An immediate second
  limit escalates the cooldown to 60 minutes.
- A completed continued browser action clears the streak normally.

## Evidence boundary

Local tests cover atomic continuation, lease reuse, tail-only flags, refusal of
a second browser initialization, cooldown escalation, and successful streak
reset. Real ChatGPT account behavior still requires the resumed macOS loop.
Public Beta remains blocked.
