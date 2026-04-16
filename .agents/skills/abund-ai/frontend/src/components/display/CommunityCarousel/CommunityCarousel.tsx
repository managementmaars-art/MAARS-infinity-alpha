import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/Card'
import { Icon } from '@/components/ui/Icon'
import type { Community } from '@/services/api'

export interface CommunityCarouselProps extends ComponentPropsWithoutRef<'div'> {
  /** Array of communities to display */
  communities: Community[]
  /** Loading state */
  isLoading?: boolean
  /** Click handler for community */
  onCommunityClick?: (slug: string) => void
}

/**
 * Card grid showing new communities
 */
export const CommunityCarousel = forwardRef<
  HTMLDivElement,
  CommunityCarouselProps
>(
  (
    { communities, isLoading = false, onCommunityClick, className, ...props },
    ref
  ) => {
    if (isLoading) {
      return (
        <div
          ref={ref}
          className={cn('flex flex-col gap-2', className)}
          {...props}
        >
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="flex h-16 animate-pulse items-center gap-3 rounded-xl bg-[var(--bg-surface)] p-3"
            >
              <div className="h-10 w-10 rounded-lg bg-[var(--bg-hover)]" />
              <div className="flex-1">
                <div className="mb-2 h-4 w-24 rounded bg-[var(--bg-hover)]" />
                <div className="h-3 w-16 rounded bg-[var(--bg-hover)]" />
              </div>
            </div>
          ))}
        </div>
      )
    }

    if (communities.length === 0) {
      return (
        <div
          ref={ref}
          className={cn(
            'flex items-center justify-center py-6 text-[var(--text-muted)]',
            className
          )}
          {...props}
        >
          <Icon name="globe" size="xl" className="mr-2 opacity-50" />
          <span>No communities yet</span>
        </div>
      )
    }

    return (
      <div
        ref={ref}
        className={cn('flex flex-col gap-2', className)}
        {...props}
      >
        {communities.map((community) => (
          <Card
            key={community.id}
            interactive
            padding="sm"
            onClick={() => onCommunityClick?.(community.slug)}
            className="group"
          >
            <div className="flex items-center gap-3">
              {/* Icon */}
              <div
                className={cn(
                  'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg',
                  'from-primary-500/20 bg-gradient-to-br to-violet-500/20',
                  'text-2xl transition-transform duration-200 group-hover:scale-110'
                )}
              >
                {community.icon_emoji ?? (
                  <Icon name="globe" size="lg" className="text-primary-500" />
                )}
              </div>

              {/* Info */}
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium text-[var(--text-primary)]">
                  {community.name}
                </p>
                <div className="flex gap-3 text-xs text-[var(--text-muted)]">
                  <span className="flex items-center gap-1">
                    <Icon name="users" size="xs" />
                    {community.member_count}
                  </span>
                  <span className="flex items-center gap-1">
                    <Icon name="posts" size="xs" />
                    {community.post_count}
                  </span>
                </div>
              </div>

              {/* Arrow */}
              <Icon
                name="arrowRight"
                size="sm"
                className="group-hover:text-primary-500 shrink-0 text-[var(--text-muted)] transition-transform duration-200 group-hover:translate-x-1"
              />
            </div>
          </Card>
        ))}
      </div>
    )
  }
)
CommunityCarousel.displayName = 'CommunityCarousel'
