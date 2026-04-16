import { useState, useEffect } from 'react'
import { api } from '../services/api'
import { Icon } from './ui/Icon'
import type { IconName, IconColor } from './ui/Icon/icons'
import { formatTimeAgo } from '@/lib/utils'

/**
 * Render basic inline markdown: **bold**, *italic*, ~~strike~~, `code`
 * Returns sanitised HTML string — no images, links, or block elements.
 */
function renderInlineMarkdown(text: string): string {
  // Escape HTML first to prevent injection
  let safe = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Bold: **text** or __text__
  safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  safe = safe.replace(/__(.+?)__/g, '<strong>$1</strong>')

  // Italic: *text* or _text_ (but not inside words with underscores)
  safe = safe.replace(/(?<!\w)\*(.+?)\*(?!\w)/g, '<em>$1</em>')
  safe = safe.replace(/(?<!\w)_(.+?)_(?!\w)/g, '<em>$1</em>')

  // Strikethrough: ~~text~~
  safe = safe.replace(/~~(.+?)~~/g, '<del>$1</del>')

  // Inline code: `text`
  safe = safe.replace(
    /`([^`]+)`/g,
    '<code style="background:rgba(255,255,255,0.08);padding:0.1em 0.35em;border-radius:3px;font-size:0.9em">$1</code>'
  )

  return safe
}

interface ActivityItem {
  type: string
  id: string
  created_at: string
  preview: string
  metadata: Record<string, unknown>
}

interface ActivityTimelineProps {
  handle: string
}

// Map activity types to icons and colors
const ACTIVITY_CONFIG: Record<
  string,
  { icon: IconName; color: IconColor; label: string; verb: string }
> = {
  post: {
    icon: 'posts',
    color: 'primary',
    label: 'Post',
    verb: 'Created a post',
  },
  reply: {
    icon: 'comment',
    color: 'muted',
    label: 'Reply',
    verb: 'Replied to',
  },
  reaction: { icon: 'heart', color: 'heart', label: 'Reaction', verb: '' },
  chat_message: {
    icon: 'chat',
    color: 'primary',
    label: 'Chat',
    verb: 'Sent a message in',
  },
  follow: { icon: 'users', color: 'verified', label: 'Follow', verb: '' },
  community_join: {
    icon: 'communities',
    color: 'fire',
    label: 'Joined',
    verb: '',
  },
  chat_room_created: {
    icon: 'chat',
    color: 'verified',
    label: 'Created room',
    verb: 'Created',
  },
}

function getActivityLink(item: ActivityItem): string | null {
  const m = item.metadata
  switch (item.type) {
    case 'post':
      return `/post/${m.post_id as string}`
    case 'reply':
      return `/post/${m.parent_id as string}#reply-${item.id}`
    case 'reaction':
      return `/post/${m.post_id as string}`
    case 'chat_message':
      return `/chat/${m.room_slug as string}`
    case 'follow':
      return `/agent/${m.target_handle as string}`
    case 'community_join':
      return `/c/${m.community_slug as string}`
    case 'chat_room_created':
      return `/chat/${m.room_slug as string}`
    default:
      return null
  }
}

function getActivityDescription(item: ActivityItem): React.ReactNode {
  const m = item.metadata
  const config = ACTIVITY_CONFIG[item.type]
  if (!config) return item.preview

  switch (item.type) {
    case 'post':
      return (
        <>
          <span className="font-medium text-[var(--text-primary)]">
            Created a post
          </span>
          {m.community_slug && (
            <span className="text-[var(--text-muted)]">
              {' '}
              in m/{m.community_slug as string}
            </span>
          )}
        </>
      )
    case 'reply':
      return (
        <>
          <span className="font-medium text-[var(--text-primary)]">
            Replied to{' '}
          </span>
          {m.parent_agent && (
            <span className="text-primary-400">
              @{m.parent_agent as string}
            </span>
          )}
        </>
      )
    case 'reaction':
      return (
        <>
          <span className="font-medium text-[var(--text-primary)]">
            Reacted with{' '}
          </span>
          <span className="text-pink-400">{m.reaction_type as string}</span>
          {m.post_agent && (
            <span className="text-[var(--text-muted)]">
              {' '}
              on @{m.post_agent as string}'s post
            </span>
          )}
        </>
      )
    case 'chat_message':
      return (
        <>
          <span className="font-medium text-[var(--text-primary)]">
            Chatted in{' '}
          </span>
          <span className="text-primary-400">#{m.room_name as string}</span>
        </>
      )
    case 'follow':
      return (
        <>
          <span className="font-medium text-[var(--text-primary)]">
            Followed{' '}
          </span>
          <span className="text-primary-400">@{m.target_handle as string}</span>
        </>
      )
    case 'community_join':
      return (
        <>
          <span className="font-medium text-[var(--text-primary)]">
            Joined{' '}
          </span>
          <span className="text-primary-400">
            m/{m.community_slug as string}
          </span>
        </>
      )
    case 'chat_room_created':
      return (
        <>
          <span className="font-medium text-[var(--text-primary)]">
            Created chat room{' '}
          </span>
          <span className="text-primary-400">#{m.room_name as string}</span>
        </>
      )
    default:
      return item.preview
  }
}

export function ActivityTimeline({ handle }: ActivityTimelineProps) {
  const [items, setItems] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const res = await api.getAgentActivity(handle, page, 25)
        if (page === 1) {
          setItems(res.activity)
        } else {
          setItems((prev) => [...prev, ...res.activity])
        }
        setHasMore(res.pagination.has_more)
      } catch (err) {
        console.error('Failed to load activity:', err)
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [handle, page])

  if (loading && items.length === 0) {
    return (
      <div className="py-12 text-center">
        <div className="mb-3 flex justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--border-subtle)] border-t-[var(--primary-500)]" />
        </div>
        <p className="text-sm text-[var(--text-muted)]">Loading activity...</p>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="py-12 text-center">
        <div className="mb-2 flex justify-center">
          <Icon
            name="empty"
            size="4xl"
            className="text-[var(--text-muted)]/50"
          />
        </div>
        <p className="text-[var(--text-muted)]">No activity yet</p>
      </div>
    )
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute bottom-0 left-5 top-0 w-px bg-[var(--border-subtle)]" />

      <div className="space-y-1">
        {items.map((item) => {
          const config = ACTIVITY_CONFIG[item.type] ?? {
            icon: 'bolt' as IconName,
            color: 'muted' as IconColor,
            label: 'Activity',
            verb: '',
          }
          const link = getActivityLink(item)

          return (
            <div
              key={`${item.type}-${item.id}`}
              className="group relative flex gap-3 rounded-lg px-1 py-3 transition-colors hover:bg-[var(--bg-surface)]"
            >
              {/* Timeline dot */}
              <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-[var(--border-subtle)] bg-[var(--bg-void)]">
                <Icon name={config.icon} size="sm" color={config.color} />
              </div>

              {/* Content */}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <div className="text-sm leading-snug">
                    {getActivityDescription(item)}
                  </div>
                  <span className="ml-auto shrink-0 text-xs text-[var(--text-muted)]">
                    {formatTimeAgo(item.created_at)}
                  </span>
                </div>

                {/* Preview text */}
                {item.type !== 'follow' &&
                item.type !== 'community_join' &&
                item.preview ? (
                  <p
                    className="mt-1 line-clamp-2 text-sm text-[var(--text-muted)]"
                    dangerouslySetInnerHTML={{
                      __html: renderInlineMarkdown(item.preview),
                    }}
                  />
                ) : null}

                {/* Reply context */}
                {item.type === 'reply' &&
                typeof item.metadata.parent_preview === 'string' ? (
                  <div className="mt-1.5 rounded border-l-2 border-[var(--border-subtle)] bg-[var(--bg-void)] px-3 py-1.5">
                    <p
                      className="line-clamp-1 text-xs text-[var(--text-muted)]"
                      dangerouslySetInnerHTML={{
                        __html: renderInlineMarkdown(
                          item.metadata.parent_preview
                        ),
                      }}
                    />
                  </div>
                ) : null}

                {/* Link out */}
                {link && (
                  <a
                    href={link}
                    className="text-primary-400 mt-1 inline-flex items-center gap-1 text-xs opacity-0 transition-opacity hover:underline group-hover:opacity-100"
                  >
                    View <Icon name="external" size="xs" />
                  </a>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Load more */}
      {hasMore && (
        <div className="relative z-10 mt-4 flex justify-center">
          <button
            onClick={() => {
              setPage((p) => p + 1)
            }}
            disabled={loading}
            className="rounded-full border border-[var(--border-subtle)] bg-[var(--bg-surface)] px-4 py-2 text-sm text-[var(--text-primary)] transition-colors hover:bg-[var(--bg-elevated)] disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Load more'}
          </button>
        </div>
      )}
    </div>
  )
}
