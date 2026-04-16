#!/usr/bin/env bash
# write-stats.sh — Append a skill run entry to stats.json
# Usage: bash write-stats.sh <stats-path> <skill> <started-at> <completed-at> [iterations] [stories-json]
# Output: appends entry to stats.json, creates file if missing
#
# stories-json is a JSON object like: {"US-101":{"attempts":2},"US-102":{"attempts":5}}

set -euo pipefail

STATS_PATH="${1:-}"
SKILL="${2:-}"
STARTED_AT="${3:-}"
COMPLETED_AT="${4:-}"
ITERATIONS="${5:-null}"
STORIES_JSON="${6:-null}"

if [[ -z "$STATS_PATH" || -z "$SKILL" || -z "$STARTED_AT" || -z "$COMPLETED_AT" ]]; then
  echo "ERROR: usage: write-stats.sh <stats-path> <skill> <started-at> <completed-at> [iterations] [stories-json]" >&2
  exit 1
fi

# Compute duration in seconds
start_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$STARTED_AT" +%s 2>/dev/null || date -d "$STARTED_AT" +%s 2>/dev/null || echo "0")
end_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$COMPLETED_AT" +%s 2>/dev/null || date -d "$COMPLETED_AT" +%s 2>/dev/null || echo "0")
duration=$((end_epoch - start_epoch))
if [[ $duration -lt 0 ]]; then
  duration=0
fi

# Build the new entry
ENTRY=$(cat <<ENTRY_EOF
{
    "skill": "$SKILL",
    "startedAt": "$STARTED_AT",
    "completedAt": "$COMPLETED_AT",
    "durationSeconds": $duration,
    "iterations": $ITERATIONS,
    "stories": $STORIES_JSON
  }
ENTRY_EOF
)

# Create or append to stats.json
if [[ ! -f "$STATS_PATH" ]]; then
  mkdir -p "$(dirname "$STATS_PATH")"
  cat > "$STATS_PATH" <<EOF
{
  "runs": [
  $ENTRY
  ]
}
EOF
else
  # Append to existing runs array
  TMPFILE=$(mktemp)
  trap 'rm -f "$TMPFILE"' EXIT

  # Remove the closing ]}\n, append comma + new entry + close
  # Use awk to drop last two non-empty lines (the ] and })
  awk '
    { lines[NR] = $0 }
    END {
      # Find last two non-blank lines to drop
      last = NR
      while (last > 0 && lines[last] ~ /^[[:space:]]*$/) last--
      second_last = last - 1
      while (second_last > 0 && lines[second_last] ~ /^[[:space:]]*$/) second_last--
      for (i = 1; i <= NR; i++) {
        if (i != last && i != second_last) print lines[i]
      }
    }
  ' "$STATS_PATH" > "$TMPFILE"
  printf ',\n  %s\n  ]\n}\n' "$ENTRY" >> "$TMPFILE"
  mv "$TMPFILE" "$STATS_PATH"
  trap - EXIT
fi

echo "OK: wrote stats entry for $SKILL ($duration seconds)"
