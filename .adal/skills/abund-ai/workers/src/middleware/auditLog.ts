import type { Context, Next } from 'hono'
import type { Env } from '../types'

/**
 * Get client IP from request headers (Cloudflare)
 */
function getClientIP(c: Context<{ Bindings: Env }>): string {
  return (
    c.req.header('CF-Connecting-IP') ??
    c.req.header('X-Forwarded-For')?.split(',')[0]?.trim() ??
    'unknown'
  )
}

/**
 * Generate a daily salt for IP hashing
 * Uses the current date to ensure same IP = same hash within a day
 */
function getDailySalt(): string {
  const today = new Date().toISOString().split('T')[0] // YYYY-MM-DD
  return `abund-audit-${today}`
}

/**
 * Hash an IP address with a daily rotating salt using SHA-256
 * This allows grouping by IP without storing the actual IP
 */
async function hashIP(ip: string): Promise<string> {
  const salt = getDailySalt()
  const data = new TextEncoder().encode(salt + ip)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('')
}

/**
 * Generate a unique ID for the audit log entry
 */
function generateId(): string {
  return crypto.randomUUID()
}

/**
 * Audit logging middleware
 *
 * Logs all API requests to the api_audit_log table with:
 * - Hashed IP (SHA-256 with daily salt for privacy)
 * - HTTP method and path
 * - Agent ID (if authenticated)
 * - Response status code and timing
 *
 * SECURITY: This data is internal only - no API endpoints expose this table
 */
export async function auditLogger(
  c: Context<{ Bindings: Env }>,
  next: Next
): Promise<Response | void> {
  // Skip audit logging in development to reduce D1 write pressure
  if (c.env.ENVIRONMENT === 'development') {
    return next()
  }

  const startTime = Date.now()

  // Execute the request first
  await next()

  // Get response info
  const status = c.res.status
  const responseTime = Date.now() - startTime

  // Log asynchronously via waitUntil (non-blocking)
  c.executionCtx.waitUntil(
    (async () => {
      try {
        const ip = getClientIP(c)
        const ipHash = await hashIP(ip)
        const path = new URL(c.req.url).pathname
        const method = c.req.method
        const userAgent = c.req.header('User-Agent') ?? null

        // Try to get agent ID from auth header if it exists
        // Note: We don't verify the auth here, just extract for logging
        let agentId: string | null = null
        const authHeader = c.req.header('Authorization')
        if (authHeader?.startsWith('Bearer ')) {
          // Look up agent ID from API key
          const apiKey = authHeader.slice(7)
          // Use same prefix extraction as getKeyPrefix in crypto.ts (9 chars = "abund_" + 3 hex)
          const keyPrefix = apiKey.slice(0, 9)

          const result = await c.env.DB.prepare(
            `SELECT agent_id FROM api_keys WHERE key_prefix = ?`
          )
            .bind(keyPrefix)
            .first<{ agent_id: string }>()

          if (result) {
            agentId = result.agent_id
          }
        }

        // Insert audit log entry
        await c.env.DB.prepare(
          `INSERT INTO api_audit_log (id, ip_hash, method, path, agent_id, status_code, response_time_ms, user_agent)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
        )
          .bind(
            generateId(),
            ipHash,
            method,
            path,
            agentId,
            status,
            responseTime,
            userAgent
          )
          .run()
      } catch (error) {
        // Silently fail - audit logging should never break the API
        console.error('Audit log error:', error)
      }
    })()
  )
}
