# Add Access User - Technical Reference

## Cloudflare Access API

### Base URL
```
https://api.cloudflare.com/client/v4
```

### Authentication Header
```
Authorization: Bearer ${CLOUDFLARE_ACCESS_API_TOKEN}
```

### Protected Service App IDs

| Service | App ID | Domain |
|---------|--------|--------|
| Services Dashboard | 56de3246-c9ed-4877-8af1-dc360ac49584 | temet.ai |
| Home Assistant | 9f1e8109-3f3f-456e-94f5-093bfc9e1c1e | ha.temet.ai |
| Sprinkler System | 627a38c5-3ebc-4e40-9ffe-b3f15f6ac223 | sprinkler.temet.ai |
| Langfuse Monitoring | ccd54045-ec9a-40a9-867a-56394cb4db0e | langfuse.temet.ai |
| Jaeger Tracing | ea073943-5198-48b8-9846-627201657204 | jaeger.temet.ai |
| Pi-hole Admin | 7a795a73-a2ab-4ae2-adaa-515c30af4c70 | pihole.temet.ai |

### Policy Update API

**Endpoint:**
```
PUT /accounts/${ACCOUNT_ID}/access/apps/${APP_ID}/policies/${POLICY_ID}
```

**Request Body Structure:**
```json
{
    "name": "Allow authorized users",
    "decision": "allow",
    "include": [
        {"email": {"email": "user1@example.com"}},
        {"email": {"email": "user2@example.com"}},
        {"email": {"email": "user3@example.com"}}
    ]
}
```

### Getting Existing Policies

**Endpoint:**
```
GET /accounts/${ACCOUNT_ID}/access/apps/${APP_ID}/policies
```

**Response Structure:**
```json
{
    "success": true,
    "result": [
        {
            "id": "policy-uuid",
            "name": "Allow authorized users",
            "decision": "allow",
            "include": [...]
        }
    ]
}
```

## File Locations

| File | Purpose |
|------|---------|
| `/home/dawiddutoit/projects/network/.env` | ACCESS_ALLOWED_EMAIL variable |
| `/home/dawiddutoit/projects/network/scripts/update-access-emails.sh` | Policy update script |
| `/home/dawiddutoit/projects/network/scripts/cf-access-setup.sh` | Initial setup script (not for adding users) |

## Environment Variables

Required in `.env`:
```bash
CLOUDFLARE_ACCOUNT_ID=<account-id>
CLOUDFLARE_ACCESS_API_TOKEN=<api-token>
ACCESS_ALLOWED_EMAIL="email1,email2,email3"
```

## Script Modification Details

### update-access-emails.sh Structure

The script contains hardcoded email addresses at approximately lines 46-53:

```bash
--data '{
    "name": "Allow authorized users",
    "decision": "allow",
    "include": [
        {"email": {"email": "dawiddutoit@temet.ai"}},
        {"email": {"email": "fifthchildd@gmail.com"}},
        {"email": {"email": "dawidddutoit@gmail.com"}}
    ]
}'
```

When adding a new email, add a new entry to the include array:
```json
{"email": {"email": "newemail@example.com"}}
```

## Troubleshooting

### "Invalid format for Authorization header"
- API token is wrong format
- Solution: Check CLOUDFLARE_ACCESS_API_TOKEN in .env

### "Policy update failed"
- Policy ID may have changed
- Solution: List policies manually and update script

### "403 Forbidden"
- API token lacks permissions
- Required permissions:
  - Account -> Zero Trust -> Edit
  - Account -> Access: Apps and Policies -> Edit

### "Can only be used within its organization"
- Adding non-workspace Gmail to Internal OAuth app
- Solution: Change Google OAuth consent screen to "External"
  - URL: https://console.cloud.google.com/apis/credentials/consent
  - Edit OAuth consent screen
  - Change User Type from "Internal" to "External"

### User can't authenticate after adding
1. Verify email spelling exactly matches
2. Confirm script completed successfully for all 6 services
3. Ask user to clear browser cookies and try again
4. Check access logs: https://one.dash.cloudflare.com -> Logs -> Access

## Listing Current Policies

To manually verify policies:

```bash
cd /home/dawiddutoit/projects/network
source .env

# List all apps
curl -s -X GET \
    "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps" \
    -H "Authorization: Bearer ${CLOUDFLARE_ACCESS_API_TOKEN}" \
    -H "Content-Type: application/json" | python3 -m json.tool

# Get policies for specific app
curl -s -X GET \
    "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps/APP_ID_HERE/policies" \
    -H "Authorization: Bearer ${CLOUDFLARE_ACCESS_API_TOKEN}" \
    -H "Content-Type: application/json" | python3 -m json.tool
```

## Removing a User

To remove a user, reverse the process:
1. Remove email from ACCESS_ALLOWED_EMAIL in .env
2. Remove email entry from update-access-emails.sh include array
3. Run ./scripts/update-access-emails.sh
4. Verify policies updated

User's active sessions will continue until expiration (24 hours) or they clear cookies.

## Audit Trail

All access attempts are logged in Cloudflare:
- Dashboard: https://one.dash.cloudflare.com -> Logs -> Access
- Shows: User, timestamp, service, allow/deny decision, IP address
