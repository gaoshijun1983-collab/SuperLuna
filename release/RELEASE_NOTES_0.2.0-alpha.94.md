# SuperLuna 0.2.0-alpha.94

Controller 150 / Skill `2026-08-19.107` closes the second interruption gap in
replacement startup provisioning. When the original provisioning and its first
orphan reclaim were both consumed but no replacement Chat identity, browser
initialization, message receipt, or account slot exists, the controller may
persist exactly one additional zero-effect recovery for the same generation.

The migration requires one exact authorization, implementation task, state,
repository identity, exact commit, tree manifest, reviewer generation, and a
formally rate-limited retirement record for the old reviewer Chat. Any active
slot, repository drift, missing retirement, conflicting Chat identity, or an
already consumed recovery fails closed with a stable reason code. Guard routes
the state owner to the reconcile command without accessing a browser or asking
the user for a product decision.

All evidence in this candidate is local controller evidence. A real Codex App
replacement startup and reviewer repository access receipt remain separate
Public Beta gates.
