---
title: Story Relations and References
impact: HIGH
impactDescription: enables proper content linking and data resolution patterns
tags: relations, references, links, multi-option, single-option, resolve_relations
---

## Story Relations and References

**Impact: HIGH (enables proper content linking and data resolution patterns)**

Use story links, single-option, and multi-option fields correctly with `resolve_relations` to fetch related content efficiently. Avoid N+1 query problems and understand resolution limits.

### Field Types for References

| Field Type | Use Case | Returns |
|------------|----------|---------|
| **Single-Option (Stories)** | One related story (author, category) | UUID string |
| **Multi-Option (Stories)** | Multiple related stories (tags, related posts) | UUID array |
| **Link** | Internal/external links | Link object with URL |

**Incorrect (not resolving relations):**

```typescript
// Bad: Only getting UUIDs, not resolved content
const { data } = await storyblokApi.get('cdn/stories/blog/my-post', {
  version: 'published'
});

// data.story.content.author = "a1b2c3d4-..." (just UUID!)
// data.story.content.categories = ["uuid1", "uuid2"] (just UUIDs!)

// Bad: Manual fetching for each relation (N+1 problem)
const authorUuid = data.story.content.author;
const authorRes = await storyblokApi.get(`cdn/stories/${authorUuid}`);
const author = authorRes.data.story;

// Bad: Fetching all stories to find by UUID
const allStories = await storyblokApi.get('cdn/stories');
const author = allStories.data.stories.find(s => s.uuid === authorUuid);
```

**Correct (using resolve_relations):**

```typescript
// Good: Resolve relations in single request
const { data } = await storyblokApi.get('cdn/stories/blog/my-post', {
  version: 'published',
  resolve_relations: 'article.author,article.categories,article.related_posts'
});

// Now relations are fully resolved objects:
// data.story.content.author = { name: "John Doe", ... }
// data.story.content.categories = [{ name: "Tech", ... }, ...]
```

```typescript
// Good: Type-safe relation handling
interface ArticleStory {
  content: {
    title: string;
    author: AuthorStory | string; // Can be resolved or UUID
    categories: (CategoryStory | string)[];
    related_posts: (ArticleStory | string)[];
  };
}

function isResolved<T extends { uuid: string }>(
  relation: T | string
): relation is T {
  return typeof relation === 'object' && relation !== null;
}

// Usage
const article = data.story as ArticleStory;

if (isResolved(article.content.author)) {
  console.log(article.content.author.content.name);
} else {
  console.log('Author not resolved, UUID:', article.content.author);
}
```

**Component schema with relations:**

```json
{
  "name": "article",
  "display_name": "Article",
  "schema": {
    "title": { "type": "text" },
    "author": {
      "type": "option",
      "source": "internal_stories",
      "filter_content_type": "author",
      "description": "Select the article author"
    },
    "categories": {
      "type": "options",
      "source": "internal_stories",
      "filter_content_type": "category",
      "min_options": 1,
      "max_options": 5
    },
    "related_posts": {
      "type": "options",
      "source": "internal_stories",
      "filter_content_type": "article",
      "max_options": 3,
      "description": "Related articles (max 3)"
    }
  }
}
```

**Resolution limits and pagination:**

```typescript
// ⚠️ Storyblok limits: max 50 resolved stories per request
// When more than 50 references need to be resolved, the API returns
// a rel_uuids array instead of the resolved rels array.
// There's also a limit of 100 first-level relations before second-level resolution stops.

// Good: Handle large relation sets with pagination
async function getArticleWithAllRelations(slug: string) {
  // First, get the article with standard resolution
  const { data } = await storyblokApi.get(`cdn/stories/${slug}`, {
    version: 'published',
    resolve_relations: 'article.author,article.categories'
  });

  const article = data.story;

  // If related_posts might exceed limits, fetch separately
  if (article.content.related_posts?.length > 0) {
    const relatedUuids = article.content.related_posts
      .filter((r: any) => typeof r === 'string'); // Get unresolved UUIDs

    if (relatedUuids.length > 0) {
      const { data: relatedData } = await storyblokApi.get('cdn/stories', {
        by_uuids: relatedUuids.join(','),
        version: 'published'
      });

      // Merge resolved stories back
      article.content.related_posts = relatedData.stories;
    }
  }

  return article;
}
```

**Fetching stories by UUIDs:**

```typescript
// Good: Batch fetch by UUIDs
async function getStoriesByUuids(uuids: string[]) {
  if (uuids.length === 0) return [];

  // Storyblok accepts comma-separated UUIDs
  const { data } = await storyblokApi.get('cdn/stories', {
    by_uuids: uuids.join(','),
    version: 'published',
    per_page: 100
  });

  return data.stories;
}

// Good: Maintain order when fetching by UUIDs
async function getStoriesByUuidsOrdered(uuids: string[]) {
  const stories = await getStoriesByUuids(uuids);

  // API doesn't guarantee order, so reorder to match input
  const storyMap = new Map(stories.map(s => [s.uuid, s]));
  return uuids
    .map(uuid => storyMap.get(uuid))
    .filter(Boolean);
}
```

**Link field handling:**

```typescript
// Good: Comprehensive link resolver
interface StoryblokLink {
  id?: string;
  url?: string;
  linktype: 'story' | 'url' | 'email' | 'asset';
  fieldtype: 'multilink';
  cached_url?: string;
  story?: { full_slug: string }; // When resolved
  anchor?: string;
  target?: '_blank' | '_self';
}

function resolveLink(link: StoryblokLink | undefined): string {
  if (!link || !link.linktype) return '';

  switch (link.linktype) {
    case 'story':
      // Use cached_url or resolved story slug
      const storyPath = link.story?.full_slug || link.cached_url || '';
      const anchor = link.anchor ? `#${link.anchor}` : '';
      return `/${storyPath}${anchor}`;

    case 'url':
      return link.url || '';

    case 'email':
      return `mailto:${link.url}`;

    case 'asset':
      return link.url || '';

    default:
      return '';
  }
}

// Usage in component
function LinkComponent({ link, children }: {
  link: StoryblokLink;
  children: React.ReactNode;
}) {
  const href = resolveLink(link);
  const isExternal = link.linktype === 'url' && href.startsWith('http');

  return (
    <a
      href={href}
      target={link.target || (isExternal ? '_blank' : undefined)}
      rel={isExternal ? 'noopener noreferrer' : undefined}
    >
      {children}
    </a>
  );
}
```

**Resolving links to stories:**

```typescript
// Good: Resolve story links with resolve_links
const { data } = await storyblokApi.get('cdn/stories/home', {
  version: 'published',
  resolve_links: 'url' // or 'story' for full story objects
});

// With resolve_links: 'url', link.cached_url is populated
// With resolve_links: 'story', link.story contains full story data
```

**Nested relations (relations within relations):**

```typescript
// ⚠️ Storyblok only resolves ONE level deep

// Article -> Author -> Company (won't auto-resolve Company)
// You need to handle nested relations manually

async function getArticleWithNestedRelations(slug: string) {
  const { data } = await storyblokApi.get(`cdn/stories/${slug}`, {
    version: 'published',
    resolve_relations: 'article.author'
  });

  const article = data.story;
  const author = article.content.author;

  // Author's company is still a UUID, resolve separately
  if (isResolved(author) && author.content.company) {
    const companyUuid = author.content.company;
    const { data: companyData } = await storyblokApi.get('cdn/stories', {
      by_uuids: companyUuid,
      version: 'published'
    });
    author.content.company = companyData.stories[0];
  }

  return article;
}
```

**GraphQL relation resolution:**

```graphql
# Good: GraphQL resolves relations automatically
query GetArticle($slug: ID!) {
  ArticleItem(id: $slug) {
    content {
      title
      # Relations are resolved by referencing their fields
      author {
        content {
          name
          bio
          avatar { filename }
          # Nested relation
          company {
            content {
              name
              website
            }
          }
        }
      }
      categories {
        items {
          content {
            name
            slug
          }
        }
      }
    }
  }
}
```

**Circular reference handling:**

```typescript
// ⚠️ Be careful with circular references (Article -> Related -> Article)

// Good: Limit resolution depth for circular refs
async function getArticleWithRelated(
  slug: string,
  depth: number = 1
): Promise<ArticleStory> {
  const { data } = await storyblokApi.get(`cdn/stories/${slug}`, {
    version: 'published',
    resolve_relations: depth > 0 ? 'article.author,article.categories' : ''
  });

  const article = data.story;

  // Only resolve related posts at top level to prevent infinite loops
  if (depth > 0 && article.content.related_posts?.length) {
    const relatedUuids = article.content.related_posts
      .map((r: any) => typeof r === 'string' ? r : r.uuid)
      .slice(0, 3); // Limit to prevent explosion

    const relatedStories = await Promise.all(
      relatedUuids.map(uuid =>
        getArticleWithRelated(uuid, depth - 1) // Reduce depth
      )
    );

    article.content.related_posts = relatedStories;
  }

  return article;
}
```

**Best practices summary:**

| Pattern | When to Use |
|---------|------------|
| `resolve_relations` | Standard relation resolution (<50 total) |
| `by_uuids` | Fetching specific stories by UUID |
| `resolve_links: 'url'` | Just need the URL path |
| `resolve_links: 'story'` | Need full linked story data |
| GraphQL | Complex nested relations, specific fields only |
| Manual resolution | Nested relations, circular refs, >50 relations |

Reference: [Content Delivery API - Resolve Relations](https://www.storyblok.com/docs/api/content-delivery/v2#core-resources/stories/retrieve-one-story) | [Links Field](https://www.storyblok.com/docs/schema-configuration#link)
