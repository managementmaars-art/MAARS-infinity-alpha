---
title: Implement SEO and Structured Data
impact: HIGH
impactDescription: improves search visibility and rich results
tags: seo, structured-data, json-ld, sitemap, meta-tags
---

## Implement SEO and Structured Data

**Impact: HIGH (improves search visibility and rich results)**

Proper SEO implementation with meta tags, Open Graph, JSON-LD structured data, and sitemaps is essential for discoverability. Create reusable SEO components that editors can configure.

**Incorrect (missing or hardcoded SEO):**

```jsx
// Bad: No SEO meta tags
const Page = ({ story }) => {
  return <main>{/* content */}</main>;
};

// Bad: Hardcoded meta without CMS control
const Page = ({ story }) => {
  return (
    <>
      <Head>
        <title>My Website</title>
        <meta name="description" content="Welcome to my site" />
      </Head>
      <main>{/* content */}</main>
    </>
  );
};

// Bad: No structured data for articles
const Article = ({ story }) => {
  return (
    <article>
      <h1>{story.content.title}</h1>
      {/* Missing JSON-LD schema */}
    </article>
  );
};
```

**Correct (comprehensive SEO implementation):**

```json
// Good: SEO component schema in Storyblok
{
  "name": "seo_meta",
  "display_name": "SEO Settings",
  "is_nestable": true,
  "schema": {
    "title": {
      "type": "text",
      "display_name": "Meta Title",
      "description": "50-60 characters recommended",
      "max_length": 70
    },
    "description": {
      "type": "textarea",
      "display_name": "Meta Description",
      "description": "150-160 characters recommended",
      "max_length": 170
    },
    "og_image": {
      "type": "asset",
      "display_name": "Social Share Image",
      "description": "1200x630px recommended",
      "filetypes": ["images"]
    },
    "og_title": {
      "type": "text",
      "display_name": "Social Title (optional)",
      "description": "Overrides meta title for social"
    },
    "og_description": {
      "type": "textarea",
      "display_name": "Social Description (optional)"
    },
    "no_index": {
      "type": "boolean",
      "display_name": "Hide from Search Engines",
      "default_value": false
    },
    "canonical_url": {
      "type": "text",
      "display_name": "Canonical URL (optional)",
      "description": "Use if content exists elsewhere"
    }
  }
}
```

```jsx
// Good: Next.js SEO component with all meta tags
// components/SEO.jsx
export default function SEO({ story, seo }) {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL;
  const url = `${baseUrl}/${story.full_slug}`;

  const title = seo?.title || story.name;
  const description = seo?.description || '';
  const ogImage = seo?.og_image?.filename
    ? `${seo.og_image.filename}/m/1200x630`
    : `${baseUrl}/default-og.jpg`;

  return (
    <>
      <title>{title}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={seo?.canonical_url || url} />

      {seo?.no_index && <meta name="robots" content="noindex,nofollow" />}

      {/* Open Graph */}
      <meta property="og:type" content="website" />
      <meta property="og:url" content={url} />
      <meta property="og:title" content={seo?.og_title || title} />
      <meta property="og:description" content={seo?.og_description || description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={seo?.og_title || title} />
      <meta name="twitter:description" content={seo?.og_description || description} />
      <meta name="twitter:image" content={ogImage} />
    </>
  );
}

// Usage in page
export async function generateMetadata({ params }) {
  const story = await fetchStory(params.slug);
  const seo = story.content.seo?.[0];

  return {
    title: seo?.title || story.name,
    description: seo?.description,
    openGraph: {
      title: seo?.og_title || seo?.title || story.name,
      description: seo?.og_description || seo?.description,
      images: [seo?.og_image?.filename + '/m/1200x630']
    }
  };
}
```

```jsx
// Good: JSON-LD structured data for articles
const ArticleSchema = ({ story, seo }) => {
  const article = story.content;
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL;

  const schema = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: article.title,
    description: seo?.description || article.excerpt,
    image: article.featured_image?.filename,
    datePublished: story.first_published_at,
    dateModified: story.published_at,
    author: {
      '@type': 'Person',
      name: article.author?.content?.name || 'Unknown'
    },
    publisher: {
      '@type': 'Organization',
      name: 'Your Company',
      logo: {
        '@type': 'ImageObject',
        url: `${baseUrl}/logo.png`
      }
    },
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `${baseUrl}/${story.full_slug}`
    }
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
};

// Good: Breadcrumb schema
const BreadcrumbSchema = ({ items }) => {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url
    }))
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  );
};
```

```javascript
// Good: Dynamic sitemap generation
// app/sitemap.js (Next.js)
export default async function sitemap() {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL;

  // Fetch all published stories
  const { data } = await storyblokApi.get('cdn/links', {
    version: 'published',
    per_page: 1000
  });

  const stories = Object.values(data.links)
    .filter(link => !link.is_folder)
    .map(link => ({
      url: `${baseUrl}/${link.slug === 'home' ? '' : link.slug}`,
      lastModified: link.published_at || link.created_at,
      changeFrequency: link.slug === 'home' ? 'daily' : 'weekly',
      priority: link.slug === 'home' ? 1 : 0.8
    }));

  return stories;
}

// Good: robots.txt
// app/robots.js
export default function robots() {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL;

  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/preview/']
      }
    ],
    sitemap: `${baseUrl}/sitemap.xml`
  };
}
```

```javascript
// Good: AI search optimization (llms.txt)
// app/llms.txt/route.js
export async function GET() {
  const { data } = await storyblokApi.get('cdn/stories', {
    version: 'published',
    per_page: 100,
    excluding_fields: 'body'
  });

  const content = `# Site Name
> Brief description of your site

## Pages
${data.stories.map(s => `- [${s.name}](/${s.full_slug}): ${s.content.seo?.[0]?.description || ''}`).join('\n')}

## Topics
- Topic 1
- Topic 2
`;

  return new Response(content, {
    headers: { 'Content-Type': 'text/plain' }
  });
}
```

**Schema types for different content:**

| Content Type | Schema.org Type | Key Properties |
|--------------|-----------------|----------------|
| Article | `Article` | headline, author, datePublished |
| Product | `Product` | name, price, availability |
| FAQ | `FAQPage` | mainEntity with Q&A |
| Organization | `Organization` | name, logo, contactPoint |
| Breadcrumb | `BreadcrumbList` | itemListElement |
| Local Business | `LocalBusiness` | address, openingHours |

Reference: [SEO Best Practices](https://www.storyblok.com/docs/guide/in-depth/seo)
