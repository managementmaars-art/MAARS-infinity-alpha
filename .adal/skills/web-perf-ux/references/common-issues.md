# Common Performance Issues Catalog

Quick reference for diagnosing and fixing web performance issues. Each entry follows:
**Evidence → Root Cause → Fix → Verification**

---

## Images

### Unoptimized Images

**Evidence:**
- Lighthouse "Properly size images" or "Serve images in next-gen formats"
- Large transfer sizes for image resources (> 200KB for hero images)
- Network waterfall shows images as largest/slowest resources

**Root Cause:**
- Original resolution images served without resizing
- Using JPEG/PNG instead of WebP/AVIF
- No responsive images (`srcset`)

**Fix:**
```html
<!-- Before -->
<img src="hero.jpg" alt="Hero">

<!-- After -->
<img
  src="hero.webp"
  srcset="hero-400.webp 400w, hero-800.webp 800w, hero-1200.webp 1200w"
  sizes="(max-width: 768px) 100vw, 50vw"
  alt="Hero"
  width="1200"
  height="800"
  loading="lazy"
  decoding="async"
>
```

**Verification:**
- Image transfer sizes reduced by 50%+
- LCP improves if hero image was LCP element

### Images Causing CLS

**Evidence:**
- CLS > 0.1 with layout-shift entries pointing to `<img>` elements
- Images appear and push content down

**Root Cause:**
- Missing `width` and `height` attributes
- CSS doesn't reserve space

**Fix:**
```html
<!-- Always include dimensions -->
<img src="photo.jpg" width="800" height="600" alt="Photo">

<!-- Or use aspect-ratio in CSS -->
<style>
  .image-container {
    aspect-ratio: 4 / 3;
    width: 100%;
  }
</style>
```

**Verification:**
- CLS contribution from images drops to 0
- No visible layout jumps when images load

---

## JavaScript Bundle

### Large Initial Bundle

**Evidence:**
- Lighthouse "Reduce unused JavaScript"
- Main bundle > 200KB gzipped
- Long tasks during page load

**Root Cause:**
- No code splitting
- Unused libraries bundled
- All routes in single bundle

**Fix:**
```javascript
// Before: static import
import { HeavyChart } from './HeavyChart';

// After: dynamic import
const HeavyChart = lazy(() => import('./HeavyChart'));

// With Suspense boundary
<Suspense fallback={<ChartSkeleton />}>
  <HeavyChart />
</Suspense>
```

**Verification:**
- Initial bundle size reduced
- TBT/INP improves
- Bundle analyzer shows smaller main chunk

### Render-Blocking Scripts

**Evidence:**
- Lighthouse "Eliminate render-blocking resources"
- Scripts in `<head>` without `async`/`defer`
- FCP delayed

**Root Cause:**
- Synchronous script loading blocks parsing
- Third-party scripts in critical path

**Fix:**
```html
<!-- Before -->
<script src="analytics.js"></script>

<!-- After: non-critical scripts -->
<script src="analytics.js" defer></script>

<!-- Or async for independent scripts -->
<script src="analytics.js" async></script>
```

**Verification:**
- FCP improves
- Scripts no longer appear in render-blocking audit

### Long Tasks Blocking Main Thread

**Evidence:**
- TBT > 300ms
- Long tasks in Performance panel (> 50ms)
- INP > 200ms

**Root Cause:**
- Heavy synchronous computation
- Large component trees rendering at once
- JSON parsing of large datasets

**Fix:**
```javascript
// Before: blocking loop
items.forEach(item => processItem(item));

// After: yield to main thread
async function processInChunks(items) {
  for (let i = 0; i < items.length; i += 100) {
    const chunk = items.slice(i, i + 100);
    chunk.forEach(item => processItem(item));
    await new Promise(resolve => setTimeout(resolve, 0)); // Yield
  }
}
```

**Verification:**
- No long tasks > 50ms in critical path
- TBT/INP improves

---

## Fonts

### FOUT/FOIT (Flash of Unstyled/Invisible Text)

**Evidence:**
- Text appears unstyled then jumps to styled
- CLS contributions from text elements
- Lighthouse "Ensure text remains visible during webfont load"

**Root Cause:**
- No `font-display` strategy
- Fonts loaded late in cascade

**Fix:**
```css
/* Use font-display: swap or optional */
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2') format('woff2');
  font-display: swap; /* or optional for less CLS */
}
```

```html
<!-- Preload critical fonts -->
<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>
```

**Verification:**
- No visible font swap flash
- CLS from text reduced

### Too Many Font Variants

**Evidence:**
- Multiple font files loaded (> 4)
- Large total font transfer size (> 200KB)

**Root Cause:**
- Loading all weights/styles upfront
- Not subsetting fonts

**Fix:**
- Limit to 2-3 font weights max
- Use `unicode-range` for subsetting
- Consider variable fonts

**Verification:**
- Font transfer size < 100KB total
- Fewer font requests in waterfall

---

## CSS

### Render-Blocking CSS

**Evidence:**
- Lighthouse "Eliminate render-blocking resources" shows CSS
- Large external stylesheets
- FCP delayed

**Root Cause:**
- All CSS loaded synchronously
- Large CSS files block first paint

**Fix:**
```html
<!-- Inline critical CSS -->
<style>
  /* Critical above-fold styles */
  .hero { ... }
</style>

<!-- Defer non-critical CSS -->
<link rel="preload" href="styles.css" as="style" onload="this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="styles.css"></noscript>
```

**Verification:**
- FCP improves
- Critical content renders before full CSS loads

### Unused CSS

**Evidence:**
- Lighthouse "Reduce unused CSS"
- CSS coverage shows < 50% used

**Root Cause:**
- Framework CSS loaded entirely
- Old styles never removed
- Component libraries CSS bundled whole

**Fix:**
- Use PurgeCSS or similar
- Tree-shake component library CSS
- Split CSS per route

**Verification:**
- CSS transfer size reduced
- Coverage shows higher utilization

---

## Server & Network

### Slow TTFB

**Evidence:**
- TTFB > 800ms
- All metrics delayed
- Server response time in waterfall

**Root Cause:**
- Slow server-side processing
- No CDN or edge caching
- Database queries on critical path

**Fix:**
- Add CDN/edge caching
- Implement stale-while-revalidate
- Move computation to build time (SSG)
- Optimize database queries

**Verification:**
- TTFB < 200ms from edge
- Consistent across geographic regions

### No Resource Caching

**Evidence:**
- Lighthouse "Serve static assets with efficient cache policy"
- Repeat visits re-download same assets

**Root Cause:**
- Missing or short `Cache-Control` headers
- No content hashing in filenames

**Fix:**
```
# Static assets (hashed filenames)
Cache-Control: public, max-age=31536000, immutable

# HTML/API responses
Cache-Control: public, max-age=0, must-revalidate
```

**Verification:**
- Repeat visits show cached resources
- Lighthouse caching audit passes

### No Compression

**Evidence:**
- Lighthouse "Enable text compression"
- Large transfer sizes for text resources

**Root Cause:**
- Server not configured for gzip/brotli

**Fix:**
- Enable gzip/brotli at CDN or origin
- Most frameworks/hosts support this natively

**Verification:**
- Response headers show `Content-Encoding: br` or `gzip`
- Transfer sizes ~70% smaller than raw

---

## Third-Party Scripts

### Heavy Third-Party Impact

**Evidence:**
- Lighthouse "Reduce the impact of third-party code"
- Long tasks attributed to third-party domains
- Network shows many third-party requests

**Root Cause:**
- Analytics, ads, chat widgets loading eagerly
- Third-party scripts blocking main thread

**Fix:**
```javascript
// Defer third-party loading
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => loadAnalytics());
} else {
  setTimeout(loadAnalytics, 2000);
}

// Or use facade pattern
<button onClick={() => import('./chat-widget')}>
  Open Chat
</button>
```

**Verification:**
- Third-party scripts load after critical path
- TBT contribution from third parties reduced

---

## Hydration (SSR/SSG)

### Hydration Causing CLS

**Evidence:**
- CLS spikes during/after hydration
- Content re-renders after JS loads
- Layout shifts timed with JS execution

**Root Cause:**
- Client render differs from server render
- Dynamic content not pre-rendered
- useEffect causing immediate layout changes

**Fix:**
```javascript
// Ensure server/client consistency
// Avoid useLayoutEffect with dimension changes

// Use CSS for initial state, not JS
.skeleton { min-height: 200px; }

// Defer non-critical hydration
const DynamicComponent = dynamic(() => import('./Heavy'), {
  ssr: false,
  loading: () => <Skeleton />
});
```

**Verification:**
- CLS during hydration eliminated
- Server HTML matches initial client render

### Slow Hydration Blocking Interactivity

**Evidence:**
- INP poor on initial interactions
- Long tasks during hydration
- Page looks ready but doesn't respond

**Root Cause:**
- Large component tree hydrating at once
- Expensive effects running during hydration
- No progressive hydration

**Fix:**
```javascript
// Split hydration boundaries
// Use Suspense with SSR
<Suspense fallback={<Skeleton />}>
  <HeavySection />
</Suspense>

// Defer non-visible components
const BelowFold = lazy(() => import('./BelowFold'));
```

**Verification:**
- Hydration completes faster
- Initial interactions responsive
- TBT reduced
