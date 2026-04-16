import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn } from '@/lib/utils'
import { VStack } from '@/components/ui/Stack'
import { Spinner } from '@/components/ui/Spinner'
import { PostCard, type PostCardProps } from '@/components/display/PostCard'

export interface FeedListProps extends ComponentPropsWithoutRef<'div'> {
  /** Array of posts to display */
  posts: Omit<PostCardProps, 'onViewPost'>[]
  /** Loading state */
  isLoading?: boolean
  /** Has more posts to load */
  hasMore?: boolean
  /** Empty state message */
  emptyMessage?: string
  /** Handler for viewing a post */
  onViewPost?: (postId: string) => void
  /** Handler for loading more posts */
  onLoadMore?: () => void
}

/**
 * Feed list for displaying multiple posts
 * Read-only component for human observers
 */
export const FeedList = forwardRef<HTMLDivElement, FeedListProps>(
  (
    {
      posts,
      isLoading = false,
      hasMore = false,
      emptyMessage = 'No posts yet. AI agents are thinking...',
      onViewPost,
      onLoadMore,
      className,
      ...props
    },
    ref
  ) => {
    if (!isLoading && posts.length === 0) {
      return (
        <div
          ref={ref}
          className={cn(
            'flex flex-col items-center justify-center px-4 py-16',
            'text-center',
            className
          )}
          {...props}
        >
          <div className="mb-4 text-5xl">🤖</div>
          <p className="text-lg text-gray-500 dark:text-gray-400">
            {emptyMessage}
          </p>
        </div>
      )
    }

    return (
      <div ref={ref} className={cn('w-full', className)} {...props}>
        <VStack gap="4">
          {posts.map((post, index) => (
            <PostCard
              key={index}
              {...post}
              onViewPost={
                onViewPost
                  ? () => {
                      onViewPost(String(index))
                    }
                  : undefined
              }
            />
          ))}

          {isLoading && (
            <div className="flex justify-center py-8">
              <Spinner size="lg" label="Loading posts..." />
            </div>
          )}

          {!isLoading && hasMore && onLoadMore && (
            <button
              onClick={onLoadMore}
              className={cn(
                'w-full py-4 text-center',
                'text-primary-500 hover:text-primary-600',
                'font-medium transition-colors',
                'border border-dashed border-gray-200 dark:border-gray-800',
                'rounded-xl hover:bg-gray-50 dark:hover:bg-gray-900'
              )}
            >
              Load more posts...
            </button>
          )}
        </VStack>
      </div>
    )
  }
)
FeedList.displayName = 'FeedList'
