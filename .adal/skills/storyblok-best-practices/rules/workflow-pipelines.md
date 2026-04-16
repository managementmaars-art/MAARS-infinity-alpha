---
title: Use Pipeline Stages for Content Staging
impact: MEDIUM-HIGH
impactDescription: enables controlled content promotion through environments
tags: pipeline, staging, environments, workflow, deployment
---

## Use Pipeline Stages for Content Staging

**Impact: MEDIUM-HIGH (enables controlled content promotion through environments)**

Pipeline stages allow content to progress through environments (Preview → Staging → Production). This enables QA review and stakeholder approval before content goes live.

**Incorrect (no staging workflow):**

```javascript
// Bad: Direct publish to production
const publishContent = async (storyId) => {
  await client.get(`spaces/${spaceId}/stories/${storyId}/publish`);
  // Content immediately visible to all users - no review!
};

// Bad: Using draft/published as only workflow states
// Limited to: Draft → Published
// No intermediate staging or review

// Bad: Separate spaces without sync
// Dev space and prod space with manual copy-paste
// Error-prone, no audit trail
```

**Correct (pipeline stage workflow):**

```javascript
// Good: Pipeline configuration in Storyblok
// Settings → Pipelines → Create Pipeline

// Pipeline structure:
// Stage 1: Preview (Development) - preview.yoursite.com
// Stage 2: Staging (QA Review) - staging.yoursite.com
// Stage 3: Production (Live) - yoursite.com

// Each stage has:
// - Preview URL for that environment
// - Access token specific to stage
// - Deployment trigger (manual or automatic)
```

```javascript
// Good: Deploy content to pipeline stage
// Management API: Deploy to stage
const deployToStage = async (storyId, stageId) => {
  try {
    await client.post(
      `spaces/${spaceId}/stories/${storyId}/push_to_pipeline_stage`,
      { pipeline_stage_id: stageId }
    );
    console.log(`Deployed story ${storyId} to stage ${stageId}`);
  } catch (error) {
    console.error('Deployment failed:', error.message);
    throw error;
  }
};

// Deploy with release
const deployReleaseToStage = async (releaseId, stageId) => {
  await client.post(
    `spaces/${spaceId}/releases/${releaseId}/deploy`,
    { pipeline_stage_id: stageId }
  );
};
```

```javascript
// Good: Fetch content for specific pipeline stage
// Each stage has its own preview URL and token

const stageConfig = {
  preview: {
    url: 'https://preview.yoursite.com',
    token: process.env.STORYBLOK_PREVIEW_TOKEN
  },
  staging: {
    url: 'https://staging.yoursite.com',
    token: process.env.STORYBLOK_STAGING_TOKEN
  },
  production: {
    url: 'https://yoursite.com',
    token: process.env.STORYBLOK_PRODUCTION_TOKEN
  }
};

const fetchForStage = async (slug, stage) => {
  const config = stageConfig[stage];

  const client = new StoryblokClient({
    accessToken: config.token
  });

  const { data } = await client.get(`cdn/stories/${slug}`, {
    version: stage === 'production' ? 'published' : 'draft'
  });

  return data.story;
};
```

```jsx
// Good: Environment-aware Next.js configuration
// next.config.js
const stage = process.env.PIPELINE_STAGE || 'production';

const stageTokens = {
  preview: process.env.STORYBLOK_PREVIEW_TOKEN,
  staging: process.env.STORYBLOK_STAGING_TOKEN,
  production: process.env.STORYBLOK_PUBLIC_TOKEN
};

module.exports = {
  env: {
    STORYBLOK_TOKEN: stageTokens[stage],
    STORYBLOK_VERSION: stage === 'production' ? 'published' : 'draft'
  }
};
```

```javascript
// Good: Webhook handler for stage deployments
// app/api/pipeline-webhook/route.js
export async function POST(request) {
  const payload = await request.json();
  const secret = request.headers.get('x-storyblok-secret');

  if (secret !== process.env.STORYBLOK_WEBHOOK_SECRET) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { action, pipeline_stage } = payload;

  switch (action) {
    case 'pipeline_deployed':
      await handleStageDeployment(pipeline_stage, payload);
      break;

    case 'story_pushed_to_pipeline':
      await notifyTeam(
        `Content pushed to ${pipeline_stage.name}`,
        payload.story
      );
      break;
  }

  return Response.json({ processed: true });
}

async function handleStageDeployment(stage, payload) {
  switch (stage.name.toLowerCase()) {
    case 'staging':
      // Trigger staging environment rebuild
      await triggerVercelDeploy(process.env.VERCEL_STAGING_HOOK);
      await notifySlack('Content deployed to staging for review');
      break;

    case 'production':
      // Trigger production rebuild
      await triggerVercelDeploy(process.env.VERCEL_PRODUCTION_HOOK);
      await invalidateCDNCache();
      await notifySlack('Content deployed to production');
      break;
  }
}
```

```javascript
// Good: Approval workflow with stages
const contentWorkflow = {
  // Author creates content → Preview stage
  async submitForReview(storyId) {
    const previewStageId = await getStageId('Preview');
    await deployToStage(storyId, previewStageId);
    await notifyReviewers(storyId);
  },

  // Reviewer approves → Staging stage
  async approveForStaging(storyId, reviewerId) {
    const stagingStageId = await getStageId('Staging');
    await deployToStage(storyId, stagingStageId);
    await logApproval(storyId, reviewerId, 'staging');
    await notifyQATeam(storyId);
  },

  // QA approves → Production stage
  async approveForProduction(storyId, approverId) {
    const productionStageId = await getStageId('Production');
    await deployToStage(storyId, productionStageId);
    await logApproval(storyId, approverId, 'production');

    // Also publish the story
    await client.get(`spaces/${spaceId}/stories/${storyId}/publish`);
  },

  // Reject and return to author
  async rejectContent(storyId, reason, reviewerId) {
    await logRejection(storyId, reviewerId, reason);
    await notifyAuthor(storyId, reason);
  }
};
```

**Pipeline vs Releases:**

| Feature | Pipeline Stages | Releases |
|---------|-----------------|----------|
| Purpose | Environment progression | Bundled publishing |
| Scope | Single story | Multiple stories |
| Workflow | Preview → Staging → Prod | Draft → Published |
| Scheduling | Per stage | Release-level |
| Use with | Content review | Campaign launches |

**Best practice: Combine both:**

```javascript
// Use Releases for grouping, Pipelines for environments
const campaignWorkflow = async (releaseId) => {
  // 1. Create release with all campaign content
  // 2. Deploy release to staging for review
  await deployReleaseToStage(releaseId, stagingStageId);

  // 3. QA reviews on staging environment
  // 4. Approve and deploy to production
  await deployReleaseToStage(releaseId, productionStageId);

  // 5. Merge release to publish all content
  await client.post(`spaces/${spaceId}/releases/${releaseId}/merge`);
};
```

**Environment configuration:**

| Stage | Token Type | Version | Cache |
|-------|------------|---------|-------|
| Preview | Preview | draft | Disabled |
| Staging | Preview | draft | Short TTL |
| Production | Public | published | Full CDN |

Reference: [Pipeline Stages](https://www.storyblok.com/docs/guide/in-depth/pipelines)
