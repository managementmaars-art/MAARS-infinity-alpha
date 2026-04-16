#!/usr/bin/env bash
# scan-project.sh — Detect framework, source dirs, config files (brownfield)
# Usage: bash scan-project.sh [project-root]
# Output: structured text with FRAMEWORK, SOURCE_DIRS, CONFIG_FILES sections

set -euo pipefail

ROOT="${1:-.}"

# Detect framework from package.json
FRAMEWORK="none"
if [[ -f "$ROOT/package.json" ]]; then
  DEPS=$(cat "$ROOT/package.json")
  if echo "$DEPS" | grep -q '"next"'; then FRAMEWORK="Next.js"
  elif echo "$DEPS" | grep -q '"nuxt"'; then FRAMEWORK="Nuxt"
  elif echo "$DEPS" | grep -q '"astro"'; then FRAMEWORK="Astro"
  elif echo "$DEPS" | grep -q '"@angular/core"'; then FRAMEWORK="Angular"
  elif echo "$DEPS" | grep -q '"svelte"'; then FRAMEWORK="Svelte"
  elif echo "$DEPS" | grep -q '"react"'; then FRAMEWORK="React"
  elif echo "$DEPS" | grep -q '"vue"'; then FRAMEWORK="Vue"
  elif echo "$DEPS" | grep -q '"express"'; then FRAMEWORK="Express"
  elif echo "$DEPS" | grep -q '"fastify"'; then FRAMEWORK="Fastify"
  elif echo "$DEPS" | grep -q '"hono"'; then FRAMEWORK="Hono"
  fi
fi
echo "FRAMEWORK=$FRAMEWORK"

# Detect source directories
echo "SOURCE_DIRS="
for dir in src lib app server client components pages routes api utils helpers models services; do
  if [[ -d "$ROOT/$dir" ]]; then
    echo "  $dir/"
  fi
done

# Detect config files
echo "CONFIG_FILES="
for f in package.json tsconfig.json vite.config.ts vite.config.js next.config.js next.config.ts next.config.mjs nuxt.config.ts nuxt.config.js angular.json svelte.config.js tailwind.config.ts tailwind.config.js postcss.config.js .env.example docker-compose.yml Dockerfile; do
  if [[ -f "$ROOT/$f" ]]; then
    echo "  $f"
  fi
done

# Detect if project has any code
FILE_COUNT=$(find "$ROOT" -maxdepth 3 -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.vue" -o -name "*.svelte" 2>/dev/null | head -100 | wc -l | tr -d ' ')
echo "CODE_FILE_COUNT=$FILE_COUNT"

if [[ "$FILE_COUNT" -gt 0 ]]; then
  echo "HAS_CODE=true"
else
  echo "HAS_CODE=false"
fi
