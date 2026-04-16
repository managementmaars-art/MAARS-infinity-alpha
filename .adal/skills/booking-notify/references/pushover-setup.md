# Pushover Setup Guide

Complete setup for Pushover dual-channel notifications alongside Telegram.

## Prerequisites

- Pushover account (<https://pushover.net/>)
- Pushover app on iOS/Android
- 1Password CLI (`op`) configured

## Step 1: Create Pushover Application

1. Go to <https://pushover.net/apps/build>
2. Create a new application (e.g., "Cal.com Booking Alerts")
3. Note the **API Token/Key** (30 characters, e.g., `a14t3ngicf...`)

## Step 2: Get Your User Key

1. Log into <https://pushover.net/>
2. Your **User Key** is shown on the dashboard (30 characters, e.g., `ury88s1def...`)

## Step 3: Upload Custom Sound (Optional)

1. Go to <https://pushover.net/> dashboard
2. Scroll to "Custom Sounds" section
3. Upload an audio file (e.g., "dune.wav")
4. Note the sound name (e.g., `dune`)

## Step 4: Store in 1Password

```bash
op item create --category "API Credential" \
  --title "Pushover - Cal.com Booking Alerts" \
  --vault "Claude Automation" \
  "username=<your-user-key>" \
  "password=<your-app-token>"
```

Note the item UUID from the output.

## Step 5: Configure mise

Add to `.mise.local.toml` (gitignored):

```toml
[env]
PUSHOVER_OP_UUID = "<uuid-from-step-4>"
PUSHOVER_SOUND = "dune"
```

To load the actual tokens at runtime, add to your project's `.mise.local.toml`:

```toml
[env]
PUSHOVER_APP_TOKEN = "{{ exec(command='op item get <uuid> --vault \"Claude Automation\" --fields password --reveal') }}"
PUSHOVER_USER_KEY = "{{ exec(command='op item get <uuid> --vault \"Claude Automation\" --fields username --reveal') }}"
PUSHOVER_SOUND = "dune"
```

## Step 6: Test

```bash
curl -s --form-string "token=$PUSHOVER_APP_TOKEN" \
  --form-string "user=$PUSHOVER_USER_KEY" \
  --form-string "title=Test Alert" \
  --form-string "message=Pushover integration working" \
  --form-string "sound=$PUSHOVER_SOUND" \
  --form-string "priority=0" \
  https://api.pushover.net/1/messages.json
```

Expected: `{"status":1,...}` and notification on your device.

## Priority Levels

| Priority | Name      | Behavior                                            |
| -------- | --------- | --------------------------------------------------- |
| 0        | Normal    | Default sound, respects quiet hours                 |
| 1        | High      | Bypasses quiet hours, alert sound                   |
| 2        | Emergency | Repeats until acknowledged, requires retry + expire |

## Critical Rules

- **Pushover is plain text only** — never send HTML tags
- Build messages in HTML for Telegram, then use `stripHtmlForPushover()` for Pushover
- Emergency priority (2) requires `retry` (seconds between retries) and `expire` (seconds until stop)
- Custom sounds must be uploaded to your Pushover account first
