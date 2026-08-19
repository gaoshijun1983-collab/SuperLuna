# SuperLuna 0.2.0-alpha.93

Controller 149 / Skill `2026-08-19.106` closes the legacy replacement-retirement
gap observed after Alpha 92. A replacement Chat can be durably bound before a
real rate limit appears, while the older startup slot may still have been
released as `reviewer_thread_id=none` and no ephemeral review-mode lease ever
existed.

The one-time compatibility migration now requires a unique startup
authorization, exact task/scope/state/repository identity, the prior reviewer
generation, a canonical provisioned browser and provider binding, a consistent
authorization/binding/replacement timestamp chain, no current-generation
request or response receipt, the same task's recorded rate limit, and a globally
empty account slot set. It writes one deterministic rebuild identity and one
retirement record. Missing binding evidence, identity drift, or any active or
uncertain slot remains fail-closed and leaves the account gate unchanged.

This is local Alpha evidence only. It does not claim a successful real App
recovery, real Chat access, or Public Beta readiness.
