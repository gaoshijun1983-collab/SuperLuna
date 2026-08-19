# SuperLuna 0.2.0-alpha.87

Controller 143 / Skill `2026-08-19.100` fixes the conceptual path error found
in the Alpha 86 real-App rollover retest.

- `superluna_repo_retest_v1` keeps implementation writes and execution locked
  to its task fixture while deriving reviewer Git evidence from the trusted
  SuperLuna source checkout recorded by the exact retest scope.
- Generic Git projects derive the reviewer source from the selected project's
  containing Git toplevel. Non-Git projects retain full-source attachment mode.
- State now persists a separate local reviewer repository root plus canonical
  remote, exact commit, tree manifest, and repository identity. These local
  paths are never reviewer-visible evidence.
- Old states start unresolved and migrate through the same preparation action;
  injected roots, changed checkout identity, symlinks, and cross-checkout
  mismatches fail closed before browser initialization.

All completion evidence for this candidate is local. The replacement Chat must
still prove access to the exact commit and both canary blobs.
