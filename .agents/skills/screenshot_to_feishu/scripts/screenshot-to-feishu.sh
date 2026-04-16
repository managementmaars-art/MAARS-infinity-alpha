#!/bin/bash
# 截图并发送到飞书 (带重试机制)
# 使用方式: 直接运行脚本即可完成截图+发送

MAX_RETRIES=3
RETRY_DELAY=2
timestamp=$(date +%Y%m%d_%H%M%S)
screenshot_path="/Users/apple/Desktop/screenshot_${timestamp}.png"

# 步骤 1: 在 Mac mini 上截图 (带重试)
screenshot_success=false
for i in $(seq 1 $MAX_RETRIES); do
    if screencapture "$screenshot_path" 2>/dev/null; then
        if [ -f "$screenshot_path" ] && [ -s "$screenshot_path" ]; then
            screenshot_success=true
            break
        fi
    fi
    if [ $i -lt $MAX_RETRIES ]; then
        sleep $RETRY_DELAY
    fi
done

if [ "$screenshot_success" = false ]; then
    echo "❌ 截图失败，已重试 $MAX_RETRIES 次"
    exit 1
fi

# 步骤 2: 发送到飞书 (带重试)
send_success=false
for i in $(seq 1 $MAX_RETRIES); do
    if openclaw message send --channel feishu --target "ou_715534dc247ce18213aee31bc8b224cf" --media "$screenshot_path" --message "📸 截图" 2>&1 | grep -q "Sent via Feishu"; then
        send_success=true
        break
    fi
    if [ $i -lt $MAX_RETRIES ]; then
        sleep $RETRY_DELAY
    fi
done

if [ "$send_success" = false ]; then
    echo "❌ 发送失败，已重试 $MAX_RETRIES 次"
    echo "截图已保存到: $screenshot_path"
    exit 1
fi

echo "✅ 截图已发送"
