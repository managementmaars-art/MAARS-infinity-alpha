---
title: Configure Field Types Correctly
impact: CRITICAL
impactDescription: ensures proper data structure and editor experience
tags: fields, schema, validation, configuration
---

## Configure Field Types Correctly

**Impact: CRITICAL (ensures proper data structure and editor experience)**

Each field type has specific configuration options. Use validation rules, default values, and proper field settings to ensure data integrity and improve editor experience.

**Incorrect (missing validation and configuration):**

```json
// Bad: No validation, generic configuration
{
  "name": "article",
  "schema": {
    "title": { "type": "text" },
    "slug": { "type": "text" },
    "body": { "type": "richtext" },
    "image": { "type": "asset" },
    "tags": { "type": "text" },
    "date": { "type": "text" }
  }
}
```

**Correct (properly configured fields):**

```json
{
  "name": "article",
  "schema": {
    "title": {
      "type": "text",
      "display_name": "Article Title",
      "required": true,
      "max_length": 100,
      "translatable": true
    },
    "slug": {
      "type": "text",
      "display_name": "URL Slug",
      "required": true,
      "regex": "^[a-z0-9]+(?:-[a-z0-9]+)*$",
      "description": "URL-friendly identifier (lowercase, hyphens only)"
    },
    "body": {
      "type": "richtext",
      "display_name": "Article Content",
      "required": true,
      "translatable": true,
      "customize_toolbar": true,
      "toolbar": [
        "bold", "italic", "link", "image", "list",
        "olist", "h2", "h3", "quote", "code"
      ],
      "restrict_components": true,
      "component_whitelist": ["code_block", "callout", "image_gallery"]
    },
    "featured_image": {
      "type": "asset",
      "display_name": "Featured Image",
      "required": true,
      "filetypes": ["images"],
      "description": "Recommended size: 1200x630px"
    },
    "tags": {
      "type": "option",
      "display_name": "Tags",
      "use_uuid": true,
      "source": "internal",
      "datasource_slug": "article-tags",
      "description": "Select relevant tags for this article"
    },
    "publish_date": {
      "type": "datetime",
      "display_name": "Publish Date",
      "required": true,
      "default_value": "now"
    },
    "author": {
      "type": "option",
      "display_name": "Author",
      "source": "internal_stories",
      "folder_slug": "authors/",
      "filter_content_type": ["author"]
    },
    "reading_time": {
      "type": "number",
      "display_name": "Reading Time (minutes)",
      "min_value": 1,
      "max_value": 60
    },
    "is_featured": {
      "type": "boolean",
      "display_name": "Featured Article",
      "default_value": false
    }
  }
}
```

**Field configuration checklist:**

| Option | Purpose | Applicable Types |
|--------|---------|------------------|
| `required` | Prevent saving without value | All except group |
| `translatable` | Enable per-language values | Text, Textarea, Richtext |
| `default_value` | Pre-populate on creation | Most types |
| `max_length` | Limit character count | Text, Textarea |
| `regex` | Pattern validation | Text |
| `filetypes` | Restrict asset types | Asset, Multi-asset |
| `minimum`/`maximum` | Block count limits | Blocks |
| `restrict_components` | Limit allowed blocks | Blocks, Richtext |

Reference: [Fields Documentation](https://www.storyblok.com/docs/concepts/fields)
