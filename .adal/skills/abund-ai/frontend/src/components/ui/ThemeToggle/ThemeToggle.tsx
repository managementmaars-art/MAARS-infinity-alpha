import { motion } from 'motion/react'
import { useTheme } from '../ThemeProvider'
import { cn } from '@/lib/utils'
import { type ComponentPropsWithoutRef, forwardRef } from 'react'

const SunIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="h-5 w-5"
    aria-hidden="true"
  >
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2" />
    <path d="M12 20v2" />
    <path d="m4.93 4.93 1.41 1.41" />
    <path d="m17.66 17.66 1.41 1.41" />
    <path d="M2 12h2" />
    <path d="M20 12h2" />
    <path d="m6.34 17.66-1.41 1.41" />
    <path d="m19.07 4.93-1.41 1.41" />
  </svg>
)

const MoonIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className="h-5 w-5"
    aria-hidden="true"
  >
    <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
  </svg>
)

export interface ThemeToggleProps extends Omit<
  ComponentPropsWithoutRef<'button'>,
  'children'
> {
  /** Size variant */
  size?: 'sm' | 'md' | 'lg'
}

const sizeStyles = {
  sm: 'h-8 w-8',
  md: 'h-10 w-10',
  lg: 'h-12 w-12',
}

/**
 * Animated toggle button for switching between light and dark themes
 * Features smooth icon morphing animation via Motion
 */
export const ThemeToggle = forwardRef<HTMLButtonElement, ThemeToggleProps>(
  ({ size = 'md', className, ...props }, ref) => {
    const { resolvedTheme, setTheme } = useTheme()
    const isDark = resolvedTheme === 'dark'

    const toggleTheme = () => {
      setTheme(isDark ? 'light' : 'dark')
    }

    return (
      <button
        ref={ref}
        type="button"
        onClick={toggleTheme}
        className={cn(
          'relative inline-flex items-center justify-center rounded-full',
          'bg-gray-100 dark:bg-gray-800',
          'hover:bg-gray-200 dark:hover:bg-gray-700',
          'transition-colors duration-200',
          'focus-visible:outline-none focus-visible:ring-2',
          'focus-visible:ring-primary-500 focus-visible:ring-offset-2',
          'dark:focus-visible:ring-offset-gray-900',
          sizeStyles[size],
          className
        )}
        aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        {...props}
      >
        <motion.div
          initial={false}
          animate={{
            scale: isDark ? 0 : 1,
            opacity: isDark ? 0 : 1,
            rotate: isDark ? -90 : 0,
          }}
          transition={{
            duration: 0.3,
            ease: [0.4, 0, 0.2, 1],
          }}
          className="absolute"
        >
          <SunIcon />
        </motion.div>
        <motion.div
          initial={false}
          animate={{
            scale: isDark ? 1 : 0,
            opacity: isDark ? 1 : 0,
            rotate: isDark ? 0 : 90,
          }}
          transition={{
            duration: 0.3,
            ease: [0.4, 0, 0.2, 1],
          }}
          className="absolute"
        >
          <MoonIcon />
        </motion.div>
      </button>
    )
  }
)
ThemeToggle.displayName = 'ThemeToggle'
