---
title: Use Releases for Scheduled Publishing
impact: MEDIUM-HIGH
impactDescription: enables coordinated content launches
tags: releases, scheduling, workflow, publishing
---

## Use Releases for Scheduled Publishing

**Impact: MEDIUM-HIGH (enables coordinated content launches)**

The Releases app bundles content changes for coordinated publishing. Use releases for campaigns, product launches, and content that must go live together.

**Incorrect (ad-hoc publishing):**

```
# Bad: Publishing individual stories separately
- Editor 1 publishes blog post at 9:00 AM
- Editor 2 publishes landing page at 9:15 AM (delay)
- Editor 3 forgets to publish banner
- Campaign launches with missing content!

# Bad: Using draft content in production
const { data } = await storyblokApi.get('cdn/stories/promo', {
  version: 'draft' // Exposes unpublished content!
});
```

**Correct (using Releases app):**

```jsx
// Good: Fetch release-specific content for staging
const fetchReleaseContent = async (slug, releaseId) => {
  const { data } = await storyblokApi.get(`cdn/stories/${slug}`, {
    version: 'draft',
    from_release: releaseId,
    token: process.env.STORYBLOK_PREVIEW_TOKEN
  });

  return data.story;
};

// Good: Preview release on staging environment
const StagingPage = async ({ params, searchParams }) => {
  const releaseId = searchParams.release;

  const story = releaseId
    ? await fetchReleaseContent(params.slug, releaseId)
    : await fetchDraftContent(params.slug);

  return <StoryblokStory story={story} />;
};
```

```jsx
// Good: Release-aware webhook handler
// app/api/release-webhook/route.js
export async function POST(request) {
  const payload = await request.json();
  const secret = request.headers.get('x-storyblok-secret');

  if (secret !== process.env.STORYBLOK_WEBHOOK_SECRET) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  switch (payload.action) {
    case 'release_merged':
      // Release was published - revalidate all affected pages
      await revalidateReleasedContent(payload.release_id);
      await triggerBuildPipeline();
      await sendSlackNotification(`Release ${payload.release_name} published`);
      break;

    case 'release_created':
      // New release created - notify team
      await notifyTeam(`New release: ${payload.release_name}`);
      break;
  }

  return Response.json({ processed: true });
};

async function revalidateReleasedContent(releaseId) {
  // Fetch stories in the release
  const { data } = await managementApi.get(
    `spaces/${SPACE_ID}/releases/${releaseId}/stories`
  );

  // Revalidate each story
  for (const story of data.stories) {
    await revalidatePath(`/${story.full_slug}`);
  }
}
```

**Release workflow example:**

```markdown
## Black Friday Campaign Release Workflow

1. **Create Release** (2 weeks before)
   - Name: "Black Friday 2024"
   - Schedule: Nov 29, 2024 00:00 UTC

2. **Add Content to Release**
   - Homepage hero banner
   - Promotional landing page
   - Product sale prices
   - Email template content

3. **Review & Approve**
   - Marketing reviews all changes
   - Legal approves disclaimers
   - QA tests on staging with `?release=123`

4. **Automatic Publishing**
   - Release publishes at scheduled time
   - Webhooks trigger cache invalidation
   - All content goes live simultaneously
```

**API for releases:**

```typescript
// Management API: Create release
const createRelease = async (name: string, scheduleAt?: Date) => {
  const { data } = await managementApi.post(`spaces/${SPACE_ID}/releases`, {
    release: {
      name,
      release_at: scheduleAt?.toISOString()
    }
  });

  return data.release;
};

// Management API: Add story to release
const addToRelease = async (releaseId: number, storyId: number) => {
  await managementApi.post(
    `spaces/${SPACE_ID}/releases/${releaseId}/stories`,
    { story_id: storyId }
  );
};

// Management API: Publish release immediately
const publishRelease = async (releaseId: number) => {
  await managementApi.post(
    `spaces/${SPACE_ID}/releases/${releaseId}/merge`
  );
};
```

**Release events for webhooks:**

| Event | Trigger | Use Case |
|-------|---------|----------|
| `release_created` | New release | Notify team |
| `release_merged` | Release published | Cache invalidation |
| `release_deleted` | Release removed | Cleanup |

Reference: [Releases](https://www.storyblok.com/docs/api/management/releases)
