---
title: Implement Field-Level Translations Correctly
impact: HIGH
impactDescription: enables efficient multi-language content management
tags: i18n, translation, localization, multilingual
---

## Implement Field-Level Translations Correctly

**Impact: HIGH (enables efficient multi-language content management)**

Field-level translation stores all language versions in a single story. Configure translatable fields properly and handle the `__i18n__` suffix in your frontend code.

**Incorrect (improper translation handling):**

```jsx
// Bad: Ignoring translations
const Article = ({ blok }) => {
  return (
    <article>
      <h1>{blok.title}</h1> {/* Only shows default language */}
      <p>{blok.description}</p>
    </article>
  );
};

// Bad: Hardcoded language
const getTranslatedField = (story, field) => {
  return story.content[`${field}__i18n__de`] || story.content[field];
};

// Bad: Not marking fields as translatable
{
  "name": "article",
  "schema": {
    "title": { "type": "text" }, // Not translatable!
    "body": { "type": "richtext" }
  }
}
```

**Correct (proper field-level translation):**

```json
// Good: Component with translatable fields
{
  "name": "article",
  "schema": {
    "title": {
      "type": "text",
      "translatable": true,
      "required": true
    },
    "description": {
      "type": "textarea",
      "translatable": true
    },
    "body": {
      "type": "richtext",
      "translatable": true
    },
    "featured_image": {
      "type": "asset",
      "translatable": true // Different images per locale
    },
    "slug": {
      "type": "text",
      "translatable": false // Same across languages
    },
    "publish_date": {
      "type": "datetime",
      "translatable": false // Same across languages
    }
  }
}
```

```jsx
// Good: React - Language-aware content fetching
const fetchStory = async (slug, language = 'default') => {
  const { data } = await storyblokApi.get(`cdn/stories/${slug}`, {
    version: 'published',
    language: language // Storyblok returns translated content
  });

  return data.story;
};

// Good: Next.js - Dynamic language routes
// app/[lang]/[...slug]/page.jsx
export async function generateStaticParams() {
  const languages = ['en', 'de', 'fr'];
  const stories = await fetchAllStories();

  return languages.flatMap((lang) =>
    stories.map((story) => ({
      lang,
      slug: story.full_slug.split('/')
    }))
  );
}

export default async function Page({ params }) {
  const { lang, slug } = params;

  const story = await fetchStory(slug.join('/'), lang);

  return <StoryblokStory story={story} />;
}
```

```jsx
// Good: Language switcher with Storyblok
const LanguageSwitcher = ({ story, currentLang }) => {
  const languages = [
    { code: 'default', label: 'English' },
    { code: 'de', label: 'Deutsch' },
    { code: 'fr', label: 'Français' }
  ];

  return (
    <nav className="language-switcher">
      {languages.map((lang) => (
        <Link
          key={lang.code}
          href={`/${lang.code === 'default' ? '' : lang.code}/${story.full_slug}`}
          className={currentLang === lang.code ? 'active' : ''}
        >
          {lang.label}
        </Link>
      ))}
    </nav>
  );
};
```

```vue
<!-- Good: Nuxt - i18n integration -->
<script setup>
const { locale } = useI18n();
const route = useRoute();

const story = await useAsyncStoryblok(
  route.path.replace(`/${locale.value}`, '') || 'home',
  {
    version: 'published',
    language: locale.value === 'en' ? 'default' : locale.value
  }
);
</script>
```

**API response structure:**

```json
// Request: /cdn/stories/article?language=de
{
  "story": {
    "content": {
      "title": "German Title", // Translated value
      "title__i18n__de": "German Title", // Also available
      "description": "German description",
      "slug": "article-slug" // Non-translatable, same value
    },
    "translated_slugs": [
      { "lang": "de", "slug": "artikel-slug", "name": "German Title" }
    ]
  }
}
```

**Translation configuration:**

| Setting | Purpose |
|---------|---------|
| Space Languages | Available languages in Settings → Internationalization |
| Field `translatable: true` | Enable per-field translation |
| `language` parameter | Fetch specific language version |
| Individual Publishing | Publish translations independently |

Reference: [Internationalization](https://www.storyblok.com/docs/concepts/internationalization)
