# Model and quota policy

## Invariants

- Keep `Luna Medium` as the default project writer. An explicitly user-fixed `Terra Medium` implementation task is also valid, but its role must be selected at initialization and remain unchanged for the run.
- Escalate one Luna turn to High only when the current task has evidence of unusual reasoning difficulty: a safety/concurrency/recovery change, an inseparable change across at least three contracts, two distinct failed bounded attempts, or a material conflict between Chat guidance and project evidence. High is a bounded escalation, not the default.
- Keep the user-confirmed reviewer mode in the bound ChatGPT web conversation; SuperLuna records visible evidence but never changes the selector.
- Never switch a model or create a task/Chat automatically.
- Treat Pro and Terra state as an auditable permission ledger, not proof that the UI changed.
- Keep `Chat advice`, `route authorization`, and `execution fact` separate. `unknown`, `authorized`, and `verified` are not interchangeable. In this release the only allowed verified fact is `manual_attested`: a human supplied concrete evidence. It is never platform verification and never evidence that the controller switched a model.
- Do not run Terra and Pro at the same time.
- Treat routing as an 80/20 ceiling, not a target: Luna High may occupy at most two of the latest ten meaningful implementation steps. Terra may occupy at most one of the latest twenty and remains exceptional.

## Fixed implementation role

Use `luna_medium` unless the user explicitly fixes the implementation task to `terra_medium`. Pass the same role to `autonomous-preflight` and `init`. The controller requires `policy.implementation_role`, `model_policy.executor.default`, and `model_policy.executor.current` to match exactly. A mismatch fails closed; it is never repaired by silently switching the task. The routing ledger below governs bounded escalation from a Luna baseline and does not rewrite an explicitly fixed Terra baseline.

## Chat routing advice

The reviewer may return `MEDIUM`, `HIGH_ONCE`, or `TERRA_REQUEST` only inside one complete final `[SUPERLUNA_MODEL_ROUTE]` block. Model words elsewhere are ordinary prose and have no routing effect. Missing, malformed, duplicated, non-final, or incomplete blocks fail closed to Medium. A `PASS` verdict can never escalate.

`HIGH_ONCE` requires a stable blocker ID, one allowed High signal, evidence, one bounded scope, and exit criteria. `record-high-attempt` records an authorized High route, not a completed High execution; its initial execution fact is `authorized`. Use `verify-execution --target high --source manual_confirmed` only when a human supplies concrete proof that the matching High turn actually ran. The stored verification type is `manual_attested`; it must be displayed as a human attestation, never as platform verification. The controller does not detect or switch models itself. The allowed High signals are safety/concurrency/recovery, an inseparable cross-contract change, two distinct failed attempts, or a material evidence conflict.

`TERRA_REQUEST` must cite the same-blocker High record with `execution_status=verified` and one of the five Terra signals below. Chat advice is only eligibility input: capability verification, a safe boundary, the rolling ceiling, and explicit user confirmation still control authorization.

## Progress accounting

Record only measured active development time attached to a completed evidence-producing action. Do not count heartbeat wakeups, Chat waiting time, network backoff, duplicate retries, or unattended wall-clock time.

Every progress event requires a unique ID, stage, 1–120 active minutes, unique evidence fingerprint, and an explicit meaningful-step flag. Replaying the same ID with the same evidence is idempotent; replaying it with different evidence or assigning the same evidence to another ID is an error. The controller never evicts old IDs to make room for a replay; a full bounded ledger must be diagnosed or completed explicitly. The published `state_schema_v7.json` mirrors this nested event shape and its 20-event bound; uniqueness and counter-to-event reconciliation remain runtime checks.

## Pro milestone review

Pro becomes eligible only after both thresholds pass:

- 180 active development minutes since the last completed Pro milestone;
- 3 meaningful, evidence-producing development steps.

There is no normal daily-count cap. The three-hour active-time threshold, one outstanding request, explicit confirmation, and exactly-once completion form the quota guard. Do not convert unattended wall time into eligibility.

At a safe `local_work` boundary:

1. Run `request-pro` and preserve its request ID.
2. Ask the user to select Pro in the already bound web Chat; do not create another Chat.
3. After visible confirmation, run `confirm-pro` with the same request ID.
4. Submit one milestone evidence packet and request a complete development guide.
5. Save the result as a versioned Markdown file inside the project root.
6. Hash the saved file and run `complete-pro` with its version, path, SHA-256, and request ID.
7. Verify the controller restored `sol_extreme` and reset only the post-Pro progress counter.

If confirmation is declined, run `cancel-pro`. Cancelling an already active Pro review requires a forced, explicit recovery after confirming that its result will not be applied.

## Terra escalation

Terra is a last implementation escalation after a bounded, execution-verified Luna High turn still leaves the same blocker unresolved. A signal name alone is not enough. Require reproducible evidence, a verified next-turn capability, a safe workflow boundary, no active Pro review, and explicit user confirmation.

Allow only these evidence-backed difficulty signals:

- `repeated_test_failure`: the same scoped failure remains after two distinct evidence-backed Luna attempts; command mistakes and environment failures do not count.
- `cross_module_refactor`: correctness requires one coordinated change across at least three modules or contracts and it cannot be split safely.
- `debugger_impasse`: reproduction and logs exist, but the root cause remains unknown after testing at least two plausible hypotheses.
- `performance_investigation`: a repeatable benchmark or profile proves a budget breach; subjective slowness does not count.
- `migration_complexity`: a real data, schema, or API compatibility migration has rollback or idempotency risk; an ordinary rename does not count.

First record the observed capability with `set-terra-capability`. Only `supported` allows a request. Then:

1. Preserve the verified Luna High execution fact and matching blocker evidence, then run `request-terra` with one matching signal and a bounded reason.
2. Ask for confirmation that the next implementation turn can use Terra.
3. Run `confirm-terra` with the request ID. This records Terra authorization only; it does not switch the executor field.
4. If an external, human-confirmed execution fact exists, record it with `verify-execution --target terra --source manual_confirmed` before completion.
5. Run `complete-terra`; an unverified execution remains `authorized`, never `verified`.

Use `cancel-terra` when the request is rejected. Downgrading capability or cancelling an approved turn requires `--force` only after verifying that the Terra turn has stopped.

## Status interpretation

Use `model-status` as the single read-only summary. `automatic_model_switch=false` and `automatic_thread_creation=false` must always remain visible. A recommendation is never authorization to consume Pro or Terra quota, and authorization is never proof of model execution.
