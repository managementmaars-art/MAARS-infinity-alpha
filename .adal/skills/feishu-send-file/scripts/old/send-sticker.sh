#!/bin/bash
# 飞书发送表情包脚本（使用图片作为表情包）- 使用「发送消息」API（不是回复消息）
# 用法: ./send-sticker.sh <app_id> <app_secret> <receive_id> <sticker_path>
#
# ⚠️ 重要：本脚本使用「发送消息」API：POST /im/v1/messages
# 不要使用「回复消息」API：POST /im/v1/messages/:message_id/reply
#
# API文档: https://open.feishu.cn/document/server-docs/im-v1/message/create

APP_ID="${1:-${FEISHU_APP_ID}}"
APP_SECRET="${2:-${FEISHU_APP_SECRET}}"
RECEIVE_ID="${3}"
STICKER_PATH="${4}"

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ] || [ -z "$RECEIVE_ID" ] || [ -z "$STICKER_PATH" ]; then
    echo "错误: 缺少必要参数"
    echo "用法: $0 <app_id> <app_secret> <receive_id> <sticker_path>"
    echo "或者设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
    exit 1
fi

if [ ! -f "$STICKER_PATH" ]; then
    echo "错误: 表情包图片不存在: $STICKER_PATH"
    exit 1
fi

STICKER_NAME=$(basename "$STICKER_PATH")

echo "=== 飞书表情包发送工具 ==="
echo "表情: $STICKER_NAME"
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

# 步骤2: 上传表情图片获取image_key
echo "[步骤2/3] 上传表情包..."
UPLOAD_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/images" \
  -H "Authorization: Bearer $TOKEN" \
  -F "image_type=message" \
  -F "image=@$STICKER_PATH")

IMAGE_KEY=$(echo "$UPLOAD_RESPONSE" | grep -o '"image_key":"[^"]*"' | cut -d'"' -f4)

if [ -z "$IMAGE_KEY" ]; then
    echo "错误: 上传表情包失败"
    echo "响应: $UPLOAD_RESPONSE"
    exit 1
fi

echo "✓ 表情包上传成功"
echo "  Image Key: ${IMAGE_KEY:0:40}..."
echo ""

# 步骤3: 发送表情包（实际上发送的是图片消息，飞书会显示为可收藏的表情样式）
echo "[步骤3/3] 发送表情包..."
SEND_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"$RECEIVE_ID\",
    \"msg_type\": \"image\",
    \"content\": \"{\\\"image_key\\\":\\\"$IMAGE_KEY\\\"}\"
  }")

# 检查响应
CODE=$(echo "$SEND_RESPONSE" | grep -o '"code":[0-9]*' | cut -d':' -f2)
MSG_ID=$(echo "$SEND_RESPONSE" | grep -o '"message_id":"[^"]*"' | cut -d'"' -f4)

if [ "$CODE" = "0" ]; then
    echo "✓ 表情包发送成功!"
    echo "  Message ID: $MSG_ID"
    exit 0
else
    echo "✗ 发送失败"
    echo "  错误码: $CODE"
    echo "  响应: $SEND_RESPONSE"
    exit 1
fi