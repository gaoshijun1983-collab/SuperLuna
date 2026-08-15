# SuperLuna 0.2.0-alpha.60

Alpha 60 fixes a real automatic-loop stall after ChatGPT rate limiting during
review submission.

## What changed

- A `review_submit_pending` run can now schedule exactly one recovery at the
  shared account circuit's exact cooldown time.
- An early or duplicated recovery occurrence cannot initialize the browser,
  read Chat, send, or write the project.
- At expiry, the one-shot recovery must delete itself before obtaining one
  `health_probe` slot and showing the fixed reviewer Chat in the visible Codex
  in-app browser.
- A healthy probe resumes the same unsent review packet. Another real rate-limit
  notice creates one replacement recovery; recurring polling remains forbidden.
- The waiting prompt remains short, bilingual, and explicit that users do not
  need to run the internal command.

## Local verification

- Repository regression suite: 339/339 passed.
- Controller regression subset: 243/243 passed.
- The focused recovery test covers exact cooldown scheduling, early execution,
  due execution, stale replay, no Chat read, and unchanged submission status.

## Remaining boundary

This is local contract evidence only. A real macOS fixed-Chat recovery is still
required, followed by the existing Windows/macOS release matrix. Public Beta
remains blocked.
