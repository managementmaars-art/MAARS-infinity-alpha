# Next.js Performance Patterns

Framework-specific guidance for Next.js applications.

## Image Optimization

### Use next/image

**Issue:** Raw `<img>` tags bypass Next.js optimization.

```jsx
// Bad: No optimization
<img src="/hero.png" alt="Hero" />

// Good: Automatic optimization
import Image from 'next/image';

<Image
  src="/hero.png"
  alt="Hero"
  width={1200}
  height={800}
  priority // For LCP images
/>
```

**Key props:**
- `priority`: Preload LCP images (above fold)
- `loading="lazy"`: Default, defer offscreen images
- `placeholder="blur"`: Prevent CLS with blur-up
- `sizes`: Optimize for responsive layouts

### Common next/image mistakes

```jsx
// Mistake: Missing priority on hero
<Image src="/hero.jpg" ... /> // Should have priority

// Mistake: fill without container sizing
<Image src="/bg.jpg" fill /> // Parent needs position: relative + dimensions

// Mistake: Unoptimized external images
// Add domain to next.config.js images.remotePatterns
```

## Route-Level Code Splitting

### App Router (Recommended)

App Router automatically code-splits by route.

```
app/
  page.tsx          → /
  dashboard/
    page.tsx        → /dashboard (separate chunk)
  settings/
    page.tsx        → /settings (separate chunk)
```

**Loading states:**
```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return <DashboardSkeleton />;
}
```

### Pages Router

```jsx
// pages/dashboard.tsx
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('../components/HeavyChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false // If not needed for SEO
});
```

## Server Components vs Client Components

### Default to Server Components

```tsx
// app/page.tsx (Server Component by default)
async function Page() {
  const data = await fetchData(); // No client bundle impact
  return <StaticContent data={data} />;
}
```

### Minimize 'use client' Boundaries

```tsx
// Bad: Entire page client-side
'use client';
export default function Page() { ... }

// Good: Only interactive parts client-side
// app/page.tsx (Server)
import { InteractiveWidget } from './InteractiveWidget';

export default function Page() {
  return (
    <div>
      <StaticHeader />
      <InteractiveWidget /> {/* Only this is 'use client' */}
      <StaticFooter />
    </div>
  );
}
```

## Font Optimization

### Use next/font

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export default function RootLayout({ children }) {
  return (
    <html className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
```

**Benefits:**
- Self-hosted (no external requests)
- Automatic `font-display: swap`
- Prevents layout shift
- Preloaded in `<head>`

## Script Optimization

### Use next/script

```tsx
import Script from 'next/script';

// Defer non-critical scripts
<Script
  src="https://analytics.example.com/script.js"
  strategy="lazyOnload"
/>

// After interactive (default for most third-party)
<Script
  src="https://widget.example.com/embed.js"
  strategy="afterInteractive"
/>

// Before interactive (rare, only if truly critical)
<Script
  src="/critical.js"
  strategy="beforeInteractive"
/>
```

## Hydration Issues

### Hydration Mismatch Debugging

```tsx
// Common cause: Date/time rendering
// Bad: Different server vs client
<span>{new Date().toLocaleString()}</span>

// Good: Suppress hydration for dynamic content
'use client';
import { useEffect, useState } from 'react';

function ClientDate() {
  const [date, setDate] = useState<string | null>(null);

  useEffect(() => {
    setDate(new Date().toLocaleString());
  }, []);

  if (!date) return <span>Loading...</span>;
  return <span>{date}</span>;
}
```

### Layout Shifts During Hydration

```tsx
// Problem: useEffect changes layout
useEffect(() => {
  setShowBanner(true); // Causes CLS
}, []);

// Solution: CSS-based initial state
// Or: Include in server render
export default function Page() {
  return (
    <>
      <Banner /> {/* Always render, hide with CSS if needed */}
      <Content />
    </>
  );
}
```

## Data Fetching Patterns

### Fetch in Server Components

```tsx
// app/products/page.tsx
async function ProductsPage() {
  // This fetch happens at build/request time, not client-side
  const products = await fetch('https://api.example.com/products', {
    next: { revalidate: 3600 } // ISR: revalidate every hour
  }).then(r => r.json());

  return <ProductList products={products} />;
}
```

### Parallel Data Fetching

```tsx
// Bad: Sequential (waterfall)
const user = await getUser();
const posts = await getPosts(user.id);

// Good: Parallel when possible
const [user, posts] = await Promise.all([
  getUser(),
  getPosts() // If doesn't depend on user
]);
```

## Static vs Dynamic

### Force Static Generation

```tsx
// app/page.tsx
export const dynamic = 'force-static';
export const revalidate = 3600; // ISR

async function Page() {
  const data = await fetchData();
  return <Content data={data} />;
}
```

### When Dynamic is Needed

```tsx
// Only use dynamic for:
// - User-specific content
// - Real-time data
// - Request-dependent logic

export const dynamic = 'force-dynamic';
// or use cookies(), headers(), searchParams
```

## Bundle Analysis

### Analyze Bundle

```bash
# Install analyzer
npm install @next/bundle-analyzer

# next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});
module.exports = withBundleAnalyzer(nextConfig);

# Run analysis
ANALYZE=true npm run build
```

### Common Bundle Bloat

```tsx
// Bad: Import entire library
import { format } from 'date-fns'; // Imports all of date-fns

// Good: Import specific function
import format from 'date-fns/format';

// Bad: Heavy library for simple task
import moment from 'moment'; // ~300KB

// Good: Native or lighter alternative
new Intl.DateTimeFormat('en-US').format(date);
```

## Performance Checklist

### Build Time
- [ ] `next build` completes without errors
- [ ] Bundle size warnings addressed
- [ ] Static pages generated where possible

### LCP
- [ ] Hero image uses `<Image priority>`
- [ ] Fonts preloaded via `next/font`
- [ ] Critical CSS inlined (automatic)

### CLS
- [ ] All images have width/height or aspect-ratio
- [ ] Fonts use `display: swap`
- [ ] No layout shifts during hydration

### INP
- [ ] Heavy components lazy loaded
- [ ] Event handlers don't block
- [ ] `use client` boundaries minimized

### General
- [ ] Third-party scripts use `next/script`
- [ ] API routes optimized
- [ ] ISR/caching configured appropriately
