# SuperLuna 0.2.0-alpha.86

Controller 142 / Skill `2026-08-19.99` closes the repository canary gap found
during the Alpha 85 real-App recovery retest.

- The repository now tracks a stable, non-sensitive root canary and nested
  canary specifically for exact-commit reviewer access verification.
- Repository preparation selects the dedicated pair atomically and verifies
  that both entries are regular committed blobs with exact blob SHA values.
- Missing, partial, symlinked, or mismatched dedicated canaries fail closed
  before browser initialization. Generic repositories without the dedicated
  pair retain safe regular-file canary discovery.

All completion evidence for this candidate is local. A replacement Chat must
still independently open the exact commit and match both blob canaries.
