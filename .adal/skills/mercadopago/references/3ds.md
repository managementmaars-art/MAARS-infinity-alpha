# 3DS 2.0 Authentication

3D Secure (3DS 2.0) validates cardholder identity during purchase, reducing fraud and increasing approval rates.

## Benefits

- **Higher approval rates** - Authenticated transactions less likely to be declined
- **Liability shift** - Reduces chargeback risk for merchants
- **Buyer protection** - Reduces fraud risk for customers

## How It Works

1. Cardholder enters card details at checkout
2. Issuer displays authentication challenge (iframe/modal)
3. Cardholder verifies identity (OTP, biometric, etc.)
4. Authentication result returned to merchant
5. Payment proceeds based on result

## Integration Options

### Checkout API (Orders API)

```javascript
// Create order with 3DS
const response = await fetch('https://api.mercadopago.com/v1/orders', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer {access_token}',
    'Content-Type': 'application/json',
    'X-Idempotency-Key': '{unique_key}'
  },
  body: JSON.stringify({
    type: 'online',
    external_reference: 'order_123',
    total_amount: 150.00,
    config: {
      online: {
        transaction_security: {
          validation: 'on_fraud_risk',
          liability_shift: 'required'
        }
      }
    },
    payer: { email: 'buyer@example.com' },
    transactions: {
      payments: [{
        amount: 150.00,
        payment_method: {
          id: 'master',
          type: 'credit_card',
          token: '{card_token}',
          installments: 1
        }
      }]
    }
  })
});
```

### Checkout API (Payments API)

```javascript
// Create payment with 3DS
const payment = await mercadopago.payment.create({
  transaction_amount: 150.00,
  token: 'card_token',
  payment_method_id: 'visa',
  payer: { email: 'buyer@example.com' },
  three_d_secure_mode: 'optional'
}, { idempotencyKey: 'unique_key' });
```

### Checkout Bricks

3DS is handled automatically when enabled in initialization:

```javascript
const bricksBuilder = mp.bricks();

// With 3DS enabled (default for high-value transactions)
const cardPayment = bricksBuilder.create('cardPayment', 'cardPaymentBrick_container', {
  initialization: { /* ... */ },
  callbacks: { /* ... */ }
});
```

## Response Handling

### No Challenge Required

Transaction proceeds automatically:

```json
{
  "status": "approved",
  "status_detail": "accredited"
}
```

### Challenge Required

```json
{
  "status": "pending",
  "status_detail": "pending_challenge",
  "three_ds_info": {
    "external_resource_url": "https://acs.bank.com/challenge",
    "creq": "eyJ0aHJlZURTU2VydmVyVHJhbnNJRCI6..."
  }
}
```

### Display Challenge (iframe)

```javascript
function display3DSChallenge(payment) {
  const { three_ds_info } = payment;
  
  if (payment.status === 'pending' && 
      payment.status_detail === 'pending_challenge') {
    
    // Create iframe for challenge
    const iframe = document.createElement('iframe');
    iframe.id = '3ds-challenge';
    iframe.style.cssText = 'width:500px;height:600px;border:none;';
    document.body.appendChild(iframe);
    
    // Create form to post to ACS
    const form = iframe.contentWindow.document.createElement('form');
    form.method = 'post';
    form.action = three_ds_info.external_resource_url;
    
    const creqField = iframe.contentWindow.document.createElement('input');
    creqField.type = 'hidden';
    creqField.name = 'creq';
    creqField.value = three_ds_info.creq;
    
    form.appendChild(creqField);
    iframe.contentWindow.document.body.appendChild(form);
    form.submit();
  }
}

// Listen for challenge completion
window.addEventListener('message', (event) => {
  if (event.data.status === 'COMPLETE') {
    // Challenge finished - check payment status
    checkPaymentStatus();
  }
});
```

## 3DS Status Codes

| 3DS Status | Meaning |
|-------------|---------|
| `authenticated` | Authentication successful |
| `attempted` | Authentication attempted (partial liability) |
| `not_authenticated` | Authentication failed |
| `challenge` | Challenge displayed/required |

## Payment Status After 3DS

| Final Status | Status Detail | Meaning |
|--------------|---------------|---------|
| `approved` | `accredited` | Payment successful |
| `rejected` | `cc_rejected_3ds_challenge` | Challenge failed |
| `cancelled` | `expired` | Challenge timeout (40 min) |

## Testing 3DS

### Test Cards (MCO)

| Card | Challenge Flow |
|------|----------------|
| Mastercard 5254 1336 7440 3564 | Challenge required |
| Visa 4013 5406 8274 6260 | No challenge |

### Test Cardholder Names

| Name | Result |
|------|--------|
| `APRO-AUTH` | Approved, authenticated |
| `APRO-ATMT` | Approved, attempted |
| `OTHE-NAUT` | Rejected, not authenticated |
| `APRO-CHOK` | Challenge, then approved |
| `OTHE-CHNO` | Challenge, then rejected |

### Test Card Numbers (MCO)

```javascript
// Successful 3DS
const testCard = {
  number: '5254133674403564',  // Mastercard
  securityCode: '123',
  expirationDate: '11/30',
  cardholderName: 'APRO-CHOK'
};
```

## Requirements

1. **TLS 1.2+** - Required for production
2. **HTTPS** - Challenge URLs must be served over HTTPS
3. **Merchant category** - Some categories may have restrictions
4. **Acquirer support** - 3DS requires acquirer support

## When 3DS is Recommended

| Scenario | Recommendation |
|----------|---------------|
| High-value transactions | Enable |
| New customer cards | Enable |
| High fraud risk markets | Enable |
| Low-value transactions | Optional |
| Returning customer, known device | Optional |

## Best Practices

1. **Show loading state** - While challenge is in progress
2. **Handle timeout** - Challenge expires after 40 minutes
3. **Mobile-friendly** - Responsive iframe for challenge
4. **Clear messaging** - Explain 3DS to customers if prompted
5. **Fallback** - Have alternative payment methods available

## Next Steps

- [Payment flow](payment-flow.md)
- [Reduce rejections](errors.md)
- [Test integration](testing.md)
