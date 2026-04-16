---
title: Integrate with Next.js App Router
impact: HIGH
impactDescription: enables modern React Server Components with Storyblok
tags: nextjs, app-router, rsc, server-components, next15
---

## Integrate with Next.js App Router

**Impact: HIGH (enables modern React Server Components with Storyblok)**

Next.js App Router requires specific patterns for React Server Components. Use `@storyblok/react/rsc` for server components and set up client providers correctly. Updated for Next.js 15 with async request APIs.

> **@storyblok/react v5+:** The React SDK v5 removed legacy richtext (use `@storyblok/richtext` instead). For RSC, use `StoryblokServerComponent` from `@storyblok/react/rsc` or `StoryblokStory` for story-level rendering.

**Incorrect (mixing client/server patterns):**

```jsx
// Bad: Using hooks in server component
// app/[...slug]/page.jsx
import { useStoryblokState } from '@storyblok/react';

export default async function Page({ params }) {
  const story = await fetchStory(params.slug);
  const liveStory = useStoryblokState(story); // Error: hooks in server component!
  return <StoryblokComponent blok={liveStory.content} />;
}

// Bad: Not separating client/server initialization
import { storyblokInit } from '@storyblok/react';

storyblokInit({
  accessToken: process.env.STORYBLOK_TOKEN,
  // Runs on server but components need client registration
});
```

**Correct (proper App Router integration):**

```jsx
// Good: lib/storyblok.js - Shared initialization
import { storyblokInit, apiPlugin } from '@storyblok/react/rsc';

export const getStoryblokApi = storyblokInit({
  accessToken: process.env.STORYBLOK_TOKEN,
  use: [apiPlugin]
});
```

```jsx
// Good: components/StoryblokProvider.jsx - Client provider
'use client';

import { storyblokInit, apiPlugin } from '@storyblok/react';
import Hero from './storyblok/Hero';
import FeatureGrid from './storyblok/FeatureGrid';
import RichText from './storyblok/RichText';

storyblokInit({
  accessToken: process.env.NEXT_PUBLIC_STORYBLOK_TOKEN,
  use: [apiPlugin],
  components: {
    hero: Hero,
    feature_grid: FeatureGrid,
    rich_text: RichText
  },
  bridge: true
});

export default function StoryblokProvider({ children }) {
  return children;
}
```

```jsx
// Good: app/layout.jsx - Root layout with provider
import StoryblokProvider from '@/components/StoryblokProvider';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <StoryblokProvider>{children}</StoryblokProvider>
      </body>
    </html>
  );
}
```

```jsx
// Good: app/[[...slug]]/page.jsx - Server Component page
import { getStoryblokApi } from '@/lib/storyblok';
import { StoryblokStory } from '@storyblok/react/rsc';
import { draftMode } from 'next/headers';

export async function generateStaticParams() {
  const storyblokApi = getStoryblokApi();
  const { data } = await storyblokApi.get('cdn/links', {
    version: 'published'
  });

  const paths = Object.values(data.links)
    .filter((link) => !link.is_folder)
    .map((link) => ({
      slug: link.slug === 'home' ? [] : link.slug.split('/')
    }));

  return paths;
}

export default async function Page({ params }) {
  const { slug } = await params; // Next.js 15: params is async
  const draft = await draftMode();
  const isDraft = draft.isEnabled;
  const resolvedSlug = slug?.join('/') || 'home';

  const storyblokApi = getStoryblokApi();
  const { data } = await storyblokApi.get(`cdn/stories/${resolvedSlug}`, {
    version: isDraft ? 'draft' : 'published',
    cv: isDraft ? Date.now() : undefined
  });

  if (!data?.story) {
    notFound();
  }

  return <StoryblokStory story={data.story} />;
}

export async function generateMetadata({ params }) {
  const { slug } = await params; // Next.js 15: params is async
  const resolvedSlug = slug?.join('/') || 'home';
  const storyblokApi = getStoryblokApi();

  try {
    const { data } = await storyblokApi.get(`cdn/stories/${resolvedSlug}`, {
      version: 'published'
    });

    return {
      title: data.story.content.seo_title || data.story.name,
      description: data.story.content.seo_description
    };
  } catch {
    return { title: 'Page' };
  }
}
```

```jsx
// Good: app/api/draft/route.js - Draft mode API (Next.js 15)
import { draftMode } from 'next/headers';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const secret = searchParams.get('secret');
  const slug = searchParams.get('slug') || '';

  if (secret !== process.env.STORYBLOK_PREVIEW_SECRET) {
    return new Response('Invalid token', { status: 401 });
  }

  // Next.js 15: draftMode() is now async
  const draft = await draftMode();
  draft.enable();

  return new Response(null, {
    status: 307,
    headers: { Location: `/${slug}` }
  });
}

// app/api/exit-draft/route.js
export async function GET() {
  const draft = await draftMode();
  draft.disable();
  return new Response(null, {
    status: 307,
    headers: { Location: '/' }
  });
}
```

```jsx
// Good: Next.js 15 - Async params and searchParams
// app/[[...slug]]/page.jsx
import { getStoryblokApi } from '@/lib/storyblok';
import { StoryblokStory } from '@storyblok/react/rsc';
import { draftMode } from 'next/headers';
import { notFound } from 'next/navigation';

// Next.js 15: params is now a Promise
export default async function Page({ params }) {
  const { slug } = await params; // Await params in Next.js 15
  const draft = await draftMode();
  const isDraft = draft.isEnabled;

  const resolvedSlug = slug?.join('/') || 'home';
  const storyblokApi = getStoryblokApi();

  const { data } = await storyblokApi.get(`cdn/stories/${resolvedSlug}`, {
    version: isDraft ? 'draft' : 'published',
    cv: isDraft ? Date.now() : undefined
  });

  if (!data?.story) {
    notFound();
  }

  return <StoryblokStory story={data.story} />;
}

// Next.js 15: generateMetadata also receives async params
export async function generateMetadata({ params }) {
  const { slug } = await params;
  const resolvedSlug = slug?.join('/') || 'home';

  try {
    const storyblokApi = getStoryblokApi();
    const { data } = await storyblokApi.get(`cdn/stories/${resolvedSlug}`, {
      version: 'published'
    });

    return {
      title: data.story.content.seo_title || data.story.name,
      description: data.story.content.seo_description
    };
  } catch {
    return { title: 'Page' };
  }
}
```

```jsx
// Good: Server Actions for content operations
// app/actions/storyblok.js
'use server';

import { revalidatePath, revalidateTag } from 'next/cache';

export async function revalidateStoryblokContent(slug) {
  // Revalidate specific path
  revalidatePath(`/${slug}`);

  // Or revalidate by tag
  revalidateTag('storyblok-content');
}

export async function refreshAllContent() {
  revalidateTag('storyblok-content');
}
```

```jsx
// Good: Parallel routes for different content sections
// app/@hero/page.jsx - Parallel route for hero
export default async function HeroSlot() {
  const { data } = await storyblokApi.get('cdn/stories/home', {
    version: 'published'
  });

  const heroBlok = data.story.content.hero?.[0];
  return heroBlok ? <Hero blok={heroBlok} /> : null;
}

// app/layout.jsx - Using parallel routes
export default function Layout({ children, hero, sidebar }) {
  return (
    <div>
      {hero}
      <main>{children}</main>
      {sidebar}
    </div>
  );
}
```

```javascript
// Good: Turbopack compatibility (next.config.js)
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Turbopack is stable in Next.js 15
  // Enable with: next dev --turbo

  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'a.storyblok.com'
      }
    ]
  },

  // Experimental features for Storyblok
  experimental: {
    // Enable if using PPR (Partial Prerendering)
    ppr: true
  }
};

module.exports = nextConfig;
```

```jsx
// Good: Client component for live editing
// components/storyblok/Hero.jsx
'use client';

import { storyblokEditable } from '@storyblok/react';

export default function Hero({ blok }) {
  return (
    <section {...storyblokEditable(blok)} className="hero">
      <h1>{blok.title}</h1>
      <p>{blok.subtitle}</p>
    </section>
  );
}
```

**Architecture summary:**

| File | Type | Purpose |
|------|------|---------|
| `lib/storyblok.js` | Server | API initialization |
| `StoryblokProvider.jsx` | Client | Component registration |
| `app/layout.jsx` | Server | Wrap with provider |
| `app/[...slug]/page.jsx` | Server | Data fetching |
| `components/storyblok/*.jsx` | Client | Editable components |

Reference: [Next.js Integration](https://www.storyblok.com/docs/guides/nextjs)
