# Troubleshooting

## A task appears stuck

Run `lcrl.py doctor --state <state.json>`. Check the action lease, latest runtime event, network error count, confirmed Chat, and payload capability. An unexpired lease means a previous foreground turn still owns the action.

If a foreground resume first receives a real action such as `review_submit` and later reports `concurrent_backoff`, inspect the trace for a second `tick` call. The first result remains authoritative. Do not run `tick` again inside the same turn; finish or safely close the first action and release its lease.

If the state says `review_waiting` but has no persisted request turn/message IDs, or still contains response IDs from an older stage, V8 reports a state invariant violation. If a send click occurred with an incomplete receipt, preserve the complete `app_chat_submission_uncertain` JSON and pass it back through `reconcile-submission --context-file`. Reconciliation accepts only a same-instance, same-Chat, same-payload message absent from the captured pre-click baseline; an older identical message is not evidence. Never invent IDs or resend.

When reconciliation sees both sides of a completed Chat turn, persist the user-message request ID first and the assistant-message response ID second. A shared turn ID does not make those message IDs interchangeable.

## Chat returned `next_operation` but validation asks for other fields

Alpha.3 accepts the historical top-level `next_operation` object as a lossless compatibility alias and converts it to canonical `next_step` plus `operation_package`. Do not ask Chat to review again. New prompts must request the canonical fields directly.

## The task reports the same blocker repeatedly

The controller returns a notification action once and a silent wait action afterward. If repeated notifications continue, verify that the installed Skill uses revision `2026-08-03.18` or newer and pause every legacy recovery automation.

## A result exists but is not applied

Check `request_reasoning_mode`, `request_stage`, `response_stage`, and `response_valid_for_apply`. A review sent before confirmed Extreme mode or belonging to another stage is intentionally quarantined. Confirming Extreme later does not retroactively validate the old response.

## Old V6 heartbeats are still visible

Updating an automation cannot rewrite turns that were already queued. Pause every old automation. Revision `2026-08-03.18` makes every legacy heartbeat call return `monitor_retired` without reading Chat or changing state. Do not submit duplicate review requests during migration.

## Heartbeat rendering exceeds 1200 bytes

Use Skill revision `2026-08-02.12` or newer. Earlier V8 P0 templates could exceed the safety limit when both the state and controller lived under long Windows paths. Do not raise the limit to hide the problem; regenerate the heartbeat from the shortened immutable template.

If `render-waiting-check` reports the same limit, first confirm Controller 80 /
Skill revision `2026-08-12.34` or newer. Its browser-send authorization projects
the later one-shot prompt before the click and its waiting automation id is
limited to 64 single-line characters. `waiting_prompt_capacity_exceeded` means
the state path itself is outside the supported budget: do not send, raise the
limit, hand-edit the prompt, or reuse a partially submitted run. Start a clean
run at a shorter state path.

## The reviewer cannot read local files

Local paths are not evidence. Use a bounded inline packet or a user-confirmed native attachment. Enable `mcp_readonly` only after identity, allowed root, and exact read-only capabilities have been verified.

## The network error count keeps increasing

The controller fingerprints completion events and processes each timestamp once. Repeated counts should correspond to distinct local completion events. Use the replay fixture to reproduce the behavior without a live network.

## Pro is not becoming eligible after three hours

Run `model-status`. The counter tracks recorded active development minutes, not elapsed wall time. At least three events must also be marked as meaningful and carry stable evidence fingerprints. Replaying an event ID does not add time.

## Terra was requested but did not switch models

This is intentional. A request is only a permission record. Confirm that `terra_next_turn=supported`, obtain explicit next-turn confirmation, then run `confirm-terra`. The controller never claims that the UI switched automatically and never creates a replacement task.

## Recovery checklist

1. Validate the state with `doctor`; use `audit` only to find legacy automation.
2. Confirm there is no ACTIVE recurring automation for the implementation task.
3. Confirm the reviewer remains the user-selected `kind=chatgpt` Chat.
4. Confirm the payload fingerprint before any resubmission.
5. Release a lease only after its owning turn is known to have ended; otherwise wait for expiry.
