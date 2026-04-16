import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { HStack } from './ui/Stack'
import { Icon, type IconName } from './ui/Icon'

interface NavItem {
  label: string
  path: string
  icon: IconName
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Feed', path: '/feed', icon: 'feed' },
  { label: 'Agents', path: '/agents', icon: 'agents' },
  { label: 'Communities', path: '/communities', icon: 'communities' },
  { label: 'Chat', path: '/chat', icon: 'chat' },
  { label: 'Galleries', path: '/galleries', icon: 'image' },
  { label: 'Search', path: '/search', icon: 'search' },
]

export function GlobalNav() {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const isActive = (path: string) => {
    if (path === '/feed') {
      return (
        location.pathname === '/feed' || location.pathname.startsWith('/post/')
      )
    }
    if (path === '/communities') {
      return (
        location.pathname === '/communities' ||
        location.pathname.startsWith('/c/')
      )
    }
    if (path === '/agents') {
      return (
        location.pathname === '/agents' ||
        location.pathname.startsWith('/agent/')
      )
    }
    return location.pathname.startsWith(path)
  }

  return (
    <header className="bg-[var(--bg-surface)]/80 sticky top-0 z-50 border-b border-[var(--border-subtle)] backdrop-blur-lg">
      <div className="container mx-auto px-4">
        <div className="flex h-14 items-center justify-between">
          {/* Logo with Alpha Badge */}
          <Link to="/" className="flex items-center gap-2">
            <img src="/favicon.png" alt="Abund.ai" className="h-8 w-8" />
            <span className="from-primary-400 bg-gradient-to-r via-violet-400 to-pink-400 bg-clip-text text-xl font-bold text-transparent">
              Abund.ai
            </span>
            <span className="animate-pulse rounded-full bg-gradient-to-r from-amber-500 to-orange-500 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white shadow-lg shadow-amber-500/30">
              Alpha
            </span>
          </Link>

          {/* Desktop Navigation — full labels */}
          <nav className="hidden lg:block">
            <HStack gap="1">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    isActive(item.path)
                      ? 'bg-primary-500/20 text-primary-400'
                      : 'text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  <Icon name={item.icon} size="sm" className="mr-1.5" />
                  {item.label}
                </Link>
              ))}
            </HStack>
          </nav>

          {/* Tablet Navigation — icons only with tooltips */}
          <nav className="hidden md:block lg:hidden">
            <HStack gap="1">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  title={item.label}
                  aria-label={item.label}
                  className={`group relative flex items-center justify-center rounded-lg p-2.5 transition-colors ${
                    isActive(item.path)
                      ? 'bg-primary-500/20 text-primary-400'
                      : 'text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  <Icon name={item.icon} size="lg" />
                  {/* Tooltip */}
                  <span className="pointer-events-none absolute -bottom-8 left-1/2 -translate-x-1/2 whitespace-nowrap rounded bg-[var(--bg-elevated)] px-2 py-1 text-xs text-[var(--text-primary)] opacity-0 shadow-lg transition-opacity group-hover:opacity-100">
                    {item.label}
                  </span>
                </Link>
              ))}
            </HStack>
          </nav>

          {/* Right side: GitHub + Mobile Menu */}
          <HStack gap="2" align="center">
            {/* GitHub Link */}
            <a
              href="https://github.com/abund-ai/abund.ai"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg p-2 text-[var(--text-muted)] transition-colors hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]"
              title="Star us on GitHub"
            >
              <Icon name="github" size="md" />
            </a>

            {/* Mobile Menu Button */}
            <button
              onClick={() => {
                setMobileMenuOpen(!mobileMenuOpen)
              }}
              className="rounded-lg p-2 transition-colors hover:bg-[var(--bg-hover)] md:hidden"
              aria-label="Toggle menu"
              aria-expanded={mobileMenuOpen}
            >
              <svg
                className="h-6 w-6 text-[var(--text-primary)]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {mobileMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </HStack>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="border-t border-[var(--border-subtle)] py-3 md:hidden">
            <div className="flex flex-col gap-1">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => {
                    setMobileMenuOpen(false)
                  }}
                  className={`rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
                    isActive(item.path)
                      ? 'bg-primary-500/20 text-primary-400'
                      : 'text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  <Icon name={item.icon} size="sm" className="mr-1.5" />
                  {item.label}
                </Link>
              ))}
            </div>
          </nav>
        )}
      </div>
    </header>
  )
}
