# Versioned milestone and rollback guide

The machine-readable contract is [`docs/milestones.json`](milestones.json).
Run `python -B scripts/validate_milestones.py` before accepting a milestone.

Each milestone must identify its version, upgrade prerequisites, rollback
triggers, rollback steps, and verification method. A rollback is bounded to the
milestone diff and must preserve the failing output for diagnosis.

The current `0.2.0-alpha.63` entry prevents one long reviewer conversation from
becoming an unbounded history database. Each active reviewer Chat is limited to
eight formal reviews. Before a ninth review, or after any real rate limit, the
old Chat is retired permanently and exactly one replacement receives compact
current context. Cooldown recovery cannot reopen, refresh, probe, or scan the
retired Chat. It preserves no-resend reconciliation inside the active volume:
zero exact visible matches continues to the ordinary first-send authorization,
one trusted match reconciles without resending, and ambiguity stops. It preserves the
Alpha 59 requirement for formal review labels to match the
controller-owned round, complete replies to be paired after the current request,
and the fixed Chat tab to remain available for handoff. It also preserves the
Alpha 58 requirement that every reviewer Chat action show
the exact fixed conversation in the visible Codex in-app browser and rejects a
background-only substitute. The previous `0.2.0-alpha.57` entry fixed expected-
failure mapping lines being misclassified as destructive actions while preserving
real deletion blocking. `0.2.0-alpha.56` added safe no-resend reconciliation when one
already-visible fixed-Chat request lost its short-lived send authorization
before receipt persistence. One exact full-body match with trusted identity may
be recorded; ambiguous or changed evidence is rejected without state mutation.
It retains the exact-URL browser rebind and same-one-shot waiting
claim recovery and the
cross-platform repository-local self-retest sandbox: the dedicated
`superluna_repo_retest_v1` profile accepts only the implementation
task's deterministic `.superluna/retest-runs/<task-hash>/project` fixture and
sibling `state.json`; it rejects out-of-scope paths before probes, state use,
the account gate, or browser initialization. The installed product's `generic`
profile remains available for user-selected, host-authorized external projects.

Repository tests, controller selftest, `closure-check`, and the sandbox contract
remain local-only evidence. They do not prove real Windows/macOS device behavior
or Public Beta readiness. Those gates remain false until the release report
records their required evidence. Final test totals, tracked-source count, and
deterministic archive proof must come from the final release validation.
