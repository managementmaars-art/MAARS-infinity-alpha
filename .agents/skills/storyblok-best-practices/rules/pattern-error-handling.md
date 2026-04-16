---
title: Implement Robust Error Handling
impact: HIGH
impactDescription: prevents crashes and improves user experience
tags: errors, fallback, resilience, api
---

## Implement Robust Error Handling

**Impact: HIGH (prevents crashes and improves user experience)**

Handle API errors, missing content, and component failures gracefully. Provide fallbacks and meaningful error messages instead of crashes.

**Incorrect (no error handling):**

```jsx
// Bad: Unhandled promise rejection
const Page = async ({ params }) => {
  const { data } = await storyblokApi.get(`cdn/stories/${params.slug}`);
  return <StoryblokComponent blok={data.story.content} />;
  // Crashes if story doesn't exist!
};

// Bad: No fallback for missing component
const DynamicComponent = ({ blok }) => {
  const Component = components[blok.component];
  return <Component blok={blok} />;
  // TypeError if component not registered!
};

// Bad: Trusting all API data
const Article = ({ blok }) => {
  return (
    <article>
      <h1>{blok.title}</h1>
      <img src={blok.image.filename} /> {/* Crashes if image is null! */}
      {blok.author.name} {/* Crashes if author not resolved! */}
    </article>
  );
};
```

**Correct (comprehensive error handling):**

```jsx
// Good: API error handling with fallback
import { notFound } from 'next/navigation';

const fetchStory = async (slug) => {
  try {
    const { data } = await storyblokApi.get(`cdn/stories/${slug}`, {
      version: 'published'
    });
    return data.story;
  } catch (error) {
    if (error.status === 404) {
      return null; // Handle 404 gracefully
    }

    console.error('Storyblok API error:', {
      slug,
      status: error.status,
      message: error.message
    });

    throw error; // Re-throw for error boundary
  }
};

const Page = async ({ params }) => {
  const story = await fetchStory(params.slug.join('/'));

  if (!story) {
    notFound(); // Next.js 404 page
  }

  return <StoryblokStory story={story} />;
};
```

```jsx
// Good: Safe component rendering with fallback
const SafeStoryblokComponent = ({ blok, fallback = null }) => {
  if (!blok || !blok.component) {
    console.warn('Invalid blok provided to StoryblokComponent');
    return fallback;
  }

  const Component = components[blok.component];

  if (!Component) {
    if (process.env.NODE_ENV === 'development') {
      return (
        <div className="component-missing">
          Component "{blok.component}" not found
        </div>
      );
    }
    return fallback;
  }

  return (
    <ErrorBoundary fallback={fallback}>
      <Component blok={blok} />
    </ErrorBoundary>
  );
};
```

```jsx
// Good: Error boundary for component isolation
'use client';

import { Component } from 'react';

class StoryblokErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Component error:', {
      component: this.props.componentName,
      error: error.message,
      stack: errorInfo.componentStack
    });

    // Report to error tracking service
    if (typeof window !== 'undefined' && window.Sentry) {
      window.Sentry.captureException(error, {
        extra: { componentStack: errorInfo.componentStack }
      });
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="component-error">
          <p>Something went wrong loading this section.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
const Page = ({ blok }) => (
  <main>
    {blok.body?.map((section) => (
      <StoryblokErrorBoundary
        key={section._uid}
        componentName={section.component}
        fallback={<SectionPlaceholder />}
      >
        <StoryblokComponent blok={section} />
      </StoryblokErrorBoundary>
    ))}
  </main>
);
```

```jsx
// Good: Safe property access
const Article = ({ blok }) => {
  return (
    <article>
      <h1>{blok.title || 'Untitled'}</h1>

      {blok.image?.filename && (
        <img
          src={`${blok.image.filename}/m/800x600`}
          alt={blok.image.alt || ''}
        />
      )}

      {blok.author?.content?.name && (
        <span className="author">By {blok.author.content.name}</span>
      )}

      {blok.categories?.length > 0 && (
        <ul className="categories">
          {blok.categories.map((cat) => (
            <li key={cat._uid || cat}>{cat.name || cat}</li>
          ))}
        </ul>
      )}
    </article>
  );
};
```

```typescript
// Good: Type guards for runtime safety
function isValidStory(story: unknown): story is ISbStoryData {
  return (
    typeof story === 'object' &&
    story !== null &&
    'content' in story &&
    typeof story.content === 'object'
  );
}

function hasRequiredFields(blok: unknown, fields: string[]): boolean {
  if (typeof blok !== 'object' || blok === null) return false;
  return fields.every(field => field in blok && blok[field] != null);
}

// Usage
const Hero = ({ blok }: { blok: HeroStoryblok }) => {
  if (!hasRequiredFields(blok, ['title'])) {
    return <HeroPlaceholder />;
  }

  return (
    <section>
      <h1>{blok.title}</h1>
    </section>
  );
};
```

Reference: [Error Handling Best Practices](https://www.storyblok.com/docs/api/content-delivery/v2/getting-started/error-handling)
