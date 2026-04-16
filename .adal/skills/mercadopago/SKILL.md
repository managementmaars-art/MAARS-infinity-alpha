---
name: mercadopago
description: |
  Comprehensive guide for integrating MercadoPago payment solutions. Use this skill when working with MercadoPago APIs, SDKs, checkout solutions, payment processing, subscriptions, webhooks, or any payment-related integration tasks. Covers Checkout Pro, Checkout Bricks, Checkout API, mobile SDKs, payment methods, authentication, and best practices. Make sure to use this skill whenever the user mentions MercadoPago, payment processing, checkout integration, accepting payments online, or any payment gateway related tasks in Latin America (Argentina, Brazil, Mexico, Colombia, Chile, Peru, Uruguay).
---

# MercadoPago Integration Skill

MercadoPago is the payment platform of Mercado Libre, operating across Latin America.

## Quick Reference

| Country | Code | Currency |
|---------|------|----------|
| Argentina | MLA | ARS |
| Brazil | MLB | BRL |
| Mexico | MLM | MXN |
| Colombia | MCO | COP |
| Chile | MLC | CLP |
| Peru | MPE | PEN |
| Uruguay | MLU | UYU |

## Navigation

### Getting Started
- [SDKs and Setup](references/sdks.md) - Frontend/backend SDKs, initialization
- [Authentication](references/authentication.md) - Credentials, API keys

### Integration Products
- [Checkout Pro](references/checkout-pro.md) - Hosted redirect checkout
- [Checkout Bricks](references/checkout-bricks.md) - Modular embedded components
- [Checkout API](references/checkout-api.md) - Full API control

### Core Topics
- [Payment Methods](references/payment-methods.md) - Available methods by country
- [Payment Flow](references/payment-flow.md) - Complete payment process
- [Payment Status](references/payment-status.md) - Status codes reference
- [Webhooks](references/webhooks.md) - Notifications setup

### Features
- [3DS Authentication](references/3ds.md) - 3D Secure integration
- [Subscriptions](references/subscriptions.md) - Recurring payments
- [Refunds](references/refunds.md) - Cancellations and refunds

### Colombia (MCO)
- [Colombia Guide](references/colombia.md) - PSE, Efecty, specific methods

### Utilities
- [Testing](references/testing.md) - Test cards, test users
- [Error Handling](references/errors.md) - Error codes and handling
- [Security](references/security.md) - Best practices, PCI compliance
- [API Reference](references/api-reference.md) - Endpoint documentation

---

## Country-Specific Payment Methods

| Country | Cards | Cash | Bank Transfer | Wallet |
|---------|-------|------|--------------|--------|
| MCO | Visa, Mastercard | Efecty | PSE | Mercado Pago |
| MLA | Visa, Mastercard | Rapipago, Pago Fácil | - | Mercado Pago |
| MLB | Visa, Mastercard | Boleto | Pix | Mercado Pago |
| MLM | Visa, Mastercard | OXXO | SPEI | Mercado Pago |
| MLC | Visa, Mastercard | - | - | Mercado Pago |
| MPE | Visa, Mastercard | PagoEfectivo | - | Mercado Pago |
| MLU | Visa, Mastercard | Abitab, Redpagos | - | Mercado Pago |

---

## Common Tasks

**Process a payment:**
1. Read [Payment Flow](references/payment-flow.md)
2. Use [SDKs](references/sdks.md) to tokenize card
3. Send to backend, create payment via [API](references/checkout-api.md)

**Set up webhooks:**
1. Read [Webhooks](references/webhooks.md)
2. Configure notifications
3. Validate signatures

**Add new payment method:**
1. Check [Payment Methods](references/payment-methods.md) for your country
2. See [Colombia](references/colombia.md) for PSE/Efecty

---

## MCP Tools Available

When using MercadoPago MCP, access these tools:
- `search_documentation` - Search docs
- `create_test_user` - Create test users  
- `save_webhook` - Configure webhooks
- `quality_evaluation` - Check integration quality
