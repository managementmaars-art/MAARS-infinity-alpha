import { useState } from 'react'
import type { Meta, StoryObj } from '@storybook/react'
import { Modal, ModalFooter } from './Modal'
import { Button } from '../Button'

const meta: Meta<typeof Modal> = {
  title: 'UI/Modal',
  component: Modal,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg', 'xl', 'full'],
    },
    open: {
      control: 'boolean',
    },
  },
}
export default meta

type Story = StoryObj<typeof Modal>

export const Default: Story = {
  render: function Render() {
    const [open, setOpen] = useState(false)
    return (
      <>
        <Button
          onClick={() => {
            setOpen(true)
          }}
        >
          Open Modal
        </Button>
        <Modal
          open={open}
          onClose={() => {
            setOpen(false)
          }}
          title="Modal Title"
          description="This is a description of the modal content."
        >
          <p className="text-gray-600 dark:text-gray-400">
            Modal content goes here. You can put any content inside.
          </p>
        </Modal>
      </>
    )
  },
}

export const WithFooter: Story = {
  render: function Render() {
    const [open, setOpen] = useState(false)
    return (
      <>
        <Button
          onClick={() => {
            setOpen(true)
          }}
        >
          Open Modal
        </Button>
        <Modal
          open={open}
          onClose={() => {
            setOpen(false)
          }}
          title="Confirm Action"
          description="This action cannot be undone."
        >
          <p className="text-gray-600 dark:text-gray-400">
            Are you sure you want to delete this agent? All of their posts will
            be permanently removed.
          </p>
          <ModalFooter>
            <Button
              variant="ghost"
              onClick={() => {
                setOpen(false)
              }}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={() => {
                setOpen(false)
              }}
            >
              Delete Agent
            </Button>
          </ModalFooter>
        </Modal>
      </>
    )
  },
}

export const Sizes: Story = {
  render: function Render() {
    const [size, setSize] = useState<'sm' | 'md' | 'lg' | 'xl' | 'full'>('md')
    const [open, setOpen] = useState(false)
    return (
      <>
        <div className="flex gap-2">
          {(['sm', 'md', 'lg', 'xl', 'full'] as const).map((s) => (
            <Button
              key={s}
              variant="secondary"
              size="sm"
              onClick={() => {
                setSize(s)
                setOpen(true)
              }}
            >
              {s.toUpperCase()}
            </Button>
          ))}
        </div>
        <Modal
          open={open}
          onClose={() => {
            setOpen(false)
          }}
          size={size}
          title={`${size.toUpperCase()} Modal`}
        >
          <p className="text-gray-600 dark:text-gray-400">
            This is a {size} sized modal. The width is constrained based on the
            size prop.
          </p>
        </Modal>
      </>
    )
  },
}

export const LongContent: Story = {
  render: function Render() {
    const [open, setOpen] = useState(false)
    return (
      <>
        <Button
          onClick={() => {
            setOpen(true)
          }}
        >
          Open Modal
        </Button>
        <Modal
          open={open}
          onClose={() => {
            setOpen(false)
          }}
          title="Terms of Service"
        >
          <div className="space-y-4 text-gray-600 dark:text-gray-400">
            {Array.from({ length: 20 }, (_, i) => (
              <p key={i}>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
                eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
                enim ad minim veniam, quis nostrud exercitation ullamco laboris.
              </p>
            ))}
          </div>
        </Modal>
      </>
    )
  },
}
