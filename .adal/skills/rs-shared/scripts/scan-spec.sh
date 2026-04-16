#!/usr/bin/env bash
# scan-spec.sh — Find spec directory, list found/missing files, detect version
# Usage: bash scan-spec.sh [project-root]
# Output: structured text with SPEC_DIR, VERSION, FOUND, MISSING sections

set -euo pipefail

ROOT="${1:-.}"

# Try .rootspec.json first
SPEC_DIR=""
if [[ -f "$ROOT/.rootspec.json" ]]; then
  SPEC_DIR=$(grep -o '"specDirectory"[[:space:]]*:[[:space:]]*"[^"]*"' "$ROOT/.rootspec.json" 2>/dev/null | head -1 | sed 's/.*"specDirectory"[[:space:]]*:[[:space:]]*"//' | sed 's/"//')
fi

# Fall back to scanning common locations
if [[ -z "$SPEC_DIR" ]]; then
  for dir in "./rootspec" "./spec" "."; do
    if [[ -f "$ROOT/$dir/00.FRAMEWORK.md" ]]; then
      SPEC_DIR="$dir"
      break
    fi
  done
fi

if [[ -z "$SPEC_DIR" ]]; then
  echo "SPEC_DIR=none"
  echo "VERSION=none"
  echo "STATUS=no_spec"
  exit 0
fi

echo "SPEC_DIR=$SPEC_DIR"

# Detect version from framework file
VERSION="unknown"
FRAMEWORK_FILE="$ROOT/$SPEC_DIR/00.FRAMEWORK.md"
if [[ -f "$FRAMEWORK_FILE" ]]; then
  VERSION=$(grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?' "$FRAMEWORK_FILE" | head -1 || echo "unknown")
fi
echo "VERSION=$VERSION"

# Check for expected files
EXPECTED_FILES=(
  "00.AXIOMS.md"
  "00.FRAMEWORK.md"
  "01.PHILOSOPHY.md"
  "02.TRUTHS.md"
  "03.INTERACTIONS.md"
  "04.SYSTEMS/SYSTEMS_OVERVIEW.md"
)

echo "FOUND="
for f in "${EXPECTED_FILES[@]}"; do
  if [[ -f "$ROOT/$SPEC_DIR/$f" ]]; then
    echo "  $f"
  fi
done

echo "MISSING="
for f in "${EXPECTED_FILES[@]}"; do
  if [[ ! -f "$ROOT/$SPEC_DIR/$f" ]]; then
    echo "  $f"
  fi
done

# Check for L5 directories
HAS_STORIES="false"
HAS_FINE_TUNING="false"
if [[ -d "$ROOT/$SPEC_DIR/05.IMPLEMENTATION/USER_STORIES" ]]; then
  HAS_STORIES="true"
fi
if [[ -d "$ROOT/$SPEC_DIR/05.IMPLEMENTATION/FINE_TUNING" ]]; then
  HAS_FINE_TUNING="true"
fi
echo "HAS_USER_STORIES=$HAS_STORIES"
echo "HAS_FINE_TUNING=$HAS_FINE_TUNING"

# Determine overall status
if [[ -f "$ROOT/$SPEC_DIR/01.PHILOSOPHY.md" ]]; then
  echo "STATUS=has_spec"
else
  echo "STATUS=framework_only"
fi

# Check if conventions docs exist
if [[ -d "$ROOT/$SPEC_DIR/CONVENTIONS" ]]; then
  echo "HAS_CONVENTIONS=true"
else
  echo "HAS_CONVENTIONS=false"
fi
