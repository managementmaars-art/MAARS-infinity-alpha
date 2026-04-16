---
title: App Payment Handlers
impact: HIGH
impactDescription: secure payment processing for app-based payment methods
tags: app, payment, checkout, transaction, finalize
---

## App Payment Handlers

**Impact: HIGH (secure payment processing for app-based payment methods)**

Apps can provide payment methods with synchronous or asynchronous payment flows. Implement proper handlers for pay, finalize, capture, and refund operations.

**Incorrect (incomplete payment handler):**

```php
// Bad: No error handling, no proper response
#[Route(path: '/payment/pay', methods: ['POST'])]
public function pay(Request $request): Response
{
    $data = json_decode($request->getContent(), true);
    $this->processPayment($data);
    return new Response('OK');
}
```

**Correct payment method configuration:**

```xml
<!-- manifest.xml -->
<payments>
    <!-- Synchronous payment (immediate result) -->
    <payment-method>
        <identifier>my_app_direct_payment</identifier>
        <name>My Direct Payment</name>
        <name lang="de-DE">Meine Direktzahlung</name>
        <description>Pay directly with My Payment Service</description>
        <pay-url>https://my-app.com/payment/pay</pay-url>
        <icon>icon.png</icon>
    </payment-method>

    <!-- Asynchronous payment (redirect flow) -->
    <payment-method>
        <identifier>my_app_redirect_payment</identifier>
        <name>My Redirect Payment</name>
        <pay-url>https://my-app.com/payment/pay</pay-url>
        <finalize-url>https://my-app.com/payment/finalize</finalize-url>
        <icon>icon.png</icon>
    </payment-method>

    <!-- Payment with capture/refund support -->
    <payment-method>
        <identifier>my_app_full_payment</identifier>
        <name>My Full Payment</name>
        <pay-url>https://my-app.com/payment/pay</pay-url>
        <finalize-url>https://my-app.com/payment/finalize</finalize-url>
        <capture-url>https://my-app.com/payment/capture</capture-url>
        <refund-url>https://my-app.com/payment/refund</refund-url>
        <recurring-url>https://my-app.com/payment/recurring</recurring-url>
    </payment-method>
</payments>
```

**Correct synchronous payment handler:**

```php
<?php declare(strict_types=1);

class PaymentController
{
    public function __construct(
        private readonly ShopRepository $shopRepository,
        private readonly PaymentGateway $gateway,
        private readonly LoggerInterface $logger
    ) {}

    #[Route(path: '/payment/pay', methods: ['POST'])]
    public function pay(Request $request): JsonResponse
    {
        try {
            $payload = $this->verifyRequest($request);

            $order = $payload['order'];
            $orderTransaction = $payload['orderTransaction'];
            $returnUrl = $payload['returnUrl'];
            $shop = $this->shopRepository->findByShopId($payload['source']['shopId']);

            // Get payment amount
            $amount = $orderTransaction['amount']['totalPrice'];
            $currency = $order['currency']['isoCode'];

            // Good: Log payment attempt
            $this->logger->info('Processing payment', [
                'orderId' => $order['id'],
                'transactionId' => $orderTransaction['id'],
                'amount' => $amount
            ]);

            // Process with payment gateway
            $result = $this->gateway->charge([
                'amount' => $amount * 100, // Convert to cents
                'currency' => $currency,
                'reference' => $orderTransaction['id'],
                'description' => 'Order ' . $order['orderNumber'],
                'customer' => [
                    'email' => $order['orderCustomer']['email'],
                    'name' => $order['orderCustomer']['firstName'] . ' ' . $order['orderCustomer']['lastName']
                ]
            ]);

            if ($result->isSuccessful()) {
                // Good: Return paid status for synchronous payment
                return new JsonResponse([
                    'status' => 'paid',
                    'message' => 'Payment successful'
                ]);
            }

            // Good: Return failed status with message
            return new JsonResponse([
                'status' => 'failed',
                'message' => $result->getErrorMessage()
            ]);

        } catch (\Exception $e) {
            $this->logger->error('Payment failed', ['error' => $e->getMessage()]);

            return new JsonResponse([
                'status' => 'failed',
                'message' => 'Payment processing error'
            ]);
        }
    }
}
```

**Correct asynchronous payment with redirect:**

```php
#[Route(path: '/payment/pay', methods: ['POST'])]
public function payAsync(Request $request): JsonResponse
{
    $payload = $this->verifyRequest($request);

    $order = $payload['order'];
    $orderTransaction = $payload['orderTransaction'];
    $returnUrl = $payload['returnUrl']; // Where to return after payment

    try {
        // Create payment session with external provider
        $session = $this->gateway->createSession([
            'amount' => $orderTransaction['amount']['totalPrice'] * 100,
            'currency' => $order['currency']['isoCode'],
            'reference' => $orderTransaction['id'],
            'success_url' => $returnUrl, // Shopware handles the redirect
            'cancel_url' => $returnUrl,
            'metadata' => [
                'shop_id' => $payload['source']['shopId'],
                'order_id' => $order['id'],
                'transaction_id' => $orderTransaction['id']
            ]
        ]);

        // Store session for finalize
        $this->storePaymentSession($orderTransaction['id'], $session);

        // Good: Redirect to external payment page
        return new JsonResponse([
            'redirectUrl' => $session->getCheckoutUrl()
        ]);

    } catch (\Exception $e) {
        return new JsonResponse([
            'status' => 'failed',
            'message' => $e->getMessage()
        ]);
    }
}

#[Route(path: '/payment/finalize', methods: ['POST'])]
public function finalize(Request $request): JsonResponse
{
    $payload = $this->verifyRequest($request);

    $orderTransaction = $payload['orderTransaction'];
    $transactionId = $orderTransaction['id'];

    try {
        // Retrieve stored session
        $session = $this->getPaymentSession($transactionId);

        // Verify payment status with gateway
        $paymentStatus = $this->gateway->getSessionStatus($session->getId());

        if ($paymentStatus->isPaid()) {
            return new JsonResponse([
                'status' => 'paid',
                'message' => 'Payment confirmed'
            ]);
        }

        if ($paymentStatus->isCancelled()) {
            return new JsonResponse([
                'status' => 'cancelled',
                'message' => 'Payment was cancelled'
            ]);
        }

        return new JsonResponse([
            'status' => 'failed',
            'message' => 'Payment not completed'
        ]);

    } catch (\Exception $e) {
        return new JsonResponse([
            'status' => 'failed',
            'message' => $e->getMessage()
        ]);
    }
}
```

**Correct capture handler:**

```php
#[Route(path: '/payment/capture', methods: ['POST'])]
public function capture(Request $request): JsonResponse
{
    $payload = $this->verifyRequest($request);

    $orderTransaction = $payload['orderTransaction'];
    $preorderPayment = $payload['preorderPayment'] ?? null;

    try {
        // Get original authorization
        $authorization = $this->getAuthorization($orderTransaction['id']);

        // Capture the payment
        $capture = $this->gateway->capture(
            $authorization->getId(),
            $orderTransaction['amount']['totalPrice'] * 100
        );

        if ($capture->isSuccessful()) {
            return new JsonResponse([
                'status' => 'paid',
                'message' => 'Payment captured'
            ]);
        }

        return new JsonResponse([
            'status' => 'failed',
            'message' => $capture->getErrorMessage()
        ]);

    } catch (\Exception $e) {
        return new JsonResponse([
            'status' => 'failed',
            'message' => $e->getMessage()
        ]);
    }
}
```

**Correct refund handler:**

```php
#[Route(path: '/payment/refund', methods: ['POST'])]
public function refund(Request $request): JsonResponse
{
    $payload = $this->verifyRequest($request);

    $refund = $payload['refund'];
    $orderTransaction = $payload['orderTransaction'];

    try {
        // Get original payment
        $payment = $this->getPayment($orderTransaction['id']);

        // Process refund
        $result = $this->gateway->refund(
            $payment->getId(),
            $refund['amount']['totalPrice'] * 100
        );

        if ($result->isSuccessful()) {
            return new JsonResponse([
                'status' => 'completed',
                'message' => 'Refund processed'
            ]);
        }

        return new JsonResponse([
            'status' => 'failed',
            'message' => $result->getErrorMessage()
        ]);

    } catch (\Exception $e) {
        return new JsonResponse([
            'status' => 'failed',
            'message' => $e->getMessage()
        ]);
    }
}
```

**Payment status values:**

| Status | Description |
|--------|-------------|
| `paid` | Payment successful |
| `failed` | Payment failed |
| `cancelled` | Payment cancelled by user |
| `authorized` | Payment authorized (capture pending) |
| `unconfirmed` | Awaiting confirmation |

Reference: [App Payments](https://developer.shopware.com/docs/guides/plugins/apps/payment.html)
