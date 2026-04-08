---
name: netlify-deployment
description: Deploy web applications to Netlify including Functions, Edge Functions, Blobs, Forms, CLI usage, and CI/CD integration.
---

# Netlify Deployment

## Core Concepts

Netlify is a cloud platform for deploying static sites, Jamstack applications, and serverless functions. It provides global CDN, automatic HTTPS, deploy previews, and a suite of backend services.

## netlify.toml Configuration

```toml
[build]
  command = "npm run build"
  publish = "dist"
  functions = "netlify/functions"

[build.environment]
  NODE_VERSION = "20"
  NPM_VERSION = "10"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    Content-Security-Policy = "default-src 'self'"

[functions]
  node_bundler = "esbuild"
  external_node_modules = ["@prisma/client"]

[[plugins]]
  package = "@netlify/plugin-nextjs"

[context.production]
  command = "npm run build:prod"

[context.deploy-preview]
  command = "npm run build:preview"

[context.branch-deploy]
  command = "npm run build"
```

## Netlify Functions (Serverless)

```javascript
// netlify/functions/api.js
import { Handler } from "@netlify/functions";

export const handler: Handler = async (event, context) => {
  const { httpMethod, path, queryStringParameters, body, headers } = event;

  // Parse body safely
  let parsedBody = {};
  try {
    parsedBody = body ? JSON.parse(body) : {};
  } catch {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: "Invalid JSON body" }),
    };
  }

  // CORS headers
  const corsHeaders = {
    "Access-Control-Allow-Origin": process.env.ALLOWED_ORIGIN || "*",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  };

  if (httpMethod === "OPTIONS") {
    return { statusCode: 204, headers: corsHeaders, body: "" };
  }

  try {
    const result = await processRequest(parsedBody);
    return {
      statusCode: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      body: JSON.stringify(result),
    };
  } catch (error) {
    console.error("Function error:", error);
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({ error: "Internal server error" }),
    };
  }
};
```

```javascript
// netlify/functions/scheduled-task.js - Scheduled function
import { schedule } from "@netlify/functions";

export const handler = schedule("@hourly", async (event) => {
  const { next_run } = JSON.parse(event.body);
  console.log(`Running scheduled task. Next run: ${next_run}`);

  await performDatabaseCleanup();
  await sendDigestEmails();

  return { statusCode: 200 };
});
```

## Edge Functions

```javascript
// netlify/edge-functions/auth-guard.js
export default async (request, context) => {
  const url = new URL(request.url);

  // Skip auth for public routes
  if (url.pathname.startsWith("/public") || url.pathname === "/login") {
    return context.next();
  }

  const token = request.headers.get("Authorization")?.replace("Bearer ", "");

  if (!token) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Verify JWT at the edge (no cold starts!)
  try {
    const payload = await verifyJWT(token, context.env.JWT_SECRET);
    // Pass user info to the origin
    const requestWithUser = new Request(request, {
      headers: {
        ...Object.fromEntries(request.headers),
        "X-User-Id": payload.sub,
        "X-User-Role": payload.role,
      },
    });
    return context.next(requestWithUser);
  } catch {
    return Response.redirect(new URL("/login", request.url), 302);
  }
};

export const config = {
  path: ["/dashboard/*", "/api/*", "/admin/*"],
  excludedPath: ["/api/public/*"],
};
```

```javascript
// netlify/edge-functions/geo-redirect.js
export default async (request, context) => {
  const country = context.geo?.country?.code;
  const url = new URL(request.url);

  const regionMap = {
    GB: "uk",
    DE: "de",
    FR: "fr",
    JP: "jp",
  };

  const region = regionMap[country];
  if (region && !url.pathname.startsWith(`/${region}`)) {
    return Response.redirect(
      new URL(`/${region}${url.pathname}`, request.url),
      302
    );
  }

  // Add geo headers for downstream use
  const response = await context.next();
  const newResponse = new Response(response.body, response);
  newResponse.headers.set("X-Country", country || "unknown");
  return newResponse;
};
```

## Netlify Blobs (Object Storage)

```javascript
import { getStore } from "@netlify/blobs";

// netlify/functions/blob-operations.js
export const handler = async (event) => {
  // Get a store (scoped to deployment or site-wide)
  const store = getStore({
    name: "user-uploads",
    consistency: "strong", // or 'eventual'
  });

  if (event.httpMethod === "POST") {
    const { key, data } = JSON.parse(event.body);

    // Store with metadata
    await store.set(key, data, {
      metadata: {
        uploadedAt: new Date().toISOString(),
        contentType: "application/json",
      },
    });

    return { statusCode: 201, body: JSON.stringify({ key }) };
  }

  if (event.httpMethod === "GET") {
    const key = event.queryStringParameters?.key;

    // Get with metadata
    const result = await store.getWithMetadata(key, { type: "json" });
    if (!result) {
      return { statusCode: 404, body: JSON.stringify({ error: "Not found" }) };
    }

    return {
      statusCode: 200,
      body: JSON.stringify({ data: result.data, metadata: result.metadata }),
    };
  }

  // List blobs with prefix
  if (event.httpMethod === "GET" && event.queryStringParameters?.list) {
    const { blobs, cursor } = await store.list({
      prefix: event.queryStringParameters.prefix,
      limit: 50,
    });
    return { statusCode: 200, body: JSON.stringify({ blobs, cursor }) };
  }
};
```

## Netlify Forms

```html
<!-- Static HTML form with Netlify detection -->
<form name="contact" method="POST" data-netlify="true" data-netlify-honeypot="bot-field">
  <input type="hidden" name="form-name" value="contact" />
  <input type="hidden" name="bot-field" />
  <input type="text" name="name" required />
  <input type="email" name="email" required />
  <textarea name="message" required></textarea>
  <button type="submit">Send</button>
</form>
```

```javascript
// Form submission handler with file upload
// netlify/functions/form-handler.js (for form notifications webhook)
export const handler = async (event) => {
  const payload = JSON.parse(event.body);

  // Payload contains: form_name, data (field values), created_at
  const { form_name, data } = payload;

  await sendNotificationEmail({
    to: process.env.NOTIFICATION_EMAIL,
    subject: `New ${form_name} submission`,
    body: Object.entries(data)
      .map(([k, v]) => `${k}: ${v}`)
      .join("\n"),
  });

  return { statusCode: 200 };
};
```

## Netlify CLI

```bash
# Install and authenticate
npm install -g netlify-cli
netlify login

# Initialize a project
netlify init

# Local development with live reload
netlify dev

# Deploy commands
netlify deploy                    # Deploy to draft URL
netlify deploy --prod             # Deploy to production
netlify deploy --dir=dist --prod  # Deploy specific directory

# Environment variables
netlify env:set DATABASE_URL "postgresql://..."
netlify env:get DATABASE_URL
netlify env:list
netlify env:import .env.production

# Function management
netlify functions:list
netlify functions:invoke my-function --payload '{"key":"value"}'

# Logs
netlify logs:function my-function

# Site management
netlify sites:list
netlify sites:create --name my-app
netlify open:site
netlify open:admin

# Build plugins
netlify build --dry             # Test build locally
```

## CI/CD with GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Netlify

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}

      - name: Deploy to Netlify (Preview)
        if: github.event_name == 'pull_request'
        uses: netlify/actions/cli@master
        with:
          args: deploy --dir=dist --message="PR Preview #${{ github.event.number }}"
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}

      - name: Deploy to Netlify (Production)
        if: github.ref == 'refs/heads/main'
        uses: netlify/actions/cli@master
        with:
          args: deploy --dir=dist --prod --message="Production deploy"
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

## Key Patterns

- **Deploy previews**: Every PR gets a unique preview URL automatically
- **Atomic deploys**: All assets deploy atomically, no partial states
- **Instant cache invalidation**: CDN cache clears on each deploy
- **Branch deploys**: Map git branches to subdomains (staging.example.com)
- **Split testing**: A/B test between different deploy branches
- **Redirects/rewrites**: Handle SPA routing, proxies, and internationalization in `netlify.toml`
- **Environment contexts**: Different env vars for production, preview, and branch deploys

## Models to Use

- **claude-opus-4-5**: Complex architecture decisions, multi-service integration
- **claude-sonnet-4-5**: Standard function implementation, CI/CD setup
- **claude-haiku-3-5**: Quick config edits, simple redirect rules
