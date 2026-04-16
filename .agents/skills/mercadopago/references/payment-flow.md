# Payment Flow

Complete payment processing flow from start to finish.

---

## Flow Diagram

```
Frontend                    Backend                    MercadoPago
   |                          |                            |
   |-- 1. Collect card data ->|                            |
   |                          |-- 2. Create payment ------>|
   |                          |                            |
   |                          |<--- 3. Payment response ----|
   |                          |                            |
|<-- 4. Show result          |                            |
   |                          |                            |
   |                          |<--- 5. Webhook notification|
```

---

## Step 1: Collect Payment Data (Frontend)

### Using Checkout Bricks
```javascript
const bricksBuilder = mp.bricks();
const paymentBrick = await bricksBuilder.create('payment', 'container', {
  initialization: { amount: 100000 },
  callbacks: {
    onSubmit: (formData) => {
      // formData contains token, paymentMethodId, etc.
      return fetch('/process_payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
    }
  }
});
```

### Using Secure Fields
```javascript
const token = await mp.fields.createCardToken({
  cardholderName: 'Juan Perez',
  identificationType: 'CC',
  identificationNumber: '123456789'
});
```

---

## Step 2: Send to Backend

```javascript
// Frontend
fetch('/process_payment', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    token: 'card_token_id',
    transactionAmount: 100000,
    paymentMethodId: 'visa',
    issuerId: '1234',
    installments: 1,
    payer: {
      email: 'buyer@email.com',
      identification: { type: 'CC', number: '123456789' }
    }
  })
});
```

---

## Step 3: Process Payment (Backend)

```javascript
// Node.js
const payment = await payments.create({
  transaction_amount: 100000,
  token: req.body.token,
  payment_method_id: req.body.paymentMethodId,
  installments: req.body.installments,
  payer: {
    email: req.body.payer.email,
    identification: req.body.payer.identification
  }
});

// Response:
{
  id: 1234567890,
  status: 'approved',
  status_detail: 'accredited',
  // ...
}
```

---

## Step 4: Handle Response

```javascript
// Backend sends response to frontend
res.json({
  status: payment.status,
  statusDetail: payment.status_detail,
  paymentId: payment.id
});

// Frontend shows result
.then(response => response.json())
.then(result => {
  if (result.status === 'approved') {
    // Show success
  } else if (result.status === 'pending') {
    // Show pending (e.g., cash payment)
  } else {
    // Show failure
  }
});
```

---

## Step 5: Webhook Notification

Your server receives webhook:
```javascript
// Express example
app.post('/webhook', (req, res) => {
  const { type, data } = req.body;
  
  if (type === 'payment') {
    const paymentId = data.id;
    // Update order status
  }
  
  res.sendStatus(200);
});
```

---

## Complete Example

### Frontend (HTML + JS)
```html
<div id="paymentBrick_container"></div>
<script src="https://sdk.mercadopago.com/js/v2"></script>
<script>
  const mp = new MercadoPago('PUBLIC_KEY');
  
  const brick = await mp.bricks().create('payment', 'paymentBrick_container', {
    initialization: { amount: 100000 },
    callbacks: {
      onSubmit: (formData) => {
        return fetch('/api/process_payment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        }).then(r => r.json());
      }
    }
  });
</script>
```

### Backend (Node.js/Express)
```javascript
app.post('/api/process_payment', async (req, res) => {
  try {
    const { token, paymentMethodId, issuerId, installments } = req.body;
    
    const payment = await payments.create({
      transaction_amount: 100000,
      token,
      payment_method_id: paymentMethodId,
      installments: parseInt(installments),
      payer: { email: 'buyer@email.com' }
    });
    
    res.json({
      status: payment.status,
      paymentId: payment.id
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

---

## Cash Payment Flow (Different)

For cash payments like PSE or Efecty:

1. Create payment → status is `pending`
2. Response includes `external_resource_url`
3. Redirect user to complete payment
4. User pays at store/bank
5. Webhook notifies when payment is confirmed
