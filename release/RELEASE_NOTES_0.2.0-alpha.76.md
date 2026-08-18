# SuperLuna 0.2.0-alpha.76

Controller 132 / Skill revision `2026-08-18.89` closes a compatibility-path
deadlock found by the repository-local macOS retest. When the platform proves
that a bound one-shot wait is missing, both current and legacy controller entry
points now preserve `review_waiting` and require exactly one replacement wait
to be created and bound. They do not access Chat or the project and do not ask
the user to make a product decision.

States already changed to `external_blocked` by the retired behavior are also
repaired on the next exact implementation-task turn entry. The repair requires
the durable platform `not_found` proof and cannot cross task identity.

This is local Alpha validation only. Public Beta still requires the recorded
real-device and consecutive-cycle evidence gates.

## Local validation

- Repository tests: 381/381 passed.
- Controller selftest: 15/15 passed.
- Closure, Skill, plugin, decision-register, milestone, and Beta-evidence
  validators passed.
- Two independent builds produced the same verified archive from 98 tracked
  source files.

The archive matches the current local Alpha 76 source. The source still needs a
frozen Git commit before real-device Beta evidence can be attributed to an exact
candidate.
