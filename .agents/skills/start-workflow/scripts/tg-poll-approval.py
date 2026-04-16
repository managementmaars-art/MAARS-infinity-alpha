#!/usr/bin/env python3
"""
tg-poll-approval.py — Poll for /approve or /deny reply to a specific message.
Usage: python3 tg-poll-approval.py <chat_id> <original_msg_id> [--timeout 3600]
Reads TG_BOT_TOKEN from ~/.claude/.env
Exit 0 = approved, 1 = denied, 2 = timeout
"""
import json, os, sys, time, urllib.request

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

def tg_get(token, method, params=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    try:
        with urllib.request.urlopen(url, timeout=35) as resp:
            return json.load(resp)
    except Exception:
        return None

def main():
    args = sys.argv[1:]
    timeout_secs = 3600
    if "--timeout" in args:
        idx = args.index("--timeout")
        timeout_secs = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    if len(args) < 2:
        sys.stderr.write("Usage: tg-poll-approval.py <chat_id> <original_msg_id> [--timeout N]\n")
        sys.exit(2)

    chat_id         = str(args[0])
    original_msg_id = int(args[1])

    env = load_env()
    token = env.get("TG_BOT_TOKEN") or os.environ.get("TG_BOT_TOKEN")
    if not token:
        sys.stderr.write("TG_BOT_TOKEN not found in ~/.claude/.env\n")
        sys.exit(2)

    deadline = time.time() + timeout_secs
    offset   = None
    print(f"Waiting for /approve or /deny (timeout: {timeout_secs}s)...", flush=True)

    while time.time() < deadline:
        params = {"timeout": 30, "allowed_updates": '["message"]'}
        if offset is not None:
            params["offset"] = offset

        data = tg_get(token, "getUpdates", params)
        if not data or not data.get("ok"):
            time.sleep(2)
            continue

        for update in data.get("result", []):
            offset = update["update_id"] + 1
            msg = update.get("message", {})
            if str(msg.get("chat", {}).get("id")) != chat_id:
                continue
            reply_to = msg.get("reply_to_message", {})
            if reply_to.get("message_id") != original_msg_id:
                continue
            text = msg.get("text", "").strip().lower()
            if text.startswith("/approve"):
                print("approved", flush=True)
                sys.exit(0)
            elif text.startswith("/deny"):
                print("denied", flush=True)
                sys.exit(1)

    print("timeout", flush=True)
    sys.exit(2)

if __name__ == "__main__":
    main()
