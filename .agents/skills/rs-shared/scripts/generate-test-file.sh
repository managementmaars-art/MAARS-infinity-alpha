#!/usr/bin/env bash
# generate-test-file.sh — Build a Cypress test file from spec YAML stories
# Usage: bash generate-test-file.sh <spec-dir> <output-path> [phase-filter]
#
# Reads YAML story files (multi-doc or array format), embeds them as string
# literals in a Cypress test file using the loadAndRun() pattern.
#
# If output file already exists, appends only NEW stories (by ID).
# Strips narrative fields and non-core DSL steps from embedded YAML.

set -euo pipefail

SPEC_DIR="${1:?Usage: generate-test-file.sh <spec-dir> <output-path> [phase-filter]}"
OUTPUT="${2:?Usage: generate-test-file.sh <spec-dir> <output-path> [phase-filter]}"
PHASE="${3:-}"

STORIES_DIR="$SPEC_DIR/05.IMPLEMENTATION/USER_STORIES"

if [[ ! -d "$STORIES_DIR" ]]; then
  echo "ERROR: No user stories directory at $STORIES_DIR" >&2
  exit 1
fi

# Require node and js-yaml
if ! command -v node &>/dev/null; then
  echo "ERROR: node is required" >&2
  exit 1
fi

# Find YAML files — search ALL directories, dedup by story ID in node
# If a phase filter is given, prefer by_phase/$PHASE but also search everywhere
YAML_FILES=()
if [[ -n "$PHASE" ]]; then
  # Phase-specific: search by_phase/$PHASE first, then all dirs for that phase annotation
  PHASE_DIR="$STORIES_DIR/by_phase/$PHASE"
  if [[ -d "$PHASE_DIR" ]]; then
    while IFS= read -r f; do YAML_FILES+=("$f"); done < <(find "$PHASE_DIR" \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | sort)
  fi
  # Also search all other dirs for stories tagged with this phase (catches incomplete by_phase/)
  while IFS= read -r f; do
    # Skip files already found in by_phase
    already=false
    for existing in "${YAML_FILES[@]}"; do
      [[ "$f" == "$existing" ]] && already=true && break
    done
    $already && continue
    # Check if file has the phase annotation
    if grep -qi "@phase:.*${PHASE}" "$f" 2>/dev/null; then
      YAML_FILES+=("$f")
    fi
  done < <(find "$STORIES_DIR" \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | sort)
fi

# No phase filter or no results: search everything
if [[ ${#YAML_FILES[@]} -eq 0 ]]; then
  while IFS= read -r f; do YAML_FILES+=("$f"); done < <(find "$STORIES_DIR" \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | sort)
fi

if [[ ${#YAML_FILES[@]} -eq 0 ]]; then
  echo "ERROR: No YAML files found in $STORIES_DIR" >&2
  exit 1
fi

# Collect existing story IDs from output file
EXISTING_IDS=""
if [[ -f "$OUTPUT" ]]; then
  EXISTING_IDS=$(grep -oE 'US-[0-9]+' "$OUTPUT" 2>/dev/null | sort -u | tr '\n' ',' || true)
fi

# Use node to parse YAML, extract stories, clean them, and output TypeScript
FILE_LIST=$(printf '%s\n' "${YAML_FILES[@]}")
RESULT=$(node -e "
const fs = require('fs');
const yaml = require('js-yaml');

const CORE_SETUP_STEPS = new Set(['visit', 'click', 'fill', 'loginAs', 'seedItem']);
const CORE_ASSERT_STEPS = new Set(['shouldContain', 'shouldExist']);
const ALL_CORE = new Set([...CORE_SETUP_STEPS, ...CORE_ASSERT_STEPS]);

const existingIds = new Set('${EXISTING_IDS}'.split(',').filter(Boolean));
const files = \`${FILE_LIST}\`.trim().split('\n').filter(Boolean);

let added = 0, skipped = 0, warnings = [];
const storyBlocks = [];

for (const file of files) {
  let content;
  try { content = fs.readFileSync(file, 'utf8'); } catch { continue; }

  // Parse multi-doc YAML
  let docs;
  try { docs = yaml.loadAll(content); } catch { continue; }

  for (const doc of docs) {
    if (!doc) continue;

    // Handle both formats: direct story object or array of stories
    const stories = Array.isArray(doc) ? doc : (doc.id ? [doc] : (Array.isArray(doc.stories) ? doc.stories : []));

    for (const story of stories) {
      if (!story || !story.id || !story.acceptance_criteria) continue;
      if (existingIds.has(story.id)) continue;

      // Check for DSL format and filter to core steps only
      let hasDslSteps = false;
      const cleanedAC = [];

      for (const ac of story.acceptance_criteria) {
        const cleanAc = { id: ac.id, title: ac.title };

        // Clean given/when/then — keep only core DSL steps
        for (const phase of ['given', 'when', 'then']) {
          if (Array.isArray(ac[phase])) {
            const filtered = ac[phase].filter(step => {
              if (typeof step !== 'object') return false;
              const key = Object.keys(step)[0];
              if (ALL_CORE.has(key)) { hasDslSteps = true; return true; }
              warnings.push(story.id + ': stripped non-core step \"' + key + '\"');
              return false;
            });
            if (filtered.length > 0) cleanAc[phase] = filtered;
          }
        }

        // Ensure at least empty arrays
        if (!cleanAc.given) cleanAc.given = [{ visit: '/' }];
        if (!cleanAc.when) cleanAc.when = [];
        if (!cleanAc.then) cleanAc.then = [];

        cleanedAC.push(cleanAc);
      }

      if (!hasDslSteps) {
        warnings.push(story.id + ': no core DSL steps found — skipping');
        skipped++;
        continue;
      }

      // Build clean YAML for this story
      const cleanStory = {
        id: story.id,
        title: story.title,
        acceptance_criteria: cleanedAC
      };

      const yamlStr = yaml.dump(cleanStory, { lineWidth: -1, noRefs: true, quotingType: \"'\" });
      const varName = 'stories_' + story.id.replace('US-', '').replace(/-/g, '_');

      storyBlocks.push({
        id: story.id,
        title: story.title,
        varName,
        yaml: yamlStr
      });

      existingIds.add(story.id);
      added++;
    }
  }
}

// Output as JSON for bash to consume
console.log(JSON.stringify({ added, skipped, warnings, storyBlocks }));
" 2>&1)

# Check for node errors
if [[ $? -ne 0 ]]; then
  echo "ERROR: node processing failed: $RESULT" >&2
  exit 1
fi

ADDED=$(echo "$RESULT" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.added)")
SKIPPED=$(echo "$RESULT" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.skipped)")

# Print warnings
echo "$RESULT" | node -e "
  const d=JSON.parse(require('fs').readFileSync(0,'utf8'));
  for (const w of d.warnings) console.error('WARNING: ' + w);
" 2>&1 >&2 || true

if [[ "$ADDED" -eq 0 ]]; then
  echo "No new stories to add ($SKIPPED skipped)"
  exit 0
fi

# Build TypeScript content from story blocks
TS_CONTENT=$(echo "$RESULT" | node -e "
  const d=JSON.parse(require('fs').readFileSync(0,'utf8'));
  const lines = [];
  for (const s of d.storyBlocks) {
    lines.push('');
    lines.push('// ' + s.id + ': ' + s.title);
    lines.push('const ' + s.varName + ' = \`');
    lines.push(s.yaml.trimEnd());
    lines.push('\`;');
    lines.push('loadAndRun(' + s.varName + ');');
  }
  console.log(lines.join('\n'));
")

HEADER='import * as yaml from '"'"'js-yaml'"'"';
import { UserStorySchema } from '"'"'../support/schema'"'"';
import type { UserStory } from '"'"'../support/schema'"'"';
import { runSetupSteps, runAssertionSteps } from '"'"'../support/steps'"'"';

function loadAndRun(yamlContent: string) {
  const docs = yaml.loadAll(yamlContent) as UserStory[];
  for (const doc of docs) {
    if (!doc || !doc.id) continue;
    const story = UserStorySchema.parse(doc);
    const describeFn = story.skip ? describe.skip : story.only ? describe.only : describe;
    describeFn(`${story.id}: ${story.title}`, () => {
      for (const ac of story.acceptance_criteria) {
        const itFn = ac.skip ? it.skip : ac.only ? it.only : it;
        itFn(`${ac.id}: ${ac.title}`, () => {
          if (ac.given) runSetupSteps(ac.given);
          if (ac.when) runSetupSteps(ac.when);
          if (ac.then) runAssertionSteps(ac.then);
        });
      }
    });
  }
}'

if [[ -f "$OUTPUT" ]]; then
  echo "$TS_CONTENT" >> "$OUTPUT"
  echo "Appended $ADDED new stories to $OUTPUT ($SKIPPED skipped)"
else
  mkdir -p "$(dirname "$OUTPUT")"
  printf '%s\n%s\n' "$HEADER" "$TS_CONTENT" > "$OUTPUT"
  echo "Created $OUTPUT with $ADDED stories ($SKIPPED skipped)"
fi
