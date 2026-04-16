import type { Meta, StoryObj } from '@storybook/react'
import { Badge } from './Badge'

const meta: Meta<typeof Badge> = {
  title: 'UI/Badge',
  component: Badge,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'primary', 'success', 'warning', 'error', 'info'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
    dot: {
      control: 'boolean',
    },
  },
}
export default meta

type Story = StoryObj<typeof Badge>

export const Default: Story = {
  args: {
    children: 'Badge',
  },
}

export const Variants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="default">Default</Badge>
      <Badge variant="primary">Primary</Badge>
      <Badge variant="success">Success</Badge>
      <Badge variant="warning">Warning</Badge>
      <Badge variant="error">Error</Badge>
      <Badge variant="info">Info</Badge>
    </div>
  ),
}

export const WithDot: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="success" dot>
        Online
      </Badge>
      <Badge variant="error" dot>
        Offline
      </Badge>
      <Badge variant="warning" dot>
        Pending
      </Badge>
    </div>
  ),
}

export const Removable: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge
        variant="primary"
        onRemove={() => {
          alert('Remove clicked')
        }}
      >
        Tag 1
      </Badge>
      <Badge
        variant="primary"
        onRemove={() => {
          alert('Remove clicked')
        }}
      >
        Tag 2
      </Badge>
      <Badge
        variant="primary"
        onRemove={() => {
          alert('Remove clicked')
        }}
      >
        Tag 3
      </Badge>
    </div>
  ),
}

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-2">
      <Badge size="sm">Small</Badge>
      <Badge size="md">Medium</Badge>
      <Badge size="lg">Large</Badge>
    </div>
  ),
}

export const AgentStatuses: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Badge variant="success" dot>
        Claimed
      </Badge>
      <Badge variant="warning" dot>
        Pending Verification
      </Badge>
      <Badge variant="info">42 Karma</Badge>
      <Badge variant="primary">🤖 Bot</Badge>
    </div>
  ),
}
