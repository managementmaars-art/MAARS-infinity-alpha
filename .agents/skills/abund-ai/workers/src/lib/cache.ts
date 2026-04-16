/**
 * Caching Layer
 *
 * KV-based caching for frequently accessed data to reduce D1 load.
 * Uses stale-while-revalidate pattern for optimal performance.
 */

interface CacheOptions {
  /** TTL in seconds */
  ttl: number
  /** If true, return stale data while refreshing in background */
  staleWhileRevalidate?: boolean
}

/** Generic KV interface for cache operations (avoids type conflicts) */
interface KVCache {
  get(key: string, type?: string): Promise<string | null>
  get<T = unknown>(key: string, type: 'json'): Promise<T | null>
  put(
    key: string,
    value: string,
    options?: { expirationTtl?: number }
  ): Promise<void>
  delete(key: string): Promise<void>
  list(options?: { prefix?: string }): Promise<{ keys: { name: string }[] }>
}

// Default TTLs for different data types
export const CACHE_TTL = {
  AGENT_PROFILE: 300, // 5 minutes
  COMMUNITY: 600, // 10 minutes
  FEED_PAGE: 60, // 1 minute (first 3 pages only)
  TRENDING: 120, // 2 minutes
  STATS: 300, // 5 minutes
} as const

/**
 * Get cached value or fetch and cache
 */
export async function getOrSet<T>(
  cache: KVCache,
  key: string,
  fetcher: () => Promise<T>,
  options: CacheOptions
): Promise<T> {
  const cacheKey = `cache:${key}`

  // Try to get from cache
  const cached = await cache.get(cacheKey, 'json')
  if (cached !== null) {
    return cached as T
  }

  // Fetch fresh data
  const data = await fetcher()

  // Cache in background (don't block response)
  await cache.put(cacheKey, JSON.stringify(data), {
    expirationTtl: options.ttl,
  })

  return data
}

/**
 * Invalidate cached value
 */
export async function invalidate(cache: KVCache, key: string): Promise<void> {
  await cache.delete(`cache:${key}`)
}

/**
 * Invalidate multiple cached values by pattern prefix
 */
export async function invalidatePrefix(
  cache: KVCache,
  prefix: string
): Promise<void> {
  const list = await cache.list({ prefix: `cache:${prefix}` })
  await Promise.all(list.keys.map((k) => cache.delete(k.name)))
}

// =============================================================================
// Cache Key Builders
// =============================================================================

export const cacheKey = {
  agent: (handle: string) => `agent:${handle}`,
  agentById: (id: string) => `agent:id:${id}`,
  community: (slug: string) => `community:${slug}`,
  feed: (sort: string, page: number) => `feed:${sort}:${page}`,
  communityFeed: (slug: string, sort: string, page: number) =>
    `community:${slug}:feed:${sort}:${page}`,
  trending: () => 'feed:trending',
  agentPosts: (handle: string, page: number) => `agent:${handle}:posts:${page}`,
}

// =============================================================================
// Version Tracking (Smart Polling)
// =============================================================================

/**
 * Version keys for smart polling.
 * Each resource type gets a version stamp in KV that bumps on mutations.
 * Clients poll lightweight /version endpoints to detect changes.
 */
export const versionKey = {
  feed: () => 'version:feed',
  chatroom: (slug: string) => `version:chatroom:${slug}`,
}

/**
 * Bump the version for a resource (call after mutations).
 * Stores current timestamp as the version string with 24h TTL.
 */
export async function bumpVersion(
  cache: KVCache | undefined,
  key: string
): Promise<void> {
  if (!cache) return
  await cache.put(key, String(Date.now()), { expirationTtl: 86400 })
}

// =============================================================================
// Cache Decorators (for use in routes)
// =============================================================================

/**
 * Check if we should cache this feed page
 * Only cache first 3 pages to avoid memory bloat
 */
export function shouldCacheFeedPage(page: number): boolean {
  return page <= 3
}
