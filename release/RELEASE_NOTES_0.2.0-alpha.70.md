# SuperLuna 0.2.0-alpha.70

Controller 126 / Skill revision `2026-08-17.83` fixes replacement reviewer Chat
binding when ChatGPT returns a modern UUID version 6, 7, or 8 conversation ID.

The controller still requires a canonical UUID variant, an exact
`https://chatgpt.com/c/<id>` URL, a new identity distinct from the retired Chat,
and the same pending rollover authorization. Temporary identities, malformed
values, mismatched URLs, and unrelated Chat surfaces remain fail-closed.

This is a technical-testing Alpha. Local tests do not prove a real macOS or
Windows reviewer cycle and do not satisfy the Public Beta gate.
