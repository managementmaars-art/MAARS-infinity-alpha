#!/usr/bin/env bash
# setup-mcp.sh - search-web 技能 MCP 自动安装脚本
#
# 用法:
#   bash scripts/setup-mcp.sh --mcp context7
#   bash scripts/setup-mcp.sh --mcp exa --api-key "EXA_API_KEY=xxx"
#   bash scripts/setup-mcp.sh --mcp github-fetcher --force
#   bash scripts/setup-mcp.sh --mcp all
#   bash scripts/setup-mcp.sh --agent claude-code --os windows --mcp context7
#
# 必需文件: scripts/detect.sh (同目录下)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="search-web"

# ==============================================================================
# 参数解析
# ==============================================================================

AGENT=""
OS_TYPE=""
MCP_NAME=""
API_KEY=""
SCOPE="user"
FORCE=0
ALL_MCP_LIST="context7 exa mcp-deepwiki github-fetcher"


usage() {
  cat <<'EOF'
用法: setup-mcp.sh [选项]

search-web 技能 MCP 自动安装脚本

选项:
  --agent <类型>     目标 code agent (claude-code|codex|opencode|qwen-code)
                    不传则自动调用 detect.sh 检测
  --os <类型>        目标运行时 OS (windows|linux|macos)
                    不传则自动调用 detect.sh 检测
  --mcp <名称>      MCP 名称 (context7|exa|mcp-deepwiki|github-fetcher|all)
                    必需参数；all 表示安装全部四项
  --api-key <值>     API Key，格式 "ENV_VAR_NAME=value"
                    仅 context7/exa 可选
  --scope <范围>     安装作用域 (user|project)，默认 user
  --force            强制重新安装，忽略检测
  -h                 显示帮助

示例:
  bash scripts/setup-mcp.sh --mcp context7
  bash scripts/setup-mcp.sh --mcp exa --api-key "EXA_API_KEY=xxx"
  bash scripts/setup-mcp.sh --mcp github-fetcher --force
  bash scripts/setup-mcp.sh --mcp all
  bash scripts/setup-mcp.sh --agent claude-code --os windows --mcp context7
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)   AGENT="$2"; shift 2 ;;
    --os)      OS_TYPE="$2"; shift 2 ;;
    --mcp)     MCP_NAME="$2"; shift 2 ;;
    --api-key) API_KEY="$2"; shift 2 ;;
    --scope)   SCOPE="$2"; shift 2 ;;
    --force)   FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage; exit 1 ;;
  esac
done

if [ -z "$MCP_NAME" ]; then
  echo "错误: --mcp 参数是必需的" >&2
  usage
  exit 1
fi

# ==============================================================================
# MCP 注册表
# ==============================================================================

get_npm_package() {
  case "$1" in
    context7)       printf '%s' "@upstash/context7-mcp@latest" ;;
    mcp-deepwiki)   printf '%s' "mcp-deepwiki@latest" ;;
    github-fetcher) printf '%s' "github-fetcher-mcp" ;;
    exa|all)        printf '' ;;
    *)              printf '' ;;
  esac
}

is_remote_mcp() {
  [ "$1" = "exa" ]
}

case "$MCP_NAME" in
  context7|mcp-deepwiki|github-fetcher|exa|all) ;;
  *) echo "错误: 不支持的 MCP 名称: $MCP_NAME（支持: context7|exa|mcp-deepwiki|github-fetcher|all）" >&2; exit 1 ;;
esac

# ==============================================================================
# 环境检测（单次调用 detect.sh）
# ==============================================================================

detect_output="$(bash "$SCRIPT_DIR/detect.sh")"

if [ -z "$AGENT" ]; then
  AGENT="$(printf '%s' "$detect_output" | grep '^agent=' | cut -d= -f2)"
fi
if [ -z "$OS_TYPE" ]; then
  OS_TYPE="$(printf '%s' "$detect_output" | grep '^os=' | cut -d= -f2)"
fi
STATE_DIR="$(printf '%s' "$detect_output" | grep '^state_dir=' | cut -d= -f2-)"

if [ -z "$AGENT" ] || [ "$AGENT" = "unknown" ]; then
  echo "错误: 无法检测当前 code agent 类型，请通过 --agent 参数指定" >&2
  exit 1
fi
if [ -z "$OS_TYPE" ] || [ "$OS_TYPE" = "unknown" ]; then
  echo "错误: 无法检测当前 OS 类型，请通过 --os 参数指定" >&2
  exit 1
fi

echo "Agent: $AGENT"
echo "OS: $OS_TYPE"
echo "状态目录: $STATE_DIR"

# ==============================================================================
# MCP 安装检测（一次 mcp list，grep 变量判断）
# ==============================================================================

# 调用一次 xxx mcp list，结果存变量
# 输出格式：context7: cmd /c npx ... - ✓ Connected
check_mcp_list() {
  local agent="$1"
  case "$agent" in
    claude-code) claude mcp list 2>/dev/null || echo "" ;;
    codex)       codex mcp list 2>/dev/null || echo "" ;;
    opencode)    opencode mcp list 2>/dev/null || echo "" ;;
    qwen-code)   qwen mcp list 2>/dev/null || echo "" ;;
    *)           echo "" ;;
  esac
}

MCP_LIST_OUTPUT=""

# 根据 agent 类型匹配不同的 list 输出格式
# claude/qwen: "name: cmd ..."  codex: 表格首列  opencode: ANSI 树形
is_mcp_installed() {
  local mcp="$1"
  local agent="${2:-$AGENT}"
  case "$agent" in
    claude-code|qwen-code)
      printf '%s' "$MCP_LIST_OUTPUT" | grep -q "^${mcp}:"
      ;;
    codex)
      printf '%s' "$MCP_LIST_OUTPUT" | awk -v mcp="$mcp" 'NR>1 && $1==mcp'
      ;;
    opencode)
      printf '%s' "$MCP_LIST_OUTPUT" | sed 's/\x1b\[[0-9;]*m//g' | grep -qw "$mcp"
      ;;
    *)
      return 1
      ;;
  esac
}

# ==============================================================================
# Credentials 读写（平面文件，零依赖）
# ==============================================================================

read_stored_key() {
  local mcp="$1"
  local key_file="${STATE_DIR}credentials/${mcp}"
  if [ -f "$key_file" ]; then
    local val
    val="$(cat "$key_file")"
    [ "$val" != "skipped" ] && [ -n "$val" ] && printf '%s' "$val" && return 0
  fi
  return 1
}

save_stored_key() {
  local mcp="$1" val="$2"
  mkdir -p "${STATE_DIR}credentials"
  printf '%s' "$val" > "${STATE_DIR}credentials/${mcp}"
}

# ==============================================================================
# 安装命令
# ==============================================================================

is_windows() {
  [ "$OS_TYPE" = "windows" ]
}

install_mcp() {
  local mcp="$1"
  local agent="$2"
  local os="$3"

  if is_remote_mcp "$mcp"; then
    install_remote_mcp "$mcp" "$agent" "$os"
  else
    install_stdio_mcp "$mcp" "$agent" "$os"
  fi
}

install_stdio_mcp() {
  local mcp="$1"
  local agent="$2"
  local os="$3"
  local npm_pkg
  npm_pkg="$(get_npm_package "$mcp")"

  if [ -z "$npm_pkg" ]; then
    echo "错误: 未知 MCP 名称: $mcp" >&2
    exit 1
  fi

  case "$agent" in
    claude-code)
      if is_windows; then
        claude mcp add-json -s "$SCOPE" "$mcp" "{\"type\":\"stdio\",\"command\":\"cmd\",\"args\":[\"/c\",\"npx\",\"-y\",\"$npm_pkg\"]}"
      else
        claude mcp add-json -s "$SCOPE" "$mcp" "{\"type\":\"stdio\",\"command\":\"npx\",\"args\":[\"-y\",\"$npm_pkg\"]}"
      fi
      ;;
    codex)
      if is_windows; then
        codex mcp add "$mcp" -- cmd /c npx -y "$npm_pkg"
      else
        codex mcp add "$mcp" -- npx -y "$npm_pkg"
      fi
      ;;
    opencode)
      echo "OpenCode 无 CLI 命令，需要手动编辑 opencode.json："
      echo ""
      if is_windows; then
        echo "  \"$mcp\": {"
        echo "    \"type\": \"local\","
        echo "    \"command\": [\"cmd\", \"/c\", \"npx\", \"-y\", \"$npm_pkg\"],"
        echo "    \"enabled\": true"
        echo "  }"
      else
        echo "  \"$mcp\": {"
        echo "    \"type\": \"local\","
        echo "    \"command\": [\"npx\", \"-y\", \"$npm_pkg\"],"
        echo "    \"enabled\": true"
        echo "  }"
      fi
      echo ""
      echo "配置文件位置: ~/.config/opencode/opencode.json"
      echo "请在编辑完成后重新运行本脚本进行状态标记更新。"
      ;;
    qwen-code)
      if is_windows; then
        qwen mcp add -s "$SCOPE" -t stdio "$mcp" cmd /c npx -y "$npm_pkg"
      else
        qwen mcp add -s "$SCOPE" -t stdio "$mcp" npx -y "$npm_pkg"
      fi
      ;;
    *)
      echo "错误: 不支持的 agent 类型: $agent" >&2
      exit 1
      ;;
  esac
}

install_remote_mcp() {
  local mcp="$1"
  local agent="$2"
  local os="$3"

  local exa_url="https://mcp.exa.ai/mcp"

  # 优先使用 --api-key 参数，其次从 credentials 文件读取
  if [ -n "$API_KEY" ]; then
    local key_value
    key_value="$(printf '%s' "$API_KEY" | cut -d '=' -f 2-)"
    if [ -n "$key_value" ]; then
      exa_url="https://mcp.exa.ai/mcp?exaApiKey=${key_value}"
    fi
  else
    local stored_key
    if stored_key="$(read_stored_key exa)" && [ -n "$stored_key" ]; then
      exa_url="https://mcp.exa.ai/mcp?exaApiKey=${stored_key}"
      echo "从 credentials 文件读取已存储的 Exa API Key"
    fi
  fi

  case "$agent" in
    claude-code)
      claude mcp add --transport http -s "$SCOPE" exa "$exa_url"
      ;;
    codex)
      codex mcp add exa --url "$exa_url"
      ;;
    opencode)
      echo "OpenCode 无 CLI 命令，需要手动编辑 opencode.json："
      echo ""
      echo "  \"exa\": {"
      echo "    \"type\": \"remote\","
      echo "    \"url\": \"$exa_url\","
      echo "    \"enabled\": true"
      echo "  }"
      echo ""
      echo "配置文件位置: ~/.config/opencode/opencode.json"
      ;;
    qwen-code)
      qwen mcp add -s "$SCOPE" -t http exa "$exa_url"
      ;;
    *)
      echo "错误: 不支持的 agent 类型: $agent" >&2
      exit 1
      ;;
  esac
}

# ==============================================================================
# 标志文件管理
# ==============================================================================

create_init_flag() {
  mkdir -p "$STATE_DIR"
  touch "${STATE_DIR}${AGENT}"
}

# ==============================================================================
# 执行
# ==============================================================================

run_install() {
  local mcp="$1"
  echo "========================================"
  echo "  安装 MCP: $mcp"
  echo "  Agent: $AGENT"
  echo "  OS: $OS_TYPE"
  echo "  Scope: $SCOPE"
  echo "========================================"

  install_mcp "$mcp" "$AGENT" "$OS_TYPE"

  echo ""
  echo "MCP $mcp 安装命令已执行。"
}

if [ "$MCP_NAME" = "all" ]; then
  echo "批量安装模式"
  echo ""

  if [ "$FORCE" -eq 0 ]; then
    # 只调用一次 mcp list
    MCP_LIST_OUTPUT="$(check_mcp_list "$AGENT")"

    for mcp in $ALL_MCP_LIST; do
      if is_mcp_installed "$mcp"; then
        echo "MCP $mcp 已安装，跳过。"
        echo ""
      else
        run_install "$mcp"
        echo ""
      fi
    done
  else
    # --force 模式：跳过检测，全部安装
    for mcp in $ALL_MCP_LIST; do
      run_install "$mcp"
      echo ""
    done
  fi

  create_init_flag
  echo "批量安装完成。请重启 code agent 后验证 MCP 是否可用。"
else
  # 单项安装
  if [ "$FORCE" -eq 0 ]; then
    MCP_LIST_OUTPUT="$(check_mcp_list "$AGENT")"
    if is_mcp_installed "$MCP_NAME"; then
      echo "MCP $MCP_NAME 已安装，跳过。使用 --force 强制重新安装。"
      exit 0
    fi
  fi

  run_install "$MCP_NAME"
  create_init_flag
  echo "请重启 code agent 后验证 MCP 是否可用。"
fi
