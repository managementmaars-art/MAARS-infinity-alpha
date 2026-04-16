import { cn } from '@/lib/utils'
import { useReducedMotion } from './useReducedMotion'

export interface ShimmerProps {
  /** Width of the shimmer element */
  width?: string | number
  /** Height of the shimmer element */
  height?: string | number
  /** Border radius */
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full'
  /** Additional class names */
  className?: string
}

const radiusMap = {
  none: 'rounded-none',
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  full: 'rounded-full',
}

/**
 * Shimmer loading placeholder with animated gradient
 * Uses CSS animation for better performance
 */
export function Shimmer({
  width = '100%',
  height = '1rem',
  rounded = 'md',
  className,
}: ShimmerProps) {
  const prefersReducedMotion = useReducedMotion()

  const style = {
    width: typeof width === 'number' ? `${String(width)}px` : width,
    height: typeof height === 'number' ? `${String(height)}px` : height,
  }

  return (
    <div
      className={cn(
        radiusMap[rounded],
        prefersReducedMotion
          ? 'bg-gray-200 dark:bg-gray-700'
          : 'animate-shimmer',
        className
      )}
      style={style}
      aria-hidden="true"
    />
  )
}
