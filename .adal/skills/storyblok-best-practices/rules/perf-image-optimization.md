---
title: Use Image Service for Optimized Delivery
impact: CRITICAL
impactDescription: dramatically improves page load performance
tags: images, performance, cdn, optimization, webp
---

## Use Image Service for Optimized Delivery

**Impact: CRITICAL (dramatically improves page load performance)**

Storyblok's Image Service provides on-the-fly resizing, format conversion, and CDN delivery. Always transform images using URL parameters instead of serving originals.

**Incorrect (unoptimized images):**

```jsx
// Bad: Using original image URL
const Image = ({ asset }) => {
  return <img src={asset.filename} alt={asset.alt} />;
  // Serves full-size original (often 5MB+)
};

// Bad: Only resizing, no format optimization
const Image = ({ asset }) => {
  const url = `${asset.filename}/m/500x300`;
  return <img src={url} alt={asset.alt} />;
  // Resizes but still serves as original format (PNG/JPG)
};

// Bad: Fixed dimensions without responsive
const Image = ({ asset }) => {
  return (
    <img
      src={`${asset.filename}/m/1200x800`}
      alt={asset.alt}
    />
  );
  // Same large image for all screen sizes
};
```

**Correct (fully optimized images):**

```jsx
// Good: Resize + explicit format conversion
const Image = ({ asset, width, height }) => {
  // /m/ triggers image service and auto-converts to WebP if browser supports it
  // For guaranteed format control (e.g., AVIF), use explicit format filters
  const optimizedUrl = `${asset.filename}/m/${width}x${height}/filters:format(webp):quality(80)`;

  return (
    <img
      src={optimizedUrl}
      alt={asset.alt || ''}
      width={width}
      height={height}
      loading="lazy"
    />
  );
};

// Good: Responsive images with srcset
const ResponsiveImage = ({ asset, sizes = '100vw' }) => {
  const widths = [320, 640, 960, 1280, 1920];

  const srcSet = widths
    .map((w) => `${asset.filename}/m/${w}x0/filters:quality(80) ${w}w`)
    .join(', ');

  return (
    <img
      src={`${asset.filename}/m/960x0/filters:quality(80)`}
      srcSet={srcSet}
      sizes={sizes}
      alt={asset.alt || ''}
      loading="lazy"
      decoding="async"
    />
  );
};

// Good: Picture element with format fallbacks
const OptimizedPicture = ({ asset, width, height }) => {
  const baseUrl = `${asset.filename}/m/${width}x${height}`;

  return (
    <picture>
      <source
        srcSet={`${baseUrl}/filters:format(avif):quality(75)`}
        type="image/avif"
      />
      <source
        srcSet={`${baseUrl}/filters:format(webp):quality(80)`}
        type="image/webp"
      />
      <img
        src={`${baseUrl}/filters:quality(85)`}
        alt={asset.alt || ''}
        width={width}
        height={height}
        loading="lazy"
      />
    </picture>
  );
};
```

```jsx
// Good: Next.js Image component integration
import Image from 'next/image';

const storyblokLoader = ({ src, width, quality }) => {
  return `${src}/m/${width}x0/filters:quality(${quality || 75})`;
};

const StoryblokImage = ({ asset, width, height, priority = false }) => {
  return (
    <Image
      loader={storyblokLoader}
      src={asset.filename}
      alt={asset.alt || ''}
      width={width}
      height={height}
      priority={priority}
      quality={80}
    />
  );
};

// next.config.js
module.exports = {
  images: {
    loader: 'custom',
    loaderFile: './lib/storyblok-image-loader.js',
    domains: ['a.storyblok.com']
  }
};
```

**Image Service URL parameters:**

| Parameter | Example | Description |
|-----------|---------|-------------|
| Resize | `/m/800x600` | Width x Height (0 = auto) |
| Quality | `/filters:quality(80)` | JPEG/WebP quality 1-100 |
| Format | `/filters:format(webp)` | Force format (webp, avif, png) |
| Focal | `/m/800x600/filters:focal(300,200,500,400)` | Smart crop focal point |
| Blur | `/filters:blur(5)` | Gaussian blur |
| Grayscale | `/filters:grayscale()` | Black & white |

**Performance checklist:**

- [ ] Always use `/m/` for resizing
- [ ] Set explicit width/height to prevent layout shift
- [ ] Use `loading="lazy"` for below-fold images
- [ ] Provide `srcset` for responsive images
- [ ] Note: `/m/` auto-converts to WebP when supported; use explicit format for AVIF or specific needs
- [ ] Set quality to 75-85 for good compression

Reference: [Image Service](https://www.storyblok.com/docs/api/image-service/cache)
