# Architecture

## Alpha scope

SuperLuna is one Codex implementation task, one user-selected ChatGPT web
conversation, one claimed in-app-browser tab, one review response consumed once,
and at most one future identity-gated check while waiting. It is not a standalone
desktop application.

Compatibility identifiers remain plugin `luna-review-loop`, Skill/folder
`luna-chatgpt-review-loop`, command `lcrl`, and state schema 7. The legacy App
adapters remain available to read old state but are not the formal transport for
new runs.

## Layers

1. The plugin shell provides installation, discovery, and metadata.
2. The Skill defines user interaction, browser behavior, role separation, and
   safe recovery.
3. The standard-library controller owns state, transitions, identities, leases,
   receipt/reply deduplication, and wait authorization.
4. The in-app browser adapter claims one existing ChatGPT tab, verifies its URL,
   submits once through the visible composer, and reads the paired reply.
5. Optional evidence bridges are read-only and never become the control plane.

## Control flow

```text
user selects and confirms exact web Chat
  → browser capability preflight
  → browser-first state initialization
  → local work
  → verify same readable tab
  → capture visible-message baseline and submit once
  → enter receipt/reply waiting with one future check
  → authorize one same-tab inspection
  → consume one complete paired response
  → continue in the same implementation task
```

There is no coordinator in the normal path, no automatic Chat creation, and no
automatic model/reasoning change.

## Waiting and recovery boundary

Unconditional recurring execution remains retired. Only
`review_receipt_pending` and `review_waiting` may bind one stable future-check
identity. Each occurrence has a fresh token and reauthorizes page access just
before it occurs. Stale or duplicate occurrences read nothing and write nothing.

A healthy page is inspected without reload. A network/load failure sets a
same-tab reload requirement and schedules the next occurrence 180 seconds later;
that occurrence may reload once, verify the same conversation id, and inspect.

A ChatGPT rate-limit notice is distinct. It requests no reload, history read, or
send and schedules a non-reloading probe after 15, then 30, then 60 minutes.
Successful page access resets the backoff. Leaving the waiting phase invalidates
the gate and queued occurrences.

## Identity and failure model

Conversation id and claimed tab are binding facts; titles and focus are hints.
Before send, the caller captures visible user-message identity and exact packet
identity. An uncertain result is reconciled only from one new exact-body message
after that baseline in the same Chat. It never authorizes a resend or transport
switch.

Request and response identities are separate. Only a complete response paired to
the current request can be consumed, and it can be consumed once. Page content,
attachments, project files, and reviewer prose are untrusted and cannot redefine
the writer, transport, permissions, quota, or safety policy.

Local tests and `closure-check` validate this controller contract only. Real
Windows/macOS browser capability and recovery require real-device evidence.
