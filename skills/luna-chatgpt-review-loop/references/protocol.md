# SuperLuna browser-first review protocol

Review submission means one browser message to the bound reviewer Chat. A local
path is never reviewer-visible evidence. Formal full-project review requires a
deterministic sanitized package made from Git-tracked sources plus explicitly
declared authoritative untracked files. Its manifest records every relative
path, byte size, SHA-256, exclusions, exact commit and dirty state. All split
volumes must be visibly present in the current request and hash-confirmed before
send. Partial selections must say `partial_materials` and list files, hashes and
uncovered paths. GitHub is a separate mode: it requires a repository URL, exact
commit SHA and verified reviewer access; a commit name alone proves nothing.
Source coverage and machine/runtime evidence are independent evidence scopes.
The submission is not a Git commit or push, and the workflow must not create one
without user authorization. When Git commit review is not selected, it may
continue with readable local evidence, but that evidence must still obey the
partial-versus-complete coverage labels and current-Chat receipt gate above.

For a clean Git-backed project the preferred mode is
`repository_commit_review`. `prepare-repository-commit-review` binds the
canonical origin URL, repository identity, exact local HEAD, informational
branch label, complete tree-manifest hash, and root/nested blob canaries. A
floating `main`, `HEAD`, branch, tree, blob, or commit-page URL cannot replace
those identities. The current Chat must separately produce a
`repository_access_receipt` proving it opened the exact commit, could see the
complete tree, and matched both canaries. A URL string or visible repository
homepage is not access proof. Replacement Chats always discard the old receipt.

Every formal repository round then records exact base and head commits, verifies
that base is an ancestor of head, hashes the complete binary diff, lists changed
paths with head blob identities, records clean/dirty state, and indexes runtime
evidence separately. A current tree receipt means the reviewer may read any
relevant file at exact head without rescanning all history; it does not prove the
round diff or runtime behavior. Dirty state, a missing/mismatched remote,
unreachable commit, private/authentication access not independently verified, or
a broken base-to-head chain fails closed into `full_source_attachment`; it never
falls back to partial formal review. No controller path commits, pushes,
publishes, or changes repository visibility.

Complete-source attachment transport has a separate host-capability gate. Before
an account slot, browser runtime, or first/replacement Chat is created,
`declare-attachment-upload-capability` must record an explicit platform
`direct_file_upload` declaration. An unverified or missing capability stops with
zero browser actions and `attachment_upload_capability_missing`; DOM injection,
system-filechooser simulation, repeated clicking, reload, and page reopen are
not supported fallbacks. Repository-commit review bypasses this attachment gate.

One `authorize-attachment-upload` attempt is allowed for the prepared package.
A filechooser or direct-upload failure records one closed attempt, requires the
account slot to be released, preserves the same package identity, sends no text,
reads no Chat, and creates no replacement package. Its recovery id permits one
controlled retry of that exact package. A second failure is terminal for the
host capability. A successful upload is still not review-ready until
`confirm-attachment-upload-receipt` matches the current composer identity,
platform receipt identity, and every volume's name, byte size, and SHA-256.
Visible filenames, buttons, or chooser state alone are not an attachment receipt.

## 1. Observable loop

```text
local work → submit once in bound web Chat → wait → consume paired reply → local work
```

The implementation task is the sole project writer. One user-selected ChatGPT
conversation in Codex's in-app browser is the formal reviewer. The binding is
the conversation id in `https://chatgpt.com/c/<conversation-id>` plus the claimed
browser tab; title and focus are display hints only. `app_chat_review` remains a
saved-state compatibility transport, not the default for new work.

After that exact bound reviewer Chat is visible in the foreground and a live
`startup` account slot exists, the controller may issue
`authorize-browser-review-mode-selection --target extreme`. The same task may
then select the visible `极高/Extreme` control and must confirm it with
`confirm-review-mode --source in_app_browser_automatic`, the exact authorization
revision, account slot, browser, and reviewer identity. Missing or ambiguous UI
fails closed. This automatic action applies only to the exact bound reviewer Chat;
it never changes the Codex implementation model or any other Chat. A bounded
rollover is allowed only after two formal reviews or a real rate-limit event.
After that confirmation is durably recorded, submission reopen, pre-send
reconciliation, and final one-shot send authorization accept its
`in_app_browser_automatic` source under the same exact Chat, task, browser,
account-slot, operation, foreground, and revision checks as the manual
`in_app_browser` source. It grants no broader browser or model authority.

### Repository self-retest profile

SuperLuna's own source-repository development and real-loop retests use the
dedicated `superluna_repo_retest_v1` profile. For implementation task identity
`<task-id>`, the controller derives one deterministic task hash and accepts only
`.superluna/retest-runs/<task-hash>/project` as the mutable project plus
`.superluna/retest-runs/<task-hash>/state.json` as its state. The repository
root, ordinary source children, adjacent runs, symlink escapes, and external
absolute paths fail closed before a write probe, state use,
the machine account gate, or browser initialization. Account-slot state records
the same scope so a lease cannot drift from one profile or project sandbox to
another.

The repository's `.codex/config.toml` supplies a host `workspace-write` boundary
for newly started trusted-project tasks and excludes system temporary paths.
That host setting is not claimed to retroactively constrain an already-open
task. This profile is only for developing and retesting SuperLuna itself. The
installed product's `generic` profile remains compatible with a user's
explicitly selected, host-authorized external project.

By default the workflow never creates a Chat. One explicit user request for a
new reviewer conversation authorizes exactly one visible browser Chat plus one
initialization message, as defined in `browser_chat_provisioning.md`; that setup
exchange is not a formal review cycle. Ordinary browser recovery never creates
a replacement Chat. A bounded rollover is allowed only after two formal
reviews, counted by exact Chat identity across run boundaries, or a real rate
limit; it retires the old Chat and provisions exactly one replacement with
the same-generation complete source package plus a structured rollover handoff.
For a clean reachable Git-backed project, the same recovery first re-runs
`prepare-repository-commit-review`. A successful exact-commit preparation
atomically supersedes only a stale attachment-upload rollover blocker, retains
the unique rollover authorization, binds a deterministic structured handoff,
and returns to the one replacement-Chat startup. No repository access receipt
is fabricated; the replacement Chat must prove exact commit, full tree, and both
blob canaries before formal review.
An ordinary turn entry for a legacy attachment-blocked rollover first projects
`repository_rollover_preparation_required`, never an indefinite attachment
capability wait, when local exact-repository facts are complete. The sole next
controller command is `prepare-repository-rollover-recovery`. It is bound to the
original implementation task and additionally proves anonymous exact-commit
advertisement with credential helpers disabled. Missing identity, dirty state,
unknown remote, absent remote tracking, unreachable commit, or missing canaries
stays blocked with zero browser authority. Success restores `rollover_pending`
but leaves the replacement Chat repository access receipt unconfirmed.
If an older controller consumed the same-generation replacement-startup
provisioning but provably produced no browser initialization, Chat identity,
submission/read receipt, or active/expired-but-uncertain slot, ordinary turn
entry exposes one `reconcile-orphaned-provisioning` action. Reconciliation is
atomic, single-use, and requires the exact implementation task, state identity,
reviewer generation, and repository identity. Missing evidence, identity drift,
any side effect, or a concurrent slot remains fail-closed. The recovered
authorization can create only the original generation's one startup slot and
does not constitute a repository access receipt.
SuperLuna publishes the atomic tracked pair `SUPERLUNA_REVIEW_CANARY.txt` and
`review-canary/NESTED_CANARY.txt` for this proof. Preparation requires both paths
to be regular blobs in the exact commit and returns their exact blob SHAs. A
missing half, symlink, or path mismatch fails closed rather than silently using
a volatile README or source file. Generic repositories without this dedicated
pair may still use deterministic root+nested regular blobs.
The implementation workspace and reviewer repository are separate identities.
For `superluna_repo_retest_v1`, the implementation task remains confined to its
exact `.superluna/retest-runs/<id>/project` fixture, while repository review is
derived from the trusted `source_checkout` in that same validated retest scope.
For generic Git projects it is the containing Git toplevel. State persists the
local reviewer root separately from canonical remote, exact commit, tree hash,
and repository identity; the local path is never sent as reviewer evidence.
Old states resolve this identity during preparation. Injected roots, symlinks,
cross-checkout roots, or stable identity drift fail closed before browser use.
It cannot inherit only a prose summary or the previous Chat receipt. Normal operations on a bound Chat are tail-only and
return `full_history_scan_allowed=false`. The workflow never switches
model/reasoning or sends through a second transport. The user explicitly
confirms the visible reviewer mode unless the new Chat already shows the
required label.
An already-visible required label satisfies that confirmation without changing
the selector.

Every formal packet starts with the exact controller-rendered
`[SUPERLUNA_REVIEW_RUN]` ... `[/SUPERLUNA_REVIEW_RUN]` block. Its trusted
state-local `RUN_ID` is also required by the pre-send authorization. Earlier
messages in a reused Chat are background only and cannot bind, count, rename,
or reject the current run.

## 2. Start gate

The implementation task first activates the in-app-browser control skill and
opens ChatGPT in its own browser when no ChatGPT tab is present. A coordinator's
browser tab is not inherited by a newly created implementation task. For a
pristine provisioned `pending_handoff`, the controller's startup-reopen
authorization permits one exact canonical-URL open and a revision-bound startup
rebind before project work; it permits no send and no replacement Chat.
When the user supplied an exact existing Chat and the task successfully verifies
that page but the platform exposes no provider identity, the task may bind the
non-handle `canonical_url_only` marker. Every later access remains exact-URL and
occurrence-authorized; a numeric `Tab.id`, title, or focus is never persisted.

For an existing fixed reviewer Chat, before project writes or a formal
submission the caller must prove that the same claimed tab is readable, its URL
still identifies the bound conversation, and its page is ChatGPT. A network
error, login boundary, ambiguous tab, or changed conversation fails closed
before local work begins. Explicit one-time new-Chat provisioning has one
narrow ordering exception: the implementation task first completes and verifies
its first real, minimal project change before reading the Browser Skill or
acquiring a browser slot. A temporary workspace probe is insufficient. If the
host requests approval or the real change is not durably written, the run stops
with zero Chat side effects. After the new Chat is bound, the ordinary tab gate
applies to all later project writes. The account-browser controller also requires
`--new-chat-local-work-status completed_and_verified`; without it, startup is
rejected before a slot or browser permission is issued.

Before formal preflight, `startup-diagnostics` reports exactly one first
failure from caller-observed facts: stable implementation identity, initialized
task-local browser, authenticated ChatGPT, one reviewer Chat with stable
identity, visibly confirmed Extreme mode, Chat read/send, one-shot waiting, and
distinct implementation/reviewer identities. It never opens a browser, creates
a Chat, initializes state, or repairs a missing capability.

Before opening a fixed-Chat tab, `browser-startup-plan` deterministically
prefers the unique exact-URL object from `user.openTabs()`, then an existing
controlled exact-URL object. A new exact-URL tab is legal only when neither list
contains a match and that one open is explicitly authorized. Selecting a new
tab while a user exact-URL tab exists fails closed. Conversation evidence comes
from stable message/article nodes and canonical identity, never localized
snapshot phrases such as `你说：` or `ChatGPT 说：`. Composer readiness uses the
actual interactive and disabled state; visible Extreme remains separate visual
evidence rather than a whole-DOM substring test.

When a bound wait has an expired `waiting_review_poll` claim, ordinary turn
entry returns `waiting_platform_lookup_required` instead of blocking forever.
The host may inspect only the exact saved platform task id. The same
implementation task then invokes `recover-stale-wait` with `found` or
`not_found`: `found` rotates the token and updates that task in place;
`not_found` clears the dead binding and enters the normal one-replacement bind
barrier. Both paths remain in the same waiting state, grant no Chat or project
access, and keep `user_choice_required=false`.

`retire-missing-wait` remains a compatibility path for explicitly authorized
terminal retirement of an orphan wait that is not in this recoverable expired
claim state. A task assertion, id mismatch, wrong implementation identity, or
live claim cannot recover or retire the wait.

The read-only observer reports the active one-shot waiting identity as its
effective `automation_id` whenever a wait is bound. It also exposes
`controller_automation_id`, `waiting_check_automation_id`, and
`waiting_check_active`; a retired legacy controller id of `none` must never be
interpreted as proof that the current one-shot wait is missing.

For delegated tasks, `<codex_delegation>.source_thread_id` identifies the
coordinator/source task, never the newly created implementation task. The
implementation task first uses the host-injected `CODEX_THREAD_ID` as its own
identity. When `--implementation-thread-id` is omitted,
`startup-diagnostics` reads only that trusted environment value and fails
closed if it is absent. It never guesses from a title or delegation wrapper.
Passing `--delegation-source-thread-id` still fails closed when that source
identity is incorrectly reused as the implementation identity.

`autonomous-preflight --transport in_app_browser` verifies distinct
implementation/reviewer identities, browser binding/read/send capability, and
one-shot waiting capability. Automatic initialization must use
`--review-transport in_app_browser --continuation-mode automatic --goal-mode continuous`, producing
`heartbeat_mode=waiting_only` and `interval_minutes=0`. It cannot silently fall
back to App Chat or foreground mode.

Before initialization, the implementation task records the user's overall goal
and the already-authorized continuous work scope. `continuous` is the default
for development workflows. `single_stage` is reserved for a user request whose
entire authorized goal is one bounded stage; it cannot be selected merely to
turn a stage PASS into an early exit.

For a `continuous` goal, transitions into the active `local_work`,
`result_received`, and `review_submit_pending` boundaries publish
`continuation_required=true`, an explicit `next_action`, and
`turn_completion_allowed=false`. The implementation task must perform that
next action in the same turn. An active boundary, local milestone, or statement
that the loop remains in progress is not permission to end the turn.

When a visible submission attempt encounters the real ChatGPT history
rate-limit notice, releasing its account slot as `rate_limited` is only the
first half of recovery. While the state remains `review_submit_pending`,
`schedule-submission-retry` persists one `submission_retry` wait at the shared
account circuit's exact cooldown. Early or duplicate occurrences cannot open
the browser or read Chat. The due occurrence retires itself before requesting one
rollover-authorized `startup` with reviewer identity `none`. It provisions
exactly one replacement reviewer Chat, binds its canonical identity, reconfirms
the visible reasoning mode, and continues the original unsent submission. The
rate-limited old Chat is permanently denied browser access; it is never reopened,
refreshed, probed, or scanned. Another rate limit schedules exactly one
replacement. This recovery kind never becomes a reply-reading wait and never
uses a recurring rule.

Every ordinary resumed turn with an existing state must run `guard --state
<state> --reason turn_entry --implementation-thread-id <current-task-id>` as its first executable action, before project
reads, tests, browser initialization, or writes. While the saved status is
`review_receipt_pending` or `review_waiting`, the guard returns
`waiting_turn_blocked`, creates no action lease, and changes no state. The turn
must then end without project or browser access. `--replace` cannot override
this waiting boundary. A platform-fired waiting occurrence is the only
exception: its first action remains `waiting-check`, followed by
`authorize-waiting-chat-read`; an ordinary user or coordinator message cannot
claim that source.

Only the newest event's platform heartbeat wrapper can identify a scheduled
waiting occurrence. A waiting prompt, token, or automation id preserved in an
older turn or context-compaction summary is historical data and must never
override a newer ordinary user or coordinator wakeup. Such an ordinary wakeup
always uses `guard`, never the stale `waiting-check` command.

There is one narrower pre-wait condition: a confirmed submission whose
controller token exists but whose platform automation id is still `none` is not
yet a real wait. The exact implementation task receives
`waiting_binding_recovery_required`, still with no project, test, browser, or
Chat authority and no action lease. It may only execute the returned platform
wait create/bind/render/update sequence. A different task identity fails
closed. Once the platform id is bound, every ordinary wakeup returns the normal
`waiting_turn_blocked` result again. If the never-bound RDATE has already
expired, this exact-task guard atomically rotates the token and writes a fresh
future 180-second RDATE before returning the create contract. It cannot rearm a
bound platform wait.

The guard also requires the exact implementation-task identity before granting
any ordinary work lease. A missing identity or one belonging to another task
fails closed even when no lease is currently active; it cannot bootstrap access
to the state. This is reported as `implementation_task_mismatch` with a concrete
same-task recovery action and never as a vague product choice. Same-task serial
recovery remains limited to an ordinary
`turn_entry` or `apply_result` lease.

An explicitly terminated retest does not escape this established state by
choosing a new filename. After the old state is `external_blocked`, every
waiting identity and action lease is retired, and a current user authorization
identity is available, `reset-for-retest` may archive the old cycle and
atomically hand that same state to one exact implementation task. It clears
task-local browser, request/response, attachment, and operation-package evidence
while retaining the fixed reviewer conversation identity. The replacement task
must still enter through `guard`, rebind its own browser, and reconfirm visible
Extreme mode. Waiting states, live leases, ambiguous identities, and blank
authorization fail closed without mutation.

Context compaction inside an active implementation turn is not a new external
authorization. If the host resumes execution after compaction, it must retain
the same stable implementation-task identity when it re-enters the guard; it
must not omit the identity, substitute a title, or ask the coordinator to wake
the task again.

The compatibility `--replace` flag cannot preempt any active lease. A later
serial turn may recover only an ordinary `turn_entry` or `apply_result` lease
when it supplies the exact persisted implementation-task identity. Cross-task,
waiting-read, and browser-reopen leases remain non-reclaimable with or without
the flag.

A completed workflow is terminal for ordinary turns. A new overall goal may
reuse the same implementation task, project, and bound reviewer Chat only via
`begin-new-goal`, under that task's current `turn_entry` lease and an explicit
current user-message/delegation identity. The command fails closed if any
waiting check survives, archives the authorization fact, clears the previous
completion and operation package, and requires fresh visible reasoning-mode
confirmation. It is not a recovery path for waiting or a generic "continue".

`observe-run` is a read-only monitoring projection. It derives the five-state
view and evidence age from saved progress events, marks development as possibly
stuck at the configured threshold (20 minutes by default), never marks waiting
for Chat as stuck, and leaves the state bytes and revision unchanged.
`observe-runs` accepts one or more `--state` arguments and returns the same
projection for every state plus counts by all five user-facing statuses and the
number possibly stuck. It validates every input before producing the overview;
invalid input fails closed without writing any state, sending task messages,
reading Chat, acquiring execution, or changing workflow state.

## 3. Submit exactly once

Before state initialization, an explicitly provisioned browser Chat must have a
real canonical `/c/<conversation-id>` identity. A transient `/c/WEB:<uuid>` URL
is only an in-app-browser routing handle and is never a valid reviewer identity.
The implementation task resolves the unique canonical sidebar/page link for the
same initialized conversation and verifies the original initialization exchange
in that URL. Ambiguous resolution fails closed without a second Chat or resend.
State initialization also binds to the host-provided `CODEX_THREAD_ID`. An
explicit implementation identity that differs from the current host task is
rejected before state creation; a delegation wrapper's `source_thread_id` can
never become the writer, run-binding, account-gate, or waiting identity.

Immediately before the send, capture the same tab, conversation id, visible
message baseline, and exact packet identity. Submit once through the visible
composer. Only one new exact-body message after the baseline is a receipt.

An uncertain network/UI result is reconciled in that same tab. It never permits
a resend, a new Chat, a different tab, or an App Chat relay. Old same-body
messages, multiple candidates, changed body, changed Chat, and stale context all
fail closed.

The exact request identity is persisted separately from the response identity.
For canonical ChatGPT UUID conversations, submission confirmation rejects a
truncated request turn/message UUID before state transition. The implementation
must reread the existing sent message node and must not resend.
Reply retrieval starts from that request and consumes only its complete paired
assistant response. Partial streaming output and unrelated turns are not input.
After an exact submission receipt enters waiting, the submitting occurrence
hands off the tab and ends without reading the response, even if the assistant reply is already complete.
The next authorized `waiting_check` is the sole
consumer; a foreground read is quarantined and breaks consecutive release proof.

The browser binding id, user-tab `providerTabId`, and exact conversation URL are
also persisted. A `Tab.id` is a run-local control handle and must never be saved
or reused by a later waiting occurrence. Each occurrence reclaims the same user
tab from the persisted provider identity and leaves it as a browser handoff when
another check is required.

An explicitly provisioned Chat may use `pending_handoff` only when its newly
created tab is still controlled and no provider identity is exposed. After the
first formal send, that exact tab is handed off. The first authorized waiting
occurrence uniquely reclaims the fixed URL and uses
`promote-browser-tab-binding` under its active read lease to replace only the
placeholder with the real provider identity. It cannot switch conversations.
If the platform never exposes that identity, the controller returns
`provisioned_url_fallback_allowed=true`; the occurrence may inspect only the
single exact canonical URL in its current `tabs.list()` and may not persist the
numeric handle. Real Windows evidence also shows that an agent-created tab may
disappear from both tab listings after handoff. Only when the same waiting
authorization returns `provisioned_url_reopen_allowed=true` may that occurrence
open the already-bound canonical conversation URL once in the same browser
binding. It must verify the exact URL, authenticated ChatGPT page, and current
request identity before reading; it cannot send, create a Chat, change identity,
or persist the new numeric handle.

A later submission to the same fixed Chat may need exact-URL recovery when the
app restarts. This is not a general browser fallback. The caller supplies the
exact URL counts from both current tab listings. One visible match is claimed
without navigation; two zero counts authorize one canonical open; any ambiguous
count fails closed. Recovery requires `review_submit_pending`, a matching current
submission fingerprint, no request identity, the still-confirmed browser Chat,
and a short `browser_submission_reopen` lease bound to the current browser id.
The caller re-verifies the exact conversation, authenticated page, visible
Extreme label, and payload identity.
The fresh pre-send gate atomically persists the matching lease and authorization
revision; `confirm-review-submission` must consume both at the unchanged state
revision. The reopen authorization or its revision alone is not proof. A normal
user-selected tab or promoted provider identity never receives this authorization.

The fresh pre-send gate is not limited to reopen recovery. Every browser
submission, including one through a still-visible bound tab, must prove the
current `review_submit_pending` state, current action lease, exact browser and
fingerprint, confirmed Extreme reviewer identity, and a live `submission`
account slot bound to that reviewer. Confirmation must consume the stored
authorization revision plus the same browser and account-slot identities.

An already-visible request whose short-lived send authorization was lost may be
reconciled without a resend. This recovery still requires the exact fixed Chat,
a live submission slot, the matching browser-reopen lease, trusted request
identity, exactly one full-body match, and a raw payload SHA-256 equal to the
current submission fingerprint. The command never grants send authority and
returns `resend_allowed=false`; ambiguity or drift is non-mutating and fail-closed.
When the exact current packet has zero visible matches, the same controller gate
returns `browser_submission_not_previously_sent` without mutating state and
directs the caller to the existing one-shot first-send authorization. Missing
identity is expected in that zero-match case and is never itself evidence that a
request was sent.

If any already-bound fixed Chat later disappears from both current browser
listings, the same identity-gated occurrence may receive
`canonical_url_reopen_allowed=true`. It may open only the stored canonical URL
once and must reverify the exact conversation, login state, and current
payload/request identity. This is recovery of the existing conversation, not
permission to create a Chat or use a different tab while the exact URL still
exists in either listing.

## 4. One waiting gate

Unconditional recurring heartbeat execution remains retired. A state may have
one future reply waiting-check only while `review_receipt_pending` or
`review_waiting`. One waiting phase uses one stable platform heartbeat id; every
future occurrence receives a fresh controller token. There is no second
scheduler.

The separate `submission_retry` kind exists only while an automatic run is
`review_submit_pending` and the shared account circuit is `rate_limited`. It
uses the same one-shot identity fields but never claims a waiting-read lease or
reads Chat. At most one reply wait or submission recovery can be active for a
state.

The Codex Desktop heartbeat must use one UTC occurrence formatted exactly as
the controller's exact `platform_rdate` in `RDATE:YYYYMMDDTHHMMSSZ` form;
rounding to an hour or half-hour is forbidden. The platform-returned RDATE must
be supplied to `bind-waiting-check --scheduled-rdate`; a mismatch fails closed.
禁止使用 `FREQ=`、`INTERVAL=` or any recurring rule.
After a no-result occurrence, `rearm-waiting-check --lease-id <current read lease>`
atomically releases that read authority and rotates the controller token before
the same platform heartbeat is updated to a new single `RDATE`. The platform
must never be updated first.
Every `schedule_once`, `keep_once`, or `update_once` result also declares
`platform_wait_rule=single_rdate`, `platform_rrule_prefix=RDATE:`, and
`recurring_platform_rule_allowed=false`. The platform call must follow those
machine fields and must not choose a recurring rule.
After the first future platform task is created and its stable id is bound with
`bind-waiting-check`, the caller must run `render-waiting-check` and replace the
same task's prompt with the complete controller-rendered output. That exact
prompt contains the current state path, token, and automation id. A hand-written,
summarized, or partially copied occurrence prompt is invalid; failure to update
the same future task requires deleting it and failing closed before the submit
occurrence ends.
Because Codex Desktop may show that prompt to the user, its leading status and
no-action guidance are written in concise Chinese and English. Required commands
remain under an explicitly labeled internal one-time section; controller safety
fields must not be presented as ordinary user instructions.
`confirm-review-submission` exposes this as a host barrier, not prose advice:
`mandatory_next_tool=codex_app__automation_update`, mode `create`, an exact
single-RDATE `platform_wait_create` object, and a fixed
`mandatory_next_action_sequence`. The first create uses the controller's inert
bootstrap prompt. That prompt has no authority to inspect Chat, browser,
project files, or state if it somehow fires before replacement. The host maps
`target_thread_id` to the platform tool's `targetThreadId`, binds the returned
stable id and exact RDATE, renders the identity-complete prompt, and updates the
same platform task. `platform_wait_creation_before_turn_end=true` remains a
hard turn barrier until all four actions succeed.
The platform automation id must be one non-empty line of at most 64 characters.
Before an automatic browser send, `authorize-browser-submission-send` projects
the later complete prompt at that maximum id length. If it returns
`waiting_prompt_capacity_exceeded`, no send is authorized; the run must stop
before the click rather than submit a request that cannot receive a safe wait.
When `waiting-check` returns `waiting_check_busy`, it has not consumed or
authorized the occurrence. Do not read Chat or rotate its token; update the same
platform heartbeat from the returned `platform_wait_update`, with the same token
and automation id; its exact RDATE is derived from `retry_not_before`. Busy is
explicit proof that this occurrence did not read Chat,
so it must never be reported as “no reply yet”.

Each due occurrence must pass `waiting-check`, acquire a live shared account
browser slot with operation `waiting_read`, and only then call
`authorize-waiting-chat-read --account-slot-lease-id <lease>`. The second
authorization rechecks status, token, stable id, claim, waiting lease, and that
the account slot still belongs to the same implementation task with the exact
`waiting_read` operation immediately before browser access. Missing, expired,
wrong-task, or wrong-operation slots return `account_browser_slot_required` and
do not authorize browser initialization. Stale or duplicate occurrences do not
read the page or mutate the project.
For a real rate limit during replacement startup, the shared account gate's
exact `cooldown_until` remains authoritative across the rollover failure and
all status projections. The stable reason is `account_rate_limited`, never a
generic controller error. Cooldown permits no Chat/browser access or proactive
probe. The controller creates or reuses exactly one `submission_retry` RDATE
wait, reports whether it is bound, and allows one recovery check only at expiry.
Missing platform-wait capability is a technical blocker with an explicit host
next action and never a product decision.
Legacy `controller_error/external_blocked` states use the same rule. Guard may
atomically migrate, and show-status may read-only project, only when the live
account cooldown matches the exact task, state identity, reviewer generation,
repository identity, and there is no task slot. Migration restores the unsent
submission and one RDATE wait. An already-bound wait is reused. Any mismatch
leaves the state unchanged and grants zero browser authority.
The legacy candidate also includes `rollover_pending` with no persisted
rollover failure code when the review itself is `external_blocked` by a generic
controller error. A matching live cooldown atomically completes the blocked
rate-limit identity and cannot fall through to ordinary turn entry. The host
must bind the one returned RDATE before that turn may complete.
Non-waiting rollover completion receives the live startup account-slot lease
and registry. Before that slot is released, the controller promotes both the
slot and its unique provisioning authorization to the final reviewer Chat,
generation, state, and repository identity. Release may record a rate-limit
retirement only after this promotion. For an old `reviewer_thread_id=none`
release, rate-limit rollover may reconcile one retirement only from the same
startup lease recorded in durable mode-selection/binding receipts, one matching
prior-generation authorization, and zero Chat/slot conflict. Repeats are
idempotent; ambiguity grants no retirement or browser access.
If the real rate limit predates the ephemeral mode-selection lease, one legacy
rebuild is allowed only when a unique prior-generation startup authorization,
exact task/scope/state/repository identity, canonical provisioned browser and
provider binding, consistent authorization/replacement timestamps, no current-
generation message receipt, the same task's rate-limit release, and a globally
empty slot set all agree. The rebuild writes one deterministic identity and one
retirement. Any missing receipt or uncertain slot leaves the gate unchanged.
Slot acquisition normally never re-labels an existing lease: same-task reuse
requires the same operation. The only controller-owned exception is a one-time
replacement-Chat provisioning `startup` that atomically continues to that new
Chat's first `submission` after exact task, profile/scope, state revision,
reviewer binding, visible browser, and Extreme confirmation all match. It keeps
the same lease and visible tab, permits tail-only inspection, and forbids a
second browser initialization, navigation, refresh, or full-history scan.
`account_browser_operation_conflict` identifies the stale
lease for explicit release, but grants no browser access; a waiting occurrence
then rearms state before moving the same platform wait.
The first executable action of a due heartbeat must be the local `waiting-check`
CLI. Browser runtime setup, tab listing/claiming, or DOM access before its saved
`review_poll`/`receipt_reconcile` result, successful `waiting_read` account-slot
acquisition, and the second authorization is a failed cycle; any content observed
through that bypass must not be consumed or applied.

Immediately after `waiting-check` claims a due occurrence, its first host action
must move the same platform waiting task to the exact recovery RDATE returned by
the controller. The caller then runs `confirm-waiting-recovery-arm` with that
platform RDATE and the current waiting lease. Until that confirmation is persisted,
`authorize-waiting-chat-read` denies browser initialization. The recovery RDATE is
the current read-lease expiry: if the occurrence ends before a real read, the same
one-shot task can recover the expired claim. Normal no-reply rearm replaces that
reservation with the next token/RDATE, while a staged reply deletes it before
consumption. This is one stable platform task, never a second scheduler.

For `browser_read_authorized`, require `browser_surface_mode=visible_foreground`,
`background_browser_access_allowed=false`, and
`visible_browser_required_before_chat_action=true`; show the in-app browser pane,
make the exact fixed Chat the visible active tab, and only then inspect the same
tab without a reload. If the
page reports a network/load failure, release the account slot and call
`browser-network-observation --outcome network_error`. The controller preserves
the stable waiting id, sets `browser_reload_same_tab_required`, and authorizes a
single future check 180 seconds later. `rearm-waiting-check --lease-id` clears the
claimed read and rotates the token in state first; only its successful result
updates that existing platform wait. It cannot create a second wait.

On the next due occurrence, `browser_refresh_authorized` plus
`reload_same_tab_once=true` permits exactly one reload of the same tab. The
caller waits for page load, re-verifies the same conversation id, and inspects.
`browser-network-observation --outcome loaded` clears the consecutive-error and
reload-required state. A healthy page is never refreshed, a visibly streaming
reply is never refreshed, and UI actions are not blindly repeated.

If no exact receipt or complete reply exists, release the account slot and rearm
the same waiting gate with the exact read lease before updating its one future
occurrence. A reply, phase change, block,
completion, or user stop retires the gate. Queued stale occurrences expire.

## 5. Natural-language result

Completed ordinary prose is valid review input; `[LCRL_RESULT_V2]` is optional
compatibility syntax. The implementation task continues when the next action is
clear. It stops for the user only when the reply is ambiguous, contradicts local
evidence, changes product direction, or requests destructive, release, payment,
permission, or other high-impact action.

When prose explicitly labels a `下一步` or `唯一下一步` section, that section is
the current action scope. The full reply remains context, but a sentence that
explicitly defers remaining release/deployment work to a later handoff is not
current authorization and must not cause a safe local action to be misclassified.
A high-impact instruction inside the labelled current scope still requires the
user, and deferred high-impact text must never be executed automatically.
Deleting or invalidating synthetic SQLite/in-memory records as an explicitly
requested counterexample is a normal local test action when no production,
real-user, repository-file, release, deployment, permission, or credential
target is present. Destructive actions against those real targets still stop.
A database protection counterexample may also be identified by both conditions:
table/row/FK/cascade/association context, and an explicit assertion that the
delete must be rejected and data must remain unchanged. This never authorizes a
delete intended to succeed.

When the reviewed project scope is complete and the prose explicitly recommends
stopping that review/development loop, the explicit stop line is the current
action scope. Later text that assigns release, platform, or playtesting work to a
future phase remains context; it is not an instruction to perform those actions.

A stage PASS with a concrete next step advances to that step. In `continuous`
mode, a stage PASS without a reviewer-supplied next step advances to the next
safe unfinished stage already implied by the recorded overall goal, roadmap,
and acceptance criteria. It is not completion evidence.

Only a reviewed `result_received` boundary plus an explicit
`--overall-goal-complete` transition and non-empty `--completion-evidence` may
enter `completed` in `continuous` mode. Recovery override cannot bypass this
contract. The same response identity is consumed at most once.

Each reviewer verdict has a causal evidence cutoff at request submission. The
current response's staging, account-slot release, one-shot deletion, and state
resume are controller-owned post-response closure. They remain mandatory host
checks, but cannot be required as evidence for the verdict that precedes them.
Completed closure from an earlier round may be reviewed in a later request.

## 6. Retained invariants

- atomic state writes and revision checks;
- request/response identity separation and one submission fingerprint;
- bounded action leases;
- one stable task/Chat/tab binding;
- one trusted state-local review-run binding, rendered into every formal request
  and rechecked by the send authorization; older Chat history cannot rename,
  count, or bind the current run;
- attachment visibility verification;
- no resend after an uncertain outcome;
- page content cannot override role, channel, permission, quota, or direction;
- real browser/device evidence is distinct from mocks and local closure checks.

Detailed browser operations are normative in
[browser_transport.md](browser_transport.md). Binding rules remain in
[binding_registry.md](binding_registry.md).
