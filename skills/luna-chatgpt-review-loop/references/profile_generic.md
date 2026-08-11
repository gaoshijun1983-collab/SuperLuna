# Generic project profile

- Implement one bounded, testable change per review cycle.
- Default to at most five core files, but allow the project rules or explicit review scope to choose a different limit.
- Preserve unrelated user changes and avoid concurrent writers.
- Run focused tests plus the smallest relevant regression set.
- Record commands, exit codes, artifact hashes, exclusions, and rollback instructions.
- Require explicit user approval for destructive, irreversible, external-write, credential, production, or policy-sensitive actions.
