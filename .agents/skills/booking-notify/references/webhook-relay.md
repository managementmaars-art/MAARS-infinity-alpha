# Webhook Relay Deployment

The webhook relay is a lightweight Cloud Run service that bridges Cal.com webhooks to Pushover emergency alerts. It provides real-time booking notifications without polling.

## Architecture

```
Cal.com → Webhook POST → Cloud Run (webhook-relay) → Pushover API → Phone alert
```

## Source Location

```
plugins/calcom-commander/scripts/webhook-relay/
├── main.py       ← Python HTTP server (stdlib only, no dependencies)
└── Dockerfile    ← Python 3.13 slim container
```

## Deploy to Cloud Run

### Step 1: Set Environment

```bash
echo "CALCOM_GCP_PROJECT: ${CALCOM_GCP_PROJECT:-NOT_SET}"
echo "CALCOM_GCP_REGION: ${CALCOM_GCP_REGION:-NOT_SET}"
echo "PUSHOVER_APP_TOKEN: ${PUSHOVER_APP_TOKEN:+SET}"
echo "PUSHOVER_USER_KEY: ${PUSHOVER_USER_KEY:+SET}"
```

### Step 2: Deploy

```bash
RELAY_SOURCE="$HOME/.claude/plugins/marketplaces/cc-skills/plugins/calcom-commander/scripts/webhook-relay"

gcloud run deploy calcom-pushover-webhook \
  --source "$RELAY_SOURCE" \
  --project="$CALCOM_GCP_PROJECT" \
  --account="$CALCOM_GCP_ACCOUNT" \
  --region="$CALCOM_GCP_REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="PUSHOVER_TOKEN=$PUSHOVER_APP_TOKEN,PUSHOVER_USER=$PUSHOVER_USER_KEY,PUSHOVER_SOUND=${PUSHOVER_SOUND:-dune}" \
  --memory=128Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1 \
  --timeout=30 \
  --quiet
```

Note the **Service URL** from the output.

### Step 3: Verify Health

```bash
curl -s "$WEBHOOK_RELAY_URL" | python3 -m json.tool
# Expected: {"status": "healthy", "service": "calcom-pushover-webhook"}
```

### Step 4: Test with Simulated Booking

```bash
curl -s -X POST "$WEBHOOK_RELAY_URL" \
  -H "Content-Type: application/json" \
  -d '{"triggerEvent":"BOOKING_CREATED","payload":{"title":"Test Meeting","attendees":[{"name":"Test User"}],"startTime":"2026-01-01T10:00:00Z","endTime":"2026-01-01T10:30:00Z"}}'
```

Expected: Pushover emergency alert with "dune" sound.

## Register Cal.com Webhook

After deploying the relay, register it with Cal.com:

```bash
# Using Cal.com API v1
CALCOM_API_KEY=$(op item get "$CALCOM_OP_UUID" --vault "Claude Automation" --fields password --reveal)

curl -s -X POST "https://api.cal.com/v1/webhooks?apiKey=$CALCOM_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"subscriberUrl\":\"$WEBHOOK_RELAY_URL\",\"eventTriggers\":[\"BOOKING_CREATED\",\"BOOKING_RESCHEDULED\",\"BOOKING_CANCELLED\"],\"active\":true}"
```

## List/Manage Webhooks

```bash
# List all webhooks
curl -s "https://api.cal.com/v1/webhooks?apiKey=$CALCOM_API_KEY" | python3 -m json.tool

# Delete a webhook
curl -s -X DELETE "https://api.cal.com/v1/webhooks/<webhook-id>?apiKey=$CALCOM_API_KEY"
```

## Update Relay

To redeploy after code changes:

```bash
gcloud run deploy calcom-pushover-webhook \
  --source "$RELAY_SOURCE" \
  --project="$CALCOM_GCP_PROJECT" \
  --region="$CALCOM_GCP_REGION" \
  --quiet
```

## Event Trigger Behavior

| Cal.com Event         | Pushover Priority | Sound | Must Acknowledge? |
| --------------------- | ----------------- | ----- | ----------------- |
| `BOOKING_CREATED`     | 2 (Emergency)     | dune  | Yes               |
| `BOOKING_RESCHEDULED` | 2 (Emergency)     | dune  | Yes               |
| `BOOKING_CANCELLED`   | 0 (Normal)        | dune  | No                |

## mise Configuration

Store the relay URL in `.mise.local.toml` for other tools to reference:

```toml
[env]
WEBHOOK_RELAY_URL = "https://calcom-pushover-webhook-XXXXX.us-central1.run.app/"
```
