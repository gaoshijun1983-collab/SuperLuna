# SuperLuna 0.2.0-alpha.61

Alpha 61 fixes a real recovery stall after a ChatGPT account cooldown.

## What changed

- A recovered packet with no prior exact match in the fixed Chat is now treated
  as not yet sent and continues to the existing one-shot first-send gate.
- One exact match with trusted request identity still reconciles without
  resending.
- Multiple matches, changed payloads, invented identity, wrong Chat, expired
  leases, or missing account authority remain fail-closed.
- The zero-match decision is read-only and does not mutate workflow state.

## Evidence boundary

Focused local regressions cover the zero-match first-send path, the existing
one-match no-resend path, invented identity rejection, and ambiguous-match
rejection. Final repository totals and package/archive verification remain
pending until release validation finishes. Public Beta remains blocked.
