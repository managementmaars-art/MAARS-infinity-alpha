# mise Configuration for Cal.com Commander

Step-by-step guide for configuring mise environment variables.

## Two-Layer Pattern

Cal.com Commander uses the standard two-layer mise pattern:

| Layer           | File               | Tracked | Contains                         |
| --------------- | ------------------ | ------- | -------------------------------- |
| Public config   | `mise.toml`        | Yes     | Tool versions, tasks, public env |
| Private secrets | `.mise.local.toml` | No      | UUIDs, project IDs, secret refs  |

## Required Variables

Add these to `.mise.local.toml` in your project directory:

```toml
[env]
# Cal.com API
CALCOM_OP_UUID = "<1password-item-uuid>"
CALCOM_API_URL = "https://your-instance.run.app"

# Telegram Bot
TELEGRAM_BOT_TOKEN = "<bot-token>"
TELEGRAM_CHAT_ID = "<chat-id>"

# AI Model
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# GCP (for deployment)
CALCOM_GCP_PROJECT = "<gcp-project-id>"
CALCOM_GCP_ACCOUNT = "<gcp-account-email>"
CALCOM_GCP_BILLING = "<billing-account-id>"
CALCOM_GCP_REGION = "us-central1"

# Supabase
SUPABASE_PROJECT_REF = "<supabase-project-ref>"
SUPABASE_DB_URL_REF = "op://Claude Automation/<item-id>/DATABASE_URL"
SUPABASE_DB_DIRECT_URL_REF = "op://Claude Automation/<item-id>/DATABASE_DIRECT_URL"
SUPABASE_ACCESS_TOKEN_REF = "op://Claude Automation/<item-id>/credential"

# Cal.com Secrets (1Password)
CALCOM_NEXTAUTH_SECRET_REF = "op://Claude Automation/<item-id>/NEXTAUTH_SECRET"
CALCOM_ENCRYPTION_KEY_REF = "op://Claude Automation/<item-id>/CALENDSO_ENCRYPTION_KEY"
CALCOM_CRON_API_KEY_REF = "op://Claude Automation/<item-id>/CRON_API_KEY"
```

## Verify

```bash
# Trust the config
mise trust

# Check all variables are loaded
mise env | grep -E "CALCOM|TELEGRAM|SUPABASE"
```

## Gitignore

Ensure `.mise.local.toml` is in your `.gitignore`:

```bash
grep -q '.mise.local.toml' .gitignore || echo '.mise.local.toml' >> .gitignore
```
