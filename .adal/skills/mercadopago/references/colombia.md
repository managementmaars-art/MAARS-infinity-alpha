# Colombia (MCO) Specific Information

## Document Types
| Type | ID | Description |
|------|-----|-------------|
| CC | `CC` | Cédula de Ciudadanía |
| CE | `CE` | Cédula de Extranjería |
| NIT | `NIT` | Número de Identificación Tributaria |
| Otro | `Otro` | Other |

## Payment Methods

### Cards
| Method | ID | Type |
|--------|-----|------|
| Visa Credit | `visa` | Credit Card |
| Mastercard Credit | `mastercard` | Credit Card |
| Visa Debit | `visa_debit` | Debit Card |
| Mastercard Debit | `mastercard_debit` | Debit Card |

### Cash/Offline Payments
| Method | ID | Instructions |
|--------|-----|--------------|
| Efecty | `efecty` | Pay at Efecty stores |

### Bank Transfer
| Method | ID | Description |
|--------|-----|-------------|
| PSE | `pse` | Pagos Seguros en Línea - Bank transfer from savings/checking accounts |

### Digital Wallet
| Method | ID | Description |
|--------|-----|-------------|
| Cuenta Mercado Pago | `mercadopago` | Mercado Pago balance/wallet |

---

## PSE (Bank Transfer) Integration

### Creating Payment with PSE
```javascript
// Backend
const payment = await payments.create({
  transaction_amount: 100000, // COP amount
  payment_method_id: 'pse',
  payer: {
    email: 'buyer@email.com',
    entity_type: 'individual', // or 'association'
    identification: {
      type: 'CC',
      number: '123456789'
    }
  },
  transaction_details: {
    financial_institution: '1001' // Bank code
  }
});

// Response includes external_resource_url for bank redirect
```

### PSE Banks (financial_institution codes)
```javascript
const pseBanks = {
  '1001': 'Banco de Bogotá',
  '1002': 'Banco de Occidente',
  '1003': 'Banco Popular',
  '1004': 'Bancolombia',
  '1005': 'BBVA Colombia',
  '1006': 'Bank Davivienda',
  '1007': 'Banco Caja Social',
  '1008': 'Banco AV Villas',
  '1009': 'Bancoomeva',
  '1010': 'Credifinanciera',
  '1012': 'Cotrafa',
  '1013': 'Confiar',
  '1014': 'Nequi',
  '1015': 'Scotiabank'
};
```

---

## Test Cards (Colombia)

| Card Number | Result |
|-------------|--------|
| 4242 4242 4242 4242 | Approved |
| 4000 0000 0000 0002 | Rejected (insufficient funds) |
| 4000 0000 0000 0010 | Rejected (bad filled) |

---

## Currency
- **Currency Code**: COP
- **Currency Symbol**: $
- **Decimal Places**: 2

---

## Common Rejection Reasons for Colombia

| Status Detail | Cause | Solution |
|--------------|-------|----------|
| `rejected_by_issuer` | Card issuer declined | Try different card |
| `high_risk` | Fraud detection | Review transaction |
| `invalid_card_token` | Token expired/invalid | Regenerate token |
| `bad_filled_card_data` | Incorrect card data | Verify card info |

---

## Cash Payment Flow (Efecty)

1. Create payment with `efecty`
2. Response includes `external_resource_url`
3. Redirect user to URL to print payment slip
4. User pays at Efecty store
5. MercadoPago notifies via webhook when payment is confirmed

---

## Specific API Parameters for Colombia

### Payer Object (Colombian specific)
```javascript
const payer = {
  email: 'buyer@email.com',
  identification: {
    type: 'CC', // or 'CE', 'NIT', 'Otro'
    number: '123456789'
  },
  // For PSE:
  entity_type: 'individual', // or 'association'
  fiscal_id: '123456789' // For business payments
};
```

---

## Webhook Topics for Colombia

| Topic | Events |
|-------|--------|
| `payment` | Payment created, updated |
| `order` | Order created, updated |
| `subscription_authorized_payment` | Recurring payment |
| `subscription_preapproval` | Subscription events |
| `mp-connect` | OAuth connection |
| `wallet_connect` | Wallet transactions |
| `stop_delivery_op_wh` | Fraud alerts |
| `topic_claims_integration_wh` | Claims/disputes |
| `topic_card_id_wh` | Card updates |
| `topic_merchant_order_wh` | Merchant orders |
| `topic_chargebacks_wh` | Chargebacks |

---

## Go to Production Checklist (Colombia)

1. Use production credentials (not test)
2. Set up webhook notifications
3. Implement proper error handling
4. Add SSL certificate to site
5. Configure all payment methods
6. Test with real cards (small amounts)
7. Review rate limits and best practices
