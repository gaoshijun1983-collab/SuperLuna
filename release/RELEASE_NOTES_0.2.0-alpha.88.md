# SuperLuna 0.2.0-alpha.88

Controller 144 / Skill `2026-08-19.101` closes the zero-side-effect orphan
provisioning gap exposed by the Alpha 87 real-App rollover retest.

- Ordinary turn entry recognizes a consumed replacement-startup provisioning
  only when it is bound to the exact task, state, reviewer generation, and
  prepared repository identity and no browser, Chat, send, read, or slot side
  effect exists.
- `reconcile-orphaned-provisioning` atomically makes that exact authorization
  available once. The next account-slot acquisition consumes it and provisions
  the original generation's single replacement startup; it cannot create a
  second authorization or Chat.
- Missing legacy evidence is accepted only for the exact repository-retest
  scope that itself binds the state path. Generic states require the explicit
  state identity. Identity drift, any browser/Chat receipt, and active or
  expired-but-uncertain slots remain fail-closed.

All completion evidence for this candidate is local. The replacement Chat must
still prove access to the exact commit and both canary blobs in a real App run.
