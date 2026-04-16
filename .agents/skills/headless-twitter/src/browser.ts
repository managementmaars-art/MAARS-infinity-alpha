import puppeteer, { Browser, Page } from 'puppeteer-core';
import { execSync, spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { detectBrowser, ensureDebugProfile, BrowserInfo } from './platform';

function isCdpReachable(url: string): boolean {
  try {
    execSync(`curl -s --max-time 2 "${url}/json/version"`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

function killBrowserProcesses(info: BrowserInfo): void {
  for (const name of info.killNames) {
    try { execSync(`killall -9 "${name}" 2>/dev/null`); } catch { /* not running */ }
  }
}

export async function connect(
  cdpUrl: string,
  debug: boolean,
  browserName?: string | null
): Promise<{ browser: Browser; page: Page }> {
  if (!isCdpReachable(cdpUrl)) {
    const port = new URL(cdpUrl).port || '9222';
    const binaryOverride = process.env.BROWSER_PATH || null;
    const info = detectBrowser(browserName, binaryOverride);

    if (!info) {
      const searched = browserName ? `'${browserName}'` : 'chrome, chromium, brave';
      console.error(`Error: No supported browser found (searched: ${searched})`);
      console.error('Override with BROWSER_PATH env var or --browser <chrome|chromium|brave>');
      process.exit(1);
    }

    if (debug) console.error(`[DEBUG] Using browser: ${info.binary}`);
    if (!ensureDebugProfile(info)) process.exit(1);

    killBrowserProcesses(info);
    try { fs.unlinkSync(path.join(info.debugDir, 'SingletonLock')); } catch { /* noop */ }

    console.error(`Launching browser with CDP on port ${port}...`);
    const child = spawn(info.binary, [
      `--remote-debugging-port=${port}`,
      '--remote-allow-origins=*',
      `--user-data-dir=${info.debugDir}`,
      '--no-first-run',
      '--restore-last-session',
    ], { stdio: 'ignore', detached: true });
    child.unref();

    for (let i = 0; i < 30; i++) {
      await new Promise(r => setTimeout(r, 500));
      if (isCdpReachable(cdpUrl)) {
        if (debug) console.error('[DEBUG] Browser CDP ready');
        break;
      }
      if (i === 29) {
        console.error('Error: Browser launched but CDP not responding after 15s');
        process.exit(1);
      }
    }
  } else if (debug) {
    console.error('[DEBUG] CDP already reachable');
  }

  if (debug) console.error(`[DEBUG] Connecting via CDP: ${cdpUrl}`);
  const browser = await puppeteer.connect({ browserURL: cdpUrl });
  const page = await browser.newPage();
  if (debug) console.error('[DEBUG] Connected to browser, opened new tab');

  return { browser, page };
}

export async function cleanup(browser: Browser, page: Page): Promise<void> {
  await page.close();
  browser.disconnect();
}
