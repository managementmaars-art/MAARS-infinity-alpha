# Cal.com API Setup Guide

How to obtain and configure Cal.com API credentials for autonomous CLI access.

## Option A: Self-Hosted Instance (Recommended)

If you've deployed Cal.com via Cloud Run or Docker Compose:

1. Log into your Cal.com instance (e.g., `https://calcom-your-project.run.app`)
2. Go to **Settings > Developer > API Keys**
3. Click **Create new API key**
4. Set expiration (or "Never" for automation)
5. Copy the generated key

## Option B: Cal.com Cloud (cal.com)

1. Log into [cal.com](https://cal.com)
2. Go to **Settings > Developer > API Keys**
3. Create a new key with appropriate permissions
4. Copy the generated key

## Store in 1Password

```bash
op item create --category "API Credential" \
  --title "Cal.com API Key" \
  --vault "Claude Automation" \
  "credential=cal_live_xxxxxxxxxxxx" \
  "api_url=https://your-calcom-instance.run.app"
```

Note the UUID from the output — this becomes your `CALCOM_OP_UUID`.

## Configure mise

Add to your project's `.mise.local.toml` (gitignored):

```toml
[env]
CALCOM_OP_UUID = "<uuid-from-1password>"
CALCOM_API_URL = "https://your-calcom-instance.run.app"
```

## Verify

```bash
CALCOM_CLI="$HOME/.claude/plugins/marketplaces/cc-skills/plugins/calcom-commander/scripts/calcom-cli/calcom"
$CALCOM_CLI event-types list
```

## API v2 Documentation

- [Cal.com API v2 Docs](https://cal.com/docs/api-reference/v2)
- Base URL: `https://api.cal.com/v2` (cloud) or `https://your-instance/api/v2` (self-hosted)
- Authentication: Bearer token in `Authorization` header
