---
title: Use Content Delivery API Correctly
impact: HIGH
impactDescription: ensures efficient content fetching and proper data handling
tags: api, cdn, content-delivery, fetching
---

## Use Content Delivery API Correctly

**Impact: HIGH (ensures efficient content fetching and proper data handling)**

The Content Delivery API is optimized for fast content retrieval. Use proper parameters for filtering, pagination, and relationship resolution to avoid performance issues.

**Incorrect (inefficient API usage):**

```jsx
// Bad: Fetching all stories without pagination
const fetchAllPosts = async () => {
  const { data } = await storyblokApi.get('cdn/stories', {
    starts_with: 'blog/'
  });
  return data.stories; // Could be thousands of stories!
};

// Bad: Fetching story then author separately (N+1)
const fetchPostWithAuthor = async (slug) => {
  const { data: post } = await storyblokApi.get(`cdn/stories/${slug}`);
  const { data: author } = await storyblokApi.get(
    `cdn/stories/${post.story.content.author}`
  );
  return { post, author };
};

// Bad: Not handling rate limits
const fetchManyStories = async (slugs) => {
  // 100 parallel requests - will hit rate limits!
  return Promise.all(slugs.map(slug =>
    storyblokApi.get(`cdn/stories/${slug}`)
  ));
};
```

**Correct (efficient API patterns):**

```jsx
// Good: Proper pagination
const fetchBlogPosts = async (page = 1, perPage = 25) => {
  const { data, total } = await storyblokApi.get('cdn/stories', {
    starts_with: 'blog/',
    version: 'published',
    per_page: perPage,
    page: page,
    sort_by: 'first_published_at:desc',
    excluding_fields: 'body' // Exclude heavy fields for list
  });

  return {
    stories: data.stories,
    total,
    totalPages: Math.ceil(total / perPage),
    currentPage: page
  };
};

// Good: Resolve relations in single request
const fetchPostWithRelations = async (slug) => {
  const { data } = await storyblokApi.get(`cdn/stories/${slug}`, {
    version: 'published',
    resolve_relations: [
      'article.author',
      'article.categories',
      'article.related_posts'
    ].join(',')
  });

  return data.story;
};

// Good: Fetch multiple by UUIDs (batched)
const fetchStoriesByUuids = async (uuids) => {
  const { data } = await storyblokApi.get('cdn/stories', {
    by_uuids: uuids.join(','),
    version: 'published'
  });

  return data.stories;
};

// Good: Filter with proper parameters
const fetchFilteredContent = async (filters) => {
  const { data } = await storyblokApi.get('cdn/stories', {
    version: 'published',
    starts_with: 'products/',
    filter_query: {
      category: { in: filters.category },
      price: { gt_float: filters.minPrice },
      is_featured: { is: 'true' }
    },
    per_page: 20,
    page: filters.page || 1
  });

  return data.stories;
};
```

```jsx
// Good: Fetch all stories with automatic pagination
const fetchAllStories = async (path = '') => {
  const perPage = 100; // Max allowed
  let page = 1;
  let allStories = [];
  let total = 0;

  do {
    const { data, headers } = await storyblokApi.get('cdn/stories', {
      starts_with: path,
      version: 'published',
      per_page: perPage,
      page: page
    });

    allStories = [...allStories, ...data.stories];
    total = parseInt(headers.total);
    page++;
  } while (allStories.length < total);

  return allStories;
};

// Good: Using links endpoint for navigation
const fetchNavigation = async () => {
  const { data } = await storyblokApi.get('cdn/links', {
    version: 'published',
    starts_with: ''
  });

  // Transform to navigation tree
  return buildNavigationTree(data.links);
};
```

**API parameters reference:**

| Parameter | Description | Example |
|-----------|-------------|---------|
| `starts_with` | Filter by path prefix | `blog/` |
| `by_uuids` | Fetch specific UUIDs | `uuid1,uuid2` |
| `excluding_fields` | Exclude heavy fields | `body,images` |
| `resolve_relations` | Resolve linked stories | `post.author` |
| `filter_query` | Advanced filtering | `{ field: { operator: value } }` |
| `per_page` | Items per page (max 100) | `25` |
| `sort_by` | Sort field and direction | `created_at:desc` |

**Filter operators:**

| Operator | Description |
|----------|-------------|
| `is` | Exact match |
| `in` | Match any in array |
| `not_in` | Exclude values |
| `like` | Pattern match |
| `gt_float` | Greater than (number) |
| `lt_float` | Less than (number) |

Reference: [Content Delivery API](https://www.storyblok.com/docs/api/content-delivery/v2/stories/retrieve-a-single-story)
