**Skill**: [asciinema-streaming-backup](../SKILL.md)

# Account & Repository Detection

Scripts for detecting GitHub accounts and current repository context.

---

## Phase 1: GitHub Account Detection

Probe 5 sources to detect GitHub accounts:

| Source     | Command                                | What it finds                                     |
| ---------- | -------------------------------------- | ------------------------------------------------- |
| SSH config | `grep -A5 "Host github" ~/.ssh/config` | Match directives with IdentityFile                |
| SSH keys   | `ls ~/.ssh/id_ed25519_*`               | Account-named keys (e.g., `id_ed25519_terrylica`) |
| gh CLI     | `gh auth status`                       | Authenticated accounts                            |
| mise env   | `grep GH_ACCOUNT .mise.toml`           | GH_ACCOUNT variable                               |
| git config | `git config user.name`                 | Global git username                               |

### Detection Script

```bash
/usr/bin/env bash << 'DETECT_ACCOUNTS_EOF'
# detect-github-accounts.sh - Probe all sources for GitHub accounts
# Uses portable parallel arrays (works in bash 3.2+ and when wrapped for zsh)

ACCOUNT_NAMES=()
ACCOUNT_SOURCES=()

log() { echo "[detect] $*"; }

# Helper: add account with source (updates existing or appends new)
add_account() {
  local account="$1" source="$2"
  local idx
  for idx in "${!ACCOUNT_NAMES[@]}"; do
    if [[ "${ACCOUNT_NAMES[$idx]}" == "$account" ]]; then
      ACCOUNT_SOURCES[$idx]+="$source "
      return
    fi
  done
  ACCOUNT_NAMES+=("$account")
  ACCOUNT_SOURCES+=("$source ")
}

# 1. SSH config Match directives
if [[ -f ~/.ssh/config ]]; then
  while IFS= read -r line; do
    if [[ "$line" =~ IdentityFile.*id_ed25519_([a-zA-Z0-9_-]+) ]]; then
      add_account "${BASH_REMATCH[1]}" "ssh-config"
    fi
  done < ~/.ssh/config
fi

# 2. SSH key filenames
for keyfile in ~/.ssh/id_ed25519_*; do
  if [[ -f "$keyfile" && "$keyfile" != *.pub ]]; then
    account=$(basename "$keyfile" | sed 's/id_ed25519_//')
    add_account "$account" "ssh-key"
  fi
done

# 3. gh CLI authenticated accounts
if command -v gh &>/dev/null; then
  while IFS= read -r account; do
    [[ -n "$account" ]] && add_account "$account" "gh-cli"
  done < <(gh auth status 2>&1 | grep -oE 'Logged in to github.com account [a-zA-Z0-9_-]+' | awk '{print $NF}')
fi

# 4. mise env GH_ACCOUNT
if [[ -f .mise.toml ]]; then
  account=$(grep -E 'GH_ACCOUNT\s*=' .mise.toml 2>/dev/null | sed 's/.*=\s*"\([^"]*\)".*/\1/')
  [[ -n "$account" ]] && add_account "$account" "mise-env"
fi

# 5. git config user.name
git_user=$(git config user.name 2>/dev/null)
[[ -n "$git_user" ]] && add_account "$git_user" "git-config"

# Score and display
log "=== Detected GitHub Accounts ==="
RECOMMENDED=""
MAX_SOURCES=0
for idx in "${!ACCOUNT_NAMES[@]}"; do
  account="${ACCOUNT_NAMES[$idx]}"
  sources="${ACCOUNT_SOURCES[$idx]}"
  count=$(echo "$sources" | wc -w | tr -d ' ')
  log "$account: $count sources ($sources)"
  if (( count > MAX_SOURCES )); then
    MAX_SOURCES=$count
    RECOMMENDED="$account"
    RECOMMENDED_SOURCES="$sources"
  fi
done

echo ""
echo "RECOMMENDED=$RECOMMENDED"
echo "SOURCES=$RECOMMENDED_SOURCES"
DETECT_ACCOUNTS_EOF
```

### AskUserQuestion

```yaml
AskUserQuestion:
  question: "Which GitHub account should be used for recording storage?"
  header: "GitHub Account Selection"
  options:
    - label: "${RECOMMENDED} (Recommended)"
      description: "Detected via: ${SOURCES}"
    # Additional detected accounts appear here dynamically
    - label: "Enter manually"
      description: "Type a GitHub username not listed above"
```

### Post-Selection

If user selects an account, ensure gh CLI is using that account:

```bash
/usr/bin/env bash << 'POST_SELECT_EOF'
# Ensure gh CLI is authenticated as selected account
SELECTED_ACCOUNT="${1:?Usage: provide selected account}"

if ! gh auth status 2>&1 | grep -q "Logged in to github.com account $SELECTED_ACCOUNT"; then
  echo "Switching gh CLI to account: $SELECTED_ACCOUNT"
  gh auth switch --user "$SELECTED_ACCOUNT" 2>/dev/null || \
    echo "Warning: Could not switch accounts. Manual auth may be needed."
fi
POST_SELECT_EOF
```

---

## Phase 1.5: Current Repository Detection

Detect current git repository context to provide intelligent defaults for Phase 2 questions.

### Detection Script

```bash
/usr/bin/env bash << 'DETECT_REPO_EOF'
# Detect current repository context for intelligent defaults

CURRENT_REPO_URL=""
CURRENT_REPO_OWNER=""
CURRENT_REPO_NAME=""
DETECTED_FROM=""

# Check if we're in a git repository
if git rev-parse --git-dir &>/dev/null; then
  # Try origin remote first
  if git remote get-url origin &>/dev/null; then
    CURRENT_REPO_URL=$(git remote get-url origin)
    DETECTED_FROM="origin remote"
  # Fallback to first available remote
  elif [[ -n "$(git remote)" ]]; then
    REMOTE=$(git remote | head -1)
    CURRENT_REPO_URL=$(git remote get-url "$REMOTE")
    DETECTED_FROM="$REMOTE remote"
  fi

  # Parse owner and name from URL (SSH or HTTPS)
  if [[ -n "$CURRENT_REPO_URL" ]]; then
    if [[ "$CURRENT_REPO_URL" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
      CURRENT_REPO_OWNER="${BASH_REMATCH[1]}"
      CURRENT_REPO_NAME="${BASH_REMATCH[2]%.git}"
    fi
  fi
fi

# Output for Claude to parse
echo "CURRENT_REPO_URL=$CURRENT_REPO_URL"
echo "CURRENT_REPO_OWNER=$CURRENT_REPO_OWNER"
echo "CURRENT_REPO_NAME=$CURRENT_REPO_NAME"
echo "DETECTED_FROM=$DETECTED_FROM"
DETECT_REPO_EOF
```

**Claude Action**: Store detected values (`CURRENT_REPO_OWNER`, `CURRENT_REPO_NAME`, `DETECTED_FROM`) for use in subsequent AskUserQuestion calls. If no repo detected, proceed without defaults.
