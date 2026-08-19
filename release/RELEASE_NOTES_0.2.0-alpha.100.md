# SuperLuna 0.2.0-alpha.100

Controller 156 / Skill `2026-08-19.113` fixes the actual persistence mismatch
found by the Alpha 99 real-machine read-only diagnosis.

The controller previously treated an OS-temporary account-browser gate as the
default authority, while the host's restart-durable SuperLuna gate lives at
`$CODEX_HOME/superluna/account-browser-gate.json`. After OS cleanup, Alpha 99
looked only for a missing temporary/default gate and therefore returned
`retirement_evidence_registry_unavailable` even though a valid persistent gate
file existed.

New account-gate operations now default to the persistent host location.
Repo-retest retirement diagnostics discover that gate after a legacy temporary
path disappears and evaluate the normal evidence matrix. Discovery does not
create evidence: a gate lacking the exact task's rate-limit record or startup
authorization returns those stable missing-evidence codes and remains blocked.

The real Alpha 99 gate was present and valid but did not contain those two facts
for the current task. Alpha 100 therefore improves persistence and diagnosis;
it does not claim that the existing NPC rollover can be safely retired from the
available evidence.
