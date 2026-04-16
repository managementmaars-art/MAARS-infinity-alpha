import { motion, type Transition } from 'motion/react'
import { type ReactNode } from 'react'
import { useReducedMotion } from './useReducedMotion'
import { cn } from '@/lib/utils'

type Direction = 'left' | 'right' | 'up' | 'down'

export interface SlideInProps {
  children: ReactNode
  /** Direction to slide from */
  direction?: Direction
  /** Slide distance in pixels */
  distance?: number
  /** Animation delay in seconds */
  delay?: number
  /** Animation duration in seconds */
  duration?: number
  /** Additional class names */
  className?: string
}

const getInitialPosition = (direction: Direction, distance: number) => {
  switch (direction) {
    case 'left':
      return { x: -distance, y: 0 }
    case 'right':
      return { x: distance, y: 0 }
    case 'up':
      return { x: 0, y: -distance }
    case 'down':
      return { x: 0, y: distance }
  }
}

/**
 * Slides in children from a specified direction
 * Respects prefers-reduced-motion
 */
export function SlideIn({
  children,
  direction = 'down',
  distance = 20,
  delay = 0,
  duration = 0.5,
  className,
}: SlideInProps) {
  const prefersReducedMotion = useReducedMotion()

  const initial = prefersReducedMotion
    ? { opacity: 0, x: 0, y: 0 }
    : { opacity: 0, ...getInitialPosition(direction, distance) }

  const transition: Transition = prefersReducedMotion
    ? { duration: 0 }
    : {
        duration,
        delay,
        ease: [0.4, 0, 0.2, 1],
      }

  return (
    <motion.div
      initial={initial}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={transition}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}
