# Approval and Audit Baseline

## High-Risk Action Classes

Require approval for:

- payment/refund/price/contract changes
- delete or bulk-mutation operations
- external broadcast (email, announcement, social)
- production config change or rollback
- permission escalation

## Approval Modes

## Blocking

- Agent generates approval card.
- Execution is blocked until human approval is received.

## Queue-Based

- Agent pushes approval request into a queue/workflow system.
- Execution continues only from approval callback/webhook.

## Approval Schema

```json
{
  "approval_id": "apr_...",
  "action": "refund_order",
  "target": {"type":"order", "id":"ord_123"},
  "risk_level": "high",
  "requested_by": "agent:ops-assistant",
  "approvers": ["user:finance_manager"],
  "expires_at": "2026-02-25T12:00:00Z",
  "status": "pending"
}
```

## Audit Schema

```json
{
  "event_id": "evt_...",
  "timestamp": "2026-02-24T13:00:00Z",
  "requested_by": "agent:ops-assistant",
  "approved_by": "user:finance_manager",
  "action": "refund_order",
  "target": {"type":"order", "id":"ord_123"},
  "before": {"status":"paid"},
  "after": {"status":"refunded"},
  "result": "success",
  "idempotency_key": "sha256(...)",
  "trace_id": "trace_..."
}
```

## Failure Handling

- Retry only idempotent operations.
- On permanent failure, emit notification with remediation owner.
- Preserve failed action payload and error class for incident review.
