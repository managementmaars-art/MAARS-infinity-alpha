#!/usr/bin/env python3
"""
tg-send.py — Send a Telegram message and print message_id.
Usage: python3 tg-send.py <chat_id> <text>
Reads TG_BOT_TOKEN from ~/.claude/.env
Exit 0 on success, 1 on failure.
"""
import json, os, sys, urllib.request, urllib.parse

def load_env():
    env_file = os.path.expanduser("~/.claude/.env")
    env = {}
    if os.path.exists(env_file):
        for line in open(env_file):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: tg-send.py <chat_id> <text>\n")
        sys.exit(1)

    chat_id = sys.argv[1]
    text    = sys.argv[2]

    env = load_env()
    token = env.get("TG_BOT_TOKEN") or os.environ.get("TG_BOT_TOKEN")
    if not token:
        sys.stderr.write("TG_BOT_TOKEN not found in ~/.claude/.env\n")
        sys.exit(1)

    payload = json.dumps({
        "chat_id": chat_id,
        "text":    text,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.load(resp)
        msg_id = result["result"]["message_id"]
        print(msg_id)  # orchestrator captures this
    except Exception as e:
        sys.stderr.write(f"Telegram send failed: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
