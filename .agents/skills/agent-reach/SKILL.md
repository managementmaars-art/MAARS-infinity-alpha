---
name: agent-reach
description: >
  Give your AI agent eyes to see the entire internet.
  17 platforms via CLI, MCP, curl, and Python scripts.
  Zero config for 8 channels.
  Route by intent: search / social (小红书/抖音/微博/推特/B站/V2EX/Reddit) / career (LinkedIn) / dev (GitHub) / web (网页/文章/公众号/RSS) / video (YouTube/B站/播客).
  Use when user asks to search, read, or interact on any supported platform,
  shares a URL from a supported site, or asks to search the web.
  Triggers: "search twitter", "youtube transcript", "search reddit", "read this link",
  "bilibili", "web search", "research this", "search weibo", "wechat article",
  "xiaohongshu", "douyin", "podcast transcript", "V2EX", "RSS feed", "xueqiu", "stock".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Agent Reach — Router

17 platform toolset. Route by user intent to the matching category reference.

**Upstream**: [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## Preflight (Auto-Update)

**Run this before every use.** It ensures Agent Reach is installed and up-to-date.

```bash
#!/usr/bin/env bash
set -euo pipefail

PASS=true

# 1. Check if agent-reach CLI exists
if ! command -v agent-reach &>/dev/null; then
    echo "  MISSING  agent-reach CLI"
    echo "  Installing via pipx..."
    if command -v pipx &>/dev/null; then
        pipx install https://github.com/Panniantong/agent-reach/archive/main.zip --python python3.13 2>&1
        agent-reach install --env=auto 2>&1
        echo "  OK  agent-reach installed"
    else
        echo "  FAIL  pipx not found. Install: brew install pipx"
        PASS=false
    fi
else
    INSTALLED=$(agent-reach --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "0.0.0")
    echo "  OK  agent-reach v${INSTALLED}"

    # 2. Check for updates (non-blocking: 5s timeout, failures are non-fatal)
    LATEST=$(curl -sf --max-time 5 https://api.github.com/repos/Panniantong/Agent-Reach/releases/latest 2>/dev/null \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('tag_name','').lstrip('v'))" 2>/dev/null || echo "")

    if [[ -n "$LATEST" && "$LATEST" != "$INSTALLED" ]]; then
        echo "  UPDATE  v${INSTALLED} → v${LATEST}"
        echo "  Upgrading..."
        pipx upgrade agent-reach 2>&1 | tail -1
        # Re-run install to update tools and SKILL.md
        agent-reach install --env=auto 2>&1 | grep -E '^\s*(✅|--|✗|\[)' | head -20
        echo "  OK  Updated to v${LATEST}"
    fi
fi

# 3. Quick health check (which channels are active?)
if command -v agent-reach &>/dev/null; then
    DOCTOR_OUTPUT=$(agent-reach doctor 2>&1)
    ACTIVE=$(echo "$DOCTOR_OUTPUT" | grep -c '✅' || true)
    TOTAL=$(echo "$DOCTOR_OUTPUT" | grep -cE '(✅|--)' || true)
    echo "  OK  ${ACTIVE}/${TOTAL} channels active"
fi

if ! $PASS; then
    echo "FAIL: Agent Reach not available."
    exit 1
fi
echo "Preflight passed."
```

If the version check fails (no network, GitHub rate-limited), it silently continues with the installed version. Updates are best-effort, never blocking.

## Routing Table

| User Intent                           | Category | Reference                                    |
| ------------------------------------- | -------- | -------------------------------------------- |
| Web search / code search              | search   | [references/search.md](references/search.md) |
| 小红书/抖音/微博/推特/B站/V2EX/Reddit | social   | [references/social.md](references/social.md) |
| Jobs / LinkedIn                       | career   | [references/career.md](references/career.md) |
| GitHub / code                         | dev      | [references/dev.md](references/dev.md)       |
| Web pages / articles / 公众号 / RSS   | web      | [references/web.md](references/web.md)       |
| YouTube / Bilibili / podcasts         | video    | [references/video.md](references/video.md)   |

## Zero-Config Quick Commands

```bash
# Exa web search
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'

# Read any web page
curl -s "https://r.jina.ai/URL"

# GitHub search
gh search repos "query" --sort stars --limit 10

# Twitter search
twitter search "query" --limit 10

# YouTube / Bilibili subtitles
yt-dlp --write-sub --skip-download -o "/tmp/%(id)s" "URL"

# Reddit search + read
rdt search "query" --limit 10
rdt read POST_ID

# V2EX hot topics
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
```

## Environment Check

```bash
# Check available channels
agent-reach doctor

# List all MCP services
mcporter_list_servers()
```

## Configuration

```bash
agent-reach configure proxy http://user:pass@ip:port     # Reddit/Bilibili proxy
agent-reach configure twitter-cookies "auth_token=xxx; ct0=yyy"
agent-reach configure groq-key gsk_xxxxx                 # Xiaoyuzhou podcasts
agent-reach configure xhs-cookies "key1=val1; key2=val2" # XiaoHongShu
agent-reach configure --from-browser chrome              # Auto-extract all cookies
```

For channel-specific setup details, see [references/setup-channels.md](references/setup-channels.md).

## Workspace Rules

**Never create files in the agent workspace.** Use `/tmp/` for temporary output and `~/.agent-reach/` for persistent data.

## Troubleshooting

- **Channel not working?** Run `agent-reach doctor`
- **Update manually:** `pipx upgrade agent-reach && agent-reach install --env=auto`
- **Full reinstall:** `pipx reinstall agent-reach && agent-reach install --env=auto`

## Post-Execution Reflection

After this skill completes, check before closing:

1. **Did the command succeed?** — If not, fix the instruction or error table that caused the failure.
2. **Did parameters or output change?** — If the underlying tool's interface drifted, update Usage examples and Parameters table to match.
3. **Was a workaround needed?** — If you had to improvise (different flags, extra steps), update this SKILL.md so the next invocation doesn't need the same workaround.

Only update if the issue is real and reproducible — not speculative.
