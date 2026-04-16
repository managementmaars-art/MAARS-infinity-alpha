#!/usr/bin/env bash
set -euo pipefail

FAILED=0
EXAMPLES=$(find sn-sdk-fluent/assets/examples -name "*.now.ts" 2>/dev/null || true)

if [[ -z "$EXAMPLES" ]]; then
  echo "OK: No .now.ts example files found (skipping import check)."
  exit 0
fi

for f in $EXAMPLES; do
  # Match bare @servicenow/sdk import — NOT @servicenow/sdk/core or @servicenow/sdk/global
  if grep -qE "from ['\"]@servicenow/sdk['\"]" "$f"; then
    echo "ERROR: $f imports from '@servicenow/sdk' instead of '@servicenow/sdk/core'."
    echo "       Use: import { ... } from '@servicenow/sdk/core'"
    FAILED=1
  else
    echo "OK: $f uses correct import path."
  fi
done

[[ $FAILED -eq 0 ]] || exit 1
