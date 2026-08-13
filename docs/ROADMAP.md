# SuperLuna product roadmap

SuperLuna remains a Codex plugin, not a standalone application. The Skill is the
interaction entrypoint; the standard-library controller is the deterministic
safety core; the in-app browser is the formal ChatGPT transport for new runs.

## 0.2: reliable browser-first loop

- Keep SuperLuna's own development and real-loop retests inside one deterministic
  repository fixture per implementation task using `superluna_repo_retest_v1`:
  `.superluna/retest-runs/<task-hash>/project` plus sibling `state.json`.
  Reject repository-root, ordinary source-child, adjacent-run, symlink-escape,
  and external paths before probes, state use, the account gate, or browser
  startup. Keep installed `generic` runs compatible with user-selected,
  host-authorized external projects.
- Use the tracked project `.codex/config.toml` as the host sandbox boundary for
  newly started trusted-project development tasks; never claim that it
  dynamically changes an already-open task's permissions.

- Prove the task's already assigned workspace writable with a disposable
  create/read/remove probe before browser initialization or Chat provisioning;
  projectless runs must use their assigned output directory rather than a
  hardcoded external path.
- Prove `Codex work → one bound ChatGPT web Chat → same Codex task continues`.
- Keep one implementation writer, one conversation id, and one claimed browser
  tab for the whole run.
- Persist the browser/provider tab identity and reclaim that same user tab on
  every wait occurrence; never treat a run-local tab handle as durable state.
- Let an explicit per-run request provision exactly one new reviewer Chat and
  one setup exchange before binding; never turn recovery into automatic Chat
  proliferation or automatic model switching.
- Bootstrap that new Chat with a controller-rendered packet containing the real
  contents and hashes of all goal-relevant core text files selected by the task.
  Do not impose a fixed file-count limit; enforce project-root, symlink, secret,
  per-file 32 KiB, and aggregate 64 KiB boundaries instead. Local paths alone
  are never reviewer context.
- Start every implementation task by activating its own in-app browser. When a
  coordinator provisioned the sole Chat, authorize one send-forbidden exact-URL
  startup open and revision-bound task-local rebind before project work; never
  assume the coordinator's tab object is inherited by the implementation task.
- When a user explicitly supplies one existing canonical Chat URL and the
  platform exposes no provider identity after successful page verification,
  persist only a URL-only marker and require exact-URL occurrence authorization;
  never persist the run-local numeric tab handle.
- Promote a newly provisioned tab's temporary `pending_handoff` identity exactly
  once at the first authorized wait, without changing its browser or conversation.
- Where the platform never exposes provider identity for an agent-created tab,
  use the authorized occurrence's unique exact canonical URL without persisting
  its run-local handle. If handoff removes that ephemeral tab from both browser
  listings, reopen only the already-bound canonical URL once under the same
  waiting authorization and browser binding, then verify the exact request before
  reading.
- If that same provisioned `pending_handoff` tab is missing before a later
  submission, require a ten-minute current-fingerprint lease for one canonical-URL
  reopen. Bind that lease to the current browser id so an app restart can rebind
  exactly once, and commit the new id only with submission confirmation; never
  extend this path to ordinary user tabs or promoted provider identities.
  Complete visual page checks before requesting the lease, then send and confirm
  immediately; a visible but unconfirmed request is never resent.
  Treat a first canonical-URL navigation timeout as uncertain: reconcile only
  the same opened tab without another open/navigation/reload, then require a
  fresh controller pre-send gate with the same lease, fingerprint, browser, and
  at least sixty seconds remaining for confirmation.
- After submission, never preview or capture the full viewport. Capture only the
  new user-message region directly, or omit the screenshot and use its confirmed
  request identity, so a fast reply cannot leak into the submitting occurrence.
- Keep unbounded recurring execution retired. During receipt/reply waiting only,
  permit one identity-gated future check and reuse its stable platform identity.
- Inspect healthy pages without refresh. After a network/load failure, permit one
  same-tab reload at the next 180-second authorized check.
- Treat ChatGPT rate limiting separately: no reload/read/send and deterministic
  machine-wide 30/60-minute circuit breaking. All local runs share at most two
  short-lived web-Chat access slots; the third queues before browser startup,
  and only one read-only health probe may close an expired circuit. Cross-device
  access remains outside the local controller's proof boundary.
- Preserve receipt reconciliation and duplicate-send protection without making
  hashes or internal state routine user concepts.
- Preserve full natural-language review context while treating an explicitly
  labelled current next-step section as the only automatic action scope; deferred
  release/deployment notes never authorize those operations, while high-impact
  instructions inside the current scope still require the user.
- Treat an explicit recommendation to stop a completed in-scope review loop as a
  bounded stop action; later release/platform work remains deferred context, not
  current authorization.
- Keep every runtime-required top-level state section declared and required by
  the published schema; continue auditing nested invariants without treating
  top-level parity as full contract equivalence.
- Keep waiting-check activity, token presence, and stale-identity cleanup tied
  to the exact runtime waiting-only status boundary in the published schema;
  leave claim/automation id equality explicitly controller-enforced.
- Keep `review_submit_pending` response-completion and apply-validity flags false
  in both runtime validation and the published schema until a review request has
  actually been submitted.
- Keep the runtime policy locks in the published schema as required constants,
  including the review-transport/control-source relationship.
- Require the runtime's durable confirmation evidence and confirmed-mode trust
  constraints in the published schema. Keep reviewer/observed-thread equality
  and other non-expressible cross-field checks explicitly controller-enforced.
- Keep attachment/filesystem capability enums, the Terra capability probe, and
  the `mcp_readonly`/`mcp_verified` pairing aligned with runtime validation;
  leave unenforced Chat capability presence optional in the published schema.
- Keep model-policy version, automatic-action locks, executor, and reviewer
  identities aligned with runtime validation; continue the nested quota-ledger
  and state-phase relationship audit without claiming full equivalence.
- Forward-test ten consecutive real cycles without outside wakeups, duplicate
  sends, cross-Chat reads, or replacement tasks.
- Preserve the current real Windows functional-loop evidence separately from
  release credit: controller-authorized auto-open, one send, independent paired
  read, and one-time consumption are observed, but the waiting occurrence was
  manually awakened and does not satisfy the no-outside-wakeup criterion.
- Complete real Windows and macOS browser compatibility evidence before public
  Beta. Local mocks and `closure-check` never satisfy that gate.

The Alpha core remains feature-frozen after this transport correction. Progress
toward Beta means real-cycle and platform evidence, not more orchestration.

## 0.3: validated usability and recovery

- Refine plain-language status and user recovery for expired login, changed Chat,
  unavailable browser capability, and platform UI changes.
- Validate cooldown behavior on real rate-limit and network-recovery events.
- Add a versioned milestone guide and rollback-section validation. The contract
  lives in `docs/milestones.json`, with a readable companion at
  `docs/MILESTONE_GUIDE.md`; validate it with
  `python -B scripts/validate_milestones.py`.

## 0.4: conversation health

- Score repeated context loss, stale instructions, evidence volume, and review
  quality without reading unrelated conversations.
- Recommend a new Chat only above a documented threshold, generate a complete
  handoff, and require explicit user confirmation before rebinding.
- Distinguish long model reasoning, streaming output, network failure, and a
  platform rate-limit notice without aggressive polling.

## 1.0 criteria

- Public installation and upgrade path with state migration.
- Cross-platform automated validation plus real end-to-end evidence.
- Explicit license, security contact, compatibility matrix, and reproducible
  release package.
- No silent model substitution, duplicate submission, writable reviewer, hidden
  quota escalation, or automatic infinite Chat creation.
- English primary documentation with maintained Chinese user guidance.
