import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn } from '@/lib/utils'

const variantStyles = {
  primary: [
    'bg-primary-500 text-white',
    'hover:bg-primary-600',
    'active:bg-primary-700',
  ].join(' '),
  secondary: [
    'bg-[var(--bg-hover)] text-[var(--text-primary)]',
    'hover:bg-[var(--bg-elevated)]',
    'active:bg-[var(--bg-surface)]',
  ].join(' '),
  ghost: [
    'bg-transparent text-[var(--text-secondary)]',
    'hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]',
    'active:bg-[var(--bg-elevated)]',
  ].join(' '),
  danger: [
    'bg-error-500 text-white',
    'hover:bg-error-600',
    'active:bg-error-600',
  ].join(' '),
} as const

const sizeStyles = {
  sm: 'h-8 px-3 text-sm gap-1.5 rounded-md',
  md: 'h-10 px-4 text-sm gap-2 rounded-lg',
  lg: 'h-12 px-6 text-base gap-2.5 rounded-lg',
} as const

export interface ButtonProps extends ComponentPropsWithoutRef<'button'> {
  /** Visual style variant */
  variant?: keyof typeof variantStyles
  /** Size of the button */
  size?: keyof typeof sizeStyles
  /** Full width button */
  fullWidth?: boolean
  /** Loading state */
  isLoading?: boolean
}

/**
 * Primary UI component for user interaction
 *
 * @example
 * ```tsx
 * <Button variant="primary" onClick={handleClick}>
 *   Click me
 * </Button>
 * ```
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      fullWidth = false,
      isLoading = false,
      className,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled ?? isLoading}
        aria-busy={isLoading}
        className={cn(
          // Base styles
          'inline-flex items-center justify-center font-medium',
          'transition-all duration-150',
          // Scale effects for "living" feel
          'hover:scale-[1.02] active:scale-[0.98]',
          // Focus styles for a11y
          'focus-visible:outline-none focus-visible:ring-2',
          'focus-visible:ring-primary-500 focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg-void)]',
          // Disabled styles
          'disabled:pointer-events-none disabled:opacity-50',
          // Variant & size
          variantStyles[variant],
          sizeStyles[size],
          // Width
          fullWidth && 'w-full',
          className
        )}
        {...props}
      >
        {isLoading ? (
          <>
            <svg
              className="h-4 w-4 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            <span className="sr-only">Loading</span>
            {children}
          </>
        ) : (
          children
        )}
      </button>
    )
  }
)
Button.displayName = 'Button'
