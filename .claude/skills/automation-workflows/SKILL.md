---
name: automation-workflows
description: AI automation workflows — n8n, Zapier-style automations, webhook patterns, cron jobs, event-driven pipelines, API integrations for MAARS automation agents
---

# Automation Workflows — MAARS Reference

## MAARS Automation Architecture
```
Trigger (Webhook/Cron/Event)
    → Task Queue (Redis/Celery)
        → Agent Execution
            → Tool Calls (APIs, DB, Files)
                → Output (Email/Webhook/DB/Notification)
```

## Webhook Patterns
```python
from fastapi import APIRouter, Request, BackgroundTasks
import hmac, hashlib

router = APIRouter()

@router.post("/webhooks/{integration}")
async def handle_webhook(
    integration: str,
    request: Request,
    background_tasks: BackgroundTasks,
):
    # Verify signature
    payload = await request.body()
    signature = request.headers.get("X-Signature-256", "")
    
    if not verify_signature(payload, signature, WEBHOOK_SECRETS[integration]):
        raise HTTPException(status_code=401)
    
    data = await request.json()
    
    # Process in background (return 200 immediately)
    background_tasks.add_task(process_webhook_event, integration, data)
    return {"status": "accepted"}

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

## Cron Job Patterns
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job("cron", hour=9, minute=0)  # Daily 9am
async def daily_briefing():
    """Generate daily briefing for all active users."""
    users = await db.fetch("SELECT id FROM users WHERE daily_briefing = true")
    for user in users:
        await agent_call("agent_secretary", {
            "task": "generate_daily_briefing",
            "user_id": user["id"],
        })

@scheduler.scheduled_job("interval", minutes=30)
async def monitor_campaigns():
    """Check campaign metrics every 30 minutes."""
    active_campaigns = await db.fetch("SELECT * FROM campaigns WHERE status = 'active'")
    for campaign in active_campaigns:
        metrics = await fetch_campaign_metrics(campaign["id"])
        if metrics["roas"] < campaign["target_roas"] * 0.8:
            await alert_agent("agent_marketing", f"Campaign {campaign['name']} underperforming")
```

## Event-Driven Pipeline
```python
import asyncio
from dataclasses import dataclass
from typing import Callable

@dataclass
class Event:
    type: str
    data: dict
    source: str

class EventBus:
    def __init__(self):
        self.handlers: dict[str, list[Callable]] = {}
    
    def on(self, event_type: str):
        def decorator(func):
            self.handlers.setdefault(event_type, []).append(func)
            return func
        return decorator
    
    async def emit(self, event: Event):
        handlers = self.handlers.get(event.type, [])
        await asyncio.gather(*[h(event) for h in handlers])

bus = EventBus()

@bus.on("task.completed")
async def on_task_complete(event: Event):
    await notify_user(event.data["user_id"], event.data["result"])
    await update_trust_score(event.data["agent_id"], success=True)

@bus.on("payment.received")
async def on_payment(event: Event):
    await provision_credits(event.data["user_id"], event.data["amount"])
    await send_receipt_email(event.data)
```

## API Integration Patterns
```python
# Generic third-party API integration
class APIIntegration:
    def __init__(self, base_url: str, api_key: str, rate_limit_rpm: int = 60):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        self.rate_limiter = asyncio.Semaphore(rate_limit_rpm // 60)
    
    async def get(self, path: str, **params) -> dict:
        async with self.rate_limiter:
            response = await self.client.get(path, params=params)
            response.raise_for_status()
            return response.json()
    
    async def post(self, path: str, data: dict) -> dict:
        async with self.rate_limiter:
            response = await self.client.post(path, json=data)
            response.raise_for_status()
            return response.json()
```

## Common Integrations Cheat Sheet
```python
INTEGRATIONS = {
    "slack": {
        "send_message": "POST /chat.postMessage",
        "auth": "Bot token in Authorization header",
        "webhook": "POST to incoming webhook URL",
    },
    "notion": {
        "create_page": "POST /v1/pages",
        "update_page": "PATCH /v1/pages/{id}",
        "query_db": "POST /v1/databases/{id}/query",
        "auth": "Bearer integration token",
    },
    "google_calendar": {
        "create_event": "POST /calendar/v3/calendars/{id}/events",
        "auth": "OAuth2 access token",
    },
    "stripe": {
        "create_payment": "POST /v1/payment_intents",
        "webhook_verify": "stripe.webhooks.constructEvent()",
    },
    "twilio": {
        "send_sms": "POST /2010-04-01/Accounts/{sid}/Messages",
        "send_whatsapp": "To: whatsapp:+1234567890",
    },
    "airtable": {
        "create_record": "POST /v0/{baseId}/{tableId}",
        "list_records": "GET /v0/{baseId}/{tableId}",
        "auth": "Bearer API key",
    },
}
```

## Models to Use
- **Workflow design**: `gpt-5.2` or `claude-opus-4-6`
- **Code generation for automations**: `claude-sonnet-4-6` or `codestral`
- **Error analysis**: `gpt-4o`
- **Quick trigger/action logic**: `deepseek-chat` (cheap + fast)
