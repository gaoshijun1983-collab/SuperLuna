# SuperLuna 0.2.0-alpha.63

Alpha 63 prevents one reviewer conversation from growing into a repeatedly
reloaded history database.

- One reviewer Chat is active at a time and is limited to eight formal reviews.
- Before a ninth review, SuperLuna requires exactly one replacement Chat.
- Any reviewer Chat that shows a real rate limit is retired permanently.
- Cooldown recovery provisions one replacement with compact current context;
  it never reopens, refreshes, health-probes, or scans the retired Chat.
- Exact request/reply pairing, no-resend reconciliation, and one-shot waiting
  checks remain fail-closed.

This is still a technical-testing Alpha. Local tests do not prove real macOS or
Windows browser behavior, and the Public Beta evidence gates remain open.
