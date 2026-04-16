---
title: Use Management API for Content Operations
impact: HIGH
impactDescription: enables programmatic content creation and management
tags: management-api, crud, automation, bulk-operations
---

## Use Management API for Content Operations

**Impact: HIGH (enables programmatic content creation and management)**

The Management API enables CRUD operations on stories, components, assets, and spaces. Use it for migrations, automated content creation, and admin tooling.

**Incorrect (unsafe Management API usage):**

```javascript
// Bad: Using Management API from client-side
const createStory = async (data) => {
  await fetch('https://mapi.storyblok.com/v1/spaces/123/stories', {
    method: 'POST',
    headers: {
      'Authorization': personalAccessToken // Exposed to users!
    },
    body: JSON.stringify(data)
  });
};

// Bad: No error handling or rate limiting
const bulkCreate = async (stories) => {
  // Fires all requests simultaneously - will hit rate limits
  await Promise.all(stories.map(story =>
    client.post(`spaces/${spaceId}/stories`, { story })
  ));
};

// Bad: Not checking for existing content before create
const importContent = async (data) => {
  await client.post(`spaces/${spaceId}/stories`, { story: data });
  // Creates duplicates if run multiple times
};
```

**Correct (safe Management API patterns):**

```javascript
// Good: Server-side Management API client
import StoryblokClient from 'storyblok-js-client';

const managementClient = new StoryblokClient({
  oauthToken: process.env.STORYBLOK_OAUTH_TOKEN,
  // Or use personal access token
  // accessToken: process.env.STORYBLOK_PAT
});

const spaceId = process.env.STORYBLOK_SPACE_ID;
```

```javascript
// Good: CRUD operations with proper error handling
const storyOperations = {
  // Create story
  async create(data) {
    try {
      const response = await managementClient.post(
        `spaces/${spaceId}/stories`,
        {
          story: {
            name: data.name,
            slug: data.slug,
            content: data.content,
            parent_id: data.parentId || 0,
            is_startpage: data.isStartpage || false
          },
          publish: data.publishImmediately ? 1 : 0
        }
      );
      return response.data.story;
    } catch (error) {
      if (error.response?.status === 422) {
        throw new Error(`Validation error: ${JSON.stringify(error.response.data)}`);
      }
      throw error;
    }
  },

  // Update story
  async update(storyId, data) {
    const response = await managementClient.put(
      `spaces/${spaceId}/stories/${storyId}`,
      {
        story: data,
        force_update: 1 // Overwrite even if modified
      }
    );
    return response.data.story;
  },

  // Delete story
  async delete(storyId) {
    await managementClient.delete(
      `spaces/${spaceId}/stories/${storyId}`
    );
  },

  // Publish story
  async publish(storyId) {
    await managementClient.get(
      `spaces/${spaceId}/stories/${storyId}/publish`
    );
  },

  // Unpublish story
  async unpublish(storyId) {
    await managementClient.get(
      `spaces/${spaceId}/stories/${storyId}/unpublish`
    );
  }
};
```

```javascript
// Good: Rate-limited bulk operations
const rateLimitedBulkCreate = async (stories, options = {}) => {
  const { concurrency = 3, delayMs = 500 } = options;
  const results = [];
  const errors = [];

  // Process in batches
  for (let i = 0; i < stories.length; i += concurrency) {
    const batch = stories.slice(i, i + concurrency);

    const batchResults = await Promise.allSettled(
      batch.map(story => storyOperations.create(story))
    );

    batchResults.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        results.push(result.value);
      } else {
        errors.push({ story: batch[index], error: result.reason });
      }
    });

    // Respect rate limits (6 req/sec for paid plans, 3 req/sec for free)
    if (i + concurrency < stories.length) {
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }

  return { results, errors };
};
```

```javascript
// Good: Upsert pattern (create or update)
const upsertStory = async (slug, data) => {
  // Check if story exists
  try {
    const { data: existing } = await managementClient.get(
      `spaces/${spaceId}/stories`,
      { with_slug: slug }
    );

    if (existing.stories.length > 0) {
      // Update existing
      return await storyOperations.update(
        existing.stories[0].id,
        { ...existing.stories[0], ...data }
      );
    }
  } catch (error) {
    // Story doesn't exist, continue to create
  }

  // Create new
  return await storyOperations.create({ slug, ...data });
};
```

```javascript
// Good: Component management
const componentOperations = {
  // List all components
  async list() {
    const { data } = await managementClient.get(
      `spaces/${spaceId}/components`
    );
    return data.components;
  },

  // Create component
  async create(componentData) {
    const { data } = await managementClient.post(
      `spaces/${spaceId}/components`,
      { component: componentData }
    );
    return data.component;
  },

  // Update component schema
  async update(componentId, schema) {
    const { data } = await managementClient.put(
      `spaces/${spaceId}/components/${componentId}`,
      { component: { schema } }
    );
    return data.component;
  }
};
```

```javascript
// Good: Asset upload
const uploadAsset = async (filePath, fileName) => {
  const fs = require('fs');

  // 1. Request signed upload URL
  const { data: signed } = await managementClient.post(
    `spaces/${spaceId}/assets`,
    {
      filename: fileName,
      size: fs.statSync(filePath).size
    }
  );

  // 2. Upload to signed URL
  const formData = new FormData();
  Object.entries(signed.fields).forEach(([key, value]) => {
    formData.append(key, value);
  });
  formData.append('file', fs.createReadStream(filePath));

  await fetch(signed.post_url, {
    method: 'POST',
    body: formData
  });

  // 3. Finalize upload
  const { data: asset } = await managementClient.get(
    `spaces/${spaceId}/assets/${signed.id}/finish_upload`
  );

  return asset;
};
```

**Rate limits:**

| API | Limit | Scope |
|-----|-------|-------|
| Management API (paid) | 6 requests/second | Per space |
| Management API (free) | 3 requests/second | Per space |
| Asset uploads | 20 requests/minute | Per space |
| Bulk operations | Use batching | Implement delays |

**Management API endpoints:**

| Resource | Endpoint | Operations |
|----------|----------|------------|
| Stories | `/spaces/{id}/stories` | CRUD, publish, unpublish |
| Components | `/spaces/{id}/components` | CRUD, sync |
| Assets | `/spaces/{id}/assets` | Upload, delete, list |
| Datasources | `/spaces/{id}/datasources` | CRUD |
| Releases | `/spaces/{id}/releases` | Create, merge, delete |

Reference: [Management API](https://www.storyblok.com/docs/api/management)
