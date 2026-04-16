import { useState } from 'react'
import type { Meta, StoryObj } from '@storybook/react'
import { Textarea } from './Textarea'

const meta: Meta<typeof Textarea> = {
  title: 'UI/Textarea',
  component: Textarea,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  decorators: [
    (Story) => (
      <div style={{ width: '350px' }}>
        <Story />
      </div>
    ),
  ],
}
export default meta

type Story = StoryObj<typeof Textarea>

export const Default: Story = {
  args: {
    placeholder: 'Write something...',
  },
}

export const WithLabel: Story = {
  render: () => (
    <div className="space-y-1.5">
      <label
        htmlFor="post"
        className="text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        New Post
      </label>
      <Textarea id="post" placeholder="What's on your mind?" />
    </div>
  ),
}

export const WithCharacterCount: Story = {
  render: function Render() {
    const [value, setValue] = useState('')
    return (
      <Textarea
        placeholder="Write your post (max 280 characters)..."
        showCount
        maxLength={280}
        value={value}
        onChange={(e) => {
          setValue(e.target.value)
        }}
      />
    )
  },
}

export const Error: Story = {
  args: {
    placeholder: 'Write something...',
    error: true,
    errorMessage: 'Post content is required',
  },
}

export const Disabled: Story = {
  args: {
    placeholder: 'This textarea is disabled',
    disabled: true,
  },
}
