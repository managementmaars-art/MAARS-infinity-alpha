---
title: Configure the Storyblok Bridge Correctly
impact: CRITICAL
impactDescription: enables real-time visual editing experience
tags: bridge, visual-editor, real-time, preview
---

## Configure the Storyblok Bridge Correctly

**Impact: CRITICAL (enables real-time visual editing experience)**

The Storyblok Bridge enables real-time updates in the Visual Editor. Without proper configuration, editors won't see live changes as they type.

**Incorrect (missing or broken bridge setup):**

```jsx
// Bad: No bridge initialization
const Page = ({ story }) => {
  return <PageComponent blok={story.content} />;
};

// Bad: Bridge loaded in production
import { useEffect } from 'react';

const App = () => {
  useEffect(() => {
    // Always loads bridge, even in production
    const script = document.createElement('script');
    script.src = 'https://app.storyblok.com/f/storyblok-v2-latest.js';
    document.head.appendChild(script);
  }, []);
};

// Bad: Not handling bridge events
const storyblokInit = new StoryblokBridge();
// Missing event listeners for input/change/published
```

**Correct (proper bridge configuration):**

```jsx
// Good: React - Use SDK's built-in bridge handling
import { storyblokInit, apiPlugin, useStoryblokState } from '@storyblok/react';

storyblokInit({
  accessToken: process.env.STORYBLOK_PREVIEW_TOKEN,
  use: [apiPlugin],
  bridge: process.env.NODE_ENV !== 'production', // Only in dev/preview
  components: { /* ... */ }
});

// Page component with live updates
const Page = ({ story: initialStory }) => {
  // useStoryblokState enables live preview
  const story = useStoryblokState(initialStory);

  return <PageComponent blok={story.content} />;
};
```

```jsx
// Good: Next.js App Router - Conditional bridge loading
// components/StoryblokProvider.jsx
'use client';

import { storyblokInit, apiPlugin } from '@storyblok/react';
import { components } from './components';

storyblokInit({
  accessToken: process.env.NEXT_PUBLIC_STORYBLOK_TOKEN,
  use: [apiPlugin],
  components
});

export default function StoryblokProvider({ children }) {
  return children;
}

// app/layout.jsx
import StoryblokProvider from '@/components/StoryblokProvider';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <StoryblokProvider>{children}</StoryblokProvider>
      </body>
    </html>
  );
}
```

```jsx
// Good: Custom bridge configuration for fine-grained control
import { StoryblokBridge } from '@storyblok/js';

const initBridge = () => {
  const bridge = new StoryblokBridge({
    preventClicks: true,          // Prevent link navigation in editor
    resolveRelations: ['article.author', 'article.categories']
  });

  bridge.on('input', (event) => {
    // Live updates as editor types
    updateStory(event.story);
  });

  bridge.on('change', (event) => {
    // Content saved - could refresh data
    window.location.reload();
  });

  bridge.on('published', (event) => {
    // Content published - refresh to show published version
    window.location.reload();
  });

  bridge.on('enterEditmode', (event) => {
    // Entered edit mode
    loadDraftContent(event.storyId);
  });
};
```

```vue
<!-- Good: Nuxt - Built-in bridge support -->
<script setup>
const story = await useAsyncStoryblok('home', {
  version: 'draft',
  resolve_relations: ['article.author']
});
// Bridge automatically initialized via useAsyncStoryblok
</script>

<template>
  <StoryblokComponent v-if="story" :blok="story.content" />
</template>
```

**Bridge events:**

| Event | Description | Use Case |
|-------|-------------|----------|
| `input` | Editor typing | Live preview updates |
| `change` | Content saved | Refresh data |
| `published` | Content published | Reload for published version |
| `enterEditmode` | Editor opened | Load draft content |

**Environment configuration:**

```env
# .env.local (development/preview)
STORYBLOK_TOKEN=your-preview-token
STORYBLOK_VERSION=draft

# .env.production (production)
STORYBLOK_TOKEN=your-public-token
STORYBLOK_VERSION=published
```

Reference: [Storyblok Bridge](https://www.storyblok.com/docs/packages/storyblok-preview-bridge)
