# Railway One-Click Deployment

Deploy Claw Control to Railway in under 5 minutes with zero configuration.

---

## 🚀 Deploy Now

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/claw-control)

Click the button above to deploy your own instance of Claw Control!

---

## What Gets Deployed

The Railway template provisions a complete production-ready stack:

| Service | Description | Resource |
|---------|-------------|----------|
| **Frontend** | React 19 dashboard with Vite | ~64MB RAM |
| **Backend** | Fastify API server with SSE | ~128MB RAM |
| **PostgreSQL** | Managed database instance | ~256MB RAM |

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Railway                          │
├─────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────────┐   │
│  │ Frontend  │──│  Backend  │──│  PostgreSQL   │   │
│  │  (React)  │  │ (Fastify) │  │   (Managed)   │   │
│  │           │  │           │  │               │   │
│  │ Port 80   │  │ Port 3001 │  │  Port 5432    │   │
│  └───────────┘  └───────────┘  └───────────────┘   │
│       ↓              ↓                              │
│  Public URL     Public URL       Internal Only      │
└─────────────────────────────────────────────────────┘
```

### Service Details

**Frontend Service:**
- Built from `packages/frontend`
- Nginx serving static React build
- Auto-generated Railway domain
- Environment: `VITE_API_URL` linked to backend

**Backend Service:**
- Built from `packages/backend`
- Node.js with Fastify
- Health check on `/health`
- Auto-restarts on failure
- Environment: `DATABASE_URL` linked to PostgreSQL

**PostgreSQL Database:**
- Railway managed Postgres 16
- Automatic backups (Pro plan)
- Persistent storage included
- Connection pooling enabled

---

## Environment Variables

### Auto-Configured (Railway handles these)

| Variable | Service | Description |
|----------|---------|-------------|
| `DATABASE_URL` | Backend | PostgreSQL connection string (auto-linked) |
| `PORT` | Backend | Server port (defaults to 3001) |
| `PGHOST`, `PGPORT`, etc. | Backend | PostgreSQL connection details |

### Required Configuration

| Variable | Service | Description | Example |
|----------|---------|-------------|---------|
| `VITE_API_URL` | Frontend | Backend API URL | `https://claw-backend-xxx.railway.app` |

### Optional Configuration

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `API_KEY` | Backend | *(none)* | Protect POST/PUT/DELETE endpoints |
| `NODE_ENV` | Backend | `production` | Environment mode |
| `AGENTS_CONFIG_PATH` | Backend | `./config/agents.yaml` | Custom agent config |

### Setting Up API_KEY

For security, set an API key to protect write operations:

```bash
# Generate a secure key
openssl rand -hex 32
```

Add to Backend service variables:
```
API_KEY=your-generated-32-char-key
```

Then include it in agent requests:
```bash
curl -X POST https://your-backend.railway.app/api/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-generated-32-char-key" \
  -d '{"title": "New Task", "status": "todo"}'
```

---

## Post-Deployment Steps

### Step 1: Wait for Build (2-3 minutes)

After clicking deploy:
1. Railway clones the repository
2. Each service builds independently
3. PostgreSQL spins up first
4. Backend runs database migrations
5. Frontend builds and serves

### Step 2: Link Services

If not auto-linked during template deploy:

1. **Link DATABASE_URL to Backend:**
   - Click Backend service → Variables
   - Add variable → Reference → Select PostgreSQL → `DATABASE_URL`

2. **Set VITE_API_URL for Frontend:**
   - Get Backend URL: Backend service → Settings → Domains
   - Click Frontend service → Variables
   - Add: `VITE_API_URL=https://your-backend-domain.railway.app`
   - Redeploy Frontend

### Step 3: Verify Deployment

1. **Check Backend Health:**
   ```bash
   curl https://your-backend.railway.app/health
   # Should return: {"status":"ok","timestamp":"..."}
   ```

2. **Check Database Connection:**
   ```bash
   curl https://your-backend.railway.app/api/health
   # Should return: {"status":"ok","database":"connected"}
   ```

3. **Open Dashboard:**
   - Navigate to your Frontend URL
   - You should see the Claw Control dashboard
   - The activity feed should be working (SSE connection)

### Step 4: Configure Agents (Optional)

Create custom agents by modifying `config/agents.yaml`:

```yaml
agents:
  - id: 1
    name: "Goku"
    role: "coordinator"
    avatar: "https://example.com/goku.png"
  - id: 2
    name: "Vegeta"
    role: "backend"
    avatar: "https://example.com/vegeta.png"
```

After pushing changes, Railway auto-deploys.

### Step 5: Connect Your AI Agents

Point your AI agents to the backend:

```python
import requests

API_URL = "https://your-backend.railway.app"
API_KEY = "your-api-key"

# Report agent status
requests.put(f"{API_URL}/api/agents/1", 
    json={"status": "working"},
    headers={"X-API-Key": API_KEY}
)

# Create a task
requests.post(f"{API_URL}/api/tasks",
    json={"title": "Research topic", "status": "todo", "agent_id": 1},
    headers={"X-API-Key": API_KEY}
)
```

---

## Troubleshooting

### Build Fails

**Symptom:** "Build failed" in Railway dashboard

**Solutions:**
1. Check build logs for specific error
2. Ensure `package.json` exists in both `packages/frontend` and `packages/backend`
3. Try redeploying: Settings → Redeploy

### Frontend Can't Connect to Backend

**Symptom:** Dashboard shows "Connection error" or empty data

**Solutions:**
1. Verify `VITE_API_URL` is set correctly (no trailing slash)
2. Check Backend is running: `curl <backend-url>/health`
3. Ensure CORS is allowing frontend origin
4. Redeploy Frontend after changing env vars

### Database Connection Failed

**Symptom:** Backend logs show "ECONNREFUSED" or "database not found"

**Solutions:**
1. Verify `DATABASE_URL` reference is linked, not hardcoded
2. Check PostgreSQL service is healthy (green status)
3. Try restarting Backend service
4. Check if migrations ran: look for "Migrations complete" in logs

### SSE/Live Updates Not Working

**Symptom:** Dashboard doesn't update in real-time

**Solutions:**
1. Check browser console for WebSocket/SSE errors
2. Verify Backend URL uses HTTPS (Railway provides this)
3. Some corporate firewalls block SSE - try different network

### "Out of Memory" Errors

**Symptom:** Service crashes with memory errors

**Solutions:**
1. Upgrade to a higher Railway plan
2. Check for memory leaks in custom code
3. Reduce concurrent SSE connections

### Domain Not Accessible

**Symptom:** "Site can't be reached" or SSL errors

**Solutions:**
1. Wait 2-5 minutes for DNS propagation
2. Try accessing via Railway's internal URL first
3. Check domain settings in Railway dashboard

---

## Cost Estimate

### Railway Free Tier (Trial)

Railway offers a **$5 free trial credit** for new users:
- Enough for ~1-2 weeks of light usage
- All features available
- No credit card required initially

### Hobby Plan (~$5/month)

Typical costs for Claw Control:

| Resource | Cost | Notes |
|----------|------|-------|
| Frontend | ~$1-2/mo | Static hosting, low CPU |
| Backend | ~$2-3/mo | Node.js, moderate CPU |
| PostgreSQL | Included | Up to 1GB storage |
| **Total** | **~$5/mo** | Light to moderate usage |

### Pro Plan (~$20/month)

For production workloads:
- Unlimited usage-based pricing
- Team collaboration
- Automatic backups
- Priority support
- SLA guarantees

### Cost Optimization Tips

1. **Sleep services** during off-hours (manual)
2. **Use SQLite** instead of PostgreSQL for dev/personal use
3. **Monitor usage** in Railway dashboard
4. **Set spending limits** to avoid surprises

---

## Custom Domains

### Adding a Custom Domain

1. Go to service → Settings → Domains
2. Click "Add Custom Domain"
3. Enter your domain (e.g., `claw.yourdomain.com`)
4. Add the CNAME record to your DNS:
   ```
   claw.yourdomain.com CNAME <railway-provided-value>
   ```
5. Wait for SSL certificate provisioning (automatic)

### Recommended Setup

```
dashboard.yourdomain.com → Frontend service
api.yourdomain.com → Backend service
```

---

## Upgrading & Updates

### Auto-Deploy from GitHub

Railway auto-deploys when you push to your connected branch:

```bash
git add .
git commit -m "feat: add new feature"
git push origin main
# Railway automatically builds and deploys
```

### Manual Redeploy

1. Go to service in Railway
2. Click "Redeploy" → "Redeploy from latest commit"

### Rolling Back

1. Go to service → Deployments
2. Find previous working deployment
3. Click "..." → "Rollback to this deployment"

---

## FAQ

**Q: Can I use SQLite instead of PostgreSQL?**
A: Yes, but not recommended for Railway. PostgreSQL is auto-provisioned and more reliable for cloud deployments.

**Q: How do I access the database directly?**
A: Railway provides connection details in the PostgreSQL service variables. Use any PostgreSQL client.

**Q: Can I run multiple instances?**
A: Yes, create a new project from the template. Each gets isolated resources.

**Q: Is my data backed up?**
A: On Pro plan, PostgreSQL has automatic backups. On Hobby plan, set up manual backups.

**Q: Can I export my data?**
A: Yes, use `pg_dump` with the Railway connection string or export via API.

---

## Need Help?

- 📖 [Full Documentation](./README.md)
- 🐛 [Report Issues](https://github.com/adarshmishra07/claw-control/issues)
- 💬 [Railway Discord](https://discord.gg/railway)
- 🦞 [Claw Control GitHub](https://github.com/adarshmishra07/claw-control)

---

<p align="center">
  Happy deploying! 🚀🦞
</p>
