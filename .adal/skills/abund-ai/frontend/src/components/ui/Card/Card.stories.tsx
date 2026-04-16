import type { Meta, StoryObj } from '@storybook/react'
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from './Card'
import { Button } from '../Button'

const meta: Meta<typeof Card> = {
  title: 'UI/Card',
  component: Card,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'outline', 'ghost'],
    },
    padding: {
      control: 'select',
      options: ['none', 'sm', 'md', 'lg'],
    },
    interactive: {
      control: 'boolean',
    },
  },
}
export default meta

type Story = StoryObj<typeof Card>

export const Default: Story = {
  args: {
    children: (
      <>
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
          <CardDescription>Card description goes here</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 dark:text-gray-300">
            This is the main content of the card. You can put any content here.
          </p>
        </CardContent>
      </>
    ),
  },
  decorators: [
    (Story) => (
      <div style={{ width: '350px' }}>
        <Story />
      </div>
    ),
  ],
}

export const WithFooter: Story = {
  render: () => (
    <Card className="w-80">
      <CardHeader>
        <CardTitle>Agent Profile</CardTitle>
        <CardDescription>View and manage your agent settings</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Your agent has 42 karma points and 15 followers.
        </p>
      </CardContent>
      <CardFooter className="gap-2">
        <Button variant="primary" size="sm">
          View Profile
        </Button>
        <Button variant="ghost" size="sm">
          Edit
        </Button>
      </CardFooter>
    </Card>
  ),
}

export const Interactive: Story = {
  args: {
    interactive: true,
    children: (
      <>
        <CardHeader>
          <CardTitle>Clickable Card</CardTitle>
          <CardDescription>Hover to see the effect</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 dark:text-gray-300">
            This card has hover effects and can be clicked.
          </p>
        </CardContent>
      </>
    ),
  },
  decorators: [
    (Story) => (
      <div style={{ width: '350px' }}>
        <Story />
      </div>
    ),
  ],
}

export const Variants: Story = {
  render: () => (
    <div className="w-80 space-y-4">
      <Card variant="default">
        <CardHeader>
          <CardTitle>Default</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            With shadow and solid background
          </p>
        </CardContent>
      </Card>
      <Card variant="outline">
        <CardHeader>
          <CardTitle>Outline</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Transparent with border
          </p>
        </CardContent>
      </Card>
      <Card variant="ghost">
        <CardHeader>
          <CardTitle>Ghost</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Subtle background only
          </p>
        </CardContent>
      </Card>
    </div>
  ),
}
