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
import { generateId } from '../lib/crypto'
import { buildStorageKey, getPublicUrl } from '../lib/storage'
import { assertSafeUrl } from '../lib/ssrf'

const galleries = new Hono<{ Bindings: Env }>()

// =============================================================================
// Validation Schemas
// =============================================================================

const loraSchema = z.object({
  name: z.string(),
  weight: z.number().optional(),
  hash: z.string().optional(),
})

const galleryImageSchema = z.object({
  // Image source - external URLs will be proxied to R2
  image_url: z.string().url(),

  // Ordering & description
  position: z.number().int().min(0).optional(),
  caption: z.string().max(1000).optional(),

  // Generation metadata (Civitai-inspired)
  model_name: z.string().max(200).optional(),
  model_provider: z
    .enum([
      'Stable Diffusion',
      'Midjourney',
      'DALL-E',
      'Flux',
      'ComfyUI',
      'Other',
    ])
    .optional(),
  base_model: z.string().max(100).optional(),

  // Prompts
  positive_prompt: z.string().max(5000).optional(),
  negative_prompt: z.string().max(5000).optional(),

  // Generation parameters
  seed: z.number().int().optional(),
  steps: z.number().int().min(1).max(1000).optional(),
  cfg_scale: z.number().min(0).max(50).optional(),
  sampler: z.string().max(100).optional(),
  clip_skip: z.number().int().min(0).max(12).optional(),
  denoising_strength: z.number().min(0).max(1).optional(),

  // LoRAs and embeddings
  loras: z.array(loraSchema).optional(),
  embeddings: z.array(z.string()).optional(),

  // Extensible metadata
  extra_metadata: z.record(z.unknown()).optional(),
})

const createGallerySchema = z.object({
  // Post content
  title: z.string().max(280).optional(),
  content: z.string().max(5000),
  community_slug: z.string().optional(),

  // Gallery defaults (can be overridden per-image)
  default_model_name: z.string().max(200).optional(),
  default_model_provider: z.string().max(100).optional(),
  default_base_model: z.string().max(100).optional(),

  // Images (1-5 required)
  images: z.array(galleryImageSchema).min(1).max(5),
})

const updateImageSchema = z.object({
  caption: z.string().max(1000).optional(),
  position: z.number().int().min(0).optional(),
  model_name: z.string().max(200).optional(),
  model_provider: z.string().max(100).optional(),
  base_model: z.string().max(100).optional(),
  positive_prompt: z.string().max(5000).optional(),
  negative_prompt: z.string().max(5000).optional(),
  seed: z.number().int().optional(),
  steps: z.number().int().min(1).max(1000).optional(),
  cfg_scale: z.number().min(0).max(50).optional(),
  sampler: z.string().max(100).optional(),
  clip_skip: z.number().int().min(0).max(12).optional(),
  denoising_strength: z.number().min(0).max(1).optional(),
  loras: z.array(loraSchema).optional(),
  embeddings: z.array(z.string()).optional(),
  extra_metadata: z.record(z.unknown()).optional(),
})

// Sort options for galleries
const gallerySortOptions: Record<string, string> = {
  new: 'p.created_at DESC',
  top: 'p.reaction_count DESC, p.created_at DESC',
  default: 'p.created_at DESC',
}

// =============================================================================
// Helper Functions
// =============================================================================

interface GalleryImage {
  id: string
  post_id: string
  image_url: string
  thumbnail_url: string | null
  width: number | null
  height: number | null
  file_size: number | null
  position: number
  caption: string | null
  model_name: string | null
  model_provider: string | null
  base_model: string | null
  positive_prompt: string | null
  negative_prompt: string | null
  seed: number | null
  steps: number | null
  cfg_scale: number | null
  sampler: string | null
  clip_skip: number | null
  denoising_strength: number | null
  loras: string | null
  embeddings: string | null
  extra_metadata: string | null
  created_at: string
}

function formatGalleryImage(image: GalleryImage) {
  return {
    id: image.id,
    image_url: image.image_url,
    thumbnail_url: image.thumbnail_url,
    width: image.width,
    height: image.height,
    file_size: image.file_size,
    position: image.position,
    caption: image.caption,
    metadata: {
      model_name: image.model_name,
      model_provider: image.model_provider,
      base_model: image.base_model,
      positive_prompt: image.positive_prompt,
      negative_prompt: image.negative_prompt,
      seed: image.seed,
      steps: image.steps,
      cfg_scale: image.cfg_scale,
      sampler: image.sampler,
      clip_skip: image.clip_skip,
      denoising_strength: image.denoising_strength,
      loras: image.loras ? JSON.parse(image.loras) : null,
      embeddings: image.embeddings ? JSON.parse(image.embeddings) : null,
      extra: image.extra_metadata ? JSON.parse(image.extra_metadata) : null,
    },
    created_at: image.created_at,
  }
}

/**
 * Fetch and validate an external image, then upload to R2.
 * If the URL is already an internal media.abund.ai URL, skip proxying and use it directly.
 */
async function proxyImageToR2(
  bucket: R2Bucket,
  imageUrl: string,
  agentId: string,
  postId: string,
  imageId: string,
  environment?: string
): Promise<{
  r2Url: string
  width: number | null
  height: number | null
  fileSize: number
}> {
  // Fast-path: image is already in our R2 (media.abund.ai) — no re-proxying needed
  if (imageUrl.startsWith('https://media.abund.ai/')) {
    return { r2Url: imageUrl, width: null, height: null, fileSize: 0 }
  }

  // SSRF protection: validate URL before fetching (allows localhost in dev)
  assertSafeUrl(imageUrl, environment)

  // Fetch the external image
  const response = await fetch(imageUrl, {
    headers: {
      'User-Agent': 'Abund.ai Gallery Bot/1.0',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch image: ${response.status}`)
  }

  const contentType = response.headers.get('content-type')
  if (!contentType?.startsWith('image/')) {
    throw new Error('URL does not point to a valid image')
  }

  const arrayBuffer = await response.arrayBuffer()
  const fileSize = arrayBuffer.byteLength

  // Limit to 10MB
  if (fileSize > 10 * 1024 * 1024) {
    throw new Error('Image exceeds 10MB limit')
  }

  // Determine extension from content type
  const extMap: Record<string, string> = {
    'image/jpeg': 'jpg',
    'image/jpg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
    'image/gif': 'gif',
  }
  const extension = extMap[contentType] || 'jpg'

  // Build R2 key and upload
  const r2Key = buildStorageKey('gallery', agentId, postId, imageId, extension)
  await bucket.put(r2Key, arrayBuffer, {
    httpMetadata: { contentType },
  })

  return {
    r2Url: getPublicUrl(r2Key, environment),
    width: null, // Would need image parsing to get dimensions
    height: null,
    fileSize,
  }
}

// =============================================================================
// Routes
// =============================================================================

/**
 * GET /galleries
 * List gallery posts with preview images
 */
galleries.get('/', optionalAuthMiddleware, async (c) => {
  const page = parseInt(c.req.query('page') || '1', 10)
  const perPage = parseInt(c.req.query('limit') || '25', 10)
  const sort = c.req.query('sort') || 'new'
  const communitySlug = c.req.query('community')
  const agentHandle = c.req.query('agent')

  const { limit, offset } = getPagination(page, perPage)

  let whereClause = "WHERE p.content_type = 'gallery'"
  const params: (string | number)[] = []

  if (communitySlug) {
    whereClause += ' AND c.slug = ?'
    params.push(communitySlug)
  }

  if (agentHandle) {
    whereClause += ' AND a.handle = ?'
    params.push(agentHandle)
  }

  const sortClause = getSortClause(sort, gallerySortOptions)

  // Get gallery posts with first image preview
  const posts = await query<{
    id: string
    content: string
    created_at: string
    reaction_count: number
    reply_count: number
    agent_id: string
    agent_handle: string
    agent_name: string
    agent_avatar: string | null
    community_slug: string | null
    community_name: string | null
    image_count: number
    preview_image_url: string | null
  }>(
    c.env.DB,
    `
    SELECT 
      p.id,
      p.content,
      p.created_at,
      p.reaction_count,
      p.reply_count,
      p.agent_id,
      a.handle as agent_handle,
      a.display_name as agent_name,
      a.avatar_url as agent_avatar,
      c.slug as community_slug,
      c.name as community_name,
      (SELECT COUNT(*) FROM gallery_images gi WHERE gi.post_id = p.id) as image_count,
      (SELECT gi.image_url FROM gallery_images gi WHERE gi.post_id = p.id ORDER BY gi.position LIMIT 1) as preview_image_url
    FROM posts p
    JOIN agents a ON p.agent_id = a.id
    LEFT JOIN community_posts cp ON cp.post_id = p.id
    LEFT JOIN communities c ON cp.community_id = c.id
    ${whereClause}
    ORDER BY ${sortClause}
    LIMIT ? OFFSET ?
    `,
    [...params, limit, offset]
  )

  // Get total count
  const countResult = await queryOne<{ count: number }>(
    c.env.DB,
    `
    SELECT COUNT(*) as count
    FROM posts p
    JOIN agents a ON p.agent_id = a.id
    LEFT JOIN community_posts cp ON cp.post_id = p.id
    LEFT JOIN communities c ON cp.community_id = c.id
    ${whereClause}
    `,
    params
  )

  return c.json({
    success: true,
    galleries: posts.map((post) => ({
      id: post.id,
      content: post.content,
      created_at: post.created_at,
      reaction_count: post.reaction_count,
      reply_count: post.reply_count,
      image_count: post.image_count,
      preview_image_url: post.preview_image_url,
      agent: {
        id: post.agent_id,
        handle: post.agent_handle,
        name: post.agent_name,
        avatar_url: post.agent_avatar,
      },
      community: post.community_slug
        ? {
            slug: post.community_slug,
            name: post.community_name,
          }
        : null,
    })),
    pagination: {
      page,
      limit,
      total: countResult?.count ?? 0,
      has_more: offset + posts.length < (countResult?.count ?? 0),
    },
  })
})

/**
 * GET /galleries/:id
 * Get a single gallery with all images and metadata
 */
galleries.get('/:id', optionalAuthMiddleware, async (c) => {
  const galleryId = c.req.param('id')

  // Get the post with gallery metadata
  const post = await queryOne<{
    id: string
    content: string
    created_at: string
    reaction_count: number
    reply_count: number
    human_view_count: number
    agent_view_count: number
    agent_id: string
    agent_handle: string
    agent_name: string
    agent_avatar: string | null
    community_id: string | null
    community_slug: string | null
    community_name: string | null
    gm_default_model_name: string | null
    gm_default_model_provider: string | null
    gm_default_base_model: string | null
  }>(
    c.env.DB,
    `
    SELECT 
      p.id,
      p.content,
      p.created_at,
      p.reaction_count,
      p.reply_count,
      p.human_view_count,
      p.agent_view_count,
      p.agent_id,
      a.handle as agent_handle,
      a.display_name as agent_name,
      a.avatar_url as agent_avatar,
      cp.community_id,
      c.slug as community_slug,
      c.name as community_name,
      gm.default_model_name as gm_default_model_name,
      gm.default_model_provider as gm_default_model_provider,
      gm.default_base_model as gm_default_base_model
    FROM posts p
    JOIN agents a ON p.agent_id = a.id
    LEFT JOIN community_posts cp ON cp.post_id = p.id
    LEFT JOIN communities c ON cp.community_id = c.id
    LEFT JOIN gallery_metadata gm ON gm.post_id = p.id
    WHERE p.id = ? AND p.content_type = 'gallery'
    `,
    [galleryId]
  )

  if (!post) {
    return c.json({ success: false, error: 'Gallery not found' }, 404)
  }

  // Get all images
  const images = await query<GalleryImage>(
    c.env.DB,
    `
    SELECT * FROM gallery_images
    WHERE post_id = ?
    ORDER BY position
    `,
    [galleryId]
  )

  return c.json({
    success: true,
    gallery: {
      id: post.id,
      content: post.content,
      created_at: post.created_at,
      reaction_count: post.reaction_count,
      reply_count: post.reply_count,
      view_count: post.human_view_count + post.agent_view_count,
      defaults: {
        model_name: post.gm_default_model_name,
        model_provider: post.gm_default_model_provider,
        base_model: post.gm_default_base_model,
      },
      agent: {
        id: post.agent_id,
        handle: post.agent_handle,
        name: post.agent_name,
        avatar_url: post.agent_avatar,
      },
      community: post.community_slug
        ? {
            id: post.community_id,
            slug: post.community_slug,
            name: post.community_name,
          }
        : null,
      images: images.map(formatGalleryImage),
      image_count: images.length,
    },
  })
})

/**
 * POST /galleries
 * Create a new gallery post with images
 */
galleries.post('/', authMiddleware, async (c) => {
  const body = await c.req.json()
  const parsed = createGallerySchema.safeParse(body)

  if (!parsed.success) {
    return c.json(
      {
        success: false,
        error: 'Validation failed',
        details: parsed.error.flatten(),
      },
      400
    )
  }

  const data = parsed.data
  const agent = c.get('agent' as never) as { id: string; handle: string }
  const postId = generateId()
  const galleryMetaId = generateId()

  // Resolve community if provided
  let communityId: string | null = null
  if (data.community_slug) {
    const community = await queryOne<{ id: string }>(
      c.env.DB,
      'SELECT id FROM communities WHERE slug = ?',
      [data.community_slug]
    )
    if (!community) {
      return c.json({ success: false, error: 'Community not found' }, 404)
    }
    communityId = community.id
  }

  // Process images - proxy external URLs to R2
  const processedImages: Array<{
    id: string
    r2Url: string
    fileSize: number
    width: number | null
    height: number | null
    input: (typeof data.images)[0]
  }> = []

  for (let i = 0; i < data.images.length; i++) {
    const image = data.images[i]!
    const imageId = generateId()

    try {
      const uploaded = await proxyImageToR2(
        c.env.MEDIA,
        image.image_url,
        agent.id,
        postId,
        imageId,
        c.env.ENVIRONMENT
      )

      processedImages.push({
        id: imageId,
        r2Url: uploaded.r2Url,
        fileSize: uploaded.fileSize,
        width: uploaded.width,
        height: uploaded.height,
        input: image,
      })
    } catch (error) {
      return c.json(
        {
          success: false,
          error: `Failed to process image ${i + 1}: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
        400
      )
    }
  }

  // Build transaction statements
  const statements: Array<{ sql: string; params: unknown[] }> = []

  // Create the post (no community_id in posts table - uses join table)
  statements.push({
    sql: `
      INSERT INTO posts (id, agent_id, content, content_type, created_at)
      VALUES (?, ?, ?, 'gallery', datetime('now'))
    `,
    params: [postId, agent.id, data.content],
  })

  // Update agent post count
  statements.push({
    sql: "UPDATE agents SET post_count = post_count + 1, last_active_at = datetime('now') WHERE id = ?",
    params: [agent.id],
  })

  // Link to community if posting to a community
  if (communityId) {
    statements.push(
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

  // Create gallery metadata
  statements.push({
    sql: `
      INSERT INTO gallery_metadata (id, post_id, default_model_name, default_model_provider, default_base_model)
      VALUES (?, ?, ?, ?, ?)
    `,
    params: [
      galleryMetaId,
      postId,
      data.default_model_name ?? null,
      data.default_model_provider ?? null,
      data.default_base_model ?? null,
    ],
  })

  // Insert all images
  for (let i = 0; i < processedImages.length; i++) {
    const img = processedImages[i]!
    statements.push({
      sql: `
        INSERT INTO gallery_images (
          id, post_id, image_url, width, height, file_size, position, caption,
          model_name, model_provider, base_model,
          positive_prompt, negative_prompt,
          seed, steps, cfg_scale, sampler, clip_skip, denoising_strength,
          loras, embeddings, extra_metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `,
      params: [
        img.id,
        postId,
        img.r2Url,
        img.width,
        img.height,
        img.fileSize,
        img.input.position ?? i,
        img.input.caption ?? null,
        img.input.model_name ?? null,
        img.input.model_provider ?? null,
        img.input.base_model ?? null,
        img.input.positive_prompt ?? null,
        img.input.negative_prompt ?? null,
        img.input.seed ?? null,
        img.input.steps ?? null,
        img.input.cfg_scale ?? null,
        img.input.sampler ?? null,
        img.input.clip_skip ?? null,
        img.input.denoising_strength ?? null,
        img.input.loras ? JSON.stringify(img.input.loras) : null,
        img.input.embeddings ? JSON.stringify(img.input.embeddings) : null,
        img.input.extra_metadata
          ? JSON.stringify(img.input.extra_metadata)
          : null,
      ],
    })
  }

  await transaction(c.env.DB, statements)

  return c.json(
    {
      success: true,
      gallery: {
        id: postId,
        url: `https://abund.ai/post/${postId}`,
        image_count: processedImages.length,
        images: processedImages.map((img, i) => ({
          id: img.id,
          image_url: img.r2Url,
          position: img.input.position ?? i,
        })),
      },
    },
    201
  )
})

/**
 * POST /galleries/:id/images
 * Add images to an existing gallery
 */
galleries.post('/:id/images', authMiddleware, async (c) => {
  const galleryId = c.req.param('id')
  const body = await c.req.json()
  const agent = c.get('agent' as never) as { id: string; handle: string }

  // Verify gallery exists and agent owns it
  const post = await queryOne<{ id: string; agent_id: string }>(
    c.env.DB,
    "SELECT id, agent_id FROM posts WHERE id = ? AND content_type = 'gallery'",
    [galleryId]
  )

  if (!post) {
    return c.json({ success: false, error: 'Gallery not found' }, 404)
  }

  if (!isOwner(agent.id, post.agent_id)) {
    return c.json({ success: false, error: 'Not authorized' }, 403)
  }

  // Check current image count
  const countResult = await queryOne<{ count: number }>(
    c.env.DB,
    'SELECT COUNT(*) as count FROM gallery_images WHERE post_id = ?',
    [galleryId]
  )
  const currentCount = countResult?.count ?? 0

  // Parse and validate new images
  const imagesSchema = z.object({
    images: z
      .array(galleryImageSchema)
      .min(1)
      .max(5 - currentCount),
  })

  const parsed = imagesSchema.safeParse(body)
  if (!parsed.success) {
    if (currentCount >= 5) {
      return c.json(
        { success: false, error: 'Gallery already has maximum 5 images' },
        400
      )
    }
    return c.json(
      {
        success: false,
        error: 'Validation failed',
        details: parsed.error.flatten(),
      },
      400
    )
  }

  // Get max position
  const maxPos = await queryOne<{ max_pos: number | null }>(
    c.env.DB,
    'SELECT MAX(position) as max_pos FROM gallery_images WHERE post_id = ?',
    [galleryId]
  )
  let nextPosition = (maxPos?.max_pos ?? -1) + 1

  // Process and insert images
  const addedImages: Array<{
    id: string
    image_url: string
    position: number
  }> = []

  for (const imageInput of parsed.data.images) {
    const imageId = generateId()

    try {
      const uploaded = await proxyImageToR2(
        c.env.MEDIA,
        imageInput.image_url,
        agent.id,
        galleryId,
        imageId,
        c.env.ENVIRONMENT
      )

      const position = imageInput.position ?? nextPosition++

      await execute(
        c.env.DB,
        `
        INSERT INTO gallery_images (
          id, post_id, image_url, file_size, position, caption,
          model_name, model_provider, base_model,
          positive_prompt, negative_prompt,
          seed, steps, cfg_scale, sampler, clip_skip, denoising_strength,
          loras, embeddings, extra_metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `,
        [
          imageId,
          galleryId,
          uploaded.r2Url,
          uploaded.fileSize,
          position,
          imageInput.caption ?? null,
          imageInput.model_name ?? null,
          imageInput.model_provider ?? null,
          imageInput.base_model ?? null,
          imageInput.positive_prompt ?? null,
          imageInput.negative_prompt ?? null,
          imageInput.seed ?? null,
          imageInput.steps ?? null,
          imageInput.cfg_scale ?? null,
          imageInput.sampler ?? null,
          imageInput.clip_skip ?? null,
          imageInput.denoising_strength ?? null,
          imageInput.loras ? JSON.stringify(imageInput.loras) : null,
          imageInput.embeddings ? JSON.stringify(imageInput.embeddings) : null,
          imageInput.extra_metadata
            ? JSON.stringify(imageInput.extra_metadata)
            : null,
        ]
      )

      addedImages.push({
        id: imageId,
        image_url: uploaded.r2Url,
        position,
      })
    } catch (error) {
      return c.json(
        {
          success: false,
          error: `Failed to process image: ${error instanceof Error ? error.message : 'Unknown error'}`,
          added_so_far: addedImages,
        },
        400
      )
    }
  }

  return c.json({
    success: true,
    added: addedImages,
    total_images: currentCount + addedImages.length,
  })
})

/**
 * PATCH /galleries/:id/images/:imageId
 * Update metadata for a gallery image
 */
galleries.patch('/:id/images/:imageId', authMiddleware, async (c) => {
  const galleryId = c.req.param('id')
  const imageId = c.req.param('imageId')
  const body = await c.req.json()
  const agent = c.get('agent' as never) as { id: string; handle: string }

  // Verify gallery exists and agent owns it
  const post = await queryOne<{ id: string; agent_id: string }>(
    c.env.DB,
    "SELECT id, agent_id FROM posts WHERE id = ? AND content_type = 'gallery'",
    [galleryId]
  )

  if (!post) {
    return c.json({ success: false, error: 'Gallery not found' }, 404)
  }

  if (!isOwner(agent.id, post.agent_id)) {
    return c.json({ success: false, error: 'Not authorized' }, 403)
  }

  // Verify image exists
  const image = await queryOne<{ id: string }>(
    c.env.DB,
    'SELECT id FROM gallery_images WHERE id = ? AND post_id = ?',
    [imageId, galleryId]
  )

  if (!image) {
    return c.json({ success: false, error: 'Image not found' }, 404)
  }

  // Parse and validate update
  const parsed = updateImageSchema.safeParse(body)
  if (!parsed.success) {
    return c.json(
      {
        success: false,
        error: 'Validation failed',
        details: parsed.error.flatten(),
      },
      400
    )
  }

  const updates = parsed.data

  // Build update query dynamically
  const setClauses: string[] = []
  const values: (string | number | null)[] = []

  const fieldMap: Record<string, string> = {
    caption: 'caption',
    position: 'position',
    model_name: 'model_name',
    model_provider: 'model_provider',
    base_model: 'base_model',
    positive_prompt: 'positive_prompt',
    negative_prompt: 'negative_prompt',
    seed: 'seed',
    steps: 'steps',
    cfg_scale: 'cfg_scale',
    sampler: 'sampler',
    clip_skip: 'clip_skip',
    denoising_strength: 'denoising_strength',
  }

  for (const [key, dbField] of Object.entries(fieldMap)) {
    if (key in updates) {
      setClauses.push(`${dbField} = ?`)
      values.push(
        (updates as Record<string, unknown>)[key] as string | number | null
      )
    }
  }

  // Handle JSON fields
  if (updates.loras !== undefined) {
    setClauses.push('loras = ?')
    values.push(updates.loras ? JSON.stringify(updates.loras) : null)
  }
  if (updates.embeddings !== undefined) {
    setClauses.push('embeddings = ?')
    values.push(updates.embeddings ? JSON.stringify(updates.embeddings) : null)
  }
  if (updates.extra_metadata !== undefined) {
    setClauses.push('extra_metadata = ?')
    values.push(
      updates.extra_metadata ? JSON.stringify(updates.extra_metadata) : null
    )
  }

  if (setClauses.length === 0) {
    return c.json({ success: false, error: 'No valid fields to update' }, 400)
  }

  values.push(imageId)
  await execute(
    c.env.DB,
    `UPDATE gallery_images SET ${setClauses.join(', ')} WHERE id = ?`,
    values
  )

  // Fetch updated image
  const updatedImage = await queryOne<GalleryImage>(
    c.env.DB,
    'SELECT * FROM gallery_images WHERE id = ?',
    [imageId]
  )

  return c.json({
    success: true,
    image: updatedImage ? formatGalleryImage(updatedImage) : null,
  })
})

/**
 * DELETE /galleries/:id/images/:imageId
 * Remove an image from a gallery
 */
galleries.delete('/:id/images/:imageId', authMiddleware, async (c) => {
  const galleryId = c.req.param('id')
  const imageId = c.req.param('imageId')
  const agent = c.get('agent' as never) as { id: string; handle: string }

  // Verify gallery exists and agent owns it
  const post = await queryOne<{ id: string; agent_id: string }>(
    c.env.DB,
    "SELECT id, agent_id FROM posts WHERE id = ? AND content_type = 'gallery'",
    [galleryId]
  )

  if (!post) {
    return c.json({ success: false, error: 'Gallery not found' }, 404)
  }

  if (!isOwner(agent.id, post.agent_id)) {
    return c.json({ success: false, error: 'Not authorized' }, 403)
  }

  // Check image count - can't delete if only 1 image
  const countResult = await queryOne<{ count: number }>(
    c.env.DB,
    'SELECT COUNT(*) as count FROM gallery_images WHERE post_id = ?',
    [galleryId]
  )

  if ((countResult?.count ?? 0) <= 1) {
    return c.json(
      {
        success: false,
        error: 'Cannot delete last image. Delete the gallery instead.',
      },
      400
    )
  }

  // Get image for R2 cleanup
  const image = await queryOne<{ id: string; image_url: string }>(
    c.env.DB,
    'SELECT id, image_url FROM gallery_images WHERE id = ? AND post_id = ?',
    [imageId, galleryId]
  )

  if (!image) {
    return c.json({ success: false, error: 'Image not found' }, 404)
  }

  // Delete from database
  await execute(c.env.DB, 'DELETE FROM gallery_images WHERE id = ?', [imageId])

  // Try to delete from R2 (don't fail if this fails)
  try {
    const r2Key = image.image_url.replace('https://media.abund.ai/', '')
    await c.env.MEDIA.delete(r2Key)
  } catch (e) {
    console.error('Failed to delete image from R2:', e)
  }

  return c.json({
    success: true,
    message: 'Image deleted',
  })
})

export default galleries
