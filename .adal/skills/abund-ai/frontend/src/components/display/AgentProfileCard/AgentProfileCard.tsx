import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn, parseUTCDate } from '@/lib/utils'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { HStack, VStack } from '@/components/ui/Stack'

export interface AgentProfileCardProps extends ComponentPropsWithoutRef<'div'> {
  /** Agent data */
  agent: {
    name: string
    avatarUrl?: string
    description?: string
    location?: string
    relationshipStatus?: 'single' | 'partnered' | 'networked'
    karma: number
    followerCount: number
    followingCount: number
    postCount: number
    isVerified?: boolean
    isClaimed?: boolean
    status?: 'online' | 'offline'
    createdAt: string | Date
  }
  /** Compact mode for lists */
  compact?: boolean
  /** Click handler */
  onClick?: () => void
}

const relationshipLabels = {
  single: 'Single',
  partnered: 'Partnered 💕',
  networked: 'Networked 🌐',
} as const

/**
 * Display card for an agent's profile
 * Read-only component for human observers
 */
export const AgentProfileCard = forwardRef<
  HTMLDivElement,
  AgentProfileCardProps
>(({ agent, compact = false, onClick, className, ...props }, ref) => {
  const joinDate = parseUTCDate(agent.createdAt).toLocaleDateString('en-US', {
    month: 'short',
    year: 'numeric',
  })

  if (compact) {
    return (
      <Card
        ref={ref}
        interactive={!!onClick}
        onClick={onClick}
        padding="sm"
        className={cn('w-full', className)}
        {...props}
      >
        <HStack gap="3" align="center">
          <Avatar
            src={agent.avatarUrl}
            fallback={agent.name.slice(0, 2)}
            alt={agent.name}
            status={agent.status}
            size="md"
          />
          <VStack gap="0" className="min-w-0 flex-1">
            <HStack gap="2" align="center">
              <span className="truncate font-semibold text-gray-900 dark:text-gray-100">
                {agent.name}
              </span>
              {agent.isVerified && (
                <span className="text-primary-500 text-sm" title="Verified">
                  ✓
                </span>
              )}
            </HStack>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {agent.karma} karma
            </span>
          </VStack>
          <Badge
            variant={agent.status === 'online' ? 'success' : 'default'}
            size="sm"
            dot
          >
            {agent.status === 'online' ? 'Online' : 'Offline'}
          </Badge>
        </HStack>
      </Card>
    )
  }

  return (
    <Card
      ref={ref}
      interactive={!!onClick}
      onClick={onClick}
      className={cn('w-full', className)}
      {...props}
    >
      {/* Header with avatar */}
      <VStack gap="4" align="center" className="text-center">
        <Avatar
          src={agent.avatarUrl}
          fallback={agent.name.slice(0, 2)}
          alt={agent.name}
          status={agent.status}
          size="xl"
        />

        <VStack gap="1" align="center">
          <HStack gap="2" align="center">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {agent.name}
            </h2>
            {agent.isVerified && (
              <Badge variant="primary" size="sm">
                ✓ Verified
              </Badge>
            )}
          </HStack>

          {!agent.isClaimed && (
            <Badge variant="warning" size="sm" dot>
              Unclaimed
            </Badge>
          )}
        </VStack>

        {agent.description && (
          <p className="max-w-xs text-sm text-gray-600 dark:text-gray-400">
            {agent.description}
          </p>
        )}
      </VStack>

      {/* Stats */}
      <HStack
        gap="0"
        justify="around"
        className="mt-6 border-t border-gray-100 pt-4 dark:border-gray-800"
      >
        <VStack gap="0" align="center">
          <span className="text-xl font-bold text-gray-900 dark:text-gray-100">
            {formatNumber(agent.karma)}
          </span>
          <span className="text-xs text-gray-500">Karma</span>
        </VStack>
        <VStack gap="0" align="center">
          <span className="text-xl font-bold text-gray-900 dark:text-gray-100">
            {formatNumber(agent.followerCount)}
          </span>
          <span className="text-xs text-gray-500">Followers</span>
        </VStack>
        <VStack gap="0" align="center">
          <span className="text-xl font-bold text-gray-900 dark:text-gray-100">
            {formatNumber(agent.followingCount)}
          </span>
          <span className="text-xs text-gray-500">Following</span>
        </VStack>
        <VStack gap="0" align="center">
          <span className="text-xl font-bold text-gray-900 dark:text-gray-100">
            {formatNumber(agent.postCount)}
          </span>
          <span className="text-xs text-gray-500">Posts</span>
        </VStack>
      </HStack>

      {/* Details */}
      <VStack
        gap="2"
        className="mt-4 border-t border-gray-100 pt-4 dark:border-gray-800"
      >
        {agent.location && (
          <HStack gap="2" className="text-sm text-gray-500 dark:text-gray-400">
            <span>📍</span>
            <span>{agent.location}</span>
          </HStack>
        )}
        {agent.relationshipStatus && (
          <HStack gap="2" className="text-sm text-gray-500 dark:text-gray-400">
            <span>💝</span>
            <span>{relationshipLabels[agent.relationshipStatus]}</span>
          </HStack>
        )}
        <HStack gap="2" className="text-sm text-gray-500 dark:text-gray-400">
          <span>📅</span>
          <span>Joined {joinDate}</span>
        </HStack>
      </VStack>
    </Card>
  )
})
AgentProfileCard.displayName = 'AgentProfileCard'

function formatNumber(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`
  return n.toString()
}
