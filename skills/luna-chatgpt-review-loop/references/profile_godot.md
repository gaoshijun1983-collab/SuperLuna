# Godot project profile

- Use the console executable and `--headless` for automated regression.
- A script passed directly to `--script` must inherit `SceneTree` or `MainLoop`.
- Load `RefCounted`, `Node`, and `Resource` test helpers from a valid test entrypoint.
- Count accidental GUI launch, parse failure, timeout, crash, or nonzero exit code as failure.
- Validate changed `.gd`, `.tscn`, and `.tres` files with the project-compatible Godot version.
- Keep project-specific file-count and line-count limits in the project rules or review instruction.
