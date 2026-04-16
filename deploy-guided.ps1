# MAARS Command -- guided deploy.
#
# This script DRIVES YOU through production deploy. It opens each website you
# need, prints exactly what to click, and waits for you to paste back the
# value it asks for. Then it does the technical work via API calls.
#
# Run from project root:
#   powershell -ExecutionPolicy Bypass -File deploy-guided.ps1
#
# IMPORTANT: file is pure ASCII (no em-dashes / smart quotes) so PowerShell's
# parser handles it regardless of console codepage.

#requires -Version 5.1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# ---------------------------------------------------------------- helpers

function Hr   { Write-Host ("-" * 72) -ForegroundColor DarkGray }
function H1   { param($t) Hr; Write-Host ("  " + $t) -ForegroundColor Cyan; Hr }
function H2   { param($t) Write-Host ""; Write-Host (">> " + $t) -ForegroundColor White -BackgroundColor DarkBlue }
function Ok   { param($t) Write-Host ("  [+] " + $t) -ForegroundColor Green }
function Note { param($t) Write-Host ("  ~   " + $t) -ForegroundColor DarkGray }
function Step { param($t) Write-Host ("    > " + $t) -ForegroundColor Yellow }

function Open {
  param($url)
  Start-Process $url
  Note "browser tab opened: $url"
}

function PauseHere {
  param($t = "Press Enter when ready")
  Read-Host "  >>> $t" | Out-Null
}

function GetSecret {
  param($prompt)
  Write-Host ""
  $sec = Read-Host "  PASTE: $prompt" -AsSecureString
  return [System.Net.NetworkCredential]::new("", $sec).Password
}

function GetText {
  param($prompt)
  Write-Host ""
  return Read-Host "  PASTE: $prompt"
}

# ---------------------------------------------------------------- intro

Clear-Host
H1 "MAARS Command -- Guided Production Deploy"
Write-Host ""
Write-Host "  This script will GUIDE you to launch MAARS on the public internet."
Write-Host ""
Write-Host "  How it works:"
Write-Host "    * The script opens each website you need in your browser"
Write-Host "    * It tells you EXACTLY what to click on that page"
Write-Host "    * You paste 4 values back into this terminal"
Write-Host "    * It does everything technical (git push, API calls, env vars, redeploy)"
Write-Host ""
Write-Host "  Total time: about 18 minutes"
Write-Host "  Cost: 0 dollars to start (free tiers everywhere)"
Write-Host ""
Write-Host "  4 values you will collect (the script tells you when and where):"
Write-Host "    1. MongoDB Atlas connection string"
Write-Host "    2. Render API key"
Write-Host "    3. Stripe live secret key (sk_live_...)"
Write-Host "    4. Stripe webhook signing secret (whsec_...)"
Write-Host ""
PauseHere "Press Enter to begin"

# ---------------------------------------------------------------- 1. Atlas

H1 "1 of 4 -- MongoDB Atlas (database for your app)"
H2 "Opening Atlas signup..."
Open "https://www.mongodb.com/cloud/atlas/register"

Write-Host ""
Write-Host "  ON THE PAGE THAT JUST OPENED:"
Write-Host ""
Step "Click 'Sign up with Google' (top of the page) -- sign in with whichever Google you want"
Step "If asked Goal/Role, just pick anything and click Finish"
Step "On the 'Deploy your database' page:"
Step "  - choose M0 (FREE) -- usually selected by default"
Step "  - Provider: AWS"
Step "  - Region: pick the closest to you"
Step "  - Name: leave default or call it 'maars-prod'"
Step "  - Click 'Create Deployment' (green button bottom-right)"
Step ""
Step "It will pop a 'Connect to your cluster' dialog:"
Step "  - Username: type 'maars'"
Step "  - Password: click 'Autogenerate Secure Password' -- COPY IT NOW (you will need it next)"
Step "  - Click 'Create Database User'"
Step "  - Click 'Choose a connection method'"
Step "  - Click 'Drivers'"
Step "  - Driver: Python  Version: 3.12 or later"
Step "  - Step 3 shows a connection string starting with 'mongodb+srv://maars:<password>@...'"
Step "  - Copy the WHOLE connection string"
Step "  - REPLACE the literal '<password>' with the password you copied above"
Step ""
Step "BEFORE leaving Atlas, click 'Network Access' (left sidebar)"
Step "  - Click 'ADD IP ADDRESS'"
Step "  - Click 'ALLOW ACCESS FROM ANYWHERE' (sets 0.0.0.0/0)"
Step "  - Click 'Confirm'"

$mongo_url = GetText "the full Mongo connection string (with password substituted in)"
if ($mongo_url -notmatch "^mongodb\+srv://") {
  Write-Host "  [!] Doesn't look like a Mongo connection string. Try again." -ForegroundColor Red
  exit 1
}
Ok "got Mongo URL"

# ---------------------------------------------------------------- 2. Render

H1 "2 of 4 -- Render (hosts your backend + frontend)"
H2 "Opening Render..."
Open "https://render.com"

Write-Host ""
Write-Host "  ON THE PAGE THAT JUST OPENED:"
Write-Host ""
Step "Click 'Get Started' (top-right)"
Step "Click 'GitHub' to sign up -- authorize Render to read your repos"
Step "On the welcome screen, you can skip any 'connect a service' prompt"

PauseHere "Press Enter when you are signed in to Render and seeing the dashboard"

H2 "Now opening the API Keys page..."
Open "https://dashboard.render.com/u/settings#api-keys"

Write-Host ""
Write-Host "  ON THIS PAGE:"
Write-Host ""
Step "Click 'Create API Key' (button near the API Keys section)"
Step "Name it: 'maars-deploy'"
Step "Click 'Create API Key' to confirm"
Step "COPY the rnd_... value that appears (you only see it once)"

$render_key = GetSecret "the Render API key (rnd_...)"
if ($render_key -notmatch "^rnd_") {
  Write-Host "  [!] Doesn't look like a Render key. Try again." -ForegroundColor Red
  exit 1
}
Ok "got Render API key"

H2 "Now applying the Blueprint (creates both services)..."
Open "https://dashboard.render.com/blueprints"

Write-Host ""
Write-Host "  ON THIS PAGE:"
Write-Host ""
Step "Click 'New Blueprint Instance' (or 'New +' then 'Blueprint' if no button)"
Step "Connect this repo: 'managementmaars-art/MAARS-infinity-alpha'"
Step "  (if you do not see it, click 'Configure account' to give Render access)"
Step "Render will read render.yaml and show TWO services:"
Step "  - maars-backend (Python web service)"
Step "  - maars-frontend (Static site)"
Step "Click 'Apply' (green button bottom-right)"
Step ""
Step "Render starts building. The build takes about 5 minutes."
Step "Leave that tab open and come back here -- this script handles the redeploy."

PauseHere "Press Enter when you have clicked Apply (no need to wait for build)"

# ---------------------------------------------------------------- 3. Stripe

H1 "3 of 4 -- Stripe (live mode billing)"
H2 "Opening your Stripe API keys page..."
Open "https://dashboard.stripe.com/apikeys"

Write-Host ""
Write-Host "  ON THIS PAGE:"
Write-Host ""
Step "Top-right of the page: there is a 'Test mode' toggle."
Step "Click it to switch to LIVE mode."
Step "  (you may need to complete business verification first if you have not)"
Step "When you are in Live mode, the page shows 'Standard keys'"
Step "Click 'Reveal live key' next to 'Secret key'"
Step "COPY the sk_live_... value"

$stripe_live = GetSecret "the Stripe live secret key (sk_live_...)"
if ($stripe_live -notmatch "^sk_live_") {
  Write-Host "  [!] Doesn't look like a live key. Try again." -ForegroundColor Red
  exit 1
}
Ok "got sk_live_..."

H2 "Now register the webhook endpoint..."
Note "We need YOUR Render backend URL for this. Default: https://maars-backend.onrender.com"
$render_backend_url = GetText "your Render backend URL (or press Enter to use the default)"
if (-not $render_backend_url) { $render_backend_url = "https://maars-backend.onrender.com" }
$webhook_url = "$render_backend_url/api/billing/webhook"
Note "webhook will point to: $webhook_url"

Open "https://dashboard.stripe.com/webhooks/create"

Write-Host ""
Write-Host "  ON THIS PAGE:"
Write-Host ""
Step "Field 'Endpoint URL': paste this exactly:"
Step ""
Write-Host "         $webhook_url" -ForegroundColor Cyan
Step ""
Step "Field 'Description' (optional): 'MAARS production'"
Step "Field 'Events to send': click '+ Select events'"
Step "  - Search 'checkout.session.completed' and check the box"
Step "  - Click 'Add events'"
Step "Click 'Add endpoint' (green button bottom-right)"
Step ""
Step "After it saves, the page shows the endpoint detail."
Step "Find 'Signing secret' (usually under 'Endpoint secret') and click 'Reveal'"
Step "COPY the whsec_... value"

$stripe_whsec = GetSecret "the Stripe webhook signing secret (whsec_...)"
if ($stripe_whsec -notmatch "^whsec_") {
  Write-Host "  [!] Doesn't look like a webhook secret. Try again." -ForegroundColor Red
  exit 1
}
Ok "got whsec_..."

# ---------------------------------------------------------------- 4. push to Render

H1 "4 of 4 -- Pushing config to Render (automatic, no clicks needed)"

# Read local .env for provider keys
$env_local = @{}
Get-Content ".env" | ForEach-Object {
  if ($_ -match "^\s*([A-Z][A-Z0-9_]*)\s*=\s*(.*?)\s*$") {
    $env_local[$Matches[1]] = $Matches[2].Trim('"').Trim("'")
  }
}

$headers = @{ "Authorization" = "Bearer $render_key"; "Accept" = "application/json" }

H2 "Looking up your maars-backend service..."
$max_tries = 18  # 18 * 10s = 3 min
$backend_id = $null
$backend_url_actual = $null
for ($i = 1; $i -le $max_tries; $i++) {
  try {
    $svcs = Invoke-RestMethod -Uri "https://api.render.com/v1/services" -Headers $headers -Method GET
    $b = $svcs | Where-Object { $_.service.name -eq "maars-backend" } | Select-Object -First 1
    if ($b) {
      $backend_id = $b.service.id
      $backend_url_actual = $b.service.serviceDetails.url
      break
    }
  } catch {
    Note "(retrying -- $($_.Exception.Message))"
  }
  Note "service not found yet (attempt $i/$max_tries) -- Render still creating it. Sleeping 10s..."
  Start-Sleep -Seconds 10
}
if (-not $backend_id) {
  Write-Host "  [!] Couldn't find maars-backend after 3 minutes. Did the Blueprint Apply succeed?" -ForegroundColor Red
  Write-Host "  [!] Check https://dashboard.render.com/blueprints -- fix any errors there, re-run this script." -ForegroundColor Red
  exit 1
}
Ok "found backend service: $backend_id"

H2 "Uploading env vars..."
$envs_to_push = @(
  @{ key = "MONGO_URL";              value = $mongo_url },
  @{ key = "STRIPE_SECRET_KEY";      value = $stripe_live },
  @{ key = "STRIPE_WEBHOOK_SECRET";  value = $stripe_whsec }
)
foreach ($k in @("OPENAI_API_KEY","ANTHROPIC_API_KEY","GROQ_API_KEY","DEEPSEEK_API_KEY","GOOGLE_API_KEY")) {
  if ($env_local[$k]) {
    $envs_to_push += @{ key = $k; value = $env_local[$k] }
    Note "+ $k"
  } else {
    Write-Host "  [!] $k is empty in your local .env -- skipping" -ForegroundColor Yellow
  }
}

$body = $envs_to_push | ConvertTo-Json -Depth 5
$null = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$backend_id/env-vars" `
  -Headers $headers -Method PUT -Body $body -ContentType "application/json"
Ok "uploaded $($envs_to_push.Count) env vars"

H2 "Triggering redeploy..."
$null = Invoke-RestMethod -Uri "https://api.render.com/v1/services/$backend_id/deploys" `
  -Headers $headers -Method POST -Body "{}" -ContentType "application/json"
Ok "redeploy triggered"

# ---------------------------------------------------------------- done

H1 "DONE -- Production deploy in progress"

if (-not $backend_url_actual) { $backend_url_actual = "https://maars-backend.onrender.com" }

Write-Host ""
Write-Host "  Render is now redeploying your backend with the secrets you provided."
Write-Host "  Expected time: 3-4 minutes."
Write-Host ""
Write-Host "  Backend URL:  $backend_url_actual"
Write-Host "  Frontend URL: probably https://maars-frontend.onrender.com"
Write-Host ""
Write-Host "  WHEN THE REDEPLOY FINISHES (you can watch progress in Render dashboard):"
Write-Host ""
Step "Open your frontend URL in a browser"
Step "Click Login -> Register with management.maars@marsgc.net (you become the owner)"
Step "Visit /admin/pricing-manager and /admin/metrics to confirm everything works"
Step ""
Step "If you want to test the live Stripe split flow:"
Step "  - Make a real test purchase via /pricing"
Step "  - Watch /admin/metrics -- operator revenue tile jumps by your operator share %"

Write-Host ""
Hr
Write-Host "  All credentials you pasted live ONLY in Render's encrypted env-var store." -ForegroundColor DarkGray
Write-Host "  This script does not write them to your local disk." -ForegroundColor DarkGray
Hr
