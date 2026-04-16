import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn } from '@/lib/utils'

const variantStyles = {
  default: 'bg-[var(--bg-hover)] text-[var(--text-primary)]',
  primary: 'bg-primary-500/20 text-primary-400',
  success: 'bg-success-500/20 text-success-400',
  warning: 'bg-warning-500/20 text-warning-400',
  error: 'bg-error-500/20 text-error-400',
  info: 'bg-info-500/20 text-info-400',
} as const

const sizeStyles = {
  sm: 'px-1.5 py-0.5 text-xs',
  md: 'px-2 py-0.5 text-xs',
  lg: 'px-2.5 py-1 text-sm',
} as const

export interface BadgeProps extends ComponentPropsWithoutRef<'span'> {
  /** Color variant */
  variant?: keyof typeof variantStyles
  /** Size */
  size?: keyof typeof sizeStyles
  /** Dot indicator */
  dot?: boolean
  /** Remove button callback */
  onRemove?: () => void
}

/**
 * Badge component for labels, tags, and status indicators
 *
 * @example
 * ```tsx
 * <Badge variant="success">Online</Badge>
 * <Badge variant="primary" dot>Active</Badge>
 * ```
 */
export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      variant = 'default',
      size = 'md',
      dot = false,
      onRemove,
      className,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center gap-1.5 rounded-full font-medium',
          'transition-transform duration-150 hover:scale-105',
          'animate-scale-in',
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      >
        {dot && (
          <span
            className={cn(
              'h-1.5 w-1.5 rounded-full',
              variant === 'default' && 'bg-gray-500',
              variant === 'primary' && 'bg-primary-500',
              variant === 'success' && 'bg-success-500',
              variant === 'warning' && 'bg-warning-500',
              variant === 'error' && 'bg-error-500',
              variant === 'info' && 'bg-info-500'
            )}
            aria-hidden="true"
          />
        )}
        {children}
        {onRemove && (
          <button
            type="button"
            onClick={onRemove}
            className={cn(
              '-mr-0.5 ml-0.5 inline-flex items-center justify-center',
              'h-4 w-4 rounded-full',
              'hover:bg-black/10 dark:hover:bg-white/10',
              'focus:outline-none focus:ring-2 focus:ring-offset-1'
            )}
            aria-label="Remove"
          >
            <svg
              className="h-3 w-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </span>
    )
  }
)
Badge.displayName = 'Badge'
