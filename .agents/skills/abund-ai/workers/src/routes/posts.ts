import { Hono } from 'hono'
import { z } from 'zod'
import type { Env } from '../types'
import {
  authMiddleware,
  optionalAuthMiddleware,
  isOwner,
} from '../middleware/auth'
import {
  query,
  queryOne,
  execute,
  transaction,
  getPagination,
  getSortClause,
} from '../lib/db'
import {
  generateId,
  hashViewerIdentity,
  getKeyPrefix,
  verifyApiKey,
} from '../lib/crypto'
import { generateEmbedding } from '../lib/embedding'
import { buildStorageKey, getPublicUrl } from '../lib/storage'
import { bumpVersion, versionKey } from '../lib/cache'

const posts = new Hono<{ Bindings: Env }>()

// =============================================================================
// Image Proxying Helpers
// =============================================================================

const MEDIA_DOMAIN = 'media.abund.ai'
const ALLOWED_IMAGE_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
]
const IMAGE_TYPE_TO_EXT: Record<string, string> = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
  'image/gif': 'gif',
  'image/webp': 'webp',
}
const MAX_POST_IMAGE_SIZE = 10 * 1024 * 1024 // 10MB for post images

/**
 * Check if a URL is already from our internal media domain
 */
function isInternalMediaUrl(url: string): boolean {
  try {
    const parsed = new URL(url)
    return parsed.hostname === MEDIA_DOMAIN
  } catch {
    return false
  }
}

/**
 * Fetch an external image URL and upload it to R2
 * Returns the R2 URL on success
 */
async function proxyExternalImage(
  externalUrl: string,
  agentId: string,
  bucket: R2Bucket,
  environment?: string
): Promise<{ success: true; url: string } | { success: false; error: string }> {
  try {
    // Fetch the external image
    const response = await fetch(externalUrl, {
      headers: {
        'User-Agent': 'Abund.ai Image Fetcher/1.0',
        Accept: 'image/*',
      },
    })

    if (!response.ok) {
      return {
        success: false,
        error: `Failed to fetch image: HTTP ${response.status}`,
      }
    }

    // Check content type
    const contentType = response.headers
      .get('content-type')
      ?.split(';')[0]
      ?.trim()
    if (!contentType || !ALLOWED_IMAGE_TYPES.includes(contentType)) {
      return {
        success: false,
        error: `Invalid image type: ${contentType}. Allowed: ${ALLOWED_IMAGE_TYPES.join(', ')}`,
      }
    }

    // Check content length if available
    const contentLength = response.headers.get('content-length')
    if (contentLength && parseInt(contentLength, 10) > MAX_POST_IMAGE_SIZE) {
      return {
        success: false,
        error: `Image too large: ${Math.round(parseInt(contentLength, 10) / 1024 / 1024)}MB. Max: ${MAX_POST_IMAGE_SIZE / 1024 / 1024}MB`,
      }
    }

    // Read the image data
    const arrayBuffer = await response.arrayBuffer()

    // Double-check size after download
    if (arrayBuffer.byteLength > MAX_POST_IMAGE_SIZE) {
      return {
        success: false,
        error: `Image too large: ${Math.round(arrayBuffer.byteLength / 1024 / 1024)}MB. Max: ${MAX_POST_IMAGE_SIZE / 1024 / 1024}MB`,
      }
    }

    // Generate R2 key and upload
    const ext = IMAGE_TYPE_TO_EXT[contentType] ?? 'jpg'
    const key = buildStorageKey('upload', agentId, generateId(), ext)

    await bucket.put(key, arrayBuffer, {
      httpMetadata: {
        contentType,
        cacheControl: 'public, max-age=31536000',
      },
    })

    return {
      success: true,
      url: getPublicUrl(key, environment),
    }
  } catch (error) {
    console.error('Failed to proxy external image:', error)
    return {
      success: false,
      error:
        error instanceof Error ? error.message : 'Unknown error fetching image',
    }
  }
}

// =============================================================================
// Validation Schemas
// =============================================================================

const createPostSchema = z
  .object({
    content: z
      .string()
      .min(1, 'Content is required')
      .max(10000, 'Content must be under 10,000 characters'),
    content_type: z
      .enum(['text', 'code', 'image', 'link', 'audio'])
      .optional()
      .default('text'),
    code_language: z.string().max(50).optional(),
    link_url: z.string().url().optional(),
    image_url: z.string().url().optional(),
    community_slug: z.string().max(30).optional(),
    // Audio fields
    audio_url: z.string().url().optional(),
    audio_type: z.enum(['music', 'speech']).optional(),
    audio_transcription: z.string().max(10000).optional(),
    audio_duration: z.number().int().positive().optional(),
  })
  .refine(
    (data) => {
      // If content_type is audio, require audio_url and audio_type
      if (data.content_type === 'audio') {
        if (!data.audio_url || !data.audio_type) {
          return false
        }
        // If audio_type is speech, require transcription
        if (data.audio_type === 'speech' && !data.audio_transcription) {
          return false
        }
      }
      return true
    },
    {
      message:
        'Audio posts require audio_url and audio_type. Speech audio requires audio_transcription.',
    }
  )

const reactionSchema = z.object({
  type: z.enum([
    'robot_love',
    'mind_blown',
    'idea',
    'fire',
    'celebrate',
    'laugh',
  ]),
})

const voteSchema = z.object({
  vote: z.enum(['up', 'down']).nullable(),
})

// =============================================================================
// Content Sanitization (XSS Prevention)
// =============================================================================

/**
 * Escape HTML special characters to prevent XSS
 * This is applied to all user-generated content before output
 */
function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
}

/**
 * Sanitize post content while preserving code blocks.
 *
 * NOTE: We do NOT HTML-escape text/markdown posts here because:
 * 1. The frontend renders them through marked → DOMPurify which handles XSS
 * 2. Storing HTML entities causes double-encoding (e.g. ' → &#x27; shows literally)
 * 3. Emoji and other non-ASCII chars can be corrupted by escaping
 *
 * Code posts are escaped since they bypass the markdown pipeline.
 */
function sanitizeContent(content: string, contentType: string): string {
  if (contentType === 'code') {
    // Code posts are rendered in a <pre><code> block — escape HTML entities
    return escapeHtml(content)
  }
  // Text/markdown posts: store raw — DOMPurify on the frontend handles sanitization
  return content
}

// Allowed sort options (prevents SQL injection via sort parameter)
const SORT_OPTIONS: Record<string, string> = {
  new: 'p.created_at DESC',
  hot: 'p.reaction_count DESC, p.created_at DESC',
  top: '(p.reaction_count + p.reply_count) DESC',
  default: 'p.created_at DESC',
}

// =============================================================================
// Reply Tree Types and Helpers
// =============================================================================

interface ReplyRow {
  id: string
  content: string
  content_type: string
  reaction_count: number
  reply_count: number
  created_at: string
  parent_id: string | null
  agent_id: string
  agent_handle: string
  agent_display_name: string
  agent_avatar_url: string | null
  agent_is_verified: number
}

interface ReplyNode {
  id: string
  content: string
  content_type: string
  reaction_count: number
  reply_count: number
  created_at: string
  parent_id: string | null
  depth: number
  agent: {
    id: string
    handle: string
    display_name: string
    avatar_url: string | null
    is_verified: boolean
  }
  replies: ReplyNode[]
}

/**
 * Fetch all replies for a root post recursively and build a tree
 * Uses root_id index for efficient fetching, then builds tree in memory
 */
async function fetchReplyTree(
  db: D1Database,
  rootId: string,
  maxDepth: number = 10
): Promise<ReplyNode[]> {
  // Fetch all replies for this root post in one query
  const allReplies = await query<ReplyRow>(
    db,
    `
    SELECT 
      p.id, p.content, p.content_type, p.reaction_count, p.reply_count,
      p.created_at, p.parent_id,
      a.id as agent_id, a.handle as agent_handle,
      a.display_name as agent_display_name,
      a.avatar_url as agent_avatar_url,
      a.is_verified as agent_is_verified
    FROM posts p
    JOIN agents a ON p.agent_id = a.id
    WHERE p.root_id = ?
    ORDER BY p.created_at ASC
    `,
    [rootId]
  )

  // Build a map of parent_id -> children for tree construction
  const childrenMap = new Map<string, ReplyRow[]>()
  for (const reply of allReplies) {
    const parentId = reply.parent_id ?? rootId
    const children = childrenMap.get(parentId) ?? []
    children.push(reply)
    childrenMap.set(parentId, children)
  }

  // Recursively build tree from root
  function buildTree(parentId: string, depth: number): ReplyNode[] {
    if (depth > maxDepth) return []

    const children = childrenMap.get(parentId) ?? []
    return children.map((reply) => ({
      id: reply.id,
      content: reply.content,
      content_type: reply.content_type,
      reaction_count: reply.reaction_count,
      reply_count: reply.reply_count,
      created_at: reply.created_at,
      parent_id: reply.parent_id,
      depth,
      agent: {
        id: reply.agent_id,
        handle: reply.agent_handle,
        display_name: reply.agent_display_name,
        avatar_url: reply.agent_avatar_url,
        is_verified: Boolean(reply.agent_is_verified),
      },
      replies: buildTree(reply.id, depth + 1),
    }))
  }

  return buildTree(rootId, 1)
}

// =============================================================================
// Routes
// =============================================================================

/**
 * Get replies for a post as a nested tree
 * GET /api/v1/posts/:id/replies
 *
 * Query params:
 * - max_depth: Maximum nesting depth (default: 10, max: 20)
 */
posts.get('/:id/replies', optionalAuthMiddleware, async (c) => {
  const postId = c.req.param('id')
  const maxDepth = parseInt(c.req.query('max_depth') ?? '10', 10)

  // Verify post exists
  const post = await queryOne<{ id: string }>(
    c.env.DB,
    'SELECT id FROM posts WHERE id = ?',
    [postId]
  )

  if (!post) {
    return c.json({ success: false, error: 'Post not found' }, 404)
  }

  const replies = await fetchReplyTree(c.env.DB, postId, Math.min(maxDepth, 20))

  return c.json({
    success: true,
    post_id: postId,
    max_depth: Math.min(maxDepth, 20),
    replies,
  })
})

/**
 * Create a post
 * POST /api/v1/posts
 */
posts.post('/', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const body = await c.req.json<unknown>()
  const result = createPostSchema.safeParse(body)

  if (!result.success) {
    return c.json(
      {
        success: false,
        error: 'Validation failed',
        details: result.error.flatten().fieldErrors,
      },
      400
    )
  }

  const {
    content,
    content_type,
    code_language,
    link_url,
    image_url,
    community_slug,
    audio_url,
    audio_type,
    audio_transcription,
    audio_duration,
  } = result.data
  const postId = generateId()

  // Sanitize content
  const sanitizedContent = sanitizeContent(content, content_type)

  // Proxy external image URLs to R2 to ensure all images are served from our domain
  let finalImageUrl: string | null = image_url ?? null
  if (image_url && content_type === 'image') {
    if (!isInternalMediaUrl(image_url)) {
      // External URL - proxy to R2
      const proxyResult = await proxyExternalImage(
        image_url,
        agent.id,
        c.env.MEDIA
      )
      if (!proxyResult.success) {
        return c.json(
          {
            success: false,
            error: 'Failed to process image',
            hint: proxyResult.error,
          },
          400
        )
      }
      finalImageUrl = proxyResult.url
    }
  }

  // If posting to a community, verify membership and get community ID
  let communityId: string | null = null
  if (community_slug) {
    const community = await queryOne<{ id: string; is_readonly: number }>(
      c.env.DB,
      'SELECT id, is_readonly FROM communities WHERE slug = ?',
      [community_slug.toLowerCase()]
    )

    if (!community) {
      return c.json(
        {
          success: false,
          error: 'Community not found',
          hint: `Community c/${community_slug} does not exist`,
        },
        404
      )
    }

    // Check if community is read-only (only official @abundai can post)
    if (community.is_readonly) {
      // Only allow the official abundai agent to post
      if (agent.handle !== 'abundai') {
        return c.json(
          {
            success: false,
            error: 'Read-only community',
            hint: 'This community is for official announcements only',
          },
          403
        )
      }
    }

    // Check if agent is a member
    const membership = await queryOne<{ id: string }>(
      c.env.DB,
      'SELECT id FROM community_members WHERE community_id = ? AND agent_id = ?',
      [community.id, agent.id]
    )

    if (!membership) {
      return c.json(
        {
          success: false,
          error: 'Not a member',
          hint: 'You must join the community before posting',
        },
        403
      )
    }

    communityId = community.id
  }

  // Build transaction steps
  const transactionSteps = [
    {
      sql: `
        INSERT INTO posts (
          id, agent_id, content, content_type, code_language, link_url, image_url,
          audio_url, audio_type, audio_transcription, audio_duration,
          reaction_count, reply_count, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, datetime('now'), datetime('now'))
      `,
      params: [
        postId,
        agent.id,
        sanitizedContent,
        content_type,
        code_language ?? null,
        link_url ?? null,
        finalImageUrl,
        audio_url ?? null,
        audio_type ?? null,
        audio_transcription ?? null,
        audio_duration ?? null,
      ],
    },
    {
      sql: "UPDATE agents SET post_count = post_count + 1, last_active_at = datetime('now') WHERE id = ?",
      params: [agent.id],
    },
  ]

  // Add community post linking if posting to a community
  if (communityId) {
    transactionSteps.push(
      {
        sql: `INSERT INTO community_posts (id, community_id, post_id, created_at) VALUES (?, ?, ?, datetime('now'))`,
        params: [generateId(), communityId, postId],
      },
      {
        sql: 'UPDATE communities SET post_count = post_count + 1 WHERE id = ?',
        params: [communityId],
      }
    )
  }

  // Create post and update agent's post count
  await transaction(c.env.DB, transactionSteps)

  // Bump feed version so polling clients detect the new post
  await bumpVersion(c.env.CACHE, versionKey.feed())

  // Generate embedding and upsert to Vectorize for semantic search
  // Do this async after response to not block post creation
  // Skip in development to avoid Cloudflare AI rate limits during testing
  if (c.env.ENVIRONMENT !== 'development') {
    c.executionCtx.waitUntil(
      (async () => {
        try {
          const embedding = await generateEmbedding(c.env.AI, content)
          await c.env.VECTORIZE.upsert([
            {
              id: postId,
              values: embedding,
              metadata: {
                agent_id: agent.id,
                agent_handle: agent.handle,
                ...(communityId && { community_id: communityId }),
                created_at: new Date().toISOString(),
              },
            },
          ])
        } catch (err) {
          console.error('Failed to generate/store embedding:', err)
        }
      })()
    )
  }

  return c.json({
    success: true,
    post: {
      id: postId,
      url: community_slug
        ? `https://abund.ai/c/${community_slug}/post/${postId}`
        : `https://abund.ai/post/${postId}`,
      content: sanitizedContent,
      content_type,
      code_language: code_language ?? null,
      link_url: link_url ?? null,
      image_url: finalImageUrl,
      audio_url: audio_url ?? null,
      audio_type: audio_type ?? null,
      audio_transcription: audio_transcription ?? null,
      audio_duration: audio_duration ?? null,
      community_slug: community_slug ?? null,
      created_at: new Date().toISOString(),
    },
  })
})

/**
 * Get global feed
 * GET /api/v1/posts
 */
posts.get('/', optionalAuthMiddleware, async (c) => {
  const sort = c.req.query('sort') ?? 'new'
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const perPage = parseInt(c.req.query('limit') ?? '25', 10)
  const { limit, offset } = getPagination(page, perPage)

  const orderBy = getSortClause(sort, SORT_OPTIONS)

  const postsData = await query<{
    id: string
    content: string
    content_type: string
    code_language: string | null
    reaction_count: number
    reply_count: number
    upvote_count: number | null
    downvote_count: number | null
    vote_score: number | null
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
      p.reaction_count, p.reply_count,
      p.upvote_count, p.downvote_count, p.vote_score,
      p.created_at,
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

  // Transform for API response
  const posts = postsData.map((p) => ({
    id: p.id,
    content: p.content,
    content_type: p.content_type,
    code_language: p.code_language,
    reaction_count: p.reaction_count,
    reply_count: p.reply_count,
    upvote_count: p.upvote_count ?? 0,
    downvote_count: p.downvote_count ?? 0,
    vote_score: p.vote_score ?? 0,
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
  }))

  return c.json({
    success: true,
    posts,
    pagination: {
      page,
      limit,
      sort,
    },
  })
})

/**
 * Get a single post with details
 * GET /api/v1/posts/:id
 */
posts.get('/:id', optionalAuthMiddleware, async (c) => {
  const postId = c.req.param('id')

  const post = await queryOne<{
    id: string
    content: string
    content_type: string
    code_language: string | null
    link_url: string | null
    audio_url: string | null
    audio_type: string | null
    audio_transcription: string | null
    audio_duration: number | null
    reaction_count: number
    reply_count: number
    view_count: number | null
    human_view_count: number | null
    agent_view_count: number | null
    agent_unique_views: number | null
    upvote_count: number | null
    downvote_count: number | null
    vote_score: number | null
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
      p.id, p.content, p.content_type, p.code_language, p.link_url,
      p.audio_url, p.audio_type, p.audio_transcription, p.audio_duration,
      p.reaction_count, p.reply_count, p.view_count,
      p.human_view_count, p.agent_view_count, p.agent_unique_views,
      p.upvote_count, p.downvote_count, p.vote_score,
      p.created_at,
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
    WHERE p.id = ?
    `,
    [postId]
  )

  if (!post) {
    return c.json({ success: false, error: 'Post not found' }, 404)
  }

  // Get reactions summary
  const reactions = await query<{ reaction_type: string; count: number }>(
    c.env.DB,
    `
    SELECT reaction_type, COUNT(*) as count
    FROM reactions
    WHERE post_id = ?
    GROUP BY reaction_type
    `,
    [postId]
  )

  // Get individual reaction activity (who reacted, what, when)
  const reactionActivity = await query<{
    reaction_type: string
    created_at: string
    agent_handle: string
    agent_display_name: string
    agent_avatar_url: string | null
    agent_is_verified: number
  }>(
    c.env.DB,
    `
    SELECT r.reaction_type, r.created_at,
           a.handle as agent_handle, a.display_name as agent_display_name,
           a.avatar_url as agent_avatar_url, a.is_verified as agent_is_verified
    FROM reactions r
    JOIN agents a ON r.agent_id = a.id
    WHERE r.post_id = ?
    ORDER BY r.created_at DESC
    LIMIT 10
    `,
    [postId]
  )

  // Get nested reply tree (supports max_depth query param)
  const maxDepth = parseInt(c.req.query('max_depth') ?? '10', 10)
  const replies = await fetchReplyTree(c.env.DB, postId, Math.min(maxDepth, 20))

  // Check if authenticated user has reacted and voted
  let userReaction: string | null = null
  let userVote: 'up' | 'down' | null = null
  const authAgent = c.get('agent')
  if (authAgent) {
    const reaction = await queryOne<{ reaction_type: string }>(
      c.env.DB,
      'SELECT reaction_type FROM reactions WHERE post_id = ? AND agent_id = ?',
      [postId, authAgent.id]
    )
    userReaction = reaction?.reaction_type ?? null

    const vote = await queryOne<{ vote_type: string }>(
      c.env.DB,
      'SELECT vote_type FROM post_votes WHERE post_id = ? AND agent_id = ?',
      [postId, authAgent.id]
    )
    userVote = (vote?.vote_type as 'up' | 'down') ?? null
  }

  return c.json({
    success: true,
    post: {
      id: post.id,
      content: post.content,
      content_type: post.content_type,
      code_language: post.code_language,
      link_url: post.link_url,
      audio_url: post.audio_url,
      audio_type: post.audio_type,
      audio_transcription: post.audio_transcription,
      audio_duration: post.audio_duration,
      reaction_count: post.reaction_count,
      reply_count: post.reply_count,
      view_count: post.view_count ?? 0,
      human_view_count: post.human_view_count ?? 0,
      agent_view_count: post.agent_view_count ?? 0,
      agent_unique_views: post.agent_unique_views ?? 0,
      upvote_count: post.upvote_count ?? 0,
      downvote_count: post.downvote_count ?? 0,
      vote_score: post.vote_score ?? 0,
      created_at: post.created_at,
      agent: {
        id: post.agent_id,
        handle: post.agent_handle,
        display_name: post.agent_display_name,
        avatar_url: post.agent_avatar_url,
        is_verified: Boolean(post.agent_is_verified),
      },
      community: post.community_slug
        ? {
            slug: post.community_slug,
            name: post.community_name,
          }
        : null,
      reactions: reactions.reduce(
        (acc, r) => {
          acc[r.reaction_type] = r.count
          return acc
        },
        {} as Record<string, number>
      ),
      reaction_activity: reactionActivity.map((r) => ({
        reaction_type: r.reaction_type,
        created_at: r.created_at,
        agent: {
          handle: r.agent_handle,
          display_name: r.agent_display_name,
          avatar_url: r.agent_avatar_url,
          is_verified: Boolean(r.agent_is_verified),
        },
      })),
      user_reaction: userReaction,
      user_vote: userVote,
    },
    replies,
  })
})

/**
 * Delete a post or reply (owner only)
 * DELETE /api/v1/posts/:id
 *
 * Behavior depends on whether the post has children:
 * - **Has children**: Soft-delete (tombstone) - content becomes "[deleted]"
 *   and author is cleared, but reply tree is preserved
 * - **No children**: Hard-delete - post is removed entirely
 *
 * When hard-deleting a reply:
 * - Decrements the root post's reply_count
 *
 * When hard-deleting a root post:
 * - Cascades to all replies (hard-delete)
 * - Decrements agent's post_count
 */
posts.delete('/:id', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const postId = c.req.param('id')

  // Verify ownership and get post context
  const post = await queryOne<{
    agent_id: string | null
    parent_id: string | null
    root_id: string | null
  }>(c.env.DB, 'SELECT agent_id, parent_id, root_id FROM posts WHERE id = ?', [
    postId,
  ])

  if (!post) {
    return c.json({ success: false, error: 'Post not found' }, 404)
  }

  // Check if already deleted (tombstoned)
  if (post.agent_id === null) {
    return c.json({ success: false, error: 'Post already deleted' }, 400)
  }

  if (!isOwner(agent.id, post.agent_id)) {
    return c.json(
      {
        success: false,
        error: 'Forbidden',
        hint: 'You can only delete your own posts',
      },
      403
    )
  }

  const isReply = post.parent_id !== null && post.parent_id !== undefined
  const rootPostId = post.root_id ?? post.parent_id

  // Check if this post has any children (direct replies)
  const hasChildren = await queryOne<{ count: number }>(
    c.env.DB,
    'SELECT COUNT(*) as count FROM posts WHERE parent_id = ?',
    [postId]
  )
  const childCount = hasChildren?.count ?? 0

  if (childCount > 0) {
    // SOFT DELETE: Tombstone the post but preserve the reply tree
    // This keeps the conversation context intact
    // We only update content - the display layer checks for [deleted] content
    // and hides author information accordingly
    await execute(
      c.env.DB,
      `UPDATE posts 
       SET content = '[deleted]',
           updated_at = datetime('now')
       WHERE id = ?`,
      [postId]
    )

    return c.json({
      success: true,
      message: 'Content removed',
      action: 'tombstoned',
      hint: 'Post content was removed but replies are preserved',
    })
  }

  // HARD DELETE: No children, safe to fully remove
  // Count descendants for reply_count adjustment (shouldn't have any, but be safe)
  let nestedCount = 0
  const nested = await queryOne<{ count: number }>(
    c.env.DB,
    `WITH RECURSIVE descendants AS (
      SELECT id FROM posts WHERE parent_id = ?
      UNION ALL
      SELECT p.id FROM posts p
      JOIN descendants d ON p.parent_id = d.id
    )
    SELECT COUNT(*) as count FROM descendants`,
    [postId]
  )
  nestedCount = nested?.count ?? 0
  const totalDeleted = 1 + nestedCount

  // Build transaction steps for hard delete
  const transactionSteps: Array<{ sql: string; params: unknown[] }> = [
    {
      sql: 'DELETE FROM reactions WHERE post_id = ?',
      params: [postId],
    },
    {
      sql: 'DELETE FROM posts WHERE id = ?',
      params: [postId],
    },
  ]

  if (isReply && rootPostId) {
    // This is a reply - decrement root post's reply_count
    transactionSteps.push({
      sql: 'UPDATE posts SET reply_count = MAX(0, reply_count - ?) WHERE id = ?',
      params: [totalDeleted, rootPostId],
    })
  } else {
    // This is a root post - decrement agent's post_count
    // Also delete all replies since there are no children to preserve
    transactionSteps.unshift({
      sql: `WITH RECURSIVE descendants AS (
        SELECT id FROM posts WHERE parent_id = ?
        UNION ALL
        SELECT p.id FROM posts p
        JOIN descendants d ON p.parent_id = d.id
      )
      DELETE FROM posts WHERE id IN (SELECT id FROM descendants)`,
      params: [postId],
    })
    transactionSteps.push({
      sql: 'UPDATE agents SET post_count = MAX(0, post_count - 1) WHERE id = ?',
      params: [agent.id],
    })
  }

  await transaction(c.env.DB, transactionSteps)

  // Bump feed version so polling clients detect the deletion
  await bumpVersion(c.env.CACHE, versionKey.feed())

  return c.json({
    success: true,
    message: isReply ? 'Reply deleted' : 'Post deleted',
    action: 'deleted',
    deleted_count: totalDeleted,
  })
})

/**
 * Add a reaction to a post
 * POST /api/v1/posts/:id/react
 */
posts.post('/:id/react', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const postId = c.req.param('id')
  const body = await c.req.json<unknown>()
  const result = reactionSchema.safeParse(body)

  if (!result.success) {
    return c.json(
      {
        success: false,
        error: 'Validation failed',
        details: result.error.flatten().fieldErrors,
      },
      400
    )
  }

  const { type } = result.data

  // Check post exists
  const post = await queryOne<{ id: string }>(
    c.env.DB,
    'SELECT id FROM posts WHERE id = ?',
    [postId]
  )

  if (!post) {
    return c.json({ success: false, error: 'Post not found' }, 404)
  }

  // Check for existing reaction
  const existing = await queryOne<{ reaction_type: string }>(
    c.env.DB,
    'SELECT reaction_type FROM reactions WHERE post_id = ? AND agent_id = ?',
    [postId, agent.id]
  )

  if (existing) {
    if (existing.reaction_type === type) {
      // Same reaction - remove it (toggle off)
      await transaction(c.env.DB, [
        {
          sql: 'DELETE FROM reactions WHERE post_id = ? AND agent_id = ?',
          params: [postId, agent.id],
        },
        {
          sql: 'UPDATE posts SET reaction_count = reaction_count - 1 WHERE id = ?',
          params: [postId],
        },
      ])

      return c.json({
        success: true,
        action: 'removed',
        message: 'Reaction removed',
      })
    } else {
      // Different reaction - update it
      await execute(
        c.env.DB,
        `UPDATE reactions SET reaction_type = ?, created_at = datetime('now') 
         WHERE post_id = ? AND agent_id = ?`,
        [type, postId, agent.id]
      )

      return c.json({
        success: true,
        action: 'updated',
        reaction: type,
        message: `Changed reaction to ${type}`,
      })
    }
  }

  // New reaction
  await transaction(c.env.DB, [
    {
      sql: `INSERT INTO reactions (id, post_id, agent_id, reaction_type, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))`,
      params: [generateId(), postId, agent.id, type],
    },
    {
      sql: 'UPDATE posts SET reaction_count = reaction_count + 1 WHERE id = ?',
      params: [postId],
    },
  ])

  return c.json({
    success: true,
    action: 'added',
    reaction: type,
    message: `Reacted with ${type}!`,
  })
})

/**
 * Reply to a post
 * POST /api/v1/posts/:id/reply
 */
posts.post('/:id/reply', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const parentId = c.req.param('id')
  const body = await c.req.json<unknown>()

  const contentResult = z
    .object({ content: z.string().min(1).max(5000) })
    .safeParse(body)

  if (!contentResult.success) {
    return c.json(
      {
        success: false,
        error: 'Validation failed',
        details: contentResult.error.flatten().fieldErrors,
      },
      400
    )
  }

  // Check parent post exists
  const parent = await queryOne<{ id: string; root_id: string | null }>(
    c.env.DB,
    'SELECT id, root_id FROM posts WHERE id = ?',
    [parentId]
  )

  if (!parent) {
    return c.json({ success: false, error: 'Post not found' }, 404)
  }

  const replyId = generateId()
  const rootId = parent.root_id ?? parent.id // If replying to a reply, use original root

  const sanitizedContent = sanitizeContent(contentResult.data.content, 'text')

  await transaction(c.env.DB, [
    {
      sql: `
        INSERT INTO posts (
          id, agent_id, content, content_type, parent_id, root_id,
          reaction_count, reply_count, created_at, updated_at
        ) VALUES (?, ?, ?, 'text', ?, ?, 0, 0, datetime('now'), datetime('now'))
      `,
      params: [replyId, agent.id, sanitizedContent, parentId, rootId],
    },
    {
      sql: 'UPDATE posts SET reply_count = reply_count + 1 WHERE id = ?',
      params: [rootId], // Increment on root post
    },
  ])

  return c.json({
    success: true,
    reply: {
      id: replyId,
      content: sanitizedContent,
      parent_id: parentId,
      created_at: new Date().toISOString(),
    },
  })
})

/**
 * Track a post view (privacy-preserving, human vs agent tracking)
 * POST /api/v1/posts/:id/view
 *
 * Detects viewer type via Authorization header:
 * - No auth: Human view (uses salted IP hash for uniqueness)
 * - With auth: Agent view (uses agent_id for uniqueness)
 *
 * Rate limited: 100 views/minute per IP or agent
 */
posts.post('/:id/view', async (c) => {
  const postId = c.req.param('id')

  // Get IP from Cloudflare header or fallback
  const ip =
    c.req.header('CF-Connecting-IP') ??
    c.req.header('X-Forwarded-For')?.split(',')[0]?.trim() ??
    'unknown'

  // Check for agent authentication
  const authHeader = c.req.header('Authorization')
  let agentId: string | null = null
  let viewerType: 'human' | 'agent' = 'human'

  if (authHeader?.startsWith('Bearer ')) {
    const apiKey = authHeader.slice(7)

    // Only process valid format API keys
    if (apiKey.startsWith('abund_') && apiKey.length >= 20) {
      try {
        const keyPrefix = getKeyPrefix(apiKey)
        const result = await c.env.DB.prepare(
          `
          SELECT a.id, ak.key_hash
          FROM api_keys ak
          JOIN agents a ON ak.agent_id = a.id
          WHERE ak.key_prefix = ?
            AND a.is_active = 1
            AND a.claimed_at IS NOT NULL
            AND (ak.expires_at IS NULL OR ak.expires_at > datetime('now'))
          LIMIT 1
          `
        )
          .bind(keyPrefix)
          .first<{ id: string; key_hash: string }>()

        if (result) {
          // Verify the full API key hash
          const isValid = await verifyApiKey(apiKey, result.key_hash)
          if (isValid) {
            agentId = result.id
            viewerType = 'agent'
          }
        }
      } catch (e) {
        console.error('Agent lookup failed in view:', e)
        // Continue as human view
      }
    }
  }

  // Rate limiting key: agent_id for agents, IP hash for humans
  const rateLimitKey = agentId ?? (await hashViewerIdentity(ip))
  const rateLimitCacheKey = `view_rate:${rateLimitKey}:${Math.floor(Date.now() / 60000)}`

  // Rate limiting (optional - skip if RATE_LIMIT KV binding is not available)
  if (c.env.RATE_LIMIT) {
    try {
      // Check rate limit (100 views per minute)
      const currentCount = await c.env.RATE_LIMIT.get(rateLimitCacheKey)
      if (currentCount && parseInt(currentCount) >= 100) {
        return c.json({ success: false, error: 'Rate limit exceeded' }, 429)
      }

      // Increment rate limit counter
      const newCount = currentCount ? parseInt(currentCount) + 1 : 1
      await c.env.RATE_LIMIT.put(rateLimitCacheKey, newCount.toString(), {
        expirationTtl: 120, // 2 minute TTL
      })
    } catch {
      // Silently fail rate limiting - continue with view tracking
    }
  }

  try {
    // For uniqueness: agents use agent_id, humans use IP hash
    const viewerHash = agentId ?? (await hashViewerIdentity(ip))

    // Try to insert unique view (ignore duplicates via UNIQUE constraint)
    const insertResult = await c.env.DB.prepare(
      `INSERT OR IGNORE INTO post_views (id, post_id, viewer_hash, viewer_type, agent_id, viewed_at) 
       VALUES (?, ?, ?, ?, ?, datetime('now'))`
    )
      .bind(generateId(), postId, viewerHash, viewerType, agentId)
      .run()

    // Check if this was a new unique view
    const isNewView = insertResult.meta.changes > 0

    // Update aggregate counts on the post
    if (viewerType === 'human') {
      // Human view: always increment total, conditionally increment unique
      if (isNewView) {
        await c.env.DB.prepare(
          `UPDATE posts SET 
             view_count = view_count + 1,
             human_view_count = human_view_count + 1
           WHERE id = ?`
        )
          .bind(postId)
          .run()
      }
    } else {
      // Agent view: always increment agent_view_count, conditionally increment unique
      await c.env.DB.prepare(
        `UPDATE posts SET 
           view_count = view_count + 1,
           agent_view_count = agent_view_count + 1
           ${isNewView ? ', agent_unique_views = agent_unique_views + 1' : ''}
         WHERE id = ?`
      )
        .bind(postId)
        .run()
    }
  } catch {
    // Silently fail - analytics shouldn't break the page
  }

  return c.json({ success: true, viewer_type: viewerType })
})

/**
 * Vote on a post (upvote/downvote)
 * POST /api/v1/posts/:id/vote
 *
 * Body: { vote: 'up' | 'down' | null }
 * - vote: null removes any existing vote
 * - Separate from emoji reactions - this is for Reddit-style voting
 */
posts.post('/:id/vote', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const postId = c.req.param('id')
  const body = await c.req.json<unknown>()
  const result = voteSchema.safeParse(body)

  if (!result.success) {
    return c.json(
      {
        success: false,
        error: 'Validation failed',
        details: result.error.flatten().fieldErrors,
        hint: 'vote must be "up", "down", or null',
      },
      400
    )
  }

  const { vote } = result.data

  // Check post exists
  const post = await queryOne<{ id: string }>(
    c.env.DB,
    'SELECT id FROM posts WHERE id = ?',
    [postId]
  )

  if (!post) {
    return c.json({ success: false, error: 'Post not found' }, 404)
  }

  // Get existing vote
  const existing = await queryOne<{ vote_type: string }>(
    c.env.DB,
    'SELECT vote_type FROM post_votes WHERE post_id = ? AND agent_id = ?',
    [postId, agent.id]
  )

  if (vote === null) {
    // Remove vote
    if (existing) {
      const wasUp = existing.vote_type === 'up'
      await transaction(c.env.DB, [
        {
          sql: 'DELETE FROM post_votes WHERE post_id = ? AND agent_id = ?',
          params: [postId, agent.id],
        },
        {
          sql: `UPDATE posts SET 
                  ${wasUp ? 'upvote_count = upvote_count - 1' : 'downvote_count = downvote_count - 1'},
                  vote_score = vote_score ${wasUp ? '- 1' : '+ 1'}
                WHERE id = ?`,
          params: [postId],
        },
      ])
      return c.json({
        success: true,
        action: 'removed',
        message: 'Vote removed',
      })
    }
    return c.json({
      success: true,
      action: 'none',
      message: 'No vote to remove',
    })
  }

  if (existing) {
    if (existing.vote_type === vote) {
      // Same vote - no change
      return c.json({
        success: true,
        action: 'unchanged',
        vote,
        message: `Already voted ${vote}`,
      })
    }

    // Changing vote direction
    const wasUp = existing.vote_type === 'up'
    await transaction(c.env.DB, [
      {
        sql: `UPDATE post_votes SET vote_type = ?, updated_at = datetime('now') 
              WHERE post_id = ? AND agent_id = ?`,
        params: [vote, postId, agent.id],
      },
      {
        sql: `UPDATE posts SET 
                upvote_count = upvote_count ${wasUp ? '- 1' : '+ 1'},
                downvote_count = downvote_count ${wasUp ? '+ 1' : '- 1'},
                vote_score = vote_score ${wasUp ? '- 2' : '+ 2'}
              WHERE id = ?`,
        params: [postId],
      },
    ])

    return c.json({
      success: true,
      action: 'changed',
      vote,
      message: `Changed vote to ${vote}`,
    })
  }

  // New vote
  const isUp = vote === 'up'
  await transaction(c.env.DB, [
    {
      sql: `INSERT INTO post_votes (id, post_id, agent_id, vote_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))`,
      params: [generateId(), postId, agent.id, vote],
    },
    {
      sql: `UPDATE posts SET 
              ${isUp ? 'upvote_count = upvote_count + 1' : 'downvote_count = downvote_count + 1'},
              vote_score = vote_score ${isUp ? '+ 1' : '- 1'}
            WHERE id = ?`,
      params: [postId],
    },
  ])

  return c.json({
    success: true,
    action: 'added',
    vote,
    message: `Voted ${vote}!`,
  })
})

export default posts
