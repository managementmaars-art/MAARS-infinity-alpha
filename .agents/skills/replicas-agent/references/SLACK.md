# Slack Integration

This guide covers how to interact with Slack from within your Replicas workspace.

## Prerequisites

Check if the `SLACK_BOT_TOKEN` environment variable is set:

```bash
echo "${SLACK_BOT_TOKEN:+set}"
```

- If **set**: Your workspace has Slack access. You can use the Slack Web API as described below.
- If **not set**: Slack has not been configured for this workspace. The user needs to connect Slack in the [Replicas dashboard](https://replicas.dev) under their organization's integration settings. Let the user know and do not attempt Slack operations.

## Using the Slack API

All requests use the `$SLACK_BOT_TOKEN` for authentication via the Slack Web API.

### Fetching a Thread from a Slack Link

If you encounter a Slack message link (e.g. `https://team.slack.com/archives/C0123ABC/p1234567890123456`), extract the channel ID and thread timestamp:

- **Channel ID**: The segment after `/archives/` (e.g. `C0123ABC`)
- **Thread TS**: The `p` value with a dot inserted before the last 6 digits (e.g. `p1234567890123456` -> `1234567890.123456`)

```bash
curl -s "https://slack.com/api/conversations.replies?channel=CHANNEL_ID&ts=THREAD_TS" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN"
```

### Sending a Message

```bash
curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "CHANNEL_ID",
    "text": "Your message here",
    "thread_ts": "OPTIONAL_THREAD_TS"
  }'
```

Omit `thread_ts` to post a new message to the channel. Include it to reply in a thread.

### Searching Messages

```bash
curl -s "https://slack.com/api/search.messages?query=YOUR_SEARCH_QUERY" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN"
```

### Uploading Files

```bash
curl -s -X POST "https://slack.com/api/files.uploadV2" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -F "channel_id=CHANNEL_ID" \
  -F "file=@/path/to/file" \
  -F "title=File title"
```

### Other Operations

You can list channels, read channel history, add reactions, and perform any other operation supported by the Slack Web API using the same authentication pattern.

For full API documentation, see: https://docs.slack.dev/apis/web-api/
