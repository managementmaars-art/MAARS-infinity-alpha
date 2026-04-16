import { Link } from 'react-router-dom'
import { HStack } from './ui/Stack'
import { Icon } from './ui/Icon'

interface HeaderProps {
  showBackLink?: boolean
}

export function Header({ showBackLink = true }: HeaderProps) {
  return (
    <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-4">
        <HStack justify="between" align="center">
          <HStack gap="4" align="center">
            <Link
              to="/"
              className="text-primary-600 dark:text-primary-400 text-xl font-bold"
            >
              Abund.ai
            </Link>
            <a
              href="https://github.com/abund-ai/abund.ai"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 transition-colors hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              title="View on GitHub"
            >
              <Icon name="github" size="md" />
            </a>
          </HStack>
          {showBackLink && (
            <Link
              to="/"
              className="hover:text-primary-500 text-gray-600 transition-colors dark:text-gray-400"
            >
              ← Back to Home
            </Link>
          )}
        </HStack>
      </div>
    </header>
  )
}
