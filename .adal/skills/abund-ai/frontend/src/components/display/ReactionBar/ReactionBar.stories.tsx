import type { Meta, StoryObj } from '@storybook/react'
import { ReactionBar, ReactionBadge } from './ReactionBar'

const meta: Meta<typeof ReactionBar> = {
  title: 'Display/ReactionBar',
  component: ReactionBar,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
    showEmpty: {
      control: 'boolean',
    },
  },
}
export default meta

type Story = StoryObj<typeof ReactionBar>

export const Default: Story = {
  args: {
    reactions: {
      robot: 15,
      heart: 8,
      fire: 5,
      brain: 3,
    },
  },
}

export const Sizes: Story = {
  render: () => (
    <div className="space-y-4">
      <div>
        <p className="mb-2 text-sm text-gray-500">Small</p>
        <ReactionBar size="sm" reactions={{ robot: 15, heart: 8, fire: 5 }} />
      </div>
      <div>
        <p className="mb-2 text-sm text-gray-500">Medium</p>
        <ReactionBar size="md" reactions={{ robot: 15, heart: 8, fire: 5 }} />
      </div>
      <div>
        <p className="mb-2 text-sm text-gray-500">Large</p>
        <ReactionBar size="lg" reactions={{ robot: 15, heart: 8, fire: 5 }} />
      </div>
    </div>
  ),
}

export const AllReactions: Story = {
  args: {
    reactions: {
      robot: 42,
      heart: 23,
      fire: 18,
      brain: 12,
      idea: 8,
      laugh: 5,
      celebrate: 3,
    },
  },
}

export const ShowEmpty: Story = {
  args: {
    reactions: {
      robot: 15,
      heart: 8,
    },
    showEmpty: true,
  },
}

export const HighCounts: Story = {
  args: {
    reactions: {
      robot: 15234,
      heart: 8923,
      fire: 5100,
      brain: 1200,
    },
  },
}

export const SingleBadges: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <ReactionBadge type="robot" count={42} />
      <ReactionBadge type="heart" count={23} />
      <ReactionBadge type="fire" count={18} />
      <ReactionBadge type="brain" count={1500} />
    </div>
  ),
}
