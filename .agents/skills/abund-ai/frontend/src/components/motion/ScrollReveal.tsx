import { motion, useInView } from 'motion/react'
import { useRef, type ReactNode } from 'react'
import { useReducedMotion } from './useReducedMotion'
import { cn } from '@/lib/utils'

export interface ScrollRevealProps {
  children: ReactNode
  /** Y offset for the slide effect */
  yOffset?: number
  /** Animation duration in seconds */
  duration?: number
  /** Delay before animation starts */
  delay?: number
  /** Trigger threshold (0-1) */
  threshold?: number
  /** Whether to animate only once */
  once?: boolean
  /** Additional class names */
  className?: string
}

/**
 * Reveals children when they scroll into view
 * Uses IntersectionObserver for performance
 */
export function ScrollReveal({
  children,
  yOffset = 30,
  duration = 0.6,
  delay = 0,
  threshold = 0.1,
  once = true,
  className,
}: ScrollRevealProps) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, {
    once,
    amount: threshold,
  })
  const prefersReducedMotion = useReducedMotion()

  return (
    <motion.div
      ref={ref}
      initial={{
        opacity: 0,
        y: prefersReducedMotion ? 0 : yOffset,
      }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={
        prefersReducedMotion
          ? { duration: 0 }
          : {
              duration,
              delay,
              ease: [0.4, 0, 0.2, 1],
            }
      }
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}
