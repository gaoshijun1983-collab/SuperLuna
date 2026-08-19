# SuperLuna 0.2.0-alpha.101

Controller 157 / Skill `2026-08-19.114` adds a fail-closed administrative seal
for one repo-retest reviewer generation whose legacy temporary account-gate
evidence can no longer be reconstructed.

The seal does not create a rate-limit record, startup authorization history, or
retirement fact. It is allowed only when the missing evidence is exactly the
rollover/rate-limit/authorization trio and the state independently proves the
same implementation task and trusted run binding, repository identity and
generation, prior legacy rate-limit lineage, replacement binding timestamp
chain, zero current request/response receipts, zero waits, and zero active
account slots.

Guard records the diagnostic hashes and missing codes, marks the old Chat
permanently unreadable, and creates one ordinary rollover authorization. The
normal account gate then grants one replacement startup. Reviewer generation
increments only after a new canonical Chat identity is bound, at which point a
fresh repository access receipt remains mandatory. Generic projects and every
uncertain or conflicting evidence shape stay blocked.

This is local controller evidence only; the original NPC state still requires
one real ordinary continuation.
