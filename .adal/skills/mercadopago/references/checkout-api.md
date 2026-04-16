# Checkout API

Full API control for custom checkout experiences. Highest customization but requires more development effort. Handle card data directly or use tokenization.

## When to Use

- Full control over UI/UX needed
- Custom checkout flow
- Mobile app integration
- Complex business logic

---

## Integration Options

| Option | PCI Level | Complexity |
|--------|-----------|------------|
| Core Methods (Secure Fields) | SAQ A | High |
| Cardform | SAQ A | Medium |

---

## Secure Fields (Core Methods)

Card data is captured in MercadoPago-hosted iframes - you never handle raw card data.

### 1. Add HTML Containers
```html
<div id="cardNumber"></div>
<div id="expirationDate"></div>
<div id="securityCode"></div>
<div id="cardholderName"></div>
<select id="docType"></select>
<input id="docNumber"></input>
```

### 2. Create Fields
```javascript
const cardNumber = mp.fields.create('cardNumber', {
  placeholder: '1234 1234 1234 1234'
}).mount('cardNumber');

const expirationDate = mp.fields.create('expirationDate', {
  placeholder: 'MM/YY'
}).mount('expirationDate');

const securityCode = mp.fields.create('securityCode', {
  placeholder: '123'
}).mount('securityCode');
```

### 3. Listen for BIN Changes
```javascript
cardNumber.on('binChange', async (data) => {
  const { bin } = data;
  if (bin.length === 6) {
    const methods = await mp.getPaymentMethods({ bin });
    const issuers = await mp.getIssuers({
      paymentMethodId: methods.results[0].id,
      bin
    });
  }
});
```

### 4. Create Card Token
```javascript
const token = await mp.fields.createCardToken({
  cardholderName: document.getElementById('cardholderName').value,
  identificationType: document.getElementById('docType').value,
  identificationNumber: document.getElementById('docNumber').value,
});
// token.id is the card token to send to backend
```

### 5. Send to Backend
```javascript
fetch('/process_payment', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    token: token.id,
    transactionAmount: 100000,
    paymentMethodId: 'visa',
    payer: { email: 'buyer@email.com' }
  })
});
```

---

## Cardform (Legacy)

Deprecated - use Secure Fields instead.

---

## Create Payment (Backend)

```javascript
const payment = await payments.create({
  transaction_amount: 100000,
  token: 'CARD_TOKEN_FROM_FRONTEND',
  payment_method_id: 'visa',
  payer: {
    email: 'buyer@email.com',
    identification: {
      type: 'CC',
      number: '123456789'
    }
  },
  installments: 1,
  description: 'Product description',
  notification_url: 'https://yoursite.com/webhook'
});
```

---

## Payment Response

```javascript
{
  id: 1234567890,
  status: 'approved',        // or 'pending', 'rejected'
  status_detail: 'accredited', // or 'pending_waiting_payment', etc.
  transaction_amount: 100000,
  payment_method_id: 'visa',
  payer: { email: 'buyer@email.com' }
}
```

---

## Idempotency

Always use idempotency keys to prevent duplicate payments:

```javascript
const requestOptions = {
  idempotencyKey: crypto.randomUUID()
};

payments.create(paymentData, requestOptions);
```
