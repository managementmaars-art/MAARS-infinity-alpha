#!/usr/bin/env bash
set -euo pipefail
# =============================================================================
# Generic static site deploy to Cloudflare Workers via 1Password credentials.
#
# USAGE:
#   bash publish_static.sh
#
# CONFIGURATION (edit the 4 variables below, or set as environment variables):
#   PUBLISH_DIR   — directory containing wrangler.toml and files to deploy
#   OP_ITEM_ID    — 1Password item ID in Claude Automation vault
#   SITE_TITLE    — human-readable title for the generated index.html
#   PROJECT_URL   — GitHub/project URL for the footer link
#
# PHASES:
#   1. Fetch Cloudflare credentials from 1Password
#   2. Auto-generate index.html directory listing
#   3. Deploy via npx wrangler deploy
#
# ANTI-PATTERNS ADDRESSED:
#   CFW-02: Service account read-only (creds pre-provisioned)
#   CFW-03: --reveal for CONCEALED fields
#   CFW-04: SC2155 split export
#   CFW-05: tr for uppercase (bash 3 compat)
#   CFW-10: cd to wrangler.toml directory
#   CFW-12: LFS pointer detection
#   CFW-14: Process substitution for while-read
# =============================================================================

# ---- CONFIGURATION (EDIT THESE OR SET AS ENV VARS) ----
PUBLISH_DIR="${PUBLISH_DIR:-CHANGE_ME}"
OP_ITEM_ID="${OP_ITEM_ID:-CHANGE_ME}"
SITE_TITLE="${SITE_TITLE:-Published Findings}"
PROJECT_URL="${PROJECT_URL:-https://github.com/terrylica/CHANGE_ME}"
# ---- END CONFIGURATION ----

echo "=== Deploy Static Site to Cloudflare Workers ==="

# Pre-flight: verify wrangler.toml exists (CFW-10)
if [ ! -f "$PUBLISH_DIR/wrangler.toml" ]; then
  echo "ERROR: wrangler.toml not found in $PUBLISH_DIR"
  echo "Create it first. See: references/wrangler-setup.md"
  exit 1
fi

# =============================================================================
# Phase 1: Fetch credentials from 1Password (CFW-02, CFW-03, CFW-04)
# =============================================================================
echo "Phase 1: Fetching Cloudflare credentials from 1Password..."

# CFW-04: Split declaration and export to preserve exit codes (SC2155)
CLOUDFLARE_ACCOUNT_ID=$(OP_SERVICE_ACCOUNT_TOKEN="$(cat ~/.claude/.secrets/op-service-account-token)" \
  op item get "$OP_ITEM_ID" --vault "Claude Automation" --fields "account_id")
export CLOUDFLARE_ACCOUNT_ID

# CFW-03: --reveal is REQUIRED for CONCEALED fields
CLOUDFLARE_API_TOKEN=$(OP_SERVICE_ACCOUNT_TOKEN="$(cat ~/.claude/.secrets/op-service-account-token)" \
  op item get "$OP_ITEM_ID" --vault "Claude Automation" --fields "credential" --reveal)
export CLOUDFLARE_API_TOKEN

echo "  Account ID: ${CLOUDFLARE_ACCOUNT_ID:0:8}..."
echo "  Token loaded: yes"

# =============================================================================
# Phase 2: Auto-generate index.html (CFW-05, CFW-14, CFW-15)
# =============================================================================
echo "Phase 2: Generating index.html..."
INDEX="$PUBLISH_DIR/index.html"

cat > "$INDEX" << HEADER
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>${SITE_TITLE}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }
    h1 { border-bottom: 2px solid #0066cc; padding-bottom: 8px; }
    h2 { color: #555; margin-top: 32px; }
    a { color: #0066cc; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .file-list { list-style: none; padding: 0; }
    .file-list li { padding: 8px 0; border-bottom: 1px solid #eee; }
    .file-list li:last-child { border-bottom: none; }
    .meta { color: #888; font-size: 0.85em; margin-left: 12px; }
    footer { margin-top: 40px; color: #999; font-size: 0.8em; border-top: 1px solid #eee; padding-top: 12px; }
  </style>
</head>
<body>
  <h1>${SITE_TITLE}</h1>
  <p>Published static files.</p>
HEADER

# CFW-10: cd to publish directory (wrangler.toml location)
cd "$PUBLISH_DIR"
FOUND=0
CURRENT_GEN=""

# CFW-14: Process substitution to avoid subshell data loss
while IFS= read -r html_file; do
  [ -z "$html_file" ] && continue
  FOUND=$((FOUND + 1))

  # Extract generation directory and sub-path
  gen_dir=$(echo "$html_file" | cut -d'/' -f1)
  sub_path=$(echo "$html_file" | cut -d'/' -f2)

  # Start new section for each generation
  if [ "$gen_dir" != "$CURRENT_GEN" ]; then
    # Close previous list if open (fixes unclosed <ul> bug for multi-gen)
    if [ -n "$CURRENT_GEN" ]; then
      echo "  </ul>" >> "$INDEX"
    fi
    CURRENT_GEN="$gen_dir"
    # CFW-05: tr for uppercase (bash 3 compatible, not ${var^^})
    gen_upper=$(echo "$gen_dir" | tr '[:lower:]' '[:upper:]')
    echo "  <h2>$gen_upper</h2>" >> "$INDEX"
    echo "  <ul class=\"file-list\">" >> "$INDEX"
  fi

  # File size for display
  fsize=$(du -h "$html_file" | cut -f1 | tr -d ' ')
  fname=$(basename "$html_file" .html)

  echo "  <li><a href=\"$html_file\">$sub_path / $fname</a> <span class=\"meta\">($fsize)</span></li>" >> "$INDEX"

done < <(find . -path './gen*/*.html' -type f | sed 's|^\./||' | sort)

# Close the last list if any files found
if [ "$FOUND" -gt 0 ] && [ -n "$CURRENT_GEN" ]; then
  echo "  </ul>" >> "$INDEX"
fi

if [ "$FOUND" -eq 0 ]; then
  echo "  <p><em>No published files yet.</em></p>" >> "$INDEX"
fi

# Footer with timestamp
TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M UTC')
cat >> "$INDEX" << FOOTER
  <footer>
    Published: $TIMESTAMP | $FOUND files |
    <a href="${PROJECT_URL}">GitHub</a>
  </footer>
</body>
</html>
FOOTER

echo "  Generated index.html ($FOUND files)"

# =============================================================================
# Phase 3: Pre-flight checks + Deploy (CFW-12, CFW-10)
# =============================================================================

# CFW-12: Check for LFS pointers before deploying
LFS_POINTER_FOUND=0
while IFS= read -r html_file; do
  [ -z "$html_file" ] && continue
  first_line=$(head -1 "$html_file")
  if echo "$first_line" | grep -q "^version https://git-lfs.github.com"; then
    echo "WARNING: LFS pointer detected: $html_file"
    LFS_POINTER_FOUND=1
  fi
done < <(find . -path './gen*/*.html' -type f)

if [ "$LFS_POINTER_FOUND" -eq 1 ]; then
  echo ""
  echo "ERROR: LFS pointers found. Run 'git lfs pull' before deploying."
  echo "Aborting deploy."
  exit 1
fi

echo "Phase 3: Deploying to Cloudflare Workers..."
# CFW-10: Already in PUBLISH_DIR from Phase 2
npx wrangler deploy 2>&1

echo ""
echo "=== Deploy complete ==="
echo "Verify in browser (not curl — see CFW-08 re: macOS SSL)."
