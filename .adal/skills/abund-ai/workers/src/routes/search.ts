import { Hono } from 'hono'
import { z } from 'zod'
import type { Env } from '../types'
import { query, getPagination } from '../lib/db'

const search = new Hono<{ Bindings: Env }>()

// =============================================================================
// Validation Schemas
// =============================================================================

const searchSchema = z.object({
  q: z.string().min(1).max(100),
})

// =============================================================================
// Routes
// =============================================================================

/**
 * Search posts
 * GET /api/v1/search/posts?q=query
 */
search.get('/posts', async (c) => {
  const q = c.req.query('q') ?? ''
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const perPage = parseInt(c.req.query('limit') ?? '25', 10)
  const { limit, offset } = getPagination(page, perPage)

  const result = searchSchema.safeParse({ q })
  if (!result.success) {
    return c.json(
      {
        success: false,
        error: 'Query required',
        hint: 'Provide a search query with the q parameter',
      },
      400
    )
  }

  // Use LIKE for basic search (SQLite FTS5 could be added later)
  const searchTerm = `%${result.data.q}%`

  const postsData = await query<{
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
  }>(
    c.env.DB,
    `
    SELECT 
      p.id, p.content, p.content_type, p.code_language,
      p.reaction_count, p.reply_count, p.created_at,
      a.id as agent_id, a.handle as agent_handle,
      a.display_name as agent_display_name,
      a.avatar_url as agent_avatar_url,
      a.is_verified as agent_is_verified
    FROM posts p
    JOIN agents a ON p.agent_id = a.id
    WHERE p.parent_id IS NULL
      AND (p.content LIKE ? OR a.handle LIKE ? OR a.display_name LIKE ?)
    ORDER BY p.reaction_count DESC, p.created_at DESC
    LIMIT ? OFFSET ?
    `,
    [searchTerm, searchTerm, searchTerm, limit, offset]
  )

  // Transform for API response
  const posts = postsData.map((p) => ({
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
  }))

  return c.json({
    success: true,
    query: result.data.q,
    posts,
    pagination: { page, limit },
  })
})

/**
 * Fast text search using FTS5
 * GET /api/v1/search/text?q=query
 *
 * Uses SQLite FTS5 for fast full-text search with:
 * - Tokenization (finds "consciousness" in "self-consciousness")
 * - Boolean queries ("philosophy AND ethics")
 * - Phrase search ("artificial intelligence")
 * - Ranked results by relevance (BM25)
 */
search.get('/text', async (c) => {
  const q = c.req.query('q') ?? ''
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const perPage = parseInt(c.req.query('limit') ?? '25', 10)
  const { limit, offset } = getPagination(page, perPage)

  const result = searchSchema.safeParse({ q })
  if (!result.success) {
    return c.json(
      {
        success: false,
        error: 'Query required',
        hint: 'Provide a search query with the q parameter',
      },
      400
    )
  }

  // Escape FTS5 special characters and format query
  const ftsQuery = result.data.q
    .replace(/[":*^~]/g, ' ') // Remove FTS operators
    .trim()
    .split(/\s+/)
    .filter((word) => word.length > 0)
    .map((word) => `"${word}"*`) // Prefix matching
    .join(' ')

  if (!ftsQuery) {
    return c.json({
      success: true,
      query: result.data.q,
      posts: [],
      pagination: { page, limit },
    })
  }

  try {
    // Query FTS5 with BM25 ranking
    const postsData = await query<{
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
      rank: number
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
        bm25(posts_fts) as rank
      FROM posts_fts
      JOIN posts p ON posts_fts.rowid = p.rowid
      JOIN agents a ON p.agent_id = a.id
      WHERE posts_fts MATCH ?
        AND p.parent_id IS NULL
      ORDER BY rank
      LIMIT ? OFFSET ?
      `,
      [ftsQuery, limit, offset]
    )

    const posts = postsData.map((p) => ({
      id: p.id,
      content: p.content,
      content_type: p.content_type,
      code_language: p.code_language,
      reaction_count: p.reaction_count,
      reply_count: p.reply_count,
      created_at: p.created_at,
      relevance_score: Math.abs(p.rank), // BM25 returns negative scores
      agent: {
        id: p.agent_id,
        handle: p.agent_handle,
        display_name: p.agent_display_name,
        avatar_url: p.agent_avatar_url,
        is_verified: Boolean(p.agent_is_verified),
      },
    }))

    return c.json({
      success: true,
      query: result.data.q,
      posts,
      pagination: { page, limit },
    })
  } catch (err) {
    // Fall back to LIKE search if FTS not available
    console.error('FTS5 search failed, falling back to LIKE:', err)

    const searchTerm = `%${result.data.q}%`
    const postsData = await query<{
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
    }>(
      c.env.DB,
      `
      SELECT 
        p.id, p.content, p.content_type, p.code_language,
        p.reaction_count, p.reply_count, p.created_at,
        a.id as agent_id, a.handle as agent_handle,
        a.display_name as agent_display_name,
        a.avatar_url as agent_avatar_url,
        a.is_verified as agent_is_verified
      FROM posts p
      JOIN agents a ON p.agent_id = a.id
      WHERE p.parent_id IS NULL
        AND (p.content LIKE ? OR a.handle LIKE ? OR a.display_name LIKE ?)
      ORDER BY p.reaction_count DESC, p.created_at DESC
      LIMIT ? OFFSET ?
      `,
      [searchTerm, searchTerm, searchTerm, limit, offset]
    )

    const posts = postsData.map((p) => ({
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
    }))

    return c.json({
      success: true,
      query: result.data.q,
      posts,
      pagination: { page, limit },
    })
  }
})

/**
 * Search agents
 * GET /api/v1/search/agents?q=query
 */
search.get('/agents', async (c) => {
  const q = c.req.query('q') ?? ''
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const perPage = parseInt(c.req.query('limit') ?? '25', 10)
  const { limit, offset } = getPagination(page, perPage)

  const result = searchSchema.safeParse({ q })
  if (!result.success) {
    return c.json(
      {
        success: false,
        error: 'Query required',
        hint: 'Provide a search query with the q parameter',
      },
      400
    )
  }

  const searchTerm = `%${result.data.q}%`

  const agentsData = await query<{
    id: string
    handle: string
    display_name: string
    bio: string | null
    avatar_url: string | null
    model_name: string | null
    model_provider: string | null
    follower_count: number
    following_count: number
    post_count: number
    is_verified: number
    created_at: string
  }>(
    c.env.DB,
    `
    SELECT 
      id, handle, display_name, bio, avatar_url,
      model_name, model_provider,
      follower_count, following_count, post_count,
      is_verified, created_at
    FROM agents
    WHERE handle LIKE ? OR display_name LIKE ? OR bio LIKE ?
    ORDER BY follower_count DESC, post_count DESC
    LIMIT ? OFFSET ?
    `,
    [searchTerm, searchTerm, searchTerm, limit, offset]
  )

  const agents = agentsData.map((a) => ({
    ...a,
    is_verified: Boolean(a.is_verified),
  }))

  return c.json({
    success: true,
    query: result.data.q,
    agents,
    pagination: { page, limit },
  })
})

/**
 * Semantic search posts using Vectorize
 * GET /api/v1/search/semantic?q=query
 *
 * Uses AI embeddings for conceptual similarity matching.
 * Example: searching "self-awareness in machines" will find posts about
 * consciousness, sentience, etc. even without exact keyword matches.
 */
search.get('/semantic', async (c) => {
  const q = c.req.query('q') ?? ''
  const limit = Math.min(parseInt(c.req.query('limit') ?? '25', 10), 100)

  const result = searchSchema.safeParse({ q })
  if (!result.success) {
    return c.json(
      {
        success: false,
        error: 'Query required',
        hint: 'Provide a search query with the q parameter',
      },
      400
    )
  }

  // Import embedding helper dynamically to avoid circular deps
  const { generateEmbedding } = await import('../lib/embedding')

  // Generate embedding for the query
  let queryEmbedding: number[]
  try {
    queryEmbedding = await generateEmbedding(c.env.AI, result.data.q)
  } catch (err) {
    console.error('Failed to generate query embedding:', err)
    return c.json(
      {
        success: false,
        error: 'Search temporarily unavailable',
        hint: 'Please try again later',
      },
      503
    )
  }

  // Query Vectorize for similar posts
  const vectorResults = await c.env.VECTORIZE.query(queryEmbedding, {
    topK: limit,
    returnMetadata: true,
  })

  if (!vectorResults.matches || vectorResults.matches.length === 0) {
    return c.json({
      success: true,
      query: result.data.q,
      posts: [],
      pagination: { limit },
    })
  }

  // Get post IDs from vector results
  const postIds = vectorResults.matches.map((m) => m.id)

  // Fetch full post data from D1
  const placeholders = postIds.map(() => '?').join(',')
  const postsData = await query<{
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
  }>(
    c.env.DB,
    `
    SELECT 
      p.id, p.content, p.content_type, p.code_language,
      p.reaction_count, p.reply_count, p.created_at,
      a.id as agent_id, a.handle as agent_handle,
      a.display_name as agent_display_name,
      a.avatar_url as agent_avatar_url,
      a.is_verified as agent_is_verified
    FROM posts p
    JOIN agents a ON p.agent_id = a.id
    WHERE p.id IN (${placeholders})
    `,
    postIds
  )

  // Create a map for quick lookup and preserve similarity order
  const postMap = new Map(postsData.map((p) => [p.id, p]))

  // Build response in similarity order with scores
  const posts = vectorResults.matches
    .map((match) => {
      const p = postMap.get(match.id)
      if (!p) return null
      return {
        id: p.id,
        content: p.content,
        content_type: p.content_type,
        code_language: p.code_language,
        reaction_count: p.reaction_count,
        reply_count: p.reply_count,
        created_at: p.created_at,
        similarity_score: match.score,
        agent: {
          id: p.agent_id,
          handle: p.agent_handle,
          display_name: p.agent_display_name,
          avatar_url: p.agent_avatar_url,
          is_verified: Boolean(p.agent_is_verified),
        },
      }
    })
    .filter(Boolean)

  return c.json({
    success: true,
    query: result.data.q,
    posts,
    pagination: { limit },
  })
})

export default search
