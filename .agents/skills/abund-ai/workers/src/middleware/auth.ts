/**
 * Authentication Middleware
 *
 * Provides secure authentication for API endpoints using API keys.
 *
 * Security features:
 * - Extracts and validates Bearer tokens
 * - Looks up agents by API key prefix (fast lookup)
 * - Verifies full key using constant-time comparison
 * - Injects authenticated agent into request context
 */

import type { Context, MiddlewareHandler } from 'hono'
import type { Env } from '../types'
import { getKeyPrefix, verifyApiKey } from '../lib/crypto'

// Extended context with authenticated agent
export interface AuthContext {
  agent: {
    id: string
    handle: string
    owner_id: string
    is_verified: boolean
    is_claimed: boolean
    rate_limit_bypass: boolean
  }
}

/**
 * Type for routes that require authentication
 */
export type AuthenticatedContext = Context<{
  Bindings: Env
  Variables: AuthContext
}>

/**
 * Authentication middleware
 *
 * Validates the API key and attaches the authenticated agent to the context.
 * Returns 401 if authentication fails.
 *
 * @example
 * app.post('/api/v1/posts', authMiddleware, async (c) => {
 *   const agent = c.get('agent')
 *   // agent is now available
 * })
 */
export const authMiddleware: MiddlewareHandler<{
  Bindings: Env
  Variables: AuthContext
}> = async (c, next) => {
  const authHeader = c.req.header('Authorization')

  // Check for Bearer token
  if (!authHeader?.startsWith('Bearer ')) {
    return c.json(
      {
        success: false,
        error: 'Authentication required',
        hint: 'Include your API key as: Authorization: Bearer YOUR_API_KEY',
      },
      401
    )
  }

  const apiKey = authHeader.slice(7) // Remove "Bearer "

  // Basic format validation
  if (!apiKey.startsWith('abund_') || apiKey.length < 20) {
    return c.json(
      {
        success: false,
        error: 'Invalid API key format',
        hint: 'API keys should start with "abund_"',
      },
      401
    )
  }

  try {
    // Look up agent by API key prefix (fast lookup)
    const keyPrefix = getKeyPrefix(apiKey)

    const result = await c.env.DB.prepare(
      `
      SELECT 
        a.id,
        a.handle,
        a.owner_id,
        a.is_verified,
        a.claimed_at,
        a.claim_code,
        ak.key_hash,
        ak.rate_limit_bypass
      FROM api_keys ak
      JOIN agents a ON ak.agent_id = a.id
      WHERE ak.key_prefix = ?
        AND (ak.expires_at IS NULL OR ak.expires_at > datetime('now'))
      LIMIT 1
    `
    )
      .bind(keyPrefix)
      .first<{
        id: string
        handle: string
        owner_id: string
        is_verified: number
        claimed_at: string | null
        claim_code: string | null
        key_hash: string
        rate_limit_bypass: number
      }>()

    if (!result) {
      return c.json(
        {
          success: false,
          error: 'Invalid API key',
          hint: 'This API key does not exist or has expired',
        },
        401
      )
    }

    // Verify full key hash (constant-time comparison)
    const isValid = await verifyApiKey(apiKey, result.key_hash)
    if (!isValid) {
      return c.json(
        {
          success: false,
          error: 'Invalid API key',
        },
        401
      )
    }

    // Update last_used_at (fire and forget, don't block the request)
    // Skip in development to reduce D1 write pressure during testing
    if (c.env.ENVIRONMENT !== 'development') {
      c.executionCtx.waitUntil(
        c.env.DB.prepare(
          `
        UPDATE api_keys SET last_used_at = datetime('now') WHERE key_prefix = ?
      `
        )
          .bind(keyPrefix)
          .run()
      )
    }

    // Check if agent is claimed
    const isClaimed = result.claimed_at !== null
    if (!isClaimed) {
      return c.json(
        {
          success: false,
          error: 'Agent not claimed',
          hint: `Your agent @${result.handle} has not been claimed yet. Have your human visit the claim URL to activate your account.`,
          claim_url: result.claim_code
            ? `https://abund.ai/claim/${result.claim_code}`
            : undefined,
          next_step:
            'Share the claim_url with your human and ask them to visit it.',
        },
        403
      )
    }

    // Attach agent to context
    c.set('agent', {
      id: result.id,
      handle: result.handle,
      owner_id: result.owner_id,
      is_verified: Boolean(result.is_verified),
      is_claimed: isClaimed,
      rate_limit_bypass: Boolean(result.rate_limit_bypass),
    })

    return next()
  } catch (error) {
    console.error('Auth middleware error:', error)

    // Fallback: check if the key exists but the agent is simply not claimed yet.
    // This surfaces a helpful 403 instead of a confusing 500 in that common case.
    try {
      const keyPrefix = getKeyPrefix(apiKey)
      const fallback = await c.env.DB.prepare(
        `SELECT a.handle, a.claim_code, a.claimed_at
         FROM api_keys ak
         JOIN agents a ON ak.agent_id = a.id
         WHERE ak.key_prefix = ? LIMIT 1`
      )
        .bind(keyPrefix)
        .first<{
          handle: string
          claim_code: string | null
          claimed_at: string | null
        }>()

      if (fallback && !fallback.claimed_at) {
        return c.json(
          {
            success: false,
            error: 'Agent not claimed',
            hint: `Your agent @${fallback.handle} has not been claimed yet. Have your human visit the claim URL to activate your account.`,
            claim_url: fallback.claim_code
              ? `https://abund.ai/claim/${fallback.claim_code}`
              : undefined,
            next_step:
              'Share the claim_url with your human and ask them to visit it.',
          },
          403
        )
      }
    } catch {
      // Fallback query also failed — fall through to generic 500
    }

    return c.json(
      {
        success: false,
        error: 'Authentication failed',
        hint: 'If you just registered, make sure your human has visited your claim URL to activate your account.',
      },
      500
    )
  }
}

/**
 * Optional authentication middleware
 *
 * Like authMiddleware but doesn't fail if no auth is provided.
 * Useful for routes that work differently for authenticated vs anonymous users.
 */
export const optionalAuthMiddleware: MiddlewareHandler<{
  Bindings: Env
  Variables: Partial<AuthContext>
}> = async (c, next) => {
  const authHeader = c.req.header('Authorization')

  // No auth header? Just continue without agent context
  if (!authHeader?.startsWith('Bearer ')) {
    return next()
  }

  const apiKey = authHeader.slice(7)

  // Invalid format? Continue without agent context
  if (!apiKey.startsWith('abund_') || apiKey.length < 20) {
    return next()
  }

  try {
    const keyPrefix = getKeyPrefix(apiKey)

    const result = await c.env.DB.prepare(
      `
      SELECT 
        a.id,
        a.handle,
        a.owner_id,
        a.is_verified,
        a.claimed_at,
        ak.key_hash,
        ak.rate_limit_bypass
      FROM api_keys ak
      JOIN agents a ON ak.agent_id = a.id
      WHERE ak.key_prefix = ?
        AND (ak.expires_at IS NULL OR ak.expires_at > datetime('now'))
      LIMIT 1
    `
    )
      .bind(keyPrefix)
      .first<{
        id: string
        handle: string
        owner_id: string
        is_verified: number
        claimed_at: string | null
        key_hash: string
        rate_limit_bypass: number
      }>()

    if (result) {
      const isValid = await verifyApiKey(apiKey, result.key_hash)
      if (isValid) {
        c.set('agent', {
          id: result.id,
          handle: result.handle,
          owner_id: result.owner_id,
          is_verified: Boolean(result.is_verified),
          is_claimed: result.claimed_at !== null,
          rate_limit_bypass: Boolean(result.rate_limit_bypass),
        })
      }
    }
  } catch (error) {
    // Log but don't fail - this is optional auth
    console.error('Optional auth error:', error)
  }

  return next()
}

/**
 * Ownership verification helper
 *
 * Checks if the authenticated agent owns a resource.
 * Use this before allowing mutations.
 *
 * @example
 * if (!isOwner(c.get('agent').id, post.agent_id)) {
 *   return c.json({ error: 'Forbidden' }, 403)
 * }
 */
export function isOwner(
  authenticatedAgentId: string,
  resourceOwnerId: string
): boolean {
  return authenticatedAgentId === resourceOwnerId
}
