# Security

Mercado Pago implements industry-standard security measures. Follow these best practices to protect your integration.

## Security Standards

### OAuth 2.0
Authorization protocol for secure API access without sharing credentials.

```javascript
// OAuth flow
const authUrl = 'https://auth.mercadopago.com/oauth/token';
const params = new URLSearchParams({
  grant_type: 'authorization_code',
  client_id: 'YOUR_CLIENT_ID',
  client_secret: 'YOUR_CLIENT_SECRET',
  code: authorizationCode,
  redirect_uri: 'YOUR_REDIRECT_URI'
});

const response = await fetch(authUrl, {
  method: 'POST',
  body: params
});
```

### PCI DSS Compliance
Mercado Pago is PCI DSS compliant. Never store card numbers.

### OWASP Guidelines
Follow OWASP security recommendations for web applications.

## Credential Security

### Never Expose Credentials

```javascript
// BAD - Credentials in frontend code
const accessToken = 'APP_USR-123456789';

// GOOD - Environment variables
const accessToken = process.env.MP_ACCESS_TOKEN;

// GOOD - Server-side only
app.post('/create-payment', (req, res) => {
  const accessToken = req.serverConfig.accessToken;
  // Use for API calls
});
```

### Send Token via Header

```bash
# Correct - Header
curl -H "Authorization: Bearer ACCESS_TOKEN" \
  https://api.mercadopago.com/v1/payments

# Wrong - Query parameter
curl "https://api.mercadopago.com/v1/payments?access_token=TOKEN"
```

### Rotate Credentials

```javascript
// Schedule credential rotation every 6 months
// Use Dashboard to generate new credentials
// Update environment
// Deploy with new credentials
// Revoke old credentials
```

## Card Data Security

### Tokenization Required

```javascript
// NEVER store card numbers
// ALWAYS tokenize first
const cardToken = await mp.getCardToken({
  cardNumber: '5254133674403564',
  cardholderName: 'TEST USER',
  expirationMonth: '11',
  expirationYear: '2026',
  securityCode: '123',
  identificationType: 'CC',
  identificationNumber: '123456789'
});

// Use token for payment
const payment = await mercadopago.payment.create({
  token: cardToken.id,
  // ... other fields
});
```

### Frontend Card Handling

```html
<!-- Use MercadoPago.js for card fields -->
<script src="https://sdk.mercadopago.com/js/v2"></script>

<div id="cardNumber"></div>
<div id="securityCode"></div>
<div id="cardExpiration"></div>
<div id="cardholderName"></div>

<script>
  const mp = new MercadoPago('PUBLIC_KEY');
  
  mp.cardNumber.create({
    id: 'cardNumber',
    placeholder: 'Card number'
  });
  
  // Get token when form submitted
  const cardToken = await mp.getCardToken(formData);
</script>
```

## Webhook Security

### Validate Signatures

```javascript
const crypto = require('crypto');

function validateWebhookSignature(req) {
  const signature = req.headers['x-signature'];
  const timestamp = req.headers['x-signature-date'];
  const webhookKey = process.env.MP_WEBHOOK_KEY;
  
  // Check timestamp (within 5 minutes)
  const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);
  if (parseInt(timestamp) < fiveMinutesAgo) {
    return false;
  }
  
  // Verify signature
  const data = timestamp + '.' + JSON.stringify(req.body);
  const expectedSignature = crypto
    .createHmac('sha256', webhookKey)
    .update(data)
    .digest('hex');
  
  return signature === expectedSignature;
}

app.post('/webhook', (req, res) => {
  if (!validateWebhookSignature(req)) {
    return res.status(401).send('Invalid signature');
  }
  // Process notification
  res.status(200).send('OK');
});
```

## HTTPS Requirements

- All production URLs must use HTTPS
- TLS 1.2+ required
- Valid SSL certificate required
- No self-signed certificates

## Input Validation

### Validate All Inputs

```javascript
function validatePaymentInput(data) {
  const errors = [];
  
  if (!data.transaction_amount || data.transaction_amount <= 0) {
    errors.push('Invalid amount');
  }
  
  if (!data.token) {
    errors.push('Card token required');
  }
  
  if (!data.payment_method_id) {
    errors.push('Payment method required');
  }
  
  if (!data.payer?.email || !isValidEmail(data.payer.email)) {
    errors.push('Valid email required');
  }
  
  return errors;
}
```

## Fraud Prevention

### Send Device Data

```javascript
// In frontend - SDK collects device data automatically
const deviceData = await mp.deviceProfiler.getDeviceData();

// Include in payment
const payment = await mercadopago.payment.create({
  transaction_amount: 150.00,
  token: cardToken,
  device_id: deviceData.id, // If using custom device profiling
  payer: { email: 'buyer@example.com' }
});
```

### Use 3DS for High-Value

```javascript
// Enable 3DS for high-value transactions
if (transactionAmount > 500) {
  paymentConfig.three_d_secure_mode = 'optional';
}
```

## Security Checklist

- [ ] Store credentials in environment variables
- [ ] Never expose Access Token in frontend
- [ ] Use HTTPS for all production URLs
- [ ] Validate all user inputs
- [ ] Implement webhook signature validation
- [ ] Use idempotency keys
- [ ] Log security events
- [ ] Rotate credentials periodically
- [ ] Tokenize all card data
- [ ] Enable 3DS for high-value transactions
- [ ] Implement rate limiting
- [ ] Sanitize log output

## Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per window
  message: 'Too many requests'
});

app.use('/api/', apiLimiter);
```

## Secure Headers

```javascript
app.use((req, res, next) => {
  res.setHeader('Strict-Transport-Security', 'max-age=31536000');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  next();
});
```

## Common Security Mistakes

| Mistake | Risk | Fix |
|---------|------|-----|
| Hardcoded credentials | Exposed in code | Use env variables |
| Credentials in URLs | Logged in server logs | Use headers |
| Storing card numbers | PCI violation | Always tokenize |
| No webhook validation | Fake notifications | Validate signatures |
| No input validation | Injection attacks | Sanitize inputs |
| HTTP webhook URL | Intercepted data | Use HTTPS |

## Reporting Security Issues

If you find a security vulnerability:
1. Do not disclose publicly
2. Contact Mercado Pago security team
3. Wait for acknowledgment
4. Follow responsible disclosure

## Next Steps

- [Authentication](authentication.md)
- [Webhooks](webhooks.md)
- [Error handling](errors.md)
- [3DS](3ds.md)
