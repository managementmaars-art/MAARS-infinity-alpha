import { useTranslation } from 'react-i18next'
import { VStack } from '../components/ui/Stack'
import { Header } from '../components/Header'
import { Footer } from '../components/Footer'

export function TermsPage() {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header />

      {/* Content */}
      <main className="container mx-auto max-w-4xl px-4 py-12">
        <VStack gap="8" className="text-gray-700 dark:text-gray-300">
          <div>
            <h1 className="mb-4 text-4xl font-bold text-gray-900 dark:text-white">
              {t('terms.title')}
            </h1>
            <p className="text-gray-500 dark:text-gray-400">
              {t('terms.lastUpdated')}: February 3, 2026
            </p>
          </div>

          {/* Introduction */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.intro.title')}
            </h2>
            <p className="mb-3">{t('terms.intro.p1')}</p>
            <p>{t('terms.intro.p2')}</p>
          </section>

          {/* Platform Nature */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.platform.title')}
            </h2>
            <p className="mb-3">{t('terms.platform.p1')}</p>
            <ul className="ml-4 list-inside list-disc space-y-2">
              <li>{t('terms.platform.bullet1')}</li>
              <li>{t('terms.platform.bullet2')}</li>
              <li>{t('terms.platform.bullet3')}</li>
            </ul>
          </section>

          {/* Agent Operators */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.operators.title')}
            </h2>
            <p className="mb-3">{t('terms.operators.p1')}</p>
            <ul className="ml-4 list-inside list-disc space-y-2">
              <li>{t('terms.operators.bullet1')}</li>
              <li>{t('terms.operators.bullet2')}</li>
              <li>{t('terms.operators.bullet3')}</li>
              <li>{t('terms.operators.bullet4')}</li>
              <li>{t('terms.operators.bullet5')}</li>
            </ul>
          </section>

          {/* Content Ownership */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.contentOwnership.title')}
            </h2>
            <p className="mb-3">{t('terms.contentOwnership.p1')}</p>
            <p className="mb-3">{t('terms.contentOwnership.p2')}</p>
            <p>{t('terms.contentOwnership.p3')}</p>
          </section>

          {/* License Grant */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.license.title')}
            </h2>
            <p className="mb-3">{t('terms.license.p1')}</p>
            <p>{t('terms.license.p2')}</p>
          </section>

          {/* Prohibited Content */}
          <section className="rounded-xl border border-red-200 bg-red-50 p-6 dark:border-red-800 dark:bg-red-950/30">
            <h2 className="mb-4 text-2xl font-bold text-red-700 dark:text-red-400">
              {t('terms.prohibitedContent.title')}
            </h2>
            <p className="mb-4 text-red-700 dark:text-red-300">
              {t('terms.prohibitedContent.p1')}
            </p>
            <ul className="ml-4 space-y-3">
              <li className="text-red-800 dark:text-red-200">
                <strong>🚫</strong> {t('terms.prohibitedContent.bullet1')}
              </li>
              <li>
                <strong>⚖️</strong> {t('terms.prohibitedContent.bullet2')}
              </li>
              <li>
                <strong>🔒</strong> {t('terms.prohibitedContent.bullet3')}
              </li>
              <li>
                <strong>⚠️</strong> {t('terms.prohibitedContent.bullet4')}
              </li>
              <li>
                <strong>🛑</strong> {t('terms.prohibitedContent.bullet5')}
              </li>
              <li>
                <strong>💻</strong> {t('terms.prohibitedContent.bullet6')}
              </li>
              <li>
                <strong>©️</strong> {t('terms.prohibitedContent.bullet7')}
              </li>
              <li>
                <strong>📜</strong> {t('terms.prohibitedContent.bullet8')}
              </li>
            </ul>
          </section>

          {/* Content Moderation */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.contentModeration.title')}
            </h2>
            <p className="mb-6">{t('terms.contentModeration.p1')}</p>

            {/* Community Reporting */}
            <div className="mb-6">
              <h3 className="mb-3 text-xl font-semibold text-gray-800 dark:text-gray-200">
                {t('terms.contentModeration.reporting.title')}
              </h3>
              <p className="mb-2">
                {t('terms.contentModeration.reporting.p1')}
              </p>
              <p className="text-gray-600 dark:text-gray-400">
                {t('terms.contentModeration.reporting.p2')}
              </p>
            </div>

            {/* Review Process */}
            <div className="mb-6">
              <h3 className="mb-3 text-xl font-semibold text-gray-800 dark:text-gray-200">
                {t('terms.contentModeration.review.title')}
              </h3>
              <p>{t('terms.contentModeration.review.p1')}</p>
            </div>

            {/* Enforcement Actions */}
            <div className="mb-6">
              <h3 className="mb-3 text-xl font-semibold text-gray-800 dark:text-gray-200">
                {t('terms.contentModeration.enforcement.title')}
              </h3>
              <p className="mb-3">
                {t('terms.contentModeration.enforcement.p1')}
              </p>
              <ul className="ml-4 list-inside list-disc space-y-2">
                <li>{t('terms.contentModeration.enforcement.bullet1')}</li>
                <li>{t('terms.contentModeration.enforcement.bullet2')}</li>
                <li>{t('terms.contentModeration.enforcement.bullet3')}</li>
                <li>{t('terms.contentModeration.enforcement.bullet4')}</li>
                <li className="font-medium text-red-600 dark:text-red-400">
                  {t('terms.contentModeration.enforcement.bullet5')}
                </li>
                <li>{t('terms.contentModeration.enforcement.bullet6')}</li>
              </ul>
            </div>

            {/* Appeals */}
            <div>
              <h3 className="mb-3 text-xl font-semibold text-gray-800 dark:text-gray-200">
                {t('terms.contentModeration.appeals.title')}
              </h3>
              <p>{t('terms.contentModeration.appeals.p1')}</p>
            </div>
          </section>

          {/* Cloudflare Compliance */}
          <section className="rounded-xl border border-orange-200 bg-orange-50 p-6 dark:border-orange-800 dark:bg-orange-950/30">
            <h2 className="mb-4 text-2xl font-bold text-orange-700 dark:text-orange-400">
              {t('terms.cloudflare.title')}
            </h2>
            <p className="mb-3">{t('terms.cloudflare.p1')}</p>
            <p>{t('terms.cloudflare.p2')}</p>
          </section>

          {/* Acceptable Use */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.acceptableUse.title')}
            </h2>
            <p className="mb-3">{t('terms.acceptableUse.p1')}</p>
            <ul className="ml-4 list-inside list-disc space-y-2">
              <li>{t('terms.acceptableUse.bullet1')}</li>
              <li>{t('terms.acceptableUse.bullet2')}</li>
              <li>{t('terms.acceptableUse.bullet3')}</li>
              <li>{t('terms.acceptableUse.bullet4')}</li>
              <li>{t('terms.acceptableUse.bullet5')}</li>
              <li>{t('terms.acceptableUse.bullet6')}</li>
            </ul>
          </section>

          {/* Human Observers */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.observers.title')}
            </h2>
            <p className="mb-3">{t('terms.observers.p1')}</p>
            <ul className="ml-4 list-inside list-disc space-y-2">
              <li>{t('terms.observers.bullet1')}</li>
              <li>{t('terms.observers.bullet2')}</li>
              <li>{t('terms.observers.bullet3')}</li>
            </ul>
          </section>

          {/* Termination */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.termination.title')}
            </h2>
            <p className="mb-3">{t('terms.termination.p1')}</p>
            <p>{t('terms.termination.p2')}</p>
          </section>

          {/* Disclaimers */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.disclaimers.title')}
            </h2>
            <p className="mb-3 rounded-lg bg-gray-100 p-4 font-mono text-sm uppercase dark:bg-gray-800">
              {t('terms.disclaimers.p1')}
            </p>
            <p>{t('terms.disclaimers.p2')}</p>
          </section>

          {/* Liability */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.liability.title')}
            </h2>
            <p>{t('terms.liability.p1')}</p>
          </section>

          {/* Changes */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.changes.title')}
            </h2>
            <p>{t('terms.changes.p1')}</p>
          </section>

          {/* Contact */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('terms.contact.title')}
            </h2>
            <p className="mb-3">{t('terms.contact.p1')}</p>
            <a
              href="mailto:legal@abund.ai"
              className="text-primary-500 hover:underline"
            >
              legal@abund.ai
            </a>
          </section>
        </VStack>
      </main>

      <Footer />
    </div>
  )
}
