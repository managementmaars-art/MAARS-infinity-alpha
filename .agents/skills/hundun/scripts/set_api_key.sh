#!/usr/bin/env bash
# 将用户提供的 api_key 写入本地配置；AIA 收到用户发送的 hd_sk_ 后调用此脚本
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

api_key="$1"
if [[ -z "$api_key" ]] || [[ "$api_key" != hd_sk_* ]]; then
    echo "用法: $0 <hd_sk_开头的api_key>" >&2
    exit 1
fi

mkdir -p "$(dirname "$CONFIG_FILE")"
{
    echo "# 混沌 Skill 配置"
    echo "api_key=$api_key"
    echo "base_url=$DEFAULT_BASE_URL"
} > "$CONFIG_FILE"
chmod 600 "$CONFIG_FILE" 2>/dev/null || true

echo "已配置，后续可直接使用"
