# SuperLuna 0.2.0-alpha.90

Controller 146 / Skill `2026-08-19.103` closes the Alpha 89 legacy-state
compatibility gap for an account cooldown that is still active.

- Guard and show-status recognize an old `controller_error/external_blocked`
  only when the account gate proves the exact task, state identity, reviewer
  generation, repository identity, active cooldown, and absence of task slots.
- Guard atomically restores the unsent submission and creates one RDATE-bound
  recovery. An existing matching recovery is reused; show-status reports its
  available/bound state without mutating the workflow.
- Identity drift, missing evidence, uncertain slots, and conflicting waits keep
  the state unchanged and grant no browser or Chat access.
- All technical projections keep `user_choice_required=false` and expose one
  concrete system next action.

This candidate has local evidence only. Real App cooldown-expiry recovery is
still outside this validation boundary.
