#!/bin/bash
# ============================================================================
# Hermes Agent Wrapper Script for WorkBuddy
# ============================================================================
# 统一的 CLI 封装脚本，提供格式化输出、错误处理和超时保护。
#
# 用法:
#   ./hermes_wrapper.sh [命令] [参数...]
#
# 示例:
#   ./hermes_wrapper.sh run "分析这个URL的内容" --timeout 60
#   ./hermes_wrapper.sh memory search "用户偏好"
#   ./hermes_wrapper.sh status
#
# 输出格式: JSON (success, output, error, duration, command)
# ============================================================================

set -euo pipefail

# ============================================================================
# 配置（动态检测，无硬编码路径）
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_CMD="${HERMES_CMD:-hermes}"
# 按优先级搜索 hermes 安装位置
if ! command -v "$HERMES_CMD" &> /dev/null; then
    for candidate in \
        "$HOME/.local/bin/hermes" \
        "$HOME/.local/hermes-agent/.venv/bin/hermes" \
        "$HOME/.workbuddy/binaries/python/envs/default/bin/hermes" \
        "$(which hermes 2>/dev/null)"; do
        if [ -x "$candidate" ]; then
            HERMES_CMD="$candidate"
            break
        fi
    done
fi
DEFAULT_TIMEOUT=300
OUTPUT_MODE="text"  # text | json | raw

# 颜色（终端输出时使用）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================ 
# 工具函数
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

# 检查 Hermes 是否安装
check_hermes() {
    if ! command -v "$HERMES_CMD" &> /dev/null; then
        log_error "Hermes Agent 未找到。"
        log_error "请运行安装脚本: bash scripts/install_hermes.sh"
        log_error "或将 ~/.local/bin 添加到 PATH: export PATH=\"\$HOME/.local/bin:\$PATH\""
        return 1
    fi
    return 0
}

# 执行 hermes 命令并捕获输出
run_hermes() {
    local cmd="$@"
    local start_time=$(date +%s%N 2>/dev/null || date +%s)
    local exit_code=0
    local output=""
    local error=""
    
    # 使用临时文件捕获输出和错误
    local tmp_output=$(mktemp)
    local tmp_error=$(mktemp)
    
    trap 'rm -f "$tmp_output" "$tmp_error"' RETURN
    
    # 执行命令
    set +e
    eval "$cmd" > "$tmp_output" 2> "$tmp_error" &
    local pid=$!
    
    # 等待完成（带超时检查由调用方控制）
    wait $pid 2>/dev/null
    exit_code=$?
    set -e
    
    # 读取输出
    output=$(cat "$tmp_output" 2>/dev/null || true)
    error=$(cat "$tmp_error" 2>/dev/null || true)
    
    # 计算耗时
    local end_time=$(date +%s%N 2>/dev/null || date +%s)
    local duration=0
    if [[ "$start_time" =~ ^[0-9]{13}$ ]] && [[ "$end_time" =~ ^[0-9]{13}$ ]]; then
        duration=$(( (end_time - start_time) / 1000000 )) # 转换为毫秒
    else
        duration=$(( end_time - start_time ))
    fi
    
    # 返回结果
    echo "{\"success\":$([ $exit_code -eq 0 ] && echo "true" || echo "false"),\"output\":$(echo "$output" | jq -Rs . 2>/dev/null || echo "\"$(echo "$output" | sed 's/"/\\"/g' | tr '\n' ' ')\""),\"error\":$(echo "$error" | jq -Rs . 2>/dev/null || echo "\"$(echo "$error" | sed 's/"/\\"/g' | tr '\n' ' ')\""),\"exit_code\":$exit_code,\"duration_ms\":$duration,\"command\":\"$(echo "$cmd" | sed 's/"/\\"/g' | head -c 200)\"}"
}

# JSON 格式输出辅助函数
json_output() {
    local success="$1"
    local output="$2"
    local error="$3"
    local duration="$4"
    local command="$5"
    
    cat << EOF
{
  "success": $success,
  "output": $(echo "$output" | jq -Rs . 2>/dev/null || echo "\"$(echo "$output" | sed 's/"/\\"/g')\""),
  "error": $(echo "$error" | jq -Rs . 2>/dev/null || echo "\"$(echo "$error" | sed 's/"/\\"/g')\""),
  "duration_ms": ${duration:-0},
  "command": "$(echo "${command:-}" | sed 's/"/\\"/g')"
}
EOF
}

# ============================================================================ 
# 命令处理
# ============================================================================

# 处理 'run' 命令（单轮执行）
handle_run() {
    local prompt=""
    local timeout=$DEFAULT_TIMEOUT
    local context_file=""
    local toolset=""
    local model=""
    local no_stream=true
    local non_interactive=true
    local args=()
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --timeout) shift; timeout="${1:-$DEFAULT_TIMEOUT}" ;;
            --context-file|-c) shift; context_file="$1" ;;
            --toolset|-t) shift; toolset="$1" ;;
            --model|-m) shift; model="$1" ;;
            --no-stream) no_stream=true ;;
            --stream) no_stream=false ;;
            --non-interactive) non_interactive=true ;;
            --interactive) non_interactive=false ;;
            -*|*) args+=("$1") ;;  # 收集其他参数作为 prompt 或选项
        esac
        shift
    done
    
    # 第一个非选项参数是 prompt
    if [ ${#args[@]} -gt 0 ] && [[ ! "${args[0]}" == -* ]]; then
        prompt="${args[0]}"
    fi
    
    if [ -z "$prompt" ]; then
        json_output false "" "缺少必需的 prompt 参数。用法: hermes_wrapper.sh run \"你的提示词\"" 0 "run"
        return 1
    fi
    
    log_info "执行 Hermes run: $prompt"
    log_info "超时: ${timeout}s, 工具集: ${toolset:-默认}"
    
    # 构建命令
    local cmd="$HERMES_CMD run \"$prompt\" --non-interactive"
    [ "$no_stream" = true ] && cmd+=" --no-stream"
    [ -n "$context_file" ] && cmd+=" --context-file \"$context_file\""
    [ -n "$toolset" ] && cmd+=" --toolset \"$toolset\""
    [ -n "$model" ] && cmd+=" --model \"$model\""
    cmd+=" --timeout $timeout"
    
    # 带超时执行
    local result
    result=$(timeout $timeout bash -c "$cmd" 2>&1) || true
    
    local exit_code=$?
    
    if [ $exit_code -eq 124 ]; then
        json_output false "" "命令超时 (${timeout}s)" "$timeout" "hermes run"
    elif [ $exit_code -ne 0 ]; then
        json_output false "$result" "命令失败，退出码: $exit_code" 0 "hermes run"
    else
        json_output true "$result" "" 0 "hermes run"
    fi
}

# 处理 'memory' 命令
handle_memory() {
    local subcmd="${1:-}"
    shift 2>/dev/null || true
    
    case "$subcmd" in
        search)
            local query="${1:-}"
            if [ -z "$query" ]; then
                json_output false "" "缺少搜索关键词。用法: hermes_wrapper.sh memory search \"关键词\"" 0 "memory search"
                return 1
            fi
            log_info "搜索记忆: $query"
            run_hermes "$HERMES_CMD memory search \"$query\""
            ;;
        list|notes)
            log_info "列出记忆笔记"
            run_hermes "$HERMES_CMD memory notes list"
            ;;
        add)
            local note="${1:-}"
            if [ -z "$note" ]; then
                json_output false "" "缺少笔记内容。用法: hermes_wrapper.sh memory add \"内容\"" 0 "memory add"
                return 1
            fi
            log_info "添加记忆笔记"
            run_hermes "$HERMES_CMD memory notes add \"$note\""
            ;;
        export)
            local path="${1:-./memory_backup}"
            log_info "导出记忆到: $path"
            run_hermes "$HERMES_CMD memory export \"$path\""
            ;;
        import)
            local path="${1:-}"
            if [ -z "$path" ]; then
                json_output false "" "缺少导入路径。用法: hermes_wrapper.sh memory import ./path" 0 "memory import"
                return 1
            fi
            log_info "从路径导入记忆: $path"
            run_hermes "$HERMES_CMD memory import \"$path\""
            ;;
        *)
            json_output false "" "未知的 memory 子命令: $subcmd. 可用: search, list, add, export, import" 0 "memory"
            return 1
            ;;
    esac
}

# 处理 'skills' 命令
handle_skills() {
    local subcmd="${1:-list}"
    shift 2>/dev/null || true
    
    case "$subcmd" in
        list|ls)
            log_info "列出所有技能"
            run_hermes "$HERMES_CMD skills list"
            ;;
        create)
            local name="${1:-}"
            local desc="${2:-}"
            if [ -z "$name" ]; then
                json_output false "" "缺少技能名称。用法: hermes_wrapper.sh skills create 名称 [--description 描述]" 0 "skills create"
                return 1
            fi
            log_info "创建技能: $name"
            if [ -n "$desc" ]; then
                run_hermes "$HERMES_CMD skills create \"$name\" --description \"$desc\""
            else
                run_hermes "$HERMES_CMD skills create \"$name\""
            fi
            ;;
        edit)
            local name="${1:-}"
            if [ -z "$name" ]; then
                json_output false "" "缺少技能名称。用法: hermes_wrapper.sh skills edit 名称" 0 "skills edit"
                return 1
            fi
            log_info "编辑技能: $name"
            run_hermes "$HERMES_CMD skills edit \"$name\""
            ;;
        remove|rm|delete)
            local name="${1:-}"
            if [ -z "$name" ]; then
                json_output false "" "缺少技能名称。用法: hermes_wrapper.sh skills remove 名称" 0 "skills remove"
                return 1
            fi
            log_warn "删除技能: $name"
            run_hermes "$HERMES_CMD skills remove \"$name\""
            ;;
        *)
            json_output false "" "未知的 skills 子命令: $subcmd. 可用: list, create, edit, remove" 0 "skills"
            return 1
            ;;
    esac
}

# 处理 'delegate' 命令（委托给子代理）
handle_delegate() {
    local task=""
    local tools=""
    local timeout=300
    local output_file=""
    local max_concurrent=3
    local context_file=""
    local verbose=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --task|-t) shift; task="$1" ;;
            --tools|--toolset) shift; tools="$1" ;;
            --timeout) shift; timeout="$1" ;;
            --output|-o) shift; output_file="$1" ;;
            --max-concurrent) shift; max_concurrent="$1" ;;
            --context-file|-c) shift; context_file="$1" ;;
            -v|--verbose) verbose=true ;;
            *) 
                if [ -z "$task" ]; then
                    task="$1"
                fi
                ;;
        esac
        shift
    done
    
    if [ -z "$task" ]; then
        cat << EOF
{
  "success": false,
  "output": "",
  "error": "缺少必需的任务描述。用法:\n  hermes_wrapper.sh delegate --task \"任务描述\" [选项]\n\n选项:\n  --task, -t     任务描述（必需）\n  --tools       限制的工具集（逗号分隔）\n  --timeout      超时时间（秒，默认300）\n  --output, -o   输出文件路径\n  --max-concurrent  最大并发数（默认3）\n  --context-file 上下文文件\n  -v, --verbose  详细输出",
  "duration_ms": 0,
  "command": "delegate"
}
EOF
        return 1
    fi
    
    log_info "委托任务: $task"
    [ "$verbose" = true ] && log_info "工具限制: ${tools:-无}, 超时: ${timeout}s"
    
    # 构建提示词
    local prompt="请使用 delegate_task 工具完成以下任务：\n\n任务: $task"
    [ -n "$tools" ] && prompt+="\n可用工具: $tools"
    prompt+="\n\n请直接执行任务并返回完整结果。"
    
    # 构建命令
    local cmd="$HERMES_CMD run \"$prompt\" --non-interactive --no-stream --timeout $timeout"
    [ -n "$context_file" ] && cmd+=" --context-file \"$context_file\""
    [ -n "$tools" ] && cmd+=" --toolset \"$tools\""
    
    # 执行
    local result
    result=$(timeout $timeout bash -c "$cmd" 2>&1) || true
    local exit_code=$?
    
    # 如果指定了输出文件，写入文件
    if [ -n "$output_file" ]; then
        mkdir -p "$(dirname "$output_file")" 2>/dev/null || true
        echo "$result" > "$output_file" 2>/dev/null || true
    fi
    
    if [ $exit_code -eq 124 ]; then
        json_output false "$result" "委托任务超时 (${timeout}s)" "$timeout" "delegate"
    elif [ $exit_code -ne 0 ]; then
        json_output false "$result" "委托任务失败，退出码: $exit_code" 0 "delegate"
    else
        json_output true "$result" "" 0 "delegate"
    fi
}

# 处理 'status' 和 'doctor' 命令
handle_status() {
    log_info "检查 Hermes 状态..."
    run_hermes "$HERMES_CMD status" 2>/dev/null || run_hermes "$HERMES_CMD doctor"
}

# 处理 'plugins' 命令
handle_plugins() {
    local subcmd="${1:-list}"
    shift 2>/dev/null || true
    run_hermes "$HERMES_CMD plugins $subcmd $*"
}

# 处理 'cron' 命令
handle_cron() {
    local subcmd="${1:-list}"
    shift 2>/dev/null || true
    run_hermes "$HERMES_CMD cron $subcmd $*"
}

# 显示帮助信息
show_help() {
    cat << 'EOF'
Hermes Agent Wrapper Script v1.0.0
===============================

用法:
  hermes_wrapper.sh <command> [options]

命令:
  run          单轮执行（推荐用于 WorkBuddy 集成）
  delegate     委托任务给子代理
  memory       记忆管理（search/list/add/export/import）
  skills       技能管理（list/create/edit/remove）
  plugins      插件管理
  cron         定时任务管理
  status       检查状态
  doctor       运行诊断
  help         显示此帮助信息

示例:
  hermes_wrapper.sh run "分析这个网页的内容" --timeout 60
  hermes_wrapper.sh delegate --t "研究竞品产品" --tools web_search,browser
  hermes_wrapper.sh memory search "用户偏好设置"
  hermes_wrapper.sh skills list
  hermes_wrapper.sh status

环境变量:
  HERMES_CMD     Hermes 命令路径（默认: 自动检测）
  DEFAULT_TIMEOUT 默认超时时间秒数（默认: 300）

输出格式: JSON (包含 success, output, error, duration_ms, command 字段)
EOF
}

# ============================================================================ 
# 主程序
# ============================================================================

main() {
    local command="${1:-help}"
    shift 2>/dev/null || true
    
    # 检查是否需要 Hermes（help 和 version 不需要）
    if [[ ! "$command" =~ ^(help|--help|-h|version|--version)$ ]]; then
        check_hermes || exit 1
    fi
    
    # 分发命令
    case "$command" in
        run|r) handle_run "$@" ;;
        delegate|d) handle_delegate "$@" ;;
        memory|m) handle_memory "$@" ;;
        skills|skill|s) handle_skills "$@" ;;
        plugins|p) handle_plugins "$@" ;;
        cron|c) handle_cron "$@" ;;
        status|st) handle_status ;;
        doctor|diag) run_hermes "$HERMES_CMD doctor" ;;
        help|--help|-h) show_help ;;
        version|--version|-v) run_hermes "$HERMES_CMD --version" ;;
        *)
            json_output false "" "未知命令: $command。运行 'hermes_wrapper.sh help' 查看帮助。" 0 "$command"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
