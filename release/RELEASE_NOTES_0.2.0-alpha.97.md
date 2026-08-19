# SuperLuna 0.2.0-alpha.97

Controller 153 / Skill `2026-08-19.110` closes the legacy task-binding
registration gap observed after Alpha 96 repository rollover recovery.

An ordinary guard can now reconstruct exactly one missing binding-registry
entry for an existing `superluna_repo_retest_v1` state. Recovery requires the
current host task ID, the persisted implementation and reviewer IDs, a trusted
compatible review-run binding, the exact retest scope, and the canonical host
Codex root to agree. The registry update is serialized and idempotent; an
identity conflict, generic/external scope, unrecorded run binding, incompatible
schema/version, or host mismatch fails closed.

Doctor exposes the same non-sensitive prerequisite map and stable
`task_binding_recovery_*` reason in Chinese and English. No recovery path opens
or reads the old Chat, initializes a browser, sends a message, or creates a
second waiting task. A successful rebuild continues the already-persisted
replacement rollover generation.

This release has local controller and repository evidence only. The original
NPC state still requires one real App continuation to prove that its exact
legacy evidence rebuilds the binding and advances to the existing replacement
startup path.
