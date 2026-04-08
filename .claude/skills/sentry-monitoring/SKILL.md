---
name: sentry-monitoring
description: Sentry error tracking and performance monitoring including Python/JS SDK setup, custom instrumentation, alerting, and source maps.
---

# Sentry Monitoring

## Overview

Sentry provides real-time error tracking, performance monitoring, session replay, and alerting. It captures unhandled exceptions, traces slow transactions, and helps reproduce issues with full context.

## Python SDK Setup

```python
# pip install sentry-sdk[fastapi]
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "development"),
    release=os.getenv("SENTRY_RELEASE", "unknown"),
    traces_sample_rate=1.0 if os.getenv("ENVIRONMENT") == "development" else 0.1,
    profiles_sample_rate=0.1,      # Profiling (CPU/memory)
    send_default_pii=False,         # Don't send PII by default
    integrations=[
        FastApiIntegration(transaction_style="endpoint"),
        SqlalchemyIntegration(),
        RedisIntegration(),
        CeleryIntegration(monitor_beat_tasks=True),
    ],
    before_send=filter_sensitive_events,
    before_send_transaction=filter_health_checks,
    ignore_errors=[KeyboardInterrupt, SystemExit],
)

def filter_sensitive_events(event, hint):
    """Strip sensitive data before sending to Sentry."""
    if "request" in event:
        event["request"].pop("cookies", None)
        if "headers" in event["request"]:
            event["request"]["headers"].pop("Authorization", None)
    return event

def filter_health_checks(event, hint):
    """Don't trace health check endpoints."""
    if event.get("transaction") in ["/health", "/ping", "/metrics"]:
        return None
    return event
```

## JavaScript/TypeScript SDK

```typescript
// app/sentry.ts (Next.js)
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.NEXT_PUBLIC_SENTRY_RELEASE,

  // Performance
  tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,
  profilesSampleRate: 0.1,

  // Session Replay
  replaysSessionSampleRate: 0.05,
  replaysOnErrorSampleRate: 1.0,   // Always replay on error

  integrations: [
    Sentry.replayIntegration({
      maskAllText: true,             // Mask all text for PII
      blockAllMedia: false,
    }),
    Sentry.browserTracingIntegration(),
    Sentry.feedbackIntegration({    // User feedback widget
      colorScheme: "auto",
    }),
  ],

  beforeSend(event, hint) {
    // Don't send errors from browser extensions
    if (event.exception?.values?.[0]?.stacktrace?.frames?.some(
      (f) => f.filename?.includes("chrome-extension://")
    )) {
      return null;
    }
    return event;
  },

  // Ignore common noisy errors
  ignoreErrors: [
    "ResizeObserver loop limit exceeded",
    "Non-Error promise rejection captured",
    /^NetworkError/,
  ],
});
```

## Custom Error Capture & Context

```python
import sentry_sdk
from sentry_sdk import capture_exception, capture_message, set_user, set_tag

# Set user context (call after authentication)
def set_sentry_user(user):
    set_user({
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
    })

# Capture exception with extra context
try:
    result = process_payment(order)
except PaymentError as e:
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("payment.provider", "stripe")
        scope.set_tag("order.id", order.id)
        scope.set_context("order", {
            "id": order.id,
            "amount": float(order.amount),
            "currency": order.currency,
            "items": len(order.items),
        })
        scope.set_level("error")
        capture_exception(e)
    raise

# Breadcrumbs for tracing user journey
sentry_sdk.add_breadcrumb(
    category="auth",
    message="User logged in",
    level="info",
    data={"method": "oauth", "provider": "google"},
)

# Manual message capture
capture_message("Quota limit approaching", level="warning")
```

## Performance Monitoring & Custom Spans

```python
import sentry_sdk

# Manual transaction
with sentry_sdk.start_transaction(op="task", name="process-batch") as transaction:
    transaction.set_tag("batch.size", len(items))

    for item in items:
        with transaction.start_child(op="db.query", description="fetch item") as span:
            span.set_data("item.id", item.id)
            result = db.fetch(item.id)

        with transaction.start_child(op="http.client", description="call external API") as span:
            response = await external_api.call(result)
            span.set_http_status(response.status_code)

# Decorator for tracing functions
@sentry_sdk.trace
def expensive_operation(data):
    # This function will appear as a span in traces
    return transform(data)
```

```typescript
// JavaScript performance monitoring
import * as Sentry from "@sentry/nextjs";

// Wrap async operations
async function fetchUserData(userId: string) {
  return Sentry.startSpan(
    { op: "db.query", name: "fetch-user" },
    async (span) => {
      span.setAttribute("user.id", userId);
      const user = await db.users.findUnique({ where: { id: userId } });
      span.setAttribute("db.rows", user ? 1 : 0);
      return user;
    }
  );
}

// Custom metrics
Sentry.metrics.increment("api.requests", 1, { tags: { endpoint: "/users" } });
Sentry.metrics.distribution("api.response_time", responseTimeMs, {
  unit: "millisecond",
  tags: { status: "200" },
});
Sentry.metrics.gauge("queue.depth", queueDepth);
```

## Cron Job Monitoring

```python
# Monitor scheduled tasks with Sentry Crons
import sentry_sdk

@sentry_sdk.monitor(monitor_slug="daily-report")
def send_daily_report():
    """This function is automatically monitored for failures and timing."""
    generate_report()
    send_email()

# Manual check-in pattern
monitor_id = sentry_sdk.capture_checkin(
    monitor_slug="weekly-cleanup",
    status="in_progress",
    monitor_config={
        "schedule": {"type": "crontab", "value": "0 0 * * 0"},
        "checkin_margin": 5,      # Minutes
        "max_runtime": 30,        # Minutes
        "failure_issue_threshold": 2,
    }
)
try:
    run_cleanup()
    sentry_sdk.capture_checkin(monitor_slug="weekly-cleanup", status="ok", check_in_id=monitor_id)
except Exception as e:
    sentry_sdk.capture_checkin(monitor_slug="weekly-cleanup", status="error", check_in_id=monitor_id)
    raise
```

## Source Maps (Next.js / Vite)

```javascript
// next.config.js
const { withSentryConfig } = require("@sentry/nextjs");

module.exports = withSentryConfig(nextConfig, {
  org: "your-org",
  project: "your-project",
  authToken: process.env.SENTRY_AUTH_TOKEN,
  silent: true,
  widenClientFileUpload: true,
  hideSourceMaps: true,           // Hide from browser, still used by Sentry
  disableLogger: true,
  automaticVercelMonitors: true,
});
```

```yaml
# CI/CD source map upload
- name: Upload Sentry source maps
  run: |
    npx @sentry/cli releases new $RELEASE_VERSION
    npx @sentry/cli releases files $RELEASE_VERSION upload-sourcemaps ./dist
    npx @sentry/cli releases finalize $RELEASE_VERSION
    npx @sentry/cli releases deploys $RELEASE_VERSION new -e production
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: your-org
    SENTRY_PROJECT: your-project
    RELEASE_VERSION: ${{ github.sha }}
```

## Alert Rules via API

```python
# Configure alerts programmatically
import httpx

SENTRY_AUTH_TOKEN = os.getenv("SENTRY_AUTH_TOKEN")
ORG = "your-org"
PROJECT = "your-project"

async def create_alert_rule():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://sentry.io/api/0/projects/{ORG}/{PROJECT}/alert-rules/",
            headers={"Authorization": f"Bearer {SENTRY_AUTH_TOKEN}"},
            json={
                "name": "High Error Rate",
                "aggregate": "count()",
                "query": "level:error",
                "timeWindow": 5,
                "thresholdType": 0,   # Above threshold
                "resolveThreshold": 10,
                "triggers": [
                    {
                        "label": "critical",
                        "alertThreshold": 100,
                        "actions": [
                            {"type": "slack", "targetType": "specific", "targetIdentifier": "#alerts"},
                            {"type": "pagerduty", "targetType": "specific"},
                        ],
                    }
                ],
            }
        )
        return response.json()
```

## Key Patterns

- **Sample rates**: Use 1.0 in dev, 0.1-0.2 in production to control volume
- **`before_send` hook**: Strip PII and filter noisy errors before they reach Sentry
- **Breadcrumbs**: Add manual breadcrumbs at key points to reconstruct user journey
- **Release tracking**: Tag releases for before/after regression comparisons
- **Source maps**: Always upload for readable stack traces in production
- **Cron monitoring**: Use `@sentry_sdk.monitor` to detect silent job failures

## Models to Use

- **claude-opus-4-5**: Alert strategy design, custom integrations, sampling configuration
- **claude-sonnet-4-5**: SDK setup, custom instrumentation, source map configuration
- **claude-haiku-3-5**: Simple error capture, breadcrumb additions
