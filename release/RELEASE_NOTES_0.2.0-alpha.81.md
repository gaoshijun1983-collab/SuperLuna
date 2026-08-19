# SuperLuna 0.2.0-alpha.81

Controller 137 / Skill `2026-08-19.94` introduces truthful reviewer-context receipts.

- A filesystem path or inline selection cannot claim full-project review.
- `prepare-project-context` inventories Git-tracked sources plus explicitly declared authoritative untracked files, rejects path escape/symlinks/secrets, and emits a deterministic manifest and as many hashed ZIP volumes as required.
- Formal review remains blocked until every prepared volume name and SHA-256 is confirmed for the current reviewer generation.
- Replacement reviewer Chats preserve the package identity but never inherit the old Chat receipt; they require the full package plus rollover handoff again.
- Source coverage does not claim runtime behavior. Real App attachment/upload confirmation remains a separate release-evidence gate.
