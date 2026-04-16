---
name: web-performance
cluster: web-dev
description: "Core Web Vitals, Lighthouse, bundle optimization, lazy loading, CDN, caching strategies"
tags: ["performance","web-vitals","lighthouse","web"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "web performance lighthouse vitals bundle optimization cdn cache"
---

## Purpose
This skill focuses on optimizing web performance by leveraging tools and strategies like Core Web Vitals, Lighthouse for audits, bundle optimization with Webpack, lazy loading in HTML/JS, CDN setup, and caching strategies to improve load times and user experience.

## When to Use
Use this skill when analyzing and improving site performance, such as for slow-loading pages, preparing for SEO impacts from Core Web Vitals, optimizing large JavaScript bundles, or implementing efficient asset delivery in production environments.

## Key Capabilities
- Run Lighthouse audits to measure Core Web Vitals (LCP, FID, CLS) with metrics like time to first byte.
- Optimize bundles using Webpack's TerserPlugin for minification and code splitting.
- Implement lazy loading via HTML attributes (e.g., `loading="lazy"` on images) or React's `lazy()` function.
- Configure CDNs with providers like Cloudflare for static asset delivery.
- Apply caching strategies using HTTP headers (e.g., Cache-Control: max-age=3600) or service workers.

## Usage Patterns
To accomplish tasks, invoke this skill via OpenClaw's API or CLI, passing parameters like URLs or config files. For audits, provide a URL and options; for optimization, supply code snippets or build configs. Always wrap calls in try-catch for error handling. Example pattern: Use the skill in a CI/CD pipeline to audit PR builds automatically.

## Common Commands/API
Use OpenClaw's CLI or API endpoint `/api/skills/web-performance/execute` with JSON payload. Authentication requires `$OPENCLAW_API_KEY` in headers.
- CLI: `openclaw execute web-performance --url https://example.com --audit-type full --output json`
- API: POST to `/api/skills/web-performance/execute` with body: `{"url": "https://example.com", "options": {"chromeFlags": "--headless"}}`
- Code snippet for lazy loading:
  ```javascript
  import React, { lazy, Suspense } from 'react';
  const LazyImage = lazy(() => import('./ImageComponent'));
  <Suspense fallback={<div>Loading...</div>}><LazyImage /></Suspense>;
  ```
- Webpack config for bundle optimization:
  ```json
  { "optimization": { "minimizer": ["terser-webpack-plugin"], "splitChunks": { "chunks": "all" } } }
  ```
- CDN config example: In Nginx, add `location /static/ { proxy_pass https://cdn.example.com; expires 1d; }`

## Integration Notes
Integrate by importing OpenClaw SDK and calling the skill function with required params. For auth, set env var `$OPENCLAW_API_KEY` before runtime. Combine with other skills like monitoring tools: e.g., pipe Lighthouse results to a logging service. Use JSON config files for multi-step optimizations, such as: `{"steps": ["audit", "optimize-bundle", "apply-caching"]}`. Ensure compatibility with Node.js 14+ for Webpack integrations.

## Error Handling
Handle errors by checking response codes from API calls (e.g., 400 for invalid URL, 401 for auth issues). In code, use try-catch around skill executions: e.g.,
```javascript
try {
  const result = await openclaw.execute('web-performance', { url: 'https://example.com' });
  console.log(result);
} catch (error) {
  if (error.code === 'AUTH_ERROR') process.env.OPENCLAW_API_KEY = 'new-key';
  else console.error(error.message);
}
```
Common issues: Invalid URLs return "Invalid input"; network errors suggest retry with exponential backoff. Always validate inputs like URLs before calling.

## Concrete Usage Examples
1. Audit a website with Lighthouse: Run `openclaw execute web-performance --url https://example.com --report-path ./report.json` to generate a JSON report with Core Web Vitals scores, then analyze LCP > 2.5s as a failure threshold.
2. Optimize and deploy with CDN: In a build script, use `openclaw execute web-performance --action optimize-bundle --config webpack.config.js`, followed by `openclaw execute web-performance --action setup-cdn --provider cloudflare --assets /static/`, to enable caching and reduce load times by 30-50%.

## Graph Relationships
- Connected to: web-dev cluster
- Related skills: seo-optimization (for performance-driven SEO), frontend-dev (for bundle and lazy loading integrations)
- Dependencies: monitoring-tools (for post-audit analysis)
