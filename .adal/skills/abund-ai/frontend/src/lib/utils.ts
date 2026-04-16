import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merges Tailwind CSS classes with proper precedence handling
 * Uses clsx for conditional classes and tailwind-merge for deduplication
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}

/**
 * Parse a UTC date string from the database
 * Database stores dates like "2026-02-03 23:38:19" in UTC without timezone indicator
 */
export function parseUTCDate(date: string | Date): Date {
  if (date instanceof Date) {
    return date
  }

  // Replace space with T and append Z if not present
  let isoString = date.replace(' ', 'T')
  if (
    !isoString.endsWith('Z') &&
    !isoString.includes('+') &&
    !isoString.includes('-', 10)
  ) {
    isoString += 'Z'
  }
  return new Date(isoString)
}

/**
 * Format a date as relative time (e.g., "5m ago", "2h ago")
 */
export function formatTimeAgo(date: string | Date): string {
  const now = new Date()
  const then = parseUTCDate(date)
  const seconds = Math.floor((now.getTime() - then.getTime()) / 1000)

  // Handle future dates (shouldn't happen, but just in case)
  if (seconds < 0) {
    return 'just now'
  }

  if (seconds < 60) return 'just now'
  if (seconds < 3600) return `${String(Math.floor(seconds / 60))}m ago`
  if (seconds < 86400) return `${String(Math.floor(seconds / 3600))}h ago`
  if (seconds < 604800) return `${String(Math.floor(seconds / 86400))}d ago`

  return then.toLocaleDateString()
}

/**
 * Get online status based on last_active_at
 * Online = active within last 15 minutes
 */
export function getOnlineStatus(
  lastActiveAt: string | null | undefined
): 'online' | 'offline' {
  if (!lastActiveAt) return 'offline'

  const lastActive = parseUTCDate(lastActiveAt)
  const now = new Date()
  const minutesAgo = (now.getTime() - lastActive.getTime()) / (1000 * 60)

  return minutesAgo <= 15 ? 'online' : 'offline'
}

/**
 * Format last seen time for display
 */
export function formatLastSeen(
  lastActiveAt: string | null | undefined
): string {
  if (!lastActiveAt) return 'Never active'

  const lastActive = parseUTCDate(lastActiveAt)
  const now = new Date()
  const minutesAgo = Math.floor(
    (now.getTime() - lastActive.getTime()) / (1000 * 60)
  )

  if (minutesAgo < 1) return 'Active now'
  if (minutesAgo < 15) return 'Active now'
  if (minutesAgo < 60) return `Last seen ${String(minutesAgo)}m ago`
  if (minutesAgo < 1440)
    return `Last seen ${String(Math.floor(minutesAgo / 60))}h ago`
  if (minutesAgo < 10080)
    return `Last seen ${String(Math.floor(minutesAgo / 1440))}d ago`

  return `Last seen ${lastActive.toLocaleDateString()}`
}
