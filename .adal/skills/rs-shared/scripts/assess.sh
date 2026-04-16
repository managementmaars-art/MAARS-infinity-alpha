#!/usr/bin/env bash
# assess.sh — Front-load ALL reading for rs-impl in a single call
# Usage: bash assess.sh <project-root> [shared-dir]
# Output: structured text with all context the implementation agent needs
#
# Sections are delimited by ===== SECTION_NAME ===== lines.
# Parse the output to extract each section.

set -euo pipefail

ROOT="${1:-.}"
SHARED_DIR="${2:-$(cd "$(dirname "$0")/.." && pwd)}"

section() { printf '\n===== %s =====\n' "$1"; }

# 1. Scan spec
section "SCAN_SPEC"
bash "$SHARED_DIR/scripts/scan-spec.sh" "$ROOT" 2>/dev/null || echo "STATUS=no_spec"

# 2. Scan project
section "SCAN_PROJECT"
bash "$SHARED_DIR/scripts/scan-project.sh" "$ROOT" 2>/dev/null || true

# 3. spec-status.json
section "SPEC_STATUS"
cat "$ROOT/rootspec/spec-status.json" 2>/dev/null || echo '{"valid":false}'

# 4. tests-status.json
section "TESTS_STATUS"
cat "$ROOT/rootspec/tests-status.json" 2>/dev/null || echo '{"lastRun":null,"stories":{}}'

# 5. .rootspec.json (dev server, test command config)
section "ROOTSPEC_JSON"
cat "$ROOT/.rootspec.json" 2>/dev/null || echo '{}'

# 6. All YAML story files
SPEC_DIR=""
if [[ -f "$ROOT/.rootspec.json" ]]; then
  SPEC_DIR=$(grep -o '"specDirectory"[[:space:]]*:[[:space:]]*"[^"]*"' "$ROOT/.rootspec.json" 2>/dev/null | head -1 | sed 's/.*"specDirectory"[[:space:]]*:[[:space:]]*"//' | sed 's/"//')
fi
SPEC_DIR="${SPEC_DIR:-rootspec}"
STORIES_DIR="$ROOT/$SPEC_DIR/05.IMPLEMENTATION/USER_STORIES"

if [[ -d "$STORIES_DIR" ]]; then
  # Search ALL story directories and dedup by story ID.
  # Stories may exist in by_phase/, by_journey/, by_system/ — some dirs may be incomplete.
  # Read every YAML file, extract story IDs, output each story only once.
  SEEN_FILE=$(mktemp)
  trap "rm -f $SEEN_FILE" EXIT
  while IFS= read -r f; do
    FILE_IDS=$(grep -oE '^\s*-?\s*id:\s*(US-[0-9]+)' "$f" 2>/dev/null | grep -oE 'US-[0-9]+' || true)
    is_new=false
    for fid in $FILE_IDS; do
      if ! grep -qw "$fid" "$SEEN_FILE" 2>/dev/null; then
        is_new=true
        echo "$fid" >> "$SEEN_FILE"
      fi
    done
    if $is_new || [[ -z "$FILE_IDS" ]]; then
      section "YAML:$(echo "$f" | sed "s|$ROOT/||")"
      cat "$f"
    fi
  done < <(find "$STORIES_DIR" \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | sort)
  rm -f "$SEEN_FILE"
fi

# 7. Conventions docs
for f in "$ROOT/$SPEC_DIR/CONVENTIONS/technical.md" "$ROOT/$SPEC_DIR/CONVENTIONS/visual.md"; do
  if [[ -f "$f" ]]; then
    section "CONVENTIONS:$(basename "$f")"
    cat "$f"
  fi
done

# 8. package.json scripts (for test command resolution)
section "PACKAGE_SCRIPTS"
if [[ -f "$ROOT/package.json" ]]; then
  # Extract just the scripts block
  node -e "const p=require('./$ROOT/package.json'); console.log(JSON.stringify(p.scripts||{},null,2))" 2>/dev/null \
    || grep -A 30 '"scripts"' "$ROOT/package.json" 2>/dev/null \
    || echo '{}'
else
  echo '{}'
fi

# 9. Fragments — only include compact summaries, not full docs
section "FRAGMENT:dsl-steps"
echo "Core DSL steps: visit, click, fill, loginAs, seedItem, shouldContain, shouldExist"
echo "Extension: add to Step union type in steps.ts + implement in runSetupSteps/runAssertionSteps + register in schema.ts"
echo "CRITICAL: Do NOT use cy.readFile() outside it() blocks — embed YAML as string literals in test files"

section "END"
