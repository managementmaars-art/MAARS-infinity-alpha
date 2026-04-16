# Checkout Pro

Checkout Pro is a hosted payment page where buyers are redirected to MercadoPago to complete payment. Easiest integration with minimal PCI compliance requirements.

## When to Use

- Quick integration needed
- Minimal customization required
- Hosted experience is acceptable
- Lower PCI compliance burden

---

## Integration Flow

1. Create preference in backend
2. Redirect buyer to MercadoPago
3. Buyer completes payment
4. Redirect back to your site
5. Receive webhook notification

---

## 1. Create Preference (Backend)

```javascript
const preference = await preferences.create({
  items: [{
    title: 'Product Name',
    quantity: 1,
    unit_price: 100000,
    currency_id: 'COP'
  }],
  payer: {
    email: 'buyer@email.com'
  },
  back_urls: {
    success: 'https://yoursite.com/success',
    pending: 'https://yoursite.com/pending',
    failure: 'https://yoursite.com/failure'
  },
  auto_return: 'approved'
});

// preference.init_point - URL to redirect
```

---

## 2. Redirect Buyer (Frontend)

### Option A: Redirect Link
```html
<a href="${preference.init_point}">Pay with MercadoPago</a>
```

### Option B: Wallet Brick
```javascript
const mp = new MercadoPago('PUBLIC_KEY');
const bricksBuilder = mp.bricks();

bricksBuilder.create('wallet', 'container', {
  initialization: { preferenceId: preference.id }
});
```

---

## Preference Options

### Items
```javascript
items: [{
  id: 'item-id',
  title: 'Product',
  description: 'Product description',
  picture_url: 'https://example.com/img.jpg',
  quantity: 1,
  unit_price: 100.00,
  currency_id: 'COP'
}]
```

### Payer
```javascript
payer: {
  name: 'Juan',
  surname: 'Perez',
  email: 'buyer@email.com',
  phone: { area_code: '57', number: '3001234567' },
  address: { zip_code: '110111', street_name: 'Calle 123' }
}
```

### Payment Methods
```javascript
payment_methods: {
  excluded_payment_types: [{ id: 'amex' }],
  excluded_payment_methods: [{ id: 'visa' }],
  installments: 12 // Max installments
}
```

### Shipments
```javascript
shipments: {
  receiver_address: {
    zip_code: '110111',
    street_name: 'Calle 123',
    city_name: 'Bogota',
    state_name: 'Cundinamarca'
  }
}
```

### External Reference
```javascript
external_reference: 'ORDER_12345'
```

---

## Return URLs

```javascript
back_urls: {
  success: 'https://yoursite.com/success',
  pending: 'https://yoursite.com/pending',
  failure: 'https://yoursite.com/failure'
}
```

---

## Notification_url

For webhook notifications:
```javascript
notification_url: 'https://yoursite.com/webhook'
```

---

## Get Preference

```javascript
const pref = await preferences.get('PREFERENCE_ID');
```
