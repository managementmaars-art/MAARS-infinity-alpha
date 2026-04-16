#!/bin/bash
# 飞书发送消息脚本 - 包装器，调用 Python 版本
# Usage: send.sh [text|card] "消息内容"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/send.py" "$@"
