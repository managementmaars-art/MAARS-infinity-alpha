# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Content Modeling (model)

**Impact:** CRITICAL
**Description:** Proper component design, field configuration, block nesting, and schema architecture are fundamental to scalable and maintainable Storyblok projects.

## 2. SDK Integration (sdk)

**Impact:** CRITICAL
**Description:** Correct usage of @storyblok/react, @storyblok/vue, @storyblok/nuxt SDKs including storyblokEditable, StoryblokComponent, rich text rendering, and bridge configuration.

## 3. Visual Editor (editor)

**Impact:** CRITICAL
**Description:** Real-time visual editing experience, bridge setup, clickable elements, draft/published content handling, and preview environment configuration.

## 4. Performance & Caching (perf)

**Impact:** CRITICAL
**Description:** CDN caching, image optimization, cache invalidation, API rate limiting, and content delivery optimization strategies.

## 5. Field Plugins (plugin)

**Impact:** HIGH
**Description:** Custom field plugin development using @storyblok/field-plugin, sandbox testing, manifest configuration, and deployment patterns.

## 6. API Development (api)

**Impact:** HIGH
**Description:** Content Delivery API v2, Management API, GraphQL API usage, authentication, pagination, and response handling.

## 7. Internationalization (i18n)

**Impact:** HIGH
**Description:** Field-level translation, folder-level translation, language configuration, individual translation publishing, and multi-locale content management.

## 8. Security & Authentication (security)

**Impact:** CRITICAL
**Description:** Access token management, OAuth2 flows, personal access tokens, preview/public token usage, and secure API key handling.

## 9. Space & Asset Management (space)

**Impact:** HIGH
**Description:** Space configuration, asset handling, datasources, folders, multi-space architecture, and component sharing.

## 10. Webhooks & Automation (webhook)

**Impact:** MEDIUM-HIGH
**Description:** Webhook configuration, event handling, pipeline integration, releases app, and third-party automation.

## 11. Workflows & Publishing (workflow)

**Impact:** MEDIUM-HIGH
**Description:** Content workflows, release management, scheduling, versioning, approval stages, and content staging.

## 12. CLI & DevOps (cli)

**Impact:** MEDIUM
**Description:** Storyblok CLI v4 commands, component sync, migrations, CI/CD integration, and development environment setup.

## 13. Next.js Integration (nextjs)

**Impact:** HIGH
**Description:** Next.js App Router, React Server Components, draft mode, ISR/SSG strategies, and production deployment patterns.

## 14. Nuxt Integration (nuxt)

**Impact:** HIGH
**Description:** Nuxt 3/4 module configuration, useAsyncStoryblok, SSR/SSG setup, and Visual Editor integration.

## 15. App Development (app)

**Impact:** HIGH
**Description:** Tool plugins, space plugins, custom sidebar apps, App Bridge authentication, and OAuth2 implementation.

## 16. Testing & Quality (test)

**Impact:** MEDIUM
**Description:** Preview environment testing, content validation, TypeScript generation, and quality assurance patterns.

## 17. Rich Text & Media (richtext)

**Impact:** MEDIUM
**Description:** Rich text field rendering, custom resolvers, media handling, image service transformations, and asset optimization.

## 18. Common Patterns (pattern)

**Impact:** HIGH
**Description:** Error handling, TypeScript patterns, component registration, dynamic rendering, and reusable architecture patterns.

## 19. SEO & Structured Data (seo)

**Impact:** HIGH
**Description:** JSON-LD structured data, Open Graph metadata, sitemap generation, robots.txt configuration, and search engine optimization patterns.

## 20. E-commerce Integration (ecommerce)

**Impact:** HIGH
**Description:** Product reference patterns, commerce platform integration (Shopify, commercetools, BigCommerce), two-step data fetching, and cart/checkout flows.

## 21. Content Migration (migration)

**Impact:** MEDIUM-HIGH
**Description:** Legacy CMS migration strategies, schema transformation, content mapping, asset migration with deduplication, and rollback patterns.

## 22. AI Features (ai)

**Impact:** MEDIUM
**Description:** Storyblok AI capabilities including alt text generation, SEO suggestions, content summarization, RAG preparation, and Strata vector layer integration.
