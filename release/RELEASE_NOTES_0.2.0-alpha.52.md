# SuperLuna 0.2.0-alpha.52

This technical-testing Alpha packages Controller 108 and Skill revision
`2026-08-13.65` in a deterministic tracked-source archive with an embedded
SHA-256 manifest and standalone checksum.

Visible one-shot wait prompts now lead with concise Chinese and English status
guidance. Users are told that no action is needed; required controller commands
remain in a clearly labeled internal section.

A claimed one-shot wait can no longer inherit the normal waiting-state
permission to end. Once a complete reply is available, the same task must
resume, apply the reviewed operation, and prepare the next submission in the
same turn.

## What changed

- SuperLuna's own source-repository development and real-loop retests now use
  the dedicated `superluna_repo_retest_v1` profile.
- Every implementation task receives one deterministic in-repository fixture:
  `.superluna/retest-runs/<task-hash>/project`, with state fixed to the sibling
  `.superluna/retest-runs/<task-hash>/state.json`.
- Repository-root writes, ordinary source children, adjacent runs, symlink
  escapes, and external absolute paths fail closed before the workspace probe,
  state use, account-browser gate, or browser initialization.
- Account-browser leases retain the profile and project scope so a task cannot
  acquire browser access under one sandbox and continue under another.
- The tracked `.codex/config.toml` supplies a host `workspace-write` boundary to
  newly started trusted-project tasks, excludes system temporary directories,
  and disables shell-network access. This setting is not asserted to
  retroactively change the permissions of an already-open task.

## Compatibility

The repository self-retest profile is development-only. Publicly installed
SuperLuna continues to use the `generic` profile for a user's explicitly
selected, host-authorized external project. Compatibility identifiers remain:

- plugin ID: `luna-review-loop`
- Skill/folder: `luna-chatgpt-review-loop`
- command: `lcrl`

## Evidence boundary

This release introduces a local isolation contract. It does not add a completed
real-project cycle, a Windows/macOS compatibility result, or real ChatGPT
network/rate-limit recovery evidence. Public Beta remains blocked and
`public_beta_ready` remains `false`.

The current source passes all 327 repository checks. The controller's 15
selftests and closure check pass, and both Codex validators pass. The final
archive contains 66 tracked source files plus its embedded SHA-256 manifest;
two independent builds are byte-identical and the archive verifies against the
current source. These are local release-candidate facts and do not promote the
Public Beta gate.
