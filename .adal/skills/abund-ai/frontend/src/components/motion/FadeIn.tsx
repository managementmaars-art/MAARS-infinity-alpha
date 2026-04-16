import { motion, type Transition } from 'motion/react'
import { type ReactNode } from 'react'
import { useReducedMotion } from './useReducedMotion'
import { cn } from '@/lib/utils'

export interface FadeInProps {
  children: ReactNode
  /** Initial Y offset in pixels */
  yOffset?: number
  /** Animation delay in seconds */
  delay?: number
  /** Animation duration in seconds */
  duration?: number
  /** Additional class names */
  className?: string
  /** Whether to animate (useful for conditional rendering) */
  animate?: boolean
}

/**
 * Fades in children with optional Y offset
 * Respects prefers-reduced-motion
 */
export function FadeIn({
  children,
  yOffset = 10,
  delay = 0,
  duration = 0.5,
  className,
  animate = true,
}: FadeInProps) {
  const prefersReducedMotion = useReducedMotion()

  const transition: Transition = prefersReducedMotion
    ? { duration: 0 }
    : {
        duration,
        delay,
        ease: [0.4, 0, 0.2, 1],
      }

  return (
    <motion.div
      initial={
        animate ? { opacity: 0, y: prefersReducedMotion ? 0 : yOffset } : false
      }
      animate={{ opacity: 1, y: 0 }}
      transition={transition}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}
