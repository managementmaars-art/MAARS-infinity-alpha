---
title: Configure Nuxt Module Correctly
impact: HIGH
impactDescription: enables seamless Storyblok integration with Nuxt
tags: nuxt, vue, module, ssr, bridge, nuxt4
---

## Configure Nuxt Module Correctly

**Impact: HIGH (enables seamless Storyblok integration with Nuxt)**

The `@storyblok/nuxt` module provides auto-imports, component registration, and bridge handling. Configure it properly for SSR/SSG and Visual Editor support.

> **Nuxt 4 Support:** For full Nuxt 4 compatibility, use `@storyblok/nuxt` **v9** which includes:
> - Fixed Visual Editor Bridge (works with Nuxt 4's new `shallowRef` data handling)
> - Updated type definitions (`null` → `undefined`)
> - Support for Nuxt 4's new `app/` directory structure
> - For Storyblok Bridge to work with Nuxt 4's Nitro server, set `deep: true` in `useAsyncStoryblok` options

**Incorrect (manual setup without module):**

```javascript
// Bad: Manual plugin without module features
// plugins/storyblok.js
import { StoryblokVue, apiPlugin } from '@storyblok/vue';

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(StoryblokVue, {
    accessToken: 'token'
    // Missing: bridge, components, SSR handling
  });
});

// Bad: Using wrong composable
const { data } = await useFetch('/api/storyblok/story');
// Doesn't handle bridge or live editing
```

**Correct (proper Nuxt module setup):**

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@storyblok/nuxt'],

  storyblok: {
    accessToken: process.env.STORYBLOK_TOKEN,
    bridge: true, // Enable Visual Editor bridge
    devtools: true, // Enable Storyblok devtools
    apiOptions: {
      region: '' // 'us' or 'cn' if applicable
    }
  },

  // For US or China regions
  // storyblok: {
  //   accessToken: process.env.STORYBLOK_TOKEN,
  //   apiOptions: {
  //     region: 'us'
  //   }
  // }
});
```

```vue
<!-- Good: storyblok/Hero.vue - Auto-registered component -->
<!-- Components in storyblok/ folder are auto-registered -->
<template>
  <section v-editable="blok" class="hero">
    <h1>{{ blok.title }}</h1>
    <p>{{ blok.subtitle }}</p>
    <NuxtImg
      v-if="blok.image?.filename"
      :src="blok.image.filename"
      :alt="blok.image.alt"
      provider="storyblok"
      width="800"
      height="600"
    />
  </section>
</template>

<script setup>
defineProps({
  blok: Object
});
</script>
```

```vue
<!-- Good: pages/[...slug].vue - Dynamic page with SSR -->
<template>
  <div>
    <StoryblokComponent v-if="story" :blok="story.content" />
  </div>
</template>

<script setup>
const route = useRoute();

// Detect Visual Editor
const isPreview = computed(() => {
  return route.query._storyblok !== undefined;
});

// Determine slug
const slug = computed(() => {
  const path = route.path === '/' ? 'home' : route.path.slice(1);
  return path;
});

// Fetch story with bridge support
const story = await useAsyncStoryblok(
  slug.value,
  {
    version: isPreview.value ? 'draft' : 'published',
    resolve_relations: ['article.author', 'article.categories']
  },
  {
    // Custom bridge config
    resolveRelations: ['article.author', 'article.categories'],
    // Required for Nuxt 4 bridge compatibility
    deep: true
  }
);

// Handle 404
if (!story.value) {
  throw createError({
    statusCode: 404,
    message: 'Page not found'
  });
}

// SEO meta
useHead({
  title: story.value.content.seo_title || story.value.name,
  meta: [
    {
      name: 'description',
      content: story.value.content.seo_description
    }
  ]
});
</script>
```

```vue
<!-- Good: Nested blocks with StoryblokComponent -->
<!-- storyblok/Page.vue -->
<template>
  <main v-editable="blok">
    <StoryblokComponent
      v-for="section in blok.body"
      :key="section._uid"
      :blok="section"
    />
  </main>
</template>

<script setup>
defineProps({
  blok: Object
});
</script>
```

```typescript
// Good: server/api/revalidate.post.ts - ISR webhook
export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const secret = getHeader(event, 'x-storyblok-secret');

  if (secret !== process.env.STORYBLOK_WEBHOOK_SECRET) {
    throw createError({ statusCode: 401, message: 'Unauthorized' });
  }

  if (body.action === 'published') {
    // Clear Nuxt cache
    const storage = useStorage();
    await storage.clear();

    // Or use Nitro cache
    // await useNitroApp().hooks.callHook('nitro:cache:purge');
  }

  return { revalidated: true };
});
```

```typescript
// Good: composables/useStoryblokImage.ts - Image optimization
export const useStoryblokImage = () => {
  const optimizeImage = (
    src: string,
    width: number,
    height: number = 0,
    quality: number = 80
  ) => {
    if (!src) return '';
    return `${src}/m/${width}x${height}/filters:quality(${quality})`;
  };

  return { optimizeImage };
};
```

**Module configuration options:**

| Option | Description | Default |
|--------|-------------|---------|
| `accessToken` | API access token | Required |
| `bridge` | Enable Visual Editor bridge | `true` |
| `devtools` | Enable Storyblok devtools | `false` |
| `apiOptions.region` | Space region (us, cn) | `''` (EU) |
| `apiOptions.https` | Use HTTPS | `true` |

**Auto-registration:**

Components in the `storyblok/` directory are automatically registered with names matching Storyblok component names:
- `storyblok/Hero.vue` → `hero`
- `storyblok/FeatureGrid.vue` → `feature_grid`
- `storyblok/ArticleCard.vue` → `article_card`

```typescript
// Good: Nuxt 4 configuration
// nuxt.config.ts
export default defineNuxtConfig({
  // Nuxt 4 compatibility (for Nuxt 3.15+)
  future: {
    compatibilityVersion: 4
  },
  compatibilityDate: '2026-01-10', // Required for Nuxt 4 behaviors

  modules: ['@storyblok/nuxt', '@nuxt/image'],

  storyblok: {
    accessToken: process.env.STORYBLOK_TOKEN,
    bridge: true,
    devtools: true
  },

  // NuxtImg provider for Storyblok
  image: {
    storyblok: {
      baseURL: 'https://a.storyblok.com'
    }
  }
});
```

```vue
<!-- Good: NuxtImg with Storyblok provider -->
<template>
  <NuxtImg
    v-if="blok.image?.filename"
    provider="storyblok"
    :src="blok.image.filename"
    :alt="blok.image.alt || ''"
    :width="800"
    :height="600"
    :modifiers="{ quality: 80 }"
    loading="lazy"
    format="webp"
  />
</template>

<!-- Responsive with sizes -->
<template>
  <NuxtPicture
    provider="storyblok"
    :src="blok.image.filename"
    :alt="blok.image.alt"
    sizes="sm:100vw md:50vw lg:800px"
    :modifiers="{ quality: 80 }"
    format="webp"
  />
</template>
```

```typescript
// Good: Nuxt DevTools Storyblok tab integration
// The @storyblok/nuxt module automatically adds a DevTools tab
// showing current story data and component tree

// Access via Nuxt DevTools (Shift+Alt+D)
// Tab: "Storyblok" shows:
// - Current story content
// - Component hierarchy
// - API cache status
```

```vue
<!-- Good: Nuxt 4 - Using new data fetching patterns -->
<script setup>
// Nuxt 4 recommends using useAsyncData with clear keys
const route = useRoute();
const slug = computed(() => route.path === '/' ? 'home' : route.path.slice(1));

const { data: story, error } = await useAsyncData(
  `storyblok-${slug.value}`,
  () => useStoryblokApi().get(`cdn/stories/${slug.value}`, {
    version: route.query._storyblok ? 'draft' : 'published',
    resolve_relations: ['article.author']
  }).then(res => res.data.story),
  {
    watch: [slug] // Re-fetch when slug changes
  }
);

// Handle errors
if (error.value) {
  throw createError({
    statusCode: 404,
    message: 'Story not found'
  });
}
</script>
```

```typescript
// Good: Type-safe composable for Storyblok
// composables/useStoryblokContent.ts
import type { ISbStoryData } from '@storyblok/vue';

export const useStoryblokContent = async <T>(
  slug: string,
  options: {
    version?: 'draft' | 'published';
    resolveRelations?: string[];
  } = {}
) => {
  const route = useRoute();
  const isPreview = computed(() => route.query._storyblok !== undefined);

  const { data, error, refresh } = await useAsyncData<ISbStoryData<T>>(
    `story-${slug}`,
    async () => {
      const response = await useStoryblokApi().get(`cdn/stories/${slug}`, {
        version: options.version || (isPreview.value ? 'draft' : 'published'),
        resolve_relations: options.resolveRelations?.join(',')
      });
      return response.data.story;
    }
  );

  return { story: data, error, refresh, isPreview };
};
```

Reference: [@storyblok/nuxt](https://www.storyblok.com/docs/packages/storyblok-nuxt)
