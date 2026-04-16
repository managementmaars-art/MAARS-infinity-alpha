---
title: Debugging & Profiling Tools
impact: MEDIUM
impactDescription: efficient problem diagnosis and performance analysis
tags: devops, debugging, profiler, xdebug, logging
---

## Debugging & Profiling Tools

**Impact: MEDIUM (efficient problem diagnosis and performance analysis)**

Use Shopware's debugging tools, Symfony profiler, and Xdebug for efficient development and problem diagnosis.

**Correct debug configuration (.env.local):**

```env
# Enable development mode
APP_ENV=dev
APP_DEBUG=1

# Enable profiler
SHOPWARE_HTTP_CACHE_ENABLED=0

# Verbose logging
SHOPWARE_LOG_LEVEL=debug

# Xdebug (in container)
XDEBUG_MODE=debug,develop
XDEBUG_CONFIG="client_host=host.docker.internal client_port=9003"
```

**Using Symfony profiler:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Subscriber;

use Symfony\Component\HttpKernel\Profiler\Profiler;

class DebugSubscriber implements EventSubscriberInterface
{
    public function __construct(
        private readonly ?Profiler $profiler
    ) {}

    public function onRequest(RequestEvent $event): void
    {
        // Disable profiler for specific requests (e.g., AJAX)
        if ($this->profiler && $this->shouldDisableProfiler($event->getRequest())) {
            $this->profiler->disable();
        }
    }
}
```

**Correct debug output in development:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class DebugService
{
    public function __construct(
        private readonly LoggerInterface $logger,
        private readonly string $environment
    ) {}

    public function debugDump(mixed $data, string $label = ''): void
    {
        // Only in development
        if ($this->environment !== 'dev') {
            return;
        }

        // Use Symfony's dump() - appears in profiler
        dump($data);

        // Also log for CLI context
        $this->logger->debug($label, [
            'data' => $this->serializeForLog($data)
        ]);
    }

    public function measureTime(callable $callback, string $label): mixed
    {
        $start = microtime(true);

        $result = $callback();

        $duration = (microtime(true) - $start) * 1000;

        $this->logger->debug(sprintf('%s took %.2f ms', $label, $duration));

        return $result;
    }

    private function serializeForLog(mixed $data): mixed
    {
        if (is_object($data)) {
            if (method_exists($data, 'getId')) {
                return [
                    'class' => get_class($data),
                    'id' => $data->getId()
                ];
            }
            return get_class($data);
        }

        return $data;
    }
}
```

**Correct Twig debugging:**

```twig
{# In development templates #}

{# Dump variable to debug bar #}
{{ dump(product) }}

{# Dump all available variables #}
{{ dump() }}

{# Conditional debug output #}
{% if app.debug %}
    <pre>{{ product|json_encode(constant('JSON_PRETTY_PRINT')) }}</pre>
{% endif %}

{# Debug block rendering #}
{% block my_block %}
    {# Shows in profiler which blocks are rendered #}
    {{ parent() }}
{% endblock %}
```

**Correct custom data collector for profiler:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Profiler;

use Symfony\Bundle\FrameworkBundle\DataCollector\AbstractDataCollector;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

class MyPluginDataCollector extends AbstractDataCollector
{
    private array $apiCalls = [];

    public function collect(Request $request, Response $response, ?\Throwable $exception = null): void
    {
        $this->data = [
            'api_calls' => $this->apiCalls,
            'total_time' => array_sum(array_column($this->apiCalls, 'duration')),
            'call_count' => count($this->apiCalls)
        ];
    }

    public function recordApiCall(string $method, string $url, float $duration, int $statusCode): void
    {
        $this->apiCalls[] = [
            'method' => $method,
            'url' => $url,
            'duration' => $duration,
            'status' => $statusCode,
            'timestamp' => microtime(true)
        ];
    }

    public function getName(): string
    {
        return 'my_plugin';
    }

    public static function getTemplate(): ?string
    {
        return '@MyPlugin/profiler/my_plugin.html.twig';
    }

    // Getters for template
    public function getApiCalls(): array
    {
        return $this->data['api_calls'] ?? [];
    }

    public function getTotalTime(): float
    {
        return $this->data['total_time'] ?? 0;
    }

    public function getCallCount(): int
    {
        return $this->data['call_count'] ?? 0;
    }
}
```

**Correct log analysis:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Psr\Log\LoggerInterface;

class DiagnosticService
{
    public function __construct(
        private readonly LoggerInterface $logger,
        private readonly EntityRepository $productRepository
    ) {}

    public function diagnoseProductIssue(string $productId, Context $context): array
    {
        $diagnostics = [];

        // Log the diagnostic start
        $this->logger->info('Starting product diagnosis', ['productId' => $productId]);

        // Check product exists
        $product = $this->productRepository->search(
            new Criteria([$productId]),
            $context
        )->first();

        if (!$product) {
            $diagnostics['error'] = 'Product not found';
            $this->logger->error('Product not found', ['productId' => $productId]);
            return $diagnostics;
        }

        // Check visibility
        $diagnostics['visibility'] = $this->checkVisibility($product, $context);

        // Check stock
        $diagnostics['stock'] = [
            'available' => $product->getAvailableStock(),
            'isCloseout' => $product->getIsCloseout(),
            'minPurchase' => $product->getMinPurchase()
        ];

        // Check pricing
        $diagnostics['pricing'] = [
            'hasPrice' => $product->getPrice() !== null,
            'calculatedPrice' => $product->getCalculatedPrice()?->getTotalPrice()
        ];

        // Check categories
        $diagnostics['categories'] = $product->getCategoryTree() ?? [];

        $this->logger->info('Product diagnosis complete', [
            'productId' => $productId,
            'diagnostics' => $diagnostics
        ]);

        return $diagnostics;
    }
}
```

**Common debug commands:**

| Command | Description |
|---------|-------------|
| `bin/console debug:event-dispatcher` | List all event listeners |
| `bin/console debug:container` | List all services |
| `bin/console debug:router` | Show all routes |
| `bin/console debug:config` | Show configuration |
| `bin/console cache:pool:list` | List cache pools |
| `bin/console messenger:failed:show` | Show failed messages |

**Xdebug breakpoint tips:**

```php
// Conditional breakpoint (in IDE)
// Break only when condition is true
$product->getId() === 'abc123...'

// Logpoint (logs without breaking)
"Processing product: {$product->getId()}"

// Trace point (shows stack trace)
// Configure in IDE settings
```

**Performance profiling with Blackfire:**

```bash
# Install Blackfire probe
blackfire curl https://your-shop.local/api/product

# Profile CLI command
blackfire run bin/console my-plugin:sync

# Compare profiles
blackfire compare profile1 profile2
```

Reference: [Symfony Profiler](https://symfony.com/doc/current/profiler.html)
