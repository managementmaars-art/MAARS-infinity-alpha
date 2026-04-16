#!/usr/bin/env python3
"""
飞书发送消息脚本 - 支持文本和卡片

配置方式（优先级从高到低）：
1. 环境变量: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_RECEIVE_ID
2. 配置文件: config.json

用法:
    send.py text "你好"
    send.py card "**加粗文本**"
"""

import json
import subprocess
import sys
import os

# 从环境变量或配置文件读取配置
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config.json")

def load_config():
    """加载配置（环境变量优先）"""
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    receive_id = os.environ.get("FEISHU_RECEIVE_ID")

    # 如果环境变量未设置，尝试读取配置文件
    if not all([app_id, app_secret, receive_id]) and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                app_id = app_id or config.get("app_id")
                app_secret = app_secret or config.get("app_secret")
                receive_id = receive_id or config.get("receive_id")
        except Exception:
            pass

    return app_id, app_secret, receive_id

def get_token(app_id, app_secret):
    """获取 tenant_access_token"""
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"app_id": app_id, "app_secret": app_secret})
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return data.get("tenant_access_token")

def send_text(receive_id, content):
    """发送纯文本消息"""
    return {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }

def send_card(receive_id, content):
    """发送卡片消息（支持 markdown）"""
    card = {
        "schema": "2.0",
        "config": {"wide_screen_mode": True},
        "body": {
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ]
        }
    }
    return {
        "receive_id": receive_id,
        "msg_type": "interactive",
        "content": json.dumps(card)
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: send.py [text|card] <content>")
        print("")
        print("环境变量:")
        print("  FEISHU_APP_ID      - 飞书应用 ID")
        print("  FEISHU_APP_SECRET  - 飞书应用密钥")
        print("  FEISHU_RECEIVE_ID  - 接收人 Open ID")
        sys.exit(1)

    # 加载配置
    app_id, app_secret, receive_id = load_config()

    if not all([app_id, app_secret, receive_id]):
        print("错误: 缺少配置")
        print("")
        print("请设置环境变量:")
        print("  export FEISHU_APP_ID=cli_xxx")
        print("  export FEISHU_APP_SECRET=xxx")
        print("  export FEISHU_RECEIVE_ID=ou_xxx")
        print("")
        print("或创建 config.json 文件")
        sys.exit(1)

    msg_type = sys.argv[1]
    content = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    # 获取 token
    token = get_token(app_id, app_secret)
    if not token:
        print("Error: Failed to get token")
        sys.exit(1)

    # 构建消息
    if msg_type in ["card", "interactive"]:
        payload = send_card(receive_id, content)
    else:
        payload = send_text(receive_id, content)

    # 发送消息
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "--data-binary", json.dumps(payload)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # 提取 code
    try:
        data = json.loads(result.stdout)
        print(f"code:{data.get('code', 'unknown')}")
    except:
        print(result.stdout)

if __name__ == "__main__":
    main()
