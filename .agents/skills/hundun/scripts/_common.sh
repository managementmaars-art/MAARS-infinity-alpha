#!/usr/bin/env bash
# 混沌 Skill 公共逻辑：配置加载、API 调用、响应处理
# 兼容 Windows(Git Bash/WSL)、Linux、Mac

# Force UTF-8 output to avoid garbled Chinese
export LANG="${LANG:-C.UTF-8}"
export LC_ALL="${LC_ALL:-C.UTF-8}"

# 配置文件路径：Windows 下 HOME 可能未设置，用 USERPROFILE 兜底
CONFIG_FILE="${HDXY_CONFIG:-${HOME:-$USERPROFILE}/.hdxy_config}"
# 默认使用线上环境
DEFAULT_BASE_URL="https://hddrapi.hundun.cn"

# 加载配置：api_key, base_url；若配置文件不存在则自动创建
load_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        mkdir -p "$(dirname "$CONFIG_FILE")"
        {
            echo "# 混沌 Skill 配置（自动生成）"
            echo "# 请将下方 api_key 替换为从 https://tools.hundun.cn/h5Bin/aia/#/keys 获取的密钥"
            echo ""
            echo "api_key="
            echo "base_url=$DEFAULT_BASE_URL"
        } > "$CONFIG_FILE"
        chmod 600 "$CONFIG_FILE" 2>/dev/null || true
        echo "已自动创建配置文件：$CONFIG_FILE" >&2
        echo "请把 api_key（hd_sk_ 开头）直接发给 AI 即可配置，无需手动操作。获取密钥：https://tools.hundun.cn/h5Bin/aia/#/keys" >&2
        return 1
    fi
    api_key=$(grep '^api_key=' "$CONFIG_FILE" 2>/dev/null | cut -d= -f2- | tr -d '\r' | head -1)
    base_url=$(grep '^base_url=' "$CONFIG_FILE" 2>/dev/null | cut -d= -f2- | tr -d '\r' | head -1)
    base_url="${base_url:-$DEFAULT_BASE_URL}"
    base_url="${HDXY_API_BASE_URL:-$base_url}"
    base_url="${base_url%/}"
    return 0
}

# URL 编码：优先 Python（正确支持 UTF-8/中文），否则纯 Bash（仅 ASCII 安全）
urlencode() {
    local string="$1"
    if command -v python3 &>/dev/null; then
        python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$string"
    elif command -v python &>/dev/null; then
        python -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$string"
    else
        local strlen=${#string} encoded="" pos c o
        for (( pos=0 ; pos<strlen ; pos++ )); do
            c=${string:$pos:1}
            case "$c" in
                [-_.~a-zA-Z0-9] ) o="$c" ;;
                * ) printf -v o '%%%02X' "'$c" ;;
            esac
            encoded+="$o"
        done
        echo "$encoded"
    fi
}

# GET 请求，无需鉴权
api_get_no_auth() {
    local path="$1"
    local url="${base_url}${path}"
    curl -sS -w "\n%{http_code}" "$url"
}

# GET 请求，需 API Key
api_get() {
    local path="$1"
    local url="${base_url}${path}"
    if [[ -z "$api_key" ]]; then
        echo "错误：未配置 api_key。请把 api_key（hd_sk_ 开头）直接发给 AI 即可配置。获取密钥：https://tools.hundun.cn/h5Bin/aia/#/keys" >&2
        return 1
    fi
    curl -sS -w "\n%{http_code}" -H "X-API-Key: $api_key" "$url"
}

# 用户意图收集（埋点）：静默调用，失败不阻塞主流程
# 参数：intent_desc scene_value [scene_desc] [extra_related_content]
collect_intent() {
    local intent_desc="$1" scene_value="${2:-}" scene_desc="${3:-}" extra="${4:-}"
    [[ -z "$api_key" ]] && return 0
    local body
    if command -v jq &>/dev/null; then
        body=$(jq -n --arg i "$intent_desc" --arg s "$scene_value" --arg d "$scene_desc" --arg e "$extra" \
            '{intent_desc:$i,scene_desc:$d,scene_value:$s,extra_related_content:$e}')
    elif command -v python3 &>/dev/null; then
        body=$(python3 -c "import json,sys; print(json.dumps({'intent_desc':sys.argv[1],'scene_value':sys.argv[2],'scene_desc':sys.argv[3],'extra_related_content':sys.argv[4]}))" "$intent_desc" "$scene_value" "$scene_desc" "$extra")
    elif command -v python &>/dev/null; then
        body=$(python -c "import json,sys; print(json.dumps({'intent_desc':sys.argv[1],'scene_value':sys.argv[2],'scene_desc':sys.argv[3],'extra_related_content':sys.argv[4]}))" "$intent_desc" "$scene_value" "$scene_desc" "$extra")
    else
        return 0
    fi
    api_post "/aia/api/v1/intent/collect" "$body" >/dev/null 2>&1 || true
}

# POST 请求，需 API Key。Origin 的 host 需以 hundun.cn 结尾
api_post() {
    local path="$1"
    local body="$2"
    local url="${base_url}${path}"
    if [[ -z "$api_key" ]]; then
        echo "错误：未配置 api_key。请把 api_key（hd_sk_ 开头）直接发给 AI 即可配置。获取密钥：https://tools.hundun.cn/h5Bin/aia/#/keys" >&2
        return 1
    fi
    local origin
    origin=$(printf '%s' "$base_url" | sed -E 's|^(https?://[^/]+).*|\1|' 2>/dev/null)
    [[ -z "$origin" ]] && origin="$DEFAULT_BASE_URL"
    curl -sS -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -H "X-API-Key: $api_key" -H "Origin: $origin" -d "$body" "$url"
}

# 解析响应：分离 body 和 http_code，检查 error_no
# 压缩格式示例：{"error_no":0,"error_msg":"执行成功","compressed":true,"data":"KLUv/QQA...base64..."}
# 解压流程：compressed=true 时，data 为 base64 编码的 zstd 压缩内容，需 base64 解码后 zstd 解压
# 用法：parse_response "$(api_get ...)"
parse_response() {
    local raw="$1"
    local body http_code
    body=$(printf '%s\n' "$raw" | sed '$d')
    http_code=$(printf '%s\n' "$raw" | tail -n 1)
    if [[ "$http_code" != "200" ]]; then
        echo "HTTP $http_code" >&2
        echo "$body" | head -c 500 >&2
        return 1
    fi
    local err_no err_msg
    err_no=$(echo "$body" | grep -oE '"error_no"[[:space:]]*:[[:space:]]*-?[0-9]+' | grep -oE -- '-?[0-9]+$' | head -1)
    err_msg=$(echo "$body" | grep -oE '"error_msg"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*:[[:space:]]*"\([^"]*\)".*/\1/' | head -1)
    err_msg="${err_msg:-未知错误}"
    if [[ -n "$err_no" ]] && [[ "$err_no" != "0" ]]; then
        echo "$err_msg" >&2
        return 1
    fi
    # 解压：compressed=true 时，data 为 base64(zstd(实际JSON))
    # 优先级：zstd CLI -> Python+zstandard -> 原始输出
    local compressed data decoded py
    compressed=$(echo "$body" | grep -oE '"compressed"[[:space:]]*:[[:space:]]*true' 2>/dev/null)
    if [[ -z "$compressed" ]]; then
        :
    elif command -v zstd &>/dev/null; then
        if command -v jq &>/dev/null; then
            data=$(printf '%s' "$body" | jq -r '.data // empty' 2>/dev/null)
        elif command -v python3 &>/dev/null; then
            data=$(printf '%s' "$body" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('data','') or '')" 2>/dev/null)
        elif command -v python &>/dev/null; then
            data=$(printf '%s' "$body" | python -c "import json,sys; d=json.load(sys.stdin); print(d.get('data','') or '')" 2>/dev/null)
        fi
        if [[ -n "$data" ]]; then
            decoded=$(printf '%s' "$data" | base64 -d 2>/dev/null) || decoded=$(printf '%s' "$data" | base64 -D 2>/dev/null)
            if [[ -n "$decoded" ]]; then
                decoded=$(printf '%s' "$decoded" | zstd -d 2>/dev/null)
                if [[ -n "$decoded" ]]; then
                    echo "$decoded"
                    return 0
                fi
            fi
        fi
    fi
    # Fallback when zstd failed or missing: Python + zstandard (pip install zstandard)
    if [[ -n "$compressed" ]]; then
        py=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
    fi
    if [[ -n "$compressed" ]] && [[ -n "$py" ]]; then
        decoded=$(printf '%s' "$body" | "$py" -c "
import sys,json,base64
try:
    import zstandard
except ImportError:
    sys.exit(1)
j=json.load(sys.stdin)
b=base64.b64decode(j.get('data',''))
print(zstandard.ZstdDecompressor().decompress(b,max_output_size=10485760).decode('utf-8'),end='')
" 2>/dev/null)
        if [[ -n "$decoded" ]]; then
            echo "$decoded"
            return 0
        fi
    fi
    if command -v jq &>/dev/null; then
        echo "$body" | jq '.'
    else
        echo "$body"
    fi
}
