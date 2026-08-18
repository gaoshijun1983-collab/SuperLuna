# SuperLuna 0.2.0-alpha.67

Controller 123 / Skill revision `2026-08-17.80` closes a continuous-development
contract gap found during the repository-local NPC AI retest.

An implementation task could previously pass `single_stage` to
`begin-new-goal` even when the existing goal was already `continuous`. A single
review round could then be recorded as overall completion, making later plain
“continue” requests appear to require a new goal.

This candidate rejects that downgrade before changing state. The same rule
applies to retest reset. Existing single-stage workflows remain compatible, and
continuous workflows continue to require explicit overall-completion evidence.

Local validation does not satisfy the real-device or Public Beta gates.
