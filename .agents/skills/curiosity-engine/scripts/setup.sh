#!/usr/bin/env bash
set -e

echo "=== Curiosity Engine Setup ==="

# Resolve paths. SCRIPT_DIR is the installed skill's scripts/ directory;
# TEMPLATE_DIR is its sibling template/ — the single source of truth for
# the wiki skeleton copied into each new workspace.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/template"

# Create working directory structure
mkdir -p vault wiki/{sources,entities,concepts,analyses}
touch vault/.gitkeep

# Copy templates into the working directory if not already present
for f in schema.md index.md log.md; do
    if [ ! -f "wiki/$f" ]; then
        cp "$TEMPLATE_DIR/$f" "wiki/$f"
        echo "  Created wiki/$f"
    fi
done

if [ ! -f CLAUDE.md ]; then
    cp "$TEMPLATE_DIR/CLAUDE.md" CLAUDE.md
    echo "  Created CLAUDE.md"
fi

# Generate Claude Code settings inline (avoids the npx/skills installer
# dropping hidden template/.claude/ directories during install). Auto-allows:
#   - git commands scoped via `git -C wiki <cmd>` AND `git -C */wiki <cmd>`
#     (the second form covers subagents that construct absolute paths to
#     the wiki directory; both still scope to a directory literally named
#     "wiki", which is the skill's convention)
#   - python3 invocations of skill scripts at this exact absolute path
#   - the evolve_guard.sh helper
#   - date (pure computation, needed for ISO timestamps in log.md)
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Regenerate if the file is missing OR empty OR not valid JSON. An earlier
# version of this script could leave behind a 0-byte settings.json when
# sed failed on a missing template, and the original `[ ! -f ]` guard would
# then skip regeneration forever. Belt-and-braces: treat any non-parseable
# existing file as a "needs regeneration" case.
regenerate_settings=0
if [ ! -s .claude/settings.json ]; then
    regenerate_settings=1
elif ! python3 -c "import json, sys; json.load(open('.claude/settings.json'))" >/dev/null 2>&1; then
    regenerate_settings=1
fi

if [ "$regenerate_settings" = "1" ]; then
    mkdir -p .claude
    cat > .claude/settings.json <<EOF
{
  "permissions": {
    "allow": [
      "Bash(git -C wiki add:*)",
      "Bash(git -C wiki commit:*)",
      "Bash(git -C wiki status:*)",
      "Bash(git -C wiki log:*)",
      "Bash(git -C wiki diff:*)",
      "Bash(git -C wiki revert:*)",
      "Bash(git -C wiki checkout:*)",
      "Bash(git -C wiki rev-parse:*)",
      "Bash(git -C wiki show:*)",
      "Bash(git -C */wiki add:*)",
      "Bash(git -C */wiki commit:*)",
      "Bash(git -C */wiki status:*)",
      "Bash(git -C */wiki log:*)",
      "Bash(git -C */wiki diff:*)",
      "Bash(git -C */wiki revert:*)",
      "Bash(git -C */wiki checkout:*)",
      "Bash(git -C */wiki rev-parse:*)",
      "Bash(git -C */wiki show:*)",
      "Bash(python3 $SKILL_ROOT/scripts/lint_scores.py:*)",
      "Bash(python3 $SKILL_ROOT/scripts/compress.py:*)",
      "Bash(python3 $SKILL_ROOT/scripts/vault_search.py:*)",
      "Bash(python3 $SKILL_ROOT/scripts/vault_index.py:*)",
      "Bash(python3 $SKILL_ROOT/scripts/local_ingest.py:*)",
      "Bash(python3 $SKILL_ROOT/scripts/scrub_check.py:*)",
      "Bash(python3 $SKILL_ROOT/scripts/score_diff.py:*)",
      "Bash(python3 $SKILL_ROOT/scripts/sweep.py:*)",
      "Bash(python3 $SKILL_ROOT/scripts/epoch_summary.py:*)",
      "Bash(bash $SKILL_ROOT/scripts/evolve_guard.sh:*)",
      "Bash(date:*)"
    ]
  }
}
EOF
    echo "  Created .claude/settings.json (auto-allow git -C wiki + skill scripts)"
fi

# Initialize wiki as its own git repo
if [ ! -d wiki/.git ]; then
    (cd wiki && git init -q && git add -A && git commit -q -m "init: curiosity engine wiki")
    echo "  Initialized wiki git repo"
fi

# Initialize vault FTS5 index
python3 "$SCRIPT_DIR/vault_index.py" --init

echo ""
echo "Ready. Open Claude Code here and try:"
echo '  > add ~/some-paper.pdf to the vault'
echo '  > what do I know about X?'
echo '  > run the curator for 10 cycles'
