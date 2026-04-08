# MAARS Infinity - Credentials & Integrations Setup Guide

Complete guide for configuring API keys and integrations for MAARS Infinity.

## Quick Start - Minimal Setup for Local Development

For local development, you only need:

1. **MongoDB URL** — Set to `mongodb://localhost:27017` if running locally
2. **JWT Secret** — Run: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. **One LLM Provider** — Choose one: OpenAI, Anthropic, Google, Groq, or Cohere

Then create `.env`:
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=maars_infinity
JWT_SECRET=<generated-secret>
OPENAI_API_KEY=sk-... # or another LLM key
```

**Now skip directly to the Minimal LLM Setup section below** and choose your provider.

---

## Full Credentials Setup

### 1. Database Credentials

#### MongoDB Atlas (Recommended - Managed Cloud Database)

1. Go to https://www.mongodb.com/cloud/atlas
2. Create account and free cluster
3. Create database user with strong password
4. Get connection string from "Connect" button
5. Copy to `.env`:
   ```bash
   MONGO_URL=mongodb+srv://user:password@cluster.mongodb.net
   DB_NAME=maars_infinity
   ```

#### MongoDB Local (Development Only)

Already running? Use:
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=maars_infinity
```

### 2. Authentication & Security

#### JWT Secret (Required)

Generate a strong 32+ character secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to .env
JWT_SECRET=<output>
```

**Never use the same secret in development and production.**

#### Google OAuth (Optional - for Google Login)

1. Go to https://console.cloud.google.com/
2. Create new project: "MAARS Infinity"
3. Enable APIs: Google+ API, Google Calendar API
4. Create OAuth 2.0 credentials (Web application)
5. Add authorized redirect URIs:
   - Development: `http://localhost:8000/api/auth/google/callback`
   - Production: `https://your-domain.com/api/auth/google/callback`
6. Copy credentials to `.env`:
   ```bash
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   ```

---

## Minimal LLM Setup - Choose One Provider

You need **at least one** LLM provider to use the chat features. Here are the easiest:

### Option 1: OpenAI (Recommended for Beginners)

1. Go to https://platform.openai.com/account/api-keys
2. Create new secret key
3. Copy to `.env`:
   ```bash
   OPENAI_API_KEY=sk-...
   ```

**Models available:** GPT-4, GPT-4 Turbo, GPT-3.5 Turbo

**Cost:** Pay-as-you-go (~$0.01-0.03 per chat message)

### Option 2: Anthropic (Best for Long Context)

1. Go to https://console.anthropic.com/
2. Create account and get API key
3. Copy to `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-...
   ```

**Models available:** Claude 3 Opus, Sonnet, Haiku

**Cost:** Pay-as-you-go (~$0.01-0.02 per chat message)

### Option 3: Google Gemini (Fast & Free Tier)

1. Go to https://makersuite.google.com/app/apikey
2. Create API key (free tier available)
3. Copy to `.env`:
   ```bash
   GOOGLE_API_KEY=...
   ```

**Models available:** Gemini Pro, Gemini Ultra

**Cost:** Free tier (50 requests/minute), pay-as-you-go after

### Option 4: Groq (Fastest, Free)

1. Go to https://console.groq.com/
2. Create account and get API key
3. Copy to `.env`:
   ```bash
   GROQ_API_KEY=gsk_...
   ```

**Models available:** Mixtral 8x7b, Llama 70b

**Cost:** Free (rate limited), no paid tier yet

### Option 5: Cohere (Specialized)

1. Go to https://dashboard.cohere.ai/
2. Create account and get API key
3. Copy to `.env`:
   ```bash
   COHERE_API_KEY=...
   ```

**Models available:** Command, Generate, Embed

**Cost:** Free tier (100k tokens/month), pay-as-you-go after

---

## Full Integration Setup

### Email (SMTP)

Send emails for notifications, password resets, etc.

#### Gmail (Easiest)

1. Go to https://myaccount.google.com/apppasswords
2. Generate app-specific password
3. Copy to `.env`:
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_EMAIL=your-email@gmail.com
   SMTP_PASSWORD=<16-char-app-password>
   SMTP_FROM_NAME=MAARS Infinity
   ```

#### SendGrid (Recommended for Production)

1. Go to https://sendgrid.com/
2. Create account and verify sender email
3. Get API key from Settings > API Keys
4. Copy to `.env`:
   ```bash
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_EMAIL=apikey
   SMTP_PASSWORD=SG...
   SMTP_FROM_NAME=MAARS Infinity
   ```

#### Mailgun

1. Go to https://www.mailgun.com/
2. Create account and domain
3. Get SMTP credentials from domain settings
4. Copy to `.env`:
   ```bash
   SMTP_HOST=smtp.mailgun.org
   SMTP_PORT=587
   SMTP_EMAIL=<mailgun-email>
   SMTP_PASSWORD=<mailgun-password>
   ```

### Payment Processing (Stripe)

Enable premium subscriptions and payments.

1. Go to https://dashboard.stripe.com/
2. Create account
3. Get API keys from Settings > API Keys
4. Copy to `.env`:
   ```bash
   STRIPE_API_KEY=sk_live_... # For production
   # or
   STRIPE_API_KEY=sk_test_... # For development
   ```

**Webhook:** Set up Stripe webhook pointing to `https://your-domain.com/api/subscriptions/webhook`

### Web Search

Enable ability to search the web for information.

#### DuckDuckGo (Free, No API Key)

Already enabled by default:
```bash
DUCKDUCKGO_ENABLED=true
```

No configuration needed!

#### Serper (Requires API Key)

1. Go to https://serper.dev/
2. Create account and get API key (20K free searches/month)
3. Copy to `.env`:
   ```bash
   SERPER_API_KEY=...
   ```

#### Alternative: Google Search API

1. Go to https://programmablesearchengine.google.com/
2. Create custom search engine
3. Get API key from Google Cloud Console
4. Copy to `.env`:
   ```bash
   GOOGLE_SEARCH_API_KEY=...
   ```

### Voice & Audio

#### ElevenLabs (Text-to-Speech)

1. Go to https://elevenlabs.io/
2. Create account (free tier: 10,000 characters/month)
3. Get API key from Profile > API Key
4. Copy to `.env`:
   ```bash
   ELEVENLABS_API_KEY=...
   ```

### Calendar Integration

#### Google Calendar

1. Go to https://console.cloud.google.com/
2. Enable Google Calendar API
3. Get API key (same as OAuth credentials above)
4. Copy to `.env`:
   ```bash
   GOOGLE_CALENDAR_API_KEY=...
   ```

#### Microsoft Calendar

1. Go to https://portal.azure.com/
2. Register application in Azure AD
3. Get client ID and secret
4. Copy to `.env`:
   ```bash
   MICROSOFT_CALENDAR_API_KEY=...
   MICROSOFT_TENANT_ID=...
   ```

### Social Media Integration (Optional)

#### Twitter/X

1. Go to https://developer.twitter.com/
2. Create app and get bearer token
3. Copy to `.env`:
   ```bash
   TWITTER_API_KEY=...
   TWITTER_API_SECRET=...
   ```

#### LinkedIn

1. Go to https://www.linkedin.com/developers/apps
2. Create app and get access token
3. Copy to `.env`:
   ```bash
   LINKEDIN_API_KEY=...
   ```

---

## Environment Variables Reference

### Required
- `MONGO_URL` — MongoDB connection string
- `DB_NAME` — Database name
- `JWT_SECRET` — JWT signing secret

### LLM (At Least One Required)
- `OPENAI_API_KEY` — OpenAI API key
- `ANTHROPIC_API_KEY` — Anthropic API key  
- `GOOGLE_API_KEY` — Google Gemini API key
- `GROQ_API_KEY` — Groq API key
- `COHERE_API_KEY` — Cohere API key

### Optional Integrations
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` — Google OAuth
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_EMAIL`, `SMTP_PASSWORD` — Email
- `STRIPE_API_KEY` — Payment processing
- `ELEVENLABS_API_KEY` — Voice synthesis
- `SERPER_API_KEY` — Enhanced web search
- `DUCKDUCKGO_ENABLED` — Basic web search (default: true)

### Server Configuration
- `ENVIRONMENT` — "development", "staging", or "production"
- `SERVER_PORT` — Server port (default: 8000)
- `UPLOAD_DIR` — File upload directory (default: ./uploads)
- `CORS_ORIGINS` — Allowed origins for requests

---

## Verification

After setting up credentials, verify they work:

```bash
# Start backend
cd backend
python server.py

# In new terminal, test LLM connection
curl -X POST http://localhost:8000/api/chats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Should return a chat response, not an authentication error
```

### Troubleshooting

**"API key invalid"**
- Double-check you copied the full key
- Regenerate the key and try again
- Check key hasn't expired

**"SMTP authentication failed"**
- Verify username/password (not email and password)
- For Gmail, use app-specific password, not Google password
- Check SMTP host and port are correct

**"Stripe webhook failed"**
- Verify webhook URL is publicly accessible
- Check webhook signing secret is correct
- Test with Stripe CLI: `stripe listen --forward-to http://localhost:8000/api/subscriptions/webhook`

**"Google OAuth redirects to wrong URL"**
- Ensure authorized redirect URI in Google Console matches exactly
- Include protocol (http://, https://)
- Check for trailing slashes

**"Web search not working"**
- DuckDuckGo should work by default (no key needed)
- If using Serper, verify API key and remaining search quota
- Check rate limiting

---

## Security Best Practices

1. **Never commit `.env` files** — Use `.env.example` as template
2. **Rotate keys regularly** — Especially in production
3. **Use different keys** — Development, staging, production should have separate keys
4. **Monitor usage** — Set up billing alerts on API providers
5. **Store securely** — Use GitHub Secrets for CI/CD, environment variable services for production
6. **Restrict scopes** — Give API keys minimum required permissions

---

## Need Help?

- **API key not working?** Check if it's been deleted or expired
- **Can't find service?** Look for "API keys" or "Settings" in product dashboard
- **Not sure which provider?** Start with OpenAI (most popular) or Groq (fastest)
- **Running in production?** Use managed services (MongoDB Atlas, SendGrid, etc.) instead of self-hosted

For detailed setup instructions for specific integrations, see the SETUP.md and DEPLOYMENT.md guides.
