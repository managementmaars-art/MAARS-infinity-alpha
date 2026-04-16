# Telegram Bot API Reference

## Quick Reference

| Action       | Endpoint                        |
| ------------ | ------------------------------- |
| Send text    | `POST /bot<TOKEN>/sendMessage`  |
| Send file    | `POST /bot<TOKEN>/sendDocument` |
| Get bot info | `GET /bot<TOKEN>/getMe`         |

Base URL: `https://api.telegram.org`

## Bot Setup

### 1. Create a Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow prompts to name your bot
4. Copy the token (format: `123456789:ABCdefGHI...`)

### 2. Get Your User ID

1. Message [@userinfobot](https://t.me/userinfobot)
2. Copy the numeric ID it returns

### 3. Start Chat with Bot (Critical!)

Before the bot can message you:

1. Search for your bot by username in Telegram
2. Press "Start" to begin the chat

## API Endpoints

### Send Text Message

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "123456789",
    "text": "Your message",
    "parse_mode": "Markdown"
  }'
```

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `chat_id` | Yes | User ID (numeric) |
| `text` | Yes | Message content (max 4096 chars) |
| `parse_mode` | No | `Markdown` or `HTML` |

### Send Document

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendDocument" \
  -F "chat_id=123456789" \
  -F "document=@/path/to/file.md" \
  -F "caption=Optional caption"
```

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `chat_id` | Yes | User ID |
| `document` | Yes | File to send |
| `caption` | No | Text caption (max 1024 chars) |

### Verify Bot Token

```bash
curl "https://api.telegram.org/bot<TOKEN>/getMe"
```

Returns `{"ok": true, "result": {...}}` if valid.

## Text Formatting

### Markdown Mode

````
*bold*
_italic_
`code`
```code block```
[link](https://example.com)
````

### HTML Mode

```html
<b>bold</b>
<i>italic</i>
<code>code</code>
<pre>code block</pre>
<a href="https://example.com">link</a>
```

**Note**: Escape special characters in user input to avoid parsing errors.

## Error Codes

| Code | Error             | Cause                                   | Solution                         |
| ---- | ----------------- | --------------------------------------- | -------------------------------- |
| 401  | Unauthorized      | Invalid bot token                       | Verify token with `/getMe`       |
| 400  | chat not found    | Invalid user ID                         | Get correct ID from @userinfobot |
| 403  | bot was blocked   | User blocked bot or hasn't started chat | User must press "Start"          |
| 429  | Too Many Requests | Rate limit exceeded                     | Wait and retry                   |

## Limits

| Limit                      | Value           |
| -------------------------- | --------------- |
| Message length             | 4096 characters |
| Caption length             | 1024 characters |
| File size                  | 50 MB           |
| Messages/second (global)   | 30              |
| Messages/minute (per user) | 20              |

## Best Practices

1. **Always check `response.ok`** before processing results
2. **Implement retry logic** with exponential backoff for 429 errors
3. **Escape special characters** in Markdown/HTML to prevent parsing errors
4. **Keep messages concise** - split long content into multiple messages
5. **Use documents for files** - preserves quality better than inline

## Example: Send with Error Handling

```typescript
async function sendTelegram(token: string, chatId: string, text: string) {
  const response = await fetch(
    `https://api.telegram.org/bot${token}/sendMessage`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text }),
    }
  );

  const data = await response.json();
  if (!data.ok) {
    throw new Error(`Telegram error: ${data.description}`);
  }
  return data.result;
}
```

## Resources

- **Official Docs**: [core.telegram.org/bots/api](https://core.telegram.org/bots/api)
- **Bot Tutorial**: [core.telegram.org/bots/tutorial](https://core.telegram.org/bots/tutorial)
- **BotFather**: [@BotFather](https://t.me/BotFather)
- **User Info Bot**: [@userinfobot](https://t.me/userinfobot)
