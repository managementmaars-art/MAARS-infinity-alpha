---
title: Channel-Specific Pricing
impact: MEDIUM
impactDescription: correct price calculation across currencies and customer groups
tags: pricing, currency, customer-group, sales-channel, tax
---

## Channel-Specific Pricing

**Impact: MEDIUM (correct price calculation across currencies and customer groups)**

Shopware 6 supports complex pricing scenarios with multiple currencies, customer groups, and quantity tiers. Implement price calculations correctly respecting all contexts.

**Incorrect (ignoring pricing context):**

```php
// Bad: Hardcoded price without context
public function getProductPrice(ProductEntity $product): float
{
    return $product->getPrice()->first()->getGross();
}

// Bad: Not respecting currency
public function formatPrice(float $price): string
{
    return '€' . number_format($price, 2);
}
```

**Correct price handling:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Checkout\Cart\Price\QuantityPriceCalculator;
use Shopware\Core\Checkout\Cart\Price\Struct\CalculatedPrice;
use Shopware\Core\Checkout\Cart\Price\Struct\QuantityPriceDefinition;
use Shopware\Core\Content\Product\ProductEntity;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

class PriceService
{
    public function __construct(
        private readonly QuantityPriceCalculator $calculator,
        private readonly CurrencyFormatter $currencyFormatter
    ) {}

    /**
     * Get the correct price for a product in the current sales channel context
     */
    public function getProductPrice(
        ProductEntity $product,
        SalesChannelContext $context,
        int $quantity = 1
    ): CalculatedPrice {
        // The product's calculatedPrice is already context-aware when loaded via Store API
        if ($product->getCalculatedPrice()) {
            $unitPrice = $product->getCalculatedPrice()->getUnitPrice();
        } else {
            // Fallback: Calculate from price definition
            $unitPrice = $this->getPriceForContext($product, $context);
        }

        // Apply quantity pricing (tier prices)
        $unitPrice = $this->applyQuantityPricing($product, $unitPrice, $quantity, $context);

        // Build price definition with tax rules
        $definition = new QuantityPriceDefinition(
            $unitPrice,
            $context->buildTaxRules($product->getTaxId()),
            $quantity
        );

        return $this->calculator->calculate($definition, $context);
    }

    /**
     * Get raw price for context (currency + customer group)
     */
    private function getPriceForContext(
        ProductEntity $product,
        SalesChannelContext $context
    ): float {
        $currencyId = $context->getCurrencyId();
        $prices = $product->getPrice();

        if (!$prices) {
            return 0.0;
        }

        // Look for currency-specific price
        foreach ($prices as $price) {
            if ($price->getCurrencyId() === $currencyId) {
                return $this->getGrossOrNet($price, $context);
            }
        }

        // Fallback to default currency with conversion
        $defaultPrice = $prices->getCurrencyPrice(Defaults::CURRENCY);

        if (!$defaultPrice) {
            return 0.0;
        }

        $basePrice = $this->getGrossOrNet($defaultPrice, $context);

        // Apply currency factor
        return $basePrice * $context->getCurrency()->getFactor();
    }

    /**
     * Get gross or net based on context
     */
    private function getGrossOrNet(PriceStruct $price, SalesChannelContext $context): float
    {
        // Check if prices should be displayed as net (B2B)
        if ($context->getTaxState() === CartPrice::TAX_STATE_NET) {
            return $price->getNet();
        }

        return $price->getGross();
    }

    /**
     * Apply quantity-based pricing (graduated prices)
     */
    private function applyQuantityPricing(
        ProductEntity $product,
        float $basePrice,
        int $quantity,
        SalesChannelContext $context
    ): float {
        $prices = $product->getPrices();

        if (!$prices || $prices->count() === 0) {
            return $basePrice;
        }

        // Filter prices for current rule (customer group)
        $applicablePrices = $prices->filter(function ($price) use ($context) {
            $ruleId = $price->getRuleId();

            // Check if rule applies to current context
            return $ruleId === null || in_array($ruleId, $context->getRuleIds(), true);
        });

        if ($applicablePrices->count() === 0) {
            return $basePrice;
        }

        // Find price for quantity
        $matchingPrice = null;
        foreach ($applicablePrices as $price) {
            if ($quantity >= $price->getQuantityStart() &&
                ($price->getQuantityEnd() === null || $quantity <= $price->getQuantityEnd())
            ) {
                $matchingPrice = $price;
                break;
            }
        }

        if (!$matchingPrice) {
            return $basePrice;
        }

        // Get price for current currency
        $currencyPrice = $matchingPrice->getPrice()->getCurrencyPrice($context->getCurrencyId());

        if (!$currencyPrice) {
            // Convert from default currency
            $defaultPrice = $matchingPrice->getPrice()->getCurrencyPrice(Defaults::CURRENCY);
            return $this->getGrossOrNet($defaultPrice, $context) * $context->getCurrency()->getFactor();
        }

        return $this->getGrossOrNet($currencyPrice, $context);
    }

    /**
     * Format price for display
     */
    public function formatPrice(
        CalculatedPrice $price,
        SalesChannelContext $context
    ): string {
        return $this->currencyFormatter->formatCurrencyByLanguage(
            $price->getTotalPrice(),
            $context->getCurrency()->getIsoCode(),
            $context->getLanguageId(),
            $context->getContext()
        );
    }

    /**
     * Get price breakdown for cart display
     */
    public function getPriceBreakdown(
        CalculatedPrice $price,
        SalesChannelContext $context
    ): array {
        $breakdown = [
            'unitPrice' => $price->getUnitPrice(),
            'quantity' => $price->getQuantity(),
            'totalPrice' => $price->getTotalPrice(),
            'currency' => $context->getCurrency()->getIsoCode()
        ];

        // Add tax details
        $taxes = [];
        foreach ($price->getCalculatedTaxes() as $tax) {
            $taxes[] = [
                'rate' => $tax->getTaxRate(),
                'tax' => $tax->getTax(),
                'price' => $tax->getPrice()
            ];
        }
        $breakdown['taxes'] = $taxes;

        // Display mode
        $breakdown['displayMode'] = $context->getTaxState(); // gross/net

        return $breakdown;
    }
}
```

**Correct custom price provider:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Content\Product\SalesChannel\Price\AbstractProductPriceCalculator;
use Shopware\Core\Content\Product\SalesChannel\SalesChannelProductEntity;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

class CustomPriceCalculator extends AbstractProductPriceCalculator
{
    public function __construct(
        private readonly AbstractProductPriceCalculator $decorated,
        private readonly ExternalPriceService $externalPriceService
    ) {}

    public function getDecorated(): AbstractProductPriceCalculator
    {
        return $this->decorated;
    }

    public function calculate(iterable $products, SalesChannelContext $context): void
    {
        // First, let Shopware calculate default prices
        $this->decorated->calculate($products, $context);

        // Then apply custom price logic
        foreach ($products as $product) {
            $this->applyCustomPrice($product, $context);
        }
    }

    private function applyCustomPrice(
        SalesChannelProductEntity $product,
        SalesChannelContext $context
    ): void {
        // Check for external price override
        $externalPrice = $this->externalPriceService->getPrice(
            $product->getProductNumber(),
            $context->getCurrencyId(),
            $context->getCurrentCustomerGroup()->getId()
        );

        if ($externalPrice === null) {
            return; // Keep default price
        }

        // Recalculate with external price
        $definition = new QuantityPriceDefinition(
            $externalPrice,
            $context->buildTaxRules($product->getTaxId())
        );

        $calculatedPrice = $this->calculator->calculate($definition, $context);

        // Override product price
        $product->setCalculatedPrice($calculatedPrice);

        // Also update cheapest price if applicable
        if ($product->getCalculatedCheapestPrice()) {
            $product->setCalculatedCheapestPrice($calculatedPrice);
        }
    }
}
```

**Currency and tax handling:**

| Context Property | Description |
|------------------|-------------|
| `getCurrencyId()` | Current currency UUID |
| `getCurrency()->getIsoCode()` | Currency ISO (EUR, USD) |
| `getCurrency()->getFactor()` | Conversion factor from default |
| `getTaxState()` | `gross` or `net` display |
| `getCurrentCustomerGroup()` | Active customer group |
| `buildTaxRules($taxId)` | Get applicable tax rules |

**Price display considerations:**

```php
// Check if showing net prices (B2B)
if ($context->getTaxState() === CartPrice::TAX_STATE_NET) {
    // Display net price
    $displayPrice = $price->getNetPrice();
    $label = 'excl. VAT';
} else {
    // Display gross price
    $displayPrice = $price->getTotalPrice();
    $label = 'incl. VAT';
}
```

Reference: [Pricing](https://developer.shopware.com/docs/concepts/commerce/core-concepts/product#pricing)
