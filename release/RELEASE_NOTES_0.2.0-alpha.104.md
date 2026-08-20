# SuperLuna 0.2.0-alpha.104

- Ordinary implementation entry now fails closed when a continuous `local_work`
  turn already owns a valid one-shot `local_continuation` occurrence. It leaves
  the bound occurrence untouched and waits for that platform wake instead of
  creating a competing implementation lease.
- The regression covers the same task, continuous goal, active reviewer
  generation, and exact continuation token/RDATE. It proves zero project or
  Chat access and no state mutation at the competing entry gate.
- The safe-block response also exposes the unchanged continuation kind, token,
  automation identity, and `lease_id=none`, so the host can resume the existing
  occurrence without guessing or creating another one.
- Fixed a response-contract regression where the local-continuation wake had
  persisted its lease but a duplicate response field overwrote the returned
  lease identity with `none`. The wake response now preserves the live lease;
  the regression proves the lease can be handed to the same task safely.
- An active local continuation whose RDATE has expired no longer remains
  permanently `already_bound`. Ordinary entry exposes one exact platform
  lookup and grants no project, browser, or Chat authority.
- If the saved platform task still exists, recovery rotates only its token and
  RDATE and updates that same task. If it is missing, recovery opens exactly
  one replacement binding. Both paths require the original implementation
  task and automation identity; a mismatch leaves the state bytes unchanged.
- The old token occurrence expires silently with zero workflow or project side
  effects. The replacement token can wake `local_work` once, while duplicate
  delivery remains a no-op.
- Git-backed review packets are now repository-first: they identify the
  canonical remote, default/current branch, exact commit, baseline comparison
  range, changed paths, locked-decision pointer, and must-read files. Local
  absolute paths are explicitly excluded from reviewer-visible evidence.
- An unverified remote identity, an exact commit not proven present on the
  target remote, or an unverified repository access identity now fails closed
  instead of silently presenting an attachment as a complete repository
  review. Attachments remain supplemental runtime evidence; non-Git projects
  retain the existing complete-source attachment flow and its stated limits.

This remains local controller evidence only. It does not prove a real App
submission, reviewer response, or Public Beta readiness.

Local validation evidence: the focused repository-review contract suite passes
26/26, including the exact-commit remote probe. The complete repository suite
passes 466/466. Controller selftest was 15/15 and closure-check reported
`ok=true`. Closure-check still reports repository and real-device gates as not
run by that command.
