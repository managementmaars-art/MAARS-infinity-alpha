# Testing

Mercado Pago provides test credentials, test cards, and test users for integration testing.

## Test Credentials

### Getting Test Credentials

1. Go to [Developer Dashboard](https://mercadopago.com/developers/panel/app)
2. Select your application
3. Go to **Testing > Test credentials**
4. Copy Public Key and Access Token

### Using Test Credentials

```javascript
// Set test credentials
mercadopago.configure({
  access_token: 'TEST_ACCESS_TOKEN',
  client_id: 'TEST_CLIENT_ID',
  client_secret: 'TEST_CLIENT_SECRET'
});
```

## Test Cards (MCO - Colombia)

### Card Numbers

| Card Type | Flag | Number | CVV | Expiry |
|-----------|------|--------|-----|--------|
| Credit | Mastercard | 5254 1336 7440 3564 | 123 | 11/30 |
| Credit | Visa | 4013 5406 8274 6260 | 123 | 11/30 |
| Credit | American Express | 3743 781877 55283 | 1234 | 11/30 |
| Debit | Visa | 4915 1120 5524 6507 | 123 | 11/30 |

### Cardholder Names for Status Simulation

| Name | Result |
|------|--------|
| `APRO` | Approved payment |
| `OTHE` | Declined - general error |
| `CONT` | Pending payment |
| `CALL` | Declined - call issuer |
| `FUND` | Declined - insufficient funds |
| `SECU` | Declined - invalid security code |
| `EXPI` | Declined - expired card |
| `FORM` | Declined - form error |
| `CARD` | Rejected - missing card number |
| `INST` | Rejected - invalid installments |
| `DUPL` | Rejected - duplicate payment |
| `LOCK` | Rejected - disabled card |
| `CTNA` | Rejected - card type not allowed |
| `ATTE` | Rejected - exceeded attempts |
| `BLAC` | Rejected - blacklisted |
| `UNSU` | Not supported |
| `TEST` | Apply amount rules |

### Test Document Numbers (MCO)

For Colombia, use any number like `123456789`.

## Testing Example

### Create Test Payment

```javascript
const payment = await mercadopago.payment.create({
  transaction_amount: 150.00,
  token: 'test_card_token',
  payment_method_id: 'mastercard',
  payer: {
    email: 'test_buyer@example.com',
    identification: {
      type: 'CC',
      number: '123456789'
    }
  },
  external_reference: 'test_order_001'
});

console.log(payment.status); // 'approved' if cardholder name is 'APRO'
```

### Test Card Tokenization

```javascript
// Using MercadoPago.js in browser
const cardData = {
  cardNumber: '5254133674403564',
  cardholderName: 'APRO',
  expirationMonth: '11',
  expirationYear: '2026',
  securityCode: '123',
  identificationType: 'CC',
  identificationNumber: '123456789'
};

// Get card token
const cardToken = await mp.getCardToken(cardData);

// Use cardToken in payment creation
```

## Test Users

### Create Test User (MCP Tool)

```javascript
// Use create_test_user MCP tool
create_test_user({
  site_id: 'MCO',
  description: 'Test Seller',
  profile: 'seller'
})
```

### Manual Creation

```bash
curl -X POST https://api.mercadopago.com/v1/test/users \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "MCO",
    "description": "Test Seller"
  }'
```

### Test User Types

| Profile | Description |
|---------|-------------|
| `seller` | Receives payments |
| `buyer` | Makes payments |
| `integrator` | For testing integrations |

## Testing Webhooks

### Local Testing with ngrok

```bash
# Start local server
ngrok http 3000

# Configure webhook URL to: https://{ngrok-id}.ngrok.io/webhook
```

### Simulate Webhook (MCP)

```javascript
// Use simulate_webhook MCP tool
simulate_webhook({
  topic: 'payment',
  resource_id: '123456789',
  callback_env_production: false
})
```

## Sandbox Environment

Test environment URLs:

| Environment | Base URL |
|-------------|----------|
| Sandbox | https://api.mercadopago.com |
| Production | https://api.mercadopago.com |

Test mode is enabled by using test credentials. Switch to production credentials before going live.

## Testing Checklist

- [ ] Create payment with approved card
- [ ] Create payment with declined card (various reasons)
- [ ] Test webhook notifications
- [ ] Test refund flow (full and partial)
- [ ] Test subscription creation and cancellation
- [ ] Test 3DS flow if applicable
- [ ] Verify error handling
- [ ] Test mobile responsiveness

## Testing Specific Scenarios

### Test PSE (Bank Transfer)

PSE doesn't have sandbox test cards. Use cash methods for testing.

### Test Cash Payments (Efecty)

```javascript
const payment = await mercadopago.payment.create({
  transaction_amount: 150.00,
  payment_method_id: 'efecty',
  payer: {
    email: 'test@example.com',
    identification: {
      type: 'CC',
      number: '123456789'
    }
  },
  external_reference: 'test_order_001'
});

// Check for 'pending' status and collect URL
console.log(payment.status); // 'pending'
console.log(payment.transaction_details.external_resource_url);
```

### Test Installments

```javascript
// Test different installment options
for (let i = 1; i <= 12; i++) {
  const payment = await mercadopago.payment.create({
    transaction_amount: 150.00,
    token: cardToken,
    payment_method_id: 'visa',
    installments: i,
    payer: { email: 'test@example.com' }
  });
  console.log(`Installments ${i}:`, payment.status);
}
```

## Going to Production

1. **Replace credentials** - Use production access token
2. **Update URLs** - Remove sandbox references
3. **Enable 3DS** - If applicable for your use case
4. **Test with real cards** - Small amounts first
5. **Monitor transactions** - Check webhook delivery

### Production Credentials

1. Go to Developer Dashboard
2. Select application
3. Go to **Production > Production credentials**
4. Activate if needed (complete business profile)
5. Copy credentials

## Common Testing Issues

| Issue | Solution |
|-------|----------|
| 404 on test endpoint | Check access token is correct |
| Webhook not received | Verify HTTPS URL, check firewall |
| Test card declined | Verify card number and CVV |
| Amount mismatch | Check currency_id matches |

## Next Steps

- [Authentication](authentication.md)
- [Payment flow](payment-flow.md)
- [Error handling](errors.md)
