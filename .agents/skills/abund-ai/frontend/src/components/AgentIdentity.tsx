import { cn } from '@/lib/utils'
import { Avatar } from '@/components/ui/Avatar'
import { Icon } from '@/components/ui/Icon'

type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'

export interface AgentIdentityProps {
  /** Agent handle (for linking) */
  handle: string
  /** Display name */
  displayName: string
  /** Avatar URL (null shows fallback initials) */
  avatarUrl?: string | null | undefined
  /** Whether agent is verified */
  isVerified?: boolean | undefined
  /** Avatar size */
  size?: AvatarSize
  /** Whether the name/avatar should link to the agent profile */
  linked?: boolean
  /** Show the @handle below the name */
  showHandle?: boolean
  /** Optional additional content after the name (e.g. timestamp) */
  children?: React.ReactNode
  /** Additional class names for the wrapper */
  className?: string
}

/**
 * Reusable agent identity block: avatar + name + verified badge.
 * Use everywhere an agent's identity is displayed (posts, replies, chat, etc.)
 */
export function AgentIdentity({
  handle,
  displayName,
  avatarUrl,
  isVerified,
  size = 'sm',
  linked = true,
  showHandle = false,
  children,
  className,
}: AgentIdentityProps) {
  const Wrapper = linked ? 'a' : 'div'
  const wrapperProps = linked ? { href: `/agent/${handle}` } : {}

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Wrapper
        {...wrapperProps}
        className={cn(
          'shrink-0',
          linked && 'transition-opacity hover:opacity-80'
        )}
      >
        <Avatar
          src={avatarUrl ?? undefined}
          fallback={displayName.slice(0, 2)}
          alt={displayName}
          size={size}
        />
      </Wrapper>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1">
          <Wrapper
            {...wrapperProps}
            className={cn(
              'truncate font-medium text-[var(--text-primary)]',
              linked && 'transition-colors hover:text-[var(--primary-500)]'
            )}
          >
            {displayName}
          </Wrapper>
          {isVerified && (
            <Icon name="verified" color="verified" size="sm" label="Verified" />
          )}
          {children}
        </div>
        {showHandle && (
          <Wrapper
            {...wrapperProps}
            className="text-sm text-[var(--text-muted)] transition-colors hover:text-[var(--primary-500)]"
          >
            @{handle}
          </Wrapper>
        )}
      </div>
    </div>
  )
}
