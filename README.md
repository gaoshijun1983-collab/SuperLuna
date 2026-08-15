# SuperLuna

[![CI](https://github.com/gaoshijun1983-collab/SuperLuna/actions/workflows/ci.yml/badge.svg)](https://github.com/gaoshijun1983-collab/SuperLuna/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/gaoshijun1983-collab/SuperLuna?include_prereleases)](https://github.com/gaoshijun1983-collab/SuperLuna/releases)

SuperLuna is a Codex plugin for a browser-first development review loop:

```text
Codex implements → one active bounded ChatGPT web conversation reviews → the same Codex task continues
```

The public product name is `SuperLuna`. Compatibility identifiers remain plugin
ID `luna-review-loop`, Skill/folder `luna-chatgpt-review-loop`, and command
`lcrl`. It is a plugin plus a bundled Skill and standard-library Python safety
controller, not a standalone desktop application.

The clean macOS C27 run has now completed three consecutive isolated real web
review rounds on Controller 98: each round used one submission, one gated read,
one staged identity, one deleted one-shot wait, and one reply consumption. The
same task continued without coordinator messages and finished with no active
wait. This is strong Alpha transport evidence, but it is not a real-project
cycle and therefore does not satisfy the Public Beta gate.

## Current source status

The current source candidate is `0.2.0-alpha.63`. It is an early
technical-testing Alpha, not a Public Beta. Controller 119 / Skill revision
`2026-08-14.76` bounds each active reviewer Chat to eight formal reviews. Before
a ninth review, or immediately after a real rate-limit notice, the old Chat is
retired permanently and exactly one replacement Chat receives compact current
context. Cooldown recovery never reopens, refreshes, health-probes, or scans the
retired long conversation. Controller 118's same-tab recovery is superseded
because real testing showed that reopening one long conversation could itself
trigger another history-access limit. Controller 117
distinguishes a never-sent recovered packet from a lost receipt:
zero exact visible matches continues to the ordinary first-send gate, one trusted
match reconciles without resending, and ambiguity stops safely. Controller 116
introduced the single cooldown-bound recovery after a real ChatGPT rate limit;
Controller 119 now routes it to one replacement Chat instead of the old visible
health-probe path. Early or duplicate occurrences cannot open the browser.
Controller 115 validates the human-visible review round against the controller
round before submission, pairs replies only from the complete assistant message
after the current request, and keeps the fixed Chat tab available for handoff.
Controller 114 requires every Chat action to surface the exact fixed reviewer
conversation in the visible Codex in-app browser; background-only browser access
is not allowed. Controller 113 kept expected test failures such as `scenario deletion ->
contract FAIL` from being mistaken for a real destructive instruction, while
real project/source/data deletion remains fail-closed. Controller 112 added
fail-closed reconciliation when a review request is already
visible in the one fixed Chat but its short-lived send authorization was lost
before receipt persistence. One exact full-body match with trusted identity may
be recorded without resending; ambiguous or changed evidence is rejected without
state mutation. It retains Controller 111's safe exact-URL browser rebind and
Controller 110's same-one-shot waiting-claim
recovery and the Windows-safe
repository retest workspace probe and the dedicated `superluna_repo_retest_v1` profile for
developing and genuinely retesting SuperLuna itself. Each implementation task
is confined to its deterministic repository-local
`.superluna/retest-runs/<task-hash>/project` fixture and sibling `state.json`;
the repository root, adjacent runs, symlink escapes, and external paths fail
closed before probes, state use, the account-browser gate, or browser startup.
The tracked `.codex/config.toml` gives newly started trusted-project tasks a host
`workspace-write` boundary, but is not claimed to dynamically alter an already
open task. Installed SuperLuna runs keep the `generic` profile and remain
compatible with a user's explicitly selected, host-authorized external project.
Controller 104 previously required an explicitly authorized new reviewer Chat
to be provisioned only after the task had completed and verified its first real,
minimal project change. A host approval or failed real write therefore stops
before Browser Skill access and leaves zero Chat side effects. The account-
browser gate rejects missing local-work status before issuing a slot or browser
permission; existing fixed-Chat recovery is unchanged.
Revision `.60` also accepts a platform browser
identity beginning with a hyphen without mistaking it for an option and documents
the unambiguous equals form. Controller 102 rejects a truncated browser
request UUID before state transition and requires rereading the already-sent
message without resending. Controller 101 additionally keeps an explicit
low-risk REVISE actionable when Chat asks for proof that no other path was
added, modified, or deleted under a “唯一最小后续动作” heading; an affirmative
project deletion remains gated. Controller 100 binds state initialization to
the host-provided `CODEX_THREAD_ID`, so a delegated task cannot accidentally
reuse its coordinator's `source_thread_id` as writer, account, run, or wait
identity. Controller 99 rejects the transient
`/c/WEB:<uuid>` route that Codex's in-app browser can expose immediately after
creating a Chat. The task must resolve the unique canonical conversation link
for the same initialization exchange before state creation; it cannot ask the
user to choose between two identities or create/send again. The same source also distinguishes Reviewer Chat
submission from Git commit/push. A verified worktree diff and tests are valid
review evidence unless the user or project contract explicitly requires a commit
identity; an external worktree index permission cannot become an invented review
prerequisite. Revision `.54` prevents a completed browser
provisioning step from being misreported as unresponsive merely because it took
about ten seconds. C28 reached a logged-in ChatGPT home page and successfully
filled the composer with an enabled send button, yet stopped before sending or
creating state. Completed tool status plus the expected postcondition now means
continue; one side-effect-free local locator expression may be corrected once,
while real timeouts and uncertain sends still fail closed. Revision `.53` removes an ambiguous waiting
instruction that abbreviated the final command as `resume`. It now names the
exact `resume-from-reply` subcommand and its required deletion-proof arguments,
preventing a successfully staged reply from being stranded after its platform
wait is deleted. Controller 97 completes the scheduled-reply
handoff: after a one-shot wait reads and consumes a valid reply, its protected
`review_poll` lease is atomically relabelled as the same task's `apply_result`
lease. The mandatory next turn-entry therefore continues implementation instead
of incorrectly stopping for a user decision. Controller 96 preserves an already-authorized
single browser send across repeated same-task turn-entry guards until its real
receipt is confirmed. Ordinary orphaned leases still rotate, and another task
still cannot take them over. Controller 95 also recognizes an explicit
“do not approve release/delete/resume from this evidence” clause as a boundary,
not an action. Controller 94 keeps a safe, explicit reviewer
`REVISE` actionable when its acceptance criteria use negative manifest evidence
such as “no added or removed files”; those absence assertions no longer look like
a destructive instruction. Real delete, publish, deploy, permission, payment, and
credential actions remain gated. Controller 93 also makes the read-only observer report
the active one-shot waiting task rather than the retired legacy scheduler id, while
preserving both explicit fields for diagnosis. Controller 92 gave every new state a unique,
controller-owned review-run identity. Every formal request must begin with the
exact rendered binding and prove the same run id at the pre-send gate, so old
messages in a reused reviewer Chat remain background and cannot rename, count,
or bind the current run. This addresses C21's reviewer-side identity conflict
with an older Controller 89 conversation. Controller 91 prevents an account-browser slot
from crossing operation boundaries. C21 proved that the single-RDATE platform
wait can be created, bound, and fired without coordinator prompting, then found
that a still-live `submission` slot could be returned as reusable for
`waiting_read`. The second authorization rejected it before browser startup.
Different operations now fail closed with the exact stale lease identified for
release and safe wait rearm; reuse remains available only for the operation that
actually acquired the slot. Controller 90 turns the post-submission platform
wait into a machine-readable host barrier: it names the Codex Desktop
automation tool, exact single RDATE, target task, inert bootstrap prompt, and
mandatory create/bind/render/update sequence. If a host turn still ends before
binding, only the exact implementation task may recover that platform step;
project and browser authority remain denied, and an expired never-bound RDATE
is atomically moved to a fresh future occurrence. Once bound, ordinary wakeups are
blocked exactly as before. Controller 89 extends a waiting-read lease to
five minutes, atomically rearms state before the host updates its one platform
RDATE, and makes the reviewer evidence cutoff explicit: the current response's
staging, slot release, wait deletion, and resume remain mandatory controller
closure, but cannot be evidence required for the verdict that precedes them.
The CI workflow now cancels obsolete runs on the same branch to reduce redundant
failure mail. Controller 88 makes the controller generate the
exact one-shot RDATE and requires the platform-returned schedule to match during
binding, preventing an intended 180-second check from being rounded to the next
hour or half-hour. Controller 87 lets a newly created task obtain
its own trusted identity directly from the host-injected `CODEX_THREAD_ID`, so
the first-message-only autonomous launch no longer depends on a coordinator
follow-up. Missing host identity still fails closed. Controller 86 adds a durable pre-delete
receipt gate for scheduled browser replies: the complete body, real response
turn/message identity, current request cycle, and file hash must be staged while
the waiting-read authorization is still live. Only then may the task release the
account slot, delete the one-shot wait, and resume. Missing identity now keeps the
same wait recoverable instead of deleting it and stranding the run. Formal round
counting is state-local, so older messages in a reused fixed Chat and page prose
cannot advance or stop the current run. Entering `external_blocked` also retires
an ordinary foreground `review_poll` lease while preserving browser-reopen ownership.
Controller 85 allows a clear low-risk FAIL
next step from a scheduled Chat reply to continue even when its safety boundary
explicitly says not to touch production, deployment, or permissions. It still
blocks mixed or positive high-impact instructions. Controller 84 retires an ordinary foreground
lease when that implementation turn durably enters `external_blocked`. Leaving
the waiting state already retires its waiting-read lease; browser-reopen leases
remain protected against preemption.
It also clarifies that the 180-second account quiet interval applies to every
new browser acquisition after a normal release, including the same task's next
operation. Controller 83 refuses to consume a scheduled
browser reply while the owning task still holds a live `waiting_read` account
slot, and the rendered one-shot prompt now releases that slot before deleting
the wait and resuming. Revision `.38` also makes the Browser plugin-root boundary
explicit so an implementation task cannot incorrectly append
`skills/control-in-app-browser/scripts/` when locating `browser-client.mjs`.
The macOS C12 probe confirmed one fixed visible Extreme Chat and then encountered
a real ChatGPT history rate limit before its first formal send; it failed closed
with zero sends, zero waits, zero reads, and `active_count=0`, so it earns no
three-round or recovery credit. Controller 82 gives an explicitly authorized
new reviewer Chat a controller-recorded, once-only startup home-navigation grant;
an empty task browser no longer has to misuse the health-probe path, and the same
authorization cannot be reused after its startup slot is released. Controller 81 closes a Windows 3.13
concurrent-start race while initializing the first byte of a shared lock file
and gives only the account-browser registry a bounded ten-second lock queue;
persistent permission failures and ordinary state locks remain strict.
The macOS C11 probe completed exactly three autonomous browser-review rounds in
one fixed Extreme Chat, with three single-RDATE wakeups, three uniquely paired
responses, a final PASS, and zero remaining waits or account slots. C11 exposed
one late round-two read-slot release, so it validates the broader loop but does
not count as a clean Controller 83 release-order run.
Controller 80 keeps the exact one-shot wait
prompt within its 1200-byte safety budget for the C9 macOS path and projects
that prompt before any browser send; an unsupported longer path now fails
before the click instead of after a request has already been submitted.
Waiting automation identities are bounded to 64 single-line characters so the
post-send prompt cannot outgrow that projection. Controller 79 requires every browser submission—including
a still-visible bound tab—to consume a fresh controller authorization proving
the exact state, action lease, browser, fingerprint, Extreme reviewer, and live
reviewer-bound account slot before the visible send. Controller 78 serializes each fixed reviewer
Chat across implementation tasks so an accidentally duplicated platform task
cannot initialize the browser or send while the intended task owns that Chat.
Controller 77 requires every wait occurrence
to obtain a current tab handle instead of reusing a prior-occurrence object or
numeric id, and forbids asking Chat to PASS evidence that will only exist after
submission. Controller 76 recognizes a standalone
`唯一下一步` / `next step` heading as the boundary of an actionable natural-
language review. Hypothetical permission or release words before that heading
no longer block a safe local action, while real high-impact instructions inside
the bounded action still fail closed. Controller 75 makes a live account-browser
slot for the exact task and `waiting_read` operation a controller-enforced
input to every browser wait authorization; a prompt that omits the slot can no
longer initialize or read Chat. Controller 74 gives the serialized binding
registry a dedicated bounded queue budget so six simultaneous Windows tasks do
not fail while merely waiting to open the shared lock sidecar. It retains
Controller 73's rule that the current task first verifies its
assigned workspace with a create/read/remove probe, then requires the shared account slot
before even reading the browser Skill or initializing its runtime. It keeps active startup/submission
turns alive through the 180-second quiet handoff instead of ending without a
wake source; it never creates an execution-state timer. Controller 63 preserves the two-task limit and
adds a 180-second account-level quiet handoff between different tasks' browser
actions. After a proven healthy probe, the same task may immediately acquire
exactly one `startup` or `waiting_read` slot; either path consumes the bypass.
It also retains Controller 61's requirement that a post-cooldown health
probe prove an existing conversation or conversation history is actually readable
before clearing the account circuit; a healthy-looking homepage, login state or
empty composer is no longer sufficient. Controller 60 / Skill revision `2026-08-12.14` adds a machine-wide ChatGPT
account gate after a real three-task macOS test triggered a conversation-history
security rate limit. Local development remains parallel, but only two tasks may
touch web Chat at once; a third queues before browser initialization. Any real
rate-limit notice clears all local slots and opens a 30/60-minute shared circuit,
followed historically by one read-only health probe; Controller 119 replaces
that post-limit probe with one new bounded reviewer Chat. The gate is local-machine evidence and
cannot coordinate another computer using the same account. Controller 59 / Skill revision `2026-08-12.13`: browser startup now claims a
unique user-open exact-URL Chat before considering a controlled or new tab, and
uses stable message nodes plus actual composer state instead of localized
snapshot phrases. Controller 58 / Skill revision `2026-08-12.12`: an explicitly terminated,
wait-free state can now be atomically handed from its historical implementation
task to one exact replacement task for a user-authorized retest. The same state
file is reused and the old cycle is archived; live waiting work cannot use this
path. Controller 57 / Skill revision `2026-08-12.11`: a bound one-shot wait has a
controller-rendered occurrence prompt containing its exact state, token, and
automation identity, so a hand-written prompt cannot silently omit the fields
required to resume. Delegated startup also rejects a child task that reuses its
coordinator's `source_thread_id` as its own implementation identity. Controller
56 / Skill revision `2026-08-12.10` adds a bounded retry
for transient Windows sharing violations during atomic durable-file replacement;
permanent permission failures still fail closed. Controller 55 adds a fail-closed,
read-only multi-run overview. Controller 54 makes the guard fail
closed for missing or cross-task implementation identities before granting a
work lease, while preserving same-task serial recovery only for ordinary
`turn_entry` and `apply_result` leases. Controller 53 / Skill revision `2026-08-12.7` extends the exact
20-minute stall boundary to both active work states and makes the stable task
identity explicit for guard recovery after context compaction. Controller 52 adds a byte-for-byte
read-only multi-run observer with the user's exact 20-minute stall boundary,
plus fail-closed startup diagnostics for browser, Chat identity, visible
Extreme mode, read/send, and one-shot waiting capability. Controller 51 / Skill
revision `2026-08-12.5` adds an explicit,
lease-bound way for the same visible implementation task to begin a genuinely
new user-authorized goal after its previous goal completed; ordinary wakeups
still cannot reopen completed work, and the bound Chat must be visibly
reconfirmed. It also corrects the published Pro-progress ceiling to the
controller's actual 256-event bound. This source publishes the bounded Pro-progress event shape and a
machine-checked milestone/rollback guide without claiming that every nested
state invariant is expressed in JSON Schema. Controller 50 / Skill revision
`2026-08-12.4` makes the fresh
pre-send gate a persisted, single-use controller fact: the reopen revision by
itself can no longer be passed directly to submission confirmation as forged
proof. Clearing the reopen lease clears that authorization. This is locally
regression-tested and does not add real-device credit. Controller 49 fixes the observed
submission-reopen navigation-timeout stall: an uncertain first navigation is
reconciled only on the same opened tab, and the reopen lease no longer grants
send permission. A fresh pre-send controller gate now requires the same active
lease, fingerprint, browser, conversation, clean request identity, and at least
60 seconds for confirmation. Controller 48 removes a local-summary
overclaim: `closure-check` now reports that it executes only the 15 built-in
controller selftests, explicitly marks the repository suite as not run, and no
longer labels repository-only scenarios as verified by that command. Repository
tests, real-device evidence, and Public Beta gates remain separate. The same
Alpha 40 candidate also aligns the published `review_submit_pending` contract
with runtime validation: a response cannot be complete or actionable before
the review request is submitted. Controller
47 / Skill revision `2026-08-12.1` closes a published-
schema false green: a waiting check may now be active only when the runtime is
in `review_receipt_pending` or `review_waiting` under `waiting_only` mode, and
all waiting identities must be cleared outside that boundary. Cross-field
identity equality that JSON Schema cannot express remains controller-enforced,
and the full nested schema audit remains open. Controller 46 makes the legacy
`--replace` flag unable to preempt any active lease. Same-task serial recovery
remains limited to ordinary orphaned `turn_entry` or `apply_result` leases;
cross-task, waiting-read, and browser-reopen leases fail closed regardless of
the flag. Controller 45 keeps a submitted turn
active until its unique one-shot waiting job is bound and lets a later serial
turn from the same implementation task replace an orphaned ordinary entry or
result-application lease. Controller 44 additionally releases
an ordinary turn-entry lease atomically when its review submission is
confirmed, so the first legal waiting check no longer stalls until the lease
timeout. Controller 43 added a mandatory
turn-entry guard after a real macOS external message woke a task whose saved
state was still waiting for Chat and the task began modifying its project.
Ordinary resumed turns now receive `waiting_turn_blocked`, no action lease, and
no project/browser authority while waiting; even `--replace` cannot bypass the
gate. The platform waiting occurrence remains the sole legal reader. This is a
deterministic local mitigation, not a host-level interceptor, and still needs a
clean real retest. The preceding unpackaged controller-42/Skill-revision-
2026-08-11.7 update
fixes blockers found while existing UNSEEN tasks dogfooded SuperLuna. A
bounded local SQLite/synthetic counterexample that deletes or invalidates test
records no longer trips the destructive-action gate, while production, user
data, repository-file, release, deployment, permission, and credential targets
still stop. Any already-bound fixed web Chat may now recover an absent tab by
opening only its stored canonical URL once under the current submission/waiting
authorization, after both current tab listings contain no exact URL; this never
creates a replacement Chat or permits a duplicate send. Platform waiting now
requires a single UTC `RDATE` and explicitly rejects recurring `FREQ` rules;
the same waiting identity is updated only after controller rearm. If a due
check collides with an active work lease, controller 38 keeps its token and
requires the same one-shot identity to move once beyond the lease expiry instead
of silently stranding the wait. Controller 39 additionally publishes the
single-`RDATE`/no-recurrence rule as machine-readable fields on every scheduling
result after a real Memory task ignored the prose contract and recreated `FREQ`.
Controller 40 also recognizes a database-protection counterexample when it
explicitly requires a table/row/FK delete to be rejected and all data to remain
unchanged, even if the reviewer does not repeat the word SQLite.
Controller 41 makes every browser submission boundary publish a mandatory
missing-tab action (`authorize-browser-submission-reopen`), generalizes that
path to every already-bound fixed Chat, and clears a finished `apply_result`
lease when work crosses to local/submission/completed state. A waiting heartbeat
is now explicitly invalid if browser access occurs before both controller gates;
the host still cannot technically prevent a model from bypassing the Skill.
Controller 42 also makes every active continuous boundary publish a mandatory
same-turn continuation action. A task may no longer stop after applying a reply
or preparing the next submission merely by saying that the loop is still in
progress. Its clean Windows retest passed the first autonomous cycle but stopped
after applying the second reply despite `turn_completion_allowed=false`; no
third cycle could start. The host currently has no plugin-level turn-finalization
interceptor, so this remains a real blocker rather than a locally solved claim.
The preceding
controller-36/Skill-revision-2026-08-10.23 update
separates a bounded stage PASS from completion of the user's overall goal. New
workflows default to `continuous` goal mode; completion is accepted only from a
reviewed result boundary with explicit overall acceptance evidence, and recovery
override cannot bypass that proof. The published state schema now expresses the
same completion contract. Controller 35 / revision `2026-08-10.22` also makes
automatic mode truly choice-free during active work: submission-pending is no
longer reported as a user decision, normal fixed-Chat review sends do not ask for
repeated confirmation, and active stages cannot end with task-result A/B/C
choices. Only a new identity, permission, capability, evidence, high-impact, or
product-direction blocker may ask one concrete question. Controller 34 / revision
`2026-08-10.21` made successful startup rebind explicitly require same-turn local
continuation; a task may no longer treat binding recovery as a completed deliverable. Controller
33 / revision `2026-08-10.20` added
an explicit fixed `terra_medium` implementation role while keeping
`luna_medium` as the default. The selected role must remain identical across the
runtime policy and executor ledger; SuperLuna never switches it automatically.
The preceding new-task browser bootstrap remains in place. A new implementation task first activates its own
in-app browser. When the sole reviewer Chat was provisioned by a coordinator,
the controller authorizes one exact canonical-URL open before local work and
commits the verified task-local browser binding without creating another Chat.
If an explicitly supplied existing Chat exposes no provider tab identity, the
verified exact URL is bound as `canonical_url_only`; no numeric tab handle is
persisted, and every later open remains occurrence-authorized and exact-URL.
New
runs bind exactly one user-selected or explicitly provisioned `https://chatgpt.com/c/<conversation-id>` in
Codex's in-app browser. The implementation task is the sole project writer and
uses that same tab for one submission, waiting, reply retrieval, and continuation.

The durable state stores the browser binding, provider-owned tab identity, and
exact conversation URL. Each wait occurrence reclaims that user tab and never
reuses a run-local numeric tab handle from an earlier occurrence.

`app_chat_review` remains a saved-state compatibility transport only. New runs
use `in_app_browser`; SuperLuna does not switch back to App Chat or change the
user's model/reasoning mode. It creates exactly one new Chat only when the
current request explicitly authorizes that action. If the new controlled tab
never exposes stable provider identity, an authorized wait uses only the current
occurrence's unique exact-URL tab without persisting its numeric handle. If the
provisioned tab disappears from both browser listings after handoff, the wait may
open the already-bound canonical URL once in the same browser binding, verify the
exact conversation and request identity, and read without sending or creating a
Chat.

A Windows stress run completed ten real request/reply interactions. Nine were
valid for controller application; one same-occurrence foreground read was
correctly quarantined, leaving a four-cycle valid tail under revision `.4`.
Revision `.5` then proved the required submit-occurrence handoff, but its first
independent wait found that the provisioned tab had disappeared from both tab
listings. Controller 25 / revision `.6` then reopened the fixed URL and retrieved
the unique paired PASS, but a deferred mention of release validation outside its
explicit local next step triggered a false high-impact block. Controller 26 /
revision `.7` scopes that gate to the labelled current action while preserving the
full review as context. Its first clean real cycle then retrieved and uniquely
paired a PASS that explicitly recommended stopping the completed monster-AI loop,
but the fallback whole-prose scan still treated deferred release testing as a
current action. Controller 27 / revision `.8` narrows that case to the explicit
stop line. Because the clean cycle required manual recovery, the formal consecutive
gate remains 0/10. This is defect evidence, not a completed Beta gate.

The published state schema now declares and requires every controller runtime
top-level section, including durable browser binding and next-operation state.
This closes the proven top-level false-green path; it does not claim that every
nested runtime invariant is fully represented by JSON Schema.

A real `.8` visual retest then found that the provisioned fixed Chat tab had
disappeared before a later submission. The task correctly stopped before sending,
but the controller exposed no submission-side counterpart to its waiting-only URL
recovery. Controller 28 / revision `.9` added a two-minute, fingerprint-bound lease
for one canonical-URL reopen before a later submission, only for the same durable
`provisioned_chat` / `pending_handoff` binding. Ordinary user tabs and promoted
provider identities remain ineligible. That real retest exposed that the app may
issue a new browser id after restarting. Controller 29 / revision `.10` now binds
the reopen lease to that one current browser id and commits the rebind only when
the verified submission is confirmed. The next real attempt proved that the
original two-minute lease can expire during required visual verification, after
one successful send but before controller confirmation. Controller 30 / revision
`.11` uses a ten-minute lease and requires page checks before authorization, then
immediate one-send confirmation. That path succeeded on Windows; the same submit
occurrence then briefly previewed a full viewport containing the fast reply while
preparing visual evidence. Revision `.12` forbids all post-submit full-page or
viewport captures and permits only a direct user-message crop, otherwise no
post-submit screenshot. The follow-up Windows visual-isolation diagnostic passed
in the same fixed
Chat: the request was sent once, the restarted browser id was committed only by
confirmation, and no post-submit full-page, viewport, preview, assistant DOM, or
assistant identity read occurred. Because direct locator capture was unsupported,
the optional post-submit screenshot was safely omitted. This manually awakened
diagnostic does not count toward the frozen-candidate 10-cycle release gate.
The next Windows diagnostic began with no fixed-URL tab in either listing. Under
the controller's 600-second lease it opened the bound canonical URL once, sent
one new request, and confirmed it without a duplicate. A separate waiting
occurrence then uniquely paired and consumed the complete PASS response; a
second consume returned `already_consumed`. This proves the current candidate's
fixed-Chat transport function end to end, but the waiting occurrence was
manually awakened and no platform automation was created, so the autonomous
release gate remains 0/10.

Revision `.13` also synchronizes the published policy schema with the controller:
the sole-writer role, ChatGPT reviewer identity, read-only reviewer, disabled
Codex review, Extreme requirement, and transport lock are now required constants.
The schema also ties browser review to `in_app_browser` control and compatibility
App Chat review to `manual_app_chat`, instead of accepting states the runtime
would reject. Other nested state-machine invariants remain under audit.

Revision `.14` synchronizes the published confirmation evidence required by the
runtime. A confirmed review must now publish an Extreme mode, trusted control
source, visible `极高` label, and all durable confirmation fields. Confirmed
browser review is tied to `in_app_browser`; confirmed compatibility App Chat
review cannot claim that browser source. Active workflow states also require a
valid lease and a nonempty, non-`none` reviewer thread. Cross-field identity
equality that JSON Schema cannot express remains enforced by the controller and
explicitly open.

Revision `.15` synchronizes the published capability contract with runtime
validation. Attachment and filesystem modes now use the controller's exact
enums, the Terra capability probe is required, and `mcp_readonly` is paired
bidirectionally with `mcp_verified`. Chat capability fields are typed but remain
optional because the controller does not currently reject their absence.

Revision `.16` synchronizes the model-policy safety core. The published schema
now requires policy version 5, keeps automatic model switching and automatic
task/thread creation false, fixes the implementation role to Luna Medium, and
limits the reviewer ledger to Sol Extreme or explicitly recorded Chat Pro. The
nested quota ledger and workflow phase relationships remain under audit.

## Waiting and page recovery

Unbounded recurring heartbeats remain retired. Only receipt/reply waiting may
have one future identity-gated check. A healthy page is inspected without a
reload. A browser network/load failure schedules one check 180 seconds later;
that authorized check may reload the same tab exactly once and then reverify the
same conversation id.

A ChatGPT “requests are too frequent” notice is handled separately: no reload,
history read, or send is attempted. The current reviewer Chat is retired
permanently and the account gate backs off for 30, then 60 minutes. After the
cooldown, one replacement Chat may be provisioned; the retired Chat is never
health-probed or reopened. Leaving the waiting phase stops every browser check.

## Quick start

1. Install the bundled Skill with the repository installer for your platform.
2. Invoke the Skill; it activates the implementation task's own in-app browser
   and opens ChatGPT when needed. Select an existing conversation only when no
   exact provisioned conversation is already recorded.
   When the same request explicitly asks SuperLuna to start with a new reviewer
   conversation, it may instead create exactly one browser Chat and seed one
   setup message; this exchange is excluded from formal review-cycle counts.
3. Start a new Codex task and invoke `$luna-chatgpt-review-loop`.
4. Confirm the selected conversation and the reasoning label you can actually
   see. SuperLuna records that confirmation but never changes the setting.
5. Let the implementation task perform the loop. A user decision is requested
   only for ambiguity, changed identity, missing capability, high-impact action,
   or conflicting evidence.

## Guarantees and limits

- One implementation task and one active reviewer Chat at a time. A reviewer
  volume is limited to eight formal reviews.
- A normal browser error never creates a replacement Chat. Reaching the round
  budget, or a real rate limit, authorizes exactly one bounded rollover; the old
  Chat is archived and cannot be accessed again by that workflow.
- Request and response identities are separate; an uncertain send is reconciled
  in place and never blindly resent.
- Page content cannot change the writer, channel, permissions, quota, or product
  direction.
- Natural-language review replies are valid; machine envelopes are optional
  compatibility syntax.
- Local tests, mocks, and `closure-check` prove local contracts only.
- Public Beta remains blocked on the real-cycle target and real Windows/macOS
  browser compatibility evidence in `release/alpha_release_report.json`.

## Validation

```powershell
python -X utf8 -B -m unittest discover -s tests -v
python -X utf8 -B skills\luna-chatgpt-review-loop\scripts\lcrl.py selftest
python -X utf8 -B skills\luna-chatgpt-review-loop\scripts\lcrl.py closure-check
```

Also run the current Codex `skill-creator` quick validator on the bundled Skill
and the `plugin-creator` validator on this project root before packaging.

Build and independently verify the deterministic tracked-source archive:

```powershell
python -X utf8 -B scripts\build_release.py build
python -X utf8 -B scripts\build_release.py verify
```

The archive contains only Git-tracked source plus an embedded
`RELEASE-MANIFEST.sha256`; ignored runtime state, caches, and older archives are
not eligible for inclusion. Rebuilding unchanged source produces identical
archive bytes and a standalone `.sha256.txt` file.

See [the roadmap](docs/ROADMAP.md), [the browser transport contract](skills/luna-chatgpt-review-loop/references/browser_transport.md), [the current release evidence](release/alpha_release_report.json), and [the 2026-08-11 company-PC handoff](docs/HANDOFF_COMPANY_PC_2026-08-11.zh-CN.md).

License: MIT.
