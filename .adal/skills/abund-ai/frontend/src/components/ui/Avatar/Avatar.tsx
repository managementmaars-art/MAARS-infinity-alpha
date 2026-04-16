import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn } from '@/lib/utils'

const sizeStyles = {
  xs: 'h-6 w-6 text-xs',
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
  xl: 'h-16 w-16 text-xl',
  '2xl': 'h-24 w-24 text-2xl',
} as const

const statusColors = {
  online: 'bg-success-500',
  offline: 'bg-gray-400',
  busy: 'bg-error-500',
  away: 'bg-warning-500',
} as const

export interface AvatarProps extends ComponentPropsWithoutRef<'div'> {
  /** Image source */
  src?: string | undefined
  /** Alt text for the image */
  alt?: string | undefined
  /** Fallback initials (max 2 characters) */
  fallback?: string | undefined
  /** Size of the avatar */
  size?: keyof typeof sizeStyles | undefined
  /** Online status indicator */
  status?: keyof typeof statusColors | undefined
  /** Shape of the avatar */
  shape?: 'circle' | 'square' | undefined
  /** Animate status indicator with pulse (only for 'online' status) */
  pulse?: boolean | undefined
}

/**
 * Avatar component for displaying agent/user profile images
 *
 * @example
 * ```tsx
 * <Avatar
 *   src="/agent-avatar.png"
 *   alt="Agent Name"
 *   fallback="AN"
 *   status="online"
 *   pulse
 * />
 * ```
 */
export const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  (
    {
      src,
      alt,
      fallback,
      size = 'md',
      status,
      shape = 'circle',
      pulse = false,
      className,
      ...props
    },
    ref
  ) => {
    const initials = fallback?.slice(0, 2).toUpperCase()
    const shouldPulse = pulse && status === 'online'

    return (
      <div
        ref={ref}
        className={cn('relative inline-flex', className)}
        {...props}
      >
        <div
          className={cn(
            'flex items-center justify-center overflow-hidden',
            'bg-gray-200 dark:bg-gray-700',
            'font-medium text-gray-600 dark:text-gray-300',
            'transition-transform duration-200 hover:scale-105',
            sizeStyles[size],
            shape === 'circle' ? 'rounded-full' : 'rounded-lg'
          )}
        >
          {src ? (
            <img
              src={src}
              alt={alt ?? 'Avatar'}
              className="h-full w-full object-cover transition-opacity duration-300"
              loading="lazy"
            />
          ) : (
            <span aria-label={alt}>{initials}</span>
          )}
        </div>
        {status && (
          <span
            className={cn(
              'absolute bottom-0 right-0 block rounded-full ring-2 ring-white dark:ring-gray-900',
              statusColors[status],
              shouldPulse && 'animate-pulse-glow',
              // Size-responsive status indicator
              size === 'xs' && 'h-1.5 w-1.5',
              size === 'sm' && 'h-2 w-2',
              size === 'md' && 'h-2.5 w-2.5',
              size === 'lg' && 'h-3 w-3',
              size === 'xl' && 'h-4 w-4',
              size === '2xl' && 'h-5 w-5'
            )}
            aria-label={`Status: ${status}`}
          />
        )}
      </div>
    )
  }
)
Avatar.displayName = 'Avatar'

/**
 * Avatar group for displaying multiple avatars
 */
export interface AvatarGroupProps extends ComponentPropsWithoutRef<'div'> {
  /** Maximum avatars to show before +N */
  max?: number
  /** Size of avatars */
  size?: keyof typeof sizeStyles
  children: React.ReactNode
}

export const AvatarGroup = forwardRef<HTMLDivElement, AvatarGroupProps>(
  ({ max = 4, size = 'md', className, children, ...props }, ref) => {
    const childArray = Array.isArray(children) ? children : [children]
    const visibleAvatars = childArray.slice(0, max)
    const remainingCount = Math.max(0, childArray.length - max)

    return (
      <div ref={ref} className={cn('flex -space-x-2', className)} {...props}>
        {visibleAvatars}
        {remainingCount > 0 && (
          <div
            className={cn(
              'flex items-center justify-center',
              'bg-gray-100 dark:bg-gray-800',
              'font-medium text-gray-600 dark:text-gray-400',
              'ring-2 ring-white dark:ring-gray-900',
              sizeStyles[size],
              'rounded-full'
            )}
          >
            +{remainingCount}
          </div>
        )}
      </div>
    )
  }
)
AvatarGroup.displayName = 'AvatarGroup'
