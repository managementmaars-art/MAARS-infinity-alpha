# Deployment Workflows

## Deploy a Next.js App from GitHub

```bash
# 1. Create project
guara projects create --name my-nextjs-app

# 2. Link directory
guara link --project my-nextjs-app

# 3. Create service (buildpack auto-detects Next.js)
guara services create --name web --build-method buildpack \
  --repo https://github.com/user/nextjs-app --port 3000

# 4. Set environment variables (if needed)
guara env set --service web NODE_ENV=production NEXT_PUBLIC_API_URL=https://api.example.com

# 5. Deploy
guara deploy --service web

# 6. Verify
guara services info --service web
guara open --service web
```

## Deploy with a Dockerfile

```bash
# 1. Create project and service
guara projects create --name my-api
guara services create --name api --build-method dockerfile \
  --repo https://github.com/user/my-api --port 8080

# 2. Set env vars
guara env set --project my-api --service api \
  DATABASE_URL=postgres://... REDIS_URL=redis://...

# 3. Deploy
guara deploy --project my-api --service api

# 4. Check deployment
guara deployments list --project my-api --service api
```

## Deploy a Monorepo Service

```bash
# For a monorepo with apps/web/ and apps/api/ directories:

guara projects create --name my-platform

# Frontend
guara services create --name web --build-method buildpack \
  --repo https://github.com/user/monorepo \
  --root-dir ./apps/web \
  --build-cmd "pnpm --filter web build" \
  --start-cmd "pnpm --filter web start" \
  --port 3000

# Backend
guara services create --name api --build-method dockerfile \
  --repo https://github.com/user/monorepo \
  --root-dir ./apps/api \
  --dockerfile-path Dockerfile \
  --port 8080

# Deploy both
guara deploy --service web
guara deploy --service api
```

## Multi-Service Project

```bash
# Create project
guara projects create --name saas-app

# Frontend service
guara services create --name frontend --build-method buildpack \
  --repo https://github.com/user/frontend --port 3000

# API service
guara services create --name api --build-method dockerfile \
  --repo https://github.com/user/api --port 8080

# Worker service (background jobs)
guara services create --name worker --build-method dockerfile \
  --repo https://github.com/user/worker --port 9090

# Set shared env vars
guara env set --service api DATABASE_URL=postgres://... JWT_SECRET=xxx
guara env set --service worker DATABASE_URL=postgres://... REDIS_URL=redis://...

# Frontend needs the API URL
guara env set --service frontend NEXT_PUBLIC_API_URL=https://api-saas-app.guaracloud.com

# Deploy all
guara deploy --service frontend
guara deploy --service api
guara deploy --service worker
```

## Add a Custom Domain

```bash
# 1. Add domain to service
guara domains add --domain app.mycompany.com --service frontend

# 2. CLI outputs CNAME target. Add DNS record at your provider:
#    app.mycompany.com CNAME <target-from-cli-output>

# 3. Wait for DNS propagation and check status
guara domains list --service frontend

# Status: pending -> active
```

## Rollback a Failed Deployment

```bash
# 1. Check what happened
guara deployments list
guara logs --level error --since 10m

# 2. Rollback to last healthy deployment
guara rollback

# 3. Verify
guara services info
```

## Update Environment and Redeploy

```bash
# Setting env vars triggers a rolling restart automatically
guara env set NEW_KEY=value

# To deploy new code instead:
guara deploy

# To deploy a specific branch:
guara deploy --branch hotfix/critical-fix
```
