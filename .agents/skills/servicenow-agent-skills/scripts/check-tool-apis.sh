#!/usr/bin/env bash
set -euo pipefail

FORBIDDEN='WebFetch|cursor_read_file|cursor_list_files|cursor_edit_file|vscode\.|copilot\.'
FAILED=0

for skill_dir in sn-sdk-fluent sn-sdk-setup sn-scripting; do
  skill_file="$skill_dir/SKILL.md"
  if [[ ! -f "$skill_file" ]]; then
    continue
  fi
  if grep -qE "$FORBIDDEN" "$skill_file"; then
    matched=$(grep -nE "$FORBIDDEN" "$skill_file" | head -5)
    echo "ERROR: $skill_file contains tool-specific API calls (WebFetch, cursor_read_file, etc.)."
    echo "       These calls break cross-platform compatibility (Claude Code, Cursor, VS Code Copilot)."
    echo "       Matches:"
    echo "$matched"
    echo "       Remove or replace with generic file-read instructions."
    FAILED=1
  else
    echo "OK: $skill_file — no tool-specific API calls."
  fi
done

[[ $FAILED -eq 0 ]] || exit 1
