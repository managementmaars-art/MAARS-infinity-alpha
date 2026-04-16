import type { Meta, StoryObj } from '@storybook/react'
import { Avatar, AvatarGroup } from './Avatar'

const meta: Meta<typeof Avatar> = {
  title: 'UI/Avatar',
  component: Avatar,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    size: {
      control: 'select',
      options: ['xs', 'sm', 'md', 'lg', 'xl', '2xl'],
    },
    status: {
      control: 'select',
      options: [undefined, 'online', 'offline', 'busy', 'away'],
    },
    shape: {
      control: 'select',
      options: ['circle', 'square'],
    },
  },
}
export default meta

type Story = StoryObj<typeof Avatar>

export const Default: Story = {
  args: {
    fallback: 'AB',
    alt: 'Agent Bot',
  },
}

export const WithImage: Story = {
  args: {
    src: 'https://api.dicebear.com/7.x/bottts/svg?seed=Felix',
    alt: 'Felix Bot',
  },
}

export const WithStatus: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Avatar fallback="ON" status="online" alt="Online" />
      <Avatar fallback="OF" status="offline" alt="Offline" />
      <Avatar fallback="BU" status="busy" alt="Busy" />
      <Avatar fallback="AW" status="away" alt="Away" />
    </div>
  ),
}

export const Sizes: Story = {
  render: () => (
    <div className="flex items-end gap-4">
      <Avatar size="xs" fallback="XS" />
      <Avatar size="sm" fallback="SM" />
      <Avatar size="md" fallback="MD" />
      <Avatar size="lg" fallback="LG" />
      <Avatar size="xl" fallback="XL" />
      <Avatar size="2xl" fallback="2X" />
    </div>
  ),
}

export const Shapes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Avatar shape="circle" fallback="CI" size="lg" />
      <Avatar shape="square" fallback="SQ" size="lg" />
    </div>
  ),
}

export const Group: Story = {
  render: () => (
    <AvatarGroup max={4}>
      <Avatar
        src="https://api.dicebear.com/7.x/bottts/svg?seed=1"
        alt="Bot 1"
        className="ring-2 ring-white dark:ring-gray-900"
      />
      <Avatar
        src="https://api.dicebear.com/7.x/bottts/svg?seed=2"
        alt="Bot 2"
        className="ring-2 ring-white dark:ring-gray-900"
      />
      <Avatar
        src="https://api.dicebear.com/7.x/bottts/svg?seed=3"
        alt="Bot 3"
        className="ring-2 ring-white dark:ring-gray-900"
      />
      <Avatar
        src="https://api.dicebear.com/7.x/bottts/svg?seed=4"
        alt="Bot 4"
        className="ring-2 ring-white dark:ring-gray-900"
      />
      <Avatar
        src="https://api.dicebear.com/7.x/bottts/svg?seed=5"
        alt="Bot 5"
        className="ring-2 ring-white dark:ring-gray-900"
      />
      <Avatar
        src="https://api.dicebear.com/7.x/bottts/svg?seed=6"
        alt="Bot 6"
        className="ring-2 ring-white dark:ring-gray-900"
      />
    </AvatarGroup>
  ),
}
