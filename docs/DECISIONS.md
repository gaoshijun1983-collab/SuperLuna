# Product decisions

This file records confirmed product boundaries. It is not a release claim.

## Product form and identity

- Distribute SuperLuna as a Codex plugin with a bundled Skill and standard-library
  Python controller; do not build a standalone desktop application.
- Preserve plugin ID `luna-review-loop`, Skill/folder
  `luna-chatgpt-review-loop`, and command `lcrl` until an explicit migration.
- The implementation task is the sole project writer.

## Formal reviewer transport

- New runs use one active user-selected ChatGPT conversation at a time in
  Codex's in-app browser.
- A reviewer conversation is bounded to eight formal reviews. Before a ninth
  review, or immediately after a real rate-limit notice, retire it permanently
  and create exactly one replacement conversation with compact current context.
  Never reopen or health-probe a retired conversation, and never keep two
  reviewer conversations active in parallel.
- Bind the conversation id from the URL and claim the same tab for the run. Titles
  and current focus are not identity.
- The implementation task owns submission, waiting, reply retrieval, and
  continuation. A coordinator is not part of the normal loop.
- `app_chat_review` remains readable for existing saved state only; do not switch
  transports mid-cycle or duplicate a submission.
- Before project writes and every send, verify the bound page is readable and is
  still the same Chat.
- After an in-app-browser restart, submission recovery must count the fixed
  Chat's exact URL in both current tab listings. Claim one visible exact match
  without navigation; open the saved URL once only when both counts are zero;
  reject ambiguity. Commit a changed browser identity only after the existing
  one-shot send gate and submission confirmation succeed.

## Waiting and recovery

- Unbounded recurring execution is retired. Only a receipt/reply wait may own one
  future identity-gated check.
- When a due wait claims Chat-read authority, that same platform wait must first
  move to the claim-expiry recovery time and be confirmed in state. Browser read
  remains denied until confirmation. If the occurrence exits before reading,
  the same wait recovers the expired claim; no second scheduler is created.
- A healthy page is read without refresh. A network/load failure schedules one
  check 180 seconds later, which may reload the same tab exactly once.
- A “requests are too frequent” notice is not a network error: perform no reload,
  history read, or send; retire that reviewer conversation, respect the shared
  cooldown, then create one replacement conversation instead of probing the old
  history again.
- Leaving the waiting phase retires the check and invalidates queued occurrences.
- An uncertain send is reconciled in the same Chat and is never blindly resent.

## Model and quota

- SuperLuna never changes the model or reasoning level automatically. The user
  confirms only what is visibly shown in the bound web Chat.
- A task/Chat change, session interruption, user cancellation, visible downgrade,
  or conflicting evidence invalidates the confirmation.
- Model recommendations remain advisory and bounded; they cannot change product
  direction or create a task/Chat.

## Platform and release truth

- Target Codex Desktop on Windows and macOS. Linux remains controller/development
  support until an equivalent browser transport exists.
- Require real browser end-to-end evidence on supported platforms before public
  Beta. Unit tests, mocks, schema fields, and local closure summaries are not
  device evidence.
- Use the MIT License and preserve English primary plus Chinese companion docs.
