---
title: Implement Proper Authentication
impact: CRITICAL
impactDescription: prevents unauthorized access to protected resources
tags: security, authentication, api, routes, context
---

## Implement Proper Authentication

**Impact: CRITICAL (prevents unauthorized access to protected resources)**

Shopware 6 uses route scopes and context validation to enforce authentication. Every route must be properly scoped, and controllers must validate the SalesChannelContext or AdminContext to ensure authenticated access.

**Incorrect (missing or improper authentication):**

```php
// Bad: No route scope defined - accessible without authentication
use Shopware\Core\Framework\Routing\Annotation\RouteScope;

class UnsafeController extends AbstractController
{
    // Bad: Missing route scope and login requirement
    #[Route(path: '/api/admin/users', name: 'api.admin.users', methods: ['GET'])]
    public function getUsers(): Response
    {
        // Bad: Exposing sensitive admin data without authentication
        $users = $this->userRepository->search(new Criteria(), Context::createDefaultContext());
        return new JsonResponse($users);
    }
}
```

```php
// Bad: Using default context instead of authenticated context
class OrderController extends AbstractController
{
    #[Route(path: '/api/orders', name: 'api.orders', methods: ['GET'])]
    public function getOrders(): Response
    {
        // Bad: Bypassing authentication by using default context
        $context = Context::createDefaultContext();
        $orders = $this->orderRepository->search(new Criteria(), $context);
        return new JsonResponse($orders);
    }
}
```

```php
// Bad: Not validating customer in sales channel context
class CustomerDataController extends StorefrontController
{
    #[Route(path: '/account/data', name: 'frontend.account.data', methods: ['GET'])]
    public function getData(SalesChannelContext $context): Response
    {
        // Bad: No check if customer is logged in
        $customerId = $context->getCustomer()->getId();
        // This will throw an error if customer is null!
    }
}
```

**Correct (proper route scopes and authentication):**

```php
// Good: Properly scoped Admin API route with authentication
use Shopware\Core\Framework\Routing\RoutingException;

#[Route(defaults: ['_routeScope' => ['api']])]
class AdminUserController extends AbstractController
{
    public function __construct(
        private readonly EntityRepository $userRepository
    ) {
    }

    #[Route(path: '/api/admin/users', name: 'api.admin.users', methods: ['GET'])]
    public function getUsers(Context $context): Response
    {
        // Good: Context is injected and validated by the framework
        // Only authenticated admin users can access this endpoint

        // Good: Use the authenticated context
        $users = $this->userRepository->search(new Criteria(), $context);

        return new JsonResponse([
            'users' => $users->getElements()
        ]);
    }
}
```

```php
// Good: Store API route with proper sales channel authentication
use Shopware\Core\System\SalesChannel\SalesChannelContext;

#[Route(defaults: ['_routeScope' => ['store-api']])]
class CustomerOrderController extends AbstractController
{
    public function __construct(
        private readonly EntityRepository $orderRepository
    ) {
    }

    #[Route(path: '/store-api/customer/orders', name: 'store-api.customer.orders', methods: ['GET'], defaults: ['_loginRequired' => true])]
    public function getCustomerOrders(Request $request, SalesChannelContext $context): Response
    {
        // Good: _loginRequired ensures customer is authenticated
        $customer = $context->getCustomer();

        // Good: Filter orders to only this customer's orders
        $criteria = new Criteria();
        $criteria->addFilter(new EqualsFilter('orderCustomer.customerId', $customer->getId()));

        return new JsonResponse(
            $this->orderRepository->search($criteria, $context->getContext())
        );
    }
}
```

```php
// Good: Storefront controller with login requirement and customer validation
use Shopware\Storefront\Controller\StorefrontController;

#[Route(defaults: ['_routeScope' => ['storefront']])]
class AccountController extends StorefrontController
{
    #[Route(path: '/account/profile', name: 'frontend.account.profile', methods: ['GET'], defaults: ['_loginRequired' => true, '_loginRequiredAllowGuest' => false])]
    public function profile(SalesChannelContext $context): Response
    {
        // Good: Framework ensures customer is logged in and not a guest
        $customer = $context->getCustomer();

        return $this->renderStorefront('@Storefront/storefront/page/account/profile.html.twig', [
            'customer' => $customer,
        ]);
    }

    #[Route(path: '/account/order/{orderId}', name: 'frontend.account.order.detail', methods: ['GET'], defaults: ['_loginRequired' => true])]
    public function orderDetail(string $orderId, SalesChannelContext $context): Response
    {
        $customer = $context->getCustomer();

        // Good: Verify order belongs to authenticated customer
        $criteria = new Criteria([$orderId]);
        $criteria->addFilter(new EqualsFilter('orderCustomer.customerId', $customer->getId()));

        $order = $this->orderRepository->search($criteria, $context->getContext())->first();

        if (!$order) {
            throw CustomerException::customerNotFound($customer->getId());
        }

        return $this->renderStorefront('@Storefront/storefront/page/account/order/detail.html.twig', [
            'order' => $order,
        ]);
    }
}
```

```php
// Good: API route with custom token authentication
use Shopware\Core\Framework\Api\Context\AdminApiSource;

#[Route(defaults: ['_routeScope' => ['api']])]
class IntegrationController extends AbstractController
{
    #[Route(path: '/api/_action/my-integration/sync', name: 'api.action.my-integration.sync', methods: ['POST'])]
    public function sync(Context $context): Response
    {
        // Good: Verify the context source for integration access
        $source = $context->getSource();

        if (!$source instanceof AdminApiSource) {
            throw new AccessDeniedException('Admin API access required');
        }

        // Good: Check if it's an integration (vs. user)
        if ($source->getIntegrationId() === null) {
            throw new AccessDeniedException('Integration access required');
        }

        // Process integration sync
        return new JsonResponse(['status' => 'synced']);
    }
}
```

**Route scope reference:**

| Scope | Authentication | Use Case |
|-------|---------------|----------|
| `api` | OAuth2 Bearer Token / Integration | Admin API endpoints |
| `store-api` | sw-access-key + optional sw-context-token | Headless storefront |
| `storefront` | Session-based | Traditional storefront |

**Route defaults reference:**

| Default | Purpose |
|---------|---------|
| `_loginRequired` | Customer must be logged in |
| `_loginRequiredAllowGuest` | Allow guest customers (default: true) |
| `_routeScope` | Define allowed API scopes |

Reference: [Route Scopes](https://developer.shopware.com/docs/guides/plugins/plugins/framework/routing) | [Store API Authentication](https://developer.shopware.com/docs/concepts/api/store-api)
