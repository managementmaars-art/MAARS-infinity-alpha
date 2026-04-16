import { useCallback, useEffect, useRef } from 'react'
import { Icon } from '@/components/ui/Icon/Icon'
import { cn } from '@/lib/utils'

interface LiveIndicatorProps {
  /** Seconds remaining until the next auto-refresh */
  secondsUntilRefresh: number
  /** Total interval duration in seconds */
  intervalSeconds: number
  /** Whether a version check is in progress */
  isChecking: boolean
  /** Trigger an immediate refresh */
  onRefresh: () => void
  /** Additional class names */
  className?: string
}

const RING_SIZE = 20
const RING_STROKE = 2.5
const RING_RADIUS = (RING_SIZE - RING_STROKE) / 2
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS

/**
 * Compact live-status indicator with a circular countdown ring,
 * a "LIVE" label, and a manual refresh button.
 *
 * Designed to sit inline next to sort controls or page headers.
 */
export function LiveIndicator({
  secondsUntilRefresh,
  intervalSeconds,
  isChecking,
  onRefresh,
  className,
}: LiveIndicatorProps) {
  const progress = secondsUntilRefresh / intervalSeconds
  const dashOffset = RING_CIRCUMFERENCE * (1 - progress)

  // Glow on refresh (flash animation)
  const pillRef = useRef<HTMLDivElement>(null)
  const prevSeconds = useRef(secondsUntilRefresh)

  const flashGlow = useCallback(() => {
    const el = pillRef.current
    if (!el) return
    el.classList.add('live-indicator-flash')
    const handler = () => {
      el.classList.remove('live-indicator-flash')
    }
    el.addEventListener('animationend', handler, { once: true })
  }, [])

  // Detect when the countdown resets (new data arrived)
  useEffect(() => {
    if (secondsUntilRefresh > prevSeconds.current && prevSeconds.current <= 1) {
      flashGlow()
    }
    prevSeconds.current = secondsUntilRefresh
  }, [secondsUntilRefresh, flashGlow])

  return (
    <>
      {/* Inline keyframes for the flash animation */}
      <style>{`
        @keyframes live-flash {
          0% { box-shadow: 0 0 0 0 oklch(0.65 0.18 145 / 0.5); }
          50% { box-shadow: 0 0 12px 4px oklch(0.65 0.18 145 / 0.3); }
          100% { box-shadow: 0 0 0 0 oklch(0.65 0.18 145 / 0); }
        }
        .live-indicator-flash {
          animation: live-flash 0.6s ease-out;
        }
      `}</style>

      <div
        ref={pillRef}
        className={cn(
          'inline-flex items-center gap-1.5 rounded-full',
          'border border-white/10 bg-white/5 backdrop-blur-sm',
          'select-none px-2.5 py-1 text-xs',
          className
        )}
      >
        {/* Countdown ring */}
        <svg
          width={RING_SIZE}
          height={RING_SIZE}
          className="shrink-0 -rotate-90"
          aria-hidden="true"
        >
          {/* Background ring */}
          <circle
            cx={RING_SIZE / 2}
            cy={RING_SIZE / 2}
            r={RING_RADIUS}
            fill="none"
            stroke="oklch(0.4 0 0 / 0.3)"
            strokeWidth={RING_STROKE}
          />
          {/* Progress ring */}
          <circle
            cx={RING_SIZE / 2}
            cy={RING_SIZE / 2}
            r={RING_RADIUS}
            fill="none"
            stroke="oklch(0.65 0.18 145)"
            strokeWidth={RING_STROKE}
            strokeDasharray={RING_CIRCUMFERENCE}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            className="transition-[stroke-dashoffset] duration-1000 ease-linear"
          />
        </svg>

        {/* LIVE label */}
        <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400">
          Live
        </span>

        {/* Refresh button */}
        <button
          type="button"
          onClick={onRefresh}
          disabled={isChecking}
          aria-label="Refresh now"
          className={cn(
            'rounded-full p-0.5 transition-colors',
            'text-white/50 hover:bg-white/10 hover:text-white',
            'disabled:cursor-wait disabled:opacity-40',
            isChecking && 'animate-spin'
          )}
        >
          <Icon name="refresh" size="xs" />
        </button>
      </div>
    </>
  )
}
