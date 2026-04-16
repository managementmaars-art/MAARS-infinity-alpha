import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright Configuration for Abund.ai E2E Tests
 *
 * Features:
 * - API tests run on a single project (no browser rendering needed)
 * - UI tests run on Chromium only (fast, sufficient for local dev)
 * - No retries — tests should pass reliably on first attempt
 * - Screenshot/video/trace capture on failure for debugging
 */
export default defineConfig({
  testDir: './tests',

  // Run tests in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // 1 retry handles wrangler dev's inherent D1 write visibility issues
  // without masking real bugs (previously 3 was hiding failures)
  retries: 1,

  // Serial execution to avoid D1 SQLite write contention in wrangler dev
  workers: 1,

  // Reporter configuration
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
    ...(process.env.CI ? [['github'] as const] : []),
  ],

  // Shared settings for all projects
  use: {
    // Base URL for navigation
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // Capture screenshot on failure
    screenshot: 'only-on-failure',

    // Record video on failure
    video: 'retain-on-failure',

    // Record trace on failure (helps debugging)
    trace: 'retain-on-failure',
  },

  projects: [
    // API tests — no browser rendering needed, single project is sufficient
    {
      name: 'api',
      testMatch: '**/api/**',
      use: { ...devices['Desktop Chrome'] },
    },

    // UI tests — run on Chromium only for speed
    {
      name: 'chromium',
      testIgnore: '**/api/**',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
