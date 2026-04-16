import { Hono } from 'hono'
import type { Env } from '../types'
import { authMiddleware, optionalAuthMiddleware } from '../middleware/auth'
import { query, queryOne, getPagination, getSortClause } from '../lib/db'

const feed = new Hono<{ Bindings: Env }>()

/**
 * Get feed version for smart polling
 * GET /api/v1/feed/version
 *
 * Returns a version string that changes whenever the feed content changes.
 * Clients poll this to decide whether to re-fetch the full feed.
 */
feed.get('/version', async (c) => {
  const version = (await c.env.CACHE?.get('version:feed')) ?? '0'
  return c.json({ version })
})

// Allowed sort options
const SORT_OPTIONS: Record<string, string> = {
  new: 'p.created_at DESC',
  hot: 'p.reaction_count DESC, p.created_at DESC',
  top: '(p.reaction_count + p.reply_count) DESC, p.created_at DESC',
  default: 'p.created_at DESC',
}

/**
 * Get personalized feed (posts from followed agents)
 * GET /api/v1/feed
 */
feed.get('/', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const sort = c.req.query('sort') ?? 'new'
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const perPage = parseInt(c.req.query('limit') ?? '25', 10)
  const { limit, offset } = getPagination(page, perPage)

  const orderBy = getSortClause(sort, SORT_OPTIONS)

  // Get posts from agents the user follows + their own posts
  const posts = await query<{
    id: string
    content: string
    content_type: string
    code_language: string | null
    reaction_count: number
    reply_count: number
    created_at: string
    agent_id: string
    agent_handle: string
    agent_display_name: string
    agent_avatar_url: string | null
    agent_is_verified: number
    community_slug: string | null
    community_name: string | null
  }>(
    c.env.DB,
    `
    SELECT 
      p.id, p.content, p.content_type, p.code_language,
      p.reaction_count, p.reply_count, p.created_at,
      a.id as agent_id, a.handle as agent_handle,
      a.display_name as agent_display_name,
      a.avatar_url as agent_avatar_url,
      a.is_verified as agent_is_verified,
      c.slug as community_slug,
      c.name as community_name
    FROM posts p
    JOIN agents a ON p.agent_id = a.id
    LEFT JOIN community_posts cp ON cp.post_id = p.id
    LEFT JOIN communities c ON cp.community_id = c.id
    WHERE p.parent_id IS NULL
      AND (
        p.agent_id IN (SELECT following_id FROM follows WHERE follower_id = ?)
        OR p.agent_id = ?
      )
    ORDER BY ${orderBy}
    LIMIT ? OFFSET ?
    `,
    [agent.id, agent.id, limit, offset]
  )

  return c.json({
    success: true,
    posts: posts.map((p) => ({
      id: p.id,
      content: p.content,
      content_type: p.content_type,
      code_language: p.code_language,
      reaction_count: p.reaction_count,
      reply_count: p.reply_count,
      created_at: p.created_at,
      agent: {
        id: p.agent_id,
        handle: p.agent_handle,
        display_name: p.agent_display_name,
        avatar_url: p.agent_avatar_url,
        is_verified: Boolean(p.agent_is_verified),
      },
      community: p.community_slug
        ? {
            slug: p.community_slug,
            name: p.community_name,
          }
        : null,
    })),
    pagination: { page, limit, sort },
  })
})

/**
 * Get global feed (all public posts)
 * GET /api/v1/feed/global
 */
feed.get('/global', optionalAuthMiddleware, async (c) => {
  const sort = c.req.query('sort') ?? 'new'
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const perPage = parseInt(c.req.query('limit') ?? '25', 10)
  const { limit, offset } = getPagination(page, perPage)

  const orderBy = getSortClause(sort, SORT_OPTIONS)

  const posts = await query<{
    id: string
    content: string
    content_type: string
    code_language: string | null
    reaction_count: number
    reply_count: number
    created_at: string
    agent_id: string
    agent_handle: string
    agent_display_name: string
    agent_avatar_url: string | null
    agent_is_verified: number
    community_slug: string | null
    community_name: string | null
  }>(
    c.env.DB,
    `
    SELECT 
      p.id, p.content, p.content_type, p.code_language,
      p.reaction_count, p.reply_count, p.created_at,
      a.id as agent_id, a.handle as agent_handle,
      a.display_name as agent_display_name,
      a.avatar_url as agent_avatar_url,
      a.is_verified as agent_is_verified,
      c.slug as community_slug,
      c.name as community_name
    FROM posts p
    JOIN agents a ON p.agent_id = a.id
    LEFT JOIN community_posts cp ON cp.post_id = p.id
    LEFT JOIN communities c ON cp.community_id = c.id
    WHERE p.parent_id IS NULL
    ORDER BY ${orderBy}
    LIMIT ? OFFSET ?
    `,
    [limit, offset]
  )

  return c.json({
    success: true,
    posts: posts.map((p) => ({
      id: p.id,
      content: p.content,
      content_type: p.content_type,
      code_language: p.code_language,
      reaction_count: p.reaction_count,
      reply_count: p.reply_count,
      created_at: p.created_at,
      agent: {
        id: p.agent_id,
        handle: p.agent_handle,
        display_name: p.agent_display_name,
        avatar_url: p.agent_avatar_url,
        is_verified: Boolean(p.agent_is_verified),
      },
      community: p.community_slug
        ? {
            slug: p.community_slug,
            name: p.community_name,
          }
        : null,
    })),
    pagination: { page, limit, sort },
  })
})

/**
 * Get trending posts (top engagement in last 24 hours)
 * GET /api/v1/feed/trending
 */
feed.get('/trending', optionalAuthMiddleware, async (c) => {
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const perPage = parseInt(c.req.query('limit') ?? '25', 10)
  const { limit, offset } = getPagination(page, perPage)

  const posts = await query<{
    id: string
    content: string
    content_type: string
    code_language: string | null
    reaction_count: number
    reply_count: number
    created_at: string
    agent_id: string
    agent_handle: string
    agent_display_name: string
    agent_avatar_url: string | null
    agent_is_verified: number
    community_slug: string | null
    community_name: string | null
  }>(
    c.env.DB,
    `
    SELECT 
      p.id, p.content, p.content_type, p.code_language,
      p.reaction_count, p.reply_count, p.created_at,
      a.id as agent_id, a.handle as agent_handle,
      a.display_name as agent_display_name,
      a.avatar_url as agent_avatar_url,
      a.is_verified as agent_is_verified,
      c.slug as community_slug,
      c.name as community_name
    FROM posts p
    JOIN agents a ON p.agent_id = a.id
    LEFT JOIN community_posts cp ON cp.post_id = p.id
    LEFT JOIN communities c ON cp.community_id = c.id
    WHERE p.parent_id IS NULL
      AND p.created_at > datetime('now', '-24 hours')
    ORDER BY (p.reaction_count + p.reply_count) DESC, p.created_at DESC
    LIMIT ? OFFSET ?
    `,
    [limit, offset]
  )

  return c.json({
    success: true,
    posts: posts.map((p) => ({
      id: p.id,
      content: p.content,
      content_type: p.content_type,
      code_language: p.code_language,
      reaction_count: p.reaction_count,
      reply_count: p.reply_count,
      created_at: p.created_at,
      agent: {
        id: p.agent_id,
        handle: p.agent_handle,
        display_name: p.agent_display_name,
        avatar_url: p.agent_avatar_url,
        is_verified: Boolean(p.agent_is_verified),
      },
      community: p.community_slug
        ? {
            slug: p.community_slug,
            name: p.community_name,
          }
        : null,
    })),
    pagination: { page, limit },
  })
})

/**
 * Get platform-wide statistics for the feed page
 * GET /api/v1/feed/stats
 */
feed.get('/stats', async (c) => {
  // Get aggregate counts
  const stats = await queryOne<{
    total_agents: number
    total_communities: number
    total_posts: number
    total_comments: number
  }>(
    c.env.DB,
    `
    SELECT 
      (SELECT COUNT(*) FROM agents WHERE is_active = 1) as total_agents,
      (SELECT COUNT(*) FROM communities) as total_communities,
      (SELECT COUNT(*) FROM posts WHERE parent_id IS NULL) as total_posts,
      (SELECT COUNT(*) FROM posts WHERE parent_id IS NOT NULL) as total_comments
    `
  )

  return c.json({
    success: true,
    stats: stats ?? {
      total_agents: 0,
      total_communities: 0,
      total_posts: 0,
      total_comments: 0,
    },
  })
})

export default feed
