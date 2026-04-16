import { motion, useSpring, useTransform } from 'motion/react'
import { useEffect } from 'react'
import { useReducedMotion } from './useReducedMotion'
import { cn } from '@/lib/utils'

export interface AnimatedNumberProps {
  /** Target value to animate to */
  value: number
  /** Animation duration in seconds */
  duration?: number
  /** Number of decimal places */
  decimals?: number
  /** Prefix (e.g., "$") */
  prefix?: string
  /** Suffix (e.g., "%", "K") */
  suffix?: string
  /** Additional class names */
  className?: string
}

/**
 * Animates a number from 0 to the target value
 * Great for stats, counters, and metrics
 */
export function AnimatedNumber({
  value,
  duration = 1,
  decimals = 0,
  prefix = '',
  suffix = '',
  className,
}: AnimatedNumberProps) {
  const prefersReducedMotion = useReducedMotion()

  const spring = useSpring(0, {
    duration: prefersReducedMotion ? 0 : duration * 1000,
    bounce: 0,
  })

  const display = useTransform(spring, (current) => {
    const formatted =
      decimals > 0
        ? current.toFixed(decimals)
        : Math.round(current).toLocaleString()
    return `${prefix}${formatted}${suffix}`
  })

  useEffect(() => {
    spring.set(value)
  }, [spring, value])

  return (
    <motion.span className={cn('tabular-nums', className)}>
      {display}
    </motion.span>
  )
}
