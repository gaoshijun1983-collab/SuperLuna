# SuperLuna 0.2.0-alpha.99

Controller 155 / Skill `2026-08-19.112` closes the retirement-registry
availability gap observed after the Alpha 98 real-App continuation.

A repo-retest state may retain a temporary account-gate path that disappears
across a host restart even though the canonical host account gate still holds
the complete durable record. Guard and the read-only retirement diagnostic now
select that canonical gate only when its existing data independently passes the
normal task, state scope, repository identity, reviewer generation, unique
startup authorization, recorded rate-limit, and global zero-slot evidence
matrix.

This is evidence recovery, not evidence creation. The controller does not infer
retirement from `rollover_blocked`, does not support the fallback for generic
profiles, and does not open a project, browser, or Chat. A missing, invalid, or
identity-mismatched canonical gate remains fail-closed with
`retirement_evidence_registry_unavailable`.

Local regression evidence does not prove the original NPC state has completed
the real replacement rollover.
