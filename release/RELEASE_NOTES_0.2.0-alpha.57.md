# SuperLuna 0.2.0-alpha.57

Alpha 57 source packages Controller 113 and Skill revision `2026-08-14.70`.

This candidate fixes a natural-language safety-gate false positive found in
Round 16 of the NPC AI review run. A reviewer described a test expectation as
`scenario deletion -> contract FAIL`; the previous controller saw the word
`deletion` and quarantined the otherwise bounded local test-contract change as
if it requested a real destructive action.

The high-impact gate now excludes only expected-failure mapping lines that
contain test, contract, assertion, or fingerprint context and an explicit
`FAIL` result. The full reviewer reply is preserved. Imperative deletion and
deletion targeting project files, source, repositories, production systems, or
user data remain fail-closed.

This remains a technical-testing Alpha. Local regression tests do not satisfy
the real macOS/Windows continuous-loop or Public Beta gates.
