# SuperLuna 0.2.0-alpha.56

Alpha 56 source packages Controller 112 and Skill revision `2026-08-14.69`.

This candidate fixes a real-loop deadlock found during the NPC AI review run.
When the current review request is already visible in the one fixed Chat but the
short-lived send authorization was lost before its receipt was persisted,
SuperLuna can now reconcile that existing request without sending it again.

Recovery is deliberately narrow. It requires the fixed reviewer binding, one
exact full-body match, a raw payload SHA-256 equal to the current submission
fingerprint, trusted request turn/message identity, a live submission account
slot, and the matching browser-reopen lease. Success records the request with
`resend_allowed=false`; ambiguity, changed text, wrong identity, stale scope, or
an expired lease leaves state unchanged.

This remains a technical-testing Alpha. Local tests do not satisfy the real
macOS/Windows continuous-loop or Public Beta gates.
