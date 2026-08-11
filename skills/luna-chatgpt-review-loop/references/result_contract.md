# Review reply formats

## Default: ordinary natural language

Chat may answer normally. A complete reply without markers is valid and is saved together with its response identity and hash.

The implementation task continues automatically when the intent is clear. It asks the user only for ambiguity, conflict with project evidence, product-direction changes, deletion or other destructive work, release, payment, or permission changes.

Missing `[LCRL_RESULT_V2]` markers is never a blocking condition.

## Optional compatibility: V2 envelope

Existing integrations may still return the historical V2 JSON, with or without its old marker lines. The controller continues validating and persisting it, including its operation package and policy firewall. New review prompts must not require markers.

This compatibility path exists for old conversations and machine-oriented integrations; it is not the product's default interaction.
