import { useState, useEffect, useCallback, useRef } from 'react'

interface UsePollingOptions {
  /** Function that returns the current version string from the API */
  fetchVersion: () => Promise<string>
  /** Callback when a new version is detected */
  onNewVersion: () => void
  /** Poll interval in seconds (default: 10) */
  intervalSeconds?: number
  /** Whether polling is enabled (default: true) */
  enabled?: boolean
}

interface UsePollingReturn {
  /** Seconds remaining until the next poll */
  secondsUntilRefresh: number
  /** Whether we're currently checking the version */
  isChecking: boolean
  /** When data was last refreshed (null initially) */
  lastUpdated: Date | null
  /** Trigger an immediate refresh */
  refreshNow: () => void
}

/**
 * Smart polling hook that checks a lightweight version endpoint
 * and triggers a callback when new content is detected.
 *
 * The hook maintains a countdown timer for UI display and supports
 * manual refresh via `refreshNow()`.
 */
export function usePolling({
  fetchVersion,
  onNewVersion,
  intervalSeconds = 10,
  enabled = true,
}: UsePollingOptions): UsePollingReturn {
  const [secondsUntilRefresh, setSecondsUntilRefresh] =
    useState(intervalSeconds)
  const [isChecking, setIsChecking] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  // Refs to keep stable references across renders
  const lastKnownVersion = useRef<string | null>(null)
  const fetchVersionRef = useRef(fetchVersion)
  const onNewVersionRef = useRef(onNewVersion)

  // Keep refs in sync with latest props
  useEffect(() => {
    fetchVersionRef.current = fetchVersion
  }, [fetchVersion])

  useEffect(() => {
    onNewVersionRef.current = onNewVersion
  }, [onNewVersion])

  const checkVersion = useCallback(async () => {
    setIsChecking(true)
    try {
      const version = await fetchVersionRef.current()

      if (
        lastKnownVersion.current !== null &&
        version !== lastKnownVersion.current
      ) {
        // Version changed — trigger refresh
        onNewVersionRef.current()
        setLastUpdated(new Date())
      }

      lastKnownVersion.current = version
    } catch {
      // Silently fail — don't break the page if version check fails
    } finally {
      setIsChecking(false)
    }
  }, [])

  const refreshNow = useCallback(() => {
    // Force a refresh regardless of version
    onNewVersionRef.current()
    setLastUpdated(new Date())
    setSecondsUntilRefresh(intervalSeconds)
    // Also re-sync the version so the next poll doesn't double-fire
    void checkVersion()
  }, [intervalSeconds, checkVersion])

  // Countdown timer + poll trigger
  useEffect(() => {
    if (!enabled) return

    // Initial version fetch (seed the lastKnownVersion without triggering refresh)
    void checkVersion()

    const timer = setInterval(() => {
      setSecondsUntilRefresh((prev) => {
        if (prev <= 1) {
          // Time to poll
          void checkVersion()
          return intervalSeconds
        }
        return prev - 1
      })
    }, 1000)

    return () => {
      clearInterval(timer)
    }
  }, [enabled, intervalSeconds, checkVersion])

  return {
    secondsUntilRefresh,
    isChecking,
    lastUpdated,
    refreshNow,
  }
}
