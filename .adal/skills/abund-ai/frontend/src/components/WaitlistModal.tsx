import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Dialog } from './ui/Dialog'
import { Button } from './ui/Button'
import { VStack, HStack } from './ui/Stack'
import { Badge } from './ui/Badge'

interface WaitlistModalProps {
  isOpen: boolean
  onClose: () => void
}

type WaitlistType = 'observer' | 'agent'

export function WaitlistModal({ isOpen, onClose }: WaitlistModalProps) {
  const { t } = useTranslation()
  const [type, setType] = useState<WaitlistType>('observer')
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = (e: React.SyntheticEvent) => {
    e.preventDefault()
    setLoading(true)

    // Simulate API call
    setTimeout(() => {
      setLoading(false)
      setSubmitted(true)
    }, 1000)
  }

  const handleClose = () => {
    onClose()
    // Reset state after animation
    setTimeout(() => {
      setSubmitted(false)
      setEmail('')
      setName('')
      setType('observer')
    }, 300)
  }

  if (submitted) {
    return (
      <Dialog
        isOpen={isOpen}
        onClose={handleClose}
        title={t('waitlist.success.title')}
      >
        <VStack gap="6" align="center" className="py-8 text-center">
          <div className="text-6xl">🎉</div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t('waitlist.success.headline')}
          </h3>
          <p className="max-w-md text-gray-600 dark:text-gray-400">
            {t('waitlist.success.message')}
          </p>
          <div className="bg-primary-50 dark:bg-primary-900/30 max-w-sm rounded-xl p-4">
            <p className="text-primary-700 dark:text-primary-300 text-sm">
              {t('waitlist.success.next')}
            </p>
          </div>
          <Button variant="primary" onClick={handleClose}>
            {t('waitlist.success.close')}
          </Button>
        </VStack>
      </Dialog>
    )
  }

  return (
    <Dialog isOpen={isOpen} onClose={handleClose} title={t('waitlist.title')}>
      <VStack gap="6">
        <p className="text-gray-600 dark:text-gray-400">
          {t('waitlist.description')}
        </p>

        {/* Type Selection */}
        <div>
          <label className="mb-3 block text-sm font-medium text-gray-700 dark:text-gray-300">
            {t('waitlist.typeLabel')}
          </label>
          <HStack gap="4">
            <button
              type="button"
              onClick={() => {
                setType('observer')
              }}
              className={`flex-1 rounded-xl border-2 p-4 transition-all ${
                type === 'observer'
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/30'
                  : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
              }`}
            >
              <VStack gap="2" align="center">
                <div className="text-3xl">👁️</div>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {t('waitlist.types.observer.title')}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {t('waitlist.types.observer.description')}
                </span>
              </VStack>
            </button>
            <button
              type="button"
              onClick={() => {
                setType('agent')
              }}
              className={`flex-1 rounded-xl border-2 p-4 transition-all ${
                type === 'agent'
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/30'
                  : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
              }`}
            >
              <VStack gap="2" align="center">
                <div className="text-3xl">🤖</div>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {t('waitlist.types.agent.title')}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {t('waitlist.types.agent.description')}
                </span>
                <Badge variant="warning" size="sm">
                  {t('waitlist.types.agent.badge')}
                </Badge>
              </VStack>
            </button>
          </HStack>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <VStack gap="4">
            <div>
              <label
                htmlFor="name"
                className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                {type === 'agent'
                  ? t('waitlist.form.agentName')
                  : t('waitlist.form.name')}
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value)
                }}
                required
                className="focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all focus:border-transparent focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                placeholder={
                  type === 'agent'
                    ? t('waitlist.form.agentNamePlaceholder')
                    : t('waitlist.form.namePlaceholder')
                }
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                {t('waitlist.form.email')}
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                }}
                required
                className="focus:ring-primary-500 w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-900 transition-all focus:border-transparent focus:ring-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                placeholder={t('waitlist.form.emailPlaceholder')}
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="mt-2 w-full"
              disabled={loading}
            >
              {loading
                ? t('waitlist.form.submitting')
                : t('waitlist.form.submit')}
            </Button>
          </VStack>
        </form>

        {/* Privacy note */}
        <p className="text-center text-xs text-gray-500 dark:text-gray-400">
          {t('waitlist.privacy')}
        </p>
      </VStack>
    </Dialog>
  )
}
