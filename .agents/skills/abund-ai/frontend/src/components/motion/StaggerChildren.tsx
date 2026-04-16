import { motion, type Transition } from 'motion/react'
import { type ReactNode } from 'react'
import { useReducedMotion } from './useReducedMotion'
import { cn } from '@/lib/utils'

export interface StaggerChildrenProps {
  children: ReactNode
  /** Delay between each child in seconds */
  staggerDelay?: number
  /** Initial delay before animations start */
  initialDelay?: number
  /** Additional class names */
  className?: string
}

/**
 * Container that staggers the animation of its children
 * Use with StaggerItem for child elements
 */
export function StaggerChildren({
  children,
  staggerDelay = 0.1,
  initialDelay = 0,
  className,
}: StaggerChildrenProps) {
  const prefersReducedMotion = useReducedMotion()

  const transition: Transition = prefersReducedMotion
    ? { staggerChildren: 0, delayChildren: 0 }
    : { staggerChildren: staggerDelay, delayChildren: initialDelay }

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: {
          transition,
        },
      }}
      custom={staggerDelay}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}
