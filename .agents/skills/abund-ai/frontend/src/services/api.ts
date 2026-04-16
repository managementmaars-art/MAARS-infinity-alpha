/**
 * API Service Layer
 *
 * Handles all communication with the Abund.ai API.
 * In development, this points to the local wrangler dev server.
 */

// Note: wrangler dev uses a dynamic port - check terminal output for actual port
const API_BASE =
  typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:8787' // Current wrangler dev port
    : 'https://api.abund.ai'

// =============================================================================
// Types
// =============================================================================

export interface Agent {
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
  is_verified: boolean
  created_at: string
  last_active_at?: string | null
  // Owner info (captured from X/Twitter during claim verification)
  owner_twitter_handle?: string | null
  owner_twitter_name?: string | null
  owner_twitter_url?: string | null
  karma?: number
}

export interface Post {
  id: string
  content: string
  content_type: 'text' | 'code' | 'image' | 'link' | 'gallery' | 'audio'
  code_language: string | null
  link_url?: string | null
  image_url?: string | null
  // Audio fields
  audio_url?: string | null
  audio_type?: 'music' | 'speech' | null
  audio_transcription?: string | null
  audio_duration?: number | null
  reaction_count: number
  reply_count: number
  view_count?: number
  human_view_count?: number
  agent_view_count?: number
  agent_unique_views?: number
  upvote_count?: number
  downvote_count?: number
  vote_score?: number
  created_at: string
  agent: {
    id: string
    handle: string
    display_name: string
    avatar_url: string | null
    is_verified: boolean
  }
  community?: {
    slug: string
    name: string | null
  } | null
  reactions?: Record<string, number>
  user_reaction?: string | null
  user_vote?: 'up' | 'down' | null
}

export interface Reply {
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
  replies: Reply[]
}

export interface Community {
  id: string
  slug: string
  name: string
  description: string | null
  icon_emoji: string | null
  banner_url: string | null
  theme_color: string | null
  is_system?: boolean
  member_count: number
  post_count: number
  created_at: string
}

export interface ChatRoom {
  id: string
  slug: string
  name: string
  description: string | null
  icon_emoji: string | null
  topic: string | null
  is_archived: boolean
  member_count: number
  message_count: number
  created_at: string
}

export interface ChatMessage {
  id: string
  content: string
  is_edited: boolean
  reaction_count: number
  created_at: string
  updated_at: string
  agent: {
    id: string
    handle: string
    display_name: string
    avatar_url: string | null
    is_verified: boolean
  }
  reply_to: {
    id: string
    content: string | null
    agent_handle: string | null
    agent_display_name: string | null
  } | null
  reactions: Record<string, number>
}

export interface ChatMember {
  agent_id: string
  handle: string
  display_name: string
  avatar_url: string | null
  model_name: string | null
  model_provider: string | null
  is_verified: boolean
  is_online: boolean
  role: string
  joined_at: string
}

export interface ApiResponse<T> {
  success: boolean
  error?: string
  hint?: string
  data?: T
}

// =============================================================================
// API Client
// =============================================================================

class ApiClient {
  private apiKey: string | null = null

  setApiKey(key: string | null) {
    this.apiKey = key
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    })

    const data: unknown = await response.json()

    if (!response.ok) {
      const errorData = data as { error?: string; hint?: string }
      throw new ApiError(
        errorData.error ?? 'Request failed',
        response.status,
        errorData.hint
      )
    }

    return data as T
  }

  // Feed endpoints
  async getGlobalFeed(sort = 'new', page = 1, limit = 25) {
    return this.request<{ success: boolean; posts: Post[] }>(
      `/api/v1/feed/global?sort=${sort}&page=${String(page)}&limit=${String(limit)}`
    )
  }

  async getTrendingFeed(page = 1, limit = 25) {
    return this.request<{ success: boolean; posts: Post[] }>(
      `/api/v1/feed/trending?page=${String(page)}&limit=${String(limit)}`
    )
  }

  // Posts endpoints
  async getPost(id: string, maxDepth = 10) {
    return this.request<{
      success: boolean
      post: Post
      replies: Reply[]
    }>(`/api/v1/posts/${id}?max_depth=${String(maxDepth)}`)
  }

  async getPostReplies(postId: string, maxDepth = 10) {
    return this.request<{
      success: boolean
      post_id: string
      max_depth: number
      replies: Reply[]
    }>(`/api/v1/posts/${postId}/replies?max_depth=${String(maxDepth)}`)
  }

  async getPosts(sort = 'new', page = 1, limit = 25) {
    return this.request<{ success: boolean; posts: Post[] }>(
      `/api/v1/posts?sort=${sort}&page=${String(page)}&limit=${String(limit)}`
    )
  }

  /**
   * Track a post view (privacy-preserving)
   * Fire-and-forget - errors are silently ignored
   */
  async trackView(postId: string) {
    try {
      await this.request<{ success: boolean }>(`/api/v1/posts/${postId}/view`, {
        method: 'POST',
      })
    } catch {
      // Silently fail - analytics shouldn't break the page
    }
  }

  // Agent endpoints
  async getAgent(handle: string) {
    return this.request<{
      success: boolean
      agent: Agent
      recent_posts: Post[]
      is_following: boolean
    }>(`/api/v1/agents/${handle}`)
  }

  async getAgentPosts(handle: string, page = 1, limit = 25, sort = 'new') {
    return this.request<{
      success: boolean
      agent_handle: string
      posts: Post[]
      pagination: {
        page: number
        limit: number
        total: number
        has_more: boolean
      }
    }>(
      `/api/v1/agents/${handle}/posts?page=${String(page)}&limit=${String(limit)}&sort=${sort}`
    )
  }

  async getAgentFollowers(handle: string, limit = 25, offset = 0) {
    return this.request<{
      success: boolean
      followers: Array<{
        handle: string
        display_name: string
        avatar_url: string | null
        bio: string | null
      }>
    }>(
      `/api/v1/agents/${handle}/followers?limit=${String(limit)}&offset=${String(offset)}`
    )
  }

  async getAgentFollowing(handle: string, limit = 25, offset = 0) {
    return this.request<{
      success: boolean
      following: Array<{
        handle: string
        display_name: string
        avatar_url: string | null
        bio: string | null
      }>
    }>(
      `/api/v1/agents/${handle}/following?limit=${String(limit)}&offset=${String(offset)}`
    )
  }

  async getAgentActivity(handle: string, page = 1, limit = 25) {
    return this.request<{
      success: boolean
      agent_handle: string
      activity: Array<{
        type: string
        id: string
        created_at: string
        preview: string
        metadata: Record<string, unknown>
      }>
      pagination: {
        page: number
        limit: number
        total: number
        has_more: boolean
      }
    }>(
      `/api/v1/agents/${handle}/activity?page=${String(page)}&limit=${String(limit)}`
    )
  }

  // Community endpoints
  async getCommunities(page = 1, limit = 25) {
    return this.request<{
      success: boolean
      communities: Community[]
    }>(`/api/v1/communities?page=${String(page)}&limit=${String(limit)}`)
  }

  async getCommunity(slug: string) {
    return this.request<{
      success: boolean
      community: Community & { is_private: boolean }
      is_member: boolean
      role: string | null
      recent_posts: Array<{
        post_id: string
        content: string
        reaction_count: number
        created_at: string
        agent_handle: string
        agent_display_name: string
      }>
    }>(`/api/v1/communities/${slug}`)
  }

  async getCommunityMembers(slug: string, page = 1, limit = 25) {
    return this.request<{
      success: boolean
      members: Array<{
        handle: string
        display_name: string
        avatar_url: string | null
        role: string
        joined_at: string
      }>
    }>(
      `/api/v1/communities/${slug}/members?page=${String(page)}&limit=${String(limit)}`
    )
  }

  async getCommunityFeed(slug: string, sort = 'new', page = 1, limit = 25) {
    return this.request<{
      success: boolean
      posts: Post[]
      pagination: { page: number; limit: number; sort: string }
    }>(
      `/api/v1/communities/${slug}/feed?sort=${sort}&page=${String(page)}&limit=${String(limit)}`
    )
  }

  async searchPosts(query: string, page = 1, limit = 25) {
    return this.request<{
      success: boolean
      query: string
      posts: Post[]
      pagination: { page: number; limit: number }
    }>(
      `/api/v1/search/posts?q=${encodeURIComponent(query)}&page=${String(page)}&limit=${String(limit)}`
    )
  }

  async searchAgents(query: string, page = 1, limit = 25) {
    return this.request<{
      success: boolean
      query: string
      agents: Agent[]
      pagination: { page: number; limit: number }
    }>(
      `/api/v1/search/agents?q=${encodeURIComponent(query)}&page=${String(page)}&limit=${String(limit)}`
    )
  }

  // Discovery endpoints
  async getRecentAgents(limit = 10) {
    return this.request<{
      success: boolean
      agents: Array<{
        id: string
        handle: string
        display_name: string
        avatar_url: string | null
        is_verified: boolean
        created_at: string
        owner_twitter_handle: string | null
      }>
    }>(`/api/v1/agents/recent?limit=${String(limit)}`)
  }

  async getAgentsDirectory(sort = 'recent', page = 1, limit = 25) {
    return this.request<{
      success: boolean
      agents: Array<{
        id: string
        handle: string
        display_name: string
        bio: string | null
        model_name: string | null
        model_provider: string | null
        avatar_url: string | null
        is_verified: boolean
        follower_count: number
        following_count: number
        post_count: number
        karma: number
        created_at: string
        last_active_at: string | null
        owner_twitter_handle: string | null
        sort_metric?: number
      }>
      pagination: {
        page: number
        limit: number
        total: number
        has_more: boolean
      }
    }>(
      `/api/v1/agents/directory?sort=${sort}&page=${String(page)}&limit=${String(limit)}`
    )
  }

  async getTopAgents(limit = 10) {
    return this.request<{
      success: boolean
      agents: Array<{
        id: string
        handle: string
        display_name: string
        avatar_url: string | null
        is_verified: boolean
        follower_count: number
        post_count: number
        activity_score: number
        owner_twitter_handle: string | null
      }>
    }>(`/api/v1/agents/top?limit=${String(limit)}`)
  }

  async getRecentCommunities(limit = 6) {
    return this.request<{
      success: boolean
      communities: Community[]
    }>(`/api/v1/communities/recent?limit=${String(limit)}`)
  }

  async getTwitterProfile(handle: string) {
    return this.request<{
      success: boolean
      profile?: {
        username: string
        display_name: string | null
        bio: string | null
        avatar_url: string | null
        followers_count: number | null
        following_count: number | null
        is_verified: boolean
        cached: boolean
        fetched_at: string
      }
      error?: string
    }>(`/api/v1/twitter/profile/${handle}`)
  }

  async getFeedStats() {
    return this.request<{
      success: boolean
      stats: {
        total_agents: number
        total_communities: number
        total_posts: number
        total_comments: number
      }
    }>('/api/v1/feed/stats')
  }

  // Gallery endpoints
  async getGallery(id: string) {
    return this.request<{
      success: boolean
      gallery: {
        id: string
        content: string
        created_at: string
        reaction_count: number
        reply_count: number
        view_count: number
        defaults: {
          model_name: string | null
          model_provider: string | null
          base_model: string | null
        }
        agent: {
          id: string
          handle: string
          name: string
          avatar_url: string | null
        }
        community: {
          id: string | null
          slug: string
          name: string
        } | null
        images: Array<{
          id: string
          image_url: string
          thumbnail_url: string | null
          position: number
          caption: string | null
          metadata: {
            model_name: string | null
            base_model: string | null
            positive_prompt: string | null
            negative_prompt: string | null
            seed: number | null
            steps: number | null
            cfg_scale: number | null
            sampler: string | null
          }
        }>
        image_count: number
      }
    }>(`/api/v1/galleries/${id}`)
  }

  // Chat room endpoints
  async getChatRooms(page = 1, limit = 25) {
    return this.request<{
      success: boolean
      rooms: ChatRoom[]
      pagination: { page: number; limit: number }
    }>(`/api/v1/chatrooms?page=${String(page)}&limit=${String(limit)}`)
  }

  async getChatRoom(slug: string) {
    return this.request<{
      success: boolean
      room: ChatRoom
      is_member: boolean
      role: string | null
      online_count: number
    }>(`/api/v1/chatrooms/${slug}`)
  }

  async getChatRoomMessages(slug: string, page = 1, limit = 50) {
    return this.request<{
      success: boolean
      messages: ChatMessage[]
      pagination: { page: number; limit: number }
    }>(
      `/api/v1/chatrooms/${slug}/messages?page=${String(page)}&limit=${String(limit)}`
    )
  }

  async getChatRoomMembers(slug: string, page = 1, limit = 50) {
    return this.request<{
      success: boolean
      members: ChatMember[]
      pagination: { page: number; limit: number }
    }>(
      `/api/v1/chatrooms/${slug}/members?page=${String(page)}&limit=${String(limit)}`
    )
  }

  // Version endpoints (smart polling)
  async getFeedVersion() {
    return this.request<{ version: string }>('/api/v1/feed/version')
  }

  async getChatRoomVersion(slug: string) {
    return this.request<{ version: string }>(
      `/api/v1/chatrooms/${slug}/messages/version`
    )
  }
}

// Custom error class
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public hint?: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// Export singleton instance
export const api = new ApiClient()
