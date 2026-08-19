# SuperLuna 0.2.0-alpha.103

- Release metadata now derives the tracked source count from the exact Git
  build input before creating the deterministic archive; the report, evidence
  matrix, and embedded manifest therefore share one count.

Controller 160 / Skill `2026-08-19.117` reconciles a verified frozen candidate
before fixed-Chat mode selection and repairs fixed-Chat submission
recovery after a Codex/browser restart. A controlled exact-URL count is trusted
only when it belongs to the current browser identity (or explicitly attests
that identity). A stale single count is treated as absent, allowing one exact
canonical URL reopen for the already-bound Chat; ambiguous counts still fail
closed. The regression covers the replacement Chat plus empty current tab-list
case without reading retired history or sending a second request.

This remains local controller evidence only. It does not prove a real App
submission or reviewer response.
