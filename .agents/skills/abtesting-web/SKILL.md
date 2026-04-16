---
name: abtesting-web
cluster: abtesting
description: "Web A/B: feature flags LaunchDarkly/Unleash, cookie segmentation, Cloudflare Workers A/B, header routing"
tags: ["web","feature-flags","launchdarkly","cloudflare"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "web ab test feature flag launchdarkly cloudflare workers segment"
---

## Purpose
This skill, abtesting-web, facilitates A/B testing for web applications by managing feature flags with tools like LaunchDarkly or Unleash, implementing cookie-based user segmentation, and routing traffic via Cloudflare Workers or header-based rules. It ensures controlled experimentation to optimize web features without downtime.

## When to Use
Use this skill for dynamic feature rollouts in web apps, such as testing new UI elements, personalizing content via cookies, or splitting traffic for experiments. Apply it when you need scalable A/B testing with tools like LaunchDarkly for enterprise features or Unleash for cost-effective setups, especially in environments with Cloudflare.

## Key Capabilities
- Feature flags: Integrate LaunchDarkly to toggle flags via API, e.g., check flag status with Unleash's `/api/features` endpoint.
- Cookie segmentation: Parse cookies in Cloudflare Workers to segment users, e.g., check for a specific cookie value like `document.cookie.includes('variant=A')`.
- Cloudflare Workers A/B: Route requests based on rules, such as using `fetch(event.request)` with conditional logic for 50% traffic split.
- Header routing: Evaluate request headers in code, e.g., if `event.request.headers.get('X-Experiment') === 'group1'`, route accordingly.
- Specific configs: Use JSON format for flag definitions, e.g., `{"name": "new-feature", "enabled": true, "variants": ["A", "B"]}`.

## Usage Patterns
To set up A/B testing, first initialize the skill with your API key, e.g., run `openclaw abtesting-web init --provider launchdarkly --key $LAUNCHDARKLY_API_KEY`. For ongoing use, query flags in your web app code: import the SDK and check status like `ldClient.variation('feature-key', false)`. Pattern for segmentation: In Cloudflare Workers, add event handlers to evaluate cookies or headers before proxying requests. Always test locally first with a mock server, then deploy via `openclaw abtesting-web deploy --env production`.

## Common Commands/API
- CLI Commands: Initialize with `openclaw abtesting-web init --cluster abtesting --tags web,feature-flags`. Create a flag via `openclaw abtesting-web create-flag --name new-ui --provider unleash --variants A,B`. List flags with `openclaw abtesting-web list --key $CLOUDFLARE_API_TOKEN`.
- API Endpoints: For LaunchDarkly, use POST to `https://app.launchdarkly.com/api/v2/flags/{projectKey}/{featureFlagKey}` with JSON body like `{"name": "test-flag", "variations": ["control", "variant"]}`. For Unleash, GET `https://your-unleash-instance/api/features` with auth header `Authorization: $UNLEASH_API_KEY`.
- Code Snippets:
  - Cloudflare Worker for A/B routing:
    ```
    addEventListener('fetch', event => {
      const variant = Math.random() < 0.5 ? 'A' : 'B';
      event.respondWith(fetch(event.request, { headers: { 'X-Variant': variant } }));
    });
    ```
  - LaunchDarkly flag check in Node.js:
    ```
    const ldClient = require('launchdarkly-node-server-sdk');
    ldClient variation('feature-key', false, (err, variation) => console.log(variation));
    ```

## Integration Notes
Integrate by setting environment variables for keys, e.g., export `LAUNCHDARKLY_API_KEY` and `CLOUDFLARE_API_TOKEN`. For web apps, add the skill as a middleware: in Express.js, use `app.use(abtestingMiddleware({ provider: 'launchdarkly' }))`. Config format: Use a YAML file like `abtesting-config.yaml` with content:
```
provider: launchdarkly
flags:
  - name: homepage-test
    variants: [A, B]
    percentage: 50
```
To combine with other services, ensure CORS is enabled for API calls, and handle webhooks for flag updates. For Cloudflare, bind the Worker to your domain via the dashboard or CLI: `wrangler publish --env production`.

## Error Handling
Common errors include invalid API keys (HTTP 401), resolved by checking `echo $LAUNCHDARKLY_API_KEY` and retrying. For flag not found, catch with try-catch in code, e.g.:
```
try {
  const flag = await ldClient.getFeatureFlag('nonexistent');
} catch (error) {
  console.error('Flag error:', error.message); // Output: "Feature flag not found"
  fallbackToDefault();
}
```
Handle network issues by adding retries: in Cloudflare Workers, use `event.waitUntil(fetchWithRetry(event.request))`. For segmentation errors, validate cookies early, e.g., if parsing fails, default to control group. Use CLI debug mode: `openclaw abtesting-web run --debug` to log API responses.

## Concrete Usage Examples
1. **Example 1: Launch A/B Test for a Web Feature**: To test a new button on your site, first run `openclaw abtesting-web init --provider launchdarkly --key $LAUNCHDARKLY_API_KEY`. Then, create the flag: `openclaw abtesting-web create-flag --name button-test --variants control,experimental`. In your frontend code, check the flag: `if (ldClient.variation('button-test') === 'experimental') { renderNewButton(); }`. Finally, monitor via Cloudflare logs for traffic splits.
2. **Example 2: Cookie-Based Segmentation with Cloudflare**: Set up segmentation by adding a Worker: `openclaw abtesting-web deploy-worker --script path/to/worker.js`. In the worker.js file, include:
   ```
   addEventListener('fetch', event => {
     const cookieValue = event.request.headers.get('cookie')?.includes('segment=premium') ? 'premium' : 'standard';
     event.respondWith(fetch(event.request, { headers: { 'X-Segment': cookieValue } }));
   });
   ```
   Use this to route premium users to variant A.

## Graph Relationships
- Related to cluster: abtesting (e.g., shares resources with other abtesting skills).
- Related to tags: web (links to web-focused skills), feature-flags (connects to flag management tools), launchdarkly (integrates with LaunchDarkly-specific skills), cloudflare (ties into Cloudflare infrastructure skills).
