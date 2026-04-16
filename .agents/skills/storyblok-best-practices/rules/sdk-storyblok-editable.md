---
title: Always Apply storyblokEditable to Components
impact: CRITICAL
impactDescription: enables Visual Editor click-to-edit functionality
tags: sdk, visual-editor, storyblokEditable, react, vue
---

## Always Apply storyblokEditable to Components

**Impact: CRITICAL (enables Visual Editor click-to-edit functionality)**

The `storyblokEditable()` function adds data attributes that make components clickable in the Visual Editor. Without it, editors cannot click on elements to edit them.

**Incorrect (missing storyblokEditable):**

```jsx
// Bad: React component without storyblokEditable
const Hero = ({ blok }) => {
  return (
    <section className="hero">
      <h1>{blok.title}</h1>
      <p>{blok.subtitle}</p>
    </section>
  );
};

// Bad: Vue component without v-editable
<template>
  <section class="hero">
    <h1>{{ blok.title }}</h1>
    <p>{{ blok.subtitle }}</p>
  </section>
</template>
```

**Correct (proper storyblokEditable usage):**

```jsx
// Good: React component with storyblokEditable
import { storyblokEditable } from '@storyblok/react';

const Hero = ({ blok }) => {
  return (
    <section {...storyblokEditable(blok)} className="hero">
      <h1>{blok.title}</h1>
      <p>{blok.subtitle}</p>
    </section>
  );
};

// Good: React Server Component (RSC)
import { storyblokEditable } from '@storyblok/react/rsc';

const Hero = ({ blok }) => {
  return (
    <section {...storyblokEditable(blok)} className="hero">
      <h1>{blok.title}</h1>
      <p>{blok.subtitle}</p>
    </section>
  );
};
```

```vue
<!-- Good: Vue component with v-editable directive -->
<template>
  <section v-editable="blok" class="hero">
    <h1>{{ blok.title }}</h1>
    <p>{{ blok.subtitle }}</p>
  </section>
</template>

<script setup>
defineProps({
  blok: Object
});
</script>
```

```astro
---
// Good: Astro component with storyblokEditable
import { storyblokEditable } from '@storyblok/astro';
const { blok } = Astro.props;
---

<section {...storyblokEditable(blok)} class="hero">
  <h1>{blok.title}</h1>
  <p>{blok.subtitle}</p>
</section>
```

**Framework patterns:**

| Framework | Import | Usage |
|-----------|--------|-------|
| React (Client) | `@storyblok/react` | `{...storyblokEditable(blok)}` |
| React (RSC) | `@storyblok/react/rsc` | `{...storyblokEditable(blok)}` |
| Vue | `@storyblok/vue` | `v-editable="blok"` |
| Nuxt | `@storyblok/nuxt` | `v-editable="blok"` |
| Astro | `@storyblok/astro` | `{...storyblokEditable(blok)}` |

**Nested components:**

```jsx
// Good: Apply to each nested component
const FeatureGrid = ({ blok }) => {
  return (
    <section {...storyblokEditable(blok)} className="feature-grid">
      <h2>{blok.headline}</h2>
      <div className="grid">
        {blok.features?.map((feature) => (
          <FeatureCard key={feature._uid} blok={feature} />
        ))}
      </div>
    </section>
  );
};

const FeatureCard = ({ blok }) => {
  return (
    <article {...storyblokEditable(blok)} className="feature-card">
      <h3>{blok.title}</h3>
      <p>{blok.description}</p>
    </article>
  );
};
```

Reference: [storyblokEditable](https://www.storyblok.com/docs/packages/storyblok-react#storyblokEditable)
