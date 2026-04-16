#!/bin/bash
# 飞书发送视频脚本 - 使用「发送消息」API（不是回复消息）
# 用法: ./send-video.sh <app_id> <app_secret> <receive_id> <video_path> [thumb_path]
#
# ⚠️ 重要：本脚本使用「发送消息」API：POST /im/v1/messages
# 不要使用「回复消息」API：POST /im/v1/messages/:message_id/reply
#
# API文档: https://open.feishu.cn/document/server-docs/im-v1/message/create

APP_ID="${1:-${FEISHU_APP_ID}}"
APP_SECRET="${2:-${FEISHU_APP_SECRET}}"
RECEIVE_ID="${3}"
VIDEO_PATH="${4}"
THUMB_PATH="${5:-}"

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ] || [ -z "$RECEIVE_ID" ] || [ -z "$VIDEO_PATH" ]; then
    echo "错误: 缺少必要参数"
    echo "用法: $0 <app_id> <app_secret> <receive_id> <video_path> [thumb_path]"
    echo "或者设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
    exit 1
fi

if [ ! -f "$VIDEO_PATH" ]; then
    echo "错误: 视频文件不存在: $VIDEO_PATH"
    exit 1
fi

VIDEO_NAME=$(basename "$VIDEO_PATH")

echo "=== 飞书视频发送工具 ==="
echo "视频: $VIDEO_NAME"
echo "接收人: $RECEIVE_ID"
echo ""

# 步骤1: 获取tenant_access_token
echo "[步骤1/4] 获取访问令牌..."
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

# 步骤2: 上传视频获取file_key
echo "[步骤2/4] 上传视频..."
UPLOAD_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=mp4" \
  -F "file=@$VIDEO_PATH")

VIDEO_KEY=$(echo "$UPLOAD_RESPONSE" | grep -o '"file_key":"[^"]*"' | cut -d'"' -f4)

if [ -z "$VIDEO_KEY" ]; then
    echo "错误: 上传视频失败"
    echo "响应: $UPLOAD_RESPONSE"
    exit 1
fi

echo "✓ 视频上传成功"
echo "  Video Key: ${VIDEO_KEY:0:40}..."
echo ""

# 步骤3: 上传封面图（如果有）
if [ -n "$THUMB_PATH" ] && [ -f "$THUMB_PATH" ]; then
    echo "[步骤3/4] 上传封面图..."
    THUMB_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/images" \
      -H "Authorization: Bearer $TOKEN" \
      -F "image_type=message" \
      -F "image=@$THUMB_PATH")
    
    THUMB_KEY=$(echo "$THUMB_RESPONSE" | grep -o '"image_key":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$THUMB_KEY" ]; then
        echo "✓ 封面上传成功"
        echo "  Image Key: ${THUMB_KEY:0:40}..."
        CONTENT="{\"file_key\":\"$VIDEO_KEY\",\"image_key\":\"$THUMB_KEY\"}"
    else
        echo "⚠ 封面上传失败，继续发送视频..."
        CONTENT="{\"file_key\":\"$VIDEO_KEY\"}"
    fi
else
    echo "[步骤3/4] 无封面图，跳过..."
    CONTENT="{\"file_key\":\"$VIDEO_KEY\"}"
fi
echo ""

# 步骤4: 发送视频消息
echo "[步骤4/4] 发送视频消息..."
SEND_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"$RECEIVE_ID\",
    \"msg_type\": \"media\",
    \"content\": \"$CONTENT\"
  }")

# 检查响应
CODE=$(echo "$SEND_RESPONSE" | grep -o '"code":[0-9]*' | cut -d':' -f2)
MSG_ID=$(echo "$SEND_RESPONSE" | grep -o '"message_id":"[^"]*"' | cut -d'"' -f4)

if [ "$CODE" = "0" ]; then
    echo "✓ 视频发送成功!"
    echo "  Message ID: $MSG_ID"
    exit 0
else
    echo "✗ 发送失败"
    echo "  错误码: $CODE"
    echo "  响应: $SEND_RESPONSE"
    exit 1
fi