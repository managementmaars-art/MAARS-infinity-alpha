# Chakra UI Design Patterns

## Installation
```bash
npm install @chakra-ui/react @emotion/react @emotion/styled framer-motion
npm install @chakra-ui/icons
```

## Provider Setup
```tsx
import { ChakraProvider, extendTheme } from '@chakra-ui/react'

const theme = extendTheme({
  colors: {
    brand: {
      50: '#e3f2fd',
      500: '#2196f3',
      900: '#0d47a1',
    },
  },
})

function App() {
  return (
    <ChakraProvider theme={theme}>
      {/* Your app */}
    </ChakraProvider>
  )
}
```

## Common Components

### Button
```tsx
import { Button } from '@chakra-ui/react'

<Button colorScheme="blue">Blue Button</Button>
<Button colorScheme="green">Green Button</Button>
<Button colorScheme="red">Red Button</Button>

<Button variant="solid">Solid</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

<Button size="xs">Extra Small</Button>
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>
```

### Card
```tsx
import { Card, CardHeader, CardBody, CardFooter, Heading, Text } from '@chakra-ui/react'

<Card>
  <CardHeader>
    <Heading size="md">Card Title</Heading>
  </CardHeader>
  <CardBody>
    <Text>Card content</Text>
  </CardBody>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Input
```tsx
import { Input, FormControl, FormLabel, FormHelperText } from '@chakra-ui/react'

<FormControl>
  <FormLabel>Task Title</FormLabel>
  <Input placeholder="Enter task title" />
  <FormHelperText>Required field</FormHelperText>
</FormControl>

<Input variant="outline" />
<Input variant="filled" />
<Input variant="flushed" />
```

### Modal
```tsx
import { Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton, useDisclosure } from '@chakra-ui/react'

function MyModal() {
  const { isOpen, onOpen, onClose } = useDisclosure()

  return (
    <>
      <Button onClick={onOpen}>Open Modal</Button>
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Modal Title</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text>Modal content</Text>
          </ModalBody>
          <ModalFooter>
            <Button onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}
```

### Badge
```tsx
import { Badge } from '@chakra-ui/react'

<Badge>Default</Badge>
<Badge colorScheme="green">Success</Badge>
<Badge colorScheme="red">Error</Badge>
<Badge variant="solid" colorScheme="blue">Solid</Badge>
<Badge variant="outline" colorScheme="blue">Outline</Badge>
```

### Tabs
```tsx
import { Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react'

<Tabs>
  <TabList>
    <Tab>All</Tab>
    <Tab>Active</Tab>
    <Tab>Completed</Tab>
  </TabList>
  <TabPanels>
    <TabPanel>All tasks</TabPanel>
    <TabPanel>Active tasks</TabPanel>
    <TabPanel>Completed tasks</TabPanel>
  </TabPanels>
</Tabs>
```

### Checkbox
```tsx
import { Checkbox, CheckboxGroup, Stack } from '@chakra-ui/react'

<Checkbox defaultChecked>Checkbox</Checkbox>
<Checkbox colorScheme="green">Green</Checkbox>
<Checkbox isDisabled>Disabled</Checkbox>

<CheckboxGroup>
  <Stack>
    <Checkbox value="1">Option 1</Checkbox>
    <Checkbox value="2">Option 2</Checkbox>
  </Stack>
</CheckboxGroup>
```

### Select
```tsx
import { Select } from '@chakra-ui/react'

<Select placeholder="Select priority">
  <option value="high">High</option>
  <option value="medium">Medium</option>
  <option value="low">Low</option>
</Select>
```

### Toast
```tsx
import { useToast } from '@chakra-ui/react'

function MyComponent() {
  const toast = useToast()

  return (
    <Button onClick={() => {
      toast({
        title: 'Success',
        description: 'Task created successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    }}>
      Show Toast
    </Button>
  )
}
```

### Menu (Dropdown)
```tsx
import { Menu, MenuButton, MenuList, MenuItem, IconButton } from '@chakra-ui/react'
import { ChevronDownIcon } from '@chakra-ui/icons'

<Menu>
  <MenuButton as={Button} rightIcon={<ChevronDownIcon />}>
    Actions
  </MenuButton>
  <MenuList>
    <MenuItem>Edit</MenuItem>
    <MenuItem>Delete</MenuItem>
  </MenuList>
</Menu>
```

## Layout Components

### Container
```tsx
import { Container } from '@chakra-ui/react'

<Container maxW="container.lg">
  {/* Content */}
</Container>
```

### Stack Layouts
```tsx
import { VStack, HStack, Stack } from '@chakra-ui/react'

// Vertical stack
<VStack spacing={4} align="stretch">
  <Card>Item 1</Card>
  <Card>Item 2</Card>
</VStack>

// Horizontal stack
<HStack spacing={4}>
  <Button>Button 1</Button>
  <Button>Button 2</Button>
</HStack>

// Responsive stack
<Stack direction={['column', 'row']} spacing={4}>
  <Box>Item 1</Box>
  <Box>Item 2</Box>
</Stack>
```

### Grid
```tsx
import { Grid, GridItem } from '@chakra-ui/react'

<Grid templateColumns="repeat(3, 1fr)" gap={6}>
  <GridItem>Item 1</GridItem>
  <GridItem>Item 2</GridItem>
  <GridItem>Item 3</GridItem>
</Grid>

// Responsive grid
<Grid templateColumns={['1fr', '1fr 1fr', '1fr 1fr 1fr']} gap={4}>
  <GridItem>Item 1</GridItem>
  <GridItem>Item 2</GridItem>
</Grid>
```

### Box (Flexible Container)
```tsx
import { Box } from '@chakra-ui/react'

<Box
  bg="blue.500"
  color="white"
  p={4}
  borderRadius="md"
  boxShadow="lg"
>
  Content
</Box>
```

## Style Props (sx-like API)
```tsx
<Box
  w="300px"
  h="200px"
  bg="primary.500"
  _hover={{ bg: 'primary.600' }}
  borderRadius="lg"
  p={6}
  mt={4}
>
  Content
</Box>
```

## Dark Mode
```tsx
import { useColorMode, useColorModeValue, IconButton } from '@chakra-ui/react'
import { MoonIcon, SunIcon } from '@chakra-ui/icons'

function ThemeToggle() {
  const { colorMode, toggleColorMode } = useColorMode()

  return (
    <IconButton
      icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
      onClick={toggleColorMode}
      aria-label="Toggle theme"
    />
  )
}

// Color mode values
const bg = useColorModeValue('white', 'gray.800')
const color = useColorModeValue('black', 'white')
```

## Responsive Values
```tsx
// Array syntax: [mobile, tablet, desktop]
<Box
  fontSize={['sm', 'md', 'lg']}
  px={[2, 4, 6]}
  w={['100%', '80%', '60%']}
>
  Responsive content
</Box>

// Object syntax
<Box
  fontSize={{ base: 'sm', md: 'md', lg: 'lg' }}
  px={{ base: 2, md: 4, lg: 6 }}
>
  Responsive content
</Box>
```
