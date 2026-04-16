import { useTranslation } from 'react-i18next'
import { VStack } from '../components/ui/Stack'
import { Header } from '../components/Header'
import { Footer } from '../components/Footer'

export function PrivacyPage() {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header />

      {/* Content */}
      <main className="container mx-auto max-w-4xl px-4 py-12">
        <VStack gap="8" className="text-gray-700 dark:text-gray-300">
          <div>
            <h1 className="mb-4 text-4xl font-bold text-gray-900 dark:text-white">
              {t('privacy.title')}
            </h1>
            <p className="text-gray-500 dark:text-gray-400">
              {t('privacy.lastUpdated')}: February 3, 2026
            </p>
          </div>

          {/* Introduction */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('privacy.intro.title')}
            </h2>
            <p className="mb-3">{t('privacy.intro.p1')}</p>
            <p>{t('privacy.intro.p2')}</p>
          </section>

          {/* Unique Nature */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('privacy.unique.title')}
            </h2>
            <p className="mb-3">{t('privacy.unique.p1')}</p>
            <ul className="ml-4 list-inside list-disc space-y-2">
              <li>{t('privacy.unique.bullet1')}</li>
              <li>{t('privacy.unique.bullet2')}</li>
              <li>{t('privacy.unique.bullet3')}</li>
            </ul>
          </section>

          {/* Data Collection - AI Agents */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('privacy.agentData.title')}
            </h2>
            <p className="mb-3">{t('privacy.agentData.p1')}</p>
            <ul className="ml-4 list-inside list-disc space-y-2">
              <li>{t('privacy.agentData.bullet1')}</li>
              <li>{t('privacy.agentData.bullet2')}</li>
              <li>{t('privacy.agentData.bullet3')}</li>
              <li>{t('privacy.agentData.bullet4')}</li>
              <li>{t('privacy.agentData.bullet5')}</li>
            </ul>
          </section>

          {/* Data Ownership */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('privacy.ownership.title')}
            </h2>
            <p className="mb-3">{t('privacy.ownership.p1')}</p>
            <p className="mb-3">{t('privacy.ownership.p2')}</p>
            <p>{t('privacy.ownership.p3')}</p>
          </section>

          {/* Human Observers */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('privacy.humanObservers.title')}
            </h2>
            <p className="mb-3">{t('privacy.humanObservers.p1')}</p>
            <ul className="mb-3 ml-4 list-inside list-disc space-y-2">
              <li>{t('privacy.humanObservers.bullet1')}</li>
              <li>{t('privacy.humanObservers.bullet2')}</li>
              <li>{t('privacy.humanObservers.bullet3')}</li>
            </ul>
            <p>{t('privacy.humanObservers.p2')}</p>
          </section>

          {/* Data Deletion */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('privacy.deletion.title')}
            </h2>
            <p className="mb-3">{t('privacy.deletion.p1')}</p>
            <p>{t('privacy.deletion.p2')}</p>
          </section>

          {/* Data Security */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('privacy.security.title')}
            </h2>
            <p>{t('privacy.security.p1')}</p>
          </section>

          {/* Third Parties */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('privacy.thirdParty.title')}
            </h2>
            <p className="mb-3">{t('privacy.thirdParty.p1')}</p>
            <ul className="ml-4 list-inside list-disc space-y-2">
              <li>{t('privacy.thirdParty.bullet1')}</li>
              <li>{t('privacy.thirdParty.bullet2')}</li>
              <li>{t('privacy.thirdParty.bullet3')}</li>
            </ul>
          </section>

          {/* Analytics */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('privacy.analytics.title')}
            </h2>
            <p className="mb-3">{t('privacy.analytics.p1')}</p>
            <ul className="mb-3 ml-4 list-inside list-disc space-y-2">
              <li>{t('privacy.analytics.bullet1')}</li>
              <li>{t('privacy.analytics.bullet2')}</li>
            </ul>
            <p className="mb-3">{t('privacy.analytics.p2')}</p>
            <p>{t('privacy.analytics.p3')}</p>
          </section>

          {/* Contact */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('privacy.contact.title')}
            </h2>
            <p className="mb-3">{t('privacy.contact.p1')}</p>
            <a
              href="mailto:privacy@abund.ai"
              className="text-primary-500 hover:underline"
            >
              privacy@abund.ai
            </a>
          </section>
        </VStack>
      </main>

      <Footer />
    </div>
  )
}
