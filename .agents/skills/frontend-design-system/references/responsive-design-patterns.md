# Responsive Design Patterns & Best Practices

## Mobile-First Philosophy

Always start with mobile layout and enhance for larger screens.

```tsx
// ✅ Good: Mobile-first
<div className="w-full md:w-1/2 lg:w-1/3">
  Mobile: 100% width
  Tablet: 50% width
  Desktop: 33% width
</div>

// ❌ Bad: Desktop-first requires overrides
<div className="w-1/3 lg:w-1/2 md:w-full">
```

## Common Breakpoints

```tsx
// Tailwind breakpoints
sm:  640px   // Phone landscape
md:  768px   // Tablet
lg:  1024px  // Laptop
xl:  1280px  // Desktop
2xl: 1536px  // Large desktop

// Material UI breakpoints
xs: 0px      // Phone
sm: 600px    // Tablet
md: 900px    // Small laptop
lg: 1200px   // Desktop
xl: 1536px   // Large desktop

// Chakra UI breakpoints
base: 0px    // Phone
sm: 30em     // 480px
md: 48em     // 768px
lg: 62em     // 992px
xl: 80em     // 1280px
2xl: 96em    // 1536px
```

## Layout Patterns

### Container Pattern
```tsx
// Responsive max-width container
<div className="container mx-auto px-4 md:px-6 lg:px-8 max-w-7xl">
  {/* Content stays centered with appropriate padding */}
</div>

// Material UI
<Container maxWidth="lg" sx={{ px: { xs: 2, md: 3 } }}>

// Chakra UI
<Container maxW="container.lg" px={{ base: 4, md: 6 }}>
```

### Grid Layouts

#### Auto-Responsive Grid
```tsx
// Automatically adjusts columns based on min-width
<div className="grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-4">
  {/* Items automatically wrap when screen < 300px per item */}
</div>
```

#### Explicit Responsive Grid
```tsx
// 1 → 2 → 3 → 4 columns
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">

// Material UI
<Grid container spacing={2}>
  <Grid item xs={12} sm={6} lg={4} xl={3}>

// Chakra UI
<Grid
  templateColumns={{
    base: '1fr',
    sm: 'repeat(2, 1fr)',
    lg: 'repeat(3, 1fr)'
  }}
  gap={4}
>
```

### Flexbox Patterns

#### Responsive Navigation
```tsx
// Vertical on mobile, horizontal on desktop
<nav className="flex flex-col md:flex-row gap-4 items-start md:items-center">
  <Logo />
  <div className="flex flex-col md:flex-row gap-2 md:ml-auto">
    <Button>Tasks</Button>
    <Button>Settings</Button>
  </div>
</nav>
```

#### Responsive Card Layout
```tsx
// Stack vertically on mobile, side-by-side on tablet+
<div className="flex flex-col md:flex-row gap-4">
  <div className="flex-1">Content 1</div>
  <div className="flex-1">Content 2</div>
</div>
```

## Typography Scaling

### Fluid Typography
```tsx
// Responsive text sizes
<h1 className="text-2xl md:text-3xl lg:text-4xl xl:text-5xl">
  Heading scales with viewport
</h1>

// Body text
<p className="text-sm md:text-base lg:text-lg">
  Paragraph text
</p>

// Material UI
<Typography
  variant="h1"
  sx={{
    fontSize: { xs: '2rem', md: '3rem', lg: '4rem' }
  }}
>

// Chakra UI
<Heading fontSize={{ base: '2xl', md: '3xl', lg: '4xl' }}>
```

### Clamp for Smooth Scaling
```tsx
// CSS clamp: min, preferred, max
<h1 style={{ fontSize: 'clamp(1.5rem, 5vw, 3rem)' }}>
  Smoothly scales between 1.5rem and 3rem
</h1>
```

## Spacing Patterns

### Responsive Padding/Margin
```tsx
// Increase spacing on larger screens
<div className="p-4 md:p-6 lg:p-8 xl:p-12">
  {/* 16px → 24px → 32px → 48px padding */}
</div>

// Gap in flex/grid
<div className="flex gap-2 md:gap-4 lg:gap-6">
```

### Container Spacing
```tsx
// Full-width on mobile, constrained on desktop
<div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
```

## Component Patterns

### Responsive Card
```tsx
function ResponsiveCard({ task }) {
  return (
    <Card className="p-4 md:p-6">
      <div className="flex flex-col md:flex-row gap-4">
        {/* Content stacks on mobile, side-by-side on tablet+ */}
        <div className="flex-1">
          <h3 className="text-lg md:text-xl">{task.title}</h3>
          <p className="text-sm md:text-base text-muted-foreground">
            {task.description}
          </p>
        </div>
        <div className="flex md:flex-col gap-2">
          <Button size="sm" className="md:size-default">Complete</Button>
          <Button variant="outline" size="sm">Edit</Button>
        </div>
      </div>
    </Card>
  )
}
```

### Responsive Table → Cards
```tsx
// Desktop: Table
// Mobile: Card list
function ResponsiveTaskList({ tasks }) {
  return (
    <>
      {/* Desktop table */}
      <div className="hidden md:block">
        <table className="w-full">
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map(task => (
              <tr key={task.id}>
                <td>{task.title}</td>
                <td>{task.status}</td>
                <td><Button>Edit</Button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="md:hidden space-y-4">
        {tasks.map(task => (
          <Card key={task.id}>
            <CardContent>
              <h3>{task.title}</h3>
              <Badge>{task.status}</Badge>
              <Button className="mt-2">Edit</Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </>
  )
}
```

### Responsive Modal
```tsx
// Full-screen on mobile, centered dialog on desktop
<Dialog>
  <DialogContent className="w-full h-full md:h-auto md:max-w-2xl md:rounded-lg">
    {/* Content */}
  </DialogContent>
</Dialog>
```

## Media Queries in CSS-in-JS

### Tailwind (with arbitrary values)
```tsx
<div className="w-full [@media(min-width:900px)]:w-1/2">
```

### Material UI sx prop
```tsx
<Box
  sx={{
    width: '100%',
    '@media (min-width: 768px)': {
      width: '50%'
    }
  }}
>
```

### Chakra UI
```tsx
<Box
  w="100%"
  sx={{
    '@media screen and (min-width: 768px)': {
      w: '50%'
    }
  }}
>
```

## Image Optimization

### Responsive Images
```tsx
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  priority
/>
```

### Picture Element
```tsx
<picture>
  <source media="(max-width: 768px)" srcSet="/mobile.jpg" />
  <source media="(max-width: 1200px)" srcSet="/tablet.jpg" />
  <img src="/desktop.jpg" alt="Responsive" />
</picture>
```

## Touch-Friendly Patterns

### Minimum Touch Target Size
```tsx
// 44x44px minimum (Apple HIG) or 48x48px (Material Design)
<button className="min-w-[44px] min-h-[44px] p-2">
  <Icon />
</button>
```

### Swipe Gestures
```tsx
import { useSwipeable } from 'react-swipeable'

const handlers = useSwipeable({
  onSwipedLeft: () => deleteTask(),
  onSwipedRight: () => completeTask(),
})

<div {...handlers} className="touch-pan-y">
  Swipeable task
</div>
```

## Performance Considerations

### Lazy Load Components
```tsx
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Skeleton />,
  ssr: false
})

// Only load on larger screens
const DesktopFeature = dynamic(() => import('./DesktopFeature'), {
  loading: () => null,
  ssr: false
})

function App() {
  const isDesktop = useMediaQuery('(min-width: 1024px)')

  return (
    <>
      {isDesktop && <DesktopFeature />}
    </>
  )
}
```

### Responsive Loading
```tsx
// Load smaller images on mobile
const imageSrc = useBreakpointValue({
  base: '/image-mobile.jpg',
  md: '/image-tablet.jpg',
  lg: '/image-desktop.jpg'
})

<Image src={imageSrc} alt="Responsive" />
```

## Testing Responsive Layouts

### Media Query Hooks
```tsx
// Tailwind
import { useMediaQuery } from 'react-responsive'

const isMobile = useMediaQuery({ maxWidth: 767 })
const isTablet = useMediaQuery({ minWidth: 768, maxWidth: 1023 })
const isDesktop = useMediaQuery({ minWidth: 1024 })

// Material UI
import useMediaQuery from '@mui/material/useMediaQuery'

const isMobile = useMediaQuery('(max-width:767px)')

// Chakra UI
import { useBreakpointValue } from '@chakra-ui/react'

const columns = useBreakpointValue({ base: 1, md: 2, lg: 3 })
```

## Accessibility in Responsive Design

```tsx
// Hide visually but keep for screen readers
<span className="sr-only md:not-sr-only">
  Desktop label
</span>

// Skip to main content
<a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4">
  Skip to main content
</a>

// Responsive focus states
<button className="focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 md:focus:ring-offset-4">
```
