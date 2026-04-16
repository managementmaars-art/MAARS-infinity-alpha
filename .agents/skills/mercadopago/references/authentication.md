# Authentication and Credentials

## Credential Types

### Public Key
- Used in **frontend** code
- Identifies your application
- Safe to expose in browser
- Found in: Tus integraciones > Detalles de aplicación

### Access Token
- Used in **backend** code
- Identifies your account
- **Never expose** in frontend
- Has test and production versions

---

## Environments

| Environment | Use For | Credentials |
|-------------|---------|-------------|
| Test | Development, testing | Test keys (prefix TEST_) |
| Production | Real transactions | Production keys |

---

## Finding Credentials

1. Go to [Tus integraciones](https://www.mercadopago.com/developers/panel/app)
2. Select your application
3. View credentials under **Credenciales de prueba** or **Credenciales de producción**

---

## Configuration

### Frontend (Public Key)
```javascript
const mp = new MercadoPago('APP_ID', {
  locale: 'es-CO'
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

## Security Best Practices

1. **Never commit credentials** to version control
2. Use **environment variables** for all secrets
3. **Rotate credentials** periodically
4. Use **test mode** during development
5. **Validate webhook signatures** to verify sender

---

## Sharing Credentials

If building for another seller, use credential sharing:
- Access their credentials via app settings
- Never store credentials of other users
- Use OAuth for authorized access

---

## Credential Validation

Test your credentials:
```bash
curl -X GET https://api.mercadopago.com/v1/payment_methods \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```
