---
title: App Scripts (Twig)
impact: MEDIUM
impactDescription: customize storefront behavior without external backend
tags: app, scripts, twig, hook, logic
---

## App Scripts (Twig)

**Impact: MEDIUM (customize storefront behavior without external backend)**

App Scripts allow running Twig-based logic at specific hook points without an external server. Use them for calculations, cart manipulation, and dynamic storefront customizations.

**Incorrect (complex logic in scripts):**

```twig
{# Bad: HTTP calls in scripts (not allowed) #}
{% set response = http.get('https://api.example.com/data') %}

{# Bad: Heavy computation #}
{% for i in 1..10000 %}
    {% set result = result + complex_calculation(i) %}
{% endfor %}
```

**Correct script structure:**

```
custom/apps/MyApp/
└── Resources/
    └── scripts/
        ├── product-page-loaded/
        │   └── add-custom-data.twig
        ├── cart-loaded/
        │   └── calculate-discount.twig
        ├── checkout-cart-page-loaded/
        │   └── add-shipping-notice.twig
        └── include/
            └── helpers.twig
```

**Correct product page script:**

```twig
{# Resources/scripts/product-page-loaded/add-custom-data.twig #}

{# Access the hook data #}
{% set product = hook.page.product %}
{% set salesChannelContext = hook.context %}

{# Add custom extension data #}
{% if product.customFields.my_app_external_sku is defined %}
    {% set stockInfo = services.repository.search('product', {
        'ids': [product.id],
        'associations': {
            'stock': {}
        }
    }).first %}

    {# Add data as extension #}
    {% do product.addExtension('myAppData', {
        'externalSku': product.customFields.my_app_external_sku,
        'stockLevel': stockInfo.stock,
        'lastUpdated': 'now'|date('Y-m-d H:i:s')
    }) %}
{% endif %}

{# Conditional based on customer group #}
{% set customer = salesChannelContext.customer %}
{% if customer %}
    {% set customerGroup = customer.groupId %}

    {% if customerGroup == 'vip-group-id' %}
        {% do product.addExtension('vipPricing', {
            'showVipPrice': true,
            'discount': 10
        }) %}
    {% endif %}
{% endif %}
```

**Correct cart manipulation script:**

```twig
{# Resources/scripts/cart-loaded/calculate-discount.twig #}

{% set cart = hook.cart %}
{% set context = hook.context %}
{% set customer = context.customer %}

{# Check minimum order value for discount #}
{% set cartTotal = cart.price.totalPrice %}
{% set minimumOrderValue = 100 %}
{% set discountPercentage = 5 %}

{% if cartTotal >= minimumOrderValue %}
    {# Calculate discount amount #}
    {% set discountAmount = (cartTotal * discountPercentage / 100) * -1 %}

    {# Check if discount already applied #}
    {% set hasDiscount = false %}
    {% for lineItem in cart.lineItems %}
        {% if lineItem.type == 'discount' and lineItem.referencedId == 'my-app-bulk-discount' %}
            {% set hasDiscount = true %}
        {% endif %}
    {% endfor %}

    {% if not hasDiscount %}
        {# Add discount line item #}
        {% set discount = services.cart.items.create({
            'type': 'discount',
            'referencedId': 'my-app-bulk-discount',
            'label': 'Bulk Order Discount (' ~ discountPercentage ~ '%)',
            'good': false,
            'priceDefinition': {
                'type': 'absolute',
                'price': discountAmount
            }
        }) %}

        {% do cart.add(discount) %}
    {% endif %}
{% endif %}
```

**Correct checkout page script:**

```twig
{# Resources/scripts/checkout-cart-page-loaded/add-shipping-notice.twig #}

{% set cart = hook.page.cart %}
{% set shippingMethod = hook.context.shippingMethod %}

{# Calculate estimated delivery based on shipping method #}
{% set today = 'now'|date('Y-m-d') %}

{% if shippingMethod.name == 'Express' %}
    {% set deliveryDays = 1 %}
{% elseif shippingMethod.name == 'Standard' %}
    {% set deliveryDays = 3 %}
{% else %}
    {% set deliveryDays = 5 %}
{% endif %}

{# Add delivery estimate to page #}
{% set estimatedDelivery = today|date_modify('+' ~ deliveryDays ~ ' days')|date('Y-m-d') %}

{% do hook.page.addExtension('deliveryEstimate', {
    'date': estimatedDelivery,
    'days': deliveryDays,
    'message': 'Estimated delivery: ' ~ estimatedDelivery|date('F j, Y')
}) %}

{# Check for items that might delay shipping #}
{% set hasBackorder = false %}
{% for item in cart.lineItems %}
    {% if item.payload.stock is defined and item.payload.stock < item.quantity %}
        {% set hasBackorder = true %}
    {% endif %}
{% endfor %}

{% if hasBackorder %}
    {% do hook.page.addExtension('shippingNotice', {
        'type': 'warning',
        'message': 'Some items may have extended delivery times due to limited stock.'
    }) %}
{% endif %}
```

**Using includes for shared logic:**

```twig
{# Resources/scripts/include/helpers.twig #}

{% macro calculateVipDiscount(customer, basePrice) %}
    {% set discount = 0 %}

    {% if customer %}
        {% set customerGroup = customer.group.name %}

        {% if customerGroup == 'VIP' %}
            {% set discount = basePrice * 0.15 %}
        {% elseif customerGroup == 'Premium' %}
            {% set discount = basePrice * 0.10 %}
        {% endif %}
    {% endif %}

    {{ discount }}
{% endmacro %}

{% macro formatPrice(amount, currency) %}
    {{ amount|number_format(2) }} {{ currency }}
{% endmacro %}
```

```twig
{# Using the include #}
{% import 'include/helpers.twig' as helpers %}

{% set discount = helpers.calculateVipDiscount(customer, product.price) %}
```

**Available hook points:**

| Hook | Description |
|------|-------------|
| `product-page-loaded` | Product detail page loaded |
| `cart-loaded` | Cart data loaded |
| `checkout-cart-page-loaded` | Checkout cart page |
| `checkout-confirm-page-loaded` | Checkout confirm page |
| `checkout-finish-page-loaded` | Order completion page |
| `checkout-info-page-loaded` | Checkout info page |
| `checkout-register-page-loaded` | Registration page |
| `account-order-page-loaded` | Customer orders page |

**Available services in scripts:**

| Service | Purpose |
|---------|---------|
| `services.repository` | Search/read entities |
| `services.cart` | Cart manipulation |
| `services.config` | System configuration |
| `services.media` | Media handling |
| `services.translator` | Translations |

**Limitations:**

- No HTTP requests to external services
- Limited execution time
- No write operations to entities (except cart)
- No access to filesystem
- Subset of Twig functions available

Reference: [App Scripts](https://developer.shopware.com/docs/guides/plugins/apps/app-scripts/)
