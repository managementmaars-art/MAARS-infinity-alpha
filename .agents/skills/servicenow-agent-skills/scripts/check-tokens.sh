#!/usr/bin/env bash
set -euo pipefail

LIMIT=18000
FAILED=0

for skill_dir in sn-sdk-fluent sn-sdk-setup sn-scripting; do
  skill_file="$skill_dir/SKILL.md"
  if [[ ! -f "$skill_file" ]]; then
    echo "ERROR: $skill_file not found."
    FAILED=1
    continue
  fi
  # Strip YAML frontmatter (between --- lines) before counting
  body=$(awk '/^---$/{if(++n==2){found=1;next}} found' "$skill_file")
  chars=$(echo "$body" | wc -c)
  if [[ $chars -gt $LIMIT ]]; then
    tokens_est=$(( chars / 4 ))
    echo "ERROR: $skill_file body exceeds token limit (~${tokens_est} tokens estimated, limit ~4500)."
    echo "       Move content to references/ files and keep SKILL.md as a routing-only index."
    FAILED=1
  else
    echo "OK: $skill_file body is within token limit (~${chars} chars)."
  fi
done

[[ $FAILED -eq 0 ]] && echo "OK: All SKILL.md files pass token gate." || exit 1
