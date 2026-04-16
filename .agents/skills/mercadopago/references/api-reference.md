# MercadoPago API Reference

## Base URLs
- Production: `https://api.mercadopago.com`
- Sandbox: `https://api.mercadopago.com` (test mode)

## Authentication
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Common Headers
```
Content-Type: application/json
X-Idempotency-Key: UNIQUE_KEY
```

---

## Payments API

### Create Payment
```
POST /v1/payments
```

**Request Body:**
```json
{
  "transaction_amount": 100.00,
  "token": "CARD_TOKEN",
  "payment_method_id": "visa",
  "payer": {
    "email": "buyer@email.com",
    "identification": {
      "type": "CC",
      "number": "123456789"
    }
  },
  "notification_url": "https://yoursite.com/webhook"
}
```

**Response:**
```json
{
  "id": 123456789,
  "status": "approved",
  "status_detail": "accredited",
  "transaction_amount": 100.00,
  "payment_method_id": "visa",
  "payer": { "email": "buyer@email.com" }
}
```

### Get Payment
```
GET /v1/payments/{PAYMENT_ID}
```

### Refund Payment
```
POST /v1/payments/{PAYMENT_ID}/refunds
```

**Request Body (partial refund):**
```json
{
  "amount": 50.00
}
```

### Cancel Payment
```
PUT /v1/payments/{PAYMENT_ID}
```

```json
{
  "status": "cancelled"
}
```

---

## Payment Methods API

### List Payment Methods
```
GET /v1/payment_methods
```

**Response includes:**
```json
{
  "id": "visa",
  "name": "Visa",
  "payment_type_id": "credit_card",
  "status": "active"
}
```

---

## Preferences API

### Create Preference
```
POST /v1/checkout/preferences
```

```json
{
  "items": [
    {
      "title": "Product Name",
      "quantity": 1,
      "price": 100.00,
      "currency_id": "COP"
    }
  ],
  "payer": {
    "email": "buyer@email.com"
  },
  "payment_methods": {
    "excluded_payment_types": [
      { "id": "amex" }
    ]
  },
  "back_urls": {
    "success": "https://yoursite.com/success",
    "pending": "https://yoursite.com/pending",
    "failure": "https://yoursite.com/failure"
  }
}
```

### Get Preference
```
GET /v1/checkout/preferences/{PREFERENCE_ID}
```

---

## Orders API

### Create Order
```
POST /v1/orders
```

```json
{
  "type": "online",
  "external_reference": "ORDER_123",
  "total_amount": 100.00,
  "currency_id": "COP",
  "payer": {
    "email": "buyer@email.com"
  },
  "transactions": {
    "payments": [
      {
        "amount": 100.00,
        "payment_method": {
          "id": "visa",
          "type": "credit_card"
        }
      }
    ]
  }
}
```

---

## Subscriptions API

### Create Preapproval Plan
```
POST /v1/preapproval_plans
```

```json
{
  "description": "Monthly Subscription",
  "auto_recurring": {
    "frequency": 1,
    "frequency_type": "months",
    "transaction_amount": 100.00,
    "currency_id": "COP"
  }
}
```

### Create Subscription
```
POST /v1/preapprovals
```

```json
{
  "preapproval_plan_id": "PLAN_ID",
  "payer": {
    "email": "subscriber@email.com"
  }
}
```

### Update Subscription
```
PUT /v1/preapprovals/{SUBSCRIPTION_ID}
```

---

## Identification Types API

### Get Identification Types
```
GET /v1/identification_types
```

**Response:**
```json
[
  { "id": "CC", "name": "Cédula de Ciudadanía" },
  { "id": "CE", "name": "Cédula de Extranjería" },
  { "id": "NIT", "name": "Número de Identificación Tributaria" }
]
```

---

## Installments API

### Get Installments
```
GET /v1/payment_methods/installments
```

**Parameters:**
- `payment_method_id`: Card issuer (e.g., `visa`)
- `amount`: Transaction amount
- `issuer_id`: Card issuer ID (optional)

---

## Important Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/payments` | POST | Create payment |
| `/v1/payments/{id}` | GET | Get payment |
| `/v1/payments/{id}/refunds` | POST | Refund payment |
| `/v1/payment_methods` | GET | List payment methods |
| `/v1/checkout/preferences` | POST | Create preference |
| `/v1/orders` | POST | Create order |
| `/v1/preapprovals` | POST | Create subscription |
| `/v1/identification_types` | GET | Get ID types |
