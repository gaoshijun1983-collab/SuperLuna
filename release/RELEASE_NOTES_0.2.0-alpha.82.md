# SuperLuna 0.2.0-alpha.82

Controller 138 / Skill `2026-08-19.95` makes exact repository review the preferred path for Git-backed projects.

- A canonical remote URL, repository identity, exact commit SHA, tree manifest hash, and non-authoritative branch label are persisted.
- First and replacement Chats require a new repository access receipt proving exact-commit/full-tree visibility with one root and one nested blob canary.
- Each formal round separately records the exact base→head chain, full diff hash, changed-path/blob manifest, workspace state, and runtime-evidence index.
- A prior tree receipt avoids rescanning full history, but never substitutes for the current round diff.
- Dirty worktrees, missing remotes, unreachable commits, unverified private access, or authentication failures require the complete sanitized attachment package. Partial review is not an automatic fallback.
- The controller never commits, pushes, publishes, or expands write permission.

Local tests do not prove that a real reviewer Chat can open a private or public exact commit. That remains a real-App release gate.
