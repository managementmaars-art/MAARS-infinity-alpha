import { motion } from 'motion/react'
import { type ReactNode } from 'react'
import { useReducedMotion } from './useReducedMotion'
import { cn } from '@/lib/utils'

export interface PulseProps {
  children: ReactNode
  /** Pulse color (CSS color value) */
  color?: string
  /** Whether to pulse */
  active?: boolean
  /** Additional class names */
  className?: string
}

/**
 * Adds a gentle pulsing glow effect around children
 * Great for status indicators and attention-grabbing elements
 */
export function Pulse({
  children,
  color = 'oklch(0.65 0.18 145)',
  active = true,
  className,
}: PulseProps) {
  const prefersReducedMotion = useReducedMotion()

  if (!active || prefersReducedMotion) {
    return <div className={cn(className)}>{children}</div>
  }

  return (
    <motion.div
      animate={{
        boxShadow: [
          `0 0 0 0 ${color.replace(')', ' / 0.4)')}`,
          `0 0 0 8px ${color.replace(')', ' / 0)')}`,
          `0 0 0 0 ${color.replace(')', ' / 0)')}`,
        ],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
      className={cn('rounded-full', className)}
    >
      {children}
    </motion.div>
  )
}
