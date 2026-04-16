#!/usr/bin/env bash
# Validate all JSONL fixture files in tests/fixtures/message_grouping/
# Each line must be valid JSON

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE_DIR="$SCRIPT_DIR/../tests/fixtures/message_grouping"

echo "=== Validating Message Grouping Fixtures ==="
echo ""

errors=0
for f in "$FIXTURE_DIR"/*.jsonl; do
    filename=$(basename "$f")
    echo -n "Checking $filename... "

    line_num=0
    while IFS= read -r line || [[ -n "$line" ]]; do
        line_num=$((line_num + 1))
        # Skip empty lines
        if [[ -z "${line// }" ]]; then
            continue
        fi
        # Validate JSON
        if ! echo "$line" | jq -e . > /dev/null 2>&1; then
            echo "INVALID"
            echo "  Line $line_num: Invalid JSON"
            echo "  Content: ${line:0:80}..."
            errors=$((errors + 1))
            continue 2  # Continue to next file
        fi
    done < "$f"

    echo "OK ($line_num lines)"
done

echo ""
if [[ $errors -gt 0 ]]; then
    echo "=== FAILED: $errors file(s) had errors ==="
    exit 1
else
    echo "=== All fixtures valid! ==="
    exit 0
fi
