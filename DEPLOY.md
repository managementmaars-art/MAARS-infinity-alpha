# MAARS Command — Production Deploy Guide

**Target stack:** Render.com (backend + frontend) + MongoDB Atlas (database) + Stripe (billing)
**Time required:** 25–40 minutes
**Cost:** $0 to start (Atlas M0 free, Render free tier with sleep) → $7/mo for always-on backend

---

## What you'll do at a glance

1. Create accounts (3 places) — 5 min
2. Provision MongoDB Atlas free cluster — 7 min
3. Push this repo to GitHub — 3 min
4. Connect Render to the repo and Apply the blueprint — 3 min
5. Paste 8 env-var values into Render dashboard — 5 min
6. Configure Stripe live mode + webhook — 5 min
7. Verify production URL works — 2 min

I (Claude in your terminal) cannot do steps 1, 2, 3 (the GitHub push), 4, 6, or 7 — those are GUI / browser auth flows. I can prepare every file, write every config, and tell you the exact value to paste at every step. You provide eyeballs and clicks.

---

## Step 1 — Create accounts (5 min)

| Service | URL | What you need |
|---|---|---|
| GitHub | <https://github.com> | Free account; you push your code here |
| Render | <https://render.com> | Sign up with GitHub (one-click) — Render reads your repos directly |
| MongoDB Atlas | <https://www.mongodb.com/cloud/atlas/register> | Sign up with Google or email; M0 free tier is what you want |

If you already have any of these (you almost certainly have GitHub and Google), use those. Stripe you already have — your `.env` shows `STRIPE_SECRET_KEY` configured.

---

## Step 2 — Provision MongoDB Atlas (7 min)

1. <https://cloud.mongodb.com/v2#/clusters> → **Build a Database** → **M0 Free**
2. Provider: AWS · Region: closest to where Render runs (default Oregon → AWS Oregon)
3. Cluster name: `maars-prod` → **Create Deployment**
4. **Security → Database Access** → **+ Add New Database User**
   - Username: `maars`
   - Password: click **Autogenerate Secure Password**, copy it (you'll need it)
   - Built-in role: **Read and write to any database**
   - **Add User**
5. **Security → Network Access** → **+ Add IP Address**
   - Click **ALLOW ACCESS FROM ANYWHERE** (sets `0.0.0.0/0`) — Render uses dynamic IPs so we have to. Your data is still password-protected.
   - **Confirm**
6. **Database → Connect → Drivers**
   - Driver: Python · Version: 3.12+
   - Copy the connection string. Looks like:
     ```
     mongodb+srv://maars:<password>@maars-prod.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```
   - **Replace `<password>`** with the password from step 4. Save this — you'll paste it into Render in step 5.

---

## Step 3 — Push this repo to GitHub (1 min)

You already have the remote configured: `origin → https://github.com/managementmaars-art/MAARS-infinity-alpha.git`. So just commit and push:

```bash
cd "c:/Users/Yaleena Yara/MAARS-Command"
git add render.yaml DEPLOY.md MEMORY.md
git commit -m "Add Render deploy blueprint + production guide"
git push origin main
```

If you have a pile of unrelated staged changes from earlier work (you do — lots of `.adal/skills/*` files and similar), and you don't want them in this commit, stage selectively as shown above. Otherwise `git add -A && git commit` and let the auto-commit hook handle it.

✅ **Verify:** open <https://github.com/managementmaars-art/MAARS-infinity-alpha> in your browser, confirm `render.yaml` is in the file list.

---

## Step 4 — Render connects + auto-detects the blueprint (3 min)

1. <https://dashboard.render.com> → **New +** (top right) → **Blueprint**
2. Connect your GitHub account if not already → select the `maars-command` repo
3. Render finds `render.yaml`, shows you **two services it will create:**
   - `maars-backend` (Python web service) — Starter plan ($7/mo, always-on) or Free (sleeps after 15min)
   - `maars-frontend` (Static site) — Free
4. Click **Apply**

Render starts building immediately. Expect ~5 minutes for the first build (downloading wheels for `motor`, `stripe`, `playwright` etc.).

While it builds, do step 5.

---

## Step 5 — Paste 8 env vars into Render (5 min)

In the Render dashboard, click **maars-backend** → **Environment** tab. The blueprint already created placeholder slots for the 8 secrets I marked `sync: false`. Click each one's pencil icon and paste the value:

| Env var | Where to get the value |
|---|---|
| `MONGO_URL` | The connection string from MongoDB Atlas step 2.6 (with `<password>` replaced) |
| `OPENAI_API_KEY` | Already in your local `.env` — copy from there |
| `ANTHROPIC_API_KEY` | Same |
| `GROQ_API_KEY` | Same |
| `DEEPSEEK_API_KEY` | Same |
| `GOOGLE_API_KEY` | Same |
| `STRIPE_SECRET_KEY` | **Use a `sk_live_...` key**, not your test `rk_test_...`. Get it from <https://dashboard.stripe.com/apikeys> after switching off Test Mode toggle |
| `STRIPE_WEBHOOK_SECRET` | Set in step 6 below — leave blank for now |

After pasting, Render auto-redeploys. Watch the **Logs** tab — you'll see `MAARS Global AI Team Backend started`.

✅ **Verify:** click the public URL Render assigned (looks like `https://maars-backend.onrender.com`) — open `/api/health` in your browser, expect `{"status": "ok", "ready": true}`.

---

## Step 6 — Stripe live mode + webhook (5 min)

1. <https://dashboard.stripe.com> → toggle **Test mode** OFF (top-right)
2. **Developers → Webhooks → + Add endpoint**
3. **Endpoint URL:** `https://maars-backend.onrender.com/api/billing/webhook` (use your actual Render URL)
4. **Events to send:** click **+ Select events** → search for and check:
   - `checkout.session.completed`
   - (Optional: `invoice.payment_succeeded`, `customer.subscription.deleted` for future renewal/cancel handling)
5. **Add endpoint** — Stripe shows you the **Signing secret** (`whsec_xxxxxxxxxxxxxxxxxx`). Copy it.
6. Back in Render: **maars-backend → Environment → STRIPE_WEBHOOK_SECRET** → paste the `whsec_…` value → save.
7. Render auto-redeploys (about 2 min).

---

## Step 7 — End-to-end production verification (2 min)

Open the live frontend: `https://maars-frontend.onrender.com` (your actual URL).

1. Click **Login** → register with `management.maars@marsgc.net` → you become the owner.
2. Visit `/setup` → it should be **locked** (admin-only post-launch — confirms first-run mode is over).
3. Visit `/admin/pricing-manager` → all 13 plans present with operator splits.
4. Visit `/admin/metrics` → revenue tile shows $0 (no purchases yet, expected).

**Optional smoke test from your terminal:**
```bash
# Replace with the API key your prod-seeded test user gets — or create one via /v1/api-keys
curl https://maars-backend.onrender.com/api/v1/models | jq '.data | length'
# → should print 620+
```

---

## What's now true

- 🌍 **Public URL** for your frontend and backend, with auto-SSL (Render handles certs)
- 💳 **Real Stripe** processing real payments, splitting them per the operator_share_pct you configured
- ☁️ **Hosted MongoDB** with backups + replica set
- 🔄 **Auto-deploy** — every `git push origin main` triggers a new deploy in ~3 min
- 📊 **Metrics + logs** at `https://dashboard.render.com` (request count, response time, memory, log stream)
- 🔐 **Env-var management** in Render dashboard (no secrets in git)

---

## What I'm leaving for you (intentional)

Things I'd add only after you have a customer:

| Item | When to do it |
|---|---|
| Custom domain (e.g. `app.maars.com`) | Buy a domain, add CNAME in your DNS provider pointing to `maars-frontend.onrender.com`, add it in Render → Settings → Custom Domain |
| Production MongoDB tier upgrade (M10+) | When you exceed 512 MB or 100 connections |
| Scheduled DB backups | Atlas M10+ does this automatically; M0 free has snapshots only |
| Sentry / error monitoring | After your first real user hits an error |
| Email transactional (SendGrid/Resend) | When you want to send invoices, password resets, welcome emails |
| Rate-limiting on Cloudflare | When you start getting bot traffic |

None of these are blockers for launch. Add them when reality demands.

---

## When you've finished steps 1-7

Tell me **"production live, URL is https://…"** and I'll:
- Update MEMORY.md with the deploy entry
- Run a verification probe against your live URL
- Wire up the seed flow on production (so you have a test user with credits on the live site)
- Help you do your first real Stripe purchase to prove the split flow on production
