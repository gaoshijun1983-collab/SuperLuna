# SuperLuna 0.2.0-alpha.84

Controller 140 / Skill `2026-08-19.97` fixes repository-backed reviewer Chat
rollover recovery being stranded behind an obsolete attachment-upload blocker.

- A successful clean, canonical, reachable exact-commit preparation now runs
  before replacement startup, clears only the prior attachment capability
  failure, and restores the single `rollover_pending` continuation.
- The repository context carries a deterministic structured handoff covering
  completed formal rounds, locked decisions, unresolved issues, runtime and
  machine evidence indexes, and the base-to-head chain.
- The replacement Chat still needs a fresh exact-commit/full-tree/root+nested
  canary access receipt. Local paths and the handoff file are not access proof.
- Dirty, unreachable, mismatched, or unverifiable repositories still fall back
  to the full-source attachment path and remain fail closed before browser use.

This release has local automated evidence only. Real Codex App repository
access, replacement Chat binding, and formal review continuation remain pending.
