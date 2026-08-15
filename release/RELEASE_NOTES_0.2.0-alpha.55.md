# SuperLuna 0.2.0-alpha.55

Alpha 55 source packages Controller 111 and Skill revision `2026-08-13.68`.
Final archive construction and verification remain pending.

## What changed

- Fixed a real-loop submission deadlock after Codex Desktop restarted its
  in-app browser. The fixed reviewer Chat could already be visible under the
  new browser identity, while the normal send gate still required the old id
  and the recovery gate expected the tab to be absent.
- Submission recovery now consumes exact-URL counts from both current tab
  listings. It claims one visible exact fixed Chat without navigation, opens
  the stored canonical URL once only when both counts are zero, and rejects
  multiple matches.
- A live implementation entry lease is atomically upgraded to the ten-minute
  submission recovery lease. The candidate browser id remains transient until
  the existing page checks, one-shot send authorization, and submission
  confirmation all succeed.
- Controller 110's same-one-shot waiting-claim recovery remains included.

## Verification scope

- Focused local controller regressions cover visible exact-Chat reuse,
  browser-id commit only after confirmation, the prior missing-tab reopen path,
  and ambiguous-match rejection.
- Repository tests pass 333/333; controller selftest passes 15/15; milestone,
  Skill, and plugin validators pass. Final archive verification remains pending.
- Local checks are not real macOS/Windows App evidence and do not satisfy the
  Public Beta gate.
