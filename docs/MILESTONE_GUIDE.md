# Versioned milestone and rollback guide

The machine-readable contract is [`docs/milestones.json`](milestones.json).
Run `python -B scripts/validate_milestones.py` before accepting a milestone.

Each milestone must identify its version, upgrade prerequisites, rollback
triggers, rollback steps, and verification method. A rollback is bounded to the
milestone diff and must preserve the failing output for diagnosis.

The current `0.2.0-alpha.44` entry is local-only evidence. Repository tests,
controller selftest, and `closure-check` do not prove real Windows/macOS device
behavior and do not prove Public Beta readiness. Those gates remain false until
the release report records their required evidence.
