#!/usr/bin/env sh
# ServiceNow Agent Skills Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/aatrey882/servicenow-agent-skills/main/install.sh | sh
# Or locally: sh install.sh
set -e

SKILLS_DIR="${HOME}/.agents/skills"
REPO="https://github.com/aatrey882/servicenow-agent-skills"
SKILLS="sn-sdk-fluent sn-sdk-setup sn-scripting"

install_from_github() {
  # Used when piped from curl — cannot rely on local files
  if ! command -v git > /dev/null 2>&1; then
    echo "Error: git is required. Install git and retry."
    exit 1
  fi
  TMP=$(mktemp -d)
  trap 'rm -rf "$TMP"' EXIT
  echo "Cloning repository..."
  git clone --depth 1 "$REPO" "$TMP/repo" 2>/dev/null
  mkdir -p "$SKILLS_DIR"
  for skill in $SKILLS; do
    rm -rf "${SKILLS_DIR:?}/$skill"
    cp -r "$TMP/repo/$skill" "$SKILLS_DIR/"
    printf "  Installed: %s/%s\n" "$SKILLS_DIR" "$skill"
  done
}

install_from_local() {
  # Used when run directly — $0 points to the script file
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  mkdir -p "$SKILLS_DIR"
  for skill in $SKILLS; do
    rm -rf "${SKILLS_DIR:?}/$skill"
    cp -r "$SCRIPT_DIR/$skill" "$SKILLS_DIR/"
    printf "  Installed: %s/%s\n" "$SKILLS_DIR" "$skill"
  done
}

main() {
  echo ""
  echo "Installing ServiceNow Agent Skills..."
  echo ""

  # [ -t 0 ] is true when stdin is a terminal (local run)
  # When piped from curl, stdin is not a terminal
  if [ -t 0 ]; then
    install_from_local
  else
    install_from_github
  fi

  # Ensure agent-specific symlinks exist for Antigravity and Claude
  for agent_dir in "${HOME}/.gemini/antigravity/skills" "${HOME}/.claude/skills"; do
    if [ -d "$(dirname "$agent_dir")" ] || [ "$(basename "$(dirname "$agent_dir")")" = "antigravity" ]; then
      mkdir -p "$agent_dir"
      for skill in $SKILLS; do
        ln -sf "${SKILLS_DIR}/$skill" "$agent_dir/$skill"
      done
    fi
  done

  echo ""
  echo "Done. Skills installed to: $SKILLS_DIR"
  echo ""
  echo "Activation:"
  echo "  Antigravity: skills loaded automatically via ~/.gemini/antigravity/skills/"
  echo "  Claude Code: skills loaded automatically via ~/.claude/skills/"
  echo "  Codex / others: load automatically from ~/.agents/skills/"
  echo "  Cursor:      add SKILL.md content to .cursorrules or .cursor/rules/"
  echo "  VS Code Copilot: add SKILL.md content to .github/copilot-instructions.md"
  echo ""
}

main
