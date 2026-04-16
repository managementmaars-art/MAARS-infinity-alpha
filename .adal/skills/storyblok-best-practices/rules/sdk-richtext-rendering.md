---
title: Render Rich Text with Custom Resolvers
impact: HIGH
impactDescription: ensures consistent styling and component handling
tags: richtext, resolver, sdk, rendering, v3, v5
---

## Render Rich Text with Custom Resolvers

**Impact: HIGH (ensures consistent styling and component handling)**

Rich text fields return structured JSON that must be rendered to HTML. Use the official `@storyblok/richtext` package (v3.3.0+) or SDK-specific components with custom resolvers for embedded components and marks.

> **@storyblok/react v5+:** The legacy `richTextResolver` was removed from the React SDK in v5. Always use the standalone `@storyblok/richtext` package for rich text rendering.

> **Note:** The community package `storyblok-rich-text-react-renderer` is still maintained but **not recommended for new projects**. Use the official `@storyblok/richtext` package instead, which provides better TypeScript support and is actively developed by Storyblok.

**Incorrect (rendering raw content or using deprecated methods):**

```jsx
// Bad: Rendering raw HTML without sanitization
const Article = ({ blok }) => {
  return (
    <div dangerouslySetInnerHTML={{ __html: blok.content }} />
  );
};

// Not recommended: Using community package instead of official solution
// ⚠️ storyblok-rich-text-react-renderer works but @storyblok/richtext is preferred
import { render } from 'storyblok-rich-text-react-renderer';
const html = render(blok.content); // Works, but use official package for new projects
```

**Correct (using official rich text package):**

```jsx
// Good: React - Using @storyblok/richtext
import { richTextResolver } from '@storyblok/richtext';
import DOMPurify from 'dompurify'; // Recommended for production

const { render } = richTextResolver();

const Article = ({ blok }) => {
  const html = render(blok.content);
  // ⚠️ Security: @storyblok/richtext only provides minimal HTML escaping.
  // For production, always sanitize HTML with DOMPurify before injection.
  const sanitizedHtml = DOMPurify.sanitize(html);
  return (
    <article {...storyblokEditable(blok)}>
      <div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />
    </article>
  );
};
```

```jsx
// Good: React - Custom resolvers for marks and nodes
import { richTextResolver } from '@storyblok/richtext';

const { render } = richTextResolver({
  resolvers: {
    // Custom mark resolvers
    marks: {
      link: ({ attrs, children }) => {
        const { href, target, linktype } = attrs;
        if (linktype === 'email') {
          return `<a href="mailto:${href}">${children}</a>`;
        }
        return `<a href="${href}" target="${target || '_self'}" rel="noopener">${children}</a>`;
      },
      bold: ({ children }) => `<strong class="font-bold">${children}</strong>`,
      highlight: ({ children }) => `<mark class="bg-yellow-200">${children}</mark>`
    },
    // Custom node resolvers
    nodes: {
      heading: ({ attrs, children }) => {
        const { level } = attrs;
        const Tag = `h${level}`;
        const classes = {
          1: 'text-4xl font-bold mb-6',
          2: 'text-3xl font-semibold mb-4',
          3: 'text-2xl font-medium mb-3'
        };
        return `<${Tag} class="${classes[level] || ''}">${children}</${Tag}>`;
      },
      paragraph: ({ children }) => `<p class="mb-4 leading-relaxed">${children}</p>`,
      code_block: ({ attrs, children }) => {
        return `<pre class="bg-gray-900 text-white p-4 rounded-lg overflow-x-auto"><code class="language-${attrs.class || ''}">${children}</code></pre>`;
      }
    }
  }
});
```

```jsx
// Good: React - Handle embedded components in rich text
import { StoryblokComponent } from '@storyblok/react';
import { richTextResolver, MarkTypes, BlockTypes } from '@storyblok/richtext';

const { render } = richTextResolver({
  renderFn: (tag, attrs, children) => {
    // Handle React elements for embedded blocks
    if (attrs?.blok) {
      return <StoryblokComponent blok={attrs.blok} key={attrs.blok._uid} />;
    }
    // Return HTML string for other nodes
    return `<${tag}${attrsToString(attrs)}>${children}</${tag}>`;
  },
  resolvers: {
    [BlockTypes.COMPONENT]: (node) => {
      return { blok: node.attrs.body[0] };
    }
  }
});
```

```vue
<!-- Good: Vue - StoryblokRichText component -->
<template>
  <article v-editable="blok">
    <StoryblokRichText
      :doc="blok.content"
      :resolvers="resolvers"
    />
  </article>
</template>

<script setup>
import { StoryblokRichText } from '@storyblok/vue';

const resolvers = {
  marks: {
    link: ({ attrs, children }) => ({
      tag: 'a',
      attrs: { href: attrs.href, class: 'text-blue-600 hover:underline' },
      children
    })
  }
};
</script>
```

**Rich text node types:**

| Type | Description | Custom Resolver Use Case |
|------|-------------|-------------------------|
| `paragraph` | Text paragraph | Custom spacing, styling |
| `heading` | H1-H6 headings | Custom classes, anchors |
| `code_block` | Code blocks | Syntax highlighting |
| `image` | Inline images | Responsive images, captions |
| `blok` | Embedded components | StoryblokComponent rendering |
| `table` | Data tables | Custom table styling |

```jsx
// Good: @storyblok/richtext v3 - Table rendering
import { richTextResolver, BlockTypes } from '@storyblok/richtext';

const { render } = richTextResolver({
  resolvers: {
    [BlockTypes.TABLE]: ({ children }) => {
      return `
        <div class="table-wrapper overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            ${children}
          </table>
        </div>
      `;
    },
    [BlockTypes.TABLE_ROW]: ({ children, attrs }) => {
      const isHeader = attrs?.isHeader;
      return isHeader
        ? `<thead><tr class="bg-gray-50">${children}</tr></thead>`
        : `<tr class="hover:bg-gray-50">${children}</tr>`;
    },
    [BlockTypes.TABLE_CELL]: ({ children, attrs }) => {
      const tag = attrs?.isHeader ? 'th' : 'td';
      const classes = attrs?.isHeader
        ? 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
        : 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
      return `<${tag} class="${classes}">${children}</${tag}>`;
    }
  }
});
```

```jsx
// Good: React 19 compatible - Using React.createElement
import { richTextResolver, BlockTypes } from '@storyblok/richtext';
import { createElement, Fragment } from 'react';
import { StoryblokComponent } from '@storyblok/react';

// React 19 renderFn for JSX output
const { render } = richTextResolver({
  renderFn: createElement,
  textFn: (text) => text,
  resolvers: {
    [BlockTypes.PARAGRAPH]: ({ children }) => {
      return createElement('p', { className: 'mb-4' }, children);
    },
    [BlockTypes.HEADING]: ({ children, attrs }) => {
      const level = attrs?.level || 2;
      return createElement(`h${level}`, {
        className: `text-${4 - level}xl font-bold mb-4`
      }, children);
    },
    [BlockTypes.COMPONENT]: ({ node }) => {
      const blok = node.attrs?.body?.[0];
      if (!blok) return null;
      return createElement(StoryblokComponent, { blok, key: blok._uid });
    }
  }
});

// Component usage with React output
const RichTextComponent = ({ content }) => {
  const elements = render(content);
  return createElement(Fragment, null, elements);
};
```

```jsx
// Good: Syntax highlighting for code blocks
import { richTextResolver, BlockTypes } from '@storyblok/richtext';
import hljs from 'highlight.js';

const { render } = richTextResolver({
  resolvers: {
    [BlockTypes.CODE_BLOCK]: ({ children, attrs }) => {
      const language = attrs?.class?.replace('language-', '') || 'plaintext';
      let highlighted;

      try {
        highlighted = hljs.highlight(children, { language }).value;
      } catch {
        highlighted = hljs.highlightAuto(children).value;
      }

      return `
        <div class="code-block relative">
          <span class="language-label absolute top-2 right-2 text-xs text-gray-400">
            ${language}
          </span>
          <pre class="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <code class="hljs language-${language}">${highlighted}</code>
          </pre>
        </div>
      `;
    }
  }
});
```

```jsx
// Good: Custom emoji mark (v3 feature)
import { richTextResolver, MarkTypes } from '@storyblok/richtext';

const { render } = richTextResolver({
  resolvers: {
    marks: {
      [MarkTypes.EMOJI]: ({ attrs }) => {
        return `<span class="emoji" role="img" aria-label="${attrs.name}">${attrs.emoji}</span>`;
      },
      [MarkTypes.SUPERSCRIPT]: ({ children }) => {
        return `<sup>${children}</sup>`;
      },
      [MarkTypes.SUBSCRIPT]: ({ children }) => {
        return `<sub>${children}</sub>`;
      }
    }
  }
});
```

Reference: [@storyblok/richtext](https://www.storyblok.com/docs/packages/storyblok-richtext)
