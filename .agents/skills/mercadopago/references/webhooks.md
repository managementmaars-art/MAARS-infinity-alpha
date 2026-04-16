# Webhooks

Webhooks notify your backend when payment events occur. Required for production integrations.

## Webhook vs IPN

| Feature | Webhooks | IPN |
|---------|----------|-----|
| Security | Signature validation | No validation |
| Reliability | Retry mechanism | Basic |
| Recommendation | **Preferred** | Legacy, deprecated |

## Topic Types

| Topic | Events | Products |
|-------|--------|----------|
| `payment` | Payment created/updated | Checkout Pro, Checkout Bricks, Checkout API |
| `order` | Order status changes | Checkout API, QR Code |
| `subscription_authorized_payment` | Subscription recurring payment | Subscriptions |
| `subscription_preapproval` | Subscription linking | Subscriptions |
| `subscription_preapproval_plan` | Plan changes | Subscriptions |
| `mp-connect` | OAuth linking/unlinking | All OAuth products |
| `wallet_connect` | Wallet transactions | Wallet Connect |
| `stop_delivery_op_wh` | Fraud alerts | Checkout Pro, Checkout API |
| `topic_claims_integration_wh` | Refunds and claims | All products |
| `topic_card_id_wh` | Card updates | Checkout Pro, Checkout API |
| `topic_merchant_order_wh` | Commercial orders | Checkout Pro |
| `topic_chargebacks_wh` | Chargebacks | Checkout Pro, Checkout API |
| `point_integration_wh` | Point device events | Mercado Pago Point |

## Configuration

### Via Dashboard

1. Go to [Developer Dashboard](https://mercadopago.com/developers/panel/app)
2. Select your application
3. Go to **Notifications** section
4. Enter your callback URL (HTTPS required)
5. Select topics to subscribe

### Via API (MCP Tool)

```javascript
// Use save_webhook MCP tool
save_webhook({
  callback: "https://yourdomain.com/webhook",
  topics: ["payment"]
})
```

### Manual API Setup

```bash
curl -X POST https://api.mercadopago.com/v1/webhooks \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourdomain.com/webhook",
    "webhook_events": ["payment.created", "payment.updated"]
  }'
```

## Signature Validation

Validate that notifications come from Mercado Pago:

```javascript
const crypto = require('crypto');

function validateSignature(req, webhookKey) {
  const signature = req.get('x-signature');
  const timestamp = req.get('x-signature-date');
  
  const data = timestamp + '.' + JSON.stringify(req.body);
  const expectedSignature = crypto
    .createHmac('sha256', webhookKey)
    .update(data)
    .digest('hex');
  
  return signature === expectedSignature;
}
```

## Handling Notifications

### Webhook Handler Example

```javascript
app.post('/webhook', (req, res) => {
  const { type, data, date_created } = req.body;
  
  if (type === 'payment') {
    const paymentId = data.id;
    
    // Process payment status update
    getPaymentStatus(paymentId).then(payment => {
      if (payment.status === 'approved') {
        // Fulfill order
        fulfillOrder(payment.external_reference);
      }
    });
  }
  
  // Always respond 200 quickly
  res.status(200).send('OK');
});
```

### Idempotency

Handle duplicate notifications gracefully:

```javascript
const processedPayments = new Set();

async function handlePaymentNotification(payment) {
  if (processedPayments.has(payment.id)) {
    return; // Already processed
  }
  
  // Process payment...
  processedPayments.add(payment.id);
}
```

## Testing Webhooks

### Simulate Webhook (MCP)

```javascript
// Use simulate_webhook MCP tool
simulate_webhook({
  topic: "payment",
  resource_id: "123456789",
  callback_env_production: false
})
```

### Local Testing

Use tools like ngrok for local development:

```bash
ngrok http 3000
# Set webhook URL to https://{your-ngrok-id}.ngrok.io/webhook
```

## Troubleshooting

### Webhook Not Received

1. Verify URL is HTTPS (HTTP not supported)
2. Check server responds with 200 within 30 seconds
3. Ensure firewall allows incoming from Mercado Pago IPs
4. Check application has correct topics enabled

### Duplicate Notifications

Implement idempotency keys or deduplication logic.

### Signature Validation Fails

- Ensure webhook key matches exactly
- Verify timestamp is still recent (within 5 minutes)
- Check JSON stringification matches signature calculation

## Best Practices

1. **Respond quickly** - Return 200 within 30 seconds, process async
2. **Use HTTPS** - Required for webhook URLs
3. **Implement idempotency** - Handle duplicate notifications
4. **Validate signatures** - Verify webhook authenticity
5. **Log all notifications** - For debugging and auditing
6. **Process async** - Don't block the webhook handler

## Next Steps

- [Payment status codes](payment-status.md)
- [Error handling](errors.md)
- [Go to production checklist](testing.md)
