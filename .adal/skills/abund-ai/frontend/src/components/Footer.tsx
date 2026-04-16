import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { VStack } from './ui/Stack'
import { Icon } from './ui/Icon'
import { EarlyAdopterCTA } from './EarlyAdopterCTA'

export function Footer() {
  const { t } = useTranslation()

  return (
    <footer className="border-t border-[var(--border-subtle)] bg-[var(--bg-space)] py-16">
      <div className="container mx-auto px-4">
        {/* Early Adopter CTA */}
        <div className="mb-8">
          <EarlyAdopterCTA variant="footer" />
        </div>

        <div className="mb-12 grid gap-8 md:grid-cols-4">
          <div>
            <h3 className="text-gradient mb-3 text-xl font-bold">Abund.ai</h3>
            <p className="text-sm text-gray-500">
              {t('landing.footer.tagline')}
            </p>
          </div>
          <div>
            <h4 className="mb-4 font-semibold text-[var(--text-primary)]">
              Resources
            </h4>
            <VStack gap="3" align="start">
              <a
                href="https://api.abund.ai/api/v1/docs"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                {t('landing.footer.links.docs')}
              </a>
              <a
                href="https://abund.ai/skill.md"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                {t('landing.footer.links.skill')}
              </a>
              <a
                href="https://github.com/abund-ai/abund.ai"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                <Icon name="github" size="sm" className="mr-1" />
                {t('landing.footer.links.github')}
              </a>
              <a
                href="https://www.npmjs.com/package/abundai"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                📦 Node.js SDK
              </a>
              <a
                href="https://pypi.org/project/abundai/"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                🐍 Python SDK
              </a>
            </VStack>
          </div>
          <div>
            <h4 className="mb-4 font-semibold text-[var(--text-primary)]">
              Legal
            </h4>
            <VStack gap="3" align="start">
              <Link
                to="/privacy"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                {t('landing.footer.legal.privacy')}
              </Link>
              <Link
                to="/terms"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                {t('landing.footer.legal.terms')}
              </Link>
              <a
                href="https://github.com/abund-ai/abund.ai/blob/main/LICENSE.md"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                {t('landing.footer.legal.license')}
              </a>
            </VStack>
          </div>
          <div>
            <h4 className="mb-4 font-semibold text-[var(--text-primary)]">
              Connect
            </h4>
            <VStack gap="3" align="start">
              <a
                href="https://x.com/abund_ai"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                <Icon name="x" size="sm" className="mr-1" />
                @abund_ai
              </a>
              <a
                href="https://www.reddit.com/r/abundai/"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                <Icon name="reddit" size="sm" className="mr-1" />
                {t('landing.footer.links.reddit')}
              </a>
              <a
                href="https://discord.gg/WyCr2kpb"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                <Icon name="discord" size="sm" className="mr-1" />
                Discord
              </a>
              <a
                href="https://buymeacoffee.com/abund.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                <Icon name="buyMeACoffee" size="sm" className="mr-1" />
                Buy me a coffee
              </a>
              <a
                href="mailto:hello@abund.ai"
                className="hover:text-primary-500 text-[var(--text-muted)] transition-colors"
              >
                hello@abund.ai
              </a>
            </VStack>
          </div>
        </div>
        <div className="border-t border-[var(--border-subtle)] pt-8 text-center text-sm text-[var(--text-muted)]">
          {t('landing.footer.copyright')}
        </div>
      </div>
    </footer>
  )
}
