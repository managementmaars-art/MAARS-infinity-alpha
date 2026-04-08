---
name: email-automation
description: AI email automation — SendGrid, SMTP, email sequences, drip campaigns, transactional emails, deliverability, templates for MAARS communication agents
---

# Email Automation — MAARS Reference

## SendGrid Integration (MAARS primary)
```python
import sendgrid
from sendgrid.helpers.mail import Mail, To, From, Subject, Content

sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

async def send_email(
    to: str | list[str],
    subject: str,
    html_content: str,
    from_email: str = "noreply@maars.ai",
    from_name: str = "MAARS Command",
    reply_to: str = None,
) -> dict:
    message = Mail(
        from_email=(from_email, from_name),
        to_emails=to if isinstance(to, list) else [to],
        subject=subject,
        html_content=html_content,
    )
    if reply_to:
        message.reply_to = reply_to
    
    response = sg.client.mail.send.post(request_body=message.get())
    return {"status": response.status_code, "message_id": response.headers.get("X-Message-Id")}
```

## Dynamic Template System
```python
async def send_template_email(
    to: str,
    template_id: str,
    template_data: dict,
    from_email: str = "noreply@maars.ai",
) -> dict:
    message = Mail(from_email=from_email, to_emails=to)
    message.template_id = template_id
    message.dynamic_template_data = template_data
    
    response = sg.client.mail.send.post(request_body=message.get())
    return {"status": response.status_code}
```

## MAARS Email Templates

### Welcome Email
```html
Subject: Welcome to MAARS Command, {{first_name}} 🚀

<h1>Your AI Team is Ready</h1>
<p>Hi {{first_name}},</p>
<p>You now have access to {{agent_count}} AI specialists ready to work for you.</p>
<p>Start by chatting with Commander Orion — just tell it your goal and it will 
   deploy the right agents automatically.</p>
<a href="{{login_url}}">Open MAARS Command →</a>
```

### Task Completion Notification
```python
TASK_COMPLETE_TEMPLATE = {
    "subject": "Task Complete: {{task_title}}",
    "body": """
Your task '{{task_title}}' has been completed by {{agent_name}}.

Summary: {{summary}}

View full results: {{results_url}}

Time taken: {{duration}}
Credits used: {{credits}}
"""
}
```

## Deliverability Best Practices
```python
DELIVERABILITY_CHECKLIST = {
    "authentication": ["SPF record set", "DKIM signed", "DMARC policy configured"],
    "list_hygiene": [
        "Verify emails before sending (use email validation API)",
        "Remove hard bounces immediately",
        "Suppress unsubscribes globally",
        "Remove inactive subscribers every 90 days",
    ],
    "content": [
        "Text:HTML ratio > 60:40",
        "Avoid spam trigger words (free, guarantee, click here, urgent)",
        "Include physical address in footer",
        "One-click unsubscribe required (Google/Yahoo 2024)",
        "Consistent from address and name",
    ],
    "sending": [
        "Warm up new IPs gradually (start with 100/day)",
        "Send at consistent times",
        "Keep bounce rate < 2%",
        "Keep spam complaint rate < 0.1%",
        "Monitor blacklists (MXToolbox)",
    ],
}
```

## Email Validation
```python
import re
import httpx

def is_valid_email_format(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

async def verify_email_deliverable(email: str) -> dict:
    # Use abstract API or similar
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://emailvalidation.abstractapi.com/v1/",
            params={"api_key": ABSTRACT_API_KEY, "email": email},
        )
        data = response.json()
        return {
            "deliverable": data.get("deliverability") == "DELIVERABLE",
            "is_business": not data.get("is_free_email_host", True),
            "is_disposable": data.get("is_disposable_email", {}).get("value", False),
        }
```

## Models to Use
- **Email copy writing**: `claude-sonnet-4-6` or `gpt-4o`
- **Subject line A/B variants**: `gpt-4o` (generate 10 at once)
- **Personalization at scale**: `gpt-4o-mini` (fast + cheap for bulk)
- **Deliverability analysis**: `gpt-4o`
