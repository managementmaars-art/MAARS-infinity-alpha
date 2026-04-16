---
name: godaddy-skill
description: Manage GoDaddy domains and DNS records. Use when the user asks to set up DNS, manage domain records, check DNS propagation, point domains to servers, or configure A/AAAA/CNAME/MX/TXT records. Supports bulk operations for quick domain setup.
allowed-tools: Bash, Read
---

# GoDaddy Skill - Domain & DNS Management

Manage domains and DNS records via the GoDaddy API. Set A records, CNAMEs, check propagation, bulk-configure DNS.

## CRITICAL: DNS Modification Confirmation Required

**Before modifying ANY DNS records, you MUST get explicit user confirmation.**

When the user asks to change DNS:
1. First, show current records using `get-records`
2. Show the proposed changes clearly
3. Ask: "Do you want me to apply these DNS changes?"
4. ONLY run set/add/delete commands AFTER the user explicitly confirms
5. NEVER modify DNS without confirmation

## First-Time Setup (~2 minutes)

### 1. Get API Key

1. Go to [GoDaddy Developer Portal](https://developer.godaddy.com/keys)
2. Click **Create New API Key**
3. Select **Production** environment
4. Copy the **Key** and **Secret**

**Note:** GoDaddy API access may require 10+ domains or a Discount Domain Club membership. If you get a 403 error, check your account eligibility.

### 2. Save Credentials

```bash
cat > ~/.claude/skills/godaddy-skill/config.json << 'EOF'
{
  "api_key": "YOUR_API_KEY",
  "api_secret": "YOUR_API_SECRET"
}
EOF
```

## Commands

### List Domains

```bash
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py list-domains
```

### Domain Info

```bash
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py domain-info DOMAIN
```

### Get DNS Records

```bash
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py get-records DOMAIN [--type TYPE] [--name NAME]
```

**Examples:**
```bash
# All records
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py get-records zergdesk.com

# Only A records
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py get-records zergdesk.com --type A

# Specific CNAME
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py get-records zergdesk.com --type CNAME --name www
```

### Set DNS Record (Replace)

Replaces all existing records of the same type + name.

```bash
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py set-record DOMAIN TYPE NAME DATA [--ttl TTL] [--priority N]
```

**Examples:**
```bash
# Point root to IP
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py set-record zergdesk.com A @ 66.241.125.67

# Point www to CNAME
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py set-record zergdesk.com CNAME www myapp.fly.dev

# Set MX record
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py set-record zergdesk.com MX @ mail.example.com --priority 10
```

### Add DNS Record (Append)

Adds a record without replacing existing ones of the same type + name.

```bash
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py add-record DOMAIN TYPE NAME DATA [--ttl TTL]
```

### Delete DNS Record

```bash
# Delete all records of type+name
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py delete-record DOMAIN TYPE NAME

# Delete specific value only
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py delete-record DOMAIN TYPE NAME --data VALUE
```

### Bulk Set (Multiple Records)

Set many records at once from JSON. Great for initial domain setup.

```bash
# From inline JSON
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py bulk-set DOMAIN '[{"type":"A","name":"@","data":"1.2.3.4"},{"type":"CNAME","name":"www","data":"app.fly.dev"}]'

# From a JSON file
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py bulk-set DOMAIN /path/to/records.json
```

**JSON format:**
```json
[
  {"type": "A", "name": "@", "data": "66.241.125.67", "ttl": 600},
  {"type": "AAAA", "name": "@", "data": "2a09:8280:1::cf:9869:0", "ttl": 600},
  {"type": "CNAME", "name": "www", "data": "myapp.fly.dev", "ttl": 600},
  {"type": "CNAME", "name": "_acme-challenge", "data": "domain.flydns.net", "ttl": 600}
]
```

### Check DNS Propagation

Uses local `dig` to check what DNS currently resolves to.

```bash
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py check-dns DOMAIN
```

## Common Workflows

### Point Domain to Fly.io

```bash
# 1. Check current records
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py get-records mydomain.com

# 2. Set the records Fly.io needs
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py bulk-set mydomain.com '[
  {"type":"A","name":"@","data":"FLY_IPV4"},
  {"type":"AAAA","name":"@","data":"FLY_IPV6"},
  {"type":"CNAME","name":"www","data":"APP.fly.dev"},
  {"type":"CNAME","name":"_acme-challenge","data":"DOMAIN.flydns.net"},
  {"type":"CNAME","name":"_acme-challenge.www","data":"www.DOMAIN.flydns.net"}
]'

# 3. Verify propagation
python3 ~/.claude/skills/godaddy-skill/godaddy_skill.py check-dns mydomain.com
```

## Output Format

All commands output JSON for easy parsing. Errors include HTTP status and detail.
