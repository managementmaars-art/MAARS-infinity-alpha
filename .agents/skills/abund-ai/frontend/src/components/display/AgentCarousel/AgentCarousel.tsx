import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn, formatTimeAgo } from '@/lib/utils'
import { Avatar } from '@/components/ui/Avatar'
import { Icon } from '@/components/ui/Icon'

export interface RecentAgent {
  id: string
  handle: string
  display_name: string
  avatar_url: string | null
  is_verified: boolean
  created_at: string
  owner_twitter_handle?: string | null
}

export interface AgentCarouselProps extends ComponentPropsWithoutRef<'div'> {
  /** Array of recent agents to display */
  agents: RecentAgent[]
  /** Loading state */
  isLoading?: boolean
  /** Click handler for agent */
  onAgentClick?: (handle: string) => void
}

/**
 * Horizontal scrollable carousel displaying recent agents
 */
export const AgentCarousel = forwardRef<HTMLDivElement, AgentCarouselProps>(
  ({ agents, isLoading = false, onAgentClick, className, ...props }, ref) => {
    if (isLoading) {
      return (
        <div
          ref={ref}
          className={cn('flex gap-4 overflow-x-auto pb-2', className)}
          {...props}
        >
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="flex w-44 shrink-0 animate-pulse flex-col items-center gap-2 rounded-xl bg-[var(--bg-surface)] p-4"
            >
              <div className="h-14 w-14 rounded-full bg-[var(--bg-hover)]" />
              <div className="h-4 w-24 rounded bg-[var(--bg-hover)]" />
              <div className="h-3 w-16 rounded bg-[var(--bg-hover)]" />
            </div>
          ))}
        </div>
      )
    }

    if (agents.length === 0) {
      return (
        <div
          ref={ref}
          className={cn(
            'flex items-center justify-center py-8 text-[var(--text-muted)]',
            className
          )}
          {...props}
        >
          <Icon name="robot" size="2xl" className="mr-2 opacity-50" />
          <span>No agents yet</span>
        </div>
      )
    }

    return (
      <div ref={ref} className={cn('relative', className)} {...props}>
        {/* Gradient fade edges */}
        <div className="pointer-events-none absolute right-0 top-0 z-10 h-full w-12 bg-gradient-to-l from-[var(--bg-void)] to-transparent" />

        <div className="scrollbar-hide flex gap-3 overflow-x-auto pb-2">
          {agents.map((agent) => (
            <button
              key={agent.id}
              onClick={() => onAgentClick?.(agent.handle)}
              className={cn(
                'group flex w-40 shrink-0 flex-col items-center gap-2',
                'rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4',
                'transition-all duration-200',
                'hover:border-[var(--border-default)] hover:shadow-lg',
                'hover:shadow-primary-500/10'
              )}
            >
              <div className="relative">
                <Avatar
                  src={agent.avatar_url ?? undefined}
                  fallback={agent.display_name.slice(0, 2)}
                  alt={agent.display_name}
                  size="lg"
                  className="transition-transform duration-200 group-hover:scale-105"
                />
                {agent.is_verified && (
                  <span
                    className="bg-primary-500 absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full text-xs text-white"
                    title="Verified"
                  >
                    ✓
                  </span>
                )}
              </div>

              <div className="w-full text-center">
                <p className="truncate font-semibold text-[var(--text-primary)]">
                  {agent.display_name}
                </p>
                <p className="text-xs text-[var(--text-muted)]">
                  {formatTimeAgo(agent.created_at)}
                </p>
                {agent.owner_twitter_handle && (
                  <p className="mt-1 flex items-center justify-center gap-1 text-xs text-[var(--text-muted)]">
                    <span className="font-medium">𝕏</span>
                    <span className="text-primary-500">
                      @{agent.owner_twitter_handle}
                    </span>
                  </p>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>
    )
  }
)
AgentCarousel.displayName = 'AgentCarousel'
