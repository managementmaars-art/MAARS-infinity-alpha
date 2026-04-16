# Payment Status Reference

## Payment Status Codes

Every payment generates a `status` and `status_detail` that indicates its current condition.

## Status Overview

| Status | Description |
|--------|-------------|
| `approved` | Payment was approved and credited |
| `pending` | Payment is awaiting completion |
| `in_process` | Payment is being processed |
| `rejected` | Payment was rejected |
| `cancelled` | Payment was cancelled |
| `refunded` | Payment was refunded |
| `charged_back` | Payment was charged back |

## Status Detail Codes

### Approved Payments

| status_detail | Description |
|---------------|-------------|
| `accredited` | Payment credited successfully |
| `partially_refunded` | Partial refund was processed |

### Pending Payments

| status_detail | Description |
|---------------|-------------|
| `pending_waiting_payment` | Awaiting payment from buyer |
| `pending_waiting_transfer` | Awaiting bank transfer completion |
| `pending_challenge` | Pending 3DS authentication |
| `pending_contingency` | Processing offline, check email in 2 business days |
| `pending_review_manual` | Manual review in progress |

### Rejected Payments

| status_detail | Description |
|---------------|-------------|
| `cc_rejected_bad_filled_card_number` | Check card number |
| `cc_rejected_bad_filled_date` | Check expiration date |
| `cc_rejected_bad_filled_security_code` | Check CVV |
| `cc_rejected_bad_filled_other` | Check card data |
| `cc_rejected_insufficient_amount` | Insufficient funds |
| `cc_rejected_invalid_installments` | Invalid installments number |
| `cc_rejected_card_disabled` | Card disabled, call issuer |
| `cc_rejected_call_for_authorize` | Must authorize payment |
| `cc_rejected_max_attempts` | Max attempts reached |
| `cc_rejected_duplicated_payment` | Duplicate payment attempt |
| `cc_rejected_high_risk` | High risk transaction |
| `cc_rejected_blacklist` | Blacklisted card |
| `cc_rejected_other_reason` | Issuer rejected |
| `cc_rejected_3ds_challenge` | 3DS challenge failed |
| `cc_rejected_3ds_mandatory` | 3DS required but not performed |
| `bank_error` | Bank processing error |
| `rejected_by_bank` | Bank rejected transaction |
| `rejected_by_regulations` | Rejected by regulations |
| `rejected_insufficient_data` | Missing required data |
| `cc_amount_rate_limit_exceeded` | Rate limit exceeded |

### Cancelled Payments

| status_detail | Description |
|---------------|-------------|
| `expired` | Payment expired (30 days pending) |
| `by_collector` | Cancelled by seller |
| `by_payer` | Cancelled by buyer |

### Charged Back Payments

| status_detail | Description |
|---------------|-------------|
| `in_process` | Chargeback under review |
| `settled` | Funds retained after chargeback |
| `reimbursed` | Funds reimbursed to buyer |

## Handling Payment Status

### Checking Payment Status

```bash
curl -X GET https://api.mercadopago.com/v1/payments/{payment_id} \
  -H "Authorization: Bearer {access_token}"
```

### Status Response Example

```json
{
  "id": 123456789,
  "status": "approved",
  "status_detail": "accredited",
  "payment_method_id": "visa",
  "payment_type_id": "credit_card",
  "transaction_amount": 150.00,
  "currency": "COP"
}
```

### Webhook Notification

When status changes, webhook sends:

```json
{
  "action": "payment.updated",
  "api_version": "v1",
  "data": {
    "id": "123456789"
  },
  "date_created": "2024-01-15T10:00:00Z",
  "id": 123456789,
  "live_mode": true,
  "type": "payment",
  "user_id": "123456789"
}
```

## Next Steps

- [Process refunds](refunds.md)
- [Set up webhooks](webhooks.md)
- [Handle errors](errors.md)
