# SuperLuna 0.2.0-alpha.50

This technical-testing Alpha packages Controller 103 / Skill revision
`2026-08-13.60`. Controller 98 completed
three consecutive isolated macOS browser-review rounds without coordinator
follow-up. It remains an Alpha and does not claim Public Beta readiness.

## Changes since alpha.49

- Makes the post-submission one-shot platform wait a machine-readable host
  barrier and preserves its exact identity through creation, binding, firing,
  deletion, and reply consumption.
- Binds every run to its own controller-owned identity so older messages in a
  reused reviewer Chat cannot rename or count the current run.
- Preserves a confirmed submission lease across same-task guards and hands a
  validated scheduled reply lease directly to `apply_result`.
- Requires the exact `resume-from-reply` command after a staged browser reply;
  the ambiguous `resume` abbreviation is explicitly forbidden.
- Adds a deterministic tracked-source release builder, embedded SHA-256 source
  manifest, archive verifier, and standalone checksum file.
- Prevents a completed Chat provisioning step from being classified as
  unresponsive based only on duration. A verified filled composer and enabled
  send control must continue; only an explicit failure/timeout may stop it.
- Keeps Reviewer Chat submission independent from Git commit/push unless the
  user or project acceptance contract explicitly requires a commit identity.
- Rejects the temporary `/c/WEB:<uuid>` route exposed during some in-app-browser
  Chat provisioning. The same initialized conversation must be resolved to and
  verified at its unique canonical URL before state creation.
- Requires the implementation identity supplied to `init` to match the host's
  `CODEX_THREAD_ID`; a delegation source identity cannot become the writer,
  account-gate, run-binding, or waiting owner.
- Recognizes a narrow “唯一最小后续动作” section and negative diff evidence such
  as “no other added, modified, or deleted paths” as a low-risk review request;
  affirmative project deletion is still gated for user decision.
- Rejects a truncated ChatGPT request UUID before submission confirmation can
  change state; the existing sent message must be reread and never resent.
- Preserves an opaque browser id beginning with `-` instead of letting argparse
  mistake it for a new option; documentation uses `--browser-id=<full-value>`.

## Validation

- 291 repository tests pass locally.
- 15 controller self-tests pass.
- Skill and plugin validators pass.
- GitHub Actions run 31650407444 passed on Windows, macOS, and Ubuntu with
  Python 3.11 and 3.13.
- Rebuilding the archive from the same tracked source produces the same bytes
  and SHA-256 digest; the verifier rejects missing, extra, or changed files.

## Status and known limitations

This release is for technical testers. The clean C27 result is isolated
transport evidence rather than a real-project Beta cycle. Ten consecutive real
project cycles without outside wakeups, the Windows/macOS browser compatibility
matrix, and real rate-limit/network recovery evidence remain incomplete.

Install with `bash scripts/install-skill.sh` on macOS/Linux or
`scripts\\install-skill.ps1` from PowerShell on Windows.
