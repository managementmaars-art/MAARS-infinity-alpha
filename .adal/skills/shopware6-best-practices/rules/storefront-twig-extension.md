---
title: Twig Template Extension & Override
impact: CRITICAL
impactDescription: upgrade-safe template customization without modifying core
tags: storefront, twig, template, extend, override, block
---

## Twig Template Extension & Override

**Impact: CRITICAL (upgrade-safe template customization without modifying core)**

Use Twig's `{% sw_extends %}` and block system to extend templates without copying entire files. Never copy full template files as they will break on Shopware updates.

**Incorrect (copying entire template file):**

```twig
{# Bad: Copied entire base.html.twig just to add one line #}
{# custom/plugins/MyPlugin/src/Resources/views/storefront/base.html.twig #}

<!DOCTYPE html>
<html>
<head>
    {# 200+ lines of copied code just to add one meta tag #}
    <meta name="custom" content="value">
    {# ... rest of copied content ... #}
</head>
</html>
```

**Correct (extending and overriding specific blocks):**

```twig
{# Good: Extend and override only the needed block #}
{# custom/plugins/MyPlugin/src/Resources/views/storefront/base.html.twig #}

{% sw_extends '@Storefront/storefront/base.html.twig' %}

{% block base_head_meta %}
    {{ parent() }}
    <meta name="custom" content="value">
{% endblock %}
```

**Correct block extension patterns:**

```twig
{# Extend product box to add custom badge #}
{# custom/plugins/MyPlugin/src/Resources/views/storefront/component/product/card/box.html.twig #}

{% sw_extends '@Storefront/storefront/component/product/card/box.html.twig' %}

{% block component_product_box_badges %}
    {{ parent() }}

    {% if product.extensions.myCustomData and product.extensions.myCustomData.showBadge %}
        <div class="badge badge-custom">
            {{ "myPlugin.badge.label"|trans }}
        </div>
    {% endif %}
{% endblock %}
```

```twig
{# Add content before checkout summary #}
{# custom/plugins/MyPlugin/src/Resources/views/storefront/page/checkout/confirm/index.html.twig #}

{% sw_extends '@Storefront/storefront/page/checkout/confirm/index.html.twig' %}

{% block page_checkout_confirm_summary %}
    <div class="my-custom-notice alert alert-info">
        {{ "myPlugin.checkout.notice"|trans }}
    </div>

    {{ parent() }}
{% endblock %}
```

**Correct (adding completely new template):**

```twig
{# New page template extending layout #}
{# custom/plugins/MyPlugin/src/Resources/views/storefront/page/custom/index.html.twig #}

{% sw_extends '@Storefront/storefront/page/page.html.twig' %}

{% block page_content %}
    <div class="custom-page">
        {% block custom_page_header %}
            <h1>{{ page.title }}</h1>
        {% endblock %}

        {% block custom_page_content %}
            <div class="product-listing">
                {% for product in page.products %}
                    {% sw_include '@Storefront/storefront/component/product/card/box.html.twig' with {
                        'product': product,
                        'layout': 'standard'
                    } %}
                {% endfor %}
            </div>
        {% endblock %}
    </div>
{% endblock %}
```

**Correct Twig include with variables:**

```twig
{# Include component with explicit variables #}
{% sw_include '@Storefront/storefront/component/product/card/box.html.twig' with {
    'product': product,
    'layout': 'standard',
    'displayMode': 'cover'
} only %}

{# Include custom component #}
{% sw_include '@MyPlugin/storefront/component/custom-widget.html.twig' with {
    'data': widgetData
} %}
```

**Using Twig functions correctly:**

```twig
{# Translation with parameters #}
{{ "myPlugin.greeting"|trans({'%name%': customer.firstName}) }}

{# Asset path for plugin assets #}
<img src="{{ asset('bundles/myplugin/images/logo.png') }}" alt="Logo">

{# Route generation #}
<a href="{{ path('frontend.custom.page', { 'id': item.id }) }}">
    {{ item.name }}
</a>

{# Check if block exists before extending #}
{% if block('my_block') is defined %}
    {{ block('my_block') }}
{% endif %}

{# Feature flag check #}
{% if feature('FEATURE_NEXT_12345') %}
    <div class="new-feature">...</div>
{% endif %}
```

**Template priority via theme.json:**

```json
{
    "name": "MyTheme",
    "author": "MyVendor",
    "views": [
        "@Storefront",
        "@Plugins",
        "@MyTheme"
    ]
}
```

**Common blocks to extend:**

| Block | Location | Purpose |
|-------|----------|---------|
| `base_head_meta` | base.html.twig | Add meta tags |
| `base_body_classes` | base.html.twig | Add body CSS classes |
| `base_header` | base.html.twig | Customize header |
| `base_footer` | base.html.twig | Customize footer |
| `page_content` | page.html.twig | Main page content |
| `page_product_detail_buy` | product-detail/buy-widget.html.twig | Buy button area |
| `component_product_box_badges` | card/box.html.twig | Product badges |
| `page_checkout_confirm_summary` | confirm/index.html.twig | Checkout summary |

Reference: [Customize Templates](https://developer.shopware.com/docs/guides/plugins/plugins/storefront/customize-templates.html)
