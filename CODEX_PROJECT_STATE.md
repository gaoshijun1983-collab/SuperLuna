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

- Source candidate: `0.2.0-alpha.102`, Controller 158, Skill `2026-08-19.115`.
- Coordinator recovery inspection is now distinct from implementation
  authority. A coordinator whose guard identity matches its host may validate
  the exact original task in state/trusted run binding and request one platform
  wakeup. It cannot read or write the project/state, use browser/Chat, or rebuild
  the binding; only the awakened original task can continue with ordinary guard.
- One repo-retest generation with permanently lost legacy account-gate evidence
  may now be administratively sealed without creating rate-limit or retirement
  facts. The state records the missing-evidence matrix and source hashes, keeps
  the old Chat unreadable, and exposes one normal replacement-startup
  authorization. Message receipts, active waits/slots, task/repository/
  generation drift, or generic profiles block the seal.
- The account-browser gate now defaults to the host-owned persistent
  `$CODEX_HOME/superluna/account-browser-gate.json`, rather than OS temporary
  storage. Repo-retest restart recovery discovers that gate after a missing
  legacy path and exposes the exact incomplete evidence matrix without creating
  retirement facts. The Alpha 99 real gate was found, but it did not contain
  the current task's rate-limit record or startup authorization; that real
  continuation therefore remains correctly blocked.
- A repo-retest state whose persisted temporary retirement-registry path was
  lost may now select the canonical host account gate only when that existing
  gate passes the full task/state scope/repository/generation/authorization/
  rate-limit/zero-slot evidence matrix. No retirement fact is synthesized;
  generic or mismatched evidence remains blocked with zero project/browser/Chat
  access.
- Task-binding recovery diagnostics now identify every trusted source without
  exposing IDs: existence, representation type, length, truncated raw and
  normalized hashes, and exact mismatch pairs. Only strict representations of
  the same UUID normalize; different UUIDs and opaque identity drift remain
  blocked before project/browser/Chat access.
- A legitimate legacy `repo_retest` state whose task binding registry entry was
  lost can now be rebuilt by ordinary guard without user choice. Recovery
  requires the current host task, persisted implementation and reviewer IDs,
  trusted run binding, compatible schema/version, exact retest scope, and host
  Codex root to agree; every mismatch has a stable
  `task_binding_recovery_*` code and zero browser/Chat authority.
- Every missing rate-limit retirement exit now exposes one non-sensitive machine
  diagnostic with all prerequisite booleans and stable missing reason codes.
  Guard evaluates it before orphan provisioning; direct rollover uses the same
  contract. A standalone read-only diagnostic also exposes controller/Skill
  entrypoint mismatch without touching state, registry, browser, or Chat.
- A legacy replacement Chat that rate-limited before an ephemeral mode-selection
  lease existed can now rebuild exactly one retirement record from the unique
  startup authorization, exact task/state/repository and prior-generation
  identities, canonical provisioned browser binding and timestamp chain, zero
  current-generation message receipts, and a globally empty slot set. Missing
  or uncertain evidence leaves the account gate byte-identical.
- Rollover completion can now promote the live startup slot and its unique
  provisioning authorization to the final reviewer Chat, generation, state,
  and repository identity before release. Legacy `none` releases reconcile
  once only from the same startup lease and durable binding receipts; ambiguous
  identities or slots remain fail-closed.
- The real legacy combination `rollover_pending + external_blocked +
  controller_error` now enters the same strict account-rate-limit migration.
  Guard cannot grant ordinary turn entry during the matching cooldown and must
  preserve one RDATE binding as a same-turn completion barrier.
- Guard and show-status now recognize legacy `controller_error/external_blocked`
  as an active account rate limit only when task, state, reviewer generation,
  repository identity, and zero-slot evidence match. Guard atomically restores
  the unsent submission and one RDATE wait; show-status projects without
  mutation. Identity drift remains blocked with zero browser authority.
- Real replacement-startup rate limits now retain `account_rate_limited`
  through top-level errors and status projection. The account gate's exact
  cooldown deadline is authoritative; cooldown has zero Chat access and only
  one RDATE-bound recovery check, whose bound/unbound state is explicit.
- A legacy replacement-startup provisioning that was consumed without any
  browser, Chat, submission, read, or slot side effect can now be atomically
  reconciled once. The reclaim is bound to the same task, state, reviewer
  generation, and repository identity; missing or ambiguous evidence remains
  blocked and no second Chat authorization is created.
- Repository self-retests now keep implementation writes/execution in their
  exact fixture while reviewer Git evidence is derived from the trusted source
  checkout. Generic Git subprojects derive their containing Git toplevel.
  State persists this reviewer repository identity separately without exposing
  its local root to Chat.
- The repository now owns an atomic, tracked reviewer-access canary pair:
  `SUPERLUNA_REVIEW_CANARY.txt` and `review-canary/NESTED_CANARY.txt`.
  Preparation accepts them only as regular exact-commit blobs, returns their
  blob SHAs, and fails closed for a missing half or symlink.
- Ordinary turn entry now routes a legacy attachment-blocked rollover to one
  exact repository preparation command when local repository facts are complete.
  The command additionally proves anonymous exact-commit reachability, restores
  only `rollover_pending`, and leaves the replacement Chat receipt unconfirmed.
- Repository-backed rollover recovery now re-runs exact-commit preparation
  before the attachment capability gate. A successful current repository check
  clears only the stale attachment blocker, restores the unique pending
  replacement continuation, and binds a deterministic structured handoff; the
  replacement Chat still needs its own repository access receipt.
- Complete-source attachment runs now require a host-declared direct upload
  capability before Chat/browser startup and an exact current-composer receipt
  over package identity, names, sizes, and SHA-256 values before text send. One
  controlled retry reuses the same package; a second failure is a terminal host
  capability blocker. Repository-commit mode is unaffected.
- Clean Git-backed projects prefer `repository_commit_review`: canonical remote, repository identity, exact commit, tree manifest, root+nested blob canaries, current-Chat access receipt, and a separately verified base→head round manifest. Any unreachable/dirty/unverified case falls back to the complete source attachment package.
- Formal review is context-receipt gated: complete source packages have deterministic manifests and split-volume hashes; legacy and replacement Chat states require a fresh current-generation receipt. Source coverage and runtime evidence remain separate.
- Stale platform-wait lookup recovery now checks round budget and rollover state
  before rotating any reply token or RDATE. Found and missing lookups both hand
  control directly to the single replacement-Chat startup continuation.
- A round-budget waiting occurrence now changes its bound one-shot from
  `review_reply` to `rollover_continuation`; neither the account-gate branch nor
  the final waiting-read authorization can return to a five-minute reply poll.
- A due reply wait that reaches the reviewer round budget is now the atomic
  rollover recovery anchor. It remains bound until the unique replacement Chat
  is durably recorded; only a matching platform deletion proof can finalize the
  rollover and continue the single pending submission. Failure retains one
  technical recovery, and status/doctor reject a rollover with no future action.
- The account-browser gate now checks the bound reviewer Chat budget before any
  browser permission. Exhaustion atomically enters `rollover_pending`; one
  provisioning failure becomes `rollover_blocked` with one recovery identity
  and never masquerades as `review_waiting`.
- Frozen Alpha 83 implementation candidate commit: `9729d92f48bfd89f778808a41d0478621fdffe61`.
- Alpha 84 source was committed and pushed as
  `a98462dd6f78bb6d764a53b8cb99aa9068ea917b`; it has local evidence only and
  receives no real-device or Public Beta credit.
- Alpha 84 repository regression passed 421/421. Controller selftest passed
  15/15; closure-check, Skill, plugin, decision-register, milestone, and
  Beta-evidence validators passed. The 105-file deterministic archive was
  rebuilt and verified locally. This remains local-only evidence.
- Alpha 85 repository regression passed 423/423. Controller selftest passed
  15/15; release, closure, Skill, plugin, decision-register, milestone, and Beta
  evidence validators passed locally. The deterministic archive contains 106
  tracked source files. Real App rollover remains unverified.
- Alpha 86 repository regression passed 425/425 locally. Controller selftest
  passed 15/15; release, closure, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. The deterministic archive contains 110
  tracked source files. Real App canary matching remains pending.
- Alpha 87 repository regression passed 427/427 locally. Controller selftest
  passed 15/15; release, closure, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Its deterministic archive contains 111
  tracked source files. Real App old-state migration remains pending.
- Alpha 88 repository regression passed 429/429 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Its deterministic archive contains 112
  tracked source files. Real App orphan reconciliation remains unverified.
- Alpha 89 repository regression passed 430/430 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Its deterministic archive contains 113
  tracked source files. Real App cooldown expiry recovery remains unverified.
- Alpha 90 repository regression passed 432/432 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Its deterministic archive contains 114
  tracked source files. Real App legacy cooldown migration remains unverified.
- Alpha 91 repository regression passed 433/433 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Its deterministic archive contains 115
  tracked source files. Real App one-shot binding remains unverified.
- Alpha 92 repository regression passed 435/435 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Its deterministic archive contains 116
  tracked source files. Real App replacement-identity retirement remains
  unverified.
- Alpha 96 repository regression passed 439/439 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Its deterministic archive contains 119
  tracked source files. Real App retirement reconstruction, consumed-orphan
  recovery, and the subsequent unique replacement startup remain unverified.
- Alpha 97 repository regression passed 441/441 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Two deterministic builds produced the
  same 121-file archive.
  The installed Skill reports Controller 153 / revision `2026-08-19.110`.
  Real App legacy binding reconstruction and rollover continuation remain
  unverified.
- Alpha 98 repository regression passed 443/443 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Two deterministic builds produced the
  same verified 122-file archive. Real App same-task identity normalization,
  binding reconstruction, and rollover continuation remain unverified.
- Alpha 99 repository regression passed 443/443 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Real App canonical retirement-registry
  recovery and the subsequent replacement continuation remain unverified.
- Alpha 100 repository regression passed 444/444 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Persistent-gate discovery is locally
  verified; real App evidence remains blocked on the missing same-task
  rate-limit record and startup authorization.
- Alpha 101 repository regression passed 444/444 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Administrative generation sealing and a
  clean generation-6 startup/binding are locally verified; the original NPC
  ordinary continuation remains a real-App gate.
- Alpha 102 repository regression passed 445/445 locally. Controller selftest
  passed 15/15; closure-check, Skill, plugin, decision-register, milestone,
  and Beta evidence validators passed. Coordinator read-only handoff and
  original-task-only execution are locally verified. The original NPC wakeup
  and rollover continuation remain a real-App gate.
- Alpha 83 repository regression passed 419/419. Controller selftest passed
  15/15; closure-check, Skill, plugin, decision-register, milestone, and
  Beta-evidence validators also passed. Two independent builds produced the
  same verified 105-file source archive. This is local Alpha evidence only.
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

Collect the six real-device Beta gates against frozen commit
`dc0ed1c6f3ee94e64ce51bdb4c4eaac0ace14082`. Run
`scripts/validate_beta_evidence.py --require-ready`
before any Public Beta declaration.

## Do not repeat

- Do not test SuperLuna against unrelated project repositories.
- Do not reopen a retired reviewer Chat or keep two reviewer Chats active.
- Do not claim Beta readiness from unit tests, mocks, or `closure-check`.
