import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn } from '@/lib/utils'

const sizeStyles = {
  xs: 'h-3 w-3',
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
  xl: 'h-12 w-12',
} as const

export interface SpinnerProps extends ComponentPropsWithoutRef<'svg'> {
  /** Size of the spinner */
  size?: keyof typeof sizeStyles
  /** Accessible label */
  label?: string
}

/**
 * Loading spinner with smooth animation
 *
 * @example
 * ```tsx
 * <Spinner size="md" label="Loading posts..." />
 * ```
 */
export const Spinner = forwardRef<SVGSVGElement, SpinnerProps>(
  ({ size = 'md', label = 'Loading', className, ...props }, ref) => {
    return (
      <svg
        ref={ref}
        className={cn('animate-spin text-current', sizeStyles[size], className)}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        role="status"
        aria-label={label}
        {...props}
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
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    )
  }
)
Spinner.displayName = 'Spinner'

/**
 * Full-screen loading overlay
 */
export interface LoadingOverlayProps extends ComponentPropsWithoutRef<'div'> {
  /** Loading message */
  message?: string
  /** Show overlay */
  show?: boolean
}

export const LoadingOverlay = forwardRef<HTMLDivElement, LoadingOverlayProps>(
  ({ message = 'Loading...', show = true, className, ...props }, ref) => {
    if (!show) return null

    return (
      <div
        ref={ref}
        className={cn(
          'fixed inset-0 z-50',
          'flex flex-col items-center justify-center gap-4',
          'bg-white/80 backdrop-blur-sm dark:bg-gray-950/80',
          className
        )}
        role="alert"
        aria-busy="true"
        aria-live="polite"
        {...props}
      >
        <Spinner size="xl" />
        <p className="font-medium text-gray-600 dark:text-gray-400">
          {message}
        </p>
      </div>
    )
  }
)
LoadingOverlay.displayName = 'LoadingOverlay'
