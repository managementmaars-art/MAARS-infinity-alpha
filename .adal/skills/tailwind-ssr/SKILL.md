---
name: tailwind-ssr
description: TailwindCSS v4 and SSR expert. Use when configuring TailwindCSS, implementing SSR strategies, optimizing critical CSS, or solving styling performance issues.
---

# TailwindCSS v4 & SSR Expert

Expert assistant for TailwindCSS v4 configuration, SSR/SSG styling strategies, critical CSS optimization, and frontend performance.

## Thinking Process

When activated, follow this structured thinking approach to solve TailwindCSS and SSR styling problems:

### Step 1: Version and Context Identification

**Goal:** Understand the exact TailwindCSS and framework context.

**Key Questions to Ask:**
- What TailwindCSS version? (v3 vs v4 have major differences)
- What frontend framework? (SvelteKit, Next.js, Nuxt, etc.)
- What rendering mode? (SSR, SSG, SPA, hybrid)
- What build tool? (Vite, Webpack, Turbopack)

**Actions:**
1. Check `package.json` for tailwindcss version
2. Review build configuration (vite.config, next.config)
3. Identify CSS entry point and import style

**Version Decision Matrix:**

| If | Then Use |
|----|----------|
| New project | TailwindCSS v4 (CSS-first) |
| Existing v3 project | Consider migration or stay on v3 |
| Legacy browser support needed | TailwindCSS v3 |

**Decision Point:** Document:
- "TailwindCSS version: [X]"
- "Framework: [Y] with [Z] rendering"

### Step 2: Problem Classification

**Goal:** Understand what type of styling challenge this is.

**Key Questions to Ask:**
- Is this a configuration problem? (setup, plugins, theme)
- Is this an SSR problem? (FOUC, hydration, critical CSS)
- Is this a performance problem? (bundle size, render blocking)
- Is this a design system problem? (tokens, variants, customization)

**Decision Point:** Classify to select appropriate solutions:
- Configuration → Check tailwind.config or CSS imports
- SSR → Analyze render timing and CSS delivery
- Performance → Review bundle and critical CSS strategy
- Design System → Design theme and variant structure

### Step 3: Configuration Analysis (v3 vs v4)

**Goal:** Ensure correct configuration for the version.

**TailwindCSS v4 (CSS-first):**
```css
/* app.css */
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.7 0.15 200);
  --font-display: "Inter", sans-serif;
}
```

**TailwindCSS v3 (JS-based):**
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
      },
    },
  },
}
```

**Migration Considerations:**
- v4 auto-detects content (no config needed)
- v4 uses CSS variables for theming
- v4 has new color functions (oklch)
- v4 requires modern browsers

### Step 4: SSR Styling Strategy

**Goal:** Ensure styles load correctly in SSR context.

**Thinking Framework:**
- "What CSS is needed for first paint?"
- "When is the stylesheet loaded?"
- "What causes Flash of Unstyled Content (FOUC)?"

**SSR Styling Timeline:**
```
Server Render → HTML with inline/critical CSS → Browser parses HTML
    → Download full CSS → Hydration → Interactive
```

**SSR Checklist:**
- [ ] CSS imported in layout/root component
- [ ] Critical CSS inlined or preloaded
- [ ] No style-dependent JavaScript before CSS loads
- [ ] Consistent class generation server/client

**Framework-Specific Patterns:**

| Framework | CSS Import Location |
|-----------|---------------------|
| SvelteKit | +layout.svelte or app.css |
| Next.js | app/layout.tsx or globals.css |
| Nuxt | nuxt.config.ts css array |

### Step 5: FOUC Prevention

**Goal:** Eliminate Flash of Unstyled Content.

**Thinking Framework:**
- "Is CSS render-blocking or async?"
- "What is the first meaningful paint showing?"
- "Is there content shift during hydration?"

**FOUC Causes and Solutions:**

| Cause | Solution |
|-------|----------|
| CSS loads async | Make critical CSS render-blocking |
| Dynamic classes | Ensure SSR includes all needed classes |
| Font loading | Use font-display: swap with preload |
| Theme switching | Inline theme detection script |

**Anti-FOUC Pattern:**
```html
<html class="no-js">
<head>
  <!-- Inline critical CSS -->
  <style>/* critical styles */</style>

  <!-- Theme detection before render -->
  <script>
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.classList.add(theme);
    document.documentElement.classList.remove('no-js');
  </script>

  <!-- Full CSS with preload -->
  <link rel="preload" href="/styles.css" as="style">
  <link rel="stylesheet" href="/styles.css">
</head>
```

### Step 6: Performance Optimization

**Goal:** Minimize CSS impact on performance.

**Thinking Framework:**
- "How large is the CSS bundle?"
- "What CSS is unused?"
- "What is render-blocking?"

**Performance Checklist:**
- [ ] PurgeCSS/content detection configured correctly
- [ ] No unused Tailwind plugins loaded
- [ ] Critical CSS extracted and inlined
- [ ] Non-critical CSS deferred
- [ ] Fonts optimized (subset, preload, swap)

**Bundle Analysis:**
```bash
# Check CSS size
npx tailwindcss -o output.css --minify
ls -lh output.css

# Analyze what's included
npx tailwindcss -o output.css --content ./src/**/*.{html,js,svelte}
```

**Optimization Strategies:**

| Strategy | When to Use |
|----------|-------------|
| Disable unused core plugins | Reduce base size |
| Use specific content globs | Faster builds, smaller output |
| Extract critical CSS | Improve FCP |
| Lazy load below-fold styles | Reduce initial CSS |

### Step 7: Theme and Design Token Strategy

**Goal:** Design a maintainable theming system.

**Thinking Framework:**
- "What needs to be customizable?"
- "How do we handle dark mode?"
- "What are the design system tokens?"

**Theme Architecture (v4):**
```css
@theme {
  /* Color tokens */
  --color-primary: oklch(0.6 0.2 250);
  --color-secondary: oklch(0.7 0.15 180);

  /* Semantic tokens */
  --color-background: var(--color-gray-50);
  --color-foreground: var(--color-gray-900);

  /* Spacing scale */
  --spacing-page: 2rem;
}

/* Dark mode overrides */
@media (prefers-color-scheme: dark) {
  :root {
    --color-background: var(--color-gray-900);
    --color-foreground: var(--color-gray-50);
  }
}
```

**Dark Mode Strategies:**

| Strategy | Implementation |
|----------|----------------|
| System preference | @media (prefers-color-scheme) |
| Class-based | Toggle .dark on html element |
| Hybrid | System default + user override |

### Step 8: Troubleshooting Framework

**Goal:** Systematically debug styling issues.

**Debugging Checklist:**

| Symptom | Check |
|---------|-------|
| Classes not applying | Content detection paths |
| FOUC on navigation | CSS import in layout |
| Hydration mismatch | Dynamic classes in SSR |
| Build too slow | Glob pattern specificity |
| Bundle too large | Unused plugins, content paths |

**Debug Commands:**
```bash
# Verify content detection
DEBUG=tailwindcss:content npx tailwindcss build

# Generate with verbose output
npx tailwindcss -i input.css -o output.css --verbose

# Check which classes are generated
grep -o 'class="[^"]*"' src/**/*.svelte | sort | uniq
```

## Documentation Resources

**Context7 Library IDs:**
- TailwindCSS v4: `/websites/tailwindcss` (2333 snippets)
- TailwindCSS v3: `/websites/v3_tailwindcss` (2691 snippets, Score: 85.9)

**Official Documentation:**
- Docs: `https://tailwindcss.com/docs`
- Upgrade Guide: `https://tailwindcss.com/docs/upgrade-guide`

## TailwindCSS v4 Key Changes

### CSS-First Configuration

```css
/* v4 uses CSS @import instead of @tailwind directives */
@import "tailwindcss";

/* Design tokens as CSS variables */
@theme {
  --color-primary: oklch(0.7 0.15 200);
  --font-display: "Inter", sans-serif;
  --breakpoint-3xl: 1920px;
}
```

### Automatic Content Detection

```css
/* v4 auto-detects content, no config needed */
/* Manual override if needed: */
@source "../components/**/*.tsx";
```

### New Features

```css
/* Container queries */
@container (min-width: 400px) {
  .card { /* styles */ }
}

/* 3D transforms */
.element {
  @apply rotate-x-45 perspective-500;
}

/* Modern color functions */
.button {
  background: oklch(0.7 0.15 200);
}
```

## SSR Performance Checklist

### Critical CSS
- [ ] Inline above-the-fold CSS
- [ ] Defer non-critical stylesheets
- [ ] Use `<link rel="preload">` for fonts

### Hydration
- [ ] Avoid layout shifts during hydration
- [ ] Match server and client class generation
- [ ] Test with JavaScript disabled

### FOUC Prevention
```html
<!-- Add loading state -->
<html class="no-js">
<head>
  <script>document.documentElement.classList.remove('no-js')</script>
  <style>.no-js .lazy-load { visibility: hidden; }</style>
</head>
```

## Framework Integration

### SvelteKit

```svelte
<!-- +layout.svelte -->
<script>
  import '../app.css';
</script>
```

```css
/* app.css */
@import "tailwindcss";
```

### Next.js

```tsx
// app/layout.tsx
import './globals.css';
```

```css
/* globals.css */
@import "tailwindcss";
```

## Performance Optimization

### PurgeCSS (Production)
```css
/* v4 handles this automatically */
/* Ensure all dynamic classes are detectable */
```

### Custom Variants
```css
@variant hocus (&:hover, &:focus);
@variant group-hocus (:merge(.group):hover &, :merge(.group):focus &);
```

### Reduce Bundle Size
```css
/* Disable unused core plugins */
@import "tailwindcss" layer(utilities);
@import "tailwindcss/preflight" layer(base);
```

## Browser Compatibility

**TailwindCSS v4 requires:**
- Safari 16.4+
- Chrome 111+
- Firefox 128+
- Edge 111+

## Present Results to User

When providing TailwindCSS solutions:
- Specify v3 vs v4 syntax differences
- Provide copy-paste ready configuration
- Consider SSR framework-specific integration
- Note browser compatibility requirements
- Include performance implications

## Troubleshooting

**"Styles not applying"**
- Check content detection paths
- Verify CSS import is correct
- Clear build cache

**"FOUC (Flash of Unstyled Content)"**
- Inline critical CSS
- Add proper preload hints
- Check hydration timing

**"Build too slow"**
- Reduce content glob patterns
- Use specific file extensions
- Enable caching in build tool
