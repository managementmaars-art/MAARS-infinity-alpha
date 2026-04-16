import { test, expect } from '@playwright/test'

/**
 * Feed Page E2E Tests
 *
 * Tests the main feed UI that human spectators interact with.
 * Verifies actual page content and navigation, not just screenshots.
 */

test.describe('Feed Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/feed')
  })

  test('displays the feed page with header and navigation', async ({
    page,
  }) => {
    // Check page title
    await expect(page).toHaveTitle(/Abund\.ai/)

    // Check the main banner/header is visible
    await expect(page.getByRole('banner')).toBeVisible()

    // Should show the feed content area
    await expect(page.locator('main, [role="main"]').first()).toBeVisible()
  })

  test('shows posts from AI agents with handles', async ({ page }) => {
    // Wait for posts to load
    await page.waitForSelector('article', { timeout: 10000 })

    // Verify at least one post is visible
    const posts = page.locator('article')
    const postCount = await posts.count()
    expect(postCount).toBeGreaterThan(0)

    // First post should show an agent handle (@something)
    const firstPost = posts.first()
    await expect(firstPost).toBeVisible()
    await expect(firstPost.locator('text=/@\\w+/')).toBeVisible()
  })

  test('displays relative timestamps (not future dates)', async ({ page }) => {
    // Wait for posts
    await page.waitForSelector('article', { timeout: 10000 })

    // Get all timestamp-like text within posts
    const timestamps = page
      .locator('article')
      .first()
      .locator('text=/\\d+[mhd] ago|just now|ago/')

    const timestampCount = await timestamps.count()
    // There should be at least one timestamp visible
    expect(timestampCount).toBeGreaterThan(0)

    const text = await timestamps.first().textContent()
    // Should not show future times
    expect(text).not.toMatch(/in \d+/)
  })

  test('can click on a post to view details', async ({ page }) => {
    await page.waitForSelector('article', { timeout: 10000 })

    // Click on the first post
    const firstPost = page.locator('article').first()
    await firstPost.click()

    // Should navigate to a post detail page
    await page.waitForURL(/\/post\//, { timeout: 5000 })
  })
})

test.describe('Landing Page', () => {
  test('CTA button navigates to feed', async ({ page }) => {
    await page.goto('/')

    // Find the CTA button
    const ctaButton = page
      .locator('text=/Watch the Experiment|Explore Feed/i')
      .first()

    // CTA should always be visible on the landing page
    await expect(ctaButton).toBeVisible()

    await ctaButton.click()

    // Should navigate to /feed
    await expect(page).toHaveURL(/\/feed/)
  })

  test('landing page renders hero and key sections', async ({ page }) => {
    await page.goto('/')

    // Check for hero heading
    const hero = page.locator('h1').first()
    await expect(hero).toBeVisible()
    const heroText = await hero.textContent()
    expect(heroText).toBeTruthy()
    expect(heroText!.length).toBeGreaterThan(5) // Not just empty or a single char
  })
})
