#!/usr/bin/env bash
# bootstrap-init.sh — Create RootSpec project structure and prerequisites
#
# Usage: bash bootstrap-init.sh <project-root> <shared-dir>
#
# Creates: rootspec/ dir, framework files, prerequisites, .rootspec.json
# Skips files that already exist (safe to re-run).
#
# Called by:
#   - orchestrator/src/phases/init.ts (programmatic init)
#   - rs-init skill (interactive init, after scanning)

set -euo pipefail

ROOT="${1:?Usage: bootstrap-init.sh <project-root> <shared-dir>}"
SHARED="${2:?Usage: bootstrap-init.sh <project-root> <shared-dir>}"

# Resolve shared dir — handle both installed skills and framework repo paths
if [[ ! -d "$SHARED" ]]; then
  echo "ERROR: Shared directory not found: $SHARED" >&2
  exit 1
fi

# Read framework version from 00.FRAMEWORK.md
VERSION="0.0.0"
if [[ -f "$SHARED/00.FRAMEWORK.md" ]]; then
  VERSION=$(grep -oE '\*\*Version:\*\* [^ ]+' "$SHARED/00.FRAMEWORK.md" | awk '{print $2}' || echo "0.0.0")
fi

echo "Bootstrapping RootSpec v${VERSION} in ${ROOT}"

# --- Step 2: Spec directory and base files ---

mkdir -p "$ROOT/rootspec"

# 2.1 Copy 00.AXIOMS.md
if [[ -f "$SHARED/00.AXIOMS.md" ]]; then
  cp "$SHARED/00.AXIOMS.md" "$ROOT/rootspec/00.AXIOMS.md"
else
  echo "WARNING: 00.AXIOMS.md not found in $SHARED" >&2
fi

# 2.2 Copy 00.FRAMEWORK.md
if [[ -f "$SHARED/00.FRAMEWORK.md" ]]; then
  cp "$SHARED/00.FRAMEWORK.md" "$ROOT/rootspec/00.FRAMEWORK.md"
else
  echo "WARNING: 00.FRAMEWORK.md not found in $SHARED" >&2
fi

# 2.3 Create spec-status.json (skip if exists)
if [[ ! -f "$ROOT/rootspec/spec-status.json" ]]; then
  cat > "$ROOT/rootspec/spec-status.json" <<EOJSON
{
  "hash": null,
  "validatedAt": null,
  "valid": false,
  "version": "${VERSION}"
}
EOJSON
fi

# 2.4 Create tests-status.json (skip if exists)
if [[ ! -f "$ROOT/rootspec/tests-status.json" ]]; then
  cat > "$ROOT/rootspec/tests-status.json" <<'EOJSON'
{
  "lastRun": null,
  "stories": {}
}
EOJSON
fi

# --- Step 3: Prerequisites ---

mkdir -p "$ROOT/scripts"

# 3.1 Dev server — copy bundled template
if [[ ! -f "$ROOT/scripts/dev.sh" ]]; then
  if [[ -f "$SHARED/scripts/dev.sh" ]]; then
    cp "$SHARED/scripts/dev.sh" "$ROOT/scripts/dev.sh"
    chmod +x "$ROOT/scripts/dev.sh"
    echo "  Created scripts/dev.sh"
  else
    echo "  WARNING: Bundled dev.sh not found" >&2
  fi
fi

# 3.2 Validation script (test.sh)
if [[ ! -f "$ROOT/scripts/test.sh" ]]; then
  cat > "$ROOT/scripts/test.sh" <<'EOSH'
#!/usr/bin/env bash
# Test runner — starts dev server, runs Cypress, stops server
set -euo pipefail
./scripts/dev.sh start
npx cypress run --config-file cypress.config.ts 2>&1
EXIT_CODE=$?
./scripts/dev.sh stop
exit $EXIT_CODE
EOSH
  chmod +x "$ROOT/scripts/test.sh"
  echo "  Created scripts/test.sh"
fi

# 3.3 Pre-commit hook
mkdir -p "$ROOT/.githooks"
if [[ ! -f "$ROOT/.githooks/pre-commit" ]]; then
  cat > "$ROOT/.githooks/pre-commit" <<'EOSH'
#!/usr/bin/env bash
# Pre-commit hook — validate spec and run tests
set -euo pipefail

# Validate spec if spec files changed
if git diff --cached --name-only | grep -q '^rootspec/'; then
  echo "Spec files changed — validating..."
  if [ -x "./scripts/validate-spec.sh" ]; then
    ./scripts/validate-spec.sh
  fi
fi

# Run tests if source files changed
if git diff --cached --name-only | grep -qE '^(src/|public/|cypress/)'; then
  echo "Source files changed — running tests..."
  if [ -x "./scripts/test.sh" ]; then
    ./scripts/test.sh
  fi
fi
EOSH
  chmod +x "$ROOT/.githooks/pre-commit"
  echo "  Created .githooks/pre-commit"
fi

# 3.4 Release script
if [[ ! -f "$ROOT/scripts/release.sh" ]]; then
  cat > "$ROOT/scripts/release.sh" <<'EOSH'
#!/usr/bin/env bash
# Simple release — tag and push
set -euo pipefail

VERSION=${1:?Usage: ./scripts/release.sh <version>}

echo "Releasing v${VERSION}..."
git tag -a "v${VERSION}" -m "Version ${VERSION}"
git push origin "v${VERSION}"
echo "Released v${VERSION}"
EOSH
  chmod +x "$ROOT/scripts/release.sh"
  echo "  Created scripts/release.sh"
fi

# 3.5 Cypress reporter — copy bundled rootspec-reporter.ts
if [[ -f "$SHARED/cypress/rootspec-reporter.ts" ]]; then
  mkdir -p "$ROOT/cypress/support"
  cp "$SHARED/cypress/rootspec-reporter.ts" "$ROOT/cypress/support/rootspec-reporter.ts"
fi

# 3.6 .gitignore entries
GITIGNORE_ENTRIES=("node_modules/" "dist/" ".dev-server.pid" ".dev-server.log")
if [[ -f "$ROOT/.gitignore" ]]; then
  for entry in "${GITIGNORE_ENTRIES[@]}"; do
    if ! grep -qF "$entry" "$ROOT/.gitignore"; then
      echo "$entry" >> "$ROOT/.gitignore"
    fi
  done
else
  printf '%s\n' "${GITIGNORE_ENTRIES[@]}" > "$ROOT/.gitignore"
fi

# --- Step 4: Write .rootspec.json ---

cat > "$ROOT/.rootspec.json" <<EOJSON
{
  "version": "${VERSION}",
  "specDirectory": "rootspec",
  "prerequisites": {
    "devServer": "./scripts/dev.sh",
    "preCommitHook": ".githooks/pre-commit",
    "releaseScript": "./scripts/release.sh",
    "validationScript": "./scripts/test.sh"
  }
}
EOJSON

# --- Package.json ---

if [[ ! -f "$ROOT/package.json" ]]; then
  cat > "$ROOT/package.json" <<'EOJSON'
{
  "name": "rootspec-project",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "./scripts/dev.sh start",
    "dev:start": "./scripts/dev.sh start",
    "dev:stop": "./scripts/dev.sh stop",
    "dev:restart": "./scripts/dev.sh restart",
    "build": "echo 'No build configured yet'",
    "test": "./scripts/test.sh"
  }
}
EOJSON
  echo "  Created package.json"
fi

echo "Bootstrap complete (v${VERSION})"
