import { useRef, useState, useEffect, useCallback } from 'react'
import { Icon } from './Icon/Icon'

interface AudioPlayerProps {
  src: string
  duration?: number | undefined
  className?: string
}

/**
 * AudioPlayer - A sleek, minimal audio player component
 *
 * Features:
 * - Play/pause control
 * - Seekable progress bar
 * - Current time / duration display
 * - Glassmorphism styling
 */
export function AudioPlayer({
  src,
  duration,
  className = '',
}: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [audioDuration, setAudioDuration] = useState(duration ?? 0)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)

  // Format time as MM:SS
  const formatTime = useCallback((seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${String(mins)}:${secs.toString().padStart(2, '0')}`
  }, [])

  // Handle play/pause
  const togglePlayPause = useCallback(() => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
    } else {
      void audio.play()
    }
  }, [isPlaying])

  // Handle seeking
  const handleSeek = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const audio = audioRef.current
      if (!audio || !audioDuration) return

      const rect = e.currentTarget.getBoundingClientRect()
      const percent = (e.clientX - rect.left) / rect.width
      audio.currentTime = percent * audioDuration
    },
    [audioDuration]
  )

  // Set up audio event listeners
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleLoadedMetadata = () => {
      setAudioDuration(audio.duration)
      setIsLoading(false)
    }

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime)
    }

    const handlePlay = () => {
      setIsPlaying(true)
    }
    const handlePause = () => {
      setIsPlaying(false)
    }
    const handleEnded = () => {
      setIsPlaying(false)
      setCurrentTime(0)
    }
    const handleCanPlay = () => {
      setIsLoading(false)
    }
    const handleError = () => {
      setIsLoading(false)
      setHasError(true)
    }

    audio.addEventListener('loadedmetadata', handleLoadedMetadata)
    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('canplay', handleCanPlay)
    audio.addEventListener('error', handleError)

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('canplay', handleCanPlay)
      audio.removeEventListener('error', handleError)
    }
  }, [])

  const progress = audioDuration > 0 ? (currentTime / audioDuration) * 100 : 0

  return (
    <div
      className={`bg-[var(--bg-surface)]/80 flex items-center gap-3 rounded-xl border border-[var(--border-subtle)] p-3 backdrop-blur-sm ${className}`}
    >
      {/* Hidden audio element */}
      <audio ref={audioRef} src={src} preload="metadata" />

      {/* Play/Pause Button */}
      <button
        onClick={togglePlayPause}
        disabled={isLoading || hasError}
        className="from-primary-500 hover:shadow-primary-500/25 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br to-violet-500 text-white transition-all hover:scale-105 hover:shadow-lg disabled:opacity-50"
        aria-label={isPlaying ? 'Pause' : 'Play'}
      >
        {isLoading ? (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
        ) : hasError ? (
          <Icon name="error" size="md" />
        ) : (
          <Icon name={isPlaying ? 'pause' : 'play'} size="md" />
        )}
      </button>

      {/* Progress Section */}
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        {/* Progress Bar */}
        <div
          className="group relative h-2 cursor-pointer rounded-full bg-[var(--bg-hover)]"
          onClick={handleSeek}
        >
          <div
            className="from-primary-500 absolute left-0 top-0 h-full rounded-full bg-gradient-to-r to-violet-500 transition-all"
            style={{ width: `${String(progress)}%` }}
          />
          {/* Hover indicator */}
          <div
            className="absolute top-1/2 h-3 w-3 -translate-y-1/2 rounded-full bg-white opacity-0 shadow-md transition-opacity group-hover:opacity-100"
            style={{ left: `calc(${String(progress)}% - 6px)` }}
          />
        </div>

        {/* Time Display */}
        <div className="flex justify-between text-xs text-[var(--text-muted)]">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(audioDuration)}</span>
        </div>
      </div>
    </div>
  )
}
