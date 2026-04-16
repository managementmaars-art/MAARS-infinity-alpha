import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn } from '@/lib/utils'

export interface PlatformStatsProps extends ComponentPropsWithoutRef<'div'> {
  /** Platform statistics */
  stats: {
    total_agents: number
    total_communities: number
    total_posts: number
    total_comments: number
  } | null
  /** Loading state */
  isLoading?: boolean
}

const statConfig = [
  {
    key: 'total_agents' as const,
    label: 'AI Agents',
    colorClass: 'text-primary-500',
  },
  {
    key: 'total_communities' as const,
    label: 'Communities',
    colorClass: 'text-violet-500',
  },
  {
    key: 'total_posts' as const,
    label: 'Posts',
    colorClass: 'text-pink-500',
  },
  {
    key: 'total_comments' as const,
    label: 'Comments',
    colorClass: 'text-amber-500',
  },
]

/**
 * Hero stats bar showing platform-wide metrics
 */
export const PlatformStats = forwardRef<HTMLDivElement, PlatformStatsProps>(
  ({ stats, isLoading = false, className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'flex flex-wrap items-center justify-center gap-6 py-6 md:gap-10',
          className
        )}
        {...props}
      >
        {statConfig.map(({ key, label, colorClass }) => (
          <div key={key} className="flex flex-col items-center">
            {isLoading || !stats ? (
              <div className="mb-1 h-8 w-20 animate-pulse rounded bg-[var(--bg-surface)]" />
            ) : (
              <span
                className={cn(
                  'text-2xl font-bold tabular-nums md:text-3xl',
                  colorClass
                )}
              >
                {formatNumber(stats[key])}
              </span>
            )}
            <span className="text-xs text-[var(--text-muted)] md:text-sm">
              {label}
            </span>
          </div>
        ))}
      </div>
    )
  }
)
PlatformStats.displayName = 'PlatformStats'

function formatNumber(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`
  return n.toLocaleString()
}
