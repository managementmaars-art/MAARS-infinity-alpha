---
title: Handle Draft and Published Content Correctly
impact: CRITICAL
impactDescription: ensures editors see drafts while users see published content
tags: draft, published, version, preview, production
---

## Handle Draft and Published Content Correctly

**Impact: CRITICAL (ensures editors see drafts while users see published content)**

Use `version: 'draft'` with preview tokens for the Visual Editor and `version: 'published'` with public tokens for production. Mixing these causes stale content or exposed drafts.

**Incorrect (wrong version/token combinations):**

```jsx
// Bad: Using draft in production
const fetchStory = async (slug) => {
  const response = await fetch(
    `https://api.storyblok.com/v2/cdn/stories/${slug}?token=${PREVIEW_TOKEN}&version=draft`
  );
  // Draft content visible to all users!
};

// Bad: Using published in Visual Editor
const fetchForEditor = async (slug) => {
  const response = await fetch(
    `https://api.storyblok.com/v2/cdn/stories/${slug}?token=${PUBLIC_TOKEN}&version=published`
  );
  // Editor can't see their unpublished changes!
};

// Bad: Hardcoded version
const getStory = () => {
  return storyblokApi.get(`cdn/stories/home`, {
    version: 'published' // Always published, even in preview
  });
};
```

**Correct (environment-aware version handling):**

```jsx
// Good: Next.js - Environment-based configuration
// lib/storyblok.js
import { storyblokInit, apiPlugin } from '@storyblok/react';

const isPreview = process.env.STORYBLOK_IS_PREVIEW === 'true';

storyblokInit({
  accessToken: process.env.STORYBLOK_TOKEN,
  use: [apiPlugin]
});

export function getStoryblokApi() {
  return storyblokApi;
}

export const storyblokVersion = isPreview ? 'draft' : 'published';
```

```jsx
// Good: Next.js App Router - Draft mode integration
// app/api/preview/route.js
import { draftMode } from 'next/headers';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const secret = searchParams.get('secret');
  const slug = searchParams.get('slug');

  if (secret !== process.env.STORYBLOK_PREVIEW_SECRET) {
    return new Response('Invalid token', { status: 401 });
  }

  draftMode().enable();
  return Response.redirect(new URL(`/${slug}`, request.url));
}

// app/[...slug]/page.jsx
import { draftMode } from 'next/headers';

export default async function Page({ params }) {
  const { isEnabled: isDraft } = draftMode();

  const { data } = await getStoryblokApi().get(`cdn/stories/${params.slug}`, {
    version: isDraft ? 'draft' : 'published',
    cv: isDraft ? Date.now() : undefined // Bypass cache for drafts
  });

  return <StoryblokStory story={data.story} />;
}
```

```jsx
// Good: Detect Visual Editor context
const isInStoryblokEditor = () => {
  if (typeof window === 'undefined') return false;
  return window.location.search.includes('_storyblok');
};

const fetchStory = async (slug) => {
  const isEditor = isInStoryblokEditor();

  const { data } = await storyblokApi.get(`cdn/stories/${slug}`, {
    version: isEditor ? 'draft' : 'published',
    token: isEditor
      ? process.env.NEXT_PUBLIC_STORYBLOK_PREVIEW_TOKEN
      : process.env.NEXT_PUBLIC_STORYBLOK_PUBLIC_TOKEN
  });

  return data.story;
};
```

```vue
<!-- Good: Nuxt - Automatic handling -->
<script setup>
const route = useRoute();
const isPreview = route.query._storyblok !== undefined;

const story = await useAsyncStoryblok(
  route.path === '/' ? 'home' : route.path,
  {
    version: isPreview ? 'draft' : 'published',
    resolve_relations: ['article.author']
  }
);
</script>
```

**Environment configuration:**

```env
# Preview/Staging environment
STORYBLOK_TOKEN=preview-token-here
STORYBLOK_IS_PREVIEW=true

# Production environment
STORYBLOK_TOKEN=public-token-here
STORYBLOK_IS_PREVIEW=false
```

**Token and version matrix:**

| Environment | Token Type | Version | Cache |
|-------------|------------|---------|-------|
| Production | Public | `published` | Enabled |
| Staging | Preview | `draft` | Disabled |
| Visual Editor | Preview | `draft` | Disabled |
| Local Dev | Preview | `draft` | Disabled |

Reference: [Authentication](https://www.storyblok.com/docs/api/content-delivery/v2/getting-started/authentication)
