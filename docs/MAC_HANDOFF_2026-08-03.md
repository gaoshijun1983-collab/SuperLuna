# SuperLuna Mac handoff

This handoff covers the browser-first source update after Alpha 27. The archive
contains only older packaged source; controller 21 / Skill revision
`2026-08-09.10` is currently an unpackaged source update.

## Install and start

```bash
bash scripts/install-skill.sh
python3 ~/.codex/skills/luna-chatgpt-review-loop/scripts/lcrl.py selftest
python3 -B -m unittest discover -s tests -v
```

Start a completely new Codex task so it discovers the installed Skill. Do not
copy Windows state, registry, automation, session-log, task, or Chat identities.

1. Open the implementation project in Codex Desktop on the Mac.
2. In Codex's in-app browser, open or select one ChatGPT web conversation. The
   user creates a new Chat manually if needed.
3. Confirm its URL conversation id, claim that exact tab, and verify the page is
   readable before project writes.
4. Manually select and confirm the visible reviewer reasoning mode. SuperLuna
   does not change it.
5. Invoke `$luna-chatgpt-review-loop` and initialize a new Mac-local
   `in_app_browser` binding.
6. Verify there is no unconditional recurring recovery task. Only receipt/reply
   waiting may have one future identity-gated check.

## Required real tests

- one full submit/wait/read/continue cycle in the same web Chat and tab;
- a long streaming reply without refresh or duplicate send;
- ordinary network/load failure followed by one same-tab reload at the next
  180-second authorized check;
- a rate-limit notice with no reload/read/send and 15/30/60-minute backoff;
- sleep/wake and Codex restart without cross-Chat reads or duplicate project work;
- ten consecutive cycles without coordinator messages or user “continue”.

Record macOS, Codex Desktop, Python, visible selector behavior, and exact failures
without including private Chat content or identifiers. See
`docs/MACOS_TEST_PLAN.md`.

## Known limits

- App adapters remain compatibility code and do not prove the browser-first path.
- Real Windows/macOS browser matrices and real recovery are still unverified.
- Mocks, unit tests, and `closure-check` are local evidence only.
- Public Beta remains false.

## Rollback

Pause any workflow using the Skill, then remove only the installed
`~/.codex/skills/luna-chatgpt-review-loop` directory or restore a separately
saved prior Skill backup. Do not delete project source. Do not copy live state
into the repository.
