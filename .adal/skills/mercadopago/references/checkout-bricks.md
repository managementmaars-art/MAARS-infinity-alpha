# Checkout Bricks Integration Guide

## Bricks Overview

Checkout Bricks are pre-built, modular UI components that provide a secure, PCI-compliant way to accept payments. Card data is tokenized in MercadoPago's iframes, so you never handle raw card numbers.

## Available Bricks

| Brick | Purpose | Use Case |
|-------|---------|----------|
| Payment Brick | All payment methods | Full checkout with cards, PSE, cash |
| Card Payment Brick | Cards only | Simple card-only checkout |
| Wallet Brick | MercadoPago account | Returning users with saved cards |
| Status Screen Brick | Payment status | Show payment result |
| Brand Brick | Card brands | Show accepted card logos |

---

## Common Initialization Pattern

```javascript
// 1. Load SDK
const mp = new MercadoPago('PUBLIC_KEY');

// 2. Create bricks builder
const bricksBuilder = mp.bricks();

// 3. Create and render brick
const brick = await bricksBuilder.create(
  'brickType',      // 'payment', 'cardPayment', 'wallet', 'statusScreen'
  'containerId',    // HTML element ID
  {
    initialization: { /* ... */ },
    customization: { /* ... */ },
    callbacks: { /* ... */ }
  }
);
```

---

## Payment Brick (Colombia - MCO)

### Basic Integration
```html
<div id="paymentBrick_container"></div>
```

```javascript
const paymentBrick = await bricksBuilder.create(
  'payment',
  'paymentBrick_container',
  {
    initialization: {
      amount: 100000, // COP
      payer: {
        email: 'buyer@email.com'
      }
    },
    customization: {
      paymentMethods: {
        creditCard: ['visa', 'mastercard'],
        debitCard: ['visa_debit', 'mastercard_debit'],
        bankTransfer: ['pse'],
        cash: ['efecty'],
        wallet: ['mercadopago']
      },
      visual: {
        style: {
          theme: 'default', // or 'dark', 'bootstrap'
          customVariables: {
            primaryColor: '##FF0000'
          }
        }
      }
    },
    callbacks: {
      onReady: () => {
        // Brick is ready
      },
      onSubmit: (formData) => {
        // Send to your backend
        // formData contains: token, paymentMethodId, issuer_id, cardholderName, etc.
        return fetch('/process_payment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        }).then(res => res.json());
      },
      onError: (error) => {
        console.error('Error:', error);
      },
      onBrickReady: () => {},
      onExit: () => {}
    }
  }
);
```

### FormData Returned by onSubmit
```javascript
{
  token: 'card_token_id',
  paymentMethodId: 'visa',
  issuer_id: '1234',
  cardholderName: 'JUAN PEREZ',
  cardholderEmail: 'buyer@email.com',
  identificationType: 'CC',
  identificationNumber: '123456789'
}
```

---

## Card Payment Brick

### Integration
```html
<div id="cardPaymentBrick_container"></div>
```

```javascript
const cardPaymentBrick = await bricksBuilder.create(
  'cardPayment',
  'cardPaymentBrick_container',
  {
    initialization: {
      totalAmount: 100000,
      paymentAmount: 100000,
    },
    customization: {
      visual: {
        style: {
          theme: 'default',
          customVariables: {
            fontFamily: 'Roboto'
          }
        }
      },
      form: {
        cardNumber: { placeholder: '1234 1234 1234 1234' },
        expirationDate: { placeholder: 'MM/YY' },
        securityCode: { placeholder: '123' },
        cardholderName: { placeholder: 'Nombre como aparece en la tarjeta' },
        cardholderEmail: { placeholder: 'email@email.com' }
      }
    },
    callbacks: {
      onSubmit: (formData) => {
        // formData.token - card token
        // formData.paymentMethodId - card issuer
        return fetch('/process_payment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        });
      },
      onError: (error) => console.error(error),
      onReady: () => {}
    }
  }
);
```

---

## Wallet Brick

### Integration
```html
<div id="walletBrick_container"></div>
```

```javascript
const walletBrick = await bricksBuilder.create(
  'wallet',
  'walletBrick_container',
  {
    initialization: {
      preferenceId: 'PREFERENCE_ID', // From your backend
      redirectMode: 'self' // or 'parent'
    },
    callbacks: {
      onReady: () => {},
      onError: (error) => console.error(error)
    }
  }
);
```

### Backend - Create Preference
```javascript
const preference = await preferences.create({
  items: [{
    title: 'Product',
    quantity: 1,
    price: 100000,
    currency_id: 'COP'
  }],
  payer: {
    email: 'buyer@email.com'
  },
  back_urls: {
    success: 'https://yoursite.com/success',
    pending: 'https://yoursite.com/pending',
    failure: 'https://yoursite.com/failure'
  }
});

// Return preference.id to frontend
```

---

## Status Screen Brick

### Integration
```html
<div id="statusScreenBrick_container"></div>
```

```javascript
const statusScreenBrick = await bricksBuilder.create(
  'statusScreen',
  'statusScreenBrick_container',
  {
    initialization: {
      paymentId: 'PAYMENT_ID_FROM_URL_OR_STORAGE'
    },
    callbacks: {
      onReady: () => {},
      onError: (error) => console.error(error)
    }
  }
);
```

### 3DS Challenge Integration
```javascript
// For 3DS, pass additional info
const statusScreenBrick = await bricksBuilder.create(
  'statusScreen',
  'statusScreenBrick_container',
  {
    initialization: {
      paymentId: paymentId,
      additionalInfo: {
        externalResourceURL: threeDsInfo.external_resource_url,
        creq: threeDsInfo.creq
      }
    },
    callbacks: {
      onReady: () => {},
      onError: (error) => console.error(error)
    }
  }
);
```

---

## Themes and Styling

### Available Themes
| Theme | Description |
|-------|-------------|
| `default` | Standard MercadoPago theme |
| `dark` | Dark theme |
| `bootstrap` | Bootstrap-compatible |

### Custom Variables
```javascript
const customization = {
  visual: {
    style: {
      theme: 'default',
      customVariables: {
        primaryColor: '##FF5733',
        secondaryColor: '#333333',
        backgroundColor: '#FFFFFF',
        fontFamily: 'Roboto, sans-serif',
        borderRadius: '8px',
        buttonHeight: '48px'
      }
    }
  }
};
```

---

## Languages

Bricks supports: Spanish (`es`), Portuguese (`pt`), English (`en`)

```javascript
// Set via SDK initialization
const mp = new MercadoPago('PUBLIC_KEY', {
  locale: 'es-CO' // Spanish Colombia
});
```

---

## Responsive Behavior

Bricks automatically adapt to container size. Set container CSS:

```css
#paymentBrick_container {
  width: 100%;
  max-width: 400px;
  min-height: 600px;
}
```

---

## Security Notes

1. Card data never touches your server - handled in MercadoPago iframe
2. Token generated is single-use and expires quickly
3. Use HTTPS on your site
4. Validate all webhook notifications
5. PCI SAQ A compliance when using Bricks

---

## Error Handling

```javascript
callbacks: {
  onError: (error) => {
    // Error types:
    // - 'invalid_fields': Form validation error
    // - 'card_error': Card was rejected
    // - 'network_error': Connection error
    // - 'back_error': User exited
    console.error('Error:', error);
  }
}
```

---

## Migration from CardForm

CardForm is deprecated. Migrate to Card Payment Brick:

1. Replace CardForm script with MercadoPago.js V2
2. Replace form inputs with Brick container div
3. Update submit handler to use `onSubmit` callback
4. Token generation is handled automatically by Brick
