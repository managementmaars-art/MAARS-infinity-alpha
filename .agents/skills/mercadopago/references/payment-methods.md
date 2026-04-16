# Payment Methods

## Get Available Payment Methods

```bash
curl -X GET https://api.mercadopago.com/v1/payment_methods \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

```javascript
const methods = await paymentMethods.get();
```

---

## Payment Methods by Country

### Colombia (MCO)

| Method | ID | Type |
|--------|-----|------|
| Visa Credit | `visa` | Credit Card |
| Mastercard Credit | `mastercard` | Credit Card |
| Visa Debit | `visa_debit` | Debit Card |
| Mastercard Debit | `mastercard_debit` | Debit Card |
| PSE | `pse` | Bank Transfer |
| Efecty | `efecty` | Cash |
| Cuenta Mercado Pago | `mercadopago` | Wallet |

### Argentina (MLA)

| Method | ID | Type |
|--------|-----|------|
| Visa | `visa` | Credit/Debit |
| Mastercard | `mastercard` | Credit/Debit |
| American Express | `amex` | Credit |
| Rapipago | `rapipago` | Cash |
| Pago Fácil | `pagofacil` | Cash |
| Cuenta Mercado Pago | `mercadopago` | Wallet |

### Brazil (MLB)

| Method | ID | Type |
|--------|-----|------|
| Visa | `visa` | Credit/Debit |
| Mastercard | `mastercard` | Credit/Debit |
| Pix | `pix` | Instant Payment |
| Boleto | `bolbradesco` | Cash |
| Hipercard | `hipercard` | Credit |
| Elo | `elo` | Credit |

### Mexico (MLM)

| Method | ID | Type |
|--------|-----|------|
| Visa | `visa` | Credit/Debit |
| Mastercard | `mastercard` | Credit/Debit |
| OXXO | `oxxo` | Cash |
| SPEI | `spei` | Bank Transfer |
| Cuenta Mercado Pago | `mercadopago` | Wallet |

### Chile (MLC)

| Method | ID | Type |
|--------|-----|------|
| Visa | `visa` | Credit/Debit |
| Mastercard | `mastercard` | Credit/Debit |
| Cuenta Mercado Pago | `mercadopago` | Wallet |

### Peru (MPE)

| Method | ID | Type |
|--------|-----|------|
| Visa | `visa` | Credit/Debit |
| Mastercard | `mastercard` | Credit/Debit |
| PagoEfectivo | `pagoefectivo` | Cash |
| Cuenta Mercado Pago | `mercadopago` | Wallet |

### Uruguay (MLU)

| Method | ID | Type |
|--------|-----|------|
| Visa | `visa` | Credit/Debit |
| Mastercard | `mastercard` | Credit/Debit |
| Abitab | `abitab` | Cash |
| Redpagos | `redpagos` | Cash |
| Cuenta Mercado Pago | `mercadopago` | Wallet |

---

## Document Types by Country

### Colombia (MCO)
| ID | Name |
|----|------|
| `CC` | Cédula de Ciudadanía |
| `CE` | Cédula de Extranjería |
| `NIT` | Número de Identificación Tributaria |
| `Otro` | Otro |

### Argentina (MLA)
| ID | Name |
|----|------|
| `DNI` | Documento Nacional de Identidad |
| `CI` | Cédula de Identidad |
| `LC` | Libreta Civil |
| `LE` | Libreta de Enrolamiento |

### Brazil (MLB)
| ID | Name |
|----|------|
| `CPF` | Cadastro de Pessoas Físicas |
| `CNPJ` | Cadastro Nacional de Pessoa Jurídica |

---

## Get Installments

```javascript
const installments = await mp.getInstallments({
  amount: 100000,
  bin: '424242',
  paymentTypeId: 'credit_card'
});

// Response:
{
  payer_costs: [
    { installments: 1, installment_amount: 100000, total_amount: 100000 },
    { installments: 3, installment_amount: 34333, total_amount: 103000 },
    // ...
  ]
}
```

---

## Get Issuers

```javascript
const issuers = await mp.getIssuers({
  paymentMethodId: 'visa',
  bin: '424242'
});

// Response:
[
  { id: '1234', name: 'Banco de Bogotá', secure_thumbnail: '...', thumbnail: '...' },
  // ...
]
```
