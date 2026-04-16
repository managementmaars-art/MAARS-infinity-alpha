#!/usr/bin/env bash
# init-conventions.sh — Extract conventions from project config files
# Usage: bash init-conventions.sh <project-root> [spec-dir]
#
# Creates rootspec/CONVENTIONS/technical.md and visual.md by scanning
# package.json, config files, and source code.
#
# Exits silently if CONVENTIONS/ already exists (never overwrites).

set -euo pipefail

ROOT="${1:-.}"
SPEC_DIR="${2:-rootspec}"
CONV_DIR="$ROOT/$SPEC_DIR/CONVENTIONS"

if [[ -d "$CONV_DIR" ]]; then
  echo "CONVENTIONS/ already exists — skipping"
  exit 0
fi

mkdir -p "$CONV_DIR"

# --- Helpers ---
has_dep() {
  local dep="$1"
  [[ -f "$ROOT/package.json" ]] && grep -q "\"$dep\"" "$ROOT/package.json" 2>/dev/null
}

dep_version() {
  local dep="$1"
  [[ -f "$ROOT/package.json" ]] && grep -oE "\"$dep\": \"[^\"]+\"" "$ROOT/package.json" 2>/dev/null | head -1 | sed 's/.*": "//' | sed 's/"//' | sed 's/[\^~]//'
}

# --- Detect Stack ---
FRAMEWORK="unknown"
FRAMEWORK_VER=""
if has_dep "next"; then FRAMEWORK="Next.js"; FRAMEWORK_VER=$(dep_version "next")
elif has_dep "nuxt"; then FRAMEWORK="Nuxt"; FRAMEWORK_VER=$(dep_version "nuxt")
elif has_dep "astro"; then FRAMEWORK="Astro"; FRAMEWORK_VER=$(dep_version "astro")
elif has_dep "@angular/core"; then FRAMEWORK="Angular"; FRAMEWORK_VER=$(dep_version "@angular/core")
elif has_dep "svelte"; then FRAMEWORK="SvelteKit"; FRAMEWORK_VER=$(dep_version "svelte")
elif has_dep "react"; then FRAMEWORK="React"; FRAMEWORK_VER=$(dep_version "react")
elif has_dep "vue"; then FRAMEWORK="Vue"; FRAMEWORK_VER=$(dep_version "vue")
fi

LANGUAGE="JavaScript"
if [[ -f "$ROOT/tsconfig.json" ]]; then
  LANGUAGE="TypeScript"
  if grep -q '"strict"' "$ROOT/tsconfig.json" 2>/dev/null; then
    LANGUAGE="TypeScript (strict mode)"
  fi
fi

STYLING=""
if has_dep "tailwindcss"; then STYLING="Tailwind CSS v$(dep_version "tailwindcss")"
elif has_dep "styled-components"; then STYLING="styled-components"
elif has_dep "@emotion/react"; then STYLING="Emotion"
elif has_dep "sass"; then STYLING="Sass/SCSS"
else
  # Check for CSS modules
  if find "$ROOT/src" -name "*.module.css" -o -name "*.module.scss" 2>/dev/null | head -1 | grep -q .; then
    STYLING="CSS Modules"
  fi
fi

# Key libraries (non-framework deps)
KEY_LIBS=""
for lib in "react" "react-dom" "@astrojs/react" "@astrojs/tailwind" "framer-motion" "zustand" "redux" "@tanstack/react-query" "swr" "prisma" "drizzle-orm" "zod" "trpc"; do
  if has_dep "$lib"; then
    ver=$(dep_version "$lib")
    if [[ -n "$KEY_LIBS" ]]; then KEY_LIBS+=", "; fi
    KEY_LIBS+="$lib${ver:+ $ver}"
  fi
done

# --- Detect Code Patterns ---
FILE_NAMING=""
if find "$ROOT/src" -name "*-*" -type f 2>/dev/null | head -1 | grep -q .; then
  FILE_NAMING="kebab-case"
elif find "$ROOT/src" -name "*[A-Z]*" -type f 2>/dev/null | head -1 | grep -q .; then
  FILE_NAMING="PascalCase for components"
fi

COMPONENT_STYLE=""
if find "$ROOT/src" -name "*.tsx" -o -name "*.jsx" 2>/dev/null | head -3 | xargs grep -l "function " 2>/dev/null | head -1 | grep -q .; then
  COMPONENT_STYLE="Function components"
fi

EXPORTS=""
DEFAULT_COUNT=$(find "$ROOT/src" \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) 2>/dev/null | head -20 | xargs grep -l "export default" 2>/dev/null | wc -l | tr -d ' ')
NAMED_COUNT=$(find "$ROOT/src" \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) 2>/dev/null | head -20 | xargs grep -l "export {" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$DEFAULT_COUNT" -gt "$NAMED_COUNT" ]]; then
  EXPORTS="Default exports"
elif [[ "$NAMED_COUNT" -gt 0 ]]; then
  EXPORTS="Named exports"
fi

# --- Detect Testing ---
E2E_FRAMEWORK=""
if has_dep "cypress"; then E2E_FRAMEWORK="Cypress"
elif has_dep "playwright"; then E2E_FRAMEWORK="Playwright"
fi

UNIT_FRAMEWORK=""
if has_dep "vitest"; then UNIT_FRAMEWORK="Vitest"
elif has_dep "jest"; then UNIT_FRAMEWORK="Jest"
fi

# --- Detect Routing ---
ROUTING=""
if [[ "$FRAMEWORK" == "Next.js" ]] || [[ "$FRAMEWORK" == "Nuxt" ]] || [[ "$FRAMEWORK" == "Astro" ]] || [[ "$FRAMEWORK" == "SvelteKit" ]]; then
  ROUTING="File-based ($FRAMEWORK)"
elif has_dep "react-router" || has_dep "react-router-dom"; then
  ROUTING="react-router"
fi

# --- Detect Visual ---
COMPONENT_LIB=""
for lib in "shadcn" "@shadcn/ui" "@radix-ui/react-dialog" "@mui/material" "@chakra-ui/react" "@mantine/core"; do
  if has_dep "$lib"; then
    case "$lib" in
      shadcn|@shadcn/ui) COMPONENT_LIB="shadcn/ui" ;;
      @radix-ui/*) COMPONENT_LIB="Radix UI" ;;
      @mui/*) COMPONENT_LIB="Material UI" ;;
      @chakra-ui/*) COMPONENT_LIB="Chakra UI" ;;
      @mantine/*) COMPONENT_LIB="Mantine" ;;
    esac
    break
  fi
done

ICON_LIB=""
for lib in "lucide-react" "@heroicons/react" "react-icons" "@phosphor-icons/react"; do
  if has_dep "$lib"; then
    case "$lib" in
      lucide-react) ICON_LIB="Lucide" ;;
      @heroicons/*) ICON_LIB="Heroicons" ;;
      react-icons) ICON_LIB="react-icons" ;;
      @phosphor-icons/*) ICON_LIB="Phosphor" ;;
    esac
    break
  fi
done

# --- Write technical.md ---
{
  echo "# Technical Conventions"
  echo ""
  echo "## Stack"
  [[ "$FRAMEWORK" != "unknown" ]] && echo "- **Framework:** $FRAMEWORK${FRAMEWORK_VER:+ $FRAMEWORK_VER}"
  echo "- **Language:** $LANGUAGE"
  [[ -n "$STYLING" ]] && echo "- **Styling:** $STYLING"
  [[ -n "$KEY_LIBS" ]] && echo "- **Key libraries:** $KEY_LIBS"

  if [[ -n "$FILE_NAMING" ]] || [[ -n "$COMPONENT_STYLE" ]] || [[ -n "$EXPORTS" ]]; then
    echo ""
    echo "## Code Patterns"
    [[ -n "$FILE_NAMING" ]] && echo "- **File naming:** $FILE_NAMING"
    [[ -n "$COMPONENT_STYLE" ]] && echo "- **Component style:** $COMPONENT_STYLE"
    [[ -n "$EXPORTS" ]] && echo "- **Exports:** $EXPORTS"
  fi

  if [[ -n "$ROUTING" ]]; then
    echo ""
    echo "## Routing"
    echo "- **Approach:** $ROUTING"
  fi

  if [[ -n "$E2E_FRAMEWORK" ]] || [[ -n "$UNIT_FRAMEWORK" ]]; then
    echo ""
    echo "## Testing"
    [[ -n "$UNIT_FRAMEWORK" ]] && echo "- **Unit:** $UNIT_FRAMEWORK"
    [[ -n "$E2E_FRAMEWORK" ]] && echo "- **E2E:** $E2E_FRAMEWORK"
  fi
} > "$CONV_DIR/technical.md"

# --- Write visual.md ---
{
  echo "# Visual Conventions"

  if [[ -n "$COMPONENT_LIB" ]]; then
    echo ""
    echo "## Component Library"
    echo "- **Base:** $COMPONENT_LIB"
    [[ -n "$STYLING" ]] && echo "- **Customization:** $STYLING classes"
  fi

  if [[ -n "$STYLING" ]] && [[ "$STYLING" == Tailwind* ]]; then
    echo ""
    echo "## Spacing"
    echo "- **Base unit:** Tailwind default (4px)"
    echo "- **Scale:** Tailwind spacing utilities"
    echo ""
    echo "## Responsive"
    echo "- **Approach:** Mobile-first"
    echo "- **Breakpoints:** Tailwind defaults (sm/md/lg/xl/2xl)"
  fi

  if [[ -n "$ICON_LIB" ]]; then
    echo ""
    echo "## Icons"
    echo "- **Library:** $ICON_LIB"
  fi
} > "$CONV_DIR/visual.md"

echo "Created $CONV_DIR/technical.md and $CONV_DIR/visual.md"
echo "Review and fill in gaps (colors, typography, motion, etc.)"
