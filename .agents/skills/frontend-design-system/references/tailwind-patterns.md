# Tailwind CSS Design Patterns

## Responsive Design Principles

### Mobile-First Breakpoints
```tsx
// ✅ Good: Mobile-first, scale up
<div className="w-full md:w-1/2 lg:w-1/3 xl:w-1/4">

// Breakpoints:
// sm: 640px  - phones landscape
// md: 768px  - tablets
// lg: 1024px - laptops
// xl: 1280px - desktops
// 2xl: 1536px - large screens
```

### Layout Patterns

#### Grid Layouts
```tsx
// Responsive grid: 1→2→3 columns
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// Auto-fit grid (fills space)
<div className="grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-4">
```

#### Flexbox Patterns
```tsx
// Responsive navigation
<nav className="flex flex-col md:flex-row items-start md:items-center gap-4">
  <Logo />
  <div className="flex gap-2 md:ml-auto">
    <Button>Action</Button>
  </div>
</nav>

// Center content
<div className="flex items-center justify-center min-h-screen">

// Space between
<div className="flex justify-between items-center">
```

### Design Tokens

#### Spacing Scale
```tsx
const spacing = {
  tight: "space-y-2",    // 8px
  normal: "space-y-4",   // 16px
  relaxed: "space-y-6",  // 24px
  loose: "space-y-8"     // 32px
}
```

#### Typography Scale
```tsx
const text = {
  xs: "text-xs",      // 0.75rem
  sm: "text-sm",      // 0.875rem
  base: "text-base",  // 1rem
  lg: "text-lg",      // 1.125rem
  xl: "text-xl",      // 1.25rem
  "2xl": "text-2xl"   // 1.5rem
}
```

#### Color Patterns
```tsx
// Semantic colors
<Button className="bg-primary text-primary-foreground hover:bg-primary/90">
<Alert className="bg-destructive/10 text-destructive border-destructive/20">

// Opacity modifiers
<div className="bg-slate-900/95 backdrop-blur-sm">
```

### Component Patterns

#### Card Component
```tsx
<div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
  <h3 className="text-2xl font-semibold leading-none tracking-tight">
    Title
  </h3>
  <p className="text-sm text-muted-foreground mt-2">
    Description
  </p>
</div>
```

#### Button Variants
```tsx
// Primary
<button className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">

// Outline
<button className="border border-input bg-background hover:bg-accent hover:text-accent-foreground">

// Ghost
<button className="hover:bg-accent hover:text-accent-foreground">
```

#### Input Fields
```tsx
<input className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" />
```

### Animations & Transitions
```tsx
// Smooth transitions
<button className="transition-all duration-200 hover:scale-105">

// Fade in
<div className="animate-in fade-in duration-300">

// Slide in from bottom
<div className="animate-in slide-in-from-bottom-4 duration-500">
```

### Accessibility Patterns
```tsx
// Screen reader only
<span className="sr-only">Hidden text for screen readers</span>

// Focus visible
<button className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">

// Disabled states
<button className="disabled:cursor-not-allowed disabled:opacity-50">
```

### Dark Mode Support
```tsx
// Color scheme variants
<div className="bg-white dark:bg-slate-950">
<p className="text-slate-900 dark:text-slate-50">

// Theme-aware icons
<SunIcon className="rotate-0 scale-100 dark:-rotate-90 dark:scale-0" />
<MoonIcon className="rotate-90 scale-0 dark:rotate-0 dark:scale-100" />
```
