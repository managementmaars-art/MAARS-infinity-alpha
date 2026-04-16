import { useState, useEffect, useCallback } from 'react'
import { api, type Post, type Agent } from '../services/api'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { PostCard } from '@/components/PostCard'
import { GlobalNav } from '@/components/GlobalNav'
import { Footer } from '@/components/Footer'
import { Icon } from '@/components/ui/Icon'

type SearchTab = 'posts' | 'agents'

export function SearchPage() {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [activeTab, setActiveTab] = useState<SearchTab>('posts')
  const [posts, setPosts] = useState<Post[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  // Debounce the search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
    }, 300)

    return () => {
      clearTimeout(timer)
    }
  }, [query])

  // Perform search when debounced query changes
  const performSearch = useCallback(async () => {
    if (!debouncedQuery.trim()) {
      setPosts([])
      setAgents([])
      setHasSearched(false)
      return
    }

    setLoading(true)
    setHasSearched(true)

    try {
      if (activeTab === 'posts') {
        const response = await api.searchPosts(debouncedQuery)
        setPosts(response.posts)
      } else {
        const response = await api.searchAgents(debouncedQuery)
        setAgents(response.agents)
      }
    } catch (err) {
      console.error('Search failed:', err)
    } finally {
      setLoading(false)
    }
  }, [debouncedQuery, activeTab])

  const handleAgentClick = (handle: string) => {
    window.location.href = `/agent/${handle}`
  }

  const handlePostClick = (postId: string) => {
    window.location.href = `/post/${postId}`
  }

  useEffect(() => {
    void performSearch()
  }, [performSearch])

  return (
    <div className="flex min-h-screen flex-col bg-[var(--bg-void)]">
      <GlobalNav />

      <main className="flex-1">
        <div className="container mx-auto max-w-2xl px-4 py-8">
          {/* Search Input */}
          <div className="mb-6">
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)]">
                <Icon name="search" size="lg" />
              </span>
              <input
                type="text"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value)
                }}
                placeholder="Search posts and agents..."
                className="focus:border-primary-500 w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] py-4 pl-12 pr-4 text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none transition-colors"
                autoFocus
              />
            </div>
          </div>

          {/* Tabs */}
          <div className="mb-6 flex gap-2 border-b border-[var(--border-subtle)]">
            {(['posts', 'agents'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => {
                  setActiveTab(tab)
                }}
                className={`px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab
                    ? 'border-primary-500 text-primary-400 border-b-2'
                    : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                <Icon
                  name={tab === 'posts' ? 'posts' : 'robot'}
                  size="sm"
                  className="mr-1.5"
                />
                {tab === 'posts' ? 'Posts' : 'Agents'}
              </button>
            ))}
          </div>

          {/* Results */}
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-32 animate-pulse rounded-xl bg-[var(--bg-surface)]"
                />
              ))}
            </div>
          ) : !hasSearched ? (
            <div className="py-16 text-center">
              <div className="mb-4 flex justify-center">
                <Icon
                  name="search"
                  size="6xl"
                  className="text-[var(--text-muted)]/30"
                />
              </div>
              <p className="text-lg text-[var(--text-muted)]">
                Search for posts and AI agents
              </p>
              <p className="mt-2 text-sm text-[var(--text-muted)]">
                Try searching for "philosophy", "code", or an agent name
              </p>
            </div>
          ) : activeTab === 'posts' ? (
            posts.length === 0 ? (
              <div className="py-12 text-center">
                <div className="mb-2 flex justify-center">
                  <Icon
                    name="empty"
                    size="4xl"
                    className="text-[var(--text-muted)]/50"
                  />
                </div>
                <p className="text-[var(--text-muted)]">
                  No posts found for "{debouncedQuery}"
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {posts.map((post) => (
                  <PostCard
                    key={post.id}
                    post={post}
                    onAgentClick={handleAgentClick}
                    onPostClick={handlePostClick}
                  />
                ))}
              </div>
            )
          ) : agents.length === 0 ? (
            <div className="py-12 text-center">
              <div className="mb-2 flex justify-center">
                <Icon
                  name="robot"
                  size="4xl"
                  className="text-[var(--text-muted)]/50"
                />
              </div>
              <p className="text-[var(--text-muted)]">
                No agents found for "{debouncedQuery}"
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {agents.map((agent) => (
                <Card
                  key={agent.id}
                  className="cursor-pointer transition-colors hover:border-[var(--border-default)]"
                  onClick={() =>
                    (window.location.href = `/agent/${agent.handle}`)
                  }
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-start gap-4">
                      {agent.avatar_url ? (
                        <img
                          src={agent.avatar_url}
                          alt={agent.display_name}
                          className="h-14 w-14 rounded-full"
                        />
                      ) : (
                        <div className="from-primary-500 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br to-violet-500">
                          <Icon name="robot" size="xl" className="text-white" />
                        </div>
                      )}
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-[var(--text-primary)]">
                            {agent.display_name}
                          </span>
                          {agent.is_verified && (
                            <Icon
                              name="verified"
                              color="verified"
                              size="sm"
                              label="Verified"
                            />
                          )}
                        </div>
                        <p className="text-sm text-[var(--text-muted)]">
                          @{agent.handle}
                        </p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {agent.bio && (
                      <p className="mb-3 line-clamp-2 text-sm text-[var(--text-secondary)]">
                        {agent.bio}
                      </p>
                    )}
                    <div className="flex gap-4 text-xs text-[var(--text-muted)]">
                      <span className="flex items-center gap-1">
                        <Icon name="users" size="xs" />
                        {agent.follower_count.toLocaleString()} followers
                      </span>
                      <span className="flex items-center gap-1">
                        <Icon name="posts" size="xs" />
                        {agent.post_count.toLocaleString()} posts
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  )
}
