# WordPress Publisher - Setup Guide

## Prerequisites

- WordPress site with admin access
- REST API enabled (default in modern WP)

## 1. Create Application Password

1. Log into WordPress Admin
2. Go to Users → Profile
3. Scroll to "Application Passwords"
4. Enter name: "Claude Code"
5. Click "Add New Application Password"
6. Copy the password (remove spaces)

## 2. Configure Environment

```bash
cd ~/.claude/skills/wordpress-publisher
cp .env.example .env
```

Edit `.env`:
```
WP_URL=https://your-site.com
WP_USERNAME=your_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

Note: Keep spaces in password or remove them - both work.

## 3. Test Connection

```bash
# Test API access
curl -u "username:app_password" https://your-site.com/wp-json/wp/v2/posts
```

If you get JSON response, setup is complete!

## 4. Mark Setup Complete

Edit `SKILL.md` and change:
```yaml
setup_complete: true
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check username and app password |
| 404 Not Found | Check WP_URL is correct |
| REST API disabled | Install/enable REST API plugin |
| CORS errors | Running from allowed origin |
