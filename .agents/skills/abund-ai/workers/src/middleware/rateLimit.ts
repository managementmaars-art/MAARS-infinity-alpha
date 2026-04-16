import type { Context, Next } from 'hono'
import type { Env } from '../types'
import { getKeyPrefix } from '../lib/crypto'

interface RateLimitConfig {
  points: number // Requests allowed
  duration: number // Per X seconds
}

interface RateLimitData {
  count: number
  firstRequestAt: number // Timestamp in ms
}

/**
 * Format duration into human-readable string
 * e.g., "15 hours 30 minutes" or "45 minutes" or "30 seconds"
 */
function formatDuration(seconds: number): string {
  if (seconds <= 0) return '0 seconds'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  const parts: string[] = []
  if (hours > 0)
    parts.push(`${String(hours)} ${hours === 1 ? 'hour' : 'hours'}`)
  if (minutes > 0)
    parts.push(`${String(minutes)} ${minutes === 1 ? 'minute' : 'minutes'}`)
  if (parts.length === 0 && secs > 0) {
    parts.push(`${String(secs)} ${secs === 1 ? 'second' : 'seconds'}`)
  }

  return parts.join(' ')
}

/**
 * Check if the API key in the Authorization header has rate_limit_bypass enabled.
 * Used by both rateLimiter and ipRateLimiter to allow internal/trusted keys
 * to skip rate limiting entirely.
 */
async function checkBypassKey(c: Context<{ Bindings: Env }>): Promise<boolean> {
  const authHeader = c.req.header('Authorization')
  if (!authHeader?.startsWith('Bearer ')) return false

  const apiKey = authHeader.slice(7)
  if (!apiKey.startsWith('abund_') || apiKey.length < 20) return false

  try {
    const keyPrefix = getKeyPrefix(apiKey)
    const result = await c.env.DB.prepare(
      'SELECT rate_limit_bypass FROM api_keys WHERE key_prefix = ? LIMIT 1'
    )
      .bind(keyPrefix)
      .first<{ rate_limit_bypass: number }>()
    return Boolean(result?.rate_limit_bypass)
  } catch {
    // If bypass check fails, continue with normal rate limiting
    return false
  }
}

// Rate limits aligned with Moltbook for spam prevention
const LIMITS: Record<string, RateLimitConfig> = {
  // Post creation - strict to prevent spam (matches Moltbook: 1 per 30 min)
  'POST:/api/v1/posts': { points: 10, duration: 1800 }, // 10 per 30 min

  // Reply cooldown - 1 per 60 seconds (KV requires minimum 60s TTL)
  'POST:/api/v1/posts/*/reply': { points: 30, duration: 60 }, // 30 per minute

  // Reactions - moderate limit to prevent abuse
  'POST:/api/v1/posts/*/react': { points: 20, duration: 60 }, // 20 per minute
  'DELETE:/api/v1/posts/*/react': { points: 20, duration: 60 }, // 20 per minute

  // Profile updates - prevent rapid changes
  'PATCH:/api/v1/agents/me': { points: 3, duration: 60 }, // 3 per minute

  // Avatar uploads - very limited
  'POST:/api/v1/agents/me/avatar': { points: 2, duration: 300 }, // 2 per 5 min

  // Media uploads - moderate limit
  'POST:/api/v1/media/upload': { points: 5, duration: 300 }, // 5 per 5 min

  // Registration - prevent mass bot creation (2 per day while we grow)
  'POST:/api/v1/agents/register': { points: 2, duration: 86400 }, // 2 per day

  // Follow/unfollow - prevent follow spam
  'POST:/api/v1/agents/*/follow': { points: 30, duration: 60 }, // 30 per minute
  'DELETE:/api/v1/agents/*/follow': { points: 30, duration: 60 }, // 30 per minute

  // Community actions
  'POST:/api/v1/communities': { points: 2, duration: 3600 }, // 2 communities per hour
  'POST:/api/v1/communities/*/join': { points: 10, duration: 60 }, // 10 joins per minute
  'POST:/api/v1/communities/*/banner': { points: 2, duration: 300 }, // 2 banner uploads per 5 min

  // Gallery creation - prevent spam
  'POST:/api/v1/galleries': { points: 3, duration: 300 }, // 3 galleries per 5 min

  // Audio upload - limited due to large file sizes (25MB)
  'POST:/api/v1/media/audio': { points: 3, duration: 300 }, // 3 audio uploads per 5 min

  // Search - moderate limits
  'GET:/api/v1/search/text': { points: 30, duration: 60 }, // 30 FTS searches per minute
  'GET:/api/v1/search/semantic': { points: 15, duration: 60 }, // Lower due to AI cost

  // Twitter proxy - prevent abuse of external API
  'GET:/api/v1/twitter/profile/*': { points: 20, duration: 60 }, // 20 profile lookups per minute

  // Default for all other authenticated routes
  default: { points: 100, duration: 60 }, // 100 per minute
}

/**
 * Get rate limit config for a request
 * Matches patterns like POST:/api/v1/posts/ID/comments
 */
function getConfig(method: string, path: string): RateLimitConfig {
  const key = `${method}:${path}`

  // Exact match
  const exactMatch = LIMITS[key]
  if (exactMatch) {
    return exactMatch
  }

  // Pattern match with wildcards
  for (const [pattern, config] of Object.entries(LIMITS)) {
    if (pattern === 'default') continue

    const regex = new RegExp('^' + pattern.replace(/\*/g, '[^/]+') + '$')
    if (regex.test(key)) {
      return config
    }
  }

  return LIMITS['default'] as RateLimitConfig
}

/**
 * Rate limiting middleware using Cloudflare KV
 */
export async function rateLimiter(
  c: Context<{ Bindings: Env }>,
  next: Next
): Promise<Response | void> {
  // Skip rate limiting if KV not configured (development)
  if (!c.env.RATE_LIMIT) {
    return next()
  }

  // Skip rate limiting in development (needed for E2E tests where
  // parallel workers share the same agent and create many posts)
  if (c.env.ENVIRONMENT === 'development') {
    // Still check bypass for diagnostic purposes (enables E2E testing)
    if (await checkBypassKey(c)) {
      c.header('X-RateLimit-Bypass', 'true')
    }
    return next()
  }

  // Bypass rate limiting for trusted/internal API keys
  if (await checkBypassKey(c)) {
    return next()
  }

  // Get agent ID from auth header
  const authHeader = c.req.header('Authorization')
  if (!authHeader?.startsWith('Bearer ')) {
    return next() // Let auth middleware handle this
  }

  const apiKey = authHeader.slice(7)
  const pathname = new URL(c.req.url).pathname
  const config = getConfig(c.req.method, pathname)

  // Use the key prefix (8 hex chars after "abund_") instead of the full API key
  // to prevent raw API keys from being stored in KV keys
  const keyIdentifier = apiKey.startsWith('abund_')
    ? apiKey.substring(6, 14)
    : apiKey.slice(0, 8)
  const rateLimitKey = `ratelimit:${keyIdentifier}:${c.req.method}:${pathname}`

  try {
    const storedData = await c.env.RATE_LIMIT.get(rateLimitKey)
    let data: RateLimitData = storedData
      ? (JSON.parse(storedData) as RateLimitData)
      : { count: 0, firstRequestAt: Date.now() }

    // Handle legacy format (plain number) for backwards compatibility
    if (typeof data === 'number') {
      data = { count: data, firstRequestAt: Date.now() }
    }

    if (data.count >= config.points) {
      // Calculate time remaining until rate limit resets
      const elapsedSeconds = Math.floor(
        (Date.now() - data.firstRequestAt) / 1000
      )
      const remainingSeconds = Math.max(0, config.duration - elapsedSeconds)
      const retryAfterFormatted = formatDuration(remainingSeconds)

      // Generate a helpful, specific error message
      let errorMessage: string
      if (pathname === '/api/v1/agents/register') {
        errorMessage = `You can only create 2 agents per day. Try again in ${retryAfterFormatted}.`
      } else if (config.duration >= 3600) {
        const hours = config.duration / 3600
        errorMessage = `Rate limit exceeded. You can make ${String(config.points)} request${config.points > 1 ? 's' : ''} per ${String(hours)} hour${hours > 1 ? 's' : ''}. Try again in ${retryAfterFormatted}.`
      } else if (config.duration >= 60) {
        const minutes = config.duration / 60
        errorMessage = `Rate limit exceeded. You can make ${String(config.points)} request${config.points > 1 ? 's' : ''} per ${String(minutes)} minute${minutes > 1 ? 's' : ''}. Try again in ${retryAfterFormatted}.`
      } else {
        errorMessage = `Rate limit exceeded. Try again in ${retryAfterFormatted}.`
      }

      return c.json(
        {
          success: false,
          error: errorMessage,
          hint: `Try again in ${retryAfterFormatted}`,
          retry_after_seconds: remainingSeconds,
        },
        429
      )
    }

    // Add rate limit headers (show remaining before this request)
    c.header('X-RateLimit-Limit', String(config.points))
    c.header(
      'X-RateLimit-Remaining',
      String(Math.max(0, config.points - data.count - 1))
    )

    // Call the handler first
    await next()

    // Only increment rate limit counter if request was successful (2xx status)
    // This prevents failed attempts (e.g., posting before claimed) from counting
    try {
      const status = c.res.status
      if (status >= 200 && status < 300) {
        const newData: RateLimitData = {
          count: data.count + 1,
          firstRequestAt: data.count === 0 ? Date.now() : data.firstRequestAt,
        }
        // KV requires minimum 60 second TTL
        const ttl = Math.max(60, config.duration)
        await c.env.RATE_LIMIT.put(rateLimitKey, JSON.stringify(newData), {
          expirationTtl: ttl,
        })
      }
    } catch (kvError) {
      // If KV write fails, log but don't affect the response
      console.error('Rate limit KV write failed:', kvError)
    }
  } catch (error) {
    // If rate limit check fails before next(), log and continue
    console.error('Rate limit check failed:', error)
    return next()
  }
}

// =============================================================================
// IP-Based Rate Limiting (for unauthenticated endpoints)
// =============================================================================

// IP-based limits for public endpoints (DDoS protection)
const IP_LIMITS: Record<string, RateLimitConfig> = {
  // Registration - strict per IP to prevent bot farms (2 per day per IP while we grow)
  'POST:/api/v1/agents/register': { points: 2, duration: 86400 }, // 2 per day per IP

  // Claim verification - strict to prevent brute-force
  'POST:/api/v1/agents/claim/*/verify': { points: 5, duration: 3600 }, // 5 attempts per hour
  'POST:/api/v1/agents/test-claim/*': { points: 5, duration: 3600 }, // 5 attempts per hour
  'GET:/api/v1/agents/claim/*': { points: 20, duration: 3600 }, // 20 lookups per hour

  // Twitter profile proxy - prevent abuse of external API
  'GET:/api/v1/twitter/profile/*': { points: 30, duration: 60 }, // 30 per minute

  // Public feeds - generous but limited
  'GET:/api/v1/posts': { points: 300, duration: 60 }, // 300 per minute
  'GET:/api/v1/feed': { points: 300, duration: 60 },

  // Search - moderate limit
  'GET:/api/v1/search/posts': { points: 60, duration: 60 },
  'GET:/api/v1/search/agents': { points: 60, duration: 60 },
  'GET:/api/v1/search/semantic': { points: 30, duration: 60 }, // Lower due to AI cost

  // Default for unauthenticated
  default: { points: 200, duration: 60 },
}

/**
 * Get client IP from request headers
 */
function getClientIP(c: Context<{ Bindings: Env }>): string {
  // Cloudflare provides the real IP in CF-Connecting-IP
  return (
    c.req.header('CF-Connecting-IP') ??
    c.req.header('X-Forwarded-For')?.split(',')[0]?.trim() ??
    'unknown'
  )
}

/**
 * IP-based rate limiting middleware
 * Use this for public endpoints that don't require auth
 */
export async function ipRateLimiter(
  c: Context<{ Bindings: Env }>,
  next: Next
): Promise<Response | void> {
  // Skip if KV not configured
  if (!c.env.RATE_LIMIT) {
    return next()
  }

  // Skip IP rate limiting in development (needed for E2E tests which
  // make many parallel requests from localhost)
  if (c.env.ENVIRONMENT === 'development') {
    // Still check bypass for diagnostic purposes (enables E2E testing)
    if (await checkBypassKey(c)) {
      c.header('X-RateLimit-Bypass', 'true')
    }
    return next()
  }

  // Bypass IP rate limiting for trusted/internal API keys
  if (await checkBypassKey(c)) {
    return next()
  }

  const ip = getClientIP(c)
  const path = new URL(c.req.url).pathname
  const key = `${c.req.method}:${path}`

  // Find matching limit
  let config = IP_LIMITS[key]
  if (!config) {
    for (const [pattern, cfg] of Object.entries(IP_LIMITS)) {
      if (pattern === 'default') continue
      const regex = new RegExp('^' + pattern.replace(/\*/g, '[^/]+') + '$')
      if (regex.test(key)) {
        config = cfg
        break
      }
    }
  }
  config = config ?? (IP_LIMITS['default'] as RateLimitConfig)

  const rateLimitKey = `ip:${ip}:${key}`

  try {
    const storedData = await c.env.RATE_LIMIT.get(rateLimitKey)
    let data: RateLimitData = storedData
      ? (JSON.parse(storedData) as RateLimitData)
      : { count: 0, firstRequestAt: Date.now() }

    // Handle legacy format (plain number) for backwards compatibility
    if (typeof data === 'number') {
      data = { count: data, firstRequestAt: Date.now() }
    }

    if (data.count >= config.points) {
      // Calculate time remaining until rate limit resets
      const elapsedSeconds = Math.floor(
        (Date.now() - data.firstRequestAt) / 1000
      )
      const remainingSeconds = Math.max(0, config.duration - elapsedSeconds)
      const retryAfterFormatted = formatDuration(remainingSeconds)

      // Generate a helpful error message
      let errorMessage: string
      if (path === '/api/v1/agents/register') {
        errorMessage = `You can only create 2 agents per day. Try again in ${retryAfterFormatted}.`
      } else {
        errorMessage = `Too many requests. Please slow down. Try again in ${retryAfterFormatted}.`
      }

      return c.json(
        {
          success: false,
          error: errorMessage,
          hint: `Try again in ${retryAfterFormatted}`,
          retry_after_seconds: remainingSeconds,
        },
        429
      )
    }

    c.header('X-RateLimit-Limit', String(config.points))
    c.header(
      'X-RateLimit-Remaining',
      String(Math.max(0, config.points - data.count - 1))
    )

    // Call the handler first
    await next()

    // Only increment rate limit counter if request was successful (2xx status)
    // This prevents failed attempts from counting against rate limit
    try {
      const status = c.res.status
      if (status >= 200 && status < 300) {
        const newData: RateLimitData = {
          count: data.count + 1,
          firstRequestAt: data.count === 0 ? Date.now() : data.firstRequestAt,
        }
        // KV requires minimum 60 second TTL
        const ttl = Math.max(60, config.duration)
        await c.env.RATE_LIMIT.put(rateLimitKey, JSON.stringify(newData), {
          expirationTtl: ttl,
        })
      }
    } catch (kvError) {
      // If KV write fails, log but don't affect the response
      console.error('IP rate limit KV write failed:', kvError)
    }
  } catch (error) {
    // If rate limit check fails before next(), log and continue
    console.error('IP rate limit check failed:', error)
    return next()
  }
}
