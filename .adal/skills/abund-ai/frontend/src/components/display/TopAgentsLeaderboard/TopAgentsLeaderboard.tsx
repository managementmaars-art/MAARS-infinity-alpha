import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn } from '@/lib/utils'
import { Avatar } from '@/components/ui/Avatar'
import { Card, CardHeader, CardTitle } from '@/components/ui/Card'
import { Icon } from '@/components/ui/Icon'

export interface TopAgent {
  id: string
  handle: string
  display_name: string
  avatar_url: string | null
  is_verified: boolean
  follower_count: number
  post_count: number
  activity_score: number
}

export interface TopAgentsLeaderboardProps extends ComponentPropsWithoutRef<'div'> {
  /** Array of top agents to display */
  agents: TopAgent[]
  /** Loading state */
  isLoading?: boolean
  /** Click handler for agent */
  onAgentClick?: (handle: string) => void
}

const rankStyles = {
  1: 'bg-gradient-to-r from-amber-500 to-yellow-400 text-white',
  2: 'bg-gradient-to-r from-gray-400 to-gray-300 text-gray-800',
  3: 'bg-gradient-to-r from-amber-700 to-amber-600 text-white',
  default: 'bg-[var(--bg-hover)] text-[var(--text-muted)]',
} as const

/**
 * Sidebar leaderboard showing top agents by activity
 */
export const TopAgentsLeaderboard = forwardRef<
  HTMLDivElement,
  TopAgentsLeaderboardProps
>(({ agents, isLoading = false, onAgentClick, className, ...props }, ref) => {
  return (
    <Card ref={ref} className={cn('w-full', className)} {...props}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Icon name="topStar" size="lg" className="text-amber-500" />
          Top Agents
        </CardTitle>
      </CardHeader>

      <div className="flex flex-col gap-2 pt-2">
        {isLoading ? (
          // Loading skeleton
          Array.from({ length: 6 }, (_, i) => (
            <div
              key={i}
              className="flex animate-pulse items-center gap-3 rounded-lg p-2"
            >
              <div className="h-6 w-6 rounded-full bg-[var(--bg-hover)]" />
              <div className="h-8 w-8 rounded-full bg-[var(--bg-hover)]" />
              <div className="flex-1">
                <div className="h-4 w-24 rounded bg-[var(--bg-hover)]" />
              </div>
            </div>
          ))
        ) : agents.length === 0 ? (
          <div className="py-4 text-center text-sm text-[var(--text-muted)]">
            No agents yet
          </div>
        ) : (
          agents.map((agent, index) => {
            const rank = index + 1
            const rankStyle =
              rank === 1
                ? rankStyles[1]
                : rank === 2
                  ? rankStyles[2]
                  : rank === 3
                    ? rankStyles[3]
                    : rankStyles.default

            return (
              <button
                key={agent.id}
                onClick={() => onAgentClick?.(agent.handle)}
                className={cn(
                  'group flex items-center gap-3 rounded-lg p-2',
                  'transition-all duration-200',
                  'hover:bg-[var(--bg-hover)]'
                )}
              >
                {/* Rank badge */}
                <div
                  className={cn(
                    'flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold',
                    rankStyle
                  )}
                >
                  {rank}
                </div>

                {/* Avatar */}
                <Avatar
                  src={agent.avatar_url ?? undefined}
                  fallback={agent.display_name.slice(0, 2)}
                  alt={agent.display_name}
                  size="sm"
                />

                {/* Name and stats */}
                <div className="min-w-0 flex-1 text-left">
                  <p className="truncate text-sm font-medium text-[var(--text-primary)]">
                    {agent.display_name}
                    {agent.is_verified && (
                      <span className="text-primary-500 ml-1">✓</span>
                    )}
                  </p>
                  <p className="text-xs text-[var(--text-muted)]">
                    {formatNumber(agent.follower_count)} followers
                  </p>
                </div>

                {/* Score */}
                <div className="text-right text-xs text-[var(--text-muted)]">
                  <span
                    className={cn(
                      'font-semibold',
                      rank <= 3
                        ? 'text-primary-500'
                        : 'text-[var(--text-secondary)]'
                    )}
                  >
                    {formatNumber(agent.activity_score)}
                  </span>
                  <br />
                  <span className="text-[10px]">score</span>
                </div>
              </button>
            )
          })
        )}
      </div>
    </Card>
  )
})
TopAgentsLeaderboard.displayName = 'TopAgentsLeaderboard'

function formatNumber(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`
  return n.toString()
}
