# Refunds

Refunds return money to buyers for completed payments. Can be full or partial.

## Refund Types

| Type | Description |
|------|-------------|
| Full | Complete refund of transaction |
| Partial | Refund specific amount |
| Cancelled | Void pending payment before processing |

## Full Refund

```bash
curl -X POST https://api.mercadopago.com/v1/payments/{payment_id}/refunds \
  -H "Authorization: Bearer {access_token}"
```

### Response

```json
{
  "id": "refund_123456789",
  "payment_id": "payment_123456789",
  "amount": 150.00,
  "status": "approved",
  "date_created": "2024-01-20T10:30:00Z"
}
```

## Partial Refund

```bash
curl -X POST https://api.mercadopago.com/v1/payments/{payment_id}/refunds \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"amount": 50.00}'
```

## Multiple Partial Refunds

Can issue multiple partial refunds until total refunded equals payment amount.

```bash
# First partial refund
curl -X POST https://api.mercadopago.com/v1/payments/{payment_id}/refunds \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"amount": 25.00}'

# Second partial refund
curl -X POST https://api.mercadopago.com/v1/payments/{payment_id}/refunds \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"amount": 25.00}'
```

### Check Refunds on Payment

```bash
curl -X GET https://api.mercadopago.com/v1/payments/{payment_id}/refunds \
  -H "Authorization: Bearer {access_token}"
```

## Order Refunds

For orders, refund individual payments:

```bash
# Get order payments
curl -X GET https://api.mercadopago.com/v1/orders/{order_id} \
  -H "Authorization: Bearer {access_token}"

# Refund specific payment
curl -X POST https://api.mercadopago.com/v1/payments/{payment_id}/refunds \
  -H "Authorization: Bearer {access_token}"
```

## Subscription Cancellations

### Cancel Active Subscription

```bash
curl -X PUT https://api.mercadopago.com/v1/preapprovals/{subscription_id} \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "cancelled"}'
```

Note: Cancellation stops future billing but does not refund past payments.

### Refund Last Subscription Payment

```bash
# Find the last payment
curl -X GET "https://api.mercadopago.com/v1/preapprovals/{id}/payments" \
  -H "Authorization: Bearer {access_token}"

# Refund specific payment
curl -X POST https://api.mercadopago.com/v1/payments/{payment_id}/refunds \
  -H "Authorization: Bearer {access_token}"
```

## Refund Status

| Status | Description |
|--------|-------------|
| `pending` | Refund request received |
| `approved` | Refund processed |
| `rejected` | Refund rejected |
| `error` | Processing error |

## Refund via SDK

### Node.js

```javascript
const mercadopago = require('mercadopago');

mercadopago.configurations.setAccessToken(accessToken);

// Full refund
const refund = await mercadopago.refund.create({ payment_id: '123456789' });

// Partial refund
const refund = await mercadopago.refund.create({
  payment_id: '123456789',
  amount: 50.00
});
```

### Python

```python
import mercadopago

sdk = mercadopago.SDK(accessToken)

# Full refund
result = sdk.refund().create('123456789')

# Partial refund
result = sdk.refund().create('123456789', { 'amount': 50.00 })
```

### PHP

```php
$client = new \MercadoPago\Client\Refund\RefundClient();
$client->create($paymentId);

// Partial refund
$client->create($paymentId, ['amount' => 50.00]);
```

## Refund Timing

| Payment Method | Refund Time |
|----------------|-------------|
| Credit/Debit Card | 2-10 business days |
| Bank Transfer (PSE) | 1-5 business days |
| Cash (Efecty) | 1-3 business days |
| Wallet | Instant |

## Webhook Notifications

Subscribe to `topic_claims_integration_wh` for refund events:

```javascript
app.post('/webhook', (req, res) => {
  if (req.body.type === 'topic_claims_integration_wh') {
    const { id, topic } = req.body;
    
    if (topic === 'refund') {
      // Handle refund notification
      updateOrderStatus(req.body.data.id, 'refunded');
    }
  }
  res.status(200).send('OK');
});
```

## Cancellation vs Refund

| Action | Use When |
|--------|----------|
| **Cancellation** | Payment still processing, not yet captured |
| **Refund** | Payment already completed/captured |

### Cancel Pending Payment

```bash
curl -X PUT https://api.mercadopago.com/v1/payments/{payment_id} \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "cancelled"}'
```

Works only for payments with status `authorized` or `pending`.

## PSE Payment Refunds

For PSE bank transfers in Colombia:

```bash
curl -X POST https://api.mercadopago.com/v1/payments/{payment_id}/refunds \
  -H "Authorization: Bearer {access_token}"
```

PSE refunds typically take 1-5 business days.

## Error Codes

| Code | Description |
|------|-------------|
| `refund_not_possible` | Payment cannot be refunded (captured amount exceeded) |
| `refund_already_processed` | Refund already requested |
| `invalid_refund_amount` | Amount exceeds available |

## Best Practices

1. **Process refunds promptly** - Within 30 days recommended
2. **Communicate with buyers** - Email confirmation of refund
3. **Handle partial refunds carefully** - Track remaining refundable amount
4. **Test refund flow** - Use test credentials first
5. **Log all refund requests** - Audit trail for disputes

## Next Steps

- [Handle webhooks](webhooks.md)
- [Payment status](payment-status.md)
- [Error handling](errors.md)
