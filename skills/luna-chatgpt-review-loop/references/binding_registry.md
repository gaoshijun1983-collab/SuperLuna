# V8 P0 binding registry

## Purpose

Keep exactly one formal Chat reviewer bound to each implementation task. A legacy recovery automation ID may remain during migration, but new foreground-only bindings use `none`. Treat stable Work and Chat IDs as truth and titles as a user-facing projection.

## Registry location

Store the mutable registry outside the Skill directory, normally at:

```text
<codex-root>/lcrl/registry/tasks.json
```

Use schema [task_registry_schema_v1.json](task_registry_schema_v1.json).

## Readable title contract

Generate titles with the controller; do not hand-build variants:

```text
🛠 <display_name>｜执行｜<iteration>
💬 <display_name>｜评审｜<iteration>
⏳ <display_name>｜等待｜<iteration>
```

Keep `display_name` at most 12 characters and each iteration/status component at most 12 characters. The leading symbols form a fixed visual role set; use identical `display_name` and `iteration` for all three surfaces. Model and reasoning choices are deliberately excluded because they can change without changing the binding.

`register-binding` returns `title_actions`. The active task must apply the implementation-task title with the Codex task title tool, apply the reviewer title only to the already selected dedicated Chat, and use the waiting title for any one-shot waiting check. Then it must verify the visible titles before the first formal submission. The controller records intent; it cannot silently rename App surfaces by itself.

Update titles only on initial binding, iteration change, blocker, completion, or handoff. Never rename from a heartbeat poll.

## Uniqueness

Require every active registry entry to have a unique:

- `task_id`
- `implementation_thread_id`
- `reviewer_thread_id`
- `automation_id`, only when a legacy automation still exists

Reject a second formal Chat for one Work, a Chat reused by two Works, duplicate legacy automations, or stale generated titles. Do not create a new task, Chat, or automation to repair a naming problem.

## New Chat discovery

The App orchestration layer may remove manual ID copying by taking a read-only `list_threads` snapshot before the user creates a regular Chat and another snapshot afterward. Pass both snapshots to `discover-reviewer-chat`. The controller considers only `kind=chatgpt`, never creates state or a registry entry, and returns one confirmation candidate only when the new stable identity is unambiguous. Zero or multiple candidates fail closed. A visible title may narrow the candidates but never replaces the stable ID or the user's confirmation.

## Recovery

For a legacy `superluna_repo_retest_v1` state whose registry entry is missing,
ordinary `guard` may rebuild exactly one entry without user input only when the
current host task ID, persisted implementation ID, trusted review-run binding,
reviewer ID, state schema/controller/Skill contract, exact retest scope, and
host Codex root all match. The operation is serialized by the registry lock and
is idempotent. `doctor --implementation-thread-id <current-task-id>` exposes the
same non-sensitive prerequisite map and stable `task_binding_recovery_*` reason.
Generic projects, external paths, unrecorded run bindings, version drift, or
registry identity conflicts remain fail-closed and grant no browser or Chat
access.

Identity diagnostics never echo task IDs. For each guard argument, host thread,
auxiliary host session, state, review-run binding, and registry entry they expose
only presence, representation kind, length, and 12-character raw/normalized
SHA-256 prefixes, followed by the exact mismatching source-name pairs. UUID
normalization is restricted to case, braces, and explicit `urn:uuid:`, `thread:`,
or `thread_id:` wrappers. Opaque values and different UUIDs never become aliases.
An unavailable host task-registry API is reported as unavailable rather than
replaced by a title or delegation-source guess.

Coordinator recovery is a separate, read-only projection. With explicit
`caller_role=coordinator_recovery`, the caller must identify itself as the
current host and name the exact original implementation target already present
in both state and trusted run binding. Canonical repo-retest scope is rechecked.
Success authorizes only a one-shot platform wake of the original task; it never
writes this registry, mutates state, reads the project, or grants browser/Chat
authority. Only the original task's later ordinary guard may rebuild a missing
entry. Target, host, run-binding, or scope drift fails closed.

A missing persisted repo-retest retirement-registry path may resolve to the
canonical host account gate only when that already-existing gate passes the
complete task, state scope, repository, generation, startup authorization,
rate-limit, and zero-slot evidence plan. This resolution does not synthesize a
retirement record. Generic states, absent canonical gates, and identity drift
remain fail-closed.

The authoritative account-browser gate lives at
`$CODEX_HOME/superluna/account-browser-gate.json`; OS temporary storage is not
restart-durable authority. Legacy temporary paths may be read for compatibility,
but persistent-gate discovery only changes the diagnostic source. Every normal
identity, scope, generation, authorization, rate-limit, and zero-slot check still
applies before any retirement or continuation write.

When those three historical facts are permanently unrecoverable for one legacy
repo-retest generation, the controller may seal the generation instead of
claiming retirement. The seal requires the exact task/run binding, repository
identity and generation, prior rate-limit lineage, replacement binding timestamp
chain, zero current message receipts, zero waits, and zero active slots. It
records hashes and the missing-evidence matrix, authorizes one clean replacement
startup, and never adds a rate-limit retirement record. Generic projects cannot
use this recovery.

If a user manually renames a surface, keep the binding because its stable ID is unchanged. Regenerate and apply the expected title at the next explicit naming event. If an ID changes, invalidate the confirmation lease and require the user to select the replacement Chat.

If registry and state diverge, stop formal submission, run `doctor-registry` and `doctor`, then re-register the existing stable IDs. Never infer identity from a similar title.
