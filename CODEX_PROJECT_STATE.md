# SuperLuna project state

## Objective

Ship a safe Codex plugin that lets one implementation task develop, submit to
one active bounded ChatGPT web Chat at a time for independent review, consume
the paired reply once, roll over safely, and continue without coordinator
intervention.

## Success criteria

- One writer, one active reviewer Chat at a time, one state-local review run.
- At most two formal reviews per Chat identity across run boundaries; the third submission proactively rolls over, bound Chat access is tail-only, and a rate-limited Chat is never reopened.
- No duplicate send/read/apply and no recurring background polling.
- Safe recovery across task, waiting occurrence, browser, and network restarts.
- Real macOS and Windows consecutive-cycle evidence before Public Beta.

## Current capabilities

- Browser-first bounded-Chat review loop with exact request/response identity.
- One wait-bound future check, shared two-slot account gate, and rate-limit
  circuit breaker.
- One cooldown-bound submission recovery that provisions exactly one replacement
  Chat and never reopens the retired long conversation.
- Zero exact packet matches after recovery continue to the ordinary first-send
  gate; one trusted match reconciles without resending; ambiguity stops.
- Same-one-shot recovery when a waiting read claim expires before a real read.
- Exact platform reconciliation for a stale claimed wait: reuse the same
  one-shot when present or rebuild exactly one when the platform reports it
  missing, without Chat or project access.
- Exact-URL fixed-Chat recovery after browser restart: reuse one visible match
  without navigation or open once when absent; ambiguity fails closed.
- Formal review-title validation plus complete post-request assistant pairing;
  fragments remain pending and the fixed Chat tab is preserved for handoff.
- Repository-local self-retest profile plus installed `generic` compatibility.
- Candidate-bound Beta evidence recorder that accepts only repository evidence,
  resets a consecutive streak on failure, and never starts Chat or automation.
- Stable technical-blocker reporting that keeps identity, capability, cooldown,
  browser-slot, and recoverable-wait failures out of the product-decision state.

## Completed and verified

- Source candidate: `0.2.0-alpha.76`, Controller 132, Skill `2026-08-18.89`.
- Alpha 76 repository regression passed 381/381. Controller selftest passed
  15/15; closure-check, Skill, plugin, decision-register, milestone, and
  Beta-evidence validators also passed. Two independent builds produced the
  same verified 98-file source archive. This is local Alpha evidence only.
- Alpha 76 makes the legacy missing-wait compatibility command converge on the
  automatic one-replacement binding barrier. It no longer changes a recoverable
  waiting review to `external_blocked` when an older running task calls it.
- Alpha 75 closes the missing-platform-wait deadlock. An ordinary wake on an
  expired waiting claim can only inspect the exact saved platform task; a found
  task is updated in place, while `not_found` rotates the wait identity and
  creates one replacement through the existing bind barrier. The review remains
  waiting and no Chat, project, or user decision is involved.
- Alpha 75 repository regression passed 380/380. Controller selftest 15/15,
  closure-check, Skill, plugin, decision-register, milestone, and Beta-evidence
  format validators also passed; this remains local-only evidence.
- Alpha 74 separates technical recovery from product decisions. Expected
  controller faults expose a stable reason code and concrete system next action
  with `user_choice_required=false`; only mutually exclusive changes to product
  goal, authorized scope, or risk boundary may show `需要你决定`.
- Alpha 74 repository regression passed 377/377. Controller selftest 15/15,
  closure-check, Skill, plugin, decision-register, milestone, and Beta-evidence
  format validators also passed; this remains local-only evidence.
- A replacement Chat created under a one-time startup slot can bind that same
  live slot from reviewer `none` to its exact canonical Chat identity at the
  visible Extreme-selection gate. This removes the real flow's missing
  reacquisition step without opening the browser twice or weakening identity
  checks.
- A newly provisioned replacement reviewer Chat can atomically continue from
  its one-time `startup` slot to its first `submission` only when exact task,
  scope, state, visible browser, reviewer binding, and Extreme confirmation
  still match; it reuses the same lease/tab and remains tail-only.
- Repository self-retests are always continuous. A stage boundary cannot end
  the run, and an exhausted 2/2 reviewer Chat rolls over before the next goal.
- Continuous goals cannot be downgraded to `single_stage` by implementation-task
  arguments during `begin-new-goal` or retest reset.
- Automatic reviewer Extreme selection is locally covered by exact task/slot/browser/Chat/revision authorization and visible-label confirmation tests.
- Automatic Extreme confirmation now remains valid through submission reopen,
  pre-send reconciliation, and final one-shot send authorization for the same
  task, account slot, browser, reviewer Chat, and request fingerprint.
- Alpha 69 local validation passed: repository 370/370 and controller selftest
  15/15; these results remain local-only and do not satisfy the real macOS or
  Public Beta gates.
- Alpha 70 local validation passed: repository 371/371 plus controller,
  milestone, Beta-evidence, decision-register, Skill, and plugin validators.
  A real replacement-Chat resume still requires macOS evidence.
- Alpha 71 repository regression passed 373/373. The replacement-Chat
  `startup → submission` continuation and its fail-closed negative path are
  locally covered; real visible macOS continuation remains unverified.
- Alpha 72 repository regression passed 374/374. The real replacement-Chat
  flow no longer needs a second startup-slot acquisition after binding: the
  original live slot is promoted only at the exact visible Extreme-selection
  gate, while a mismatched browser or Chat remains fail-closed. Real visible
  macOS continuation remains unverified.
- Alpha 73 adds a narrow same-task repository-retest reset: after an explicitly
  terminated failed cycle and full lease/wait cleanup, the same implementation
  task may reuse its exact hashed sandbox and state. Cross-task handoff remains
  rejected and requires a new task-local sandbox. Repository regression passed
  375/375; this remains local-only evidence.
- Controller selftest: 15/15.
- Milestone, Skill, and plugin validators pass.
- Beta evidence matrix and CI truth validator are present; all six real-device
  gates remain explicitly blocked and cannot be promoted by local/mock evidence.
- Beta evidence is gate-bound, platform-bound, candidate-bound, and checked
  against the full hashed JSON artifact; unrelated files cannot unlock a gate.

## Locked decisions

- Product remains a Codex plugin, not a standalone desktop app.
- New runs use the in-app browser; legacy App Chat state is compatibility only.
- SuperLuna never changes the Codex implementation model; it may automatically
  select Extreme only in the exact bound reviewer Chat under controller authorization.
- Local validation never counts as real-device or Public Beta evidence.

## Constraints and risks

- Alpha 76 source archive and deterministic rebuild verification are complete.
- The current source contains validated but not yet committed Alpha 76 changes;
  it is not a frozen Git candidate until those changes are committed.
- The browser-restart recovery fix still needs a new real macOS loop.
- Controller 119 bounded rollover, permanent rate-limited-Chat retirement, and
  replacement binding are locally regression-tested but still require a fresh
  real macOS loop after the ChatGPT account cooldown ends.
- Public Beta remains blocked by the real-cycle and platform matrix gates.

## Current files

- Controller: `skills/luna-chatgpt-review-loop/scripts/lcrl.py`
- Skill: `skills/luna-chatgpt-review-loop/SKILL.md`
- Tests: `tests/test_lcrl.py`, `tests/test_package.py`
- Release truth: `release/alpha_release_report.json`
- Beta evidence truth: `docs/beta_evidence_matrix.json`
- Decision index: `DECISION_REGISTER.json`

## Idea backlog

- Improve plain-language recovery status after browser identity changes.
- Measure real rate-limit cooldown behavior without increasing polling.

## Next decision point

Freeze the next candidate commit, then collect the six real-device Beta gates
against that exact commit. Run `scripts/validate_beta_evidence.py --require-ready`
before any Public Beta declaration.

## Do not repeat

- Do not test SuperLuna against unrelated project repositories.
- Do not reopen a retired reviewer Chat or keep two reviewer Chats active.
- Do not claim Beta readiness from unit tests, mocks, or `closure-check`.
