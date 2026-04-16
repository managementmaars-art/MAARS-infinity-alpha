#!/usr/bin/env bash
# scaffold-cypress.sh — Create all Cypress infrastructure in one call
# Usage: bash scaffold-cypress.sh <project-root> <shared-dir>
# Output: reports what was created vs skipped
#
# Only creates files that don't already exist (never overwrites).
# After running, the agent only needs to customize task bodies and extend DSL.

set -euo pipefail

ROOT="${1:-.}"
SHARED_DIR="${2:-$(cd "$(dirname "$0")/.." && pwd)}"
CREATED=()
SKIPPED=()

write_if_missing() {
  local filepath="$1"
  local content="$2"
  local fullpath="$ROOT/$filepath"

  if [[ -f "$fullpath" ]]; then
    SKIPPED+=("$filepath")
    return
  fi

  mkdir -p "$(dirname "$fullpath")"
  printf '%s' "$content" > "$fullpath"
  CREATED+=("$filepath")
}

# --- Detect baseUrl from project config ---
BASE_URL="http://localhost:3000"
if [[ -f "$ROOT/astro.config.mjs" ]] || [[ -f "$ROOT/astro.config.ts" ]]; then
  BASE_URL="http://localhost:4321"
elif [[ -f "$ROOT/vite.config.ts" ]] || [[ -f "$ROOT/vite.config.js" ]]; then
  BASE_URL="http://localhost:5173"
elif [[ -f "$ROOT/next.config.js" ]] || [[ -f "$ROOT/next.config.ts" ]] || [[ -f "$ROOT/next.config.mjs" ]]; then
  BASE_URL="http://localhost:3000"
elif [[ -f "$ROOT/nuxt.config.ts" ]]; then
  BASE_URL="http://localhost:3000"
fi

# --- 1. cypress.config.ts ---
write_if_missing "cypress.config.ts" "import { defineConfig } from 'cypress';
import { rootspecReporter } from './cypress/support/rootspec-reporter';

export default defineConfig({
  e2e: {
    baseUrl: '${BASE_URL}',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.ts',
    video: false,
    screenshotOnRunFailure: false,
    defaultCommandTimeout: 10000,
    setupNodeEvents(on, config) {
      rootspecReporter(on, { statusPath: 'rootspec/tests-status.json' });

      // Placeholder tasks — customize bodies as needed
      on('task', {
        loginAs(role: string) { return null; },
        seedItem(data: Record<string, unknown>) { return null; },
        resetDatabase() { return null; },
        log(message: string) { console.log(message); return null; },
      });

      return config;
    },
  },
});
"

# --- 2. cypress/support/e2e.ts ---
# The afterEach screenshot hook is critical for /rs-review.
# If the impl agent creates e2e.ts before scaffold runs, the hook is missing.
# Strategy: write full file if missing, or append hook if file exists without it.
# The screenshot hook content — written via heredoc to avoid quoting hell
SCREENSHOT_HOOK_FILE="$ROOT/cypress/support/screenshot-hook.ts"

write_e2e_with_hook() {
  local fullpath="$ROOT/cypress/support/e2e.ts"
  if [[ -f "$fullpath" ]]; then
    SKIPPED+=("cypress/support/e2e.ts")
  else
    mkdir -p "$(dirname "$fullpath")"
    cat > "$fullpath" <<'EOTS'
// Global test setup
beforeEach(() => {
  cy.clearLocalStorage();
  cy.clearCookies();
});
EOTS
    CREATED+=("cypress/support/e2e.ts")
  fi

  # Always ensure screenshot hook import is present
  if ! grep -q "screenshot-hook" "$fullpath" 2>/dev/null; then
    printf '\nimport "./screenshot-hook";\n' >> "$fullpath"
  fi
}

# Write the screenshot hook as a separate file — immune to e2e.ts being
# overwritten by the impl agent. Always overwrite to pick up changes.
write_screenshot_hook() {
  mkdir -p "$(dirname "$SCREENSHOT_HOOK_FILE")"
  cat > "$SCREENSHOT_HOOK_FILE" <<'EOTS'
// Capture a full-page screenshot after each passing criterion.
// Screenshots land at cypress/screenshots/<spec>/US-101--AC-101-1.png
// Used by /rs-review for visual quality inspection.
afterEach(function () {
  if (this.currentTest?.state === 'passed') {
    const titles: string[] = (this.currentTest as any).titlePath?.() ?? [];
    const joined = titles.join(' ');
    const storyMatch = joined.match(/US-\d+/);
    const critMatch = joined.match(/AC-\d+-\d+/);
    if (storyMatch) {
      const name = critMatch
        ? `${storyMatch[0]}--${critMatch[0]}`
        : storyMatch[0];
      cy.screenshot(name, { capture: 'fullPage' });
    }
  }
});
EOTS
}

write_e2e_with_hook
write_screenshot_hook

# --- 3. cypress/support/steps.ts ---
write_if_missing "cypress/support/steps.ts" "import type { Step } from './schema';

export function runSetupSteps(steps: Step[]) {
  for (const s of steps ?? []) {
    if ('visit' in s) cy.visit(s.visit);
    else if ('click' in s) cy.get(s.click.selector).first().click();
    else if ('fill' in s) cy.get(s.fill.selector).clear().type(s.fill.value);
    else if ('loginAs' in s) cy.task('loginAs', s.loginAs);
    else if ('seedItem' in s) cy.task('seedItem', s.seedItem);
  }
}

export function runAssertionSteps(steps: Step[]) {
  for (const s of steps ?? []) {
    if ('shouldContain' in s) {
      cy.get(s.shouldContain.selector).should('contain', s.shouldContain.text);
    }
    else if ('shouldExist' in s) {
      cy.get(s.shouldExist.selector).should('exist');
    }
  }
}
"

# --- 4. cypress/support/schema.ts ---
write_if_missing "cypress/support/schema.ts" "import { z } from 'zod';

const StepSchema = z.union([
  z.object({ visit: z.string() }),
  z.object({ click: z.object({ selector: z.string() }) }),
  z.object({ fill: z.object({ selector: z.string(), value: z.string() }) }),
  z.object({ loginAs: z.string() }),
  z.object({ seedItem: z.record(z.unknown()) }),
  z.object({ shouldContain: z.object({ selector: z.string(), text: z.string() }) }),
  z.object({ shouldExist: z.object({ selector: z.string() }) }),
]);

const AcceptanceCriterionSchema = z.object({
  id: z.string(),
  title: z.string(),
  narrative: z.string().optional(),
  skip: z.boolean().optional(),
  only: z.boolean().optional(),
  given: z.array(StepSchema).optional(),
  when: z.array(StepSchema).optional(),
  then: z.array(StepSchema).optional(),
});

const UserStorySchema = z.object({
  id: z.string(),
  title: z.string(),
  requirement_id: z.string().optional(),
  skip: z.boolean().optional(),
  only: z.boolean().optional(),
  acceptance_criteria: z.array(AcceptanceCriterionSchema),
});

export { StepSchema, AcceptanceCriterionSchema, UserStorySchema };
export type Step = z.infer<typeof StepSchema>;
export type AcceptanceCriterion = z.infer<typeof AcceptanceCriterionSchema>;
export type UserStory = z.infer<typeof UserStorySchema>;
"

# --- 5. cypress/support/rootspec-reporter.ts ---
REPORTER_SRC="$SHARED_DIR/cypress/rootspec-reporter.ts"
REPORTER_DEST="$ROOT/cypress/support/rootspec-reporter.ts"
if [[ -f "$REPORTER_DEST" ]]; then
  SKIPPED+=("cypress/support/rootspec-reporter.ts")
else
  mkdir -p "$(dirname "$REPORTER_DEST")"
  cp "$REPORTER_SRC" "$REPORTER_DEST"
  CREATED+=("cypress/support/rootspec-reporter.ts")
fi

# --- 6. cypress/tsconfig.json ---
write_if_missing "cypress/tsconfig.json" '{
  "compilerOptions": {
    "target": "es5",
    "lib": ["es5", "dom", "es2015.promise"],
    "types": ["cypress"]
  },
  "include": ["**/*.ts"]
}
'

# --- 7. Check and install dependencies ---
DEPS_NEEDED=()
if [[ -f "$ROOT/package.json" ]]; then
  for dep in cypress js-yaml zod; do
    if ! grep -q "\"$dep\"" "$ROOT/package.json" 2>/dev/null; then
      DEPS_NEEDED+=("$dep")
    fi
  done
fi

if [[ ${#DEPS_NEEDED[@]} -gt 0 ]]; then
  echo "Installing missing dependencies: ${DEPS_NEEDED[*]}"
  (cd "$ROOT" && npm install --save-dev "${DEPS_NEEDED[@]}" 2>&1 | tail -3)
fi

# --- Report ---
echo ""
echo "=== Scaffold Report ==="
if [[ ${#CREATED[@]} -gt 0 ]]; then
  echo "CREATED:"
  for f in "${CREATED[@]}"; do echo "  $f"; done
fi
if [[ ${#SKIPPED[@]} -gt 0 ]]; then
  echo "SKIPPED (already exist):"
  for f in "${SKIPPED[@]}"; do echo "  $f"; done
fi
if [[ ${#DEPS_NEEDED[@]} -gt 0 ]]; then
  echo "INSTALLED: ${DEPS_NEEDED[*]}"
fi
echo "=== Done ==="
