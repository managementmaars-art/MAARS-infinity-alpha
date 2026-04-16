---
name: playwright-bot-bypass
description: This skill should be used when the user asks to "bypass bot detection", "avoid CAPTCHA", "stealth browser automation", "undetected playwright", "bypass Google bot check", "rebrowser-playwright", or needs to automate websites that detect and block bots.
version: 2.0.0
---

# Playwright Bot Bypass

Bypass bot detection systems using rebrowser-playwright with stealth techniques. Passes bot.sannysoft.com and enables automation on sites with aggressive bot protection (Cloudflare, Akamai, PerimeterX, etc.).

## Why Standard Playwright Gets Detected

| Detection Point | Standard Playwright | This Solution |
|-----------------|---------------------|---------------|
| `navigator.webdriver` | `true` | Removed |
| WebGL Renderer | SwiftShader (software) | Real GPU (Apple M2, etc.) |
| User Agent | Contains "HeadlessChrome" | Clean Chrome UA |
| `chrome.runtime` | Missing | Complete runtime object |
| `navigator.plugins` | Empty array | 3 standard plugins |
| `navigator.languages` | `['en-US']` only | Matches Accept-Language header |
| Permissions API | Inconsistent state | Patched to match real Chrome |
| `outerWidth/Height` | Same as inner (no chrome) | Offset like real browser |
| Canvas fingerprint | Deterministic | Noise injected |

## Prerequisites

- **Node.js 18+** with ESM support (`.mjs` files)
- **Google Chrome** installed (not just Chromium)
- **Headed mode** required (`headless: false`) — no display = no stealth

Verify Chrome is installed:
```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version
# Linux
google-chrome --version
```

## Quick Start

### 1. Install

```bash
npm init -y && npm install rebrowser-playwright
```

### 2. Create `stealth-test.mjs`

```javascript
import { chromium } from 'rebrowser-playwright';

const browser = await chromium.launch({
  headless: false,
  channel: 'chrome',
  args: ['--disable-blink-features=AutomationControlled', '--no-sandbox']
});

const context = await browser.newContext({
  locale: 'ko-KR',
  extraHTTPHeaders: { 'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7' }
});

await context.addInitScript(() => {
  // Remove webdriver
  delete Object.getPrototypeOf(navigator).webdriver;

  // chrome.runtime
  if (!window.chrome) window.chrome = {};
  if (!window.chrome.runtime) {
    window.chrome.runtime = {
      PlatformOs: { MAC: 'mac', WIN: 'win', ANDROID: 'android', CROS: 'cros', LINUX: 'linux', OPENBSD: 'openbsd' },
      PlatformArch: { ARM: 'arm', X86_32: 'x86-32', X86_64: 'x86-64' }
    };
  }

  // Plugins (Cloudflare checks this)
  Object.defineProperty(navigator, 'plugins', {
    get: () => {
      const arr = [
        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
        { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
      ];
      arr.__proto__ = PluginArray.prototype;
      return arr;
    }
  });

  // Languages (must match Accept-Language header)
  Object.defineProperty(navigator, 'languages', {
    get: () => ['ko-KR', 'ko', 'en-US', 'en']
  });
});

const page = await context.newPage();

try {
  await page.goto('https://bot.sannysoft.com', { waitUntil: 'networkidle' });
  await page.screenshot({ path: '/tmp/stealth-test.png' });
  console.log('Screenshot saved: /tmp/stealth-test.png');
} finally {
  await browser.close();
}
```

### 3. Run

```bash
node stealth-test.mjs
```

## Using the Template (Recommended)

The `scripts/stealth-template.mjs` provides a reusable factory with all patches pre-applied:

```javascript
import { createStealthBrowser, humanDelay, humanType, simulateMouseMovement } from './scripts/stealth-template.mjs';

const { browser, page } = await createStealthBrowser();

try {
  await page.goto('https://example.com');

  // Human-like mouse movement (avoids Cloudflare Turnstile)
  await simulateMouseMovement(page);

  // Human-like typing instead of instant fill
  await humanType(page, 'input[name="q"]', 'search query');
  await humanDelay(300, 800);
} finally {
  await browser.close();
}
```

### Template Options

```javascript
const { browser, context, page } = await createStealthBrowser({
  headless: false,             // Required for stealth (default)
  viewport: { width: 1280, height: 800 },  // Default
  locale: 'ko-KR',            // Browser locale (default)
  userAgent: null,             // Custom UA (optional)
  storageState: './session.json',  // Cookie persistence (optional)
  proxy: { server: 'http://proxy:8080' }   // Proxy (optional)
});

// Save session for reuse
import { saveSession } from './scripts/stealth-template.mjs';
await saveSession(context, './session.json');
```

## Stealth Patches Applied

The template applies these patches via `addInitScript`:

| # | Patch | Target |
|---|-------|--------|
| 1 | `navigator.webdriver` removal | All bot detectors |
| 2 | `chrome.runtime` object | Cloudflare, sannysoft |
| 3 | `navigator.plugins` (3 plugins) | Cloudflare Bot Management |
| 4 | `navigator.languages` (ko-KR,en) | Akamai (cross-checks with HTTP header) |
| 5 | Permissions API normalization | PerimeterX |
| 6 | `hardwareConcurrency` / `deviceMemory` | Advanced fingerprinters |
| 7 | `outerWidth` / `outerHeight` offset | Headless detection |
| 8 | Canvas fingerprint noise | Cloudflare Turnstile |

Plus launch args: `--disable-blink-features=AutomationControlled`, `--no-sandbox`

## Scripts

- **`scripts/stealth-template.mjs`** — Reusable stealth browser factory (all examples import this)
- **`scripts/bot-detection-test.mjs`** — Verify bypass at bot.sannysoft.com

## Examples

- **`examples/stealth-google-search.mjs`** — Google search without CAPTCHA
- **`examples/ab-test.mjs`** — Side-by-side detected vs stealth comparison
- **`examples/stealth-twitter-scrape.mjs`** — Twitter/X profile scraping

> **Note**: `ab-test.mjs` requires both `rebrowser-playwright` AND `playwright`:
> ```bash
> npm install rebrowser-playwright playwright && npx playwright install chromium
> ```

All screenshots are saved to `/tmp/` for predictable paths.

## Limitations

- Requires `headless: false` (headed mode with display)
- Needs real Google Chrome installed (`channel: 'chrome'`)
- Some sites may still detect based on behavior patterns — use `humanDelay`, `humanType`, `simulateMouseMovement`
- Does not bypass CAPTCHAs, only prevents triggering them
- TLS/JA3 fingerprint is handled by `channel: 'chrome'` (uses real Chrome binary)

## Python Support

### undetected-chromedriver (Recommended)

```bash
pip install undetected-chromedriver
```

```python
import undetected_chromedriver as uc

# Match your Chrome version: check chrome://version
driver = uc.Chrome()  # auto-detects version

driver.get("https://www.google.com")
search_box = driver.find_element("name", "q")
search_box.send_keys("your search query")
search_box.submit()
```

> Python `playwright-stealth` only patches at JS level — WebGL still shows SwiftShader. Use `undetected-chromedriver` instead.

### Alternative: Call Node.js from Python

```python
import subprocess
result = subprocess.run(['node', 'stealth-script.mjs', query], capture_output=True)
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ERR_MODULE_NOT_FOUND` | Run `npm install rebrowser-playwright` in the same directory as your script |
| Browser not opening | Verify Chrome is installed (see Prerequisites) |
| WebGL shows SwiftShader | Confirm import is from `rebrowser-playwright`, not `playwright` |
| Still getting detected | Add `simulateMouseMovement()` and `humanDelay()` between actions |
| Process hangs | Ensure `browser.close()` is in a `finally` block |
| `SyntaxError: await` | File must be `.mjs` or have `"type": "module"` in package.json |
