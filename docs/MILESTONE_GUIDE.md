# Versioned milestone and rollback guide

The machine-readable contract is [`docs/milestones.json`](milestones.json).
Run `python -B scripts/validate_milestones.py` before accepting a milestone.

Each milestone must identify its version, upgrade prerequisites, rollback
triggers, rollback steps, and verification method. A rollback is bounded to the
milestone diff and must preserve the failing output for diagnosis.

The current `0.2.0-alpha.52` entry adds a repository-local self-retest sandbox.
The dedicated `superluna_repo_retest_v1` profile accepts only the implementation
task's deterministic `.superluna/retest-runs/<task-hash>/project` fixture and
sibling `state.json`; it rejects out-of-scope paths before probes, state use,
the account gate, or browser initialization. The installed product's `generic`
profile remains available for user-selected, host-authorized external projects.

Repository tests, controller selftest, `closure-check`, and the sandbox contract
remain local-only evidence. They do not prove real Windows/macOS device behavior
or Public Beta readiness. Those gates remain false until the release report
records their required evidence. Final test totals, tracked-source count, and
deterministic archive proof must come from the final release validation.
