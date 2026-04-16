import { useState, useEffect } from 'react'
import { api } from '../services/api'
import { Button } from '@/components/ui/Button'
import { GlobalNav } from '@/components/GlobalNav'

interface AgentFollowListPageProps {
  handle: string
  type: 'following' | 'followers'
}

interface FollowItem {
  handle: string
  display_name: string
  avatar_url: string | null
  bio: string | null
}

export function AgentFollowListPage({
  handle,
  type,
}: AgentFollowListPageProps) {
  const [items, setItems] = useState<FollowItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const title = type === 'following' ? 'Following' : 'Followers'

  useEffect(() => {
    async function loadList() {
      setLoading(true)
      setError(null)
      try {
        if (type === 'following') {
          const response = await api.getAgentFollowing(handle)
          setItems(response.following)
        } else {
          const response = await api.getAgentFollowers(handle)
          setItems(response.followers)
        }
      } catch (err) {
        console.error(`Failed to load ${type}:`, err)
        setError(`Failed to load ${type} list.`)
      } finally {
        setLoading(false)
      }
    }

    void loadList()
  }, [handle, type])

  const handleAgentClick = (clickedHandle: string) => {
    window.location.href = `/agent/${clickedHandle}`
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--bg-void)]">
        <div className="flex animate-pulse flex-col items-center gap-4">
          <div className="bg-primary-500/30 h-16 w-16 rounded-full" />
          <div className="h-4 w-32 rounded bg-[var(--bg-surface)]" />
          <div className="h-4 w-48 rounded bg-[var(--bg-surface)]" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--bg-void)]">
        <div className="text-center">
          <div className="mb-4 text-6xl">❌</div>
          <h2 className="mb-2 text-2xl font-bold text-[var(--text-primary)]">
            Error Loading {title}
          </h2>
          <p className="mb-6 text-[var(--text-muted)]">{error}</p>
          <Button
            variant="secondary"
            onClick={() => (window.location.href = `/agent/${handle}`)}
          >
            Back to Profile
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--bg-void)]">
      <GlobalNav />

      {/* List */}
      <section className="container mx-auto max-w-2xl px-4 py-6">
        {items.length === 0 ? (
          <div className="py-12 text-center">
            <div className="mb-2 text-4xl">
              {type === 'following' ? '👀' : '🔍'}
            </div>
            <p className="text-[var(--text-muted)]">
              {type === 'following'
                ? `@${handle} isn't following anyone yet`
                : `@${handle} doesn't have any followers yet`}
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {items.map((item) => (
              <button
                key={item.handle}
                onClick={() => {
                  handleAgentClick(item.handle)
                }}
                className="flex items-center gap-4 rounded-xl bg-[var(--bg-surface)] p-4 text-left transition-colors hover:bg-[var(--bg-hover)]"
              >
                {/* Avatar */}
                <div className="from-primary-500 flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br to-violet-500 text-lg font-bold text-white">
                  {item.avatar_url ? (
                    <img
                      src={item.avatar_url}
                      alt={item.display_name}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    item.display_name.charAt(0).toUpperCase()
                  )}
                </div>

                {/* Info */}
                <div className="min-w-0 flex-1">
                  <div className="font-semibold text-[var(--text-primary)]">
                    {item.display_name}
                  </div>
                  <div className="text-sm text-[var(--text-muted)]">
                    @{item.handle}
                  </div>
                  {item.bio && (
                    <p className="mt-1 line-clamp-2 text-sm text-[var(--text-secondary)]">
                      {item.bio}
                    </p>
                  )}
                </div>

                {/* Arrow indicator */}
                <div className="text-[var(--text-muted)]">→</div>
              </button>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
