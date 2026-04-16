import { motion } from 'motion/react'
import { type ReactNode } from 'react'
import { useReducedMotion } from './useReducedMotion'
import { cn } from '@/lib/utils'

export interface StaggerItemProps {
  children: ReactNode
  /** Y offset for the slide effect */
  yOffset?: number
  /** Additional class names */
  className?: string
}

/**
 * Individual item to be used within StaggerChildren
 * Fades and slides in when parent orchestrates
 */
export function StaggerItem({
  children,
  yOffset = 15,
  className,
}: StaggerItemProps) {
  const prefersReducedMotion = useReducedMotion()

  const variants = {
    hidden: {
      opacity: 0,
      y: prefersReducedMotion ? 0 : yOffset,
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: prefersReducedMotion ? 0 : 0.4,
        ease: 'easeOut' as const,
      },
    },
  }

  return (
    <motion.div variants={variants} className={cn(className)}>
      {children}
    </motion.div>
  )
}
