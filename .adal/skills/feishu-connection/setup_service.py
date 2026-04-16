#!/usr/bin/env python3
"""Generate a macOS launchd plist to keep the Feishu bridge running."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

APP_ID = os.getenv("FEISHU_APP_ID")
if not APP_ID:
    print("Please set FEISHU_APP_ID environment variable", file=sys.stderr)
    sys.exit(1)

HOME = Path.home()
SKILL_DIR = Path(__file__).resolve().parent
BRIDGE_PATH = SKILL_DIR / "bridge.py"
LABEL = "com.clawdbot.feishu-bridge"
SECRET_PATH = os.getenv("FEISHU_APP_SECRET_PATH", str(HOME / ".clawdbot/secrets/feishu_app_secret"))

UV_PATH = shutil.which("uv") or "uv"

env_vars = {
    "HOME": str(HOME),
    "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
    "FEISHU_APP_ID": APP_ID,
    "FEISHU_APP_SECRET_PATH": SECRET_PATH,
}

optional_vars = [
    "CLAWDBOT_CONFIG_PATH",
    "CLAWDBOT_AGENT_ID",
    "FEISHU_THINKING_THRESHOLD_MS",
]

for key in optional_vars:
    if os.getenv(key):
        env_vars[key] = os.getenv(key, "")

env_block = "\n".join([f"      <key>{k}</key>\n      <string>{v}</string>" for k, v in env_vars.items()])

plist = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
  <dict>
    <key>Label</key>
    <string>{LABEL}</string>

    <key>ProgramArguments</key>
    <array>
      <string>{UV_PATH}</string>
      <string>run</string>
      <string>python</string>
      <string>{BRIDGE_PATH}</string>
    </array>

    <key>WorkingDirectory</key>
    <string>{SKILL_DIR}</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>EnvironmentVariables</key>
    <dict>
{env_block}
    </dict>

    <key>StandardOutPath</key>
    <string>{HOME}/.clawdbot/logs/feishu-bridge.out.log</string>
    <key>StandardErrorPath</key>
    <string>{HOME}/.clawdbot/logs/feishu-bridge.err.log</string>
  </dict>
</plist>
"""

(HOME / ".clawdbot/logs").mkdir(parents=True, exist_ok=True)

out_path = HOME / "Library/LaunchAgents" / f"{LABEL}.plist"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(plist, encoding="utf-8")

print(f"✅ Wrote: {out_path}")
print("\nTo start the service:")
print(f"  launchctl load {out_path}")
print("\nTo stop:")
print(f"  launchctl unload {out_path}")
