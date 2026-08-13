# SuperLuna 0.2.0-alpha.53

Alpha 53 packages Controller 109 and Skill revision `2026-08-13.66`.
It supersedes Alpha 52 without rewriting the already published Alpha 52 tag.

## What changed

- Fixed the repository self-retest workspace probe on Windows. Python on
  Windows does not support the Unix `dir_fd` form used by Alpha 52.
- The Windows path keeps the exact task-derived project/state scope, rejects
  symlink or reparse-point drift, and checks directory identity before and
  after the bounded write probe.
- macOS and Linux retain the directory-file-descriptor implementation.
- Added a regression for the Windows-compatible branch; all existing
  out-of-scope, adjacent-run, and symlink-escape checks remain intact.

## Verification

- Repository tests: 328/328.
- Controller selftest: 15/15.
- Skill and plugin validators: passed.
- Final archive: pending rebuild after the cross-platform CI result.

## Status

This is a technical-testing Alpha, not a Public Beta. Real consecutive project
cycles, platform coverage, host continuation enforcement, and real browser
network/rate-limit recovery remain release blockers.
