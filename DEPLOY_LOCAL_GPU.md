# Local Media GPU — Deploy Guide

The single biggest unflipped cost lever in your stack. Currently every image / video / voice call is paid (Flux HD ~$0.005/img, Fal LTX ~$0.005/sec, ElevenLabs ~$0.018/min). With a self-hosted GPU box, those costs drop to **electricity + amortized hardware**, ~$0 marginal per call.

**Expected impact (from your own Cost Optimization Levers panel):** **~$18/mo per heavy media client**. At 100 heavy clients that's **$21,600/year** of variable cost converted to a fixed amortizable expense.

This guide assumes you're going from **all-cloud media** today → **GPU-first with cloud fallback**. Cloud stays as the safety net when the GPU box is full or down.

---

## What you're deploying

A single Linux box (your own server, a rented dedicated, or a cloud VM with GPU passthrough) running:

| Service | Model | Replaces | Endpoint |
|---|---|---|---|
| **ComfyUI / SD-WebUI** | SDXL or Flux-dev local weights | Pollinations free / Flux HD paid | `POST /sdapi/v1/txt2img` or `POST /api/prompt` |
| **Whisper** | `whisper-large-v3` (CTranslate2 / faster-whisper) | Groq Whisper free / OpenAI Whisper paid | `POST /v1/audio/transcriptions` |
| **XTTS-v2** or **Coqui** | XTTS-v2 multilingual | Edge TTS free / ElevenLabs paid | `POST /v1/tts` |
| **SVD / AnimateDiff** *(optional)* | Stable Video Diffusion local | Fal LTX paid | `POST /sdapi/v1/svd` |

You point MAARS at this box via env vars; the smart router prefers it for media calls and falls through to cloud only when the box returns 5xx or saturates.

---

## Minimum hardware

| Tier | GPU | VRAM | RAM | Disk | Use case |
|---|---|---|---|---|---|
| **Starter** | 1× RTX 4090 (24 GB) | 24 GB | 64 GB | 1 TB NVMe | SDXL + Whisper + XTTS for ~50 concurrent clients |
| **Production** | 2× RTX 4090 OR 1× A6000 (48 GB) | 48 GB | 128 GB | 2 TB NVMe | + SVD video, ~200 concurrent |
| **Heavy** | 1× H100 (80 GB) OR 2× A6000 | 80–96 GB | 256 GB | 4 TB NVMe | Video + image + voice at scale |

**Where to buy the box:**
- **Self-host (best $/perf at scale)**: a 4090 desktop ~$2,800 + spare power supply. ROI ≈ 13 weeks at 100 heavy clients.
- **Rent dedicated**: Hetzner GEX44 (RTX 4000 SFF Ada, 20 GB) at €184/mo. Decent starter, weak for SDXL-XL.
- **Cloud GPU on demand**: Vast.ai or RunPod 4090 spot ~$0.30/hr (~$216/mo if running 24/7). Easy first, expensive at scale.

---

## Stack — fastest path to working

The path of least resistance: **ComfyUI** (image + video) + **faster-whisper-server** (STT) + **Coqui XTTS** (voice). All three are well-maintained, OpenAI-API-compatible (or close), and have docker-compose recipes.

### Step 1 — install NVIDIA driver + Docker + nvidia-container-toolkit

```bash
# Ubuntu 22.04 LTS / 24.04 LTS
sudo apt update && sudo apt install -y nvidia-driver-550 docker.io docker-compose-plugin
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
nvidia-smi  # verify GPU visible
```

### Step 2 — `docker-compose.yml` for the three services

Put this at `/opt/maars-gpu/docker-compose.yml`:

```yaml
services:
  comfyui:
    image: yanwk/comfyui-boot:cu121
    runtime: nvidia
    ports: ["8188:8188"]
    volumes:
      - ./comfyui/models:/root/ComfyUI/models
      - ./comfyui/output:/root/ComfyUI/output
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    restart: unless-stopped

  whisper:
    image: fedirz/faster-whisper-server:latest-cuda
    runtime: nvidia
    ports: ["8000:8000"]
    environment:
      - WHISPER__MODEL=large-v3
      - WHISPER__COMPUTE_TYPE=float16
      - NVIDIA_VISIBLE_DEVICES=all
    restart: unless-stopped

  xtts:
    image: ghcr.io/coqui-ai/xtts-streaming-server:latest-cuda121
    runtime: nvidia
    ports: ["8020:80"]
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    restart: unless-stopped
```

Bring it up:

```bash
cd /opt/maars-gpu
docker compose up -d
docker compose logs -f   # verify all three healthy
```

### Step 3 — download model weights (one-time)

ComfyUI ships empty; you need at least an SDXL checkpoint:

```bash
cd /opt/maars-gpu/comfyui/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
# Optional: Flux-dev quantized (~12GB)
# wget https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors
```

Whisper-large-v3 + XTTS-v2 weights download automatically on first request.

### Step 4 — expose to the internet (HTTPS)

You **do not** want raw 8188 / 8000 / 8020 on the public internet. Front them with **Caddy** for instant TLS:

```text
# /etc/caddy/Caddyfile
gpu.your-domain.com {
    reverse_proxy /image/* localhost:8188
    reverse_proxy /stt/*   localhost:8000
    reverse_proxy /tts/*   localhost:8020
    basicauth {
        maars  $2a$14$YOUR_BCRYPT_HASH_HERE
    }
}
```

Generate the bcrypt password with `caddy hash-password` then put the hash above.

### Step 5 — wire MAARS to the GPU box

Add these to your **MAARS backend** environment (`backend/.env` or your hosting platform's secret store):

```bash
# Local media routing — flips the four cells in the Cost Optimization
# Levers panel from "OFF · NEEDS ENV" to "ACTIVE".
MAARS_LOCAL_IMAGE_URL=https://gpu.your-domain.com/image
MAARS_LOCAL_STT_URL=https://gpu.your-domain.com/stt
MAARS_LOCAL_TTS_URL=https://gpu.your-domain.com/tts
MAARS_LOCAL_GPU_AUTH=Basic <base64-of-maars:password>

# Optional: if you only deployed images and not voice, set just the
# ones you have. Smart router uses cloud fallback for the rest.
```

Then restart your backend (`docker compose restart backend` or platform reload). The router picks up the env vars on next request.

### Step 6 — flip the lever in admin

Go to **/admin/pricing-manager → Cost Optimization Levers** and toggle **Local media GPU = ON**. The card will now show **ACTIVE** (env detected) instead of **NEEDS ENV**. Treasury starts charging $0 for media tracks immediately.

---

## Verification

Run a smoke test from your dev box:

```bash
# Image (Comfy)
curl -X POST https://gpu.your-domain.com/image/api/prompt \
    -u maars:password \
    -H "Content-Type: application/json" \
    -d '{"prompt": {"6": {"inputs": {"text": "a cat"}, "class_type": "CLIPTextEncode"}}}'

# STT (faster-whisper, OpenAI-compatible)
curl -X POST https://gpu.your-domain.com/stt/v1/audio/transcriptions \
    -u maars:password \
    -F file=@sample.mp3 -F model=whisper-large-v3

# TTS (Coqui)
curl -X POST https://gpu.your-domain.com/tts/tts \
    -u maars:password \
    -H "Content-Type: application/json" \
    -d '{"text": "hello world", "language": "en"}'
```

All three should return 200 within a few seconds. Once they do, fire a real client request through MAARS and check the Universal AI Gateway → Per-Track Routing panel. **Image / Voiceover / TTS / STT** should show provider = `local_gpu` instead of `fal_flux` / `elevenlabs` / `edge_tts` / `groq_whisper`.

---

## Operating cost (real numbers)

| Item | Monthly | Notes |
|---|---:|---|
| Electricity (1× 4090 @ 350W avg, 24/7) | ~$25 | Depends on local rate; 250–450W typical |
| Internet / bandwidth | $0–50 | Most commodity broadband fine; only matters at heavy concurrent video |
| Hardware amortization (Starter @ $2,800 over 24 mo) | $116 | Pay it once; depreciates linearly |
| **Total** | **~$140–190/mo** | Fixed regardless of client count |

Compare to cloud spend for the same workload: **~$18 × 100 heavy clients = $1,800/mo**. Break-even at ~10 heavy clients, then every client beyond that is pure margin.

---

## Failure modes + mitigations

| Risk | Mitigation |
|---|---|
| GPU box goes down | Smart router falls through to cloud automatically (existing behavior). Set up Uptime Robot to alert. |
| GPU saturates under load | Run 2× boxes behind a load balancer (HAProxy, simple round-robin). Or buy a second 4090. |
| Model weights drift / out of date | Schedule a `git pull` + container rebuild quarterly. Pin model versions in the compose file. |
| Power outage takes the box | Either UPS, or accept the 5-minute fallback to cloud during the outage. |
| Compromised GPU box | Caddy basic-auth + only your MAARS backend IP in firewall. Never expose to public internet. |
| Bad image generation quality | Quality Gate (already live in your backend) detects low-quality output via reverse-prompt similarity scoring + escalates to cloud Flux HD. Client never sees the bad output. |

---

## Next levers (after GPU lands)

Once Local GPU is ACTIVE, the next two cost levers in your panel:

1. **Telnyx (vs Twilio)** — `~$5/mo per heavy client`. Just sign up at telnyx.com, get an API key, set `TELNYX_API_KEY` in your env. Voice calls auto-route through Telnyx; ~45% cheaper per minute.

2. **Self-hosted SMTP** — `~$0.40/mo per heavy client`. Postfix on a $5 DigitalOcean droplet with warmed IPs. Set `MAARS_SMTP_HOST`, `MAARS_SMTP_USER`, `MAARS_SMTP_PASS` in env. Auto-replaces SendGrid for outbound campaign mail.

Both have the same flip-and-forget pattern as the GPU lever. The Cost Optimization Levers panel will turn green for each as the env vars are detected.

---

## TL;DR — fastest path

1. Buy a $2,800 4090 desktop, install Ubuntu + Docker + nvidia-container-toolkit
2. Drop the docker-compose.yml above into `/opt/maars-gpu`, `docker compose up -d`
3. Caddy in front for TLS + basic auth
4. Set `MAARS_LOCAL_IMAGE_URL` / `MAARS_LOCAL_STT_URL` / `MAARS_LOCAL_TTS_URL` in MAARS backend env
5. Toggle the lever ON in admin
6. Watch your cost-per-credit drop ~70% within a week of measured traffic
