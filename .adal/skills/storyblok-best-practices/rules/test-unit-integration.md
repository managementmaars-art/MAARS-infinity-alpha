---
title: Test Storyblok Components and Integration
impact: MEDIUM
impactDescription: ensures reliability and catches regressions
tags: testing, unit-tests, integration, mocking, e2e
---

## Test Storyblok Components and Integration

**Impact: MEDIUM (ensures reliability and catches regressions)**

Test Storyblok components with mocked API responses, validate content transformations, and run E2E tests against preview environments.

**Incorrect (no testing or brittle tests):**

```javascript
// Bad: No tests for Storyblok components
// Components are deployed without verification

// Bad: Tests that hit real API
test('fetches story', async () => {
  const story = await storyblokApi.get('cdn/stories/home');
  expect(story).toBeDefined();
  // Flaky: depends on real API, content can change
});

// Bad: Testing implementation details
test('hero renders', () => {
  render(<Hero blok={mockBlok} />);
  expect(screen.getByTestId('hero-wrapper')).toHaveClass('hero-section');
  // Brittle: breaks with CSS changes
});
```

**Correct (comprehensive testing strategy):**

```javascript
// Good: Mock Storyblok API for unit tests
// __mocks__/storyblok.js
export const mockStoryblokApi = {
  get: jest.fn(),
  post: jest.fn()
};

export const createMockStory = (overrides = {}) => ({
  id: 123,
  uuid: 'test-uuid',
  name: 'Test Story',
  slug: 'test-story',
  full_slug: 'test-story',
  content: {
    component: 'page',
    body: [],
    ...overrides.content
  },
  published_at: '2024-01-01T00:00:00.000Z',
  ...overrides
});

export const createMockBlok = (component, fields = {}) => ({
  _uid: `mock-${Math.random().toString(36).substr(2, 9)}`,
  component,
  ...fields
});
```

```javascript
// Good: Unit tests for Storyblok components
// components/__tests__/Hero.test.jsx
import { render, screen } from '@testing-library/react';
import Hero from '../Hero';
import { createMockBlok } from '@/__mocks__/storyblok';

describe('Hero Component', () => {
  const defaultBlok = createMockBlok('hero', {
    title: 'Welcome',
    subtitle: 'This is a subtitle',
    image: {
      filename: 'https://a.storyblok.com/test.jpg',
      alt: 'Hero image'
    },
    buttons: []
  });

  it('renders title and subtitle', () => {
    render(<Hero blok={defaultBlok} />);

    expect(screen.getByRole('heading', { level: 1 }))
      .toHaveTextContent('Welcome');
    expect(screen.getByText('This is a subtitle')).toBeInTheDocument();
  });

  it('renders image with optimization', () => {
    render(<Hero blok={defaultBlok} />);

    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('alt', 'Hero image');
    expect(img.src).toContain('/m/'); // Image service applied
  });

  it('handles missing optional fields', () => {
    const minimalBlok = createMockBlok('hero', { title: 'Only Title' });

    render(<Hero blok={minimalBlok} />);

    expect(screen.getByText('Only Title')).toBeInTheDocument();
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  it('applies storyblokEditable attributes', () => {
    const { container } = render(<Hero blok={defaultBlok} />);

    // Check for data-blok-c and data-blok-uid attributes
    const editableElement = container.querySelector('[data-blok-uid]');
    expect(editableElement).toBeInTheDocument();
  });

  it('renders nested buttons', () => {
    const blokWithButtons = createMockBlok('hero', {
      title: 'Test',
      buttons: [
        createMockBlok('button', { label: 'Primary', variant: 'primary' }),
        createMockBlok('button', { label: 'Secondary', variant: 'secondary' })
      ]
    });

    render(<Hero blok={blokWithButtons} />);

    expect(screen.getByText('Primary')).toBeInTheDocument();
    expect(screen.getByText('Secondary')).toBeInTheDocument();
  });
});
```

```javascript
// Good: Test API integration with mocking
// lib/__tests__/storyblok.test.js
import { getStory, getAllStories } from '../storyblok';
import { mockStoryblokApi, createMockStory } from '@/__mocks__/storyblok';

jest.mock('@storyblok/react', () => ({
  getStoryblokApi: () => mockStoryblokApi
}));

describe('Storyblok API Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches single story with correct parameters', async () => {
    const mockStory = createMockStory({ name: 'Home' });
    mockStoryblokApi.get.mockResolvedValueOnce({
      data: { story: mockStory }
    });

    const story = await getStory('home');

    expect(mockStoryblokApi.get).toHaveBeenCalledWith(
      'cdn/stories/home',
      expect.objectContaining({
        version: 'published'
      })
    );
    expect(story.name).toBe('Home');
  });

  it('handles 404 errors gracefully', async () => {
    mockStoryblokApi.get.mockRejectedValueOnce({
      status: 404,
      message: 'Not found'
    });

    const story = await getStory('non-existent');

    expect(story).toBeNull();
  });

  it('resolves relations when specified', async () => {
    const mockStory = createMockStory({
      content: {
        component: 'article',
        author: { content: { name: 'John' } }
      }
    });
    mockStoryblokApi.get.mockResolvedValueOnce({
      data: { story: mockStory }
    });

    await getStory('article', {
      resolveRelations: ['article.author']
    });

    expect(mockStoryblokApi.get).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        resolve_relations: 'article.author'
      })
    );
  });
});
```

```javascript
// Good: Test rich text rendering
// components/__tests__/RichText.test.jsx
import { render, screen } from '@testing-library/react';
import RichText from '../RichText';

describe('RichText Component', () => {
  const createRichText = (content) => ({
    type: 'doc',
    content
  });

  it('renders paragraphs', () => {
    const content = createRichText([
      { type: 'paragraph', content: [{ type: 'text', text: 'Hello world' }] }
    ]);

    render(<RichText content={content} />);

    expect(screen.getByText('Hello world')).toBeInTheDocument();
  });

  it('renders headings with correct levels', () => {
    const content = createRichText([
      {
        type: 'heading',
        attrs: { level: 2 },
        content: [{ type: 'text', text: 'Section Title' }]
      }
    ]);

    render(<RichText content={content} />);

    expect(screen.getByRole('heading', { level: 2 }))
      .toHaveTextContent('Section Title');
  });

  it('renders links with correct attributes', () => {
    const content = createRichText([
      {
        type: 'paragraph',
        content: [
          {
            type: 'text',
            text: 'Click here',
            marks: [{
              type: 'link',
              attrs: { href: 'https://example.com', target: '_blank' }
            }]
          }
        ]
      }
    ]);

    render(<RichText content={content} />);

    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', 'https://example.com');
    expect(link).toHaveAttribute('target', '_blank');
  });

  it('renders embedded components', () => {
    const content = createRichText([
      {
        type: 'blok',
        attrs: {
          body: [{ _uid: '123', component: 'callout', text: 'Note' }]
        }
      }
    ]);

    render(<RichText content={content} />);

    expect(screen.getByText('Note')).toBeInTheDocument();
  });
});
```

```javascript
// Good: E2E tests with Playwright
// e2e/storyblok.spec.js
import { test, expect } from '@playwright/test';

test.describe('Storyblok Content', () => {
  test('homepage loads with CMS content', async ({ page }) => {
    await page.goto('/');

    // Verify CMS-driven content renders
    await expect(page.locator('h1')).toBeVisible();

    // Check for storyblok editable markers (dev mode)
    if (process.env.NODE_ENV === 'development') {
      await expect(page.locator('[data-blok-uid]').first()).toBeVisible();
    }
  });

  test('navigation works for CMS pages', async ({ page }) => {
    await page.goto('/');

    // Click a CMS-driven link
    await page.click('a[href="/about"]');

    // Verify page loaded
    await expect(page).toHaveURL('/about');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('preview mode shows draft content', async ({ page }) => {
    // Enter preview mode
    await page.goto('/api/preview?secret=test-secret&slug=draft-page');

    // Verify draft content is visible
    await expect(page.locator('[data-draft="true"]')).toBeVisible();

    // Exit preview
    await page.goto('/api/preview/exit');
  });
});

test.describe('Visual Editor Integration', () => {
  test.skip(({ browserName }) => browserName !== 'chromium',
    'Visual Editor tests only run in Chromium');

  test('editable markers present in preview', async ({ page }) => {
    // Add Storyblok preview parameter
    await page.goto('/?_storyblok=123');

    // Check for editable elements
    const editableElements = page.locator('[data-blok-c]');
    await expect(editableElements.first()).toBeVisible();
  });
});
```

```javascript
// Good: Visual regression testing
// e2e/visual.spec.js
import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('hero section matches snapshot', async ({ page }) => {
    await page.goto('/');

    const hero = page.locator('[data-testid="hero"]');
    await expect(hero).toHaveScreenshot('hero-section.png', {
      maxDiffPixels: 100
    });
  });

  test('responsive layouts', async ({ page }) => {
    await page.goto('/');

    // Mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page).toHaveScreenshot('homepage-mobile.png');

    // Tablet
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page).toHaveScreenshot('homepage-tablet.png');

    // Desktop
    await page.setViewportSize({ width: 1440, height: 900 });
    await expect(page).toHaveScreenshot('homepage-desktop.png');
  });
});
```

**Testing strategy:**

| Test Type | Purpose | Tools |
|-----------|---------|-------|
| Unit | Component logic | Jest, Testing Library |
| Integration | API + Component | Jest with mocks |
| E2E | Full user flows | Playwright, Cypress |
| Visual | UI regression | Playwright, Percy |

Reference: [Testing Best Practices](https://www.storyblok.com/docs/guide/in-depth/testing)
