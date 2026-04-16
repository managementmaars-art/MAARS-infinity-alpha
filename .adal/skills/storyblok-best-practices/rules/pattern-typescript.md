---
title: Generate and Use TypeScript Types
impact: HIGH
impactDescription: provides type safety and improved developer experience
tags: typescript, types, generation, schema, zod, cli
---

## Generate and Use TypeScript Types

**Impact: HIGH (provides type safety and improved developer experience)**

Generate TypeScript types from Storyblok components to ensure type safety. Use `storyblok-generate-ts`, CLI v4, or Zod for runtime validation. Keep types in sync with your schema.

**Incorrect (untyped Storyblok content):**

```typescript
// Bad: Using 'any' types
const Hero = ({ blok }: { blok: any }) => {
  return (
    <section>
      <h1>{blok.title}</h1>
      <p>{blok.sutitle}</p> {/* Typo not caught! */}
    </section>
  );
};

// Bad: Manual type definitions that drift
interface HeroBlok {
  title: string;
  subtitle: string;
  // Missing: image, buttons - out of sync with Storyblok
}
```

**Correct (generated TypeScript types):**

```bash
# Install type generator
npm install --save-dev storyblok-generate-ts

# Generate types from components.json
npx storyblok-generate-ts \
  --sourceFilePaths .storyblok/*/components.json \
  --destinationFilePath ./src/types/storyblok.d.ts

# Or use Storyblok CLI v4 (first pull, then generate)
storyblok components pull --space 12345
storyblok types generate --space 12345
```

```typescript
// Generated: src/types/storyblok.d.ts
import { StoryblokStory } from 'storyblok-generate-ts';

export interface HeroStoryblok {
  _uid: string;
  component: 'hero';
  title: string;
  subtitle?: string;
  image?: AssetStoryblok;
  buttons?: ButtonStoryblok[];
}

export interface ButtonStoryblok {
  _uid: string;
  component: 'button';
  label: string;
  link: MultilinkStoryblok;
  variant?: 'primary' | 'secondary';
}

export interface PageStoryblok {
  _uid: string;
  component: 'page';
  body?: (HeroStoryblok | FeatureGridStoryblok | CtaStoryblok)[];
  seo?: SeoStoryblok[];
}

export interface AssetStoryblok {
  id: number;
  alt: string;
  name: string;
  focus: string;
  title: string;
  filename: string;
  copyright: string;
  fieldtype: string;
}

export interface MultilinkStoryblok {
  id?: string;
  cached_url?: string;
  linktype?: 'story' | 'url' | 'email' | 'asset';
  url?: string;
  anchor?: string;
  target?: '_self' | '_blank';
}
```

```typescript
// Good: Type-safe React component
import { HeroStoryblok } from '@/types/storyblok';
import { storyblokEditable } from '@storyblok/react';

interface HeroProps {
  blok: HeroStoryblok;
}

const Hero = ({ blok }: HeroProps) => {
  return (
    <section {...storyblokEditable(blok)} className="hero">
      <h1>{blok.title}</h1>
      {blok.subtitle && <p>{blok.subtitle}</p>}

      {blok.image?.filename && (
        <img
          src={`${blok.image.filename}/m/800x600`}
          alt={blok.image.alt}
        />
      )}

      {blok.buttons?.map((button) => (
        <Button key={button._uid} blok={button} />
      ))}
    </section>
  );
};
```

```typescript
// Good: Type-safe story fetching
import { ISbStoryData } from '@storyblok/react';
import { PageStoryblok } from '@/types/storyblok';

type PageStory = ISbStoryData<PageStoryblok>;

const fetchPage = async (slug: string): Promise<PageStory> => {
  const { data } = await storyblokApi.get(`cdn/stories/${slug}`, {
    version: 'published'
  });

  return data.story;
};

// Usage with full type safety
const page = await fetchPage('home');
const bodyBlocks = page.content.body; // Typed as (HeroStoryblok | ...)[]
```

```typescript
// Good: Dynamic component renderer with types
import { StoryblokComponent } from '@storyblok/react';
import { PageStoryblok } from '@/types/storyblok';

interface PageProps {
  blok: PageStoryblok;
}

const Page = ({ blok }: PageProps) => {
  return (
    <main {...storyblokEditable(blok)}>
      {blok.body?.map((section) => (
        <StoryblokComponent blok={section} key={section._uid} />
      ))}
    </main>
  );
};
```

**CI/CD type generation:**

```yaml
# .github/workflows/types.yml
name: Generate Storyblok Types

on:
  repository_dispatch:
    types: [storyblok-schema-change]
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate Types
        run: |
          npx storyblok-generate-ts \
            --sourceFilePaths .storyblok/components/*/components.json \
            --destinationFilePath ./src/types/storyblok.d.ts

      - name: Commit Types
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add src/types/storyblok.d.ts
          git commit -m "chore: update Storyblok types" || exit 0
          git push
```

```bash
# Good: Storyblok CLI v4 type generation
# CLI v4 uses domain-verb command structure

storyblok login
storyblok components pull --space 12345

# Generate types with CLI v4
# types generate must include same flags used when pulling
storyblok types generate --space 12345

# Additional options:
# --strict: Disable loose typing for more precise types
# --type-prefix: Prepend a prefix to generated types
```

```typescript
// Good: Zod schemas for runtime validation
import { z } from 'zod';

// Define Zod schemas that match Storyblok structure
const AssetSchema = z.object({
  id: z.number().optional(),
  alt: z.string().optional(),
  filename: z.string(),
  title: z.string().optional()
});

const LinkSchema = z.object({
  id: z.string().optional(),
  url: z.string().optional(),
  cached_url: z.string().optional(),
  linktype: z.enum(['story', 'url', 'email', 'asset']).optional(),
  target: z.enum(['_self', '_blank']).optional()
});

const HeroSchema = z.object({
  _uid: z.string(),
  component: z.literal('hero'),
  title: z.string(),
  subtitle: z.string().optional(),
  image: AssetSchema.optional(),
  buttons: z.array(z.object({
    _uid: z.string(),
    component: z.literal('button'),
    label: z.string(),
    link: LinkSchema.optional(),
    variant: z.enum(['primary', 'secondary']).optional()
  })).optional()
});

// Infer TypeScript type from Zod schema
type HeroBlok = z.infer<typeof HeroSchema>;

// Runtime validation
const validateHero = (data: unknown): HeroBlok => {
  return HeroSchema.parse(data);
};

// Safe parsing (doesn't throw)
const safeParseHero = (data: unknown) => {
  const result = HeroSchema.safeParse(data);
  if (result.success) {
    return result.data;
  }
  console.error('Validation errors:', result.error.issues);
  return null;
};
```

```typescript
// Good: Type narrowing utilities for union types
import { PageStoryblok, HeroStoryblok, FeatureGridStoryblok } from '@/types/storyblok';

// Type guard functions
function isHero(blok: PageStoryblok['body'][number]): blok is HeroStoryblok {
  return blok.component === 'hero';
}

function isFeatureGrid(blok: PageStoryblok['body'][number]): blok is FeatureGridStoryblok {
  return blok.component === 'feature_grid';
}

// Generic type guard factory
function isComponent<T extends { component: string }>(
  componentName: T['component']
) {
  return (blok: { component: string }): blok is T => {
    return blok.component === componentName;
  };
}

// Usage
const heroGuard = isComponent<HeroStoryblok>('hero');

// In component
const Page = ({ blok }: { blok: PageStoryblok }) => {
  return (
    <main>
      {blok.body?.map((section) => {
        if (isHero(section)) {
          // section is now HeroStoryblok
          return <Hero key={section._uid} title={section.title} />;
        }
        if (isFeatureGrid(section)) {
          // section is now FeatureGridStoryblok
          return <FeatureGrid key={section._uid} features={section.features} />;
        }
        return <StoryblokComponent key={section._uid} blok={section} />;
      })}
    </main>
  );
};
```

```typescript
// Good: Generic utility types for Storyblok
import { ISbStoryData, ISbComponentType } from '@storyblok/react';

// Extract content type from story
type StoryContent<T extends ISbStoryData> = T['content'];

// Make all Storyblok blok fields optional except _uid and component
type PartialBlok<T extends ISbComponentType<string>> = Pick<T, '_uid' | 'component'> &
  Partial<Omit<T, '_uid' | 'component'>>;

// Utility to get all component names from union
type ComponentName<T extends { component: string }> = T['component'];

// Create lookup type for components
type ComponentMap = {
  hero: HeroStoryblok;
  feature_grid: FeatureGridStoryblok;
  button: ButtonStoryblok;
};

// Get component type by name
type GetComponent<K extends keyof ComponentMap> = ComponentMap[K];

// Usage
const getComponentData = <K extends keyof ComponentMap>(
  blok: ComponentMap[K]
): ComponentMap[K] => {
  return blok;
};
```

```typescript
// Good: Strict null checks for optional fields
interface StrictHeroProps {
  blok: HeroStoryblok;
}

const Hero = ({ blok }: StrictHeroProps) => {
  // Use nullish coalescing for defaults
  const title = blok.title ?? 'Default Title';
  const subtitle = blok.subtitle ?? undefined;

  // Optional chaining for nested properties
  const imageUrl = blok.image?.filename;
  const imageAlt = blok.image?.alt ?? '';

  // Array safety
  const buttons = blok.buttons ?? [];
  const hasButtons = buttons.length > 0;

  return (
    <section>
      <h1>{title}</h1>
      {subtitle && <p>{subtitle}</p>}
      {imageUrl && <img src={imageUrl} alt={imageAlt} />}
      {hasButtons && (
        <div className="buttons">
          {buttons.map(btn => (
            <Button key={btn._uid} blok={btn} />
          ))}
        </div>
      )}
    </section>
  );
};
```

Reference: [storyblok-generate-ts](https://www.npmjs.com/package/storyblok-generate-ts)
