---
title: Migrate Content to Storyblok
impact: MEDIUM-HIGH
impactDescription: ensures smooth CMS transitions without data loss
tags: migration, import, export, backup, cli
---

## Migrate Content to Storyblok

**Impact: MEDIUM-HIGH (ensures smooth CMS transitions without data loss)**

Content migration requires careful planning, schema mapping, and validation. Use the CLI and Management API for reliable, repeatable migrations.

**Incorrect (manual or unsafe migration):**

```javascript
// Bad: No backup before migration
const migrate = async () => {
  await deleteAllContent();  // Dangerous!
  await importNewContent();
};

// Bad: No validation of imported content
const importStories = async (stories) => {
  for (const story of stories) {
    await client.post('spaces/123/stories', { story });
    // No error handling, no duplicate checking
  }
};

// Bad: Migrating without schema first
// Content fails validation if components don't exist
```

**Correct (safe migration workflow):**

```bash
# Step 1: Backup existing space before any changes
storyblok pull-components --space SOURCE_SPACE_ID
storyblok pull-stories --space SOURCE_SPACE_ID

# Creates backups in .storyblok/
# ├── components/
# │   └── components.json
# └── stories/
#     └── stories.json
```

```javascript
// Step 2: Schema migration first
// migrate-schema.js
import StoryblokClient from 'storyblok-js-client';

const client = new StoryblokClient({
  oauthToken: process.env.STORYBLOK_MANAGEMENT_TOKEN
});

const spaceId = process.env.TARGET_SPACE_ID;

// Create components before content
const migrateSchema = async (components) => {
  for (const component of components) {
    try {
      // Check if component exists
      const { data: existing } = await client.get(
        `spaces/${spaceId}/components`,
        { search: component.name }
      );

      if (existing.components.length > 0) {
        // Update existing
        await client.put(
          `spaces/${spaceId}/components/${existing.components[0].id}`,
          { component }
        );
        console.log(`Updated: ${component.name}`);
      } else {
        // Create new
        await client.post(
          `spaces/${spaceId}/components`,
          { component }
        );
        console.log(`Created: ${component.name}`);
      }
    } catch (error) {
      console.error(`Failed: ${component.name}`, error.message);
    }
  }
};
```

```javascript
// Step 3: Content migration with validation
// migrate-content.js
const migrateContent = async (stories, options = {}) => {
  const { dryRun = false, batchSize = 5 } = options;
  const results = { success: [], failed: [], skipped: [] };

  // Sort by parent relationship (parents first)
  const sorted = sortByDependency(stories);

  for (let i = 0; i < sorted.length; i += batchSize) {
    const batch = sorted.slice(i, i + batchSize);

    for (const story of batch) {
      try {
        // Transform content for target schema
        const transformed = transformContent(story);

        // Validate required fields
        if (!validateStory(transformed)) {
          results.skipped.push({ story, reason: 'validation failed' });
          continue;
        }

        if (dryRun) {
          console.log(`[DRY RUN] Would create: ${story.full_slug}`);
          results.success.push(story);
          continue;
        }

        // Check for existing story
        const existing = await findExistingStory(story.full_slug);

        if (existing) {
          // Update existing
          await client.put(
            `spaces/${spaceId}/stories/${existing.id}`,
            { story: transformed, force_update: 1 }
          );
          console.log(`Updated: ${story.full_slug}`);
        } else {
          // Create new
          await client.post(
            `spaces/${spaceId}/stories`,
            { story: transformed }
          );
          console.log(`Created: ${story.full_slug}`);
        }

        results.success.push(story);

      } catch (error) {
        console.error(`Failed: ${story.full_slug}`, error.message);
        results.failed.push({ story, error: error.message });
      }
    }

    // Rate limiting
    await delay(500);
  }

  return results;
};
```

```javascript
// Step 4: Content transformation for schema differences
const transformContent = (story) => {
  const content = story.content;

  return {
    name: story.name,
    slug: story.slug,
    full_slug: story.full_slug,
    parent_id: story.parent_id,
    content: {
      component: mapComponentName(content.component),
      ...transformFields(content)
    }
  };
};

const mapComponentName = (oldName) => {
  const mapping = {
    'old_hero': 'hero',
    'old_feature_block': 'feature_card',
    'blog_post': 'article'
  };
  return mapping[oldName] || oldName;
};

const transformFields = (content) => {
  const result = { ...content };

  // Transform field names
  if (content.hero_image) {
    result.featured_image = content.hero_image;
    delete result.hero_image;
  }

  // Transform rich text format
  if (content.body_html) {
    result.body = htmlToStoryblokRichtext(content.body_html);
    delete result.body_html;
  }

  // Transform nested blocks
  if (content.sections) {
    result.body = content.sections.map(section => ({
      ...section,
      component: mapComponentName(section.component),
      _uid: generateUid()
    }));
    delete result.sections;
  }

  return result;
};
```

```javascript
// Step 5: Asset migration with deduplication
const migrateAssets = async (assets) => {
  const assetMap = new Map(); // old URL -> new URL

  for (const asset of assets) {
    try {
      // Check if asset already exists (by filename hash)
      const hash = await getFileHash(asset.url);
      const existing = await findAssetByHash(hash);

      if (existing) {
        assetMap.set(asset.url, existing.filename);
        console.log(`Skipped (duplicate): ${asset.filename}`);
        continue;
      }

      // Download and upload
      const buffer = await downloadFile(asset.url);
      const uploaded = await uploadAsset(buffer, asset.filename);

      assetMap.set(asset.url, uploaded.filename);
      console.log(`Uploaded: ${asset.filename}`);

    } catch (error) {
      console.error(`Failed: ${asset.filename}`, error.message);
    }

    await delay(300); // Rate limiting
  }

  return assetMap;
};

// Replace old URLs in content with new Storyblok URLs
const updateAssetReferences = (content, assetMap) => {
  let json = JSON.stringify(content);

  for (const [oldUrl, newUrl] of assetMap) {
    json = json.replace(new RegExp(escapeRegex(oldUrl), 'g'), newUrl);
  }

  return JSON.parse(json);
};
```

```javascript
// Step 6: Validation and rollback
const validateMigration = async () => {
  const { data: stories } = await client.get(`spaces/${spaceId}/stories`, {
    per_page: 100
  });

  const issues = [];

  for (const story of stories.stories) {
    // Check for broken asset references
    const content = JSON.stringify(story.content);
    const brokenAssets = content.match(/https?:\/\/old-cdn\.com\/[^"]+/g);

    if (brokenAssets) {
      issues.push({
        story: story.full_slug,
        issue: 'broken_assets',
        details: brokenAssets
      });
    }

    // Check for missing required fields
    if (!story.content.title && story.content.component === 'article') {
      issues.push({
        story: story.full_slug,
        issue: 'missing_title'
      });
    }
  }

  return issues;
};

// Rollback from backup
const rollback = async (backupPath) => {
  const backup = JSON.parse(fs.readFileSync(backupPath));

  for (const story of backup.stories) {
    await client.put(
      `spaces/${spaceId}/stories/${story.id}`,
      { story, force_update: 1 }
    );
  }
};
```

**Migration checklist:**

| Phase | Tasks |
|-------|-------|
| **Prepare** | Backup source, map schemas, create components |
| **Assets** | Migrate assets first, build URL mapping |
| **Content** | Migrate in dependency order, transform fields |
| **Validate** | Check for broken refs, missing fields |
| **Publish** | Publish content, verify live site |
| **Cleanup** | Remove old redirects, update DNS |

**CLI commands:**

```bash
# Export from source
storyblok pull-components --space SOURCE_ID
storyblok pull-stories --space SOURCE_ID --format json

# Import to target
storyblok push-components --space TARGET_ID
storyblok push-stories --space TARGET_ID
```

Reference: [Migration Guide](https://www.storyblok.com/docs/guide/in-depth/migration)
