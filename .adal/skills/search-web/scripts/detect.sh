#!/usr/bin/env bash
# detect.sh - 运行时环境检测脚本
# 无参数执行，输出: agent / os / state_dir
#
# ⚠️ 硬拷贝此脚本后，必须将下方 REPLACE_ME 替换为实际 skill 名称
DEFAULT_SKILL_NAME="search-web"

set -euo pipefail

# ==============================================================================
# OS 检测
# ==============================================================================

is_wsl() {
  [ -n "${WSL_DISTRO_NAME:-}" ] && return 0
  [ -n "${WSL_INTEROP:-}" ] && return 0
  [ -r /proc/version ] && grep -qi 'microsoft' /proc/version && return 0
  return 1
}

detect_runtime_type() {
  local uname_out
  uname_out="$(uname -s 2>/dev/null || printf 'unknown')"
  case "$uname_out" in
    Windows*)      printf 'windows-native' ;;
    MINGW*|MSYS*|CYGWIN*) printf 'windows-msys' ;;
    Linux)
      if is_wsl; then printf 'linux-wsl'; else printf 'linux-native'; fi ;;
    Darwin)        printf 'macos-native' ;;
    *)             printf 'unknown' ;;
  esac
}

detect_os_type() {
  local runtime_type="${1:-$(detect_runtime_type)}"
  case "$runtime_type" in
    windows-msys|windows-native) printf 'windows' ;;
    linux-wsl|linux-native)      printf 'linux' ;;
    macos-native)                printf 'macos' ;;
    *)                           printf 'unknown' ;;
  esac
}

# ==============================================================================
# Agent 检测
# ==============================================================================

append_signal() {
  local current_signals="$1"
  local next_signal="$2"
  if [ -n "$current_signals" ]; then
    printf '%s\n%s' "$current_signals" "$next_signal"
  else
    printf '%s' "$next_signal"
  fi
}

detect_by_env() {
  local signals=""
  local agent=""
  local confidence=0
  local found_claude=0 found_codex=0 found_opencode=0 found_qwen=0
  local opencode_confidence=0 codex_confidence=0 qwen_confidence=0

  if [ -n "${CLAUDECODE:-}" ]; then
    signals=$(append_signal "$signals" "CLAUDECODE=$CLAUDECODE")
    agent="claude-code"; confidence=90; found_claude=1
  fi

  if [ -n "${CLAUDE_CODE_ENTRYPOINT:-}" ]; then
    signals=$(append_signal "$signals" "CLAUDE_CODE_ENTRYPOINT=$CLAUDE_CODE_ENTRYPOINT")
    found_claude=1
    if [ "$agent" != "claude-code" ]; then agent="claude-code"; confidence=85
    else confidence=95; fi
  fi

  if [ -n "${CODEX_THREAD_ID:-}" ]; then
    signals=$(append_signal "$signals" "CODEX_THREAD_ID=$CODEX_THREAD_ID")
    found_codex=1
    [ "$codex_confidence" -eq 0 ] && codex_confidence=90
  fi

  if [ -n "${OPENCODE:-}" ]; then
    signals=$(append_signal "$signals" "OPENCODE=$OPENCODE")
    found_opencode=1
    [ "$opencode_confidence" -eq 0 ] && opencode_confidence=90
  fi

  if [ -n "${OPENCODE_PID:-}" ]; then
    signals=$(append_signal "$signals" "OPENCODE_PID=$OPENCODE_PID")
    found_opencode=1
    [ "$opencode_confidence" -eq 0 ] && opencode_confidence=85 || opencode_confidence=95
  fi

  if [ -n "${QWEN_CODE:-}" ]; then
    signals=$(append_signal "$signals" "QWEN_CODE=$QWEN_CODE")
    found_qwen=1
    [ "$qwen_confidence" -eq 0 ] && qwen_confidence=90
  fi

  if [ "$found_claude" -eq 0 ]; then
    if [ "$found_codex" -eq 1 ] && [ "$found_opencode" -eq 0 ] && [ "$found_qwen" -eq 0 ]; then
      agent="codex"; confidence=$codex_confidence
    elif [ "$found_opencode" -eq 1 ] && [ "$found_codex" -eq 0 ] && [ "$found_qwen" -eq 0 ]; then
      agent="opencode"; confidence=$opencode_confidence
    elif [ "$found_qwen" -eq 1 ] && [ "$found_codex" -eq 0 ] && [ "$found_opencode" -eq 0 ]; then
      agent="qwen-code"; confidence=$qwen_confidence
    fi
  fi

  printf '%s|%s\n' "$agent" "$confidence"
}

detect_agent() {
  local env_result env_agent env_confidence
  env_result=$(detect_by_env)
  env_agent=$(printf '%s' "$env_result" | cut -d '|' -f 1)
  env_confidence=$(printf '%s' "$env_result" | cut -d '|' -f 2)

  if [ -n "$env_agent" ]; then
    printf '%s|%s|环境变量\n' "$env_agent" "$env_confidence"
  else
    printf 'unknown|0|无匹配信号\n'
  fi
}

# ==============================================================================
# 状态目录
# ==============================================================================

get_state_dir() {
  local skill_name="$1"
  printf '%s\n' "$HOME/.config/${skill_name}/"
}

# ==============================================================================
# 主流程
# ==============================================================================

result=$(detect_agent)
agent=$(printf '%s' "$result" | cut -d '|' -f 1)

runtime_type=$(detect_runtime_type)
os_type=$(detect_os_type "$runtime_type")

state_path="$(get_state_dir "$DEFAULT_SKILL_NAME")"

# 初始化检查：状态目录下是否存在当前 agent 类型的标志文件
# 例如 ~/.config/skill-harness/claude-code
init_flag="${state_path}${agent}"
if [ -f "$init_flag" ]; then
  initialized="true"
else
  initialized="false"
fi

printf 'agent=%s\nos=%s\nstate_dir=%s\ninitialized=%s\n' "$agent" "$os_type" "$state_path" "$initialized"
