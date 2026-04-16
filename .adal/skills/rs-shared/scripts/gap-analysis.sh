#!/usr/bin/env bash
# gap-analysis.sh — Compare project version against bundled framework version
# Usage: bash gap-analysis.sh [project-root]
# Output: structured key=value lines for rs-update to consume

set -euo pipefail

ROOT="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SHARED_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
UPDATE_MD="$SHARED_DIR/../rs-update/UPDATE.md"

# --- Project version (from .rootspec.json) ---
PROJECT_VERSION="none"
if [[ -f "$ROOT/.rootspec.json" ]]; then
  PROJECT_VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$ROOT/.rootspec.json" 2>/dev/null \
    | head -1 | sed 's/.*"version"[[:space:]]*:[[:space:]]*"//' | sed 's/"//')
fi
echo "PROJECT_VERSION=$PROJECT_VERSION"

if [[ "$PROJECT_VERSION" == "none" ]]; then
  echo "GAP=no_project"
  exit 0
fi

# --- Bundled version (from rs-shared/00.FRAMEWORK.md) ---
BUNDLED_VERSION="unknown"
if [[ -f "$SHARED_DIR/00.FRAMEWORK.md" ]]; then
  BUNDLED_VERSION=$(grep -oE '[0-9]+\.[0-9]+\.[0-9]+' "$SHARED_DIR/00.FRAMEWORK.md" | head -1 || echo "unknown")
fi
echo "BUNDLED_VERSION=$BUNDLED_VERSION"

# --- Compare versions ---
if [[ "$PROJECT_VERSION" == "$BUNDLED_VERSION" ]]; then
  echo "GAP=none"
  exit 0
fi

# Parse semver components
IFS='.' read -r P_MAJOR P_MINOR P_PATCH <<< "$PROJECT_VERSION"
IFS='.' read -r B_MAJOR B_MINOR B_PATCH <<< "$BUNDLED_VERSION"

if [[ "$P_MAJOR" != "$B_MAJOR" ]]; then
  echo "GAP=major"
elif [[ "$P_MINOR" != "$B_MINOR" ]]; then
  echo "GAP=minor"
else
  echo "GAP=patch"
fi

# --- Spec directory ---
SPEC_DIR=""
if [[ -f "$ROOT/.rootspec.json" ]]; then
  SPEC_DIR=$(grep -o '"specDirectory"[[:space:]]*:[[:space:]]*"[^"]*"' "$ROOT/.rootspec.json" 2>/dev/null \
    | head -1 | sed 's/.*"specDirectory"[[:space:]]*:[[:space:]]*"//' | sed 's/"//')
fi
SPEC_DIR="${SPEC_DIR:-rootspec}"
echo "SPEC_DIR=$SPEC_DIR"

# --- Framework/Axioms staleness ---
FRAMEWORK_STALE="false"
if [[ -f "$ROOT/$SPEC_DIR/00.FRAMEWORK.md" && -f "$SHARED_DIR/00.FRAMEWORK.md" ]]; then
  if ! diff -q "$ROOT/$SPEC_DIR/00.FRAMEWORK.md" "$SHARED_DIR/00.FRAMEWORK.md" > /dev/null 2>&1; then
    FRAMEWORK_STALE="true"
  fi
fi
echo "FRAMEWORK_STALE=$FRAMEWORK_STALE"

AXIOMS_STALE="false"
if [[ -f "$ROOT/$SPEC_DIR/00.AXIOMS.md" && -f "$SHARED_DIR/00.AXIOMS.md" ]]; then
  if ! diff -q "$ROOT/$SPEC_DIR/00.AXIOMS.md" "$SHARED_DIR/00.AXIOMS.md" > /dev/null 2>&1; then
    AXIOMS_STALE="true"
  fi
fi
echo "AXIOMS_STALE=$AXIOMS_STALE"

# --- Stale templates (compare project scripts against bundled templates) ---
STALE_TEMPLATES=""
if [[ -f "$ROOT/scripts/dev.sh" && -f "$SHARED_DIR/scripts/dev.sh" ]]; then
  if ! diff -q "$ROOT/scripts/dev.sh" "$SHARED_DIR/scripts/dev.sh" > /dev/null 2>&1; then
    STALE_TEMPLATES="scripts/dev.sh"
  fi
fi
echo "STALE_TEMPLATES=$STALE_TEMPLATES"

# --- Parse UPDATE.md for prerequisite changes between versions ---
NEW_PREREQUISITES=""
CHANGED_PREREQUISITES=""
HAS_BREAKING="false"

if [[ -f "$UPDATE_MD" ]]; then
  # Extract sections between project version and bundled version
  # UPDATE.md has ## X.Y.Z headers; we want entries AFTER project version up to bundled version
  IN_RANGE="false"
  while IFS= read -r line; do
    # Detect version headers
    if [[ "$line" =~ ^##\ ([0-9]+\.[0-9]+\.[0-9]+) ]]; then
      VER="${BASH_REMATCH[1]}"
      if [[ "$VER" == "$PROJECT_VERSION" ]]; then
        IN_RANGE="false"  # Don't include the version we're already on
      elif [[ "$VER" == "$BUNDLED_VERSION" || "$IN_RANGE" == "true" ]]; then
        IN_RANGE="true"
      fi
      continue
    fi

    if [[ "$IN_RANGE" == "true" ]]; then
      # Parse NEW: and CHANGED: prerequisite lines
      if [[ "$line" =~ ^[[:space:]]*NEW:\ (.+) ]]; then
        entry="${BASH_REMATCH[1]}"
        if [[ -n "$NEW_PREREQUISITES" ]]; then
          NEW_PREREQUISITES="$NEW_PREREQUISITES|$entry"
        else
          NEW_PREREQUISITES="$entry"
        fi
      elif [[ "$line" =~ ^[[:space:]]*CHANGED:\ (.+) ]]; then
        entry="${BASH_REMATCH[1]}"
        if [[ -n "$CHANGED_PREREQUISITES" ]]; then
          CHANGED_PREREQUISITES="$CHANGED_PREREQUISITES|$entry"
        else
          CHANGED_PREREQUISITES="$entry"
        fi
      elif [[ "$line" =~ ^Breaking: ]]; then
        HAS_BREAKING="true"
      fi
    fi
  done < "$UPDATE_MD"
fi

echo "NEW_PREREQUISITES=$NEW_PREREQUISITES"
echo "CHANGED_PREREQUISITES=$CHANGED_PREREQUISITES"
echo "HAS_BREAKING=$HAS_BREAKING"
