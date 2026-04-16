#!/bin/bash
# ============================================================================
# Hermes Agent Delegate Script for WorkBuddy
# ============================================================================
# 子代理委托专用脚本，支持：
# - 任务描述注入和格式化
# - 工具集限制（减少 Token 消耗）
# - 超时控制和自动终止
# - 输出解析和结构化返回
# - 并发管理（上限3个，符合 Hermes 限制）
# - 错误回调接口（集成 Self-Improving Agent CN）
#
# 用法:
#   ./hermes_delegate.sh --task "任务描述" [选项]
#
# 示例:
#   ./hermes_delegate.sh \
#     --task "分析竞品A和B的产品特性差异" \
#     --tools "web_search,browser,file_write" \
#     --timeout 300 \
#     --output ./result.md
# ============================================================================

set -euo pipefail

# ============================================================================
# 配置常量（动态检测，无硬编码路径）
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_CMD="${HERMES_CMD:-hermes}"
# 动态搜索 hermes 命令
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
MAX_CONCURRENT_DELEGATES=3
# 使用用户目录下的临时目录（而非 /tmp，更可靠）
LOCK_DIR="${TMPDIR:-/tmp}/hermes_delegates_$(id -u)"
SELF_IMPROVING_MEMORY="${HOME}/.workbuddy/memory/self-improving/learnings.jsonl"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================================
# 日志函数
# ============================================================================
log_info()    { echo -e "${BLUE}[DELEGATE-INFO]${NC} $(date '+%H:%M:%S') $*" >&2; }
log_success() { echo -e "${GREEN}[DELEGATE-SUCCESS]${NC} $*" >&2; }
log_error()   { echo -e "${RED}[DELEGATE-ERROR]${NC} $*" >&2; }
log_warn()    { echo -e "${YELLOW}[DELEGATE-WARN]${NC} $*" >&2; }
log_debug()   { [[ "${DEBUG:-false}" == "true" ]] && echo -e "${MAGENTA}[DEBUG]${NC} $*" >&2 || true; }

# ============================================================================
# 工具函数
# ============================================================================

# 检查依赖
check_dependencies() {
    log_debug "检查依赖..."
    
    if ! command -v "$HERMES_CMD" &> /dev/null; then
        log_error "Hermes 命令未找到: $HERMES_CMD"
        return 1
    fi
    
    if ! command -v timeout &> /dev/null; then
        log_warn "timeout 命令不可用，将使用后台进程方式处理超时"
    fi
    
    log_debug "依赖检查通过"
    return 0
}

# 创建锁文件用于并发控制
acquire_lock() {
    local task_id="$1"
    mkdir -p "$LOCK_DIR"
    
    # 检查当前运行的 delegate 数量
    local current_count=$(find "$LOCK_DIR" -name "*.lock" -type f 2>/dev/null | wc -l | tr -d ' ')
    
    if [ "$current_count" -ge "$MAX_CONCURRENT_DELEGATES" ]; then
        log_error "已达到最大并发数 ($MAX_CONCURRENT_DELEGATES)，当前运行: $current_count 个任务"
        return 1
    fi
    
    # 创建锁文件
    local lock_file="$LOCK_DIR/${task_id}.lock"
    echo "$(date +%s)" > "$lock_file"
    echo "$task_id" >> "$lock_file"
    
    log_debug "获取锁: $lock_file (当前: $((current_count + 1))/$MAX_CONCURRENT_DELEGATES)"
    return 0
}

# 释放锁
release_lock() {
    local task_id="$1"
    local lock_file="$LOCK_DIR/${task_id}.lock"
    rm -f "$lock_file" 2>/dev/null || true
    log_debug "释放锁: $lock_file"
}

# 清理所有过期锁（超过1小时的视为过期）
cleanup_stale_locks() {
    local now=$(date +%s)
    find "$LOCK_DIR" -name "*.lock" -type f -mmin +60 -delete 2>/dev/null || true
}

# 生成唯一任务ID
generate_task_id() {
    echo "delegate_$(date '+%Y%m%d_%H%M%S')_$$_${RANDOM}"
}

# 构建委托提示词
build_delegate_prompt() {
    local task="$1"
    local tools="${2:-}"
    local context_content="${3:-}"
    local constraints="${4:-}"
    
    local prompt=""
    
    prompt+="你是一个专业的子代理。请使用 delegate_task 工具完成以下任务。\n\n"
    prompt+="## 任务描述\n\n$task\n\n"
    
    if [ -n "$tools" ]; then
        prompt+="## 可用工具限制\n\n"
        prompt+="本次任务仅可使用以下工具：$tools\n\n"
    fi
    
    if [ -n "$context_content" ]; then
        prompt+="## 额外上下文\n\n$context_content\n\n"
    fi
    
    if [ -n "$constraints" ]; then
        prompt+="## 执行约束\n\n$constraints\n\n"
    fi
    
    prompt+="## 输出要求\n\n"
    prompt+="- 请直接执行任务并返回完整结果\n"
    prompt+="- 结果应包含关键发现、数据或结论\n"
    prompt+="- 如果遇到错误，请详细说明错误原因\n"
    prompt+="- 使用 Markdown 格式组织输出\n"
    
    echo -e "$prompt"
}

# 解析输出结果（提取关键信息）
parse_output() {
    local raw_output="$1"
    local output_file="${2:-}"
    
    # 如果指定了输出文件，写入原始输出
    if [ -n "$output_file" ]; then
        mkdir -p "$(dirname "$output_file")" 2>/dev/null || true
        echo -e "$raw_output" > "$output_file"
        log_success "结果已保存到: $output_file"
    fi
    
    # 返回原始输出（由调用方决定是否解析）
    echo -e "$raw_output"
}

# 错误回调：记录到 Self-Improving 记录
error_callback() {
    local error_type="$1"
    local error_message="$2"
    local task_description="${3:-}"
    local original_command="${4:-}"
    
    log_info "触发错误回调 (Self-Improving)..."
    
    # 确保目录存在
    mkdir -p "$(dirname "$SELF_IMPROVING_MEMORY")" 2>/dev/null || true
    
    # 检查 jq 是否可用
    if ! command -v jq &> /dev/null; then
        log_warn "jq 不可用，跳过 Self-Improving 记录"
        return 0
    fi
    
    # 构建 JSONL 记录
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local record=$(cat << EOF
{
  "timestamp": "$timestamp",
  "error_type": "$error_type",
  "error_message": $(echo "$error_message" | jq -Rs .),
  "task": $(echo "$task_description" | jq -Rs .),
  "command": $(echo "$original_command" | jq -Rs .),
  "source": "hermes-delegate",
  "context": {
    "hermes_version": "$($HERMES_CMD --version 2>/dev/null | head -1 || echo "unknown")",
    "platform": "$(uname -s)",
    "user": "$(whoami)"
  },
  "lesson": "TODO: 待分析此错误的根本原因和解决方案"
}
EOF
)
    
    # 追加到记录文件
    echo "$record" >> "$SELF_IMPROVING_MEMORY" 2>/dev/null || {
        log_warn "无法写入 Self-Improving 记录文件"
        return 0
    }
    
    log_success "错误记录已保存到: $SELF_IMPROVING_MEMORY"
    return 0
}

# 格式化 JSON 输出
format_json_result() {
    local success="$1"
    local output="$2"
    local error="$3"
    local duration_ms="$4"
    local task_id="$5"
    local output_path="$6"
    
    cat << EOF
{
  "success": $success,
  "task_id": "$task_id",
  "output": $(echo "$output" | jq -Rs . 2>/dev/null || echo "\"$(echo "$output" | head -c 1000 | sed 's/"/\\"/g' | tr '\n' ' ')\""),
  "error": $(echo "$error" | jq -Rs . 2>/dev/null || echo "\"$(echo "$error" | sed 's/"/\\"/g' | tr '\n' ' ')\""),
  "duration_ms": ${duration_ms:-0},
  "output_file": "${output_path:-}",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "hermes_version": "$($HERMES_CMD --version 2>/dev/null | head -1 || echo "unknown")"
}
EOF
}

# ============================================================================
# 主执行函数
# ============================================================================
execute_delegate() {
    local task="$1"
    local tools="$2"
    local timeout_sec="$3"
    local context_file="$4"
    local output_file="$5"
    local max_concurrent="$6"
    local verbose="$7"
    
    # 生成任务 ID
    local task_id
    task_id=$(generate_task_id)
    
    log_info "========== 开始委托任务 =========="
    log_info "任务 ID: $task_id"
    log_info "任务内容: $task"
    [ -n "$tools" ] && log_info "工具限制: $tools"
    log_info "超时设置: ${timeout_sec}s"
    [ -n "$output_file" ] && log_info "输出文件: $output_file"
    log_info "======================================="
    
    # 清理过期锁
    cleanup_stale_locks
    
    # 获取并发锁
    if ! acquire_lock "$task_id"; then
        error_callback "CONCURRENT_LIMIT_REACHED" "达到最大并发限制 ($max_concurrent)" "$task" "hermes_delegate"
        format_json_result false "" "并发限制: 无法获取执行锁，已有 $max_concurrent 个任务在运行。稍后重试。" 0 "$task_id" "$output_file"
        return 1
    fi
    
    # 确保退出时释放锁
    trap 'release_lock "$task_id"' EXIT
    
    # 读取上下文文件（如果存在）
    local context_content=""
    if [ -n "$context_file" ] && [ -f "$context_file" ]; then
        context_content=$(cat "$context_file")
        log_debug "已加载上下文文件: $context_file ($(wc -c < "$context_file") bytes)"
    fi
    
    # 构建提示词
    local prompt
    prompt=$(build_delegate_prompt "$task" "$tools" "$context_content" "")
    
    [ "$verbose" = true ] && log_debug "生成的提示词:\n$prompt"
    
    # 构建命令
    local cmd="$HERMES_CMD run '$prompt' --non-interactive --no-stream --timeout $timeout_sec"
    [ -n "$tools" ] && cmd+=" --toolset '$tools'"
    [ -n "$context_file" ] && cmd+=" --context-file '$context_file'"
    
    log_info "执行命令: hermes run <prompt> --non-interactive --no-stream --timeout $timeout_sec"
    
    # 记录开始时间
    local start_time=$(date +%s%N 2>/dev/null || date +%s)
    
    # 执行命令（带超时保护）
    local raw_output=""
    local exit_code=0
    
    if command -v timeout &> /dev/null; then
        raw_output=$(timeout "$timeout_sec" bash -c "$cmd" 2>&1) || exit_code=$?
    else
        # fallback: 使用后台进程 + 等待
        raw_output=$(bash -c "$cmd" 2>&1) &
        local pid=$!
        
        # 等待完成（带手动超时检查）
        local waited=0
        while kill -0 $pid 2>/dev/null; do
            sleep 5
            waited=$((waited + 5))
            if [ "$waited" -ge "$timeout_sec" ]; then
                kill -9 $pid 2>/dev/null || true
                exit_code=124  # timeout exit code
                break
            fi
        done
        
        [ $exit_code -eq 0 ] && wait $pid 2>/dev/null || exit_code=$?
        raw_output=$(cat "${TMPDIR:-/tmp}/hermes_delegate_out_$$" 2>/dev/null || true)
    fi
    
    # 计算耗时
    local end_time=$(date +%s%N 2>/dev/null || date +%s)
    local duration_ms=0
    if [[ "$start_time" =~ ^[0-9]{13}$ ]] && [[ "$end_time" =~ ^[0-9]{13}$ ]]; then
        duration_ms=$(( (end_time - start_time) / 1000000 ))
    else
        duration_ms=$(( (end_time - start_time) * 1000 ))
    fi
    
    # 处理结果
    case $exit_code in
        0)
            log_success "任务完成 (${duration_ms}ms)"
            
            # 解析并可能写入文件
            parse_output "$raw_output" "$output_file" >/dev/null
            
            format_json_result true "$raw_output" "" "$duration_ms" "$task_id" "$output_file"
            ;;
        124)
            log_error "任务超时 (${timeout_sec}s)"
            
            error_callback "TIMEOUT" "任务执行超时 (${timeout_sec}s): $task" "$task" "$cmd"
            format_json_result false "" "任务超时: 已等待 ${timeout_sec}s 但任务未完成。建议: 1) 简化任务范围, 2) 增加 --timeout 参数, 3) 减少工具集以降低复杂度。" "$duration_ms" "$task_id" "$output_file"
            ;;
        *)
            log_error "任务失败 (退出码: $exit_code)"
            [ "$verbose" = true ] && log_error "错误输出: $raw_output"
            
            error_callback "EXECUTION_ERROR" "命令失败 (退出码: $exit_code): ${raw_output:0:500}" "$task" "$cmd"
            format_json_result false "$raw_output" "执行失败 (退出码 $exit_code)。可能原因: API Key 无效、网络问题、模型不支持等。运行 \`hermes doctor\` 诊断。" "$duration_ms" "$task_id" "$output_file"
            ;;
    esac
    
    # 释放锁
    release_lock "$task_id"
    trap - EXIT
    
    return $exit_code
}

# ============================================================================
# 参数解析
# ============================================================================
show_help() {
    cat << 'EOF'
Hermes Agent Delegate Script v1.0.0
===================================

用法:
  hermes_delegate.sh --task "任务描述" [选项]

必需选项:
  --task, -t       任务描述（必需）

可选选项:
  --tools, --toolset   限制的工具集（逗号分隔）
                        可用值: web_search, browser, file_operations,
                                terminal, memory, code_execution 等
  --timeout            超时时间（秒，默认: 300）
  --output, -o         输出文件路径（保存原始输出）
  --max-concurrent     最大并发数（默认: 3，最大: 3）
  --context-file, -c   额外上下文文件路径
  -v, --verbose        显示详细调试信息
  --dry-run            只显示将要执行的命令，不实际执行
  -h, --help           显示帮助信息

示例:
  # 基础用法
  hermes_delegate.sh --t "研究 React 和 Vue 的性能对比"

  # 限制工具和超时
  hermes_delegate.sh -t "分析网站 SEO 问题" \
    --tools web_search,browser \
    --timeout 120

  # 带输出文件
  hermes_delegate.sh -t "编写单元测试" \
    --tools file_operations,code_execution,terminal \
    --output ./test_results.md

  # 带上下文文件
  hermes_delegate.sh -t "根据代码审查反馈修改" \
    -c ./review_comments.md \
    -o ./changes.md

环境变量:
  HERMES_CMD              Hermes 命令名称（默认: hermes）
  MAX_CONCURRENT_DELEGATES 最大并发数覆盖（默认: 3）

输出格式:
  JSON (包含 success, task_id, output, error, duration_ms, output_file 字段)

错误回调:
  当任务失败或超时时，自动记录到 Self-Improving 记录文件:
  ~/.workbuddy/memory/self-improving/learnings.jsonl

限制:
  - 最大并发子代理数: 3（Hermes 内部限制）
  - 最小超时时间: 10 秒
  - 最大超时时间: 3600 秒（1小时）
EOF
}

# ============================================================================
# 入口点
# ============================================================================
main() {
    # 默认值
    local task=""
    local tools=""
    local timeout=$DEFAULT_TIMEOUT
    local output_file=""
    local max_concurrent=$MAX_CONCURRENT_DELEGATES
    local context_file=""
    local verbose=false
    local dry_run=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --task|-t)
                shift; task="$1"
                ;;
            --tools|--toolset)
                shift; tools="$1"
                ;;
            --timeout)
                shift
                # 验证超时值
                if [[ "$1" =~ ^[0-9]+$ ]] && [ "$1" -ge 10 ] && [ "$1" -le 3600 ]; then
                    timeout="$1"
                else
                    log_error "无效的超时值: $1 (允许范围: 10-3600秒)"
                    exit 1
                fi
                ;;
            --output|-o)
                shift; output_file="$1"
                ;;
            --max-concurrent)
                shift
                if [[ "$1" =~ ^[0-9]+$ ]] && [ "$1" -ge 1 ] && [ "$1" -le 3 ]; then
                    max_concurrent="$1"
                else
                    log_error "无效的并发数: $1 (允许范围: 1-3)"
                    exit 1
                fi
                ;;
            --context-file|-c)
                shift; context_file="$1"
                ;;
            -v|--verbose)
                verbose=true
                export DEBUG="true"
                ;;
            --dry-run)
                dry_run=true
                ;;
            -h|--help|--version)
                show_help
                exit 0
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                # 第一个非选项参数作为 task
                if [ -z "$task" ]; then
                    task="$1"
                else
                    log_warn "忽略多余参数: $1"
                fi
                ;;
        esac
        shift
    done
    
    # 验证必需参数
    if [ -z "$task" ]; then
        log_error "缺少必需的 --task 参数"
        echo ""
        show_help
        exit 1
    fi
    
    # Dry run 模式
    if [ "$dry_run" = true ]; then
        log_info "[DRY RUN] 将要执行的委托任务:"
        log_info "  任务: $task"
        log_info "  工具限制: ${tools:-无限制}"
        log_info "  超时: ${timeout}s"
        log_info "  输出文件: ${output_file:-无}"
        log_info "  上下文文件: ${context_file:-无}"
        log_info "  最大并发: $max_concurrent"
        exit 0
    fi
    
    # 检查依赖
    check_dependencies || exit 1
    
    # 执行委托
    execute_delegate "$task" "$tools" "$timeout" "$context_file" "$output_file" "$max_concurrent" "$verbose"
}

# 执行主函数
main "$@"
