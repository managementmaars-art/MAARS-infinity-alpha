---
title: Implement Logging Correctly
impact: MEDIUM
impactDescription: enables effective debugging and monitoring
tags: logging, debugging, observability, monolog
---

## Implement Logging Correctly

**Impact: MEDIUM (enables effective debugging and monitoring)**

Proper logging enables debugging in production and provides visibility into application behavior. Shopware uses Monolog through Symfony's logging infrastructure.

**Incorrect (logging anti-patterns):**

```php
// Bad: Using echo/print for debugging
class MyService
{
    public function process(OrderEntity $order): void
    {
        echo "Processing order: " . $order->getId();  // Never in production!
        var_dump($order);  // Exposes data, breaks output
        print_r($order->getLineItems());
    }
}

// Bad: Logging sensitive data
class PaymentService
{
    public function processPayment(PaymentData $data): void
    {
        // Bad: Logging credit card numbers!
        $this->logger->info('Processing payment', [
            'cardNumber' => $data->getCardNumber(),
            'cvv' => $data->getCvv(),
            'customerId' => $data->getCustomerId(),
        ]);
    }
}

// Bad: Wrong log levels
class ProductImporter
{
    public function import(array $products): void
    {
        foreach ($products as $product) {
            // Bad: DEBUG for normal operations floods logs
            $this->logger->debug('Importing product', ['sku' => $product['sku']]);

            try {
                $this->importProduct($product);
            } catch (\Exception $e) {
                // Bad: INFO for errors - won't trigger alerts
                $this->logger->info('Import failed', ['error' => $e->getMessage()]);
            }
        }
    }
}

// Bad: No context, useless messages
class CheckoutService
{
    public function checkout(): void
    {
        $this->logger->error('Error occurred');  // What error? Where?
        $this->logger->info('Done');  // Done with what?
    }
}

// Bad: Logging to custom files without rotation
class CustomLogger
{
    public function log(string $message): void
    {
        file_put_contents('/var/log/my-plugin.log', $message, FILE_APPEND);
        // No rotation = disk full eventually
    }
}
```

**Correct (proper logging implementation):**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Psr\Log\LoggerInterface;

class OrderProcessingService
{
    public function __construct(
        private readonly LoggerInterface $logger
    ) {}

    public function processOrder(string $orderId, Context $context): void
    {
        // Good: Structured logging with context
        $this->logger->info('Starting order processing', [
            'orderId' => $orderId,
            'salesChannelId' => $context->getSource()->getSalesChannelId(),
        ]);

        try {
            $order = $this->loadOrder($orderId, $context);

            // Good: DEBUG for detailed tracing (disabled in prod by default)
            $this->logger->debug('Order loaded', [
                'orderId' => $orderId,
                'itemCount' => $order->getLineItems()->count(),
                'total' => $order->getAmountTotal(),
            ]);

            $this->validateOrder($order);
            $this->processPayment($order);

            // Good: INFO for significant events
            $this->logger->info('Order processed successfully', [
                'orderId' => $orderId,
                'orderNumber' => $order->getOrderNumber(),
            ]);

        } catch (ValidationException $e) {
            // Good: WARNING for recoverable issues
            $this->logger->warning('Order validation failed', [
                'orderId' => $orderId,
                'violations' => $e->getViolations(),
            ]);
            throw $e;

        } catch (PaymentException $e) {
            // Good: ERROR for failures requiring attention
            $this->logger->error('Payment processing failed', [
                'orderId' => $orderId,
                'errorCode' => $e->getErrorCode(),
                'message' => $e->getMessage(),
                'exception' => $e,  // Full stack trace in logs
            ]);
            throw $e;

        } catch (\Throwable $e) {
            // Good: CRITICAL for unexpected errors
            $this->logger->critical('Unexpected error during order processing', [
                'orderId' => $orderId,
                'exception' => $e,
            ]);
            throw $e;
        }
    }
}
```

```php
// Good: Sanitizing sensitive data
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class PaymentLoggingService
{
    public function __construct(
        private readonly LoggerInterface $logger
    ) {}

    public function logPaymentAttempt(PaymentData $data): void
    {
        // Good: Mask sensitive data
        $this->logger->info('Payment attempt', [
            'customerId' => $data->getCustomerId(),
            'cardLast4' => substr($data->getCardNumber(), -4),
            'cardType' => $data->getCardType(),
            'amount' => $data->getAmount(),
            // Never log: full card number, CVV, passwords
        ]);
    }
}
```

```php
// Good: Custom channel for plugin logs
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Monolog\Logger;

class PluginSpecificLogger
{
    private LoggerInterface $logger;

    public function __construct(
        LoggerInterface $myPluginLogger  // Injected via services.xml
    ) {
        $this->logger = $myPluginLogger;
    }

    public function logSync(string $entityType, int $count): void
    {
        $this->logger->info('Sync completed', [
            'entityType' => $entityType,
            'count' => $count,
            'timestamp' => (new \DateTime())->format('c'),
        ]);
    }
}
```

```xml
<!-- Good: Custom logger channel in services.xml -->
<service id="MyVendor\MyPlugin\Service\PluginSpecificLogger">
    <argument type="service" id="monolog.logger.my_plugin"/>
</service>
```

```yaml
# Good: Custom channel configuration in config/packages/monolog.yaml
monolog:
    channels:
        - my_plugin

    handlers:
        my_plugin:
            type: rotating_file
            path: "%kernel.logs_dir%/my_plugin_%kernel.environment%.log"
            level: info
            channels: ["my_plugin"]
            max_files: 14
```

**Log level guidelines:**

| Level | Use Case |
|-------|----------|
| DEBUG | Detailed trace info (disabled in prod) |
| INFO | Significant events (order placed, sync complete) |
| NOTICE | Normal but noteworthy (config change) |
| WARNING | Unexpected but handled (retry, fallback) |
| ERROR | Failure requiring attention |
| CRITICAL | System component unavailable |
| ALERT | Immediate action required |
| EMERGENCY | System unusable |

Reference: [Logging in Shopware](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/logging.html)
