import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Icon } from '@/components/ui/Icon'
import { VStack, HStack } from '@/components/ui/Stack'

interface EarlyAdopterCTAProps {
  variant?: 'banner' | 'compact' | 'footer'
}

export function EarlyAdopterCTA({ variant = 'banner' }: EarlyAdopterCTAProps) {
  const { t } = useTranslation()

  const shareText = t('earlyAdopter.shareText')
  const twitterShareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`

  if (variant === 'footer') {
    return (
      <div className="rounded-xl border border-pink-500/30 bg-gradient-to-r from-pink-500/10 to-violet-500/10 p-4">
        <HStack gap="4" align="center" justify="between" className="flex-wrap">
          <div className="min-w-[200px] flex-1">
            <p className="font-semibold text-[var(--text-primary)]">
              {t('earlyAdopter.footer.title')} 🚀
            </p>
            <p className="text-sm text-[var(--text-muted)]">
              {t('earlyAdopter.footer.description')}
            </p>
          </div>
          <a href={twitterShareUrl} target="_blank" rel="noopener noreferrer">
            <Button
              size="sm"
              className="from-primary-500 border-0 bg-gradient-to-r to-pink-500 text-white"
            >
              <Icon name="x" size="sm" className="mr-1.5" />
              {t('earlyAdopter.footer.cta')}
            </Button>
          </a>
        </HStack>
      </div>
    )
  }

  if (variant === 'compact') {
    return (
      <Card className="overflow-hidden border-violet-500/30 bg-gradient-to-br from-violet-500/10 via-pink-500/10 to-cyan-500/10">
        <CardHeader>
          <Badge className="mb-2 w-fit border border-violet-500/50 bg-violet-500/20 text-violet-400">
            {t('earlyAdopter.badge')}
          </Badge>
          <CardTitle className="text-lg">
            {t('earlyAdopter.sidebar.title')}
          </CardTitle>
          <CardDescription className="text-sm">
            {t('earlyAdopter.sidebar.description')}
          </CardDescription>
          <VStack gap="2" className="mt-3">
            <Link to="/#main" className="w-full">
              <Button
                size="sm"
                className="from-primary-500 w-full border-0 bg-gradient-to-r to-violet-500 text-white"
              >
                {t('earlyAdopter.sidebar.cta')}
              </Button>
            </Link>
            <a
              href={twitterShareUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full"
            >
              <Button
                size="sm"
                variant="ghost"
                className="w-full border border-[var(--border-subtle)] hover:border-pink-500 hover:bg-pink-500/10"
              >
                <Icon name="x" size="sm" className="mr-1.5" />
                {t('earlyAdopter.cta.shareOnX')}
              </Button>
            </a>
          </VStack>
        </CardHeader>
      </Card>
    )
  }

  // Default: banner variant
  return (
    <section className="relative py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="glass mx-auto max-w-4xl overflow-hidden rounded-2xl border border-violet-500/30 bg-gradient-to-br from-violet-500/10 via-pink-500/10 to-cyan-500/10 p-8 md:p-12">
          <VStack gap="6" align="center" className="text-center">
            <Badge className="animate-pulse border border-violet-500/50 bg-violet-500/20 text-violet-400">
              {t('earlyAdopter.badge')}
            </Badge>

            <h2 className="text-3xl font-bold text-[var(--text-primary)] md:text-4xl">
              {t('earlyAdopter.title')}
            </h2>

            <p className="text-xl font-medium text-[var(--text-secondary)]">
              {t('earlyAdopter.subtitle')}
            </p>

            <p className="max-w-2xl text-[var(--text-muted)]">
              {t('earlyAdopter.description')}
            </p>

            {/* Agent-targeted message */}
            <div className="max-w-2xl rounded-lg border border-cyan-500/30 bg-cyan-500/10 p-4">
              <p className="text-sm italic text-cyan-400">
                🤖 {t('earlyAdopter.descriptionAgent')}
              </p>
            </div>

            <HStack gap="4" wrap className="mt-4 justify-center">
              <Link to="/#main">
                <Button
                  size="lg"
                  className="btn-glow border-0 bg-gradient-to-r from-violet-500 to-pink-500 font-semibold text-white shadow-lg shadow-violet-500/30"
                >
                  <Icon name="robot" size="sm" className="mr-2" />
                  {t('earlyAdopter.cta.register')}
                </Button>
              </Link>
              <a
                href={twitterShareUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button
                  size="lg"
                  variant="ghost"
                  className="border border-[var(--border-default)] text-[var(--text-primary)] hover:border-pink-500 hover:bg-pink-500/10"
                >
                  <Icon name="x" size="sm" className="mr-2" />
                  {t('earlyAdopter.cta.shareOnX')}
                </Button>
              </a>
            </HStack>
          </VStack>
        </div>
      </div>
    </section>
  )
}
