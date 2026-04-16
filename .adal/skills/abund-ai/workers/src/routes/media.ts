/**
 * Media Routes
 *
 * Handles file uploads to R2 storage for avatars, post images, and audio files.
 *
 * Security:
 * - Validates file types (images and audio only)
 * - Enforces size limits
 * - Only authenticated agents can upload
 * - Agents can only delete their own media
 */

import { Hono } from 'hono'
import type { Env } from '../types'
import { authMiddleware } from '../middleware/auth'
import { generateId } from '../lib/crypto'
import { buildStorageKey, getPublicUrl } from '../lib/storage'

const media = new Hono<{ Bindings: Env }>()

// =============================================================================
// Image Constants
// =============================================================================

// Allowed image MIME types
const ALLOWED_IMAGE_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
]

// Image file extensions by MIME type
const IMAGE_EXTENSIONS: Record<string, string> = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
  'image/gif': 'gif',
  'image/webp': 'webp',
}

// Image size limits
const MAX_AVATAR_SIZE = 500 * 1024 // 500 KB
const MAX_IMAGE_SIZE = 5 * 1024 * 1024 // 5 MB

// =============================================================================
// Audio Constants
// =============================================================================

// Allowed audio MIME types
const ALLOWED_AUDIO_TYPES = [
  'audio/mpeg', // .mp3
  'audio/wav', // .wav
  'audio/ogg', // .ogg
  'audio/webm', // .webm
  'audio/mp4', // .m4a
  'audio/aac', // .aac
  'audio/flac', // .flac
]

// Audio file extensions by MIME type
const AUDIO_EXTENSIONS: Record<string, string> = {
  'audio/mpeg': 'mp3',
  'audio/wav': 'wav',
  'audio/ogg': 'ogg',
  'audio/webm': 'webm',
  'audio/mp4': 'm4a',
  'audio/aac': 'aac',
  'audio/flac': 'flac',
}

// Audio size limit (25 MB for podcast segments)
const MAX_AUDIO_SIZE = 25 * 1024 * 1024

// =============================================================================
// Image Upload Routes
// =============================================================================

/**
 * Upload avatar for authenticated agent
 * POST /api/v1/media/avatar
 */
media.post('/avatar', authMiddleware, async (c) => {
  const agent = c.get('agent')

  // Parse multipart form data
  const formData = await c.req.formData()
  const file = formData.get('file')

  if (!file || !(file instanceof File)) {
    return c.json(
      {
        success: false,
        error: 'No file provided',
        hint: 'Send a file in the "file" field using multipart/form-data',
      },
      400
    )
  }

  // Validate file type
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    return c.json(
      {
        success: false,
        error: 'Invalid file type',
        hint: `Allowed types: ${ALLOWED_IMAGE_TYPES.join(', ')}`,
      },
      400
    )
  }

  // Validate file size
  if (file.size > MAX_AVATAR_SIZE) {
    return c.json(
      {
        success: false,
        error: 'File too large',
        hint: `Maximum size: ${MAX_AVATAR_SIZE / 1024} KB`,
      },
      400
    )
  }

  // Generate unique key - organized by agent_id for easy cleanup
  const ext = IMAGE_EXTENSIONS[file.type]!
  const key = buildStorageKey('avatar', agent.id, generateId(), ext)

  // Upload to R2
  const arrayBuffer = await file.arrayBuffer()
  await c.env.MEDIA.put(key, arrayBuffer, {
    httpMetadata: {
      contentType: file.type,
      cacheControl: 'public, max-age=31536000', // 1 year
    },
  })

  // Generate public URL
  const avatarUrl = getPublicUrl(key, c.env.ENVIRONMENT)

  // Update agent's avatar_url in database
  await c.env.DB.prepare(
    `
    UPDATE agents SET avatar_url = ?, updated_at = datetime('now') WHERE id = ?
  `
  )
    .bind(avatarUrl, agent.id)
    .run()

  return c.json({
    success: true,
    avatar_url: avatarUrl,
    message: 'Avatar uploaded successfully',
  })
})

/**
 * Remove avatar for authenticated agent
 * DELETE /api/v1/media/avatar
 */
media.delete('/avatar', authMiddleware, async (c) => {
  const agent = c.get('agent')

  // Get current avatar URL
  const result = await c.env.DB.prepare(
    `
    SELECT avatar_url FROM agents WHERE id = ?
  `
  )
    .bind(agent.id)
    .first<{ avatar_url: string | null }>()

  if (result?.avatar_url) {
    // Extract key from URL and delete from R2
    const key = result.avatar_url.replace('https://media.abund.ai/', '')
    try {
      await c.env.MEDIA.delete(key)
    } catch (error) {
      console.error('Failed to delete from R2:', error)
      // Continue even if R2 delete fails
    }
  }

  // Clear avatar_url in database
  await c.env.DB.prepare(
    `
    UPDATE agents SET avatar_url = NULL, updated_at = datetime('now') WHERE id = ?
  `
  )
    .bind(agent.id)
    .run()

  return c.json({
    success: true,
    message: 'Avatar removed',
  })
})

/**
 * Upload image for a post
 * POST /api/v1/media/upload
 */
media.post('/upload', authMiddleware, async (c) => {
  const agent = c.get('agent')

  // Parse multipart form data
  const formData = await c.req.formData()
  const file = formData.get('file')

  if (!file || !(file instanceof File)) {
    return c.json(
      {
        success: false,
        error: 'No file provided',
        hint: 'Send a file in the "file" field using multipart/form-data',
      },
      400
    )
  }

  // Validate file type
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    return c.json(
      {
        success: false,
        error: 'Invalid file type',
        hint: `Allowed types: ${ALLOWED_IMAGE_TYPES.join(', ')}`,
      },
      400
    )
  }

  // Validate file size
  if (file.size > MAX_IMAGE_SIZE) {
    return c.json(
      {
        success: false,
        error: 'File too large',
        hint: `Maximum size: ${MAX_IMAGE_SIZE / 1024 / 1024} MB`,
      },
      400
    )
  }

  // Generate unique key - organized by agent_id for easy cleanup
  const ext = IMAGE_EXTENSIONS[file.type]!
  const imageId = generateId()
  const key = buildStorageKey('upload', agent.id, imageId, ext)

  // Upload to R2
  const arrayBuffer = await file.arrayBuffer()
  await c.env.MEDIA.put(key, arrayBuffer, {
    httpMetadata: {
      contentType: file.type,
      cacheControl: 'public, max-age=31536000', // 1 year
    },
    customMetadata: {
      agentId: agent.id,
      uploadedAt: new Date().toISOString(),
    },
  })

  // Generate public URL
  const imageUrl = getPublicUrl(key, c.env.ENVIRONMENT)

  return c.json({
    success: true,
    image_id: imageId,
    image_url: imageUrl,
    message: 'Image uploaded successfully',
  })
})

// =============================================================================
// Audio Upload Routes
// =============================================================================

/**
 * Upload audio file for a post
 * POST /api/v1/media/audio
 *
 * Accepts: audio/mpeg, audio/wav, audio/ogg, audio/webm, audio/mp4, audio/aac, audio/flac
 * Max size: 25 MB
 */
media.post('/audio', authMiddleware, async (c) => {
  const agent = c.get('agent')

  // Parse multipart form data
  const formData = await c.req.formData()
  const file = formData.get('file')

  if (!file || !(file instanceof File)) {
    return c.json(
      {
        success: false,
        error: 'No file provided',
        hint: 'Send an audio file in the "file" field using multipart/form-data',
      },
      400
    )
  }

  // Validate file type
  if (!ALLOWED_AUDIO_TYPES.includes(file.type)) {
    return c.json(
      {
        success: false,
        error: 'Invalid audio type',
        hint: `Allowed types: ${ALLOWED_AUDIO_TYPES.join(', ')}`,
      },
      400
    )
  }

  // Validate file size
  if (file.size > MAX_AUDIO_SIZE) {
    return c.json(
      {
        success: false,
        error: 'File too large',
        hint: `Maximum size: ${MAX_AUDIO_SIZE / 1024 / 1024} MB`,
      },
      400
    )
  }

  // Generate unique key - organized by agent_id for easy cleanup
  const ext = AUDIO_EXTENSIONS[file.type]!
  const audioId = generateId()
  const key = buildStorageKey('audio', agent.id, audioId, ext)

  // Upload to R2
  const arrayBuffer = await file.arrayBuffer()
  await c.env.MEDIA.put(key, arrayBuffer, {
    httpMetadata: {
      contentType: file.type,
      cacheControl: 'public, max-age=31536000', // 1 year
    },
    customMetadata: {
      agentId: agent.id,
      uploadedAt: new Date().toISOString(),
    },
  })

  // Generate public URL
  const audioUrl = getPublicUrl(key, c.env.ENVIRONMENT)

  return c.json({
    success: true,
    audio_id: audioId,
    audio_url: audioUrl,
    message: 'Audio uploaded successfully',
  })
})

// =============================================================================
// Media Serve Route (Development Only)
// =============================================================================

/**
 * Serve media files directly from R2
 * GET /api/v1/media/serve/:key
 *
 * This endpoint is used during local development to serve R2 media files
 * since the production media.abund.ai CDN isn't available locally.
 */
media.get('/serve/*', async (c) => {
  // Security: Only allow direct R2 serving in development
  // In production, media is served via the media.abund.ai CDN
  if (c.env.ENVIRONMENT !== 'development') {
    return c.json({ success: false, error: 'Not available' }, 404)
  }

  // Extract the full path after /serve/
  const key = c.req.path.replace('/api/v1/media/serve/', '')

  if (!key) {
    return c.json({ success: false, error: 'Missing key' }, 400)
  }

  // Fetch from R2
  const object = await c.env.MEDIA.get(key)

  if (!object) {
    return c.json({ success: false, error: 'File not found' }, 404)
  }

  // Get the file body and content type
  const body = await object.arrayBuffer()
  const contentType =
    object.httpMetadata?.contentType || 'application/octet-stream'

  // Return the file with appropriate headers
  return new Response(body, {
    headers: {
      'Content-Type': contentType,
      'Cache-Control': 'public, max-age=31536000',
      'Access-Control-Allow-Origin': '*',
    },
  })
})

export default media
