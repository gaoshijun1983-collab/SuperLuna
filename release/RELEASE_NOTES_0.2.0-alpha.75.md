# SuperLuna 0.2.0-alpha.75

Controller 131 / Skill revision `2026-08-18.88` closes a waiting-state
deadlock found in the repository-local macOS retest.

## Changed

- An ordinary turn entering a waiting state with an expired read claim now
  requests an exact lookup of the single bound platform wait.
- If that wait still exists, SuperLuna rotates the token and updates the same
  task in place.
- If the platform reports `not_found`, SuperLuna clears only the dead binding
  and creates exactly one replacement through the existing bootstrap/bind gate.
- Recovery remains in `review_waiting`, grants no Chat or project access, and
  keeps `user_choice_required=false`.
- Wrong task identity, wrong platform id, non-waiting state, or a live claim
  continues to fail closed without changing state.

## Evidence boundary

Repository regression passed 380/380. Controller selftest 15/15 and the Skill,
plugin, decision-register, milestone, and Beta-evidence validators also passed.

The automated checks are repository-local evidence only. This candidate is
still an Alpha; real macOS/Windows consecutive-cycle and rate-limit evidence
remain required before Public Beta.
