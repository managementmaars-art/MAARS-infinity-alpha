---
title: Handle Rich Text Media Correctly
impact: MEDIUM
impactDescription: ensures proper rendering of embedded media
tags: richtext, media, images, assets
---

## Handle Rich Text Media Correctly

**Impact: MEDIUM (ensures proper rendering of embedded media)**

Rich text fields can contain embedded images, assets, and components. Handle these with custom resolvers to ensure proper optimization and styling.

**Incorrect (ignoring embedded media):**

```jsx
// Bad: Only rendering text, missing images
import { richTextResolver } from '@storyblok/richtext';

const { render } = richTextResolver();

const RichText = ({ content }) => {
  return <div dangerouslySetInnerHTML={{ __html: render(content) }} />;
  // Images render with original URLs, no optimization
};

// Bad: Not handling embedded components
const { render } = richTextResolver();
// Embedded bloks render as [object Object] or are skipped
```

**Correct (comprehensive media handling):**

```jsx
// Good: Custom resolver for images and assets
import { richTextResolver, BlockTypes, MarkTypes } from '@storyblok/richtext';

const { render } = richTextResolver({
  resolvers: {
    [BlockTypes.IMAGE]: (node) => {
      const { src, alt, title } = node.attrs;

      // Apply image service optimization
      const optimizedSrc = `${src}/m/800x0/filters:quality(80)`;
      const srcSet = [400, 800, 1200]
        .map(w => `${src}/m/${w}x0/filters:quality(80) ${w}w`)
        .join(', ');

      return `
        <figure class="rich-text-image">
          <img
            src="${optimizedSrc}"
            srcset="${srcSet}"
            sizes="(max-width: 800px) 100vw, 800px"
            alt="${alt || ''}"
            loading="lazy"
            decoding="async"
          />
          ${title ? `<figcaption>${title}</figcaption>` : ''}
        </figure>
      `;
    },

    [BlockTypes.PARAGRAPH]: ({ children }) => {
      if (!children || children === '<br>') return '';
      return `<p class="mb-4">${children}</p>`;
    },

    [BlockTypes.HEADING]: ({ attrs, children }) => {
      const level = attrs.level;
      const id = children
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/(^-|-$)/g, '');

      return `<h${level} id="${id}" class="heading-${level}">${children}</h${level}>`;
    }
  }
});
```

```jsx
// Good: React component with custom renderers
import { StoryblokComponent } from '@storyblok/react';
import { richTextResolver, BlockTypes } from '@storyblok/richtext';
import { createElement } from 'react';

const RichTextRenderer = ({ content, className }) => {
  // Custom renderers that return React elements
  const renderNode = (node, children) => {
    switch (node.type) {
      case BlockTypes.IMAGE:
        return (
          <figure key={Math.random()} className="rich-text-image">
            <img
              src={`${node.attrs.src}/m/800x0`}
              alt={node.attrs.alt || ''}
              loading="lazy"
            />
            {node.attrs.title && (
              <figcaption>{node.attrs.title}</figcaption>
            )}
          </figure>
        );

      case BlockTypes.BLOK:
        // Render embedded Storyblok components
        return node.attrs.body.map(blok => (
          <StoryblokComponent key={blok._uid} blok={blok} />
        ));

      case BlockTypes.PARAGRAPH:
        return <p key={Math.random()}>{children}</p>;

      default:
        return children;
    }
  };

  const html = render(content);

  return (
    <div
      className={`rich-text ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};
```

```jsx
// Good: Handle links to assets (PDFs, documents)
const { render } = richTextResolver({
  resolvers: {
    [MarkTypes.LINK]: ({ attrs, children }) => {
      const { href, target, linktype } = attrs;

      // Handle asset links
      if (linktype === 'asset') {
        const fileExt = href.split('.').pop().toLowerCase();
        const isDocument = ['pdf', 'doc', 'docx', 'xls', 'xlsx'].includes(fileExt);

        return `
          <a
            href="${href}"
            target="_blank"
            rel="noopener noreferrer"
            class="asset-link ${isDocument ? 'document-link' : ''}"
            download
          >
            ${children}
            <span class="file-type">(${fileExt.toUpperCase()})</span>
          </a>
        `;
      }

      // Handle story links
      if (linktype === 'story') {
        return `<a href="/${href}" class="internal-link">${children}</a>`;
      }

      // Handle email links
      if (linktype === 'email') {
        return `<a href="mailto:${href}">${children}</a>`;
      }

      // External links
      return `
        <a
          href="${href}"
          target="${target || '_self'}"
          ${target === '_blank' ? 'rel="noopener noreferrer"' : ''}
        >
          ${children}
        </a>
      `;
    }
  }
});
```

```jsx
// Good: Video embedding in rich text (via component)
const VideoEmbed = ({ blok }) => {
  const { video_url, caption } = blok;

  // Handle YouTube
  if (video_url.includes('youtube.com') || video_url.includes('youtu.be')) {
    const videoId = extractYouTubeId(video_url);
    return (
      <figure className="video-embed">
        <iframe
          src={`https://www.youtube-nocookie.com/embed/${videoId}`}
          title={caption}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          loading="lazy"
        />
        {caption && <figcaption>{caption}</figcaption>}
      </figure>
    );
  }

  // Handle Vimeo
  if (video_url.includes('vimeo.com')) {
    const videoId = extractVimeoId(video_url);
    return (
      <figure className="video-embed">
        <iframe
          src={`https://player.vimeo.com/video/${videoId}`}
          title={caption}
          allowFullScreen
          loading="lazy"
        />
        {caption && <figcaption>{caption}</figcaption>}
      </figure>
    );
  }

  return null;
};
```

**Rich text block types:**

| Block Type | Description | Custom Handling |
|------------|-------------|-----------------|
| `image` | Inline images | Optimization, srcset |
| `blok` | Embedded components | StoryblokComponent |
| `code_block` | Code snippets | Syntax highlighting |
| `horizontal_rule` | Separator | Custom styling |

Reference: [@storyblok/richtext](https://www.storyblok.com/docs/packages/storyblok-richtext)
