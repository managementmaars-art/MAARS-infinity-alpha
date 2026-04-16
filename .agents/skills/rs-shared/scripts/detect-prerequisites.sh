#!/usr/bin/env bash
# detect-prerequisites.sh — Detect dev server, pre-commit, release, and test tooling
# Usage: bash detect-prerequisites.sh [project-root]
# Output: structured text with detected prerequisites

set -euo pipefail

ROOT="${1:-.}"

# --- Dev server ---
DEV_SERVER="none"
# Prefer managed dev.sh script (has process management)
if [[ -f "$ROOT/scripts/dev.sh" ]]; then
  DEV_SERVER="./scripts/dev.sh"
elif [[ -f "$ROOT/package.json" ]]; then
  # Check for dev:start first (managed), then plain scripts
  for script in "dev:start" dev start serve; do
    if grep -qE "\"$script\"[[:space:]]*:" "$ROOT/package.json"; then
      DEV_SERVER="npm run $script"
      break
    fi
  done
fi
if [[ "$DEV_SERVER" == "none" && -f "$ROOT/Makefile" ]]; then
  for target in dev serve; do
    if grep -qE "^${target}:" "$ROOT/Makefile"; then
      DEV_SERVER="make $target"
      break
    fi
  done
fi
echo "DEV_SERVER=$DEV_SERVER"

# --- Pre-commit hook ---
PRE_COMMIT_HOOK="none"
if [[ -f "$ROOT/.husky/pre-commit" ]]; then
  PRE_COMMIT_HOOK=".husky/pre-commit"
elif [[ -f "$ROOT/.git/hooks/pre-commit" ]]; then
  PRE_COMMIT_HOOK=".git/hooks/pre-commit"
elif [[ -f "$ROOT/lefthook.yml" ]]; then
  PRE_COMMIT_HOOK="lefthook.yml"
elif [[ -f "$ROOT/.pre-commit-config.yaml" ]]; then
  PRE_COMMIT_HOOK=".pre-commit-config.yaml"
fi
echo "PRE_COMMIT_HOOK=$PRE_COMMIT_HOOK"

# --- Release script ---
RELEASE_SCRIPT="none"
if [[ -f "$ROOT/scripts/release.sh" ]]; then
  RELEASE_SCRIPT="scripts/release.sh"
elif [[ -f "$ROOT/.release-it.json" ]]; then
  RELEASE_SCRIPT=".release-it.json"
elif [[ -f "$ROOT/.release-it.yaml" ]]; then
  RELEASE_SCRIPT=".release-it.yaml"
elif [[ -f "$ROOT/.releaserc" ]]; then
  RELEASE_SCRIPT=".releaserc"
elif [[ -f "$ROOT/.releaserc.json" ]]; then
  RELEASE_SCRIPT=".releaserc.json"
fi
echo "RELEASE_SCRIPT=$RELEASE_SCRIPT"

# --- Validation/testing ---
VALIDATION_SCRIPT="none"
if [[ -f "$ROOT/package.json" ]]; then
  # Check for test scripts in priority order (most specific first)
  for script in "test:e2e" "cypress" "test"; do
    if grep -qE "\"$script\"[[:space:]]*:" "$ROOT/package.json"; then
      VALIDATION_SCRIPT="npm run $script"
      break
    fi
  done
fi
if [[ "$VALIDATION_SCRIPT" == "none" && -f "$ROOT/Makefile" ]]; then
  if grep -qE "^test:" "$ROOT/Makefile"; then
    VALIDATION_SCRIPT="make test"
  fi
fi
if [[ "$VALIDATION_SCRIPT" == "none" && -f "$ROOT/scripts/test.sh" ]]; then
  VALIDATION_SCRIPT="scripts/test.sh"
fi
echo "VALIDATION_SCRIPT=$VALIDATION_SCRIPT"
