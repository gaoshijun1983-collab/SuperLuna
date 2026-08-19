# SuperLuna 0.2.0-alpha.102

Controller 158 / Skill `2026-08-19.115` separates coordinator recovery
inspection from implementation authority.

An explicitly identified coordinator may run a read-only recovery projection
only when its guard identity matches the current host, the requested target is
the exact implementation identity recorded by state and trusted run binding,
and the repository-retest scope is canonical. Success returns one platform
wakeup action for the original implementation task. It performs no project,
state, registry, browser, or Chat access and cannot rebuild the binding.

The awakened original task must still run ordinary guard with its stable task
identity before any implementation continuation. Target, host, run-binding,
schema, or scope drift returns a stable `coordinator_recovery_*` reason with
`user_choice_required=false`.

This is local controller evidence only. It does not prove a real App recovery
or reviewer Chat loop.
