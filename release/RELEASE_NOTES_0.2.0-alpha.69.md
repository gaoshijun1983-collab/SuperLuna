# SuperLuna 0.2.0-alpha.69

Controller 125 / Skill revision `2026-08-17.82` fixes a repository self-retest
ending at a stage boundary instead of continuing the authorized development
loop.

## Changed

- `superluna_repo_retest_v1` always uses `goal_mode=continuous`.
- Legacy repository-retest states stored as `single_stage` are interpreted as
  continuous when reopened.
- Starting the next authorized goal after the active reviewer Chat reaches 2/2
  formal reviews immediately retires the old Chat and requires one replacement.
- The old Chat cannot be reopened or reconfirmed during this handoff.

## Scope

This is a local controller and workflow-contract fix. It does not count as a
real macOS or Windows loop, and SuperLuna remains an early technical Alpha.
