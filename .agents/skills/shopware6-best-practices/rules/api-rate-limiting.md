---
title: API Rate Limiting
impact: MEDIUM
impactDescription: Rate limiting protects APIs from abuse and denial of service attacks while ensuring fair resource allocation
tags: [shopware6, api, rate-limiting, security, performance]
---

## API Rate Limiting

Shopware 6 provides built-in rate limiting functionality to protect API endpoints from abuse. Proper configuration prevents DoS attacks and ensures API availability for legitimate users.

Reference: https://developer.shopware.com/docs/guides/hosting/infrastructure/rate-limiter

### Incorrect

```php
<?php

// Bad: No rate limiting on resource-intensive endpoint
namespace MyPlugin\Controller\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['store-api']])]
class VulnerableController extends AbstractController
{
    // Bad: Public endpoint with no rate limiting - DoS vulnerable
    #[Route(path: '/store-api/my-plugin/search', methods: ['POST'])]
    public function search(Request $request): JsonResponse
    {
        // Expensive database operation without protection
        $results = $this->performExpensiveSearch($request->get('query'));

        return new JsonResponse(['results' => $results]);
    }

    // Bad: Login attempt without rate limiting - brute force vulnerable
    #[Route(path: '/store-api/my-plugin/verify', methods: ['POST'])]
    public function verify(Request $request): JsonResponse
    {
        $code = $request->get('code');

        if ($this->validateCode($code)) {
            return new JsonResponse(['valid' => true]);
        }

        return new JsonResponse(['valid' => false]);
    }
}
```

```yaml
# Bad: No rate limiter configuration in shopware.yaml
shopware:
    api:
        # Missing rate_limiter configuration
```

### Correct

```yaml
# Good: Proper rate limiter configuration in config/packages/shopware.yaml
shopware:
    api:
        rate_limiter:
            # Good: Configure login rate limiting
            login:
                enabled: true
                policy: time_backoff
                reset: 24 hours
                limits:
                    - limit: 10
                      interval: 60 seconds
                    - limit: 15
                      interval: 300 seconds
                    - limit: 20
                      interval: 3600 seconds

            # Good: Custom rate limiter for plugin endpoint
            my_plugin_search:
                enabled: true
                policy: fixed_window
                limit: 100
                interval: 60 seconds
                lock_factory: lock.factory

            # Good: Strict rate limiting for sensitive operations
            my_plugin_verify:
                enabled: true
                policy: sliding_window
                limit: 5
                interval: 300 seconds

            # Good: Rate limiting for contact form
            contact_form:
                enabled: true
                policy: time_backoff
                reset: 24 hours
                limits:
                    - limit: 3
                      interval: 60 seconds
                    - limit: 5
                      interval: 3600 seconds
```

```php
<?php

// Good: Controller with rate limiting applied
namespace MyPlugin\Controller\Api;

use Shopware\Core\Framework\RateLimiter\RateLimiter;
use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['store-api']])]
class ProtectedController extends AbstractController
{
    public function __construct(
        private readonly RateLimiter $rateLimiter
    ) {
    }

    #[Route(
        path: '/store-api/my-plugin/search',
        name: 'store-api.my-plugin.search',
        methods: ['POST']
    )]
    public function search(Request $request, SalesChannelContext $context): JsonResponse
    {
        // Good: Apply rate limiting based on client IP
        $this->rateLimiter->ensureAccepted(
            'my_plugin_search',
            $request->getClientIp()
        );

        $results = $this->performSearch($request->get('query'));

        return new JsonResponse(['results' => $results]);
    }

    #[Route(
        path: '/store-api/my-plugin/verify',
        name: 'store-api.my-plugin.verify',
        methods: ['POST']
    )]
    public function verify(Request $request, SalesChannelContext $context): JsonResponse
    {
        // Good: Rate limit by combination of IP and context
        $cacheKey = $request->getClientIp() . '-' . $context->getSalesChannelId();

        $this->rateLimiter->ensureAccepted('my_plugin_verify', $cacheKey);

        $code = $request->get('code');

        if ($this->validateCode($code)) {
            // Good: Reset rate limiter on successful verification
            $this->rateLimiter->reset('my_plugin_verify', $cacheKey);

            return new JsonResponse(['valid' => true]);
        }

        return new JsonResponse(['valid' => false], Response::HTTP_UNAUTHORIZED);
    }
}
```

```php
<?php

// Good: Custom rate limiter factory for advanced scenarios
namespace MyPlugin\RateLimiter;

use Shopware\Core\Framework\RateLimiter\Policy\TimeBackoff;
use Shopware\Core\Framework\RateLimiter\RateLimiterFactory;
use Symfony\Component\Lock\LockFactory;
use Symfony\Component\RateLimiter\Storage\StorageInterface;

class MyPluginRateLimiterFactory
{
    public function __construct(
        private readonly StorageInterface $storage,
        private readonly LockFactory $lockFactory
    ) {
    }

    public function create(string $id): TimeBackoff
    {
        // Good: Custom time backoff policy with specific limits
        return new TimeBackoff(
            $id,
            $this->storage,
            $this->lockFactory->createLock($id),
            [
                ['limit' => 3, 'interval' => '60 seconds'],
                ['limit' => 5, 'interval' => '300 seconds'],
                ['limit' => 10, 'interval' => '3600 seconds'],
            ],
            new \DateInterval('P1D')
        );
    }
}
```

```xml
<!-- Good: Service registration for rate-limited controller -->
<service id="MyPlugin\Controller\Api\ProtectedController" public="true">
    <argument type="service" id="shopware.rate_limiter"/>
    <tag name="controller.service_arguments"/>
</service>
```
