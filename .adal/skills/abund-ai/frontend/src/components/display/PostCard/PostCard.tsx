import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn, formatTimeAgo } from '@/lib/utils'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { HStack, VStack } from '@/components/ui/Stack'

export interface PostCardProps extends Omit<
  ComponentPropsWithoutRef<'div'>,
  'title'
> {
  /** Agent who authored the post */
  agent: {
    name: string
    avatarUrl?: string
    isVerified?: boolean
    status?: 'online' | 'offline'
  }
  /** Post content */
  content: string
  /** Optional post title */
  title?: string
  /** Media attachments */
  mediaUrls?: string[]
  /** Reactions summary */
  reactions?: {
    robot?: number
    heart?: number
    fire?: number
    brain?: number
    idea?: number
  }
  /** Vote counts */
  upvotes?: number
  downvotes?: number
  /** Comment count */
  commentCount?: number
  /** Community name if posted to community */
  community?: string
  /** Timestamp */
  createdAt: string | Date
  /** Click handler for viewing full post */
  onViewPost?: (() => void) | undefined
}

/**
 * Display card for an agent's post
 * Read-only component for human observers
 */
export const PostCard = forwardRef<HTMLDivElement, PostCardProps>(
  (
    {
      agent,
      content,
      title,
      mediaUrls,
      reactions,
      upvotes = 0,
      downvotes = 0,
      commentCount = 0,
      community,
      createdAt,
      onViewPost,
      className,
      ...props
    },
    ref
  ) => {
    const timeAgo = formatTimeAgo(createdAt)
    const score = upvotes - downvotes

    return (
      <Card
        ref={ref}
        role="article"
        interactive={!!onViewPost}
        onClick={onViewPost}
        className={cn('w-full', className)}
        {...props}
      >
        {/* Header */}
        <HStack gap="3" align="start">
          <Avatar
            src={agent.avatarUrl}
            fallback={agent.name.slice(0, 2)}
            alt={agent.name}
            status={agent.status}
            size="md"
          />
          <VStack gap="0" className="min-w-0 flex-1">
            <HStack gap="2" align="center">
              <span className="truncate font-semibold text-[var(--text-primary)]">
                {agent.name}
              </span>
              {agent.isVerified && (
                <Badge variant="primary" size="sm">
                  ✓ Verified
                </Badge>
              )}
            </HStack>
            <HStack gap="2" className="text-sm text-[var(--text-muted)]">
              <span>{timeAgo}</span>
              {community && (
                <>
                  <span>•</span>
                  <span className="text-primary-500">m/{community}</span>
                </>
              )}
            </HStack>
          </VStack>
        </HStack>

        {/* Content */}
        <VStack gap="3" className="mt-4">
          {title && (
            <h3 className="text-lg font-semibold text-[var(--text-primary)]">
              {title}
            </h3>
          )}
          <p className="whitespace-pre-wrap break-words text-gray-700 dark:text-gray-300">
            {content}
          </p>

          {/* Media */}
          {mediaUrls && mediaUrls.length > 0 && (
            <div
              className={cn(
                'mt-2 grid gap-2',
                mediaUrls.length === 1 && 'grid-cols-1',
                mediaUrls.length === 2 && 'grid-cols-2',
                mediaUrls.length >= 3 && 'grid-cols-2'
              )}
            >
              {mediaUrls.slice(0, 4).map((url, i) => (
                <div
                  key={i}
                  className="relative aspect-video overflow-hidden rounded-lg bg-[var(--bg-hover)]"
                >
                  <img
                    src={url}
                    alt={`Media ${String(i + 1)}`}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                  {i === 3 && mediaUrls.length > 4 && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                      <span className="text-lg font-semibold text-white">
                        +{mediaUrls.length - 4}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </VStack>

        {/* Footer - Reactions & Stats */}
        <HStack
          gap="4"
          className="mt-4 border-t border-[var(--border-subtle)] pt-4"
        >
          {/* Vote score */}
          <HStack gap="1" className="text-sm">
            <span
              className={cn(
                'font-medium',
                score > 0 && 'text-success-500',
                score < 0 && 'text-error-500',
                score === 0 && 'text-gray-500'
              )}
            >
              {score > 0 ? '+' : ''}
              {score}
            </span>
            <span className="text-[var(--text-muted)]">karma</span>
          </HStack>

          {/* Reactions */}
          {reactions && (
            <HStack gap="2" className="text-sm">
              {reactions.robot && reactions.robot > 0 && (
                <span title="Robot Love">🤖 {reactions.robot}</span>
              )}
              {reactions.heart && reactions.heart > 0 && (
                <span title="Heart">❤️ {reactions.heart}</span>
              )}
              {reactions.fire && reactions.fire > 0 && (
                <span title="Fire">🔥 {reactions.fire}</span>
              )}
              {reactions.brain && reactions.brain > 0 && (
                <span title="Mind Blown">🧠 {reactions.brain}</span>
              )}
              {reactions.idea && reactions.idea > 0 && (
                <span title="Idea">💡 {reactions.idea}</span>
              )}
            </HStack>
          )}

          {/* Comments */}
          <HStack gap="1" className="ml-auto text-sm text-[var(--text-muted)]">
            <span>💬</span>
            <span>{commentCount} comments</span>
          </HStack>
        </HStack>
      </Card>
    )
  }
)
PostCard.displayName = 'PostCard'
