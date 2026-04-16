---
title: Secure API Token Management
impact: CRITICAL
impactDescription: prevents unauthorized access and data exposure
tags: security, tokens, authentication, environment, csp, rotation
---

## Secure API Token Management

**Impact: CRITICAL (prevents unauthorized access and data exposure)**

Never expose preview or personal access tokens in client-side code. Use public tokens for client-side requests and preview tokens only in server-side code.

**Incorrect (exposed sensitive tokens):**

```jsx
// Bad: Preview token in client-side code
const StoryblokClient = () => {
  const client = new StoryblokClient({
    accessToken: 'preview-token-xxxxx' // Exposed in bundle!
  });
};

// Bad: Personal access token in frontend
const updateContent = async () => {
  await fetch('https://mapi.storyblok.com/v1/spaces/123/stories', {
    headers: {
      'Authorization': 'my-personal-token' // NEVER DO THIS
    }
  });
};

// Bad: Token in version control
// .env (committed to git)
STORYBLOK_TOKEN=preview-xxxxxxxxxxxxx

// Bad: Token in client bundle
// next.config.js
module.exports = {
  env: {
    STORYBLOK_PREVIEW_TOKEN: process.env.STORYBLOK_PREVIEW_TOKEN
    // This exposes to client!
  }
};
```

**Correct (secure token handling):**

```jsx
// Good: Public token for client-side (read-only published content)
// This is safe - public tokens only access published content
const storyblokInit({
  accessToken: process.env.NEXT_PUBLIC_STORYBLOK_PUBLIC_TOKEN,
  use: [apiPlugin]
});

// Good: Preview token only server-side
// lib/storyblok-server.js (never imported in client code)
import StoryblokClient from 'storyblok-js-client';

const serverClient = new StoryblokClient({
  accessToken: process.env.STORYBLOK_PREVIEW_TOKEN // Server-only env var
});

export const getPreviewStory = async (slug) => {
  const { data } = await serverClient.get(`cdn/stories/${slug}`, {
    version: 'draft'
  });
  return data.story;
};
```

```jsx
// Good: Next.js - Proper environment variable usage
// .env.local (never committed)
// Note: The NEXT_PUBLIC_ prefix is specific to Next.js
// Other frameworks use different conventions:
// - Nuxt: NUXT_PUBLIC_ prefix
// - Vite: VITE_ prefix
// - Astro: PUBLIC_ prefix
STORYBLOK_PREVIEW_TOKEN=preview-xxxxx  # Server-only (no prefix)
STORYBLOK_MANAGEMENT_TOKEN=personal-token  # Server-only (no prefix)
NEXT_PUBLIC_STORYBLOK_TOKEN=public-xxxxx  # Safe for client (Next.js)

// next.config.js - No token exposure
module.exports = {
  // Don't put tokens in env config
};

// API route for server-side operations
// app/api/preview/route.js
export async function GET(request) {
  const secret = request.nextUrl.searchParams.get('secret');

  if (secret !== process.env.PREVIEW_SECRET) {
    return Response.json({ error: 'Invalid' }, { status: 401 });
  }

  // Use preview token safely server-side
  const story = await getPreviewStory(slug);
  return Response.json(story);
}
```

```jsx
// Good: API route for Management API operations
// app/api/storyblok/route.js
import StoryblokClient from 'storyblok-js-client';

const managementClient = new StoryblokClient({
  oauthToken: process.env.STORYBLOK_MANAGEMENT_TOKEN
});

export async function POST(request) {
  // Authenticate the request first
  const session = await getServerSession();
  if (!session) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Now safe to use management API
  const result = await managementClient.post(
    `spaces/${SPACE_ID}/stories`,
    { story: { /* ... */ } }
  );

  return Response.json(result);
}
```

**Token types and usage:**

| Token Type | Use Case | Client-Safe | Capabilities |
|------------|----------|-------------|--------------|
| Public | Production frontend | ✅ Yes | Read published |
| Preview | Visual Editor, staging | ❌ No | Read draft + published |
| Personal Access | Management API | ❌ Never | Full read/write |
| OAuth | App integrations | ❌ No | Scoped access |

**Environment variable naming:**

```env
# Client-safe (NEXT_PUBLIC_ prefix in Next.js)
NEXT_PUBLIC_STORYBLOK_TOKEN=public-xxxxx

# Server-only (no prefix)
STORYBLOK_PREVIEW_TOKEN=preview-xxxxx
STORYBLOK_MANAGEMENT_TOKEN=personal-xxxxx
STORYBLOK_WEBHOOK_SECRET=webhook-secret
```

**.gitignore must include:**

```gitignore
.env
.env.local
.env.*.local
```

**Token rotation strategy:**

```javascript
// Good: Implement token rotation for long-lived integrations
// scripts/rotate-tokens.js
import StoryblokClient from 'storyblok-js-client';

const rotatePreviewToken = async () => {
  const client = new StoryblokClient({
    oauthToken: process.env.STORYBLOK_MANAGEMENT_TOKEN
  });

  const spaceId = process.env.STORYBLOK_SPACE_ID;

  // 1. Create new token
  const { data: newToken } = await client.post(
    `spaces/${spaceId}/api_keys`,
    {
      api_key: {
        name: `preview-${Date.now()}`,
        access: 'full' // or 'public'
      }
    }
  );

  console.log('New token created:', newToken.api_key.name);

  // 2. Update environment (varies by platform)
  // For Vercel:
  // await updateVercelEnv('STORYBLOK_PREVIEW_TOKEN', newToken.api_key.access_token);

  // For AWS:
  // await updateSSMParameter('/app/storyblok/preview-token', newToken.api_key.access_token);

  // 3. Wait for deployment propagation
  await delay(30000);

  // 4. Revoke old tokens (keep last 2 for rollback)
  const { data: tokens } = await client.get(`spaces/${spaceId}/api_keys`);
  const oldTokens = tokens.api_keys
    .filter(t => t.name.startsWith('preview-'))
    .sort((a, b) => b.created_at.localeCompare(a.created_at))
    .slice(2); // Keep 2 most recent

  for (const token of oldTokens) {
    await client.delete(`spaces/${spaceId}/api_keys/${token.id}`);
    console.log('Revoked old token:', token.name);
  }
};

// Run rotation monthly via cron
// 0 0 1 * * rotatePreviewToken
```

**Content Security Policy for Visual Editor:**

```javascript
// Good: CSP headers that allow Visual Editor iframe
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://app.storyblok.com",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https://a.storyblok.com https://*.storyblok.com",
              "frame-ancestors 'self' https://app.storyblok.com",
              "connect-src 'self' https://api.storyblok.com https://mapi.storyblok.com"
            ].join('; ')
          }
        ]
      }
    ];
  }
};

// For preview/staging only - more permissive
const previewCSP = {
  'frame-ancestors': "'self' https://app.storyblok.com https://*.storyblok.com",
  'script-src': "'self' 'unsafe-inline' 'unsafe-eval' https://app.storyblok.com"
};
```

```javascript
// Good: Rate limit protection for API routes
// middleware.js
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'), // 10 requests per 10 seconds
});

export async function middleware(request) {
  if (request.nextUrl.pathname.startsWith('/api/storyblok')) {
    const ip = request.ip ?? '127.0.0.1';
    const { success, limit, reset, remaining } = await ratelimit.limit(ip);

    if (!success) {
      return new Response('Too Many Requests', {
        status: 429,
        headers: {
          'X-RateLimit-Limit': limit.toString(),
          'X-RateLimit-Remaining': remaining.toString(),
          'X-RateLimit-Reset': reset.toString()
        }
      });
    }
  }
}
```

```javascript
// Good: Webhook signature verification (enhanced)
import crypto from 'crypto';

const verifyWebhookSignature = (payload, signature, secret) => {
  const expectedSignature = crypto
    .createHmac('sha1', secret)
    .update(payload)
    .digest('hex');

  // Timing-safe comparison to prevent timing attacks
  const sigBuffer = Buffer.from(signature);
  const expectedBuffer = Buffer.from(expectedSignature);

  if (sigBuffer.length !== expectedBuffer.length) {
    return false;
  }

  return crypto.timingSafeEqual(sigBuffer, expectedBuffer);
};

// Usage in webhook handler
export async function POST(request) {
  const signature = request.headers.get('webhook-signature');
  const payload = await request.text();

  if (!verifyWebhookSignature(payload, signature, process.env.STORYBLOK_WEBHOOK_SECRET)) {
    console.warn('Invalid webhook signature attempt', {
      ip: request.headers.get('x-forwarded-for'),
      userAgent: request.headers.get('user-agent')
    });
    return Response.json({ error: 'Invalid signature' }, { status: 401 });
  }

  // Process webhook...
}
```

**Security checklist:**

- [ ] Public tokens only in client-side code
- [ ] Preview tokens server-side only
- [ ] Personal tokens never in code
- [ ] .env files in .gitignore
- [ ] CSP headers configured for Visual Editor
- [ ] Webhook signatures verified
- [ ] Rate limiting on API routes
- [ ] Token rotation scheduled
- [ ] Old tokens revoked

Reference: [Access Tokens](https://www.storyblok.com/docs/concepts/access-tokens)
