---
name: sanity-cms
description: Sanity headless CMS including GROQ queries, schema definition, Studio configuration, image pipeline, and webhooks.
---

# Sanity CMS

## Overview

Sanity is a headless CMS with a real-time content lake, GROQ query language, customizable Studio, and a powerful image transformation pipeline via Sanity CDN.

## Installation & Setup

```bash
# Create new Sanity project
npm create sanity@latest

# Install client in your app
npm install @sanity/client @sanity/image-url

# Sanity CLI
npm install -g @sanity/cli
sanity login
sanity init
sanity deploy   # Deploy Studio
```

## Schema Definition

```javascript
// schemas/post.js
export default {
  name: "post",
  title: "Blog Post",
  type: "document",
  fields: [
    {
      name: "title",
      title: "Title",
      type: "string",
      validation: (Rule) => Rule.required().min(10).max(100),
    },
    {
      name: "slug",
      title: "Slug",
      type: "slug",
      options: { source: "title", maxLength: 96 },
      validation: (Rule) => Rule.required(),
    },
    {
      name: "author",
      title: "Author",
      type: "reference",
      to: [{ type: "author" }],
    },
    {
      name: "mainImage",
      title: "Main Image",
      type: "image",
      options: { hotspot: true },
      fields: [
        { name: "alt", type: "string", title: "Alternative Text" },
        { name: "caption", type: "string", title: "Caption" },
      ],
    },
    {
      name: "categories",
      title: "Categories",
      type: "array",
      of: [{ type: "reference", to: { type: "category" } }],
    },
    {
      name: "publishedAt",
      title: "Published at",
      type: "datetime",
    },
    {
      name: "body",
      title: "Body",
      type: "array",
      of: [
        { type: "block" },
        {
          type: "image",
          options: { hotspot: true },
          fields: [{ name: "alt", type: "string", title: "Alt Text" }],
        },
        {
          type: "code",
          options: { language: "javascript", withFilename: true },
        },
      ],
    },
    {
      name: "seo",
      title: "SEO",
      type: "object",
      fields: [
        { name: "metaTitle", type: "string" },
        { name: "metaDescription", type: "text", rows: 3 },
        { name: "ogImage", type: "image" },
      ],
    },
  ],
  preview: {
    select: {
      title: "title",
      author: "author.name",
      media: "mainImage",
    },
    prepare(selection) {
      const { author } = selection;
      return { ...selection, subtitle: author ? `by ${author}` : "" };
    },
  },
  orderings: [
    {
      title: "Published Date, New",
      name: "publishedAtDesc",
      by: [{ field: "publishedAt", direction: "desc" }],
    },
  ],
};
```

## GROQ Queries

```javascript
import { createClient } from "@sanity/client";

const client = createClient({
  projectId: process.env.SANITY_PROJECT_ID,
  dataset: process.env.SANITY_DATASET || "production",
  apiVersion: "2024-01-01",    // Pin to a date for stability
  useCdn: true,                // Use CDN for reads (faster, cached)
  token: process.env.SANITY_TOKEN, // Only needed for writes/drafts
});

// Fetch all published posts with author and categories
const posts = await client.fetch(`
  *[_type == "post" && defined(slug.current) && publishedAt <= now()] | order(publishedAt desc) {
    _id,
    title,
    "slug": slug.current,
    publishedAt,
    "author": author-> {
      name,
      "image": image.asset->url,
      bio
    },
    "categories": categories[]-> { title, "slug": slug.current },
    "mainImage": mainImage {
      asset->,
      alt,
      hotspot,
      crop
    },
    "estimatedReadingTime": round(length(pt::text(body)) / 5 / 180)
  }
`);

// Single post by slug
const post = await client.fetch(`
  *[_type == "post" && slug.current == $slug][0] {
    ...,
    "author": author-> { name, bio, "image": image.asset->url },
    "relatedPosts": *[_type == "post" && references(^.categories[]._ref) && _id != ^._id][0..2] {
      title,
      "slug": slug.current,
      mainImage
    }
  }
`, { slug });

// Paginated query
const { data, total } = await client.fetch(`
  {
    "data": *[_type == "post"] | order(publishedAt desc) [$start...$end] {
      _id, title, "slug": slug.current, publishedAt
    },
    "total": count(*[_type == "post"])
  }
`, { start: page * 10, end: (page + 1) * 10 });

// Full-text search
const results = await client.fetch(`
  *[_type == "post" && [title, pt::text(body)] match $query] {
    _id, title, "slug": slug.current,
    "excerpt": pt::text(body)[0..200]
  }
`, { query: `${searchTerm}*` });
```

## Image Pipeline with @sanity/image-url

```javascript
import imageUrlBuilder from "@sanity/image-url";

const builder = imageUrlBuilder(client);

function urlFor(source) {
  return builder.image(source);
}

// Usage examples
const imageUrl = urlFor(post.mainImage)
  .width(800)
  .height(450)
  .fit("crop")
  .crop("focalpoint")   // Uses hotspot data
  .auto("format")       // Serve WebP/AVIF when supported
  .quality(80)
  .url();

// Responsive srcset
function getSrcSet(image, widths = [400, 800, 1200, 1600]) {
  return widths
    .map((w) => `${urlFor(image).width(w).auto("format").url()} ${w}w`)
    .join(", ");
}

// Next.js Image component integration
function SanityImage({ image, alt, ...props }) {
  return (
    <Image
      src={urlFor(image).url()}
      alt={image.alt || alt}
      sizes="(max-width: 768px) 100vw, 50vw"
      {...props}
    />
  );
}
```

## Studio Configuration

```javascript
// sanity.config.ts
import { defineConfig } from "sanity";
import { deskTool } from "sanity/desk";
import { visionTool } from "@sanity/vision";
import { media } from "sanity-plugin-media";
import { colorInput } from "@sanity/color-input";
import { schemaTypes } from "./schemas";
import { structure } from "./desk/structure";

export default defineConfig({
  name: "default",
  title: "My CMS",
  projectId: process.env.SANITY_STUDIO_PROJECT_ID,
  dataset: process.env.SANITY_STUDIO_DATASET || "production",
  plugins: [
    deskTool({ structure }),
    visionTool(),      // GROQ query playground
    media(),           // Media library plugin
    colorInput(),
  ],
  schema: { types: schemaTypes },
  document: {
    // Prevent accidental deletion of referenced documents
    actions: (prev, { schemaType }) =>
      schemaType === "post"
        ? prev.filter(({ action }) => action !== "delete")
        : prev,
  },
});

// desk/structure.ts - Custom desk structure
import { StructureBuilder } from "sanity/desk";

export const structure = (S: StructureBuilder) =>
  S.list()
    .title("Content")
    .items([
      S.listItem()
        .title("Blog Posts")
        .child(
          S.documentList()
            .title("Posts")
            .filter('_type == "post"')
            .defaultOrdering([{ field: "publishedAt", direction: "desc" }])
        ),
      S.divider(),
      ...S.documentTypeListItems().filter(
        (item) => !["post"].includes(item.getId())
      ),
    ]);
```

## Webhooks & Real-time Listening

```javascript
// Webhook handler (Next.js API route)
import { isValidSignature, SIGNATURE_HEADER_NAME } from "@sanity/webhook";

export async function POST(request) {
  const body = await request.text();
  const signature = request.headers.get(SIGNATURE_HEADER_NAME);

  if (!isValidSignature(body, signature, process.env.SANITY_WEBHOOK_SECRET)) {
    return new Response("Unauthorized", { status: 401 });
  }

  const event = JSON.parse(body);
  const { _type, _id, operation } = event;

  if (_type === "post" && ["create", "update"].includes(operation)) {
    // Revalidate Next.js cache
    await fetch(`/api/revalidate?tag=posts&secret=${process.env.REVALIDATE_SECRET}`);
  }

  return new Response("OK");
}

// Real-time listener for live preview
const subscription = client
  .listen('*[_type == "post"]', {}, { includeResult: true })
  .subscribe((update) => {
    if (update.type === "mutation") {
      console.log("Document updated:", update.result);
      refreshPreview(update.result);
    }
  });

// Cleanup
subscription.unsubscribe();
```

## Mutations (Writing Content)

```javascript
// Create a document
await client.create({
  _type: "post",
  title: "New Post",
  slug: { _type: "slug", current: "new-post" },
  publishedAt: new Date().toISOString(),
});

// Patch (update) a document
await client
  .patch("document-id")
  .set({ title: "Updated Title" })
  .setIfMissing({ publishedAt: new Date().toISOString() })
  .inc({ viewCount: 1 })
  .commit();

// Upload an asset
const imageAsset = await client.assets.upload("image", fileBuffer, {
  filename: "my-image.jpg",
  contentType: "image/jpeg",
});

// Transaction for atomic operations
await client
  .transaction()
  .create({ _type: "category", title: "Tech" })
  .patch("post-id", (p) => p.set({ published: true }))
  .commit();
```

## Key Patterns

- **Pin `apiVersion`** to a date string to prevent breaking changes
- **Use CDN** (`useCdn: true`) for public reads; disable for drafts/previews
- **GROQ projections** shape the response — only fetch fields you need
- **Hotspot + crop** enables smart image cropping around focal points
- **Real-time listener** powers live preview and collaborative editing
- **Webhooks** trigger ISR/cache revalidation in Next.js or other frameworks

## Models to Use

- **claude-opus-4-5**: Complex schema design, content modeling, custom plugins
- **claude-sonnet-4-5**: GROQ queries, Studio configuration, image pipelines
- **claude-haiku-3-5**: Simple queries, field additions, webhook setup
