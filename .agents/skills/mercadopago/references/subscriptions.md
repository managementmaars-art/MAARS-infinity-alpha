# Subscriptions

Subscriptions enable recurring payments for products or services with automatic billing.

## Subscription Types

### With Associated Plan
Same subscription reused for multiple payers. Ideal for:
- Monthly/annual memberships
- Tiered pricing plans
- Product subscriptions

### Without Associated Plan
Custom subscription per payer. Ideal for:
- Variable amounts
- Custom frequencies
- Donor-specific billing

## Available Payment Methods by Country

| Country | Credit | Debit | Cash | Bank Transfer |
|---------|--------|-------|------|---------------|
| MCO | Yes | Yes | Efecty | PSE |
| MLA | Yes | Yes | Rapipago, Pago Fácil | - |
| MLB | Yes | - | Boleto, Pix | Pix |
| MLM | Yes | Yes | OXXO, Paycash | SPEI |
| MLC | Yes | Yes | - | - |
| MPE | Yes | Yes | PagoEfectivo | - |
| MLU | Yes | Yes | Abitab, Redpagos | - |

## Creating a Plan

```bash
curl -X POST https://api.mercadopago.com/v1/preapproval_plan \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Premium Plan",
    "billing_frequency": "monthly",
    "payment_types_enabled": ["credit_card"],
    "accepted_payment_methods": ["visa", "mastercard"],
    "auto_recurring": {
      "frequency": 1,
      "frequency_type": "months",
      "transaction_amount": 29.99,
      "currency_id": "COP"
    },
    "external_reference": "plan_001"
  }'
```

### Plan Response

```json
{
  "id": "plan_123456789",
  "description": "Premium Plan",
  "billing_frequency": "monthly",
  "auto_recurring": {
    "transaction_amount": 29.99,
    "currency_id": "COP"
  },
  "status": "active"
}
```

## Creating a Subscription

### With Plan

```bash
curl -X POST https://api.mercadopago.com/v1/preapprovals \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "plan_123456789",
    "payer": {
      "email": "subscriber@example.com"
    },
    "external_reference": "subscription_001"
  }'
```

### Without Plan (Custom Amount)

```bash
curl -X POST https://api.mercadopago.com/v1/preapprovals \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_recurring": {
      "frequency": 1,
      "frequency_type": "months",
      "transaction_amount": 50.00,
      "currency_id": "COP"
    },
    "payer": {
      "email": "subscriber@example.com"
    },
    "description": "Donation",
    "external_reference": "donation_001"
  }'
```

## Subscription Response

```json
{
  "id": "preapproval_123456789",
  "plan_id": "plan_123456789",
  "payer": {
    "email": "subscriber@example.com"
  },
  "status": "authorized",
  "auto_recurring": {
    "transaction_amount": 29.99
  },
  "start_date": "2024-02-01T00:00:00Z",
  "next_payment_date": "2024-03-01T00:00:00Z"
}
```

## Subscription Status

| Status | Description |
|--------|-------------|
| `authorized` | Active and processing |
| `paused` | Subscription paused |
| `cancelled` | Subscription cancelled |
| `expired` | Subscription expired |
| `pending` | Awaiting first payment |

## Managing Subscriptions

### Pause Subscription

```bash
curl -X PUT https://api.mercadopago.com/v1/preapprovals/{id} \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "paused"}'
```

### Cancel Subscription

```bash
curl -X PUT https://api.mercadopago.com/v1/preapprovals/{id} \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "cancelled"}'
```

### Update Amount

```bash
curl -X PUT https://api.mercadopago.com/v1/preapprovals/{id} \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_recurring": {
      "transaction_amount": 39.99,
      "currency_id": "COP"
    }
  }'
```

### Change Payment Method

```bash
curl -X PUT https://api.mercadopago.com/v1/preapprovals/{id} \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type": application/json" \
  -d '{
    "card_token_id": "new_card_token"
  }'
```

## Free Trial

```bash
curl -X POST https://api.mercadopago.com/v1/preapproval_plan/{plan_id} \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "free_trial": {
      "frequency": 1,
      "frequency_type": "months"
    }
  }'
```

## Webhook Notifications

Subscribe to `subscription_authorized_payment` topic:

```javascript
// Handle subscription payment
app.post('/webhook', (req, res) => {
  if (req.body.type === 'subscription_authorized_payment') {
    const { id, status, preapproval_id } = req.body.data;
    
    if (status === 'authorized') {
      // Payment successful - fulfill service
      activateMember(preapproval_id);
    }
  }
  res.status(200).send('OK');
});
```

## Searching Subscriptions

```bash
curl -X GET "https://api.mercadopago.com/v1/preapprovals/search?status=authorized" \
  -H "Authorization: Bearer {access_token}"
```

## Use Cases

### Membership Sites
```javascript
// Create plan for monthly membership
const plan = await mercadopago.preapprovalPlan.create({
  description: "Gold Membership",
  billing_frequency: "monthly",
  auto_recurring: {
    frequency: 1,
    frequency_type: "months",
    transaction_amount: 29.99,
    currency_id: "COP"
  }
});
```

### Donations
```javascript
// Open-ended donation
const subscription = await mercadopago.preapproval.create({
  auto_recurring: {
    frequency: 1,
    frequency_type: "months",
    transaction_amount: 0,  // Payer chooses
    free_recurrence: true
  },
  payer: { email: "donor@example.com" },
  description: "Monthly Donation"
});
```

### Usage-Based Billing
```javascript
// Custom amount per billing period
const subscription = await mercadopago.preapproval.create({
  auto_recurring: {
    frequency: 1,
    frequency_type: "months",
    transaction_amount: 0,
    currency_id: "COP"
  },
  payer: { email: "customer@example.com" },
  description: "Usage-based Service"
});
```

## Best Practices

1. **Clear cancellation policy** - Easy to cancel subscriptions
2. **Notification emails** - Before renewal, after payment
3. **Multiple payment methods** - Offer alternatives for failures
4. **Retry logic** - Automatic retry on failed payments
5. **Proration** - Handle mid-cycle plan changes

## Next Steps

- [Set up webhooks](webhooks.md)
- [Process refunds](refunds.md)
- [Test payments](testing.md)
