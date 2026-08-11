#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/skills/luna-chatgpt-review-loop"
target_root="${CODEX_HOME:-$HOME/.codex}/skills"
target_dir="$target_root/luna-chatgpt-review-loop"

mkdir -p "$target_root"
if [[ -e "$target_dir" ]]; then
  echo "Refusing to overwrite existing Skill: $target_dir" >&2
  echo "Move or remove it explicitly, then run this installer again." >&2
  exit 2
fi

cp -R "$source_dir" "$target_dir"
find "$target_dir" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$target_dir" -type f -name '*.pyc' -delete
python3 "$target_dir/scripts/lcrl.py" selftest
echo "Installed: $target_dir"
echo "Start a new Codex task to load the updated Skill."
