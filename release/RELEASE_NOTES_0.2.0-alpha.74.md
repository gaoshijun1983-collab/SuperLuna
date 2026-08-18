# SuperLuna 0.2.0-alpha.74

Controller 130 / Skill revision `2026-08-18.87` separates technical recovery
from real product decisions.

- Expected technical blockers expose stable reason codes, concrete Chinese and
  English explanations, and an explicit system recovery action with
  `user_choice_required=false`.
- Task identity mismatch, missing capability, cooldown, browser-slot conflict,
  recoverable wait, missing platform wait, and controller failure no longer
  appear as the vague `需要你决定` state.
- A real user decision is reserved for mutually exclusive changes to the
  confirmed product goal, authorized scope, or risk boundary. It must include
  one concrete question and two or three options with their impacts.
- This is local controller evidence only. Real macOS, Windows, and Public Beta
  gates remain blocked until their recorded evidence is complete.
