#!/bin/bash
# ============================================================================
# Hermes Agent 一键安装脚本（通用可移植版）
# ============================================================================
# 支持 macOS 和 Linux，自动检测系统环境并完成安装。
#
# 用法:
#   ./install_hermes.sh              # 完整安装
#   ./install_hermes.sh --skip-deps  # 跳过系统依赖检查
#   ./install_hermes.sh --prefix ~/local  # 自定义安装前缀
#
# 安装内容:
#   1. 检查 Python 3.11+ 环境
#   2. 创建 Python 虚拟环境
#   3. 从 GitHub 克隆 Hermes Agent
#   4. 安装依赖并创建 CLI 入口
#   5. 初始化配置目录
#   6. 验证安装
# ============================================================================

set -euo pipefail

# ============================================================================
# 配置
# ============================================================================
INSTALL_DIR="${HERMES_INSTALL_DIR:-$HOME/.local/hermes-agent}"
VENV_DIR="$INSTALL_DIR/.venv"
BIN_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.hermes"
REPO_URL="https://github.com/NousResearch/hermes-agent.git"
REPO_BRANCH="main"
SKIP_DEPS=false

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================================
# 日志
# ============================================================================
log_info()    { echo -e "${BLUE}[INSTALL]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }

# ============================================================================
# 参数解析
# ============================================================================
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-deps) SKIP_DEPS=true; shift ;;
        --prefix) shift; INSTALL_DIR="$1/hermes-agent"; VENV_DIR="$INSTALL_DIR/.venv"; shift ;;
        --help|-h)
            echo "用法: $0 [--skip-deps] [--prefix DIR]"
            echo ""
            echo "选项:"
            echo "  --skip-deps    跳过系统依赖检查"
            echo "  --prefix DIR   自定义安装前缀（默认: ~/.local）"
            echo "  -h, --help     显示帮助"
            exit 0
            ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
done

# ============================================================================
# 步骤 1: 检查系统依赖
# ============================================================================
check_system_deps() {
    log_info "检查系统依赖..."

    # Python
    local python_cmd=""
    for cmd in python3.11 python3.12 python3.13 python3 python; do
        if command -v "$cmd" &> /dev/null; then
            local ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
            local major=$(echo "$ver" | cut -d. -f1)
            local minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
                python_cmd="$cmd"
                break
            fi
        fi
    done

    if [ -z "$python_cmd" ]; then
        log_error "需要 Python 3.11+，但未找到。"
        log_error "请先安装 Python 3.11+:"
        log_error "  macOS: brew install python@3.11"
        log_error "  Linux: sudo apt install python3.11 python3.11-venv"
        log_error "  或使用 pyenv: pyenv install 3.11.15"
        return 1
    fi
    log_success "Python: $($python_cmd --version)"

    # Git
    if ! command -v git &> /dev/null; then
        log_error "需要 git 但未找到。"
        log_error "  macOS: xcode-select --install"
        log_error "  Linux: sudo apt install git"
        return 1
    fi
    log_success "Git: $(git --version)"

    # pip
    if ! $python_cmd -m pip --version &> /dev/null; then
        log_warn "pip 不可用，将尝试安装..."
        $python_cmd -m ensurepip --upgrade 2>/dev/null || {
            log_error "无法安装 pip，请手动安装。"
            return 1
        }
    fi
    log_success "pip: $($python_cmd -m pip --version)"

    export PYTHON_CMD="$python_cmd"
    return 0
}

# ============================================================================
# 步骤 2: 克隆/更新仓库
# ============================================================================
clone_repo() {
    log_info "安装 Hermes Agent 到 $INSTALL_DIR..."

    if [ -d "$INSTALL_DIR/.git" ]; then
        log_info "检测到已有安装，执行更新..."
        cd "$INSTALL_DIR"
        git pull --ff-only 2>/dev/null || {
            log_warn "更新失败，将使用现有版本继续。"
        }
    else
        # 备份已有目录（非 git 仓库）
        if [ -d "$INSTALL_DIR" ]; then
            log_warn "备份现有目录: ${INSTALL_DIR}.bak"
            mv "$INSTALL_DIR" "${INSTALL_DIR}.bak"
        fi

        git clone --depth 1 --branch "$REPO_BRANCH" "$REPO_URL" "$INSTALL_DIR" || {
            log_error "克隆失败，请检查网络连接。"
            return 1
        }
    fi

    log_success "Hermes Agent 源码就绪"
    return 0
}

# ============================================================================
# 步骤 3: 创建虚拟环境并安装依赖
# ============================================================================
setup_venv() {
    log_info "创建 Python 虚拟环境..."

    if [ -d "$VENV_DIR" ]; then
        log_info "虚拟环境已存在，跳过创建。"
    else
        "$PYTHON_CMD" -m venv "$VENV_DIR" || {
            log_error "创建虚拟环境失败。"
            log_error "Debian/Ubuntu 可能需要: sudo apt install python3.11-venv"
            return 1
        }
    fi

    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"

    log_info "升级 pip..."
    pip install --upgrade pip --quiet 2>/dev/null

    log_info "安装 Hermes 依赖..."
    if [ -f "$INSTALL_DIR/requirements.txt" ]; then
        pip install -r "$INSTALL_DIR/requirements.txt --quiet 2>/dev/null
    elif [ -f "$INSTALL_DIR/pyproject.toml" ]; then
        pip install -e "$INSTALL_DIR" --quiet 2>/dev/null
    else
        # 尝试直接安装
        pip install hermes-agent --quiet 2>/dev/null || {
            log_warn "pip install hermes-agent 失败，尝试从源码安装..."
            cd "$INSTALL_DIR"
            pip install . --quiet 2>/dev/null || {
                log_error "安装依赖失败。请手动运行:"
                log_error "  source $VENV_DIR/bin/activate"
                log_error "  cd $INSTALL_DIR && pip install -e ."
                return 1
            }
        }
    fi

    log_success "依赖安装完成"
    return 0
}

# ============================================================================
# 步骤 4: 创建 CLI 入口
# ============================================================================
create_cli_entry() {
    log_info "创建 CLI 入口..."

    mkdir -p "$BIN_DIR"

    local cli_script="$BIN_DIR/hermes"

    cat > "$cli_script" << 'CLISCRIPT'
#!/bin/bash
# Hermes Agent CLI 入口（自动生成）
# 由 install_hermes.sh 创建，请勿手动修改。

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 尝试检测安装位置
if [ -z "${HERMES_INSTALL_DIR:-}" ]; then
    # 按优先级搜索
    for candidate in \
        "$HOME/.local/hermes-agent" \
        "$HOME/.hermes-agent" \
        "/opt/hermes-agent" \
        "/tmp/hermes-agent"; do
        if [ -f "$candidate/hermes" ] || [ -f "$candidate/src/hermes/__main__.py" ]; then
            export HERMES_INSTALL_DIR="$candidate"
            break
        fi
    done
fi

if [ -z "${HERMES_INSTALL_DIR:-}" ]; then
    echo "Error: Hermes Agent 未找到。请运行 install_hermes.sh 重新安装。" >&2
    exit 1
fi

# 激活虚拟环境并运行
VENV_DIR="$HERMES_INSTALL_DIR/.venv"

if [ -d "$VENV_DIR/bin" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "Error: 虚拟环境不存在: $VENV_DIR" >&2
    echo "请运行 install_hermes.sh 重新安装。" >&2
    exit 1
fi

# 运行 hermes
if [ -f "$HERMES_INSTALL_DIR/hermes" ]; then
    python "$HERMES_INSTALL_DIR/hermes" "$@"
elif [ -f "$HERMES_INSTALL_DIR/src/hermes/__main__.py" ]; then
    python -m hermes "$@"
else
    # 尝试作为已安装的 Python 包运行
    if command -v hermes &> /dev/null; then
        hermes "$@"
    else
        echo "Error: 无法找到 Hermes 入口点。" >&2
        exit 1
    fi
fi
CLISCRIPT

    chmod +x "$cli_script"
    log_success "CLI 入口: $cli_script"
    return 0
}

# ============================================================================
# 步骤 5: 初始化配置
# ============================================================================
init_config() {
    log_info "初始化配置目录..."

    mkdir -p "$CONFIG_DIR"
    mkdir -p "$CONFIG_DIR/cron"
    mkdir -p "$CONFIG_DIR/sessions"
    mkdir -p "$CONFIG_DIR/logs"
    mkdir -p "$CONFIG_DIR/skills"
    mkdir -p "$CONFIG_DIR/memories"

    # 创建默认 .env（如果不存在）
    if [ ! -f "$CONFIG_DIR/.env" ]; then
        cat > "$CONFIG_DIR/.env" << 'ENVFILE'
# =============================================================================
# Hermes Agent 环境变量配置
# =============================================================================
# 选择至少一个 LLM 提供商并填入 API Key。

# --- 推荐提供商（任选其一）---
# OpenRouter（支持多种模型）
# OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Anthropic（Claude 系列）
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# OpenAI
# OPENAI_API_KEY=sk-your-key-here

# Google Gemini
# GOOGLE_API_KEY=your-key-here

# 智谱 AI / Z.AI（GLM 系列）
# GLM_API_KEY=your-key-here
# GLM_BASE_URL=https://api.z.ai/api/paas/v4

# Kimi / Moonshot
# KIMI_API_KEY=your-key-here

# --- 可选增强 ---
# FIRECRAWL_API_KEY=fc-your-key      # 网页抓取
# FAL_KEY=your-fal-key               # 图像生成
# ELEVENLABS_API_KEY=your-key        # 高级语音
# EXA_API_KEY=your-key               # 搜索引擎
# GITHUB_TOKEN=ghp-your-token        # GitHub 集成
ENVFILE
        log_success "创建默认配置: $CONFIG_DIR/.env"
    else
        log_info "配置文件已存在: $CONFIG_DIR/.env"
    fi

    # 创建默认 config.yaml（如果不存在）
    if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
        # 运行 hermes setup 来生成默认配置
        if [ -x "$BIN_DIR/hermes" ]; then
            "$BIN_DIR/hermes" setup --non-interactive 2>/dev/null || true
        fi
    fi

    log_success "配置目录: $CONFIG_DIR"
    return 0
}

# ============================================================================
# 步骤 6: 验证安装
# ============================================================================
verify_install() {
    log_info "验证安装..."

    local errors=0

    # 检查 CLI
    if command -v hermes &> /dev/null || [ -x "$BIN_DIR/hermes" ]; then
        log_success "hermes 命令可用"
    else
        log_error "hermes 命令不可用"
        errors=$((errors + 1))
    fi

    # 检查版本
    if [ -x "$BIN_DIR/hermes" ]; then
        local ver
        ver=$("$BIN_DIR/hermes" --version 2>&1 | head -1 || echo "unknown")
        log_success "版本: $ver"
    fi

    # 检查配置
    if [ -f "$CONFIG_DIR/.env" ]; then
        log_success "配置文件: $CONFIG_DIR/.env"
    else
        log_warn "配置文件不存在，需要手动配置 API Key"
        errors=$((errors + 1))
    fi

    # PATH 检查
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        log_warn "请将 $BIN_DIR 添加到 PATH:"
        log_warn "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
        log_warn "  source ~/.zshrc"
    fi

    echo ""
    if [ $errors -eq 0 ]; then
        log_success "安装完成！运行以下命令开始使用："
        echo ""
        echo "  1. 配置 API Key:"
        echo "     nano $CONFIG_DIR/.env"
        echo ""
        echo "  2. 运行诊断:"
        echo "     $BIN_DIR/hermes doctor"
        echo ""
        echo "  3. 开始对话:"
        echo "     $BIN_DIR/hermes chat"
        return 0
    else
        log_error "安装完成但有 $errors 个问题，请检查上方输出。"
        return 1
    fi
}

# ============================================================================
# 主流程
# ============================================================================
main() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   Hermes Agent 安装程序 v1.0.0           ║${NC}"
    echo -e "${CYAN}║   通用可移植版                          ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
    echo ""

    # 步骤 1: 检查系统依赖
    if [ "$SKIP_DEPS" = false ]; then
        check_system_deps || exit 1
    else
        log_warn "跳过系统依赖检查"
        export PYTHON_CMD="${PYTHON_CMD:-python3}"
    fi

    # 步骤 2: 克隆仓库
    clone_repo || exit 1

    # 步骤 3: 创建虚拟环境
    setup_venv || exit 1

    # 步骤 4: 创建 CLI 入口
    create_cli_entry || exit 1

    # 步骤 5: 初始化配置
    init_config || exit 1

    # 步骤 6: 验证
    verify_install
}

main "$@"
