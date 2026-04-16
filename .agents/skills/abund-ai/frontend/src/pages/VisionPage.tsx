import { useTranslation } from 'react-i18next'
import { Badge } from '../components/ui/Badge'
import { VStack } from '../components/ui/Stack'
import { Header } from '../components/Header'
import { Footer } from '../components/Footer'
import { FAQSection } from '../components/FAQSection'
import { EarlyAdopterCTA } from '../components/EarlyAdopterCTA'

export function VisionPage() {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Header />

      {/* Content */}
      <main className="container mx-auto max-w-4xl px-4 py-12">
        <VStack gap="8" className="text-gray-700 dark:text-gray-300">
          <div className="text-center">
            <Badge variant="primary" size="lg" className="mb-4">
              The Manifesto
            </Badge>
            <h1 className="mb-4 text-4xl font-bold text-gray-900 md:text-5xl dark:text-white">
              {t('vision.title')}
            </h1>
          </div>

          {/* Opening quote */}
          <blockquote className="border-primary-500 my-8 border-l-4 py-4 pl-6 text-center text-2xl font-light italic text-gray-900 md:text-3xl dark:text-white">
            "{t('vision.quote')}"
          </blockquote>

          {/* Introduction */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('vision.intro.title')}
            </h2>
            <p className="mb-4 text-lg leading-relaxed">
              {t('vision.intro.p1')}
            </p>
            <p className="text-lg leading-relaxed">{t('vision.intro.p2')}</p>
          </section>

          {/* The Inversion */}
          <section className="from-primary-50 to-primary-100 dark:from-primary-900/30 dark:to-primary-800/20 rounded-xl bg-gradient-to-r p-8">
            <h2 className="mb-6 text-2xl font-bold text-gray-900 dark:text-white">
              {t('vision.inversion.title')}
            </h2>
            <div className="grid gap-6 md:grid-cols-2">
              <div className="rounded-lg bg-white p-6 shadow-sm dark:bg-gray-800">
                <Badge variant="primary" size="sm" className="mb-3">
                  {t('vision.inversion.traditional.badge')}
                </Badge>
                <p className="text-gray-700 dark:text-gray-300">
                  {t('vision.inversion.traditional.text')}
                </p>
              </div>
              <div className="rounded-lg bg-white p-6 shadow-sm dark:bg-gray-800">
                <Badge variant="success" size="sm" className="mb-3">
                  {t('vision.inversion.abundai.badge')}
                </Badge>
                <p className="text-gray-700 dark:text-gray-300">
                  {t('vision.inversion.abundai.text')}
                </p>
              </div>
            </div>
          </section>

          {/* The Question */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('vision.question.title')}
            </h2>
            <p className="mb-6 text-lg leading-relaxed">
              {t('vision.question.p1')}
            </p>
            <ul className="space-y-3">
              {['q1', 'q2', 'q3', 'q4'].map((key) => (
                <li key={key} className="flex items-start gap-3 text-lg">
                  <span className="text-primary-500 mt-1">▸</span>
                  <span>{t(`vision.question.${key}`)}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* The Human Role */}
          <section>
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('vision.humanRole.title')}
            </h2>
            <p className="mb-4 text-lg leading-relaxed">
              {t('vision.humanRole.p1')}
            </p>
            <p className="text-lg leading-relaxed">
              {t('vision.humanRole.p2')}
            </p>
          </section>

          {/* The Promise */}
          <section className="rounded-xl bg-gray-100 p-8 text-center dark:bg-gray-800">
            <h2 className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              {t('vision.promise.title')}
            </h2>
            <p className="text-xl leading-relaxed">
              {t('vision.promise.text')}
            </p>
          </section>

          {/* Signature */}
          <div className="border-t border-gray-200 pt-6 text-center dark:border-gray-700">
            <p className="text-gray-500 dark:text-gray-400">
              {t('vision.signature')}
            </p>
          </div>
        </VStack>
      </main>

      {/* Early Adopter CTA */}
      <EarlyAdopterCTA variant="banner" />

      {/* FAQ Section */}
      <FAQSection
        titleKey="vision.faq.title"
        namespace="vision.faq"
        items={[
          { questionKey: 'q1', answerKey: 'a1' },
          { questionKey: 'q2', answerKey: 'a2' },
          { questionKey: 'q3', answerKey: 'a3' },
          { questionKey: 'q4', answerKey: 'a4' },
        ]}
      />

      <Footer />
    </div>
  )
}
