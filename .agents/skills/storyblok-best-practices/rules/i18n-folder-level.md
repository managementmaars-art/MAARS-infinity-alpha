---
title: Folder-Level Internationalization with Dimensions
impact: HIGH
impactDescription: enables region-specific content and SEO-optimized multi-language sites
tags: i18n, internationalization, dimensions, folders, multi-region, seo
---

## Folder-Level Internationalization with Dimensions

**Impact: HIGH (enables region-specific content and SEO-optimized multi-language sites)**

Use folder-level translation for sites where regions need different content structures, unique pages, or SEO-optimized URLs per locale. This approach uses the Dimensions app to manage language/region folders.

### When to Use Folder-Level vs Field-Level

| Approach | Use Case |
|----------|----------|
| **Field-level** | Same content structure, only text differs |
| **Folder-level** | Different pages per region, SEO URLs needed, region-specific content |
| **Space-level** | Completely separate teams, different schemas per market |

**Incorrect (mixing approaches inconsistently):**

```javascript
// Bad: Hardcoded language paths without Dimensions
const locales = ['en', 'de', 'fr'];

// Bad: Fetching without proper folder structure
const { data } = await storyblokApi.get('cdn/stories', {
  starts_with: `${lang}/`, // Fragile, no dimension support
  language: lang // Mixing folder and field-level
});

// Bad: No fallback strategy
const story = await getStory(`${locale}/${slug}`);
// Returns 404 if translation doesn't exist
```

**Correct (folder-level with Dimensions app):**

```
# Folder structure with Dimensions
stories/
├── en/                    # English (default)
│   ├── home
│   ├── about
│   ├── blog/
│   │   ├── welcome-post
│   │   └── getting-started
│   └── products/
│       └── product-a
├── de/                    # German
│   ├── home
│   ├── ueber-uns          # Different slug for SEO
│   ├── blog/
│   │   └── willkommen     # Translated slug
│   └── produkte/          # German folder name
│       └── produkt-a
└── fr/                    # French
    ├── home
    ├── a-propos
    └── blog/
        └── bienvenue
```

```typescript
// Good: Dimension-aware content fetching
interface LocaleConfig {
  code: string;
  folder: string;
  default: boolean;
  fallback?: string;
}

const locales: LocaleConfig[] = [
  { code: 'en', folder: 'en', default: true },
  { code: 'de', folder: 'de', default: false, fallback: 'en' },
  { code: 'fr', folder: 'fr', default: false, fallback: 'en' },
  { code: 'de-at', folder: 'de-at', default: false, fallback: 'de' },
];

async function getLocalizedStory(
  slug: string,
  locale: string
): Promise<StoryblokStory | null> {
  const localeConfig = locales.find(l => l.code === locale);
  if (!localeConfig) return null;

  const fullSlug = `${localeConfig.folder}/${slug}`;

  try {
    const { data } = await storyblokApi.get(`cdn/stories/${fullSlug}`, {
      version: 'published',
    });
    return data.story;
  } catch (error) {
    // Fallback to parent locale
    if (localeConfig.fallback) {
      return getLocalizedStory(slug, localeConfig.fallback);
    }
    return null;
  }
}
```

```typescript
// Good: Generate localized paths for static generation
async function getLocalizedPaths() {
  const paths: { params: { slug: string[]; locale: string } }[] = [];

  for (const locale of locales) {
    const { data } = await storyblokApi.get('cdn/stories', {
      starts_with: `${locale.folder}/`,
      version: 'published',
      per_page: 100,
    });

    for (const story of data.stories) {
      // Remove locale prefix from slug
      const slugWithoutLocale = story.full_slug
        .replace(`${locale.folder}/`, '');

      paths.push({
        params: {
          slug: slugWithoutLocale.split('/'),
          locale: locale.code,
        },
      });
    }
  }

  return paths;
}
```

**Next.js App Router with folder-level i18n:**

```typescript
// app/[locale]/[...slug]/page.tsx
import { notFound } from 'next/navigation';

interface PageProps {
  params: Promise<{ locale: string; slug?: string[] }>;
}

export async function generateStaticParams() {
  const paths = await getLocalizedPaths();
  return paths.map(p => p.params);
}

export default async function Page({ params }: PageProps) {
  const { locale, slug } = await params;
  const slugPath = slug?.join('/') || 'home';

  const story = await getLocalizedStory(slugPath, locale);
  if (!story) notFound();

  return <StoryblokComponent blok={story.content} />;
}
```

```typescript
// Good: Middleware for locale detection
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';

const defaultLocale = 'en';
const supportedLocales = ['en', 'de', 'fr', 'de-at'];

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Check if pathname has locale
  const hasLocale = supportedLocales.some(
    locale => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (hasLocale) return NextResponse.next();

  // Detect preferred locale from header
  const acceptLanguage = request.headers.get('accept-language') || '';
  const preferredLocale = acceptLanguage
    .split(',')
    .map(lang => lang.split(';')[0].trim().toLowerCase())
    .find(lang => supportedLocales.includes(lang)) || defaultLocale;

  // Redirect to localized path
  return NextResponse.redirect(
    new URL(`/${preferredLocale}${pathname}`, request.url)
  );
}

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)'],
};
```

**Nuxt with folder-level i18n:**

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@storyblok/nuxt', '@nuxtjs/i18n'],

  i18n: {
    locales: [
      { code: 'en', iso: 'en-US', dir: 'ltr' },
      { code: 'de', iso: 'de-DE', dir: 'ltr' },
      { code: 'fr', iso: 'fr-FR', dir: 'ltr' },
    ],
    defaultLocale: 'en',
    strategy: 'prefix', // /en/about, /de/about
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root',
    },
  },
});
```

```vue
<!-- pages/[...slug].vue -->
<script setup lang="ts">
const { locale } = useI18n();
const route = useRoute();
const storyblokApi = useStoryblokApi();

const slug = computed(() => {
  const pathSlug = route.params.slug
    ? (Array.isArray(route.params.slug)
        ? route.params.slug.join('/')
        : route.params.slug)
    : 'home';
  return `${locale.value}/${pathSlug}`;
});

const { data: story } = await useAsyncData(
  `story-${slug.value}`,
  () => storyblokApi.get(`cdn/stories/${slug.value}`, {
    version: 'published',
  }).then(res => res.data.story)
);
</script>
```

**Hreflang and SEO for folder-level:**

```typescript
// Good: Generate hreflang tags
interface AlternateLink {
  hreflang: string;
  href: string;
}

async function getAlternateLinks(
  slug: string,
  currentLocale: string
): Promise<AlternateLink[]> {
  const alternates: AlternateLink[] = [];
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL;

  for (const locale of locales) {
    // Check if translation exists
    const exists = await checkStoryExists(`${locale.folder}/${slug}`);

    if (exists) {
      alternates.push({
        hreflang: locale.code,
        href: `${baseUrl}/${locale.folder}/${slug}`,
      });
    }
  }

  // Add x-default pointing to default locale
  const defaultLocale = locales.find(l => l.default);
  if (defaultLocale) {
    alternates.push({
      hreflang: 'x-default',
      href: `${baseUrl}/${defaultLocale.folder}/${slug}`,
    });
  }

  return alternates;
}
```

```tsx
// Good: Head component with hreflang
export function LocalizedHead({
  slug,
  locale,
  alternates
}: {
  slug: string;
  locale: string;
  alternates: AlternateLink[];
}) {
  return (
    <head>
      {alternates.map(alt => (
        <link
          key={alt.hreflang}
          rel="alternate"
          hrefLang={alt.hreflang}
          href={alt.href}
        />
      ))}
      <link rel="canonical" href={`${baseUrl}/${locale}/${slug}`} />
    </head>
  );
}
```

**Linking between localized content:**

```typescript
// Good: Locale-aware link resolution
function resolveLocalizedLink(
  link: StoryblokLink,
  currentLocale: string
): string {
  if (link.linktype === 'story') {
    // Story links include the full path with locale folder
    return `/${link.cached_url}`;
  }

  if (link.linktype === 'url') {
    return link.url;
  }

  return '/';
}

// Good: Language switcher component
async function getLanguageSwitcherLinks(
  currentSlug: string,
  currentLocale: string
): Promise<{ locale: string; href: string; available: boolean }[]> {
  const slugWithoutLocale = currentSlug.replace(
    new RegExp(`^${currentLocale}/`),
    ''
  );

  return Promise.all(
    locales.map(async locale => {
      const translatedSlug = `${locale.folder}/${slugWithoutLocale}`;
      const exists = await checkStoryExists(translatedSlug);

      return {
        locale: locale.code,
        href: exists ? `/${translatedSlug}` : `/${locale.folder}`,
        available: exists,
      };
    })
  );
}
```

**Dimension values for region-specific data:**

```typescript
// Good: Fetch datasources with dimension for locale
async function getLocalizedDatasource(
  datasourceSlug: string,
  locale: string
) {
  const { data } = await storyblokApi.get('cdn/datasource_entries', {
    datasource: datasourceSlug,
    dimension: locale, // Fetches locale-specific values
    per_page: 100,
  });

  return data.datasource_entries;
}

// Usage: Get localized categories
const categories = await getLocalizedDatasource('categories', 'de');
// Returns German translations of category names
```

Reference: [Folder-Level Translation](https://www.storyblok.com/docs/concepts/internationalization#folder-level-translation) | [Dimensions App](https://www.storyblok.com/apps/dimensions)
