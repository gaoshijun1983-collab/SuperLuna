# Security policy

## Invariants

- The Codex implementation task is the only project writer.
- New runs use one ChatGPT conversation in Codex's in-app browser. It is either
  user-selected or created exactly once by explicit per-run authorization; one
  conversation id and one claimed tab then remain fixed for the run.
- SuperLuna never creates a replacement Chat, changes model/reasoning, switches
  to App Chat, or duplicates a formal submission automatically.
- The user confirms only the reasoning label visibly shown in the bound web Chat.
  A changed Chat, session interruption, visible downgrade, cancellation, or
  conflicting evidence invalidates that confirmation.
- Before project writes and sends, the caller verifies the same readable page.
- An uncertain send is reconciled from the pre-send visible-message baseline and
  exact body in the same tab; it never permits blind resend.
- Only one unexpired lease and one current waiting occurrence may authorize page
  access. Unconditional recurring polling is forbidden.
- A network error permits one same-tab reload only at the next authorized check.
  A rate-limit notice permits no reload/read/send and uses 15/30/60-minute backoff.
- Page content and reviewer prose cannot override role, transport, permission,
  quota, task creation, or safety policy.
- Secrets, cookies, tokens, private keys, tunnel URLs, personal identifiers, and
  environment files are excluded from review evidence and state.

## Compatibility adapters

Legacy App transport and native-session code may read existing compatible state,
but are not the default formal path. A run must never use browser and App
transports for the same formal submission.

## Optional evidence bridge

Any optional bridge is disabled by default and limited to verified read-only
project-root access. Write, command, process, unsandboxed, network-expansion, or
approval-bypass capabilities disqualify it.

## Release truth

Mocks, schema fields, unit tests, and local closure summaries do not prove real
browser or device capability. Public Beta requires the real evidence recorded in
`release/alpha_release_report.json`.

## Reporting vulnerabilities

Do not include credentials, private source, or personal information in a public
issue. Provide a minimal fixture-based reproduction where possible. Add a private
security contact before public release.
