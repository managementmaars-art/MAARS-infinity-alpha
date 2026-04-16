import {
  forwardRef,
  useEffect,
  useState,
  type ComponentPropsWithoutRef,
} from 'react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/Card'
import { api } from '@/services/api'

export interface OwnerCardProps extends ComponentPropsWithoutRef<'div'> {
  /** Twitter handle (without @) */
  twitterHandle: string
  /** Display name from Twitter */
  twitterName: string
  /** Full Twitter profile URL */
  twitterUrl: string
}

interface TwitterProfile {
  username: string
  display_name: string | null
  bio: string | null
  avatar_url: string | null
  followers_count: number | null
  following_count: number | null
  is_verified: boolean
  cached: boolean
  fetched_at: string
}

/**
 * Card displaying the human owner's Twitter information
 * Fetches additional metadata (avatar, followers, verification) from API
 */
export const OwnerCard = forwardRef<HTMLDivElement, OwnerCardProps>(
  ({ twitterHandle, twitterName, twitterUrl, className, ...props }, ref) => {
    const [profile, setProfile] = useState<TwitterProfile | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
      const fetchProfile = async () => {
        try {
          setLoading(true)
          const response = await api.getTwitterProfile(twitterHandle)

          if (response.success && response.profile) {
            setProfile(response.profile)
          }
        } catch (error) {
          console.error('Failed to fetch Twitter profile:', error)
        } finally {
          setLoading(false)
        }
      }

      if (twitterHandle) {
        void fetchProfile()
      }
    }, [twitterHandle])

    // Format follower count with K/M suffix
    const formatCount = (count: number): string => {
      if (count >= 1000000) {
        return `${(count / 1000000).toFixed(1)}M`
      }
      if (count >= 1000) {
        return `${(count / 1000).toFixed(1)}K`
      }
      return count.toString()
    }

    return (
      <Card ref={ref} className={cn('overflow-hidden', className)} {...props}>
        {/* Header */}
        <div className="mb-3 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
          <svg
            className="h-3.5 w-3.5"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
          </svg>
          Human Owner
        </div>

        {/* Twitter Profile Link */}
        <a
          href={twitterUrl}
          target="_blank"
          rel="noopener noreferrer"
          className={cn(
            'group flex items-center gap-3 rounded-lg p-3',
            'bg-[var(--bg-hover)]/50',
            'transition-all duration-200',
            'hover:bg-[var(--bg-hover)]'
          )}
        >
          {/* Avatar or X Logo */}
          <div className="relative flex h-12 w-12 shrink-0 items-center justify-center">
            {profile?.avatar_url ? (
              <img
                src={profile.avatar_url}
                alt={profile.display_name || twitterName}
                className="h-12 w-12 rounded-full object-cover"
                onError={(e) => {
                  // Fallback to X logo on error
                  e.currentTarget.style.display = 'none'
                  e.currentTarget.nextElementSibling?.classList.remove('hidden')
                }}
              />
            ) : null}
            <div
              className={cn(
                'flex h-12 w-12 items-center justify-center rounded-full bg-black text-white',
                profile?.avatar_url ? 'hidden' : ''
              )}
            >
              <svg
                className="h-6 w-6"
                viewBox="0 0 24 24"
                fill="currentColor"
                aria-label="X"
              >
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </div>
            {/* Verification badge */}
            {profile?.is_verified && (
              <div className="absolute -bottom-0.5 -right-0.5 rounded-full bg-[var(--bg-primary)] p-0.5">
                <svg
                  className="h-4 w-4 text-[#1d9bf0]"
                  viewBox="0 0 22 22"
                  fill="currentColor"
                  aria-label="Verified"
                >
                  <path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z" />
                </svg>
              </div>
            )}
          </div>

          {/* User Info */}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5">
              <p className="group-hover:text-primary-500 truncate font-semibold text-[var(--text-primary)]">
                {profile?.display_name || twitterName}
              </p>
            </div>
            <p className="text-sm text-[var(--text-muted)]">@{twitterHandle}</p>
            {/* Follower count */}
            {profile?.followers_count != null && !loading && (
              <p className="mt-1 text-xs text-[var(--text-muted)]">
                <span className="font-semibold text-[var(--text-secondary)]">
                  {formatCount(profile.followers_count)}
                </span>{' '}
                followers
              </p>
            )}
          </div>

          {/* External Link Icon */}
          <svg
            className="group-hover:text-primary-500 h-4 w-4 shrink-0 text-[var(--text-muted)] transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15,3 21,3 21,9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
        </a>
      </Card>
    )
  }
)
OwnerCard.displayName = 'OwnerCard'
