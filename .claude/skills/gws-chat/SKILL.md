---
name: gws-chat
description: Google Chat API — messages, spaces, webhooks, bots, cards v2, interactive messages
---

# Google Chat API — MAARS Reference

## Webhook (No Auth Required)
```python
import requests

def send_chat_message(webhook_url: str, text: str):
    requests.post(webhook_url, json={"text": text})

def send_card(webhook_url: str, title: str, body: str):
    requests.post(webhook_url, json={
        "cardsV2": [{
            "cardId": "card1",
            "card": {
                "header": {"title": title},
                "sections": [{"widgets": [{"textParagraph": {"text": body}}]}]
            }
        }]
    })
```

## Bot API
```python
from googleapiclient.discovery import build
service = build("chat", "v1", credentials=creds)

# Send message
message = service.spaces().messages().create(
    parent="spaces/SPACE_ID",
    body={"text": "Hello from bot!"}
).execute()

# Send card with button
message = service.spaces().messages().create(
    parent="spaces/SPACE_ID",
    body={
        "cardsV2": [{
            "card": {
                "sections": [{
                    "widgets": [
                        {"textParagraph": {"text": "Approve this request?"}},
                        {"buttonList": {"buttons": [
                            {"text": "Approve", "onClick": {"action": {"actionMethodName": "approve"}}},
                            {"text": "Deny", "onClick": {"action": {"actionMethodName": "deny"}}},
                        ]}}
                    ]
                }]
            }
        }]
    }
).execute()

# List spaces
spaces = service.spaces().list().execute()
members = service.spaces().members().list(parent="spaces/SPACE_ID").execute()
```

## Common Patterns
- Webhooks = simplest (no OAuth, just POST to URL)
- Bots receive events via Pub/Sub or HTTPS endpoint
- Card v2 for rich interactive messages with buttons, forms
- Slash commands configured in Google Cloud Console
