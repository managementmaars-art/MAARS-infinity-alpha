# MAARS Deployment — Cost Lever Env Vars

All 5 cost-optimization levers are flipped **ON** in the admin UI (operator intent). At deploy time, set the env vars below so each lever becomes *verified* (claim + env detected) instead of *claimed only*. Until then the admin UI shows a "NEEDS ENV" warning next to the lever.

Target all-in expected cost per plan with every lever on:

| Plan | Credits | Expected cost | Margin % |
|---|---:|---:|---:|
| Free | 50 | $1.60 | — |
| Starter | 300 | $1.68 | 96.64% |
| Essential | 600 | $1.83 | 98.17% |
| Basic | 1,200 | $2.06 | 98.97% |
| Standard | 2,000 | $2.50 | 99.29% |
| Professional | 3,000 | $3.09 | 99.38% |
| Advanced | 4,000 | $3.82 | 99.49% |
| Business | 5,000 | $4.55 | 99.54% |
| Agency | 6,500 | $5.30 | 99.65% |
| Studio | 7,500 | $6.03 | 99.76% |
| Enterprise | 8,500 | $7.46 | 99.79% |
| Corporate | 9,500 | $8.89 | 99.82% |
| Elite | 10,000 | $10.30 | 99.87% |
| White Label | 20,000 | $16.21 | 99.92% |

(Numbers include LLM + media + email + voice + proxy/GPU/infra amortization.)

---

## Lever 1 — `local_media` (SDXL / Whisper / XTTS / SVD self-host)

Cuts marginal image/video/TTS cost to **$0** (replaces Replicate/OpenAI media billing with self-hosted GPU).

```bash
MAARS_LOCAL_IMAGE_URL=http://<gpu-host>:<port>        # e.g. http://localhost:7860
MAARS_COST_GPU_MONTHLY_USD=800                         # $ hardware amortized + electricity per month
MAARS_AMORT_GPU_CLIENTS=15                             # active media clients sharing the GPU box
```

**How to set up the GPU box:** rent a runpod.io A100 ($1.89/hr on-demand or ~$500/mo reserved), or buy a single RTX 4090 workstation (~$3,500 one-time + $50/mo electricity → ~$200/mo amortized over 24 months). Run Automatic1111 (SDXL), whisper.cpp, XTTS-v2, Stable Video Diffusion behind a single FastAPI router on `<gpu-host>:<port>`.

---

## Lever 2 — `self_smtp` (Postfix self-host)

Cuts email marginal cost from $0.0001 → **$0**.

```bash
MAARS_SMTP_HOST=<your-smtp-host>                       # e.g. 127.0.0.1
MAARS_SMTP_PORT=587
MAARS_SMTP_USER=<user>
MAARS_SMTP_PASS=<pass>
MAARS_SMTP_FROM=noreply@<your-domain>
MAARS_COST_EMAIL_SELF_USD=0.0                          # default already 0
```

**Setup:** install Postfix on the same VPS. Configure SPF (`v=spf1 ip4:<vps-ip> -all`), DKIM (`opendkim`), DMARC (`v=DMARC1; p=none`) on your sending domain's DNS. Without these three, inbox placement collapses. Budget 30-60 min.

---

## Lever 3 — `telnyx_voice` (Telnyx instead of Twilio)

Voice: **$0.013/min → $0.007/min** (≈45% off).

```bash
TELNYX_API_KEY=<telnyx-v2-key>
TELNYX_CONNECTION_ID=<sip-connection-id>
TELNYX_FROM_NUMBER=+1<your-number>
MAARS_COST_VOICE_PER_MIN_USD=0.007                     # router uses this automatically when lever is on
```

**Setup:** telnyx.com → sign up (no credit card for $2 credit, card for real volume) → Numbers → buy a US/UK DID ($1/mo) → API Keys → V2 key → copy connection ID from the SIP connection you create.

---

## Lever 4 — `native_lead_research` (BrowserAgent scraping, no Apollo)

Already **active + configured** by default — uses the built-in browser automation. No env var required.

```bash
# Optional: if you want NumVerify phone validation
NUMVERIFY_API_KEY=<apilayer-key>                       # 100 req/mo free tier
```

---

## Lever 5 — `proxy_pool` (residential proxy rotation)

Required to scale lead scraping past ~50 active clients without IP bans. Amortized across scraping clients.

```bash
MAARS_PROXY_POOL=<proxy-provider-url-list>             # comma-separated or JSON, consumed by BrowserAgent
MAARS_COST_PROXY_POOL_USD=50                           # monthly proxy subscription
MAARS_AMORT_PROXY_CLIENTS=20                           # active scraping clients sharing the pool
```

**Setup:** Bright Data / Oxylabs / Smartproxy — starter residential plan ~$50/mo for 5-10 GB. Paste the rotating endpoint list (or the single `user:pass@host:port` credential) into `MAARS_PROXY_POOL`.

---

## Infra (always applies, no lever)

```bash
MAARS_COST_INFRA_MONTHLY_USD=80                        # VPS + Mongo + bandwidth per month
MAARS_AMORT_INFRA_CLIENTS=50                           # total clients sharing the infra
```

Tune these two numbers to your actual Render/Mongo/Stripe invoices after month 1.

---

## Verification after deploy

Hit `GET /api/admin/cost-config` — every lever should report `active: true` AND `env_detected: true`. If `env_detected` is false on any lever, that env var didn't land; the operator-intent claim still shows in the UI but the deployed stack isn't actually saving money.

Ledger reflecting the real post-deploy state: `GET /api/admin/pricing/full-ledger`.
