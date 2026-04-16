---
title: Organize Assets and Datasources
impact: HIGH
impactDescription: ensures maintainable content architecture at scale
tags: assets, datasources, folders, organization
---

## Organize Assets and Datasources

**Impact: HIGH (ensures maintainable content architecture at scale)**

Use asset folders, datasources, and proper naming to keep content organized. Plan structure early to avoid costly reorganization later.

**Incorrect (flat, unorganized structure):**

```
# Bad: All assets in root
assets/
├── hero-image.jpg
├── logo.png
├── team-member-1.jpg
├── blog-post-banner.jpg
├── icon-facebook.svg
├── product-photo.jpg
└── ... (hundreds more mixed files)

# Bad: No datasources for repeated options
// Hardcoding options in each component
{
  "name": "article",
  "schema": {
    "category": {
      "type": "option",
      "options": [
        { "value": "tech" },
        { "value": "news" },
        { "value": "lifestyle" }
      ]
    }
  }
}
```

**Correct (organized asset structure):**

```
# Good: Logical folder hierarchy
assets/
├── brand/
│   ├── logos/
│   │   ├── logo-dark.svg
│   │   └── logo-light.svg
│   └── icons/
│       ├── social/
│       └── ui/
├── content/
│   ├── blog/
│   │   └── 2024/
│   ├── products/
│   └── team/
├── marketing/
│   ├── campaigns/
│   └── banners/
└── downloads/
    └── documents/
```

```json
// Good: Use datasources for shared options
// Datasource: "article-categories" (slug: article-categories)
{
  "datasource_entries": [
    { "name": "Technology", "value": "tech" },
    { "name": "News", "value": "news" },
    { "name": "Lifestyle", "value": "lifestyle" },
    { "name": "Business", "value": "business" }
  ]
}

// Component using datasource
{
  "name": "article",
  "schema": {
    "category": {
      "type": "option",
      "source": "internal",
      "datasource_slug": "article-categories",
      "use_uuid": false
    },
    "tags": {
      "type": "options", // Multi-select
      "source": "internal",
      "datasource_slug": "article-tags"
    }
  }
}
```

```jsx
// Good: Fetch datasource entries
const fetchCategories = async () => {
  const { data } = await storyblokApi.get('cdn/datasource_entries', {
    datasource: 'article-categories',
    per_page: 100
  });

  return data.datasource_entries.map(entry => ({
    label: entry.name,
    value: entry.value
  }));
};
```

```jsx
// Good: Story folder structure for content types
stories/
├── home (page)
├── about (page)
├── blog/
│   ├── _folder_settings (content-type: folder)
│   ├── getting-started (content-type: article)
│   └── best-practices (content-type: article)
├── products/
│   ├── product-a (content-type: product)
│   └── product-b (content-type: product)
├── authors/
│   ├── john-doe (content-type: author)
│   └── jane-smith (content-type: author)
└── config/
    ├── navigation (content-type: navigation)
    └── footer (content-type: footer)
```

```typescript
// Good: Type-safe datasource fetching
interface DatasourceEntry {
  id: number;
  name: string;
  value: string;
  dimension_value: string | null;
}

const useDatasource = (slug: string) => {
  const [entries, setEntries] = useState<DatasourceEntry[]>([]);

  useEffect(() => {
    const fetch = async () => {
      const { data } = await storyblokApi.get('cdn/datasource_entries', {
        datasource: slug,
        per_page: 100
      });
      setEntries(data.datasource_entries);
    };
    fetch();
  }, [slug]);

  return entries;
};

// Usage
const categories = useDatasource('article-categories');
```

**Datasource dimensions:**

```json
// Datasource with dimensions for multi-language
{
  "datasource_entries": [
    {
      "name": "Technology",
      "value": "tech",
      "dimension_value": null // Default
    },
    {
      "name": "Technologie",
      "value": "tech",
      "dimension_value": "de" // German dimension
    }
  ]
}

// Fetch with dimension
const { data } = await storyblokApi.get('cdn/datasource_entries', {
  datasource: 'article-categories',
  dimension: 'de'
});
```

**Organization checklist:**

| Resource | Structure | Naming |
|----------|-----------|--------|
| Assets | Type/Year folders | descriptive-name.ext |
| Datasources | Category grouping | category-options |
| Stories | Content type folders | kebab-case slugs |
| Components | Prefix by purpose | layout_, card_, seo_ |

Reference: [Asset Folders](https://www.storyblok.com/docs/api/management/asset-folders)
