---
title: Payment Handler Implementation
impact: CRITICAL
impactDescription: secure payment processing for plugin-based payment methods
tags: payment, checkout, integration, transaction, gateway
---

## Payment Handler Implementation

**Impact: CRITICAL (secure payment processing for plugin-based payment methods)**

Payment handlers manage the payment flow in Shopware plugins. Implement synchronous or asynchronous handlers correctly with proper transaction state management.

**Incorrect (incomplete payment handler):**

```php
// Bad: Missing interface, no error handling
class MyPaymentHandler
{
    public function pay($transaction): void
    {
        $this->gateway->charge($transaction->getAmount());
    }
}
```

**Correct synchronous payment handler:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service\Payment;

use Shopware\Core\Checkout\Payment\Cart\PaymentHandler\SynchronousPaymentHandlerInterface;
use Shopware\Core\Checkout\Payment\Cart\SyncPaymentTransactionStruct;
use Shopware\Core\Checkout\Payment\PaymentException;
use Shopware\Core\Framework\Validation\DataBag\RequestDataBag;
use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Psr\Log\LoggerInterface;

class MySyncPaymentHandler implements SynchronousPaymentHandlerInterface
{
    public function __construct(
        private readonly PaymentGatewayClient $gateway,
        private readonly LoggerInterface $logger
    ) {}

    public function pay(
        SyncPaymentTransactionStruct $transaction,
        RequestDataBag $dataBag,
        SalesChannelContext $salesChannelContext
    ): void {
        $order = $transaction->getOrder();
        $transactionId = $transaction->getOrderTransaction()->getId();

        $this->logger->info('Processing payment', [
            'transactionId' => $transactionId,
            'orderId' => $order->getId(),
            'amount' => $order->getAmountTotal()
        ]);

        try {
            // Get payment data from checkout form
            $cardToken = $dataBag->get('myPaymentCardToken');

            if (!$cardToken) {
                throw PaymentException::syncProcessInterrupted(
                    $transactionId,
                    'Card token is required'
                );
            }

            // Process payment with gateway
            $result = $this->gateway->charge([
                'amount' => (int) ($order->getAmountTotal() * 100),
                'currency' => $order->getCurrency()->getIsoCode(),
                'token' => $cardToken,
                'reference' => $order->getOrderNumber(),
                'description' => 'Order ' . $order->getOrderNumber(),
                'metadata' => [
                    'order_id' => $order->getId(),
                    'customer_id' => $order->getOrderCustomer()->getCustomerId()
                ]
            ]);

            if (!$result->isSuccessful()) {
                throw PaymentException::syncProcessInterrupted(
                    $transactionId,
                    $result->getErrorMessage()
                );
            }

            $this->logger->info('Payment successful', [
                'transactionId' => $transactionId,
                'gatewayId' => $result->getTransactionId()
            ]);

        } catch (GatewayException $e) {
            $this->logger->error('Payment gateway error', [
                'transactionId' => $transactionId,
                'error' => $e->getMessage()
            ]);

            throw PaymentException::syncProcessInterrupted(
                $transactionId,
                'Payment failed: ' . $e->getMessage()
            );
        }
    }
}
```

**Correct asynchronous payment handler:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service\Payment;

use Shopware\Core\Checkout\Payment\Cart\PaymentHandler\AsynchronousPaymentHandlerInterface;
use Shopware\Core\Checkout\Payment\Cart\AsyncPaymentTransactionStruct;
use Shopware\Core\Checkout\Payment\PaymentException;
use Shopware\Core\Framework\Validation\DataBag\RequestDataBag;
use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Symfony\Component\HttpFoundation\RedirectResponse;
use Symfony\Component\HttpFoundation\Request;

class MyAsyncPaymentHandler implements AsynchronousPaymentHandlerInterface
{
    public function __construct(
        private readonly PaymentGatewayClient $gateway,
        private readonly EntityRepository $transactionRepository,
        private readonly LoggerInterface $logger
    ) {}

    public function pay(
        AsyncPaymentTransactionStruct $transaction,
        RequestDataBag $dataBag,
        SalesChannelContext $salesChannelContext
    ): RedirectResponse {
        $order = $transaction->getOrder();
        $returnUrl = $transaction->getReturnUrl();
        $transactionId = $transaction->getOrderTransaction()->getId();

        try {
            // Create checkout session with payment gateway
            $session = $this->gateway->createCheckoutSession([
                'amount' => (int) ($order->getAmountTotal() * 100),
                'currency' => $order->getCurrency()->getIsoCode(),
                'success_url' => $returnUrl,
                'cancel_url' => $returnUrl,
                'metadata' => [
                    'shopware_transaction_id' => $transactionId,
                    'order_number' => $order->getOrderNumber()
                ],
                'line_items' => $this->buildLineItems($order)
            ]);

            // Store session ID for finalize
            $this->storeSessionId($transactionId, $session->getId(), $salesChannelContext->getContext());

            $this->logger->info('Redirecting to payment gateway', [
                'transactionId' => $transactionId,
                'sessionId' => $session->getId()
            ]);

            // Redirect to external payment page
            return new RedirectResponse($session->getCheckoutUrl());

        } catch (GatewayException $e) {
            $this->logger->error('Failed to create checkout session', [
                'error' => $e->getMessage()
            ]);

            throw PaymentException::asyncProcessInterrupted(
                $transactionId,
                'Failed to initialize payment: ' . $e->getMessage()
            );
        }
    }

    public function finalize(
        AsyncPaymentTransactionStruct $transaction,
        Request $request,
        SalesChannelContext $salesChannelContext
    ): void {
        $transactionId = $transaction->getOrderTransaction()->getId();

        try {
            // Retrieve stored session ID
            $sessionId = $this->getSessionId($transactionId, $salesChannelContext->getContext());

            if (!$sessionId) {
                throw PaymentException::asyncFinalizeInterrupted(
                    $transactionId,
                    'Payment session not found'
                );
            }

            // Verify payment status with gateway
            $session = $this->gateway->getSession($sessionId);

            if ($session->getPaymentStatus() === 'paid') {
                $this->logger->info('Payment confirmed', [
                    'transactionId' => $transactionId,
                    'gatewaySessionId' => $sessionId
                ]);
                return; // Success - Shopware will set transaction to paid
            }

            if ($session->getPaymentStatus() === 'cancelled') {
                throw PaymentException::customerCanceled(
                    $transactionId,
                    'Payment was cancelled by customer'
                );
            }

            throw PaymentException::asyncFinalizeInterrupted(
                $transactionId,
                'Payment not completed: ' . $session->getPaymentStatus()
            );

        } catch (GatewayException $e) {
            throw PaymentException::asyncFinalizeInterrupted(
                $transactionId,
                'Payment verification failed: ' . $e->getMessage()
            );
        }
    }

    private function buildLineItems(OrderEntity $order): array
    {
        $items = [];
        foreach ($order->getLineItems() as $lineItem) {
            $items[] = [
                'name' => $lineItem->getLabel(),
                'quantity' => $lineItem->getQuantity(),
                'amount' => (int) ($lineItem->getUnitPrice() * 100)
            ];
        }
        return $items;
    }

    private function storeSessionId(string $transactionId, string $sessionId, Context $context): void
    {
        $this->transactionRepository->update([
            [
                'id' => $transactionId,
                'customFields' => [
                    'my_plugin_gateway_session' => $sessionId
                ]
            ]
        ], $context);
    }

    private function getSessionId(string $transactionId, Context $context): ?string
    {
        $criteria = new Criteria([$transactionId]);
        $transaction = $this->transactionRepository->search($criteria, $context)->first();
        return $transaction?->getCustomFields()['my_plugin_gateway_session'] ?? null;
    }
}
```

**Service registration:**

```xml
<!-- services.xml -->
<service id="MyVendor\MyPlugin\Service\Payment\MySyncPaymentHandler">
    <argument type="service" id="MyVendor\MyPlugin\Service\PaymentGatewayClient"/>
    <argument type="service" id="logger"/>
    <tag name="shopware.payment.method.sync"/>
</service>

<service id="MyVendor\MyPlugin\Service\Payment\MyAsyncPaymentHandler">
    <argument type="service" id="MyVendor\MyPlugin\Service\PaymentGatewayClient"/>
    <argument type="service" id="order_transaction.repository"/>
    <argument type="service" id="logger"/>
    <tag name="shopware.payment.method.async"/>
</service>
```

**Payment method registration in plugin class:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin;

use Shopware\Core\Framework\Plugin;
use Shopware\Core\Framework\Plugin\Context\InstallContext;
use Shopware\Core\Framework\Plugin\Context\UninstallContext;
use Shopware\Core\Framework\Plugin\Context\ActivateContext;
use Shopware\Core\Framework\Plugin\Util\PluginIdProvider;

class MyPlugin extends Plugin
{
    public function install(InstallContext $installContext): void
    {
        $this->addPaymentMethod($installContext->getContext());
    }

    public function uninstall(UninstallContext $uninstallContext): void
    {
        $this->setPaymentMethodActive(false, $uninstallContext->getContext());
    }

    public function activate(ActivateContext $activateContext): void
    {
        $this->setPaymentMethodActive(true, $activateContext->getContext());
    }

    private function addPaymentMethod(Context $context): void
    {
        $paymentMethodRepository = $this->container->get('payment_method.repository');
        $pluginIdProvider = $this->container->get(PluginIdProvider::class);

        $pluginId = $pluginIdProvider->getPluginIdByBaseClass(self::class, $context);

        $paymentMethodRepository->upsert([
            [
                'handlerIdentifier' => MySyncPaymentHandler::class,
                'name' => 'My Payment Method',
                'description' => 'Pay securely with My Payment',
                'pluginId' => $pluginId,
                'translations' => [
                    'de-DE' => [
                        'name' => 'Meine Zahlungsmethode',
                        'description' => 'Sicher bezahlen mit meiner Zahlung'
                    ],
                    'en-GB' => [
                        'name' => 'My Payment Method',
                        'description' => 'Pay securely with My Payment'
                    ]
                ]
            ]
        ], $context);
    }
}
```

**Payment handler interfaces:**

| Interface | Use Case |
|-----------|----------|
| `SynchronousPaymentHandlerInterface` | Immediate result (credit card) |
| `AsynchronousPaymentHandlerInterface` | Redirect flow (PayPal, Klarna) |
| `PreparedPaymentHandlerInterface` | Pre-validated payments |
| `RefundPaymentHandlerInterface` | Refund support |
| `RecurringPaymentHandlerInterface` | Subscription payments |

Reference: [Payment Handler](https://developer.shopware.com/docs/guides/plugins/plugins/checkout/payment/add-payment-plugin.html)
