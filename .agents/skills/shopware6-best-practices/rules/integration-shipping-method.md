---
title: Shipping Method Provider
impact: HIGH
impactDescription: custom shipping calculations and carrier integrations
tags: shipping, checkout, carrier, delivery, rates
---

## Shipping Method Provider

**Impact: HIGH (custom shipping calculations and carrier integrations)**

Shipping method providers calculate shipping costs and delivery times. Implement proper delivery time calculation, price computation, and carrier API integration.

**Incorrect (hardcoded shipping logic):**

```php
// Bad: Hardcoded prices, no carrier integration
class MyShippingHandler
{
    public function getPrice(): float
    {
        return 4.99; // Always same price
    }
}
```

**Correct shipping method handler:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service\Shipping;

use Shopware\Core\Checkout\Cart\Cart;
use Shopware\Core\Checkout\Cart\Delivery\Struct\DeliveryInformation;
use Shopware\Core\Checkout\Cart\Delivery\Struct\ShippingLocation;
use Shopware\Core\Checkout\Cart\LineItem\CartDataCollection;
use Shopware\Core\Checkout\Cart\Price\QuantityPriceCalculator;
use Shopware\Core\Checkout\Cart\Price\Struct\CalculatedPrice;
use Shopware\Core\Checkout\Cart\Price\Struct\QuantityPriceDefinition;
use Shopware\Core\Checkout\Cart\Tax\Struct\TaxRuleCollection;
use Shopware\Core\Checkout\Shipping\Cart\ShippingMethodCalculator;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

class MyShippingMethodCalculator implements ShippingMethodCalculator
{
    public function __construct(
        private readonly QuantityPriceCalculator $calculator,
        private readonly CarrierApiClient $carrierApi,
        private readonly SystemConfigService $config,
        private readonly LoggerInterface $logger
    ) {}

    public function calculate(
        Cart $cart,
        ShippingLocation $location,
        CartDataCollection $data,
        SalesChannelContext $context
    ): CalculatedPrice {
        // Get shipping method configuration
        $salesChannelId = $context->getSalesChannelId();
        $basePrice = (float) $this->config->get('MyPlugin.config.baseShippingPrice', $salesChannelId) ?? 4.99;
        $freeShippingThreshold = (float) $this->config->get('MyPlugin.config.freeShippingThreshold', $salesChannelId) ?? 50.0;

        // Check for free shipping
        $cartTotal = $cart->getPrice()->getTotalPrice();
        if ($cartTotal >= $freeShippingThreshold) {
            return $this->createPrice(0.0, $context);
        }

        // Calculate total weight
        $totalWeight = $this->calculateTotalWeight($cart);

        // Get rates from carrier API
        try {
            $rates = $this->carrierApi->getRates([
                'weight' => $totalWeight,
                'destination' => [
                    'country' => $location->getCountry()->getIso(),
                    'zip' => $location->getAddress()?->getZipcode(),
                    'city' => $location->getAddress()?->getCity()
                ],
                'service' => 'standard'
            ]);

            $shippingPrice = $rates->getPrice() ?? $basePrice;

        } catch (CarrierApiException $e) {
            $this->logger->warning('Carrier API failed, using base price', [
                'error' => $e->getMessage()
            ]);
            $shippingPrice = $basePrice;
        }

        // Apply weight surcharge
        $weightSurcharge = $this->calculateWeightSurcharge($totalWeight);
        $finalPrice = $shippingPrice + $weightSurcharge;

        return $this->createPrice($finalPrice, $context);
    }

    private function calculateTotalWeight(Cart $cart): float
    {
        $weight = 0.0;

        foreach ($cart->getLineItems() as $lineItem) {
            $deliveryInfo = $lineItem->getDeliveryInformation();
            if ($deliveryInfo) {
                $weight += $deliveryInfo->getWeight() * $lineItem->getQuantity();
            }
        }

        return $weight;
    }

    private function calculateWeightSurcharge(float $weight): float
    {
        // Surcharge for heavy packages
        if ($weight > 30) {
            return 15.00;
        }
        if ($weight > 20) {
            return 8.00;
        }
        if ($weight > 10) {
            return 4.00;
        }

        return 0.0;
    }

    private function createPrice(float $price, SalesChannelContext $context): CalculatedPrice
    {
        $taxRules = $context->buildTaxRules($context->getShippingMethod()->getTaxId());

        $definition = new QuantityPriceDefinition($price, $taxRules);

        return $this->calculator->calculate($definition, $context);
    }
}
```

**Correct delivery time calculator:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service\Shipping;

use Shopware\Core\Checkout\Cart\Delivery\Struct\DeliveryDate;
use Shopware\Core\Checkout\Cart\Delivery\Struct\DeliveryPosition;
use Shopware\Core\Checkout\Cart\Delivery\DeliveryCalculator;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

class MyDeliveryTimeCalculator
{
    public function __construct(
        private readonly CarrierApiClient $carrierApi,
        private readonly SystemConfigService $config
    ) {}

    public function calculateDeliveryDate(
        DeliveryPosition $position,
        SalesChannelContext $context
    ): DeliveryDate {
        $shippingMethod = $context->getShippingMethod();
        $deliveryTime = $shippingMethod->getDeliveryTime();

        // Get carrier-specific delivery estimate
        try {
            $estimate = $this->carrierApi->getDeliveryEstimate([
                'destination' => $context->getShippingLocation()->getCountry()->getIso(),
                'service' => 'standard'
            ]);

            $minDays = $estimate->getMinDays();
            $maxDays = $estimate->getMaxDays();

        } catch (CarrierApiException $e) {
            // Fallback to configured delivery time
            $minDays = $deliveryTime?->getMin() ?? 2;
            $maxDays = $deliveryTime?->getMax() ?? 5;
        }

        // Account for product-specific lead time
        $lineItem = $position->getLineItem();
        $deliveryInfo = $lineItem->getDeliveryInformation();

        if ($deliveryInfo && $deliveryInfo->getDeliveryTime()) {
            $productDelivery = $deliveryInfo->getDeliveryTime();
            $minDays = max($minDays, $productDelivery->getMin());
            $maxDays = max($maxDays, $productDelivery->getMax());
        }

        // Check stock and add restocking time
        if ($deliveryInfo && $deliveryInfo->getStock() < $lineItem->getQuantity()) {
            $restockTime = $deliveryInfo->getRestockTime() ?? 7;
            $minDays += $restockTime;
            $maxDays += $restockTime;
        }

        $earliest = (new \DateTime())->modify("+{$minDays} days");
        $latest = (new \DateTime())->modify("+{$maxDays} days");

        return new DeliveryDate($earliest, $latest);
    }
}
```

**Correct carrier tracking integration:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service\Shipping;

use Shopware\Core\Checkout\Order\Aggregate\OrderDelivery\OrderDeliveryEntity;

class ShippingTrackingService
{
    public function __construct(
        private readonly CarrierApiClient $carrierApi,
        private readonly EntityRepository $orderDeliveryRepository,
        private readonly LoggerInterface $logger
    ) {}

    public function createShipment(OrderDeliveryEntity $delivery, Context $context): string
    {
        $order = $delivery->getOrder();
        $address = $delivery->getShippingOrderAddress();

        // Create shipment with carrier
        $shipment = $this->carrierApi->createShipment([
            'reference' => $order->getOrderNumber(),
            'recipient' => [
                'name' => $address->getFirstName() . ' ' . $address->getLastName(),
                'company' => $address->getCompany(),
                'street' => $address->getStreet(),
                'zip' => $address->getZipcode(),
                'city' => $address->getCity(),
                'country' => $address->getCountry()->getIso(),
                'phone' => $address->getPhoneNumber(),
                'email' => $order->getOrderCustomer()->getEmail()
            ],
            'parcels' => $this->buildParcels($delivery),
            'service' => 'standard'
        ]);

        // Store tracking information
        $trackingCodes = $delivery->getTrackingCodes() ?? [];
        $trackingCodes[] = $shipment->getTrackingNumber();

        $this->orderDeliveryRepository->update([
            [
                'id' => $delivery->getId(),
                'trackingCodes' => $trackingCodes,
                'customFields' => [
                    'my_plugin_shipment_id' => $shipment->getId(),
                    'my_plugin_label_url' => $shipment->getLabelUrl()
                ]
            ]
        ], $context);

        $this->logger->info('Shipment created', [
            'deliveryId' => $delivery->getId(),
            'trackingNumber' => $shipment->getTrackingNumber()
        ]);

        return $shipment->getTrackingNumber();
    }

    public function getTrackingStatus(string $trackingNumber): array
    {
        $tracking = $this->carrierApi->getTracking($trackingNumber);

        return [
            'status' => $tracking->getStatus(),
            'location' => $tracking->getCurrentLocation(),
            'estimatedDelivery' => $tracking->getEstimatedDelivery(),
            'events' => array_map(fn($event) => [
                'timestamp' => $event->getTimestamp(),
                'status' => $event->getStatus(),
                'location' => $event->getLocation(),
                'description' => $event->getDescription()
            ], $tracking->getEvents())
        ];
    }

    private function buildParcels(OrderDeliveryEntity $delivery): array
    {
        $positions = $delivery->getPositions();
        $totalWeight = 0;

        foreach ($positions as $position) {
            $deliveryInfo = $position->getOrderLineItem()->getDeliveryInformation();
            if ($deliveryInfo) {
                $totalWeight += $deliveryInfo->getWeight() * $position->getQuantity();
            }
        }

        return [
            [
                'weight' => max($totalWeight, 0.1), // Minimum weight
                'dimensions' => [
                    'length' => 30,
                    'width' => 20,
                    'height' => 10
                ]
            ]
        ];
    }
}
```

**Service registration:**

```xml
<service id="MyVendor\MyPlugin\Service\Shipping\MyShippingMethodCalculator">
    <argument type="service" id="Shopware\Core\Checkout\Cart\Price\QuantityPriceCalculator"/>
    <argument type="service" id="MyVendor\MyPlugin\Service\CarrierApiClient"/>
    <argument type="service" id="Shopware\Core\System\SystemConfig\SystemConfigService"/>
    <argument type="service" id="logger"/>
</service>
```

Reference: [Shipping Method](https://developer.shopware.com/docs/guides/plugins/plugins/checkout/shipping/add-shipping-method.html)
