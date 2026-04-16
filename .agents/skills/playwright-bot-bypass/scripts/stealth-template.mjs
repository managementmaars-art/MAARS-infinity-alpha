#!/usr/bin/env node
/**
 * Stealth Browser Template v2
 * Reusable template for bot-detection-free browser automation
 *
 * Patches: webdriver, chrome.runtime, plugins, languages, permissions,
 *          hardwareConcurrency, outerWidth/Height, canvas noise
 *
 * Usage:
 *   import { createStealthBrowser, humanDelay, humanType, simulateMouseMovement } from './stealth-template.mjs';
 *   const { browser, context, page } = await createStealthBrowser();
 */

import { chromium } from 'rebrowser-playwright';

/**
 * Create a stealth browser instance that bypasses bot detection
 * @param {Object} options
 * @param {boolean} options.headless - Run headed (default: false, required for stealth)
 * @param {Object} options.viewport - Viewport size (default: { width: 1280, height: 800 })
 * @param {string} options.userAgent - Custom user agent (optional)
 * @param {string} options.locale - Browser locale (default: 'ko-KR')
 * @param {string} options.storageState - Path to saved session state for cookie persistence (optional)
 * @param {Object} options.proxy - Proxy config { server, username?, password? } (optional)
 * @returns {Promise<{browser, context, page}>}
 */
export async function createStealthBrowser(options = {}) {
  const {
    headless = false,
    viewport = { width: 1280, height: 800 },
    userAgent = null,
    locale = 'ko-KR',
    storageState = null,
    proxy = null
  } = options;

  const launchOptions = {
    headless,
    channel: 'chrome',
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox'
    ]
  };
  if (proxy) launchOptions.proxy = proxy;

  const browser = await chromium.launch(launchOptions);

  const contextOptions = {
    viewport,
    locale,
    extraHTTPHeaders: {
      'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }
  };
  if (userAgent) contextOptions.userAgent = userAgent;
  if (storageState) contextOptions.storageState = storageState;

  const context = await browser.newContext(contextOptions);

  // ── Stealth patches ──────────────────────────────────────
  await context.addInitScript(() => {
    // 1. Remove webdriver property
    delete Object.getPrototypeOf(navigator).webdriver;

    // 2. chrome.runtime
    if (!window.chrome) window.chrome = {};
    if (!window.chrome.runtime) {
      window.chrome.runtime = {
        PlatformOs: { MAC: 'mac', WIN: 'win', ANDROID: 'android', CROS: 'cros', LINUX: 'linux', OPENBSD: 'openbsd' },
        PlatformArch: { ARM: 'arm', X86_32: 'x86-32', X86_64: 'x86-64' },
        PlatformNaclArch: { ARM: 'arm', X86_32: 'x86-32', X86_64: 'x86-64' },
        RequestUpdateCheckStatus: { THROTTLED: 'throttled', NO_UPDATE: 'no_update', UPDATE_AVAILABLE: 'update_available' },
        OnInstalledReason: { INSTALL: 'install', UPDATE: 'update', CHROME_UPDATE: 'chrome_update', SHARED_MODULE_UPDATE: 'shared_module_update' },
        OnRestartRequiredReason: { APP_UPDATE: 'app_update', OS_UPDATE: 'os_update', PERIODIC: 'periodic' }
      };
    }

    // 3. navigator.plugins (Cloudflare checks this)
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

    // 4. navigator.languages (cross-checked with Accept-Language header)
    Object.defineProperty(navigator, 'languages', {
      get: () => ['ko-KR', 'ko', 'en-US', 'en']
    });

    // 5. Permissions API (PerimeterX checks this)
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) =>
      parameters.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters);

    // 6. hardwareConcurrency & deviceMemory
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });

    // 7. outerWidth/outerHeight (headless has outer === inner)
    Object.defineProperty(window, 'outerWidth', { get: () => window.innerWidth + 16 });
    Object.defineProperty(window, 'outerHeight', { get: () => window.innerHeight + 88 });

    // 8. Canvas fingerprint noise
    const _getContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (type, ...args) {
      const ctx = _getContext.call(this, type, ...args);
      if (type === '2d' && ctx) {
        const _getImageData = ctx.getImageData.bind(ctx);
        ctx.getImageData = function (x, y, w, h) {
          const data = _getImageData(x, y, w, h);
          for (let i = 0; i < data.data.length; i += 400) {
            data.data[i] ^= 1;
          }
          return data;
        };
      }
      return ctx;
    };
  });

  const page = await context.newPage();

  return { browser, context, page };
}

/**
 * Save session state for cookie persistence
 * @param {BrowserContext} context
 * @param {string} path - File path to save state
 */
export async function saveSession(context, path) {
  await context.storageState({ path });
}

/**
 * Add human-like delays between actions
 * @param {number} min - Minimum delay in ms
 * @param {number} max - Maximum delay in ms
 */
export function humanDelay(min = 100, max = 500) {
  return new Promise(resolve => {
    const delay = Math.random() * (max - min) + min;
    setTimeout(resolve, delay);
  });
}

/**
 * Type text with human-like speed
 * @param {Page} page - Playwright page
 * @param {string} selector - Element selector
 * @param {string} text - Text to type
 */
export async function humanType(page, selector, text) {
  await page.click(selector);
  for (const char of text) {
    await page.keyboard.type(char);
    await humanDelay(50, 150);
  }
}

/**
 * Simulate natural mouse movement on the page
 * Helps avoid Cloudflare Turnstile detection
 * @param {Page} page
 * @param {number} moves - Number of movements (default: random 5-10)
 */
export async function simulateMouseMovement(page, moves) {
  const count = moves ?? 5 + Math.floor(Math.random() * 5);
  for (let i = 0; i < count; i++) {
    await page.mouse.move(
      100 + Math.random() * 600,
      100 + Math.random() * 400,
      { steps: 10 }
    );
    await humanDelay(50, 200);
  }
}

// CLI: Run directly to test
const scriptPath = process.argv[1]?.replace(/\\/g, '/');
if (import.meta.url === `file://${scriptPath}` || import.meta.url === `file:///${scriptPath}`) {
  console.log('Testing stealth browser...');
  const { browser, page } = await createStealthBrowser();

  process.on('SIGINT', async () => {
    await browser.close();
    process.exit(0);
  });

  await page.goto('https://bot.sannysoft.com');
  console.log('Browser opened. Check results in the browser window.');
  console.log('Press Ctrl+C to close.');
}
