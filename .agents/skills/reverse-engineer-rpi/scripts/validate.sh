#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m py_compile \
  "$SKILL_DIR/scripts/reverse_engineer_rpi.py" \
  "$SKILL_DIR/scripts/fetch_url.py" \
  "$SKILL_DIR/scripts/generate_feature_inventory_md.py" \
  "$SKILL_DIR/scripts/scaffold_feature_registry.py" \
  "$SKILL_DIR/scripts/generate_feature_catalog_md.py" \
  "$SKILL_DIR/scripts/validate_feature_registry.py" \
  "$SKILL_DIR/scripts/binary/list_embedded_archives.py" \
  "$SKILL_DIR/scripts/binary/extract_embedded_archives.py"

echo "OK: reverse-engineer-rpi validate.sh passed"
