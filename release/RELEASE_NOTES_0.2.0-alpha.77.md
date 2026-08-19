# SuperLuna 0.2.0-alpha.77

Controller 133 / Skill revision `2026-08-18.90` closes the pre-browser reviewer
budget gap. The account-browser gate now checks the exact state before issuing
any permission, atomically enters `rollover_pending` at 2/2 formal reviews, and
denies old-Chat initialization, navigation, history reads, and sends.

The original browser-capable implementation task owns one replacement-Chat
provisioning chain. A creation failure records one idempotent recovery identity
as `rollover_blocked`; it never becomes `review_waiting` and cannot create a
second task, Chat, or send. Local validation does not replace real macOS or
Windows closed-loop evidence, so Public Beta remains blocked.
