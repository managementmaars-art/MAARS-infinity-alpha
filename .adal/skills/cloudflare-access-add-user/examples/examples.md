# Add Access User - Examples

## Example 1: Adding a Single Workspace Email

**User Request:** "Add sarah@temet.ai to Cloudflare Access"

**Current .env:**
```
ACCESS_ALLOWED_EMAIL="dawiddutoit@temet.ai,fifthchildd@gmail.com"
```

**Updated .env:**
```
ACCESS_ALLOWED_EMAIL="dawiddutoit@temet.ai,fifthchildd@gmail.com,sarah@temet.ai"
```

**Script include array update:**
```json
"include": [
    {"email": {"email": "dawiddutoit@temet.ai"}},
    {"email": {"email": "fifthchildd@gmail.com"}},
    {"email": {"email": "sarah@temet.ai"}}
]
```

**Result:** Workspace email works immediately with Internal OAuth.

---

## Example 2: Adding a Personal Gmail Account

**User Request:** "Grant access to johndoe@gmail.com"

**Important:** Before this will work, Google OAuth consent screen must be "External":
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Edit OAuth consent screen
3. Change User Type: Internal -> External
4. Save

**Current .env:**
```
ACCESS_ALLOWED_EMAIL="dawiddutoit@temet.ai"
```

**Updated .env:**
```
ACCESS_ALLOWED_EMAIL="dawiddutoit@temet.ai,johndoe@gmail.com"
```

**Script include array update:**
```json
"include": [
    {"email": {"email": "dawiddutoit@temet.ai"}},
    {"email": {"email": "johndoe@gmail.com"}}
]
```

---

## Example 3: Adding Multiple Users at Once

**User Request:** "Add these users: alice@temet.ai, bob@gmail.com, charlie@temet.ai"

**Current .env:**
```
ACCESS_ALLOWED_EMAIL="dawiddutoit@temet.ai"
```

**Updated .env:**
```
ACCESS_ALLOWED_EMAIL="dawiddutoit@temet.ai,alice@temet.ai,bob@gmail.com,charlie@temet.ai"
```

**Script include array update:**
```json
"include": [
    {"email": {"email": "dawiddutoit@temet.ai"}},
    {"email": {"email": "alice@temet.ai"}},
    {"email": {"email": "bob@gmail.com"}},
    {"email": {"email": "charlie@temet.ai"}}
]
```

---

## Example 4: User Already Exists (Duplicate)

**User Request:** "Add dawiddutoit@temet.ai to access"

**Current .env:**
```
ACCESS_ALLOWED_EMAIL="dawiddutoit@temet.ai,fifthchildd@gmail.com"
```

**Response:**
```
Email dawiddutoit@temet.ai is already in ACCESS_ALLOWED_EMAIL.
No changes needed - this user already has access.

Current allowed users:
- dawiddutoit@temet.ai
- fifthchildd@gmail.com
```

---

## Example 5: Invalid Email Format

**User Request:** "Add john.doe to access"

**Response:**
```
Invalid email format: john.doe

Please provide a valid email address (e.g., john.doe@example.com)
```

---

## Example 6: Script Output - Success

```
$ ./scripts/update-access-emails.sh
Updating policies for all services to include all three emails...

Processing app: 56de3246-c9ed-4877-8af1-dc360ac49584
  Updating policy: a1b2c3d4-e5f6-7890-abcd-ef1234567890
  [checkmark] Policy updated successfully

Processing app: 9f1e8109-3f3f-456e-94f5-093bfc9e1c1e
  Updating policy: b2c3d4e5-f6a7-8901-bcde-f12345678901
  [checkmark] Policy updated successfully

Processing app: 627a38c5-3ebc-4e40-9ffe-b3f15f6ac223
  Updating policy: c3d4e5f6-a7b8-9012-cdef-123456789012
  [checkmark] Policy updated successfully

Processing app: ccd54045-ec9a-40a9-867a-56394cb4db0e
  Updating policy: d4e5f6a7-b8c9-0123-defa-234567890123
  [checkmark] Policy updated successfully

Processing app: ea073943-5198-48b8-9846-627201657204
  Updating policy: e5f6a7b8-c9d0-1234-efab-345678901234
  [checkmark] Policy updated successfully

Processing app: 7a795a73-a2ab-4ae2-adaa-515c30af4c70
  Updating policy: f6a7b8c9-d0e1-2345-fabc-456789012345
  [checkmark] Policy updated successfully

All policies updated!
```

---

## Example 7: Script Output - Partial Failure

```
$ ./scripts/update-access-emails.sh
Updating policies for all services to include all three emails...

Processing app: 56de3246-c9ed-4877-8af1-dc360ac49584
  Updating policy: a1b2c3d4-e5f6-7890-abcd-ef1234567890
  [checkmark] Policy updated successfully

Processing app: 9f1e8109-3f3f-456e-94f5-093bfc9e1c1e
  [warning] No existing policy found, skipping

...
```

**Troubleshooting:** Policy may have been deleted. Run `./scripts/cf-access-setup.sh list` to check applications, then re-run `./scripts/cf-access-setup.sh setup` to recreate missing policies.

---

## Example 8: Test Instructions for New User

After adding `newuser@gmail.com`:

```
ACCESS GRANTED FOR: newuser@gmail.com

To verify your access:

1. Open an incognito/private browser window
   (Important: Use incognito to avoid cached sessions)

2. Navigate to: https://pihole.temet.ai

3. You'll see the Cloudflare Access login page
   Click "Google" to authenticate

4. Sign in with: newuser@gmail.com
   (Must match exactly - the email you provided)

5. After successful authentication, you'll see Pi-hole admin interface

All services you can access:
- https://pihole.temet.ai - Pi-hole DNS admin
- https://jaeger.temet.ai - Jaeger tracing UI
- https://langfuse.temet.ai - Langfuse monitoring
- https://sprinkler.temet.ai - Sprinkler system
- https://ha.temet.ai - Home Assistant
- https://temet.ai - Services dashboard

Note: Sessions last 24 hours. You'll need to re-authenticate after that.

If you see "Access Denied":
1. Verify you're using the exact email address
2. Clear browser cookies and try again
3. Contact the admin to verify the email was added correctly
```

---

## Example 9: Complete Workflow

**User:** "Add my friend jane@example.com to the network"

**Step 1 - Check current state:**
```bash
grep "ACCESS_ALLOWED_EMAIL" /home/dawiddutoit/projects/network/.env
# ACCESS_ALLOWED_EMAIL="dawiddutoit@temet.ai,fifthchildd@gmail.com,dawidddutoit@gmail.com"
```

**Step 2 - Validate email:**
- Format: valid (jane@example.com)
- Duplicate check: not in current list

**Step 3 - Update .env:**
Edit ACCESS_ALLOWED_EMAIL to:
```
ACCESS_ALLOWED_EMAIL="dawiddutoit@temet.ai,fifthchildd@gmail.com,dawidddutoit@gmail.com,jane@example.com"
```

**Step 4 - Update script:**
Edit /home/dawiddutoit/projects/network/scripts/update-access-emails.sh around line 48:
```json
"include": [
    {"email": {"email": "dawiddutoit@temet.ai"}},
    {"email": {"email": "fifthchildd@gmail.com"}},
    {"email": {"email": "dawidddutoit@gmail.com"}},
    {"email": {"email": "jane@example.com"}}
]
```

**Step 5 - Run update:**
```bash
cd /home/dawiddutoit/projects/network && ./scripts/update-access-emails.sh
```

**Step 6 - Verify output:**
All 6 services show "Policy updated successfully"

**Step 7 - Provide instructions to user:**
Share test instructions for jane@example.com

---

## Edge Cases

### Case: Email with Plus Sign
Email: `john+test@gmail.com`
- Valid format, should work
- Treated as unique email by Cloudflare

### Case: Case Sensitivity
Email provided: `John.Doe@Gmail.COM`
- Store as provided, but authentication is case-insensitive
- User can sign in with `john.doe@gmail.com`

### Case: Corporate Email with SSO
Email: `employee@bigcorp.com`
- May work if BigCorp uses Google Workspace
- May fail if BigCorp uses different SSO provider
- User will see Google login, but their corporate account may not work
