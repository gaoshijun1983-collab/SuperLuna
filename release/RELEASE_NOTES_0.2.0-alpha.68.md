# SuperLuna 0.2.0-alpha.68

Controller 124 / Skill revision `2026-08-17.81` changes ChatGPT rate-limit
handling from reactive recovery to proactive prevention.

## Changed

- One exact reviewer Chat may complete at most two formal reviews across run and
  goal boundaries. The third submission is stopped before browser access and
  requires the existing single-Chat rollover flow.
- Every normal operation on an already bound reviewer Chat is explicitly
  tail-only. Full-history scanning is denied even before a rate limit is seen.
- Older states adopt the current safety cap instead of retaining a more
  permissive historical value.

## Evidence boundary

The repository regression suite and validators prove the local controller
contract only. They do not prove that ChatGPT will never apply an account limit,
and this candidate remains pre-Beta until the recorded real-device gates pass.
