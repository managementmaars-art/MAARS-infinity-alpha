# MAARS Deployment Setup

Everything you need to flip on — ordered by priority. Each section shows what to do, what to paste where, and what MAARS does automatically.

---

## 1 · Sentry (production error monitoring) — 5 min · free

**Why:** MAARS logs "Sentry disabled (no SENTRY_DSN). Production error monitoring is OFF." right now. Every prod crash is invisible without this.

**Steps:**
1. Sign up at https://sentry.io → create a new Project → type: Python / FastAPI
2. Copy the DSN (looks like `https://abc123@o456.ingest.us.sentry.io/789`)
3. Paste into Render dashboard → `maars-backend` service → Environment → `SENTRY_DSN`

**What MAARS does automatically:** [services/error_monitoring.py](backend/services/error_monitoring.py) calls `init_sentry()` on startup. Every unhandled exception + explicit `capture_exception()` hits the dashboard. Zero code changes on your side.

---

## 2 · Domain + DNS (SPF / DKIM / DMARC) — 20-40 min

**Why:** Without proper DNS records, email goes to spam. Without a domain, you're on `*.onrender.com`.

**Steps:**
1. Buy a domain (Cloudflare Registrar / Namecheap — ~$10-15/yr)
2. In Render dashboard → `maars-frontend` → Custom Domain → add your domain
3. Render gives you CNAME/A records → paste into your DNS provider
4. **Email records** (if you send email via SendGrid/Resend/Postmark):
   - **SPF:** `v=spf1 include:sendgrid.net include:_spf.resend.com ~all` (combine the ones you use)
   - **DKIM:** the provider gives you a `CNAME` like `s1._domainkey.yourdomain.com` → follow their dashboard
   - **DMARC:** add TXT `_dmarc` record: `v=DMARC1; p=none; rua=mailto:you@yourdomain.com`
5. Wait ≤24h for DNS to propagate. Verify with https://mxtoolbox.com/SuperTool.aspx

**Stays in MAARS:** Nothing — this is pure infra.

---

## 3 · Stripe end-to-end test — 15 min

**Why:** Need to verify a user can sign up → pick a plan → pay → get credits → use the gateway.

**Steps:**
1. Stripe dashboard → Developers → API keys → copy **publishable + secret** (both test and live)
2. Dashboard → Developers → Webhooks → Add endpoint: `https://<your-render-backend>.onrender.com/api/billing/stripe-webhook` (event types: `checkout.session.completed`, `invoice.paid`, `customer.subscription.updated`)
3. Copy the webhook signing secret (`whsec_...`)
4. Set in Render dashboard: `STRIPE_SECRET_KEY=sk_test_...`, `STRIPE_WEBHOOK_SECRET=whsec_...`
5. **Test run:** use test card `4242 4242 4242 4242` (any future expiry + any CVC) → buy cheapest plan → verify credits land in your user's wallet

**What MAARS does automatically:** Webhook receiver already in [routes/billing.py](backend/routes/billing.py). Wallet credit top-up fires on `checkout.session.completed`.

---

## 4 · Render deployment trigger — 10 min

**Why:** Backend + frontend need to live somewhere publicly reachable before any of the above works end-to-end.

**Steps:**
1. Push the repo to GitHub if not already
2. Render dashboard → New + → Blueprint → connect the repo → select [render.yaml](render.yaml)
3. Render prompts you for every `sync: false` env var (they're all listed) → paste your values from your local `.env`
4. Click Apply → both services build + deploy

**What MAARS does automatically:** [render.yaml](render.yaml) is pre-configured with 70+ env vars, healthcheck path `/api/health`, auto-deploy on push, Mongo Atlas connection slot, cross-service URL wiring (frontend knows backend URL automatically).

---

## 5 · Cartesia (voice) — 5 min · free tier

**Why:** Sub-200ms duplex voice agents. The current Twilio path is half-duplex dial-only.

**Steps:**
1. Sign up at https://play.cartesia.ai → API keys → create one
2. Render env: `CARTESIA_API_KEY=sk_car_...`

**What MAARS does automatically:** [services/voice_stream.py](backend/services/voice_stream.py) uses it for TTS. Pairs with LiveKit (#6).

---

## 6 · LiveKit Cloud — 10 min · free for dev

**Why:** Real-time WebRTC transport for voice sessions between client and the agent pipeline.

**Steps:**
1. Sign up at https://cloud.livekit.io → create a project
2. Settings → API keys → copy `API Key`, `API Secret`, `URL (wss://...)`
3. Render env:
   - `LIVEKIT_URL=wss://your-project.livekit.cloud`
   - `LIVEKIT_API_KEY=API...`
   - `LIVEKIT_API_SECRET=secret...`
4. `pip install livekit-api livekit-agents cartesia assemblyai` (add to `backend/requirements.txt` when you're ready to run the voice worker)

**What MAARS does automatically:** [services/voice_stream.py](backend/services/voice_stream.py) issues room tokens + scaffolds the agent handler. Real-time loop runs as a separate `livekit-agents` worker process; deploy it as a second Render service or a cheap VPS.

---

## 7 · AssemblyAI Universal (meeting notes) — 5 min · free trial

**Why:** 99-language auto-detect + diarization + streaming STT. Used for meeting-notes pipeline AND live voice agent transcription.

**Steps:**
1. Sign up at https://www.assemblyai.com → API keys → copy
2. Render env: `ASSEMBLYAI_API_KEY=...`

**What MAARS does automatically:** [services/transcription_pipeline.py](backend/services/transcription_pipeline.py) does upload → transcribe → summarize via `llm_gateway` → persist to `db.meeting_notes`. Endpoint forthcoming (wire when you want a standalone "meeting notes" client feature).

---

## 8 · ColiVara (visual document RAG) — 5 min · free tier

**Why:** For scanned PDFs, slides, charts, tables — the chunk-text RAG approach loses layout. ColPali retrieves pages as images.

**Steps:**
1. Sign up at https://colivara.com → API keys → copy
2. Render env: `COLIVARA_API_KEY=...`

**What MAARS does automatically:** [services/vision_rag.py](backend/services/vision_rag.py) handles ingest + retrieval + vision-LLM answer. Use alongside text RAG when clients have visual-heavy docs.

---

## 9 · Parlant sidecar (regulated flows) — 20 min

**Why:** KYC / insurance / medical intake can't pass audit with monolithic prompts. Parlant = deterministic state machines.

**Steps:**
1. On a second Render service OR a cheap DigitalOcean droplet: `pip install parlant`
2. Run: `parlant-server --port 8800 --host 0.0.0.0`
3. Register your journeys via Parlant's CLI or API (their docs: https://github.com/emcie-co/parlant)
4. MAARS env:
   - `PARLANT_URL=http://<sidecar-host>:8800`
   - `PARLANT_API_KEY=...` (if you set one)

**What MAARS does automatically:** [services/parlant_bridge.py](backend/services/parlant_bridge.py) auto-registers a new `state_machine` workflow tool. Any workflow can now have a node that routes a turn through a specific Parlant journey.

---

## 10 · GPU runtime for fine-tuning — deferred to 50+ clients

**Why:** Client-custom models via Unsloth LoRA. The [services/finetune_pipeline.py](backend/services/finetune_pipeline.py) exports the dataset; training runs on external GPU.

**Options (cheapest to most robust):**

- **Google Colab** — free T4, 12 hours max. Good for a one-off LoRA run on a toy dataset.
- **Modal.com** — pay-per-second, spins up an A10G for ~$1/hr, Python SDK is one-liner.
- **RunPod** — reserved H100 $2/hr, on-demand A40 $0.4/hr. CLI-driven.
- **Beam.cloud** — similar to Modal, Python-native.

**Steps (Modal example):**
```python
import modal
stub = modal.Stub("maars-finetune")
@stub.function(gpu="A10G", image=modal.Image.debian_slim().pip_install("unsloth", "trl"))
def train(jsonl_url: str, base_model: str = "unsloth/Qwen2.5-3B-Instruct"):
    # Unsloth LoRA recipe; push result to Hugging Face on completion
    ...
```

1. Call `POST /api/finetune/export` from the MAARS admin to produce a JSONL
2. Upload the JSONL to S3 / HF Datasets
3. Kick the Modal/RunPod job with that URL as input
4. On completion, register the resulting model in MAARS's smart_router so it becomes a routing candidate

**What MAARS does automatically:** Nothing yet — the scaffold exports; the training is your external job. Deferred per your "revisit at 50+ clients" memo.

---

## Summary checklist

| # | Service | Status | Env vars | Priority |
|---|---|---|---|---|
| 1 | Sentry | Wired, needs DSN | `SENTRY_DSN` | **High** — prod errors silent without it |
| 2 | Domain + DNS | Manual setup | — | **High** — affects email + brand |
| 3 | Stripe E2E | Needs webhook URL | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | **High** — revenue path |
| 4 | Render deploy | render.yaml ready | 70+ vars (all `sync: false`) | **High** — unlocks everything |
| 5 | Cartesia | Scaffolded | `CARTESIA_API_KEY` | Medium — voice unlock |
| 6 | LiveKit | Scaffolded + token issuer | `LIVEKIT_URL` + `_KEY` + `_SECRET` | Medium — voice unlock |
| 7 | AssemblyAI | Wired (meeting notes) | `ASSEMBLYAI_API_KEY` | Medium — meeting notes + voice STT |
| 8 | ColiVara | Wired | `COLIVARA_API_KEY` | Low-Medium — visual RAG |
| 9 | Parlant | Bridge ready | `PARLANT_URL` + `_API_KEY` | Low — only if regulated client |
| 10 | GPU runtime | Export scaffold ready | — | Defer to 50+ clients |

**Fastest path to launched:** do 1, 2, 3, 4 in that order (half a day). The other 6 are feature unlocks you turn on when a client pulls for them.
