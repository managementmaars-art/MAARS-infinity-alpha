#!/bin/bash
# 飞书发送语音消息脚本 - 使用「发送消息」API（不是回复消息）
# 用法: ./send-audio.sh <app_id> <app_secret> <receive_id> <audio_path>
#
# ⚠️ 重要：本脚本使用「发送消息」API：POST /im/v1/messages
# 不要使用「回复消息」API：POST /im/v1/messages/:message_id/reply
#
# API文档: https://open.feishu.cn/document/server-docs/im-v1/message/create

APP_ID="${1:-${FEISHU_APP_ID}}"
APP_SECRET="${2:-${FEISHU_APP_SECRET}}"
RECEIVE_ID="${3}"
AUDIO_PATH="${4}"

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ] || [ -z "$RECEIVE_ID" ] || [ -z "$AUDIO_PATH" ]; then
    echo "错误: 缺少必要参数"
    echo "用法: $0 <app_id> <app_secret> <receive_id> <audio_path>"
    echo "或者设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
    exit 1
fi

if [ ! -f "$AUDIO_PATH" ]; then
    echo "错误: 音频文件不存在: $AUDIO_PATH"
    exit 1
fi

AUDIO_NAME=$(basename "$AUDIO_PATH")

# 判断文件类型
EXTENSION="${AUDIO_PATH##*.}"
if [ "$EXTENSION" = "opus" ]; then
    FILE_TYPE="opus"
    MSG_TYPE="audio"
elif [ "$EXTENSION" = "mp3" ] || [ "$EXTENSION" = "mpeg" ]; then
    FILE_TYPE="opus"  # 飞书语音消息推荐 opus 格式
    MSG_TYPE="file"   # mp3 作为文件发送
else
    FILE_TYPE="stream"
    MSG_TYPE="file"
fi

echo "=== 飞书语音发送工具 ==="
echo "音频: $AUDIO_NAME"
echo "格式: $EXTENSION -> $FILE_TYPE"
echo "消息类型: $MSG_TYPE"
echo "接收人: $RECEIVE_ID"
echo ""

# 步骤1: 获取tenant_access_token
echo "[步骤1/3] 获取访问令牌..."
TOKEN_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"$APP_ID\",
    \"app_secret\": \"$APP_SECRET\"
  }")

TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "错误: 获取令牌失败"
    echo "响应: $TOKEN_RESPONSE"
    exit 1
fi

echo "✓ 令牌获取成功"
echo ""

# 步骤2: 上传音频文件获取file_key
echo "[步骤2/3] 上传音频文件..."
UPLOAD_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=$FILE_TYPE" \
  -F "file_name=$AUDIO_NAME" \
  -F "file=@$AUDIO_PATH")

FILE_KEY=$(echo "$UPLOAD_RESPONSE" | grep -o '"file_key":"[^"]*"' | cut -d'"' -f4)

if [ -z "$FILE_KEY" ]; then
    echo "错误: 上传音频失败"
    echo "响应: $UPLOAD_RESPONSE"
    exit 1
fi

echo "✓ 音频上传成功"
echo "  File Key: ${FILE_KEY:0:40}..."
echo ""

# 步骤3: 发送语音消息
echo "[步骤3/3] 发送语音消息..."
SEND_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"$RECEIVE_ID\",
    \"msg_type\": \"$MSG_TYPE\",
    \"content\": \"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"
  }")

# 检查响应
CODE=$(echo "$SEND_RESPONSE" | grep -o '"code":[0-9]*' | cut -d':' -f2)
MSG_ID=$(echo "$SEND_RESPONSE" | grep -o '"message_id":"[^"]*"' | cut -d'"' -f4)

if [ "$CODE" = "0" ]; then
    echo "✓ 语音消息发送成功!"
    echo "  Message ID: $MSG_ID"
    exit 0
else
    echo "✗ 发送失败"
    echo "  错误码: $CODE"
    echo "  响应: $SEND_RESPONSE"
    exit 1
fi