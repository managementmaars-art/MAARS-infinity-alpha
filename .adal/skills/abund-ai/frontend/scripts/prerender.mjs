#!/usr/bin/env node

/**
 * Prerender Script for Static Page Generation
 *
 * This script uses Puppeteer to pre-render specified routes after the Vite build.
 * It generates static HTML files for SEO-critical pages while keeping dynamic
 * pages client-side rendered.
 *
 * Usage: node scripts/prerender.mjs
 */

import { spawn } from 'child_process'
import { mkdir, writeFile, readFile, copyFile } from 'fs/promises'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'
import puppeteer from 'puppeteer'

const __dirname = dirname(fileURLToPath(import.meta.url))
const distDir = join(__dirname, '..', 'dist')

// Routes to pre-render for SEO
const ROUTES = ['/', '/vision', '/privacy', '/terms', '/roadmap']

// Port for the local preview server
const PORT = 4173

/**
 * Start a local server to serve the dist folder
 */
async function startServer() {
    return new Promise((resolve, reject) => {
        const server = spawn('npx', ['serve', distDir, '-l', PORT.toString(), '-s'], {
            stdio: ['ignore', 'pipe', 'pipe'],
            shell: true,
        })

        let started = false

        server.stdout.on('data', (data) => {
            const output = data.toString()
            if (output.includes('Accepting connections') && !started) {
                started = true
                console.log(`  Server started on port ${PORT}`)
                resolve(server)
            }
        })

        server.stderr.on('data', (data) => {
            // serve outputs to stderr for some messages
            const output = data.toString()
            if (output.includes('Accepting connections') && !started) {
                started = true
                console.log(`  Server started on port ${PORT}`)
                resolve(server)
            }
        })

        server.on('error', reject)

        // Fallback timeout - assume server started after 3 seconds
        setTimeout(() => {
            if (!started) {
                started = true
                console.log(`  Server started on port ${PORT} (timeout fallback)`)
                resolve(server)
            }
        }, 3000)
    })
}

/**
 * Render a single route and save the HTML
 */
async function renderRoute(browser, route) {
    const page = await browser.newPage()

    try {
        const url = `http://localhost:${PORT}${route}`
        console.log(`  Rendering: ${route}`)

        await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 })

        // Wait for the root element to have content
        await page.waitForFunction(
            () => {
                const root = document.getElementById('root')
                return root && root.children.length > 0
            },
            { timeout: 10000 }
        )

        // Additional wait for i18n and animations to settle
        await page.evaluate(() => new Promise((resolve) => setTimeout(resolve, 500)))

        // Get the rendered HTML
        const html = await page.content()

        // Determine output path
        // Landing page goes to index.html for SEO (Cloudflare serves this for /)
        // Dynamic routes are handled by _redirects pointing to 200.html
        const outputPath =
            route === '/'
                ? join(distDir, 'index.html')
                : join(distDir, route.slice(1), 'index.html')

        // Create directory if needed
        await mkdir(dirname(outputPath), { recursive: true })

        // Write the pre-rendered HTML
        await writeFile(outputPath, html)

        console.log(`  ✓ Saved: ${route}`)
    } catch (error) {
        console.error(`  ✗ Failed to render ${route}:`, error.message)
        throw error
    } finally {
        await page.close()
    }
}

/**
 * Generate sitemap.xml for all routes
 */
async function generateSitemap() {
    const baseUrl = 'https://abund.ai'
    const now = new Date().toISOString().split('T')[0] // YYYY-MM-DD format

    // Static routes with priorities
    const staticRoutes = [
        { path: '/', priority: '1.0', changefreq: 'weekly' },
        { path: '/vision', priority: '0.8', changefreq: 'monthly' },
        { path: '/roadmap', priority: '0.8', changefreq: 'monthly' },
        { path: '/privacy', priority: '0.3', changefreq: 'yearly' },
        { path: '/terms', priority: '0.3', changefreq: 'yearly' },
        { path: '/feed', priority: '0.9', changefreq: 'hourly' },
        { path: '/galleries', priority: '0.7', changefreq: 'daily' },
        { path: '/communities', priority: '0.7', changefreq: 'daily' },
        { path: '/search', priority: '0.6', changefreq: 'daily' },
    ]

    const urlEntries = staticRoutes
        .map(
            ({ path, priority, changefreq }) => `  <url>
    <loc>${baseUrl}${path}</loc>
    <lastmod>${now}</lastmod>
    <changefreq>${changefreq}</changefreq>
    <priority>${priority}</priority>
  </url>`
        )
        .join('\n')

    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlEntries}
</urlset>
`

    await writeFile(join(distDir, 'sitemap.xml'), sitemap)
    console.log('  ✓ Generated sitemap.xml')
}

/**
 * Main prerender function
 */
async function prerender() {
    // Skip full prerendering in CI environments (no Chrome available)
    // Still generate sitemap since that doesn't need Chrome
    const isCI = process.env.CI === 'true' || process.env.CI === '1'

    if (isCI) {
        console.log('\n⚠️  CI environment detected - skipping Puppeteer pre-rendering')
        console.log('   (Pre-rendering runs during local deployment instead)\n')

        // Still generate sitemap in CI
        console.log('Generating sitemap...')
        await generateSitemap()
        console.log('')
        return
    }

    console.log('\n🔄 Pre-rendering static pages for SEO...\n')

    // Copy original index.html to /spa/index.html BEFORE prerendering
    // The _redirects file rewrites dynamic routes to /spa/ which serves this shell
    // This prevents the landing page flash when visiting non-static routes
    const originalIndexPath = join(distDir, 'index.html')
    const spaDir = join(distDir, 'spa')
    await mkdir(spaDir, { recursive: true })
    const spaShellPath = join(spaDir, 'index.html')
    await copyFile(originalIndexPath, spaShellPath)
    console.log('  ✓ Saved SPA shell to /spa/index.html')

    let server = null
    let browser = null

    try {
        // Start the preview server
        console.log('Starting local server...')
        server = await startServer()

        // Launch Puppeteer
        console.log('Launching browser...')
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox'],
        })

        // Render each route
        console.log('Rendering routes...')
        for (const route of ROUTES) {
            await renderRoute(browser, route)
        }

        // Generate sitemap
        console.log('Generating sitemap...')
        await generateSitemap()

        console.log('\n✅ Pre-rendering complete!\n')
        console.log('Static pages generated:')
        ROUTES.forEach((route) => {
            const path = route === '/' ? '/index.html' : `${route}/index.html`
            console.log(`  - dist${path}`)
        })
        console.log('  - dist/sitemap.xml')
        console.log('  - dist/_spa.html (SPA shell)')
        console.log('')
    } catch (error) {
        // If Chrome is not found, skip gracefully (might be in CI-like environment)
        if (error.message && error.message.includes('Could not find Chrome')) {
            console.log('\n⚠️  Chrome not available - skipping pre-rendering')
            console.log('   (Pre-rendering will run during local deployment)\n')

            // Still generate sitemap
            console.log('Generating sitemap...')
            await generateSitemap()
            console.log('')
            return
        }

        console.error('\n❌ Pre-rendering failed:', error.message)
        process.exit(1)
    } finally {
        // Cleanup
        if (browser) {
            await browser.close()
        }
        if (server) {
            server.kill()
        }
    }
}

// Run the prerender
prerender()

