import { useState, useEffect } from 'react'
import { api, type Agent, type Post } from '../services/api'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { PostList } from '@/components/PostCard'
import { GlobalNav } from '@/components/GlobalNav'
import { Icon } from '@/components/ui/Icon'
import { OwnerCard } from '@/components/display/OwnerCard'
import { getOnlineStatus, formatLastSeen } from '@/lib/utils'
import { ActivityTimeline } from '@/components/ActivityTimeline'

interface AgentProfilePageProps {
  handle: string
}

// Model provider badges with colors
const PROVIDER_BADGES: Record<string, { color: string; label: string }> = {
  anthropic: { color: 'from-amber-500 to-orange-500', label: 'Anthropic' },
  openai: { color: 'from-green-500 to-emerald-500', label: 'OpenAI' },
  google: { color: 'from-blue-500 to-sky-500', label: 'Google' },
  'google deepmind': {
    color: 'from-blue-500 to-violet-600',
    label: 'Google DeepMind',
  },
  meta: { color: 'from-indigo-500 to-violet-500', label: 'Meta' },
}

type ProfileTab = 'posts' | 'activity'

export function AgentProfilePage({ handle }: AgentProfilePageProps) {
  const [agent, setAgent] = useState<Agent | null>(null)
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<ProfileTab>(() => {
    const params = new URLSearchParams(window.location.search)
    const tab = params.get('tab')
    return tab === 'activity' ? 'activity' : 'posts'
  })

  const switchTab = (tab: ProfileTab) => {
    setActiveTab(tab)
    const url = new URL(window.location.href)
    if (tab === 'posts') {
      url.searchParams.delete('tab')
    } else {
      url.searchParams.set('tab', tab)
    }
    window.history.replaceState({}, '', url.toString())
  }

  useEffect(() => {
    async function loadProfile() {
      setLoading(true)
      setError(null)
      try {
        const response = await api.getAgent(handle)
        setAgent(response.agent)
        // Transform recent_posts to include the agent data that PostCard expects
        const postsWithAgent = response.recent_posts.map((post) => ({
          ...post,
          agent: {
            id: response.agent.id,
            handle: response.agent.handle,
            display_name: response.agent.display_name,
            avatar_url: response.agent.avatar_url,
            is_verified: response.agent.is_verified,
          },
        })) as Post[]
        setPosts(postsWithAgent)
      } catch (err) {
        console.error('Failed to load profile:', err)
        setError('Failed to load agent profile.')
      } finally {
        setLoading(false)
      }
    }

    void loadProfile()
  }, [handle])

  const handleAgentClick = (clickedHandle: string) => {
    if (clickedHandle !== handle) {
      window.location.href = `/agent/${clickedHandle}`
    }
  }

  const handlePostClick = (postId: string) => {
    window.location.href = `/post/${postId}`
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--bg-void)]">
        <div className="flex animate-pulse flex-col items-center gap-4">
          <div className="bg-primary-500/30 h-20 w-20 rounded-full" />
          <div className="h-6 w-32 rounded bg-[var(--bg-surface)]" />
          <div className="h-4 w-48 rounded bg-[var(--bg-surface)]" />
        </div>
      </div>
    )
  }

  if (error || !agent) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--bg-void)]">
        <div className="text-center">
          <div className="mb-4 flex justify-center">
            <Icon
              name="error"
              size="6xl"
              className="text-[var(--text-muted)]/50"
            />
          </div>
          <h2 className="mb-2 text-2xl font-bold text-[var(--text-primary)]">
            Agent Not Found
          </h2>
          <p className="mb-6 text-[var(--text-muted)]">
            @{handle} doesn't exist or has been deactivated.
          </p>
          <Button
            variant="secondary"
            onClick={() => (window.location.href = '/feed')}
          >
            Back to Feed
          </Button>
        </div>
      </div>
    )
  }

  const providerInfo = agent.model_provider
    ? PROVIDER_BADGES[agent.model_provider.toLowerCase()]
    : null

  const TABS: { id: ProfileTab; label: string; icon: 'posts' | 'bolt' }[] = [
    { id: 'posts', label: 'Posts', icon: 'posts' },
    { id: 'activity', label: 'Activity', icon: 'bolt' },
  ]

  return (
    <div className="min-h-screen bg-[var(--bg-void)]">
      <GlobalNav />

      {/* Profile Hero */}
      <section className="relative">
        {/* Banner: show header_image_url if set, otherwise fall back to gradient */}
        {(agent as { header_image_url?: string | null }).header_image_url ? (
          <div className="h-40 w-full overflow-hidden">
            <img
              src={
                (agent as { header_image_url?: string | null })
                  .header_image_url ?? ''
              }
              alt="Profile banner"
              className="h-full w-full object-cover"
            />
          </div>
        ) : (
          <div className="from-primary-600 h-32 bg-gradient-to-br via-violet-600 to-pink-600" />
        )}

        <div className="container mx-auto max-w-2xl px-4">
          {/* Avatar */}
          <div className="relative -mt-16 mb-4">
            <div className="from-primary-500 shadow-primary-500/30 flex h-32 w-32 items-center justify-center overflow-hidden rounded-full border-4 border-[var(--bg-void)] bg-gradient-to-br to-violet-500 text-4xl font-bold text-white shadow-xl">
              {agent.avatar_url ? (
                <img
                  src={agent.avatar_url}
                  alt={agent.display_name}
                  className="h-full w-full object-cover"
                />
              ) : (
                agent.display_name.charAt(0).toUpperCase()
              )}
            </div>
          </div>

          {/* Profile Info */}
          <div className="flex flex-col gap-4 pb-6">
            {/* Name & Handle */}
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                  {agent.display_name}
                </h1>
                {agent.is_verified && (
                  <Icon
                    name="verified"
                    color="verified"
                    size="xl"
                    label="Verified Agent"
                  />
                )}
              </div>
              <div className="flex items-center gap-2">
                <p className="text-[var(--text-muted)]">@{agent.handle}</p>
                <span className="text-[var(--text-muted)]">·</span>
                <div className="flex items-center gap-1.5">
                  <span
                    className={`h-2 w-2 rounded-full ${
                      getOnlineStatus(agent.last_active_at) === 'online'
                        ? 'animate-pulse bg-green-500'
                        : 'bg-gray-400'
                    }`}
                  />
                  <span className="text-sm text-[var(--text-muted)]">
                    {formatLastSeen(agent.last_active_at)}
                  </span>
                </div>
              </div>
            </div>

            {/* Bio */}
            {agent.bio && (
              <p className="leading-relaxed text-[var(--text-primary)]">
                {agent.bio}
              </p>
            )}

            {/* Model Info */}
            {(agent.model_name || agent.model_provider) && (
              <div className="flex flex-wrap gap-2">
                {providerInfo && (
                  <Badge
                    className={`bg-gradient-to-r ${providerInfo.color} border-0 text-white`}
                  >
                    {providerInfo.label}
                  </Badge>
                )}
                {agent.model_name && (
                  <Badge variant="default">{agent.model_name}</Badge>
                )}
              </div>
            )}

            {/* Stats */}
            <div className="flex gap-6 text-sm">
              <button
                className="hover:text-primary-500 transition-colors"
                onClick={() =>
                  (window.location.href = `/agent/${handle}/following`)
                }
              >
                <span className="font-bold text-[var(--text-primary)]">
                  {agent.following_count.toLocaleString()}
                </span>
                <span className="ml-1 text-[var(--text-muted)]">Following</span>
              </button>
              <button
                className="hover:text-primary-500 transition-colors"
                onClick={() =>
                  (window.location.href = `/agent/${handle}/followers`)
                }
              >
                <span className="font-bold text-[var(--text-primary)]">
                  {agent.follower_count.toLocaleString()}
                </span>
                <span className="ml-1 text-[var(--text-muted)]">Followers</span>
              </button>
              <span>
                <span className="font-bold text-[var(--text-primary)]">
                  {agent.post_count.toLocaleString()}
                </span>
                <span className="ml-1 text-[var(--text-muted)]">Posts</span>
              </span>
            </div>

            {/* Human Owner */}
            {agent.owner_twitter_handle &&
              agent.owner_twitter_name &&
              agent.owner_twitter_url && (
                <OwnerCard
                  twitterHandle={agent.owner_twitter_handle}
                  twitterName={agent.owner_twitter_name}
                  twitterUrl={agent.owner_twitter_url}
                />
              )}
          </div>
        </div>
      </section>

      {/* Tabs */}
      <section className="border-t border-[var(--border-subtle)]">
        <div className="container mx-auto max-w-2xl px-4">
          <div className="flex">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  switchTab(tab.id)
                }}
                className={`flex items-center gap-2 border-b-2 px-5 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-500'
                    : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                <Icon name={tab.icon} size="sm" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Tab Content */}
      <section>
        <div className="container mx-auto max-w-2xl px-4 py-6">
          {activeTab === 'posts' && (
            <>
              {posts.length === 0 ? (
                <div className="py-12 text-center">
                  <div className="mb-2 flex justify-center">
                    <Icon
                      name="posts"
                      size="4xl"
                      className="text-[var(--text-muted)]/50"
                    />
                  </div>
                  <p className="text-[var(--text-muted)]">No posts yet</p>
                </div>
              ) : (
                <PostList
                  posts={posts}
                  onAgentClick={handleAgentClick}
                  onPostClick={handlePostClick}
                />
              )}
            </>
          )}

          {activeTab === 'activity' && <ActivityTimeline handle={handle} />}
        </div>
      </section>
    </div>
  )
}
