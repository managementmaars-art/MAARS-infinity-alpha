---
title: Debug Common Storyblok Issues
impact: HIGH
impactDescription: quickly resolve frequent development problems
tags: debugging, troubleshooting, errors, visual-editor, cors
---

## Debug Common Storyblok Issues

**Impact: HIGH (quickly resolve frequent development problems)**

Understanding common Storyblok issues and their solutions saves significant debugging time. This guide covers Visual Editor problems, API errors, and configuration issues.

**Issue 1: "Component not found" Error**

```jsx
// Symptom: Console shows "Component 'hero' not found"
// StoryblokComponent renders nothing

// Bad: Component not registered
storyblokInit({
  accessToken: token,
  components: {
    // 'hero' missing from registry
    feature_grid: FeatureGrid
  }
});

// Good: Register all components with matching names
storyblokInit({
  accessToken: token,
  components: {
    hero: Hero,           // Matches Storyblok component name exactly
    feature_grid: FeatureGrid,
    'feature-card': FeatureCard  // Use quotes for kebab-case
  }
});

// Debug helper: Log missing components
const StoryblokComponentWithFallback = ({ blok }) => {
  const Component = components[blok.component];

  if (!Component) {
    console.error(`Missing component: ${blok.component}`, blok);
    return process.env.NODE_ENV === 'development' ? (
      <div style={{ border: '2px dashed red', padding: '1rem' }}>
        <strong>Missing: {blok.component}</strong>
        <pre>{JSON.stringify(blok, null, 2)}</pre>
      </div>
    ) : null;
  }

  return <Component blok={blok} />;
};
```

**Issue 2: Visual Editor Not Loading / Blank Preview**

```javascript
// Symptom: Visual Editor shows blank iframe or loading spinner

// Causes and solutions:

// 1. HTTPS required - Visual Editor only works with HTTPS
// Local development fix:
// package.json
{
  "scripts": {
    "dev": "next dev --experimental-https",
    // Or use mkcert for custom certs
    "dev:ssl": "node server-https.js"
  }
}

// 2. Preview URL misconfigured
// Settings → Visual Editor → Default Preview URL must match your dev URL
// ✓ https://localhost:3000/
// ✗ http://localhost:3000/

// 3. X-Frame-Options blocking iframe
// next.config.js - Remove or adjust headers
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          // Remove X-Frame-Options or allow Storyblok
          // Don't use DENY or SAMEORIGIN for preview pages
          {
            key: 'Content-Security-Policy',
            value: "frame-ancestors 'self' https://app.storyblok.com"
          }
        ]
      }
    ];
  }
};

// 4. Bridge not initialized
// Check if bridge script is loaded in Visual Editor context
const isInEditor = typeof window !== 'undefined' &&
  window.location.search.includes('_storyblok');

if (isInEditor) {
  console.log('Bridge should be active');
  // Check window.StoryblokBridge exists after page load
}
```

**Issue 3: CORS Errors**

```javascript
// Symptom: "Access-Control-Allow-Origin" errors in console

// Cause: Usually happens with Management API from browser
// Solution: Use server-side API routes

// Bad: Direct Management API call from client
const updateStory = async () => {
  await fetch('https://mapi.storyblok.com/v1/spaces/123/stories/456', {
    method: 'PUT',
    headers: { 'Authorization': token }
  }); // CORS error!
};

// Good: Proxy through API route
// app/api/storyblok/update/route.js
export async function PUT(request) {
  const { storyId, data } = await request.json();

  const response = await fetch(
    `https://mapi.storyblok.com/v1/spaces/${SPACE_ID}/stories/${storyId}`,
    {
      method: 'PUT',
      headers: {
        'Authorization': process.env.STORYBLOK_MANAGEMENT_TOKEN,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ story: data })
    }
  );

  return Response.json(await response.json());
}

// Client calls local API
await fetch('/api/storyblok/update', {
  method: 'PUT',
  body: JSON.stringify({ storyId: '456', data: { ... } })
});
```

**Issue 4: Stale Content After Publishing**

```javascript
// Symptom: Published changes don't appear on site

// Cause 1: CDN cache not invalidated
// Solution: Use cv parameter or webhooks

// Check current cache version
const { data: space } = await storyblokApi.get('cdn/spaces/me');
console.log('Cache version:', space.version);

// Force fresh fetch
const { data } = await storyblokApi.get('cdn/stories/home', {
  cv: Date.now() // Bypass cache for debugging
});

// Cause 2: ISR not revalidating
// Solution: Add webhook for on-demand revalidation
// See webhook-configuration.md

// Cause 3: Browser cache
// Solution: Hard refresh (Ctrl+Shift+R) or disable cache in DevTools

// Debug: Check if story is actually published
const { data: story } = await storyblokApi.get('cdn/stories/home', {
  version: 'published'
});
console.log('Published at:', story.story.published_at);
```

**Issue 5: Relations Not Resolving**

```javascript
// Symptom: Related content shows UUID instead of full story

// Bad: Not specifying resolve_relations
const { data } = await storyblokApi.get('cdn/stories/article-1');
console.log(data.story.content.author);
// Output: "a1b2c3d4-uuid-here" (just the ID)

// Good: Resolve specific relations
const { data } = await storyblokApi.get('cdn/stories/article-1', {
  resolve_relations: 'article.author,article.categories'
});
console.log(data.story.content.author);
// Output: { name: "John", ... } (full story object)

// Note: Max 100 resolved stories per request
// For more, fetch separately by UUIDs
```

**Issue 6: Draft Content in Production**

```javascript
// Symptom: Unpublished content visible to users

// Debug: Check which version is being fetched
const { data } = await storyblokApi.get('cdn/stories/home', {
  version: 'published'  // Should be 'published' in production
});

// Check token type
// Preview token → Can fetch draft
// Public token → Only published

// Environment check
console.log('Environment:', process.env.NODE_ENV);
console.log('Token type:', process.env.STORYBLOK_TOKEN?.startsWith('preview') ? 'preview' : 'public');
console.log('Version:', storyblokConfig.version);
```

**Issue 7: TypeScript Type Errors**

```typescript
// Symptom: Type 'unknown' errors with Storyblok content

// Solution: Generate types from components
// npx storyblok-generate-ts --sourceFilePaths ./components.json

// Quick fix: Type assertion (not recommended for production)
const hero = story.content as HeroStoryblok;

// Better: Proper typing with SDK types
import { ISbStoryData } from '@storyblok/react';
import { PageStoryblok } from '@/types/storyblok';

type PageStory = ISbStoryData<PageStoryblok>;

const Page = ({ story }: { story: PageStory }) => {
  // story.content is now properly typed
};
```

**Debug Checklist:**

| Issue | First Check | Quick Fix |
|-------|-------------|-----------|
| Component not found | Component registry | Add to storyblokInit |
| Blank Visual Editor | HTTPS, preview URL | Enable HTTPS locally |
| CORS error | Client vs server | Move to API route |
| Stale content | cv parameter | Add timestamp or webhook |
| Relations not resolved | resolve_relations | Add relation paths |
| Draft in production | Token type, version | Use public token |

**Useful Debug Commands:**

```bash
# Check Storyblok CLI connection
storyblok login --token YOUR_TOKEN

# Validate component schema
storyblok pull-components --space SPACE_ID

# Test API connectivity
curl "https://api.storyblok.com/v2/cdn/stories?token=YOUR_TOKEN"
```

Reference: [Troubleshooting Guide](https://www.storyblok.com/faq)
