---
title: Use GraphQL API for Complex Queries
impact: HIGH
impactDescription: enables efficient data fetching with precise field selection
tags: graphql, api, apollo, queries, performance
---

## Use GraphQL API for Complex Queries

**Impact: HIGH (enables efficient data fetching with precise field selection)**

Storyblok's GraphQL API allows precise field selection, reducing payload size. Use it for complex queries with multiple relations or when you need specific fields only.

**Incorrect (inefficient GraphQL usage):**

```javascript
// Bad: Fetching all fields when only needing a few
const query = `
  query {
    PageItem(id: "home") {
      content
    }
  }
`;
// Returns entire content blob, no field selection benefit

// Bad: Not using variables (injection risk)
const query = `
  query {
    PageItem(id: "${userInput}") {
      content
    }
  }
`;

// Bad: Multiple separate queries instead of one
const query1 = `query { PageItem(id: "home") { content } }`;
const query2 = `query { PageItem(id: "about") { content } }`;
// Two network requests when one would suffice
```

**Correct (optimized GraphQL patterns):**

```javascript
// Good: Apollo Client setup for Storyblok
import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client';

const client = new ApolloClient({
  link: new HttpLink({
    uri: 'https://gapi.storyblok.com/v1/api',
    headers: {
      Token: process.env.STORYBLOK_TOKEN,
      Version: 'published' // or 'draft' for preview
    }
  }),
  cache: new InMemoryCache()
});
```

```graphql
# Good: Precise field selection with fragments
fragment ArticleFields on ArticleComponent {
  title
  excerpt
  featured_image {
    filename
    alt
  }
  author {
    content
  }
}

query GetArticles($startsWith: String!, $perPage: Int!) {
  ArticleItems(
    starts_with: $startsWith
    per_page: $perPage
    sort_by: "first_published_at:desc"
  ) {
    items {
      slug
      first_published_at
      content {
        ...ArticleFields
      }
    }
    total
  }
}
```

```javascript
// Good: Using variables for safe queries
const GET_STORY = gql`
  query GetStory($slug: ID!) {
    PageItem(id: $slug) {
      slug
      name
      first_published_at
      content {
        component
        body
      }
    }
  }
`;

const { data } = await client.query({
  query: GET_STORY,
  variables: { slug: 'home' }
});
```

```graphql
# Good: Filtering with filter_query
query GetFilteredProducts($category: String!) {
  ProductItems(
    filter_query_v2: {
      category: { in: $category }
      is_featured: { is: true }
    }
    per_page: 20
  ) {
    items {
      slug
      content {
        name
        price
        category
      }
    }
  }
}
```

```javascript
// Good: Batch multiple queries in one request
const BATCH_QUERY = gql`
  query GetPageData($homeSlug: ID!, $navSlug: ID!) {
    home: PageItem(id: $homeSlug) {
      content {
        body
      }
    }
    navigation: ConfigItem(id: $navSlug) {
      content {
        nav_items
      }
    }
    articles: ArticleItems(per_page: 5) {
      items {
        slug
        content {
          title
        }
      }
    }
  }
`;

// Single request for all data
const { data } = await client.query({
  query: BATCH_QUERY,
  variables: {
    homeSlug: 'home',
    navSlug: 'config/navigation'
  }
});
```

```javascript
// Good: Persisted queries for production
import { createPersistedQueryLink } from '@apollo/client/link/persisted-queries';
import { sha256 } from 'crypto-hash';

const persistedLink = createPersistedQueryLink({
  sha256,
  useGETForHashedQueries: true // Enables CDN caching
});

const client = new ApolloClient({
  link: persistedLink.concat(httpLink),
  cache: new InMemoryCache()
});
```

**GraphQL vs REST comparison:**

| Feature | GraphQL | REST (CDN) |
|---------|---------|------------|
| Field selection | Precise | All fields |
| Multiple resources | Single query | Multiple requests |
| Caching | Apollo cache | CDN + cv param |
| Relations | In query | resolve_relations param |
| Best for | Complex queries | Simple fetches |

**Query naming conventions:**

| Pattern | Example | Use Case |
|---------|---------|----------|
| `{Type}Item` | `PageItem(id: "home")` | Single story by slug |
| `{Type}Items` | `PageItems(per_page: 10)` | List of stories |
| `filter_query_v2` | `filter_query_v2: { field: { op: value } }` | Advanced filtering in GraphQL |

**GraphQL endpoint:**

```
EU: https://gapi.storyblok.com/v1/api
US: https://gapi-us.storyblok.com/v1/api
CN: https://gapi-cn.storyblok.com/v1/api
```

Reference: [GraphQL API](https://www.storyblok.com/docs/graphql-api)
