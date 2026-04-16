# agent-browser CLI — Setup Guide

This guide covers installing agent-browser and connecting it to your Chrome browser.

---

## Installation

```bash
npm install -g agent-browser
```

Or use npx without installing globally:

```bash
npx agent-browser --help
```

Verify installation:

```bash
agent-browser --version
```

---

## Enabling Remote Debugging in Chrome

agent-browser connects to your real Chrome via the Chrome DevTools Protocol (CDP). You need to enable remote debugging first.

### Option A: Via Chrome UI (Chrome 136+, recommended)

1. Open Chrome normally
2. Go to `chrome://inspect/#remote-debugging`
3. Enable **"Allow remote debugging for this browser instance"**
4. Wait until status shows **"Server running at: 127.0.0.1:9222"**

### Option B: Via Command Line

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

> **Note**: Chrome 136+ blocks `--remote-debugging-port` with the default profile. Use the UI toggle (Option A) instead, or add `--user-data-dir=/tmp/chrome-debug` when using the CLI approach.

---

## Connecting agent-browser to Chrome

### Auto-connect (recommended)

```bash
agent-browser --auto-connect open https://example.com
```

This auto-discovers a Chrome instance with remote debugging enabled on the default port (9222).

### Explicit CDP port

```bash
agent-browser --cdp 9222 open https://example.com
```

---

## Verifying the Connection

```bash
# List all open tabs — if this works, you're connected
agent-browser --auto-connect tab
```

---

## Troubleshooting

### Connection refused / timeout

- Chrome's remote debugging is not enabled, or is using a different port
- Ensure Chrome is running with remote debugging enabled (see above)
- Check that no firewall is blocking port 9222

### `snapshot -i` returns empty

- The page may be loading — try `agent-browser --auto-connect wait --load networkidle` first
- The page may render content inside iframes — see the skill's iframe section

### `fill` does not work

- The target element may be a `contenteditable` div (rich text editor) rather than a standard input
- Use `keyboard inserttext "text"` instead
