---
title: Implement CSRF Protection
impact: HIGH
impactDescription: prevents cross-site request forgery attacks
tags: security, csrf, storefront, forms, ajax
---

## Implement CSRF Protection

**Impact: HIGH (prevents cross-site request forgery attacks)**

Cross-Site Request Forgery (CSRF) attacks trick authenticated users into performing unintended actions. Shopware 6 provides built-in CSRF protection for storefront forms. Always use CSRF tokens for state-changing operations and follow proper HTTP method semantics.

**Incorrect (missing CSRF protection):**

```php
// Bad: Using GET for state-changing operations
#[Route(defaults: ['_routeScope' => ['storefront']])]
class CartController extends StorefrontController
{
    // Bad: GET request modifies cart state - no CSRF protection
    #[Route(path: '/cart/add/{productId}', name: 'frontend.cart.add', methods: ['GET'])]
    public function addToCart(string $productId, SalesChannelContext $context): Response
    {
        $this->cartService->add($productId, $context);
        return $this->redirectToRoute('frontend.cart.page');
    }

    // Bad: No CSRF token validation
    #[Route(path: '/cart/clear', name: 'frontend.cart.clear', methods: ['POST'])]
    public function clearCart(SalesChannelContext $context): Response
    {
        // Bad: Missing _csrf_token check
        $this->cartService->clear($context);
        return new JsonResponse(['success' => true]);
    }
}
```

```twig
{# Bad: Form without CSRF token #}
<form action="{{ path('frontend.account.update') }}" method="POST">
    <input type="text" name="firstName" value="{{ customer.firstName }}">
    <input type="text" name="lastName" value="{{ customer.lastName }}">
    {# Bad: Missing CSRF token field #}
    <button type="submit">Update</button>
</form>
```

```javascript
// Bad: AJAX request without CSRF token
fetch('/frontend/cart/add', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ productId: '123' })
    // Bad: No CSRF token in request
});
```

**Correct (proper CSRF implementation):**

```php
// Good: POST for state changes with CSRF validation
use Shopware\Storefront\Controller\StorefrontController;
use Shopware\Core\Framework\Routing\Annotation\Since;

#[Route(defaults: ['_routeScope' => ['storefront']])]
class CartController extends StorefrontController
{
    public function __construct(
        private readonly CartService $cartService
    ) {
    }

    // Good: POST method for state changes, CSRF handled by framework
    #[Route(path: '/cart/add', name: 'frontend.cart.add', methods: ['POST'], defaults: ['XmlHttpRequest' => true])]
    public function addToCart(Request $request, SalesChannelContext $context): Response
    {
        // Good: CSRF token is validated automatically for storefront POST requests
        $productId = $request->request->get('productId');

        $this->cartService->add($productId, $context);

        return $this->createActionResponse($request);
    }

    // Good: Explicit CSRF check for custom endpoints
    #[Route(path: '/cart/clear', name: 'frontend.cart.clear', methods: ['POST'])]
    public function clearCart(Request $request, SalesChannelContext $context): Response
    {
        // Good: Validate CSRF token manually if needed
        $token = $request->request->get('_csrf_token');

        if (!$this->isCsrfTokenValid('frontend.cart.clear', $token)) {
            throw new InvalidCsrfTokenException();
        }

        $this->cartService->clear($context);

        return $this->redirectToRoute('frontend.cart.page');
    }
}
```

```php
// Good: Controller with proper HTTP method semantics
#[Route(defaults: ['_routeScope' => ['storefront']])]
class AccountController extends StorefrontController
{
    // Good: GET for reading data (safe, idempotent)
    #[Route(path: '/account/profile', name: 'frontend.account.profile', methods: ['GET'], defaults: ['_loginRequired' => true])]
    public function profile(SalesChannelContext $context): Response
    {
        return $this->renderStorefront('@Storefront/storefront/page/account/profile.html.twig', [
            'customer' => $context->getCustomer(),
        ]);
    }

    // Good: POST for creating/updating data (not safe, not idempotent)
    #[Route(path: '/account/profile', name: 'frontend.account.profile.save', methods: ['POST'], defaults: ['_loginRequired' => true])]
    public function saveProfile(Request $request, SalesChannelContext $context): Response
    {
        // CSRF is validated automatically for POST requests in storefront scope
        $data = $request->request->all();

        $this->accountService->updateProfile($data, $context);

        return $this->redirectToRoute('frontend.account.profile');
    }

    // Good: DELETE for deletions (explicit CSRF required)
    #[Route(path: '/account/address/{addressId}', name: 'frontend.account.address.delete', methods: ['POST'], defaults: ['_loginRequired' => true])]
    public function deleteAddress(string $addressId, Request $request, SalesChannelContext $context): Response
    {
        // Good: Using POST with _method override for DELETE semantics
        $this->addressService->delete($addressId, $context);

        return $this->redirectToRoute('frontend.account.address.page');
    }
}
```

```twig
{# Good: Form with CSRF token using Shopware's form helper #}
{% sw_csrf 'frontend.account.profile.save' %}

<form action="{{ path('frontend.account.profile.save') }}" method="POST">
    {# Good: Include CSRF token field #}
    {{ sw_csrf('frontend.account.profile.save') }}

    <input type="text" name="firstName" value="{{ customer.firstName }}">
    <input type="text" name="lastName" value="{{ customer.lastName }}">
    <button type="submit">Update Profile</button>
</form>
```

```twig
{# Good: AJAX form with CSRF token in meta tag #}
{% block base_header %}
    {{ parent() }}
    {# Good: Make CSRF token available for JavaScript #}
    <meta name="csrf-token" content="{{ sw_csrf('frontend.cart.add', {'mode': 'token'}) }}">
{% endblock %}
```

```javascript
// Good: AJAX request with CSRF token
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

fetch('/cart/add', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken  // Good: CSRF token in header
    },
    body: JSON.stringify({ productId: '123' })
});

// Good: Using Shopware's HttpClient plugin which handles CSRF automatically
import HttpClient from 'src/service/http-client.service';

const client = new HttpClient();
client.post('/cart/add', JSON.stringify({ productId: '123' }), (response) => {
    // HttpClient automatically includes CSRF token
    console.log('Added to cart');
});
```

```php
// Good: Disabling CSRF for specific Store API routes (API uses token auth instead)
#[Route(defaults: ['_routeScope' => ['store-api']])]
class StoreApiController extends AbstractController
{
    // Good: Store API uses sw-context-token for authentication, not CSRF
    #[Route(path: '/store-api/cart/add', name: 'store-api.cart.add', methods: ['POST'])]
    public function addToCart(Request $request, SalesChannelContext $context): Response
    {
        // Store API is protected by sw-access-key and sw-context-token
        // CSRF is not needed for API routes
        return new JsonResponse(['success' => true]);
    }
}
```

**HTTP method semantics:**

| Method | Safe | Idempotent | Use Case |
|--------|------|------------|----------|
| GET | Yes | Yes | Read data, navigation |
| POST | No | No | Create, submit forms |
| PUT | No | Yes | Full update |
| PATCH | No | Yes | Partial update |
| DELETE | No | Yes | Remove resources |

**CSRF protection by scope:**

| Scope | CSRF Protection | Token Method |
|-------|-----------------|--------------|
| `storefront` | Automatic for POST | Session-based |
| `store-api` | Not needed | sw-context-token |
| `api` | Not needed | OAuth2 Bearer |

Reference: [Storefront CSRF](https://developer.shopware.com/docs/guides/plugins/plugins/storefront/add-csrf-protection) | [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
