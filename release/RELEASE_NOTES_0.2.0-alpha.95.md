# SuperLuna 0.2.0-alpha.95

Controller 151 / Skill `2026-08-19.108` closes the legacy ordering gap where a
rate-limited reviewer Chat had no formal account-gate retirement record before
the consumed-orphan provisioning recovery ran.

Ordinary turn entry may now atomically rebuild that one retirement and continue
directly to the Alpha 94 recovery. The proof requires the same implementation
task, state, reviewer and generation, persistent account rate-limit ownership,
a `rate_limited` rollover, exact repository commit and tree, the canonical
provisioned reviewer binding, one prior-generation startup authorization, no
pending replacement or request/response receipt, and an empty account gate.

Incomplete proof returns a stable `retirement_evidence_*` reason plus an
automatic system next action. It never opens or reads the retired Chat, creates
a replacement, or asks for a product decision. This is local controller
evidence only; the real App continuation remains a separate Beta gate.
