# Error Handling Guide

## Quick Reference

| Error                | Cause                    | Solution                                       |
| -------------------- | ------------------------ | ---------------------------------------------- |
| "Bot not configured" | Setup not run            | `tsx scripts/setup.ts <token> <id> <key>`      |
| "Unauthorized"       | Invalid token or blocked | Verify token, start chat with bot              |
| "chat not found"     | Wrong user ID            | Get ID from @userinfobot                       |
| "EAI_AGAIN"          | DNS resolution failure   | Scripts use undici with proxy auto-detection   |
| Deployment failed    | Invalid deploy key       | Get new key from dashboard                     |

## Setup Errors

### "Bot not configured"

**Cause**: Configuration file missing or incomplete.

**Solution**:

```bash
tsx scripts/setup.ts <bot_token> <user_id> <deploy_key>
```

### "Invalid deploy key format"

**Cause**: Deploy key not copied correctly or expired.

**Solution**:

1. Go to [dashboard.convex.dev](https://dashboard.convex.dev)
2. Navigate to your project → Settings → Deploy Keys
3. Create a new "Production" deploy key
4. Copy the full key (format: `prod:deployment-name|key...`)

## Telegram API Errors

### "Unauthorized" or "bot was blocked by the user"

**Causes**:

- User hasn't started chat with bot
- Bot token is invalid
- User blocked the bot

**Solutions**:

1. Search for your bot in Telegram by username
2. Press "Start" to begin the chat
3. Verify bot token: `curl "https://api.telegram.org/bot<TOKEN>/getMe"`

### "chat not found"

**Cause**: User ID is incorrect.

**Solution**:

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy the numeric ID it returns
3. Update environment variable: `npx convex env set TELEGRAM_USER_ID "correct_id"`

### Rate Limit (429 Too Many Requests)

**Cause**: Exceeded Telegram's rate limits.

**Limits**:

- 30 messages/second globally
- 20 messages/minute per user

**Solution**: Wait and retry. For personal use, this is rarely hit.

## Network Errors

### "EAI_AGAIN" DNS Resolution Failure

**Cause**: Node.js native fetch doesn't use the environment's egress proxy, causing DNS resolution failures in sandboxed environments.

**Solution**: The tsx scripts now use `undici` with automatic proxy detection from `HTTP_PROXY`/`HTTPS_PROXY` environment variables. This is already configured in all scripts.

**How it works**:

- Scripts import `fetch` and `ProxyAgent` from `undici`
- Proxy is auto-detected: `process.env.HTTP_PROXY || process.env.HTTPS_PROXY`
- All fetch calls use `dispatcher: proxyAgent` option

**If you still have issues**:

1. Verify proxy environment variables are set
2. Check that undici is installed: `npm list undici`
3. Reinstall if needed: `npm install undici`

### General Network Issues

**Symptoms**: Timeouts, connection refused, DNS errors.

**Solutions**:

1. Check internet connection
2. Verify proxy environment variables (`HTTP_PROXY`, `HTTPS_PROXY`)
3. Check Convex status at [status.convex.dev](https://status.convex.dev)
4. Review logs: `npx convex logs`

## Deployment Errors

### "Could not resolve 'fs'" Error

**Cause**: Missing `"use node";` directive.

**Fix**: Ensure first line of `convex/telegram.ts` is:

```typescript
'use node';
```

### "Two output files share the same path" Error

**Cause**: Duplicate .js files in convex directory.

**Fix**:

```bash
rm -f convex/*.js convex/_generated/*.js
npx convex deploy
```

### TypeScript "Property does not exist" Errors

**Cause**: Missing type definitions or incorrect function visibility.

**Fixes**:

- Ensure internal functions use `internalQuery`/`internalMutation`
- Add `as any` type assertions to fetch responses

### "Cannot write file" TypeScript Error

**Cause**: TypeScript trying to generate files that exist.

**Fix**:

```bash
rm -f convex/_generated/*.js
```

## Message Delivery Issues

### Messages Not Sending

**Diagnostic steps**:

1. **Check cron is running**:
   - Convex Dashboard → Functions → Crons
   - Should see `process-scheduled-messages` every minute

2. **Verify environment variables**:

   ```bash
   npx convex env list
   ```

3. **Check pending messages**:
   - Dashboard → Data → `scheduled_messages`
   - Verify `status: "pending"` and `scheduled_time` is past

4. **Review logs**:
   ```bash
   npx convex logs --watch
   ```

### Wrong Timestamp Format

**Symptom**: Messages scheduled but never sent.

**Cause**: Using seconds instead of milliseconds.

**Correct format**: Unix timestamp in **milliseconds** (13 digits)

- ✅ `1768355400000`
- ❌ `1768355400`

**Get current timestamp**:

```javascript
Date.now(); // JavaScript
```

```bash
date +%s000  # Bash
```

## Debugging Commands

```bash
# Check configuration
cat /mnt/user-data/outputs/telegram_config.json

# Test database connection
tsx scripts/list_scheduled.ts

# Verify Telegram API
tsx scripts/send_message.ts "test"

# Check Convex deployment
curl https://<deployment>.convex.cloud

# Monitor real-time logs
npx convex logs --watch

# List environment variables
npx convex env list
```
