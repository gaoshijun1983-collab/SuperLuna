# SuperLuna 0.2.0-alpha.49

This is the first public open-source release of SuperLuna: a Codex plugin,
bundled Skill, and deterministic standard-library Python controller for a
browser-first development review loop.

```text
Codex implements -> one bound ChatGPT web conversation reviews -> the same Codex task continues
```

## Highlights

- One implementation writer and one explicitly bound reviewer conversation.
- Durable state, revision checks, action leases, and fail-closed identity gates.
- Duplicate-send and duplicate-reply-consumption protection.
- Waiting checks are valid only while waiting for Chat and are invalidated on
  every state or wait-identity change.
- Read-only multi-run observation with the exact 20-minute stall boundary.
- Windows atomic persistence tolerates only short transient sharing violations;
  persistent permission failures still fail closed.
- English primary documentation, Chinese guidance, MIT license, security policy,
  contribution guide, and machine-readable release evidence.

## Validation

- 209 repository tests passed locally.
- 15 controller self-tests passed.
- GitHub Actions passed on Windows, macOS, and Ubuntu with Python 3.11 and 3.13.
- Skill, milestone, package metadata, and source-tree release checks passed.

## Status and known limitations

This release is for technical testers. It is not Public Beta and does not claim
that every Codex Desktop host capability is enforceable by a plugin. Fresh real
macOS tasks did not receive the in-app-browser execution tool in the latest
three startup attempts, so the frozen consecutive real-cycle gate remains 0/10.
Real network/rate-limit recovery and the complete macOS browser matrix remain
open. The exact evidence and blockers are published in
`release/alpha_release_report.json`.

## Install

macOS/Linux:

```bash
bash scripts/install-skill.sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-skill.ps1
```

After installation, start a new Codex task and invoke
`$luna-chatgpt-review-loop`.

License: MIT.
