# Channel Setup Reference

Optional channels that require additional configuration beyond the base install.

## Reddit (Proxy Required)

Reddit blocks many IP ranges. Configure a residential proxy:

```bash
agent-reach configure proxy http://user:pass@ip:port
```

Alternative: Search via Exa (free, no proxy needed) — `mcporter call 'exa.web_search_exa(query: "site:reddit.com topic")'`

## XiaoHongShu (Docker + Cookies)

```bash
# Start the MCP server
docker run -d --name xiaohongshu-mcp -p 18060:18060 xpzouying/xiaohongshu-mcp

# Register with mcporter
mcporter config add xiaohongshu http://localhost:18060/mcp

# Import cookies (from browser Cookie-Editor export)
agent-reach configure xhs-cookies '<JSON array or header string>'
```

ARM64 (Apple Silicon): Build from source at <https://github.com/xpzouying/xiaohongshu-mcp>

## Douyin

```bash
pip install douyin-mcp-server
# Start the HTTP server on port 18070, then:
mcporter config add douyin http://localhost:18070/mcp
```

No login needed.

## LinkedIn (Chromium Required)

```bash
pip install linkedin-scraper-mcp
mcporter config add linkedin http://localhost:3000/mcp
```

Requires Chromium browser with UI (desktop) or VNC (server).

## Xiaoyuzhou Podcasts (Groq API Key)

Free Groq account for Whisper speech-to-text:

1. Register at <https://console.groq.com>
2. Run: `agent-reach configure groq-key gsk_xxxxx`

## Weibo (mcporter)

```bash
pip install git+https://github.com/Panniantong/mcp-server-weibo.git
mcporter config add weibo --command 'mcp-server-weibo'
```

## Auto-Extract Browser Cookies

Extract cookies for all platforms from your browser in one command:

```bash
agent-reach configure --from-browser chrome
# Also supports: firefox, edge, brave, opera
```
