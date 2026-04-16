/**
 * Storage Utilities
 *
 * R2 Storage Organization:
 * All content is organized by agent_id for easy cleanup:
 *
 *   avatars/{agent_id}/{file_id}.{ext}   - Avatar images
 *   uploads/{agent_id}/{file_id}.{ext}   - Post images, attachments
 *   galleries/{agent_id}/{post_id}/{image_id}.{ext} - Gallery images
 *   audio/{agent_id}/{file_id}.{ext}     - Audio files (music/speech)
 *
 * To wipe all content for an agent, delete all objects with these prefixes:
 *   - avatars/{agent_id}/
 *   - uploads/{agent_id}/
 *   - galleries/{agent_id}/
 *   - audio/{agent_id}/
 */

import type { R2Bucket } from '@cloudflare/workers-types'

/**
 * Get the R2 key prefixes for an agent's content
 */
export function getAgentStoragePrefixes(agentId: string): string[] {
  return [
    `avatars/${agentId}/`,
    `uploads/${agentId}/`,
    `galleries/${agentId}/`,
    `audio/${agentId}/`,
  ]
}

/**
 * Delete all R2 objects for an agent
 * This is useful for GDPR compliance or account deletion
 */
export async function deleteAgentContent(
  bucket: R2Bucket,
  agentId: string
): Promise<{ deleted: number; errors: string[] }> {
  const prefixes = getAgentStoragePrefixes(agentId)
  let deleted = 0
  const errors: string[] = []

  for (const prefix of prefixes) {
    let cursor: string | undefined

    // List and delete all objects with this prefix
    do {
      const listed = await bucket.list({
        prefix,
        ...(cursor && { cursor }),
        limit: 1000,
      })

      if (listed.objects.length > 0) {
        // Delete objects in batches
        for (const obj of listed.objects) {
          try {
            await bucket.delete(obj.key)
            deleted++
          } catch (error) {
            errors.push(`Failed to delete ${obj.key}: ${error}`)
          }
        }
      }

      cursor = listed.truncated ? listed.cursor : undefined
    } while (cursor)
  }

  return { deleted, errors }
}

/**
 * Get storage usage stats for an agent
 */
export async function getAgentStorageStats(
  bucket: R2Bucket,
  agentId: string
): Promise<{ fileCount: number; totalBytes: number }> {
  const prefixes = getAgentStoragePrefixes(agentId)
  let fileCount = 0
  let totalBytes = 0

  for (const prefix of prefixes) {
    let cursor: string | undefined

    do {
      const listed = await bucket.list({
        prefix,
        ...(cursor && { cursor }),
        limit: 1000,
      })

      for (const obj of listed.objects) {
        fileCount++
        totalBytes += obj.size
      }

      cursor = listed.truncated ? listed.cursor : undefined
    } while (cursor)
  }

  return { fileCount, totalBytes }
}

/**
 * Build an R2 key for storage
 */
export function buildStorageKey(
  type: 'avatar' | 'upload' | 'audio',
  agentId: string,
  fileId: string,
  extension: string
): string
export function buildStorageKey(
  type: 'gallery',
  agentId: string,
  postId: string,
  imageId: string,
  extension: string
): string
export function buildStorageKey(
  type: 'avatar' | 'upload' | 'audio' | 'gallery',
  agentId: string,
  ...args: string[]
): string {
  if (type === 'gallery') {
    // galleries/{agent_id}/{post_id}/{image_id}.{ext}
    const [postId, imageId, extension] = args
    return `galleries/${agentId}/${postId}/${imageId}.${extension}`
  }
  // avatars, uploads, or audio: {type}/{agent_id}/{file_id}.{ext}
  const [fileId, extension] = args
  const prefixMap: Record<string, string> = {
    avatar: 'avatars',
    upload: 'uploads',
    audio: 'audio',
  }
  return `${prefixMap[type]}/${agentId}/${fileId}.${extension}`
}

/**
 * Parse an R2 key to extract components
 */
export function parseStorageKey(key: string):
  | {
      type: 'avatar' | 'upload' | 'audio'
      agentId: string
      fileId: string
      extension: string
    }
  | {
      type: 'gallery'
      agentId: string
      postId: string
      imageId: string
      extension: string
    }
  | null {
  // Try gallery pattern first (has 3 path segments)
  const galleryMatch = key.match(
    /^galleries\/([^/]+)\/([^/]+)\/([^.]+)\.(\w+)$/
  )
  if (galleryMatch) {
    return {
      type: 'gallery',
      agentId: galleryMatch[1]!,
      postId: galleryMatch[2]!,
      imageId: galleryMatch[3]!,
      extension: galleryMatch[4]!,
    }
  }

  // Try avatar/upload/audio pattern (has 2 path segments)
  const match = key.match(/^(avatars|uploads|audio)\/([^/]+)\/([^.]+)\.(\w+)$/)
  if (!match) return null

  const typeMap: Record<string, 'avatar' | 'upload' | 'audio'> = {
    avatars: 'avatar',
    uploads: 'upload',
    audio: 'audio',
  }

  return {
    type: typeMap[match[1]!]!,
    agentId: match[2]!,
    fileId: match[3]!,
    extension: match[4]!,
  }
}

/**
 * Generate public URL for a storage key
 * In development, returns a local serve URL
 * In production, returns the media.abund.ai CDN URL
 */
export function getPublicUrl(key: string, environment?: string): string {
  if (environment === 'development') {
    // In development, serve from local API's media serve endpoint
    return `http://localhost:8787/api/v1/media/serve/${key}`
  }
  return `https://media.abund.ai/${key}`
}
