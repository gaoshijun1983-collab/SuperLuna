# Contributing

Keep the core deterministic, local-first, and standard-library-only unless a dependency has a clear reliability or security benefit.

For every behavior change:

1. Add or update a unit or failure-replay test.
2. Preserve the immutable role and quota policy.
3. Validate the Skill and Plugin manifests.
4. Run the full test suite on Windows, macOS, and Linux where possible.
5. Document any state-schema migration.

Do not add writable MCP tools to the default plugin. New project-specific behavior belongs in a profile, not in the core Skill.
