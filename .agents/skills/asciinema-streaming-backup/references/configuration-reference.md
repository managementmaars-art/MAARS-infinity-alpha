**Skill**: [asciinema-streaming-backup](../SKILL.md)

# Configuration Reference

All AskUserQuestion sequences for core and advanced configuration, plus URL normalization and task templates.

---

## Phase 2: Core Configuration

### 2.1 Repository URL

**If current repo detected** (from Phase 1.5):

```yaml
AskUserQuestion:
  question: "Which repository should store the recordings?"
  header: "Repository"
  options:
    - label: "${CURRENT_REPO_OWNER}/${CURRENT_REPO_NAME} (Recommended)"
      description: "Current repo detected from ${DETECTED_FROM}"
    - label: "Create dedicated repo: ${GITHUB_ACCOUNT}/asciinema-recordings"
      description: "Separate repository for all recordings"
    - label: "Enter different repository"
      description: "Specify another repository (user/repo format)"
```

**If no current repo detected**:

```yaml
AskUserQuestion:
  question: "Enter the GitHub repository URL for storing recordings:"
  header: "Repository URL"
  options:
    - label: "Create dedicated repo: ${GITHUB_ACCOUNT}/asciinema-recordings"
      description: "Separate repository for all recordings (Recommended)"
    - label: "Enter repository manually"
      description: "SSH (git@github.com:user/repo.git), HTTPS, or shorthand (user/repo)"
```

### URL Normalization

Handles multiple formats:

```bash
/usr/bin/env bash << 'NORMALIZE_URL_EOF'
# Normalize to SSH format for consistent handling
normalize_repo_url() {
  local url="$1"

  # Shorthand: user/repo -> git@github.com:user/repo.git
  if [[ "$url" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$ ]]; then
    echo "git@github.com:${url}.git"
  # HTTPS: https://github.com/user/repo -> git@github.com:user/repo.git
  elif [[ "$url" =~ ^https://github\.com/([^/]+)/([^/]+)/?$ ]]; then
    echo "git@github.com:${BASH_REMATCH[1]}/${BASH_REMATCH[2]%.git}.git"
  # Already SSH format
  else
    echo "$url"
  fi
}

URL="${1:?Usage: provide URL to normalize}"
normalize_repo_url "$URL"
NORMALIZE_URL_EOF
```

### Confirmation for Free-Form Input

If user selected "Enter different/manually":

```yaml
AskUserQuestion:
  question: "You entered '${USER_INPUT}'. Normalized to: ${NORMALIZED_URL}. Is this correct?"
  header: "Confirm Repository"
  options:
    - label: "Yes, use ${NORMALIZED_URL}"
      description: "Proceed with this repository"
    - label: "No, let me re-enter"
      description: "Go back to repository selection"
```

### 2.2 Recording Directory

```yaml
AskUserQuestion:
  question: "Where should recordings be stored locally?"
  header: "Recording Directory"
  options:
    - label: "~/asciinema_recordings/${RESOLVED_REPO_NAME} (Recommended)"
      description: "Example: ~/asciinema_recordings/alpha-forge"
    - label: "Custom path"
      description: "Enter a different directory path"
```

**Note**: `${RESOLVED_REPO_NAME}` is the actual repo name from Phase 1.5 or Phase 2.1, not a variable placeholder. Display the concrete path to user.

### 2.3 Branch Name

```yaml
AskUserQuestion:
  question: "What should the orphan branch be named?"
  header: "Branch Name"
  options:
    - label: "asciinema-recordings (Recommended)"
      description: "Matches ~/asciinema_recordings/ parent directory pattern"
    - label: "gh-recordings"
      description: "GitHub-prefixed alternative (gh = GitHub storage)"
    - label: "recordings"
      description: "Minimal name"
    - label: "Custom"
      description: "Enter a custom branch name"
```

**Naming Convention**: The default `asciinema-recordings` matches the parent directory `~/asciinema_recordings/` for consistency.

---

## Phase 3: Advanced Configuration

### Configuration Parameters

| Parameter      | Default | Options                                     |
| -------------- | ------- | ------------------------------------------- |
| Idle threshold | 30s     | 15s, 30s (Recommended), 60s, Custom (5-300) |
| zstd level     | 3       | 1 (fast), 3 (Recommended), 6, Custom (1-22) |
| Brotli level   | 9       | 6, 9 (Recommended), 11, Custom (1-11)       |
| Auto-push      | Yes     | Yes (Recommended), No                       |
| Poll interval  | 5s      | 2s, 5s (Recommended), 10s                   |

### 3.1 Idle Threshold

```yaml
AskUserQuestion:
  question: "How long should the chunker wait before creating a chunk?"
  header: "Idle Threshold"
  options:
    - label: "15 seconds"
      description: "More frequent chunks, smaller files"
    - label: "30 seconds (Recommended)"
      description: "Balanced chunk size and frequency"
    - label: "60 seconds"
      description: "Larger chunks, less frequent uploads"
    - label: "Custom (5-300 seconds)"
      description: "Enter a custom threshold"
```

### 3.2 zstd Compression Level

```yaml
AskUserQuestion:
  question: "What zstd compression level for streaming chunks?"
  header: "zstd Level"
  options:
    - label: "1 (Fast)"
      description: "Fastest compression, larger files"
    - label: "3 (Recommended)"
      description: "Good balance of speed and compression"
    - label: "6 (Better compression)"
      description: "Slower but smaller chunks"
    - label: "Custom (1-22)"
      description: "Enter a custom level"
```

### 3.3 Brotli Compression Level

```yaml
AskUserQuestion:
  question: "What brotli compression level for final archives?"
  header: "Brotli Level"
  options:
    - label: "6"
      description: "Faster archival, slightly larger files"
    - label: "9 (Recommended)"
      description: "Great compression with reasonable speed"
    - label: "11 (Maximum)"
      description: "Best compression, slowest (may timeout on large files)"
    - label: "Custom (1-11)"
      description: "Enter a custom level"
```

### 3.4 Auto-Push

```yaml
AskUserQuestion:
  question: "Should chunks be automatically pushed to GitHub?"
  header: "Auto-Push"
  options:
    - label: "Yes (Recommended)"
      description: "Push immediately after each chunk"
    - label: "No"
      description: "Manual push when ready"
```

### 3.5 Poll Interval

```yaml
AskUserQuestion:
  question: "How often should the chunker check for idle state?"
  header: "Poll Interval"
  options:
    - label: "2 seconds"
      description: "More responsive, slightly higher CPU"
    - label: "5 seconds (Recommended)"
      description: "Good balance"
    - label: "10 seconds"
      description: "Lower resource usage"
```

---

## TodoWrite Task Templates

### Template: Full Setup

```
1. [Preflight] Validate all tools installed (asciinema, zstd, brotli, git, gh)
2. [Preflight] AskUserQuestion: offer installation for missing tools
3. [Account] Detect GitHub accounts from 5 sources
4. [Account] AskUserQuestion: select GitHub account
5. [Config] AskUserQuestion: repository URL
6. [Config] AskUserQuestion: recording directory
7. [Config] AskUserQuestion: branch name
8. [Advanced] AskUserQuestion: idle threshold
9. [Advanced] AskUserQuestion: zstd level
10. [Advanced] AskUserQuestion: brotli level
11. [Advanced] AskUserQuestion: auto-push
12. [Advanced] AskUserQuestion: poll interval
13. [Branch] Check if orphan branch exists on remote
14. [Branch] AskUserQuestion: handle existing branch
15. [Branch] Create orphan branch if needed
16. [Branch] Create GitHub Actions workflow with embedded parameters
17. [Local] Clone orphan branch to ~/asciinema_recordings/
18. [Local] Generate idle-chunker.sh with embedded parameters
19. [Validate] Run autonomous validation (8 tests)
20. [Validate] AskUserQuestion: recording test (user action)
21. [Validate] AskUserQuestion: chunker live test (user action)
22. [Guide] Display configuration summary and usage instructions
```

### Template: Recording Session

```
1. [Context] Detect workspace from $PWD
2. [Context] Generate datetime for filename
3. [Context] Ensure tmp/ directory exists
4. [Command] Generate asciinema rec command
5. [Command] Generate idle-chunker command
6. [Guide] Display two-terminal workflow instructions
```
