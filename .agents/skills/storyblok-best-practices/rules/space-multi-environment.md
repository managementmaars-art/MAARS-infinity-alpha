---
title: Manage Multi-Space Architecture
impact: HIGH
impactDescription: enables enterprise-grade environment separation
tags: multi-space, environments, sync, enterprise, deployment
---

## Manage Multi-Space Architecture

**Impact: HIGH (enables enterprise-grade environment separation)**

For enterprise projects, use separate Storyblok spaces for development, staging, and production. This provides complete isolation, independent testing, and safe schema changes.

**Incorrect (single space for all environments):**

```javascript
// Bad: Using one space with only draft/published
// - Schema changes affect production immediately
// - No safe testing of component changes
// - Can't test migrations without risk

// Bad: Manual component sync between spaces
// Copy-paste components between spaces
// - Error-prone, inconsistent
// - No version control
// - No rollback capability
```

**Correct (multi-space architecture):**

```bash
# Space structure
Development Space (ID: 111111)
├── Full access for developers
├── Experimental components
└── Test content

Staging Space (ID: 222222)
├── Mirrors production schema
├── QA testing
└── Pre-release content

Production Space (ID: 333333)
├── Locked schema (admin only)
├── Live content
└── Public access tokens only
```

```javascript
// Good: Environment configuration
// config/storyblok.js
const environments = {
  development: {
    spaceId: process.env.STORYBLOK_DEV_SPACE_ID,
    previewToken: process.env.STORYBLOK_DEV_PREVIEW_TOKEN,
    managementToken: process.env.STORYBLOK_DEV_MANAGEMENT_TOKEN,
    region: 'eu'
  },
  staging: {
    spaceId: process.env.STORYBLOK_STAGING_SPACE_ID,
    previewToken: process.env.STORYBLOK_STAGING_PREVIEW_TOKEN,
    managementToken: process.env.STORYBLOK_STAGING_MANAGEMENT_TOKEN,
    region: 'eu'
  },
  production: {
    spaceId: process.env.STORYBLOK_PROD_SPACE_ID,
    publicToken: process.env.STORYBLOK_PROD_PUBLIC_TOKEN,
    // No management token in production builds!
    region: 'eu'
  }
};

export const getConfig = () => {
  const env = process.env.STORYBLOK_ENV || 'development';
  return environments[env];
};
```

```bash
# Good: CLI-based schema sync between spaces
# Pull components from development
storyblok pull-components --space 111111 --path ./schema/dev

# Push to staging after review
storyblok push-components \
  --source ./schema/dev/components.json \
  --space 222222

# Push to production after staging approval
storyblok push-components \
  --source ./schema/dev/components.json \
  --space 333333
```

```yaml
# Good: CI/CD pipeline for schema deployment
# .github/workflows/storyblok-schema.yml
name: Deploy Storyblok Schema

on:
  push:
    branches: [main]
    paths:
      - 'schema/**'

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Install Storyblok CLI
        run: npm install -g storyblok

      - name: Login
        run: storyblok login --token ${{ secrets.STORYBLOK_PAT }}

      - name: Deploy to Staging
        run: |
          storyblok push-components \
            --source ./schema/components.json \
            --space ${{ secrets.STORYBLOK_STAGING_SPACE }}

      - name: Verify Deployment
        run: |
          storyblok pull-components \
            --space ${{ secrets.STORYBLOK_STAGING_SPACE }} \
            --path ./schema/verify
          diff ./schema/components.json ./schema/verify/components.json

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Install Storyblok CLI
        run: npm install -g storyblok

      - name: Login
        run: storyblok login --token ${{ secrets.STORYBLOK_PAT }}

      - name: Backup Production Schema
        run: |
          storyblok pull-components \
            --space ${{ secrets.STORYBLOK_PROD_SPACE }} \
            --path ./schema/backup

      - name: Upload Backup
        uses: actions/upload-artifact@v4
        with:
          name: schema-backup-${{ github.sha }}
          path: ./schema/backup

      - name: Deploy to Production
        run: |
          storyblok push-components \
            --source ./schema/components.json \
            --space ${{ secrets.STORYBLOK_PROD_SPACE }}
```

```javascript
// Good: Content sync between spaces (for initial setup)
// scripts/sync-content.js
import StoryblokClient from 'storyblok-js-client';

const sourceClient = new StoryblokClient({
  oauthToken: process.env.SOURCE_MANAGEMENT_TOKEN
});

const targetClient = new StoryblokClient({
  oauthToken: process.env.TARGET_MANAGEMENT_TOKEN
});

const syncContent = async (sourceSpaceId, targetSpaceId, options = {}) => {
  const { includeAssets = true, includeUnpublished = false } = options;

  // 1. Sync datasources
  console.log('Syncing datasources...');
  const { data: datasources } = await sourceClient.get(
    `spaces/${sourceSpaceId}/datasources`
  );

  for (const ds of datasources.datasources) {
    await targetClient.post(
      `spaces/${targetSpaceId}/datasources`,
      { datasource: ds }
    ).catch(() => {
      // Update if exists
      return targetClient.put(
        `spaces/${targetSpaceId}/datasources/${ds.id}`,
        { datasource: ds }
      );
    });
  }

  // 2. Sync assets (if enabled)
  if (includeAssets) {
    console.log('Syncing assets...');
    await syncAssets(sourceSpaceId, targetSpaceId);
  }

  // 3. Sync stories
  console.log('Syncing stories...');
  const { data: stories } = await sourceClient.get(
    `spaces/${sourceSpaceId}/stories`,
    { per_page: 100 }
  );

  for (const story of stories.stories) {
    if (!includeUnpublished && !story.published) continue;

    const { data: fullStory } = await sourceClient.get(
      `spaces/${sourceSpaceId}/stories/${story.id}`
    );

    await upsertStory(targetSpaceId, fullStory.story);
  }
};

const upsertStory = async (spaceId, story) => {
  try {
    // Try to find existing story by slug
    const { data: existing } = await targetClient.get(
      `spaces/${spaceId}/stories`,
      { with_slug: story.full_slug }
    );

    if (existing.stories.length > 0) {
      await targetClient.put(
        `spaces/${spaceId}/stories/${existing.stories[0].id}`,
        { story, force_update: 1 }
      );
    } else {
      await targetClient.post(
        `spaces/${spaceId}/stories`,
        { story }
      );
    }
  } catch (error) {
    console.error(`Failed to sync: ${story.full_slug}`, error.message);
  }
};
```

```javascript
// Good: Environment-specific feature flags
// lib/features.js
const featureFlags = {
  development: {
    experimentalComponents: true,
    debugMode: true,
    draftPreview: true
  },
  staging: {
    experimentalComponents: true,
    debugMode: true,
    draftPreview: true
  },
  production: {
    experimentalComponents: false,
    debugMode: false,
    draftPreview: false
  }
};

export const getFeatures = () => {
  const env = process.env.STORYBLOK_ENV || 'development';
  return featureFlags[env];
};
```

**Multi-space vs single-space:**

| Aspect | Multi-Space | Single-Space |
|--------|-------------|--------------|
| Schema isolation | ✅ Complete | ❌ Shared |
| Safe testing | ✅ Yes | ⚠️ Limited |
| Cost | Higher | Lower |
| Complexity | Higher | Lower |
| Use case | Enterprise | Small/Medium |

**Space roles and permissions:**

| Role | Development | Staging | Production |
|------|-------------|---------|------------|
| Developer | Full access | Read + limited write | Read only |
| Content Editor | No access | Full content | Full content |
| Admin | Full access | Full access | Full access |
| Reviewer | Read only | Full access | Read only |

**Backup strategy:**

```bash
# Weekly production backup
storyblok pull-components --space PROD_SPACE --path ./backups/components/$(date +%Y%m%d)
storyblok pull-stories --space PROD_SPACE --path ./backups/stories/$(date +%Y%m%d)

# Store backups in S3/GCS
aws s3 sync ./backups s3://your-bucket/storyblok-backups/
```

Reference: [Multi-Space Management](https://www.storyblok.com/docs/guide/in-depth/spaces)
