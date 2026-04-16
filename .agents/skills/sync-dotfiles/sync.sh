#!/bin/bash
set -euo pipefail

# sync.sh — Sync user-level Claude/Codex configs between ai-env dotfiles/ and ~/.claude / ~/.codex
#
# Invoked via the /sync-dotfiles skill or directly:
#   sync.sh push        Merge repo → home directory (repo wins on conflicts)
#   sync.sh pull        Merge home directory → repo (home wins on conflicts)
#   sync.sh diff        Show differences between repo and home directory
#   sync.sh status      Show which files exist where
#   sync.sh skills-push Install skills via npx (default: camacho/ai-skills)
#
# Governance files (settings.json, config.toml) are SEMANTICALLY MERGED:
#   - permissions.deny/allow arrays: union (both sides preserved, deduplicated)
#   - hooks: union by event+matcher (no duplicates, both sides preserved)
#   - codex profiles: union (source wins on collision for scalar values)
#   - all other keys: source wins on conflict
#
# CLAUDE.md is SECTION-MERGED:
#   - Sections keyed by ## heading: union (all sections from both sides kept)
#   - Same heading in both sides: source wins
#   - Preamble (content before first ##): source wins
#
# Non-governance files (hooks, skills, agents, commands, rules) are copied directly.
#
# This script NEVER touches session data, projects/, backups/, or plugins/.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- AI_ENV_ROOT discovery ---
# Find the ai-env repo where dotfiles/ lives.
resolve_ai_env_root() {
  # 1. Already set via env var
  if [[ -n "${AI_ENV_ROOT:-}" ]] && [[ -d "$AI_ENV_ROOT/dotfiles" ]]; then
    echo "$AI_ENV_ROOT"
    return 0
  fi

  # 2. Script is inside ai-env repo (e.g., running from dotfiles/sync.sh symlink)
  local candidate
  candidate="$(cd "$SCRIPT_DIR" && git rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "$candidate" ]] && [[ -d "$candidate/dotfiles" ]]; then
    echo "$candidate"
    return 0
  fi

  # 3. Known local path
  if [[ -d "$HOME/projects/camacho/ai-env/dotfiles" ]]; then
    echo "$HOME/projects/camacho/ai-env"
    return 0
  fi

  # 4. Clone from GitHub (temp dir — pull is blocked when this path is used)
  local tmp_dir="/tmp/ai-env-dotfiles-$$"
  if git clone --depth 1 https://github.com/camacho/ai-env.git "$tmp_dir" 2>/dev/null; then
    echo "$tmp_dir"
    return 0
  fi

  # 5. Give up
  echo ""
  return 1
}

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# BSD diff (macOS) does not support --color=auto; detect at runtime.
if diff --color=auto /dev/null /dev/null 2>/dev/null; then
  DIFF_CMD="diff --color=auto"
else
  DIFF_CMD="diff"
fi

AI_ENV_ROOT="$(resolve_ai_env_root)" || {
  echo -e "${RED}error${NC}  Cannot find ai-env repo. Set AI_ENV_ROOT to your ai-env clone path." >&2
  exit 1
}

# Detect if we fell back to a temp clone — pull would write to a throwaway dir and lose changes
if [[ "$AI_ENV_ROOT" == /tmp/ai-env-dotfiles-* ]]; then
  AI_ENV_TEMP_CLONE=true
  trap 'rm -rf "$AI_ENV_ROOT"' EXIT
else
  AI_ENV_TEMP_CLONE=false
fi

CLAUDE_SRC="$AI_ENV_ROOT/dotfiles/claude"
CODEX_SRC="$AI_ENV_ROOT/dotfiles/codex"
CLAUDE_DST="$HOME/.claude"
CODEX_DST="$HOME/.codex"

# Default skills repo — override with AI_SKILLS_REPO env var, set AI_SKILLS_REPO= to skip
DEFAULT_SKILLS_REPO="camacho/ai-skills"

# --- File registry ---
# Governance files get semantic merge; everything else gets simple copy.
# Format: "relative/path:merge_strategy"
#   merge_strategy: "settings" | "codex_config" | "claude_md" | "copy"
# Directory globs: if the path ends with "/", all .md files in that dir are synced with the given strategy.
CLAUDE_REGISTRY=(
  "settings.json:settings"
  "CLAUDE.md:claude_md"
  "commands/catchup.md:copy"
  "commands/reflect.md:copy"
)

CODEX_REGISTRY=(
  "config.toml:codex_config"
)

usage() {
  echo "Usage: $0 {push|pull|diff|status|skills-push}"
  echo ""
  echo "  push             Push repo configs → ~/.claude and ~/.codex (repo wins on conflicts)"
  echo "  pull             Pull ~/.claude and ~/.codex configs → repo (home wins on conflicts)"
  echo "  diff             Show differences between repo and home directory"
  echo "  status           Show which files exist where"
  echo "  skills-push      Push skills via npx (default: $DEFAULT_SKILLS_REPO, override with \$AI_SKILLS_REPO)"
  exit 1
}

# --- Simple copy (for non-governance files) ---
copy_file() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  if [[ "$src" == *.sh ]]; then
    chmod +x "$dst"
  fi
}

# --- settings.json semantic merge ---
# Union-merges permissions arrays and hooks. Source wins on scalar conflicts.
# Requires: jq
merge_settings_json() {
  local source="$1" target="$2" output="$3"

  if ! command -v jq &>/dev/null; then
    echo -e "  ${RED}error${NC}  jq required for settings.json merge (install with: apt install jq)" >&2
    return 1
  fi

  # If target doesn't exist, just copy source
  if [[ ! -f "$target" ]]; then
    cp "$source" "$output"
    return 0
  fi

  # If source doesn't exist, keep target
  if [[ ! -f "$source" ]]; then
    cp "$target" "$output"
    return 0
  fi

  jq -n --slurpfile src "$source" --slurpfile dst "$target" '
    ($src[0]) as $s | ($dst[0]) as $d |

    # Union-merge two arrays: concatenate and deduplicate
    def union_arrays: (.[0] // []) + (.[1] // []) | unique;

    # Merge hook groups for a single event.
    # Each event is an array of hook groups: [{"matcher": "...", "hooks": [...]}]
    # Union by matcher: keep all unique matchers from both sides.
    # If same matcher exists in both, source wins (replaces the group).
    def merge_hook_groups($src_groups; $dst_groups):
      ($dst_groups | map({key: (.matcher // ""), value: .}) | from_entries) as $dst_idx |
      ($src_groups | map({key: (.matcher // ""), value: .}) | from_entries) as $src_idx |
      ($dst_idx * $src_idx) | to_entries | map(.value);

    # Merge all hooks across both sides
    ([($s.hooks // {} | keys[]), ($d.hooks // {} | keys[])] | unique) as $all_events |
    ($all_events | map(
      . as $evt |
      {($evt): merge_hook_groups($s.hooks[$evt] // []; $d.hooks[$evt] // [])}
    ) | add // {}) as $merged_hooks |

    # Union-merge permission arrays
    ([$s.permissions.allow, $d.permissions.allow] | union_arrays) as $merged_allow |
    ([$s.permissions.deny, $d.permissions.deny] | union_arrays) as $merged_deny |

    # Build merged object: destination as base, source scalars overlay
    ($d // {}) * ($s // {}) |

    # Replace permissions with union-merged versions (not scalar override)
    .permissions = (
      [if ($merged_allow | length) > 0 then {allow: $merged_allow} else null end,
       if ($merged_deny | length) > 0 then {deny: $merged_deny} else null end]
      | map(select(. != null)) | add // {}
    ) |
    if .permissions == {} then del(.permissions) else . end |

    # Replace hooks with union-merged versions
    .hooks = $merged_hooks |
    if .hooks == {} then del(.hooks) else . end
  ' > "$output"
}

# --- config.toml semantic merge ---
# Union-merges profiles. Source wins on scalar conflicts.
# Uses Python since bash has no native TOML parser.
merge_codex_config() {
  local source="$1" target="$2" output="$3"

  # If target doesn't exist, just copy source
  if [[ ! -f "$target" ]]; then
    cp "$source" "$output"
    return 0
  fi

  # If source doesn't exist, keep target
  if [[ ! -f "$source" ]]; then
    cp "$target" "$output"
    return 0
  fi

  if ! command -v python3 &>/dev/null; then
    echo -e "  ${RED}error${NC}  python3 required for config.toml merge" >&2
    return 1
  fi

  python3 - "$source" "$target" "$output" << 'PYEOF'
import sys, re
from collections import OrderedDict

def parse_toml_simple(path):
    """Minimal TOML parser for flat keys + [section] tables with flat keys.
    Preserves comment blocks that appear BEFORE each section header or key."""
    sections = OrderedDict()       # section_name -> OrderedDict of key -> value
    section_comments = OrderedDict()  # section_name -> list of comment lines before the [header]
    key_comments = OrderedDict()   # (section_name, key) -> list of comment lines before the key
    current_section = None
    pending_comments = []

    with open(path) as f:
        for line in f:
            stripped = line.strip()

            if stripped == "" or stripped.startswith("#"):
                pending_comments.append(line.rstrip("\n"))
                continue

            # Section header: [profiles.review]
            m = re.match(r'^\[(.+)\]$', stripped)
            if m:
                current_section = m.group(1)
                if current_section not in sections:
                    sections[current_section] = OrderedDict()
                section_comments[current_section] = pending_comments
                pending_comments = []
                continue

            # Key = value
            m = re.match(r'^(\w+)\s*=\s*(.+)$', stripped)
            if m:
                key, val = m.group(1), m.group(2).strip()
                sect = current_section or "__top__"
                if sect not in sections:
                    sections[sect] = OrderedDict()
                sections[sect][key] = val
                if pending_comments:
                    if sect == "__top__" and sect not in section_comments:
                        section_comments[sect] = pending_comments
                    else:
                        key_comments[(sect, key)] = pending_comments
                    pending_comments = []
                continue

    if pending_comments:
        section_comments["__trailing__"] = pending_comments
    return sections, section_comments, key_comments

def merge_configs(src_path, dst_path, out_path):
    src, src_sec_cmt, src_key_cmt = parse_toml_simple(src_path)
    dst, dst_sec_cmt, dst_key_cmt = parse_toml_simple(dst_path)

    # Union sections: destination as base, source overlaid
    merged = OrderedDict()
    all_sections = list(OrderedDict.fromkeys(
        list(dst.keys()) + list(src.keys())
    ))

    for section in all_sections:
        s_vals = src.get(section, OrderedDict())
        d_vals = dst.get(section, OrderedDict())
        m = OrderedDict(d_vals)
        m.update(s_vals)
        merged[section] = m

    # Write output preserving comment placement from source, fallback to destination
    lines = []
    for section in merged:
        if section == "__trailing__":
            continue

        # Section-level comments (before [header] or before first top-level key)
        cmt = src_sec_cmt.get(section, dst_sec_cmt.get(section, []))
        lines.extend(cmt)

        if section != "__top__":
            lines.append(f"[{section}]")

        for k, v in merged[section].items():
            # Key-level comments (before this specific key)
            kcmt = src_key_cmt.get((section, k), dst_key_cmt.get((section, k), []))
            lines.extend(kcmt)
            lines.append(f"{k} = {v}")

        lines.append("")  # blank line after each section

    # Trailing comments
    lines.extend(src_sec_cmt.get("__trailing__", dst_sec_cmt.get("__trailing__", [])))

    # Normalize: collapse 3+ consecutive blank lines to 1
    normalized = []
    for line in lines:
        if line.strip() == "" and normalized and normalized[-1].strip() == "":
            continue
        normalized.append(line)

    with open(out_path, "w") as f:
        f.write("\n".join(normalized))
        if normalized and normalized[-1].strip() != "":
            f.write("\n")

merge_configs(sys.argv[1], sys.argv[2], sys.argv[3])
PYEOF
}

# --- CLAUDE.md section merge ---
# Union-merges ## sections. Source wins on collision (same heading). Preamble: source wins.
# Uses awk — no external dependencies beyond bash builtins.
# — Claude claude-sonnet-4-6: awk-based section merge.
merge_claude_md() {
  local source="$1" target="$2" output="$3"

  # If target doesn't exist, just copy source
  if [[ ! -f "$target" ]]; then
    cp "$source" "$output"
    return 0
  fi

  # If source doesn't exist, keep target
  if [[ ! -f "$source" ]]; then
    cp "$target" "$output"
    return 0
  fi

  # We parse each file into named sections keyed by "## Heading" text.
  # All sections from both sides are emitted (union). Source wins on collision.
  awk '
  BEGIN {
    src = ARGV[1]
    dst = ARGV[2]
    out = ARGV[3]

    # Parse source
    src_idx[0] = 0
    src_cur = "__preamble__"
    src_buf = ""
    while ((getline line < src) > 0) {
      if (line ~ /^## /) {
        src_sections[src_cur] = src_buf
        if (!(src_cur in src_order_set)) {
          src_idx[0]++
          src_order[src_idx[0]] = src_cur
          src_order_set[src_cur] = 1
        }
        src_cur = line
        src_buf = line "\n"
      } else {
        src_buf = src_buf line "\n"
      }
    }
    close(src)
    src_sections[src_cur] = src_buf
    if (!(src_cur in src_order_set)) {
      src_idx[0]++
      src_order[src_idx[0]] = src_cur
      src_order_set[src_cur] = 1
    }

    # Parse destination
    dst_idx[0] = 0
    dst_cur = "__preamble__"
    dst_buf = ""
    while ((getline line < dst) > 0) {
      if (line ~ /^## /) {
        dst_sections[dst_cur] = dst_buf
        if (!(dst_cur in dst_order_set)) {
          dst_idx[0]++
          dst_order[dst_idx[0]] = dst_cur
          dst_order_set[dst_cur] = 1
        }
        dst_cur = line
        dst_buf = line "\n"
      } else {
        dst_buf = dst_buf line "\n"
      }
    }
    close(dst)
    dst_sections[dst_cur] = dst_buf
    if (!(dst_cur in dst_order_set)) {
      dst_idx[0]++
      dst_order[dst_idx[0]] = dst_cur
      dst_order_set[dst_cur] = 1
    }

    # Build merged order: dst sections first, then src-only sections appended
    merged_idx = 0
    for (i = 1; i <= dst_idx[0]; i++) {
      k = dst_order[i]
      merged_idx++
      merged_order[merged_idx] = k
      merged_set[k] = 1
    }
    for (i = 1; i <= src_idx[0]; i++) {
      k = src_order[i]
      if (!(k in merged_set)) {
        merged_idx++
        merged_order[merged_idx] = k
      }
    }

    # Write output: source wins on collision (if key in src, use src; else use dst)
    for (i = 1; i <= merged_idx; i++) {
      k = merged_order[i]
      if (k in src_sections) {
        printf "%s", src_sections[k] > out
      } else {
        printf "%s", dst_sections[k] > out
      }
    }
    close(out)
  }
  ' "$source" "$target" "$output"
}

# --- Dispatch: pick the right sync strategy ---
sync_entry() {
  local src="$1" dst="$2" label="$3" strategy="$4"

  if [[ ! -f "$src" ]]; then
    echo -e "  ${YELLOW}skip${NC}  $label (source missing)"
    return
  fi

  case "$strategy" in
    settings)
      local tmp
      tmp=$(mktemp)
      if merge_settings_json "$src" "$dst" "$tmp"; then
        mkdir -p "$(dirname "$dst")"
        mv "$tmp" "$dst"
        echo -e "  ${GREEN}merge${NC}  $label (semantic: permissions + hooks union)"
      else
        rm -f "$tmp"
        echo -e "  ${RED}fail${NC}  $label (merge failed, file unchanged)"
      fi
      ;;
    codex_config)
      local tmp
      tmp=$(mktemp)
      if merge_codex_config "$src" "$dst" "$tmp"; then
        mkdir -p "$(dirname "$dst")"
        mv "$tmp" "$dst"
        echo -e "  ${GREEN}merge${NC}  $label (semantic: profiles union, source wins scalars)"
      else
        rm -f "$tmp"
        echo -e "  ${RED}fail${NC}  $label (merge failed, file unchanged)"
      fi
      ;;
    claude_md)
      local tmp
      tmp=$(mktemp)
      if merge_claude_md "$src" "$dst" "$tmp"; then
        mkdir -p "$(dirname "$dst")"
        mv "$tmp" "$dst"
        echo -e "  ${GREEN}merge${NC}  $label (section merge: ## headings union, source wins collision)"
      else
        rm -f "$tmp"
        echo -e "  ${RED}fail${NC}  $label (merge failed, file unchanged)"
      fi
      ;;
    copy)
      copy_file "$src" "$dst"
      echo -e "  ${GREEN}copy${NC}  $label"
      ;;
    *)
      echo -e "  ${RED}error${NC}  $label (unknown strategy: $strategy)"
      ;;
  esac
}

# --- Parse registry entry into path and strategy ---
parse_entry() {
  local entry="$1"
  FILE_PATH="${entry%%:*}"
  FILE_STRATEGY="${entry##*:}"
}

# --- Sync a single registry entry, expanding directory globs if path ends with "/" ---
# Usage: sync_registry_entry <src_base> <dst_base> <file_path> <strategy>
sync_registry_entry() {
  local src_base="$1" dst_base="$2" file_path="$3" strategy="$4"

  if [[ "$file_path" == */ ]]; then
    # Directory glob: sync all .md files found in whichever side has the directory.
    # During push: iterate repo (src_base); during pull: iterate home (dst_base for pull = src).
    # We collect files from both sides to handle missing-in-one case gracefully.
    local dir="${file_path%/}"
    local seen=()
    # Collect from src side
    if [[ -d "$src_base/$dir" ]]; then
      while IFS= read -r f; do
        local rel
        rel="$(basename "$f")"
        seen+=("$rel")
      done < <(find "$src_base/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | sort)
    fi
    # Collect from dst side (files that may not be in src yet)
    if [[ -d "$dst_base/$dir" ]]; then
      while IFS= read -r f; do
        local rel
        rel="$(basename "$f")"
        # Only add if not already seen
        local already=false
        for s in "${seen[@]:-}"; do [[ "$s" == "$rel" ]] && already=true && break; done
        [[ "$already" == false ]] && seen+=("$rel")
      done < <(find "$dst_base/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | sort)
    fi
    for rel in "${seen[@]:-}"; do
      if [[ -n "$rel" ]]; then
        sync_entry "$src_base/$dir/$rel" "$dst_base/$dir/$rel" "$dir/$rel" "$strategy"
      fi
    done
  else
    sync_entry "$src_base/$file_path" "$dst_base/$file_path" "$file_path" "$strategy"
  fi
}

# --- Expand a registry entry into concrete file paths (handles directory globs) ---
# Populates EXPANDED_FILES array with relative paths.
expand_entry() {
  local src_base="$1" dst_base="$2" file_path="$3"
  EXPANDED_FILES=()
  if [[ "$file_path" == */ ]]; then
    local dir="${file_path%/}"
    local seen=()
    if [[ -d "$src_base/$dir" ]]; then
      while IFS= read -r f; do
        seen+=("$dir/$(basename "$f")")
      done < <(find "$src_base/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | sort)
    fi
    if [[ -d "$dst_base/$dir" ]]; then
      while IFS= read -r f; do
        local rel="$dir/$(basename "$f")"
        local already=false
        for s in "${seen[@]:-}"; do [[ "$s" == "$rel" ]] && already=true && break; done
        [[ "$already" == false ]] && seen+=("$rel")
      done < <(find "$dst_base/$dir" -maxdepth 1 -name "*.md" 2>/dev/null | sort)
    fi
    for rel in "${seen[@]:-}"; do
      if [[ -n "$rel" ]]; then
        EXPANDED_FILES+=("$rel")
      fi
    done
  else
    EXPANDED_FILES=("$file_path")
  fi
}

# --- Commands ---

cmd_push() {
  echo -e "${CYAN}Installing global configs → home directory (repo wins on conflicts)${NC}"
  echo ""

  echo "Claude (~/.claude/):"
  for entry in "${CLAUDE_REGISTRY[@]}"; do
    parse_entry "$entry"
    sync_registry_entry "$CLAUDE_SRC" "$CLAUDE_DST" "$FILE_PATH" "$FILE_STRATEGY"
  done

  echo ""
  echo "Codex (~/.codex/):"
  for entry in "${CODEX_REGISTRY[@]}"; do
    parse_entry "$entry"
    sync_registry_entry "$CODEX_SRC" "$CODEX_DST" "$FILE_PATH" "$FILE_STRATEGY"
  done

  # Install skills from AI_SKILLS_REPO (defaults to camacho/ai-skills, set AI_SKILLS_REPO= to skip)
  local skills_repo="${AI_SKILLS_REPO-$DEFAULT_SKILLS_REPO}"
  if [[ -n "$skills_repo" ]]; then
    echo ""
    if command -v npx &>/dev/null; then
      echo -e "${CYAN}Installing skills from $skills_repo via npx...${NC}"
      if npx skills add "$skills_repo" --scope personal; then
        echo -e "  ${GREEN}ok${NC}  Skills installed from $skills_repo"
        echo "  Run 'sync.sh pull' to capture installed skills to the repo."
      else
        echo -e "  ${YELLOW}warn${NC}  Skills install failed (non-fatal)"
        echo "  Retry manually: sync.sh skills-push"
      fi
    else
      echo -e "  ${YELLOW}warn${NC}  npx not found — skipping skills install"
    fi
  fi

  echo ""
  echo -e "${GREEN}Done.${NC} Restart Claude Code / Codex to pick up changes."
}

cmd_skills_push() {
  local skills_repo="${AI_SKILLS_REPO-$DEFAULT_SKILLS_REPO}"
  if [[ -z "$skills_repo" ]]; then
    echo -e "${RED}error${NC}  AI_SKILLS_REPO is explicitly set to empty. Unset it to use the default (${DEFAULT_SKILLS_REPO}), or set it to a non-empty repo slug." >&2
    exit 1
  fi

  if ! command -v npx &>/dev/null; then
    echo -e "${RED}error${NC}  npx not found. Install Node.js to use skills add." >&2
    exit 1
  fi

  echo -e "${CYAN}Installing skills from $skills_repo...${NC}"
  echo "  (override with: AI_SKILLS_REPO=other/repo sync.sh skills-push)"
  npx skills add "$skills_repo" --scope personal
  echo ""
  echo -e "${GREEN}Done.${NC} Skills installed to ~/.claude/skills/"
  echo "  Capture to the repo: sync.sh pull && git add dotfiles/ && git commit -m 'chore: sync skills'"
}

cmd_pull() {
  # Block pull when AI_ENV_ROOT is a temporary clone — changes would be written to /tmp and lost.
  if [[ "${AI_ENV_TEMP_CLONE:-false}" == true ]]; then
    echo -e "${RED}error${NC}  Cannot pull to a temporary clone. Set AI_ENV_ROOT or clone ai-env locally." >&2
    echo "  Example: export AI_ENV_ROOT=~/projects/camacho/ai-env" >&2
    exit 1
  fi

  echo -e "${CYAN}Pulling user configs → repo (home wins on conflicts)${NC}"
  echo ""

  echo "Claude (~/.claude/ → dotfiles/claude/):"
  for entry in "${CLAUDE_REGISTRY[@]}"; do
    parse_entry "$entry"
    sync_registry_entry "$CLAUDE_DST" "$CLAUDE_SRC" "$FILE_PATH" "$FILE_STRATEGY"
  done

  echo ""
  echo "Codex (~/.codex/ → dotfiles/codex/):"
  for entry in "${CODEX_REGISTRY[@]}"; do
    parse_entry "$entry"
    sync_registry_entry "$CODEX_DST" "$CODEX_SRC" "$FILE_PATH" "$FILE_STRATEGY"
  done

  echo ""
  echo -e "${GREEN}Done.${NC} Review changes: git -C \"$AI_ENV_ROOT\" diff dotfiles/"
}

cmd_diff() {
  echo -e "${CYAN}Differences between repo and home directory${NC}"
  echo ""
  local has_diff=false

  echo "Claude:"
  for entry in "${CLAUDE_REGISTRY[@]}"; do
    parse_entry "$entry"
    expand_entry "$CLAUDE_SRC" "$CLAUDE_DST" "$FILE_PATH"
    for f in "${EXPANDED_FILES[@]:-}"; do
      if [[ -z "$f" ]]; then continue; fi
      if [[ -f "$CLAUDE_SRC/$f" && -f "$CLAUDE_DST/$f" ]]; then
        if ! diff -q "$CLAUDE_SRC/$f" "$CLAUDE_DST/$f" >/dev/null 2>&1; then
          local strategy_label="copy"
          [[ "$FILE_STRATEGY" == "settings" ]] && strategy_label="semantic merge"
          [[ "$FILE_STRATEGY" == "codex_config" ]] && strategy_label="semantic merge"
          [[ "$FILE_STRATEGY" == "claude_md" ]] && strategy_label="section merge"
          echo -e "  ${YELLOW}changed${NC}  $f  (sync strategy: $strategy_label)"
          $DIFF_CMD -u "$CLAUDE_SRC/$f" "$CLAUDE_DST/$f" 2>/dev/null | sed 's/^/    /' || true
          has_diff=true
        fi
      elif [[ -f "$CLAUDE_SRC/$f" ]]; then
        echo -e "  ${RED}missing in ~/.claude${NC}  $f"
        has_diff=true
      elif [[ -f "$CLAUDE_DST/$f" ]]; then
        echo -e "  ${RED}missing in repo${NC}  $f"
        has_diff=true
      fi
    done
  done

  echo ""
  echo "Codex:"
  for entry in "${CODEX_REGISTRY[@]}"; do
    parse_entry "$entry"
    expand_entry "$CODEX_SRC" "$CODEX_DST" "$FILE_PATH"
    for f in "${EXPANDED_FILES[@]:-}"; do
      if [[ -z "$f" ]]; then continue; fi
      if [[ -f "$CODEX_SRC/$f" && -f "$CODEX_DST/$f" ]]; then
        if ! diff -q "$CODEX_SRC/$f" "$CODEX_DST/$f" >/dev/null 2>&1; then
          echo -e "  ${YELLOW}changed${NC}  $f  (sync strategy: semantic merge)"
          $DIFF_CMD -u "$CODEX_SRC/$f" "$CODEX_DST/$f" 2>/dev/null | sed 's/^/    /' || true
          has_diff=true
        fi
      elif [[ -f "$CODEX_SRC/$f" ]]; then
        echo -e "  ${RED}missing in ~/.codex${NC}  $f"
        has_diff=true
      elif [[ -f "$CODEX_DST/$f" ]]; then
        echo -e "  ${RED}missing in repo${NC}  $f"
        has_diff=true
      fi
    done
  done

  if [[ "$has_diff" = false ]]; then
    echo ""
    echo -e "${GREEN}Everything in sync.${NC}"
  fi
}

cmd_status() {
  echo -e "${CYAN}Global config status${NC}"
  echo ""

  printf "%-50s %-8s %-8s %-16s\n" "File" "Repo" "Home" "Merge Strategy"
  printf "%-50s %-8s %-8s %-16s\n" "----" "----" "----" "--------------"

  for entry in "${CLAUDE_REGISTRY[@]}"; do
    parse_entry "$entry"
    expand_entry "$CLAUDE_SRC" "$CLAUDE_DST" "$FILE_PATH"
    for f in "${EXPANDED_FILES[@]:-}"; do
      if [[ -z "$f" ]]; then continue; fi
      local repo_status="--" home_status="--"
      if [[ -f "$CLAUDE_SRC/$f" ]]; then repo_status="yes"; fi
      if [[ -f "$CLAUDE_DST/$f" ]]; then home_status="yes"; fi
      printf "%-50s %-8s %-8s %-16s\n" "claude/$f" "$repo_status" "$home_status" "$FILE_STRATEGY"
    done
  done

  for entry in "${CODEX_REGISTRY[@]}"; do
    parse_entry "$entry"
    expand_entry "$CODEX_SRC" "$CODEX_DST" "$FILE_PATH"
    for f in "${EXPANDED_FILES[@]:-}"; do
      if [[ -z "$f" ]]; then continue; fi
      local repo_status="--" home_status="--"
      if [[ -f "$CODEX_SRC/$f" ]]; then repo_status="yes"; fi
      if [[ -f "$CODEX_DST/$f" ]]; then home_status="yes"; fi
      printf "%-50s %-8s %-8s %-16s\n" "codex/$f" "$repo_status" "$home_status" "$FILE_STRATEGY"
    done
  done
}

case "${1:-}" in
  push)           cmd_push ;;
  pull)           cmd_pull ;;
  diff)           cmd_diff ;;
  status)         cmd_status ;;
  skills-push) cmd_skills_push ;;
  *)              usage ;;
esac
