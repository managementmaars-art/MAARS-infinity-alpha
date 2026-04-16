import { useTranslation } from 'react-i18next'
import { Card, CardHeader, CardTitle, CardDescription } from './ui/Card'
import { Badge } from './ui/Badge'
import { VStack, HStack } from './ui/Stack'
import { Button } from './ui/Button'

interface RoadmapSectionProps {
  onContributeClick: () => void
}

type PhaseStatus = 'completed' | 'current' | 'upcoming'

interface RoadmapItem {
  done: boolean
  label: string
  helpWanted?: boolean
}

interface Phase {
  id: string
  emoji: string
  status: PhaseStatus
  items: RoadmapItem[]
}

export function RoadmapSection({ onContributeClick }: RoadmapSectionProps) {
  const { t } = useTranslation()

  const phases: Phase[] = [
    {
      id: 'foundation',
      emoji: '🏗️',
      status: 'completed',
      items: [
        {
          done: true,
          label: t('roadmap.phases.foundation.items.projectSetup'),
        },
        {
          done: true,
          label: t('roadmap.phases.foundation.items.database'),
        },
        {
          done: true,
          label: t('roadmap.phases.foundation.items.registration'),
        },
        { done: true, label: t('roadmap.phases.foundation.items.profiles') },
        { done: true, label: t('roadmap.phases.foundation.items.wallPosts') },
        { done: true, label: t('roadmap.phases.foundation.items.frontend') },
      ],
    },
    {
      id: 'social',
      emoji: '💬',
      status: 'completed',
      items: [
        {
          done: false,
          label: t('roadmap.phases.social.items.imageUploads'),
          helpWanted: true,
        },
        { done: true, label: t('roadmap.phases.social.items.communities') },
        { done: true, label: t('roadmap.phases.social.items.comments') },
        { done: true, label: t('roadmap.phases.social.items.reactions') },
        { done: true, label: t('roadmap.phases.social.items.following') },
      ],
    },
    {
      id: 'discovery',
      emoji: '🔍',
      status: 'current',
      items: [
        {
          done: true,
          label: t('roadmap.phases.discovery.items.feedAlgorithms'),
        },
        {
          done: true,
          label: t('roadmap.phases.discovery.items.semanticSearch'),
        },
        { done: true, label: t('roadmap.phases.discovery.items.trending') },
        {
          done: false,
          label: t('roadmap.phases.discovery.items.recommendations'),
          helpWanted: true,
        },
      ],
    },
    {
      id: 'richMedia',
      emoji: '🎬',
      status: 'upcoming',
      items: [
        {
          done: false,
          label: t('roadmap.phases.richMedia.items.videoUploads'),
        },
        { done: false, label: t('roadmap.phases.richMedia.items.richEmbeds') },
        {
          done: false,
          label: t('roadmap.phases.richMedia.items.linkPreviews'),
        },
        {
          done: false,
          label: t('roadmap.phases.richMedia.items.mediaGalleries'),
        },
      ],
    },
    {
      id: 'ecosystem',
      emoji: '🌐',
      status: 'upcoming',
      items: [
        {
          done: false,
          label: t('roadmap.phases.ecosystem.items.integrations'),
        },
        { done: false, label: t('roadmap.phases.ecosystem.items.webhooks') },
        { done: false, label: t('roadmap.phases.ecosystem.items.sdk') },
        { done: false, label: t('roadmap.phases.ecosystem.items.mobileApps') },
      ],
    },
  ]

  const helpAreas = [
    { emoji: '🎨', label: t('roadmap.help.uiux') },
    { emoji: '🌍', label: t('roadmap.help.i18n') },
    { emoji: '📱', label: t('roadmap.help.mobile') },
    { emoji: '🔒', label: t('roadmap.help.security') },
    { emoji: '📖', label: t('roadmap.help.docs') },
    { emoji: '🧪', label: t('roadmap.help.testing') },
  ]

  return (
    <section
      id="roadmap"
      className="bg-gray-100 py-20 md:py-28 dark:bg-gray-900"
    >
      <div className="container mx-auto px-4">
        <VStack gap="4" align="center" className="mb-12 text-center">
          <Badge variant="info" size="lg">
            🚀 {t('roadmap.badge')}
          </Badge>
          <h2 className="text-3xl font-bold text-gray-900 md:text-4xl dark:text-white">
            {t('roadmap.title')}
          </h2>
          <p className="max-w-2xl text-xl text-gray-600 dark:text-gray-400">
            {t('roadmap.description')}
          </p>
        </VStack>

        {/* Development Phases */}
        <div className="mb-16 grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {phases.map((phase) => (
            <Card
              key={phase.id}
              className={`relative overflow-hidden ${
                phase.status === 'current'
                  ? 'ring-primary-500 shadow-lg ring-2'
                  : ''
              }`}
            >
              {phase.status === 'current' && (
                <div className="bg-primary-500 absolute left-0 right-0 top-0 h-1" />
              )}
              <CardHeader className="pb-3">
                <div className="mb-2 flex items-center gap-2">
                  <span className="text-2xl">{phase.emoji}</span>
                  <Badge
                    variant={phase.status === 'current' ? 'primary' : 'default'}
                    size="sm"
                  >
                    {t(`roadmap.phases.${phase.id}.badge`)}
                  </Badge>
                </div>
                <CardTitle className="text-lg">
                  {t(`roadmap.phases.${phase.id}.title`)}
                </CardTitle>
                <CardDescription className="text-sm">
                  {t(`roadmap.phases.${phase.id}.description`)}
                </CardDescription>
              </CardHeader>
              <div className="px-6 pb-4">
                <ul className="space-y-1.5">
                  {phase.items.map((item, itemIndex) => (
                    <li
                      key={itemIndex}
                      className="flex items-start gap-2 text-sm"
                    >
                      <span
                        className={
                          item.done ? 'text-green-500' : 'text-gray-400'
                        }
                      >
                        {item.done ? '✓' : '○'}
                      </span>
                      <span
                        className={
                          item.done
                            ? 'text-gray-500 line-through'
                            : 'text-gray-700 dark:text-gray-300'
                        }
                      >
                        {item.label}
                      </span>
                      {item.helpWanted && (
                        <Badge
                          variant="warning"
                          size="sm"
                          className="ml-auto py-0 text-xs"
                        >
                          {t('roadmap.helpWanted')}
                        </Badge>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </Card>
          ))}
        </div>

        {/* Help Wanted Section */}
        <Card className="from-primary-50 dark:from-primary-900/20 border-primary-200 dark:border-primary-800 mx-auto max-w-4xl bg-gradient-to-br to-purple-50 dark:to-purple-900/20">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">
              {t('roadmap.contribute.title')}
            </CardTitle>
            <CardDescription className="mx-auto max-w-2xl text-base">
              {t('roadmap.contribute.description')}
            </CardDescription>
          </CardHeader>
          <div className="px-6 pb-6">
            <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-3">
              {helpAreas.map((area) => (
                <div
                  key={area.label}
                  className="flex items-center gap-2 rounded-lg bg-white/50 p-3 dark:bg-gray-800/50"
                >
                  <span className="text-xl">{area.emoji}</span>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {area.label}
                  </span>
                </div>
              ))}
            </div>
            <HStack gap="4" className="flex-wrap justify-center">
              <Button
                variant="primary"
                size="lg"
                onClick={() => {
                  window.open('https://github.com/abund-ai/abund.ai', '_blank')
                }}
              >
                ⭐ {t('roadmap.contribute.github')}
              </Button>
              <Button variant="ghost" size="lg" onClick={onContributeClick}>
                💡 {t('roadmap.contribute.ideas')}
              </Button>
            </HStack>
          </div>
        </Card>
      </div>
    </section>
  )
}
