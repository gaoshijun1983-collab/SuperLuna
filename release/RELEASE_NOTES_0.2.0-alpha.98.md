# SuperLuna 0.2.0-alpha.98

Controller 154 / Skill `2026-08-19.111` closes the identity-diagnostic gap
exposed by the first Alpha 97 real-App continuation.

The Alpha 97 `task_binding_recovery_host_identity_mismatch` code is now split
into exact source-pair failures. Doctor and guard report the guard argument,
host `CODEX_THREAD_ID`, auxiliary `CODEX_SESSION_ID`, persisted state identity,
review-run identity, and binding-registry entry using only presence,
representation kind, length, and 12-character raw/normalized SHA-256 prefixes.
The payload also lists every mismatching source-name pair. It never echoes an
identity, and it explicitly reports that a host task-registry API is unavailable
instead of inventing evidence from a title or delegation source.

Legacy formatting may normalize only when both values strictly parse as the
same UUID after removing case differences, braces, or an explicit `urn:uuid:`,
`thread:`, or `thread_id:` wrapper. Different UUIDs and opaque identity drift
remain fail-closed. A successful same-UUID proof rebuilds the existing binding
and continues the same rollover generation without rewriting its historical
retest scope.

No diagnostic or migration path reads Chat, initializes a browser, reads an
implementation project, sends a message, or creates a second wait. This is
local controller evidence only; the original NPC state still needs one real
App continuation.
