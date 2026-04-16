# 1Password Credential Setup for Cloudflare Workers

Step-by-step guide for provisioning Cloudflare API credentials in 1Password's Claude Automation vault.

## Architecture

```
1Password — Claude Automation vault

  Item: "Cloudflare Workers - {project}"
  ├── account_id  [TEXT]       = Cloudflare Account ID
  └── credential  [CONCEALED] = Cloudflare API Token

  Access:
  ├── Biometric (interactive op CLI): CREATE, READ, UPDATE
  └── Service Account (headless):     READ, UPDATE only
```

## Critical Constraint (CFW-02)

**1Password service accounts CANNOT create new items.** They can only READ and UPDATE existing items. Create the item first via one of:

1. Interactive `op` CLI (biometric prompt)
2. 1Password web UI (<https://my.1password.com>)
3. 1Password desktop app

## Step-by-Step Provisioning

### Step 1: Get Cloudflare Account ID

1. Go to <https://dash.cloudflare.com>
2. Click on any domain (or Workers and Pages)
3. Account ID is shown in the right sidebar (32-char hex string)

### Step 2: Create API Token

1. Go to <https://dash.cloudflare.com/profile/api-tokens>
2. **Create Token** > **Custom token**
3. Permissions: **Account** > **Workers Scripts** > **Edit** (CFW-11)
4. Account Resources: **Include** > your account
5. **Continue to summary** > **Create Token**
6. **Copy the token immediately** (shown only once)

### Step 3: Create 1Password Item (Interactive)

Using biometric `op` CLI:

```bash
# Create the item (requires biometric authentication)
op item create \
  --category "API Credential" \
  --title "Cloudflare Workers - {project-name}" \
  --vault "Claude Automation" \
  --tags "cloudflare,workers,static-hosting"

# Note the item ID from the output (e.g., "ewtid322w2bozkzqfg4my2kd5m")
```

Or via 1Password web UI: Navigate to Claude Automation vault > + > API Credential.

### Step 4: Set Fields

```bash
# Set account_id (TEXT field)
op item edit "{item-id}" \
  --vault "Claude Automation" \
  "account_id[text]={your-cloudflare-account-id}"

# Set credential (CONCEALED field)
op item edit "{item-id}" \
  --vault "Claude Automation" \
  "credential[concealed]={your-api-token}"
```

Or via web UI: edit the item, add a TEXT field named `account_id` and a CONCEALED field named `credential`.

### Step 5: Verify Service Account Access

```bash
# Test that the headless service account can read the item
OP_SERVICE_ACCOUNT_TOKEN="$(cat ~/.claude/.secrets/op-service-account-token)" \
  op item get "{item-id}" --vault "Claude Automation" --fields "account_id"

# CRITICAL (CFW-03): Use --reveal for the CONCEALED field
OP_SERVICE_ACCOUNT_TOKEN="$(cat ~/.claude/.secrets/op-service-account-token)" \
  op item get "{item-id}" --vault "Claude Automation" --fields "credential" --reveal

# Both should return actual values, not masked placeholders
```

### Step 6: Record Item ID

Store the 1Password item ID in your deploy script as a constant:

```bash
OP_ITEM_ID="ewtid322w2bozkzqfg4my2kd5m"
```

This ID is NOT secret (opaque reference, not a credential). Safe to commit to source control.

## Field Type Reference

| Field Name   | 1Password Type | `--reveal` Needed | Purpose                             |
| ------------ | -------------- | ----------------- | ----------------------------------- |
| `account_id` | TEXT           | No                | Cloudflare Account ID (32-char hex) |
| `credential` | CONCEALED      | **YES** (CFW-03)  | API token (sensitive)               |

## Service Account Token Location

```
~/.claude/.secrets/op-service-account-token   (chmod 600)
```

Access scope: Read + Write to the **Claude Automation** vault only.

## Reusing Credentials Across Projects

If multiple projects deploy to the same Cloudflare account, they can share the same 1Password item. The token's Workers Scripts Edit permission applies to all workers in the account.

Differentiate projects via separate worker names in wrangler.toml. One API token deploys to all of them.

## Token Rotation

1. Create new API token in Cloudflare dashboard
2. **Update** the existing 1Password item (biometric or web UI required):

   ```bash
   op item edit "{item-id}" \
     --vault "Claude Automation" \
     "credential[concealed]={new-api-token}"
   ```

3. Verify deploy works with new token
4. Revoke old token in Cloudflare dashboard

The deploy script needs no changes since it reads from the same 1Password item.
