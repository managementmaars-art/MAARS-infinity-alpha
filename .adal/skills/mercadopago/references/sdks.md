# SDKs and Setup

## Frontend SDKs

### MercadoPago.js V2 (Web)
```html
<script src="https://sdk.mercadopago.com/js/v2"></script>
```
```bash
npm install @mercadopago/sdk-js
```

```javascript
const mp = new MercadoPago('YOUR_PUBLIC_KEY');
```

### React SDK
```bash
npm install @mercadopago/sdk-react
```

```javascript
import { initMercadoPago } from '@mercadopago/sdk-react';
initMercadoPago('YOUR_PUBLIC_KEY');
```

### Mobile SDKs

**iOS** (Swift Package Manager):
```
https://github.com/mercadopago/sdk-ios
```

**Android** (Maven):
```
https://artifacts.mercadolibre.com/repository/android-releases
```

---

## Backend SDKs

### Node.js
```bash
npm install mercadopago
```
```javascript
import { MercadoPagoConfig, Payments } from 'mercadopago';

const client = new MercadoPagoConfig({
  accessToken: 'YOUR_ACCESS_TOKEN',
});
```

### Python
```bash
pip install mercadopago
```
```python
import mercadopago
sdk = mercadopago.SDK("ACCESS_TOKEN")
```

### PHP (Composer)
```bash
composer require mercadopago/sdk
```
```php
use MercadoPago\MercadoPagoConfig;
MercadoPagoConfig::setAccessToken("YOUR_ACCESS_TOKEN");
```

### Java
```xml
<dependency>
  <groupId>com.mercadopago</groupId>
  <artifactId>sdk-java</artifactId>
  <version>2.1.0</version>
</dependency>
```

### Ruby
```bash
gem install mercadopago
```
```ruby
sdk = Mercadopago::SDK.new('ACCESS_TOKEN')
```

### .NET
```bash
dotnet add package mercadopago-sdk
```
```csharp
MercadoPagoConfig.AccessToken = "ACCESS_TOKEN";
```

### Go
```bash
go get github.com/mercadopago/go-sdk
```

---

## SDK Initialization

### Frontend (Public Key)
```javascript
const mp = new MercadoPago('PUBLIC_KEY', {
  locale: 'es-CO' // Optional: specify locale
});
```

### Backend (Access Token)
```javascript
// Node.js
MercadoPagoConfig.setAccessToken('ACCESS_TOKEN');

// Python
sdk = mercadopago.SDK("ACCESS_TOKEN")

// PHP
MercadoPagoConfig::setAccessToken("ACCESS_TOKEN");
```

---

## MercadoPago.js Core Methods

### Create Card Token (Secure Fields)
```javascript
const cardToken = await mp.fields.createCardToken({
  cardholderName: 'Juan Perez',
  identificationType: 'CC',
  identificationNumber: '123456789',
});
// Returns: { id: 'card_token_id', ... }
```

### Get Identification Types
```javascript
const idTypes = await mp.getIdentificationTypes();
// Returns: [{ id: 'CC', name: 'Cédula de Ciudadanía' }, ...]
```

### Get Payment Methods
```javascript
const methods = await mp.getPaymentMethods({ bin: '424242' });
// Returns: { results: [{ id: 'visa', name: 'Visa' }, ...] }
```

### Get Installments
```javascript
const installments = await mp.getInstallments({
  amount: 100000,
  bin: '424242',
  paymentTypeId: 'credit_card'
});
```

---

## React Components

### Wallet Component
```jsx
import { Wallet } from '@mercadopago/sdk-react';

<Wallet initialization={{ preferenceId: 'PREF_ID' }} />
```

### Status Screen Component
```jsx
import { StatusScreen } from '@mercadopago/sdk-react';

<StatusScreen initialization={{ paymentId: 'PAYMENT_ID' }} />
```

### Payment Brick (React)
```jsx
import { Payment } from '@mercadopago/sdk-react';

<Payment
  initialization={{ amount: 100000 }}
  customization={{ paymentMethods: { creditCard: ['visa'] } }}
  onSubmit={handleSubmit}
/>
```
