---
title: Set Up Preview and Production Environments
impact: MEDIUM
impactDescription: enables safe content testing before publishing
tags: preview, production, environments, testing
---

## Set Up Preview and Production Environments

**Impact: MEDIUM (enables safe content testing before publishing)**

Separate preview and production environments with different tokens and configurations. This allows editors to test content safely before publishing.

**Incorrect (single environment):**

```jsx
// Bad: Same config for all environments
const storyblokConfig = {
  accessToken: 'preview-token', // Preview token in production!
  version: 'draft' // Draft content visible to users!
};

// Bad: No preview URL configured
// Editors can't see how content looks on the actual site
```

**Correct (environment separation):**

```typescript
// Good: Environment-aware configuration
// lib/storyblok.ts
const isProduction = process.env.NODE_ENV === 'production';
const isPreview = process.env.STORYBLOK_PREVIEW === 'true';

export const storyblokConfig = {
  accessToken: isPreview
    ? process.env.STORYBLOK_PREVIEW_TOKEN
    : process.env.STORYBLOK_PUBLIC_TOKEN,
  version: isPreview ? 'draft' : 'published',
  cache: {
    type: isPreview ? 'none' : 'memory',
    clear: 'auto'
  }
};
```

```env
# .env.production (Vercel/Netlify production)
STORYBLOK_PUBLIC_TOKEN=public-xxxxx
STORYBLOK_PREVIEW=false

# .env.preview (Vercel preview branches)
STORYBLOK_PREVIEW_TOKEN=preview-xxxxx
STORYBLOK_PREVIEW=true

# .env.local (local development)
STORYBLOK_PREVIEW_TOKEN=preview-xxxxx
STORYBLOK_PREVIEW=true
```

**Storyblok Visual Editor setup:**

```markdown
## Configure Preview URLs in Storyblok

1. Go to Settings → Visual Editor
2. Add preview URLs:

| Environment | URL | Use Case |
|-------------|-----|----------|
| Development | `https://localhost:3000/` | Local testing |
| Preview | `https://preview.yoursite.com/` | Staging |
| Production | `https://yoursite.com/` | Published view |

3. Set default preview URL
4. Configure HTTPS for local dev (required for Visual Editor)
```

```jsx
// Good: Detect preview context
// lib/preview.ts
export function isInStoryblokEditor(): boolean {
  if (typeof window === 'undefined') return false;
  return window.location !== window.parent.location; // In iframe
}

export function isPreviewMode(): boolean {
  if (typeof window === 'undefined') return false;
  const params = new URLSearchParams(window.location.search);
  return params.has('_storyblok') || params.has('_storyblok_tk[space_id]');
}
```

```jsx
// Good: Next.js preview mode setup
// app/api/preview/enter/route.js
import { draftMode, cookies } from 'next/headers';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const secret = searchParams.get('secret');
  const slug = searchParams.get('slug') || '';

  // Validate secret
  if (secret !== process.env.STORYBLOK_PREVIEW_SECRET) {
    return new Response('Invalid token', { status: 401 });
  }

  // Enable draft mode
  draftMode().enable();

  // Redirect to the page
  return new Response(null, {
    status: 307,
    headers: {
      Location: `/${slug}`,
      'Set-Cookie': `__prerender_bypass=true; Path=/; HttpOnly; SameSite=None; Secure`
    }
  });
}

// app/api/preview/exit/route.js
export async function GET() {
  draftMode().disable();

  return new Response(null, {
    status: 307,
    headers: { Location: '/' }
  });
}
```

```jsx
// Good: Conditional rendering for preview
const PreviewBanner = () => {
  const isPreview = usePreviewMode();

  if (!isPreview) return null;

  return (
    <div className="preview-banner">
      <span>Preview Mode</span>
      <a href="/api/preview/exit">Exit Preview</a>
    </div>
  );
};
```

**Vercel configuration:**

```json
// vercel.json
{
  "build": {
    "env": {
      "STORYBLOK_PUBLIC_TOKEN": "@storyblok-public-token"
    }
  },
  "env": {
    "STORYBLOK_PREVIEW_TOKEN": "@storyblok-preview-token"
  }
}
```

**Environment matrix:**

| Environment | Token | Version | Caching | Visual Editor |
|-------------|-------|---------|---------|---------------|
| Production | Public | published | Enabled | No |
| Staging | Preview | draft | Disabled | Yes |
| Preview Deploy | Preview | draft | Disabled | Yes |
| Local Dev | Preview | draft | Disabled | Yes |

Reference: [Visual Editor](https://www.storyblok.com/docs/concepts/visual-editor)
