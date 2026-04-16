import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

export interface BrowserInfo {
  binary: string;
  profileDir: string;
  debugDir: string;
  killNames: string[];
}

const isMac = process.platform === 'darwin';
const home = os.homedir();

interface BrowserDef {
  name: string;
  binaries: string[];
  profileDir: string;
  debugDir: string;
  killNames: string[];
}

const flatpakSystemBase = '/var/lib/flatpak/exports/bin';
const flatpakUserBase = path.join(home, '.local', 'share', 'flatpak', 'exports', 'bin');
const xdgBin = path.join(home, '.local', 'bin');

function flatpakPaths(id: string): string[] {
  return [
    path.join(flatpakSystemBase, id),
    path.join(flatpakUserBase, id),
  ];
}

const BROWSERS: BrowserDef[] = [
  {
    name: 'chrome',
    binaries: isMac
      ? [
          '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
          '/opt/homebrew/bin/google-chrome',
          '/usr/local/bin/google-chrome',
          'google-chrome',
          'google-chrome-stable',
        ]
      : [
          'google-chrome',
          'google-chrome-stable',
          '/snap/bin/google-chrome',
          ...flatpakPaths('com.google.Chrome'),
          path.join(xdgBin, 'google-chrome'),
        ],
    profileDir: isMac
      ? path.join(home, 'Library', 'Application Support', 'Google', 'Chrome')
      : path.join(home, '.config', 'google-chrome'),
    debugDir: isMac
      ? path.join(home, 'Library', 'Application Support', 'Google', 'Chrome-Debug')
      : path.join(home, '.config', 'google-chrome-debug'),
    killNames: isMac ? ['Google Chrome'] : ['chrome', 'google-chrome'],
  },
  {
    name: 'chromium',
    binaries: isMac
      ? [
          '/Applications/Chromium.app/Contents/MacOS/Chromium',
          '/opt/homebrew/bin/chromium',
          '/usr/local/bin/chromium',
          'chromium',
          'chromium-browser',
        ]
      : [
          'chromium-browser',
          'chromium',
          '/snap/bin/chromium',
          ...flatpakPaths('org.chromium.Chromium'),
          path.join(xdgBin, 'chromium'),
          path.join(xdgBin, 'chromium-browser'),
        ],
    profileDir: isMac
      ? path.join(home, 'Library', 'Application Support', 'Chromium')
      : path.join(home, '.config', 'chromium'),
    debugDir: isMac
      ? path.join(home, 'Library', 'Application Support', 'Chromium-Debug')
      : path.join(home, '.config', 'chromium-debug'),
    killNames: isMac ? ['Chromium'] : ['chromium', 'chromium-browser'],
  },
  {
    name: 'brave',
    binaries: isMac
      ? [
          '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
          '/opt/homebrew/bin/brave-browser',
          '/usr/local/bin/brave-browser',
          'brave',
          'brave-browser',
        ]
      : [
          'brave-browser',
          'brave',
          '/snap/bin/brave',
          ...flatpakPaths('com.brave.Browser'),
          path.join(xdgBin, 'brave-browser'),
          path.join(xdgBin, 'brave'),
        ],
    profileDir: isMac
      ? path.join(home, 'Library', 'Application Support', 'BraveSoftware', 'Brave-Browser')
      : path.join(home, '.config', 'BraveSoftware', 'Brave-Browser'),
    debugDir: isMac
      ? path.join(home, 'Library', 'Application Support', 'BraveSoftware', 'Brave-Browser-Debug')
      : path.join(home, '.config', 'BraveSoftware', 'Brave-Browser-Debug'),
    killNames: isMac ? ['Brave Browser'] : ['brave', 'brave-browser'],
  },
];

export const VALID_BROWSERS = BROWSERS.map(b => b.name);

export function isExecutable(bin: string): boolean {
  if (bin.startsWith('/')) return fs.existsSync(bin);
  try {
    execSync(`command -v ${bin}`, { stdio: 'ignore', shell: '/bin/sh' });
    return true;
  } catch {
    return false;
  }
}

export function detectBrowser(
  name?: string | null,
  binaryOverride?: string | null
): BrowserInfo | null {
  if (binaryOverride) {
    const def = name ? BROWSERS.find(b => b.name === name) : BROWSERS[0];
    if (!def) return null;
    return {
      binary: binaryOverride,
      profileDir: def.profileDir,
      debugDir: def.debugDir,
      killNames: def.killNames,
    };
  }

  const candidates = name ? BROWSERS.filter(b => b.name === name) : BROWSERS;

  for (const def of candidates) {
    for (const bin of def.binaries) {
      if (isExecutable(bin)) {
        return {
          binary: bin,
          profileDir: def.profileDir,
          debugDir: def.debugDir,
          killNames: def.killNames,
        };
      }
    }
  }

  return null;
}

export function ensureDebugProfile(info: BrowserInfo): boolean {
  if (fs.existsSync(path.join(info.debugDir, 'Default'))) return true;
  if (!fs.existsSync(path.join(info.profileDir, 'Default'))) {
    console.error('Error: No browser profile found to copy');
    console.error(`Expected: ${info.profileDir}/Default`);
    console.error('Override with BROWSER_PATH env var or --browser <chrome|chromium|brave>');
    return false;
  }

  console.error('First run: copying browser profile for CDP mode...');
  fs.mkdirSync(info.debugDir, { recursive: true });
  execSync(`cp -r "${info.profileDir}/Default" "${info.debugDir}/Default"`);
  try {
    execSync(`cp "${info.profileDir}/Local State" "${info.debugDir}/Local State"`);
  } catch {
    // Local State is optional
  }
  console.error('Profile copied.');
  return true;
}
