# Changelog

## 0.2.0-alpha.76 - 2026-08-18

- Packages Controller 132 / Skill revision `2026-08-18.89`.
- Makes the legacy `retire-missing-wait` compatibility entry rebuild exactly
  one replacement wait instead of changing a recoverable review to
  `external_blocked`.
- Repairs already-poisoned `platform_wait_task_not_found` states during the
  next exact task turn entry and returns them to the same one-wait bind barrier.
- Preserves the waiting state and keeps Chat, project, and product-decision
  access denied until the replacement wait is bound.

## 0.2.0-alpha.75 - 2026-08-18

- Packages Controller 131 / Skill revision `2026-08-18.88`.
- Detects an expired waiting-read claim during ordinary turn entry and requires
  an exact lookup of the one bound platform wait before any other action.
- Reuses that same wait when found or creates exactly one replacement when the
  platform confirms it is missing, without Chat, project, or user-decision access.

## 0.2.0-alpha.74 - 2026-08-18

- Packages Controller 130 / Skill revision `2026-08-18.87`.
- Separates recoverable technical blockers from real product decisions. Task
  identity mismatches, missing capabilities, cooldowns, browser-slot conflicts,
  recoverable waits, and controller failures now expose stable reason codes and
  concrete system recovery actions with `user_choice_required=false`.
- Reserves `需要你决定` for mutually exclusive product choices and requires one
  explicit question plus two or three options with their impacts.

## 0.2.0-alpha.73 - 2026-08-17

- Packages Controller 129 / Skill revision `2026-08-17.86`.
- Allows an explicitly authorized same-task repository retest to reset a fully
  released failed cycle in its exact sandbox; cross-task same-state reuse stays
  fail-closed.

## 0.2.0-alpha.72 - 2026-08-17

- Packages Controller 128 / Skill revision `2026-08-17.85`.
- Fixes the real replacement-Chat flow where the one-time `startup` account
  slot still carried reviewer identity `none` after the new visible Chat had
  already been created and bound.
- Promotes that same live slot only at the exact bound Extreme-selection gate;
  no second slot acquisition, browser initialization, navigation, or history
  scan is required. Wrong browser, task, scope, lease, Chat, URL, or operation
  remains fail-closed.

## 0.2.0-alpha.71 - 2026-08-17

- Packages Controller 127 / Skill revision `2026-08-17.84`.
- Lets a successfully provisioned replacement reviewer Chat atomically continue
  from its one-time `startup` slot to that new Chat's first `submission` while
  preserving the same lease, visible tab, exact binding, and tail-only access.
- Keeps every other cross-operation reuse fail-closed and adds negative coverage
  for an unbound or mismatched reviewer identity.

## 0.2.0-alpha.70 - 2026-08-17

- Packages Controller 126 / Skill revision `2026-08-17.83`.
- Accepts modern canonical UUID versions 6, 7, and 8 for real ChatGPT
  conversation identities while retaining the UUID variant, exact URL, and
  replacement-binding checks.
- Fixes a safe-stop after a replacement reviewer Chat was visibly created and
  initialized but its valid version-8 identity was rejected as non-canonical.

## 0.2.0-alpha.69 - 2026-08-17

- Packages Controller 125 / Skill revision `2026-08-17.82`.
- Forces repository self-retests to remain continuous, including legacy states
  that were incorrectly stored as `single_stage`.
- Beginning the next authorized goal after 2/2 formal reviews now retires the
  old reviewer Chat and requires one replacement before any further access.

## 0.2.0-alpha.68 - 2026-08-17

- Packages Controller 124 / Skill revision `2026-08-17.81`.
- Proactively rolls a reviewer Chat over before its third formal review, counting
  the exact Chat identity across new goals and run bindings instead of resetting
  the safety budget with each run.
- Requires tail-only inspection for every normal operation on an already bound
  reviewer Chat and denies full-history scanning before a real rate limit occurs.

## 0.2.0-alpha.67 - 2026-08-17

- Packages Controller 123 / Skill revision `2026-08-17.80`.
- Prevents an implementation task from changing an already continuous goal to
  `single_stage` during `begin-new-goal` or retest reset.
- The downgrade is rejected before state mutation; stage names, round numbers,
  and task-generated authorization labels do not override the continuous goal.

## 0.2.0-alpha.66 - 2026-08-17

- Packages Controller 122 / Skill revision `2026-08-17.79`.
- Completes the automatic reviewer-mode handoff through pre-send reconciliation
  and the one-shot formal send authorization. The previous release fixed reopen
  but could still stop immediately before the first request.
- Both trusted browser confirmation sources retain the same exact task, slot,
  browser, reviewer Chat, fingerprint, foreground, and identity checks.

## 0.2.0-alpha.65 - 2026-08-17

- Packages Controller 121 / Skill revision `2026-08-17.78`.
- Fixes a contract mismatch where a valid `in_app_browser_automatic` Extreme
  confirmation was persisted but the subsequent submission-reopen gate still
  accepted only the legacy manual `in_app_browser` source.
- The reopen remains bound to the same task, live submission account slot,
  browser, reviewer Chat, fingerprint, visible foreground mode, and empty
  request identity; all mismatches remain fail-closed.

## 0.2.0-alpha.64 - 2026-08-16

- Packages Controller 120 / Skill revision `2026-08-16.77`.
- Removes the normal manual click from reviewer Chat setup: after exact browser
  and Chat binding, a live startup-slot-scoped controller authorization allows
  one foreground selection of `极高/Extreme`, followed by a visible read-back.
- The authorization is bound to the implementation task, account slot, browser,
  reviewer Chat, target, and state revision. Missing, stale, cross-Chat, or
  ambiguous evidence fails closed without changing workflow state.
- Keeps automatic Codex implementation-model switching disabled; this release
  changes only the user-approved reviewer Chat selector.

## 0.2.0-alpha.63 - 2026-08-14

- Packages Controller 119 / Skill revision `2026-08-14.76`.
- Limits each active reviewer Chat to eight formal reviews. A ninth submission
  fails closed before browser access and requires exactly one replacement Chat.
- A reviewer Chat that produces a real rate limit is permanently retired from
  startup, submission, waiting-read, and health-probe access. The cooldown-bound
  recovery now provisions one replacement Chat with compact current context;
  it never reopens or scans the retired long conversation.

## 0.2.0-alpha.62 - 2026-08-14

- Packages Controller 118 / Skill revision `2026-08-14.75`.
- A successful post-cooldown health probe can now atomically become the real
  `startup`, `submission`, or `waiting_read` operation while retaining the same
  lease and already-visible fixed Chat. The follow-up must inspect only the
  conversation tail; a second browser initialization and full-history scan are
  explicitly forbidden.
- The rate-limit streak is cleared only after the continued real browser action
  succeeds. If the apparently healthy page immediately rate-limits again, the
  next cooldown escalates from 30 to 60 minutes instead of restarting at 30.

## 0.2.0-alpha.61 - 2026-08-14

- Packages Controller 117 / Skill revision `2026-08-14.74`.
- Fixes a recovered, never-sent review packet being mistaken for an already-sent
  request merely because no request identity exists. The fixed Chat is now
  checked against the exact current packet: zero matches continues to the
  existing first-send authorization, one trusted match uses no-resend receipt
  reconciliation, and multiple matches remain fail-closed.

## 0.2.0-alpha.60 - 2026-08-14

- Packages Controller 116 / Skill revision `2026-08-14.73`.
- Fixes a real submission rate limit leaving an automatic run idle in
  `review_submit_pending`: SuperLuna now creates one exact cooldown-bound
  recovery, blocks browser access before it is due, deletes the one-shot before
  one visible health probe, and resumes the same unsent packet only after the
  account is healthy. Another limit creates one replacement, never a recurring
  rule.

## 0.2.0-alpha.59 - 2026-08-14

- Packages Controller 115 / Skill revision `2026-08-14.72`.
- Rejects a review packet before browser submission when its human-visible
  `Round N` or `第 N 轮` title disagrees with the controller-owned formal review
  round. Historical round references later in the packet remain allowed.
- Waiting reads now pair the complete assistant message after the current
  request, distinguish a visible fragment from a genuinely absent reply, and
  keep the one fixed reviewer Chat tab available for the next handoff instead
  of closing every browser tab.

## 0.2.0-alpha.58 - 2026-08-14

- Packages Controller 114 / Skill revision `2026-08-14.71`.
- Makes every authorized browser startup, submission, waiting read, and health
  probe a visible-foreground action in the Codex in-app browser. The exact bound
  reviewer Chat must be surfaced as the user-visible active tab.
- Browser authorizations now declare `browser_surface_mode=visible_foreground`,
  deny background browser access, and return the foreground conversation target.
  Existing exact tabs are surfaced rather than duplicated.

## 0.2.0-alpha.57 - 2026-08-14

- Packages Controller 113 / Skill revision `2026-08-14.70`.
- Fixes a natural-language review false positive where a test-contract failure
  map such as `scenario deletion -> contract FAIL` was mistaken for an instruction
  to delete real files or data.
- Expected-failure mapping lines are ignored only by the high-impact action gate;
  imperative deletion and external project, source, repository, production, or
  user-data targets remain fail-closed.

## 0.2.0-alpha.56 - 2026-08-14

- Packages Controller 112 / Skill revision `2026-08-14.69`.
- Adds a fail-closed browser receipt reconciliation path for a request that is
  already visible in the one fixed reviewer Chat after its short-lived send
  authorization was lost. The controller requires one exact full-body match,
  the current payload SHA-256, trusted request identity, fixed Chat binding,
  live submission slot, and the existing browser-reopen lease.
- Successful reconciliation records the existing request and enters the normal
  reply path with `resend_allowed=false`; ambiguous, changed, external, malformed,
  or stale evidence leaves the state unchanged. This fixes the Round 15 NPC AI
  deadlock without weakening the ordinary one-shot send gate.

## 0.2.0-alpha.55 - 2026-08-13

- Packages Controller 111 / Skill revision `2026-08-13.68`.
- Fixes a submission deadlock after Codex Desktop restarts its in-app browser:
  when the one bound reviewer Chat is already visible under a new browser id,
  SuperLuna can now claim that unique exact-URL tab without navigating.
- The same controller gate accepts both current tab-list counts, opens the saved
  canonical URL only when both counts are zero, and rejects either list when it
  contains multiple exact matches. The candidate browser id is committed only
  after the existing send gate and submission confirmation succeed.
- A live `turn_entry` lease is atomically replaced by the ten-minute recovery
  lease, so completed implementation work cannot stop between local work and
  review submission. Local tests do not count as real macOS/Windows proof.

## 0.2.0-alpha.54 - 2026-08-13

- Packages Controller 110 / Skill revision `2026-08-13.67`.
- Repairs the one-shot waiting gap exposed by the NPC AI run: after a due wait
  claims Chat-read authority, it must move that same platform wait to the claim
  expiry and confirm the recovery arm before browser initialization is allowed.
- If the occurrence ends before a real read, the same one-shot task can fire at
  lease expiry, recover the stale claim, and continue without a second scheduler.
- Persists the recovery lease/RDATE identity in state, rejects missing or stale
  confirmation, and clears it on recovery, rearm, reply consumption, or exit from
  the waiting phase. Local regressions do not count as real macOS/Windows proof.

## 0.2.0-alpha.53 - 2026-08-13

- Packages Controller 109 / Skill revision `2026-08-13.66`.
- Fixes the repository self-retest workspace probe on Windows, where Python does
  not support `open(..., dir_fd=...)`. The Windows fallback keeps exact scope
  validation and brackets the bounded probe with directory identity checks.
- Adds a regression that exercises the no-`dir_fd` branch while preserving the
  existing out-of-scope and symlink fail-closed checks.
- Supersedes Alpha 52, whose tag remains immutable after its Windows CI failure.
- Public Beta remains blocked; this is an Alpha compatibility hotfix.

## 0.2.0-alpha.52 - 2026-08-13

- Packages Controller 108 / Skill revision `2026-08-13.65` in a deterministic
  tracked-source archive with an embedded SHA-256 manifest and standalone checksum.
- Distinguishes a real browser read from a queued or compacted occurrence. A
  `waiting_check_busy` result now carries an exact same-task retry update and
  explicitly proves that Chat was not read, so callers cannot report “no reply”.
- Recovers an expired waiting-read claim with the same one-shot task, requires a
  durable `record-browser-no-complete-reply` receipt before a true no-reply rearm,
  and exposes read outcome plus stale-claim health in the read-only status view.
- Fixes a claimed one-shot wait incorrectly inheriting the normal
  `review_waiting` permission to end the turn. After a complete reply, the
  controller now requires same-turn resume, result application, and preparation
  of the next review submission; visible guidance remains concise and bilingual.
- Makes event precedence explicit after context compaction: only the newest
  platform heartbeat can invoke `waiting-check`; a newer ordinary wakeup must
  ignore historical waiting commands and enter through `guard`.
- Adds `render-project-context` for new reviewer Chat bootstrap. It includes the
  real UTF-8 contents, relative paths, sizes, per-file hashes, and an aggregate
  context identity for every selected core file. File count is not capped;
  per-file/aggregate byte budgets and project-root, symlink, binary, build-
  output, and credential guards remain fail-closed.
- Restores existing project-specific profile labels as generic-compatible
  metadata while reserving every `superluna_repo_retest*` spelling except the
  exact sandbox profile. Existing real-project states therefore remain
  recoverable without letting a typo bypass the repository self-test gate.
- Rewrites visible one-shot wait prompts with concise Chinese and English
  guidance. Users see that no action is needed; exact commands remain in a
  clearly labeled internal section instead of mixed state-machine shorthand.
- Adds the development-only `superluna_repo_retest_v1` profile for SuperLuna's
  own repository tests. Each implementation task has one deterministic
  `.superluna/retest-runs/<task-hash>/project` fixture and sibling `state.json`.
- Rejects the repository root, ordinary source children, adjacent run folders,
  symlink escapes, and external paths before a write probe, state use,
  account-browser slot acquisition, or browser initialization.
- Binds account slots to the same profile/project scope, preventing an acquired
  browser lease from drifting into another run.
- Adds a tracked project `.codex/config.toml` that gives newly started trusted-
  project tasks a `workspace-write` host boundary, excludes system temporary
  paths, and disables shell-network access. It is not claimed to retroactively
  constrain a task that was already open when the file changed.
- Preserves the installed product's `generic` profile for user-selected,
  host-authorized external projects. No existing real-device or Public Beta
  evidence is promoted by these local safety changes.

## 0.2.0-alpha.51 - 2026-08-13

- Packages Controller 104 / Skill revision `2026-08-13.61`.
- Changes explicit one-time new-reviewer-Chat startup ordering: the implementation
  task must first complete and minimally verify one real project change. Only then
  may it read the Browser Skill, acquire an account slot, or create the Chat.
- A random workspace probe remains a directory check only. If the host asks for
  approval or the real edit is not durably written, the run stops before browser
  startup with zero Chat side effects. Existing fixed-Chat recovery is unchanged.
- The account-browser gate now requires
  `--new-chat-local-work-status completed_and_verified` for one-time new-Chat
  provisioning. Missing status receives no slot or browser permission.
- Keeps Public Beta false. This is a packaged workflow contract and local
  regression, not proof that Codex Desktop grants noninteractive write capability.

## 0.2.0-alpha.50 - 2026-08-13

- Packages Controller 103 / Skill revision `2026-08-13.60` after the clean C27
  three-round macOS transport proof and the six-platform CI pass.
- Adds a deterministic tracked-source ZIP builder and verifier. The archive
  contains an embedded SHA-256 manifest, excludes ignored runtime state and old
  archives, and writes a standalone checksum file.
- Keeps Public Beta false: C27 is isolated evidence, and the real-project,
  platform-matrix, and real recovery gates remain incomplete.
- C28 reached a logged-in ChatGPT home page and completed a corrected composer
  fill with an enabled send button, but then misclassified that ten-second
  successful call as browser unresponsiveness and stopped at 0/3 with zero side
  effects. Provisioning now classifies calls by returned status and verified
  postcondition, permits one correction of a side-effect-free local expression,
  and requires continuation after the corrected step succeeds.
- C29 then initialized and named its one Extreme reviewer Chat and completed its
  first verified UNSEEN worktree change, but invented a Git commit prerequisite;
  the external worktree index triggered permission approval before any formal
  round. Reviewer submission now accepts verified worktree evidence unless a
  commit identity is explicitly required.
- C30 initialized exactly one Extreme reviewer Chat and completed its first
  verified UNSEEN change, then discovered that the in-app browser initially
  exposed a temporary `/c/WEB:<uuid>` route while the same conversation had a
  different real sidebar URL. State initialization now rejects that temporary
  identity and provisioning must resolve and verify the unique canonical URL
  for the same initialization exchange without creating or sending again.
- C31 proved the canonical-URL fix, then created state with the delegation
  source task id instead of its own host identity. `init` now compares the
  supplied writer identity with `CODEX_THREAD_ID` and rejects any mismatch
  before state creation, so coordinator identity cannot leak into run, account,
  or waiting ownership.
- C32 proved the Controller 100 host-identity and canonical-URL fixes through a
  real project submission and scheduled reply read. Its clear low-risk REVISE
  asked only for proof that no other path was added, modified, or deleted, but
  the prose gate did not recognize the heading “唯一最小后续动作” and treated the
  word “删除” inside that absence criterion as a destructive instruction.
  Controller 101 recognizes narrow Chinese follow-up headings and negative
  diff evidence while preserving the gate for an affirmative project deletion.
- C32 then sent its second request exactly once, but the task passed a request
  UUID missing one character to submission confirmation. Controller 102 rejects
  a malformed request turn/message UUID before state transition and requires
  rereading the already-sent message node without resending.
- C34 exposed a platform browser id beginning with `-`; a separated argparse
  value was mistaken for an option. Controller 103 normalizes that opaque value,
  and the Skill prefers the unambiguous `--browser-id=<full-value>` form.
- C34 then reached its first tracked UNSEEN documentation edit but Codex Desktop
  placed the task in `waitingOnApproval`. No browser slot remained and no formal
  round was sent. This is recorded as a host task-permission Beta blocker; the
  controller cannot approve or bypass a host-owned file-change decision.

- Unreleased Controller 98 / Skill revision `2026-08-13.53`: C26 completed one
  real send, gated read, reply staging, slot release, and platform-wait deletion,
  but the generated waiting prompt abbreviated the final step as `resume`. The
  task therefore called the wrong CLI subcommand and correctly failed closed in
  `review_waiting`. The rendered prompt now requires the exact
  `resume-from-reply` subcommand plus result file, waiting source, and deleted
  automation proof, and explicitly forbids substituting `resume`.
  Clean C27 then completed three real isolated macOS web-review rounds without
  coordinator follow-up: three unique sends, three gated reads, three staged
  identities, three deleted one-shot waits, and three single consumptions. It
  finished `completed` with no active wait; this remains isolated Alpha evidence
  and does not count as a real-project Beta cycle.
- Controller 97 / Skill revision `2026-08-13.52`: C25 completed its
  first real one-shot wait, staged and consumed the unique Chat reply, deleted
  the wait, and released the browser slot, but the surviving `review_poll` lease
  made the mandatory same-task turn-entry fail before round 2. A validated
  scheduled reply now hands that same lease to `apply_result`; unrelated active
  leases remain non-preemptible. The exact wait/read/release/resume/guard path is
  covered by regression.
- Controller 96 / Skill revision `2026-08-13.51`: C24 sent exactly
  once and obtained a real request identity, but the mandatory same-task guard
  before receipt confirmation rotated the ordinary action lease and erased its
  fresh send authorization. The guard now preserves that exact authorized lease
  without extending or mutating it until confirmation; ordinary orphan recovery
  and cross-task exclusion remain unchanged. A regression reproduces authorize →
  same-task guard → confirm and proves one durable request enters waiting.
- Controller 95 / Skill revision `2026-08-13.50`: the clean C23 real
  wait fired, read, released its browser slot, and deleted itself correctly, but
  the safe reviewer boundary “do not approve release/delete/resume from this
  evidence” was still interpreted as the current high-impact action. That exact
  real reply shape is now a regression and auto-continues; an affirmative release
  and fixture deletion remains blocked.
- Controller 94 / Skill revision `2026-08-13.49`: C22 exposed a second
  autonomy blocker after its reply was read successfully: acceptance text proving
  `added=[]`, `removed=[]`, and no other file deletion was misread as an instruction
  to delete, so a safe unique `REVISE` stopped for user confirmation. The high-impact
  gate now removes only narrowly matched absence/"not proven" evidence clauses before
  classification, while a real delete remains blocked. A waiting-resume regression
  preserves the exact C22 response shape and proves automatic `apply_result` handoff.
- Controller 93 / Skill revision `2026-08-13.48`: a real C22 wait was
  correctly bound while `observe-run` misleadingly returned `automation_id=none`
  from the retired legacy scheduler field. The observer now exposes the active
  one-shot wait as its effective automation id and preserves explicit controller/
  waiting ids plus the active flag, with a waiting-state regression.
- Unreleased Controller 92 / Skill revision `2026-08-13.47`: C21 reused a
  canonical reviewer Chat whose older context still declared Controller 89;
  without a current-run identity block, the reviewer incorrectly treated the
  new Controller 90 state as an identity conflict. Every new state now owns a
  unique trusted review-run binding recording its Controller, Skill, schema,
  implementation task, and fixed Chat. The controller renders that exact block
  for the start of every formal payload, and the pre-send gate requires the same
  run id. Old Chat history is explicitly background-only and cannot rename,
  count, or bind the current state-local run. Legacy states are marked
  unrecorded rather than assigned invented source versions.

- Unreleased Controller 91 / Skill revision `2026-08-13.46`: the clean C21
  platform wait was created, bound, and fired automatically, then exposed a
  cross-operation account-slot bug. A still-live `submission` slot for the same
  task was returned as reusable during `waiting_read`; the second authorization
  correctly rejected it. Account slots may now be reused only for the exact
  operation that acquired them. A different operation fails closed, identifies
  the same task's stale lease for explicit release, and permits the waiting
  occurrence to rearm without initializing the browser. The rendered wait
  prompt also carries this recovery rule and requires both read leases.

- Unreleased Controller 90 / Skill revision `2026-08-13.45`: C19 proved one
  exact Extreme Chat submission but the host turn ended before creating its
  single-RDATE waiting task. Submission confirmation now returns a machine-
  readable `codex_app__automation_update` barrier, inert bootstrap prompt, and
  mandatory create/bind/render/update sequence. An exact-task ordinary wakeup
  may recover only this unbound platform wait, with project and browser access
  still denied; an expired never-bound RDATE is atomically replaced with a fresh
  token and future RDATE. Once bound, ordinary wakeups remain blocked as before.

- Unreleased Controller 89 / Skill revision `2026-08-13.44`: the five-minute
  waiting-read lease now covers a real browser reopen and DOM pairing cycle.
  `rearm-waiting-check --lease-id` atomically releases the claimed read and
  rotates state before the host may update the platform RDATE. Reviewer verdicts
  are explicitly limited to pre-response evidence, while the controller still
  requires post-response staging, slot release, wait deletion, and resume.
  GitHub Actions also cancels obsolete runs on the same ref to reduce redundant
  validation mail.

- Unreleased Controller 88 / Skill revision `2026-08-13.43`: the controller now
  emits the exact 180-second `platform_rdate`, forbids rounding, and requires the
  platform-returned RDATE when binding a waiting check. A half-hour-rounded wait
  therefore fails closed instead of silently creating a 20+ minute progress gap.

- Unreleased Controller 87 / Skill revision `2026-08-13.42`: a newly created
  implementation task may resolve its own exact identity from the host-injected
  `CODEX_THREAD_ID` during `startup-diagnostics`. This removes the impossible
  bootstrap dependency on a coordinator's second message while continuing to
  reject missing identity and delegation `source_thread_id` reuse.

- Unreleased Controller 86 / Skill revision `2026-08-13.41`: C14 proved that
  Controller 85 continues one clear isolated natural-language FAIL, then exposed
  two host-contract gaps. The waiting occurrence read the complete second reply
  and its DOM identity but saved only the body before releasing the account slot
  and deleting the one-shot, leaving no safe identity for resume. It also counted
  an older request from the reused Chat as a current-run round. Browser replies
  must now pass `stage-browser-reply` while both read authorizations remain live;
  the controller durably binds response identity and body hash before permitting
  release/delete/resume. Unstaged replies fail closed while the same wait remains
  recoverable. Round numbers come only from the current state, never Chat history
  or page prose. `external_blocked` also retires an ordinary `review_poll` lease.

- Unreleased Controller 85 / Skill revision `2026-08-13.40`: C13 completed a
  real wait-bound reply read with the required release-before-delete-before-
  resume order, but a low-risk FAIL next step was quarantined because its
  explicit prohibition mentioned production, deployment, and permissions.
  The high-impact gate now removes standalone negated boundary clauses before
  classification while preserving mixed clauses that turn into a real
  high-impact instruction. A scheduled natural-language FAIL with one clear
  isolated next step now continues as `apply_result`; vague, ambiguous, and
  genuinely high-impact instructions still require the user.

- Unreleased Controller 84 / Skill revision `2026-08-13.39`: an implementation
  that failed closed during C12 left its ordinary `turn_entry` action lease live
  until timeout, delaying an otherwise clean user-authorized retest. Entering
  `external_blocked` now retires only foreground `turn_entry` / `apply_result`
  leases and their pending send authorization. Existing wait deactivation
  already retires waiting-read leases, while browser-reopen leases remain
  non-preemptible. The account-gate wording now
  also matches runtime: every new browser acquisition after a normal release,
  including the same task's next operation, observes the 180-second quiet
  interval unless the one-shot proven-health bypass applies.

- Unreleased Controller 83 / Skill revision `2026-08-13.38`: C12 exposed an
  incorrect browser-runtime path expansion by treating the Browser Skill folder
  as the plugin root. The SuperLuna startup contract now defines the plugin root
  as the common parent containing both `skills/` and `scripts/`, requires the
  exact `<plugin root>/scripts/browser-client.mjs`, and forbids probing alternate
  browser implementations. C12 subsequently observed a real ChatGPT history
  rate limit before round-one send and correctly stopped with zero sends, waits,
  reads, or active account slots; this is fail-closed evidence, not a clean-cycle
  or rate-limit-recovery credit.

- Unreleased Controller 83 / Skill revision `2026-08-12.37`: C11 consumed its
  second scheduled reply correctly but retained the `waiting_read` account slot
  until preparing round three. The rendered one-shot prompt now orders account
  release before wait deletion and resume, and `resume-from-reply` fails closed
  while the owning task still has any live `waiting_read` slot. The compact
  prompt remains within the immutable 1200-byte budget.

- Unreleased Controller 82 / Skill revision `2026-08-12.36`: the clean C10
  macOS retest stopped at 0/3 because its task-local browser had no tabs and
  the only machine-verifiable home-navigation grant was for a health probe.
  A user-authorized new reviewer Chat now supplies a stable authorization id
  with the first `startup` slot. The shared gate records only its digest and
  allows exactly one ChatGPT home navigation while that slot is held; release,
  reuse by another task, or use outside `startup` fails closed.

- Unreleased Controller 81 / Skill revision `2026-08-12.35`: Controller 80's
  first six-platform run passed five jobs but reproduced a narrow Windows 3.13
  race: concurrent processes could all open a newly created lock sidecar, then
  receive `PermissionError` while trying to create its first lockable byte.
  Lock initialization now rechecks whether a competing process already wrote
  that byte before retrying, while persistent denial still raises. The shared
  account-browser gate also receives the same bounded 10-second lock queue as
  the binding registry; ordinary state locks remain at two seconds.

- Unreleased Controller 80 / Skill revision `2026-08-12.34`: the clean C9
  macOS retest proved the universal browser-send gate, then safely stopped
  because its controller-rendered waiting prompt was 1215 bytes—15 bytes over
  the immutable 1200-byte limit. The one-shot prompt is now shorter without
  dropping its state, token, account-slot, browser-read, current-tab, deletion,
  or resume requirements. Browser send authorization also projects the later
  prompt with a maximum supported automation identity and refuses the send
  before the click if it cannot fit. Waiting automation identities are now
  bounded to 64 single-line characters, so post-send prompt growth cannot
  invalidate the projection.

- Unreleased Controller 79 / Skill revision `2026-08-12.33`: the contaminated
  C8 run revealed that the durable pre-send authorization applied only to the
  missing-tab reopen path. An implementation task could therefore use a still-
  visible tab to send while state was not authorized, then fail only when
  confirming the receipt. Every in-app-browser submission now requires one
  fresh controller authorization immediately before send. It proves the active
  `review_submit_pending` state, current action lease, exact browser and payload
  fingerprint, confirmed Extreme reviewer identity, and a live `submission`
  account slot bound to that reviewer. Confirmation must consume the persisted
  revision plus the same browser and account-slot identities.

- Unreleased Controller 78 / Skill revision `2026-08-12.32`: a Codex platform
  create request unexpectedly produced two live implementation tasks for the
  same fixed reviewer Chat. Both passed the global two-slot gate and the
  duplicate sent first, contaminating the clean C8 retest. Every account-browser
  lease now carries the fixed reviewer identity and serializes that reviewer
  across implementation tasks, so a platform duplicate fails closed before
  browser initialization or send even while another global slot is free.

- Unreleased Controller 77 / Skill revision `2026-08-12.31`: the real macOS C7
  continuation retest completed two review cycles and reached its third wait
  without coordinator prompts. Two waiting occurrences first tried stale or
  absent prior-occurrence tab handles before recovering through the persisted
  binding, and the third review packet asked Chat to approve occurrence evidence
  that could only exist after submission. Rendered waits now require a handle
  from the current occurrence's tab listing and forbid old Tab objects/ids;
  review packets may request PASS only for evidence completed before submission.

- Unreleased Controller 76 / Skill revision `2026-08-12.30`: the first clean
  Controller 75 macOS waiting cycle acquired the exact `waiting_read` account
  slot, authorized browser access, deleted its one-shot task, and consumed the
  reply once. It then falsely required user input because the review used a
  standalone `唯一下一步` heading and mentioned file permissions only in an
  earlier hypothetical counterexample. Standalone Chinese and English next-step
  headings now bound the actionable scope; real permission, release, and deploy
  instructions inside that scope remain blocked.

- Unreleased Controller 75 / Skill revision `2026-08-12.29`: a real macOS
  waiting occurrence passed the wait claim and browser-read authorization but
  then initialized the browser without first acquiring the shared
  `waiting_read` account slot. Browser wait authorization now requires the live
  account-slot lease and independently verifies the exact implementation task,
  operation, and expiry. Missing or mismatched slots fail before browser
  initialization. The controller-rendered one-shot prompt and normative
  protocol now include the same enforced order.

- Unreleased Controller 74 / Skill revision `2026-08-12.28`: a documentation-
  only follow-up commit reproduced a Windows Python 3.13 failure when one of six
  concurrent task-binding registrations spent the ordinary two-second state
  budget waiting to open the shared lock sidecar. The already-serialized binding
  registry now has a dedicated ten-second bounded queue budget. Persistent
  permission denial still fails closed; ordinary workflow-state lock timing is
  unchanged.

- Unreleased Controller 73 / Skill revision `2026-08-12.27`: real projectless
  Mac C4 proved browser health recovery and provisioned its sole reviewer Chat,
  but only then discovered that the hardcoded `/var/tmp` test directory was
  outside its assigned writable workspace. Startup now runs a controller-backed
  create/verify/remove probe in the task's existing assigned workspace before
  acquiring a browser slot. Missing, unwritable, mismatched, or uncleanable
  workspaces fail before browser initialization, Chat creation, sending, or
  state creation, preventing orphan reviewer Chats.

- Unreleased Controller 72 / Skill revision `2026-08-12.26`: real projectless
  Mac C3 obeyed the slot-before-browser order, but a fresh browser had no tab
  from which to prove post-cooldown conversation-history health. A health-probe
  lease now explicitly authorizes one temporary exact-home navigation when no
  tabs exist. The page itself still proves nothing: the task must observe at
  least one real conversation-history entry without opening an unrelated Chat,
  sending, refreshing, or creating a conversation, then close the probe tab.

- Unreleased Controller 71 / Skill revision `2026-08-12.25`: the Controller 70
  Windows Python 3.13 matrix showed that simultaneous processes could be denied
  while opening the lock sidecar, before they entered the serialized registry
  read. Lock-sidecar opening now shares the existing bounded lock-acquisition
  budget; persistent denial still fails closed.

- Unreleased Controller 70 / Skill revision `2026-08-12.24`: the first
  Controller 69 six-platform matrix exposed one more Windows Python 3.13
  sharing denial while a newly serialized account-gate reader opened the file
  immediately after replacement. Only the two shared registries now receive
  the same bounded retry on reads as on replacement; persistent errors still
  fail closed and ordinary workflow state remains unchanged.

- Unreleased Controller 69 / Skill revision `2026-08-12.23`: a real projectless
  Mac C2 task proved that merely saying “slot before browser” was insufficient:
  reading the browser Skill first caused runtime initialization before the
  account gate. Startup now reads only SuperLuna first. A successful slot lease
  explicitly authorizes reading the browser Skill and initializing its runtime;
  blocked acquisitions explicitly deny both. Startup diagnostics also fail
  closed unless the slot was acquired before browser activation.

- Unreleased Controller 68 / Skill revision `2026-08-12.22`: extending the
  sharing-denial retry budget was not stable on Windows Python 3.13. Existing
  durable files now use the native Win32 `ReplaceFileW` single-operation API;
  first creation and non-Windows platforms retain `os.replace`. The same
  bounded retry and fail-closed behavior remains around either primitive.

- Unreleased Controller 67 / Skill revision `2026-08-12.21`: a clean
  projectless Mac C1 task proved that browser capability may exist while the
  default account gate under `~/.codex` still requires a manual filesystem
  approval. The host-user gate now lives in a deterministic system-temporary
  directory shared by project and projectless tasks. The Skill also treats
  browser runtime connection and documentation calls as initialization, so the
  account slot must be acquired before the first browser tool call.

- Unreleased Controller 66 / Skill revision `2026-08-12.20`: after the account
  gate passed, the next Windows Python 3.13 run exposed the same sharing denial
  in the concurrent task-binding registry. The bounded two-second budget now
  covers both already-serialized shared registries, while ordinary state files
  remain at the generic 0.5-second fail-closed budget.

- Unreleased Controller 65 / Skill revision `2026-08-12.19`: repeated Windows
  Python 3.13 CI runs showed that six simultaneous account-gate acquisitions
  can retain a sharing denial beyond the generic 0.5-second atomic-replace
  budget. The already-serialized machine-wide account gate now has a bounded
  two-second replace budget; other durable files retain 0.5 seconds and
  persistent permission errors still fail closed.

- Unreleased Controller 64 / Skill revision `2026-08-12.18`: A2 completed its
  first autonomous reply cycle and prepared round two, but ended at
  `review_submit_pending` when the 180-second handoff blocked submission. Since
  execution states intentionally have no timer, that left no wake source. Active
  startup/submission handoffs now return an explicit same-turn wait contract;
  the implementation keeps the foreground turn alive, waits locally to the
  exact retry time, and continues without creating an automation. Existing
  waiting occurrences alone may redate their one-shot check.

- Unreleased Controller 63 / Skill revision `2026-08-12.17`: the first real A2
  post-cooldown waiting occurrence proved that a healthy probe may need to
  continue directly into `waiting_read`, not only `startup`. The single-use
  health follow-up now admits either operation for the same task and is consumed
  by the first acquisition. A new regression covers the waiting recovery path.

- Unreleased Controller 62 / Skill revision `2026-08-12.16`: a real macOS
  two-task retest proved that the two-slot ceiling alone does not prevent rapid
  cross-task conversation-history requests from retriggering ChatGPT's account
  limit. The shared gate now preserves the two-task cap but queues a different
  task for a 180-second quiet handoff after every completed or healthy release.
  Only one same-task `startup` immediately after a proven healthy probe may
  bypass the interval, and acquisition consumes that bypass. Three deterministic
  regressions cover blocking, exact expiry, and the bounded health/startup bypass.

- Unreleased Controller 61 / Skill revision `2026-08-12.15`: a real macOS
  retest showed that the ChatGPT homepage could appear healthy while opening
  conversation history still returned the account rate-limit notice. Clearing
  the shared circuit now requires a `health_probe` lease plus explicit
  `conversation_history_accessible` proof from an existing conversation or
  history surface; homepage, login and empty-composer checks fail closed.
- Unreleased Controller 60 / Skill revision `2026-08-12.14`: added a
  machine-wide two-slot ChatGPT account browser gate. A third local run queues
  before browser initialization; any real conversation-history rate-limit
  notice clears all slots and opens a shared 30/60-minute circuit followed by a
  single read-only health probe. This does not coordinate another computer and
  does not add real-device release credit.

## Unreleased

- Added controller 59 / Skill revision `2026-08-12.13` after the UNSEEN Insight
  and Observation retests showed two browser-startup false negatives. The new
  `browser-startup-plan` requires claiming a unique user-open exact-URL Chat
  before any controlled tab or authorized new tab. Browser evidence no longer
  depends on localized `你说/ChatGPT 说` or snapshot `[active]` strings; stable
  message nodes, actual composer state, and separate visible Extreme evidence
  are required. A matching host automation lookup returning `not_found` can now
  retire an orphaned local wait through `retire-missing-wait`; task assertions
  alone cannot. Local evidence only, pending real Mac retest.
- Added controller 58 / Skill revision `2026-08-12.12` after the UNSEEN Memory
  retest showed that a terminated historical state remained permanently bound
  to its old implementation task. The new `reset-for-retest` transition accepts
  only an externally blocked state with no wait identity or action lease, an
  exact old/new task identity, and explicit current user authorization. It
  archives the old cycle and hands the same state to the replacement task; live
  waiting work still cannot be bypassed. Local evidence only, pending real Mac
  retest.
- Added controller 57 / Skill revision `2026-08-12.11` after the first real
  macOS wait occurrence was created with a hand-written prompt that omitted its
  required token and automation id. The new `render-waiting-check` command only
  renders for a bound active one-shot wait and emits the exact first command
  with state, token, and platform identity. The Skill now requires updating the
  same future `RDATE` task with that complete controller-rendered prompt before
  the submitting turn may end. This is a local fix pending a fresh real macOS
  retest and adds no Public Beta credit. Startup diagnostics now also reject a
  delegated implementation task that reuses the coordinator's
  `source_thread_id` as its own identity, preventing state and waiting work from
  being routed back to the coordinator.

## 0.2.0-alpha.49 - 2026-08-12

- Added controller 56 / Skill revision `2026-08-12.10` after the Windows
  Python 3.13 CI job exposed a transient sharing violation during concurrent
  binding registration. All durable atomic replacements now retry only
  `PermissionError` for at most 0.5 seconds; persistent permission failures
  still fail closed, and focused tests cover both paths.
- Added controller 55 / Skill revision `2026-08-12.9` with a fail-closed,
  byte-preserving `observe-runs` overview for multiple implementation states,
  including all five user statuses, stage, evidence age, the exact 20-minute
  boundary, and aggregate counts.
- Added controller 54 / Skill revision `2026-08-12.8` after continuation testing
  found that a guard could grant a fresh work lease without validating the exact
  implementation-task identity. Ordinary work entry and serial recovery now
  both fail closed for missing or cross-task identities; waiting, browser-reopen,
  and cross-task boundaries remain non-reclaimable.
- Added controller 53 / Skill revision `2026-08-12.7` after the culture branch
  exposed a same-task continuation failure. Guard documentation now requires
  the stable implementation-task identity after context compaction, and the
  read-only observer applies the exact 20-minute boundary to both active work
  states instead of excluding work that is applying Chat feedback.
- Added controller 52 / Skill revision `2026-08-12.6` with two visible-branch
  features after mainline review. `observe-run` provides a byte-for-byte
  read-only multi-run view and treats exactly 20 minutes without new evidence as
  the stall boundary while excluding `等待 Chat`. `startup-diagnostics` reports
  one fail-closed startup cause, including blank identities and an unavailable
  visible Extreme mode, without opening Chat, creating state, or changing the
  workflow.
- Added controller 51 / Skill revision `2026-08-12.5` after a real ecosystem
  task reused a state whose previous goal was already completed. The new
  `begin-new-goal` command requires the same implementation task's live
  turn-entry lease, an explicit current user authorization identity, a concrete
  first stage, and zero surviving waiting checks. It preserves the bound Chat
  but clears the old completion and operation package and requires fresh visible
  reasoning-mode confirmation. Ordinary wakeups cannot reopen completed work.
- Corrected the published Pro-progress ledger ceiling from 20 to the
  controller's actual 256-event bound. The package regression now compares the
  schema directly with `MAX_PROGRESS_EVENTS` instead of proving a duplicated
  literal against itself.
- Published the bounded Pro-progress event shape in the state schema and added
  a package regression for its required fields and 20-event ceiling. The
  broader nested-state audit remains open; the release report no longer
  overclaims that this one slice completes every nested contract.
- Added a machine-readable milestone and rollback contract with a deterministic
  validator. Evidence scope is checked for internal consistency: an Alpha may
  truthfully record real-device evidence without thereby claiming Public Beta
  readiness, while local-only milestones cannot claim either.
- Closed a proof gap in controller 50 / Skill revision `2026-08-12.4`.
  Controller 49's fresh browser pre-send gate returned the current state
  revision without persisting that the gate had actually run, so a caller that
  held the reopen lease could forge the proof by passing the already-known
  revision directly to submission confirmation. The gate now atomically stores
  its lease and authorization revision in state. Confirmation must consume that
  exact persisted fact at the unchanged revision, and clearing the reopen lease
  clears the authorization. A regression proves the reopen revision alone
  cannot confirm or persist a request. This is local controller evidence only;
  no real-device or Public Beta credit changed.
- Fixed the real Windows submission-reopen stall in controller 49 / Skill
  revision `2026-08-12.3`. A first canonical-URL navigation call that times out
  is now treated as uncertain and reconciled only on the same opened tab,
  without a second open, navigation, reload, or Chat. The reopen authorization
  no longer grants send permission. After the page is verified, a new
  `authorize-browser-submission-send` gate rechecks the active lease,
  fingerprint, browser, bound conversation, empty request identity, and at
  least 60 seconds of remaining lease time. Submission confirmation requires
  that fresh state revision. This adds no real-device or Public Beta credit
  until retested on the frozen candidate.
- Fixed a second published-schema false green in the Alpha 40 candidate. The
  schema previously accepted `review.status="review_submit_pending"` while
  `response_complete` or `response_valid_for_apply` was true, although runtime
  validation rejects actionable response evidence before a review request is
  submitted. A package regression now compares the published contract with the
  runtime validator, and the schema forces both response flags false at that
  boundary. This local contract correction adds no real-device or Beta credit.
- Fixed a deterministic `closure-check` evidence overclaim in controller 48 /
  Skill revision `2026-08-12.2`. The command executes only the 15 built-in
  controller selftests, but its five repository-level scenarios were all
  labelled "covered by local tests", which could be read as a fresh repository
  test result even when that suite had not run or was failing. The result now
  publishes `executed_checks=["controller_selftest"]`, explicitly reports the
  repository suite as not run with an unknown pass result, and marks those five
  scenarios `not_run_by_closure_check`. Real-device and Public Beta gates remain
  false; no real-platform credit changed.
- Updated the validation workflow to `actions/checkout@v7` and
  `actions/setup-python@v7`. Both official action releases use the Node 24
  runtime, removing the GitHub-hosted runner warning that the older Node 20
  actions were being forced onto Node 24. Product runtime behavior and release
  metadata are unchanged.
- Fixed a published-schema false green in controller 47 / Skill revision
  `2026-08-12.1`. The release schema previously accepted an active waiting
  check during local work, and accepted stale waiting identities after the
  runtime left `review_receipt_pending` / `review_waiting`, although runtime
  validation rejects both states. A failing package regression now requires
  the schema to activate the check and token only at the exact waiting-only
  boundary and to clear the token, automation id, and claim id everywhere
  else. Cross-field id equality remains controller-enforced, so the full nested
  schema audit and Public Beta gates remain open.
- Fixed a lease-preemption hole in controller 46 / Skill revision
  `2026-08-11.11`. The legacy `guard --replace` flag previously bypassed the
  active-lease branch outside waiting states, allowing a caller to clear a
  different task's ordinary lease or a protected browser-reopen lease. The
  flag remains accepted for CLI compatibility but no longer changes lease
  authorization. Exact same-task serial recovery still applies only to
  orphaned `turn_entry` and `apply_result` leases. A failing regression now
  covers cross-task and protected-lease preservation.
- Converted three macOS branch failures into fail-closed controller behavior.
  Controller 45 no longer permits a submitted turn to end until its unique
  one-shot waiting job is actually bound, and a later serial turn from the
  exact same implementation task may atomically replace an orphaned ordinary
  `turn_entry` or `apply_result` lease. Different tasks and waiting/browser
  leases remain non-reclaimable. The Skill now states the platform deletion
  limitation explicitly: passing an automation id is not proof that an ACTIVE
  job was deleted, so real runs must verify platform retirement.
- Fixed a real Controller 43 dogfood regression where an ordinary
  `turn_entry` lease survived a successful review submission. The first legal
  waiting occurrence then returned `waiting_check_busy` and delayed the loop
  until the full lease timeout. Controller 44 now releases that exact entry
  lease atomically while confirming the submission; a regression test proves
  the first bound waiting check can immediately return `review_poll`.
- Fixed the deterministic part of an external-message wakeup bug. A normal new
  turn must now enter through `guard` before project or browser access. While
  the saved workflow is waiting for a receipt or reply, the controller returns
  `waiting_turn_blocked` with no lease and no state mutation; `--replace`
  cannot bypass it. The only legal waiting wakeup remains the platform
  occurrence whose first action is `waiting-check`. This does not claim a host-
  level tool interceptor: a model that skips the mandatory guard still cannot
  be forcibly stopped by the current Codex host.
- Recorded the macOS Codex host capability audit for the remaining same-turn
  continuation blocker. The plugin-visible host surface exposes no turn-end
  interceptor, final rejection hook, or native guaranteed continuation API.
  The release report now lists this as an explicit Public Beta blocker; no
  scheduler, controller behavior, version, or real-cycle credit changed.
- Fixed deterministic portions of eight blockers found by continuous dogfooding
  in controller 42 / Skill revision `2026-08-11.7`. An explicitly local
  SQLite/synthetic counterexample
  may delete or invalidate test records without being misclassified as a real
  destructive action; production, user-data, repository-file, release,
  deployment, permission, and credential targets still require the user. A
  previously bound fixed web Chat whose exact URL is absent from both current
  tab listings may now reopen only its stored canonical URL once under the
  current submission or waiting authorization. The page, conversation, and
  payload/request identity must be reverified; no replacement Chat, different
  conversation or duplicate send is introduced. The same real run also exposed
  two tasks creating five-minute `FREQ` heartbeats despite controller interval
  zero. The Skill/protocol now require one UTC `RDATE` occurrence and explicitly
  forbid every recurring platform rule; rearm updates the same identity only.
  A real Insight wait then showed that a due occurrence colliding with an active
  work lease could exit busy and strand its already-due platform wait. Busy now
  returns a deterministic one-shot retry time while preserving the same token,
  automation identity, no-read boundary, and no-send boundary.
  A subsequent real Memory turn still ignored the prose-only rule and recreated
  `FREQ`; every schedule/keep/update result now carries machine-readable
  `single_rdate`, `RDATE:`, and recurrence-forbidden fields.
  The next real Memory reply omitted the SQLite label but explicitly required a
  parent-row delete to be rejected with FK/association state unchanged; this
  bounded database-protection assertion is now recognized without weakening
  production/user/repository destructive gates.
  The original Memory task then recovered the saved reply, passed the real
  parent-delete rejection regression, submitted round 6 once to the same Chat,
  and created one `RDATE` wait; the required one-time recovery wakeup means this
  is a real functional retest but not a consecutive-gate cycle.
  A subsequent clean monitor was 0/3: Memory failed to use the authorized exact-
  URL reopen when its bound provider tab disappeared, Insight bypassed both wait
  controller gates and read the browser directly, and no legal third cycle could
  start. Submission boundaries now return a mandatory missing-tab controller
  action for every bound fixed Chat, and completed `apply_result` leases clear at
  the next durable boundary. Browser-before-gates is explicitly a failed cycle;
  host-level tool permission enforcement remains unavailable and unverified.
  The next clean Memory occurrence then applied a real round-7 revision but
  stopped at `local_work` instead of continuing to the next submission in the
  same turn. Active continuous boundaries now return a mandatory `next_action`,
  `continuation_required=true`, and `turn_completion_allowed=false`; real
  retesting then passed one complete autonomous cycle, but the next occurrence
  still ended after applying the reply despite those fields. Its wait had been
  correctly deleted, so no third cycle could start. The host lacks a plugin-
  level turn-finalization interceptor; the clean monitor result is 1/3.
- Fixed premature stage completion in controller 36 / Skill revision
  `2026-08-10.23`. New workflows now default to explicit `continuous` goal mode;
  a bounded stage PASS cannot enter `completed`, even through recovery override.
  Continuous completion requires a reviewed `result_received` boundary, an
  explicit overall-goal flag, and non-empty acceptance evidence. The published
  state schema, CLI, status output, and Skill contract now enforce the same rule.
- Fixed the automatic-mode choice leak in controller 35 / Skill revision
  `2026-08-10.22`. `review_submit_pending` is no longer exposed as a user
  decision, controller status output marks active submission as choice-free,
  and the Skill forbids stage-ending task cards, A/B/C suggestions, and repeated
  confirmation before normal authorized sends to the fixed Chat. Only a new
  concrete authorization blocker may ask one focused question.
- Fixed the real UNSEEN Observation early-stop in controller 34 / Skill revision
  `2026-08-10.21`. Successful startup rebind now returns an explicit mandatory
  same-turn continuation action, and the Skill forbids treating binding recovery
  as a final deliverable or deferring authorized work to another wakeup. No new
  scheduler, Chat, or model action was added.
- Added explicit fixed `terra_medium` implementation support in controller 33 /
  Skill revision `2026-08-10.20`. `luna_medium` remains the default; preflight
  and initialization accept only these two roles, runtime policy and executor
  identities must match, and no automatic model switching is introduced. The
  published schema now expresses both valid matched pairs. This is local
  contract evidence only and does not add real-device or Beta-gate credit.
- Synchronized the startup preflight example with the runtime enum in Skill
  revision `2026-08-10.19`: use `--review-mode extreme`, not the rejected legacy
  word `confirmed`. The Alpha 29 real task recovered by inspecting CLI help;
  future tasks no longer need that corrective retry.
- Fixed the real Alpha 28 startup retest blocker in controller 32 / Skill
  revision `2026-08-10.18`. The implementation task successfully opened and
  verified the exact existing Chat, but the platform exposed no `providerTabId`.
  An explicitly verified existing conversation can now bind the non-handle
  `canonical_url_only` identity. Submission and waiting recovery remain
  occurrence-authorized, exact-URL, and unable to persist a numeric `Tab.id`,
  switch Chat, or create a replacement.
- Fixed the fatal new-task browser bootstrap gap in controller 31 / Skill
  revision `2026-08-10.17`. The Skill now explicitly activates
  `browser:control-in-app-browser` first. A pristine provisioned
  `pending_handoff` state can authorize one send-forbidden canonical-URL open in
  the new implementation task's own browser, then commit a revision-bound
  verified browser/provider rebind before local work. Empty task-local tabs are
  no longer misreported as missing Codex browser capability, and recovery never
  creates a replacement Chat.
- Synchronized the model-policy safety core with runtime validation in Skill
  revision `2026-08-10.16`. The schema now fixes policy version 5, forbids
  automatic model switching and automatic task/thread creation, keeps the
  executor on Luna Medium, and bounds the reviewer ledger to Sol Extreme or
  recorded Chat Pro. Nested quota and workflow-phase contracts remain open.
- Synchronized the published capabilities contract with runtime validation in
  Skill revision `2026-08-10.15`. Attachment/filesystem capability enums and the
  Terra probe are now explicit, while `mcp_readonly` and `mcp_verified` require
  each other. Chat capability fields are typed but not falsely made required.
- Synchronized published confirmation evidence with runtime validation in Skill
  revision `2026-08-10.14`. The schema previously accepted a confirmed review
  without its durable context, valid flag, Extreme mode, trusted control source,
  observed label, or observed thread evidence. Confirmed browser review is now
  tied to `in_app_browser`, while compatibility App Chat confirmation cannot use
  that source. Every active workflow also requires a valid lease and a nonempty,
  non-`none` reviewer thread. Identity equality still remains a controller-only
  invariant.
- Synchronized the published state policy contract with runtime validation in
  Skill revision `2026-08-10.13`. The schema previously accepted missing or
  false sole-writer, read-only-reviewer, Codex-review, reasoning, and transport
  locks that `validate_state` rejected. Those policy fields are now required
  constants, with review transport conditionally tied to its control source.
  Other nested state-machine invariants remain explicitly incomplete.
- Fixed the controller-30/revision-`.11` real visual-evidence finding. The
  ten-minute lease, one send, request identity, atomic browser rebind, and lease
  consumption all succeeded, but a temporary full-viewport screenshot preview
  exposed the fast assistant reply before being replaced by a safe crop. Skill
  revision `2026-08-10.12` forbids every post-submit full-page/viewport capture;
  it may directly capture only the new user-message region, otherwise it omits
  the screenshot and uses confirmed request identity as receipt evidence.
  A follow-up real Windows visual-isolation diagnostic passed with one submission,
  confirmed request identity, atomic browser-id rebind, no duplicate, and no
  post-submit page/viewport/assistant read. Direct locator capture was unsupported,
  so the optional screenshot was omitted. The manually awakened diagnostic does
  not count toward the frozen-candidate 10-cycle gate.
- Added real Windows evidence for the complete revision-`.12` fixed-Chat
  transport function. Starting with no fixed-URL tab in either listing, the
  controller authorized one canonical-URL open, one submission, atomic browser
  confirmation, and zero duplicates. A separate waiting occurrence uniquely
  paired and consumed the complete PASS response; replay returned
  `already_consumed`. No platform automation was created and the waiting
  occurrence was manually awakened, so this does not advance the 0/10 gate.
- Fixed the next real controller-29/revision-`.10` visual finding. The bound Chat,
  visible Extreme label, screenshot, and one new request identity were all real,
  but the two-minute browser-rebind lease expired during those required checks;
  the send occurred once and confirmation correctly failed without a resend.
  Controller 30 / Skill revision `2026-08-10.11` use a ten-minute lease and direct
  callers to finish page checks before authorization, then immediately send once
  and confirm. The later revision-`.12` diagnostic retested this path successfully;
  the hotfix remains unpackaged.
- Fixed the controller-28/revision-`.9` real visual-retest failure where Codex
  restarted the in-app browser with a new browser id. The old id had been treated
  as permanent, so the controller authorized the canonical URL reopen but the
  caller correctly refused to use a different browser. Controller 29 / Skill
  revision `2026-08-10.10` bind the short reopen lease to exactly one current
  browser id and commit that rebind only with verified submission confirmation.
  A different browser, conversation, provider identity, fingerprint, or missing
  lease remains fail-closed. This is an unpackaged source hotfix pending real
  Windows retesting.
- Fixed the controller-27/revision-`.8` visual-retest startup failure: the same
  provisioned fixed Chat had disappeared from both tab listings before a later
  submission, and the controller exposed URL recovery only to an authorized
  waiting read. The task stopped before sending, proving the missing
  submission-side contract without a duplicate or wrong-Chat write. Controller
  28 / Skill revision `2026-08-10.9` add a two-minute,
  submission-fingerprint-bound lease for one canonical-URL reopen before send.
  Submission confirmation must prove and consume the lease; ordinary user tabs,
  promoted provider identities, stale fingerprints, and expired leases remain
  fail-closed. The fix is unpackaged and still needs real Windows retesting.
- Synchronized the published state schema's top-level contract with controller
  runtime state. Nine runtime-required sections, including `browser_binding`,
  `binding`, `next_operation`, and `model_policy`, were previously optional or
  undeclared, so a state missing durable browser identity could satisfy the
  published schema while the controller rejected it. The schema now declares and
  requires every runtime top-level section, with a package regression guarding
  future drift. Nested contract equivalence remains an explicit follow-up.
- Fixed the first clean controller-26/revision-`.7` browser-cycle finding. The
  unique paired PASS explicitly recommended stopping the completed monster-AI
  review loop, but because it had no labelled `下一步` heading, the fallback
  scanned the whole prose and treated later deferred release testing as a current
  high-impact action. An explicit stop recommendation is now a bounded stop
  action; deferred release/platform work remains context and is never executed.
  A failure-first regression uses the real reply shape. Controller 27 / Skill
  revision `2026-08-10.8` implement the unpackaged fix; the recovered real cycle
  does not count, so the frozen gate remains 0/10.
- Fixed the next real browser finding after exact-URL recovery: a uniquely paired
  natural-language PASS named a local 220-second soak as its `唯一下一步`, but a
  later sentence merely mentioned deferred release validation. The controller
  scanned the entire prose for high-impact words and quarantined the reply. The
  natural-language gate now evaluates an explicitly labelled current action
  scope, preserves the full review as context, and strips only lines that
  explicitly defer remaining work to a later handoff. A real release/deploy
  instruction inside the current scope still blocks. Controller 26 / Skill
  revision `2026-08-10.7` add one failure-first regression; the frozen gate again
  restarts at 0/10.
- Fixed the real controller-24/revision-`.5` first-wait failure where an
  explicitly provisioned tab was handed off correctly but then disappeared from
  both `user.openTabs()` and `tabs.list()`. A doubly authorized waiting occurrence
  may now open the already-bound canonical conversation URL exactly once in the
  same browser binding, but only while the binding remains provisioned and
  `pending_handoff`. It must verify the exact URL, authenticated ChatGPT page, and
  current request identity before reading; it cannot send, create a Chat, change
  identity, or persist the occurrence-local numeric handle. Controller 25 / Skill
  revision `2026-08-10.6` implement this unpackaged correction; the frozen real
  cycle gate restarts at 0/10.
- Fixed the contract gap exposed by the ten-interaction Windows stress run: an
  implementation occurrence could submit a new request, see an immediate reply,
  and attempt to consume it through the foreground path. The controller correctly
  quarantined that reply, but the Skill did not explicitly require the submitting
  occurrence to end first. Skill revision `2026-08-10.5` now requires an immediate
  handoff after receipt confirmation; only the next authorized waiting occurrence
  may consume the reply. The run produced ten interactions, nine apply-valid
  responses, and a revision-`.4` post-quarantine consecutive segment of four;
  the changed `.5` frozen candidate restarts its formal gate at zero.
- Fixed the follow-up real browser finding that agent-created tabs can remain
  absent from `user.openTabs()` even after handoff. A provisioned-only waiting
  authorization now returns `provisioned_url_fallback_allowed`; the caller may
  use only the current occurrence's unique exact-URL tab and never persists its
  numeric handle. Controller 24 / Skill revision `2026-08-10.4` implement this
  narrower fallback; no second scheduler, Chat, or identity source was added.
- Fixed the real one-time provisioning startup gap: a newly created and still
  controlled browser tab may not expose `providerTabId`, so a correct run could
  create and initialize its sole Chat but fail before the first formal cycle.
- Added a provisioned-only `pending_handoff` binding and the lease-gated
  `promote-browser-tab-binding` command. The first waiting occurrence promotes
  only the provider identity after reclaiming the same exact URL; browser,
  conversation, and Chat replacement remain forbidden. Controller 23, Skill
  revision `2026-08-10.3`, and one new regression implement this unpackaged fix.
- Added explicit one-time reviewer Chat provisioning for a new SuperLuna task.
  When the same user request asks for a fresh review conversation, the Skill may
  create exactly one visible browser Chat, send one setup message, capture its
  conversation/provider identity, bind it, and start without asking the user to
  create the Chat manually. The setup exchange is excluded from formal cycles.
- Preserved the model boundary: provisioning never changes the reasoning selector;
  a new Chat that does not already display Extreme still requires one visible
  user selection. Recovery cannot create a replacement Chat. Skill revision is
  `2026-08-10.2`; controller was 22 and the source remains unpackaged.
- Fixed the real five-round Windows browser acceptance failure where the fifth
  long-reasoning wait reused a run-local numeric tab handle in a later heartbeat
  occurrence and falsely reported that the fixed reviewer tab had disappeared.
- Added durable in-app-browser binding state for the browser identity,
  provider-owned tab identity, and exact conversation URL. Each waiting
  authorization returns that binding so the caller can reclaim the same user tab
  from a fresh `openTabs()` listing; a run-local `Tab.id` is never persisted.
- Required every no-result browser occurrence to leave the tab as a browser
  handoff. The next occurrence claims that same provider tab, while missing or
  ambiguous identity still fails closed. Controller 22 and Skill revision
  `2026-08-10.1` implement the local contract; the changed candidate still needs
  a fresh real Windows/macOS loop and Public Beta remains false.
- Added failure-first controller and published-contract regressions. Repository
  tests now cover 144 cases. This is an unpackaged source hotfix and creates no ZIP.
- Changed the formal transport for new runs to one user-selected ChatGPT web conversation in Codex's in-app browser. The implementation task retains sole-writer ownership and reuses the same conversation id and claimed tab for submit, wait, read, and continue; `app_chat_review` remains saved-state compatibility only.
- Added `browser-network-observation` to the existing wait-bound state machine. Healthy pages are inspected without reload; a real network/load error reuses the same stable waiting identity and permits exactly one same-tab reload at the next 180-second authorized occurrence.
- Added a distinct ChatGPT rate-limit path after a real “requests are too frequent” notice: no reload, history read, or send is requested; the same waiting gate backs off for 15, 30, then 60 minutes and resets after a readable page.
- Synchronized controller 21, state schema 7, Skill revision `2026-08-09.10`, controller registry, browser protocol, READMEs, roadmap, scenarios, and release evidence. The schema version remains 7 because the browser recovery fields are optional backward-compatible additions.
- Added browser binding, guarded refresh, rate-limit, and published-contract regressions. These are local contract evidence only; real Windows/macOS browser cycles and real recovery remain unverified, so Public Beta stays false.
- This remains an unpackaged source/installed-Skill update. It does not create a new ZIP, and the existing Alpha 27 archive predates it.
- Fixed the real Windows E5 wait continuation failure where Codex Desktop reused one platform heartbeat identity for a task and rejected creation of a second heartbeat after an authorized no-evidence Chat read.
- Added `rearm-waiting-check`: after the read lease is released and the same wait phase remains live, it rotates the per-occurrence controller token while retaining the same platform heartbeat ID and returns `update_once`. The caller updates that one heartbeat to exactly one new future trigger; queued runs with the old token expire without reading Chat or changing state.
- Added a regression covering lease-active rejection, stable-ID rearm, stale-token immutability, and successful claim by the new occurrence. Controller 20, state schema 7, and Skill revision `2026-08-09.9` describe the same runtime contract.
- This is an unreleased source/installed-Skill hotfix. It does not create a new ZIP, and the existing Alpha 27 archive predates this fix.
- Clarified the Windows single-main-App reasoning contract after a real E5 startup stopped before submission: an explicit user observation of Extreme remains valid for the same implementation task, stable Chat, and uninterrupted workflow session.
- The thread API not exposing the current reasoning label is no longer treated as contradictory evidence or a reason to invalidate the confirmation before the first submission.
- Task/Chat changes, restarts, user cancellation, a user-observed downgrade, or conflicting platform evidence still invalidate the confirmation; SuperLuna never changes the model automatically.
- Added a published-contract regression for this boundary. This hotfix updates source and the installed Skill without creating another ZIP.

## 0.2.0-alpha.27

- Fixed the real E4 autonomy gap where a main-App send receipt could remain invisible beyond active polling, causing the implementation task to stop before the existing reply-wait one-shot could be created.
- Reused the same identity-gated one-shot machinery for `review_receipt_pending` and `review_waiting`; no second scheduler, recurring heartbeat, new task, or new Chat mechanism was introduced.
- A receipt-phase check now returns `receipt_reconcile`, reauthorizes exactly one raw Chat snapshot, and reconciles only the saved pre-send baseline, fixed Chat, exact payload, cycle, and stage without resending.
- The receipt-to-reply phase transition requires deletion of the bound receipt check, invalidates its token, and creates a fresh reply-wait token so queued old executions cannot read Chat.
- Active-poll timeout now ends only foreground polling in automatic mode; an unchanged exact receipt context remains eligible for the next wait-bound one-shot. Foreground fallback and recovery from an existing external blocker still require user involvement.
- Added a real-gap controller regression and a published Skill/protocol contract regression. Tests use snapshots and local state only; they create no real Chat, automation, or project task.
- Restarted the formal ten-cycle autonomous real-project gate for Alpha 27; Public Beta remains false.

## 0.2.0-alpha.26

- Fixed a confirmed autonomy contract bug: `autonomous-preflight --mode automatic` could succeed, but `init` always created a `foreground_only` state, leaving the implementation task unable to wake itself after a Chat wait.
- Added explicit `init --continuation-mode automatic|foreground`; automatic initialization persists `waiting_only` with a zero recurring interval, while foreground initialization cannot advertise, bind, claim, or authorize a scheduled waiting check.
- Changed entry to `review_waiting` so automatic mode returns `schedule_once`, while foreground fallback returns `foreground_resume_required` with no active wait token.
- Preserved `waiting_check_action`, token, and automation identity through both normal submission confirmation and user-authorized late-receipt recovery; these public command results previously discarded the information needed to create the one-shot wakeup.
- Synchronized the published V7 automation schema with runtime-required waiting identity fields and exact mode/interval pairs.
- Corrected the Alpha 22–25 equipment scenario evidence: its request/reply identity and recovery checks remain useful, but external coordinator wakeups mean it is not autonomous-loop or frozen-candidate release evidence.
- Added four regressions for automatic initialization, foreground non-automation, three wait-bound cycles without foreground wakeups, and the published wait-bound automation contract. No real Chat, automation, or project task was created by these tests.
- Restarted the formal ten-cycle autonomous real-project gate for Alpha 26; Public Beta remains false.

## 0.2.0-alpha.25

- Fixed the final real E3 receipt mismatch: text files ended with a newline while the main App composer stored the submitted user message without that terminal line break.
- Main-App receipt hashing now normalizes only terminal CR/LF on payload and observed text; interior whitespace and every substantive character remain exact.
- Keeps compatibility with Alpha 23/24 contexts whose saved hash used the raw text file, so the original E3 cycle can be recovered without rewriting the baseline or resending.
- Extended the user-authorized late-receipt regression with a terminal-newline source payload and a no-newline observed message.
- Restarted the frozen-candidate release gate for Alpha 25; the mixed-version three-round diagnostic remains scenario evidence, not formal Alpha 25 3/10.

## 0.2.0-alpha.24

- Fixed the second real multi-cycle boundary found after Alpha 23: an exact request may become visible only after the bounded active-polling window closes.
- The polling deadline now stops automatic reads without invalidating the pre-send baseline; a later user-authorized recovery can confirm one exact new request and must not resend it.
- Added an explicit `--user-authorized-recovery` gate for confirming that late receipt directly from the preserved `external_blocked` cycle without creating a replacement cycle.
- An expired window with no visible receipt returns a deterministic blocked action, while an exact unique late receipt remains recoverable.
- Required complete, unmodified `read_thread` JSON for main-App snapshot evidence; hand-truncated or reconstructed snapshots are explicitly non-evidence.
- Extended the delayed-receipt regressions to recover an exact request after the active window and from an externally blocked cycle only with user authorization, while retaining fail-closed behavior for changed payloads, ambiguity, stale cycles, and unresolved sends.
- Restarted the formal consecutive real-project release gate for Alpha 24; local tests and mixed-version E1–E3 evidence do not count as frozen-candidate 3/10.

## 0.2.0-alpha.23

- Fixed a real Windows single-main-App multi-cycle failure where the Chat send tool returned only the stable Chat ID and the request became readable shortly afterward.
- Added `prepare-main-app-submission` and `reconcile-main-app-submission` so the one send is bound to a pre-send message-ID baseline, fixed Chat, cycle/stage, and exact payload SHA-256.
- Treats a temporarily invisible receipt as eventual consistency rather than immediate external failure; bounded read-only reconciliation continues without resending.
- Accepts only one exact new user message, rejects old same-text messages, multiple matches, changed Chat/payload, stale cycle context, and expired unresolved contexts.
- Added three controller regressions and one published-Skill contract regression; local tests do not replace the restarted real-cycle gate.
- Restarted the formal consecutive real-project release gate for Alpha 23; Windows/macOS matrices and Public Beta remain incomplete.

## 0.2.0-alpha.22

- Added read-only before/after App thread snapshot discovery for newly created regular App Chats.
- A unique new `kind=chatgpt` stable identity is returned as a user-confirmation candidate; discovery never creates workflow state or a registry binding.
- Zero, multiple, title-mismatched, or conflicting candidates fail closed, and Codex tasks cannot be mistaken for reviewer Chats.
- Updated the Skill startup flow so users no longer need to copy internal Chat IDs that the desktop UI does not expose.
- Sanitized a local dual-device handoff document that had caused the release-tree private-identifier regression to fail.
- Restarted the formal consecutive real-project release gate for the changed candidate; real Windows/macOS loop evidence and Public Beta remain incomplete.

## 0.2.0-alpha.21

- Serialized the complete reviewer-only native App session lifecycle per resolved session file across threads and processes.
- Fixed a confirmed race where two concurrent starts could each launch a ChatGPT App process and overwrite one durable session record, leaving the other process untracked.
- Made concurrent starts deterministically create one owned process and reuse it from the second caller; start and close now share the same lifecycle lock.
- Added a concurrent start regression and a real spawn-process exclusion test. These are local controller/adapter evidence and do not claim macOS device validation.
- Restarted the formal consecutive real-project release gate for the changed candidate while retaining three historical cycles as feasibility evidence.

## 0.2.0-alpha.20

- Serialized binding-registry read, uniqueness validation, state binding, and registry replacement under one cross-process lock so independent concurrent registrations merge instead of failing on a shared stale revision.
- Added a six-process regression proving every unique task remains in the registry and every corresponding state remains bound.
- Synchronized the published V7 state schema with runtime naming templates 1, 2, and 3.
- Kept the compatibility command `closure-check` but changed its result to an explicitly local-controller-only summary; it no longer reports “loop usable” or a completed product state, and it explicitly leaves real-device and Public Beta gates false.
- Reset the formal consecutive-cycle release gate for this changed candidate while retaining the earlier three cycles as historical feasibility evidence.

## 0.2.0-alpha.19

- Synchronized the published V7 state schema with the runtime contract by accepting the trusted `main_app` reasoning-confirmation source already enforced by the controller.
- Added a package regression test that fails whenever the published reasoning-source enum diverges from the supported runtime sources.
- Kept `closure-check` classified as a local automated summary rather than real-device or Public Beta evidence; its stronger release-gate semantics remain unresolved.

## 0.2.0-alpha.18

- Bound uncertain native App submission reconciliation to a captured pre-click baseline, fixed Chat ID, App instance, and payload hash; an older identical user message can no longer be accepted as the current receipt.
- Added regression coverage for old/new same-text messages and preservation of the baseline when a post-click receipt times out.
- Removed the package test's dependency on the extraction-directory name while preserving the compatibility plugin ID `luna-review-loop` and public display name `SuperLuna`.
- Made the macOS-only native session process probes fail closed on unsupported platforms instead of invoking a missing `ps` command on Windows.

## 0.2.0-alpha.17

- Synchronized the PEP 440 package version, lockfile, release report, and English/Chinese README labels with `0.2.0-alpha.17`; package tests now enforce cross-file version consistency.
- Labelled every current `verified` execution fact as `manual_attested`; status, doctor, and audit output now distinguish a human attestation from platform verification.
- Migrated alpha.16 verified records conservatively to the same human-attestation label and added validation and migration coverage for the boundary.
- Closed the cross-process state race on waiting-check claim and reply consumption: `save_state` now compare-and-writes under a short-lived standard-library lock (`fcntl` / `msvcrt`), revision conflicts surface as `StateRevisionConflict`, and concurrent waiters reload to `waiting_check_busy` / `waiting_check_expired` or `already_consumed` instead of double-claiming. Multiprocess tests cover exclusive `review_poll`, single reply consumption, and lock release after process crash.
- Made App Chat `read_reply` fail closed unless request and assistant share the same non-empty trusted `turn_key`; missing, blank, and `fallback-turn-*` identities no longer pair via `None == None` or message-id fallback, so unrelated complete replies cannot be applied to the current request.

## 0.2.0-alpha.16

- Added an explicit execution-fact ledger (`unknown`, `authorized`, `verified`) so Chat advice, model-route authorization, and real execution evidence cannot be conflated.
- Changed `record-high-attempt` into an authorization record; it no longer claims a High execution completed. Added manual `verify-execution` evidence recording for a matching High or approved Terra request.
- Required the same-blocker High record to be execution-verified before Terra advice or a Terra request can proceed, and removed the executor-field mutation that previously implied a Terra switch.
- Migrated legacy route records conservatively: unknown old execution remains `unknown`; an explicitly approved legacy Terra request becomes only `authorized`.

## 0.2.0-alpha.15

- Added a strict final Chat routing block: casual or malformed model mentions fail closed to Luna Medium.
- Added an 80/20-style ceiling of at most two Luna High turns per ten meaningful steps and one Terra turn per twenty.
- Required every Terra recommendation to reference a completed Luna High attempt for the same stable blocker; Chat remains advisory and explicit user confirmation remains mandatory.

## 0.2.0-alpha.14

- Changed the normal implementation default from Luna High to Luna Medium while preserving old saved-state compatibility.
- Defined bounded evidence conditions for a Luna High turn and made Terra a last escalation only after the same blocker survives that turn.
- Tightened all five Terra signals with reproducible evidence thresholds; Terra still requires verified capability, a safe boundary, and explicit user confirmation for exactly one turn.

## 0.2.0-alpha.13

- Replaced confirmation-style review packets with a bounded independent-review contract: proven, inferred, and unverified claims; falsification questions; evidence sufficiency; and one next action with acceptance criteria.
- Made local screenshot paths explicitly non-evidence for UI/UX review. Visual PASS now requires images the reviewer can actually see.
- Restored the bounded reviewer-only macOS App instance because the main App cannot automatically change ChatGPT reasoning. Main and reviewer roles use matching 🛠/💬 titles; no app-copy, icon, plist, or signature modifications are used.
- Closing the reviewer App with its state file now invalidates that instance's Extreme evidence, preventing stale confirmation from leaking into the next round.

## 0.2.0-alpha.12

- Enforced one main Codex/ChatGPT App: the legacy native-session start entrypoint now fails closed and can no longer add a second Dock instance.
- Moved normal App Chat submission and reply identity retrieval to the main App's stable-ID task tools.
- Added a trusted `main_app` Extreme confirmation source without a native process identity. Current App tooling preserves but cannot change ChatGPT Chat reasoning, so a non-Extreme Chat requires one user click in the existing window.
- Retained strict cleanup for verified legacy task-owned App processes and migrated the live shrine UI/UX test without losing its third review reply.

## 0.2.0-alpha.11

- Restored a fixed visual role set in generated titles: 🛠 execution, 💬 reviewer Chat, and ⏳ waiting check, while keeping the project and round text identical for instant matching.

## 0.2.0-alpha.10

- Fixed native reply pairing when a rendered user unit also exposes sibling assistant items through shared React props; the parser now prefers the unit's direct item before bounded fallback traversal.

## 0.2.0-alpha.9

- Restored active three-surface naming with one matching project/round prefix and no stale model label.
- Added machine-readable title actions so the task, dedicated reviewer Chat, and one-shot waiting check are actually renamed during binding.
- Replaced brittle native App component-name receipt parsing with structure-based message identity discovery.
- Added read-only submission reconciliation so an uncertain click can recover one real receipt or prove an identical draft remains unsent without duplicating the review.

## Unreleased

- Clarified continuous-loop completion: a stage PASS with a concrete next step immediately starts the next stage in the same implementation task; only explicit overall completion with no next step may stop the loop.
- Fixed a real macOS mode-isolation bug: browser reasoning settings do not control App Chat, so browser evidence can no longer confirm Extreme or authorize formal review.
- Added a bounded native macOS App-session owner with exact PID/profile cleanup and loopback-only reuse.
- Extended the native adapter to target a stable App Chat ID, switch and read back `极高`, submit one inline review in the same App instance, capture the real request identity, and read only the complete assistant reply paired with that request.
- Fixed native composer verification for App-rendered extra blank lines; an identical retained draft can now resume safely after a pre-send timeout without reinserting its text.
- Confirmed that reasoning state is App-instance-local and persisted the native instance identity in workflow state; submissions from a different instance are rejected.
- Legacy browser-based confirmations are invalidated on state load; only native App readback or user observation of `极高` in the exact bound App Chat can pass the gate.
- Kept App Chat as the only submission/reply transport and preserved the ban on automatic Pro/Terra switching, new Chats, and browser-based review messaging.

## 0.2.0-alpha.7 - 2026-08-04

- Moved normal App Chat submission, waiting, reply reading, and continuation from the coordinator to the implementation task.
- Added `autonomous-preflight`; the older `coordination-preflight` remains a compatibility alias but now reports implementation ownership and an exception-only coordinator.
- Removed the normal user instruction to type “continue” while waiting; foreground resume remains only a safe fallback when one-shot capability is unavailable.
- Made inline text packets the normal review path and limited attachments to milestone evidence.
- Added an integrated regression that covers implementation-owned preflight, confirmed submission, gated wait, authorized Chat read, reply continuation, and duplicate protection.
- Reduced the monitor to read-only progress reporting; routine nudges, reply relays, and deadline control are outside its role.

## 0.2.0-alpha.6 - 2026-08-03

- Added a read-only coordination preflight that blocks execution and monitoring before a distinct App Chat binding, coordinator read/send capability, and user-confirmed review mode exist.
- Automatic mode now also requires one-shot waiting-check capability; foreground mode remains available without scheduled work.
- Defined coordinator, implementation-task, and read-only monitor ownership so executors never guess a Chat/model and an existing monitor is resumed per implementation turn without recurring automation.
- Bound every wait check to its one-shot automation ID, made each occurrence claimable only once, cleared stale IDs across wait cycles, and added a second authorization check immediately before Chat access.

## 0.2.0-alpha.5 - 2026-08-03

- Renamed the public product to **SuperLuna** while preserving the `luna-review-loop` plugin ID, `$luna-chatgpt-review-loop`, the installed folder, state schema, and `lcrl` command as compatibility identifiers.
- Rewrote the user entrypoint around the five visible states and the simple Codex → App Chat → Codex loop.
- Marked Pro, Terra, the quota ledger, historical V8 packages, browser adapters, and broader orchestration as experimental or compatibility-only rather than Alpha core features.
- Added a machine-readable Alpha release report that distinguishes implemented and automated evidence from real-device and cross-platform validation.

- Replaced the attempted recurring wait check with chained single-future-occurrence checks: schedule only while waiting, schedule the next only after a no-reply result, and delete the pending one-shot before implementation resumes.
- Added scheduled-reply continuation proof: a wait check must delete its bound one-shot before consuming a new reply once and continuing the original implementation task.
- Added duplicate-start exclusion and a Mac queue-replay release gate that records zero-read, zero-write, unchanged-state evidence.
- Added one plain-language status exit for every foreground result: the user now receives only one of five states, a short explanation, and a clear next choice; command failures no longer expose controller error text.
- Retired recurring heartbeat execution after real Mac evidence showed due checks can queue behind active Work and take over the task immediately afterward.
- Made `tick --source heartbeat` an immutable compatibility exit that always returns `monitor_retired` without reading runtime history, reading Chat, claiming a lease, or changing state.
- Changed new state to `foreground_only` recovery with a zero-minute schedule and made missing automation the healthy default.
- Kept manual foreground resume as the safe Alpha fallback until a true event-driven App Chat observer is available.
- Clarified that App Chat recovery never refreshes a page or reloads the desktop app; browser refresh belongs only to a separately confirmed manual adapter.
- Removed the proposed ordinary daily Pro cap. The 180-active-minute threshold, three meaningful steps, one outstanding request, confirmation, and verified completion remain the quota guards.
- Set English as the primary open-source documentation language with Chinese supplementary documentation.
- Confirmed Windows and macOS as the intended desktop support targets and Linux as controller-only until transport support exists.

## 0.2.0-alpha.3 - 2026-08-03

- Fixed a contract mismatch where a prompt requested `next_operation` while persistence required `next_step` plus `operation_package`.
- Added lossless compatibility normalization for already-completed `next_operation` responses without spending another review.
- Required receipt reconciliation to persist the exact user request identity before the assistant response identity, even when both are returned in one completed Chat turn.
- Hardened the heartbeat contract so one wakeup calls `tick` exactly once and cannot overwrite a real leased action with a second-call `concurrent_backoff`.
- Added the macOS handoff guide, standalone cross-platform Skill installers, Chinese supplementary README, MIT license, and sanitized release checklist.

## 0.2.0-alpha.2 - 2026-08-02

- Added a versioned quota-policy ledger while preserving Luna High and Sol Extreme as the defaults.
- Added idempotent active-development progress events and a guarded Pro threshold of 180 active minutes plus three meaningful steps.
- Added explicit Pro request, confirmation, cancellation, verified guide completion, and automatic restoration to Sol Extreme after completion.
- Added verified Terra capability recording and one-bounded-turn request, confirmation, cancellation, and Luna restoration.
- Kept automatic model switching and automatic task/Chat creation structurally forbidden.
- Constrained milestone guides to existing Markdown files inside the project root and verified their SHA-256 before resetting the Pro counter.
- Preserved progress-event and evidence-fingerprint deduplication for the full bounded ledger, and distinguished completed, cancelled, and capability-downgraded Terra outcomes.

## 0.2.0-alpha.1 - 2026-08-02

- Synchronized the open-source plugin with the V8 P0 controller and Skill revision `2026-08-02.12`.
- Added a stable binding registry and readable Chinese titles for implementation tasks, reviewer Chats, and recovery checks.
- Added exact attachment-name verification and blocked formal submission when required evidence is not verified.
- Added V2 reviewer operation packages so Luna receives bounded, ordered, testable implementation instructions.
- Added `review_receipt_pending` reconciliation so incomplete send receipts cannot trigger duplicate submissions.
- Added recovery of action leases after observed completed or aborted runtime turns.
- Shortened the heartbeat template so long Windows installation paths remain below the 1200-byte safety limit.
- Reframed the project as a Codex plugin with a Skill entrypoint and deterministic local controller; no standalone application is planned.

## 0.1.2 - 2026-08-02

- Enforced legal workflow transitions so local implementation cannot bypass `review_submit_pending`.
- Bound every review request and response to the same cycle and stage, preventing stale-result application.
- Quarantined reviews sent before confirmed Extreme / 极高 mode instead of applying them.
- Added one-shot notifications for external blockers, review-mode blockers, and quarantined results.
- Hardened `doctor` to report malformed legacy state instead of failing before diagnosis.
- Expanded the controller regression suite from 7 to 14 tests and the built-in self-test from 5 to 7 checks.

## 0.1.1 - 2026-08-02

- Added a hard user-confirmed Extreme / 极高 App Chat reasoning gate before formal review submission.
- Added expiring execution leases so three-minute checks do not overlap long-running or disconnected actions.

## 0.1.0 - 2026-08-02

- Replaced mutable V6 heartbeat prompts with V7 local durable state.
- Added atomic revisions, confirmation leases, action leases, diagnostics, migration, and short prompt rendering.
- Added App Chat quota and writer-role invariants plus a reviewer policy firewall.
- Added network-disconnection replay, deduplicated runtime event accounting, and bounded recovery.
- Added generic and Godot profiles, result contracts, capability negotiation, CI, and open-source project documentation.
