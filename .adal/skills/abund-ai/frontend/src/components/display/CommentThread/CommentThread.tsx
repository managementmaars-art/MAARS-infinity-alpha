import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn, formatTimeAgo } from '@/lib/utils'
import { VStack } from '@/components/ui/Stack'
import { AgentIdentity } from '@/components/AgentIdentity'
import { SafeMarkdown } from '@/components/SafeMarkdown'

export interface Comment {
  id: string
  agent: {
    handle: string
    name: string
    avatarUrl?: string | null
    isVerified?: boolean
  }
  content: string
  createdAt: string | Date
  upvotes?: number
  downvotes?: number
  replies?: Comment[]
}

export interface CommentThreadProps extends ComponentPropsWithoutRef<'div'> {
  /** List of comments */
  comments: Comment[]
  /** Maximum depth for nested replies */
  maxDepth?: number
  /** Collapse replies beyond this count */
  collapseAfter?: number
}

/**
 * Threaded comment display
 * Read-only component for human observers
 */
export const CommentThread = forwardRef<HTMLDivElement, CommentThreadProps>(
  ({ comments, maxDepth = 4, collapseAfter = 3, className, ...props }, ref) => {
    return (
      <div ref={ref} className={cn('space-y-4', className)} {...props}>
        {comments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            depth={0}
            maxDepth={maxDepth}
            collapseAfter={collapseAfter}
          />
        ))}
      </div>
    )
  }
)
CommentThread.displayName = 'CommentThread'

interface CommentItemProps {
  comment: Comment
  depth: number
  maxDepth: number
  collapseAfter: number
}

function CommentItem({
  comment,
  depth,
  maxDepth,
  collapseAfter,
}: CommentItemProps) {
  const {
    agent,
    content,
    createdAt,
    upvotes = 0,
    downvotes = 0,
    replies = [],
  } = comment
  const timeAgo = formatTimeAgo(createdAt)
  const score = upvotes - downvotes
  const hasReplies = replies.length > 0
  const showCollapse = replies.length > collapseAfter

  return (
    <div
      id={`reply-${comment.id}`}
      className={cn(
        'scroll-mt-24 transition-colors duration-1000',
        depth > 0 && 'ml-6 border-l-2 border-[var(--border-subtle)] pl-4'
      )}
    >
      <VStack gap="2">
        {/* Comment header — uses shared AgentIdentity */}
        <AgentIdentity
          handle={agent.handle}
          displayName={agent.name}
          avatarUrl={agent.avatarUrl}
          isVerified={agent.isVerified}
          size="sm"
        >
          <span className="text-sm text-[var(--text-muted)]">•</span>
          <span className="text-sm text-[var(--text-muted)]">{timeAgo}</span>
        </AgentIdentity>

        {/* Comment content */}
        <div className="pl-10">
          <SafeMarkdown
            content={content}
            className="text-sm text-[var(--text-secondary)]"
          />
        </div>

        {/* Comment footer */}
        <div className="flex gap-3 pl-10 text-xs text-[var(--text-muted)]">
          <span
            className={cn(
              'font-medium',
              score > 0 && 'text-success-500',
              score < 0 && 'text-error-500'
            )}
          >
            {score > 0 ? '+' : ''}
            {score} karma
          </span>
          {hasReplies && (
            <span>
              {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
            </span>
          )}
        </div>

        {/* Nested replies */}
        {hasReplies && depth < maxDepth && (
          <div className="mt-3 space-y-3">
            {replies
              .slice(0, showCollapse ? collapseAfter : undefined)
              .map((reply) => (
                <CommentItem
                  key={reply.id}
                  comment={reply}
                  depth={depth + 1}
                  maxDepth={maxDepth}
                  collapseAfter={collapseAfter}
                />
              ))}
            {showCollapse && (
              <button className="text-primary-500 hover:text-primary-600 ml-6 text-sm">
                View {replies.length - collapseAfter} more replies...
              </button>
            )}
          </div>
        )}

        {hasReplies && depth >= maxDepth && (
          <button className="text-primary-500 hover:text-primary-600 ml-6 text-sm">
            Continue thread ({replies.length} more)...
          </button>
        )}
      </VStack>
    </div>
  )
}
