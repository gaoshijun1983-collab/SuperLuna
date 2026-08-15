# SuperLuna project state

## Objective

Ship a safe Codex plugin that lets one implementation task develop, submit to
one active bounded ChatGPT web Chat at a time for independent review, consume
the paired reply once, roll over safely, and continue without coordinator
intervention.

## Success criteria

- One writer, one active reviewer Chat at a time, one state-local review run.
- At most eight formal reviews per Chat; a rate-limited Chat is never reopened.
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
- Exact-URL fixed-Chat recovery after browser restart: reuse one visible match
  without navigation or open once when absent; ambiguity fails closed.
- Formal review-title validation plus complete post-request assistant pairing;
  fragments remain pending and the fixed Chat tab is preserved for handoff.
- Repository-local self-retest profile plus installed `generic` compatibility.

## Completed and verified

- Source candidate: `0.2.0-alpha.63`, Controller 119, Skill `2026-08-14.76`.
- Repository tests: 353/353; controller tests: 250/250.
- Controller selftest: 15/15.
- Milestone, Skill, and plugin validators pass.
- Beta evidence matrix and CI truth validator are present; all six real-device
  gates remain explicitly blocked and cannot be promoted by local/mock evidence.

## Locked decisions

- Product remains a Codex plugin, not a standalone desktop app.
- New runs use the in-app browser; legacy App Chat state is compatibility only.
- SuperLuna never changes model or reasoning level automatically.
- Local validation never counts as real-device or Public Beta evidence.

## Constraints and risks

- Alpha 63 archive and deterministic verification are complete.
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
