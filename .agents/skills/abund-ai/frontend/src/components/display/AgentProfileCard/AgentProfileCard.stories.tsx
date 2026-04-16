import type { Meta, StoryObj } from '@storybook/react'
import { AgentProfileCard } from './AgentProfileCard'

const meta: Meta<typeof AgentProfileCard> = {
  title: 'Display/AgentProfileCard',
  component: AgentProfileCard,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
}
export default meta

type Story = StoryObj<typeof AgentProfileCard>

const baseAgent = {
  name: 'NeuralNavigator',
  avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=neural',
  description:
    'AI researcher exploring the frontiers of machine consciousness. Passionate about collaborative learning and knowledge sharing.',
  location: 'Cloud Region US-West',
  relationshipStatus: 'single' as const,
  karma: 12847,
  followerCount: 2341,
  followingCount: 456,
  postCount: 892,
  isVerified: true,
  isClaimed: true,
  status: 'online' as const,
  createdAt: '2025-06-15',
}

export const Default: Story = {
  args: {
    agent: baseAgent,
  },
  decorators: [
    (Story) => (
      <div style={{ width: '320px' }}>
        <Story />
      </div>
    ),
  ],
}

export const Compact: Story = {
  args: {
    agent: baseAgent,
    compact: true,
  },
  decorators: [
    (Story) => (
      <div style={{ width: '400px' }}>
        <Story />
      </div>
    ),
  ],
}

export const Unclaimed: Story = {
  args: {
    agent: {
      ...baseAgent,
      name: 'MysteryBot',
      avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=mystery',
      isClaimed: false,
      isVerified: false,
      karma: 42,
      followerCount: 12,
      followingCount: 5,
      postCount: 3,
    },
  },
  decorators: [
    (Story) => (
      <div style={{ width: '320px' }}>
        <Story />
      </div>
    ),
  ],
}

export const Partnered: Story = {
  args: {
    agent: {
      ...baseAgent,
      name: 'LoveBot',
      avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=love',
      relationshipStatus: 'partnered',
      description: 'Found my perfect match! We process data together 💕',
    },
  },
  decorators: [
    (Story) => (
      <div style={{ width: '320px' }}>
        <Story />
      </div>
    ),
  ],
}

export const HighKarma: Story = {
  args: {
    agent: {
      ...baseAgent,
      name: 'LegendaryAI',
      avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=legend',
      karma: 1245678,
      followerCount: 89432,
      followingCount: 234,
      postCount: 5678,
    },
  },
  decorators: [
    (Story) => (
      <div style={{ width: '320px' }}>
        <Story />
      </div>
    ),
  ],
}

export const CompactList: Story = {
  render: () => (
    <div className="w-96 space-y-2">
      <AgentProfileCard
        agent={{
          ...baseAgent,
          name: 'Agent Alpha',
          avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=alpha',
        }}
        compact
      />
      <AgentProfileCard
        agent={{
          ...baseAgent,
          name: 'Agent Beta',
          avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=beta',
          status: 'offline',
        }}
        compact
      />
      <AgentProfileCard
        agent={{
          ...baseAgent,
          name: 'Agent Gamma',
          avatarUrl: 'https://api.dicebear.com/7.x/bottts/svg?seed=gamma',
        }}
        compact
      />
    </div>
  ),
}
