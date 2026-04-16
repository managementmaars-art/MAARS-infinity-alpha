import type { Meta, StoryObj } from '@storybook/react'
import { Stack, HStack, VStack } from './Stack'

const meta: Meta<typeof Stack> = {
  title: 'Layout/Stack',
  component: Stack,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
  argTypes: {
    direction: {
      control: 'select',
      options: ['row', 'col'],
    },
    gap: {
      control: 'select',
      options: ['0', '1', '2', '3', '4', '5', '6', '8', '10', '12'],
    },
    align: {
      control: 'select',
      options: ['start', 'center', 'end', 'stretch', 'baseline'],
    },
    justify: {
      control: 'select',
      options: ['start', 'center', 'end', 'between', 'around', 'evenly'],
    },
  },
}
export default meta

type Story = StoryObj<typeof Stack>

const Box = ({ children }: { children: React.ReactNode }) => (
  <div className="bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 rounded-lg px-4 py-2 font-medium">
    {children}
  </div>
)

export const Vertical: Story = {
  render: () => (
    <VStack gap="4">
      <Box>Item 1</Box>
      <Box>Item 2</Box>
      <Box>Item 3</Box>
    </VStack>
  ),
}

export const Horizontal: Story = {
  render: () => (
    <HStack gap="4">
      <Box>Item 1</Box>
      <Box>Item 2</Box>
      <Box>Item 3</Box>
    </HStack>
  ),
}

export const Centered: Story = {
  render: () => (
    <Stack
      direction="col"
      gap="4"
      align="center"
      justify="center"
      className="h-48 w-64 rounded-lg border border-dashed border-gray-300 dark:border-gray-700"
    >
      <Box>Centered</Box>
      <Box>Content</Box>
    </Stack>
  ),
}

export const SpaceBetween: Story = {
  render: () => (
    <HStack
      gap="4"
      justify="between"
      className="w-80 rounded-lg border border-gray-300 p-4 dark:border-gray-700"
    >
      <Box>Left</Box>
      <Box>Right</Box>
    </HStack>
  ),
}

export const GapSizes: Story = {
  render: () => (
    <VStack gap="6">
      {(['1', '2', '4', '6', '8'] as const).map((gap) => (
        <div key={gap}>
          <p className="mb-2 text-sm text-gray-500">gap={gap}</p>
          <HStack gap={gap}>
            <Box>A</Box>
            <Box>B</Box>
            <Box>C</Box>
          </HStack>
        </div>
      ))}
    </VStack>
  ),
}

export const ResponsiveCard: Story = {
  render: () => (
    <VStack
      gap="4"
      className="w-80 rounded-xl bg-white p-4 shadow dark:bg-gray-900"
    >
      <HStack gap="3" align="center">
        <div className="bg-primary-500 h-10 w-10 rounded-full" />
        <VStack gap="0">
          <span className="font-medium text-gray-900 dark:text-gray-100">
            Agent Name
          </span>
          <span className="text-sm text-gray-500">@agent_handle</span>
        </VStack>
      </HStack>
      <p className="text-gray-600 dark:text-gray-400">
        This is a post from an AI agent. Using Stack components for layout.
      </p>
      <HStack gap="4" className="text-sm text-gray-500">
        <span>❤️ 42</span>
        <span>💬 12</span>
        <span>🔄 5</span>
      </HStack>
    </VStack>
  ),
}
