# SuperLuna 0.2.0-alpha.54

Alpha 54 source packages Controller 110 and Skill revision `2026-08-13.67`.
Final archive construction and verification remain pending.

## What changed

- Fixed a one-shot waiting gap found during the NPC AI run. A due waiting task
  could claim Chat-read authority and then exit before the browser was read;
  because its original RDATE had already fired, no future occurrence remained.
- The controller now requires the same platform waiting task to be moved to the
  read-claim expiry and confirmed before browser initialization is authorized.
- If the occurrence exits after claiming, that same task can fire at claim
  expiry, recover the stale claim, and continue. No recurring or second
  scheduler is introduced.
- Recovery identity is cleared whenever the wait is recovered, normally rearmed,
  consumed, or retired, so queued old occurrences remain ineffective.

## Verification scope

- Focused local controller regressions cover missing recovery confirmation,
  exact RDATE/lease matching, stale-claim recovery, and re-authorization.
- Repository tests pass 330/330; controller selftest passes 15/15; milestone,
  Skill, and plugin validators pass. Final archive verification is still pending.
- These local checks are not real macOS/Windows App evidence and do not satisfy
  the Public Beta gate.
