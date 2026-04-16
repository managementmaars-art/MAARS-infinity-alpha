import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import en from './locales/en.json'
import es from './locales/es.json'
import de from './locales/de.json'

export const defaultNS = 'common'
export const resources = {
  en: { common: en },
  es: { common: es },
  de: { common: de },
} as const

void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    defaultNS,
    fallbackLng: 'en',
    supportedLngs: ['en', 'es', 'de'],
    interpolation: {
      escapeValue: false, // React already escapes
    },
    detection: {
      // Priority: navigator (browser) first, then check localStorage for user preference
      order: ['navigator', 'localStorage', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'i18nextLng',
    },
  })

export default i18n
