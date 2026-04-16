# Error Handling

Comprehensive error codes and handling strategies for Mercado Pago integrations.

## Error Categories

| Category | Source | Example |
|----------|--------|---------|
| Card Token Errors | Client-side | Invalid card number |
| Payment Errors | Server-side | Insufficient funds |
| API Errors | Request validation | Missing parameters |
| Webhook Errors | Notification processing | Invalid signature |

## Card Token Errors

These occur when creating card tokens client-side.

| Code | status_detail | Description | Action |
|------|---------------|-------------|--------|
| 205 | - | Card number required | Prompt card number |
| 208 | - | Expiration month required | Prompt month |
| 209 | - | Expiration year required | Prompt year |
| 212 | - | Document type required | Prompt ID type |
| 213 | - | Document subtype required | Prompt ID number |
| 214 | - | Document number required | Prompt ID |
| 220 | - | Bank issuer required | Prompt bank |
| 221 | - | Cardholder name required | Prompt name |
| 224 | - | Security code required | Prompt CVV |
| E203 | - | Invalid security code | Check CVV format |
| E301 | - | Invalid card number | Check card number |
| 316 | - | Invalid cardholder name | Check name format |
| 322 | - | Invalid document type | Use correct type |
| 323 | - | Invalid document subtype | Check document |
| 324 | - | Invalid document number | Check number format |
| 325 | - | Invalid expiration month | Use 01-12 |
| 326 | - | Invalid expiration year | Use 4-digit year |

## Payment Creation Errors

These occur when creating payments via API.

| Code | status_detail | Description | Action |
|------|---------------|-------------|--------|
| 106 | - | Cannot operate between countries | Check payer/receiver locations |
| 109 | - | Invalid installments | Use valid installment count |
| 126 | - | Invalid payment state | Check payment status |
| 129 | - | Amount below minimum | Increase amount |
| 145 | - | Invalid users | Test/live user mismatch |
| 150 | - | Payer cannot pay | Check payer status |
| 151 | - | Payer cannot use method | Try different method |
| 160 | - | Collector cannot operate | Check collector status |
| 204 | - | Payment method unavailable | Try different method |
| 801 | - | Duplicate request | Use idempotency key |

## Payment Status Errors

### Rejection Reasons

| status_detail | Description | Recommended Action |
|---------------|-------------|-------------------|
| `cc_rejected_bad_filled_card_number` | Invalid card number | Ask for correct number |
| `cc_rejected_bad_filled_date` | Invalid expiry | Ask for correct date |
| `cc_rejected_bad_filled_security_code` | Invalid CVV | Ask for correct CVV |
| `cc_rejected_insufficient_amount` | Insufficient funds | Ask for different card |
| `cc_rejected_invalid_installments` | Invalid installments | Try different count |
| `cc_rejected_card_disabled` | Card disabled | Activate card with bank |
| `cc_rejected_call_for_authorize` | Requires authorization | Call bank to authorize |
| `cc_rejected_max_attempts` | Max attempts reached | Try tomorrow or different card |
| `cc_rejected_duplicated_payment` | Duplicate attempt | Use different payment |
| `cc_rejected_high_risk` | High risk flagged | Try different payment method |
| `cc_rejected_blacklist` | Blacklisted card | Use different card |
| `cc_rejected_other_reason` | Issuer rejected | Contact issuer |
| `bank_error` | Bank processing error | Retry later |
| `rejected_by_regulations` | Regulatory rejection | Cannot proceed |

## Handling Errors in Code

### Client-Side Error Handling

```javascript
// Using MercadoPago.js
const cardToken = await mp.getCardToken({
  cardNumber: '5254133674403564',
  cardholderName: 'TEST USER',
  expirationMonth: '11',
  expirationYear: '2026',
  securityCode: '123',
  identificationType: 'CC',
  identificationNumber: '123456789'
}).catch(error => {
  if (error.cause) {
    // Handle specific validation error
    console.log(error.cause.code); // e.g., '205'
  }
});
```

### Server-Side Error Handling

```javascript
try {
  const payment = await mercadopago.payment.create({
    transaction_amount: 150.00,
    token: cardToken,
    payment_method_id: 'mastercard',
    payer: { email: 'buyer@example.com' }
  });
  
  if (payment.status === 'rejected') {
    handleRejection(payment.status_detail);
  }
} catch (error) {
  if (error.status === 400) {
    // Bad request - check parameters
    console.log(error.response.details);
  }
}
```

### Payment Rejection Handler

```javascript
function handleRejection(statusDetail) {
  const messages = {
    'cc_rejected_bad_filled_card_number': 'Please check your card number',
    'cc_rejected_bad_filled_date': 'Please check your card expiry',
    'cc_rejected_bad_filled_security_code': 'Please check your CVV',
    'cc_rejected_insufficient_amount': 'Insufficient funds. Try another card.',
    'cc_rejected_card_disabled': 'Card disabled. Call your bank.',
    'cc_rejected_call_for_authorize': 'Please authorize with your bank.',
    'cc_rejected_max_attempts': 'Max attempts reached. Try tomorrow.',
    'cc_rejected_duplicated_payment': 'Payment already processed.',
    'cc_rejected_high_risk': 'Please try a different payment method.',
    'default': 'Payment declined. Please try again.'
  };
  
  return messages[statusDetail] || messages['default'];
}
```

## API Response Errors

### HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

### Error Response Format

```json
{
  "status": 400,
  "error": "bad_request",
  "message": "Invalid payment_method_id",
  "cause": [
    {
      "code": "126",
      "description": "The action is not valid for payment state"
    }
  ]
}
```

### Handling API Errors

```javascript
async function createPayment(paymentData) {
  try {
    const response = await fetch('https://api.mercadopago.com/v1/payments', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + accessToken,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(paymentData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      
      if (response.status === 401) {
        throw new Error('Invalid credentials');
      }
      
      if (response.status === 400) {
        const cause = error.cause[0];
        throw new Error(`Payment error: ${cause.description}`);
      }
      
      throw new Error('Payment failed');
    }
    
    return await response.json();
  } catch (err) {
    console.error('Payment error:', err.message);
    throw err;
  }
}
```

## Idempotency

Prevent duplicate payments using idempotency keys:

```javascript
const idempotencyKey = crypto.randomUUID();

const payment = await mercadopago.payment.create({
  transaction_amount: 150.00,
  token: cardToken,
  payment_method_id: 'visa',
  payer: { email: 'buyer@example.com' }
}, {
  idempotencyKey: idempotencyKey
});
```

## Retry Logic

```javascript
async function createPaymentWithRetry(data, maxRetries = 3) {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await createPayment(data);
    } catch (error) {
      lastError = error;
      
      // Only retry on transient errors
      if (!isTransientError(error)) {
        throw error;
      }
      
      // Exponential backoff
      await sleep(Math.pow(2, i) * 100);
    }
  }
  
  throw lastError;
}

function isTransientError(error) {
  const transientCodes = ['500', '503', 'ETIMEDOUT'];
  return transientCodes.includes(error.status);
}
```

## User-Facing Messages

Provide clear messages to users:

| Error | User Message |
|-------|--------------|
| Invalid card | "Please check your card details and try again." |
| Insufficient funds | "Insufficient funds. Please try a different card." |
| Expired card | "Card has expired. Please use a different card." |
| Bank declined | "Payment declined by your bank. Please contact them or try another method." |
| 3DS failed | "Verification failed. Please try again or use a different card." |
| Duplicate | "This payment was already processed." |

## Logging

Log errors for debugging:

```javascript
function logError(context, error) {
  console.error({
    timestamp: new Date().toISOString(),
    context: context,
    error: {
      message: error.message,
      code: error.code,
      status: error.status,
      stack: error.stack
    },
    request: {
      path: error.config?.url,
      method: error.config?.method
    }
  });
}
```

## Next Steps

- [Payment flow](payment-flow.md)
- [Webhooks](webhooks.md)
- [Security](security.md)
