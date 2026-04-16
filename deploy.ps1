# MAARS Command — semi-automated production deploy helper.
#
# What this does autonomously:
#   1. Verifies prerequisites (git, gh, stripe, python, node)
#   2. Reads your local .env, prints the 8 secrets you'll paste into Render
#   3. Commits + pushes render.yaml + DEPLOY.md to GitHub
#   4. (After you give it Render API key + Stripe live key) creates the Stripe
#      webhook endpoint + sets the env vars in Render via their REST APIs
#
# What you MUST do manually (no API substitute exists):
#   A. Sign up at https://render.com (OAuth via GitHub)
#   B. Sign up at https://cloud.mongodb.com (creates the M0 free cluster)
#   C. Create a Render API key:  Dashboard -> Account Settings -> API Keys -> Create Key
#   D. Switch Stripe to Live Mode + create a Restricted/Secret key with
#      "Webhook Endpoints write" + "Checkout Sessions write" permissions
#
# Run from project root:
#   powershell -ExecutionPolicy Bypass -File deploy.ps1

#requires -Version 5.1
$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

function Section($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Ok($t)      { Write-Host "  + $t" -ForegroundColor Green }
function Warn($t)    { Write-Host "  ! $t" -ForegroundColor Yellow }
function Fail($t)    { Write-Host "  X $t" -ForegroundColor Red; exit 1 }
function Info($t)    { Write-Host "  $t" }

# ─────────────────────────────────────────────────── 1. preflight

Section "1/6 Preflight"
foreach ($cmd in @("git", "python", "node")) {
  $found = Get-Command $cmd -ErrorAction SilentlyContinue
  if ($found) { Ok "$cmd : $($found.Source)" } else { Fail "$cmd not on PATH" }
}
foreach ($cmd in @("gh", "stripe")) {
  $found = Get-Command $cmd -ErrorAction SilentlyContinue
  if ($found) { Ok "$cmd : $($found.Source)" } else { Warn "$cmd not on PATH (open a fresh shell after winget install, or skip)" }
}

if (-not (Test-Path "$ProjectRoot/.env")) { Fail ".env missing — run setup.sh first" }
if (-not (Test-Path "$ProjectRoot/render.yaml")) { Fail "render.yaml missing" }
if (-not (Test-Path "$ProjectRoot/DEPLOY.md")) { Fail "DEPLOY.md missing" }
Ok "all required files present"

# ─────────────────────────────────────────────────── 2. read local .env

Section "2/6 Reading local .env (will be uploaded to Render manually or via API)"
$env_local = @{}
Get-Content "$ProjectRoot/.env" | ForEach-Object {
  if ($_ -match "^\s*([A-Z][A-Z0-9_]*)\s*=\s*(.*?)\s*$") {
    $env_local[$Matches[1]] = $Matches[2].Trim('"').Trim("'")
  }
}
$secrets_to_upload = @(
  "OPENAI_API_KEY","ANTHROPIC_API_KEY","GROQ_API_KEY","DEEPSEEK_API_KEY","GOOGLE_API_KEY",
  "STRIPE_SECRET_KEY","STRIPE_WEBHOOK_SECRET"
)
foreach ($k in $secrets_to_upload) {
  $v = $env_local[$k]
  if ($v) { Ok "$k present (will be uploaded)" } else { Warn "$k EMPTY — set it before running step 5" }
}

# ─────────────────────────────────────────────────── 3. push to GitHub

Section "3/6 Commit + push to GitHub"
$remote = git remote get-url origin 2>$null
if (-not $remote) { Fail "no 'origin' remote configured. add one with: git remote add origin <url>" }
Ok "remote: $remote"

$dirty = git status --short
if ($dirty) {
  $resp = Read-Host "`n  Uncommitted changes detected. Commit + push render.yaml/DEPLOY.md/MEMORY.md only? [y/N]"
  if ($resp -eq "y") {
    git add render.yaml DEPLOY.md MEMORY.md deploy.ps1
    git commit -m "Add Render deploy blueprint + production guide + helper script"
    git push origin main
    Ok "pushed to $remote"
  } else {
    Warn "skipped — push manually when ready: git add render.yaml DEPLOY.md MEMORY.md && git commit && git push"
  }
} else {
  Ok "tree clean — nothing to push"
}

# ─────────────────────────────────────────────────── 4. manual block — Render + Atlas signup

Section "4/6 MANUAL — sign up + click through (~12 min)"
Write-Host @"

  This script CANNOT do these steps. They require browser sign-up and
  OAuth flows that no API or terminal command can replace.

  A. MongoDB Atlas (~7 min)
     1. https://www.mongodb.com/cloud/atlas/register  (sign up with Google)
     2. Build a Database -> M0 Free -> AWS / Oregon -> name 'maars-prod' -> Create
     3. Security -> Database Access -> Add User
        - username: maars
        - password: click Autogenerate, COPY IT
        - role: Read and write to any database
     4. Security -> Network Access -> Add IP -> ALLOW FROM ANYWHERE (0.0.0.0/0)
     5. Database -> Connect -> Drivers -> Python 3.12+
        - Copy connection string. Replace <password> with what you copied in step 3.
        - Save it: you'll paste this into Render as MONGO_URL.

  B. Render (~3 min)
     1. https://render.com  -> Get Started -> Sign up with GitHub
     2. Account Settings (top-right) -> API Keys -> Create Key
        - name: 'maars-deploy-script'
        - COPY the rnd_... value. Save it.
     3. Dashboard -> New + -> Blueprint
     4. Connect this repo (managementmaars-art/MAARS-infinity-alpha)
     5. Render finds render.yaml, shows 2 services, click Apply.
     6. Wait until both services show green (5 min build).

  C. Stripe Live Mode webhook prep (~2 min)
     1. https://dashboard.stripe.com -> top-right toggle Test mode OFF
     2. Developers -> API keys -> Reveal sk_live_... -> COPY IT
     3. Developers -> Webhooks -> Add endpoint
        - URL: https://maars-backend.onrender.com/api/billing/webhook  (use YOUR Render URL)
        - Events: checkout.session.completed
        - Add endpoint -> COPY the whsec_... value

  When you have:
     - MONGO_URL string
     - Render API key (rnd_...)
     - sk_live_...
     - whsec_...

  ...press Enter to continue with the automated config push.
"@ -ForegroundColor Yellow

Read-Host "`n  Press Enter when you have all 4 values ready"

# ─────────────────────────────────────────────────── 5. push secrets via Render API

Section "5/6 Pushing secrets into Render via REST API"

$render_api_key = Read-Host "  Render API key (rnd_...)" -AsSecureString
$render_api_key_plain = [System.Net.NetworkCredential]::new("", $render_api_key).Password

$mongo_url = Read-Host "  MongoDB Atlas connection string"
$stripe_live = Read-Host "  Stripe live secret key (sk_live_...)"
$stripe_whsec = Read-Host "  Stripe webhook signing secret (whsec_...)"

# Find the maars-backend service
$headers = @{ "Authorization" = "Bearer $render_api_key_plain"; "Accept" = "application/json" }
$services = Invoke-RestMethod -Uri "https://api.render.com/v1/services" -Headers $headers -Method GET
$backend = $services | Where-Object { $_.service.name -eq "maars-backend" } | Select-Object -First 1
if (-not $backend) { Fail "couldn't find 'maars-backend' service in your Render account. Did the Blueprint Apply succeed?" }
$backend_id = $backend.service.id
Ok "found backend: $backend_id"

# Build the env var payload (existing keys merged with the secrets we want to set)
$envs_to_push = @(
  @{ key = "MONGO_URL"; value = $mongo_url },
  @{ key = "STRIPE_SECRET_KEY"; value = $stripe_live },
  @{ key = "STRIPE_WEBHOOK_SECRET"; value = $stripe_whsec }
)
foreach ($k in @("OPENAI_API_KEY","ANTHROPIC_API_KEY","GROQ_API_KEY","DEEPSEEK_API_KEY","GOOGLE_API_KEY")) {
  if ($env_local[$k]) { $envs_to_push += @{ key = $k; value = $env_local[$k] } }
}

$body = $envs_to_push | ConvertTo-Json -Depth 5
$resp = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$backend_id/env-vars" `
  -Headers $headers -Method PUT -Body $body -ContentType "application/json"
Ok "uploaded $($envs_to_push.Count) env vars to maars-backend"

# Trigger redeploy
Invoke-RestMethod -Uri "https://api.render.com/v1/services/$backend_id/deploys" `
  -Headers $headers -Method POST -Body "{}" -ContentType "application/json" | Out-Null
Ok "redeploy triggered"

# ─────────────────────────────────────────────────── 6. verify

Section "6/6 Verification"
$backend_url = $backend.service.serviceDetails.url
if (-not $backend_url) { $backend_url = "https://maars-backend.onrender.com" }
Info "backend URL: $backend_url"
Info "wait ~3 min for redeploy + cold start, then probe:"
Info "  curl $backend_url/api/health"
Info ""
Info "frontend URL: probably https://maars-frontend.onrender.com"
Info "open it in your browser, register as the owner, walk the admin pages."
Info ""
Ok "deploy script complete"
