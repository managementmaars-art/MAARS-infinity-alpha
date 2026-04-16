#!/usr/bin/env bash
# preflight-story.sh — Extract requirements from YAML stories and check what exists
# Usage: bash preflight-story.sh <yaml-file-or-dir> <project-root>
#
# Parses YAML story files for routes, selectors, DSL steps, and Cypress tasks.
# Cross-references against the project source to report what exists vs. what's missing.
# Run BEFORE writing code to know exactly what needs to be built.
#
# Output: KEY=value lines for each category (machine-parseable)

set -euo pipefail

INPUT="${1:?Usage: preflight-story.sh <yaml-file-or-dir> <project-root>}"
ROOT="${2:-.}"

# Require node and js-yaml
if ! command -v node &>/dev/null; then
  echo "ERROR: node is required" >&2
  exit 1
fi

# Collect YAML files
YAML_FILES=()
if [[ -d "$INPUT" ]]; then
  while IFS= read -r f; do YAML_FILES+=("$f"); done < <(find "$INPUT" \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | sort)
elif [[ -f "$INPUT" ]]; then
  YAML_FILES=("$INPUT")
else
  echo "ERROR: $INPUT is not a file or directory" >&2
  exit 1
fi

if [[ ${#YAML_FILES[@]} -eq 0 ]]; then
  echo "ERROR: No YAML files found" >&2
  exit 1
fi

FILE_LIST=$(printf '%s\n' "${YAML_FILES[@]}")

# Extract all requirements from YAML using node
REQUIREMENTS=$(node -e "
const fs = require('fs');
const yaml = require('js-yaml');

const CORE_SETUP = new Set(['visit', 'click', 'fill', 'loginAs', 'seedItem']);
const CORE_ASSERT = new Set(['shouldContain', 'shouldExist']);
const CORE_ALL = new Set([...CORE_SETUP, ...CORE_ASSERT]);

const files = \`${FILE_LIST}\`.trim().split('\n').filter(Boolean);

const routes = new Set();
const selectors = new Set();
const dslSteps = new Set();
const customSteps = new Set();
const tasks = new Set();
const storyIds = [];

for (const file of files) {
  let content;
  try { content = fs.readFileSync(file, 'utf8'); } catch { continue; }

  let docs;
  try { docs = yaml.loadAll(content); } catch { continue; }

  for (const doc of docs) {
    if (!doc) continue;
    const stories = Array.isArray(doc) ? doc : (doc.id ? [doc] : (Array.isArray(doc.stories) ? doc.stories : []));

    for (const story of stories) {
      if (!story || !story.id || !story.acceptance_criteria) continue;
      storyIds.push(story.id);

      for (const ac of story.acceptance_criteria) {
        for (const phase of ['given', 'when', 'then']) {
          if (!Array.isArray(ac[phase])) continue;
          for (const step of ac[phase]) {
            if (typeof step !== 'object') continue;
            const key = Object.keys(step)[0];
            dslSteps.add(key);

            if (!CORE_ALL.has(key)) customSteps.add(key);

            // Extract routes from visit steps
            if (key === 'visit') routes.add(step.visit);

            // Extract selectors from steps with selector property
            const val = step[key];
            if (val && typeof val === 'object' && val.selector) {
              selectors.add(val.selector);
            }

            // Track Cypress tasks (loginAs, seedItem, and custom tasks)
            if (key === 'loginAs') tasks.add('loginAs');
            if (key === 'seedItem') tasks.add('seedItem');
          }
        }
      }
    }
  }
}

console.log(JSON.stringify({
  storyIds,
  routes: [...routes],
  selectors: [...selectors],
  dslSteps: [...dslSteps],
  customSteps: [...customSteps],
  tasks: [...tasks]
}));
" 2>&1)

if [[ $? -ne 0 ]]; then
  echo "ERROR: YAML parsing failed: $REQUIREMENTS" >&2
  exit 1
fi

# Parse JSON output
STORY_IDS=$(echo "$REQUIREMENTS" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.storyIds.join(','))")
ROUTES=$(echo "$REQUIREMENTS" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.routes.join(','))")
SELECTORS=$(echo "$REQUIREMENTS" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.selectors.join(','))")
DSL_STEPS=$(echo "$REQUIREMENTS" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.dslSteps.join(','))")
CUSTOM_STEPS=$(echo "$REQUIREMENTS" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.customSteps.join(','))")
TASKS=$(echo "$REQUIREMENTS" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.tasks.join(','))")

echo "STORY_IDS=$STORY_IDS"
echo "ROUTES_NEEDED=$ROUTES"
echo "SELECTORS_NEEDED=$SELECTORS"
echo "DSL_STEPS_USED=$DSL_STEPS"
echo "CUSTOM_STEPS_NEEDED=$CUSTOM_STEPS"
echo "TASKS_NEEDED=$TASKS"

# Cross-reference against project source
SRC_DIR="$ROOT/src"

# Check routes — look for page/route files matching visit paths
ROUTES_EXIST=""
ROUTES_MISSING=""
IFS=',' read -ra ROUTE_ARR <<< "$ROUTES"
for route in "${ROUTE_ARR[@]}"; do
  [[ -z "$route" ]] && continue
  found=false

  # Normalize route to potential file paths
  # /dashboard → src/pages/dashboard.astro, src/pages/dashboard/index.astro, src/app/dashboard/page.tsx, etc.
  clean="${route#/}"
  clean="${clean:-index}"

  # Search for matching page files across frameworks
  if find "$SRC_DIR" -type f \( \
    -name "${clean}.astro" -o -name "${clean}.tsx" -o -name "${clean}.jsx" -o \
    -name "${clean}.vue" -o -name "${clean}.svelte" -o \
    -path "*/${clean}/index.*" -o -path "*/${clean}/page.*" -o \
    -path "*/pages/${clean}.*" -o -path "*/app/${clean}/page.*" \
  \) 2>/dev/null | grep -q .; then
    found=true
  fi

  if $found; then
    ROUTES_EXIST="${ROUTES_EXIST:+$ROUTES_EXIST,}$route"
  else
    ROUTES_MISSING="${ROUTES_MISSING:+$ROUTES_MISSING,}$route"
  fi
done
echo "ROUTES_EXIST=$ROUTES_EXIST"
echo "ROUTES_MISSING=$ROUTES_MISSING"

# Check selectors — grep source for data-test attributes
SELECTORS_EXIST=""
SELECTORS_MISSING=""
IFS=',' read -ra SEL_ARR <<< "$SELECTORS"
for sel in "${SEL_ARR[@]}"; do
  [[ -z "$sel" ]] && continue

  # Extract data-test value from selector like [data-test=hero-tagline]
  dt_val=$(echo "$sel" | grep -oE 'data-test[=~|^$*]?[^]]*' | head -1 || true)

  if [[ -n "$dt_val" ]] && [[ -d "$SRC_DIR" ]]; then
    # Search for the attribute in source files
    if grep -rq "$dt_val" "$SRC_DIR" 2>/dev/null; then
      SELECTORS_EXIST="${SELECTORS_EXIST:+$SELECTORS_EXIST,}$sel"
    else
      SELECTORS_MISSING="${SELECTORS_MISSING:+$SELECTORS_MISSING,}$sel"
    fi
  else
    SELECTORS_MISSING="${SELECTORS_MISSING:+$SELECTORS_MISSING,}$sel"
  fi
done
echo "SELECTORS_EXIST=$SELECTORS_EXIST"
echo "SELECTORS_MISSING=$SELECTORS_MISSING"

# Check custom DSL steps — look in steps.ts
STEPS_FILE=$(find "$ROOT/cypress" -name "steps.ts" 2>/dev/null | head -1)
CUSTOM_STEPS_EXIST=""
CUSTOM_STEPS_MISSING=""
IFS=',' read -ra CSTEP_ARR <<< "$CUSTOM_STEPS"
for step in "${CSTEP_ARR[@]}"; do
  [[ -z "$step" ]] && continue
  if [[ -n "$STEPS_FILE" ]] && grep -q "'$step'" "$STEPS_FILE" 2>/dev/null; then
    CUSTOM_STEPS_EXIST="${CUSTOM_STEPS_EXIST:+$CUSTOM_STEPS_EXIST,}$step"
  else
    CUSTOM_STEPS_MISSING="${CUSTOM_STEPS_MISSING:+$CUSTOM_STEPS_MISSING,}$step"
  fi
done
echo "CUSTOM_STEPS_EXIST=$CUSTOM_STEPS_EXIST"
echo "CUSTOM_STEPS_MISSING=$CUSTOM_STEPS_MISSING"

# Check Cypress tasks — look in cypress.config.ts
CONFIG_FILE=$(find "$ROOT" -maxdepth 1 -name "cypress.config.*" 2>/dev/null | head -1)
TASKS_EXIST=""
TASKS_MISSING=""
IFS=',' read -ra TASK_ARR <<< "$TASKS"
for task in "${TASK_ARR[@]}"; do
  [[ -z "$task" ]] && continue
  if [[ -n "$CONFIG_FILE" ]] && grep -q "'$task'" "$CONFIG_FILE" 2>/dev/null; then
    TASKS_EXIST="${TASKS_EXIST:+$TASKS_EXIST,}$task"
  else
    TASKS_MISSING="${TASKS_MISSING:+$TASKS_MISSING,}$task"
  fi
done
echo "TASKS_EXIST=$TASKS_EXIST"
echo "TASKS_MISSING=$TASKS_MISSING"

# Summary
echo ""
echo "--- PREFLIGHT SUMMARY ---"
TOTAL_SEL=$(echo "$SELECTORS" | tr ',' '\n' | grep -c . || echo 0)
EXIST_SEL=$(echo "$SELECTORS_EXIST" | tr ',' '\n' | grep -c . || echo 0)
MISS_SEL=$(echo "$SELECTORS_MISSING" | tr ',' '\n' | grep -c . || echo 0)
echo "Stories: $(echo "$STORY_IDS" | tr ',' '\n' | grep -c . || echo 0)"
echo "Routes: needed=$(echo "$ROUTES" | tr ',' '\n' | grep -c . || echo 0) exist=$(echo "$ROUTES_EXIST" | tr ',' '\n' | grep -c . || echo 0) missing=$(echo "$ROUTES_MISSING" | tr ',' '\n' | grep -c . || echo 0)"
echo "Selectors: needed=$TOTAL_SEL exist=$EXIST_SEL missing=$MISS_SEL"
echo "Custom DSL steps: $(echo "$CUSTOM_STEPS" | tr ',' '\n' | grep -c . || echo 0) needed"
echo "Cypress tasks: $(echo "$TASKS" | tr ',' '\n' | grep -c . || echo 0) needed"
