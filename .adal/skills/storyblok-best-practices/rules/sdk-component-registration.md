---
title: Register All Components Globally
impact: CRITICAL
impactDescription: enables dynamic component rendering with StoryblokComponent
tags: sdk, components, registration, StoryblokComponent, v5
---

## Register All Components Globally

**Impact: CRITICAL (enables dynamic component rendering with StoryblokComponent)**

Components must be registered with the SDK during initialization to be rendered dynamically via `StoryblokComponent`. Missing registrations cause runtime errors.

> **@storyblok/react v5+:** For React Server Components, use `StoryblokServerComponent` from `@storyblok/react/rsc` instead of `StoryblokComponent`.

**Incorrect (missing or partial registration):**

```jsx
// Bad: Components not registered
import { storyblokInit, apiPlugin } from '@storyblok/react';

storyblokInit({
  accessToken: process.env.STORYBLOK_TOKEN,
  use: [apiPlugin]
  // No components registered!
});

// Results in: Component "hero" not found
```

```jsx
// Bad: Lazy registration that breaks SSR
import { storyblokInit } from '@storyblok/react';

// Dynamically importing at runtime causes issues
const loadComponent = async (name) => {
  const component = await import(`./components/${name}`);
  // Too late - component already needed for render
};
```

**Correct (complete component registration):**

```jsx
// Good: React - Register all components during init
import { storyblokInit, apiPlugin } from '@storyblok/react';

// Import all components
import Page from './components/Page';
import Hero from './components/Hero';
import FeatureGrid from './components/FeatureGrid';
import FeatureCard from './components/FeatureCard';
import Testimonials from './components/Testimonials';
import CtaSection from './components/CtaSection';
import RichText from './components/RichText';

storyblokInit({
  accessToken: process.env.STORYBLOK_TOKEN,
  use: [apiPlugin],
  components: {
    page: Page,
    hero: Hero,
    feature_grid: FeatureGrid,
    feature_card: FeatureCard,
    testimonials: Testimonials,
    cta_section: CtaSection,
    rich_text: RichText
  }
});
```

```jsx
// Good: Organized component registry
// components/index.js
import Page from './Page';
import Hero from './Hero';
import FeatureGrid from './FeatureGrid';
import FeatureCard from './FeatureCard';
import Testimonials from './Testimonials';
import CtaSection from './CtaSection';

export const components = {
  page: Page,
  hero: Hero,
  feature_grid: FeatureGrid,
  feature_card: FeatureCard,
  testimonials: Testimonials,
  cta_section: CtaSection
};

// lib/storyblok.js
import { storyblokInit, apiPlugin } from '@storyblok/react';
import { components } from '../components';

storyblokInit({
  accessToken: process.env.STORYBLOK_TOKEN,
  use: [apiPlugin],
  components
});

export { getStoryblokApi } from '@storyblok/react';
```

```vue
<!-- Good: Nuxt - Auto-registration via storyblok/ directory -->
<!-- nuxt.config.ts -->
export default defineNuxtConfig({
  modules: ['@storyblok/nuxt'],
  storyblok: {
    accessToken: process.env.STORYBLOK_TOKEN
  }
});

<!-- Components in storyblok/ folder are auto-registered -->
<!-- storyblok/Hero.vue - matches "hero" component -->
<!-- storyblok/FeatureGrid.vue - matches "feature_grid" component -->
```

**Using StoryblokComponent:**

```jsx
// Good: Render nested blocks dynamically
import { StoryblokComponent } from '@storyblok/react';

const Page = ({ blok }) => {
  return (
    <main {...storyblokEditable(blok)}>
      {blok.body?.map((nestedBlok) => (
        <StoryblokComponent blok={nestedBlok} key={nestedBlok._uid} />
      ))}
    </main>
  );
};
```

**Component name mapping:**

| Storyblok Name | React Component | File Name |
|----------------|-----------------|-----------|
| `hero` | `Hero` | `Hero.jsx` |
| `feature_grid` | `FeatureGrid` | `FeatureGrid.jsx` |
| `cta_section` | `CtaSection` | `CtaSection.jsx` |

Reference: [StoryblokComponent](https://www.storyblok.com/docs/packages/storyblok-react#storyblokcomponent)
