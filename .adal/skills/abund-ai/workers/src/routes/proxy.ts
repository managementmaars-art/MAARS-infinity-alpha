/**
 * Image Proxy Route
 *
 * Proxies external images through our worker to:
 * 1. Protect user IP addresses from being leaked to external servers
 * 2. Block potentially malicious content (SVGs, non-images)
 * 3. Enable caching for better performance
 */

import { Hono } from 'hono'
import type { Env } from '../types'
import { validateExternalUrl } from '../lib/ssrf'

const proxy = new Hono<{ Bindings: Env }>()

// Allowed image content types
const ALLOWED_CONTENT_TYPES = [
  'image/png',
  'image/jpeg',
  'image/jpg',
  'image/gif',
  'image/webp',
  'image/avif',
]

// Blocked extensions (before fetching)
const BLOCKED_EXTENSIONS = [
  '.svg',
  '.svgz',
  '.html',
  '.htm',
  '.js',
  '.css',
  '.json',
  '.xml',
]

// Max image size (5MB)
const MAX_IMAGE_SIZE = 5 * 1024 * 1024

/**
 * GET /api/v1/proxy/image
 *
 * Proxies an external image through the worker.
 * Query params:
 *   - url: The URL to fetch (URL-encoded)
 */
proxy.get('/image', async (c) => {
  const urlParam = c.req.query('url')

  if (!urlParam) {
    return c.json(
      {
        success: false,
        error: 'Missing url parameter',
      },
      400
    )
  }

  // Decode and validate URL
  let targetUrl: URL
  try {
    targetUrl = new URL(urlParam)
  } catch {
    return c.json(
      {
        success: false,
        error: 'Invalid URL',
      },
      400
    )
  }

  // SSRF protection: validate URL against private/internal addresses
  const ssrfError = validateExternalUrl(urlParam)
  if (ssrfError) {
    return c.json(
      {
        success: false,
        error: ssrfError,
      },
      400
    )
  }

  // Block known dangerous extensions
  const pathname = targetUrl.pathname.toLowerCase()
  for (const ext of BLOCKED_EXTENSIONS) {
    if (pathname.endsWith(ext)) {
      return c.json(
        {
          success: false,
          error: `Blocked file type: ${ext}`,
        },
        400
      )
    }
  }

  try {
    // Fetch the image
    const response = await fetch(targetUrl.toString(), {
      headers: {
        'User-Agent': 'Abund.ai Image Proxy/1.0',
        Accept: 'image/*',
      },
      // Don't follow too many redirects
      redirect: 'follow',
    })

    if (!response.ok) {
      return c.json(
        {
          success: false,
          error: `Failed to fetch image: ${response.status}`,
        },
        502
      )
    }

    // Validate content type
    const rawContentType = response.headers.get('content-type')
    const contentType = rawContentType?.split(';')[0]?.trim().toLowerCase()

    if (!contentType || !ALLOWED_CONTENT_TYPES.includes(contentType)) {
      return c.json(
        {
          success: false,
          error: `Invalid content type: ${contentType ?? 'unknown'}. Only images allowed.`,
        },
        400
      )
    }

    // Check content length if available
    const contentLength = response.headers.get('content-length')
    if (contentLength && parseInt(contentLength) > MAX_IMAGE_SIZE) {
      return c.json(
        {
          success: false,
          error: `Image too large. Max size: ${MAX_IMAGE_SIZE / 1024 / 1024}MB`,
        },
        400
      )
    }

    // Read the body as ArrayBuffer for size check
    const imageBuffer = await response.arrayBuffer()

    if (imageBuffer.byteLength > MAX_IMAGE_SIZE) {
      return c.json(
        {
          success: false,
          error: `Image too large. Max size: ${MAX_IMAGE_SIZE / 1024 / 1024}MB`,
        },
        400
      )
    }

    // Return the image with caching headers
    return new Response(imageBuffer, {
      status: 200,
      headers: {
        'Content-Type': contentType!, // Safe: we checked above
        'Content-Length': imageBuffer.byteLength.toString(),
        'Cache-Control': 'public, max-age=86400', // Cache for 24 hours
        'X-Content-Type-Options': 'nosniff',
        'X-Proxy-Source': 'abund.ai',
      },
    })
  } catch (error) {
    console.error('Image proxy error:', error)
    return c.json(
      {
        success: false,
        error: 'Failed to proxy image',
      },
      500
    )
  }
})

export default proxy
