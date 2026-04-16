---
title: Configure Webhooks for Content Events
impact: MEDIUM-HIGH
impactDescription: enables automated workflows and cache invalidation
tags: webhooks, automation, events, integration
---

## Configure Webhooks for Content Events

**Impact: MEDIUM-HIGH (enables automated workflows and cache invalidation)**

Webhooks notify external systems when content changes. Configure them for cache invalidation, build triggers, and third-party integrations with proper security.

**Incorrect (insecure webhook handling):**

```jsx
// Bad: No signature verification
export async function POST(request) {
  const body = await request.json();

  if (body.action === 'published') {
    await revalidatePath(body.full_slug);
  }

  return Response.json({ ok: true });
  // Anyone can trigger this endpoint!
}

// Bad: Trusting all webhook data
export async function POST(request) {
  const { story_id, action, full_slug } = await request.json();

  // Directly using webhook data without validation
  await database.update(story_id, { status: action });
  await sendEmail(`Content ${full_slug} was ${action}`);
}

// Bad: Blocking webhook response
export async function POST(request) {
  const body = await request.json();

  // Long-running operations block webhook
  await rebuildEntireSite(); // Takes 5 minutes
  await syncToExternalCMS();
  await sendNotifications();

  return Response.json({ ok: true }); // Webhook times out!
}
```

**Correct (secure webhook implementation):**

```jsx
// Good: Webhook with secret verification
// app/api/webhook/route.js
import crypto from 'crypto';

export async function POST(request) {
  const body = await request.text();
  const signature = request.headers.get('webhook-signature');
  const secret = process.env.STORYBLOK_WEBHOOK_SECRET;

  // Verify signature
  const expectedSignature = crypto
    .createHmac('sha1', secret)
    .update(body)
    .digest('hex');

  if (signature !== expectedSignature) {
    return Response.json({ error: 'Invalid signature' }, { status: 401 });
  }

  const payload = JSON.parse(body);

  // Process webhook
  await handleWebhookEvent(payload);

  return Response.json({ received: true });
}

async function handleWebhookEvent(payload) {
  const { action, story_id, full_slug, space_id } = payload;

  switch (action) {
    case 'published':
      await handlePublish(full_slug);
      break;
    case 'unpublished':
      await handleUnpublish(full_slug);
      break;
    case 'deleted':
      await handleDelete(story_id);
      break;
    case 'moved':
      await handleMove(payload.old_full_slug, full_slug);
      break;
  }
}
```

```jsx
// Good: Non-blocking webhook with queue
import { Queue } from 'bullmq';

const webhookQueue = new Queue('storyblok-webhooks');

export async function POST(request) {
  const signature = request.headers.get('webhook-signature');
  const body = await request.text();

  if (!verifySignature(body, signature)) {
    return Response.json({ error: 'Invalid' }, { status: 401 });
  }

  // Queue for async processing
  await webhookQueue.add('process', JSON.parse(body));

  // Respond immediately
  return Response.json({ queued: true });
}

// Worker process
webhookQueue.process('process', async (job) => {
  const { action, full_slug } = job.data;

  if (action === 'published') {
    await revalidatePath(`/${full_slug}`);
    await invalidateCDNCache(full_slug);
    await triggerSearchReindex(full_slug);
    await sendSlackNotification(full_slug);
  }
});
```

```jsx
// Good: Next.js on-demand ISR revalidation
// app/api/revalidate/route.js
import { revalidatePath, revalidateTag } from 'next/cache';

export async function POST(request) {
  const secret = request.headers.get('x-storyblok-secret');

  if (secret !== process.env.STORYBLOK_WEBHOOK_SECRET) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const payload = await request.json();

  try {
    if (payload.action === 'published' || payload.action === 'unpublished') {
      const slug = payload.full_slug;

      // Revalidate specific page
      revalidatePath(`/${slug}`);

      // Revalidate listing pages that might include this content
      if (slug.startsWith('blog/')) {
        revalidatePath('/blog');
        revalidateTag('blog-posts');
      }

      // Revalidate homepage if it shows recent content
      revalidatePath('/');
    }

    return Response.json({
      revalidated: true,
      slug: payload.full_slug
    });
  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
}
```

**Webhook events:**

| Event | Trigger | Use Case |
|-------|---------|----------|
| `story.published` | Story published | Cache invalidation, build |
| `story.unpublished` | Story unpublished | Remove from index |
| `story.deleted` | Story deleted | Cleanup |
| `story.moved` | Story moved | Update URLs |
| `asset.replaced` | Asset replaced | Image cache |
| `datasource.updated` | Datasource changed | Refresh options |

**Storyblok webhook configuration:**

1. Navigate to Settings → Webhooks
2. Click "New Webhook"
3. Enter endpoint URL
4. Select events to trigger
5. Add secret for verification
6. Test webhook

Reference: [Webhooks](https://www.storyblok.com/docs/concepts/webhooks)
