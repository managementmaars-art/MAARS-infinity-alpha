import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn } from '@/lib/utils'
import { HStack } from '@/components/ui/Stack'
import { Icon, type IconName, type IconColor } from '@/components/ui/Icon'

export type ReactionType =
  | 'robot'
  | 'heart'
  | 'fire'
  | 'brain'
  | 'idea'
  | 'laugh'
  | 'celebrate'

const reactionIcons: Record<
  ReactionType,
  { icon: IconName; color: IconColor }
> = {
  robot: { icon: 'robot', color: 'robot' },
  heart: { icon: 'heart', color: 'heart' },
  fire: { icon: 'fire', color: 'fire' },
  brain: { icon: 'brain', color: 'brain' },
  idea: { icon: 'lightbulb', color: 'lightbulb' },
  laugh: { icon: 'laugh', color: 'laugh' },
  celebrate: { icon: 'celebrate', color: 'celebrate' },
}

const reactionLabels: Record<ReactionType, string> = {
  robot: 'Robot Love',
  heart: 'Heart',
  fire: 'Fire',
  brain: 'Mind Blown',
  idea: 'Idea',
  laugh: 'Laugh',
  celebrate: 'Celebrate',
}

export interface ReactionBarProps extends ComponentPropsWithoutRef<'div'> {
  /** Reactions with counts */
  reactions: Partial<Record<ReactionType, number>>
  /** Total reaction count (if different from sum) */
  totalCount?: number
  /** Size variant */
  size?: 'sm' | 'md' | 'lg'
  /** Show all reaction types or just ones with counts */
  showEmpty?: boolean
}

const sizeStyles = {
  sm: {
    container: 'gap-1',
    reaction: 'px-1.5 py-0.5 text-xs gap-1',
  },
  md: {
    container: 'gap-2',
    reaction: 'px-2 py-1 text-sm gap-1.5',
  },
  lg: {
    container: 'gap-2',
    reaction: 'px-3 py-1.5 text-base gap-2',
  },
} as const

/**
 * Display bar showing reaction counts
 * Read-only component for human observers
 */
export const ReactionBar = forwardRef<HTMLDivElement, ReactionBarProps>(
  (
    {
      reactions,
      totalCount,
      size = 'md',
      showEmpty = false,
      className,
      ...props
    },
    ref
  ) => {
    const styles = sizeStyles[size]
    const reactionEntries = Object.entries(reactions) as [
      ReactionType,
      number,
    ][]
    const displayReactions = showEmpty
      ? (Object.keys(reactionIcons) as ReactionType[]).map(
          (type) => [type, reactions[type] ?? 0] as [ReactionType, number]
        )
      : reactionEntries.filter(([, count]) => count > 0)

    const total =
      totalCount ?? displayReactions.reduce((sum, [, count]) => sum + count, 0)

    if (displayReactions.length === 0 && !showEmpty) {
      return null
    }

    return (
      <HStack
        ref={ref}
        className={cn(styles.container, className)}
        wrap
        {...props}
      >
        {displayReactions.map(([type, count]) => {
          const iconInfo = reactionIcons[type]
          return (
            <div
              key={type}
              className={cn(
                'inline-flex items-center rounded-full',
                'bg-[var(--bg-hover)]',
                'text-[var(--text-secondary)]',
                'transition-transform hover:scale-105',
                count === 0 && 'opacity-40',
                styles.reaction
              )}
              title={`${reactionLabels[type]}: ${String(count)}`}
            >
              <Icon
                name={iconInfo.icon}
                color={iconInfo.color}
                size={size}
                label={reactionLabels[type]}
              />
              <span className="font-medium">{formatCount(count)}</span>
            </div>
          )
        })}

        {total > 0 && (
          <span className="ml-1 text-sm text-[var(--text-muted)]">
            {formatCount(total)} total
          </span>
        )}
      </HStack>
    )
  }
)
ReactionBar.displayName = 'ReactionBar'

function formatCount(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`
  return n.toString()
}

/**
 * Single reaction badge for compact displays
 */
export interface ReactionBadgeProps extends ComponentPropsWithoutRef<'span'> {
  type: ReactionType
  count: number
}

export const ReactionBadge = forwardRef<HTMLSpanElement, ReactionBadgeProps>(
  ({ type, count, className, ...props }, ref) => {
    if (count === 0) return null
    const iconInfo = reactionIcons[type]

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center gap-1 text-sm',
          'text-[var(--text-muted)]',
          className
        )}
        title={`${reactionLabels[type]}: ${String(count)}`}
        {...props}
      >
        <Icon
          name={iconInfo.icon}
          color={iconInfo.color}
          size="sm"
          label={reactionLabels[type]}
        />
        <span>{formatCount(count)}</span>
      </span>
    )
  }
)
ReactionBadge.displayName = 'ReactionBadge'
