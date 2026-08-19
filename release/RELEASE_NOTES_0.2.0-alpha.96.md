# SuperLuna 0.2.0-alpha.96

Controller 152 / Skill `2026-08-19.109` closes the diagnostic bypass that left
some legacy rate-limit retirement failures presented as generic
`controller_error`.

Every missing-retirement path now uses one non-sensitive machine diagnostic.
It reports a Boolean for each controller version, Skill revision, task/reviewer
identity, rate-limited rollover, exact repository, zero-side-effect, slot,
durable rate-limit, browser-binding, and prior-generation authorization
prerequisite. The first failure remains the stable reason code and the complete
ordered missing list is also returned.

Ordinary guard evaluates this evidence before orphan provisioning, and the
direct rollover command returns the same structured technical blocker instead
of throwing a generic error. `diagnose-rate-limit-retirement` is a pure read-only
entrypoint and can explicitly expose installed Controller or Skill revision
drift. No path reads a Chat, initializes a browser, creates a replacement, or
asks for a product choice.

This is local controller evidence only. The original NPC state still requires
one real App continuation to verify which persisted prerequisite is present and
that the unique replacement startup continues.
