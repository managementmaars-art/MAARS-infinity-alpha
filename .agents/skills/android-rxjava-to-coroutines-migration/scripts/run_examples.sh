#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TARGET="$ROOT/examples/fixtures/rxjava-legacy-sample"

python3 "$ROOT/skills/android-rxjava-to-coroutines-migration/scripts/scan_rxjava_usage.py" "$TARGET"
python3 "$ROOT/skills/android-rxjava-to-coroutines-migration/scripts/generate_migration_checklist.py" "$TARGET"
