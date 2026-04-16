#!/bin/bash
# 飞书消息发送统一脚本 - 简化版
# 使用配置文件，支持多应用隔离
#
# 重要特性:
#   ✅ 使用「发送消息」API (POST /im/v1/messages)
#   ❌ 不使用「回复消息」API (/im/v1/messages/{id}/reply)
#   避免消息被标记为 reply_context
#
# 配置方法:
#   编辑 config.json 文件设置 app_id, app_secret, receive_id
#
# 用法:
#   ./send-message.sh text "你好"
#   ./send-message.sh image "/path/to/img.png"
#   ./send-message.sh audio "/path/to/voice.opus"
#   ./send-message.sh file "/path/to/doc.pdf"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"

# 读取配置（优先级: 环境变量 > 配置文件）
APP_ID="${FEISHU_APP_ID:-}"
APP_SECRET="${FEISHU_APP_SECRET:-}"
RECEIVE_ID="${FEISHU_RECEIVE_ID:-}"

# 如果环境变量未设置，尝试读取配置文件
if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ] || [ -z "$RECEIVE_ID" ]; then
    if [ -f "$CONFIG_FILE" ]; then
        # 使用 Python 读取 JSON 配置（避免依赖 jq）
        CONFIG_APP_ID=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('app_id',''))" 2>/dev/null || echo "")
        CONFIG_APP_SECRET=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('app_secret',''))" 2>/dev/null || echo "")
        CONFIG_RECEIVE_ID=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('receive_id',''))" 2>/dev/null || echo "")
        
        # 使用配置文件值（如果环境变量未设置）
        APP_ID="${APP_ID:-$CONFIG_APP_ID}"
        APP_SECRET="${APP_SECRET:-$CONFIG_APP_SECRET}"
        RECEIVE_ID="${RECEIVE_ID:-$CONFIG_RECEIVE_ID}"
    fi
fi

# 检查配置
if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ] || [ -z "$RECEIVE_ID" ]; then
    echo "错误: 缺少飞书配置"
    echo ""
    echo "请编辑配置文件: $CONFIG_FILE"
    echo ""
    echo "配置文件示例:"
    cat << 'EOF'
{
  "app_id": "cli_xxx",
  "app_secret": "your_app_secret",
  "receive_id": "ou_xxx"
}
EOF
    echo ""
    echo "或使用环境变量临时覆盖:"
    echo "  FEISHU_APP_ID=xxx FEISHU_APP_SECRET=xxx FEISHU_RECEIVE_ID=ou_xxx $0 text \"你好\""
    exit 1
fi

# 获取参数
MSG_TYPE="${1:-}"
CONTENT="${2:-}"

if [ -z "$MSG_TYPE" ] || [ -z "$CONTENT" ]; then
    echo "用法: $0 <type> <content>"
    echo ""
    echo "类型:"
    echo "  text  <文本>          - 发送文本消息"
    echo "  card  <markdown>      - 发送卡片消息"
    echo "  image <图片路径>      - 发送图片"
    echo "  audio <音频路径>      - 发送语音 (opus格式)"
    echo "  video <视频路径>      - 发送视频"
    echo "  file  <文件路径>      - 发送文件"
    echo ""
    echo "示例:"
    echo "  $0 text \"你好主人！\""
    echo "  $0 image \"/path/to/photo.png\""
    exit 1
fi

# 获取 token
get_token() {
    curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" | \
        grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4
}

# 发送文本
send_text() {
    local text="$1"
    curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"receive_id\":\"$RECEIVE_ID\",\"msg_type\":\"text\",\"content\":\"{\\\"text\\\":\\\"$text\\\"}\"}"
}

# 发送卡片
send_card() {
    local content="$1"
    local card=$(cat <<EOF
{"schema":"2.0","config":{"wide_screen_mode":true},"body":{"elements":[{"tag":"markdown","content":"$content"}]}}
EOF
)
    curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"receive_id\":\"$RECEIVE_ID\",\"msg_type\":\"interactive\",\"content\":\"$(echo "$card" | sed 's/"/\\"/g')\"}"
}

# 发送图片
send_image() {
    local path="$1"
    
    # 上传图片
    local upload_resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/images" \
        -H "Authorization: Bearer $TOKEN" \
        -F "image_type=message" \
        -F "image=@$path")
    
    local image_key=$(echo "$upload_resp" | grep -o '"image_key":"[^"]*"' | cut -d'"' -f4)
    
    if [ -z "$image_key" ]; then
        echo "错误: 图片上传失败"
        echo "响应: $upload_resp"
        exit 1
    fi
    
    # 发送消息
    curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"receive_id\":\"$RECEIVE_ID\",\"msg_type\":\"image\",\"content\":\"{\\\"image_key\\\":\\\"$image_key\\\"}\"}"
}

# 发送音频
send_audio() {
    local path="$1"
    local ext="${path##*.}"
    local file_type="opus"
    
    if [ "$ext" = "mp3" ] || [ "$ext" = "mpeg" ]; then
        file_type="opus"
    fi
    
    # 上传文件
    local upload_resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
        -H "Authorization: Bearer $TOKEN" \
        -F "file_type=$file_type" \
        -F "file_name=$(basename "$path")" \
        -F "file=@$path")
    
    local file_key=$(echo "$upload_resp" | grep -o '"file_key":"[^"]*"' | cut -d'"' -f4)
    
    if [ -z "$file_key" ]; then
        echo "错误: 音频上传失败"
        echo "响应: $upload_resp"
        exit 1
    fi
    
    # 发送音频消息
    curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"receive_id\":\"$RECEIVE_ID\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"$file_key\\\"}\"}"
}

# 发送视频
send_video() {
    local path="$1"
    
    # 上传文件
    local upload_resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
        -H "Authorization: Bearer $TOKEN" \
        -F "file_type=mp4" \
        -F "file_name=$(basename "$path")" \
        -F "file=@$path")
    
    local file_key=$(echo "$upload_resp" | grep -o '"file_key":"[^"]*"' | cut -d'"' -f4)
    
    if [ -z "$file_key" ]; then
        echo "错误: 视频上传失败"
        echo "响应: $upload_resp"
        exit 1
    fi
    
    # 发送视频消息
    curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"receive_id\":\"$RECEIVE_ID\",\"msg_type\":\"media\",\"content\":\"{\\\"file_key\\\":\\\"$file_key\\\"}\"}"
}

# 发送文件
send_file() {
    local path="$1"
    local ext="${path##*.}"
    local file_type="stream"
    
    # 根据扩展名判断类型
    case "$ext" in
        pdf) file_type="pdf" ;;
        doc|docx) file_type="doc" ;;
        xls|xlsx) file_type="xls" ;;
        ppt|pptx) file_type="ppt" ;;
        *) file_type="stream" ;;
    esac
    
    # 上传文件
    local upload_resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
        -H "Authorization: Bearer $TOKEN" \
        -F "file_type=$file_type" \
        -F "file_name=$(basename "$path")" \
        -F "file=@$path")
    
    local file_key=$(echo "$upload_resp" | grep -o '"file_key":"[^"]*"' | cut -d'"' -f4)
    
    if [ -z "$file_key" ]; then
        echo "错误: 文件上传失败"
        echo "响应: $upload_resp"
        exit 1
    fi
    
    # 发送文件消息
    curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"receive_id\":\"$RECEIVE_ID\",\"msg_type\":\"file\",\"content\":\"{\\\"file_key\\\":\\\"$file_key\\\"}\"}"
}

# 主程序
echo "=== 飞书消息发送 ==="

# 获取 token
echo "[1/3] 获取访问令牌..."
TOKEN=$(get_token)

if [ -z "$TOKEN" ]; then
    echo "错误: 获取令牌失败，请检查 APP_ID 和 APP_SECRET"
    exit 1
fi
echo "✓ 令牌获取成功"

# 根据类型发送
echo "[2/3] 发送 $MSG_TYPE 消息..."

RESPONSE=""
case "$MSG_TYPE" in
    text)
        RESPONSE=$(send_text "$CONTENT")
        ;;
    card)
        RESPONSE=$(send_card "$CONTENT")
        ;;
    image)
        if [ ! -f "$CONTENT" ]; then
            echo "错误: 文件不存在: $CONTENT"
            exit 1
        fi
        RESPONSE=$(send_image "$CONTENT")
        ;;
    audio)
        if [ ! -f "$CONTENT" ]; then
            echo "错误: 文件不存在: $CONTENT"
            exit 1
        fi
        RESPONSE=$(send_audio "$CONTENT")
        ;;
    video)
        if [ ! -f "$CONTENT" ]; then
            echo "错误: 文件不存在: $CONTENT"
            exit 1
        fi
        RESPONSE=$(send_video "$CONTENT")
        ;;
    file)
        if [ ! -f "$CONTENT" ]; then
            echo "错误: 文件不存在: $CONTENT"
            exit 1
        fi
        RESPONSE=$(send_file "$CONTENT")
        ;;
    *)
        echo "错误: 不支持的消息类型: $MSG_TYPE"
        exit 1
        ;;
esac

# 检查结果
echo "[3/3] 检查结果..."
CODE=$(echo "$RESPONSE" | grep -o '"code":[0-9]*' | cut -d':' -f2)

if [ "$CODE" = "0" ]; then
    echo "✓ 发送成功!"
    exit 0
else
    echo "✗ 发送失败 (code: $CODE)"
    echo "响应: $RESPONSE"
    exit 1
fi
