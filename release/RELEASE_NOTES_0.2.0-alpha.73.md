# SuperLuna 0.2.0-alpha.73

Controller 129 / Skill revision `2026-08-17.86` fixes repository self-retest
continuity after an explicitly terminated failed cycle.

- The same implementation task may reset and reuse its exact hashed repository
  sandbox only after all action leases and waiting identities are retired.
- A different task still cannot reuse that state; it must receive a new
  task-local sandbox.
- This is local controller evidence only. Real macOS and Public Beta gates stay
  blocked until their recorded evidence is complete.
