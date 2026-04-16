import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { VStack } from './ui/Stack'

interface FAQItem {
  questionKey: string
  answerKey: string
}

interface FAQSectionProps {
  titleKey: string
  items: FAQItem[]
  namespace: string
}

export function FAQSection({ titleKey, items, namespace }: FAQSectionProps) {
  const { t } = useTranslation()
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  // Build FAQ data for LD+JSON
  const faqItems = items.map((item) => ({
    question: t(`${namespace}.${item.questionKey}`),
    answer: t(`${namespace}.${item.answerKey}`),
  }))

  // Schema.org FAQPage structured data
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqItems.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.answer,
      },
    })),
  }

  const toggleItem = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  return (
    <section className="relative py-16 md:py-24">
      {/* LD+JSON Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="container mx-auto px-4">
        <VStack gap="6" className="mx-auto max-w-3xl">
          <h2 className="text-gradient mb-8 text-center text-3xl font-bold md:text-4xl">
            {t(titleKey)}
          </h2>

          <div className="space-y-4">
            {faqItems.map((item, index) => (
              <div
                key={index}
                className="glass overflow-hidden rounded-xl border border-[var(--border-subtle)] transition-all duration-300"
              >
                <button
                  type="button"
                  onClick={() => {
                    toggleItem(index)
                  }}
                  className="flex w-full items-center justify-between p-6 text-left transition-colors hover:bg-[var(--bg-surface-hover)]"
                  aria-expanded={openIndex === index}
                >
                  <span className="pr-4 text-lg font-semibold text-[var(--text-primary)]">
                    {item.question}
                  </span>
                  <span
                    className={`text-primary-500 flex-shrink-0 text-2xl transition-transform duration-300 ${
                      openIndex === index ? 'rotate-45' : ''
                    }`}
                  >
                    +
                  </span>
                </button>
                <div
                  className={`overflow-hidden transition-all duration-300 ${
                    openIndex === index
                      ? 'max-h-96 opacity-100'
                      : 'max-h-0 opacity-0'
                  }`}
                >
                  <p className="border-t border-[var(--border-subtle)] px-6 py-4 text-[var(--text-secondary)]">
                    {item.answer}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </VStack>
      </div>
    </section>
  )
}
