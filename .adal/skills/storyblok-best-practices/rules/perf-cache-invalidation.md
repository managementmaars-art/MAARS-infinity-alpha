---
title: Implement Proper Cache Invalidation
impact: CRITICAL
impactDescription: ensures fresh content while maintaining performance
tags: cache, invalidation, cdn, cv, performance
---

## Implement Proper Cache Invalidation

**Impact: CRITICAL (ensures fresh content while maintaining performance)**

Storyblok CDN caches responses. Use the cache version (`cv`) parameter and webhooks to ensure users see fresh content after publishing while maintaining fast delivery.

**Incorrect (cache-unaware implementation):**

```jsx
// Bad: No cache consideration
const fetchStory = async (slug) => {
  const response = await fetch(
    `https://api.storyblok.com/v2/cdn/stories/${slug}?token=${TOKEN}`
  );
  // Cached indefinitely - stale content after publish
};

// Bad: Always bypassing cache
const fetchStory = async (slug) => {
  const response = await fetch(
    `https://api.storyblok.com/v2/cdn/stories/${slug}?token=${TOKEN}&cv=${Date.now()}`
  );
  // Every request bypasses CDN - no caching benefit
};

// Bad: Static build without revalidation
export async function getStaticProps() {
  const story = await getStory('home');
  return { props: { story } };
  // Never updates until full rebuild
}
```

**Correct (proper cache management):**

```jsx
// Good: Use cv parameter from space settings
const fetchStory = async (slug) => {
  // First, get the current cache version
  const spaceResponse = await fetch(
    `https://api.storyblok.com/v2/cdn/spaces/me?token=${TOKEN}`
  );
  const { space } = await spaceResponse.json();
  const cv = space.version;

  // Then fetch content with cv
  const storyResponse = await fetch(
    `https://api.storyblok.com/v2/cdn/stories/${slug}?token=${TOKEN}&cv=${cv}`
  );
  return storyResponse.json();
};

// Good: Store cv globally and update via webhook
let cachedCv = null;

const getCacheVersion = async () => {
  if (cachedCv) return cachedCv;

  const { space } = await storyblokApi.get('cdn/spaces/me');
  cachedCv = space.version;
  return cachedCv;
};

// Webhook handler to invalidate
export async function POST(request) {
  const body = await request.json();

  if (body.action === 'published') {
    cachedCv = null; // Clear cached cv
    // Or: cachedCv = body.space_version;
  }
}
```

```jsx
// Good: Next.js ISR with on-demand revalidation
// app/[...slug]/page.jsx
export async function generateStaticParams() {
  const { data } = await storyblokApi.get('cdn/stories', {
    version: 'published',
    excluding_fields: 'body'
  });
  return data.stories.map((story) => ({
    slug: story.full_slug.split('/')
  }));
}

export default async function Page({ params }) {
  const { data } = await storyblokApi.get(`cdn/stories/${params.slug.join('/')}`, {
    version: 'published'
  });

  return <StoryblokStory story={data.story} />;
}

// app/api/revalidate/route.js
import { revalidatePath, revalidateTag } from 'next/cache';

export async function POST(request) {
  const body = await request.json();
  const secret = request.headers.get('x-webhook-secret');

  if (secret !== process.env.STORYBLOK_WEBHOOK_SECRET) {
    return Response.json({ error: 'Invalid secret' }, { status: 401 });
  }

  if (body.action === 'published') {
    const slug = body.full_slug || body.story?.full_slug;

    if (slug) {
      revalidatePath(`/${slug}`);
    } else {
      revalidateTag('storyblok'); // Revalidate all
    }
  }

  return Response.json({ revalidated: true });
}
```

```jsx
// Good: Nuxt with fetch caching
// nuxt.config.ts
export default defineNuxtConfig({
  storyblok: {
    accessToken: process.env.STORYBLOK_TOKEN,
    cacheProvider: 'memory' // Or 'custom'
  }
});

// composables/useStoryblokCache.ts
export const useStoryblokCache = () => {
  const { $storyblokApi } = useNuxtApp();

  const fetchWithCache = async (path, options) => {
    const cacheKey = `storyblok:${path}`;

    // Check Nuxt's built-in cache
    const cached = await useStorage().getItem(cacheKey);
    if (cached) return cached;

    const data = await $storyblokApi.get(path, options);
    await useStorage().setItem(cacheKey, data, { ttl: 60 });

    return data;
  };

  return { fetchWithCache };
};
```

**Cache strategy matrix:**

| Environment | Strategy | cv Parameter | TTL |
|-------------|----------|--------------|-----|
| Production | CDN + ISR | Required | 60s-3600s |
| Preview | No cache | `Date.now()` | 0 |
| Visual Editor | No cache | `Date.now()` | 0 |
| Static Build | Build-time | Fixed at build | ∞ |

**Webhook configuration:**

Configure in Storyblok Dashboard → Settings → Webhooks:
- Event: `story.published`, `story.unpublished`, `story.deleted`
- URL: `https://yoursite.com/api/revalidate`
- Secret: Shared secret for verification

Reference: [How Stories Are Cached](https://www.storyblok.com/faq/how-stories-are-cached-content-delivery-api)
