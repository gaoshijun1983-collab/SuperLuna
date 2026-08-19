# SuperLuna 0.2.0-alpha.83

Controller 139 / Skill `2026-08-19.96` fails closed when the current Codex host cannot provide a supported direct attachment upload.

- Complete-source runs check an explicit `direct_file_upload` capability before acquiring an account slot, initializing a browser, or creating a first/replacement reviewer Chat.
- Filechooser and direct-upload failures close after one browser action. They send no text, read no Chat, do not refresh or reopen a page, and preserve the original package identity.
- One recovery identity permits one controlled retry of the same package. A second failure becomes terminal `attachment_upload_capability_missing` for that host.
- Formal review requires a current-composer receipt matching package identity plus every volume's filename, byte size, and SHA-256. A visible filename or button is insufficient.
- Exact repository-commit review remains independent of attachment upload.

Local controller tests do not prove that a real Codex host exposes direct file upload or returns the required composer receipt. That remains a real-App Beta gate.
The currently bundled Browser documentation exposes only the filechooser flow, not a separate direct-upload API; therefore the observed macOS in-app-browser failure must currently resolve as `attachment_upload_capability_missing`, not as another automatic chooser retry.
